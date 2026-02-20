"""Statistics API endpoints."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.database.models import User
from src.statistics.schemas import (
    DailyStat,
    PeriodSummary,
    PersonalRecord,
    StatsPeriod,
    StatsOverview,
    WeeklyTrend,
)
from src.statistics.service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/summary", response_model=PeriodSummary)
async def get_period_summary(
    period: StatsPeriod = Query(default=StatsPeriod.WEEK),
    sport_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PeriodSummary:
    """Get summary statistics for a time period."""
    service = StatisticsService(db)
    return await service.get_period_summary(current_user.id, period, sport_type)


@router.get("/daily", response_model=list[DailyStat])
async def get_daily_stats(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=date.today),
    sport_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[DailyStat]:
    """Get daily statistics for charting."""
    service = StatisticsService(db)
    return await service.get_daily_stats(
        current_user.id, start_date, end_date, sport_type
    )


@router.get("/records", response_model=list[PersonalRecord])
async def get_personal_records(
    sport_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[PersonalRecord]:
    """Get personal best records."""
    service = StatisticsService(db)
    return await service.get_personal_records(current_user.id, sport_type)


@router.get("/trend", response_model=WeeklyTrend)
async def get_weekly_trend(
    sport_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WeeklyTrend:
    """Get week-over-week comparison."""
    service = StatisticsService(db)
    return await service.get_weekly_trend(current_user.id, sport_type)


@router.get("/overview", response_model=StatsOverview)
async def get_stats_overview(
    period: StatsPeriod = Query(default=StatsPeriod.WEEK),
    sport_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StatsOverview:
    """Get complete statistics overview including summary, daily stats, and records."""
    service = StatisticsService(db)

    summary = await service.get_period_summary(current_user.id, period, sport_type)
    daily_stats = await service.get_daily_stats(
        current_user.id,
        summary.period_start,
        summary.period_end,
        sport_type,
    )
    records = await service.get_personal_records(current_user.id, sport_type)

    return StatsOverview(
        period=period.value,
        summary=summary,
        daily_stats=daily_stats,
        personal_records=records,
    )
