/* ==========================================================================
   SAFE21 — Italian / English switch for chisiamo.html and strumenti.html
   ==========================================================================

   The pages are written in Italian (what search engines index). English is
   applied at runtime, like on the homepage, and the choice is SHARED with
   the homepage: the same localStorage key "safe21-lang", so a visitor who
   picked EN on the home finds these pages in English too.

   Two dictionaries:
   - the page's own, in <script type="application/json" id="i18n-en">,
     keyed by the elements' data-i18n attributes (innerHTML, so values may
     hold markup), plus "meta.title" and "meta.description";
   - the menu and footer phrases, in i18n-common.json, written by
     tools/menu.py from the same lists that build the menu (one source),
     plus the page's own "phrases" (short texts repeated on the page, like
     the card labels). Those are matched on the exact text of the page's
     text nodes, outside the [data-i18n] elements.

   The Italian originals are captured from the DOM before the first switch,
   so the markup stays the only copy of the Italian text. After every
   switch a "safe21:lang" event tells other scripts (strumenti.js) to
   re-render their live texts.
   ========================================================================== */
(function () {
  var KEY = 'safe21-lang';
  var btns = document.querySelectorAll('.lang-btn');
  var pageEl = document.getElementById('i18n-en');
  if (!pageEl) return;
  var PAGE = JSON.parse(pageEl.textContent);
  var COMMON = null;                       // loaded below
  var els = document.querySelectorAll('[data-i18n]');
  var metaDesc = document.querySelector('meta[name="description"]');

  // Italian originals, captured once.
  var IT = {};
  els.forEach(function (el) { IT[el.getAttribute('data-i18n')] = el.innerHTML; });
  IT['meta.title'] = document.title;
  IT['meta.description'] = metaDesc ? metaDesc.getAttribute('content') : '';

  // Text nodes whose exact text is a known phrase (menu, footer, page).
  var shellNodes = [];
  function collectShell() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentElement;
        return p && !p.closest('script, style, [data-i18n]')
          ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var n;
    while ((n = w.nextNode())) {
      // Long sentences span several source lines: compare the text with
      // its whitespace collapsed.
      var t = n.nodeValue.replace(/\s+/g, ' ').trim();
      if (t && COMMON[t] !== undefined) shellNodes.push({ node: n, it: n.nodeValue, key: t });
    }
  }

  function apply(lang) {
    var en = lang === 'en';
    els.forEach(function (el) {
      var k = el.getAttribute('data-i18n');
      var v = en ? PAGE[k] : IT[k];
      if (v !== undefined) el.innerHTML = v;
    });
    document.title = en && PAGE['meta.title'] ? PAGE['meta.title'] : IT['meta.title'];
    if (metaDesc) {
      metaDesc.setAttribute('content',
        en && PAGE['meta.description'] ? PAGE['meta.description'] : IT['meta.description']);
    }
    shellNodes.forEach(function (s) {
      // Keep the spaces around the text: they separate it from the arrows.
      var lead = s.it.match(/^\s*/)[0], trail = s.it.match(/\s*$/)[0];
      s.node.nodeValue = en ? lead + COMMON[s.key] + trail : s.it;
    });
    document.documentElement.setAttribute('lang', lang);
    btns.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
    });
    document.dispatchEvent(new CustomEvent('safe21:lang', { detail: lang }));
  }

  function choose(lang) {
    apply(lang);
    try { localStorage.setItem(KEY, lang); } catch (e) { /* private mode */ }
  }

  btns.forEach(function (b) {
    b.addEventListener('click', function () { choose(b.getAttribute('data-lang')); });
  });

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  var start = saved === 'en' ? 'en' : 'it';

  fetch('i18n-common.json')
    .then(function (r) { return r.ok ? r.json() : {}; })
    .catch(function () { return {}; })
    .then(function (common) {
      COMMON = common;
      var own = PAGE.phrases || {};
      Object.keys(own).forEach(function (k) { COMMON[k] = own[k]; });
      collectShell();
      if (start === 'en') apply('en');
    });
})();
