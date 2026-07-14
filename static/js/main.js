'use strict';

/* =============================================
   MAIN.JS — vanilla JS, no jQuery dependency
   ============================================= */

/* ----- Scroll progress bar ----- */
(function initScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  if (!bar) return;
  function update() {
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = total > 0 ? (scrolled / total * 100) + '%' : '0%';
  }
  window.addEventListener('scroll', update, { passive: true });
})();

/* ----- Sticky header compact mode ----- */
(function initStickyHeader() {
  const header = document.getElementById('siteHeader');
  if (!header) return;
  let ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        header.classList.toggle('compact', window.scrollY > 80);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
})();

/* ----- Mobile menu ----- */
(function initMobileMenu() {
  const menu    = document.getElementById('mobMnu');
  const open    = document.getElementById('mobMenuOpen');
  const close   = document.getElementById('mobMenuClose');
  const backdrop = document.getElementById('mobMenuBackdrop');
  const icon    = document.getElementById('burgerIcon');
  if (!menu) return;

  const iconOpen  = icon ? icon.getAttribute('src') : '';
  const iconClose = icon ? (icon.dataset.closeSrc || iconOpen) : '';

  function openMenu() {
    menu.classList.add('activeMnu');
    backdrop.classList.add('active');
    document.body.classList.add('body-lock');
    if (open) open.setAttribute('aria-expanded', 'true');
    if (icon && iconClose) icon.src = iconClose;
  }
  function closeMenu() {
    menu.classList.remove('activeMnu');
    backdrop.classList.remove('active');
    document.body.classList.remove('body-lock');
    if (open) open.setAttribute('aria-expanded', 'false');
    if (icon && iconOpen) icon.src = iconOpen;
  }

  if (open) open.addEventListener('click', function () {
    menu.classList.contains('activeMnu') ? closeMenu() : openMenu();
  });
  if (close) close.addEventListener('click', closeMenu);
  if (backdrop) backdrop.addEventListener('click', function (e) {
    if (e.target === backdrop) closeMenu();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });

  // Close menu on nav link click
  menu.querySelectorAll('.mob-main-nav a').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });

  // Mobile lang switcher — ?hl= bypasses cached legacy 301 on /ru/
  menu.querySelectorAll('.mob-lang-row .lang-switcher a').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var href = link.getAttribute('href');
      if (!href || link.closest('.current-lang')) return;
      e.preventDefault();
      window.location.assign(href);
    });
  });
})();

/* ----- Clean ?hl= from URL after language switch (replaceState, no reload) ----- */
(function initCleanLangParam() {
  var params = new URLSearchParams(window.location.search);
  if (!params.has('hl')) return;
  params.delete('hl');
  var clean = window.location.pathname + (params.toString() ? '?' + params.toString() : '') + window.location.hash;
  window.history.replaceState(null, '', clean);
})();

/* ----- Scroll reveal (IntersectionObserver) ----- */
(function initReveal() {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.reveal-up,.reveal-left,.reveal-right').forEach(function (el) {
      el.classList.add('revealed');
    });
    return;
  }
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal-up,.reveal-left,.reveal-right').forEach(function (el) {
    observer.observe(el);
  });
})();

/* ----- Accordion (FAQ, docs mobile tabs) ----- */
(function initAccordion() {
  var roots = document.querySelectorAll('#accordion, #docsAccordion, .mobSServiseTabs');
  roots.forEach(function (root) {
    root.querySelectorAll('.card-header[data-target]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = this.getAttribute('data-target');
        var panel = document.getElementById(targetId);
        var isOpen = this.getAttribute('aria-expanded') === 'true';

        root.querySelectorAll('.card-header').forEach(function (b) {
          b.setAttribute('aria-expanded', 'false');
        });
        root.querySelectorAll('.collapse').forEach(function (p) {
          p.classList.remove('open');
          p.style.maxHeight = '';
        });

        if (!isOpen && panel) {
          this.setAttribute('aria-expanded', 'true');
          panel.classList.add('open');
          panel.style.maxHeight = panel.scrollHeight + 'px';
        }
      });
    });
  });
})();

/* ----- Desktop tabs (cats.php, service pages) ----- */
(function initDocsTabs() {
  document.querySelectorAll('.docs-section, .service-tabs, .service-tabs-desktop').forEach(function (section) {
    var btns = section.querySelectorAll('.servBtnItem[data-target]');
    if (!btns.length) return;

    btns.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var targetId = btn.getAttribute('data-target');
        var target = document.getElementById(targetId);
        if (!target) return;

        btns.forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        section.querySelectorAll('.servList').forEach(function (p) {
          p.classList.remove('active');
        });

        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        target.classList.add('active');
      });
    });
  });
})();

