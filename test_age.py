from datetime import date

from app.services.who.age import calculate_age_in_months

date_of_birth = date(2023, 5, 15)
measurement_date = date(2026, 9, 29)

age_months = calculate_age_in_months(date_of_birth, measurement_date)
print(f"Age: {age_months} months")