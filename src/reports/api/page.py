import os
from datetime import timezone, timedelta
from os.path import splitext
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from reports.api.dependencies import validate_jwt
from reports.core.config import settings
from reports.infrastructure.minio.repository import MinioRepository
from reports.schemas.user_models import UserPayload

page_router = APIRouter()

templates: Jinja2Templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "templates"))

@page_router.get("/", response_class=HTMLResponse)
async def index(request: Request,
                auth: UserPayload = Depends(validate_jwt)):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@page_router.get("/create", response_class=HTMLResponse)
async def create_report(request: Request,
                        auth: UserPayload = Depends(validate_jwt)):
    context = {
        'request': request,
        'osm_tile_url': settings.OSM_TILE_URL,
        'osm_attribution': settings.OSM_ATTRIBUTION,
        'leaflet_js_url': settings.LEAFLET_JS_URL,
        'leaflet_js_integrity': settings.LEAFLET_JS_INTEGRITY,
        'leaflet_js_crossorigin': settings.LEAFLET_JS_CROSSORIGIN,
        'leaflet_css_url': settings.LEAFLET_CSS_URL,
        'leaflet_css_integrity': settings.LEAFLET_CSS_INTEGRITY,
        'leaflet_css_crossorigin': settings.LEAFLET_CSS_CROSSORIGIN,
    }
    return templates.TemplateResponse(request=request, name="create_report.html", context=context)


@page_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request,
                        auth: UserPayload = Depends(validate_jwt)):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="settings.html", context=context)


@page_router.get("/documents", response_class=HTMLResponse)
@inject
async def documents_page(request: Request,
                         repository: FromDishka[MinioRepository],
                         auth: UserPayload = Depends(validate_jwt)):
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


@page_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="login.html", context=context)


@page_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(request=request, name="register.html", context=context)

