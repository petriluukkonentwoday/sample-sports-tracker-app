"""Sync API endpoints for offline support."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.activities.schemas import ActivityCreate
from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.database.models import User
from src.sync.schemas import (
    ActivityBatchResult,
    SyncBatchRequest,
    SyncBatchResponse,
)
from src.sync.service import SyncService

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/batch", response_model=SyncBatchResponse)
async def sync_batch(
    batch: SyncBatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SyncBatchResponse:
    """Process a batch of sync operations from offline client.

    This endpoint handles create, update, and delete operations
    for activities that were recorded while the device was offline.
    It also returns any server-side changes since the last sync.
    """
    service = SyncService(db)
    return await service.process_sync_batch(current_user.id, batch)


@router.post(
    "/activities/batch",
    response_model=ActivityBatchResult,
    status_code=status.HTTP_201_CREATED,
)
async def batch_create_activities(
    activities: list[ActivityCreate],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityBatchResult:
    """Create multiple activities in a single request.

    Useful for syncing offline-recorded activities.
    Duplicates (by client_id) are automatically skipped.
    """
    service = SyncService(db)
    created, skipped, errors = await service.batch_create_activities(
        current_user.id, activities
    )

    return ActivityBatchResult(
        created=created,
        skipped=skipped,
        errors=errors,
    )
