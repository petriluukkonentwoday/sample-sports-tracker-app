"""WebSocket connection manager for live tracking."""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LiveSession:
    """Active live tracking session."""

    activity_id: str
    user_id: str
    user_name: str
    sport_type: str
    started_at: datetime
    is_public: bool = False
    allowed_viewers: set[str] = field(default_factory=set)
    last_point: dict | None = None


class ConnectionManager:
    """Manages WebSocket connections for live activity tracking."""

    def __init__(self) -> None:
        # activity_id -> set of WebSocket connections
        self._connections: dict[str, set] = defaultdict(set)
        # activity_id -> LiveSession
        self._sessions: dict[str, LiveSession] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def start_session(
        self,
        activity_id: str,
        user_id: str,
        user_name: str,
        sport_type: str,
        is_public: bool = False,
        allowed_viewers: list[str] | None = None,
    ) -> LiveSession:
        """Start a new live tracking session."""
        async with self._lock:
            session = LiveSession(
                activity_id=activity_id,
                user_id=user_id,
                user_name=user_name,
                sport_type=sport_type,
                started_at=datetime.utcnow(),
                is_public=is_public,
                allowed_viewers=set(allowed_viewers or []),
            )
            self._sessions[activity_id] = session
            return session

    async def end_session(self, activity_id: str, user_id: str) -> bool:
        """End a live tracking session."""
        async with self._lock:
            session = self._sessions.get(activity_id)
            if not session or session.user_id != user_id:
                return False

            # Notify all viewers that session ended
            await self._broadcast(
                activity_id,
                {
                    "type": "session_ended",
                    "activity_id": activity_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # Close all connections
            for websocket in list(self._connections[activity_id]):
                try:
                    await websocket.close()
                except Exception:
                    pass

            del self._sessions[activity_id]
            self._connections.pop(activity_id, None)
            return True

    async def get_session(self, activity_id: str) -> LiveSession | None:
        """Get a live session by activity ID."""
        return self._sessions.get(activity_id)

    async def get_active_sessions(
        self,
        viewer_id: str | None = None,
    ) -> list[LiveSession]:
        """Get list of active live sessions visible to a viewer."""
        sessions = []
        for session in self._sessions.values():
            if session.is_public:
                sessions.append(session)
            elif viewer_id and viewer_id in session.allowed_viewers:
                sessions.append(session)
            elif viewer_id and viewer_id == session.user_id:
                sessions.append(session)
        return sessions

    def can_view(self, session: LiveSession, viewer_id: str | None) -> bool:
        """Check if a viewer can access a live session."""
        if session.is_public:
            return True
        if viewer_id is None:
            return False
        if viewer_id == session.user_id:
            return True
        return viewer_id in session.allowed_viewers

    async def connect(self, activity_id: str, websocket) -> bool:
        """Add a WebSocket connection to a live session."""
        session = self._sessions.get(activity_id)
        if not session:
            return False

        async with self._lock:
            self._connections[activity_id].add(websocket)

        # Send current state to new viewer
        await websocket.send_json({
            "type": "session_info",
            "activity_id": activity_id,
            "user_name": session.user_name,
            "sport_type": session.sport_type,
            "started_at": session.started_at.isoformat(),
            "last_point": session.last_point,
            "viewer_count": len(self._connections[activity_id]),
        })

        # Notify others about new viewer
        await self._broadcast(
            activity_id,
            {
                "type": "viewer_joined",
                "viewer_count": len(self._connections[activity_id]),
            },
            exclude=websocket,
        )

        return True

    async def disconnect(self, activity_id: str, websocket) -> None:
        """Remove a WebSocket connection from a live session."""
        async with self._lock:
            self._connections[activity_id].discard(websocket)

        # Notify others about viewer leaving
        if activity_id in self._sessions:
            await self._broadcast(
                activity_id,
                {
                    "type": "viewer_left",
                    "viewer_count": len(self._connections[activity_id]),
                },
            )

    async def broadcast_location(
        self,
        activity_id: str,
        latitude: float,
        longitude: float,
        elevation_meters: float | None = None,
        speed_mps: float | None = None,
        heart_rate: int | None = None,
        timestamp: datetime | None = None,
    ) -> int:
        """Broadcast a location update to all viewers."""
        session = self._sessions.get(activity_id)
        if not session:
            return 0

        point = {
            "latitude": latitude,
            "longitude": longitude,
            "elevation_meters": elevation_meters,
            "speed_mps": speed_mps,
            "heart_rate": heart_rate,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        }

        # Update last point in session
        session.last_point = point

        message = {
            "type": "location_update",
            "activity_id": activity_id,
            "point": point,
        }

        return await self._broadcast(activity_id, message)

    async def _broadcast(
        self,
        activity_id: str,
        message: dict,
        exclude=None,
    ) -> int:
        """Send a message to all connected viewers."""
        connections = self._connections.get(activity_id, set())
        sent_count = 0

        for websocket in list(connections):
            if websocket == exclude:
                continue
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception:
                # Connection failed, remove it
                async with self._lock:
                    self._connections[activity_id].discard(websocket)

        return sent_count


# Global connection manager instance
manager = ConnectionManager()
