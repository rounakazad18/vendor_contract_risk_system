/**
 * views/clause-table.js
 * Centralized Shared Clause Table renderer — risk-ranked, searchable, filterable.
 */

import { appState } from '../state.js';
import { severityBadgeHtml } from '../components/severity-badge.js';
import { escapeHtml } from '../utils/sanitize.js';

export function renderSharedClauseTable() {
  const rpt = appState.report;
  if (!rpt) return;
  const searchQ = (document.getElementById('clauseSearchInput')?.value || '').trim().toLowerCase();
  const sevFilter = document.getElementById('severityFilterSelect')?.value || 'ALL';
  const tbody = document.getElementById('sharedClauseTableBody');
  if (!tbody) return;

  const filtered = rpt.risk_ranked_clauses.filter(c => {
    if (sevFilter !== 'ALL' && c.risk_severity !== sevFilter) return false;
    if (!searchQ) return true;
    const refStr = c.retrieved_playbook_references[0]?.section_ref || '';
    return (
      c.clause_heading.toLowerCase().includes(searchQ) ||
      c.original_text.toLowerCase().includes(searchQ) ||
      refStr.toLowerCase().includes(searchQ) ||
      c.clause_id.toLowerCase().includes(searchQ)
    );
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-8 text-center text-slate-500">
          No clauses match your search or severity filter.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(c => {
    const ref = c.retrieved_playbook_references[0];
    const clauseIdEsc = escapeHtml(c.clause_id);
    const clauseNumEsc = escapeHtml(String(c.clause_number));
    const headingEsc = escapeHtml(c.clause_heading);
    const riskExpEsc = escapeHtml(c.risk_explanation);
    const subclauseCount = (c.subclauses || []).length;
    const statusEsc = escapeHtml(c.processing_status || 'VALIDATED');

    return `
      <tr class="hover:bg-slate-50 transition border-b border-slate-200">
        <td class="py-3 px-3">
          <div class="font-bold text-slate-900">Clause ${clauseNumEsc}: ${headingEsc}</div>
          <div class="text-[11px] mono text-slate-400">${clauseIdEsc} • ${subclauseCount} subclause(s)</div>
        </td>
        <td class="py-3 px-3 font-extrabold text-sm text-slate-900">${c.risk_score} <span class="text-xs font-normal text-slate-500">/ 100</span></td>
        <td class="py-3 px-3">${severityBadgeHtml(c.risk_severity)}</td>
        <td class="py-3 px-3">
          ${ref
            ? `<div class="font-semibold text-indigo-700">${escapeHtml(ref.section_ref)}</div>
               <div class="text-[11px] text-slate-500">${escapeHtml(ref.heading)} (Sim: ${(ref.similarity_score * 100).toFixed(0)}%)</div>`
            : `<span class="text-rose-600 font-semibold">Missing Playbook Ref</span>`
          }
        </td>
        <td class="py-3 px-3 max-w-md"><p class="text-slate-700 line-clamp-2">${riskExpEsc}</p></td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[11px] mono bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
            ${statusEsc}
          </span>
        </td>
        <td class="py-3 px-3 text-right">
          <button data-inspect-clause="${clauseIdEsc}" class="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition">
            Check &amp; Redline
          </button>
        </td>
      </tr>
    `;
  }).join('');
}
