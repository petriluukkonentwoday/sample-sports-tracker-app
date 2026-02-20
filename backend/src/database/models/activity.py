"""Activity and GPS tracking models."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.user import User


class Activity(Base):
    """Recorded sports activity (workout session)."""

    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Activity type
    sport_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # running, cycling, swimming, gym, etc.
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    active_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # excluding pauses

    # Distance & speed
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_speed_mps: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # meters per second
    max_speed_mps: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_pace_spm: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # seconds per meter

    # Elevation
    elevation_gain_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation_loss_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_elevation_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_elevation_meters: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Health metrics
    calories_burned: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Sync metadata
    client_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, index=True
    )  # for offline sync
    synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_manual_entry: Mapped[bool] = mapped_column(default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")
    points: Mapped[list["ActivityPoint"]] = relationship(
        "ActivityPoint", back_populates="activity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Activity {self.sport_type} {self.started_at}>"


class ActivityPoint(Base):
    """GPS track point within an activity."""

    __tablename__ = "activity_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), index=True
    )

    # Location
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_meters: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metrics at this point
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    speed_mps: Mapped[float | None] = mapped_column(Float, nullable=True)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    activity: Mapped["Activity"] = relationship("Activity", back_populates="points")

    def __repr__(self) -> str:
        return f"<ActivityPoint ({self.latitude}, {self.longitude})>"
