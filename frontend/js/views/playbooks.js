/**
 * views/playbooks.js
 * Internal company playbook chunks & multi-agent execution telemetry renderer.
 */

import { appState } from '../state.js';
import { escapeHtml } from '../utils/sanitize.js';

export function renderPlaybooksAndTelemetryView() {
  const q = (document.getElementById('playbookSearchInput')?.value || '').trim().toLowerCase();
  const filtered = appState.playbookChunks.filter(ch => {
    if (!q) return true;
    return (
      ch.section_ref.toLowerCase().includes(q) ||
      ch.heading.toLowerCase().includes(q) ||
      (ch.policy_rule || '').toLowerCase().includes(q) ||
      ch.category.toLowerCase().includes(q)
    );
  });

  const chunksContainer = document.getElementById('playbookChunksContainer');
  if (chunksContainer) {
    if (filtered.length === 0) {
      chunksContainer.innerHTML = `
        <div class="p-6 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
          No playbook rules match "${escapeHtml(q)}".
        </div>
      `;
    } else {
      chunksContainer.innerHTML = filtered.map(ch => {
        const sectionRefEsc = escapeHtml(ch.section_ref);
        const headingEsc = escapeHtml(ch.heading);
        const categoryEsc = escapeHtml(ch.category);
        const policyRuleEsc = escapeHtml(ch.policy_rule);
        const wordingEsc = escapeHtml(ch.preferred_wording_template);

        return `
          <div class="p-4 rounded-xl bg-white border border-slate-200 space-y-2 shadow-2xs">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="text-xs mono font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">${sectionRefEsc}</span>
                <span class="text-sm font-bold text-slate-900">${headingEsc}</span>
              </div>
              <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">${categoryEsc}</span>
            </div>
            <p class="text-xs text-slate-700 leading-relaxed"><strong>Governing Rule:</strong> ${policyRuleEsc}</p>
            <p class="text-xs text-emerald-800 bg-emerald-50/70 p-2.5 rounded-lg border border-emerald-200 leading-relaxed">
              <strong>Preferred Replacement Wording:</strong> ${wordingEsc}
            </p>
          </div>
        `;
      }).join('');
    }
  }

  const traceBody = document.getElementById('agentTraceTableBody');
  if (traceBody && appState.report?.agent_traces) {
    traceBody.innerHTML = appState.report.agent_traces.map(t => {
      const agentNameEsc = escapeHtml(t.agent_name);
      const stageEsc = escapeHtml(t.stage);
      const clausesProcessedEsc = escapeHtml(String(t.clauses_processed));
      const durationEsc = escapeHtml(String(t.duration_ms));
      const statusEsc = escapeHtml(t.status);
      const detailsEsc = escapeHtml(t.details);

      return `
        <tr class="hover:bg-slate-50 border-b border-slate-200">
          <td class="py-2.5 px-3 font-bold text-slate-900 mono">${agentNameEsc}</td>
          <td class="py-2.5 px-3 text-slate-700 font-medium">${stageEsc}</td>
          <td class="py-2.5 px-3 text-slate-700">${clausesProcessedEsc}</td>
          <td class="py-2.5 px-3 mono text-slate-600">${durationEsc} ms</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">✓ ${statusEsc}</span></td>
          <td class="py-2.5 px-3 text-slate-600">${detailsEsc}</td>
        </tr>
      `;
    }).join('');
  }
}
