"""Pydantic schemas for activities."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SportType(str, Enum):
    """Supported sport types."""

    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WALKING = "walking"
    HIKING = "hiking"
    GYM = "gym"
    YOGA = "yoga"
    OTHER = "other"


class ActivityPointCreate(BaseModel):
    """Schema for creating a GPS track point."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    elevation_meters: float | None = None
    accuracy_meters: float | None = None
    timestamp: datetime
    speed_mps: float | None = None
    heart_rate: int | None = Field(default=None, ge=30, le=250)
    cadence: int | None = Field(default=None, ge=0)


class ActivityPointResponse(BaseModel):
    """Schema for GPS track point response."""

    id: int
    latitude: float
    longitude: float
    elevation_meters: float | None
    timestamp: datetime
    speed_mps: float | None
    heart_rate: int | None
    cadence: int | None

    model_config = {"from_attributes": True}


class ActivityCreate(BaseModel):
    """Schema for creating an activity."""

    sport_type: SportType
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int = Field(ge=0)
    active_duration_seconds: int | None = Field(default=None, ge=0)

    # Distance & speed
    distance_meters: float | None = Field(default=None, ge=0)
    avg_speed_mps: float | None = Field(default=None, ge=0)
    max_speed_mps: float | None = Field(default=None, ge=0)

    # Elevation
    elevation_gain_meters: float | None = None
    elevation_loss_meters: float | None = None

    # Health metrics
    calories_burned: int | None = Field(default=None, ge=0)
    avg_heart_rate: int | None = Field(default=None, ge=30, le=250)
    max_heart_rate: int | None = Field(default=None, ge=30, le=250)
    avg_cadence: int | None = Field(default=None, ge=0)

    # GPS points (optional, sent separately for large tracks)
    points: list[ActivityPointCreate] | None = None

    # Offline sync
    client_id: str | None = Field(default=None, max_length=36)
    is_manual_entry: bool = False


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""

    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    sport_type: SportType | None = None
    calories_burned: int | None = Field(default=None, ge=0)


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    id: str
    user_id: str
    sport_type: str
    title: str | None
    description: str | None

    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int
    active_duration_seconds: int | None

    distance_meters: float | None
    avg_speed_mps: float | None
    max_speed_mps: float | None
    avg_pace_spm: float | None

    elevation_gain_meters: float | None
    elevation_loss_meters: float | None

    calories_burned: int | None
    avg_heart_rate: int | None
    max_heart_rate: int | None
    avg_cadence: int | None

    client_id: str | None
    is_manual_entry: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ActivityDetailResponse(ActivityResponse):
    """Activity response including GPS points."""

    points: list[ActivityPointResponse] = []


class ActivityListParams(BaseModel):
    """Query parameters for activity listing."""

    sport_type: SportType | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
