from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    tenure_months: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    monthly_charges: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    total_charges: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    contract_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    payment_method: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    internet_service: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    support_tickets: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    satisfaction_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    churned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    signup_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
