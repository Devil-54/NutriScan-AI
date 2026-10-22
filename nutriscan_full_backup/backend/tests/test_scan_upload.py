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


def _files(image_bytes: bytes, filename: str = "label.jpg", content_type: str = "image/jpeg") -> dict:
    return {"file": (filename, image_bytes, content_type)}


class TestScanUpload:
    async def test_upload_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/scans/upload", files=_files(make_test_image_bytes()))
        assert response.status_code == 401

    async def test_valid_upload_succeeds(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(make_test_image_bytes(500, 500)),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["status"] == "uploaded"
        assert data["width_px"] == 500
        assert data["height_px"] == 500
        assert len(data["checksum_sha256"]) == 64

    async def test_upload_rejects_disallowed_extension(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(b"not-really-an-image", filename="label.txt", content_type="text/plain"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"

    async def test_upload_rejects_corrupted_image(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(b"\xff\xd8\xff\xe0garbagenotarealjpeg", filename="label.jpg"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "INVALID_IMAGE"

    async def test_upload_rejects_empty_file(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(b"", filename="label.jpg"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "EMPTY_FILE"

    async def test_upload_rejects_below_minimum_resolution(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(make_test_image_bytes(50, 50)),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "IMAGE_TOO_SMALL"

    async def test_upload_rejects_oversized_file(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        # Bogus oversized payload - fails the declared-size check before any image parsing is attempted.
        oversized = b"0" * (9 * 1024 * 1024)
        response = await client.post(
            "/api/v1/scans/upload",
            files=_files(oversized, filename="label.jpg"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "FILE_TOO_LARGE"

    async def test_duplicate_upload_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        image_bytes = make_test_image_bytes(400, 400)

        first = await client.post("/api/v1/scans/upload", files=_files(image_bytes), headers=headers)
        assert first.status_code == 201

        second = await client.post("/api/v1/scans/upload", files=_files(image_bytes), headers=headers)
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "DUPLICATE_UPLOAD"

    async def test_same_image_different_users_not_duplicate(self, client: AsyncClient) -> None:
        image_bytes = make_test_image_bytes(400, 400)

        token_a = await _register_and_login(client, email="a@example.com")
        resp_a = await client.post(
            "/api/v1/scans/upload", files=_files(image_bytes), headers={"Authorization": f"Bearer {token_a}"}
        )
        assert resp_a.status_code == 201

        token_b = await _register_and_login(client, email="b@example.com")
        resp_b = await client.post(
            "/api/v1/scans/upload", files=_files(image_bytes), headers={"Authorization": f"Bearer {token_b}"}
        )
        assert resp_b.status_code == 201
