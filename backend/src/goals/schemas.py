"""Pydantic schemas for goals."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, computed_field


class GoalType(str, Enum):
    """Types of fitness goals."""

    DISTANCE = "distance"  # meters
    DURATION = "duration"  # seconds
    FREQUENCY = "frequency"  # number of activities
    CALORIES = "calories"  # kcal


class GoalPeriod(str, Enum):
    """Goal time periods."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class GoalCreate(BaseModel):
    """Schema for creating a goal."""

    title: str = Field(max_length=200)
    goal_type: GoalType
    sport_type: str | None = Field(default=None, max_length=50)
    target_value: float = Field(gt=0)
    period: GoalPeriod
    start_date: datetime
    end_date: datetime | None = None

    # Reminder settings
    reminder_enabled: bool = False
    reminder_time: str | None = Field(
        default=None, pattern=r"^([01]?\d|2[0-3]):[0-5]\d$"
    )
    reminder_days: str | None = Field(default=None, max_length=20)


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""

    title: str | None = Field(default=None, max_length=200)
    target_value: float | None = Field(default=None, gt=0)
    is_active: bool | None = None
    reminder_enabled: bool | None = None
    reminder_time: str | None = None
    reminder_days: str | None = None


class GoalResponse(BaseModel):
    """Schema for goal response."""

    id: str
    user_id: str
    title: str
    goal_type: str
    sport_type: str | None
    target_value: float
    current_value: float
    period: str
    start_date: datetime
    end_date: datetime | None
    is_active: bool
    is_achieved: bool
    achieved_at: datetime | None
    reminder_enabled: bool
    reminder_time: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def progress_percent(self) -> float:
        """Calculate goal progress as percentage."""
        if self.target_value <= 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    model_config = {"from_attributes": True}
