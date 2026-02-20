"""Activities service layer."""

from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.activities.schemas import (
    ActivityCreate,
    ActivityListParams,
    ActivityUpdate,
)
from src.database.models import Activity, ActivityPoint


class ActivityService:
    """Service for activity CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_activity(
        self,
        user_id: str,
        data: ActivityCreate,
    ) -> Activity:
        """Create a new activity record."""
        # Check for duplicate by client_id (offline sync)
        if data.client_id:
            existing = await self.db.execute(
                select(Activity).where(
                    Activity.user_id == user_id,
                    Activity.client_id == data.client_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Activity with this client_id already exists")

        # Calculate pace if distance and duration available
        avg_pace_spm = None
        if data.distance_meters and data.distance_meters > 0 and data.duration_seconds:
            avg_pace_spm = data.duration_seconds / data.distance_meters

        activity = Activity(
            user_id=user_id,
            sport_type=data.sport_type.value,
            title=data.title,
            description=data.description,
            started_at=data.started_at,
            ended_at=data.ended_at,
            duration_seconds=data.duration_seconds,
            active_duration_seconds=data.active_duration_seconds,
            distance_meters=data.distance_meters,
            avg_speed_mps=data.avg_speed_mps,
            max_speed_mps=data.max_speed_mps,
            avg_pace_spm=avg_pace_spm,
            elevation_gain_meters=data.elevation_gain_meters,
            elevation_loss_meters=data.elevation_loss_meters,
            calories_burned=data.calories_burned,
            avg_heart_rate=data.avg_heart_rate,
            max_heart_rate=data.max_heart_rate,
            avg_cadence=data.avg_cadence,
            client_id=data.client_id,
            is_manual_entry=data.is_manual_entry,
            synced_at=datetime.utcnow(),
        )
        self.db.add(activity)
        await self.db.flush()

        # Add GPS points if provided
        if data.points:
            for point_data in data.points:
                point = ActivityPoint(
                    activity_id=activity.id,
                    latitude=point_data.latitude,
                    longitude=point_data.longitude,
                    elevation_meters=point_data.elevation_meters,
                    accuracy_meters=point_data.accuracy_meters,
                    timestamp=point_data.timestamp,
                    speed_mps=point_data.speed_mps,
                    heart_rate=point_data.heart_rate,
                    cadence=point_data.cadence,
                )
                self.db.add(point)

        return activity

    async def get_activity(
        self,
        activity_id: str,
        user_id: str,
        include_points: bool = False,
    ) -> Activity | None:
        """Get a single activity by ID."""
        query = select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == user_id,
        )

        if include_points:
            query = query.options(selectinload(Activity.points))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_activities(
        self,
        user_id: str,
        params: ActivityListParams,
    ) -> tuple[list[Activity], int]:
        """List activities with filtering and pagination."""
        conditions = [Activity.user_id == user_id]

        if params.sport_type:
            conditions.append(Activity.sport_type == params.sport_type.value)
        if params.start_date:
            conditions.append(Activity.started_at >= params.start_date)
        if params.end_date:
            conditions.append(Activity.started_at <= params.end_date)

        # Get total count
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar() or 0

        # Get paginated results
        query = (
            select(Activity)
            .where(and_(*conditions))
            .order_by(Activity.started_at.desc())
            .offset(params.offset)
            .limit(params.limit)
        )
        result = await self.db.execute(query)
        activities = list(result.scalars().all())

        return activities, total_count

    async def update_activity(
        self,
        activity_id: str,
        user_id: str,
        data: ActivityUpdate,
    ) -> Activity | None:
        """Update an activity."""
        activity = await self.get_activity(activity_id, user_id)
        if not activity:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "sport_type" and value is not None:
                setattr(activity, field, value.value)
            else:
                setattr(activity, field, value)

        return activity

    async def delete_activity(
        self,
        activity_id: str,
        user_id: str,
    ) -> bool:
        """Delete an activity."""
        activity = await self.get_activity(activity_id, user_id)
        if not activity:
            return False

        await self.db.delete(activity)
        return True

    async def add_points_to_activity(
        self,
        activity_id: str,
        user_id: str,
        points: list[dict],
    ) -> int:
        """Add GPS points to an existing activity."""
        activity = await self.get_activity(activity_id, user_id)
        if not activity:
            raise ValueError("Activity not found")

        count = 0
        for point_data in points:
            point = ActivityPoint(activity_id=activity_id, **point_data)
            self.db.add(point)
            count += 1

        return count
