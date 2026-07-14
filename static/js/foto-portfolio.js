'use strict';

(function initPortfolioSlider() {
  var slider = document.getElementById('portfolioSlider');
  var track = document.getElementById('portfolioTrack');
  var dotsBox = document.getElementById('portfolioDots');
  var prevBtn = document.getElementById('portfolioPrev');
  var nextBtn = document.getElementById('portfolioNext');
  if (!slider || !track) return;

  var items = track.querySelectorAll('.foto-portfolio-item');
  if (!items.length) return;

  var current = 0;
  var visible = 1;
  var total = items.length;
  var startX = 0;
  var isDragging = false;
  var suppressClick = false;
  var autoTimer = null;

  function getVisible() {
    if (window.innerWidth >= 1000) return 3;
    if (window.innerWidth >= 768) return 2;
    return 1;
  }

  function getMaxIndex() {
    return Math.max(0, total - visible);
  }

  function buildDots() {
    if (!dotsBox) return;
    dotsBox.innerHTML = '';
    for (var i = 0; i < total; i++) {
      var dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'foto-portfolio-dot' + (i === current ? ' active' : '');
      dot.setAttribute('aria-label', 'Фото ' + (i + 1));
      dot.addEventListener('click', function (idx) {
        return function () { goTo(idx); };
      }(i));
      dotsBox.appendChild(dot);
    }
  }

  function updateDots() {
    if (!dotsBox) return;
    dotsBox.querySelectorAll('.foto-portfolio-dot').forEach(function (dot, i) {
      dot.classList.toggle('active', i === current);
    });
  }

  function getStep() {
    var first = items[0];
    if (!first) return 0;
    return first.offsetWidth + 10;
  }

  function goTo(idx, animate) {
    var maxIndex = getMaxIndex();
    if (idx > maxIndex) {
      current = 0;
    } else if (idx < 0) {
      current = maxIndex;
    } else {
      current = idx;
    }

    if (animate === false) {
      track.style.transition = 'none';
    } else {
      track.style.transition = '';
    }

    track.style.transform = 'translate3d(-' + (current * getStep()) + 'px, 0, 0)';
    updateDots();

    if (animate === false) {
      requestAnimationFrame(function () {
        track.style.transition = '';
      });
    }
  }

  function recalc() {
    visible = getVisible();
    if (current > getMaxIndex()) {
      current = getMaxIndex();
    }
    buildDots();
    goTo(current, false);
  }

  function startAutoplay() {
    stopAutoplay();
    autoTimer = window.setInterval(function () {
      goTo(current + 1);
    }, 5000);
  }

  function stopAutoplay() {
    if (autoTimer) {
      window.clearInterval(autoTimer);
      autoTimer = null;
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      goTo(current - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      goTo(current + 1);
    });
  }

  track.addEventListener('touchstart', function (e) {
    startX = e.touches[0].clientX;
    isDragging = true;
    stopAutoplay();
  }, { passive: true });

  track.addEventListener('touchend', function (e) {
    if (!isDragging) return;
    var diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 40) {
      goTo(diff > 0 ? current + 1 : current - 1);
      suppressClick = true;
    }
    isDragging = false;
    startAutoplay();
  }, { passive: true });

  track.addEventListener('click', function (e) {
    if (!suppressClick) return;
    e.preventDefault();
    e.stopPropagation();
    suppressClick = false;
  }, true);

  slider.addEventListener('mouseenter', stopAutoplay);
  slider.addEventListener('mouseleave', startAutoplay);
  slider.addEventListener('focusin', stopAutoplay);
  slider.addEventListener('focusout', startAutoplay);

  window.addEventListener('resize', recalc, { passive: true });
  recalc();
  startAutoplay();
})();
