"""
Standard response envelopes, matching the Phase 2 API convention:

Success: {"success": true, "data": {...}, "meta": {...}}
Error:   {"success": false, "error": {"code": "...", "message": "..."}}
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: DataT
    meta: dict[str, Any] | None = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: list[DataT]
    meta: PaginationMeta
