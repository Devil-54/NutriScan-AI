from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import CurrentUserDep, get_user_repository, require_role
from app.core.exceptions import NotFoundException
from app.domain.enums import UserRole
from app.domain.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.domain.schemas.user import UserListItem, UserRead
from app.infrastructure.db.repositories.user_repository import UserRepository
from sqlalchemy import func, select

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=SuccessResponse[UserRead])
async def get_me(
    current_user: CurrentUserDep,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> SuccessResponse[UserRead]:
    user = await user_repo.get_by_id(current_user.user_id)
    if user is None:
        raise NotFoundException("User not found", error_code="USER_NOT_FOUND")
    return SuccessResponse(data=UserRead.model_validate(user))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def deactivate_me(
    current_user: CurrentUserDep,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> None:
    """Soft delete: deactivate rather than hard-delete, preserving referential
    integrity with scans/audit history that will exist from later phases."""
    user = await user_repo.get_by_id(current_user.user_id)
    if user is None:
        raise NotFoundException("User not found", error_code="USER_NOT_FOUND")
    user.is_active = False
    await user_repo.commit()


@router.get(
    "",
    response_model=PaginatedResponse[UserListItem],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def list_users(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, description="Search by name or email"),
) -> PaginatedResponse[UserListItem]:
    from app.infrastructure.db.models.user import User

    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)

    if q:
        pattern = f"%{q}%"
        stmt = stmt.where((User.name.ilike(pattern)) | (User.email.ilike(pattern)))
        count_stmt = count_stmt.where((User.name.ilike(pattern)) | (User.email.ilike(pattern)))

    total = (await user_repo.session.execute(count_stmt)).scalar_one()
    stmt = stmt.offset((page - 1) * limit).limit(limit).order_by(User.created_at.desc())
    result = await user_repo.session.execute(stmt)
    users = result.scalars().all()

    total_pages = (total + limit - 1) // limit if total else 0

    return PaginatedResponse(
        data=[UserListItem.model_validate(u) for u in users],
        meta=PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages),
    )
