import csv
from decimal import Decimal, InvalidOperation
import csv
import io
import math
import shutil
import subprocess
from pathlib import Path

ANTHRO_HELPER = Path(__file__).with_name("anthro_helper.R")
ANTHRO_OUTPUT_COLUMNS = (
    "zlen",
    "zwei",
    "zwfl",
    "zbmi",
    "cbmi",
    "clenhei",
    "cmeasure",
    "flen",
    "fwei",
    "fwfl",
    "fbmi",
)


class AnthroServiceUnavailableError(RuntimeError):
    """Raised when R or the CRAN anthro package cannot calculate a result."""


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate mathematical BMI without classifying it."""
    _validate_measurement(weight_kg, "weight_kg")
    _validate_measurement(height_cm, "height_cm")
    height_m = height_cm / 100
    return round(weight_kg / (height_m**2), 2)


def normalize_sex(sex: str) -> tuple[str, str]:
    """Return canonical API sex and the code expected by WHO Anthro."""
    normalized = sex.strip().lower()
    if normalized == "male":
        return "male", "m"
    if normalized == "female":
        return "female", "f"
    raise ValueError("sex must be 'male' or 'female'")


def run_anthro(
    anthro_sex: str,
    age_days: int,
    weight_kg: float,
    lenhei_cm: float,
    measure: str,
) -> dict[str, float | bool | str | None]:
    """Run CRAN anthro through Rscript and parse its one-row CSV output."""
    if shutil.which("Rscript") is None:
        raise AnthroServiceUnavailableError(
            "WHO Anthro calculation service is unavailable."
        )

    command = [
        "Rscript",
        "--vanilla",
        str(ANTHRO_HELPER),
        anthro_sex,
        str(age_days),
        repr(weight_kg),
        repr(lenhei_cm),
        measure,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise AnthroServiceUnavailableError(
            "WHO Anthro calculation service is unavailable."
        ) from error

    if completed.returncode != 0:
        raise AnthroServiceUnavailableError(
            "WHO Anthro calculation service is unavailable."
        )

    try:
        reader = csv.DictReader(io.StringIO(completed.stdout))
        if reader.fieldnames is None or not set(ANTHRO_OUTPUT_COLUMNS).issubset(
            reader.fieldnames
        ):
            raise ValueError("Unexpected Anthro output columns")
        rows = list(reader)
        if len(rows) != 1:
            raise ValueError("Anthro must return exactly one record")

        result: dict[str, float | bool | str | None] = {}
        for column, text_value in rows[0].items():
            text_value = (text_value or "").strip()
            if column == "cmeasure":
                result[column] = text_value or None
            elif column.startswith("f"):
                if text_value in ("1", "TRUE", "True"):
                    result[column] = True
                elif text_value in ("0", "FALSE", "False"):
                    result[column] = False
                else:
                    result[column] = None
            elif not text_value:
                result[column] = None
            else:
                number = float(text_value)
                result[column] = number if math.isfinite(number) else None
        return result
    except (csv.Error, TypeError, ValueError) as error:
        raise AnthroServiceUnavailableError(
            "WHO Anthro calculation service is unavailable."
        ) from error


def _validate_measurement(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite value greater than zero")