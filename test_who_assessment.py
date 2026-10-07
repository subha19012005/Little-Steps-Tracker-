import shutil
import subprocess
import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.routes.assessment import GrowthAssessmentRequest
from app.services.who.age import calculate_age_in_days, calculate_age_in_months
from app.services.who.assessment import assess_child, resolve_measurement_position
from app.services.who.zscore import (
    AnthroServiceUnavailableError,
    calculate_bmi,
    normalize_sex,
    run_anthro,
)

CLIENT = TestClient(app)
BASE_REQUEST = {
    "child_id": "TEST-001",
    "date_of_birth": "2023-05-15",
    "sex": "female",
    "height_cm": 95.2,
    "weight_kg": 14.1,
    "measurement_date": "2026-09-29",
}
UNAVAILABLE_SCORE_RESULT = {
    "zlen": None,
    "zwei": None,
    "zwfl": None,
    "zbmi": None,
    "cbmi": None,
    "clenhei": None,
    "cmeasure": None,
    "flen": False,
    "fwei": False,
    "fwfl": False,
    "fbmi": False,
}
NORMAL_SCORE_RESULT = {
    **UNAVAILABLE_SCORE_RESULT,
    "zlen": 0.0,
    "zwei": 0.0,
    "zwfl": 0.0,
    "zbmi": 0.0,
}


def _anthro_is_installed() -> bool:
    executable = shutil.which("Rscript")
    if executable is None:
        return False
    try:
        check = subprocess.run(
            [
                executable,
                "--vanilla",
                "-e",
                "quit(status=if (requireNamespace('anthro', quietly=TRUE)) 0 else 1)",
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return check.returncode == 0


class AgeAndMeasurementTests(unittest.TestCase):
    def test_exact_age_in_days_and_completed_months(self) -> None:
        dob = date(2023, 5, 15)
        measurement_date = date(2026, 9, 29)
        self.assertEqual(calculate_age_in_days(dob, measurement_date), 1233)
        self.assertEqual(calculate_age_in_months(dob, measurement_date), 40)

    def test_measurement_before_birth_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "before date_of_birth"):
            calculate_age_in_days(date(2023, 5, 15), date(2023, 5, 14))

    def test_age_based_position_uses_731_day_boundary(self) -> None:
        self.assertEqual(
            resolve_measurement_position(730, None), ("length", "age-based assumed")
        )
        self.assertEqual(
            resolve_measurement_position(731, None), ("height", "age-based assumed")
        )

    def test_explicit_position_is_preserved(self) -> None:
        self.assertEqual(
            resolve_measurement_position(700, "height"),
            ("height", "explicitly provided"),
        )

    def test_invalid_position_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "measurement_position"):
            resolve_measurement_position(700, "standing")

    def test_sex_mapping_for_both_sexes(self) -> None:
        self.assertEqual(normalize_sex("male"), ("male", "m"))
        self.assertEqual(normalize_sex("female"), ("female", "f"))

    def test_assessment_passes_sex_days_and_explicit_position_to_anthro(self) -> None:
        with patch(
            "app.services.who.assessment.run_anthro",
            return_value=UNAVAILABLE_SCORE_RESULT,
        ) as anthro_call:
            assess_child(
                date(2023, 5, 15),
                "female",
                95.2,
                14.1,
                date(2026, 9, 29),
                "length",
            )
        anthro_call.assert_called_once_with("f", 1233, 14.1, 95.2, "L")

    def test_bmi_is_mathematical_only(self) -> None:
        self.assertEqual(calculate_bmi(14.1, 95.2), 15.56)


