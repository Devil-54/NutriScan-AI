from __future__ import annotations

import io

import pytest
from httpx import AsyncClient
from PIL import Image, ImageDraw

from app.api.v1.deps import get_ocr_service
from app.domain.enums import OcrEngine
from app.infrastructure.ocr.ocr_engines import BaseOcrEngine, OcrResult
from app.infrastructure.ocr.ocr_service import OcrService
from app.main import app

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


class FakeEngine(BaseOcrEngine):
    def __init__(self, engine_name: OcrEngine, text: str, confidence: float):
        self.engine_name = engine_name
        self._text = text
        self._confidence = confidence

    def _run(self, img) -> OcrResult:
        return OcrResult(text=self._text, confidence=self._confidence, engine=self.engine_name, boxes=[])


@pytest.fixture(autouse=True)
def _override_ocr_service():
    fake_service = OcrService(
        primary=FakeEngine(OcrEngine.PADDLEOCR, "Sugar, Salt, Wheat Flour", 96.5),
        fallback=FakeEngine(OcrEngine.PADDLEOCR, "fallback text", 90.0),
    )
    app.dependency_overrides[get_ocr_service] = lambda: fake_service
    yield
    app.dependency_overrides.pop(get_ocr_service, None)


def _sharp_image_bytes(w=800, h=400) -> bytes:
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in range(20, h - 20, 30):
        draw.line([(20, y), (w - 20, y + 5)], fill=(0, 0, 0), width=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post(
        "/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD}
    )
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return login_resp.json()["data"]["access_token"]


async def _upload_scan(client: AsyncClient, headers: dict) -> str:
    resp = await client.post(
        "/api/v1/scans/upload",
        files={"file": ("label.jpg", _sharp_image_bytes(), "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["data"]["scan_id"]


class TestOcrProcess:
    async def test_process_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/ocr/process?scan_id=00000000-0000-0000-0000-000000000000")
        assert response.status_code == 401

    async def test_process_returns_expected_shape(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)

        response = await client.post(f"/api/v1/ocr/process?scan_id={scan_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert set(data.keys()) == {
            "ingredients_text", "confidence", "engine", "product_name", "brand", "category", "nutrition"
        }
        assert data["ingredients_text"] == "Sugar, Salt, Wheat Flour"
        assert data["confidence"] == 96.5
        assert data["engine"] == "PaddleOCR"

    async def test_process_nonexistent_scan_404(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.post(f"/api/v1/ocr/process?scan_id={fake_id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "SCAN_NOT_FOUND"

    async def test_process_other_users_scan_404(self, client: AsyncClient) -> None:
        token_a = await _register_and_login(client, email="a@example.com")
        scan_id = await _upload_scan(client, {"Authorization": f"Bearer {token_a}"})

        token_b = await _register_and_login(client, email="b@example.com")
        response = await client.post(
            f"/api/v1/ocr/process?scan_id={scan_id}", headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response.status_code == 404

    async def test_double_process_rejected(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)

        first = await client.post(f"/api/v1/ocr/process?scan_id={scan_id}", headers=headers)
        assert first.status_code == 200

        second = await client.post(f"/api/v1/ocr/process?scan_id={scan_id}", headers=headers)
        assert second.status_code == 400
        assert second.json()["error"]["code"] == "OCR_ALREADY_PROCESSED"


class TestOcrStatus:
    async def test_status_pending_before_processing(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)

        response = await client.get(f"/api/v1/ocr/status/{scan_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "pending"

    async def test_status_completed_after_processing(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)
        await client.post(f"/api/v1/ocr/process?scan_id={scan_id}", headers=headers)

        response = await client.get(f"/api/v1/ocr/status/{scan_id}", headers=headers)
        assert response.json()["data"]["status"] == "completed"
        assert response.json()["data"]["processing_time_ms"] is not None


class TestOcrResult:
    async def test_result_not_ready_before_processing(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)

        response = await client.get(f"/api/v1/ocr/result/{scan_id}", headers=headers)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "OCR_NOT_READY"

    async def test_result_available_after_processing(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        scan_id = await _upload_scan(client, headers)
        await client.post(f"/api/v1/ocr/process?scan_id={scan_id}", headers=headers)

        response = await client.get(f"/api/v1/ocr/result/{scan_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["ingredients_text"] == "Sugar, Salt, Wheat Flour"
        assert data["engine"] == "PaddleOCR"
