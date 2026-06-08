from datetime import datetime
from pydantic import BaseModel

from src.utils.enum import GenderEnum


class TokenSchema(BaseModel):
    access: str
    refresh: str


class UserAuthorizationSchema(BaseModel):
    username: str
    password: str


class CurrentUserSchema(BaseModel):
    id: int
    role: str
