from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import UserRepository
from reports.schemas.api.user import CreateUserRequest
from reports.schemas.user_models import UserCreate, UserCreated
from pwdlib import PasswordHash


class UserRegistrationUseCase:
    def __init__(self, repository: UserRepository,
                 database: Database,
                 password_hasher: PasswordHash):
        self._repository = repository
        self._database = database
        self._hasher = password_hasher

    async def execute(self, payload: CreateUserRequest) -> UserCreated:
        password_hash = self._hasher.hash(payload.password)
        data = UserCreate(password_hash=password_hash, **payload.model_dump())
        async with self._database.session() as session:
            result = await self._repository.add(data, session=session)

        return result