/* ----- Reviews slider ----- */
(function initReviews() {
  const slider  = document.getElementById('reviewsSlider');
  const track   = document.getElementById('reviewsTrack');
  const dotsBox = document.getElementById('reviewsDots');
  const prevBtn = document.getElementById('revPrev');
  const nextBtn = document.getElementById('revNext');
  if (!slider || !track) return;

  const items = track.querySelectorAll('.rev-item');
  let current = 0;
  let visible = getVisible();
  let total   = Math.ceil(items.length / visible);
  let startX  = 0;
  let isDragging = false;

  function getVisible() {
    if (window.innerWidth >= 1280) return 3;
    if (window.innerWidth >= 768)  return 2;
    return 1;
  }

  function buildDots() {
    if (!dotsBox) return;
    dotsBox.innerHTML = '';
    for (let i = 0; i < total; i++) {
      const dot = document.createElement('button');
      dot.className = 'rev-dot' + (i === current ? ' active' : '');
      dot.setAttribute('aria-label', 'Слайд ' + (i + 1));
      dot.addEventListener('click', function () { goTo(i); });
      dotsBox.appendChild(dot);
    }
  }

  function goTo(idx) {
    current = Math.max(0, Math.min(idx, total - 1));
    const itemStep = items[0].offsetWidth + 16;
    track.style.transform = 'translateX(-' + (current * visible * itemStep) + 'px)';
    dotsBox && dotsBox.querySelectorAll('.rev-dot').forEach(function (d, i) {
      d.classList.toggle('active', i === current);
    });
  }

  function recalc() {
    visible = getVisible();
    total   = Math.ceil(items.length / visible);
    if (current >= total) current = total - 1;
    buildDots();
    goTo(current);
  }

  if (prevBtn) prevBtn.addEventListener('click', function () { goTo(current - 1); });
  if (nextBtn) nextBtn.addEventListener('click', function () { goTo(current + 1); });

  // Touch / swipe support
  track.addEventListener('touchstart', function (e) {
    startX = e.touches[0].clientX;
    isDragging = true;
  }, { passive: true });
  track.addEventListener('touchend', function (e) {
    if (!isDragging) return;
    const diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) { diff > 0 ? goTo(current + 1) : goTo(current - 1); }
    isDragging = false;
  }, { passive: true });

  // Auto-advance
  let autoTimer = setInterval(function () { goTo((current + 1) % total); }, 6000);
  slider.addEventListener('mouseenter', function () { clearInterval(autoTimer); });
  slider.addEventListener('mouseleave', function () {
    autoTimer = setInterval(function () { goTo((current + 1) % total); }, 6000);
  });

  window.addEventListener('resize', recalc, { passive: true });
  recalc();
})();

/* ----- Toast notification ----- */
function showToast() {
  const wrap = document.getElementById('toastWrap');
  if (!wrap) return;
  wrap.classList.add('show');
  setTimeout(function () { wrap.classList.remove('show'); }, 5000);
}
(function () {
  const closeBtn = document.getElementById('toastClose');
  if (closeBtn) closeBtn.addEventListener('click', function () {
    document.getElementById('toastWrap').classList.remove('show');
  });
})();

/* ----- Form validation helper ----- */
function validatePhone(val) {
  return val.replace(/\D/g, '').length >= 9;
}

function getCsrf() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const cookie = document.cookie.split(';').find(function (c) { return c.trim().startsWith('csrftoken='); });
  return cookie ? cookie.split('=')[1] : '';
}

function handleFormSubmit(form, callback) {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const input   = form.querySelector('[type="tel"]');
    const wrap    = input ? input.closest('.form-field-wrap') : null;
    const errEl   = form.querySelector('.banerForm__error, .field-error');

    if (input && !validatePhone(input.value)) {
      if (wrap)  wrap.classList.add('has-error');
      if (errEl) errEl.classList.add('visible');
      input.focus();
      return;
    }
    if (wrap)  wrap.classList.remove('has-error');
    if (errEl) errEl.classList.remove('visible');

    const btn = form.querySelector('.btn-submit');
    if (btn) btn.classList.add('loading');

    const action  = form.dataset.action || '/api/leads/phone/';
    const channel = form.dataset.channel || '';
    const data    = new FormData(form);
    if (channel && !data.get('channel')) data.append('channel', channel);
    if (!data.get('loc')) data.append('loc', document.title);

    fetch(action, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
      body: data,
    })
      .then(function (res) { return res.json(); })
      .then(function (json) {
        if (btn) btn.classList.remove('loading');
        if (json.ok) {
          form.reset();
          showToast();
          if (typeof callback === 'function') callback();
        } else {
          if (wrap)  wrap.classList.add('has-error');
          if (errEl) errEl.classList.add('visible');
        }
      })
      .catch(function () {
        if (btn) btn.classList.remove('loading');
        showToast();
        if (typeof callback === 'function') callback();
      });
  });

  const phoneInput = form.querySelector('[type="tel"]');
  if (phoneInput) {
    phoneInput.addEventListener('input', function () {
      const wrap  = this.closest('.form-field-wrap');
      const errEl = form.querySelector('.banerForm__error, .field-error');
      if (wrap)  wrap.classList.remove('has-error');
      if (errEl) errEl.classList.remove('visible');
    });
  }
}

