/**
 * views/redlines.js
 * Redline Studio view renderer — clause sidebar + word-level diff viewer.
 */

import { appState } from '../state.js';
import { severityBadgeHtml } from '../components/severity-badge.js';
import { escapeHtml } from '../utils/sanitize.js';
import { showToast } from '../components/toast.js';

// ---------------------------------------------------------------------------
// LCS-based word diff helper
// ---------------------------------------------------------------------------
function computeWordDiff(original, suggested) {
  const origWords = original.split(/(\s+)/);
  const sugWords  = suggested.split(/(\s+)/);

  // Filter to actual word tokens and whitespace separately
  const oTokens = origWords;
  const sTokens = sugWords;

  // Build LCS table on non-whitespace words only for alignment
  const oWords = origWords.filter(t => t.trim().length > 0);
  const sWords = sugWords.filter(t => t.trim().length > 0);

  const m = oWords.length;
  const n = sWords.length;
  // LCS DP
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = oWords[i - 1] === sWords[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }

  // Backtrack to build diff sequences
  const diffOrig = []; // 'keep' | 'remove'
  const diffSug  = []; // 'keep' | 'add'
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && oWords[i - 1] === sWords[j - 1]) {
      diffOrig.unshift({ word: oWords[i - 1], type: 'keep' });
      diffSug.unshift({ word: sWords[j - 1], type: 'keep' });
      i--; j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      diffSug.unshift({ word: sWords[j - 1], type: 'add' });
      j--;
    } else {
      diffOrig.unshift({ word: oWords[i - 1], type: 'remove' });
      i--;
    }
  }

  // Build HTML for original side (removed words struck through)
  const origHtml = diffOrig.map(d =>
    d.type === 'remove'
      ? `<span class="diff-remove line-through text-rose-600 bg-rose-50">${escapeHtml(d.word)}</span>`
      : escapeHtml(d.word)
  ).join(' ');

  // Build HTML for suggested side (added words highlighted)
  const sugHtml = diffSug.map(d =>
    d.type === 'add'
      ? `<span class="diff-add text-emerald-700 bg-emerald-50 font-semibold">${escapeHtml(d.word)}</span>`
      : escapeHtml(d.word)
  ).join(' ');

  // Unified mode: interleave removed (-) and added (+) lines
  const removedWords = diffOrig.filter(d => d.type === 'remove').map(d => escapeHtml(d.word));
  const addedWords   = diffSug.filter(d => d.type === 'add').map(d => escapeHtml(d.word));
  let unifiedHtml = '';
  if (removedWords.length) {
    unifiedHtml += `<div class="text-rose-600 bg-rose-50/60 px-2 py-0.5 rounded mb-0.5"><span class="font-bold mr-1">−</span>${removedWords.join(' ')}</div>`;
  }
  if (addedWords.length) {
    unifiedHtml += `<div class="text-emerald-700 bg-emerald-50/60 px-2 py-0.5 rounded"><span class="font-bold mr-1">+</span>${addedWords.join(' ')}</div>`;
  }
  if (!unifiedHtml) {
    unifiedHtml = `<div class="text-slate-500 italic text-xs">No differences detected.</div>`;
  }

  return { origHtml, sugHtml, unifiedHtml };
}

