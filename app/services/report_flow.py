from app.infrastructure.storage.s3_client import S3Client
from app.infrastructure.rabbit.publisher import RabbitPublisher
from app.services.pdf_generator import PDFGenerator
import logging

ROUTING_KEY = "reports.generated"
logger = logging.getLogger("uvicorn")

class GenerateReportFlow:
    """
    Класс, реализующий бизнес-логику процесса генерации отчета.

    Включает в себя генерацию PDF, загрузку в S3 и уведомление о завершении.
    """
    def __init__(self, pdf_generator: PDFGenerator, s3_client: S3Client, publisher: RabbitPublisher):
        """
        Инициализирует поток генерации отчета.

        :param pdf_generator: Сервис генерации PDF.
        :param s3_client: Клиент для работы с S3-хранилищем.
        :param publisher: Издатель RabbitMQ для отправки уведомлений.
        """
        self.pdf_generator = pdf_generator
        self.s3_client = s3_client
        self.publisher = publisher

    async def execute(self, report_id: int):
        """
        Запускает выполнение процесса генерации отчета.

        :param report_id: Идентификатор отчета.
        """
        logger.info(f"Начинаю генерацию PDF для отчета {report_id}")
        pdf_content = await self.pdf_generator.generate_pdf(report_id) #TODO передавать данные для генерации
        
        filename = f"report_{report_id}.pdf"
        s3_url = await self.s3_client.upload(pdf_content, filename)
        logger.info(f"Отчет {report_id} загружен в S3: {s3_url}")

        await self.publisher.publish_direct(
            routing_key=ROUTING_KEY,
            body={"report_id": report_id, "s3_url": s3_url}
        )
        logger.info(f"Событие reports.generated опубликовано для отчета {report_id}")
