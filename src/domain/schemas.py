from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from src.auth.schemas import UserProfileSchema
from src.utils import PermissionEnum


# =- Owner Model -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class OwnerDomainSchema(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: str
    phone: str

    birth_date: datetime
    birth_place: str

    passport_from: str
    passport_number: str
    passport_series: int | None

    issue_date: datetime
    expiry_date: datetime | None

    department_code: str | None
    issue_by: str


class OwnerDomainSchemaResponse(OwnerDomainSchema):
    id: int


# =- Domain Model-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-
class DomainSchema(BaseModel):
    owner_id: int
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


# =- Owner Domain Model-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class OwnerWithDomainSchema(DomainSchemaResponse):
    owner_first_name: str
    owner_last_name: str


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
