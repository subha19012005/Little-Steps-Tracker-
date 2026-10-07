# Person 5: WHO Growth Assessment

Person 5 is a FastAPI module for calculating WHO under-five growth z-scores and returning basic screening classifications. It uses the WHO Anthro calculation rather than implementing growth reference formulas in application code. Results support screening and decision-making; they are **not a medical diagnosis**.

## Scope and limitations

- Supports children below 60 completed months of age only.
- Uses WHO under-five growth references; WHO 5–19-year references are not implemented.
- Returns HAZ, WAZ, WHZ, and BAZ from WHO Anthro. WHZ is used for under-five weight-for-height nutritional-status classification; BAZ has no separate classification.
- Does not include ML prediction, database/storage, or a Flutter UI.

## Requirements

- Python 3.11.
- R 4.4.1 (the version verified for this module).
- CRAN package `anthro` 1.1.0.
- On Windows, `Rscript.exe` must be available on the `PATH` inherited by Python. The verified executable is `C:\Program Files\R\R-4.4.1\bin\Rscript.exe`.

For a PowerShell session where R is not already on `PATH`, add its `bin` directory before starting the API:

```powershell
$env:PATH = "C:\Program Files\R\R-4.4.1\bin;$env:PATH"
```

## Start the API

From the project directory, run:

```powershell
python -m uvicorn app.main:app
```

The API runs at `http://127.0.0.1:8000`. Interactive Swagger documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Growth assessment endpoint

`POST /api/growth-assessment`

Required JSON request fields:

| Field | Description |
| --- | --- |
| `child_id` | Caller-provided child identifier |
| `date_of_birth` | Date of birth in `YYYY-MM-DD` format |
| `sex` | `female` or `male` |
| `height_cm` | Positive measured length/height in centimetres |
| `weight_kg` | Positive measured weight in kilograms |
| `measurement_date` | Measurement date in `YYYY-MM-DD` format |

The optional `measurement_position` field accepts `length` or `height`. If omitted, the position is assumed from age: length below 731 days and height at or above 731 days. The response identifies the position and whether it was assumed or explicitly provided.

Age in days is the exact calendar-day difference between `date_of_birth` and `measurement_date`. Age in months is the number of completed calendar months between those dates. WHO Anthro under-five assessment is restricted to ages below 60 completed months.

### Example request

```json
{
  "child_id": "TEST-001",
  "date_of_birth": "2023-05-15",
  "sex": "female",
  "height_cm": 95.2,
  "weight_kg": 14.1,
  "measurement_date": "2026-09-29",
  "measurement_position": "height"
}
```

### Example successful response

```json
{
  "child_id": "TEST-001",
  "age_days": 1233,
  "age_months": 40,
  "sex": "female",
  "height_cm": 95.2,
  "weight_kg": 14.1,
  "bmi": 15.5576936657016,
  "haz": -0.72,
  "waz": -0.31,
  "whz": 0.13,
  "baz": 0.17,
  "haz_status": "Not stunted",
  "waz_status": "Not underweight",
  "whz_status": "Normal",
  "status": "Within reference range",
  "follow_up_required": false,
  "measurement_position": "height",
  "measurement_position_source": "explicitly provided",
  "clenhei": 95.2,
  "cmeasure": "h"
}
```

`haz_status`, `waz_status`, and `whz_status` are under-five classifications. Invalid scores or Anthro flags retain the `Requires Review` behavior. `status` and `follow_up_required` are application-level screening outputs, not diagnoses.

## WHO Anthro setup

The service invokes `Rscript` and the installed CRAN `anthro` package for the WHO calculation. If R/`Rscript` or `anthro` is unavailable to the running Python process, the assessment endpoint returns HTTP 503. See [the WHO setup notes](app/data/who/README.md) for further details.
