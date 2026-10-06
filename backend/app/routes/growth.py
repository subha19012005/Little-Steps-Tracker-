"""API routes for growth monitoring and measurement management."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.schemas.growth_record import GrowthRecordCreate, GrowthRecordResponse
from app.crud.growth import create_growth_record, get_growth_history

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Growth Monitoring"])


@router.post(
    "/api/growth-records",
    response_model=GrowthRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a child growth measurement record",
    description="Saves a new physical growth measurement (height and weight) for a child."
)
def add_growth_record(
    record: GrowthRecordCreate,
    db: Session = Depends(get_db)
):
    """Saves a new growth measurement for a child.

    - **child_id**: Unique child identifier (e.g. LST-001)
    - **measurement_date**: Date of measurement (YYYY-MM-DD)
    - **height**: Height in cm (must be > 0)
    - **weight**: Weight in kg (must be > 0)
    """
    try:
        new_record = create_growth_record(db=db, record_data=record)
        return new_record
    except SQLAlchemyError as exc:
        logger.error(f"Database error while saving growth record: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store growth measurement record due to a database error."
        )


@router.get(
    "/api/children/{child_id}/growth-history",
    response_model=List[GrowthRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve a child's growth measurement history",
    description="Returns all historical growth measurements for the specified child, ordered with the newest first."
)
def get_child_growth_history(
    child_id: str = Path(
        ...,
        description="The unique identifier of the child (e.g. LST-001)",
        min_length=1
    ),
    db: Session = Depends(get_db)
):
    """Fetches growth history for a specific child.

    Returns a list of growth records ordered by measurement date descending.
    If the child has no recorded growth measurements, an empty list is returned.
    """
    cleaned_child_id = child_id.strip()
    if not cleaned_child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="child_id must not be empty or whitespace only."
        )

    try:
        records = get_growth_history(db=db, child_id=cleaned_child_id)
        return records
    except SQLAlchemyError as exc:
        logger.error(f"Database error while retrieving growth history: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve growth records due to a database error."
        )