// ---------------------------------------------------------------------------
// Redline Studio main renderer
// ---------------------------------------------------------------------------
export function renderRedlineStudio() {
  const rpt = appState.report;
  if (!rpt) return;
  const flaggedOnly = document.getElementById('toggleFlaggedOnly').checked;
  const searchQ = (document.getElementById('studioSearchInput')?.value || '').trim().toLowerCase();

  const list = rpt.risk_ranked_clauses.filter(c => {
    if (flaggedOnly && !c.is_flagged) return false;
    if (!searchQ) return true;
    const ref = c.retrieved_playbook_references[0]?.section_ref || '';
    return (
      c.clause_heading.toLowerCase().includes(searchQ) ||
      c.original_text.toLowerCase().includes(searchQ) ||
      ref.toLowerCase().includes(searchQ)
    );
  });

  if (!appState.selectedClauseId || !list.some(c => c.clause_id === appState.selectedClauseId)) {
    appState.selectedClauseId = list[0] ? list[0].clause_id : (rpt.risk_ranked_clauses[0]?.clause_id || null);
  }

  // Sidebar
  const sidebarEl = document.getElementById('redlineClauseSidebarList');
  sidebarEl.innerHTML = list.map(c => {
    const isSelected = c.clause_id === appState.selectedClauseId;
    const isAccepted = !!appState.acceptedRedlines[c.clause_id];
    const clauseId   = escapeHtml(c.clause_id);
    const clauseNum  = escapeHtml(String(c.clause_number));
    const heading    = escapeHtml(c.clause_heading);
    const sectionRef = escapeHtml(c.retrieved_playbook_references[0]?.section_ref || 'No Direct Match');
    return `
      <button data-select-clause="${clauseId}" class="w-full text-left p-3 rounded-xl border transition flex items-start justify-between gap-2 ${
        isSelected
          ? 'bg-indigo-50/90 border-indigo-500 shadow-xs'
          : 'bg-white hover:bg-slate-50 border-slate-200'
      }">
        <div class="space-y-1">
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-bold text-slate-900">Clause ${clauseNum}: ${heading}</span>
            ${isAccepted ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">Approved</span>` : ''}
          </div>
          <div class="text-[11px] text-slate-500">${sectionRef}</div>
        </div>
        <div class="text-right shrink-0">
          <div class="text-xs font-extrabold text-slate-900">${c.risk_score}/100</div>
          <div class="mt-0.5">${severityBadgeHtml(c.risk_severity)}</div>
        </div>
      </button>
    `;
  }).join('');

  // Detail panel
  const selectedClause = rpt.risk_ranked_clauses.find(c => c.clause_id === appState.selectedClauseId);
  const detailEl = document.getElementById('redlineDetailContainer');
  if (!selectedClause) {
    detailEl.innerHTML = `<p class="text-sm text-slate-500">No clauses match your current filter.</p>`;
    return;
  }

  const ref            = selectedClause.retrieved_playbook_references[0];
  const isAccepted     = !!appState.acceptedRedlines[selectedClause.clause_id];
  const hasMemoryMatch = (selectedClause.redline_rationale || '').includes('Repeat Counterparty Memory Match');

  const clauseIdEsc    = escapeHtml(selectedClause.clause_id);
  const clauseNumEsc   = escapeHtml(String(selectedClause.clause_number));
  const headingEsc     = escapeHtml(selectedClause.clause_heading);
  const riskExpEsc     = escapeHtml(selectedClause.risk_explanation);
  const sectionRefEsc  = escapeHtml(ref ? ref.section_ref : 'Unmapped Topic');
  const refHeadingEsc  = escapeHtml(ref ? ref.heading : '');
  const govRuleEsc     = escapeHtml(ref ? (ref.governing_policy_rule || ref.policy_rule) : 'No governing policy retrieved.');
  const redlineRatEsc  = escapeHtml(selectedClause.redline_rationale);

  // Word diff
  const diff = computeWordDiff(
    selectedClause.original_text,
    selectedClause.suggested_replacement_wording
  );

  detailEl.innerHTML = `
    <div class="flex flex-wrap items-start justify-between gap-3 pb-4 border-b border-slate-200">
      <div>
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs mono font-bold text-indigo-600">${clauseIdEsc}</span>
          ${severityBadgeHtml(selectedClause.risk_severity)}
          <span class="text-xs font-bold text-slate-800">Risk Score: ${selectedClause.risk_score} / 100</span>
          ${hasMemoryMatch ? `<span class="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-300 font-bold">★ Repeat Counterparty Memory Applied</span>` : ''}
        </div>
        <h2 class="text-lg font-bold text-slate-900 mt-1">
          Clause ${clauseNumEsc}: ${headingEsc}
        </h2>
      </div>

      <div class="flex items-center gap-2">
        <button id="btnCopySuggestedWording" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 transition">
          Copy Redline Wording
        </button>
        <button id="btnToggleAcceptRedline" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
          isAccepted
            ? 'bg-emerald-600 text-white'
            : 'bg-indigo-600 hover:bg-indigo-500 text-white'
        }">
          ${isAccepted ? '✓ Redline Approved' : 'Approve Suggested Redline'}
        </button>
      </div>
    </div>

    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xs font-bold uppercase tracking-wider text-indigo-700">
          Playbook Reference Behind Flag: ${ref ? `${sectionRefEsc} (${refHeadingEsc})` : 'Unmapped Topic'}
        </span>
        <span class="text-xs mono text-slate-500">
          RAG Similarity: ${ref ? (ref.similarity_score * 100).toFixed(0) + '%' : 'N/A'}
        </span>
      </div>
      <p class="text-xs text-slate-700 leading-relaxed">
        <strong>Governing Playbook Rule:</strong> ${govRuleEsc}
      </p>
      <p class="text-xs text-slate-700 leading-relaxed">
        <strong>Identified Risk &amp; Violation Explanation:</strong> ${riskExpEsc}
      </p>
    </div>

    <!-- Split / Unified toggle -->
    <div class="flex items-center gap-2 pt-1">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Diff View:</span>
      <button data-diff-mode="split"
        class="diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-indigo-600 text-white transition"
        id="btnDiffSplit">Split</button>
      <button data-diff-mode="unified"
        class="diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition"
        id="btnDiffUnified">Unified</button>
    </div>

    <!-- Split mode (default) -->
    <div id="diffSplitPanel" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="p-4 rounded-xl bg-rose-50/50 border border-rose-200 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase text-rose-800">Original Vendor Contract Wording</span>
          <span class="text-[11px] font-semibold text-rose-600">Uploaded Contract Text</span>
        </div>
        <p class="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">${diff.origHtml}</p>
      </div>

      <div class="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase text-emerald-800">Suggested Playbook-Aligned Redline</span>
          <span class="text-[11px] font-semibold text-emerald-700">${ref ? sectionRefEsc : 'Compliant'}</span>
        </div>
        <p class="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">${diff.sugHtml}</p>
      </div>
    </div>

    <!-- Unified mode (hidden by default) -->
    <div id="diffUnifiedPanel" class="hidden p-4 rounded-xl bg-slate-50 border border-slate-200 overflow-auto max-h-72 space-y-0.5">
      <div class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Unified Diff</div>
      ${diff.unifiedHtml}
    </div>

    <!-- Editable textarea -->
    <div class="space-y-1 pt-1">
      <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Edit Suggested Wording</label>
      <textarea id="editableRedlineTextarea" rows="6"
        class="w-full p-2.5 text-xs text-slate-900 font-medium bg-white border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 leading-relaxed"
      >${escapeHtml(selectedClause.suggested_replacement_wording)}</textarea>
    </div>

    <div class="space-y-3 pt-1">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">Redline Rationale &amp; Structured Diff Operations</h3>
      <p class="text-xs text-slate-700 leading-relaxed bg-indigo-50/50 p-3 rounded-lg border border-indigo-100">
        ${redlineRatEsc}
      </p>
      <div class="space-y-1.5">
        ${(selectedClause.diff_operations || []).map(op => `
          <div class="text-xs p-2.5 rounded-lg border border-slate-200 flex items-start gap-2">
            <span class="px-2 py-0.5 rounded font-bold text-[10px] ${
              op.op_type === 'REMOVE' ? 'bg-rose-100 text-rose-800' :
              op.op_type === 'MODIFY' ? 'bg-amber-100 text-amber-800' :
              'bg-emerald-100 text-emerald-800'
            }">${op.op_type}</span>
            <span class="text-slate-700">${escapeHtml(op.reason || op.detail || '')}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // Copy button
  document.getElementById('btnCopySuggestedWording').addEventListener('click', () => {
    const val = document.getElementById('editableRedlineTextarea').value;
    try {
      navigator.clipboard.writeText(val);
    } catch (e) {
      const ta = document.getElementById('editableRedlineTextarea');
      ta.select();
      document.execCommand('copy');
    }
    showToast(`Copied redline wording for Clause ${selectedClause.clause_number}`);
  });

  // Accept / revoke button
  document.getElementById('btnToggleAcceptRedline').addEventListener('click', () => {
    selectedClause.suggested_replacement_wording = document.getElementById('editableRedlineTextarea').value;
    appState.acceptedRedlines[selectedClause.clause_id] = !appState.acceptedRedlines[selectedClause.clause_id];
    showToast(
      appState.acceptedRedlines[selectedClause.clause_id]
        ? `Approved redline for Clause ${selectedClause.clause_number}`
        : `Reverted approval for Clause ${selectedClause.clause_number}`
    );
    renderRedlineStudio();
  });

  // Split / Unified toggle
  document.getElementById('btnDiffSplit').addEventListener('click', () => {
    document.getElementById('diffSplitPanel').classList.remove('hidden');
    document.getElementById('diffUnifiedPanel').classList.add('hidden');
    document.getElementById('btnDiffSplit').className = 'diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-indigo-600 text-white transition';
    document.getElementById('btnDiffUnified').className = 'diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
  });
  document.getElementById('btnDiffUnified').addEventListener('click', () => {
    document.getElementById('diffSplitPanel').classList.add('hidden');
    document.getElementById('diffUnifiedPanel').classList.remove('hidden');
    document.getElementById('btnDiffUnified').className = 'diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-indigo-600 text-white transition';
    document.getElementById('btnDiffSplit').className = 'diff-toggle-btn px-2.5 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
  });
}
