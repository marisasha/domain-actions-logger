from fastapi import APIRouter, HTTPException
from fastapi import status, Depends
from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError

from src.auth.schemas import UserProfileSchema
from src.auth.models import UserModel
from src.domain.models import *
from src.domain.schemas import *
from src.domain.dependencies import SessionDep

from src.auth.security import decode_access_token

router = APIRouter(
    tags=[
        "api domain",
    ],
    prefix="/api",
)


@router.post("/owners", summary="Create owner", status_code=status.HTTP_201_CREATED)
async def create_owner(
    owner: OwnerDomainSchema,
    session: SessionDep,
    current_username: str = Depends(decode_access_token),
) -> OwnerDomainSchemaResponse:
    try:

        new_owner = OwnerDomainModel(
            first_name=owner.first_name,
            last_name=owner.last_name,
            gender=owner.gender,
            email=owner.email,
            phone=owner.phone,
            birth_date=owner.birth_date,
            birth_place=owner.birth_place,
            passport_from=owner.passport_from,
            passport_number=owner.passport_number,
            passport_series=owner.passport_series,
            issue_date=owner.issue_date,
            expiry_date=owner.expiry_date,
            department_code=owner.department_code,
            issue_by=owner.issue_by,
        )

        session.add(new_owner)
        await session.commit()
        return new_owner

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/owners/{id}", summary="Get owner information", status_code=status.HTTP_200_OK
)
async def get_owner(
    session: SessionDep, id: int, current_username: str = Depends(decode_access_token)
) -> OwnerDomainSchemaResponse:
    owner_execute = await session.execute(
        select(OwnerDomainModel).where(OwnerDomainModel.id == id)
    )

    owner = owner_execute.scalar_one_or_none()
    if owner == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with id {id} not found",
        )
    return owner


@router.get(
    "/owners/{owner_id}/domains",
    summary="Get owner's domains",
    status_code=status.HTTP_200_OK,
)
async def get_owner_domains(
    session: SessionDep,
    owner_id: int,
    current_username: str = Depends(decode_access_token),
) -> list[DomainSchemaResponse]:
    owner_domains_execute = await session.execute(
        select(DomainModel).where(DomainModel.owner_id == owner_id)
    )

    owner_domains = owner_domains_execute.scalars().all()
    if owner_domains == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with owner id {owner_id} not found",
        )
    return owner_domains


@router.get(
    "/owners/{owner_id}/domains/{domain_id}",
    summary="Get owner's domain by owner_id and domain_id",
    status_code=status.HTTP_200_OK,
)
async def get_owner_and_domain(
    session: SessionDep,
    owner_id: int,
    domain_id: int,
    current_username: str = Depends(decode_access_token),
):
    owner_and_domain_execute = await session.execute(
        select(OwnerDomainModel, DomainModel)
        .join(OwnerDomainModel, DomainModel.owner_id == OwnerDomainModel.id)
        .where(OwnerDomainModel.id == owner_id)
        .where(DomainModel.id == domain_id)
    )

    owner_and_domain = owner_and_domain_execute.one_or_none()
    if owner_and_domain == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with owner id {owner_id} or domain with id {domain_id} not found",
        )
    owner, domain = owner_and_domain
    return OwnerWithDomainSchema(
        **domain.__dict__,
        owner_first_name=owner.first_name,
        owner_last_name=owner.last_name,
    )


@router.post("/domains", summary="Create domain", status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain: DomainSchema,
    session: SessionDep,
    current_username: str = Depends(decode_access_token),
) -> DomainSchemaResponse:
    try:

        is_domain_name_exist = await session.execute(
            select(exists().where(DomainModel.name == domain.name))
        )
        if is_domain_name_exist.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Domain with name {domain.name}already exists",
            )

        new_domain = DomainModel(
            owner_id=domain.owner_id,
            name=domain.name,
            registration_date=domain.registration_date,
            expiry_date=domain.expiry_date,
            status=domain.status,
            registration_certificate_url=domain.registration_certificate_url,
        )

        session.add(new_domain)
        await session.commit()
        return new_domain

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with id {domain.owner_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/domains/{id}",
    summary="Get domain information by id",
    status_code=status.HTTP_200_OK,
)
async def get_domain(
    session: SessionDep, id: int, current_username: str = Depends(decode_access_token)
) -> DomainSchemaResponse:
    domain_execute = await session.execute(
        select(DomainModel).where(DomainModel.id == id)
    )

    domain = domain_execute.scalar_one_or_none()
    if domain == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {id} not found",
        )
    return domain