/* ----- Init forms ----- */
(function initForms() {
  const bound = new WeakSet();

  function bindForm(form, callback) {
    if (!form || bound.has(form)) return;
    bound.add(form);
    handleFormSubmit(form, callback);
  }

  document.querySelectorAll('form[data-action]').forEach(function (form) {
    let callback;
    if (form.id === 'popupTelForm') {
      callback = function () { closeModal(); };
    } else if (form.id === 'calc-form-data') {
      callback = function () { form.classList.remove('active'); };
    }
    bindForm(form, callback);
  });

  document.querySelectorAll('form[data-lead-form]').forEach(function (form) {
    if (form.dataset.action) return;
    var kind = form.getAttribute('data-lead-form');
    form.dataset.action = kind === 'calculator'
      ? '/api/leads/calculator/'
      : '/api/leads/phone/';
    var callback;
    if (form.id === 'calc-form-data') {
      callback = function () { form.classList.remove('active'); };
    }
    bindForm(form, callback);
  });

  bindForm(document.getElementById('banerFormTop'));
})();

/* ----- Modal (popup) ----- */
function openModal() {
  const modal = document.getElementById('popupTel');
  if (!modal) return;
  modal.removeAttribute('hidden');
  document.body.classList.add('body-lock');
  const input = modal.querySelector('input');
  if (input) setTimeout(function () { input.focus(); }, 100);
}
function closeModal() {
  const modal = document.getElementById('popupTel');
  if (!modal) return;
  modal.setAttribute('hidden', '');
  document.body.classList.remove('body-lock');
}

(function initModal() {
  const closeBtn = document.getElementById('popupTelClose');
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  const overlay = document.getElementById('popupTel');
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  // Trigger popup from CTA links
  document.querySelectorAll('.open-popup-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      openModal();
    });
  });
})();

/* ----- Scroll to top ----- */
(function initScrollTop() {
  const btn = document.getElementById('scrollTopBtn');
  if (!btn) return;

  window.addEventListener('scroll', function () {
    if (window.scrollY > 400) {
      btn.removeAttribute('hidden');
    } else {
      btn.setAttribute('hidden', '');
    }
  }, { passive: true });

  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

/* ----- Smooth scroll for anchor links ----- */
(function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (!href || href === '#') return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      const headerH = document.getElementById('siteHeader')
        ? document.getElementById('siteHeader').offsetHeight
        : 80;
      const top = target.getBoundingClientRect().top + window.scrollY - headerH - 16;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });
})();

/* ----- Phone input: auto-format ----- */
(function initPhoneMask() {
  document.querySelectorAll('input[type="tel"]').forEach(function (input) {
    input.addEventListener('input', function () {
      let val = this.value.replace(/\D/g, '');
      if (val.startsWith('380')) val = val.slice(3);
      if (val.startsWith('0')) val = val.slice(1);
      this.value = val.length ? '0' + val.slice(0, 9) : '';
    });
  });
})();

/* ----- Contacts: location switcher (Google Maps embed) ----- */
(function initLocationLinks() {
  var links = document.querySelectorAll('.locationLink');
  var frame = document.getElementById('contactMapFrame');
  if (!links.length || !frame) return;

  function normalizeDecimal(value) {
    return String(value).replace(',', '.');
  }

  function parseCoords(link) {
    if (link.dataset.lat && link.dataset.lng) {
      return {
        lat: parseFloat(normalizeDecimal(link.dataset.lat)),
        lng: parseFloat(normalizeDecimal(link.dataset.lng)),
      };
    }
    if (link.dataset.cordinates) {
      var match = String(link.dataset.cordinates).match(/^(-?\d+[.,]\d+),(-?\d+[.,]\d+)$/);
      if (match) {
        return {
          lat: parseFloat(normalizeDecimal(match[1])),
          lng: parseFloat(normalizeDecimal(match[2])),
        };
      }
    }
    return null;
  }

  function buildEmbedUrl(lat, lng) {
    return 'https://www.google.com/maps?q=' + lat + ',' + lng + '&hl=uk&z=16&output=embed';
  }

  links.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      links.forEach(function (l) {
        l.classList.remove('active');
      });
      this.classList.add('active');

      var coords = parseCoords(this);
      if (!coords || !coords.lat || !coords.lng) return;
      frame.src = buildEmbedUrl(coords.lat, coords.lng);
    });
  });
})();

