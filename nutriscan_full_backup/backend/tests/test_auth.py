from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register(client: AsyncClient, email: str = "jane@example.com") -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD},
    )
    return response.json()


class TestRegister:
    async def test_register_success(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={"name": "Jane Doe", "email": "jane@example.com", "password": VALID_PASSWORD},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["email"] == "jane@example.com"

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/register",
            json={"name": "Jane Two", "email": "jane@example.com", "password": VALID_PASSWORD},
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    async def test_register_weak_password_rejected(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={"name": "Jane Doe", "email": "weak@example.com", "password": "weak"},
        )
        assert response.status_code == 422 or response.status_code == 400

    async def test_register_password_over_bcrypt_byte_limit_rejected(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Jane Doe",
                "email": "long-password@example.com",
                "password": "StrongPass1" + "x" * 62,
            },
        )
        assert response.status_code in (400, 422)


class TestLogin:
    async def test_login_success(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/login", json={"email": "jane@example.com", "password": "WrongPass1"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_login_unknown_email_same_generic_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login", json={"email": "nobody@example.com", "password": VALID_PASSWORD}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


class TestRefreshAndLogout:
    async def test_refresh_token_rotation(self, client: AsyncClient) -> None:
        await _register(client)
        login_resp = await client.post(
            "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
        )
        refresh_token = login_resp.json()["data"]["refresh_token"]

        refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()["data"]
        assert new_tokens["refresh_token"] != refresh_token

        # Reusing the old (now-revoked) refresh token must fail.
        reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert reuse_resp.status_code == 401

    async def test_logout_revokes_refresh_token(self, client: AsyncClient) -> None:
        await _register(client)
        login_resp = await client.post(
            "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
        )
        data = login_resp.json()["data"]
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        logout_resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_resp.status_code == 204

        refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 401
