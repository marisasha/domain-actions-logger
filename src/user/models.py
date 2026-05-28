from datetime import datetime
import time
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[str] = mapped_column(
        CheckConstraint("gender IN ('M', 'F')", name="check_gender_valid"),
    )
    email: Mapped[str | None] = mapped_column(unique=True, nullable=True, default=None)
    birth_date: Mapped[datetime]
    phone: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool]
