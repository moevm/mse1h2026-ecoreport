from reports.domain.generator_utils.report_generator.report_generator import ReportGenerator
from reports.domain.generator_utils.report_generator.docx_generator import DocxGenerator
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.rabbitmq.publisher import RabbitPublisher
from reports.schemas.report_models import ReportInputData, GeneratedReportData

class GenerateReportUseCase:
    def __init__(self,
                    publisher: RabbitPublisher,
                    generator: ReportGenerator,
                    docx_generator: DocxGenerator,
                    repository: MinioRepository):
        self._publisher = publisher
        self._generator = generator
        self._docx_generator = docx_generator
        self._repository = repository

    async def execute(self, message: ReportInputData):
        data_dict = message.model_dump()
        
        # Генератор PDF
        pdf_bytes = self._generator.generate(data_dict)
        pdf_object_name = self._repository.put_object(
            obj_id=message.report_id,
            obj=pdf_bytes,
            file_type="pdf"
        )
        await self._publisher.publish_generated_message(
            GeneratedReportData(user_id=message.user_id, file_name=pdf_object_name)
        )
        
        # Генератор DOCX
        try:
            docx_bytes = self._docx_generator.generate(data_dict)
            docx_object_name = self._repository.put_object(
                obj_id=message.report_id,
                obj=docx_bytes,
                file_type="docx"
            )
            await self._publisher.publish_generated_message(
                GeneratedReportData(user_id=message.user_id, file_name=docx_object_name)
            )
        except Exception:
            pass