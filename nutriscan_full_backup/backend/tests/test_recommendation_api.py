from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post("/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return resp.json()["data"]["access_token"]


class TestGenerateEndpoint:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/recommendation/generate", json={"ingredients": ["Sugar"]})
        assert response.status_code == 401

    async def test_empty_ingredients_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/v1/recommendation/generate", json={"ingredients": []}, headers=headers)
        assert response.status_code == 400

    async def test_returns_full_shape(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/recommendation/generate", json={"ingredients": ["Rice", "Water"]}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        expected_keys = {
            "status", "risk_level", "safe_foods", "unsafe_foods", "alternatives", "health_tips",
            "nutrition_advice", "lifestyle_advice", "ingredient_warnings", "recommendation_score",
            "confidence_score", "reasons",
        }
        assert expected_keys.issubset(data.keys())
        assert data["status"] == "safe"

    async def test_high_sugar_with_nutrition_input(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/recommendation/generate",
            json={"ingredients": ["Sugar"], "nutrition": {"sugar_g": 30}},
            headers=headers,
        )
        assert response.status_code == 200


class TestHistoryEndpoint:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/recommendation/history")
        assert response.status_code == 401

    async def test_records_generation_in_history(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post("/api/v1/recommendation/generate", json={"ingredients": ["Rice"]}, headers=headers)
        await client.post("/api/v1/recommendation/generate", json={"ingredients": ["Salt"]}, headers=headers)

        response = await client.get("/api/v1/recommendation/history", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["total"] == 2

    async def test_history_isolated_per_user(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="a@example.com")
        await client.post(
            "/api/v1/recommendation/generate", json={"ingredients": ["Rice"]}, headers={"Authorization": f"Bearer {token_a}"}
        )
        token_b = await _register_and_login(client, email="b@example.com")
        response = await client.get(
            "/api/v1/recommendation/history", headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response.json()["meta"]["total"] == 0
