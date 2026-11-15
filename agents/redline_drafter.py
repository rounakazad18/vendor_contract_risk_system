"""
Agent 4: Redline Drafter Agent
"""

from __future__ import annotations
import logging
from typing import List, Optional
from schemas import ClauseRecord, DiffOperation
from shared_memory import SharedClauseTable
from negotiation_memory import NegotiationHistoryMemory
from framework_adapter import kernel_function

logger = logging.getLogger(__name__)


class RedlineDrafterAgent:
    AGENT_NAME = "RedlineDrafterAgent"

    def __init__(
        self,
        negotiation_memory: Optional[NegotiationHistoryMemory] = None,
        counterparty_name: str = "ApexCloud Infrastructure Inc.",
    ) -> None:
        self.negotiation_memory = negotiation_memory
        self.counterparty_name = counterparty_name

    @kernel_function(
        name="draft_playbook_redline_tool",
        description="Drafts playbook-grounded replacement wording and consults repeat counterparty negotiation memory.",
    )
    async def draft_redline_for_clause(
        self, clause: ClauseRecord, shared_table: SharedClauseTable
    ) -> ClauseRecord:
        if not clause.is_flagged:
            return await shared_table.update_redline(
                clause_id=clause.clause_id,
                suggested_wording=clause.original_text,
                rationale="No redline required. Original clause wording complies with internal playbook standards.",
                diff_operations=[],
            )

        if clause.missing_playbook_reference or not clause.retrieved_playbook_references:
            raise ValueError(
                f"Cannot draft policy-grounded redline for Clause {clause.clause_id}: "
                "no traceable playbook reference retrieved."
            )

        primary_ref = clause.retrieved_playbook_references[0]

        precedent = None
        if self.negotiation_memory and self.counterparty_name:
            precedent = self.negotiation_memory.lookup_precedent(
                counterparty_name=self.counterparty_name,
                playbook_section_ref=primary_ref.section_ref,
                category=primary_ref.category,
            )

        if precedent is not None:
            suggested_wording = (
                f"{clause.clause_number}. {clause.clause_heading}. "
                f"{precedent.approved_redline_wording}"
            )
            memory_note = (
                f"[Repeat Counterparty Memory Match: {precedent.prior_contract_id} for "
                f"'{precedent.counterparty_name}' — {precedent.agreed_fallback_note}] "
            )
        else:
            preferred_template = primary_ref.preferred_wording_template.strip()
            if preferred_template:
                suggested_wording = (
                    f"{clause.clause_number}. {clause.clause_heading}. {preferred_template}"
                )
            else:
                suggested_wording = (
                    f"{clause.clause_number}. {clause.clause_heading}. "
                    f"The parties agree that {primary_ref.governing_policy_rule}"
                )
            memory_note = ""
            if self.negotiation_memory and self.counterparty_name:
                self.negotiation_memory.record_agreed_redline(
                    counterparty_name=self.counterparty_name,
                    category=primary_ref.category,
                    playbook_section_ref=primary_ref.section_ref,
                    approved_redline_wording=preferred_template or primary_ref.governing_policy_rule,
                    agreed_fallback_note=f"Auto-recorded from active review ({primary_ref.section_ref}).",
                    prior_contract_id="ACTIVE-SESSION",
                )

        diff_ops: List[DiffOperation] = self._build_diff_operations(clause, primary_ref.section_ref)

        rationale_parts = [
            f"{memory_note}Grounded in {primary_ref.section_ref} ({primary_ref.document_title} — {primary_ref.heading})."
        ]
        if clause.policy_violations:
            rationale_parts.append(f"Eliminates policy violation: {clause.policy_violations[0]}")
        if clause.missing_protections:
            rationale_parts.append(f"Inserts mandatory protection: {clause.missing_protections[0]}")
        if primary_ref.fallback_position:
            rationale_parts.append(f"Negotiation Fallback Position: {primary_ref.fallback_position}")

        rationale = " ".join(rationale_parts)

        return await shared_table.update_redline(
            clause_id=clause.clause_id,
            suggested_wording=suggested_wording,
            rationale=rationale,
            diff_operations=diff_ops,
        )

    def _build_diff_operations(
        self, clause: ClauseRecord, section_ref: str
    ) -> List[DiffOperation]:
        ops: List[DiffOperation] = []

        if clause.unfavorable_obligations:
            for unfav in clause.unfavorable_obligations:
                ops.append(
                    DiffOperation(
                        op_type="REMOVE",
                        original_fragment=unfav,
                        replacement_fragment="[Removed unfavorable vendor-skewed obligation]",
                        reason=f"Prohibited under {section_ref}.",
                    )
                )

        if clause.policy_violations:
            for viol in clause.policy_violations:
                ops.append(
                    DiffOperation(
                        op_type="MODIFY",
                        original_fragment=clause.original_text[:140] + "...",
                        replacement_fragment=clause.retrieved_playbook_references[0].preferred_wording_template[:140] + "...",
                        reason=f"Replaces non-compliant clause terms to satisfy {section_ref}: {viol}",
                    )
                )

        if clause.missing_protections:
            for mp in clause.missing_protections:
                ops.append(
                    DiffOperation(
                        op_type="ADD",
                        original_fragment="[Omitted in vendor draft]",
                        replacement_fragment=mp,
                        reason=f"Required affirmative protection mandated by {section_ref}.",
                    )
                )

        return ops
