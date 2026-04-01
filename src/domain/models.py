from datetime import datetime
import time
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class OwnerDomainModel(Base):
    __tablename__ = "owner_domain"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True)

    birth_date: Mapped[datetime]
    birth_place: Mapped[str]

    passport_from: Mapped[str]
    passport_number: Mapped[str]
    passport_series: Mapped[int | None] = mapped_column(nullable=True)

    issue_date: Mapped[datetime]
    expiry_date: Mapped[datetime | None] = mapped_column(nullable=True)

    department_code: Mapped[str | None] = mapped_column(nullable=True)
    issue_by: Mapped[str]


class DomainModel(Base):
    __tablename__ = "domain"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("owner_domain.id", ondelete="CASCADE")
    )

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
            "permission IN ('user', 'moderator', 'admin')",
            name="check_permission_valid",
        )
    )
    permission_give_date: Mapped[datetime]
    last_used_date: Mapped[datetime | None] = mapped_column(nullable=True)
