"""Automated test suite for Growth Monitoring API endpoints and validations.

Uses an isolated in-memory SQLite database and FastAPI TestClient so tests run
fast, reliably, and without requiring a live PostgreSQL instance or credentials.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db

# Create an in-memory SQLite database engine for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def client():
    """Fixture that builds fresh tables in SQLite and yields a FastAPI TestClient."""
    # Create tables in test in-memory DB
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Teardown: clean up tables and dependency overrides
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


# ==============================================================================
# 1. Health and Root Endpoint Tests
# ==============================================================================
def test_root_endpoint(client: TestClient):
    """Test that the root endpoint returns expected service status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Little Steps Tracker API is running"}


def test_health_check_endpoint(client: TestClient):
    """Test that the health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ==============================================================================
# 2. Valid Growth Record Creation
# ==============================================================================
def test_create_valid_growth_record(client: TestClient):
    """Test creating a valid child growth record returns 201 and record data."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["child_id"] == "LST-001"
    assert data["measurement_date"] == "2026-10-05"
    assert data["height"] == 95.2
    assert data["weight"] == 14.1
    assert "created_at" in data


# ==============================================================================
# 3. Validation: Empty or Missing child_id
# ==============================================================================
def test_reject_empty_child_id(client: TestClient):
    """Test that an empty child_id is rejected with 422 Unprocessable Entity."""
    payload = {
        "child_id": "",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422
    assert "details" in response.json()


def test_reject_whitespace_child_id(client: TestClient):
    """Test that a whitespace-only child_id is rejected."""
    payload = {
        "child_id": "   ",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


# ==============================================================================
# 4. Validation: Negative and Zero Height
# ==============================================================================
def test_reject_negative_height(client: TestClient):
    """Test that negative height is rejected with 422."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": -5.0,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


def test_reject_zero_height(client: TestClient):
    """Test that zero height is rejected with 422."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": 0.0,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


# ==============================================================================
# 5. Validation: Negative and Zero Weight
# ==============================================================================
def test_reject_negative_weight(client: TestClient):
    """Test that negative weight is rejected with 422."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": -2.5
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


def test_reject_zero_weight(client: TestClient):
    """Test that zero weight is rejected with 422."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": 0.0
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


# ==============================================================================
# 6. Validation: Invalid Date Format
# ==============================================================================
def test_reject_invalid_date(client: TestClient):
    """Test that malformed date string is rejected with 422."""
    payload = {
        "child_id": "LST-001",
        "measurement_date": "not-a-valid-date",
        "height": 95.2,
        "weight": 14.1
    }
    response = client.post("/api/growth-records", json=payload)
    assert response.status_code == 422


# ==============================================================================
# 7. Growth History Retrieval & Ordering
# ==============================================================================
def test_retrieve_growth_history_ordered_descending(client: TestClient):
    """Test retrieving child growth history returns records ordered newest first."""
    # Create older record
    client.post("/api/growth-records", json={
        "child_id": "LST-001",
        "measurement_date": "2026-08-01",
        "height": 92.0,
        "weight": 13.0
    })

    # Create newest record
    client.post("/api/growth-records", json={
        "child_id": "LST-001",
        "measurement_date": "2026-10-05",
        "height": 95.2,
        "weight": 14.1
    })

    # Create middle record
    client.post("/api/growth-records", json={
        "child_id": "LST-001",
        "measurement_date": "2026-09-05",
        "height": 94.0,
        "weight": 13.7
    })

    # Create record for a different child (should NOT be returned)
    client.post("/api/growth-records", json={
        "child_id": "LST-002",
        "measurement_date": "2026-10-01",
        "height": 88.5,
        "weight": 12.4
    })

    # Fetch history for LST-001
    response = client.get("/api/children/LST-001/growth-history")
    assert response.status_code == 200

    records = response.json()
    assert len(records) == 3

    # Check order: newest first
    assert records[0]["measurement_date"] == "2026-10-05"
    assert records[0]["height"] == 95.2
    assert records[0]["weight"] == 14.1

    assert records[1]["measurement_date"] == "2026-09-05"
    assert records[1]["height"] == 94.0

    assert records[2]["measurement_date"] == "2026-08-01"
    assert records[2]["height"] == 92.0


# ==============================================================================
# 8. Empty Growth History
# ==============================================================================
def test_empty_growth_history_returns_empty_list(client: TestClient):
    """Test querying a child with no growth records returns 200 and empty list."""
    response = client.get("/api/children/NON_EXISTENT_CHILD/growth-history")
    assert response.status_code == 200
    assert response.json() == []


# ==============================================================================
# 9. Child ID Whitespace Path Parameter Validation
# ==============================================================================
def test_whitespace_child_id_path_param_rejected(client: TestClient):
    """Test that a whitespace-only child_id in path is rejected with 400."""
    response = client.get("/api/children/%20%20/growth-history")
    assert response.status_code == 400
    assert "child_id must not be empty" in response.json()["detail"]
