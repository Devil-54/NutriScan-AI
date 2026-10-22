from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import (
    CurrentUserDep,
    get_additive_repository,
    get_allergen_repository,
    get_category_repository,
    get_food_product_repository,
    get_import_job_repository,
    get_ingredient_repository,
    require_role,
)
from app.domain.enums import UserRole
from app.domain.schemas.common import SuccessResponse
from app.domain.schemas.knowledge_graph import (
    AdditiveSearchResult,
    AllergenSearchResult,
    ImportDatasetRequest,
    ImportJobRead,
    IngredientSearchResult,
    ProductSearchResult,
)
from app.infrastructure.db.repositories.additive_repository import AdditiveRepository
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.use_cases.knowledge_graph.import_dataset import ImportDatasetUseCase
from app.use_cases.knowledge_graph.search import (
    SearchAdditiveUseCase,
    SearchAllergenUseCase,
    SearchIngredientUseCase,
    SearchProductUseCase,
)

router = APIRouter(prefix="/kg", tags=["Knowledge Graph"])


@router.post(
    "/import", response_model=SuccessResponse[ImportJobRead], dependencies=[Depends(require_role(UserRole.ADMIN))]
)
async def import_dataset(
    payload: ImportDatasetRequest,
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
    product_repo: Annotated[FoodProductRepository, Depends(get_food_product_repository)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
    import_job_repo: Annotated[ImportJobRepository, Depends(get_import_job_repository)],
) -> SuccessResponse[ImportJobRead]:
    use_case = ImportDatasetUseCase(ingredient_repo, product_repo, category_repo, import_job_repo)
    result = await use_case.execute(payload)
    return SuccessResponse(data=result)


@router.get("/ingredients/search", response_model=SuccessResponse[list[IngredientSearchResult]])
async def search_ingredients(
    current_user: CurrentUserDep,
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> SuccessResponse[list[IngredientSearchResult]]:
    use_case = SearchIngredientUseCase(ingredient_repo)
    result = await use_case.execute(q, limit)
    return SuccessResponse(data=result)


@router.get("/products/search", response_model=SuccessResponse[list[ProductSearchResult]])
async def search_products(
    current_user: CurrentUserDep,
    product_repo: Annotated[FoodProductRepository, Depends(get_food_product_repository)],
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> SuccessResponse[list[ProductSearchResult]]:
    use_case = SearchProductUseCase(product_repo)
    result = await use_case.execute(q, limit)
    return SuccessResponse(data=result)


@router.get("/allergens/search", response_model=SuccessResponse[list[AllergenSearchResult]])
async def search_allergens(
    current_user: CurrentUserDep,
    allergen_repo: Annotated[AllergenRepository, Depends(get_allergen_repository)],
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> SuccessResponse[list[AllergenSearchResult]]:
    use_case = SearchAllergenUseCase(allergen_repo)
    result = await use_case.execute(q, limit)
    return SuccessResponse(data=result)


@router.get("/additives/search", response_model=SuccessResponse[list[AdditiveSearchResult]])
async def search_additives(
    current_user: CurrentUserDep,
    additive_repo: Annotated[AdditiveRepository, Depends(get_additive_repository)],
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> SuccessResponse[list[AdditiveSearchResult]]:
    use_case = SearchAdditiveUseCase(additive_repo)
    result = await use_case.execute(q, limit)
    return SuccessResponse(data=result)
