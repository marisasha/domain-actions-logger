from datetime import timedelta
import json
import random

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi import status
from sqlalchemy import delete, exists, func, select


from src.exeptions import exception_handler
from src.user.schemas import *
from src.user.models import *
from src.user.dependencies import SessionDep
from src.redis.decorators import cache
from src.rabbit.service import rabbit_service
from src.logger import logger

from src.auth.security import decode_access_token, hash_password
from src.auth.schemas import CurrentUserSchema
from src.utils import n_print

router = APIRouter(tags=["api user"], prefix="/api")


@router.post("/users", summary="Сreate new user", status_code=status.HTTP_201_CREATED)
@exception_handler
async def create_user(
    user: UserSchemaRequest, session: SessionDep
) -> UserSchemaResponse:

    user_dict = user.model_dump()
    for field in ["username", "email", "phone"]:
        is_field_exists = await session.execute(
            select(exists().where(getattr(UserModel, field) == user_dict[field]))
        )
        if is_field_exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.title()} already exists",
            )

    new_user = UserModel(
        username=user.username,
        password=hash_password(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        gender=str(user.gender),
        email=user.email,
        birth_date=user.birth_date,
        phone=user.phone,
        is_admin=False,
        is_email_verificated=False,
    )

    session.add(new_user)
    await session.commit()

    token = str(random.randint(100000000000000, 1000000000000000))

    new_email_verification = VerificationModel(
        token=token,
        user_id=new_user.id,
        expires_at=datetime.now() + timedelta(hours=1),
        is_used=False,
    )

    session.add(new_email_verification)
    await session.commit()

    data_for_email_accept = {
        "first_name": user.first_name,
        "email": user.email,
        "token": token,
    }

    await rabbit_service.router.broker.publish(
        data_for_email_accept, "email_verification"
    )

    return new_user


@router.post(
    "/user/verify-email",
    summary="Api for send link for accept email ",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def verify_email(
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
):

    user = await session.get(UserModel, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {current_user.id} not found",
        )
    if user.is_email_verificated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Email already accepted"
        )
    token = str(random.randint(1000000000000, 10000000000000))

    new_verify_email = VerificationModel(
        user_id=current_user.id,
        code=token,
        expires_at=datetime.now() + timedelta(minutes=5),
        is_used=False,
    )

    session.add(new_verify_email)
    await session.commit()

    data_for_email_accept = {
        "id": new_verify_email.id,
        "first_name": user.first_name,
        "email": user.email,
        "token": token,
    }

    await rabbit_service.router.broker.publish(
        data_for_email_accept, "email_verification"
    )

    return new_verify_email.id


@router.post(
    "/user/verify-account",
    summary="Api for send link for accept email ",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def verify_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
):

    user = await session.get(UserModel, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {user_id} not found",
        )
    code = str(random.randint(100000, 999999))

    new_verify_user = VerificationModel(
        user_id=user_id,
        code=code,
        expires_at=datetime.now() + timedelta(minutes=5),
        is_used=False,
    )

    session.add(new_verify_user)
    await session.commit()

    data_for_user_accept = {
        "first_name": user.first_name,
        "email": user.email,
        "code": code,
    }

    await rabbit_service.router.broker.publish(data_for_user_accept, "move_accept")

    return new_verify_user.id


@router.get(
    "/user/verify-code",
    summary="Api for accept email ",
    status_code=status.HTTP_202_ACCEPTED,
)
@exception_handler
async def accept_code(
    session: SessionDep,
    id: str = Query(..., description="Verification id"),
    code: str = Query(..., description="Verification token"),
    is_email_verification: bool = Query(..., description="Is Verification email ?"),
):

    verification_code_execute = await session.execute(
        select(VerificationModel).where(
            VerificationModel.code == code and VerificationModel.id == id
        )
    )

    verification_code = verification_code_execute.scalar_one_or_none()
    if verification_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email verification code with token {code} not found",
        )

    if verification_code.expires_at > datetime.now():
        if not verification_code.is_used:
            if is_email_verification:
                user = await session.get(UserModel, verification_code.user_id)
                user.is_email_verificated = True
            verification_code.is_used = True
            await session.commit()
            return {"message": "Access allowed"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Verification code has been used ",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification code timeout has expired ",
        )


@router.patch(
    "/users/{user_id}",
    summary="Change user data by user_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def change_user(
    new_user_data: UserChangeDataSchema,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserSchemaResponse:

    if user_id != int(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make this operation",
        )
    user = await session.get(UserModel, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id{user_id} not found",
        )

    update_data = new_user_data.model_dump(exclude_unset=True)

    for field in ["username", "email", "phone"]:
        if field in update_data:
            is_field_exists = await session.execute(
                select(exists().where(getattr(UserModel, field) == update_data[field]))
            )
            if is_field_exists.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field.title()} already exists",
                )

    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    return user


@router.delete(
    "/users/{user_id}",
    summary="Delete user by id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> MessageSchemaResponse:
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make this operation",
        )
    user_execute = await session.execute(
        delete(UserModel).where(UserModel.id == user_id)
    )

    if user_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    await session.commit()
    return MessageSchemaResponse(message="User successfully deleted !")


@router.get(path="/users", summary="Get all users", status_code=status.HTTP_200_OK)
@exception_handler
@cache(expire=30, prefix="get_users", model=UserSchema)
async def get_users(session: SessionDep) -> list[UserSchema]:
    users_execute = await session.execute(select(UserModel))
    users = users_execute.scalars().all()
    if not users:
        return None
    users = [UserSchema.model_validate(u) for u in users]
    return users
