"""Main application entrypoint for the Little Steps Tracker backend.

Module: Person 3 - Growth Monitoring Backend & Database
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database.connection import engine, Base
from app.routes.growth import router as growth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("little_steps_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown tasks.

    Attempts to auto-create tables on startup for convenience in local development.
    If the database is not yet initialized or reachable, logs a warning so development
    and testing can proceed without hard crashing the server process.
    """
    try:
        # Create database tables if they do not exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as exc:
        logger.warning(
            "Could not connect to database on startup to create tables. "
            "Verify PostgreSQL is running and DATABASE_URL is configured. "
            f"Details: {exc}"
        )
    yield


app = FastAPI(
    title="Little Steps Tracker - Growth Monitoring API",
    description=(
        "Backend REST API for recording and retrieving child physical growth measurements.\n\n"
        "Responsible Module: Person 3 (Growth Monitoring Backend & Database)\n"
        "Integrates with Person 4 (Flutter Growth Monitoring UI) and Person 1 (Child Management)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ------------------------------------------------------------------------------
# CORS Middleware Configuration
# ------------------------------------------------------------------------------
# NOTE: Allowing origins=["*"] is configured for local development so that the
# Flutter mobile application running on Android Emulator (10.0.2.2), iOS Simulator,
# or physical testing devices over Wi-Fi can communicate with this API.
# In production, this should be restricted to specific trusted origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Custom Exception Handlers
# ------------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Transforms Pydantic validation errors into clean, readable JSON for Flutter."""
    errors = []
    for err in exc.errors():
        field_name = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        errors.append({
            "field": field_name,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "validation_error")
        })
    logger.warning(f"Validation failed on {request.method} {request.url.path}: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request body contains invalid or missing fields.",
            "details": errors
        }
    )


# ------------------------------------------------------------------------------
# Root & Health Check Endpoints
# ------------------------------------------------------------------------------
@app.get("/", tags=["System"])
def root():
    """Root endpoint to verify the API service is active."""
    return {"message": "Little Steps Tracker API is running"}


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint used by uptime monitors, deployment checks, and tests."""
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Include Routers
# ------------------------------------------------------------------------------
app.include_router(growth_router)
