"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient) -> None:
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Test registration with duplicate email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "full_name": "First User",
    }

    # First registration
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # Duplicate registration
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
            "full_name": "Login User",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    """Test login with wrong password fails."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw@example.com",
            "password": "correctpassword",
            "full_name": "Test User",
        },
    )

    # Try login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpw@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test getting current user profile."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient) -> None:
    """Test token refresh."""
    # Register and get tokens
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "testpassword123",
            "full_name": "Refresh User",
        },
    )
    tokens = response.json()

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
