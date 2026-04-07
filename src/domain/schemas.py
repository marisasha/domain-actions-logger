from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from src.user.schemas import UserProfileSchema
from src.utils import PermissionEnum, GenderEnum


# =- Domain Model-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-
class DomainSchema(BaseModel):
    name: str
    registration_date: datetime
    expiry_date: datetime
    status: str
    registration_certificate_url: str | None


class DomainSchemaResponse(DomainSchema):
    id: int


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
    domain_name: str
    user_first_name: str
    user_last_name: str


class PermissionChangeSchema(BaseModel):
    permission: PermissionEnum


class DomainPermissionSchema(BaseModel):
    domain_name: str
    permission: PermissionEnum
    permission_give_date: datetime
    last_used_date: datetime


class UserPermissionSchema(BaseModel):
    first_name: str
    last_name: str
    permission: PermissionEnum
    permission_give_date: datetime
    last_used_date: datetime


class UserDomainsResponse(BaseModel):
    user: Optional[UserProfileSchema]
    domains: List[DomainPermissionSchema]


class DomainUsersResponse(BaseModel):
    domain: Optional[DomainProfileSchema]
    users: List[UserPermissionSchema]


# =- Message Response -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class MessageSchemaResponse(BaseModel):
    message: str
