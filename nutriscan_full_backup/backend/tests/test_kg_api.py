from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass1"


async def _register_and_login(client: AsyncClient, email: str = "jane@example.com") -> str:
    await client.post("/api/v1/auth/register", json={"name": "Jane Doe", "email": email, "password": VALID_PASSWORD})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return resp.json()["data"]["access_token"]


class TestSearchEndpointsAuth:
    async def test_ingredient_search_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/kg/ingredients/search?q=sugar")
        assert response.status_code == 401

    async def test_product_search_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/kg/products/search?q=chips")
        assert response.status_code == 401

    async def test_allergen_search_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/kg/allergens/search?q=peanut")
        assert response.status_code == 401

    async def test_additive_search_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/kg/additives/search?q=INS")
        assert response.status_code == 401


class TestSearchEndpointsEmptyResults:
    async def test_ingredient_search_empty_db(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/kg/ingredients/search?q=sugar", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"] == []


class TestImportEndpoint:
    async def test_import_requires_admin(self, client: AsyncClient) -> None:
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/kg/import",
            json={"source": "open_food_facts", "file_path": "/tmp/does_not_matter.csv"},
            headers=headers,
        )
        assert response.status_code == 403

    async def test_import_admin_gate_blocks_before_validation(self, client: AsyncClient) -> None:
        """Non-admins are blocked by RBAC regardless of payload validity - this is correct
        fail-closed behavior (invalid payloads should not be validated for unauthorized callers)."""
        token = await _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/kg/import", json={"source": "bad_source", "file_path": "x.csv"}, headers=headers
        )
        assert response.status_code == 403


async def test_import_request_schema_rejects_unsupported_source() -> None:
    from pydantic import ValidationError

    from app.domain.schemas.knowledge_graph import ImportDatasetRequest

    try:
        ImportDatasetRequest(source="bad_source", file_path="x.csv")
        assert False, "expected ValidationError"
    except ValidationError:
        pass
