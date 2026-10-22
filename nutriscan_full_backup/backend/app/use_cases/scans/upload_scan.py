from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import ConflictException, ValidationException
from app.core.logging import get_logger
from app.domain.enums import ScanStatus
from app.domain.schemas.scan import ScanUploadResponse
from app.infrastructure.db.models.scan_session import ScanSession
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.storage.image_validator import validate_and_probe_image
from app.infrastructure.storage.scan_storage_service import ScanStorageService
from app.infrastructure.storage.virus_scanner import VirusScanner

logger = get_logger()


class UploadScanUseCase:
    def __init__(
        self,
        scan_repo: ScanRepository,
        storage_service: ScanStorageService,
        virus_scanner: VirusScanner,
        audit_repo: AuditLogRepository,
    ) -> None:
        self.scan_repo = scan_repo
        self.storage_service = storage_service
        self.virus_scanner = virus_scanner
        self.audit_repo = audit_repo

    async def execute(
        self,
        user_id: uuid.UUID,
        file_bytes: bytes,
        claimed_filename: str,
        ip_address: str | None = None,
    ) -> ScanUploadResponse:
        logger.bind(event="UPLOAD_STARTED", user_id=str(user_id)).info("Scan upload started")

        # ---- Per-user daily upload cap (abuse/cost control, independent of the per-minute rate limiter) ----
        since = datetime.now(timezone.utc) - timedelta(days=1)
        recent_uploads = await self.scan_repo.count_uploads_since(user_id, since)
        if recent_uploads >= settings.MAX_UPLOADS_PER_USER_PER_DAY:
            raise ValidationException(
                "Daily upload limit reached - please try again tomorrow", error_code="UPLOAD_LIMIT_EXCEEDED"
            )

        # ---- Validation (extension, MIME sniffing, size, resolution, corruption) ----
        try:
            probe = validate_and_probe_image(file_bytes, claimed_filename)
        except Exception:
            logger.bind(event="UPLOAD_FAILED", user_id=str(user_id)).warning("Scan upload failed validation")
            raise

        # ---- Duplicate protection: same user, identical content, still active ----
        duplicate = await self.scan_repo.find_active_duplicate(user_id, probe.checksum_sha256)
        if duplicate is not None:
            raise ConflictException(
                f"This image has already been uploaded (scan_id={duplicate.scan_id})",
                error_code="DUPLICATE_UPLOAD",
            )

        # ---- Virus scan (placeholder interface per Phase 3B scope) ----
        verdict = await self.virus_scanner.scan(file_bytes)
        if not verdict.is_clean:
            logger.bind(event="SECURITY_EVENT", user_id=str(user_id)).error(
                f"Upload rejected by virus scanner: {verdict.detail}"
            )
            raise ValidationException("Uploaded file failed a security scan", error_code="UPLOAD_REJECTED_SECURITY")

        scan_id = uuid.uuid4()
        try:
            storage_path, thumbnail_path = await self.storage_service.save_scan_files(
                user_id=user_id, scan_id=scan_id, file_bytes=file_bytes, probe=probe
            )
        except Exception:
            logger.bind(event="UPLOAD_FAILED", user_id=str(user_id), scan_id=str(scan_id)).error(
                "Scan upload failed during storage write"
            )
            raise

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.SCAN_EXPIRATION_DAYS)

        scan = ScanSession(
            scan_id=scan_id,
            user_id=user_id,
            original_filename=claimed_filename[:255],
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            mime_type=probe.mime_type,
            file_size_bytes=probe.size_bytes,
            checksum_sha256=probe.checksum_sha256,
            width_px=probe.width_px,
            height_px=probe.height_px,
            status=ScanStatus.UPLOADED,
            expires_at=expires_at,
        )
        self.scan_repo.add(scan)
        await self.scan_repo.flush()

        await self.audit_repo.record(
            action="SCAN_UPLOADED",
            user_id=user_id,
            entity_type="scan",
            entity_id=str(scan_id),
            ip_address=ip_address,
            metadata={"size_bytes": probe.size_bytes},
        )
        await self.scan_repo.commit()

        logger.bind(event="UPLOAD_COMPLETED", user_id=str(user_id), scan_id=str(scan_id)).info(
            "Scan upload completed"
        )

        return ScanUploadResponse(
            scan_id=scan.scan_id,
            status=scan.status,
            original_filename=scan.original_filename,
            file_size_bytes=scan.file_size_bytes,
            width_px=scan.width_px,
            height_px=scan.height_px,
            checksum_sha256=scan.checksum_sha256,
        )
