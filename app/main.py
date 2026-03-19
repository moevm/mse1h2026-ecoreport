from fastapi import FastAPI, Request, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import shutil
import os
import uuid

app: FastAPI = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates: Jinja2Templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="index.html", context=context)


@app.get("/create", response_class=HTMLResponse)
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
    return templates.TemplateResponse(name="create_report.html", context=context)


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="settings.html", context=context)


@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="documents.html", context=context)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="login.html", context=context)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="register.html", context=context)


@app.get("/download/{id}")
async def download_file(request: Request):
    '''
    Скачивание файла по id
    '''
    file_id = request.get('path_params')['id']
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(UPLOAD_DIR, filename)
            return FileResponse(
                path=file_path,
                filename=filename
            )
    raise HTTPException(status_code=404, detail="Файл не найден")


@app.post("/upload")
async def upload_file(file: UploadFile):
    '''
    Сюда загружается файл .csv или .xlsx с данными, на данный момент он просто сохраняется в отдельной папке.
    В будущем здесь будет обработка содержимого файла.
    '''
    try:
        file_id = uuid.uuid4()
        file_ext = os.path.splitext(file.filename)[1]
        file_new_name = f'{file_id}{file_ext}'
        file_path = os.path.join(UPLOAD_DIR,file_new_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return JSONResponse({
            "status": "success",
            "original_name": file.filename,
            "saved_as": file_new_name
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/generate-report")
async def generate_report(request: Request):
    '''Сюда будут отправляться данные формы для генерирования отчета'''
    return JSONResponse({"status": "success"}, status_code=200)
