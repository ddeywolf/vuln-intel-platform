"""Vulnerability CRUD and search API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityResponse, VulnerabilityUpdate
from app.services.vulnerability_service import VulnerabilityService
from app.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[VulnerabilityResponse])
async def list_vulnerabilities(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    severity: str | None = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    source: str | None = Query(None, description="Filter by source (nvd, github, osv, cisa)"),
    search: str | None = Query(None, description="Full-text search term"),
    cisa_kev: bool | None = Query(None, description="Filter by CISA KEV status"),
    exploit_available: bool | None = Query(None, description="Filter by exploit availability"),
):
    """Return a paginated list of vulnerabilities with optional filters."""
    service = VulnerabilityService(db)
    return await service.list(
        pagination=pagination,
        severity=severity,
        source=source,
        search=search,
        cisa_kev=cisa_kev,
        exploit_available=exploit_available,
    )


@router.post("", response_model=VulnerabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_vulnerability(
    payload: VulnerabilityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new vulnerability record."""
    service = VulnerabilityService(db)
    return await service.create(payload)


@router.get("/{cve_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    cve_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return vulnerability detail by CVE ID."""
    service = VulnerabilityService(db)
    vuln = await service.get_by_cve_id(cve_id)
    if vuln is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerability not found")
    return vuln


@router.patch("/{cve_id}", response_model=VulnerabilityResponse)
async def update_vulnerability(
    cve_id: str,
    payload: VulnerabilityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update a vulnerability record."""
    service = VulnerabilityService(db)
    vuln = await service.update(cve_id, payload)
    if vuln is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerability not found")
    return vuln


@router.delete("/{cve_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vulnerability(
    cve_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a vulnerability record."""
    service = VulnerabilityService(db)
    deleted = await service.delete(cve_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerability not found")
