"""
Centralized thread-safe and async-safe Shared Clause Table for multi-agent coordination.
"""

from __future__ import annotations
import asyncio
import datetime
import hashlib
import logging
import threading
from typing import Dict, List, Optional
from schemas import (
    ClauseRecord,
    PlaybookReference,
    RiskSeverity,
    ProcessingStatus,
    DiffOperation,
)

logger = logging.getLogger(__name__)


class SharedClauseTable:
    def __init__(self) -> None:
        self._records: Dict[str, ClauseRecord] = {}
        self._content_hashes: Dict[str, str] = {}
        self._lock = threading.RLock()
        self._async_lock: Optional[asyncio.Lock] = None

    def _get_async_lock(self) -> asyncio.Lock:
        with self._lock:
            if self._async_lock is None:
                self._async_lock = asyncio.Lock()
            return self._async_lock

    @staticmethod
    def _compute_hash(text: str) -> str:
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def register_clause(self, record: ClauseRecord) -> bool:
        if not record.clause_id or not record.original_text or not record.original_text.strip():
            raise ValueError("Invalid ClauseRecord: clause_id and non-empty original_text are required.")

        text_hash = self._compute_hash(record.original_text)
        with self._lock:
            if record.clause_id in self._records:
                logger.warning("Duplicate clause_id '%s' skipped.", record.clause_id)
                return False
            if text_hash in self._content_hashes:
                logger.warning(
                    "Duplicate clause text detected (matches '%s'); skipping '%s'.",
                    self._content_hashes[text_hash],
                    record.clause_id,
                )
                return False

            record.processing_status = ProcessingStatus.EXTRACTED
            record.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            self._records[record.clause_id] = record
            self._content_hashes[text_hash] = record.clause_id
            return True

    def get_clause(self, clause_id: str) -> Optional[ClauseRecord]:
        with self._lock:
            return self._records.get(clause_id)

    def get_all_clauses(self) -> List[ClauseRecord]:
        with self._lock:
            return list(self._records.values())

    def get_clauses_by_status(self, status: ProcessingStatus) -> List[ClauseRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.processing_status == status]

    async def update_playbook_retrieval(
        self,
        clause_id: str,
        references: List[PlaybookReference],
        policy_rules: List[str],
        missing_reference: bool = False,
    ) -> ClauseRecord:
        async with self._get_async_lock():
            with self._lock:
                if clause_id not in self._records:
                    raise KeyError(f"Clause ID '{clause_id}' not found in SharedClauseTable.")
                rec = self._records[clause_id]
                rec.retrieved_playbook_references = references
                rec.applicable_policy_rules = policy_rules
                rec.missing_playbook_reference = missing_reference
                rec.processing_status = ProcessingStatus.PLAYBOOK_RETRIEVED
                rec.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return rec

    async def update_risk_assessment(
        self,
        clause_id: str,
        risk_score: int,
        risk_severity: RiskSeverity,
        risk_explanation: str,
        missing_protections: List[str],
        policy_violations: List[str],
        ambiguous_language: List[str],
        unfavorable_obligations: List[str],
    ) -> ClauseRecord:
        if not isinstance(risk_score, int) or not (0 <= risk_score <= 100):
            raise ValueError(f"Invalid risk_score {risk_score}: must be an integer between 0 and 100.")
        if not isinstance(risk_severity, RiskSeverity):
            raise ValueError(f"Invalid risk_severity {risk_severity}: must be a RiskSeverity enum.")
        if not risk_explanation or not risk_explanation.strip():
            raise ValueError("Risk explanation cannot be empty.")

        async with self._get_async_lock():
            with self._lock:
                if clause_id not in self._records:
                    raise KeyError(f"Clause ID '{clause_id}' not found in SharedClauseTable.")
                rec = self._records[clause_id]
                rec.risk_score = risk_score
                rec.risk_severity = risk_severity
                rec.risk_explanation = risk_explanation.strip()
                rec.missing_protections = missing_protections
                rec.policy_violations = policy_violations
                rec.ambiguous_language = ambiguous_language
                rec.unfavorable_obligations = unfavorable_obligations
                rec.processing_status = ProcessingStatus.RISK_SCORED
                rec.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return rec

    async def update_redline(
        self,
        clause_id: str,
        suggested_wording: str,
        rationale: str,
        diff_operations: List[DiffOperation],
    ) -> ClauseRecord:
        if not suggested_wording or not suggested_wording.strip():
            raise ValueError("Suggested replacement wording cannot be empty.")
        if not rationale or not rationale.strip():
            raise ValueError("Redline rationale cannot be empty.")

        async with self._get_async_lock():
            with self._lock:
                if clause_id not in self._records:
                    raise KeyError(f"Clause ID '{clause_id}' not found in SharedClauseTable.")
                rec = self._records[clause_id]
                rec.suggested_replacement_wording = suggested_wording.strip()
                rec.redline_rationale = rationale.strip()
                rec.diff_operations = diff_operations
                rec.processing_status = ProcessingStatus.REDLINE_DRAFTED
                rec.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return rec

    def mark_validated(self, clause_id: str) -> ClauseRecord:
        with self._lock:
            if clause_id not in self._records:
                raise KeyError(f"Clause ID '{clause_id}' not found in SharedClauseTable.")
            rec = self._records[clause_id]
            rec.processing_status = ProcessingStatus.VALIDATED
            rec.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return rec

    def mark_failed(self, clause_id: str, error_message: str) -> ClauseRecord:
        with self._lock:
            if clause_id not in self._records:
                raise KeyError(f"Clause ID '{clause_id}' not found in SharedClauseTable.")
            rec = self._records[clause_id]
            rec.processing_status = ProcessingStatus.FAILED
            rec.error_message = error_message
            rec.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return rec

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._content_hashes.clear()
