/**
 * views/evaluation.js
 * 10-clause benchmark evaluation table renderer.
 */

import { appState } from '../state.js';
import { escapeHtml } from '../utils/sanitize.js';

export function renderEvaluationView() {
  const ev = appState.evaluation;
  if (!ev) return;

  const badgeEl = document.getElementById('evalAgreementBadge');
  if (badgeEl) {
    badgeEl.textContent = `Overall Agreement: ${ev.agreed_count} / ${ev.total_clauses} (${ev.agreement_percentage}%)`;
  }

  const tbody = document.getElementById('evalTableBody');
  if (!tbody || !ev.rows) return;

  tbody.innerHTML = ev.rows.map(r => {
    const clauseNumEsc = escapeHtml(String(r.clause_number));
    const headingEsc = escapeHtml(r.clause_heading);
    const humanLabelEsc = escapeHtml(r.group_human_label);
    const systemLabelEsc = escapeHtml(r.system_3tier_label);
    const severityEsc = escapeHtml(r.system_5tier_severity);
    const playbookRefEsc = escapeHtml(r.playbook_ref);

    return `
      <tr class="hover:bg-slate-50 border-b border-slate-200">
        <td class="py-2.5 px-3 font-bold text-slate-900">Clause ${clauseNumEsc}: ${headingEsc}</td>
        <td class="py-2.5 px-3 font-semibold">${humanLabelEsc}</td>
        <td class="py-2.5 px-3 font-semibold text-indigo-700">${systemLabelEsc}</td>
        <td class="py-2.5 px-3 font-bold">${r.risk_score}/100 (${severityEsc})</td>
        <td class="py-2.5 px-3 mono text-slate-600">${playbookRefEsc}</td>
        <td class="py-2.5 px-3">
          <span class="px-2.5 py-0.5 rounded-full font-bold text-[11px] ${
            r.agreed
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
              : 'bg-rose-100 text-rose-800 border border-rose-300'
          }">
            ${r.agreed ? '✓ YES (Agree)' : '✕ NO'}
          </span>
        </td>
      </tr>
    `;
  }).join('');
}
