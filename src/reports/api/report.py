import uuid
import asyncio
import json
import pydantic
from os.path import splitext
from dishka import FromDishka
from fastapi import APIRouter, Request, Response, UploadFile, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from dishka.integrations.fastapi import inject

from reports.domain.use_cases.reports.download_report import DownloadReportUseCase
from reports.domain.use_cases.reports.new_report_generation import NewReportGenerateUseCase
from reports.domain.use_cases.reports.save_report import SaveDataUseCase
from reports.domain.use_cases.reports.update_report import UpdateDataUseCase
from reports.domain.use_cases.reports.delete_report import DeleteDataUseCase
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.websocket.report_notifications import report_notification_hub
from reports.schemas.report_models import ReportInputData
from reports.api.dependencies import validate_jwt
from reports.schemas.user_models import UserPayload

reports_router = APIRouter(dependencies=[Depends(validate_jwt)])


@reports_router.get("/download/{id}",
                    status_code=status.HTTP_200_OK)
@inject
async def download_file(id: str,
                        use_case: FromDishka[DownloadReportUseCase]):
    try:
        result: bytes = await use_case.execute(id)
        return Response(content=result, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@reports_router.get("/download-file/{object_name:path}",
                    status_code=status.HTTP_200_OK)
@inject
async def download_object_file(object_name: str, repository: FromDishka[MinioRepository]):
    extension = splitext(object_name)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".geojson": "application/geo+json",
    }

    if extension not in media_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unsupported file extension")

    try:
        result = repository.get_object(object_name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return Response(
        content=result,
        media_type=media_types[extension],
        headers={"Content-Disposition": f'attachment; filename="{object_name}"'}
    )


@reports_router.post("/upload")
async def upload_file(file: UploadFile):
    '''
    Сюда загружается файл .csv или .xlsx с данными, на данный момент он просто сохраняется в отдельной папке.
    В будущем здесь будет обработка содержимого файла.
    '''
    pass


@reports_router.post("/generate-report", status_code=status.HTTP_201_CREATED)
@inject
async def generate_report(payload: dict,
                          save_use_case: FromDishka[SaveDataUseCase],
                          generate_use_case: FromDishka[NewReportGenerateUseCase],
                          user_data: UserPayload = Depends(validate_jwt)):
    try:
        user_id = user_data.user_id
        report_id = str(uuid.uuid4())
        message = ReportInputData(**payload, user_id=user_id, report_id=report_id)

        await save_use_case.execute(data=message)
        await generate_use_case.execute(message=message)
        
        return {"status": "success", "report_id": report_id}
    except pydantic.ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@reports_router.get("/events/report-ready")
async def report_ready_events(request: Request,
                              user_data: UserPayload = Depends(validate_jwt)):
    user_id = user_data.user_id

    async def event_stream():
        queue = await report_notification_hub.subscribe(user_id)
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    payload = json.dumps(event, ensure_ascii=False)
                    yield f"event: report_ready\ndata: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            await report_notification_hub.unsubscribe(user_id, queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@reports_router.post("/save-report-data", status_code=status.HTTP_201_CREATED)
@inject
async def save_report_data(payload: dict,
                           use_case: FromDishka[SaveDataUseCase],
                           user_data: UserPayload = Depends(validate_jwt)):
    try:
        user_id = user_data.user_id
        report_id = str(uuid.uuid4())
        message = ReportInputData(**payload, user_id=user_id, report_id=report_id)
        await use_case.execute(data=message)
        return {"status": "success", "message": "Report data saved successfully."}
    except pydantic.ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@reports_router.put("/update-report-data/{file_id}", status_code=status.HTTP_200_OK)
@inject
async def update_report_data(file_id: int,
                             payload: dict,
                             use_case: FromDishka[UpdateDataUseCase],
                             user_data: UserPayload = Depends(validate_jwt)):
    try:
        user_id = user_data.user_id
        report_id = str(uuid.uuid4())
        message = ReportInputData(**payload, user_id=user_id, report_id=report_id)
        await use_case.execute(file_id=file_id, data=message)
        return {"status": "success", "message": "Report data updated successfully."}
    except pydantic.ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors()
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@reports_router.delete("/delete-report-data/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_report_data(file_id: int, use_case: FromDishka[DeleteDataUseCase]):
    try:
        await use_case.execute(file_id=file_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))