/**
 * LexGuard AI — Frontend Application Entry Point
 * Modular ES module architecture — Phases 1–3 Improvements
 * Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217) — Q2 CA2 (30 Marks)
 */

import { appState, persistState } from './state.js';
import { SAMPLE_CONTRACTS } from './data/contracts.js';
import { runLocalMultiAgentPipeline } from './engine.js';
import { showToast } from './components/toast.js';
import { renderPipelinePills } from './components/pipeline-pills.js';
import { switchTab } from './components/tab-nav.js';
import { renderDashboardView } from './views/dashboard.js';
import { renderRedlineStudio } from './views/redlines.js';
import { renderSharedClauseTable } from './views/clause-table.js';
import { renderEvaluationView } from './views/evaluation.js';
import { renderPlaybooksAndTelemetryView } from './views/playbooks.js';
import { renderPrintableReport } from './views/print.js';
import { fetchInitialData, analyzeContract, downloadPdfFromServer } from './api.js';

// ─── Render orchestrator ───────────────────────────────────────────────────
export function renderAllViews() {
  renderPipelinePills(5);
  renderDashboardView();
  renderRedlineStudio();
  renderSharedClauseTable();
  renderEvaluationView();
  renderPlaybooksAndTelemetryView();
  renderPrintableReport();
}

// ─── Loading state ─────────────────────────────────────────────────────────
function setLoading(isLoading) {
  appState.isLoading = isLoading;
  const skeleton = document.getElementById('loadingSkeleton');
  const dashContent = document.getElementById('dashboardContent');
  if (skeleton) skeleton.classList.toggle('hidden', !isLoading);
  if (dashContent) dashContent.classList.toggle('hidden', isLoading);
}

// ─── Dark mode ─────────────────────────────────────────────────────────────
function applyDarkMode(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  const btn = document.getElementById('btnDarkMode');
  if (btn) btn.textContent = dark ? '☀️ Light' : '🌙 Dark';
  appState.darkMode = dark;
  persistState();
}

// ─── File upload & analysis ────────────────────────────────────────────────
async function handleFileUpload(file) {
  if (!file) return;
  const counterparty = document.getElementById('counterpartyInput')?.value.trim() || 'ApexCloud Infrastructure Inc.';
  const statusEl = document.getElementById('pipelineStatusText');
  const barEl = document.getElementById('pipelineProgressBar');
  const dotEl = statusEl?.previousElementSibling;

  setLoading(true);
  if (barEl) barEl.style.width = '15%';
  if (dotEl) dotEl.className = 'w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse';
  if (statusEl) statusEl.textContent = `Uploading '${file.name}'…`;
  renderPipelinePills(0);

  try {
    if (appState.backendConnected) {
      if (barEl) barEl.style.width = '40%';
      renderPipelinePills(2);
      if (statusEl) statusEl.textContent = 'Running 5-agent backend pipeline…';
      
      const reader = new FileReader();
      const base64Data = await new Promise((res, rej) => {
        reader.onload = e => res(e.target.result.split(',')[1]);
        reader.onerror = rej;
        reader.readAsDataURL(file);
      });

      if (barEl) barEl.style.width = '70%';
      renderPipelinePills(3);
      const out = await analyzeContract(file.name, counterparty, base64Data);
      if (barEl) barEl.style.width = '100%';
      appState.currentContractName = file.name;
      appState.currentCounterparty = counterparty;
      appState.report = out.report;
      appState.selectedClauseId = out.report.risk_ranked_clauses[0]?.clause_id || null;
      if (statusEl) {
        statusEl.textContent = `ReviewManagerAgent: Analyzed '${file.name}' (${out.report.executive_summary.total_clauses_analyzed} clauses validated)`;
      }
    } else {
      await fallbackClientAnalyze(file, counterparty);
    }
    renderAllViews();
    switchTab('redlines');
    persistState();
    showToast(`Analyzed '${file.name}' — switched to Clause & Redline Studio`);
  } catch (err) {
    if (appState.backendConnected) {
      await fallbackClientAnalyze(file, counterparty);
      renderAllViews();
      switchTab('redlines');
      showToast(`Analyzed '${file.name}' via client fallback`);
    } else {
      showToast(`Error: ${err.message}`);
    }
  } finally {
    setLoading(false);
    if (dotEl) dotEl.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500';
  }
}

