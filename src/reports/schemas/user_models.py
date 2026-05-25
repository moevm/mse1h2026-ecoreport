from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserPayload(BaseModel):
    user_id: int
    user_name: str

class UserBase(BaseModel):
    user_name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UserCreate(UserBase):
    password_hash: str

class UserCreated(UserBase):
    user_id: int = Field(validation_alias="id")
    password_hash: str
    created_at: datetime

class UserUpdate(UserBase):
    image_path: str | None
    user_name: str | None
    password: str | None

class UserUpdated(UserBase):
    user_id: int = Field(validation_alias="id")
    image_path: str
    password_hash: str
    updated_at: datetime

class UserFullData(UserBase):
    user_id: int = Field(validation_alias="id")
    password_hash: str
    image_path: str | None
    created_at: datetime
    updated_at: datetime


