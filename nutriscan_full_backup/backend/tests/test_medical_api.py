from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post("/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return resp.json()["data"]["access_token"]


class TestMedicalProfileEndpoint:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/medical/profile")
        assert response.status_code == 401

    async def test_returns_derived_summary(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/v1/medical/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert set(data.keys()) == {"conditions", "allergies", "age", "is_pregnant"}
        assert data["conditions"] == []
        assert data["is_pregnant"] is False


class TestMedicalEvaluateEndpoint:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/medical/evaluate", json={"ingredients": ["Sugar"]})
        assert response.status_code == 401

    async def test_empty_ingredients_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/v1/medical/evaluate", json={"ingredients": []}, headers=headers)
        assert response.status_code == 400

    async def test_no_conditions_returns_safe(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/medical/evaluate", json={"ingredients": ["Rice", "Water"]}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "safe"
        assert data["health_score"] == 100

    async def test_evaluate_end_to_end_completes(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/medical/evaluate",
            json={"ingredients": ["Sugar"], "nutrition": {"sugar_g": 30}},
            headers=headers,
        )
        assert response.status_code == 200
        assert "status" in response.json()["data"]


class TestMedicalHistoryEndpoint:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/medical/history")
        assert response.status_code == 401

    async def test_records_evaluation_in_history(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        await client.post("/api/v1/medical/evaluate", json={"ingredients": ["Rice"]}, headers=headers)
        await client.post("/api/v1/medical/evaluate", json={"ingredients": ["Salt"]}, headers=headers)

        response = await client.get("/api/v1/medical/history", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["total"] == 2
        assert len(body["data"]) == 2

    async def test_history_isolated_per_user(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="a@example.com")
        await client.post(
            "/api/v1/medical/evaluate", json={"ingredients": ["Rice"]}, headers={"Authorization": f"Bearer {token_a}"}
        )

        token_b = await _register_and_login(client, email="b@example.com")
        response = await client.get("/api/v1/medical/history", headers={"Authorization": f"Bearer {token_b}"})
        assert response.json()["meta"]["total"] == 0


class TestKgAutoResolution:
    async def test_evaluate_works_with_unresolvable_ingredient(self, client: AsyncClient) -> None:
        """Confirms /medical/evaluate degrades gracefully (no crash, SAFE default) when the
        Knowledge Graph has no matching entry yet - the 'works before dataset import too' contract."""
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/medical/evaluate", json={"ingredients": ["UnknownIngredientXYZ"]}, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "safe"
