from jose import jwt
from datetime import datetime, timedelta, timezone

from reports.schemas.user_models import UserBase
from reports.core.config import settings


def create_token(data: UserBase) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {
        "user_id": data.user_id,
        "user_name": data.user_name,
        "exp": expire_at
    }

    return jwt.encode(payload, settings.SECRET.get_secret_value(), algorithm=settings.ALGORITHM)



