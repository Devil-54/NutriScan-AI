from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_test_image_bytes

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post(
        "/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD}
    )
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return login_resp.json()["data"]["access_token"]


async def _upload(client: AsyncClient, headers: dict, seed: int, filename: str = "label.jpg") -> str:
    image_bytes = make_test_image_bytes(400 + seed, 400 + seed)  # vary dimensions to vary checksum
    resp = await client.post(
        "/api/v1/scans/upload",
        files={"file": (filename, image_bytes, "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["data"]["scan_id"]


class TestScanHistory:
    async def test_history_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/scans/history")
        assert response.status_code == 401

    async def test_history_pagination(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        for i in range(5):
            await _upload(client, headers, seed=i)

        response = await client.get("/api/v1/scans/history?page=1&limit=2", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 2
        assert body["meta"]["total"] == 5
        assert body["meta"]["total_pages"] == 3

    async def test_history_only_shows_own_scans(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="a@example.com")
        await _upload(client, {"Authorization": f"Bearer {token_a}"}, seed=1)

        token_b = await _register_and_login(client, email="b@example.com")
        response = await client.get("/api/v1/scans/history", headers={"Authorization": f"Bearer {token_b}"})
        assert response.status_code == 200
        assert response.json()["meta"]["total"] == 0

    async def test_history_stats_are_authenticated_and_use_saved_scans(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="stats-a@example.com")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        await _upload(client, headers_a, seed=1)
        await _upload(client, headers_a, seed=2)

        token_b = await _register_and_login(client, email="stats-b@example.com")
        response = await client.get(
            "/api/v1/scans/history/stats",
            headers={"Authorization": f"Bearer {token_b}"},
        )

        assert response.status_code == 200
        assert response.json()["data"] == {
            "total_scans": 0,
            "safe_foods": 0,
            "warnings": 0,
        }

    async def test_history_search_by_filename(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        await _upload(client, headers, seed=1, filename="chips_packet.jpg")
        await _upload(client, headers, seed=2, filename="soda_can.jpg")

        response = await client.get("/api/v1/scans/history?search=chips", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["total"] == 1
        assert "chips" in body["data"][0]["original_filename"]

    async def test_history_sort_direction(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        first_id = await _upload(client, headers, seed=1)
        second_id = await _upload(client, headers, seed=2)

        response = await client.get("/api/v1/scans/history?sort_dir=asc", headers=headers)
        body = response.json()
        ids_in_order = [row["scan_id"] for row in body["data"]]
        assert ids_in_order.index(first_id) < ids_in_order.index(second_id)
