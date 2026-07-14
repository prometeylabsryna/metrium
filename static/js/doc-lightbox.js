'use strict';

(function initDocLightbox() {
  var triggers = document.querySelectorAll('[data-doc-lightbox]');
  if (!triggers.length) return;

  var overlay = null;
  var imgEl = null;
  var closeBtn = null;
  var prevBtn = null;
  var nextBtn = null;
  var lastFocus = null;
  var scrollY = 0;
  var isOpen = false;
  var gallery = [];
  var currentIndex = 0;

  function build() {
    if (overlay) return;

    overlay = document.createElement('div');
    overlay.className = 'doc-lightbox';
    overlay.setAttribute('hidden', '');
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Перегляд зображення');

    closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'doc-lightbox__close';
    closeBtn.setAttribute('aria-label', 'Закрити');
    closeBtn.innerHTML = '&times;';

    prevBtn = document.createElement('button');
    prevBtn.type = 'button';
    prevBtn.className = 'doc-lightbox__nav doc-lightbox__nav--prev';
    prevBtn.setAttribute('aria-label', 'Попереднє фото');
    prevBtn.innerHTML = '&#10094;';
    prevBtn.hidden = true;

    nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.className = 'doc-lightbox__nav doc-lightbox__nav--next';
    nextBtn.setAttribute('aria-label', 'Наступне фото');
    nextBtn.innerHTML = '&#10095;';
    nextBtn.hidden = true;

    var figure = document.createElement('div');
    figure.className = 'doc-lightbox__figure';

    imgEl = document.createElement('img');
    imgEl.className = 'doc-lightbox__img';
    imgEl.alt = '';

    figure.appendChild(imgEl);
    overlay.appendChild(closeBtn);
    overlay.appendChild(prevBtn);
    overlay.appendChild(nextBtn);
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
    prevBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      showRelative(-1);
    });
    nextBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      showRelative(1);
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

  function isCloneTrigger(el) {
    return !!(el.closest('[data-clone]') || el.closest('[aria-hidden="true"]'));
  }

  function collectGallery(trigger) {
    var group = trigger.getAttribute('data-lightbox-group');
    if (!group) return [trigger];

    var nodes = document.querySelectorAll(
      '[data-doc-lightbox][data-lightbox-group="' + group + '"]'
    );
    var items = [];
    var seen = {};

    nodes.forEach(function (el) {
      if (isCloneTrigger(el)) return;
      var src = el.getAttribute('href');
      if (!src || seen[src]) return;
      seen[src] = true;
      items.push(el);
    });

    return items.length ? items : [trigger];
  }

  function updateNav() {
    var multi = gallery.length > 1;
    prevBtn.hidden = !multi;
    nextBtn.hidden = !multi;
    overlay.classList.toggle('doc-lightbox--gallery', multi);
  }

  function showAt(index) {
    if (!gallery.length) return;
    currentIndex = (index + gallery.length) % gallery.length;
    var item = gallery[currentIndex];
    var src = item.getAttribute('href');
    var img = item.querySelector('img');
    imgEl.onload = function () {
      fitMobileImage();
    };
    imgEl.src = src;
    imgEl.alt = img ? (img.getAttribute('alt') || '') : '';
    if (imgEl.complete && imgEl.naturalWidth) fitMobileImage();
    updateNav();
  }

  function isMobileViewport() {
    return window.matchMedia('(max-width: 767px)').matches;
  }

  function fitMobileImage() {
    if (!overlay || !imgEl) return;
    if (!isMobileViewport() || !imgEl.naturalWidth || !imgEl.naturalHeight) {
      overlay.classList.remove('doc-lightbox--cover');
      return;
    }
    var viewRatio = overlay.clientWidth / Math.max(overlay.clientHeight, 1);
    var imgRatio = imgEl.naturalWidth / imgEl.naturalHeight;
    // Широкі (landscape) кадри на портреті — як звичайні фото: cover на весь екран
    overlay.classList.toggle('doc-lightbox--cover', imgRatio > viewRatio);
  }

  function showRelative(delta) {
    if (gallery.length < 2) return;
    showAt(currentIndex + delta);
  }

  function open(trigger) {
    build();
    lastFocus = document.activeElement;
    gallery = collectGallery(trigger);
    var src = trigger.getAttribute('href');
    currentIndex = 0;
    for (var i = 0; i < gallery.length; i++) {
      if (gallery[i].getAttribute('href') === src) {
        currentIndex = i;
        break;
      }
    }
    showAt(currentIndex);
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
    gallery = [];
    currentIndex = 0;
    if (overlay) overlay.classList.remove('doc-lightbox--cover');
    updateNav();
    unlockScroll();
    focusEl(lastFocus);
    window.scrollTo(0, scrollY);
  }

  triggers.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var src = link.getAttribute('href');
      if (!src) return;
      e.preventDefault();
      open(link);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (!isOpen) return;
    if (e.key === 'Escape') {
      close();
      return;
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      showRelative(-1);
      return;
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      showRelative(1);
    }
  });

  window.addEventListener('resize', function () {
    if (isOpen) fitMobileImage();
  }, { passive: true });
})();
