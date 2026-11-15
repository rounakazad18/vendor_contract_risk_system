"""
Agent 3: Risk Scorer Agent
"""

from __future__ import annotations
import logging
import re
from typing import Dict, List, Tuple, Any
from schemas import ClauseRecord, RiskSeverity
from shared_memory import SharedClauseTable
from framework_adapter import kernel_function

logger = logging.getLogger(__name__)


class RiskScorerAgent:
    AGENT_NAME = "RiskScorerAgent"

    RULE_EVALUATORS: List[Dict[str, Any]] = [
        {
            "id": "RULE_LIAB_CAP_LOW",
            "category": "Liability",
            "pattern": r"(?:one\s*\(1\)\s*month|1\s*month|three\s*\(3\)\s*months|fees\s+paid\s+in\s+the\s+month|exceed\s+\$10,000)",
            "weight": 48,
            "violation": "Vendor liability cap is severely below the mandatory 12-month fees floor (2x/24-month super-cap for data/IP).",
            "unfavorable": "Caps Vendor aggregate liability at 1–3 months of fees while exposing Customer to disproportionate loss.",
        },
        {
            "id": "RULE_LIAB_ASYMMETRIC_CONSEQUENTIAL",
            "category": "Liability",
            "pattern": r"(?:vendor\s+shall\s+not\s+be\s+liable\s+for\s+any\s+indirect|in\s+no\s+event\s+shall\s+vendor\s+be\s+liable|customer\s+waives\s+all\s+claims\s+for\s+consequential|excludes\s+data\s+breach\s+from\s+cap)",
            "weight": 47,
            "violation": "One-sided consequential damages waiver or exclusion of super-cap carve-outs (data breach, confidentiality, IP indemnity).",
            "missing_protection": "Mutual consequential damages waiver and mandatory super-cap carve-outs for IP infringement, confidentiality, and data security breaches.",
        },
        {
            "id": "RULE_DATA_BREACH_DELAY",
            "category": "Data Privacy & AI",
            "pattern": r"(?:ten\s*\(10\)\s*business\s+days|10\s+business\s+days|seven\s*\(7\)\s*days|commercially\s+reasonable\s+time\s+after\s+confirming|within\s+14\s+days|within\s+30\s+days)",
            "weight": 46,
            "violation": "Security incident notification window exceeds the strict 24-hour (or 48-hour outer regulatory) playbook mandate.",
            "unfavorable": "Delays breach reporting up to 10 business days, jeopardizing GDPR/CCPA/CERT-In 72-hour regulatory reporting timelines.",
        },
        {
            "id": "RULE_AI_MODEL_TRAINING",
            "category": "Data Privacy & AI",
            "pattern": r"(?:train\s+its\s+artificial\s+intelligence|train.*foundation\s+models|perpetual.*royalty-free.*license\s+to\s+use\s+customer\s+data|machine\s+learning\s+models|fine-tune\s+models)",
            "weight": 46,
            "violation": "Express violation of Company AI Governance Policy prohibiting Vendor from training or fine-tuning AI/ML models on Customer Data.",
            "missing_protection": "Explicit prohibition against using Customer Data, prompts, or outputs to train shared or third-party AI/ML models.",
        },
        {
            "id": "RULE_IP_VENDOR_RETENTION",
            "category": "Intellectual Property",
            "pattern": r"(?:all\s+deliverables.*belong\s+exclusively\s+to\s+vendor|vendor\s+shall\s+own\s+all\s+right,\s+title,\s+and\s+interest\s+in.*custom|assigns\s+to\s+vendor\s+all\s+rights\s+in\s+deliverables|derivative\s+works.*sole\s+property\s+of\s+vendor)",
            "weight": 88,
            "violation": "Assigns ownership of paid custom deliverables and derivative works to Vendor instead of Customer ('Work Made for Hire' violation).",
            "missing_protection": "Full ownership assignment ('Work Made for Hire') of custom deliverables and Customer-specific configurations to Customer.",
            "unfavorable": "Customer pays for custom development but only receives a revocable, non-transferable license.",
        },
        {
            "id": "RULE_INDEMNITY_ONE_WAY",
            "category": "Indemnification",
            "pattern": r"(?:customer\s+shall\s+indemnify,\s+defend,\s+and\s+hold\s+harmless\s+vendor|vendor\s+disclaims\s+any\s+obligation\s+to\s+indemnify|solely\s+at\s+customer's\s+expense\s+defend\s+vendor)",
            "weight": 78,
            "violation": "One-way indemnification clause requiring Customer to indemnify Vendor while omitting Vendor IP infringement and data breach indemnity.",
            "missing_protection": "Uncapped Vendor indemnification for third-party IP infringement, gross negligence, willful misconduct, and data breaches.",
            "unfavorable": "Shifts all third-party litigation defense costs onto Customer without reciprocal Vendor protection.",
        },
        {
            "id": "RULE_RENEWAL_LOCKIN",
            "category": "Term & Termination",
            "pattern": r"(?:automatically\s+renew\s+for\s+successive\s+thirty-six\s*\(36\)|36-month|three\s*\(3\)\s*year\s+renewal|120\s+days\s+prior\s+written\s+notice|non-cancellable.*no\s+right\s+to\s+terminate\s+for\s+convenience)",
            "weight": 74,
            "violation": "Multi-year (36-month) evergreen auto-renewal with excessive 120-day notice window and ban on termination for convenience.",
            "missing_protection": "Right to terminate for convenience upon 30 days' prior written notice with pro-rata refund of prepaid unearned fees.",
            "unfavorable": "Locks Customer into a 3-year renewal cycle with no early exit or pro-rata refund mechanism.",
        },
        {
            "id": "RULE_PAYMENT_TERMS_ESCALATION",
            "category": "Commercial & Payment",
            "pattern": r"(?:net\s*15|within\s+fifteen\s*\(15\)\s*days|2\.5%\s+per\s+month|increase\s+fees\s+at\s+any\s+time\s+in\s+its\s+sole\s+discretion|uncapped\s+annual\s+price)",
            "weight": 68,
            "violation": "Violates Net-45 minimum payment standard, imposes punitive 2.5%/month late fees, and allows uncapped unilateral price hikes.",
            "missing_protection": "Net-45 payment window, right to withhold disputed invoices in good faith, and annual renewal price increase cap (lesser of CPI or 3%).",
            "unfavorable": "Short 15-day invoice payment cycle coupled with 30% annualized late interest and uncapped fee escalation.",
        },
        {
            "id": "RULE_GOVERNING_LAW_OFFSHORE",
            "category": "Governing Law & Dispute",
            "pattern": r"(?:laws\s+of\s+the\s+cayman\s+islands|george\s+town|customer\s+shall\s+bear\s+all\s+costs\s+and\s+attorneys'\s+fees|waives\s+any\s+objection\s+to\s+offshore)",
            "weight": 52,
            "violation": "Designates unapproved offshore jurisdiction (Cayman Islands) and one-way fee shifting requiring Customer to pay Vendor's legal costs.",
            "missing_protection": "Approved governing law (State of Delaware or State of New York) and prevailing-party or mutual bear-own-costs fee allocation.",
        },
        {
            "id": "RULE_AUDIT_RESTRICTED",
            "category": "Audit & Compliance",
            "pattern": r"(?:once\s+every\s+twenty-four\s*\(24\)\s*months|self-attestation\s+letter|prohibited\s+from\s+conducting\s+any\s+on-site\s+or\s+third-party\s+security\s+audit)",
            "weight": 46,
            "violation": "Replaces annual SOC 2 Type II / ISO 27001 certification delivery and customer audit rights with a biennial Vendor self-attestation.",
            "missing_protection": "Annual SOC 2 Type II report delivery and right to audit upon 15 business days' notice (or immediately following a security incident).",
        },
        {
            "id": "RULE_SUBPROCESSOR_UNRESTRICTED",
            "category": "Subcontracting",
            "pattern": r"(?:engage\s+any\s+third-party\s+subcontractors\s+or\s+subprocessors\s+without\s+prior\s+notice|without\s+prior\s+notice\s+or\s+consent\s+of\s+customer)",
            "weight": 28,
            "violation": "Permits unrestricted onboarding of fourth-party data subprocessors without prior written notice or Customer right to object.",
            "missing_protection": "30-day advance written notice of new subprocessors, Customer objection window, and written flow-down of equivalent security obligations.",
        },
    ]

    AMBIGUITY_PATTERNS: List[Tuple[str, str]] = [
        (r"\bcommercially\s+reasonable\s+efforts\b", "Uses subjective 'commercially reasonable efforts' instead of measurable SLA or timeline commitments."),
        (r"\bin\s+its\s+sole\s+(?:and\s+absolute\s+)?discretion\b", "Grants unilateral 'sole discretion' to Vendor without objective criteria or Customer consent."),
        (r"\bfrom\s+time\s+to\s+time\b", "Permits unilateral modification of terms or policies 'from time to time' without formal written amendment."),
        (r"\bas\s+soon\s+as\s+practicable\b", "Uses indefinite 'as soon as practicable' timing rather than a fixed hour/day deadline."),
    ]

    @staticmethod
    def categorize_score(score: int) -> RiskSeverity:
        if score >= 80:
            return RiskSeverity.CRITICAL
        if score >= 60:
            return RiskSeverity.HIGH
        if score >= 40:
            return RiskSeverity.MEDIUM
        if score >= 20:
            return RiskSeverity.LOW
        return RiskSeverity.NO_RISK

    @kernel_function(
        name="score_clause_with_rules_tool",
        description="Evaluates a contract clause against retrieved playbook rules and returns a 0-100 risk score and severity breakdown.",
    )
    def score_clause_with_rules_tool(self, clause: ClauseRecord) -> Dict[str, Any]:
        text = clause.original_text
        lower_text = text.lower()

        total_score = 0
        missing_protections: List[str] = []
        policy_violations: List[str] = []
        ambiguous_language: List[str] = []
        unfavorable_obligations: List[str] = []

        for rule in self.RULE_EVALUATORS:
            if re.search(rule["pattern"], lower_text, re.IGNORECASE):
                total_score += int(rule["weight"])
                if "violation" in rule and rule["violation"] not in policy_violations:
                    policy_violations.append(rule["violation"])
                if "missing_protection" in rule and rule["missing_protection"] not in missing_protections:
                    missing_protections.append(rule["missing_protection"])
                if "unfavorable" in rule and rule["unfavorable"] not in unfavorable_obligations:
                    unfavorable_obligations.append(rule["unfavorable"])

        for ref in clause.retrieved_playbook_references:
            m_prohibited = re.search(
                r"(?im)^\*\*Prohibited Terms\*\*:\s*(.+)$", ref.supporting_excerpt
            )
            if m_prohibited:
                terms = [
                    t.strip(" -•*\"'").lower()
                    for t in m_prohibited.group(1).split(";")
                    if len(t.strip()) > 3
                ]
                for term in terms:
                    if term in lower_text and total_score < 25:
                        total_score += 25
                        msg = f"Contains prohibited term '{term}' flagged under {ref.section_ref}."
                        if msg not in policy_violations:
                            policy_violations.append(msg)

        for pat, desc in self.AMBIGUITY_PATTERNS:
            if re.search(pat, lower_text, re.IGNORECASE):
                ambiguous_language.append(desc)
                if total_score > 0:
                    total_score += 4

        if total_score == 0:
            if clause.missing_playbook_reference:
                total_score = 15
                risk_explanation = (
                    "No direct internal playbook policy matched this clause topic. "
                    "Preliminary scan shows standard commercial phrasing, but manual verification is advised."
                )
            else:
                if "confidential" in lower_text:
                    total_score = 10
                elif "force majeure" in lower_text:
                    total_score = 8
                else:
                    total_score = 5
                primary_ref = (
                    clause.retrieved_playbook_references[0].section_ref
                    if clause.retrieved_playbook_references
                    else "Internal Playbook"
                )
                risk_explanation = (
                    f"Clause aligns with company playbook requirements ({primary_ref}). "
                    "Mutual obligations, standard definitions, and protective carve-outs are properly preserved."
                )
        else:
            total_score = min(98, total_score)
            primary_ref = (
                clause.retrieved_playbook_references[0].section_ref
                if clause.retrieved_playbook_references
                else "Unmapped Policy"
            )
            explanation_parts: List[str] = [f"Violates {primary_ref}:"]
            if policy_violations:
                explanation_parts.append(" ".join(policy_violations))
            if unfavorable_obligations:
                explanation_parts.append(" ".join(unfavorable_obligations))
            if missing_protections:
                explanation_parts.append(f"Missing required protection: {missing_protections[0]}")
            risk_explanation = " ".join(explanation_parts)

        severity = self.categorize_score(total_score)
        return {
            "risk_score": total_score,
            "risk_severity": severity,
            "risk_explanation": risk_explanation,
            "missing_protections": missing_protections,
            "policy_violations": policy_violations,
            "ambiguous_language": ambiguous_language,
            "unfavorable_obligations": unfavorable_obligations,
        }

    async def evaluate_clause(
        self, clause: ClauseRecord, shared_table: SharedClauseTable
    ) -> ClauseRecord:
        res = self.score_clause_with_rules_tool(clause)
        return await shared_table.update_risk_assessment(
            clause_id=clause.clause_id,
            risk_score=res["risk_score"],
            risk_severity=res["risk_severity"],
            risk_explanation=res["risk_explanation"],
            missing_protections=res["missing_protections"],
            policy_violations=res["policy_violations"],
            ambiguous_language=res["ambiguous_language"],
            unfavorable_obligations=res["unfavorable_obligations"],
        )
