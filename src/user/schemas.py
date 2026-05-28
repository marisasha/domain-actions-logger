from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.utils import GenderEnum


class UserSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    gender: GenderEnum
    email: Optional[str] = None
    birth_date: datetime
    phone: str

    model_config = {"from_attributes": True}


class UserSchemaResponse(UserSchema):
    id: int


class UserChangeDataSchema(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[datetime] = None
    phone: Optional[str] = None


class UserSchemaRequest(UserSchema):
    password: str


class UserProfileSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class MessageSchemaResponse(BaseModel):
    message: str
