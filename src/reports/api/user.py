from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response
from starlette import status
from starlette.exceptions import HTTPException

from reports.domain.use_cases.users.user_login import UserLoginUseCase
from reports.domain.use_cases.users.user_registration import UserRegistrationUseCase
from reports.schemas.api.user import CreateUserRequest, CreateUserResponse, LoginUserRequest, LoginUserResponse
from reports.domain.jwt_generator import create_token

user_router = APIRouter(prefix="/user")


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def user_registration(request: CreateUserRequest, use_case: FromDishka[UserRegistrationUseCase]):
    try:
        result = await use_case.execute(request)
        return CreateUserResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.post("/login", status_code=status.HTTP_200_OK)
@inject
async def user_login(request: LoginUserRequest,
                     response: Response,
                     use_case: FromDishka[UserLoginUseCase]):
    try:
        result = await use_case.execute(request)
        if result:
            token = create_token(result)
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                samesite="lax",
                path="/",
            )
            return LoginUserResponse(**result.model_dump(), token=token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")










