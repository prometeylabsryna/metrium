'use strict';

/**
 * Foto Marquee — безперервна бігова стрічка фото робіт.
 * Швидкість задається в px/сек через data-marquee-speed.
 */
(function initFotoMarquee() {
  var DEFAULT_SPEED = 45;
  var MIN_COPIES = 3;

  function initMarquee(marquee) {
    var track = marquee.querySelector('.foto-marquee__track');
    var group = marquee.querySelector('.foto-marquee__group');
    if (!track || !group) return;

    var speed = parseFloat(marquee.dataset.marqueeSpeed) || DEFAULT_SPEED;
    var mobileSpeed = parseFloat(marquee.dataset.marqueeSpeedMobile) || null;
    var resizeTimer = null;

    track.querySelectorAll('.foto-marquee__group[data-clone]').forEach(function (el) {
      el.remove();
    });

    function buildAndAnimate() {
      track.style.setProperty('animation', 'none');

      track.querySelectorAll('.foto-marquee__group[data-clone]').forEach(function (el) {
        el.remove();
      });

      var setWidth = group.offsetWidth;
      if (!setWidth) return;

      var copies = Math.max(MIN_COPIES, Math.ceil((window.innerWidth * 2.5) / setWidth) + 1);
      var fragment = document.createDocumentFragment();

      for (var i = 1; i < copies; i++) {
        var clone = group.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.dataset.clone = '1';
        fragment.appendChild(clone);
      }
      track.appendChild(fragment);

      var isMobile = window.innerWidth < 768;
      var effectiveSpeed = (isMobile && mobileSpeed) ? mobileSpeed : speed;
      var duration = setWidth / effectiveSpeed;

      track.style.setProperty('--marquee-shift', '-' + setWidth + 'px');
      track.style.setProperty('--marquee-duration', duration + 's');
      track.style.removeProperty('animation');
    }

    function start() {
      buildAndAnimate();
    }

    var images = group.querySelectorAll('img');
    var pending = 0;

    images.forEach(function (img) {
      if (!img.complete) {
        pending++;
        img.addEventListener('load', function onLoad() {
          img.removeEventListener('load', onLoad);
          pending--;
          if (pending === 0) start();
        });
      }
    });

    if (pending === 0) start();

    if (typeof ResizeObserver !== 'undefined') {
      var ro = new ResizeObserver(function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          track.style.setProperty('animation', 'none');
          buildAndAnimate();
        }, 150);
      });
      ro.observe(marquee);
    } else {
      window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          track.style.setProperty('animation', 'none');
          buildAndAnimate();
        }, 150);
      }, { passive: true });
    }
  }

  document.querySelectorAll('.foto-marquee').forEach(initMarquee);
})();
