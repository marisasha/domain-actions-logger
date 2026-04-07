from datetime import datetime
import time
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.user.models import UserModel


class DomainModel(Base):
    __tablename__ = "domain"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    registration_date: Mapped[datetime]
    expiry_date: Mapped[datetime]

    status: Mapped[str] = mapped_column(
        CheckConstraint(
            "status IN ('registered', 'active', 'expired')", name="check_status_valid"
        )
    )
    registration_certificate_url: Mapped[str | None] = mapped_column(
        nullable=True, default=None
    )


class UserDomainModel(Base):
    __tablename__ = "user_domain"
    __table_args__ = (UniqueConstraint("user_id", "domain_id", name="uq_user_domain"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domain.id", ondelete="CASCADE"))

    permission: Mapped[str] = mapped_column(
        CheckConstraint(
            "permission IN ('user', 'moderator', 'admin','owner')",
            name="check_permission_valid",
        )
    )
    permission_give_date: Mapped[datetime]
    last_used_date: Mapped[datetime | None] = mapped_column(nullable=True)


class Move(Base):
    __tablename__ = "user_domain_move"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_domain_id: Mapped[int] = mapped_column(
        ForeignKey("user_domain.id", ondelete="CASCADE")
    )

    type: Mapped[str] = mapped_column(
        CheckConstraint(
            "type IN ('CREATE','READ','UPDATE','DELETE')", name="check_type_valid"
        )
    )
    description: Mapped[str]
    date: Mapped[datetime]
