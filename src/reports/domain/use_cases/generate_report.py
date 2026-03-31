from reports.domain.generator_utils.report_generator.report_generator import ReportGenerator
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.rabbitmq.publisher import RabbitPublisher
from reports.schemas.report_models import ReportInputData, GeneratedReportData


class GenerateReportUseCase:
    def __init__(self,
                 publisher: RabbitPublisher,
                 generator: ReportGenerator,
                 repository: MinioRepository):
        self._publisher = publisher
        self._generator = generator
        self._repository = repository

    async def execute(self, message: ReportInputData):
        bytes_data = self._generator.generate(message.model_dump()) # TODO await
        object_name = self._repository.put_object(obj_id=message.report_id, obj=bytes_data)
        await self._publisher.publish_generated_message(GeneratedReportData(user_id=message.user_id,
                                                                            file_name=object_name))
