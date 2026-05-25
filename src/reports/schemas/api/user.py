from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CreateUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    user_name: str
    created_at: datetime

class CreateUserRequest(BaseModel):
    user_name: str
    password: str

class LoginUserResponse(CreateUserResponse):
    token: str

class LoginUserRequest(CreateUserRequest):
    pass

