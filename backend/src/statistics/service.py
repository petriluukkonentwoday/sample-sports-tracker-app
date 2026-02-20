"""Statistics service layer."""

from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Activity
from src.statistics.schemas import (
    DailyStat,
    PeriodSummary,
    PersonalRecord,
    StatsPeriod,
    WeeklyTrend,
)


class StatisticsService:
    """Service for calculating user statistics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_period_summary(
        self,
        user_id: str,
        period: StatsPeriod,
        sport_type: str | None = None,
    ) -> PeriodSummary:
        """Calculate summary statistics for a time period."""
        start_date, end_date = self._get_period_bounds(period)

        conditions = [
            Activity.user_id == user_id,
            Activity.started_at >= start_date,
            Activity.started_at < end_date,
        ]
        if sport_type:
            conditions.append(Activity.sport_type == sport_type)

        # Aggregate query
        result = await self.db.execute(
            select(
                func.count(Activity.id).label("count"),
                func.coalesce(func.sum(Activity.distance_meters), 0).label("distance"),
                func.coalesce(func.sum(Activity.duration_seconds), 0).label("duration"),
                func.coalesce(func.sum(Activity.calories_burned), 0).label("calories"),
            ).where(and_(*conditions))
        )
        row = result.one()

        total_activities = row.count or 0
        total_distance = float(row.distance or 0)
        total_duration = int(row.duration or 0)
        total_calories = int(row.calories or 0)

        avg_distance = total_distance / total_activities if total_activities else 0
        avg_duration = total_duration / total_activities if total_activities else 0

        # Calculate average pace (seconds per km)
        avg_pace_per_km = None
        if total_distance > 0:
            avg_pace_per_km = (total_duration / total_distance) * 1000

        # Get sports breakdown
        breakdown_result = await self.db.execute(
            select(
                Activity.sport_type,
                func.count(Activity.id).label("count"),
            )
            .where(and_(*conditions))
            .group_by(Activity.sport_type)
        )
        sports_breakdown = {row.sport_type: row.count for row in breakdown_result}

        return PeriodSummary(
            period_start=start_date.date(),
            period_end=end_date.date(),
            total_activities=total_activities,
            total_distance_meters=total_distance,
            total_duration_seconds=total_duration,
            total_calories=total_calories,
            avg_distance_meters=avg_distance,
            avg_duration_seconds=avg_duration,
            avg_pace_per_km=avg_pace_per_km,
            sports_breakdown=sports_breakdown,
        )

    async def get_daily_stats(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        sport_type: str | None = None,
    ) -> list[DailyStat]:
        """Get daily statistics for charting."""
        conditions = [
            Activity.user_id == user_id,
            Activity.started_at >= datetime.combine(start_date, datetime.min.time()),
            Activity.started_at < datetime.combine(end_date, datetime.min.time()),
        ]
        if sport_type:
            conditions.append(Activity.sport_type == sport_type)

        # Group by date
        result = await self.db.execute(
            select(
                func.date(Activity.started_at).label("activity_date"),
                func.count(Activity.id).label("count"),
                func.coalesce(func.sum(Activity.distance_meters), 0).label("distance"),
                func.coalesce(func.sum(Activity.duration_seconds), 0).label("duration"),
                func.coalesce(func.sum(Activity.calories_burned), 0).label("calories"),
            )
            .where(and_(*conditions))
            .group_by(func.date(Activity.started_at))
            .order_by(func.date(Activity.started_at))
        )

        # Create a dict for easy lookup
        stats_by_date = {
            row.activity_date: DailyStat(
                date=row.activity_date,
                activities=row.count,
                distance_meters=float(row.distance),
                duration_seconds=int(row.duration),
                calories=int(row.calories),
            )
            for row in result
        }

        # Fill in missing dates with zeros
        daily_stats = []
        current_date = start_date
        while current_date < end_date:
            if current_date in stats_by_date:
                daily_stats.append(stats_by_date[current_date])
            else:
                daily_stats.append(
                    DailyStat(
                        date=current_date,
                        activities=0,
                        distance_meters=0.0,
                        duration_seconds=0,
                        calories=0,
                    )
                )
            current_date += timedelta(days=1)

        return daily_stats

    async def get_personal_records(
        self,
        user_id: str,
        sport_type: str | None = None,
    ) -> list[PersonalRecord]:
        """Get personal best records."""
        records = []
        sport_types = [sport_type] if sport_type else await self._get_user_sports(user_id)

        for sport in sport_types:
            # Longest distance
            distance_record = await self._get_max_record(
                user_id, sport, "distance_meters"
            )
            if distance_record:
                records.append(
                    PersonalRecord(
                        record_type="longest_distance",
                        sport_type=sport,
                        value=distance_record[0],
                        unit="meters",
                        activity_id=distance_record[1],
                        achieved_at=distance_record[2],
                    )
                )

            # Longest duration
            duration_record = await self._get_max_record(
                user_id, sport, "duration_seconds"
            )
            if duration_record:
                records.append(
                    PersonalRecord(
                        record_type="longest_duration",
                        sport_type=sport,
                        value=float(duration_record[0]),
                        unit="seconds",
                        activity_id=duration_record[1],
                        achieved_at=duration_record[2],
                    )
                )

            # Fastest pace (lowest avg_pace_spm where distance > 1000m)
            pace_result = await self.db.execute(
                select(
                    Activity.avg_pace_spm,
                    Activity.id,
                    Activity.started_at,
                )
                .where(
                    Activity.user_id == user_id,
                    Activity.sport_type == sport,
                    Activity.avg_pace_spm.isnot(None),
                    Activity.distance_meters >= 1000,
                )
                .order_by(Activity.avg_pace_spm.asc())
                .limit(1)
            )
            pace_row = pace_result.first()
            if pace_row:
                records.append(
                    PersonalRecord(
                        record_type="fastest_pace",
                        sport_type=sport,
                        value=pace_row[0],
                        unit="seconds_per_meter",
                        activity_id=pace_row[1],
                        achieved_at=pace_row[2],
                    )
                )

        return records

    async def get_weekly_trend(
        self,
        user_id: str,
        sport_type: str | None = None,
    ) -> WeeklyTrend:
        """Get week-over-week comparison."""
        current_week = await self.get_period_summary(
            user_id, StatsPeriod.WEEK, sport_type
        )

        # Get previous week
        now = datetime.utcnow()
        days_since_monday = now.weekday()
        this_monday = now - timedelta(days=days_since_monday)
        last_monday = this_monday - timedelta(days=7)

        prev_conditions = [
            Activity.user_id == user_id,
            Activity.started_at >= last_monday.replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            Activity.started_at < this_monday.replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
        ]
        if sport_type:
            prev_conditions.append(Activity.sport_type == sport_type)

        result = await self.db.execute(
            select(
                func.count(Activity.id).label("count"),
                func.coalesce(func.sum(Activity.distance_meters), 0).label("distance"),
                func.coalesce(func.sum(Activity.duration_seconds), 0).label("duration"),
                func.coalesce(func.sum(Activity.calories_burned), 0).label("calories"),
            ).where(and_(*prev_conditions))
        )
        row = result.one()

        previous_week = PeriodSummary(
            period_start=last_monday.date(),
            period_end=this_monday.date(),
            total_activities=row.count or 0,
            total_distance_meters=float(row.distance or 0),
            total_duration_seconds=int(row.duration or 0),
            total_calories=int(row.calories or 0),
            avg_distance_meters=(
                float(row.distance or 0) / row.count if row.count else 0
            ),
            avg_duration_seconds=(
                int(row.duration or 0) / row.count if row.count else 0
            ),
            avg_pace_per_km=None,
            sports_breakdown={},
        )

        # Calculate changes
        distance_change = 0.0
        if previous_week.total_distance_meters > 0:
            distance_change = (
                (current_week.total_distance_meters - previous_week.total_distance_meters)
                / previous_week.total_distance_meters
            ) * 100

        duration_change = 0.0
        if previous_week.total_duration_seconds > 0:
            duration_change = (
                (current_week.total_duration_seconds - previous_week.total_duration_seconds)
                / previous_week.total_duration_seconds
            ) * 100

        return WeeklyTrend(
            current_week=current_week,
            previous_week=previous_week,
            distance_change_percent=distance_change,
            duration_change_percent=duration_change,
            activity_count_change=(
                current_week.total_activities - previous_week.total_activities
            ),
        )

    async def _get_user_sports(self, user_id: str) -> list[str]:
        """Get list of sport types the user has activities for."""
        result = await self.db.execute(
            select(Activity.sport_type)
            .where(Activity.user_id == user_id)
            .distinct()
        )
        return [row[0] for row in result]

    async def _get_max_record(
        self,
        user_id: str,
        sport_type: str,
        field: str,
    ) -> tuple[float, str, datetime] | None:
        """Get maximum value for a field."""
        column = getattr(Activity, field)
        result = await self.db.execute(
            select(column, Activity.id, Activity.started_at)
            .where(
                Activity.user_id == user_id,
                Activity.sport_type == sport_type,
                column.isnot(None),
            )
            .order_by(column.desc())
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1], row[2]) if row else None

    def _get_period_bounds(
        self, period: StatsPeriod
    ) -> tuple[datetime, datetime]:
        """Get date bounds for a period."""
        now = datetime.utcnow()

        if period == StatsPeriod.WEEK:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=7)
        elif period == StatsPeriod.MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
        elif period == StatsPeriod.YEAR:
            start = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end = start.replace(year=now.year + 1)
        else:  # ALL_TIME
            start = datetime(2000, 1, 1)
            end = now + timedelta(days=1)

        return start, end