class APIValidationTests(unittest.TestCase):
    def test_invalid_birth_measurement_order_returns_400(self) -> None:
        request = {**BASE_REQUEST, "measurement_date": "2023-05-14"}
        response = CLIENT.post("/api/growth-assessment", json=request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("before date_of_birth", response.json()["detail"])

    def test_invalid_sex_returns_400(self) -> None:
        response = CLIENT.post(
            "/api/growth-assessment", json={**BASE_REQUEST, "sex": "unknown"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("sex must be", response.json()["detail"])

    def test_non_positive_measurement_returns_400(self) -> None:
        for field in ("height_cm", "weight_kg"):
            with self.subTest(field=field):
                response = CLIENT.post(
                    "/api/growth-assessment", json={**BASE_REQUEST, field: 0}
                )
                self.assertEqual(response.status_code, 400)

    def test_age_of_60_completed_months_returns_400(self) -> None:
        request = {
            **BASE_REQUEST,
            "date_of_birth": "2020-01-01",
            "measurement_date": "2025-01-01",
        }
        response = CLIENT.post("/api/growth-assessment", json=request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("below 60 completed months", response.json()["detail"])

    def test_optional_position_is_backward_compatible(self) -> None:
        model = GrowthAssessmentRequest(**BASE_REQUEST)
        self.assertIsNone(model.measurement_position)

    def test_r_or_anthro_unavailable_returns_generic_503(self) -> None:
        with patch("app.services.who.zscore.shutil.which", return_value=None):
            response = CLIENT.post("/api/growth-assessment", json=BASE_REQUEST)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "WHO Anthro calculation service is unavailable.",
        )

    def test_missing_scores_return_review_without_fabricated_values(self) -> None:
        with patch(
            "app.services.who.assessment.run_anthro",
            return_value=UNAVAILABLE_SCORE_RESULT,
        ):
            response = CLIENT.post("/api/growth-assessment", json=BASE_REQUEST)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        for indicator in ("haz", "waz", "whz", "baz"):
            self.assertIsNone(result[indicator])
        self.assertEqual(result["status"], "Requires Review")
        self.assertTrue(result["follow_up_required"])
        for field in ("haz_status", "waz_status", "whz_status"):
            self.assertEqual(result[field], "Requires Review")
        self.assertEqual(result["measurement_position"], "height")
        self.assertEqual(result["measurement_position_source"], "age-based assumed")


class WHOClassificationTests(unittest.TestCase):
    def test_classifications_follow_under_five_cutoffs(self) -> None:
        cases = (
            ("haz", 0.0, "Not stunted"),
            ("waz", 0.0, "Not underweight"),
            ("whz", 0.0, "Normal"),
            ("haz", -2.5, "Stunting"),
            ("haz", -3.5, "Severe stunting"),
            ("waz", -2.5, "Underweight"),
            ("waz", -3.5, "Severe underweight"),
            ("whz", -2.5, "Wasting"),
            ("whz", -3.5, "Severe wasting"),
            ("whz", 2.5, "Overweight"),
            ("whz", 3.5, "Obesity"),
            ("haz", -3.0, "Stunting"),
            ("haz", -2.0, "Not stunted"),
            ("waz", -3.0, "Underweight"),
            ("waz", -2.0, "Not underweight"),
            ("whz", -3.0, "Wasting"),
            ("whz", -2.0, "Normal"),
            ("whz", 2.0, "Normal"),
            ("whz", 3.0, "Overweight"),
        )
        status_fields = {
            "haz": "haz_status",
            "waz": "waz_status",
            "whz": "whz_status",
        }
        anthro_fields = {"haz": "zlen", "waz": "zwei", "whz": "zwfl"}

        for indicator, score, expected in cases:
            with self.subTest(indicator=indicator, score=score):
                result = {
                    **NORMAL_SCORE_RESULT,
                    anthro_fields[indicator]: score,
                }
                with patch(
                    "app.services.who.assessment.run_anthro",
                    return_value=result,
                ):
                    response = CLIENT.post(
                        "/api/growth-assessment", json=BASE_REQUEST
                    )
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(
                    response.json()[status_fields[indicator]], expected
                )

    def test_non_finite_scores_require_review(self) -> None:
        for score in (float("inf"), float("nan")):
            with self.subTest(score=score):
                result = {**NORMAL_SCORE_RESULT, "zlen": score}
                with patch(
                    "app.services.who.assessment.run_anthro",
                    return_value=result,
                ):
                    assessment = assess_child(
                        date(2023, 5, 15),
                        "female",
                        95.2,
                        14.1,
                        date(2026, 9, 29),
                    )
                self.assertEqual(assessment["haz_status"], "Requires Review")
                self.assertEqual(assessment["status"], "Requires Review")
                self.assertTrue(assessment["follow_up_required"])

    def test_flagged_results_require_review(self) -> None:
        flagged_result = {**NORMAL_SCORE_RESULT, "fwfl": True}
        with patch(
            "app.services.who.assessment.run_anthro",
            return_value=flagged_result,
        ):
            flagged_response = CLIENT.post(
                "/api/growth-assessment", json=BASE_REQUEST
            )
        flagged = flagged_response.json()
        self.assertEqual(flagged["status"], "Requires Review")
        self.assertTrue(flagged["follow_up_required"])
        self.assertEqual(flagged["whz_status"], "Requires Review")
        self.assertEqual(flagged["haz_status"], "Not stunted")
        self.assertEqual(flagged["waz_status"], "Not underweight")


@unittest.skipUnless(_anthro_is_installed(), "Rscript with CRAN anthro is not installed")
class AnthroIntegrationTests(unittest.TestCase):
    def test_both_sexes_return_all_scores_matching_direct_anthro(self) -> None:
        age_days = calculate_age_in_days(date(2023, 5, 15), date(2026, 9, 29))
        for api_sex, anthro_sex in (("female", "f"), ("male", "m")):
            with self.subTest(sex=api_sex):
                direct_result = run_anthro(
                    anthro_sex, age_days, 14.1, 95.2, "H"
                )
                response = CLIENT.post(
                    "/api/growth-assessment",
                    json={**BASE_REQUEST, "sex": api_sex, "measurement_position": "height"},
                )
                self.assertEqual(response.status_code, 200, response.text)
                api_result = response.json()
                for api_field, anthro_field in (
                    ("haz", "zlen"),
                    ("waz", "zwei"),
                    ("whz", "zwfl"),
                    ("baz", "zbmi"),
                    ("bmi", "cbmi"),
                ):
                    self.assertIsNotNone(direct_result[anthro_field])
                    self.assertEqual(api_result[api_field], direct_result[anthro_field])


if __name__ == "__main__":
    unittest.main()