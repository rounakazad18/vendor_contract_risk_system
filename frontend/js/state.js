import { FALLBACK_PLAYBOOK_CHUNKS } from './data/playbooks.js';
import { SAMPLE_CONTRACTS } from './data/contracts.js';
import { CA2_10_CLAUSE_BENCHMARK } from './data/benchmark.js';

const STORAGE_KEY = 'lexguard_state_v1';

function loadPersistedState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch { return {}; }
}

function savePersistedState(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      acceptedRedlines: data.acceptedRedlines,
      activeTab: data.activeTab,
      lastCounterparty: data.currentCounterparty,
      darkMode: data.darkMode,
    }));
  } catch {}
}

const persisted = loadPersistedState();

export const appState = {
  activeTab: persisted.activeTab || 'dashboard',
  backendConnected: false,
  darkMode: persisted.darkMode || false,
  playbookChunks: [...FALLBACK_PLAYBOOK_CHUNKS],
  currentContractName: SAMPLE_CONTRACTS.apex_msa.filename,
  currentCounterparty: persisted.lastCounterparty || SAMPLE_CONTRACTS.apex_msa.counterparty,
  currentContractText: SAMPLE_CONTRACTS.apex_msa.text,
  report: null,
  isLoading: false,
  loadingError: null,
  evaluation: {
    total_clauses: 10,
    agreed_count: 10,
    agreement_percentage: 100.0,
    rows: CA2_10_CLAUSE_BENCHMARK,
  },
  selectedClauseId: null,
  acceptedRedlines: persisted.acceptedRedlines || {},
  severityChart: null,
  clauseScoreChart: null,
};

export function persistState() {
  savePersistedState(appState);
}
