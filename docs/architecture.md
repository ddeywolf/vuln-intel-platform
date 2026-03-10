# Architecture Overview

## System Architecture

The Vulnerability Intelligence Platform follows a modern, microservices-inspired architecture with clear separation of concerns.

```
┌────────────────────────────────────────────────────────────────┐
│                         User's Browser                         │
│                   Next.js 15 Frontend (port 3000)              │
└──────────────────────────┬─────────────────────────────────────┘
                           │ HTTPS / REST
┌──────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend (port 8000)                  │
│                                                                │
│   ┌──────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│   │  API Routes  │  │  Services  │  │  Ingestion Modules   │  │
│   │  /api/v1/    │  │ (Business  │  │  nvd, github, osv,   │  │
│   │  vulns       │  │  Logic)    │  │  cisa_kev, epss      │  │
│   │  assets      │  └────────────┘  └──────────────────────┘  │
│   │  alerts      │                                            │
│   │  dashboard   │  ┌────────────┐  ┌──────────────────────┐  │
│   │  auth        │  │ SQLAlchemy │  │  Elasticsearch       │  │
│   └──────────────┘  │  ORM       │  │  Client              │  │
│                     └──────┬─────┘  └──────────┬───────────┘  │
└────────────────────────────┼────────────────────┼─────────────┘
                             │                    │
          ┌──────────────────▼──────┐  ┌──────────▼────────────┐
          │  PostgreSQL (port 5432) │  │ Elasticsearch (9200)   │
          │  Primary data store     │  │ Full-text search index │
          └─────────────────────────┘  └────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Celery Workers                             │
│                                                                 │
│   ┌──────────────────────────┐  ┌───────────────────────────┐  │
│   │      Celery Worker       │  │       Celery Beat         │  │
│   │  (async task execution)  │  │  (periodic task scheduler)│  │
│   └──────────────────────────┘  └───────────────────────────┘  │
│                    │                          │                  │
└────────────────────┼──────────────────────────┼─────────────────┘
                     │                          │
          ┌──────────▼──────────────────────────▼────┐
          │               Redis (port 6379)           │
          │     Task broker + result backend          │
          └───────────────────────────────────────────┘
```

## Component Descriptions

### Frontend (Next.js 15)
- **App Router** pages for dashboard, vulnerabilities, assets, alerts, and login
- **Server components** for data-fetching pages (dashboard, vuln detail)
- **Client components** for interactive pages (vuln list with filters, assets, alerts)
- **Tailwind CSS** for styling
- **Recharts** for data visualization (severity distribution pie chart)

### Backend (FastAPI)
- **API Routes** — versioned REST endpoints under `/api/v1/`
- **Services layer** — business logic separated from route handlers
- **SQLAlchemy async** — non-blocking PostgreSQL queries
- **Pydantic v2** — request validation and response serialization

### Database (PostgreSQL)
Four primary tables:
- `vulnerabilities` — CVE records with CVSS/EPSS scores, KEV status
- `assets` — software inventory with CPE identifiers
- `alerts` — notification rules
- `users` — authenticated user accounts

### Search (Elasticsearch)
- Vulnerability records are indexed for fast full-text search
- `vulnerabilities` index with English-language analyzer on description
- Float fields for range queries on CVSS/EPSS scores

### Task Queue (Celery + Redis)
- **Workers** execute ingestion tasks asynchronously
- **Beat scheduler** triggers periodic tasks on defined schedules
- Redis serves as both broker and result backend

### Ingestion Pipeline

```
External Source (NVD, GitHub, OSV, CISA, EPSS)
        │
        ▼
   fetch() — HTTP request to external API/feed
        │
        ▼
   parse() — Normalize to VulnerabilityCreate schema
        │
        ▼
   sync()  — Upsert to PostgreSQL + index in Elasticsearch
```

## Data Flow

### Ingestion Flow
1. Celery Beat triggers scheduled task (e.g., `sync_nvd` every 2 hours)
2. Task calls `nvd.fetch()` to download CVE data from NVD REST API
3. Each CVE item is passed through `nvd.parse()` to normalize to schema
4. `VulnerabilityService.upsert()` creates or updates the record in PostgreSQL
5. Record is indexed in Elasticsearch for search

### API Request Flow
1. Next.js frontend sends HTTP request to FastAPI backend
2. FastAPI validates request with Pydantic schemas
3. Route handler calls service layer for business logic
4. Service queries PostgreSQL via SQLAlchemy async session
5. Response serialized through Pydantic and returned as JSON

### Authentication Flow
1. User submits email/password to `POST /api/v1/auth/login`
2. `AuthService.authenticate()` verifies credentials with bcrypt
3. JWT access token (30 min) + refresh token (7 days) issued
4. Frontend stores tokens in localStorage
5. Subsequent API requests include `Authorization: Bearer <token>` header

## Security Considerations
- Passwords hashed with bcrypt (via passlib)
- JWT tokens signed with HMAC-SHA256
- Short-lived access tokens (30 min) with refresh token rotation
- CORS restricted to frontend origin
- No secrets in source code — all config via environment variables
- SQL injection protected by SQLAlchemy ORM parameterization
