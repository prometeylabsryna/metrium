'use strict';

(function initDocLightbox() {
  var triggers = document.querySelectorAll('[data-doc-lightbox]');
  if (!triggers.length) return;

  var overlay = null;
  var imgEl = null;
  var closeBtn = null;
  var lastFocus = null;
  var scrollY = 0;

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
    closeBtn.addEventListener('click', close);
  }

  function lockScroll() {
    scrollY = window.scrollY || window.pageYOffset || 0;
    document.body.classList.add('body-lock');
    document.body.style.top = '-' + scrollY + 'px';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
  }

  function unlockScroll() {
    document.body.classList.remove('body-lock');
    document.body.style.top = '';
    document.body.style.position = '';
    document.body.style.width = '';
    window.scrollTo(0, scrollY);
  }

  function open(src, alt) {
    build();
    lastFocus = document.activeElement;
    imgEl.src = src;
    imgEl.alt = alt || '';
    overlay.removeAttribute('hidden');
    lockScroll();
    closeBtn.focus();
  }

  function close() {
    if (!overlay || overlay.hasAttribute('hidden')) return;
    overlay.setAttribute('hidden', '');
    imgEl.removeAttribute('src');
    unlockScroll();
    if (lastFocus && typeof lastFocus.focus === 'function') {
      lastFocus.focus();
    }
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
