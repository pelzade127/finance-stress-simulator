# Finance Stress Simulator - Setup Guide

Complete guide to get the backend running on Windows with PowerShell.

## Prerequisites

- Python 3.11+ installed
- PostgreSQL installed and running
- Git installed
- (Optional) Poetry installed (`pip install poetry`)

## Quick Start (10 minutes)

### Step 1: Clone and Navigate

```powershell
git clone <your-repo-url>
cd finance-stress-simulator/backend
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy errors:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

**Option A: Using Poetry (recommended)**
```powershell
poetry install
```

**Option B: Using pip**
```powershell
pip install fastapi uvicorn[standard] sqlmodel psycopg[binary] httpx python-dotenv pydantic pytest pytest-asyncio
```

### Step 4: Set Up Database

#### Install PostgreSQL (if not already installed)
Download from: https://www.postgresql.org/download/windows/

#### Create Database
```powershell
# Open psql (PostgreSQL command line)
psql -U postgres

# Create database
CREATE DATABASE stress_simulator;

# Exit
\q
```

### Step 5: Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your settings
notepad .env
```

**Required settings in `.env`:**
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/stress_simulator
COL_API_BASE_URL=http://localhost:3001
```

Replace `your_password` with your PostgreSQL password.

### Step 6: Run the Application

```powershell
# Make sure you're in backend/ directory with venv activated
python -m app.main
```

You should see:
```
🚀 Starting Finance Stress Simulator API...
📊 Initializing database...
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Test It Works

Open browser to: http://localhost:8000

You should see:
```json
{
  "message": "Finance Stress Simulator API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### Step 8: Explore API Docs

Navigate to: http://localhost:8000/docs

This opens the interactive Swagger UI where you can test all endpoints.

## Testing the API

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Create a Snapshot
```powershell
curl -X POST http://localhost:8000/api/snapshots `
  -H "Content-Type: application/json" `
  -d '{
    "city": "San Francisco, CA",
    "monthly_income_takehome": 6000,
    "emergency_fund_balance": 15000,
    "essential_total": 3500,
    "discretionary_total": 1200,
    "use_col_baseline": false
  }'
```

Save the returned `id` value.

### 3. Run Simulation
```powershell
curl -X POST http://localhost:8000/api/simulate `
  -H "Content-Type: application/json" `
  -d '{
    "snapshot_id": "paste-id-here"
  }'
```

## Running Tests

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest app/tests/test_simulator.py
```

## Common Issues & Solutions

### Issue: "Execution Policy" Error on Windows

**Error:**
```
.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: PostgreSQL Connection Failed

**Error:**
```
connection to server at "localhost" (::1), port 5432 failed
```

**Solutions:**
1. Check PostgreSQL is running:
   ```powershell
   # Check if running
   Get-Service -Name postgresql*
   
   # Start if needed
   Start-Service postgresql-x64-15  # (adjust version number)
   ```

2. Verify connection string in `.env`

3. Test connection manually:
   ```powershell
   psql -U postgres -d stress_simulator
   ```

### Issue: "Module not found" errors

**Solution:**
Make sure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### Issue: COL API not available

**Not a problem!** The app falls back to cached data in `data/col_fallback.json`.

If you want to test with your actual COL API:
1. Make sure your COL Calculator is running
2. Update `COL_API_BASE_URL` in `.env` to point to it

## Project Structure Explained

```
backend/
├── app/
│   ├── core/              # Configuration & database
│   │   ├── config.py      # Environment settings
│   │   └── db.py          # Database connection
│   │
│   ├── models/            # Database models (SQLModel)
│   │   ├── snapshot.py    # Financial snapshot model
│   │   └── run.py         # Simulation run model
│   │
│   ├── domain/            # Business logic (pure Python, no dependencies)
│   │   ├── scenarios.py   # Scenario definitions
│   │   ├── simulator.py   # Core simulation engine
│   │   └── levers.py      # Recommendation calculator
│   │
│   ├── services/          # External integrations
│   │   └── col_client.py  # Cost of Living API client
│   │
│   ├── api/
│   │   └── routes/        # API endpoints
│   │       ├── health.py
│   │       ├── snapshots.py
│   │       └── simulate.py
│   │
│   ├── tests/             # Unit tests
│   │   └── test_simulator.py
│   │
│   └── main.py            # FastAPI application
│
├── data/                  # Static data
│   └── col_fallback.json  # Fallback COL data
│
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Example environment file
└── pyproject.toml         # Python dependencies
```

## Development Workflow

### 1. Adding a New Scenario

Edit `app/domain/scenarios.py`:
```python
DEFAULT_SCENARIOS.append(
    ScenarioDefinition(
        type=ScenarioType.NEW_SCENARIO,
        name="My New Scenario",
        description="Description here",
        default_params={"param1": value1}
    )
)
```

Update `app/domain/simulator.py` to handle the new scenario type.

### 2. Adding a New Endpoint

Create new file in `app/api/routes/`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/my-endpoint", tags=["my-tag"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

Register in `app/main.py`:
```python
from app.api.routes.my_route import router as my_router
app.include_router(my_router, prefix="/api")
```

### 3. Database Migrations (Optional - for production)

Install alembic:
```powershell
pip install alembic
```

Initialize:
```powershell
alembic init alembic
```

Create migration:
```powershell
alembic revision --autogenerate -m "description"
```

Apply migration:
```powershell
alembic upgrade head
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables Reference

```env
# Database (required)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Cost of Living API (optional - falls back to cached data)
COL_API_BASE_URL=http://localhost:3001
COL_API_TIMEOUT_SECONDS=10

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Application
APP_NAME=Finance Stress Simulator
VERSION=0.1.0
```

## Deployment

### Option 1: Render
1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Option 2: Railway
1. New Project → Deploy from GitHub
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

### Option 3: Fly.io
1. Install flyctl
2. `fly launch`
3. `fly deploy`

## Next Steps

1. ✅ Get backend running locally
2. ✅ Test all endpoints in Swagger UI
3. ✅ Run unit tests
4. 🔨 Build frontend (React)
5. 🚀 Deploy both

## Need Help?

Common commands cheatsheet:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run server
python -m app.main

# Run tests
pytest

# Check database
psql -U postgres -d stress_simulator

# View logs
# (server logs appear in terminal)

# Deactivate venv
deactivate
```

## What Makes This Project Special

**Clean Architecture:**
- Domain logic is pure Python (no framework deps)
- Easy to test
- Easy to extend

**Type Safety:**
- Pydantic models for validation
- SQLModel for type-safe database
- Full type hints throughout

**Real Integration:**
- Calls your COL API
- Graceful fallback
- Demonstrates inter-project communication

**Production Ready:**
- Proper error handling
- Health checks
- Structured logging
- Unit tests

---

You're ready to build! 🚀
