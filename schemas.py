"""
Structured schemas and data models for inter-agent communication in the
Multi-Agent Vendor Contract Risk Review System.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import datetime


class RiskSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NO_RISK = "No Risk"


class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    EXTRACTED = "EXTRACTED"
    PLAYBOOK_RETRIEVED = "PLAYBOOK_RETRIEVED"
    RISK_SCORED = "RISK_SCORED"
    REDLINE_DRAFTED = "REDLINE_DRAFTED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


class ApprovalRecommendation(str, Enum):
    APPROVE = "Approve"
    APPROVE_WITH_CHANGES = "Approve with Changes"
    REJECT = "Reject"


@dataclass
class PlaybookChunk:
    chunk_id: str
    document_id: str
    document_title: str
    section_ref: str
    heading: str
    category: str
    policy_rule: str
    mandatory_requirements: List[str]
    prohibited_terms: List[str]
    fallback_position: str
    preferred_wording_template: str
    raw_excerpt: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlaybookReference:
    chunk_id: str
    document_id: str
    document_title: str
    section_ref: str
    heading: str
    category: str
    governing_policy_rule: str
    supporting_excerpt: str
    similarity_score: float
    preferred_wording_template: str = ""
    fallback_position: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiffOperation:
    op_type: str  # "REMOVE", "MODIFY", "ADD"
    original_fragment: str
    replacement_fragment: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClauseRecord:
    clause_id: str
    clause_number: str
    clause_heading: str
    original_text: str
    subclauses: List[str] = field(default_factory=list)
    retrieved_playbook_references: List[PlaybookReference] = field(default_factory=list)
    applicable_policy_rules: List[str] = field(default_factory=list)
    missing_playbook_reference: bool = False
    risk_score: int = 0
    risk_severity: RiskSeverity = RiskSeverity.NO_RISK
    risk_explanation: str = ""
    missing_protections: List[str] = field(default_factory=list)
    policy_violations: List[str] = field(default_factory=list)
    ambiguous_language: List[str] = field(default_factory=list)
    unfavorable_obligations: List[str] = field(default_factory=list)
    suggested_replacement_wording: str = ""
    redline_rationale: str = ""
    diff_operations: List[DiffOperation] = field(default_factory=list)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    updated_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    @property
    def is_flagged(self) -> bool:
        return self.risk_severity in (
            RiskSeverity.CRITICAL,
            RiskSeverity.HIGH,
            RiskSeverity.MEDIUM,
            RiskSeverity.LOW,
        ) and self.risk_score >= 20

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risk_severity"] = self.risk_severity.value
        data["processing_status"] = self.processing_status.value
        data["is_flagged"] = self.is_flagged
        return data


@dataclass
class AgentExecutionTrace:
    agent_name: str
    stage: str
    started_at: str
    completed_at: str
    duration_ms: float
    clauses_processed: int
    status: str
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutiveSummary:
    contract_name: str
    total_clauses_analyzed: int
    flagged_clauses_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    no_risk_count: int
    average_risk_score: float
    overall_contract_risk_score: int
    overall_risk_level: str
    overall_assessment_narrative: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FinalRecommendations:
    top_risks_requiring_attention: List[str]
    clauses_requiring_legal_review: List[str]
    recommended_negotiation_priorities: List[str]
    approval_recommendation: ApprovalRecommendation
    approval_justification: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["approval_recommendation"] = self.approval_recommendation.value
        return data


@dataclass
class ContractReviewReport:
    report_id: str
    generated_at: str
    contract_filename: str
    playbooks_indexed: List[str]
    executive_summary: ExecutiveSummary
    risk_ranked_clauses: List[ClauseRecord]
    suggested_redlines: List[ClauseRecord]
    final_recommendations: FinalRecommendations
    agent_traces: List[AgentExecutionTrace]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "contract_filename": self.contract_filename,
            "playbooks_indexed": self.playbooks_indexed,
            "executive_summary": self.executive_summary.to_dict(),
            "risk_ranked_clauses": [c.to_dict() for c in self.risk_ranked_clauses],
            "suggested_redlines": [c.to_dict() for c in self.suggested_redlines],
            "final_recommendations": self.final_recommendations.to_dict(),
            "agent_traces": [t.to_dict() for t in self.agent_traces],
        }
