"""
frontend_app.py
===============
Interactive Streamlit Frontend for the Multi-Agent Vendor Contract Risk Review System.
Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
CO3 & CO4 — 30 Marks

Run:  python -m streamlit run frontend_app.py
      (uses system Python which has Streamlit + ReportLab;
       injects venv site-packages so all backend imports resolve)

CONSTRAINT: This file ONLY imports from existing backend modules as READ-ONLY.
            No existing backend file is modified.
"""

from __future__ import annotations

# ── Bootstrap: inject venv site-packages so backend imports work under system Python ──
import sys, os, glob

_HERE = os.path.dirname(os.path.abspath(__file__))
# Check both Windows (.venv/Lib/site-packages) and Unix/Mac (.venv/lib/python*/site-packages)
_VENV_SP_WIN = os.path.join(_HERE, ".venv", "Lib", "site-packages")
if os.path.exists(_VENV_SP_WIN) and _VENV_SP_WIN not in sys.path:
    sys.path.insert(0, _VENV_SP_WIN)

for sp in glob.glob(os.path.join(_HERE, ".venv", "lib", "python*", "site-packages")):
    if sp not in sys.path:
        sys.path.insert(0, sp)

# Also add the project root so "from agents import …" etc. resolve
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ── Standard-library & third-party (available in system Python) ──────────────────────
import asyncio
import io
import json
import tempfile
import textwrap
import datetime
from typing import Optional

import streamlit as st

# ── Backend imports (READ-ONLY) ───────────────────────────────────────────────────────
from agents import ReviewManagerAgent  # noqa: E402
from data.sample_data import (  # noqa: E402
    populate_default_vector_store,
    generate_sample_contract_files,
    SAMPLE_VENDOR_CONTRACT_TXT,
)
from report_generator import generate_report_html  # noqa: E402
from evaluate_10_clauses import (  # noqa: E402
    run_10_clause_evaluation,
    TenClauseEvaluationSummary,
    TEN_LABELLED_CLAUSES_DATASET,
)
from schemas import (  # noqa: E402
    ContractReviewReport,
    RiskSeverity,
    ApprovalRecommendation,
)

# ── PDF generation (ReportLab — pure-Python, no external binary) ──────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
    KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ─────────────────────────────────────────────────────────────────────────────────────
# Constants & helpers
# ─────────────────────────────────────────────────────────────────────────────────────

GROUP_BANNER = "Group 2 — Gursirat Singh (12326116) & Rounak Azad (12326217)"
SYSTEM_TITLE = "Q2 Contract Clause Risk Review System  |  CO3 & CO4"

SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#65A30D",
    "No Risk": "#16A34A",
}
SEVERITY_BG = {
    "Critical": "#FEF2F2",
    "High": "#FFF7ED",
    "Medium": "#FFFBEB",
    "Low": "#F7FEE7",
    "No Risk": "#F0FDF4",
}

AGENT_STEPS = [
    ("🔍", "Clause Splitter Agent", "Extracting & numbering clauses from the uploaded document"),
    ("📚", "Playbook Retrieval Agent", "Running RAG similarity search over internal company playbooks"),
    ("⚖️", "Risk Scorer Agent", "Scoring each clause 0–100 and assigning severity (Low/Medium/High/Critical)"),
    ("✏️", "Redline Drafter Agent", "Generating playbook-grounded replacement wording & checking counterparty memory"),
    ("✅", "Review Manager Agent", "Validating citations & compiling the final Contract Review Report"),
]


def _sev_badge(severity: str) -> str:
    col = SEVERITY_COLORS.get(severity, "#6B7280")
    return (
        f'<span style="background:{col};color:#fff;padding:2px 10px;'
        f'border-radius:12px;font-size:0.78rem;font-weight:700;">{severity}</span>'
    )


def _rec_badge(rec: str) -> str:
    colors_map = {
        "Approve": "#16A34A",
        "Approve with Changes": "#D97706",
        "Reject": "#DC2626",
    }
    col = colors_map.get(rec, "#6B7280")
    return (
        f'<span style="background:{col};color:#fff;padding:4px 16px;'
        f'border-radius:16px;font-size:1rem;font-weight:700;">{rec}</span>'
    )


