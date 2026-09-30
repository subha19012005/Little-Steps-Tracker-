from fastapi import FastAPI
from models.child import ChildCreate
import uuid

app = FastAPI(title="Little Steps Tracker API")


@app.get("/")
def root():
    return {
        "message": "Little Steps Tracker API is running"
    }


@app.post("/api/children")
def register_child(child: ChildCreate):
    child_id = f"CH-{uuid.uuid4().hex[:6].upper()}"

    return {
        "message": "Child registered successfully",
        "child_id": child_id,
        "name": child.name,
        "date_of_birth": child.date_of_birth,
        "gender": child.gender,
        "centre": child.centre
    }