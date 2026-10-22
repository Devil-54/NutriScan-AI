from __future__ import annotations

from app.core.logging import get_logger
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.storage.scan_storage_service import ScanStorageService
from app.infrastructure.storage.storage_backend import StorageBackend

logger = get_logger()


class CleanupExpiredScansUseCase:
    """
    Permanently deletes files (and soft-deletes the DB row if not already)
    for scans past their `expires_at`. Intended to be invoked by a
    scheduled job/admin trigger, not by end users directly.
    """

    def __init__(self, scan_repo: ScanRepository, storage_service: ScanStorageService) -> None:
        self.scan_repo = scan_repo
        self.storage_service = storage_service

    async def execute(self) -> int:
        expired = await self.scan_repo.find_expired()
        for scan in expired:
            await self.storage_service.delete_scan_files(scan.storage_path, scan.thumbnail_path)
            if not scan.is_deleted:
                await self.scan_repo.soft_delete(scan)
            logger.bind(event="SCAN_EXPIRED_CLEANED", scan_id=str(scan.scan_id)).info(
                "Expired scan files removed"
            )
        await self.scan_repo.commit()
        return len(expired)


class DetectOrphanFilesUseCase:
    """
    Compares every file physically present in storage against every path
    referenced by a (non-purged) DB row, and reports files with no
    referencing row - e.g. left behind by a crash between file-write and
    DB-commit. Read-only: reports findings, does not delete anything
    automatically, since orphan detection false-positives are expensive to
    get wrong.
    """

    def __init__(self, scan_repo: ScanRepository, storage_backend: StorageBackend) -> None:
        self.scan_repo = scan_repo
        self.storage_backend = storage_backend

    async def execute(self) -> list[str]:
        referenced_paths = await self.scan_repo.all_storage_paths()
        all_paths = set(self.storage_backend.list_all_relative_paths())
        orphans = sorted(all_paths - referenced_paths)
        if orphans:
            logger.bind(event="ORPHAN_FILES_DETECTED", count=len(orphans)).warning(
                f"Detected {len(orphans)} orphan file(s) in storage"
            )
        return orphans
