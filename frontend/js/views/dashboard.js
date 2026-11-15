/**
 * views/dashboard.js
 * Dashboard view renderer — KPI cards, risk lists, negotiation priorities, charts.
 */

import { appState } from '../state.js';
import { severityBadgeHtml } from '../components/severity-badge.js';
import { escapeHtml } from '../utils/sanitize.js';

// ---------------------------------------------------------------------------
// Count-up animation helper
// ---------------------------------------------------------------------------
function animateCount(el, targetValue, duration = 600) {
  if (!el) return;
  const start = performance.now();
  const from = 0;
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (targetValue - from) * eased);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ---------------------------------------------------------------------------
// Dashboard view
// ---------------------------------------------------------------------------
export function renderDashboardView() {
  const rpt = appState.report;
  if (!rpt) return;
  const es = rpt.executive_summary;
  const fr = rpt.final_recommendations;

  document.getElementById('activeContractLabel').textContent = rpt.contract_filename;
  document.getElementById('summaryReportIdBadge').textContent = rpt.report_id;
  document.getElementById('dashboardContractTitle').textContent = rpt.contract_filename;
  document.getElementById('dashboardNarrative').textContent = es.overall_assessment_narrative;

  const recBadge = document.getElementById('approvalRecBadge');
  recBadge.textContent = fr.approval_recommendation;
  recBadge.className =
    'px-3 py-1 rounded-full text-sm font-bold border ' +
    (fr.approval_recommendation === 'Approve'
      ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
      : fr.approval_recommendation === 'Reject'
      ? 'bg-rose-100 text-rose-800 border-rose-300'
      : 'bg-amber-100 text-amber-800 border-amber-300');
  document.getElementById('approvalJustificationText').textContent = fr.approval_justification;

  // KPI numbers with count-up
  const kpiMap = {
    kpiCompositeScore: es.overall_contract_risk_score,
    kpiTotalClauses:   es.total_clauses_analyzed,
    kpiCriticalCount:  es.critical_count,
    kpiHighCount:      es.high_count,
    kpiMedLowCount:    es.medium_count + es.low_count,
    kpiNoRiskCount:    es.no_risk_count,
  };
  for (const [id, val] of Object.entries(kpiMap)) {
    animateCount(document.getElementById(id), val, 600);
  }
  document.getElementById('kpiCompositeLevel').textContent = es.overall_risk_level;
  document.getElementById('kpiFlaggedCount').textContent = `${es.flagged_clauses_count} Flagged for Redline`;

  // Top risks list (up to 4)
  const flagged = rpt.risk_ranked_clauses.filter(c => c.is_flagged);
  const topRisksEl = document.getElementById('topRisksList');
  if (flagged.length === 0) {
    topRisksEl.innerHTML = `<li class="p-3 rounded-lg bg-emerald-50 text-emerald-800 font-medium">No flagged risks detected. All clauses comply with internal playbooks.</li>`;
  } else {
    topRisksEl.innerHTML = flagged.slice(0, 4).map(c => {
      const heading      = escapeHtml(c.clause_heading);
      const clauseNum    = escapeHtml(String(c.clause_number));
      const clauseId     = escapeHtml(c.clause_id);
      const riskText     = escapeHtml((c.policy_violations && c.policy_violations[0]) || c.risk_explanation);
      return `
        <li class="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between gap-2">
          <div>
            <span class="font-bold text-slate-900">Clause ${clauseNum} (${heading}) — ${c.risk_score}/100:</span>
            <span class="text-slate-600 ml-1">${riskText}</span>
          </div>
          <button data-inspect-clause="${clauseId}" class="shrink-0 px-2.5 py-1 rounded bg-indigo-600 text-white font-semibold hover:bg-indigo-500">
            Inspect →
          </button>
        </li>
      `;
    }).join('');
  }

  // Negotiation priorities list (up to 4)
  const negEl = document.getElementById('negotiationPrioritiesList');
  if (flagged.length === 0) {
    negEl.innerHTML = `<li class="p-3 rounded-lg bg-emerald-50 text-emerald-800 font-medium list-none">Contract ready for execution without redlines.</li>`;
  } else {
    negEl.innerHTML = flagged.slice(0, 4).map(c => {
      const ref        = c.retrieved_playbook_references[0];
      const heading    = escapeHtml(c.clause_heading);
      const clauseNum  = escapeHtml(String(c.clause_number));
      const sectionRef = escapeHtml(ref ? ref.section_ref : 'Playbook');
      const fallback   = escapeHtml(ref ? ref.fallback_position : 'Escalate to Legal.');
      return `
        <li class="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
          <span class="font-bold text-slate-900">[Clause ${clauseNum} — ${heading}]</span>
          <span class="text-slate-600"> Enforce ${sectionRef} replacement wording. <strong>Fallback:</strong> ${fallback}</span>
        </li>
      `;
    }).join('');
  }

  renderCharts(rpt);
}

