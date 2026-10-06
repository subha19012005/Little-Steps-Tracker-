"""CRUD (Create, Read, Update, Delete) operations for growth records."""

import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.growth_record import GrowthRecord
from app.schemas.growth_record import GrowthRecordCreate

logger = logging.getLogger(__name__)


def create_growth_record(db: Session, record_data: GrowthRecordCreate) -> GrowthRecord:
    """Inserts a new growth record for a child into the database.

    Args:
        db: SQLAlchemy database session.
        record_data: Validated Pydantic schema with growth metrics.

    Returns:
        GrowthRecord: The created SQLAlchemy model instance.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    db_record = GrowthRecord(
        child_id=record_data.child_id,
        measurement_date=record_data.measurement_date,
        height=record_data.height,
        weight=record_data.weight
    )
    try:
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to create growth record for child {record_data.child_id}: {exc}")
        raise


def get_growth_history(db: Session, child_id: str) -> List[GrowthRecord]:
    """Retrieves all growth records belonging to a child, ordered by date descending.

    Args:
        db: SQLAlchemy database session.
        child_id: Unique identifier of the child (e.g., 'LST-001').

    Returns:
        List[GrowthRecord]: List of growth records, newest first.
    """
    try:
        records = (
            db.query(GrowthRecord)
            .filter(GrowthRecord.child_id == child_id)
            .order_by(GrowthRecord.measurement_date.desc(), GrowthRecord.id.desc())
            .all()
        )
        return records
    except SQLAlchemyError as exc:
        logger.error(f"Failed to fetch growth history for child {child_id}: {exc}")
        raise
