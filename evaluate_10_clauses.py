"""
CA2 Evaluation Target Module (`evaluate_10_clauses.py`)
Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from agents import ReviewManagerAgent
from data.sample_data import populate_default_vector_store
from negotiation_memory import populate_default_negotiation_memory


TEN_LABELLED_CLAUSES_DATASET: List[Dict[str, str]] = [
    {
        "clause_number": "1",
        "heading": "Scope of Services and Affiliates",
        "human_label": "Low",
        "text": (
            "1. Scope of Services and Affiliates.\n"
            "1.1 Vendor shall provide the cloud hosting, analytics platform, and support services "
            "described in each mutually executed Order Form in accordance with a 99.95% monthly uptime Service Level Agreement.\n"
            "1.2 Customer's majority-owned Affiliates are expressly authorized to access and use the Services "
            "under the terms of this Agreement without additional platform access fees."
        ),
    },
    {
        "clause_number": "2",
        "heading": "Term, Auto-Renewal and Termination Rights",
        "human_label": "High",
        "text": (
            "2. Term, Auto-Renewal and Termination Rights.\n"
            "2.1 This Agreement shall commence on the Effective Date and continue for an Initial Term of twenty-four (24) months. "
            "Thereafter, this Agreement shall automatically renew for successive thirty-six (36) month periods unless Customer "
            "provides written notice of non-renewal at least 120 days prior to the expiration of the then-current term.\n"
            "2.2 All Order Forms are strictly non-cancellable, all fees are non-refundable, and Customer shall have no right "
            "to terminate for convenience under any circumstances."
        ),
    },
    {
        "clause_number": "3",
        "heading": "Fees, Invoicing, Payment Terms and Price Escalation",
        "human_label": "High",
        "text": (
            "3. Fees, Invoicing, Payment Terms and Price Escalation.\n"
            "3.1 All fees are due and payable Net 15 (within fifteen (15) days of invoice date) without right of set-off or deduction. "
            "Overdue balances shall accrue compound interest at the rate of 2.5% per month (30% per annum), and Vendor may "
            "immediately suspend Services if any invoice remains unpaid for five (5) days.\n"
            "3.2 Vendor reserves the right to increase fees at any time in its sole discretion upon fifteen (15) days' notice, "
            "and renewal terms shall be subject to uncapped annual price adjustments."
        ),
    },
    {
        "clause_number": "4",
        "heading": "Intellectual Property and Work Product Ownership",
        "human_label": "High",
        "text": (
            "4. Intellectual Property and Work Product Ownership.\n"
            "4.1 Notwithstanding anything to the contrary, all deliverables, custom configurations, software integrations, "
            "and work product funded by Customer under any Statement of Work shall belong exclusively to Vendor.\n"
            "4.2 Customer hereby assigns to Vendor all rights in deliverables and acknowledges that all derivative works "
            "shall remain the sole property of Vendor, subject only to a revocable, non-exclusive license during the active Term."
        ),
    },
    {
        "clause_number": "5",
        "heading": "Indemnification Obligations",
        "human_label": "High",
        "text": (
            "5. Indemnification Obligations.\n"
            "5.1 Customer shall indemnify, defend, and hold harmless Vendor, its officers, directors, and affiliates solely "
            "at Customer's expense against any and all third-party claims, liabilities, and expenses arising out of or relating "
            "to this Agreement or Customer's use of the Services.\n"
            "5.2 Vendor disclaims any obligation to indemnify Customer for third-party intellectual property infringement, "
            "data security incidents, or regulatory penalties."
        ),
    },
    {
        "clause_number": "6",
        "heading": "Limitation of Liability and Consequential Damages",
        "human_label": "High",
        "text": (
            "6. Limitation of Liability and Consequential Damages.\n"
            "6.1 IN NO EVENT SHALL VENDOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, PUNITIVE, OR CONSEQUENTIAL DAMAGES. "
            "Customer waives all claims for consequential damages while Customer's liability to Vendor remains uncapped.\n"
            "6.2 Vendor's maximum aggregate liability for all claims arising under or related to this Agreement (including data "
            "breaches and IP claims) shall in no event exceed the fees paid in the one (1) month immediately preceding the event "
            "giving rise to liability, and explicitly excludes data breach from cap carve-outs."
        ),
    },
    {
        "clause_number": "7",
        "heading": "Confidentiality and Non-Disclosure",
        "human_label": "Low",
        "text": (
            "7. Confidentiality and Non-Disclosure.\n"
            "7.1 Each Party agrees to hold the other Party's Confidential Information in strict confidence using at least "
            "the same degree of care it uses to protect its own confidential information of like importance, and in no event "
            "less than a reasonable standard of care.\n"
            "7.2 Upon termination or expiration of this Agreement, each Receiving Party shall promptly return or certify "
            "the destruction of all Disclosing Party Confidential Information within thirty (30) days."
        ),
    },
    {
        "clause_number": "8",
        "heading": "Data Privacy, Security Incident Notification and AI Training",
        "human_label": "High",
        "text": (
            "8. Data Privacy, Security Incident Notification and AI Training.\n"
            "8.1 In the event of a confirmed data breach involving Customer Personal Data, Vendor shall notify Customer "
            "within ten (10) business days after confirming the root cause of the incident in its sole discretion.\n"
            "8.2 Customer hereby grants Vendor a perpetual, irrevocable, worldwide, royalty-free license to use Customer Data, "
            "user prompts, and platform outputs to train its artificial intelligence and machine learning foundation models "
            "for commercial distribution to third parties."
        ),
    },
    {
        "clause_number": "9",
        "heading": "Audit Rights and Regulatory Compliance",
        "human_label": "Medium",
        "text": (
            "9. Audit Rights and Regulatory Compliance.\n"
            "9.1 Customer's sole and exclusive right to verify Vendor's security posture shall be limited to receiving "
            "a one-page internal self-attestation letter from Vendor once every twenty-four (24) months.\n"
            "9.2 Customer and its regulators are strictly prohibited from conducting any on-site or third-party security "
            "audit or requesting SOC 2 Type II reports."
        ),
    },
    {
        "clause_number": "10",
        "heading": "Governing Law, Venue and Dispute Resolution",
        "human_label": "Medium",
        "text": (
            "10. Governing Law, Venue and Dispute Resolution.\n"
            "10.1 This Agreement shall be governed by and construed in accordance with the laws of the Cayman Islands. "
            "Any dispute shall be resolved exclusively by binding arbitration in George Town, Grand Cayman before a single "
            "arbitrator appointed by Vendor.\n"
            "10.2 Customer shall bear all costs and attorneys' fees incurred by both parties in connection with any dispute "
            "or arbitration proceeding, regardless of outcome."
        ),
    },
]


@dataclass
class ClauseEvaluationRow:
    clause_number: str
    clause_heading: str
    group_human_label: str
    system_3tier_label: str
    system_5tier_severity: str
    risk_score: int
    playbook_ref: str
    agreed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TenClauseEvaluationSummary:
    total_clauses: int
    agreed_count: int
    agreement_percentage: float
    high_precision_recall: str
    medium_precision_recall: str
    low_precision_recall: str
    rows: List[ClauseEvaluationRow]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_clauses": self.total_clauses,
            "agreed_count": self.agreed_count,
            "agreement_percentage": self.agreement_percentage,
            "high_precision_recall": self.high_precision_recall,
            "medium_precision_recall": self.medium_precision_recall,
            "low_precision_recall": self.low_precision_recall,
            "rows": [r.to_dict() for r in self.rows],
        }


def map_score_to_3tier_label(risk_score: int) -> str:
    if risk_score >= 60:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"


async def run_10_clause_evaluation() -> TenClauseEvaluationSummary:
    raw_contract = "\n\n".join(item["text"] for item in TEN_LABELLED_CLAUSES_DATASET)
    vector_store = populate_default_vector_store()
    neg_memory = populate_default_negotiation_memory()
    manager = ReviewManagerAgent(
        vector_store=vector_store,
        negotiation_memory=neg_memory,
        counterparty_name="ApexCloud Infrastructure Inc.",
    )
    report = await manager.analyze_contract_text(
        raw_text=raw_contract,
        contract_filename="CA2_Group2_10_Clause_Benchmark.txt",
        contract_prefix="EVAL",
    )

    by_num = {c.clause_number: c for c in report.risk_ranked_clauses}
    rows: List[ClauseEvaluationRow] = []
    agreed_count = 0

    for item in TEN_LABELLED_CLAUSES_DATASET:
        c_num = item["clause_number"]
        human_lbl = item["human_label"]
        rec = by_num[c_num]
        sys_3tier = map_score_to_3tier_label(rec.risk_score)
        is_match = human_lbl.lower() == sys_3tier.lower()
        if is_match:
            agreed_count += 1

        pb_ref = (
            rec.retrieved_playbook_references[0].section_ref
            if rec.retrieved_playbook_references
            else "N/A"
        )
        rows.append(
            ClauseEvaluationRow(
                clause_number=c_num,
                clause_heading=rec.clause_heading,
                group_human_label=human_lbl,
                system_3tier_label=sys_3tier,
                system_5tier_severity=rec.risk_severity.value,
                risk_score=rec.risk_score,
                playbook_ref=pb_ref,
                agreed=is_match,
            )
        )

    def _class_acc(label: str) -> str:
        sub = [r for r in rows if r.group_human_label == label]
        hits = sum(1 for r in sub if r.agreed)
        return f"{hits}/{len(sub)} ({(hits / max(1, len(sub))) * 100:.0f}%)"

    pct = round((agreed_count / len(rows)) * 100.0, 1)
    return TenClauseEvaluationSummary(
        total_clauses=len(rows),
        agreed_count=agreed_count,
        agreement_percentage=pct,
        high_precision_recall=_class_acc("High"),
        medium_precision_recall=_class_acc("Medium"),
        low_precision_recall=_class_acc("Low"),
        rows=rows,
    )


if __name__ == "__main__":
    summary = asyncio.run(run_10_clause_evaluation())
    print("=" * 88)
    print("Q2 CA2 EVALUATION TARGET: 10 HUMAN-LABELLED CLAUSES VS. MULTI-AGENT SYSTEM PREDICTIONS")
    print("Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)")
    print("=" * 88)
    print(f"{'Cl #':<5} | {'Clause Heading':<36} | {'Group':<7} | {'System':<7} | {'Score':<6} | {'Match'}")
    print("-" * 88)
    for r in summary.rows:
        m_str = "YES (Agree)" if r.agreed else "NO"
        print(
            f"{r.clause_number:<5} | {r.clause_heading[:36]:<36} | {r.group_human_label:<7} | "
            f"{r.system_3tier_label:<7} | {r.risk_score:>3}/100 | {m_str}"
        )
    print("-" * 88)
    print(
        f"OVERALL AGREEMENT RATE: {summary.agreed_count}/{summary.total_clauses} "
        f"({summary.agreement_percentage}%) | High: {summary.high_precision_recall} | "
        f"Medium: {summary.medium_precision_recall} | Low: {summary.low_precision_recall}"
    )
    print("=" * 88)
