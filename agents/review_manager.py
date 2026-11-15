"""
Agent 5: Review Manager Agent
Responsibilities:
- Act as the central orchestrator in the Manager-Worker Multi-Agent Architecture.
- Register and coordinate specialist agents via the Semantic Kernel / Agent Framework registry.
- Delegate tasks to all specialist agents (Clause Splitter, Playbook Retrieval, Risk Scorer, Redline Drafter).
- Manage execution order, dependencies, and controlled parallel batch processing.
- Coordinate shared memory (SharedClauseTable) and Repeat Counterparty NegotiationHistoryMemory.
- Validate agent outputs and handle failures gracefully.
- Compile the final risk-ranked ContractReviewReport.
"""

from __future__ import annotations
import asyncio
import datetime
import logging
import time
import uuid
from typing import List, Optional, Callable
from schemas import (
    ClauseRecord,
    ContractReviewReport,
    ExecutiveSummary,
    FinalRecommendations,
    AgentExecutionTrace,
    RiskSeverity,
    ProcessingStatus,
    ApprovalRecommendation,
)
from shared_memory import SharedClauseTable
from vector_store import PlaybookVectorStore
from negotiation_memory import NegotiationHistoryMemory, populate_default_negotiation_memory
from framework_adapter import AgentKernelRegistry
from .clause_splitter import ClauseSplitterAgent
from .playbook_retrieval import PlaybookRetrievalAgent
from .risk_scorer import RiskScorerAgent
from .redline_drafter import RedlineDrafterAgent

logger = logging.getLogger(__name__)


