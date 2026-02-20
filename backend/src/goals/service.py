"""Goals service layer."""

from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Activity, Goal
from src.goals.schemas import GoalCreate, GoalPeriod, GoalType, GoalUpdate


class GoalService:
    """Service for goal CRUD and progress tracking."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_goal(self, user_id: str, data: GoalCreate) -> Goal:
        """Create a new fitness goal."""
        goal = Goal(
            user_id=user_id,
            title=data.title,
            goal_type=data.goal_type.value,
            sport_type=data.sport_type,
            target_value=data.target_value,
            current_value=0.0,
            period=data.period.value,
            start_date=data.start_date,
            end_date=data.end_date,
            reminder_enabled=data.reminder_enabled,
            reminder_time=data.reminder_time,
            reminder_days=data.reminder_days,
        )
        self.db.add(goal)
        await self.db.flush()

        # Calculate initial progress
        await self.update_goal_progress(goal)

        return goal

    async def get_goal(self, goal_id: str, user_id: str) -> Goal | None:
        """Get a single goal by ID."""
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_goals(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> list[Goal]:
        """List all goals for a user."""
        conditions = [Goal.user_id == user_id]
        if active_only:
            conditions.append(Goal.is_active == True)  # noqa: E712

        result = await self.db.execute(
            select(Goal)
            .where(and_(*conditions))
            .order_by(Goal.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_goal(
        self,
        goal_id: str,
        user_id: str,
        data: GoalUpdate,
    ) -> Goal | None:
        """Update a goal."""
        goal = await self.get_goal(goal_id, user_id)
        if not goal:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        return goal

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal."""
        goal = await self.get_goal(goal_id, user_id)
        if not goal:
            return False

        await self.db.delete(goal)
        return True

    async def update_goal_progress(self, goal: Goal) -> None:
        """Recalculate goal progress from activities."""
        # Determine date range based on period
        start_date, end_date = self._get_period_dates(goal)

        # Build activity query
        conditions = [
            Activity.user_id == goal.user_id,
            Activity.started_at >= start_date,
        ]
        if end_date:
            conditions.append(Activity.started_at <= end_date)
        if goal.sport_type:
            conditions.append(Activity.sport_type == goal.sport_type)

        # Calculate progress based on goal type
        goal_type = GoalType(goal.goal_type)

        if goal_type == GoalType.FREQUENCY:
            # Count activities
            result = await self.db.execute(
                select(func.count(Activity.id)).where(and_(*conditions))
            )
            goal.current_value = float(result.scalar() or 0)

        elif goal_type == GoalType.DISTANCE:
            # Sum distances
            result = await self.db.execute(
                select(func.sum(Activity.distance_meters)).where(and_(*conditions))
            )
            goal.current_value = float(result.scalar() or 0)

        elif goal_type == GoalType.DURATION:
            # Sum durations
            result = await self.db.execute(
                select(func.sum(Activity.duration_seconds)).where(and_(*conditions))
            )
            goal.current_value = float(result.scalar() or 0)

        elif goal_type == GoalType.CALORIES:
            # Sum calories
            result = await self.db.execute(
                select(func.sum(Activity.calories_burned)).where(and_(*conditions))
            )
            goal.current_value = float(result.scalar() or 0)

        # Check if achieved
        if goal.current_value >= goal.target_value and not goal.is_achieved:
            goal.is_achieved = True
            goal.achieved_at = datetime.utcnow()

    async def refresh_all_goals(self, user_id: str) -> int:
        """Refresh progress for all active goals."""
        goals = await self.list_goals(user_id, active_only=True)
        for goal in goals:
            await self.update_goal_progress(goal)
        return len(goals)

    def _get_period_dates(self, goal: Goal) -> tuple[datetime, datetime | None]:
        """Get start and end dates for goal period calculation."""
        now = datetime.utcnow()
        period = GoalPeriod(goal.period)

        if period == GoalPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == GoalPeriod.WEEKLY:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=7)
        elif period == GoalPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
        elif period == GoalPeriod.YEARLY:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=now.year + 1)
        else:  # CUSTOM
            start = goal.start_date
            end = goal.end_date

        return start, end
