from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import ReportsRepository
from reports.schemas.report_models import GeneratedReportData


class SaveDataUseCase:
    def __init__(self, postgres_repository: ReportsRepository, database: Database):
        self._postgres_repository = postgres_repository
        self._database = database

    async def execute(self, data: GeneratedReportData):
        async with self._database.session() as session:
            await self._postgres_repository.add_report(data, session)
