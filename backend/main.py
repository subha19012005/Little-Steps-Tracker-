
from fastapi import FastAPI, HTTPException
from models.child import ChildCreate
from dotenv import load_dotenv
from datetime import datetime, timezone
import psycopg
import uuid
import os
import traceback

load_dotenv()

app = FastAPI(title="Little Steps Tracker API")


# PostgreSQL connection
def get_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


@app.get("/")
def root():
    return {
        "message": "Little Steps Tracker API is running"
    }


@app.post("/api/children")
def register_child(child: ChildCreate):
    # Generate the child ID used by the QR module
    child_id = f"CH-{uuid.uuid4().hex[:6].upper()}"

    # Validate and split the child's full name
    name_parts = child.name.strip().split(maxsplit=1)

    if not name_parts or not name_parts[0]:
        raise HTTPException(
            status_code=400,
            detail="Child name cannot be empty"
        )

    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Database sex column accepts only one character
    gender_value = child.gender.strip().lower()

    gender_map = {
        "female": "F",
        "male": "M",
        "f": "F",
        "m": "M"
    }

    if gender_value not in gender_map:
        raise HTTPException(
            status_code=400,
            detail="Gender must be Male or Female"
        )

    sex = gender_map[gender_value]

    conn = None

    try:
        conn = get_connection()
        now = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC for DB

        # Generate a UUID for the primary key (children.id is varchar(36), NOT NULL, no default)
        row_id = str(uuid.uuid4())

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO children
                (
                    id,
                    external_child_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    sex,
                    location,
                    qr_identifier,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row_id,       # id          — UUID primary key
                    child_id,     # external_child_id — CH-XXXXXX (used by QR module)
                    first_name,
                    last_name,
                    child.date_of_birth,
                    sex,
                    child.centre, # location    — varchar(255), stores the centre name
                    child_id,     # qr_identifier — same as external_child_id
                    now,          # created_at  — NOT NULL, no default
                    now           # updated_at  — NOT NULL, no default
                )
            )

        conn.commit()

        return {
            "message": "Child registered successfully",
            "child_id": child_id,
            "name": child.name,
            "date_of_birth": child.date_of_birth,
            "gender": child.gender,
            "centre": child.centre
        }

    except psycopg.Error:
        if conn is not None:
            conn.rollback()

        # Print the full database traceback in the backend terminal
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Database error while registering child"
        )

    finally:
        if conn is not None:
            conn.close()


@app.get("/api/children/{child_id}")
def get_child(child_id: str):
    """
    Retrieve a child record by the QR child ID (format: CH-XXXXXX).
    The ID is matched against the qr_identifier column.
    Returns 404 if no matching record exists.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    external_child_id,
                    first_name,
                    last_name,
                    date_of_birth,
                    sex,
                    location
                FROM children
                WHERE qr_identifier = %s
                LIMIT 1
                """,
                (child_id,)
            )
            row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Child not found"
            )

        external_child_id, first_name, last_name, date_of_birth, sex, location = row

        # Map single-char sex back to full word for display
        gender_display = "Female" if sex == "F" else "Male" if sex == "M" else sex

        full_name = f"{first_name} {last_name}".strip()

        return {
            "child_id": external_child_id,
            "name": full_name,
            "date_of_birth": str(date_of_birth),
            "gender": gender_display,
            "centre": location or ""
        }

    except HTTPException:
        raise  # re-raise 404 cleanly without logging

    except psycopg.Error:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching child"
        )

    finally:
        if conn is not None:
            conn.close()
