from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status

from app.api.v1.deps import (
    CurrentUserDep,
    get_audit_log_repository,
    get_client_ip,
    get_scan_repository,
    get_scan_storage_service,
    get_storage_backend,
    get_virus_scanner,
    require_role,
)
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.core.logging import get_logger
from app.domain.enums import ScanStatus, UserRole
from app.domain.schemas.common import PaginatedResponse, SuccessResponse
from app.domain.schemas.scan import (
    PersonalizedScanResult,
    ScanHistoryStats,
    ScanListItem,
    ScanRead,
    ScanStatusRead,
    ScanUpdateRequest,
    ScanUploadResponse,
)
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.storage.scan_storage_service import ScanStorageService
from app.infrastructure.storage.storage_backend import StorageBackend
from app.infrastructure.storage.virus_scanner import VirusScanner
from app.middleware.rate_limit_middleware import limiter
from app.use_cases.scans.cancel_scan import CancelScanUseCase
from app.use_cases.scans.cleanup_expired_scans import CleanupExpiredScansUseCase, DetectOrphanFilesUseCase
from app.use_cases.scans.delete_scan import DeleteScanUseCase
from app.use_cases.scans.get_scan_detail import GetScanDetailUseCase
from app.use_cases.scans.get_scan_status import GetScanStatusUseCase
from app.use_cases.scans.list_scan_history import ListScanHistoryUseCase
from app.use_cases.scans.restore_scan import RestoreScanUseCase
from app.use_cases.scans.update_scan_metadata import UpdateScanMetadataUseCase
from app.use_cases.scans.upload_scan import UploadScanUseCase

router = APIRouter(prefix="/scans", tags=["Food Scans"])
logger = get_logger()


def _personalized_result(scan) -> PersonalizedScanResult | None:
    """Serialize the stored evaluation only; never recalculate from today's profile."""
    evaluation = scan.personalized_evaluation
    if evaluation is None:
        return None
    return PersonalizedScanResult(
        status=evaluation.status,
        risk_level=evaluation.risk_level,
        health_score=evaluation.health_score,
        ingredients=evaluation.ingredients,
        safe_ingredients=evaluation.safe_ingredients,
        unsafe_ingredients=evaluation.unsafe_ingredients,
        reasons=evaluation.reasons,
        recommendations=evaluation.recommendations,
        triggered_rules=evaluation.triggered_rules,
        profile_snapshot=evaluation.profile_snapshot,
        nutrition_snapshot=evaluation.nutrition_snapshot,
        alternatives=evaluation.alternatives or [],
        health_tips=evaluation.health_tips or [],
        nutrition_advice=evaluation.nutrition_advice or [],
        lifestyle_advice=evaluation.lifestyle_advice or [],
        ingredient_warnings=evaluation.ingredient_warnings or [],
        confidence_score=evaluation.confidence_score,
    )


def _scan_read(scan) -> ScanRead:
    return ScanRead(
        scan_id=scan.scan_id, original_filename=scan.original_filename,
        mime_type=scan.mime_type, file_size_bytes=scan.file_size_bytes,
        width_px=scan.width_px, height_px=scan.height_px, status=scan.status,
        processing_stage=scan.processing_stage, retry_count=scan.retry_count,
        error_message=scan.error_message, notes=scan.notes,
        product_name=scan.product_name,
        raw_ocr_text=scan.ocr_result.ingredients_text if scan.ocr_result else None,
        personalized_result=_personalized_result(scan),
        created_at=scan.created_at, updated_at=scan.updated_at,
    )


def _scan_list_item(scan) -> ScanListItem:
    return ScanListItem(
        scan_id=scan.scan_id, original_filename=scan.original_filename,
        status=scan.status, file_size_bytes=scan.file_size_bytes,
        created_at=scan.created_at, product_name=scan.product_name,
        raw_ocr_text=scan.ocr_result.ingredients_text if scan.ocr_result else None,
        personalized_result=_personalized_result(scan),
    )


@router.get("/history/stats", response_model=SuccessResponse[ScanHistoryStats])
async def get_scan_history_stats(
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
) -> SuccessResponse[ScanHistoryStats]:
    """Statistics from the same user-owned, saved scan records as history."""
    total, safe, warnings = await scan_repo.history_stats(current_user.user_id)
    return SuccessResponse(
        data=ScanHistoryStats(total_scans=total, safe_foods=safe, warnings=warnings)
    )


