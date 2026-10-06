"""Pydantic schemas for data validation and serialization of growth records."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GrowthRecordBase(BaseModel):
    """Base schema containing shared growth measurement attributes."""

    child_id: str = Field(
        ...,
        description="Unique identifier for the child (e.g. LST-001)",
        examples=["LST-001"]
    )
    measurement_date: date = Field(
        ...,
        description="Date when the measurement was taken (YYYY-MM-DD)",
        examples=["2026-10-05"]
    )
    height: float = Field(
        ...,
        gt=0,
        description="Height in centimeters (must be greater than 0)",
        examples=[95.2]
    )
    weight: float = Field(
        ...,
        gt=0,
        description="Weight in kilograms (must be greater than 0)",
        examples=[14.1]
    )

    @field_validator("child_id")
    @classmethod
    def validate_child_id(cls, v: str) -> str:
        """Validates that child_id is non-empty and stripped."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("child_id is required and must not be empty")
        return v.strip()


class GrowthRecordCreate(GrowthRecordBase):
    """Schema for creating a new growth measurement record."""
    pass


class GrowthRecordResponse(GrowthRecordBase):
    """Schema for returning growth measurement details to Flutter client."""

    id: int = Field(..., description="Unique record database ID", examples=[1])
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the measurement record was stored"
    )

    model_config = ConfigDict(from_attributes=True)
