"""Goals API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.database.models import User
from src.goals.schemas import GoalCreate, GoalResponse, GoalUpdate
from src.goals.service import GoalService

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    """Create a new fitness goal."""
    service = GoalService(db)
    goal = await service.create_goal(current_user.id, data)
    return GoalResponse.model_validate(goal)


@router.get("/", response_model=list[GoalResponse])
async def list_goals(
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[GoalResponse]:
    """List all goals for the current user."""
    service = GoalService(db)
    goals = await service.list_goals(current_user.id, active_only=active_only)
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    """Get a single goal by ID."""
    service = GoalService(db)
    goal = await service.get_goal(goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    # Refresh progress before returning
    await service.update_goal_progress(goal)
    return GoalResponse.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    """Update a goal."""
    service = GoalService(db)
    goal = await service.update_goal(goal_id, current_user.id, data)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a goal."""
    service = GoalService(db)
    deleted = await service.delete_goal(goal_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )


@router.post("/refresh", response_model=dict)
async def refresh_all_goals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Refresh progress for all active goals."""
    service = GoalService(db)
    count = await service.refresh_all_goals(current_user.id)
    return {"refreshed_goals": count}
