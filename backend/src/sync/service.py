"""Sync service for offline support."""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.activities.schemas import ActivityCreate
from src.activities.service import ActivityService
from src.database.models import Activity
from src.sync.schemas import (
    SyncBatchRequest,
    SyncBatchResponse,
    SyncItem,
    SyncItemResult,
    SyncOperation,
)


class SyncService:
    """Service for handling offline sync operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def process_sync_batch(
        self,
        user_id: str,
        batch: SyncBatchRequest,
    ) -> SyncBatchResponse:
        """Process a batch of sync operations."""
        results = []

        for item in batch.items:
            result = await self._process_sync_item(user_id, item)
            results.append(result)

        # Get server changes since last sync
        server_changes = []
        if batch.last_sync_timestamp:
            server_changes = await self._get_server_changes(
                user_id, batch.last_sync_timestamp
            )

        return SyncBatchResponse(
            synced_at=datetime.utcnow(),
            results=results,
            server_changes=server_changes,
        )

    async def batch_create_activities(
        self,
        user_id: str,
        activities: list[ActivityCreate],
    ) -> tuple[int, int, list[dict]]:
        """Create multiple activities, skipping duplicates."""
        created = 0
        skipped = 0
        errors = []

        activity_service = ActivityService(self.db)

        for activity_data in activities:
            try:
                await activity_service.create_activity(user_id, activity_data)
                created += 1
            except ValueError as exc:
                if "already exists" in str(exc):
                    skipped += 1
                else:
                    errors.append({
                        "client_id": activity_data.client_id,
                        "error": str(exc),
                    })

        return created, skipped, errors

    async def _process_sync_item(
        self,
        user_id: str,
        item: SyncItem,
    ) -> SyncItemResult:
        """Process a single sync item."""
        try:
            if item.entity_type == "activity":
                return await self._sync_activity(user_id, item)
            else:
                return SyncItemResult(
                    client_id=item.client_id,
                    success=False,
                    error=f"Unknown entity type: {item.entity_type}",
                )
        except Exception as exc:
            return SyncItemResult(
                client_id=item.client_id,
                success=False,
                error=str(exc),
            )

    async def _sync_activity(
        self,
        user_id: str,
        item: SyncItem,
    ) -> SyncItemResult:
        """Sync an activity operation."""
        activity_service = ActivityService(self.db)

        if item.operation == SyncOperation.CREATE:
            # Check for existing by client_id
            existing = await self._get_activity_by_client_id(
                user_id, item.client_id
            )
            if existing:
                # Already synced - return existing server ID
                return SyncItemResult(
                    client_id=item.client_id,
                    server_id=existing.id,
                    success=True,
                    conflict=False,
                )

            # Create new activity
            if not item.data:
                return SyncItemResult(
                    client_id=item.client_id,
                    success=False,
                    error="No data provided for create operation",
                )

            activity_data = ActivityCreate(**item.data)
            activity_data.client_id = item.client_id
            activity = await activity_service.create_activity(user_id, activity_data)

            return SyncItemResult(
                client_id=item.client_id,
                server_id=activity.id,
                success=True,
            )

        elif item.operation == SyncOperation.UPDATE:
            if not item.server_id:
                return SyncItemResult(
                    client_id=item.client_id,
                    success=False,
                    error="server_id required for update",
                )

            activity = await activity_service.get_activity(item.server_id, user_id)
            if not activity:
                return SyncItemResult(
                    client_id=item.client_id,
                    success=False,
                    error="Activity not found",
                )

            # Check for conflicts (server updated after client timestamp)
            if activity.updated_at > item.timestamp:
                return SyncItemResult(
                    client_id=item.client_id,
                    server_id=item.server_id,
                    success=False,
                    conflict=True,
                    error="Server version is newer",
                )

            # Apply updates
            if item.data:
                for field, value in item.data.items():
                    if hasattr(activity, field):
                        setattr(activity, field, value)

            return SyncItemResult(
                client_id=item.client_id,
                server_id=item.server_id,
                success=True,
            )

        elif item.operation == SyncOperation.DELETE:
            if not item.server_id:
                return SyncItemResult(
                    client_id=item.client_id,
                    success=False,
                    error="server_id required for delete",
                )

            deleted = await activity_service.delete_activity(item.server_id, user_id)
            return SyncItemResult(
                client_id=item.client_id,
                server_id=item.server_id,
                success=deleted,
                error=None if deleted else "Activity not found",
            )

        return SyncItemResult(
            client_id=item.client_id,
            success=False,
            error=f"Unknown operation: {item.operation}",
        )

    async def _get_activity_by_client_id(
        self,
        user_id: str,
        client_id: str,
    ) -> Activity | None:
        """Find activity by client_id."""
        result = await self.db.execute(
            select(Activity).where(
                Activity.user_id == user_id,
                Activity.client_id == client_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_server_changes(
        self,
        user_id: str,
        since: datetime,
    ) -> list[dict]:
        """Get activities modified on server since timestamp."""
        result = await self.db.execute(
            select(Activity).where(
                and_(
                    Activity.user_id == user_id,
                    Activity.updated_at > since,
                )
            )
        )
        activities = result.scalars().all()

        return [
            {
                "entity_type": "activity",
                "server_id": a.id,
                "client_id": a.client_id,
                "updated_at": a.updated_at.isoformat(),
                "data": {
                    "sport_type": a.sport_type,
                    "title": a.title,
                    "distance_meters": a.distance_meters,
                    "duration_seconds": a.duration_seconds,
                    "calories_burned": a.calories_burned,
                },
            }
            for a in activities
        ]
