from fastapi import FastAPI
from models.child import ChildCreate
from dotenv import load_dotenv
import psycopg
import uuid
import os

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
    child_id = f"CH-{uuid.uuid4().hex[:6].upper()}"

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO children
                (child_id, name, date_of_birth, gender, centre)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    child_id,
                    child.name,
                    child.date_of_birth,
                    child.gender,
                    child.centre
                )
            )

        conn.commit()

    finally:
        conn.close()

    return {
        "message": "Child registered successfully",
        "child_id": child_id,
        "name": child.name,
        "date_of_birth": child.date_of_birth,
        "gender": child.gender,
        "centre": child.centre
    }