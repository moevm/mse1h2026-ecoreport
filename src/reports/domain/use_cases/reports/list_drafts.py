from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import ReportsRepository, FileRepository
from reports.schemas.report_models import DraftSummary


class ListDraftsUseCase:
    def __init__(
        self,
        postgres_repository: ReportsRepository,
        database: Database,
        file_repository: FileRepository,
    ):
        self._postgres_repository = postgres_repository
        self._database = database
        self._file_repository = file_repository

    async def execute(self, user_id: int) -> list[DraftSummary]:
        async with self._database.session() as session:
            reports = await self._postgres_repository.list_drafts_by_user(user_id, session)
            result = []
            for report in reports:
                f = await self._file_repository.get_by_id(report.file_id, session)
                title = None
                full_object_name = None
                organization_name = None
                if f:
                    title = f.short_object_name or f.full_object_name
                    full_object_name = f.full_object_name
                    organization_name = f.organization_name
                result.append(DraftSummary(
                    file_id=report.file_id,
                    title=title,
                    full_object_name=full_object_name,
                    organization_name=organization_name,
                    last_modified=report.created_at,
                ))
            return result
