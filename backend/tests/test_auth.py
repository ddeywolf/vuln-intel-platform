"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_user(client: AsyncClient):
    """Registering a new user returns 201 with user details."""
    payload = {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "role": "analyst",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    """Registering with an existing email returns 400."""
    payload = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "role": "viewer",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


async def test_login_success(client: AsyncClient):
    """Logging in with valid credentials returns access and refresh tokens."""
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logintest@example.com", "password": "mypassword123", "role": "viewer"},
    )
    # Login (OAuth2 form data)
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "logintest@example.com", "password": "mypassword123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    """Logging in with wrong password returns 401."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "correctpassword", "role": "viewer"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    """Logging in with an unknown email returns 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient):
    """A valid refresh token returns a new token pair."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "password123", "role": "viewer"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "password123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    resp = await client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
