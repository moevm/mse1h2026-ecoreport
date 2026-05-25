from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status
from reports.core.config import settings
from jose import jwt, JWTError

from reports.schemas.user_models import UserPayload

bearer_scheme = HTTPBearer()

async def validate_jwt(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> UserPayload:
    token = credentials.credentials
    try:
        data = jwt.decode(token, key=settings.SECRET.get_secret_value(), algorithms=[settings.ALGORITHM])
        return UserPayload.model_validate(data)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)



