"""Pydantic schemas for offline sync."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.activities.schemas import ActivityCreate


class SyncOperation(str, Enum):
    """Types of sync operations."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncItem(BaseModel):
    """A single item to sync."""

    operation: SyncOperation
    entity_type: str  # activity, goal, etc.
    client_id: str = Field(max_length=36)
    server_id: str | None = None  # for updates/deletes
    timestamp: datetime  # when the operation happened on client
    data: dict | None = None  # payload for create/update


class SyncBatchRequest(BaseModel):
    """Request to sync multiple items."""

    client_device_id: str = Field(max_length=100)
    last_sync_timestamp: datetime | None = None
    items: list[SyncItem] = Field(max_length=100)


class SyncItemResult(BaseModel):
    """Result of syncing a single item."""

    client_id: str
    server_id: str | None = None
    success: bool
    error: str | None = None
    conflict: bool = False


class SyncBatchResponse(BaseModel):
    """Response after syncing a batch."""

    synced_at: datetime
    results: list[SyncItemResult]
    server_changes: list[dict] = []  # changes from server since last sync


class ActivityBatchCreate(BaseModel):
    """Batch create activities for offline sync."""

    activities: list[ActivityCreate] = Field(max_length=50)


class ActivityBatchResult(BaseModel):
    """Result of batch activity creation."""

    created: int
    skipped: int  # duplicates by client_id
    errors: list[dict]
