from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, exists, func, select
from fastapi import status, Depends

from src.domain.dependencies import SessionDep
from src.domain.models import *
from src.domain.schemas import *

from src.user.schemas import UserProfileSchema
from src.user.models import UserModel

from src.auth.security import decode_access_token
from src.auth.schemas import CurrentUserSchema
from src.utils import n_print

router = APIRouter(
    tags=[
        "api domain",
    ],
    prefix="/api",
)


@router.post("/domains", summary="Create domain", status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain: DomainSchema,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> DomainSchemaResponse:
    try:

        is_domain_name_exist = await session.execute(
            select(exists().where(DomainModel.name == domain.name))
        )
        if is_domain_name_exist.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Domain with name {domain.name} already exists",
            )

        new_domain = DomainModel(
            name=domain.name,
            registration_date=domain.registration_date,
            expiry_date=domain.expiry_date,
            status=domain.status,
            registration_certificate_url=domain.registration_certificate_url,
        )
        session.add(new_domain)
        await session.flush()

        new_user_domain = UserDomainModel(
            user_id=current_user.id,
            domain_id=new_domain.id,
            permission="owner",
            permission_give_date=datetime.now(),
            last_used_date=datetime.now(),
        )
        session.add(new_user_domain)
        await session.commit()
        return new_domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/domains/{domain_id}",
    summary="Get domain information by id",
    status_code=status.HTTP_200_OK,
)
async def get_domain(
    session: SessionDep,
    domain_id: int,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> DomainSchemaResponse:
    domain = await session.get(DomainModel, domain_id)
    if domain is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found",
        )
    return domain


