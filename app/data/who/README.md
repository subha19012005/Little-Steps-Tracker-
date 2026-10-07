# WHO Anthro setup

This project uses the CRAN `anthro` package, which supplies the WHO Child Growth Standards calculation and reference data. No manual WHO CSV files are required or included.

## Install

Install R for Windows from [CRAN](https://cran.r-project.org/bin/windows/base/), then open PowerShell in the project directory and install the package:

```powershell
Rscript --version
Rscript -e "install.packages('anthro', repos='https://cloud.r-project.org')"
```

R installs the package's dependencies through CRAN. The FastAPI service invokes `Rscript`; if R or `anthro` is unavailable, the endpoint returns HTTP 503.

## Inputs and supported ages

Anthro receives exact age in days, weight in kilograms, and length/height in centimetres. Its under-five z-score calculation supports children younger than 60 months; this module rejects ages of 60 completed months or older. WHO's length/height transition is at 731 days: below 731 days uses recumbent length, and at or above 731 days uses standing height.

The API accepts optional `measurement_position` values `length` or `height`. If omitted, position is assumed from age and the response identifies that assumption. If the explicitly measured position does not match the age group, Anthro applies its documented 0.7 cm adjustment. Length and standing height are distinct measurements and should not be silently interchanged.

## Under-five classifications

The response includes `haz_status`, `waz_status`, and `whz_status`. For HAZ and WAZ, scores below -3 are severe, scores from -3 inclusive to -2 exclusive are moderate, and scores at least -2 are not classified as deficient. WHZ is severe wasting below -3, wasting from -3 inclusive to -2 exclusive, normal from -2 through +2 inclusive, overweight above +2 through +3 inclusive, and obesity above +3. WHZ is the primary weight-for-height nutritional-status classification; BAZ is returned as calculated by Anthro but is not separately classified. Invalid or flagged indicator results are marked `Requires Review`. The overall `status` and `follow_up_required` remain application-level screening decisions, not diagnoses.

The results are screening/decision support only and do not replace assessment by a qualified health professional.