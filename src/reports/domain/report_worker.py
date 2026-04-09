from faststream.rabbit import RabbitQueue, RabbitExchange
import logging
from reports.core.config import settings
from reports.domain.use_cases.save_report import SaveDataUseCase
from reports.infrastructure.rabbitmq.broker import broker
from reports.infrastructure.websocket.report_notifications import report_notification_hub
from reports.schemas.report_models import ReportInputData, GeneratedReportData
from reports.domain.use_cases.generate_report import GenerateReportUseCase
from reports.core.providers.setup import container

exchange = RabbitExchange(name=settings.RABBITMQ_EXCHANGE)
new_gen_queue = RabbitQueue(name=settings.RABBITMQ_ROUTING_KEY_TO_GENERATION)
gen_queue = RabbitQueue(name=settings.RABBITMQ_ROUTING_KEY_GENERATED)

@broker.subscriber(new_gen_queue, exchange)
async def handle_new_request(msg: str):
    message = ReportInputData.model_validate_json(msg)
    async with container() as c:
        use_case = await c.get(GenerateReportUseCase)
        await use_case.execute(message)

@broker.subscriber(gen_queue, exchange)
async def handle_generated(msg: str):
    message = GeneratedReportData.model_validate_json(msg)
    async with container() as c:
        use_case = await c.get(SaveDataUseCase)
        await use_case.execute(message)

    await report_notification_hub.publish_report_ready(
        user_id=message.user_id,
        file_name=message.file_name,
    )
