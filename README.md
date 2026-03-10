# 🛡️ Vulnerability Intelligence Platform

A comprehensive, production-ready full-stack platform for aggregating, analyzing, and acting on security vulnerability data.

## Features

- **CVE Aggregation** — Ingest from NVD (NIST), GitHub Advisory Database, OSV.dev, CISA KEV, EPSS
- **Risk Scoring** — Composite scoring using CVSS + EPSS + exploit availability + CISA KEV status
- **Dashboard** — Real-time stats: total vulnerabilities, critical/high counts, severity distribution
- **Vulnerability Explorer** — Searchable, filterable table with full CVE detail views
- **Asset Mapping** — Track your software inventory and map known vulnerabilities
- **Alerting** — Configurable alert rules with severity thresholds and notification channels
- **Scheduled Ingestion** — Celery Beat workers keep data fresh automatically
- **JWT Auth** — Secure API with OAuth2/JWT authentication

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+ / FastAPI |
| **Frontend** | React 18 / Next.js 14 / TypeScript / Tailwind CSS |
| **Database** | PostgreSQL 16 (primary), Elasticsearch 8 (search) |
| **Task Queue** | Celery + Redis |
| **Containerization** | Docker + Docker Compose |
| **Auth** | JWT / OAuth2 |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone & configure

```bash
git clone https://github.com/ddeywolf/vuln-intel-platform.git
cd vuln-intel-platform
cp .env.example .env
# Edit .env and set SECRET_KEY, NVD_API_KEY, GITHUB_TOKEN
```

### 2. Start the platform

```bash
docker-compose up --build
```

### 3. Access the services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Elasticsearch | http://localhost:9200 |

### 4. Run database migrations

```bash
docker-compose exec backend alembic upgrade head
```

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

## Project Structure

```
vuln-intel-platform/
├── backend/            # Python FastAPI backend
│   ├── app/
│   │   ├── api/        # Route handlers
│   │   ├── models/     # SQLAlchemy ORM models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   ├── ingestion/  # External data source connectors
│   │   ├── tasks/      # Celery async tasks
│   │   └── utils/      # Shared utilities
│   ├── alembic/        # Database migrations
│   └── tests/          # Pytest test suite
├── frontend/           # Next.js 14 frontend
│   └── src/
│       ├── app/        # Next.js App Router pages
│       ├── components/ # Reusable React components
│       ├── lib/        # API client & utilities
│       └── types/      # TypeScript type definitions
├── docs/               # Architecture & API documentation
└── docker-compose.yml  # Local development environment
```

## Data Sources

| Source | Update Frequency | Description |
|---|---|---|
| [NVD (NIST)](https://nvd.nist.gov/) | Every 2 hours | Primary CVE database |
| [GitHub Advisories](https://github.com/advisories) | Every hour | OSS vulnerability advisories |
| [OSV.dev](https://osv.dev/) | Every 4 hours | Open Source Vulnerability database |
| [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | Daily | Known Exploited Vulnerabilities |
| [EPSS](https://www.first.org/epss/) | Daily | Exploit Prediction Scoring System |

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/vulnerabilities` | List vulnerabilities (paginated, filterable) |
| `GET` | `/api/v1/vulnerabilities/{cve_id}` | Get vulnerability detail |
| `GET/POST` | `/api/v1/assets` | Asset inventory CRUD |
| `GET/POST` | `/api/v1/alerts` | Alert rule CRUD |
| `GET` | `/api/v1/dashboard/stats` | Aggregate dashboard statistics |
| `POST` | `/api/v1/auth/login` | Login / get JWT token |
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/refresh` | Refresh JWT token |

See [`docs/api.md`](docs/api.md) for full API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run tests: `pytest` (backend) and `npm test` (frontend)
5. Submit a pull request

## License

MIT License — see [LICENSE](LICENSE) for details.
