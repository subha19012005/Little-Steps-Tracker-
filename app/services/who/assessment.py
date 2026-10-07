from datetime import date
from math import isfinite
from typing import TypeGuard

from app.services.who.age import calculate_age_in_days, calculate_age_in_months
from app.services.who.zscore import calculate_bmi, normalize_sex, run_anthro

LENGTH_HEIGHT_TRANSITION_DAYS = 731
MAX_COMPLETED_AGE_MONTHS = 60


def resolve_measurement_position(
    age_days: int, measurement_position: str | None
) -> tuple[str, str]:
    """Choose an explicit position or assume the age-appropriate position."""
    if measurement_position is not None:
        if measurement_position not in ("length", "height"):
            raise ValueError("measurement_position must be 'length' or 'height'")
        return measurement_position, "explicitly provided"

    if age_days < LENGTH_HEIGHT_TRANSITION_DAYS:
        return "length", "age-based assumed"
    return "height", "age-based assumed"


def assess_child(
    date_of_birth: date,
    sex: str,
    height_cm: float,
    weight_kg: float,
    measurement_date: date,
    measurement_position: str | None = None,
) -> dict[str, object]:
    """Calculate WHO Anthro indicators and screening status for one child."""
    _validate_positive(height_cm, "height_cm")
    _validate_positive(weight_kg, "weight_kg")
    canonical_sex, anthro_sex = normalize_sex(sex)
    age_days = calculate_age_in_days(date_of_birth, measurement_date)
    age_months = calculate_age_in_months(date_of_birth, measurement_date)
    if age_months >= MAX_COMPLETED_AGE_MONTHS:
        raise ValueError(
            "WHO Anthro under-5 z-scores require an age below 60 completed months"
        )

    position, position_source = resolve_measurement_position(
        age_days, measurement_position
    )
    measure_code = "L" if position == "length" else "H"
    result = run_anthro(anthro_sex, age_days, weight_kg, height_cm, measure_code)

    scores = (result["zlen"], result["zwei"], result["zwfl"], result["zbmi"])
    flags = (result["flen"], result["fwei"], result["fwfl"], result["fbmi"])
    scores_valid = all(
        isinstance(score, (int, float)) and isfinite(score) for score in scores
    )
    flags_clear = all(flag is False for flag in flags)
    requires_review = not (scores_valid and flags_clear)

    return {
        "age_days": age_days,
        "age_months": age_months,
        "sex": canonical_sex,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "bmi": (
            result["cbmi"]
            if result["cbmi"] is not None
            else calculate_bmi(weight_kg, height_cm)
        ),
        "haz": result["zlen"],
        "waz": result["zwei"],
        "whz": result["zwfl"],
        "baz": result["zbmi"],
        "haz_status": _classify_haz(result["zlen"], result["flen"]),
        "waz_status": _classify_waz(result["zwei"], result["fwei"]),
        "whz_status": _classify_whz(result["zwfl"], result["fwfl"]),
        "status": "Requires Review" if requires_review else "Within reference range",
        "follow_up_required": requires_review,
        "measurement_position": position,
        "measurement_position_source": position_source,
        "clenhei": result["clenhei"],
        "cmeasure": result["cmeasure"],
    }


def _validate_positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite value greater than zero")


def _classify_haz(score: object, flagged: object) -> str:
    if flagged is not False or not _is_finite_score(score):
        return "Requires Review"
    if score < -3:
        return "Severe stunting"
    if score < -2:
        return "Stunting"
    return "Not stunted"


def _classify_waz(score: object, flagged: object) -> str:
    if flagged is not False or not _is_finite_score(score):
        return "Requires Review"
    if score < -3:
        return "Severe underweight"
    if score < -2:
        return "Underweight"
    return "Not underweight"


def _classify_whz(score: object, flagged: object) -> str:
    if flagged is not False or not _is_finite_score(score):
        return "Requires Review"
    if score < -3:
        return "Severe wasting"
    if score < -2:
        return "Wasting"
    if score <= 2:
        return "Normal"
    if score <= 3:
        return "Overweight"
    return "Obesity"


def _is_finite_score(score: object) -> TypeGuard[int | float]:
    return isinstance(score, (int, float)) and isfinite(score)