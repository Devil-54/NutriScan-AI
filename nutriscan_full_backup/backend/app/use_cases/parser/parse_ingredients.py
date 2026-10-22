from __future__ import annotations

import time
import uuid

from app.core.logging import get_logger
from app.domain.schemas.parser import ParseIngredientsResponse
from app.infrastructure.db.models.ingredient_parse import IngredientParse
from app.infrastructure.db.repositories.ingredient_parse_repository import IngredientParseRepository
from app.infrastructure.parser.ingredient_parser import PARSER_VERSION, parse_ingredients

logger = get_logger()


class ParseIngredientsUseCase:
    def __init__(self, parse_repo: IngredientParseRepository) -> None:
        self.parse_repo = parse_repo

    async def execute(self, ocr_text: str, user_id: uuid.UUID | None) -> ParseIngredientsResponse:
        logger.bind(event="PARSER_STARTED").info("Ingredient parsing started")
        start = time.perf_counter()

        result = parse_ingredients(ocr_text)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.bind(
            event="PARSER_FINISHED", ingredient_count=result.count, execution_time_ms=elapsed_ms
        ).info("Ingredient parsing finished")

        row = IngredientParse(
            user_id=user_id,
            raw_text=ocr_text,
            parsed_ingredients=result.ingredients,
            ingredient_count=result.count,
            parser_version=PARSER_VERSION,
        )
        self.parse_repo.add(row)
        await self.parse_repo.commit()

        return ParseIngredientsResponse(ingredients=result.ingredients, count=result.count)