@router.post(
    "/domains/users",
    summary="Create relationship user and domain",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_domain(
    user_domain: UserDomainSchema,
    session: SessionDep,
    current_username: str = Depends(decode_access_token),
) -> UserDomainSchema:
    try:

        is_user_and_domain_exists = await session.execute(
            select(
                exists().where(
                    UserDomainModel.user_id == user_domain.user_id,
                    UserDomainModel.domain_id == user_domain.domain_id,
                )
            )
        )
        if is_user_and_domain_exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Relationship user {user_domain.user_id} and domain {user_domain.domain_id} already exists",
            )

        new_user_domain = UserDomainModel(
            user_id=user_domain.user_id,
            domain_id=user_domain.domain_id,
            permission=user_domain.permission,
            permission_give_date=user_domain.permission_give_date,
            last_used_date=user_domain.last_used_date,
        )

        session.add(new_user_domain)
        await session.commit()
        return new_user_domain

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_domain.user_id} or domain with id {user_domain.domain_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/domains/{domain_id}/users",
    summary="Get all users for domain by domain_id",
    status_code=status.HTTP_200_OK,
)
async def get_users_for_domain(
    domain_id: int,
    session: SessionDep,
    current_username: str = Depends(decode_access_token),
):
    domain_users_execute = await session.execute(
        select(
            DomainModel.id.label("domain_id"),
            DomainModel.name.label("domain_name"),
            UserModel.first_name.label("user_first_name"),
            UserModel.last_name.label("user_last_name"),
            UserDomainModel.permission,
            UserDomainModel.permission_give_date,
            UserDomainModel.last_used_date,
        )
        .join(DomainModel, DomainModel.id == UserDomainModel.domain_id)
        .join(UserModel, UserModel.id == UserDomainModel.user_id)
        .where(UserDomainModel.domain_id == domain_id)
    )

    domain_users_row = domain_users_execute.all()
    if not domain_users_row:
        return DomainUsersResponse(domain=None, users=[])

    domain = DomainProfileSchema(
        id=domain_users_row[0].domain_id, name=domain_users_row[0].domain_name
    )

    users = [
        UserPermissionSchema(
            first_name=row.user_first_name,
            last_name=row.user_last_name,
            permission=row.permission,
            permission_give_date=row.permission_give_date,
            last_used_date=row.last_used_date,
        )
        for row in domain_users_row
    ]

    return DomainUsersResponse(domain=domain, users=users)


@router.get(
    "/domains/users/{user_id}",
    summary="Get all domains for user by user_id",
    status_code=status.HTTP_200_OK,
)
async def get_domains_for_user(
    user_id: int,
    session: SessionDep,
    current_username: str = Depends(decode_access_token),
):
    user_domains_execute = await session.execute(
        select(
            UserModel.id.label("user_id"),
            UserModel.first_name.label("user_first_name"),
            UserModel.last_name.label("user_last_name"),
            DomainModel.name.label("domain_name"),
            UserDomainModel.permission,
            UserDomainModel.permission_give_date,
            UserDomainModel.last_used_date,
        )
        .join(DomainModel, DomainModel.id == UserDomainModel.domain_id)
        .join(UserModel, UserModel.id == UserDomainModel.user_id)
        .where(UserDomainModel.user_id == user_id)
    )
    user_domains_rows = user_domains_execute.all()
    if not user_domains_rows:
        return UserDomainsResponse(user=None, domains=[])

    user = UserProfileSchema(
        id=user_domains_rows[0].user_id,
        first_name=user_domains_rows[0].user_first_name,
        last_name=user_domains_rows[0].user_last_name,
    )
    domains = [
        DomainPermissionSchema(
            domain_name=row.domain_name,
            permission=row.permission,
            permission_give_date=row.permission_give_date,
            last_used_date=row.last_used_date,
        )
        for row in user_domains_rows
    ]

    return UserDomainsResponse(user=user, domains=domains)
