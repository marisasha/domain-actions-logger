from datetime import datetime
from pydantic import BaseModel


# =- Owner domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
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


# =- Owner Domain -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-


class OwnerWithDomainSchema(DomainSchemaResponse):
    owner_first_name: str
    owner_last_name: str
