import { postForm } from './utils.js';

function showThanks() {
  const popup = document.getElementById('thanck');
  if (popup) {
    popup.classList.add('active');
    popup.removeAttribute('hidden');
  }
}

function bindLeadForms() {
  document.querySelectorAll('[data-lead-form="phone"]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const btn = form.querySelector('[type="submit"]');
      if (btn) btn.disabled = true;
      try {
        await postForm('/api/leads/phone/', new FormData(form));
        form.reset();
        showThanks();
      } catch (err) {
        console.error(err);
      } finally {
        if (btn) btn.disabled = false;
      }
    });
  });

  document.querySelectorAll('[data-lead-form="calculator"]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const btn = form.querySelector('[type="submit"]');
      if (btn) btn.disabled = true;
      try {
        await postForm('/api/leads/calculator/', new FormData(form));
        showThanks();
      } catch (err) {
        console.error(err);
      } finally {
        if (btn) btn.disabled = false;
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', bindLeadForms);
