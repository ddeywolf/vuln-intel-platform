# API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Authentication

### POST /auth/register
Register a new user account.

**Request body:**
```json
{
  "email": "analyst@example.com",
  "password": "securepassword",
  "full_name": "Jane Analyst",
  "role": "analyst"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "analyst@example.com",
  "full_name": "Jane Analyst",
  "role": "analyst",
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "last_login_at": null
}
```

---

### POST /auth/login
Authenticate and receive JWT tokens. Uses OAuth2 form data.

**Request form data:**
```
username=analyst@example.com&password=securepassword
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer"
}
```

---

### POST /auth/refresh
Refresh an access token using a valid refresh token.

**Query parameter:** `?refresh_token=<token>`

**Response (200):** Same as `/auth/login`

---

## Vulnerabilities

### GET /vulnerabilities
List vulnerabilities with optional filtering and pagination.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 25, max: 100) |
| `severity` | string | Filter: CRITICAL, HIGH, MEDIUM, LOW |
| `source` | string | Filter: nvd, github, osv, cisa |
| `search` | string | Full-text search in CVE ID or description |
| `cisa_kev` | bool | Filter: only CISA KEV entries |
| `exploit_available` | bool | Filter: only entries with known exploits |

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "cve_id": "CVE-2024-12345",
      "source": "nvd",
      "description": "A critical remote code execution vulnerability...",
      "severity": "CRITICAL",
      "cvss_score": 9.8,
      "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "epss_score": 0.94312,
      "epss_percentile": 0.99721,
      "risk_score": 9.5,
      "exploit_available": true,
      "cisa_kev": true,
      "cisa_kev_date_added": "2024-01-10T00:00:00Z",
      "published_date": "2024-01-08T00:00:00Z",
      "modified_date": "2024-01-12T00:00:00Z",
      "references": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2024-12345"}],
      "affected_products": [{"package": "example-lib", "ecosystem": "PyPI"}],
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 25,
  "total_pages": 50,
  "has_next": true,
  "has_prev": false
}
```

---

### POST /vulnerabilities
Create a new vulnerability record.

**Request body:**
```json
{
  "cve_id": "CVE-2024-99999",
  "source": "manual",
  "description": "Description of the vulnerability",
  "severity": "HIGH",
  "cvss_score": 8.1,
  "exploit_available": false,
  "cisa_kev": false
}
```

**Response (201):** Full `VulnerabilityResponse` object.

---

### GET /vulnerabilities/{cve_id}
Get a single vulnerability by CVE ID.

**Path parameter:** `cve_id` — e.g., `CVE-2024-12345`

**Response (200):** Full `VulnerabilityResponse` object.

**Response (404):** `{"detail": "Vulnerability not found"}`

---

### PATCH /vulnerabilities/{cve_id}
Partially update a vulnerability.

**Request body** (all fields optional):
```json
{
  "exploit_available": true,
  "epss_score": 0.85
}
```

**Response (200):** Updated `VulnerabilityResponse` object.

---

### DELETE /vulnerabilities/{cve_id}
Delete a vulnerability record.

**Response (204):** No content.

---

## Assets

### GET /assets
List assets with pagination.

**Response (200):** Paginated `AssetResponse` list.

---

### POST /assets
Create a new asset.

**Request body:**
```json
{
  "name": "Apache HTTP Server",
  "vendor": "Apache",
  "version": "2.4.51",
  "asset_type": "application",
  "cpe": "cpe:2.3:a:apache:http_server:2.4.51:*:*:*:*:*:*:*"
}
```

**Response (201):** Full `AssetResponse` object.

---

### GET /assets/{id}
Get a single asset by ID.

---

### PATCH /assets/{id}
Partially update an asset.

---

### DELETE /assets/{id}
Delete an asset.

---

## Alerts

### GET /alerts
List alert rules with pagination.

**Response (200):** Paginated `AlertResponse` list.

---

### POST /alerts
Create a new alert rule.

**Request body:**
```json
{
  "name": "Critical CVEs in Production",
  "description": "Alert when CRITICAL CVEs are published",
  "criteria": {
    "severity": ["CRITICAL"],
    "keywords": ["apache", "nginx"]
  },
  "severity_threshold": "CRITICAL",
  "notification_channel": "email",
  "notification_target": "security-team@example.com",
  "is_active": true
}
```

**Response (201):** Full `AlertResponse` object.

---

### GET /alerts/{id}
Get a single alert rule by ID.

---

### PATCH /alerts/{id}
Partially update an alert rule (e.g., enable/disable).

---

### DELETE /alerts/{id}
Delete an alert rule.

---

## Dashboard

### GET /dashboard/stats
Get aggregate platform statistics for the dashboard.

**Response (200):**
```json
{
  "total_vulnerabilities": 45832,
  "critical_count": 1243,
  "high_count": 8921,
  "cisa_kev_count": 1098,
  "exploit_available_count": 3412,
  "assets_monitored": 42,
  "active_alerts": 7,
  "severity_distribution": {
    "CRITICAL": 1243,
    "HIGH": 8921,
    "MEDIUM": 22145,
    "LOW": 13423
  },
  "source_distribution": {
    "nvd": 42100,
    "github": 2800,
    "osv": 932
  },
  "recent_vulnerabilities": [
    {
      "id": 45832,
      "cve_id": "CVE-2024-99998",
      "description": "Remote code execution in...",
      "severity": "CRITICAL",
      "cvss_score": 9.8,
      "published_date": "2024-03-10T00:00:00Z",
      "cisa_kev": false
    }
  ]
}
```

---

## Health

### GET /health
Check API health status.

**Response (200):**
```json
{"status": "ok", "version": "1.0.0"}
```

---

## Error Responses

All errors follow the RFC 7807 problem format:

```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes:
- `400 Bad Request` — Invalid input or duplicate resource
- `401 Unauthorized` — Missing or invalid token
- `403 Forbidden` — Insufficient permissions
- `404 Not Found` — Resource does not exist
- `422 Unprocessable Entity` — Request validation failed
- `500 Internal Server Error` — Unexpected server error
