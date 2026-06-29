/* Pulse.is live chat — FAB offsets (mobile / tablet / iOS Safari) */
(function initPulseChatOffsets() {
  // #region agent log
  var _dbgApplyCount = 0;
  var _dbgMutCount = 0;
  var _dbgInsetCount = 0;
  var _dbgStart = Date.now();
  function _dbgLog(message, data, hypothesisId) {
    fetch('http://127.0.0.1:7395/ingest/cd1b0c32-25fc-45af-bcd9-1c48029f63fc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': 'f5ec68' },
      body: JSON.stringify({
        sessionId: 'f5ec68',
        runId: 'post-fix',
        hypothesisId: hypothesisId,
        location: 'pulse-chat.js',
        message: message,
        data: data,
        timestamp: Date.now(),
      }),
    }).catch(function () {});
  }
  // #endregion

  var OFFSET_QUERY = '(max-width: 1024px)';
  var MOBILE_QUERY = '(max-width: 767px)';
  var CHAT_BOTTOM_MOBILE = 72;
  var CHAT_BOTTOM_TABLET = 80;
  var CHAT_BOTTOM_DESKTOP = 24;
  var MOBILE_SIDE = 16;

  var insetProbe = null;
  var insetCache = { bottom: 0, left: 0, right: 0 };
  var applyRaf = 0;
  var mountObserver = null;
  var chatOffsetApplied = false;

  function needsOffset() {
    return window.matchMedia(OFFSET_QUERY).matches;
  }

  function isMobile() {
    return window.matchMedia(MOBILE_QUERY).matches;
  }

  function ensureInsetProbe() {
    if (insetProbe || !document.body) return;
    insetProbe = document.createElement('div');
    insetProbe.setAttribute('aria-hidden', 'true');
    insetProbe.style.cssText =
      'position:fixed;visibility:hidden;pointer-events:none;top:0;left:0;width:0;height:0;';
    document.body.appendChild(insetProbe);
  }

  function refreshInsetCache() {
    ensureInsetProbe();
    if (!insetProbe) return;
    ['bottom', 'left', 'right'].forEach(function (edge) {
      var prop = 'padding-' + edge;
      insetProbe.style.padding = '0';
      insetProbe.style[prop] = 'env(safe-area-inset-' + edge + ')';
      insetCache[edge] = parseFloat(window.getComputedStyle(insetProbe).getPropertyValue(prop)) || 0;
    });
    // #region agent log
    _dbgInsetCount += 1;
    if (_dbgInsetCount <= 3 || _dbgInsetCount % 100 === 0) {
      _dbgLog('refreshInsetCache', { count: _dbgInsetCount, insetCache: insetCache }, 'H1');
    }
    // #endregion
  }

  function readSafeInset(edge) {
    return insetCache[edge] || 0;
  }

  function getExtraBottom() {
    if (!window.visualViewport) return 0;
    var vv = window.visualViewport;
    return Math.max(0, Math.round(window.innerHeight - vv.height - vv.offsetTop));
  }

  function getChatBottomPx() {
    var base = CHAT_BOTTOM_DESKTOP;
    if (isMobile()) {
      base = CHAT_BOTTOM_MOBILE;
    } else if (needsOffset()) {
      base = CHAT_BOTTOM_TABLET;
    }
    return base + readSafeInset('bottom') + getExtraBottom();
  }

  function getLeftPx() {
    return MOBILE_SIDE + readSafeInset('left');
  }

  function getChatRoot() {
    return document.querySelector('sp-live-chat');
  }

  function applyChatOffset() {
    var chat = getChatRoot();
    if (!chat || !chat.shadowRoot) return false;

    var fab = chat.shadowRoot.querySelector('.widget-fab');
    if (!fab) return false;

    if (needsOffset()) {
      var bottomPx = getChatBottomPx();
      var leftPx = getLeftPx();
      fab.style.setProperty('bottom', bottomPx + 'px');
      fab.style.setProperty('left', leftPx + 'px');
      fab.style.setProperty('right', 'auto');

      var styleEl = chat.shadowRoot.getElementById('metrium-chat-offset');
      if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'metrium-chat-offset';
        chat.shadowRoot.appendChild(styleEl);
      }
      styleEl.textContent =
        '.widget-fab{bottom:' + bottomPx + 'px;left:' + leftPx + 'px;right:auto;}';
    } else {
      fab.style.removeProperty('left');
      fab.style.removeProperty('right');
      fab.style.setProperty('bottom', getChatBottomPx() + 'px');

      var resetStyle = chat.shadowRoot.getElementById('metrium-chat-offset');
      if (resetStyle) resetStyle.remove();
    }

    chatOffsetApplied = true;
    return true;
  }

  function applyStackOffsets() {
    var stack = document.getElementById('siteFabStack');
    if (!stack) return;

    if (isMobile()) {
      stack.style.paddingBottom = (56 + readSafeInset('bottom') + getExtraBottom()) + 'px';
      stack.style.paddingRight = (MOBILE_SIDE + readSafeInset('right')) + 'px';
    } else {
      stack.style.removeProperty('padding-bottom');
      stack.style.removeProperty('padding-right');
    }
  }

  function applyAllNow() {
    // #region agent log
    _dbgApplyCount += 1;
    if (_dbgApplyCount <= 5 || _dbgApplyCount === 50 || _dbgApplyCount % 500 === 0) {
      _dbgLog('applyAllNow', { count: _dbgApplyCount, elapsedMs: Date.now() - _dbgStart }, 'H2');
    }
    // #endregion
    applyStackOffsets();
    applyChatOffset();
  }

  function applyAll() {
    if (applyRaf) return;
    applyRaf = window.requestAnimationFrame(function () {
      applyRaf = 0;
      applyAllNow();
    });
  }

  function stopMountObserver() {
    if (!mountObserver) return;
    mountObserver.disconnect();
    mountObserver = null;
  }

  function scheduleChatOffset(retries) {
    if (applyChatOffset()) {
      stopMountObserver();
      return;
    }
    if (retries <= 0) return;
    setTimeout(function () { scheduleChatOffset(retries - 1); }, 300);
  }

  function watchChatMount() {
    if (!window.MutationObserver || mountObserver) return;
    mountObserver = new MutationObserver(function () {
      if (!getChatRoot()) return;
      // #region agent log
      _dbgMutCount += 1;
      if (_dbgMutCount <= 5 || _dbgMutCount === 50 || _dbgMutCount % 500 === 0) {
        _dbgLog('MutationObserver fired', {
          count: _dbgMutCount,
          hasChat: true,
          chatOffsetApplied: chatOffsetApplied,
          elapsedMs: Date.now() - _dbgStart,
        }, 'H1');
      }
      // #endregion
      if (applyChatOffset()) {
        stopMountObserver();
        return;
      }
      scheduleChatOffset(3);
    });
    mountObserver.observe(document.body, { childList: true, subtree: true });
  }

  function boot() {
    refreshInsetCache();
    applyAllNow();
    scheduleChatOffset(40);
    watchChatMount();
  }

  document.addEventListener('spLiveChatLoaded', function () {
    refreshInsetCache();
    scheduleChatOffset(10);
    window.setTimeout(function () {
      if (applyChatOffset()) stopMountObserver();
    }, 800);
  });

  window.addEventListener('resize', function () {
    refreshInsetCache();
    applyAll();
  }, { passive: true });

  window.addEventListener('orientationchange', function () {
    refreshInsetCache();
    applyAll();
  }, { passive: true });

  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', applyAll, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
