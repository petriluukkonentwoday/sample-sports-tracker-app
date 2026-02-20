"""Activities API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.activities.schemas import (
    ActivityCreate,
    ActivityDetailResponse,
    ActivityListParams,
    ActivityPointCreate,
    ActivityResponse,
    ActivityUpdate,
    SportType,
)
from src.activities.service import ActivityService
from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.database.models import User

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    data: ActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    """Create a new activity."""
    service = ActivityService(db)

    try:
        activity = await service.create_activity(current_user.id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ActivityResponse.model_validate(activity)


@router.get("/", response_model=list[ActivityResponse])
async def list_activities(
    sport_type: SportType | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[ActivityResponse]:
    """List activities with optional filtering."""
    service = ActivityService(db)
    params = ActivityListParams(
        sport_type=sport_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    activities, _ = await service.list_activities(current_user.id, params)
    return [ActivityResponse.model_validate(a) for a in activities]


@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity(
    activity_id: str,
    include_points: bool = Query(default=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityDetailResponse:
    """Get a single activity with GPS points."""
    service = ActivityService(db)
    activity = await service.get_activity(
        activity_id, current_user.id, include_points=include_points
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return ActivityDetailResponse.model_validate(activity)


@router.patch("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    """Update an activity."""
    service = ActivityService(db)
    activity = await service.update_activity(activity_id, current_user.id, data)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return ActivityResponse.model_validate(activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an activity."""
    service = ActivityService(db)
    deleted = await service.delete_activity(activity_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )


@router.post("/{activity_id}/points", status_code=status.HTTP_201_CREATED)
async def add_activity_points(
    activity_id: str,
    points: list[ActivityPointCreate],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Add GPS points to an existing activity."""
    service = ActivityService(db)

    try:
        points_data = [p.model_dump() for p in points]
        count = await service.add_points_to_activity(
            activity_id, current_user.id, points_data
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"added_points": count}
