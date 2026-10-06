"""SQLAlchemy model for child growth measurement records."""

from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from app.database.connection import Base


class GrowthRecord(Base):
    """Represents a physical growth measurement for a child.

    Attributes:
        id (int): Primary key autoincrementing record ID.
        child_id (str): Identifier of the child (e.g., 'LST-001').
        measurement_date (date): Date on which the measurement was taken.
        height (float): Measured height in centimeters (cm).
        weight (float): Measured weight in kilograms (kg).
        created_at (datetime): Timestamp when this record was stored in the database.
    """

    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(String(50), nullable=False, index=True)
    measurement_date = Column(Date, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<GrowthRecord(id={self.id}, child_id='{self.child_id}', "
            f"date={self.measurement_date}, height={self.height}, weight={self.weight})>"
        )
