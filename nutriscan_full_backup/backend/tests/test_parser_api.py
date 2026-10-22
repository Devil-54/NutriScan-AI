from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post(
        "/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD}
    )
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return login_resp.json()["data"]["access_token"]


class TestParserApi:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/parser/ingredients", json={"ocr_text": "Sugar, Salt"})
        assert response.status_code == 401

    async def test_parses_and_returns_expected_shape(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/parser/ingredients",
            json={"ocr_text": "Sugar, Wheat Flour (Maida), Palm Oil, Salt"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert set(data.keys()) == {"ingredients", "count"}
        assert data["ingredients"] == ["Sugar", "Wheat Flour", "Palm Oil", "Salt"]
        assert data["count"] == 4

    async def test_empty_input_returns_empty_list(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/parser/ingredients", json={"ocr_text": ""}, headers=headers)
        assert response.status_code == 200
        assert response.json()["data"] == {"ingredients": [], "count": 0}
