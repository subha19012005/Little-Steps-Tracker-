# Little Steps Tracker — Growth Monitoring Backend & Database

Backend module for the **"Little Steps Tracker"** college project.  
**Role:** Person 3 — Growth Monitoring Backend & Database.

This service allows the Flutter mobile application to:
1. Record child growth measurements (height and weight).
2. Retrieve a child's chronological growth measurement history (newest first).
3. Validate growth measurement inputs before storing them in PostgreSQL.
4. Expose clean, standardized REST APIs and Swagger interactive documentation.
5. Provide automated test coverage without needing live production databases.

---

## Architecture & Data Flow

```text
Flutter Mobile App (Person 4)
             │
             ▼ [HTTP REST JSON]
      FastAPI Router (routes/growth.py)
             │
             ▼ [Validated Pydantic Schemas]
       CRUD Operations (crud/growth.py)
             │
             ▼ [SQLAlchemy Declarative Model]
          PostgreSQL Database (little_steps_tracker)
```

### Module Boundaries
- **Person 1 (Child Management):** Owns child registration and generates `child_id` (e.g. `LST-001`). This backend uses `child_id` directly without creating child records.
- **Person 2 (QR Identification):** Scans QR codes to extract `child_id` on mobile.
- **Person 3 (This Module):** Stores raw growth measurements (`height`, `weight`, `date`) and serves history.
- **Person 4 (Flutter Growth UI):** Consumes these APIs to display forms, records, and growth charts.
- **Person 5 (WHO Growth Assessment):** Classifies nutritional status and calculates Z-scores from raw measurements in a downstream module.

---

## Tech Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **ORM:** SQLAlchemy 2.x
- **Database Driver:** psycopg2-binary
- **Validation:** Pydantic v2
- **Database:** PostgreSQL
- **Testing:** Pytest, HTTPX

---

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, lifespan, CORS, error handling
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py           # SQLAlchemy engine & session dependency
│   ├── models/
│   │   ├── __init__.py
│   │   └── growth_record.py        # SQLAlchemy GrowthRecord model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── growth_record.py        # Pydantic schemas & validations
│   ├── crud/
│   │   ├── __init__.py
│   │   └── growth.py               # Database queries (insert, query history)
│   └── routes/
│       ├── __init__.py
│       └── growth.py               # REST API route handlers
├── tests/
│   ├── __init__.py
│   └── test_growth.py              # Automated Pytest suite (in-memory SQLite)
├── .env.example                    # Template for environment variables
├── .gitignore                      # Git ignore file for Python & secrets
├── requirements.txt                # Python dependencies
└── README.md                       # Setup and usage guide

database/
└── schema.sql                      # PostgreSQL DDL script for growth_records table

docs/
└── api.md                          # API contract & Flutter integration guide
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed: `python --version`
- PostgreSQL 14+ installed and running on port 5432

### 2. Create Virtual Environment

Open a terminal in the `backend/` directory:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
```

Activate the virtual environment:
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database (.env)

1. Create a PostgreSQL database named `little_steps_tracker` using pgAdmin, psql, or your terminal:
   ```sql
   CREATE DATABASE little_steps_tracker;
   ```

2. Copy `.env.example` to `.env`:
   - **Windows:**
     ```powershell
     copy .env.example .env
     ```
   - **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

3. Update the `.env` file with your PostgreSQL password:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/little_steps_tracker
   HOST=0.0.0.0
   PORT=8000
   ```

> 💡 **Table Creation:**  
> When the FastAPI application starts, it automatically creates the `growth_records` table if it does not already exist. You can also manually run the SQL script located at `database/schema.sql`.

---

## Running the Application

### Start Development Server
```bash
uvicorn app.main:app --reload
```

To allow connections from mobile devices or other computers on your local Wi-Fi:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing API Documentation
Once running, open your web browser:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Automated Tests

The test suite runs against an isolated in-memory SQLite database. You do **not** need a running PostgreSQL server to run tests.

From the `backend/` directory:
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

All 9 test cases will run and verify:
- System root (`/`) and health check (`/health`)
- Creating valid growth records (`POST /api/growth-records`)
- Rejection of empty or whitespace `child_id` (HTTP 422)
- Rejection of non-positive height values (`height <= 0`)
- Rejection of non-positive weight values (`weight <= 0`)
- Rejection of malformed date strings
- Proper chronological descending ordering of growth history
- Safe empty response (`[]`) when a child has no prior records
- Rejection of invalid path parameters (HTTP 400)

---

## API Summary for Person 4 (Flutter)

Detailed schema contracts and Dart code examples are provided in [`docs/api.md`](../docs/api.md).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root service greeting |
| `GET` | `/health` | Health check endpoint |
| `POST` | `/api/growth-records` | Save a new height/weight measurement |
| `GET` | `/api/children/{child_id}/growth-history` | Get all records for a child (newest first) |

### Important Network Note for Mobile App Testing
- **Android Emulator:** Use `http://10.0.2.2:8000` as the base URL.
- **iOS Simulator:** Use `http://127.0.0.1:8000` as the base URL.
- **Physical Device:** Connect the phone and laptop to the same Wi-Fi, run the server with `--host 0.0.0.0`, and set Flutter base URL to `http://<YOUR_PC_IP>:8000` (e.g. `http://192.168.1.50:8000`).
