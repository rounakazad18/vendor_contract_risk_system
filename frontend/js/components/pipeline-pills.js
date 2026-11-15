export function renderPipelinePills(activeStageIdx = 5) {
  const container = document.getElementById('agentStepPills');
  if (!container) return;

  const stages = [
    { name: '1. ClauseSplitter',   role: 'PDF/DOCX/TXT Split' },
    { name: '2. PlaybookRetrieval', role: 'RAG Vector Lookup' },
    { name: '3. RiskScorer',       role: '@kernel_function Score' },
    { name: '4. RedlineDrafter',   role: 'Playbook + Memory' },
    { name: '5. ReviewManager',    role: 'Validation & Report' },
  ];

  container.innerHTML = stages.map((stage, idx) => {
    const done = idx < activeStageIdx;
    const pillClass = done
      ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900 pipeline-pill-done'
      : 'bg-slate-50 border-slate-200 text-slate-400';
    const delayStyle = done ? ` style="animation-delay:${idx * 0.08}s"` : '';
    const icon = done ? '✓' : '⋯';

    return `
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg border ${pillClass} text-sm"${delayStyle}>
        <div class="font-bold">${stage.name}</div>
        <div class="text-[11px] opacity-80">${stage.role}</div>
        <span>${icon}</span>
      </div>
    `;
  }).join('');
}
