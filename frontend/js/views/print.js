/**
 * views/print.js
 * Printable PDF / paper report view generator.
 */

import { appState } from '../state.js';
import { escapeHtml } from '../utils/sanitize.js';

export function renderPrintableReport() {
  const rpt = appState.report;
  if (!rpt) return;
  const es = rpt.executive_summary;
  const fr = rpt.final_recommendations;
  const container = document.getElementById('printableReportSection');
  if (!container) return;

  const contractFileNameEsc = escapeHtml(rpt.contract_filename);
  const reportIdEsc = escapeHtml(rpt.report_id);
  const generatedAtEsc = escapeHtml(rpt.generated_at);
  const riskLevelEsc = escapeHtml(es.overall_risk_level);
  const recEsc = escapeHtml(fr.approval_recommendation);
  const narrativeEsc = escapeHtml(es.overall_assessment_narrative);
  const justEsc = escapeHtml(fr.approval_justification);

  container.innerHTML = `
    <div class="border-b-2 border-slate-900 pb-4 mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Q2: Contract Clause Risk Review System — Official Report</h1>
      <p class="text-xs text-slate-700 mt-1">
        <strong>Group 2:</strong> Gursirat Singh (12326116) &amp; Rounak Azad (12326217) &nbsp;|&nbsp; CO3 &amp; CO4 (30 Marks)
      </p>
      <p class="text-xs text-slate-600 mt-1">
        Contract: <strong>${contractFileNameEsc}</strong> | Report ID: <strong>${reportIdEsc}</strong> | Generated: ${generatedAtEsc}
      </p>
      <p class="text-sm font-bold mt-2">
        Composite Risk Score: ${es.overall_contract_risk_score}/100 (${riskLevelEsc}) — Recommendation: ${recEsc}
      </p>
    </div>
    <div class="space-y-3 mb-6">
      <h2 class="text-base font-bold text-slate-900">1. Executive Summary</h2>
      <p class="text-xs text-slate-700 leading-relaxed">${narrativeEsc}</p>
      <p class="text-xs text-slate-700 leading-relaxed"><strong>Approval Justification:</strong> ${justEsc}</p>
    </div>
    <div class="space-y-4">
      <h2 class="text-base font-bold text-slate-900">2. Risk-Ranked Clauses, Playbook References &amp; Suggested Redlines</h2>
      ${rpt.risk_ranked_clauses.map(c => {
        const ref = c.retrieved_playbook_references[0];
        const clNumEsc = escapeHtml(String(c.clause_number));
        const headingEsc = escapeHtml(c.clause_heading);
        const sevEsc = escapeHtml(c.risk_severity);
        const refStrEsc = escapeHtml(ref ? `${ref.section_ref} (${ref.heading})` : 'N/A');
        const expEsc = escapeHtml(c.risk_explanation);
        const origEsc = escapeHtml(c.original_text);
        const redlineEsc = escapeHtml(c.suggested_replacement_wording);

        return `
          <div class="border-b border-slate-300 pb-3 mb-3 space-y-1">
            <div class="text-sm font-bold text-slate-900">
              Clause ${clNumEsc}: ${headingEsc} — Score: ${c.risk_score}/100 (${sevEsc})
            </div>
            <div class="text-xs text-slate-600"><strong>Playbook Reference:</strong> ${refStrEsc}</div>
            <div class="text-xs text-slate-700"><strong>Risk Explanation:</strong> ${expEsc}</div>
            <div class="text-xs text-slate-700"><strong>Original Wording:</strong> ${origEsc}</div>
            ${c.is_flagged ? `<div class="text-xs text-slate-900"><strong>Suggested Redline Wording:</strong> ${redlineEsc}</div>` : ''}
          </div>
        `;
      }).join('')}
    </div>
  `;
}