def _run_async(coro):
    """Run an async coroutine from a sync Streamlit context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ─────────────────────────────────────────────────────────────────────────────────────
# PDF Report Generator (ReportLab)
# ─────────────────────────────────────────────────────────────────────────────────────

def build_pdf_report(report: ContractReviewReport) -> bytes:
    """Generate a print-ready PDF from a ContractReviewReport using ReportLab."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"Contract Risk Review — {report.contract_filename}",
        author="Multi-Agent Contract Risk Review System — Group 2",
    )

    styles = getSampleStyleSheet()
    primary = colors.HexColor("#0F172A")
    accent = colors.HexColor("#1E3A8A")
    sev_rl = {
        "Critical": colors.HexColor("#DC2626"),
        "High": colors.HexColor("#EA580C"),
        "Medium": colors.HexColor("#D97706"),
        "Low": colors.HexColor("#65A30D"),
        "No Risk": colors.HexColor("#16A34A"),
    }

    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, textColor=colors.white,
                        leading=22, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, textColor=primary,
                        leading=17, spaceBefore=14, spaceAfter=6)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=10.5, textColor=accent,
                        leading=14, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=6)
    bold = ParagraphStyle("Bold", parent=body, fontName="Helvetica-Bold")
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, textColor=colors.HexColor("#475569"))
    banner_sub = ParagraphStyle("BannerSub", parent=body, fontSize=9, textColor=colors.HexColor("#E2E8F0"))

    es = report.executive_summary
    fr = report.final_recommendations

    story = []

    # ── Banner header ──
    banner_data = [
        [Paragraph("Multi-Agent Vendor Contract Risk Review Report", h1)],
        [Paragraph(f"Contract: <b>{report.contract_filename}</b> &nbsp;|&nbsp; "
                   f"Report ID: <b>{report.report_id}</b> &nbsp;|&nbsp; Generated: {report.generated_at}",
                   banner_sub)],
        [Paragraph(f"Overall Risk Score: <b>{es.overall_contract_risk_score}/100 ({es.overall_risk_level})</b> "
                   f"&nbsp;|&nbsp; Recommendation: <b>{fr.approval_recommendation.value}</b>", banner_sub)],
        [Paragraph(f"{GROUP_BANNER}  |  {SYSTEM_TITLE}", banner_sub)],
    ]
    banner_tbl = Table(banner_data, colWidths=[doc.width])
    banner_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), primary),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(banner_tbl)
    story.append(Spacer(1, 10 * mm))

    # ── Executive Summary ──
    story.append(Paragraph("1. Executive Summary & Risk Distribution", h2))
    story.append(Paragraph(es.overall_assessment_narrative, body))
    story.append(Spacer(1, 4 * mm))

    kpi_data = [
        ["Total Clauses", "Flagged", "Critical", "High", "Medium", "Low", "No Risk", "Composite Score"],
        [str(es.total_clauses_analyzed), str(es.flagged_clauses_count),
         str(es.critical_count), str(es.high_count), str(es.medium_count),
         str(es.low_count), str(es.no_risk_count), f"{es.overall_contract_risk_score}/100"],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[doc.width / 8] * 8)
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("<b>Internal Playbooks Indexed in RAG Vector Store:</b>", bold))
    for pb in report.playbooks_indexed:
        story.append(Paragraph(f"• {pb}", small))
    story.append(Spacer(1, 6 * mm))

    # ── Risk-Ranked Clause Table ──
    story.append(Paragraph("2. Risk-Ranked Clause Evaluation Summary", h2))
    story.append(Paragraph(
        "All extracted clauses ranked highest to lowest risk score, with governing playbook reference and primary finding.",
        body))

    ranked_rows = [["Clause & Heading", "Risk Score", "Playbook Reference", "Primary Finding"]]
    for cl in report.risk_ranked_clauses:
        ref = cl.retrieved_playbook_references[0].section_ref if cl.retrieved_playbook_references else "No Match"
        rule = cl.retrieved_playbook_references[0].heading if cl.retrieved_playbook_references else "Manual Review"
        finding = cl.policy_violations[0] if cl.policy_violations else cl.risk_explanation
        ranked_rows.append([
            Paragraph(f"<b>Clause {cl.clause_number}:</b> {cl.clause_heading}", small),
            Paragraph(f"<b>{cl.risk_score}/100</b><br/>{cl.risk_severity.value}", small),
            Paragraph(f"<b>{ref}</b><br/>{rule}", small),
            Paragraph(textwrap.shorten(finding, 160, placeholder="…"), small),
        ])

    col_w = [doc.width * f for f in [0.22, 0.13, 0.25, 0.40]]
    ranked_tbl = Table(ranked_rows, colWidths=col_w, repeatRows=1)
    ranked_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ranked_tbl)
    story.append(PageBreak())

    # ── Redline Comparison Sections ──
    story.append(Paragraph("3. Clause-by-Clause Redline & Playbook Comparison", h2))
    story.append(Paragraph(
        f"For each of the {es.flagged_clauses_count} flagged clauses, the Redline Drafter Agent generated "
        "replacement wording grounded in the retrieved company playbook sections.", body))

    for cl in report.suggested_redlines:
        ref_obj = cl.retrieved_playbook_references[0] if cl.retrieved_playbook_references else None
        ref_citation = (f"{ref_obj.section_ref} ({ref_obj.document_title} — {ref_obj.heading})"
                        if ref_obj else "Unmapped Policy")
        policy_rule = ref_obj.governing_policy_rule if ref_obj else "N/A"
        sev_col = sev_rl.get(cl.risk_severity.value, colors.grey)

        block = []
        block.append(Paragraph(
            f"Clause {cl.clause_number}: {cl.clause_heading} — Score: {cl.risk_score}/100 ({cl.risk_severity.value})",
            h3))
        block.append(Paragraph(f"<b>Governing Playbook Citation:</b> {ref_citation}", small))
        block.append(Paragraph(f"<b>Applicable Policy Rule:</b> {policy_rule}", small))
        block.append(Spacer(1, 2 * mm))
        block.append(Paragraph(f"<b>Risk & Policy Violation Analysis:</b> {cl.risk_explanation}", body))
        block.append(Spacer(1, 2 * mm))

        # Side-by-side comparison table
        compare_data = [
            [Paragraph("<b>Original Vendor Wording</b>", bold),
             Paragraph("<b>Suggested Playbook-Aligned Redline</b>", bold)],
            [Paragraph(cl.original_text or "—", small),
             Paragraph(cl.suggested_replacement_wording or "—", small)],
        ]
        compare_tbl = Table(compare_data, colWidths=[doc.width / 2, doc.width / 2])
        compare_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FFF1F2")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F0FDF4")),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#FFF1F2")),
            ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#F0FDF4")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        block.append(compare_tbl)
        block.append(Spacer(1, 2 * mm))
        block.append(Paragraph(f"<b>Redline Rationale:</b> {cl.redline_rationale}", small))

        if cl.diff_operations:
            block.append(Paragraph("<b>Diff Operations:</b>", bold))
            for op in cl.diff_operations:
                block.append(Paragraph(f"• [{op.op_type}] {op.reason}", small))

        block.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
        block.append(Spacer(1, 3 * mm))
        story.append(KeepTogether(block[:4]))  # keep heading + citation together
        story.extend(block[4:])

    story.append(PageBreak())

    # ── Final Recommendations ──
    story.append(Paragraph("4. Final Recommendations & Negotiation Roadmap", h2))
    rec_val = fr.approval_recommendation.value
    rec_col = {"Approve": "#16A34A", "Approve with Changes": "#D97706", "Reject": "#DC2626"}.get(rec_val, "#6B7280")
    story.append(Paragraph(
        f'Overall Approval Recommendation: <font color="{rec_col}"><b>{rec_val}</b></font> — {fr.approval_justification}',
        body))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("A. Most Critical Risks Requiring Immediate Attention", h3))
    for item in fr.top_risks_requiring_attention:
        story.append(Paragraph(f"• {item}", small))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("B. Clauses Requiring Legal & InfoSec Review", h3))
    for item in fr.clauses_requiring_legal_review:
        story.append(Paragraph(f"• {item}", small))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("C. Recommended Counterparty Negotiation Priorities", h3))
    for i, item in enumerate(fr.recommended_negotiation_priorities, 1):
        story.append(Paragraph(f"{i}. {item}", small))

    story.append(PageBreak())

    # ── Agent Execution Telemetry ──
    story.append(Paragraph("5. Multi-Agent Orchestration & Execution Telemetry", h2))
    trace_data = [["Agent Module", "Workflow Stage", "Clauses", "Duration (ms)", "Details"]]
    for tr in report.agent_traces:
        trace_data.append([
            Paragraph(f"<b>{tr.agent_name}</b>", small),
            Paragraph(tr.stage, small),
            str(tr.clauses_processed),
            f"{tr.duration_ms:.1f}",
            Paragraph(textwrap.shorten(tr.details, 120, placeholder="…"), small),
        ])
    trace_col_w = [doc.width * f for f in [0.20, 0.22, 0.08, 0.10, 0.40]]
    trace_tbl = Table(trace_data, colWidths=trace_col_w, repeatRows=1)
    trace_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(trace_tbl)

    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────────────
