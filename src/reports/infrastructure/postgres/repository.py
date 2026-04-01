from typing import Type
from reports.infrastructure.postgres.models import Report
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, values
from reports.schemas.report_models import GeneratedReportData

class ReportsRepository:
    _collection: Type[Report] = Report

    async def add_report(self, data: GeneratedReportData,
                        session: AsyncSession) -> None:
        values_data = data.model_dump()
        query = insert(self._collection).values(values_data)
        await session.execute(query)

    async def get_all_reports_id(self, user_id: str,
                                session: AsyncSession) -> list[str]:
        query = select(self._collection).where(self._collection.user_id == user_id)
        result = (await session.scalars(query)).all()
        return [obj.file_id for obj in result]

    async def get_latest_report_id(self, user_id: str,
                                session: AsyncSession) -> str:
        query = (select(self._collection)
                .where(self._collection.user_id == user_id)
                .order_by(self._collection.created_at.desc())
                .limit(1))
        result = (await session.execute(query)).one()
        return result.file_id