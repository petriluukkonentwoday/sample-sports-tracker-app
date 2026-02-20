"""Tests for live tracking endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_live_session(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test starting a live tracking session."""
    response = await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "test-activity-123",
            "sport_type": "running",
            "is_public": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["activity_id"] == "test-activity-123"
    assert data["sport_type"] == "running"
    assert data["is_public"] is True
    assert data["viewer_count"] == 0


@pytest.mark.asyncio
async def test_start_duplicate_session_fails(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that starting a duplicate session fails."""
    # Start first session
    await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "duplicate-test",
            "sport_type": "cycling",
            "is_public": True,
        },
    )

    # Try to start duplicate
    response = await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "duplicate-test",
            "sport_type": "cycling",
            "is_public": True,
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_live_sessions(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test listing active live sessions."""
    # Start a public session
    await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "list-test-session",
            "sport_type": "running",
            "is_public": True,
        },
    )

    # List sessions
    response = await client.get("/api/v1/live/sessions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) >= 1

    session_ids = [s["activity_id"] for s in data["sessions"]]
    assert "list-test-session" in session_ids


@pytest.mark.asyncio
async def test_get_live_session(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test getting a specific live session."""
    # Start session
    await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "get-test-session",
            "sport_type": "hiking",
            "is_public": True,
        },
    )

    # Get session details
    response = await client.get(
        "/api/v1/live/sessions/get-test-session",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["activity_id"] == "get-test-session"
    assert data["sport_type"] == "hiking"


@pytest.mark.asyncio
async def test_push_location_update(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test pushing a location update to a live session."""
    # Start session
    await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "location-test",
            "sport_type": "running",
            "is_public": True,
        },
    )

    # Push location
    response = await client.post(
        "/api/v1/live/sessions/location-test/location",
        headers=auth_headers,
        json={
            "latitude": 60.1699,
            "longitude": 24.9384,
            "elevation_meters": 25.5,
            "speed_mps": 3.5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "broadcast_to" in data


@pytest.mark.asyncio
async def test_end_live_session(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test ending a live session."""
    # Start session
    await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "end-test-session",
            "sport_type": "skiing",
            "is_public": True,
        },
    )

    # End session
    response = await client.delete(
        "/api/v1/live/sessions/end-test-session",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify session is gone
    get_response = await client.get(
        "/api/v1/live/sessions/end-test-session",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_private_session_access(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that private sessions are only visible to allowed viewers."""
    # Start private session (no allowed viewers)
    response = await client.post(
        "/api/v1/live/sessions",
        headers=auth_headers,
        json={
            "activity_id": "private-session",
            "sport_type": "running",
            "is_public": False,
            "allowed_viewers": [],
        },
    )

    assert response.status_code == 201

    # Owner can still access it
    get_response = await client.get(
        "/api/v1/live/sessions/private-session",
        headers=auth_headers,
    )
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_location_update_session_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test pushing location to non-existent session."""
    response = await client.post(
        "/api/v1/live/sessions/nonexistent/location",
        headers=auth_headers,
        json={
            "latitude": 60.0,
            "longitude": 24.0,
        },
    )

    assert response.status_code == 404
