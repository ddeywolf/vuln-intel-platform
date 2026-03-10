"""Tests for asset API endpoints."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_list_assets_empty(client: AsyncClient):
    """Listing assets returns empty result initially."""
    resp = await client.get("/api/v1/assets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


async def test_create_asset(client: AsyncClient):
    """Creating an asset returns 201 with the created record."""
    payload = {
        "name": "Apache HTTP Server",
        "vendor": "Apache",
        "version": "2.4.51",
        "asset_type": "application",
        "cpe": "cpe:2.3:a:apache:http_server:2.4.51:*:*:*:*:*:*:*",
    }
    resp = await client.post("/api/v1/assets", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Apache HTTP Server"
    assert data["vendor"] == "Apache"
    assert data["id"] is not None


async def test_get_asset(client: AsyncClient):
    """Retrieving an asset by ID returns the correct record."""
    # Create
    payload = {"name": "OpenSSL", "vendor": "OpenSSL Foundation", "version": "3.0.0",
               "asset_type": "library"}
    create_resp = await client.post("/api/v1/assets", json=payload)
    asset_id = create_resp.json()["id"]

    # Get
    resp = await client.get(f"/api/v1/assets/{asset_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "OpenSSL"


async def test_get_asset_not_found(client: AsyncClient):
    """Requesting a non-existent asset returns 404."""
    resp = await client.get("/api/v1/assets/999999")
    assert resp.status_code == 404


async def test_update_asset(client: AsyncClient):
    """Patching an asset updates its version field."""
    payload = {"name": "Nginx", "version": "1.24.0", "asset_type": "application"}
    create_resp = await client.post("/api/v1/assets", json=payload)
    asset_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/v1/assets/{asset_id}", json={"version": "1.25.0"})
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.25.0"


async def test_delete_asset(client: AsyncClient):
    """Deleting an asset returns 204 and subsequent GET returns 404."""
    payload = {"name": "Test App", "asset_type": "application"}
    create_resp = await client.post("/api/v1/assets", json=payload)
    asset_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/assets/{asset_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/assets/{asset_id}")
    assert get_resp.status_code == 404
