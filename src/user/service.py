from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi import status
from sqlalchemy import delete, exists, func, select


from src.user.schemas import *
from src.user.models import *
from src.user.dependencies import SessionDep

from src.auth.security import decode_access_token, hash_password
from src.auth.schemas import CurrentUserSchema
from src.utils import n_print

router = APIRouter(tags=["api user"], prefix="/api")


@router.post("/users", summary="Сreate new user", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserSchemaRequest, session: SessionDep
) -> UserSchemaResponse:

    try:
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
        )

        session.add(new_user)
        await session.commit()
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch(
    "/users/{user_id}",
    summary="Change user data by user_id",
    status_code=status.HTTP_200_OK,
)
async def change_user(
    new_user_data: UserChangeDataSchema,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> UserSchemaResponse:
    try:
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
                    select(
                        exists().where(getattr(UserModel, field) == update_data[field])
                    )
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete(
    "/users/{user_id}",
    summary="Delete user by id",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> MessageSchemaResponse:
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
