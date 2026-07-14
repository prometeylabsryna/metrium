'use strict';

(function initDocLightbox() {
  var triggers = document.querySelectorAll('[data-doc-lightbox]');
  if (!triggers.length) return;

  var overlay = null;
  var imgEl = null;
  var closeBtn = null;
  var lastFocus = null;
  var scrollY = 0;
  var isOpen = false;

  function build() {
    if (overlay) return;

    overlay = document.createElement('div');
    overlay.className = 'doc-lightbox';
    overlay.setAttribute('hidden', '');
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Зразок документа');

    closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'doc-lightbox__close';
    closeBtn.setAttribute('aria-label', 'Закрити');
    closeBtn.innerHTML = '&times;';

    var figure = document.createElement('div');
    figure.className = 'doc-lightbox__figure';

    imgEl = document.createElement('img');
    imgEl.className = 'doc-lightbox__img';
    imgEl.alt = '';

    figure.appendChild(imgEl);
    overlay.appendChild(closeBtn);
    overlay.appendChild(figure);
    document.body.appendChild(overlay);

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay || e.target === figure) close();
    });
    closeBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      close();
    });
  }

  function onTouchMove(e) {
    if (!isOpen) return;
    if (overlay && overlay.contains(e.target)) return;
    e.preventDefault();
  }

  function lockScroll() {
    scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    document.documentElement.classList.add('doc-lightbox-lock');
    document.body.classList.add('body-lock', 'doc-lightbox-lock');
    document.addEventListener('touchmove', onTouchMove, { passive: false });
  }

  function unlockScroll() {
    document.documentElement.classList.remove('doc-lightbox-lock');
    document.body.classList.remove('body-lock', 'doc-lightbox-lock');
    document.removeEventListener('touchmove', onTouchMove);
    window.scrollTo(0, scrollY);
  }

  function focusEl(el) {
    if (!el || typeof el.focus !== 'function') return;
    try {
      el.focus({ preventScroll: true });
    } catch (err) {
      el.focus();
      window.scrollTo(0, scrollY);
    }
  }

  function open(src, alt) {
    build();
    lastFocus = document.activeElement;
    imgEl.src = src;
    imgEl.alt = alt || '';
    overlay.removeAttribute('hidden');
    isOpen = true;
    lockScroll();
    focusEl(closeBtn);
  }

  function close() {
    if (!isOpen || !overlay || overlay.hasAttribute('hidden')) return;
    isOpen = false;
    overlay.setAttribute('hidden', '');
    imgEl.removeAttribute('src');
    unlockScroll();
    focusEl(lastFocus);
    window.scrollTo(0, scrollY);
  }

  triggers.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var src = link.getAttribute('href');
      if (!src) return;
      e.preventDefault();
      var img = link.querySelector('img');
      open(src, img ? img.getAttribute('alt') : '');
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });
})();