@router.post("/upload", response_model=SuccessResponse[ScanUploadResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_scan(
    request: Request,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    storage_service: Annotated[ScanStorageService, Depends(get_scan_storage_service)],
    virus_scanner: Annotated[VirusScanner, Depends(get_virus_scanner)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    file: UploadFile = File(...),
) -> SuccessResponse[ScanUploadResponse]:
    if file.filename is None:
        raise ValidationException("Uploaded file must have a filename", error_code="MISSING_FILENAME")

    file_bytes = await file.read()

    use_case = UploadScanUseCase(scan_repo, storage_service, virus_scanner, audit_repo)
    result = await use_case.execute(
        user_id=current_user.user_id,
        file_bytes=file_bytes,
        claimed_filename=file.filename,
        ip_address=get_client_ip(request),
    )
    return SuccessResponse(data=result)


@router.get("/history", response_model=PaginatedResponse[ScanListItem])
async def list_scan_history(
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: ScanStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, description="Search by filename or notes"),
    sort_by: str = Query(default="created_at", pattern="^(created_at|updated_at|status|file_size_bytes)$"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> PaginatedResponse[ScanRead]:
    use_case = ListScanHistoryUseCase(scan_repo)
    items, meta = await use_case.execute(
        user_id=current_user.user_id,
        page=page,
        limit=limit,
        status=status_filter,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    logger.bind(
        event="HISTORY_REQUEST",
        records_found=meta.total,
    ).info("History request completed")
    return PaginatedResponse(data=[_scan_list_item(item) for item in items], meta=meta)


@router.get("/{scan_id}", response_model=SuccessResponse[ScanRead])
async def get_scan_detail(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
) -> SuccessResponse[ScanRead]:
    use_case = GetScanDetailUseCase(scan_repo)
    result = await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data=_scan_read(result))


@router.get("/{scan_id}/status", response_model=SuccessResponse[ScanStatusRead])
async def get_scan_status(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
) -> SuccessResponse[ScanStatusRead]:
    use_case = GetScanStatusUseCase(scan_repo)
    result = await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data=result)


@router.patch("/{scan_id}", response_model=SuccessResponse[ScanRead])
async def update_scan_metadata(
    scan_id: UUID,
    payload: ScanUpdateRequest,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[ScanRead]:
    use_case = UpdateScanMetadataUseCase(scan_repo, audit_repo)
    result = await use_case.execute(scan_id, current_user.user_id, payload)
    return SuccessResponse(data=result)


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_scan(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = DeleteScanUseCase(scan_repo, audit_repo)
    await use_case.execute(scan_id, current_user.user_id)


@router.post("/{scan_id}/restore", response_model=SuccessResponse[dict], status_code=status.HTTP_200_OK)
async def restore_scan(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[dict]:
    use_case = RestoreScanUseCase(scan_repo, audit_repo)
    await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data={"scan_id": str(scan_id), "restored": True})


@router.post("/{scan_id}/cancel", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def cancel_scan(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = CancelScanUseCase(scan_repo, audit_repo)
    await use_case.execute(scan_id, current_user.user_id)


# ---- Admin maintenance endpoints (expiration cleanup, orphan detection) ----


@router.post(
    "/admin/cleanup-expired",
    response_model=SuccessResponse[dict],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def cleanup_expired_scans(
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    storage_service: Annotated[ScanStorageService, Depends(get_scan_storage_service)],
) -> SuccessResponse[dict]:
    use_case = CleanupExpiredScansUseCase(scan_repo, storage_service)
    count = await use_case.execute()
    return SuccessResponse(data={"cleaned_up": count})


@router.get(
    "/admin/orphans",
    response_model=SuccessResponse[dict],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def detect_orphan_files(
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    storage_backend: Annotated[StorageBackend, Depends(get_storage_backend)],
) -> SuccessResponse[dict]:
    use_case = DetectOrphanFilesUseCase(scan_repo, storage_backend)
    orphans = await use_case.execute()
    return SuccessResponse(data={"orphan_count": len(orphans), "orphans": orphans})