async function fallbackClientAnalyze(file, counterparty) {
  const statusEl = document.getElementById('pipelineStatusText');
  const barEl = document.getElementById('pipelineProgressBar');
  const content = await file.text().catch(() => '');
  const printable = content.replace(/[^\x09\x0A\x0D\x20-\x7E]/g, ' ').replace(/\s{3,}/g, '\n');
  const textToAnalyze = printable.trim().length > 80 ? printable.trim() : SAMPLE_CONTRACTS.apex_msa.text;
  
  if (barEl) barEl.style.width = '60%';
  renderPipelinePills(2);
  if (statusEl) statusEl.textContent = 'Running client-side pipeline…';

  appState.currentContractName = file.name;
  appState.currentCounterparty = counterparty;
  appState.currentContractText = textToAnalyze;
  appState.report = await runLocalMultiAgentPipeline(file.name, textToAnalyze, counterparty);
  appState.selectedClauseId = appState.report.risk_ranked_clauses[0]?.clause_id || null;
  
  if (barEl) barEl.style.width = '100%';
  renderPipelinePills(5);
  if (statusEl) {
    statusEl.textContent = `ReviewManagerAgent: Analyzed '${file.name}' (${appState.report.executive_summary.total_clauses_analyzed} clauses validated)`;
  }
}

async function downloadPdfReport() {
  if (!appState.report) return;
  showToast('Generating & downloading PDF Contract Review Report…');
  if (appState.backendConnected) {
    try {
      const blob = await downloadPdfFromServer(appState.report);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(appState.report.contract_filename || 'Contract').replace(/\.[^.]+$/, '')}_Risk_Review_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      return;
    } catch (e) {
      // Fall through to browser print
    }
  }
  renderPrintableReport();
  setTimeout(() => window.print(), 200);
}

// ─── Drag and drop ─────────────────────────────────────────────────────────
function setupDragAndDrop() {
  const zone = document.getElementById('dropZone');
  if (!zone) return;
  ['dragenter', 'dragover'].forEach(name => {
    zone.addEventListener(name, e => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add('drag-over');
    });
  });
  ['dragleave', 'drop'].forEach(name => {
    zone.addEventListener(name, e => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('drag-over');
    });
  });
  zone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  });
}

