// utils/clipboard.js — Cross-browser clipboard helper

/**
 * Copy text to the system clipboard.
 * Tries the modern Clipboard API first; falls back to execCommand for older browsers.
 * @param {string} text - The text to copy.
 * @returns {Promise<void>}
 */
export async function copyToClipboard(text) {
  if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch (_) {
      // fall through to execCommand fallback
    }
  }

  // execCommand fallback (deprecated but widely supported)
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0;';
  document.body.appendChild(textarea);
  textarea.select();
  textarea.setSelectionRange(0, textarea.value.length); // iOS support
  document.execCommand('copy');
  document.body.removeChild(textarea);
}
