// utils/sanitize.js — HTML escaping utilities

/**
 * Escape a string for safe insertion into HTML.
 * Replaces &, <, >, ", and ' with their HTML entity equivalents.
 * @param {string} str
 * @returns {string}
 */
export function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** Alias for escapeHtml — shorthand used throughout the app. */
export const safe = escapeHtml;
