"""Pydantic schemas for live tracking."""

from datetime import datetime

from pydantic import BaseModel, Field


class LiveSessionStart(BaseModel):
    """Request to start a live tracking session."""

    activity_id: str
    sport_type: str
    is_public: bool = False
    allowed_viewers: list[str] = Field(default_factory=list)


class LiveSessionResponse(BaseModel):
    """Response with live session info."""

    activity_id: str
    user_id: str
    user_name: str
    sport_type: str
    started_at: datetime
    is_public: bool
    viewer_count: int = 0
    last_point: dict | None = None


class LiveLocationUpdate(BaseModel):
    """Location update from the tracking device."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    elevation_meters: float | None = None
    accuracy_meters: float | None = None
    speed_mps: float | None = Field(default=None, ge=0)
    heart_rate: int | None = Field(default=None, ge=30, le=250)
    timestamp: datetime | None = None


class LiveSessionList(BaseModel):
    """List of active live sessions."""

    sessions: list[LiveSessionResponse]
