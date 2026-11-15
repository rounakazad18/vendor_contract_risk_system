"""
Counterparty Negotiation-History Memory (`negotiation_memory.py`).
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import datetime
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class NegotiationMemoryEntry:
    counterparty_name: str
    category: str
    playbook_section_ref: str
    approved_redline_wording: str
    agreed_fallback_note: str
    prior_contract_id: str
    recorded_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NegotiationHistoryMemory:
    def __init__(self) -> None:
        self._by_section: Dict[Tuple[str, str], NegotiationMemoryEntry] = {}
        self._by_category: Dict[Tuple[str, str], NegotiationMemoryEntry] = {}
        self._history_log: List[NegotiationMemoryEntry] = []

    @staticmethod
    def _norm(val: str) -> str:
        return " ".join(val.lower().strip().split())

    def record_agreed_redline(
        self,
        counterparty_name: str,
        category: str,
        playbook_section_ref: str,
        approved_redline_wording: str,
        agreed_fallback_note: str = "Prior counterparty precedent applied.",
        prior_contract_id: str = "PRIOR-MSA-2025",
    ) -> NegotiationMemoryEntry:
        entry = NegotiationMemoryEntry(
            counterparty_name=counterparty_name.strip(),
            category=category.strip(),
            playbook_section_ref=playbook_section_ref.strip(),
            approved_redline_wording=approved_redline_wording.strip(),
            agreed_fallback_note=agreed_fallback_note.strip(),
            prior_contract_id=prior_contract_id.strip(),
            recorded_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )
        cp_key = self._norm(counterparty_name)
        sec_key = self._norm(playbook_section_ref)
        cat_key = self._norm(category)

        self._by_section[(cp_key, sec_key)] = entry
        self._by_category[(cp_key, cat_key)] = entry
        self._history_log.append(entry)
        return entry

    def lookup_precedent(
        self,
        counterparty_name: str,
        playbook_section_ref: str = "",
        category: str = "",
    ) -> Optional[NegotiationMemoryEntry]:
        cp_key = self._norm(counterparty_name)
        if playbook_section_ref:
            sec_key = self._norm(playbook_section_ref)
            if (cp_key, sec_key) in self._by_section:
                return self._by_section[(cp_key, sec_key)]
        if category:
            cat_key = self._norm(category)
            if (cp_key, cat_key) in self._by_category:
                return self._by_category[(cp_key, cat_key)]
        return None

    def get_all_entries(self) -> List[NegotiationMemoryEntry]:
        return list(self._history_log)


def populate_default_negotiation_memory() -> NegotiationHistoryMemory:
    mem = NegotiationHistoryMemory()
    mem.record_agreed_redline(
        counterparty_name="ApexCloud Infrastructure Inc.",
        category="Liability",
        playbook_section_ref="POL-LEGAL-2026-v4.2 §4.1",
        approved_redline_wording=(
            "NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, "
            "AND EACH PARTY'S AGGREGATE LIABILITY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE "
            "IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM; PROVIDED THAT SUCH LIMITATIONS SHALL "
            "NOT APPLY TO (A) INDEMNIFICATION OBLIGATIONS, (B) BREACHES OF CONFIDENTIALITY OR DATA "
            "SECURITY OBLIGATIONS (WHICH SHALL BE SUBJECT TO A SUPER-CAP EQUAL TO THREE TIMES (3X) "
            "ANNUAL FEES OR $3,000,000, WHICHEVER IS GREATER), OR (C) GROSS NEGLIGENCE OR WILLFUL MISCONDUCT."
        ),
        agreed_fallback_note="Repeat Counterparty Precedent (ApexCloud 2025 Master Addendum): Mutual 12-month cap + 3x/$3M Data/Confidentiality Super-Cap.",
        prior_contract_id="APEX-MSA-2025-014",
    )
    mem.record_agreed_redline(
        counterparty_name="ApexCloud Infrastructure Inc.",
        category="Data Privacy & AI",
        playbook_section_ref="POL-SEC-2026-v3.1 §2.3",
        approved_redline_wording=(
            "Vendor shall notify Customer in writing within twenty-four (24) hours of discovering any "
            "actual or reasonably suspected Security Incident affecting Customer Data and shall promptly "
            "cooperate at Vendor's expense in investigation, mitigation, and regulatory reporting. "
            "Customer retains all right, title, and interest in Customer Data; Vendor is strictly "
            "prohibited from using Customer Data, inputs, or outputs to train, fine-tune, or validate "
            "any artificial intelligence, machine learning, or foundation model."
        ),
        agreed_fallback_note="Repeat Counterparty Precedent (ApexCloud 2025 DPA): 24-hour breach notification & absolute ban on AI model training.",
        prior_contract_id="APEX-DPA-2025-019",
    )
    return mem
