"""Tests for vulnerability API endpoints."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_list_vulnerabilities_empty(client: AsyncClient):
    """Listing vulnerabilities returns an empty paginated result initially."""
    resp = await client.get("/api/v1/vulnerabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1


async def test_create_vulnerability(client: AsyncClient):
    """Creating a vulnerability returns 201 with the created record."""
    payload = {
        "cve_id": "CVE-2024-99999",
        "source": "nvd",
        "description": "Test vulnerability for unit testing.",
        "severity": "HIGH",
        "cvss_score": 8.1,
        "exploit_available": False,
        "cisa_kev": False,
    }
    resp = await client.post("/api/v1/vulnerabilities", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["cve_id"] == "CVE-2024-99999"
    assert data["severity"] == "HIGH"
    assert data["id"] is not None


async def test_get_vulnerability_by_cve_id(client: AsyncClient):
    """Retrieving a vulnerability by CVE ID returns the correct record."""
    # Create first
    payload = {
        "cve_id": "CVE-2024-88888",
        "source": "nvd",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "exploit_available": True,
        "cisa_kev": True,
    }
    create_resp = await client.post("/api/v1/vulnerabilities", json=payload)
    assert create_resp.status_code == 201

    # Get by ID
    resp = await client.get("/api/v1/vulnerabilities/CVE-2024-88888")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cve_id"] == "CVE-2024-88888"
    assert data["cisa_kev"] is True


async def test_get_vulnerability_not_found(client: AsyncClient):
    """Requesting a non-existent CVE returns 404."""
    resp = await client.get("/api/v1/vulnerabilities/CVE-9999-00000")
    assert resp.status_code == 404


async def test_update_vulnerability(client: AsyncClient):
    """Patching a vulnerability updates its fields."""
    # Create
    payload = {
        "cve_id": "CVE-2024-77777",
        "source": "github",
        "severity": "MEDIUM",
        "cvss_score": 5.5,
        "exploit_available": False,
        "cisa_kev": False,
    }
    await client.post("/api/v1/vulnerabilities", json=payload)

    # Update
    update = {"exploit_available": True, "severity": "HIGH"}
    resp = await client.patch("/api/v1/vulnerabilities/CVE-2024-77777", json=update)
    assert resp.status_code == 200
    data = resp.json()
    assert data["exploit_available"] is True
    assert data["severity"] == "HIGH"


async def test_delete_vulnerability(client: AsyncClient):
    """Deleting a vulnerability returns 204 and subsequent GET returns 404."""
    payload = {
        "cve_id": "CVE-2024-66666",
        "source": "osv",
        "severity": "LOW",
        "exploit_available": False,
        "cisa_kev": False,
    }
    await client.post("/api/v1/vulnerabilities", json=payload)

    resp = await client.delete("/api/v1/vulnerabilities/CVE-2024-66666")
    assert resp.status_code == 204

    get_resp = await client.get("/api/v1/vulnerabilities/CVE-2024-66666")
    assert get_resp.status_code == 404


async def test_filter_by_severity(client: AsyncClient):
    """Filtering vulnerabilities by severity returns only matching records."""
    # Create two vulnerabilities with different severities
    await client.post(
        "/api/v1/vulnerabilities",
        json={"cve_id": "CVE-2024-55551", "source": "nvd", "severity": "CRITICAL",
              "exploit_available": False, "cisa_kev": False},
    )
    await client.post(
        "/api/v1/vulnerabilities",
        json={"cve_id": "CVE-2024-55552", "source": "nvd", "severity": "LOW",
              "exploit_available": False, "cisa_kev": False},
    )

    resp = await client.get("/api/v1/vulnerabilities?severity=CRITICAL")
    assert resp.status_code == 200
    data = resp.json()
    assert all(v["severity"] == "CRITICAL" for v in data["items"])
