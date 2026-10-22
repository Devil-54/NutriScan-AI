from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.v1.deps import (
    CurrentUserDep,
    get_ocr_result_repository,
    get_ocr_service,
    get_scan_repository,
    get_storage_backend,
)
from app.domain.schemas.common import SuccessResponse
from app.domain.schemas.ocr import OcrProcessResponse, OcrResultResponse, OcrStatusResponse
from app.infrastructure.db.repositories.ocr_result_repository import OcrResultRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.ocr.ocr_service import OcrService
from app.infrastructure.storage.storage_backend import StorageBackend
from app.use_cases.ocr.get_ocr_result import GetOcrResultUseCase
from app.use_cases.ocr.get_ocr_status import GetOcrStatusUseCase
from app.use_cases.ocr.process_scan_ocr import ProcessScanOcrUseCase

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/process", response_model=SuccessResponse[OcrProcessResponse])
async def process_ocr(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    ocr_result_repo: Annotated[OcrResultRepository, Depends(get_ocr_result_repository)],
    storage_backend: Annotated[StorageBackend, Depends(get_storage_backend)],
    ocr_service: Annotated[OcrService, Depends(get_ocr_service)],
) -> SuccessResponse[OcrProcessResponse]:
    use_case = ProcessScanOcrUseCase(scan_repo, ocr_result_repo, storage_backend, ocr_service)
    result = await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data=result)


@router.get("/status/{scan_id}", response_model=SuccessResponse[OcrStatusResponse])
async def get_ocr_status(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    ocr_result_repo: Annotated[OcrResultRepository, Depends(get_ocr_result_repository)],
) -> SuccessResponse[OcrStatusResponse]:
    use_case = GetOcrStatusUseCase(scan_repo, ocr_result_repo)
    result = await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data=result)


@router.get("/result/{scan_id}", response_model=SuccessResponse[OcrResultResponse])
async def get_ocr_result(
    scan_id: UUID,
    current_user: CurrentUserDep,
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
    ocr_result_repo: Annotated[OcrResultRepository, Depends(get_ocr_result_repository)],
) -> SuccessResponse[OcrResultResponse]:
    use_case = GetOcrResultUseCase(scan_repo, ocr_result_repo)
    result = await use_case.execute(scan_id, current_user.user_id)
    return SuccessResponse(data=result)
