from dishka import make_async_container, Provider, provide, Scope
from faststream.rabbit import RabbitBroker
from minio import Minio
from pwdlib import PasswordHash

from reports.core.config import settings
from reports.domain.use_cases.reports.download_report import DownloadReportUseCase
from reports.domain.use_cases.reports.generate_report import GenerateReportUseCase
from reports.domain.use_cases.reports.new_report_generation import NewReportGenerateUseCase
from reports.domain.use_cases.reports.save_report import SaveDataUseCase
from reports.domain.use_cases.reports.update_report import UpdateDataUseCase
from reports.domain.use_cases.reports.delete_report import DeleteDataUseCase
from reports.domain.use_cases.reports.save_draft import SaveDraftUseCase
from reports.domain.use_cases.reports.update_draft import UpdateDraftUseCase
from reports.domain.use_cases.reports.delete_draft import DeleteDraftUseCase
from reports.domain.use_cases.reports.get_draft import GetDraftUseCase
from reports.domain.use_cases.reports.list_drafts import ListDraftsUseCase
from reports.domain.use_cases.users.user_login import UserLoginUseCase
from reports.domain.use_cases.users.user_registration import UserRegistrationUseCase
from reports.infrastructure.minio.repository import MinioRepository
from reports.infrastructure.minio.client import MinioClient
from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository, UserRepository
)
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
    def get_reports_repository(self) -> ReportsRepository:
        return ReportsRepository()

    @provide
    def get_users_repository(self) -> UserRepository:
        return UserRepository()

    @provide
    def get_file_repository(self) -> FileRepository:
        return FileRepository()

    @provide
    def get_documents_gost_repository(self) -> DocumentsGostRepository:
        return DocumentsGostRepository()

    @provide
    def get_test_results_repository(self) -> TestResultsRepository:
        return TestResultsRepository()

    @provide
    def get_observation_point_repository(self) -> ObservationPointRepository:
        return ObservationPointRepository()

    @provide
    def get_observation_dynamic_repository(self) -> ObservationDynamicRepository:
        return ObservationDynamicRepository()

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

    @provide
    def get_password_hasher(self) -> PasswordHash:
        return PasswordHash.recommended()


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
    def get_save_data_use_case(self,
                               postgres_repository: ReportsRepository,
                               database: Database,
                               file_repository: FileRepository,
                               documents_gost_repository: DocumentsGostRepository,
                               test_results_repository: TestResultsRepository,
                               observation_point_repository: ObservationPointRepository,
                               observation_dynamic_repository: ObservationDynamicRepository) -> SaveDataUseCase:
        return SaveDataUseCase(
            postgres_repository, database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_update_data_use_case(self,
                                 database: Database,
                                 file_repository: FileRepository,
                                 documents_gost_repository: DocumentsGostRepository,
                                 test_results_repository: TestResultsRepository,
                                 observation_point_repository: ObservationPointRepository,
                                 observation_dynamic_repository: ObservationDynamicRepository) -> UpdateDataUseCase:
        return UpdateDataUseCase(
            database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_delete_data_use_case(self,
                                 database: Database,
                                 file_repository: FileRepository,
                                 documents_gost_repository: DocumentsGostRepository,
                                 test_results_repository: TestResultsRepository,
                                 observation_point_repository: ObservationPointRepository,
                                 observation_dynamic_repository: ObservationDynamicRepository) -> DeleteDataUseCase:
        return DeleteDataUseCase(
            database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_download_report_use_case(self, repository: MinioRepository) -> DownloadReportUseCase:
        return DownloadReportUseCase(repository)

    @provide
    def get_save_draft_use_case(self,
                                postgres_repository: ReportsRepository,
                                database: Database,
                                file_repository: FileRepository,
                                documents_gost_repository: DocumentsGostRepository,
                                test_results_repository: TestResultsRepository,
                                observation_point_repository: ObservationPointRepository,
                                observation_dynamic_repository: ObservationDynamicRepository) -> SaveDraftUseCase:
        return SaveDraftUseCase(
            postgres_repository, database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_update_draft_use_case(self,
                                  postgres_repository: ReportsRepository,
                                  database: Database,
                                  file_repository: FileRepository,
                                  documents_gost_repository: DocumentsGostRepository,
                                  test_results_repository: TestResultsRepository,
                                  observation_point_repository: ObservationPointRepository,
                                  observation_dynamic_repository: ObservationDynamicRepository) -> UpdateDraftUseCase:
        return UpdateDraftUseCase(
            postgres_repository, database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_delete_draft_use_case(self,
                                  postgres_repository: ReportsRepository,
                                  database: Database,
                                  file_repository: FileRepository,
                                  documents_gost_repository: DocumentsGostRepository,
                                  test_results_repository: TestResultsRepository,
                                  observation_point_repository: ObservationPointRepository,
                                  observation_dynamic_repository: ObservationDynamicRepository) -> DeleteDraftUseCase:
        return DeleteDraftUseCase(
            postgres_repository, database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_get_draft_use_case(self,
                               postgres_repository: ReportsRepository,
                               database: Database,
                               file_repository: FileRepository,
                               documents_gost_repository: DocumentsGostRepository,
                               test_results_repository: TestResultsRepository,
                               observation_point_repository: ObservationPointRepository,
                               observation_dynamic_repository: ObservationDynamicRepository) -> GetDraftUseCase:
        return GetDraftUseCase(
            postgres_repository, database, file_repository, documents_gost_repository,
            test_results_repository, observation_point_repository, observation_dynamic_repository
        )

    @provide
    def get_list_drafts_use_case(self,
                                 postgres_repository: ReportsRepository,
                                 database: Database,
                                 file_repository: FileRepository) -> ListDraftsUseCase:
        return ListDraftsUseCase(postgres_repository, database, file_repository)

    @provide
    def create_user_use_case(self,
                             repository: UserRepository,
                             database: Database,
                             hasher: PasswordHash) -> UserRegistrationUseCase:
        return UserRegistrationUseCase(repository, database, hasher)

    @provide
    def login_user_use_case(self,
                            repository: UserRepository,
                            database: Database,
                            hasher: PasswordHash) -> UserLoginUseCase:
        return UserLoginUseCase(repository, database, hasher)


container = make_async_container(InfrastructureProvider(), RepositoryProvider(), ServiceProvider(), UseCaseProvider())