@router.post(
    "/domains/users",
    summary="Create relationship user and domain",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_domain(
    user_domain: UserDomainIDSchema,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserDomainIDSchema:
    try:
        # Проверка прав доступа(разрешено владельцу/админу домена , админу сайта)
        current_user_permission_execute = await session.execute(
            select(UserDomainModel.permission).where(
                UserDomainModel.user_id == current_user.id,
                UserDomainModel.domain_id == user_domain.domain_id,
            )
        )
        current_user_permission = current_user_permission_execute.scalar_one_or_none()
        access_for_change = False
        # Владелец может удалить связь при любых права на домен, админ домена может удалить связь если права != владелец или админ
        if current_user.role == "admin":
            access_for_change = True
        if current_user_permission == "owner" and user_domain.permission != "owner":
            access_for_change = True
        if current_user_permission == "admin":
            if user_domain.permission != "owner" and user_domain.permission != "admin":
                access_for_change = True

        if not access_for_change:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to make this operation",
            )

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
    except HTTPException:
        raise
    except DBAPIError:
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
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> DomainUsersResponse:

    domain_users_execute = await session.execute(
        select(
            UserDomainModel.domain_id,
            DomainModel.name.label("domain_name"),
            UserDomainModel.user_id,
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

    domain_users_rows = domain_users_execute.all()
    if not domain_users_rows:
        return DomainUsersResponse(domain=None, users=[])

    # Проверка прав доступа к данным (данные посмотреть может только пользователь домена или администратор сайта)
    access_for_data = False
    for dur in domain_users_rows:
        if current_user.id == dur.user_id:
            access_for_data = True
            break

    if not access_for_data and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make this operation",
        )

    domain = DomainProfileSchema(
        id=domain_users_rows[0].domain_id, name=domain_users_rows[0].domain_name
    )

    users = [
        UserPermissionSchema(
            first_name=row.user_first_name,
            last_name=row.user_last_name,
            permission=row.permission,
            permission_give_date=row.permission_give_date,
            last_used_date=row.last_used_date,
        )
        for row in domain_users_rows
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
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserDomainsResponse:

    # Проверка прав доступа к данным (разрешено текущиму пользователю при current_user.id==user_id , администратору сайта)
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make this operation",
        )

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


@router.get(
    "/domains/{domain_id}/users/{user_id}",
    summary="Get user domain by domain_id and user_id",
    status_code=status.HTTP_200_OK,
)
async def get_user_domain(
    domain_id: int,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserDomainSchemaResponse:
    user_domain_execute = await session.execute(
        select(
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
        .where(UserDomainModel.domain_id == domain_id)
    )

    user_domain_tuple = user_domain_execute.one_or_none()
    if user_domain_tuple is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User domain with domain_id {domain_id} and user_id {user_id} not found",
        )
    # Проверка прав доступа(разрешено владельцу/админу домена , текущему пользователю при user_id != current_user.id , админу сайта)
    if user_id != current_user.id and current_user.role != "admin":
        # Получаем права текущего пользователя на этот домен
        current_user_permission_execute = await session.execute(
            select(UserDomainModel.permission).where(
                UserDomainModel.user_id == current_user.id,
                UserDomainModel.domain_id == domain_id,
            )
        )
        current_user_permission = current_user_permission_execute.scalar_one_or_none()
        # Проверяем, есть ли у текущего пользователя права администратора или владельца
        if current_user_permission not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to make this operation",
            )

    user_domain = UserDomainSchemaResponse(
        user_first_name=user_domain_tuple.user_first_name,
        user_last_name=user_domain_tuple.user_last_name,
        domain_name=user_domain_tuple.domain_name,
        permission=user_domain_tuple.permission,
        permission_give_date=user_domain_tuple.permission_give_date,
        last_used_date=user_domain_tuple.last_used_date,
    )
    return user_domain


@router.patch(
    "/domains/{domain_id}/users/{user_id}",
    summary="Change user domain permission by domain_id and user_id",
    status_code=status.HTTP_200_OK,
)
async def change_user_domain_permission(
    permission: PermissionChangeSchema,
    domain_id: int,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserDomainIDSchema:
    try:
        user_domain_execute = await session.execute(
            select(UserDomainModel)
            .where(UserDomainModel.domain_id == domain_id)
            .where(UserDomainModel.user_id == user_id)
        )

        user_domain = user_domain_execute.scalar_one_or_none()
        if user_domain is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User domain with domain_id {domain_id} and user_id {user_id} not found",
            )

        # Проверка прав доступа(разрешено владельцу/админу домена , админу сайта)
        current_user_permission_execute = await session.execute(
            select(UserDomainModel.permission).where(
                UserDomainModel.user_id == current_user.id,
                UserDomainModel.domain_id == domain_id,
            )
        )
        current_user_permission = current_user_permission_execute.scalar_one_or_none()
        access_for_change = False
        # Владелец может изменять любые права на домен, админ домена может изменять права если права != владелец или админ
        if current_user.role == "admin":
            access_for_change = True
        if current_user_permission == "owner" and permission.permission != "owner":
            access_for_change = True
        if current_user_permission == "admin":
            if permission.permission != "owner" and permission.permission != "admin":
                if (
                    user_domain.permission != "owner"
                    and user_domain.permission != "admin"
                ):
                    access_for_change = True

        if not access_for_change:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to make this operation",
            )

        user_domain.permission = permission.permission
        user_domain.permission_give_date = datetime.now()

        await session.commit()
        await session.refresh(user_domain)

        return user_domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/domains/{domain_id}/users/{user_id}",
    summary="Delete user domain by domain_id and user_id",
    status_code=status.HTTP_200_OK,
)
async def delete_user_domain_permission(
    domain_id: int,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> MessageSchemaResponse:
    try:
        user_domain_execute = await session.execute(
            select(UserDomainModel)
            .where(UserDomainModel.domain_id == domain_id)
            .where(UserDomainModel.user_id == user_id)
        )

        user_domain = user_domain_execute.scalar_one_or_none()
        if user_domain is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User domain with domain_id {domain_id} and user_id {user_id} not found",
            )

        # Проверка прав доступа(разрешено владельцу/админу домена , админу сайта)
        current_user_permission_execute = await session.execute(
            select(UserDomainModel.permission).where(
                UserDomainModel.user_id == current_user.id,
                UserDomainModel.domain_id == domain_id,
            )
        )
        current_user_permission = current_user_permission_execute.scalar_one_or_none()
        access_for_change = False
        # Владелец может удалить связь при любых права на домен, админ домена может удалить связь если права != владелец или админ
        if current_user.role == "admin":
            access_for_change = True
        if current_user_permission == "owner":
            access_for_change = True
        if current_user_permission == "admin":
            if user_domain.permission != "owner" and user_domain.permission != "admin":
                access_for_change = True

        if not access_for_change:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to make this operation",
            )
        await session.delete(user_domain)
        await session.commit()
        return MessageSchemaResponse(message="User domain successfully deleted!")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
