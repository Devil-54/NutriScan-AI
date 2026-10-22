from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"

VALID_PROFILE_PAYLOAD = {
    "age": 28,
    "gender": "female",
    "height_cm": "165.00",
    "weight_kg": "60.00",
    "activity_level": "moderate",
    "fitness_goal": "weight_loss",
    "diet_preference": "vegetarian",
    "pregnancy_status": False,
    "period_status": None,
    "allergies": "peanuts, milk",
    "diseases": "diabetes, hypertension",
    "emergency_notes": None,
}


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post(
        "/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD}
    )
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return login_resp.json()["data"]["access_token"]


class TestHealthProfile:
    async def test_get_profile_before_creation_returns_null_profile(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.get("/api/v1/profile/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["data"]["health_profile"] is None

    async def test_create_and_bmi_is_server_computed(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.put("/api/v1/profile/me", json=VALID_PROFILE_PAYLOAD, headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]

        # BMI = 60 / (1.65^2) ≈ 22.0 - client never supplies this value.
        assert float(data["bmi"]) == pytest.approx(22.0, abs=0.1)
        assert data["allergies"] == "peanuts, milk"
        assert data["diseases"] == "diabetes, hypertension"

    async def test_implausible_height_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        bad_payload = {**VALID_PROFILE_PAYLOAD, "height_cm": "1.65"}  # meters typed into a cm field
        response = await client.put("/api/v1/profile/me", json=bad_payload, headers=headers)
        assert response.status_code in (400, 422)


class TestAllergiesValidation:
    async def test_unknown_allergen_id_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.put(
            "/api/v1/profile/me/allergies",
            json={"allergies": [{"allergen_id": fake_id, "severity": "severe"}]},
            headers=headers,
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "UNKNOWN_ALLERGEN"
