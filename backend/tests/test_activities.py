"""Tests for activity endpoints."""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_activity(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test creating an activity."""
    now = datetime.utcnow()
    response = await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "title": "Morning Run",
            "started_at": now.isoformat(),
            "ended_at": (now + timedelta(hours=1)).isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000,
            "calories_burned": 500,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sport_type"] == "running"
    assert data["title"] == "Morning Run"
    assert data["distance_meters"] == 10000


@pytest.mark.asyncio
async def test_list_activities(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test listing activities."""
    now = datetime.utcnow()

    # Create a few activities
    for i in range(3):
        await client.post(
            "/api/v1/activities/",
            headers=auth_headers,
            json={
                "sport_type": "running",
                "title": f"Run {i}",
                "started_at": (now - timedelta(days=i)).isoformat(),
                "duration_seconds": 1800,
            },
        )

    # List
    response = await client.get("/api/v1/activities/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_filter_activities_by_sport(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test filtering activities by sport type."""
    now = datetime.utcnow()

    # Create running activity
    await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "started_at": now.isoformat(),
            "duration_seconds": 1800,
        },
    )

    # Create cycling activity
    await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "cycling",
            "started_at": now.isoformat(),
            "duration_seconds": 3600,
        },
    )

    # Filter for running only
    response = await client.get(
        "/api/v1/activities/",
        headers=auth_headers,
        params={"sport_type": "running"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sport_type"] == "running"


@pytest.mark.asyncio
async def test_get_activity_detail(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test getting activity details with GPS points."""
    now = datetime.utcnow()

    # Create activity with points
    create_response = await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "started_at": now.isoformat(),
            "duration_seconds": 1800,
            "points": [
                {
                    "latitude": 60.1699,
                    "longitude": 24.9384,
                    "timestamp": now.isoformat(),
                },
                {
                    "latitude": 60.1700,
                    "longitude": 24.9385,
                    "timestamp": (now + timedelta(minutes=1)).isoformat(),
                },
            ],
        },
    )

    activity_id = create_response.json()["id"]

    # Get details
    response = await client.get(
        f"/api/v1/activities/{activity_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["points"]) == 2


@pytest.mark.asyncio
async def test_update_activity(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test updating an activity."""
    now = datetime.utcnow()

    # Create
    create_response = await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "title": "Original Title",
            "started_at": now.isoformat(),
            "duration_seconds": 1800,
        },
    )
    activity_id = create_response.json()["id"]

    # Update
    response = await client.patch(
        f"/api/v1/activities/{activity_id}",
        headers=auth_headers,
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_activity(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting an activity."""
    now = datetime.utcnow()

    # Create
    create_response = await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "started_at": now.isoformat(),
            "duration_seconds": 1800,
        },
    )
    activity_id = create_response.json()["id"]

    # Delete
    response = await client.delete(
        f"/api/v1/activities/{activity_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify deleted
    get_response = await client.get(
        f"/api/v1/activities/{activity_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404
