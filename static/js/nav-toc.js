'use strict';

/* Page Table of Contents — auto-builds from h2 inside main */
(function initPageToc() {
  var container = document.getElementById('pageToc');
  if (!container || container.dataset.tocInit === '1') return;
  container.dataset.tocInit = '1';

  var toggle = container.querySelector('.page-toc__toggle');
  var list   = container.querySelector('.page-toc__list');
  if (!toggle || !list) return;

  toggle.setAttribute('type', 'button');

  /* Gather all H2 headings that are inside <main> but outside the TOC block */
  var headings = document.querySelectorAll('main h2');
  if (headings.length < 2) {
    container.classList.add('is-hidden');
    return;
  }

  headings.forEach(function (h, i) {
    if (!h.id) {
      h.id = 'toc-section-' + i;
    }
    var li = document.createElement('li');
    var a  = document.createElement('a');
    a.href        = '#' + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    list.appendChild(li);
  });

  toggle.addEventListener('click', function () {
    container.classList.toggle('open');
    var isOpen = container.classList.contains('open');
    toggle.setAttribute('aria-expanded', String(isOpen));
  });

  /* Smooth-scroll offset for sticky header */
  list.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      container.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      var headerH = document.getElementById('siteHeader')
        ? document.getElementById('siteHeader').offsetHeight + 16
        : 96;
      var top = target.getBoundingClientRect().top + window.scrollY - headerH;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });
})();
