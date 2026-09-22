/* ==========================================================================
   SAFE21 blog — shared behaviour
   ==========================================================================

   Loaded by every blog page with a deferred <script>. Three independent
   pieces, each guarded so it simply does nothing when its markup is absent:
   the mobile menu, the light/dark switch, and the image lightbox (articles
   without a figure just skip it).

   The pre-paint theme script stays inline in each page's <head>: it has to
   run before the first paint, which an external file cannot guarantee.
   ========================================================================== */

/**
 * Mobile menu toggle.
 *
 * Same dependency-free behaviour as index.html: the hamburger opens a
 * slide-down drawer, which closes on link tap, on Escape, and resets
 * automatically when the viewport grows past the mobile breakpoint.
 */
(function () {
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('mobile-menu');
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    // The label describes the NEXT action, so it flips with the state.
    toggle.setAttribute('aria-label', open ? 'Chiudi menu' : 'Apri menu');
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  // Close after tapping a link, otherwise the drawer would stay open
  // over the destination content.
  menu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () { setOpen(false); });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });

  // Reset when rotating/resizing to desktop, where the drawer is hidden
  // by CSS but would otherwise keep a stale aria-expanded="true".
  window.addEventListener('resize', function () {
    if (window.innerWidth > 760) setOpen(false);
  });
})();

/**
 * Light/dark theme switch — blog pages only.
 *
 * The whole theme lives in CSS custom properties, so switching means
 * toggling one attribute on <html>. The choice is stored under
 * "safe21-blog-theme" in sessionStorage, a key of its own (the homepage
 * uses "safe21-lang" for the language, and the two must not collide).
 * sessionStorage means the choice lasts only for the current visit;
 * every new visit starts dark.
 *
 * The <meta name="theme-color"> tag is updated too, so the browser
 * chrome on mobile matches the page instead of staying navy.
 */
(function () {
  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  var meta = document.querySelector('meta[name="theme-color"]');
  if (!btn) return;

  var COLORS = { dark: '#0A0F1C', light: '#F4F6F9' };

  function apply(theme) {
    var isLight = theme === 'light';
    if (isLight) {
      root.setAttribute('data-theme', 'light');
    } else {
      root.removeAttribute('data-theme');
    }
    // aria-pressed reports the *state*; the label describes the
    // *next* action, which is what a screen-reader user needs.
    btn.setAttribute('aria-pressed', String(isLight));
    btn.setAttribute('aria-label', isLight ? 'Passa al tema scuro' : 'Passa al tema chiaro');
    if (meta) meta.setAttribute('content', COLORS[isLight ? 'light' : 'dark']);
    // sessionStorage, not localStorage: the choice is forgotten when the
    // browser/tab closes, so the next visit starts dark again.
    try { sessionStorage.setItem('safe21-blog-theme', isLight ? 'light' : 'dark'); } catch (e) {}
  }

  // Sync the button with whatever the pre-paint script already set.
  apply(root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');

  btn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    apply(next);
    // Stamp the choice into the address bar (no reload), so copying the
    // link right now shares the page in this exact theme. Deliberately
    // NOT done on the initial sync above: only an explicit click should
    // rewrite the link, not every ordinary page load.
    try {
      var url = new URL(location.href);
      url.searchParams.set('theme', next);
      history.replaceState(null, '', url);
    } catch (e) {}
  });
})();

/**
 * Image lightbox. Clicking the figure image opens it in a full-screen
 * overlay at natural pixel size (1:1); the overlay scrolls if the image is
 * larger than the viewport. Closes on backdrop click, the X button, or
 * Escape. No external library.
 */
(function () {
  var overlay = document.getElementById('lightbox');
  if (!overlay) return;
  var big = overlay.querySelector('img');
  var closeBtn = overlay.querySelector('.lightbox-close');
  var lastFocus = null;

  function open(src, alt) {
    big.src = src; big.alt = alt || '';
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';   // lock background scroll
    lastFocus = document.activeElement;
    closeBtn.focus();
  }
  function close() {
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    big.src = '';                              // free the large image
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.querySelectorAll('figure.source img').forEach(function (img) {
    img.addEventListener('click', function () {
      open(img.currentSrc || img.src, img.alt);
    });
  });
  // Backdrop click closes; clicking the image itself does not.
  overlay.addEventListener('click', function (e) { if (e.target !== big) close(); });
  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('open')) close();
  });
})();
