from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.who.assessment import assess_child
from app.services.who.zscore import AnthroServiceUnavailableError

router = APIRouter(prefix="/api", tags=["WHO Growth Assessment"])


class GrowthAssessmentRequest(BaseModel):
    child_id: str
    date_of_birth: date
    sex: str
    height_cm: float = Field(gt=0, allow_inf_nan=False)
    weight_kg: float = Field(gt=0, allow_inf_nan=False)
    measurement_date: date
    measurement_position: Literal["length", "height"] | None = None


@router.post("/growth-assessment")
def create_growth_assessment(request: GrowthAssessmentRequest) -> dict[str, object]:
    """Return WHO Anthro screening results; this is not a medical diagnosis."""
    try:
        assessment = assess_child(
            date_of_birth=request.date_of_birth,
            sex=request.sex,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            measurement_date=request.measurement_date,
            measurement_position=request.measurement_position,
        )
    except AnthroServiceUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail="WHO Anthro calculation service is unavailable.",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"child_id": request.child_id, **assessment}