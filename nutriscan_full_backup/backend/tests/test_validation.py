from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.schemas.auth import RegisterRequest
from app.domain.schemas.profile import HealthProfileUpdate
from app.infrastructure.db.models.health_profile import HealthProfile


class TestPasswordValidation:
    @pytest.mark.parametrize(
        "password",
        ["alllowercase1", "ALLUPPERCASE1", "NoDigitsHere", "short1A"],
    )
    def test_weak_passwords_rejected(self, password: str) -> None:
        with pytest.raises(ValidationError):
            RegisterRequest(name="Test User", email="test@example.com", password=password)

    def test_strong_password_accepted(self) -> None:
        req = RegisterRequest(name="Test User", email="test@example.com", password="StrongPass1")
        assert req.password == "StrongPass1"


class TestHealthProfileValidation:
    def test_age_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            HealthProfileUpdate(
                age=150,
                gender="male",
                height_cm=Decimal("175"),
                weight_kg=Decimal("70"),
                activity_level="moderate",
                fitness_goal="maintenance",
                diet_preference="non_vegetarian",
            )

    def test_meters_typed_as_cm_rejected(self) -> None:
        with pytest.raises(ValidationError):
            HealthProfileUpdate(
                age=30,
                gender="male",
                height_cm=Decimal("1.75"),
                weight_kg=Decimal("70"),
                activity_level="moderate",
                fitness_goal="maintenance",
                diet_preference="non_vegetarian",
            )


class TestBmiComputation:
    def test_bmi_matches_known_value(self) -> None:
        bmi = HealthProfile.compute_bmi(Decimal("165"), Decimal("60"))
        assert bmi == Decimal("22.0")

    def test_bmi_is_quantized_to_one_decimal(self) -> None:
        bmi = HealthProfile.compute_bmi(Decimal("180"), Decimal("82"))
        assert str(bmi).split(".")[1] == "3" or len(str(bmi).split(".")[1]) == 1
