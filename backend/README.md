# Sports Tracker Backend

FastAPI backend for the Sports Tracker mobile application. Provides REST API endpoints for user authentication, activity tracking, goal management, statistics, and offline sync.

## Features

- **Authentication**: JWT-based auth with email/password and OAuth support
- **Activities**: CRUD for workouts with GPS tracking and metrics
- **Goals**: Fitness goals with automatic progress tracking
- **Statistics**: Weekly/monthly summaries, personal records, trends
- **Offline Sync**: Batch sync support for mobile clients

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installation

```bash
# Clone and enter directory
cd backend

# Install dependencies with uv (creates .venv automatically)
uv sync

# Copy environment config
cp .env.example .env
# Edit .env with your settings
```

<details>
<summary>Alternative: pip installation</summary>

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```
</details>

### Run Development Server

```bash
# Start server with auto-reload (uv)
uv run uvicorn src.main:app --reload

# Or without uv (with activated venv)
uvicorn src.main:app --reload
```

Server runs at `http://localhost:8000`. API docs available at `/docs`.

### Run Tests

```bash
uv run pytest
# or: pytest (with activated venv)
```

## Project Structure

```
backend/
├── src/
│   ├── auth/           # Authentication module
│   ├── activities/     # Activity CRUD
│   ├── goals/          # Goals CRUD
│   ├── statistics/     # Stats & analytics
│   ├── sync/           # Offline sync
│   ├── database/       # Models & connection
│   ├── config.py       # Settings
│   └── main.py         # FastAPI app
├── tests/              # Pytest tests
├── alembic/            # Database migrations
├── requirements.txt
└── pyproject.toml
```

## API Endpoints

### Auth (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login (returns JWT tokens)
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user profile
- `PATCH /me` - Update user profile

### Activities (`/api/v1/activities`)
- `POST /` - Create activity
- `GET /` - List activities (with filters)
- `GET /{id}` - Get activity with GPS points
- `PATCH /{id}` - Update activity
- `DELETE /{id}` - Delete activity
- `POST /{id}/points` - Add GPS points

### Goals (`/api/v1/goals`)
- `POST /` - Create goal
- `GET /` - List goals
- `GET /{id}` - Get goal with progress
- `PATCH /{id}` - Update goal
- `DELETE /{id}` - Delete goal
- `POST /refresh` - Refresh all goal progress

### Statistics (`/api/v1/statistics`)
- `GET /summary` - Period summary (week/month/year)
- `GET /daily` - Daily stats for charts
- `GET /records` - Personal records
- `GET /trend` - Week-over-week trend
- `GET /overview` - Complete stats overview

### Sync (`/api/v1/sync`)
- `POST /batch` - Process offline sync batch
- `POST /activities/batch` - Batch create activities

## Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT signing key | (required) |
| `DATABASE_URL` | Database connection URL | SQLite |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy 2.0 (async)
- **Auth**: python-jose (JWT) + passlib (bcrypt)
- **Validation**: Pydantic v2
- **Testing**: pytest + httpx

## License

MIT
