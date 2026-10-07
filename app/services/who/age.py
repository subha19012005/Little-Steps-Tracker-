from datetime import date
from calendar import monthrange


def calculate_age_in_days(date_of_birth: date, measurement_date: date) -> int:
    """Return exact calendar days between birth and measurement dates."""
    if measurement_date < date_of_birth:
        raise ValueError("measurement_date cannot be before date_of_birth")
    return (measurement_date - date_of_birth).days


def calculate_age_in_months(date_of_birth: date, measurement_date: date) -> int:
    """Return the number of completed calendar months between two dates."""
    if measurement_date < date_of_birth:
        raise ValueError("measurement_date cannot be before date_of_birth")

    age_months = (measurement_date.year - date_of_birth.year) * 12
    age_months += measurement_date.month - date_of_birth.month

    last_day_of_measurement_month = monthrange(
        measurement_date.year, measurement_date.month
    )[1]
    completed_birth_day = min(date_of_birth.day, last_day_of_measurement_month)
    if measurement_date.day < completed_birth_day:
        age_months -= 1

    return age_months