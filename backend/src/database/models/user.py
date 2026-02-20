"""User model for authentication and profiles."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.activity import Activity
    from src.database.models.goal import Goal


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # OAuth fields
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Preferences
    preferred_units: Mapped[str] = mapped_column(
        String(10), default="metric"
    )  # metric / imperial
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        "Goal", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
