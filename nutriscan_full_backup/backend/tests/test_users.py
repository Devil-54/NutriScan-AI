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


class TestGetMe:
    async def test_get_me_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_get_me_success(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "jane@example.com"

    async def test_get_me_invalid_token_rejected(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer not-a-real-token"})
        assert response.status_code == 401


class TestUserListRBAC:
    async def test_regular_user_cannot_list_users(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN_ROLE"
