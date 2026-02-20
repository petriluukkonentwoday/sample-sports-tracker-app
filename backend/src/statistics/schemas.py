"""Pydantic schemas for statistics."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class StatsPeriod(str, Enum):
    """Time periods for statistics."""

    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all_time"


class PeriodSummary(BaseModel):
    """Summary statistics for a time period."""

    period_start: date
    period_end: date
    total_activities: int
    total_distance_meters: float
    total_duration_seconds: int
    total_calories: int
    avg_distance_meters: float
    avg_duration_seconds: float
    avg_pace_per_km: float | None  # seconds per km
    sports_breakdown: dict[str, int]  # sport_type -> count


class PersonalRecord(BaseModel):
    """A personal best record."""

    record_type: str  # longest_distance, fastest_pace, longest_duration, etc.
    sport_type: str
    value: float
    unit: str
    activity_id: str
    achieved_at: datetime


class DailyStat(BaseModel):
    """Statistics for a single day (for charts)."""

    date: date
    activities: int
    distance_meters: float
    duration_seconds: int
    calories: int


class WeeklyTrend(BaseModel):
    """Week-over-week trend data."""

    current_week: PeriodSummary
    previous_week: PeriodSummary
    distance_change_percent: float
    duration_change_percent: float
    activity_count_change: int


class StatsOverview(BaseModel):
    """Complete statistics overview."""

    period: str
    summary: PeriodSummary
    daily_stats: list[DailyStat]
    personal_records: list[PersonalRecord]
