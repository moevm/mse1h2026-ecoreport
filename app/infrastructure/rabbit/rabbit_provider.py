import aio_pika
from typing import AsyncIterator
from dishka import Provider, Scope
from app.infrastructure.rabbit.connection import RabbitConnectionManager
from app.infrastructure.rabbit.consumer import RabbitConsumer
from app.infrastructure.rabbit.publisher import RabbitPublisher
from app.infrastructure.rabbit.topology import ReportsTopology
from app.infrastructure.storage.s3_client import S3Client
from app.services.pdf_generator import PDFGenerator
from app.services.report_flow import GenerateReportFlow
from app.services.workers.report_worker import ReportWorker
from app.services.workers.manager import WorkerManager

rabbit_provider = Provider(scope=Scope.APP)

@rabbit_provider.provide
async def provide_connection_manager() -> AsyncIterator[RabbitConnectionManager]:
    connection_manager = RabbitConnectionManager()
    await connection_manager.connect()
    yield connection_manager
    await connection_manager.close()

@rabbit_provider.provide
async def provide_exchange(manager: RabbitConnectionManager) -> aio_pika.abc.AbstractRobustExchange:
    channel = await manager.get_channel()
    return await ReportsTopology.setup(channel)

@rabbit_provider.provide
async def provide_publisher(exchange: aio_pika.abc.AbstractRobustExchange) -> RabbitPublisher:
    return RabbitPublisher(exchange=exchange)

@rabbit_provider.provide
async def provide_consumer(manager: RabbitConnectionManager) -> RabbitConsumer:
    channel = await manager.get_channel()
    return RabbitConsumer(channel=channel)

@rabbit_provider.provide
async def provide_s3_client() -> S3Client:
    return S3Client()

@rabbit_provider.provide
async def provide_pdf_generator() -> PDFGenerator:
    return PDFGenerator()

@rabbit_provider.provide
async def provide_report_flow(pdf_generator: PDFGenerator, s3_client: S3Client,
                              publisher: RabbitPublisher) -> GenerateReportFlow:
    return GenerateReportFlow(pdf_generator, s3_client, publisher)

@rabbit_provider.provide
async def provide_report_worker(consumer: RabbitConsumer, flow: GenerateReportFlow) -> ReportWorker:
    return ReportWorker(consumer, flow)

@rabbit_provider.provide
async def provide_worker_manager(report_worker: ReportWorker) -> WorkerManager:
    return WorkerManager([report_worker])
