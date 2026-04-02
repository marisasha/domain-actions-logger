from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from src.auth.schemas import UserProfileSchema


# =- Owner domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
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


# =- Domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-
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


# =- Owner Domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class OwnerWithDomainSchema(DomainSchemaResponse):
    owner_first_name: str
    owner_last_name: str


# =- User Domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-
class UserDomainSchema(BaseModel):
    user_id: int
    domain_id: int
    permission: str
    permission_give_date: datetime
    last_used_date: datetime | None


class DomainPermissionSchema(BaseModel):
    domain_name: str
    permission: str
    permission_give_date: datetime
    last_used_date: datetime


class UserPermissionSchema(BaseModel):
    first_name: str
    last_name: str
    permission: str
    permission_give_date: datetime
    last_used_date: datetime


class UserDomainsResponse(BaseModel):
    user: Optional[UserProfileSchema]
    domains: List[DomainPermissionSchema]


class DomainUsersResponse(BaseModel):
    domain: Optional[DomainProfileSchema]
    users: List[UserPermissionSchema]
