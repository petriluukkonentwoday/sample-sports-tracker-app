"""Live tracking API endpoints with WebSocket support."""

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from src.auth.dependencies import get_current_active_user
from src.auth.security import verify_token
from src.database.models import User
from src.live.manager import manager
from src.live.schemas import (
    LiveLocationUpdate,
    LiveSessionList,
    LiveSessionResponse,
    LiveSessionStart,
)

router = APIRouter(prefix="/live", tags=["Live Tracking"])


@router.post(
    "/sessions",
    response_model=LiveSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_live_session(
    data: LiveSessionStart,
    current_user: User = Depends(get_current_active_user),
) -> LiveSessionResponse:
    """Start a new live tracking session.

    This creates a session that others can subscribe to via WebSocket.
    The activity_id should be a new activity being recorded.
    """
    # Check if session already exists
    existing = await manager.get_session(data.activity_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Live session for this activity already exists",
        )

    session = await manager.start_session(
        activity_id=data.activity_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        sport_type=data.sport_type,
        is_public=data.is_public,
        allowed_viewers=data.allowed_viewers,
    )

    return LiveSessionResponse(
        activity_id=session.activity_id,
        user_id=session.user_id,
        user_name=session.user_name,
        sport_type=session.sport_type,
        started_at=session.started_at,
        is_public=session.is_public,
        viewer_count=0,
    )


@router.delete("/sessions/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_live_session(
    activity_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """End a live tracking session.

    This closes all viewer WebSocket connections and removes the session.
    """
    ended = await manager.end_session(activity_id, current_user.id)
    if not ended:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live session not found or not owned by you",
        )


@router.get("/sessions", response_model=LiveSessionList)
async def list_live_sessions(
    current_user: User = Depends(get_current_active_user),
) -> LiveSessionList:
    """List all active live sessions visible to the current user."""
    sessions = await manager.get_active_sessions(viewer_id=current_user.id)

    return LiveSessionList(
        sessions=[
            LiveSessionResponse(
                activity_id=s.activity_id,
                user_id=s.user_id,
                user_name=s.user_name,
                sport_type=s.sport_type,
                started_at=s.started_at,
                is_public=s.is_public,
                last_point=s.last_point,
            )
            for s in sessions
        ]
    )


@router.get("/sessions/{activity_id}", response_model=LiveSessionResponse)
async def get_live_session(
    activity_id: str,
    current_user: User = Depends(get_current_active_user),
) -> LiveSessionResponse:
    """Get details of a specific live session."""
    session = await manager.get_session(activity_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live session not found",
        )

    if not manager.can_view(session, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this session",
        )

    return LiveSessionResponse(
        activity_id=session.activity_id,
        user_id=session.user_id,
        user_name=session.user_name,
        sport_type=session.sport_type,
        started_at=session.started_at,
        is_public=session.is_public,
        last_point=session.last_point,
    )


@router.post("/sessions/{activity_id}/location")
async def push_location_update(
    activity_id: str,
    location: LiveLocationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Push a location update to all viewers of a live session.

    This is called by the mobile app as the user moves.
    The update is broadcast to all connected WebSocket viewers.
    """
    session = await manager.get_session(activity_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the session owner can push location updates",
        )

    viewer_count = await manager.broadcast_location(
        activity_id=activity_id,
        latitude=location.latitude,
        longitude=location.longitude,
        elevation_meters=location.elevation_meters,
        speed_mps=location.speed_mps,
        heart_rate=location.heart_rate,
        timestamp=location.timestamp,
    )

    return {"broadcast_to": viewer_count}


@router.websocket("/ws/{activity_id}")
async def websocket_live_tracking(
    websocket: WebSocket,
    activity_id: str,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint to receive live location updates.

    Connect to this endpoint to watch someone's activity in real-time.
    The map in the UI updates as new GPS points arrive.

    Query params:
        token: JWT access token for authentication

    Messages received:
        - session_info: Initial session state when connected
        - location_update: New GPS point with lat, lng, elevation, etc.
        - viewer_joined/viewer_left: Viewer count changes
        - session_ended: Live session has ended
    """
    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    viewer_id = payload.get("sub")

    # Check session exists and viewer has permission
    session = await manager.get_session(activity_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    if not manager.can_view(session, viewer_id):
        await websocket.close(code=4003, reason="Access denied")
        return

    # Accept connection
    await websocket.accept()

    # Register connection
    connected = await manager.connect(activity_id, websocket)
    if not connected:
        await websocket.close(code=4004, reason="Session no longer active")
        return

    try:
        # Keep connection alive and handle client messages
        while True:
            # Wait for any client messages (ping/pong, etc.)
            data = await websocket.receive_json()

            # Handle ping
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(activity_id, websocket)
