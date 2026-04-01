from reports.infrastructure.rabbitmq.publisher import RabbitPublisher
from reports.schemas.report_models import ReportInputData


class NewReportGenerateUseCase:
    def __init__(self, publisher: RabbitPublisher):
        self._publisher = publisher

    async def execute(self, message: ReportInputData):
        await self._publisher.publish_new_generate_message(message)