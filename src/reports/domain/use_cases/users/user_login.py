from pwdlib import PasswordHash

from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import UserRepository
from reports.schemas.api.user import LoginUserRequest
from reports.schemas.user_models import UserFullData


class UserLoginUseCase:
    def __init__(self, repository: UserRepository,
                 database: Database,
                 hasher: PasswordHash):
        self._repository = repository
        self._database = database
        self._hasher = hasher

    async def execute(self, payload: LoginUserRequest) -> UserFullData | None:
        async with self._database.session() as session:
            user_data = await self._repository.get_by_user_name(payload.user_name, session=session)

        if not user_data:
            return None

        is_valid_password = self._hasher.verify(payload.password, user_data.password_hash)

        if not is_valid_password:
            return None
        else:
            return user_data






