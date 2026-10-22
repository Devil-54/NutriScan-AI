from __future__ import annotations

from pydantic import BaseModel, Field


class ParseIngredientsRequest(BaseModel):
    ocr_text: str = Field(min_length=0, max_length=20000)


class ParseIngredientsResponse(BaseModel):
    ingredients: list[str]
    count: int
