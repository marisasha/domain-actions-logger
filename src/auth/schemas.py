from datetime import datetime
from pydantic import BaseModel


class TokenSchema(BaseModel):
    access: str
    refresh: str


class UserSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    birth_date: datetime
    phone: str


class UserSchemaResponse(UserSchema):
    id: int


class UserSchemaRequest(UserSchema):
    password: str


class UserAuthorizationSchema(BaseModel):
    username: str
    password: str
