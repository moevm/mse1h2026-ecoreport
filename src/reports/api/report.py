import uuid

from dishka import FromDishka
from fastapi import APIRouter, Request, Response, UploadFile, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from dishka.integrations.fastapi import inject
import os

from reports.domain.use_cases.download_report import DownloadReportUseCase
from reports.domain.use_cases.generate_report import GenerateReportUseCase
from reports.domain.use_cases.new_report_generation import NewReportGenerateUseCase
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
async def documents_page(request: Request):
    context = {'request': request}
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
