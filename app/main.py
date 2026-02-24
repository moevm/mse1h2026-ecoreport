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

UPLOAD_DIR = "uploads"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="index.html", context=context)


@app.get("/download/{id}")
async def download_file(request: Request):
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
async def generate_report(file_id: str=Form(), example: str=Form()):
    return JSONResponse({"file_id":file_id, "example": example}, status_code=200)
