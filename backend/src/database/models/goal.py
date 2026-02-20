"""Goal model for tracking fitness targets."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.user import User


class Goal(Base):
    """Fitness goal (distance, frequency, calories, etc.)."""

    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Goal definition
    title: Mapped[str] = mapped_column(String(200))
    goal_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # distance, duration, frequency, calories
    sport_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # null = all sports
    target_value: Mapped[float] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Time period
    period: Mapped[str] = mapped_column(
        String(20)
    )  # daily, weekly, monthly, yearly, custom
    start_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False)
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Reminder settings
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_time: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )  # HH:MM format
    reminder_days: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # comma-separated: 1,2,3...

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")

    @property
    def progress_percent(self) -> float:
        """Calculate goal progress as percentage."""
        if self.target_value <= 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    def __repr__(self) -> str:
        return f"<Goal {self.title} ({self.progress_percent:.1f}%)>"
