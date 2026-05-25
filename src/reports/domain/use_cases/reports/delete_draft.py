from sqlalchemy import delete
from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository
)
from reports.infrastructure.postgres.models import Report


class DeleteDraftUseCase:
    def __init__(
        self,
        postgres_repository: ReportsRepository,
        database: Database,
        file_repository: FileRepository,
        documents_gost_repository: DocumentsGostRepository,
        test_results_repository: TestResultsRepository,
        observation_point_repository: ObservationPointRepository,
        observation_dynamic_repository: ObservationDynamicRepository,
    ):
        self._postgres_repository = postgres_repository
        self._database = database
        self._file_repository = file_repository
        self._documents_gost_repository = documents_gost_repository
        self._test_results_repository = test_results_repository
        self._observation_point_repository = observation_point_repository
        self._observation_dynamic_repository = observation_dynamic_repository

    async def execute(self, file_id: int, user_id: int) -> None:
        async with self._database.session() as session:
            try:
                draft = await self._postgres_repository.get_draft_by_file_id(file_id, user_id, session)
                if not draft:
                    raise ValueError(f"Draft with file_id={file_id} not found for user {user_id}")

                existing_file = await self._file_repository.get_by_id(file_id, session)
                if not existing_file:
                    raise ValueError(f"File with id={file_id} not found")

                query = delete(Report).where(Report.file_id == file_id)
                await session.execute(query)

                await self._observation_dynamic_repository.delete_by_file_id(file_id, session)
                await self._observation_point_repository.delete_by_file_id(file_id, session)

                await self._file_repository.delete(file_id, session)

                if existing_file.gost_id:
                    await self._documents_gost_repository.delete(existing_file.gost_id, session)
                if existing_file.test_results_id:
                    await self._test_results_repository.delete(existing_file.test_results_id, session)

                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
