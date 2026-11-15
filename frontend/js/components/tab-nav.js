import { appState } from '../state.js';

export function switchTab(tabId) {
  const cleanTab = tabId.replace(/^view-/, '');
  appState.activeTab = cleanTab;
  const targetId = `view-${cleanTab}`;

  const allViews = document.querySelectorAll('.tab-view');
  allViews.forEach(el => {
    if (el.id !== targetId) {
      el.classList.remove('active');
      el.classList.add('hidden');
    }
  });

  const target = document.getElementById(targetId);
  if (target) {
    target.classList.remove('hidden');
    requestAnimationFrame(() => target.classList.add('active'));
  }

  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    const btnTab = btn.getAttribute('data-tab') || btn.dataset.tab;
    const isSelected = btnTab === cleanTab;
    btn.setAttribute('aria-selected', isSelected ? 'true' : 'false');
    if (isSelected) {
      btn.classList.remove('text-slate-300', 'hover:text-white');
      btn.classList.add('bg-indigo-600', 'text-white');
    } else {
      btn.classList.remove('bg-indigo-600', 'text-white');
      btn.classList.add('text-slate-300', 'hover:text-white');
    }
  });

  try {
    localStorage.setItem('lexguard_active_tab', cleanTab);
  } catch {}
}
