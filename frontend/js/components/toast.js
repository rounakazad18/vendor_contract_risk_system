export function showToast(msg, type = 'info') {
  const el = document.getElementById('toastNotification');
  const txt = document.getElementById('toastMessage');
  if (!el || !txt) return;
  txt.textContent = msg;
  el.classList.remove('hidden', 'toast-exit');
  el.classList.add('toast-enter');
  clearTimeout(el._toastTimer);
  el._toastTimer = setTimeout(() => {
    el.classList.remove('toast-enter');
    el.classList.add('toast-exit');
    setTimeout(() => el.classList.add('hidden'), 300);
  }, 3200);
}
