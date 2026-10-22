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


async def _upload(client: AsyncClient, headers: dict) -> str:
    resp = await client.post(
        "/api/v1/scans/upload",
        files={"file": ("label.jpg", make_test_image_bytes(400, 400), "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["data"]["scan_id"]


class TestScanDetailAndStatus:
    async def test_get_detail_success(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        response = await client.get(f"/api/v1/scans/{scan_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"]["scan_id"] == scan_id

    async def test_get_status_success(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        response = await client.get(f"/api/v1/scans/{scan_id}/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "uploaded"

    async def test_get_nonexistent_scan_returns_404(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.get(f"/api/v1/scans/{fake_id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "SCAN_NOT_FOUND"

    async def test_other_users_scan_is_not_accessible(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="a@example.com")
        scan_id = await _upload(client, {"Authorization": f"Bearer {token_a}"})

        token_b = await _register_and_login(client, email="b@example.com")
        response = await client.get(f"/api/v1/scans/{scan_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert response.status_code == 404


class TestScanMetadataUpdate:
    async def test_update_notes(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        response = await client.patch(
            f"/api/v1/scans/{scan_id}", json={"notes": "Bought at the store on MG Road"}, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["notes"] == "Bought at the store on MG Road"


class TestScanDeleteAndRestore:
    async def test_delete_then_hidden_from_history(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        delete_resp = await client.delete(f"/api/v1/scans/{scan_id}", headers=headers)
        assert delete_resp.status_code == 204

        history_resp = await client.get("/api/v1/scans/history", headers=headers)
        assert history_resp.json()["meta"]["total"] == 0

    async def test_delete_then_not_accessible_via_status(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)
        await client.delete(f"/api/v1/scans/{scan_id}", headers=headers)

        response = await client.get(f"/api/v1/scans/{scan_id}/status", headers=headers)
        assert response.status_code == 404

    async def test_restore_brings_scan_back(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)
        await client.delete(f"/api/v1/scans/{scan_id}", headers=headers)

        restore_resp = await client.post(f"/api/v1/scans/{scan_id}/restore", headers=headers)
        assert restore_resp.status_code == 200

        history_resp = await client.get("/api/v1/scans/history", headers=headers)
        assert history_resp.json()["meta"]["total"] == 1

    async def test_restore_non_deleted_scan_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        response = await client.post(f"/api/v1/scans/{scan_id}/restore", headers=headers)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "SCAN_NOT_DELETED"


class TestScanCancel:
    async def test_cancel_uploaded_scan_succeeds(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)

        response = await client.post(f"/api/v1/scans/{scan_id}/cancel", headers=headers)
        assert response.status_code == 204

        status_resp = await client.get(f"/api/v1/scans/{scan_id}/status", headers=headers)
        assert status_resp.json()["data"]["status"] == "cancelled"

    async def test_cancel_already_cancelled_scan_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload(client, headers)
        await client.post(f"/api/v1/scans/{scan_id}/cancel", headers=headers)

        response = await client.post(f"/api/v1/scans/{scan_id}/cancel", headers=headers)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_SCAN_STATE"


class TestScanAdminEndpoints:
    async def test_regular_user_cannot_access_cleanup(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/scans/admin/cleanup-expired", headers=headers)
        assert response.status_code == 403

    async def test_regular_user_cannot_access_orphans(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/scans/admin/orphans", headers=headers)
        assert response.status_code == 403
