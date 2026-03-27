from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi import status
from sqlalchemy import func, select
from datetime import datetime, timedelta, timezone

from src.auth.models import *
from src.auth.schemas import *
from src.auth.dependencies import SessionDep
from src.auth.security import *

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register", summary="Сreate new user", status_code=status.HTTP_201_CREATED
)
async def register(user: UserSchemaPOST, session: SessionDep) -> UserSchema:

    is_username_exist = await session.execute(
        select(True).where(UserModel.username == user.username)
    )
    if is_username_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username already exists",
        )

    new_user = UserModel(
        username=user.username,
        password=hash_password(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        birth_date=user.birth_date,
        phone=user.phone,
    )
    session.add(new_user)
    await session.commit()

    return new_user


@router.post(
    "/auth/token", summary="Authorization user by token", status_code=status.HTTP_200_OK
)
async def login(data: UserAuthorizationSchema, session: SessionDep) -> TokenSchema:
    execute_user = await session.execute(
        select(UserModel).where(UserModel.username == data.username)
    )
    user = execute_user.scalar_one_or_none()
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username does not exists",
        )

    is_user_verificate = verify_password(data.password, user.password)

    if not is_user_verificate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token({"sub": data.username})
    refresh_token = create_refresh_token({"sub": data.username})
    return TokenSchema(access=access_token, refresh=refresh_token)


@router.post(
    "/auth/token/refresh", summary="Token refresher", status_code=status.HTTP_200_OK
)
async def refresh_token(
    username: str = Depends(decode_refresh_token),
) -> dict[str, str]:
    access_token = create_access_token({"sub": username})
    return {"access": access_token}
