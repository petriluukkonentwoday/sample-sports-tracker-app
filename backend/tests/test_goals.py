"""Tests for goal endpoints."""

from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_goal(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test creating a fitness goal."""
    response = await client.post(
        "/api/v1/goals/",
        headers=auth_headers,
        json={
            "title": "Run 50km this week",
            "goal_type": "distance",
            "sport_type": "running",
            "target_value": 50000,
            "period": "weekly",
            "start_date": datetime.utcnow().isoformat(),
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Run 50km this week"
    assert data["target_value"] == 50000
    assert data["current_value"] == 0
    assert data["progress_percent"] == 0


@pytest.mark.asyncio
async def test_list_goals(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test listing goals."""
    # Create goals
    for i in range(2):
        await client.post(
            "/api/v1/goals/",
            headers=auth_headers,
            json={
                "title": f"Goal {i}",
                "goal_type": "frequency",
                "target_value": 5,
                "period": "weekly",
                "start_date": datetime.utcnow().isoformat(),
            },
        )

    # List
    response = await client.get("/api/v1/goals/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_goal_progress_updates_with_activities(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that goal progress updates when activities are added."""
    now = datetime.utcnow()

    # Create distance goal
    goal_response = await client.post(
        "/api/v1/goals/",
        headers=auth_headers,
        json={
            "title": "Weekly distance goal",
            "goal_type": "distance",
            "sport_type": "running",
            "target_value": 10000,
            "period": "weekly",
            "start_date": now.isoformat(),
        },
    )
    goal_id = goal_response.json()["id"]

    # Add activity
    await client.post(
        "/api/v1/activities/",
        headers=auth_headers,
        json={
            "sport_type": "running",
            "started_at": now.isoformat(),
            "duration_seconds": 1800,
            "distance_meters": 5000,
        },
    )

    # Get goal (triggers progress refresh)
    response = await client.get(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_value"] == 5000
    assert data["progress_percent"] == 50.0


@pytest.mark.asyncio
async def test_update_goal(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a goal."""
    # Create
    create_response = await client.post(
        "/api/v1/goals/",
        headers=auth_headers,
        json={
            "title": "Original Goal",
            "goal_type": "calories",
            "target_value": 1000,
            "period": "daily",
            "start_date": datetime.utcnow().isoformat(),
        },
    )
    goal_id = create_response.json()["id"]

    # Update
    response = await client.patch(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers,
        json={"title": "Updated Goal", "target_value": 2000},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Goal"
    assert response.json()["target_value"] == 2000


@pytest.mark.asyncio
async def test_delete_goal(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a goal."""
    # Create
    create_response = await client.post(
        "/api/v1/goals/",
        headers=auth_headers,
        json={
            "title": "Goal to delete",
            "goal_type": "frequency",
            "target_value": 3,
            "period": "weekly",
            "start_date": datetime.utcnow().isoformat(),
        },
    )
    goal_id = create_response.json()["id"]

    # Delete
    response = await client.delete(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
