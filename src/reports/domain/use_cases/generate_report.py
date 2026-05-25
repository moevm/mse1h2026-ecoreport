from reports.domain.generator_utils.report_generator.report_generator import ReportGenerator
from reports.domain.generator_utils.geo_export import generate_report_geojson
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
        data = message.model_dump()
        bytes_data = self._generator.generate(data) # TODO await
        object_name = self._repository.put_object(obj_id=message.report_id, obj=bytes_data)

        geojson_str = generate_report_geojson(data)
        geojson_name = self._repository.put_geojson(obj_id=message.report_id, obj=geojson_str.encode("utf-8"))

        await self._publisher.publish_generated_message(GeneratedReportData(user_id=message.user_id, file_name=object_name))