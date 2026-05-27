from functools import wraps
from typing import Literal, Optional
from fastapi import HTTPException, Depends, status
from sqlalchemy import select
from src.auth.schemas import CurrentUserSchema
from src.domain.models import UserDomainModel
from src.domain.dependencies import SessionDep, get_session

"""
    Декоратор для проверки прав пользователя на домен.
    Виды проверок

    1)тип: Управление (просмотр / создание)
    что проверяется: роль в UserModels

    2)тип: Аутентификация(Проверка соотвествия пользователя текущему пользователю)
    что проверяется: user_id в UserModels и id в current_user
    """


def require_permission(
    role: Optional[Literal["owner", "admin", "moderator", "user"]] = None,
    authentication: Optional[bool] = None,
):

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            access_role_permission = False
            access_authentication_permission = False
            if role:
                domain_id = kwargs.get("domain_id")
                if domain_id is None:
                    for key, value in kwargs.items():
                        if hasattr(value, "domain_id"):
                            domain_id = value.domain_id
                            break
                    if domain_id is None:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="domain_id not found in request body",
                        )
                current_user = kwargs.get("current_user")
                session = kwargs.get("session")

                if not current_user or not session:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing current_user or session dependency",
                    )

                # Проверяем права
                access_role_permission = await check_permission_for_management(
                    domain_id=domain_id,
                    current_user=current_user,
                    required_role=role,
                    session=session,
                )

            if authentication:
                user_id = kwargs.get("user_id")
                if user_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="user_id not found in request body",
                    )
                current_user = kwargs.get("current_user")
                if user_id != current_user.id and current_user.role != "admin":
                    access_authentication_permission = False
                else:
                    access_authentication_permission = True
            if (
                access_role_permission == False
                and access_authentication_permission == False
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to make this operation",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def check_permission_for_management(
    domain_id: int,
    current_user: CurrentUserSchema,
    required_role: str,
    session: SessionDep,
):
    current_user_permission_execute = await session.execute(
        select(UserDomainModel.permission).where(
            UserDomainModel.user_id == current_user.id,
            UserDomainModel.domain_id == domain_id,
        )
    )

    current_user_permission = current_user_permission_execute.scalar_one_or_none()
    access = False

    if current_user.role == "admin":
        access = True
    if required_role == "owner" and current_user_permission == "owner":
        access = True
    if required_role == "admin" and current_user_permission in ["owner", "admin"]:
        access = True
    if required_role == "moderator" and current_user_permission in [
        "owner",
        "admin",
        "moderator",
    ]:
        access = True
    if required_role == "user" and current_user_permission in [
        "owner",
        "admin",
        "moderator",
        "user",
    ]:
        access = True

    return access


"""
    Функция для провери прав для редакции и удаления
        тип: Правка (редактирование/удаление данных)
        что проверяется: иерархия ролей для выполнения действия
"""


async def check_permission_for_correct(
    domain_id: int,
    user_id: int,
    current_user: CurrentUserSchema,
    session: SessionDep,
    permission: Optional[str] = None,
):
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

    current_user_permission_execute = await session.execute(
        select(UserDomainModel.permission).where(
            UserDomainModel.user_id == current_user.id,
            UserDomainModel.domain_id == domain_id,
        )
    )

    current_user_permission = current_user_permission_execute.scalar_one_or_none()
    access = False
    # Владелец может редактировать/удалить связь при любых права на домен, админ домена может редактировать/удалить
    # связь если права != владелец или админ
    if current_user.role == "admin":
        access = True
    if current_user_permission == "owner":
        access = True
    # если есть permission который мы передали в аргументах, мы используем его
    if permission:
        if current_user_permission == "admin":
            if permission != "owner" and permission != "admin":
                access = True
    else:
        if current_user_permission == "admin":
            if user_domain.permission != "owner" and user_domain.permission != "admin":
                access = True

    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make this operation",
        )
    return user_domain
