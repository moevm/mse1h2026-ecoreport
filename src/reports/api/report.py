import uuid
import asyncio
import json
import pydantic

from datetime import timedelta, timezone
from os.path import splitext

from dishka import FromDishka
from fastapi import APIRouter, Request, Response, UploadFile, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from dishka.integrations.fastapi import inject
import os

from reports.domain.use_cases.download_report import DownloadReportUseCase
from reports.domain.use_cases.generate_report import GenerateReportUseCase
from reports.domain.use_cases.new_report_generation import NewReportGenerateUseCase
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.websocket.report_notifications import report_notification_hub
from reports.schemas.report_models import ReportInputData

reports_router = APIRouter()

templates: Jinja2Templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "templates"))

@reports_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@reports_router.get("/create", response_class=HTMLResponse)
async def create_report(request: Request):
    context = {
        'request': request,
        'osm_tile_url': os.getenv("OSM_TILE_URL"),
        'osm_attribution': os.getenv("OSM_ATTRIBUTION"),
        'leaflet_js_url': os.getenv("LEAFLET_JS_URL"),
        'leaflet_js_integrity': os.getenv("LEAFLET_JS_INTEGRITY"),
        'leaflet_js_crossorigin': os.getenv("LEAFLET_JS_CROSSORIGIN"),
        'leaflet_css_url': os.getenv("LEAFLET_CSS_URL"),
        'leaflet_css_integrity': os.getenv("LEAFLET_CSS_INTEGRITY"),
        'leaflet_css_crossorigin': os.getenv("LEAFLET_CSS_CROSSORIGIN"),
    }
    return templates.TemplateResponse(request=request, name="create_report.html", context=context)


@reports_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="settings.html", context=context)


@reports_router.get("/documents", response_class=HTMLResponse)
@inject
async def documents_page(request: Request, repository: FromDishka[MinioRepository]):
    reports_map: dict[str, dict] = {}
    allowed_extensions = {".pdf", ".docx", ".geojson"}
    gmt_plus_3 = timezone(timedelta(hours=3))

    for obj in repository.list_objects():
        extension = splitext(obj.object_name)[1].lower()
        if extension not in allowed_extensions:
            continue

        report_key = splitext(obj.object_name)[0]
        report = reports_map.get(report_key)

        if report is None:
            report = {
                "title": report_key,
                "last_modified": obj.last_modified,
                "files": {
                    "pdf": None,
                    "docx": None,
                    "geojson": None,
                },
            }
            reports_map[report_key] = report

        report["files"][extension.removeprefix(".")] = obj.object_name

        if report["last_modified"] is None or (
            obj.last_modified is not None and obj.last_modified > report["last_modified"]
        ):
            report["last_modified"] = obj.last_modified

    reports = sorted(
        reports_map.values(),
        key=lambda item: item["last_modified"] or 0,
        reverse=True,
    )

    for report in reports:
        last_modified = report.get("last_modified")

        if last_modified is not None:
            if last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)
            last_modified = last_modified.astimezone(gmt_plus_3)

        report["last_modified"] = (
            last_modified.strftime("%d.%m.%Y %H:%M")
            if last_modified is not None
            else "Дата создания недоступна"
        )

    context = {
        'request': request,
        'reports': reports,
    }
    return templates.TemplateResponse(request=request, name="documents.html", context=context)


@reports_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="login.html", context=context)


@reports_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="register.html", context=context)


@reports_router.get("/download/{id}",
                    status_code=status.HTTP_200_OK)
@inject
async def download_file(id: str,
                        use_case: FromDishka[DownloadReportUseCase]):
    try:
        result: bytes = await use_case.execute(id)
        return Response(content=result, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

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


@reports_router.post("/generate-report",
                    status_code=status.HTTP_201_CREATED)
@inject
async def generate_report(payload: dict,
                    use_case: FromDishka[NewReportGenerateUseCase]):
    try:
        user_id = "1" # TODO переделать
        report_id = str(uuid.uuid4())
        message = ReportInputData(**payload, user_id=user_id, report_id=report_id)
        await use_case.execute(message=message)
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
async def report_ready_events(request: Request):
    user_id = "1"  # TODO получать user_id из авторизации

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
