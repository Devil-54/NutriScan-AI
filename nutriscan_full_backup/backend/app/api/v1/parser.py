from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import CurrentUserDep, get_ingredient_parse_repository
from app.domain.schemas.common import SuccessResponse
from app.domain.schemas.parser import ParseIngredientsRequest, ParseIngredientsResponse
from app.infrastructure.db.repositories.ingredient_parse_repository import IngredientParseRepository
from app.use_cases.parser.parse_ingredients import ParseIngredientsUseCase

router = APIRouter(prefix="/parser", tags=["Ingredient Parser"])


@router.post("/ingredients", response_model=SuccessResponse[ParseIngredientsResponse])
async def parse_ingredients_endpoint(
    payload: ParseIngredientsRequest,
    current_user: CurrentUserDep,
    parse_repo: Annotated[IngredientParseRepository, Depends(get_ingredient_parse_repository)],
) -> SuccessResponse[ParseIngredientsResponse]:
    use_case = ParseIngredientsUseCase(parse_repo)
    result = await use_case.execute(payload.ocr_text, current_user.user_id)
    return SuccessResponse(data=result)
