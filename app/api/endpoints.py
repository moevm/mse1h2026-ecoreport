from fastapi import APIRouter, Request
from dishka.integrations.fastapi import inject, FromDishka
from fastapi.templating import Jinja2Templates
from app.infrastructure.rabbit.publisher import RabbitPublisher


ROUTING_KEY = "reports.generate"

router = APIRouter()


@router.get("/")
async def index(request: Request):
    """
    Отображает главную страницу приложения.

    :param request: Объект запроса FastAPI.
    :return: Ответ с отрендеренным шаблоном index.html.
    """
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate-report")
@inject
async def generate_report(report_id: int, publisher: FromDishka[RabbitPublisher]):
    """
    Эндпоинт для запуска процесса генерации отчета.
    Отправляет сообщение в очередь RabbitMQ.

    :param report_id: Идентификатор отчета для генерации.
    :param publisher: Издатель RabbitMQ (внедряется через Dishka).
    :return: Dict со статусом постановки в очередь.
    """
    await publisher.publish_direct(routing_key=ROUTING_KEY, body={"report_id": report_id})
    return {"status": "queued"}