# Pipeline runner
# ─────────────────────────────────────────────────────────────────────────────────────

def _make_manager() -> ReviewManagerAgent:
    vs = populate_default_vector_store()
    return ReviewManagerAgent(vector_store=vs, max_concurrency=6)


def run_pipeline_on_text(
    raw_text: str,
    contract_filename: str,
    progress_placeholder,
    status_placeholder,
) -> ContractReviewReport:
    """Run the 5-agent pipeline with a live step progress UI."""

    step_states = ["⏳"] * len(AGENT_STEPS)

    def _render_progress(active_idx: int, done: bool = False):
        lines = []
        for i, (icon, name, desc) in enumerate(AGENT_STEPS):
            if done or i < active_idx:
                indicator = "✅"
            elif i == active_idx:
                indicator = "🔄"
            else:
                indicator = "⏳"
            lines.append(f"{indicator} **Agent {i + 1}: {name}**  \n&nbsp;&nbsp;&nbsp;&nbsp;_{desc}_")
        progress_placeholder.markdown("\n\n".join(lines), unsafe_allow_html=True)

    _render_progress(0)
    status_placeholder.info("▶ Starting pipeline — initialising agents & vector store…")

    manager = _make_manager()
    _progress_steps = [0]

    def _cb(stage: str, pct: int):
        # Map pct → agent step index
        idx = max(0, min(4, (pct - 10) // 20))
        _render_progress(idx)
        status_placeholder.info(f"🔄 [{pct}%] {stage}")

    report = _run_async(
        manager.analyze_contract_text(
            raw_text=raw_text,
            contract_filename=contract_filename,
            contract_prefix="CL",
            progress_callback=_cb,
        )
    )

    _render_progress(5, done=True)
    status_placeholder.success("✅ All 5 agents completed — report ready!")
    return report


def run_pipeline_on_file(
    file_path: str,
    contract_filename: str,
    progress_placeholder,
    status_placeholder,
) -> ContractReviewReport:
    manager = _make_manager()

    def _cb(stage: str, pct: int):
        idx = max(0, min(4, (pct - 10) // 20))
        lines = []
        for i, (icon, name, desc) in enumerate(AGENT_STEPS):
            if i < idx:
                indicator = "✅"
            elif i == idx:
                indicator = "🔄"
            else:
                indicator = "⏳"
            lines.append(f"{indicator} **Agent {i + 1}: {name}**  \n&nbsp;&nbsp;&nbsp;&nbsp;_{desc}_")
        progress_placeholder.markdown("\n\n".join(lines), unsafe_allow_html=True)
        status_placeholder.info(f"🔄 [{pct}%] {stage}")

    report = _run_async(
        manager.analyze_contract_file(
            file_path=file_path,
            contract_prefix="CL",
            progress_callback=_cb,
        )
    )

    # Mark all done
    lines = [f"✅ **Agent {i + 1}: {n}**  \n&nbsp;&nbsp;&nbsp;&nbsp;_{d}_"
             for i, (_, n, d) in enumerate(AGENT_STEPS)]
    progress_placeholder.markdown("\n\n".join(lines), unsafe_allow_html=True)
    status_placeholder.success("✅ All 5 agents completed — report ready!")
    return report


# ─────────────────────────────────────────────────────────────────────────────────────
# UI Sections
# ─────────────────────────────────────────────────────────────────────────────────────

def render_executive_summary(report: ContractReviewReport):
    es = report.executive_summary
    fr = report.final_recommendations

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
                    color: #fff; padding: 24px 28px; border-radius: 16px; margin-bottom: 20px;
                    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);">
          <div style="display:flex; justify-content:space-between; align-items:center;">
             <h2 style="margin:0; font-size:1.5rem; color:#FFFFFF !important; font-weight:800;">📋 Executive Summary</h2>
             <span style="font-size:0.8rem; background:rgba(255,255,255,0.12); padding:4px 12px; border-radius:20px; color:#E2E8F0;">
               {report.contract_filename}
             </span>
          </div>
          <p style="margin:8px 0 0 0; font-size:0.8rem; color:#94A3B8;">{GROUP_BANNER} &nbsp;|&nbsp; {SYSTEM_TITLE}</p>
          <div style="margin:16px 0 0 0; font-size:0.95rem; color:#E2E8F0; line-height:1.6; border-top:1px solid rgba(255,255,255,0.1); padding-top:14px;">
            {es.overall_assessment_narrative}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI Cards with Modern Glass/Card Look
    cols = st.columns(7)
    kpis = [
        ("Total Clauses", es.total_clauses_analyzed, "#1E3A8A", "#EFF6FF"),
        ("Flagged", es.flagged_clauses_count, "#7C3AED", "#F5F3FF"),
        ("Critical", es.critical_count, "#DC2626", "#FEF2F2"),
        ("High", es.high_count, "#EA580C", "#FFF7ED"),
        ("Medium", es.medium_count, "#D97706", "#FFFBEB"),
        ("Low", es.low_count, "#65A30D", "#F7FEE7"),
        ("No Risk", es.no_risk_count, "#16A34A", "#F0FDF4"),
    ]
    for col, (label, val, color, bg) in zip(cols, kpis):
        col.markdown(
            f"""<div style="background:{bg}; border: 1px solid {color}30; border-top: 4px solid {color};
            padding:14px 10px; border-radius:12px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="font-size:1.8rem; font-weight:800; color:{color}; line-height:1.2;">{val}</div>
            <div style="font-size:0.75rem; color:#475569; font-weight:600; margin-top:4px;">{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Composite Risk Score", f"{es.overall_contract_risk_score} / 100")
    c2.metric("Average Clause Score", f"{es.average_risk_score} / 100")
    with c3:
        st.markdown("**Approval Recommendation**")
        st.markdown(_rec_badge(fr.approval_recommendation.value), unsafe_allow_html=True)

    with st.expander("📌 Final Recommendations & Negotiation Roadmap", expanded=False):
        st.markdown(f"**Approval Justification:** {fr.approval_justification}")

        if fr.top_risks_requiring_attention:
            st.markdown("**🔴 Top Risks Requiring Immediate Attention:**")
            for item in fr.top_risks_requiring_attention:
                st.markdown(f"- {item}")

        if fr.clauses_requiring_legal_review:
            st.markdown("**⚖️ Clauses Requiring Legal Review:**")
            for item in fr.clauses_requiring_legal_review:
                st.markdown(f"- {item}")

        if fr.recommended_negotiation_priorities:
            st.markdown("**🎯 Negotiation Priorities:**")
            for i, item in enumerate(fr.recommended_negotiation_priorities, 1):
                st.markdown(f"{i}. {item}")

    with st.expander("📡 Multi-Agent Execution Telemetry", expanded=False):
        trace_rows = []
        for tr in report.agent_traces:
            trace_rows.append({
                "Agent": tr.agent_name,
                "Stage": tr.stage,
                "Clauses": tr.clauses_processed,
                "Duration (ms)": f"{tr.duration_ms:.1f}",
                "Status": tr.status,
                "Details": tr.details,
            })
        if trace_rows:
            import pandas as pd
            st.dataframe(pd.DataFrame(trace_rows), use_container_width=True)


def render_clause_inspector(report: ContractReviewReport):
    st.markdown("## 🔍 Interactive Clause-by-Clause Risk & Redline Inspector")

    # Search + filter controls
    st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; padding:16px 20px; 
                    border-radius:12px; margin-bottom:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-weight:700; color:#1E3A8A; font-size:1rem; margin-bottom:10px;">
                🔎 Filter & Search Analyzed Clauses
            </div>
    """, unsafe_allow_html=True)
    
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_q = st.text_input("Search clauses", placeholder="Search by clause title, obligation, or legal keyword...", label_visibility="collapsed")
    with col_filter:
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All Severities", "Critical", "High", "High/Critical", "Medium", "Low", "No Risk"],
            label_visibility="collapsed",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    clauses = report.risk_ranked_clauses

    # Apply filters
    if search_q:
        q = search_q.lower()
        clauses = [c for c in clauses if q in c.clause_heading.lower() or q in c.original_text.lower()]

    if severity_filter not in ("All", "All Severities", ""):
        if severity_filter == "High/Critical":
            clauses = [c for c in clauses if c.risk_severity.value in ("Critical", "High")]
        else:
            clauses = [c for c in clauses if c.risk_severity.value == severity_filter]

    st.markdown(f"**Showing {len(clauses)} clause(s)**")

    if not clauses:
        st.info("No clauses match the current filter.")
        return

    for cl in clauses:
        sev = cl.risk_severity.value
        sev_col = SEVERITY_COLORS.get(sev, "#6B7280")
        sev_bg = SEVERITY_BG.get(sev, "#F9FAFB")
        ref = cl.retrieved_playbook_references[0] if cl.retrieved_playbook_references else None

        with st.expander(
            f"Clause {cl.clause_number}: {cl.clause_heading}  |  "
            f"Score: {cl.risk_score}/100  |  {sev}",
            expanded=False,
        ):
            # Header strip
            st.markdown(
                f"""<div style="background:{sev_bg};border-left:5px solid {sev_col};
                padding:10px 14px;border-radius:6px;margin-bottom:12px;">
                <span style="font-size:1rem;font-weight:700;color:{sev_col};">
                Clause {cl.clause_number}: {cl.clause_heading}</span>
                &nbsp;&nbsp;{_sev_badge(sev)}
                &nbsp;&nbsp;<span style="font-size:0.85rem;color:#475569;">
                Risk Score: <b>{cl.risk_score}/100</b></span>
                </div>""",
                unsafe_allow_html=True,
            )

            # Playbook reference
            if ref:
                st.markdown(
                    f"""**📚 Governing Playbook Reference**
- **Policy ID / Section:** {ref.document_id} — {ref.section_ref}
- **Policy Heading:** {ref.heading}
- **Category:** {ref.category}
- **RAG Similarity Score:** {ref.similarity_score:.4f}
- **Governing Policy Rule:** {ref.governing_policy_rule}"""
                )
            else:
                st.warning("No playbook reference retrieved for this clause.")

            st.markdown("---")

            # Risk explanation
            if cl.risk_explanation:
                st.markdown(f"**⚠️ Risk Explanation:**  \n{cl.risk_explanation}")

            if cl.policy_violations:
                st.markdown("**🚨 Policy Violations:**")
                for v in cl.policy_violations:
                    st.markdown(f"- {v}")

            if cl.missing_protections:
                st.markdown("**🛡️ Missing Protections:**")
                for v in cl.missing_protections:
                    st.markdown(f"- {v}")

            if cl.ambiguous_language:
                st.markdown("**❓ Ambiguous Language:**")
                for v in cl.ambiguous_language:
                    st.markdown(f"- {v}")

            if cl.unfavorable_obligations:
                st.markdown("**⚡ Unfavorable Obligations:**")
                for v in cl.unfavorable_obligations:
                    st.markdown(f"- {v}")

            if cl.subclauses:
                st.markdown("**📄 Subclauses Extracted:**")
                for sc in cl.subclauses:
                    st.markdown(f"- {sc}")

            # Side-by-side redline comparison
            if cl.suggested_replacement_wording:
                st.markdown("---")
                st.markdown("### ↔️ Side-by-Side Redline Comparison")
                left_col, right_col = st.columns(2)
                with left_col:
                    st.markdown(
                        f"""<div style="background:#FFF1F2;border:1px solid #FECACA;
                        border-top:4px solid #DC2626;padding:16px;border-radius:10px;height:100%;
                        box-shadow:0 2px 4px rgba(220,38,38,0.05);">
                        <div style="font-weight:700;color:#DC2626;margin-bottom:8px;font-size:0.95rem;">
                        🔴 Original Vendor Wording</div>
                        <div style="font-size:0.88rem;color:#1E293B;line-height:1.6;white-space:pre-wrap;">{cl.original_text}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with right_col:
                    st.markdown(
                        f"""<div style="background:#F0FDF4;border:1px solid #BBF7D0;
                        border-top:4px solid #16A34A;padding:16px;border-radius:10px;height:100%;
                        box-shadow:0 2px 4px rgba(22,163,74,0.05);">
                        <div style="font-weight:700;color:#16A34A;margin-bottom:8px;font-size:0.95rem;">
                        🟢 Suggested Playbook-Aligned Redline</div>
                        <div style="font-size:0.88rem;color:#1E293B;line-height:1.6;white-space:pre-wrap;">{cl.suggested_replacement_wording}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                st.markdown(f"**📝 Redline Rationale:** {cl.redline_rationale}")

                if cl.diff_operations:
                    st.markdown("**Diff Operations:**")
                    for op in cl.diff_operations:
                        tag_colors = {"REMOVE": "#DC2626", "MODIFY": "#D97706", "ADD": "#16A34A"}
                        tc = tag_colors.get(op.op_type, "#6B7280")
                        st.markdown(
                            f'<span style="background:{tc};color:#fff;padding:1px 7px;'
                            f'border-radius:4px;font-size:0.75rem;">{op.op_type}</span> '
                            f'**{op.reason}**',
                            unsafe_allow_html=True,
                        )

                # Copy redline button
                st.code(cl.suggested_replacement_wording, language=None)
                st.caption("☝️ Click to copy the redline wording above")


def render_evaluation_scorecard():
    st.markdown("## 📊 10-Clause Ground-Truth Evaluation Scorecard")
    st.markdown(
        f"""
        > **CA2 Evaluation Target** — Comparing Group 2's human-labelled risk annotations
        > (`Low`, `Medium`, `High`) against the multi-agent system's predictions on
        > 10 benchmark clauses.
        >
        > _{GROUP_BANNER}_
        """
    )

    with st.expander("📋 10 Labelled Benchmark Clauses (Ground Truth)", expanded=False):
        for item in TEN_LABELLED_CLAUSES_DATASET:
            st.markdown(
                f"**Clause {item['clause_number']}: {item['heading']}** — "
                f"Human Label: **{item['human_label']}**"
            )

    if st.button("▶ Run 10-Clause Evaluation Now", type="primary"):
        with st.spinner("Running 10-clause benchmark evaluation through the multi-agent pipeline…"):
            try:
                summary = _run_async(run_10_clause_evaluation())
                st.session_state["eval_summary"] = summary
            except Exception as e:
                st.error(f"Evaluation failed: {e}")
                return

    summary: Optional[TenClauseEvaluationSummary] = st.session_state.get("eval_summary")
    if summary is None:
        st.info("Click the button above to run the evaluation.")
        return

    # Agreement banner
    pct = summary.agreement_percentage
    pct_col = "#16A34A" if pct >= 80 else "#D97706" if pct >= 60 else "#DC2626"
    st.markdown(
        f"""<div style="background:{pct_col}18;border:2px solid {pct_col};
        padding:16px 20px;border-radius:10px;text-align:center;margin:12px 0;">
        <span style="font-size:2rem;font-weight:800;color:{pct_col};">
        {summary.agreed_count}/{summary.total_clauses} = {pct}% Agreement</span>
        <br><span style="color:#475569;">Overall system–human label agreement rate</span>
        </div>""",
        unsafe_allow_html=True,
    )

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("High Precision/Recall", summary.high_precision_recall)
    mc2.metric("Medium Precision/Recall", summary.medium_precision_recall)
    mc3.metric("Low Precision/Recall", summary.low_precision_recall)

    st.markdown("### 10-Clause Comparison Table")
    rows = []
    for r in summary.rows:
        rows.append({
            "Cl #": r.clause_number,
            "Clause Heading": r.clause_heading,
            "Group Label": r.group_human_label,
            "System Label (3-tier)": r.system_3tier_label,
            "System Severity (5-tier)": r.system_5tier_severity,
            "Risk Score": f"{r.risk_score}/100",
            "Playbook Ref": r.playbook_ref,
            "Match": "✅ YES" if r.agreed else "❌ NO",
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.apply(
            lambda row: ["background:#F0FDF4" if row["Match"] == "✅ YES" else "background:#FFF1F2"] * len(row),
            axis=1,
        ),
        use_container_width=True,
        height=380,
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Contract Clause Risk Review System — Group 2",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # ── Global CSS ──
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        [data-testid="stAppViewContainer"] { 
            background: #F8FAFC !important; 
            color: #0F172A !important; 
        }
        [data-testid="stHeader"] { 
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #E2E8F0;
        }
        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
            color: #0F172A !important;
        }

        /* Typography */
        p, span, label, div, li, strong, b, em { 
            color: #0F172A; 
        }
        h1, h2, h3, h4, h5, h6 { 
            color: #0F172A !important; 
            letter-spacing: -0.02em;
            font-weight: 700;
        }

        /* Sleek Modern Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: #E2E8F0;
            padding: 6px;
            border-radius: 12px;
            border-bottom: none !important;
        }
        .stTabs [data-baseweb="tab"] { 
            font-size: 0.92rem; 
            font-weight: 600; 
            color: #475569 !important;
            background: transparent !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            border: none !important;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] { 
            background: #FFFFFF !important;
            color: #1E3A8A !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
        }

        /* Modern Card Styling */
        .stExpander {
            border: none !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03) !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
            margin-bottom: 12px !important;
            transition: all 0.2s ease;
        }
        .stExpander:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }
        .stExpander > details {
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
        }
        .stExpander summary {
            font-weight: 600 !important;
            padding: 14px 18px !important;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 1px solid #CBD5E1 !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15) !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        }

        /* Metric Cards */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            padding: 16px 20px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        [data-testid="stMetricValue"] {
            font-weight: 800 !important;
            color: #1E3A8A !important;
        }

        /* Code block font */
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Top Navigation Bar ──
    nav_left, nav_mid, nav_right = st.columns([3, 5, 2])
    with nav_left:
        st.markdown(
            f"""<div style="padding:8px 0;">
            <span style="font-size:1.3rem;font-weight:800;color:#0F172A;">⚖️ ContractRisk AI</span><br>
            <span style="font-size:0.72rem;color:#64748B;">{GROUP_BANNER}</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with nav_mid:
        st.markdown(
            f"""<div style="text-align:center;padding:8px 0;color:#475569;font-size:0.82rem;">
            {SYSTEM_TITLE}
            </div>""",
            unsafe_allow_html=True,
        )
    with nav_right:
        # PDF download button (shown when report is available)
        report: Optional[ContractReviewReport] = st.session_state.get("report")
        if report is not None:
            pdf_bytes = st.session_state.get("pdf_bytes")
            if pdf_bytes is None:
                pdf_bytes = build_pdf_report(report)
                st.session_state["pdf_bytes"] = pdf_bytes
            safe_name = report.contract_filename.replace(" ", "_").replace("/", "_")
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"{safe_name}_Risk_Review_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

    st.markdown("---")

    # ── Tabs ──
    tab_upload, tab_clauses, tab_eval = st.tabs([
        "📤 Upload & Analyse",
        "🔍 Clause Inspector",
        "📊 10-Clause Evaluation",
    ])

    # ════════════════════ TAB 1: Upload & Analyse ════════════════════
    with tab_upload:
        st.markdown("## 📤 Upload Vendor Contract & Run Analysis")

        # Group attribution banner
        st.markdown(
            f"""<div style="background:#1E3A8A;color:#fff;padding:12px 18px;
            border-radius:8px;margin-bottom:16px;">
            <b>{GROUP_BANNER}</b><br>
            <span style="font-size:0.82rem;color:#BFDBFE;">{SYSTEM_TITLE}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        col_upload, col_sample = st.columns([3, 1])
        with col_upload:
            uploaded = st.file_uploader(
                "Drag & drop your vendor contract here, or click to browse",
                type=["pdf", "docx", "txt"],
                help="Accepts .pdf, .docx, and .txt vendor contracts",
            )
        with col_sample:
            st.markdown("<br>", unsafe_allow_html=True)
            use_sample = st.button(
                "📋 Load 12-Clause Sample Contract\n(ApexCloud MSA 2026)",
                use_container_width=True,
            )
            use_10clause = st.button(
                "📋 Load 10-Clause Benchmark\n(CA2 Evaluation Target)",
                use_container_width=True,
            )

        # Determine what to run
        trigger_analysis = False
        raw_text_to_analyse: Optional[str] = None
        contract_name = "Uploaded_Vendor_Contract.txt"
        is_file_upload = False
        tmp_path: Optional[str] = None

        if uploaded is not None and st.button("▶ Run Contract Analysis", type="primary"):
            trigger_analysis = True
            contract_name = uploaded.name
            if uploaded.name.endswith(".txt"):
                raw_text_to_analyse = uploaded.read().decode("utf-8", errors="replace")
            else:
                # Save to temp file for PDF/DOCX handling
                suffix = "." + uploaded.name.rsplit(".", 1)[-1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(uploaded.read())
                tmp.flush()
                tmp.close()
                tmp_path = tmp.name
                is_file_upload = True

        elif use_sample:
            trigger_analysis = True
            raw_text_to_analyse = SAMPLE_VENDOR_CONTRACT_TXT
            contract_name = "ApexCloud_Enterprise_MSA_2026.txt"

        elif use_10clause:
            from evaluate_10_clauses import TEN_LABELLED_CLAUSES_DATASET
            trigger_analysis = True
            raw_text_to_analyse = "\n\n".join(item["text"] for item in TEN_LABELLED_CLAUSES_DATASET)
            contract_name = "CA2_Group2_10_Clause_Benchmark.txt"

        if trigger_analysis:
            st.session_state.pop("report", None)
            st.session_state.pop("pdf_bytes", None)
            st.session_state.pop("eval_summary", None)

            st.markdown("### 🤖 Multi-Agent Pipeline Execution")
            progress_ph = st.empty()
            status_ph = st.empty()

            try:
                if is_file_upload and tmp_path:
                    report = run_pipeline_on_file(tmp_path, contract_name, progress_ph, status_ph)
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                else:
                    report = run_pipeline_on_text(
                        raw_text_to_analyse, contract_name, progress_ph, status_ph
                    )
                st.session_state["report"] = report
                st.rerun()
            except Exception as e:
                st.error(f"❌ Pipeline error: {e}")
                import traceback
                st.code(traceback.format_exc())

        # Show summary if report already in session
        report: Optional[ContractReviewReport] = st.session_state.get("report")
        if report is not None:
            render_executive_summary(report)

            # PDF download (also in-tab)
            pdf_bytes = st.session_state.get("pdf_bytes")
            if pdf_bytes is None:
                pdf_bytes = build_pdf_report(report)
                st.session_state["pdf_bytes"] = pdf_bytes
            safe_name = report.contract_filename.replace(" ", "_").replace("/", "_")
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"{safe_name}_Risk_Review_Report.pdf",
                mime="application/pdf",
                type="primary",
            )
        else:
            st.markdown(
                """
                <div style="border:2px dashed #CBD5E1;border-radius:12px;padding:40px;
                text-align:center;color:#94A3B8;margin-top:16px;">
                <div style="font-size:2.5rem;">📄</div>
                <div style="font-size:1rem;margin-top:8px;">
                Upload a vendor contract (PDF / DOCX / TXT) or click a sample button above,<br>
                then press <b>▶ Run Contract Analysis</b> to start the 5-agent review pipeline.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ════════════════════ TAB 2: Clause Inspector ════════════════════
    with tab_clauses:
        report: Optional[ContractReviewReport] = st.session_state.get("report")
        if report is None:
            st.info("👆 Upload and analyse a contract first (see the **Upload & Analyse** tab).")
        else:
            render_clause_inspector(report)

    # ════════════════════ TAB 3: 10-Clause Evaluation ════════════════════
    with tab_eval:
        render_evaluation_scorecard()


if __name__ == "__main__":
    main()
