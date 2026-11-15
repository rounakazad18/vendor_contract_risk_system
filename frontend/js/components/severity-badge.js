import { escapeHtml } from '../utils/sanitize.js';

export function severityBadgeHtml(severity) {
  const styles = {
    'Critical': 'bg-rose-100 text-rose-800 border-rose-300 severity-critical-pulse',
    'High': 'bg-orange-100 text-orange-800 border-orange-300',
    'Medium': 'bg-amber-100 text-amber-800 border-amber-300',
    'Low': 'bg-sky-100 text-sky-800 border-sky-300',
    'No Risk': 'bg-emerald-100 text-emerald-800 border-emerald-300',
  };
  const cls = styles[severity] || styles['No Risk'];
  const safeSev = escapeHtml(severity);
  return `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${cls}">${safeSev}</span>`;
}
