"""
Report Generator Module
"""

from __future__ import annotations
import html
from schemas import ContractReviewReport, RiskSeverity


def _esc(val: str) -> str:
    return html.escape(str(val or ""))


def generate_report_html(report: ContractReviewReport) -> str:
    es = report.executive_summary
    fr = report.final_recommendations

    ranked_rows_html = []
    for cl in report.risk_ranked_clauses:
        primary_ref = (
            cl.retrieved_playbook_references[0].section_ref
            if cl.retrieved_playbook_references
            else "No Direct Match"
        )
        primary_rule = (
            cl.retrieved_playbook_references[0].heading
            if cl.retrieved_playbook_references
            else "Manual Review Required"
        )
        sev_marker = {
            RiskSeverity.CRITICAL: "▲ Critical",
            RiskSeverity.HIGH: "▲ High",
            RiskSeverity.MEDIUM: "◆ Medium",
            RiskSeverity.LOW: "● Low",
            RiskSeverity.NO_RISK: "✓ No Risk",
        }.get(cl.risk_severity, cl.risk_severity.value)

        concise_summary = (
            cl.policy_violations[0]
            if cl.policy_violations
            else cl.risk_explanation
        )

        ranked_rows_html.append(
            f"""
            <tr>
              <td><strong>Clause {_esc(cl.clause_number)}: {_esc(cl.clause_heading)}</strong></td>
              <td><strong>{cl.risk_score}/100</strong> ({_esc(sev_marker)})</td>
              <td><strong>{_esc(primary_ref)}</strong> — {_esc(primary_rule)}</td>
              <td>{_esc(concise_summary)}</td>
            </tr>
            """
        )

    redline_sections_html = []
    for cl in report.suggested_redlines:
        primary_ref_obj = (
            cl.retrieved_playbook_references[0] if cl.retrieved_playbook_references else None
        )
        ref_citation = (
            f"{primary_ref_obj.section_ref} ({primary_ref_obj.document_title} — {primary_ref_obj.heading})"
            if primary_ref_obj
            else "Unmapped Policy"
        )
        policy_rule_text = (
            primary_ref_obj.governing_policy_rule if primary_ref_obj else "N/A"
        )

        diff_items = []
        for op in cl.diff_operations:
            diff_items.append(
                f"<li><strong>[{_esc(op.op_type)}]</strong> {_esc(op.reason)}</li>"
            )
        diff_list_html = (
            f"<ul>{''.join(diff_items)}</ul>" if diff_items else ""
        )

        redline_sections_html.append(
            f"""
            <article class="entry">
              <h3>Clause {_esc(cl.clause_number)}: {_esc(cl.clause_heading)} — Risk Score: {cl.risk_score}/100 ({_esc(cl.risk_severity.value)})</h3>
              <p><strong>Governing Playbook Citation:</strong> {_esc(ref_citation)}<br>
              <strong>Applicable Company Policy Rule:</strong> {_esc(policy_rule_text)}</p>
              <p><strong>Identified Risk &amp; Policy Violation Analysis:</strong> {_esc(cl.risk_explanation)}</p>
              <p><strong>Original Vendor Contract Wording:</strong> {_esc(cl.original_text)}</p>
              <p><strong>Proposed Playbook-Aligned Replacement Wording:</strong> {_esc(cl.suggested_replacement_wording)}</p>
              <p><strong>Redline Rationale &amp; Negotiation Fallback:</strong> {_esc(cl.redline_rationale)}</p>
              {diff_list_html}
              <hr>
            </article>
            """
        )

    compliant_clauses = [c for c in report.risk_ranked_clauses if not c.is_flagged]
    compliant_rows_html = []
    for cl in compliant_clauses:
        ref_str = (
            cl.retrieved_playbook_references[0].section_ref
            if cl.retrieved_playbook_references
            else "N/A"
        )
        compliant_rows_html.append(
            f"""
            <tr>
              <td><strong>Clause {_esc(cl.clause_number)}: {_esc(cl.clause_heading)}</strong></td>
              <td>{cl.risk_score}/100 ({_esc(cl.risk_severity.value)})</td>
              <td>{_esc(ref_str)}</td>
              <td>{_esc(cl.original_text)}</td>
            </tr>
            """
        )

    trace_rows_html = []
    for tr in report.agent_traces:
        trace_rows_html.append(
            f"""
            <tr>
              <td><strong>{_esc(tr.agent_name)}</strong></td>
              <td>{_esc(tr.stage)}</td>
              <td>{tr.clauses_processed}</td>
              <td>{tr.duration_ms:.2f} ms</td>
              <td>✓ {_esc(tr.status)} — {_esc(tr.details)}</td>
            </tr>
            """
        )

    top_risks_li = "".join(f"<li>{_esc(item)}</li>" for item in fr.top_risks_requiring_attention)
    legal_rev_li = "".join(f"<li>{_esc(item)}</li>" for item in fr.clauses_requiring_legal_review)
    neg_prio_li = "".join(f"<li>{_esc(item)}</li>" for item in fr.recommended_negotiation_priorities)
    playbooks_li = "".join(f"<li>{_esc(pb)}</li>" for pb in report.playbooks_indexed)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vendor Contract Risk Review Report — {_esc(report.contract_filename)}</title>
  <style>
    :root {{
      --primary: #0F172A;
      --accent: #1E3A8A;
      --text: #1E293B;
      --bg: #FFFFFF;
    }}

    @page {{
      size: A4;
      margin: 20mm 18mm;
      background: var(--bg);
      @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Inter', 'Noto Sans', sans-serif;
        font-size: 8.5pt;
        color: var(--text);
      }}
      @bottom-left {{
        content: "Multi-Agent Vendor Contract Risk Review Report | " "{_esc(report.report_id)}";
        font-family: 'Inter', 'Noto Sans', sans-serif;
        font-size: 8.5pt;
        color: var(--text);
      }}
    }}

    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
    }}
    body {{
      font-family: 'Inter', 'Noto Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 10pt;
      line-height: 1.58;
      color: var(--text);
    }}
    @media screen {{
      html, body {{ background: var(--bg); }}
      body {{ max-width: 900px; margin: 0 auto; padding: 32px 40px; }}
    }}

    main.document-flow {{ width: 100%; margin: 0; padding: 0; }}
    * {{ border: none; border-radius: 0; box-shadow: none; background: transparent; outline: none; }}

    h1 {{ font-family: 'Inter', 'Noto Sans', sans-serif; font-size: 18.5pt; line-height: 1.25; margin: 0 0 6px 0; color: #FFFFFF; }}
    h2 {{ font-family: 'Inter', 'Noto Sans', sans-serif; font-size: 13pt; line-height: 1.3; margin: 22px 0 8px 0; color: var(--primary); break-after: avoid; page-break-after: avoid; }}
    h3 {{ font-size: 10.5pt; line-height: 1.3; margin: 16px 0 6px 0; color: var(--accent); break-after: avoid; page-break-after: avoid; }}
    p {{ margin: 0 0 9px 0; }}
    ul, ol {{ margin: 0 0 10px 0; padding-left: 18px; }}
    li {{ margin-bottom: 4px; }}

    section, article, .entry {{ margin-bottom: 14px; }}

    table {{ width: 100%; border-collapse: collapse; margin: 10px 0 14px 0; }}
    th, td {{ text-align: left; vertical-align: top; padding: 6px 8px; font-size: 9.5pt; line-height: 1.4; }}
    th {{ border-bottom: 2px solid var(--primary); font-weight: 700; color: var(--primary); }}
    td {{ border-bottom: 1px solid rgba(15, 23, 42, 0.12); }}
    hr {{ border-bottom: 1px solid rgba(15, 23, 42, 0.15); margin: 12px 0; }}
    .full-bleed-header {{ background: var(--primary); color: #FFFFFF; padding: 18px 22px; margin-bottom: 18px; }}
    .full-bleed-header p {{ color: #E2E8F0; margin: 3px 0 0 0; font-size: 9.5pt; }}

    tr, figure {{ break-inside: avoid; page-break-inside: avoid; }}
  </style>
</head>
<body>
  <main class="document-flow">
    <div class="full-bleed-header">
      <h1>Multi-Agent Vendor Contract Risk Review Report</h1>
      <p>Group 2: <strong>Gursirat Singh (12326116)</strong> &amp; <strong>Rounak Azad (12326217)</strong> &nbsp;|&nbsp; Q2 CA2 (CO3 &amp; CO4 — 30 Marks)</p>
      <p>Contract: <strong>{_esc(report.contract_filename)}</strong> &nbsp;|&nbsp; Report ID: <strong>{_esc(report.report_id)}</strong> &nbsp;|&nbsp; Generated: {_esc(report.generated_at)}</p>
      <p>Overall Contract Risk Score: <strong>{es.overall_contract_risk_score}/100 ({_esc(es.overall_risk_level)})</strong> &nbsp;|&nbsp; Recommendation: <strong>{_esc(fr.approval_recommendation.value)}</strong></p>
    </div>

    <section>
      <h2>1. Executive Summary &amp; Risk Distribution</h2>
      <p>{_esc(es.overall_assessment_narrative)}</p>
      <table>
        <thead>
          <tr>
            <th>Total Clauses</th>
            <th>Flagged Clauses</th>
            <th>Critical (80–100)</th>
            <th>High (60–79)</th>
            <th>Medium (40–59)</th>
            <th>Low (20–39)</th>
            <th>No Risk (0–19)</th>
            <th>Composite Risk</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>{es.total_clauses_analyzed}</strong></td>
            <td><strong>{es.flagged_clauses_count}</strong></td>
            <td><strong>{es.critical_count}</strong></td>
            <td><strong>{es.high_count}</strong></td>
            <td><strong>{es.medium_count}</strong></td>
            <td><strong>{es.low_count}</strong></td>
            <td><strong>{es.no_risk_count}</strong></td>
            <td><strong>{es.overall_contract_risk_score} / 100</strong></td>
          </tr>
        </tbody>
      </table>
      <p><strong>Internal Company Playbooks Indexed in RAG Vector Store:</strong></p>
      <ul>
        {playbooks_li}
      </ul>
    </section>

    <section>
      <h2>2. Risk-Ranked Clause Evaluation Summary</h2>
      <p>All extracted clauses are ranked below from highest to lowest risk score (0–100) alongside their governing internal playbook reference and primary risk finding.</p>
      <table>
        <thead>
          <tr>
            <th style="width: 22%;">Clause &amp; Heading</th>
            <th style="width: 15%;">Risk Score</th>
            <th style="width: 25%;">Playbook Reference</th>
            <th style="width: 38%;">Primary Policy Assessment</th>
          </tr>
        </thead>
        <tbody>
          {''.join(ranked_rows_html)}
        </tbody>
      </table>
    </section>

    <section>
      <h2>3. Suggested Playbook-Aligned Redlines &amp; Clause Comparison</h2>
      <p>For each of the {es.flagged_clauses_count} flagged clauses, the Redline Drafter Agent generated replacement wording grounded strictly in the retrieved company playbook sections.</p>
      {''.join(redline_sections_html)}
    </section>

    <section>
      <h2>4. Compliant Clauses Verified Against Playbook</h2>
      <p>The following clauses satisfied internal playbook requirements without requiring redline modifications:</p>
      <table>
        <thead>
          <tr>
            <th style="width: 22%;">Clause</th>
            <th style="width: 14%;">Score</th>
            <th style="width: 18%;">Playbook Ref</th>
            <th style="width: 46%;">Original Contract Wording</th>
          </tr>
        </thead>
        <tbody>
          {''.join(compliant_rows_html)}
        </tbody>
      </table>
    </section>

    <section>
      <h2>5. Final Recommendations &amp; Negotiation Roadmap</h2>
      <p><strong>Overall Contract Approval Recommendation: {_esc(fr.approval_recommendation.value)}</strong> — {_esc(fr.approval_justification)}</p>

      <h3>A. Most Critical Risks Requiring Immediate Attention</h3>
      <ul>
        {top_risks_li}
      </ul>

      <h3>B. Clauses Requiring Escalated Legal &amp; InfoSec Review</h3>
      <ul>
        {legal_rev_li}
      </ul>

      <h3>C. Recommended Counterparty Negotiation Priorities &amp; Fallbacks</h3>
      <ol>
        {neg_prio_li}
      </ol>
    </section>

    <section>
      <h2>6. Multi-Agent Orchestration &amp; Execution Telemetry</h2>
      <p>The Review Manager Agent coordinated four specialist worker agents over the SharedClauseTable:</p>
      <table>
        <thead>
          <tr>
            <th style="width: 22%;">Agent Module</th>
            <th style="width: 22%;">Workflow Stage</th>
            <th style="width: 10%;">Clauses</th>
            <th style="width: 12%;">Duration</th>
            <th style="width: 34%;">Execution Details</th>
          </tr>
        </thead>
        <tbody>
          {''.join(trace_rows_html)}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
