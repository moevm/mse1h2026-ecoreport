from dishka import make_async_container, Provider, provide, Scope
from faststream.rabbit import RabbitBroker
from minio import Minio

from reports.core.config import settings
from reports.domain.use_cases.download_report import DownloadReportUseCase
from reports.domain.use_cases.generate_report import GenerateReportUseCase
from reports.domain.use_cases.new_report_generation import NewReportGenerateUseCase
from reports.domain.use_cases.save_report import SaveDataUseCase
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.minio.client import MinioClient
from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import ReportsRepository
from reports.infrastructure.rabbitmq.broker import broker
from reports.infrastructure.rabbitmq.publisher import RabbitPublisher
from reports.domain.generator_utils.report_generator.report_generator import ReportGenerator


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide
    def get_rabbit_broker(self) -> RabbitBroker:
        return broker

    @provide
    def get_database(self) -> Database:
        return Database(settings.postgres_url)

    @provide
    def get_minio_raw_client(self) -> Minio:
        endpoint = f"{settings.MINIO_HOST}:{settings.MINIO_PORT}"
        return Minio(endpoint,
                     access_key=settings.MINIO_ROOT_USER.get_secret_value(),
                     secret_key=settings.MINIO_ROOT_PASSWORD.get_secret_value(),
                     secure=False)

    @provide
    def get_minio_client(self, client: Minio) -> MinioClient:
        return MinioClient(client)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_postgres_repository(self) -> ReportsRepository:
        return ReportsRepository()

    @provide
    def get_minio_repository(self, client: Minio) -> MinioRepository:
        return MinioRepository(client)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_rabbit_publisher(self, rabbit_broker: RabbitBroker) -> RabbitPublisher:
        return RabbitPublisher(rabbit_broker)

    @provide
    def get_report_generator(self) -> ReportGenerator:
        return ReportGenerator()


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_new_generate_report_use_case(self, publisher: RabbitPublisher) -> NewReportGenerateUseCase:
        return NewReportGenerateUseCase(publisher)

    @provide
    def get_generate_report_use_case(self, publisher: RabbitPublisher,
                                     generator: ReportGenerator,
                                     repository: MinioRepository) -> GenerateReportUseCase:
        return GenerateReportUseCase(publisher, generator, repository)

    @provide
    def get_save_data_use_case(self, repository: ReportsRepository,
                                 database: Database) -> SaveDataUseCase:
        return SaveDataUseCase(repository, database)

    @provide
    def get_download_report_use_case(self, repository: MinioRepository) -> DownloadReportUseCase:
        return DownloadReportUseCase(repository)


container = make_async_container(InfrastructureProvider(),
                                 RepositoryProvider(),
                                 ServiceProvider(),
                                 UseCaseProvider())
