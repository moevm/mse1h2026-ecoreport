from faststream.rabbit import RabbitBroker
from reports.schemas.report_models import ReportInputData, GeneratedReportData
from reports.core.config import settings

class RabbitPublisher:
    def __init__(self, broker: RabbitBroker):
        self._broker = broker

    async def publish_new_generate_message(self, message: ReportInputData):
        await self._broker.publish(message=message.model_dump_json(),
                                    exchange=settings.RABBITMQ_EXCHANGE,
                                    routing_key=settings.RABBITMQ_ROUTING_KEY_TO_GENERATION)

    async def publish_generated_message(self, message: GeneratedReportData):
        await self._broker.publish(message=message.model_dump_json(),
                                    exchange=settings.RABBITMQ_EXCHANGE,
                                    routing_key=settings.RABBITMQ_ROUTING_KEY_GENERATED)