class ReviewManagerAgent:
    """
    Agent 5: Central Orchestrator implementing the Manager-Worker Delegation Architecture.
    Coordinates specialist worker agents, registers `@kernel_function` plugins in
    `AgentKernelRegistry`, consults `NegotiationHistoryMemory`, enforces policy traceability,
    and compiles the final `ContractReviewReport`.
    """

    AGENT_NAME = "ReviewManagerAgent"

    def __init__(
        self,
        vector_store: PlaybookVectorStore,
        shared_table: Optional[SharedClauseTable] = None,
        negotiation_memory: Optional[NegotiationHistoryMemory] = None,
        counterparty_name: str = "ApexCloud Infrastructure Inc.",
        max_concurrency: int = 6,
    ) -> None:
        self.vector_store = vector_store
        self.shared_table = shared_table or SharedClauseTable()
        self.negotiation_memory = (
            negotiation_memory
            if negotiation_memory is not None
            else populate_default_negotiation_memory()
        )
        self.counterparty_name = counterparty_name
        self.max_concurrency = max_concurrency

        # Initialize the 4 specialist worker agents
        self.splitter_agent = ClauseSplitterAgent()
        self.retrieval_agent = PlaybookRetrievalAgent(vector_store=self.vector_store)
        self.scorer_agent = RiskScorerAgent()
        self.redline_agent = RedlineDrafterAgent(
            negotiation_memory=self.negotiation_memory,
            counterparty_name=self.counterparty_name,
        )

        # Register specialist plugins in Semantic Kernel / Agent Framework registry
        self.kernel_registry = AgentKernelRegistry()
        self.kernel_registry.register_plugin(self.splitter_agent, "ClauseSplitterPlugin")
        self.kernel_registry.register_plugin(self.retrieval_agent, "PlaybookRetrievalPlugin")
        self.kernel_registry.register_plugin(self.scorer_agent, "RiskScorerPlugin")
        self.kernel_registry.register_plugin(self.redline_agent, "RedlineDrafterPlugin")

        self.traces: List[AgentExecutionTrace] = []

    def _record_trace(
        self,
        agent_name: str,
        stage: str,
        start_iso: str,
        t0: float,
        clauses_count: int,
        status: str,
        details: str,
    ) -> None:
        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        end_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.traces.append(
            AgentExecutionTrace(
                agent_name=agent_name,
                stage=stage,
                started_at=start_iso,
                completed_at=end_iso,
                duration_ms=duration_ms,
                clauses_processed=clauses_count,
                status=status,
                details=details,
            )
        )

    async def analyze_contract_file(
        self,
        file_path: str,
        contract_prefix: str = "CL",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> ContractReviewReport:
        self.traces.clear()
        t0 = time.perf_counter()
        start_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Extracting text from contract document", 10)

        raw_text = self.splitter_agent.extract_text_from_file(file_path)
        self._record_trace(
            agent_name=self.splitter_agent.AGENT_NAME,
            stage="1. Text Extraction",
            start_iso=start_iso,
            t0=t0,
            clauses_count=0,
            status="COMPLETED",
            details=f"Extracted {len(raw_text):,} characters from '{file_path.split('/')[-1]}'.",
        )
        return await self.analyze_contract_text(
            raw_text=raw_text,
            contract_filename=file_path.split("/")[-1],
            contract_prefix=contract_prefix,
            progress_callback=progress_callback,
            reset_traces=False,
        )

    async def analyze_contract_text(
        self,
        raw_text: str,
        contract_filename: str = "Uploaded_Vendor_Contract.txt",
        contract_prefix: str = "CL",
        progress_callback: Optional[Callable[[str, int], None]] = None,
        reset_traces: bool = True,
    ) -> ContractReviewReport:
        self.shared_table.clear()
        if reset_traces:
            self.traces.clear()

        if not self.vector_store.chunks:
            raise RuntimeError(
                "PlaybookVectorStore has no indexed playbook chunks. Index at least one playbook before running analysis."
            )

        # Step 1: Delegate to Clause Splitter Agent
        t_split = time.perf_counter()
        iso_split = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Clause Splitter Agent segmenting clauses", 25)

        clauses = self.splitter_agent.split_text_into_clauses(
            raw_text=raw_text,
            shared_table=self.shared_table,
            contract_prefix=contract_prefix,
        )
        if not clauses:
            raise ValueError("ClauseSplitterAgent extracted 0 valid clauses from contract.")

        self._record_trace(
            agent_name=self.splitter_agent.AGENT_NAME,
            stage="2. Clause Splitting & Deduplication",
            start_iso=iso_split,
            t0=t_split,
            clauses_count=len(clauses),
            status="COMPLETED",
            details=f"Segmented and registered {len(clauses)} unique clauses in SharedClauseTable.",
        )

        semaphore = asyncio.Semaphore(self.max_concurrency)

        # Step 2: Delegate to Playbook Retrieval Agent (controlled parallel RAG lookup)
        t_rag = time.perf_counter()
        iso_rag = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Playbook Retrieval Agent running RAG similarity search", 45)

        async def _retrieve_worker(cl: ClauseRecord) -> None:
            async with semaphore:
                await self.retrieval_agent.retrieve_for_clause(cl, self.shared_table)

        await asyncio.gather(*[_retrieve_worker(c) for c in clauses])
        self._record_trace(
            agent_name=self.retrieval_agent.AGENT_NAME,
            stage="3. RAG Playbook Retrieval",
            start_iso=iso_rag,
            t0=t_rag,
            clauses_count=len(clauses),
            status="COMPLETED",
            details=(
                f"Retrieved governing playbook policies across {len(self.vector_store.indexed_documents)} "
                f"playbook documents for {len(clauses)} clauses."
            ),
        )

        # Step 3: Delegate to Risk Scorer Agent (controlled parallel scoring via @kernel_function tool)
        t_score = time.perf_counter()
        iso_score = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Risk Scorer Agent evaluating policy violations & severity", 65)

        async def _score_worker(cl: ClauseRecord) -> None:
            async with semaphore:
                await self.scorer_agent.evaluate_clause(cl, self.shared_table)

        await asyncio.gather(*[_score_worker(c) for c in clauses])
        self._record_trace(
            agent_name=self.scorer_agent.AGENT_NAME,
            stage="4. Clause Risk Scoring (@kernel_function)",
            start_iso=iso_score,
            t0=t_score,
            clauses_count=len(clauses),
            status="COMPLETED",
            details=f"Scored {len(clauses)} clauses (0–100 scale) and classified risk severities.",
        )

        # Step 4: Delegate to Redline Drafter Agent (with Repeat Counterparty NegotiationHistoryMemory)
        t_red = time.perf_counter()
        iso_red = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Redline Drafter Agent generating playbook-aligned replacement wording", 85)

        async def _redline_worker(cl: ClauseRecord) -> None:
            async with semaphore:
                await self.redline_agent.draft_redline_for_clause(cl, self.shared_table)

        await asyncio.gather(*[_redline_worker(c) for c in clauses])
        flagged_count = sum(1 for c in self.shared_table.get_all_clauses() if c.is_flagged)
        self._record_trace(
            agent_name=self.redline_agent.AGENT_NAME,
            stage="5. Redline Wording & Memory Lookup",
            start_iso=iso_red,
            t0=t_red,
            clauses_count=flagged_count,
            status="COMPLETED",
            details=f"Generated playbook-grounded replacement wording and diffs for {flagged_count} flagged clauses (Counterparty: {self.counterparty_name}).",
        )

        # Step 5: Review Manager validation & report consolidation
        t_val = time.perf_counter()
        iso_val = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if progress_callback:
            progress_callback("Review Manager validating traceability and compiling report", 95)

        all_records = self.shared_table.get_all_clauses()
        for rec in all_records:
            self._validate_clause_record(rec)
            self.shared_table.mark_validated(rec.clause_id)

        self._record_trace(
            agent_name=self.AGENT_NAME,
            stage="6. Validation & Report Consolidation",
            start_iso=iso_val,
            t0=t_val,
            clauses_count=len(all_records),
            status="COMPLETED",
            details="Validated 100% policy traceability and consolidated final ContractReviewReport.",
        )

        report = self._compile_report(contract_filename, all_records)

        if progress_callback:
            progress_callback("Contract Risk Review Complete", 100)

        return report

    def _validate_clause_record(self, rec: ClauseRecord) -> None:
        if rec.processing_status not in (
            ProcessingStatus.REDLINE_DRAFTED,
            ProcessingStatus.VALIDATED,
        ):
            self.shared_table.mark_failed(
                rec.clause_id, f"Incomplete processing status: {rec.processing_status}"
            )
            raise ValueError(
                f"Validation failed for Clause {rec.clause_id}: unexpected status {rec.processing_status}"
            )

        if not (0 <= rec.risk_score <= 100):
            self.shared_table.mark_failed(rec.clause_id, "Out-of-range risk_score")
            raise ValueError(f"Validation failed for Clause {rec.clause_id}: invalid risk_score")

        if rec.is_flagged:
            if rec.missing_playbook_reference or not rec.retrieved_playbook_references:
                self.shared_table.mark_failed(
                    rec.clause_id, "Flagged risk lacks a traceable playbook reference."
                )
                raise ValueError(
                    f"Constraint violation on Clause {rec.clause_id}: every flagged risk must have a traceable playbook reference."
                )
            if not rec.suggested_replacement_wording.strip() or not rec.redline_rationale.strip():
                self.shared_table.mark_failed(
                    rec.clause_id, "Flagged clause is missing replacement wording or rationale."
                )
                raise ValueError(
                    f"Constraint violation on Clause {rec.clause_id}: missing redline wording or rationale."
                )

    def _compile_report(
        self, contract_filename: str, records: List[ClauseRecord]
    ) -> ContractReviewReport:
        ranked_clauses = sorted(
            records, key=lambda r: (-r.risk_score, r.clause_id)
        )
        flagged_clauses = [r for r in ranked_clauses if r.is_flagged]

        crit_count = sum(1 for r in records if r.risk_severity == RiskSeverity.CRITICAL)
        high_count = sum(1 for r in records if r.risk_severity == RiskSeverity.HIGH)
        med_count = sum(1 for r in records if r.risk_severity == RiskSeverity.MEDIUM)
        low_count = sum(1 for r in records if r.risk_severity == RiskSeverity.LOW)
        no_risk_count = sum(1 for r in records if r.risk_severity == RiskSeverity.NO_RISK)

        avg_score = round(
            sum(r.risk_score for r in records) / max(1, len(records)), 1
        )
        top3_mean = (
            sum(r.risk_score for r in ranked_clauses[:3]) / min(3, len(ranked_clauses))
            if ranked_clauses
            else 0
        )
        overall_score = int(round(0.45 * avg_score + 0.55 * top3_mean))

        if crit_count >= 1 or overall_score >= 70:
            overall_level = "High / Critical Exposure"
        elif high_count >= 1 or overall_score >= 45:
            overall_level = "Moderate-High Exposure"
        elif med_count >= 1 or overall_score >= 25:
            overall_level = "Moderate Exposure"
        else:
            overall_level = "Low Risk / Playbook Compliant"

        if crit_count >= 4 or overall_score >= 88:
            approval_rec = ApprovalRecommendation.REJECT
            approval_just = (
                "Contract exhibits pervasive, fundamental conflicts with company legal and security "
                "playbooks across core liability, IP, and regulatory pillars. Reject vendor paper and "
                "re-issue on Company Standard Master Services Agreement."
            )
        elif crit_count > 0 or high_count > 0 or med_count > 0:
            approval_rec = ApprovalRecommendation.APPROVE_WITH_CHANGES
            approval_just = (
                f"Contract contains {crit_count} Critical and {high_count} High-risk clauses that violate "
                "mandatory internal playbook rules. Execution is contingent upon Vendor accepting the "
                "proposed redlines on Critical and High severity provisions."
            )
        else:
            approval_rec = ApprovalRecommendation.APPROVE
            approval_just = (
                "All material clauses align with internal company playbook tolerances. Approved for execution."
            )

        exec_summary = ExecutiveSummary(
            contract_name=contract_filename,
            total_clauses_analyzed=len(records),
            flagged_clauses_count=len(flagged_clauses),
            critical_count=crit_count,
            high_count=high_count,
            medium_count=med_count,
            low_count=low_count,
            no_risk_count=no_risk_count,
            average_risk_score=avg_score,
            overall_contract_risk_score=overall_score,
            overall_risk_level=overall_level,
            overall_assessment_narrative=(
                f"Multi-agent analysis of '{contract_filename}' evaluated {len(records)} clauses against "
                f"{len(self.vector_store.indexed_documents)} internal company playbooks. "
                f"A total of {len(flagged_clauses)} clauses were flagged ({crit_count} Critical, "
                f"{high_count} High, {med_count} Medium, {low_count} Low), yielding a composite contract "
                f"risk score of {overall_score}/100 ({overall_level}). Recommendation: {approval_rec.value}."
            ),
        )

        top_risks = [
            f"Clause {r.clause_number} ({r.clause_heading}) — Score {r.risk_score}/100 [{r.risk_severity.value}]: {r.risk_explanation}"
            for r in flagged_clauses[:4]
        ]
        legal_review_clauses = [
            f"Clause {r.clause_number}: {r.clause_heading} ({r.risk_severity.value}, {r.risk_score}/100 — Ref: {r.retrieved_playbook_references[0].section_ref})"
            for r in flagged_clauses
            if r.risk_severity in (RiskSeverity.CRITICAL, RiskSeverity.HIGH, RiskSeverity.MEDIUM)
        ]
        negotiation_priorities = [
            f"Priority {idx + 1} [Clause {r.clause_number} — {r.clause_heading}]: Replace vendor language per {r.retrieved_playbook_references[0].section_ref}. Fallback: {r.retrieved_playbook_references[0].fallback_position or 'Escalate to General Counsel.'}"
            for idx, r in enumerate(flagged_clauses[:5])
        ]

        final_recs = FinalRecommendations(
            top_risks_requiring_attention=top_risks,
            clauses_requiring_legal_review=legal_review_clauses,
            recommended_negotiation_priorities=negotiation_priorities,
            approval_recommendation=approval_rec,
            approval_justification=approval_just,
        )

        return ContractReviewReport(
            report_id=f"RPT-{uuid.uuid4().hex[:8].upper()}",
            generated_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            contract_filename=contract_filename,
            playbooks_indexed=[
                f"{doc_id}: {title}" for doc_id, title in self.vector_store.indexed_documents.items()
            ],
            executive_summary=exec_summary,
            risk_ranked_clauses=ranked_clauses,
            suggested_redlines=flagged_clauses,
            final_recommendations=final_recs,
            agent_traces=list(self.traces),
        )
