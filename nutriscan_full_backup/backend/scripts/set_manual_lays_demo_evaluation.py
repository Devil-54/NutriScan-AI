"""Persist the approved fixed Lay's college-demo evaluation.

This is deliberately a development-only, one-record update. It never creates
a scan or evaluation, never alters OCR/nutrition/timestamps, and refuses to
run if the supplied authenticated user does not own exactly one active Lay's
scan. History and Scan Details then consume the same saved evaluation.

Usage: poetry run python -m scripts.set_manual_lays_demo_evaluation --user-id <UUID>
"""
from __future__ import annotations

import argparse
import asyncio
import uuid

from sqlalchemy import select

from app.domain.enums import RiskLevel, VerdictStatus
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.models.scan_session import ScanSession
from app.infrastructure.db.session import AsyncSessionLocal


LAYS_FILENAME = "Lay's Potato Chips.png"
MANUAL_CONCERNS = [
    ("vegetable oil", "Fat-related consideration."),
    ("salt", "Sodium-related consideration."),
    ("total fat", "10 g per serving on the scanned label."),
    ("saturated fat", "1.5 g per serving on the scanned label."),
    ("dietary fiber", "1 g per serving on the scanned label."),
    ("processed/fried snack profile", "Dietary consideration based on the scanned oil-and-salt snack profile."),
]
MANUAL_RESULT = "Processed snack with relatively high total fat and limited dietary fiber per serving. Moderate health concern for this demo evaluation."
MANUAL_RECOMMENDATIONS = [
    "Consume in moderation.",
    "Prefer balanced meals with vegetables, whole grains and adequate protein.",
    "Limit frequent consumption of highly processed snack foods.",
]


async def set_manual_lays_demo_evaluation(user_id: uuid.UUID) -> uuid.UUID:
    async with AsyncSessionLocal() as session:
        scans = list((await session.execute(
            select(ScanSession).where(
                ScanSession.user_id == user_id,
                ScanSession.original_filename == LAYS_FILENAME,
                ScanSession.deleted_at.is_(None),
            )
        )).scalars())
        if len(scans) != 1:
            raise ValueError(
                f"Expected exactly one active {LAYS_FILENAME!r} scan for this user; found {len(scans)}. "
                "No record was changed."
            )

        scan = scans[0]
        evaluation = await session.scalar(
            select(MedicalEvaluation).where(
                MedicalEvaluation.scan_id == scan.scan_id,
                MedicalEvaluation.user_id == user_id,
            )
        )
        if evaluation is None:
            raise ValueError("Lay's scan has no saved evaluation. No record was changed.")

        # Only persisted evaluation fields change. Scan identity, label OCR,
        # nutrition snapshot, and the original scan timestamp are untouched.
        evaluation.health_score = 70
        evaluation.risk_level = RiskLevel.MODERATE.value
        evaluation.severity = RiskLevel.MODERATE.value
        evaluation.status = VerdictStatus.WARNING.value
        evaluation.unsafe_ingredients = [factor for factor, _ in MANUAL_CONCERNS]
        evaluation.triggered_rules = ["manual_lays_demo_evaluation"]
        evaluation.reasons = [MANUAL_RESULT]
        evaluation.recommendations = MANUAL_RECOMMENDATIONS
        evaluation.ingredient_warnings = [
            {"ingredient": factor, "reason": reason} for factor, reason in MANUAL_CONCERNS
        ]
        await session.commit()
        return scan.scan_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Set the fixed saved Lay's college-demo evaluation.")
    parser.add_argument("--user-id", required=True, type=uuid.UUID)
    args = parser.parse_args()
    scan_id = asyncio.run(set_manual_lays_demo_evaluation(args.user_id))
    print(f"Updated existing Lay's scan evaluation: scan_id={scan_id}, score=70, risk=moderate")


if __name__ == "__main__":
    main()
