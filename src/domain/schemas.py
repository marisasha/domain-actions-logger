from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.user.schemas import UserProfileSchema
from src.utils.enum import PermissionEnum, GenderEnum, MoveEnum


# =- Domain Model-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-
class DomainSchema(BaseModel):
    name: str
    registration_date: datetime
    expiry_date: datetime
    status: str
    registration_certificate_url: str | None


class DomainSchemaResponse(DomainSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DomainProfileSchema(BaseModel):
    id: int
    name: str


# =- User Domain Model -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-
class UserDomainSchema(BaseModel):
    permission: PermissionEnum
    permission_give_date: datetime
    last_used_date: datetime | None


class UserDomainIDSchema(UserDomainSchema):
    user_id: int
    domain_id: int


class UserDomainSchemaResponse(UserDomainSchema):
    user_domain_id: int
    domain_name: str
    user_first_name: str
    user_last_name: str


class PermissionChangeSchema(BaseModel):
    user_id: int
    domain_id: int
    permission: PermissionEnum


class DomainPermissionSchema(UserDomainSchema):
    user_domain_id: int
    domain_name: str


class UserPermissionSchema(UserDomainSchema):
    user_domain_id: int
    first_name: str
    last_name: str


class UserDomainsPermissionResponse(BaseModel):
    user: Optional[UserProfileSchema]
    domains: List[DomainPermissionSchema]


class DomainUsersPermissionResponse(BaseModel):
    domain: Optional[DomainProfileSchema]
    users: List[UserPermissionSchema]


# =- Move Schema -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class MoveSchema(BaseModel):
    user_domain_id: int
    type: MoveEnum
    description: str
    date: datetime


class MoveSchemaResponse(MoveSchema):
    id: int


class UserMoveSchema(MoveSchema):
    first_name: str
    last_name: str


class DomainUsersMovesResponse(BaseModel):
    domain: Optional[DomainProfileSchema]
    moves: List[UserMoveSchema]


# =- Message Response -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class MessageSchemaResponse(BaseModel):
    message: str
