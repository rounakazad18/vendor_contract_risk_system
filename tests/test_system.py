"""
Comprehensive Unit & Integration Test Suite (`tests/test_system.py`)
Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
"""

from __future__ import annotations
import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas import (
    ClauseRecord,
    RiskSeverity,
    ProcessingStatus,
    ApprovalRecommendation,
)
from shared_memory import SharedClauseTable
from vector_store import PlaybookVectorStore
from negotiation_memory import NegotiationHistoryMemory, populate_default_negotiation_memory
from evaluate_10_clauses import run_10_clause_evaluation
from agents import (
    ClauseSplitterAgent,
    PlaybookRetrievalAgent,
    RiskScorerAgent,
    RedlineDrafterAgent,
    ReviewManagerAgent,
)
from data.sample_data import (
    populate_default_vector_store,
    generate_sample_contract_files,
    SAMPLE_VENDOR_CONTRACT_TXT,
    UNNUMBERED_POORLY_FORMATTED_CONTRACT_TXT,
)


class TestVendorContractRiskSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.mkdtemp(prefix="contract_test_")
        cls.sample_files = generate_sample_contract_files(cls.temp_dir)
        cls.vector_store = populate_default_vector_store()

    def test_01_contract_text_extraction_txt_docx_and_pdf(self) -> None:
        """1. Test contract text extraction from TXT, DOCX, and PDF files."""
        splitter = ClauseSplitterAgent()
        txt_content = splitter.extract_text_from_file(self.sample_files["txt"])
        docx_content = splitter.extract_text_from_file(self.sample_files["docx"])
        pdf_content = splitter.extract_text_from_file(self.sample_files["pdf"])

        self.assertIn("MASTER SAAS AND CLOUD SERVICES AGREEMENT", txt_content)
        self.assertIn("Limitation of Liability", txt_content)
        self.assertIn("MASTER SAAS AND CLOUD SERVICES AGREEMENT", docx_content)
        self.assertIn("Cayman Islands", docx_content)
        self.assertIn("MASTER SAAS AND CLOUD SERVICES AGREEMENT", pdf_content)
        self.assertIn("Limitation of Liability", pdf_content)

    def test_02_clause_splitting_numbered_and_unnumbered(self) -> None:
        """2. Test clause splitting, numbering, subclause preservation, and unnumbered contracts."""
        splitter = ClauseSplitterAgent()
        table = SharedClauseTable()
        records = splitter.split_text_into_clauses(
            SAMPLE_VENDOR_CONTRACT_TXT, table, contract_prefix="TST"
        )
        self.assertEqual(len(records), 12)
        self.assertEqual(records[0].clause_id, "TST-001")
        self.assertEqual(records[0].clause_number, "1")
        self.assertTrue(len(records[0].subclauses) >= 2)

        unnum_table = SharedClauseTable()
        unnum_records = splitter.split_text_into_clauses(
            UNNUMBERED_POORLY_FORMATTED_CONTRACT_TXT, unnum_table, contract_prefix="UNN"
        )
        self.assertEqual(len(unnum_records), 3)
        self.assertEqual(unnum_records[0].clause_id, "UNN-001")

    def test_03_playbook_retrieval_accuracy_and_missing_ref(self) -> None:
        """3. Test RAG playbook retrieval accuracy across multiple playbooks and missing-policy detection."""
        retrieval_agent = PlaybookRetrievalAgent(self.vector_store, min_similarity=0.22)
        table = SharedClauseTable()
        splitter = ClauseSplitterAgent()
        records = splitter.split_text_into_clauses(SAMPLE_VENDOR_CONTRACT_TXT, table)

        async def _run():
            clause_6 = [r for r in records if r.clause_number == "6"][0]
            refs_6, missing_6 = await retrieval_agent.retrieve_for_clause(clause_6, table)
            self.assertFalse(missing_6)
            self.assertTrue(len(refs_6) >= 1)
            self.assertIn("POL-LEGAL-2026-v4.2 §4.1", refs_6[0].section_ref)

            clause_8 = [r for r in records if r.clause_number == "8"][0]
            refs_8, missing_8 = await retrieval_agent.retrieve_for_clause(clause_8, table)
            self.assertFalse(missing_8)
            self.assertIn("POL-SEC-2026-v3.1 §2.3", refs_8[0].section_ref)

            unrelated = ClauseRecord(
                clause_id="UNREL-01",
                clause_number="99",
                clause_heading="Cafeteria Catering Menu & Parking Spaces",
                original_text="Vendor shall provide three reserved bicycle parking spots in the west garage.",
            )
            table.register_clause(unrelated)
            refs_unrel, missing_unrel = await retrieval_agent.retrieve_for_clause(unrelated, table)
            self.assertTrue(missing_unrel)
            self.assertEqual(len(refs_unrel), 0)

        asyncio.run(_run())

    def test_04_risk_scoring_consistency(self) -> None:
        """4. Test risk scoring consistency (0-100) and Critical/High/Medium/Low/No Risk categorization."""
        splitter = ClauseSplitterAgent()
        retrieval = PlaybookRetrievalAgent(self.vector_store)
        scorer = RiskScorerAgent()
        table = SharedClauseTable()
        records = splitter.split_text_into_clauses(SAMPLE_VENDOR_CONTRACT_TXT, table)

        async def _run():
            for r in records:
                await retrieval.retrieve_for_clause(r, table)
                await scorer.evaluate_clause(r, table)

            by_num = {r.clause_number: r for r in table.get_all_clauses()}
            self.assertEqual(by_num["6"].risk_severity, RiskSeverity.CRITICAL)
            self.assertGreaterEqual(by_num["6"].risk_score, 80)
            self.assertEqual(by_num["8"].risk_severity, RiskSeverity.CRITICAL)
            self.assertEqual(by_num["4"].risk_severity, RiskSeverity.CRITICAL)

            self.assertEqual(by_num["5"].risk_severity, RiskSeverity.HIGH)
            self.assertEqual(by_num["2"].risk_severity, RiskSeverity.HIGH)
            self.assertEqual(by_num["3"].risk_severity, RiskSeverity.HIGH)

            self.assertEqual(by_num["11"].risk_severity, RiskSeverity.MEDIUM)
            self.assertEqual(by_num["9"].risk_severity, RiskSeverity.MEDIUM)

            self.assertEqual(by_num["10"].risk_severity, RiskSeverity.LOW)

            self.assertEqual(by_num["1"].risk_severity, RiskSeverity.NO_RISK)
            self.assertEqual(by_num["7"].risk_severity, RiskSeverity.NO_RISK)
            self.assertEqual(by_num["12"].risk_severity, RiskSeverity.NO_RISK)

        asyncio.run(_run())

    def test_05_redline_generation_and_grounding(self) -> None:
        """5. Test redline generation preserves playbook grounding and produces diff operations."""
        splitter = ClauseSplitterAgent()
        retrieval = PlaybookRetrievalAgent(self.vector_store)
        scorer = RiskScorerAgent()
        redliner = RedlineDrafterAgent()
        table = SharedClauseTable()
        records = splitter.split_text_into_clauses(SAMPLE_VENDOR_CONTRACT_TXT, table)

        async def _run():
            for r in records:
                await retrieval.retrieve_for_clause(r, table)
                await scorer.evaluate_clause(r, table)
                await redliner.draft_redline_for_clause(r, table)

            by_num = {r.clause_number: r for r in table.get_all_clauses()}
            cl6 = by_num["6"]
            self.assertIn("TWELVE (12) MONTHS", cl6.suggested_replacement_wording)
            self.assertIn("POL-LEGAL-2026-v4.2 §4.1", cl6.redline_rationale)
            self.assertTrue(len(cl6.diff_operations) >= 2)

        asyncio.run(_run())

    def test_06_shared_memory_deduplication_and_sync(self) -> None:
        """6 & 7. Test SharedClauseTable deduplication and concurrent synchronization."""
        table = SharedClauseTable()
        rec1 = ClauseRecord(
            clause_id="DUP-001",
            clause_number="1",
            clause_heading="Payment",
            original_text="Customer shall pay all undisputed invoices within forty-five (45) days.",
        )
        rec2 = ClauseRecord(
            clause_id="DUP-001",
            clause_number="2",
            clause_heading="Other",
            original_text="Different text entirely for duplicate ID test.",
        )
        rec3 = ClauseRecord(
            clause_id="DUP-002",
            clause_number="2",
            clause_heading="Payment Copy",
            original_text="customer   shall pay all undisputed invoices within forty-five (45) days.",
        )

        self.assertTrue(table.register_clause(rec1))
        self.assertFalse(table.register_clause(rec2))
        self.assertFalse(table.register_clause(rec3))
        self.assertEqual(len(table.get_all_clauses()), 1)

    def test_07_manager_orchestration_and_end_to_end_analysis(self) -> None:
        """8 & 9. Test ReviewManagerAgent orchestration, telemetry, and end-to-end report generation."""
        manager = ReviewManagerAgent(vector_store=self.vector_store)
        progress_steps = []

        def _on_progress(stage: str, pct: int) -> None:
            progress_steps.append((stage, pct))

        report = asyncio.run(
            manager.analyze_contract_file(
                self.sample_files["pdf"],
                contract_prefix="MSA",
                progress_callback=_on_progress,
            )
        )

        self.assertEqual(report.executive_summary.total_clauses_analyzed, 12)
        self.assertEqual(report.executive_summary.flagged_clauses_count, 9)
        self.assertEqual(report.executive_summary.critical_count, 3)
        self.assertEqual(report.executive_summary.high_count, 3)
        self.assertEqual(report.executive_summary.medium_count, 2)
        self.assertEqual(report.executive_summary.low_count, 1)
        self.assertEqual(report.executive_summary.no_risk_count, 3)
        self.assertEqual(
            report.final_recommendations.approval_recommendation,
            ApprovalRecommendation.APPROVE_WITH_CHANGES,
        )
        self.assertEqual(len(report.agent_traces), 6)
        self.assertEqual(progress_steps[-1][1], 100)

        scores = [c.risk_score for c in report.risk_ranked_clauses]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_08_invalid_documents_and_malformed_agent_responses(self) -> None:
        """10. Test error handling for invalid documents and malformed agent outputs."""
        splitter = ClauseSplitterAgent()
        table = SharedClauseTable()

        with self.assertRaises(FileNotFoundError):
            splitter.extract_text_from_file("/tmp/non_existent_contract_99999.pdf")

        bad_ext = os.path.join(self.temp_dir, "contract.exe")
        with open(bad_ext, "w") as f:
            f.write("binary")
        with self.assertRaises(ValueError):
            splitter.extract_text_from_file(bad_ext)

        with self.assertRaises(ValueError):
            splitter.split_text_into_clauses("   ", table)

        valid_rec = ClauseRecord(
            clause_id="MAL-001",
            clause_number="1",
            clause_heading="Scope",
            original_text="Vendor shall provide standard consulting services to Customer.",
        )
        table.register_clause(valid_rec)
        with self.assertRaises(ValueError):
            asyncio.run(
                table.update_risk_assessment(
                    clause_id="MAL-001",
                    risk_score=145,
                    risk_severity=RiskSeverity.CRITICAL,
                    risk_explanation="Malformed score",
                    missing_protections=[],
                    policy_violations=[],
                    ambiguous_language=[],
                    unfavorable_obligations=[],
                )
            )

        unmapped_flagged = ClauseRecord(
            clause_id="MAL-002",
            clause_number="2",
            clause_heading="Unmapped",
            original_text="Some risky clause without any retrieved playbook reference.",
            missing_playbook_reference=True,
            risk_score=75,
            risk_severity=RiskSeverity.HIGH,
        )
        table.register_clause(unmapped_flagged)
        redliner = RedlineDrafterAgent()
        with self.assertRaises(ValueError):
            asyncio.run(redliner.draft_redline_for_clause(unmapped_flagged, table))

    def test_09_ca2_ten_clause_ground_truth_evaluation(self) -> None:
        """11. Test CA2 Evaluation Target: 10 human-labelled clauses agreement benchmark."""
        summary = asyncio.run(run_10_clause_evaluation())
        self.assertEqual(summary.total_clauses, 10)
        self.assertEqual(summary.agreed_count, 10)
        self.assertEqual(summary.agreement_percentage, 100.0)

    def test_10_negotiation_history_memory_and_kernel_plugins(self) -> None:
        """12. Test Repeat Counterparty Negotiation-History Memory and @kernel_function registry."""
        manager = ReviewManagerAgent(
            vector_store=self.vector_store,
            negotiation_memory=populate_default_negotiation_memory(),
            counterparty_name="ApexCloud Infrastructure Inc.",
        )
        self.assertGreaterEqual(len(manager.kernel_registry.tool_metadata), 2)

        report = asyncio.run(
            manager.analyze_contract_text(
                SAMPLE_VENDOR_CONTRACT_TXT,
                contract_filename="ApexCloud_Repeat_Contract_2026.txt",
            )
        )
        by_num = {c.clause_number: c for c in report.risk_ranked_clauses}
        self.assertIn(
            "Repeat Counterparty Memory Match: APEX-MSA-2025-014",
            by_num["6"].redline_rationale,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