/* ----- Mobile services submenu toggle ----- */
(function initMobServicesToggle() {
  var btn = document.getElementById('mobServicesToggle');
  var sub = document.getElementById('mobServicesSubmenu');
  if (!btn || !sub) return;

  btn.addEventListener('click', function () {
    var isOpen = sub.classList.toggle('open');
    btn.classList.toggle('active', isOpen);
    btn.setAttribute('aria-expanded', String(isOpen));
  });

  sub.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      sub.classList.remove('open');
      btn.classList.remove('active');
      btn.setAttribute('aria-expanded', 'false');
    });
  });
})();

/* ----- Mobile passport submenu toggle ----- */
(function initMobSubPassportToggle() {
  var btn = document.getElementById('mobSubPassportToggle');
  var sub = document.getElementById('mobSubPassportMenu');
  if (!btn || !sub) return;

  btn.addEventListener('click', function () {
    var isOpen = sub.classList.toggle('open');
    btn.classList.toggle('active', isOpen);
    btn.setAttribute('aria-expanded', String(isOpen));
  });

  sub.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      sub.classList.remove('open');
      btn.classList.remove('active');
      btn.setAttribute('aria-expanded', 'false');
    });
  });
})();

/* ----- Desktop nav dropdown keyboard/touch support ----- */
(function initNavDropdown() {
  var dropdowns = document.querySelectorAll('.has-dropdown');
  if (!dropdowns.length) return;

  /* CSS :hover handles desktop mouse — JS only handles touch + keyboard */

  dropdowns.forEach(function (item) {
    var dropdown = item.querySelector('.nav-dropdown');
    if (!dropdown) return;

    var trigger = item.querySelector('a');

    function openDrop() {
      item.classList.add('is-touch-open');
      trigger.setAttribute('aria-expanded', 'true');
    }
    function closeDrop() {
      item.classList.remove('is-touch-open');
      trigger.setAttribute('aria-expanded', 'false');
    }

    trigger.addEventListener('touchstart', function (e) {
      var isOpen = item.classList.contains('is-touch-open');
      if (!isOpen) {
        e.preventDefault();
        document.querySelectorAll('.has-dropdown.is-touch-open').forEach(function (el) {
          el.classList.remove('is-touch-open');
          var t = el.querySelector('a');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
        openDrop();
      }
    }, { passive: false });

    document.addEventListener('touchstart', function (e) {
      if (!item.contains(e.target)) { closeDrop(); }
    }, { passive: true });

    trigger.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        var isOpen = item.classList.contains('is-touch-open');
        if (isOpen) { closeDrop(); }
        else { openDrop(); }
      }
      if (e.key === 'Escape') {
        closeDrop();
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.has-dropdown.is-touch-open').forEach(function (el) {
        el.classList.remove('is-touch-open');
        var t = el.querySelector('a');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
      document.querySelectorAll('.has-sub-dropdown.is-sub-open').forEach(function (el) {
        el.classList.remove('is-sub-open');
      });
    }
  });
})();

/* ----- Nested sub-dropdown touch support (iPad / tablet) ----- */
(function initSubNavDropdown() {
  var subItems = document.querySelectorAll('.has-sub-dropdown');
  if (!subItems.length) return;

  subItems.forEach(function (item) {
    var trigger = item.querySelector(':scope > a');
    if (!trigger) return;

    function closeSub() {
      item.classList.remove('is-sub-open');
    }

    function closeAllSubs() {
      document.querySelectorAll('.has-sub-dropdown.is-sub-open').forEach(function (el) {
        el.classList.remove('is-sub-open');
      });
    }

    trigger.addEventListener('touchstart', function (e) {
      var isOpen = item.classList.contains('is-sub-open');
      if (!isOpen) {
        e.preventDefault();
        closeAllSubs();
        item.classList.add('is-sub-open');
      }
    }, { passive: false });

    document.addEventListener('touchstart', function (e) {
      if (!item.contains(e.target)) { closeSub(); }
    }, { passive: true });
  });
})();