// ---------------------------------------------------------------------------
// Chart rendering (severity doughnut, clause score bar, radar)
// ---------------------------------------------------------------------------
export function renderCharts(rpt) {
  const es = rpt.executive_summary;
  const sevCanvas   = document.getElementById('severityChartCanvas');
  const barCanvas   = document.getElementById('clauseScoreChartCanvas');
  if (!sevCanvas || !barCanvas || typeof Chart === 'undefined') return;

  // Severity doughnut
  if (appState.severityChart) appState.severityChart.destroy();
  appState.severityChart = new Chart(sevCanvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Critical (80–100)', 'High (60–79)', 'Medium (40–59)', 'Low (20–39)', 'No Risk (0–19)'],
      datasets: [{
        data: [es.critical_count, es.high_count, es.medium_count, es.low_count, es.no_risk_count],
        backgroundColor: ['#E11D48', '#EA580C', '#D97706', '#0284C7', '#059669'],
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } }
      }
    }
  });

  // Clause score bar chart
  if (appState.clauseScoreChart) appState.clauseScoreChart.destroy();
  const sorted = [...rpt.risk_ranked_clauses];
  appState.clauseScoreChart = new Chart(barCanvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels: sorted.map(c => `Cl. ${c.clause_number}: ${c.clause_heading.substring(0, 22)}`),
      datasets: [{
        label: 'Risk Score (0–100)',
        data: sorted.map(c => c.risk_score),
        backgroundColor: sorted.map(c =>
          c.risk_score >= 80 ? '#E11D48' :
          c.risk_score >= 60 ? '#EA580C' :
          c.risk_score >= 40 ? '#D97706' :
          c.risk_score >= 20 ? '#0284C7' : '#059669'
        ),
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      scales: {
        x: { min: 0, max: 100, grid: { color: '#F1F5F9' } },
        y: { ticks: { font: { size: 10 } }, grid: { display: false } }
      },
      plugins: { legend: { display: false } }
    }
  });

  // Radar chart — 5 category risk totals
  const radarCanvas = document.getElementById('radarChartCanvas');
  if (!radarCanvas) return;

  if (appState.radarChart) appState.radarChart.destroy();

  const liabilityKw   = ['liability', 'limitation', 'consequential', 'damages', 'indemnif', 'cap'];
  const ipKw          = ['intellectual property', 'work product', 'deliverable', 'derivative', 'ownership', 'assign'];
  const privacyKw     = ['data privacy', 'data breach', 'security incident', 'ai', 'machine learning', 'subprocessor', 'audit'];
  const commercialKw  = ['fees', 'payment', 'invoic', 'price', 'renewal', 'terminate', 'term'];
  const governanceKw  = ['governing law', 'venue', 'dispute', 'arbitration', 'force majeure', 'business continuity'];

  function categoryScore(clauses, keywords) {
    return clauses.reduce((sum, c) => {
      const text = (c.clause_heading + ' ' + c.original_text).toLowerCase();
      const match = keywords.some(kw => text.includes(kw));
      return sum + (match ? c.risk_score : 0);
    }, 0);
  }

  const clauses = rpt.risk_ranked_clauses;
  const radarData = [
    categoryScore(clauses, liabilityKw),
    categoryScore(clauses, ipKw),
    categoryScore(clauses, privacyKw),
    categoryScore(clauses, commercialKw),
    categoryScore(clauses, governanceKw)
  ];

  appState.radarChart = new Chart(radarCanvas.getContext('2d'), {
    type: 'radar',
    data: {
      labels: ['Liability', 'IP', 'Data Privacy', 'Commercial', 'Governance'],
      datasets: [{
        label: 'Category Risk',
        data: radarData,
        backgroundColor: 'rgba(79, 70, 229, 0.15)',
        borderColor: '#4F46E5',
        pointBackgroundColor: '#4F46E5',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      scales: {
        r: {
          beginAtZero: true,
          ticks: { font: { size: 10 } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
