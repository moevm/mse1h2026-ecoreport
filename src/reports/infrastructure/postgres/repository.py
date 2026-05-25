from typing import Type, Optional
from reports.infrastructure.postgres.models import (
    Report, User, File, DocumentsGost, ObservationPoint, TestResults, ObservationDynamic
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from reports.schemas.report_models import (
    ReportCreate,
    FileCreate, FileUpdate,
    DocumentsGostCreate, DocumentsGostUpdate,
    ObservationPointCreate, ObservationPointUpdate,
    TestResultsCreate, TestResultsUpdate,
    ObservationDynamicCreate, ObservationDynamicUpdate
)
from reports.schemas.user_models import UserCreate, UserUpdate, UserCreated, UserUpdated, UserFullData


class ReportsRepository:
    _collection: Type[Report] = Report

    async def add_report(self, data: ReportCreate, session: AsyncSession) -> None:
        query = insert(self._collection).values(**data.model_dump())
        await session.execute(query)

    async def get_all_reports_id(self, user_id: str, session: AsyncSession) -> list[str]:
        query = select(self._collection).where(self._collection.user_id == user_id)
        result = (await session.scalars(query)).all()
        return [obj.file_id for obj in result]

    async def get_latest_report_id(self, user_id: str, session: AsyncSession) -> str:
        query = (select(self._collection)
                .where(self._collection.user_id == user_id)
                .order_by(self._collection.created_at.desc())
                .limit(1))
        result = (await session.execute(query)).one()
        return result.file_id

    async def list_drafts_by_user(self, user_id: int, session: AsyncSession) -> list[Report]:
        query = (select(self._collection)
                 .where(self._collection.user_id == user_id, self._collection.is_draft == True)
                 .order_by(self._collection.created_at.desc()))
        result = (await session.scalars(query)).all()
        return list(result)

    async def get_draft_by_file_id(self, file_id: int, user_id: int, session: AsyncSession) -> Optional[Report]:
        query = select(self._collection).where(
            self._collection.file_id == file_id,
            self._collection.user_id == user_id,
            self._collection.is_draft == True
        )
        return (await session.scalars(query)).first()

    async def mark_as_final(self, file_id: int, user_id: int, session: AsyncSession) -> None:
        query = (update(self._collection)
                 .where(self._collection.file_id == file_id, self._collection.user_id == user_id)
                 .values(is_draft=False))
        await session.execute(query)


class UserRepository:
    _collection: Type[User] = User

    async def add(self, data: UserCreate, session: AsyncSession) -> UserCreated:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection)
        result = await session.execute(query)
        return UserCreated.model_validate(result.scalar_one())

    async def get_by_id(self, record_id: int, session: AsyncSession) -> UserFullData | None:
        query = select(self._collection).where(self._collection.id == record_id)
        result = (await session.execute(query)).scalar_one_or_none()
        return UserFullData.model_validate(result) if result else None

    async def get_by_user_name(self, user_name: str, session: AsyncSession) -> UserFullData | None:
        query = select(self._collection).where(self._collection.user_name == user_name)
        result = (await session.execute(query)).scalar_one_or_none()
        return UserFullData.model_validate(result) if result else None

    async def update(self, record_id: int, data: UserUpdate, session: AsyncSession) -> UserUpdated:
        query = (update(self._collection).where(self._collection.id == record_id)
                 .values(**data.model_dump(exclude_unset=True)).returning(self._collection))
        result = await session.execute(query)
        return UserUpdated.model_validate(result.scalar_one())

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)


class DocumentsGostRepository:
    _collection: Type[DocumentsGost] = DocumentsGost

    async def add(self, data: DocumentsGostCreate, session: AsyncSession) -> int:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection.id)
        result = await session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, record_id: int, session: AsyncSession) -> Optional[DocumentsGost]:
        query = select(self._collection).where(self._collection.id == record_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, record_id: int, data: DocumentsGostUpdate, session: AsyncSession) -> None:
        query = update(self._collection).where(self._collection.id == record_id).values(**data.model_dump(exclude_unset=True))
        await session.execute(query)

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)


class ObservationPointRepository:
    _collection: Type[ObservationPoint] = ObservationPoint

    async def add(self, data: ObservationPointCreate, session: AsyncSession) -> int:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection.id)
        result = await session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, record_id: int, session: AsyncSession) -> Optional[ObservationPoint]:
        query = select(self._collection).where(self._collection.id == record_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, record_id: int, data: ObservationPointUpdate, session: AsyncSession) -> None:
        query = update(self._collection).where(self._collection.id == record_id).values(**data.model_dump(exclude_unset=True))
        await session.execute(query)

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)

    async def delete_by_file_id(self, file_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.file_id == file_id)
        await session.execute(query)

    async def list_by_file_id(self, file_id: int, session: AsyncSession) -> list[ObservationPoint]:
        query = select(self._collection).where(self._collection.file_id == file_id)
        result = (await session.scalars(query)).all()
        return list(result)


class TestResultsRepository:
    _collection: Type[TestResults] = TestResults

    async def add(self, data: TestResultsCreate, session: AsyncSession) -> int:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection.id)
        result = await session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, record_id: int, session: AsyncSession) -> Optional[TestResults]:
        query = select(self._collection).where(self._collection.id == record_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, record_id: int, data: TestResultsUpdate, session: AsyncSession) -> None:
        query = update(self._collection).where(self._collection.id == record_id).values(**data.model_dump(exclude_unset=True))
        await session.execute(query)

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)


class ObservationDynamicRepository:
    _collection: Type[ObservationDynamic] = ObservationDynamic

    async def add(self, data: ObservationDynamicCreate, session: AsyncSession) -> int:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection.id)
        result = await session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, record_id: int, session: AsyncSession) -> Optional[ObservationDynamic]:
        query = select(self._collection).where(self._collection.id == record_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, record_id: int, data: ObservationDynamicUpdate, session: AsyncSession) -> None:
        query = update(self._collection).where(self._collection.id == record_id).values(**data.model_dump(exclude_unset=True))
        await session.execute(query)

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)

    async def delete_by_file_id(self, file_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.file_id == file_id)
        await session.execute(query)

    async def list_by_file_id(self, file_id: int, session: AsyncSession) -> list[ObservationDynamic]:
        query = select(self._collection).where(self._collection.file_id == file_id)
        result = (await session.scalars(query)).all()
        return list(result)


class FileRepository:
    _collection: Type[File] = File

    async def add(self, data: FileCreate, session: AsyncSession) -> int:
        query = insert(self._collection).values(**data.model_dump(exclude_unset=True)).returning(self._collection.id)
        result = await session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, record_id: int, session: AsyncSession) -> Optional[File]:
        query = select(self._collection).where(self._collection.id == record_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, record_id: int, data: FileUpdate, session: AsyncSession) -> None:
        query = update(self._collection).where(self._collection.id == record_id).values(**data.model_dump(exclude_unset=True))
        await session.execute(query)

    async def delete(self, record_id: int, session: AsyncSession) -> None:
        query = delete(self._collection).where(self._collection.id == record_id)
        await session.execute(query)