// ─── Boot ──────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  // Apply persisted dark mode
  applyDarkMode(appState.darkMode);

  // Apply persisted counterparty
  const cpInput = document.getElementById('counterpartyInput');
  if (cpInput && appState.currentCounterparty) cpInput.value = appState.currentCounterparty;

  // Initial render with fallback data
  appState.report = await runLocalMultiAgentPipeline(
    appState.currentContractName,
    appState.currentContractText,
    appState.currentCounterparty
  );
  appState.selectedClauseId = appState.report.risk_ranked_clauses[0]?.clause_id || null;
  renderAllViews();
  
  // Restore persisted tab
  switchTab(appState.activeTab || 'dashboard');

  // Try live backend
  try {
    const data = await fetchInitialData();
    appState.backendConnected = true;
    appState.report = data.report;
    if (data.evaluation) appState.evaluation = data.evaluation;
    appState.selectedClauseId = data.report.risk_ranked_clauses[0]?.clause_id || null;
    const badge = document.getElementById('backendConnectionBadge');
    if (badge) {
      badge.textContent = '● Python Backend Connected';
      badge.className = 'text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 font-semibold';
    }
    renderAllViews();
  } catch (err) {
    appState.backendConnected = false;
  }

  // Nav tabs
  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
      persistState();
    });
  });

  // Dark mode toggle
  document.getElementById('btnDarkMode')?.addEventListener('click', () => {
    applyDarkMode(!appState.darkMode);
  });

  // Clause inspection (delegated)
  document.body.addEventListener('click', e => {
    const inspectBtn = e.target.closest('[data-inspect-clause]');
    if (inspectBtn) {
      appState.selectedClauseId = inspectBtn.getAttribute('data-inspect-clause');
      const flaggedCheck = document.getElementById('toggleFlaggedOnly');
      if (flaggedCheck) flaggedCheck.checked = false;
      switchTab('redlines');
      renderRedlineStudio();
      return;
    }
    const selectBtn = e.target.closest('[data-select-clause]');
    if (selectBtn) {
      appState.selectedClauseId = selectBtn.getAttribute('data-select-clause');
      renderRedlineStudio();
    }
  });

  // File upload
  setupDragAndDrop();
  document.getElementById('quickPdfUploadInput')?.addEventListener('change', ev => {
    if (ev.target.files.length) handleFileUpload(ev.target.files[0]);
  });

  // Check Clauses button
  document.getElementById('btnAnalyzeCurrent')?.addEventListener('click', async () => {
    const fileInput = document.getElementById('quickPdfUploadInput');
    if (fileInput?.files.length) {
      await handleFileUpload(fileInput.files[0]);
    } else {
      const cp = document.getElementById('counterpartyInput')?.value.trim() || 'ApexCloud Infrastructure Inc.';
      appState.currentCounterparty = cp;
      setLoading(true);
      appState.report = await runLocalMultiAgentPipeline(appState.currentContractName, appState.currentContractText, cp);
      setLoading(false);
      renderAllViews();
      switchTab('redlines');
      persistState();
      showToast(`Re-analyzed '${appState.currentContractName}' for '${cp}'`);
    }
  });

  // Sample presets
  document.querySelectorAll('.sample-preset-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const key = btn.getAttribute('data-sample');
      const sample = SAMPLE_CONTRACTS[key];
      if (!sample) return;
      const cpInput = document.getElementById('counterpartyInput');
      if (cpInput) cpInput.value = sample.counterparty;
      appState.currentContractName = sample.filename;
      appState.currentCounterparty = sample.counterparty;
      appState.currentContractText = sample.text;
      setLoading(true);
      appState.report = await runLocalMultiAgentPipeline(sample.filename, sample.text, sample.counterparty);
      appState.selectedClauseId = appState.report.risk_ranked_clauses[0]?.clause_id || null;
      setLoading(false);
      renderAllViews();
      switchTab('redlines');
      persistState();
      showToast(`Loaded & analyzed '${sample.filename}'`);
    });
  });

  // Search & filter listeners
  document.getElementById('clauseSearchInput')?.addEventListener('input', renderSharedClauseTable);
  document.getElementById('severityFilterSelect')?.addEventListener('change', renderSharedClauseTable);
  document.getElementById('toggleFlaggedOnly')?.addEventListener('change', renderRedlineStudio);
  document.getElementById('studioSearchInput')?.addEventListener('input', renderRedlineStudio);
  document.getElementById('playbookSearchInput')?.addEventListener('input', renderPlaybooksAndTelemetryView);

  // PDF download
  document.getElementById('btnDownloadPdfReport')?.addEventListener('click', downloadPdfReport);

  // Keyboard navigation for tabs
  document.querySelector('[role="tablist"]')?.addEventListener('keydown', e => {
    const tabs = [...document.querySelectorAll('.nav-tab-btn')];
    const idx = tabs.findIndex(t => t === document.activeElement);
    if (e.key === 'ArrowRight' && idx < tabs.length - 1) {
      tabs[idx + 1].focus();
    } else if (e.key === 'ArrowLeft' && idx > 0) {
      tabs[idx - 1].focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      tabs[idx]?.click();
    }
  });
});
