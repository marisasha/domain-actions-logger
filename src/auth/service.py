from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi import status
from sqlalchemy import exists, func, select

from src.auth.schemas import *
from src.auth.dependencies import SessionDep
from src.auth.security import *

from src.user.models import UserModel

router = APIRouter(tags=["auth"])


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
    role = "admin" if user.is_admin else "user"

    access_token = create_access_token({"sub": str(user.id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": role})
    return TokenSchema(access=access_token, refresh=refresh_token)


@router.post(
    "/auth/token/refresh", summary="Token refresher", status_code=status.HTTP_200_OK
)
async def refresh_token(
    user: CurrentUserSchema = Depends(decode_refresh_token),
) -> dict[str, str]:
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access": access_token}
