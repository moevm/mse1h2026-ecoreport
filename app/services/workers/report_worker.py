import json
import logging
from app.infrastructure.rabbit.consumer import RabbitConsumer
from app.infrastructure.rabbit.topology import ReportsTopology
from app.services.report_flow import GenerateReportFlow

logger = logging.getLogger("uvicorn")

class ReportWorker:
    """
    Класс воркера для обработки сообщений о необходимости генерации отчета.
    """
    def __init__(self, consumer: RabbitConsumer, flow: GenerateReportFlow):
        """
        Инициализирует воркера.

        :param consumer: Потребитель RabbitMQ.
        :param flow: Поток генерации отчета (бизнес-логика).
        """
        self.consumer = consumer
        self.flow = flow

    async def run(self):
        """
        Запускает цикл обработки сообщений из очереди.
        """
        logger.info(f"Воркер {self.__class__.__name__} запущен")
        async for message in self.consumer.consume(ReportsTopology.GENERATE_QUEUE_NAME):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    report_id = payload.get("report_id")
                    if report_id:
                        await self.flow.execute(report_id)
                    else:
                        logger.error(f"Некорректный payload в {ReportsTopology.GENERATE_QUEUE_NAME}: {payload}")
                except Exception as e:
                    logger.exception(f"Ошибка при обработке сообщения: {e}")
