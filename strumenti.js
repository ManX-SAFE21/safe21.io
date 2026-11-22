/* ==========================================================================
   SAFE21 — strumenti.html: live data from GitHub
   ==========================================================================

   Every card names its repository (data-repo). On each visit this script
   asks the public GitHub API for the latest release and fills in:
   - the version and the publication date;
   - the "Scarica il file" button, pointed straight at the release ZIP;
   - for Electrum plugins (data-manifest = path of manifest.json in the
     repository), the "Serve" row from min_electrum_version, read from the
     manifest of THAT release, so a raised requirement shows up by itself.
   Web apps (data-web) have no release: only the last update date is shown.
   Umbrel apps (data-umbrel = app folder in the store repository) are
   installed from the store, not from a ZIP: the version comes from the
   app's umbrel-app.yml, the date from the last commit of that folder.
   A [data-copy] button copies its text (the store address).
   A [data-dialog] link opens that <dialog> instead of following its href.
   Live texts (dates, "Scarica il file (1,0 MB)", "o successivo", "Copia")
   follow the page language set by i18n.js: the raw values are kept on the
   elements and painted again on every "safe21:lang" event.

   Everything written in the HTML is the fallback: without JavaScript, or
   when GitHub does not answer (it allows 60 calls per hour per visitor),
   the buttons keep pointing to the release page, which always works.
   ========================================================================== */
(function () {
  var API = 'https://api.github.com/repos/ManX-SAFE21/';
  var RAW = 'https://raw.githubusercontent.com/ManX-SAFE21/';

  function getJSON(url) {
    return fetch(url).then(function (r) {
      return r.ok ? r.json() : Promise.reject(r.status);
    });
  }

  function en() { return document.documentElement.lang === 'en'; }

  // Raw values live in data-* attributes; paint() writes them in the
  // current language.
  function paint() {
    document.querySelectorAll('[data-iso]').forEach(function (el) {
      el.textContent = new Date(el.getAttribute('data-iso')).toLocaleDateString(
        en() ? 'en-GB' : 'it-IT', { day: 'numeric', month: 'long', year: 'numeric' });
    });
    document.querySelectorAll('[data-mb]').forEach(function (el) {
      var mb = Number(el.getAttribute('data-mb'));
      el.textContent = en()
        ? 'Download the file (' + mb.toFixed(1) + ' MB)'
        : 'Scarica il file (' + mb.toFixed(1).replace('.', ',') + ' MB)';
    });
    document.querySelectorAll('[data-el]').forEach(function (el) {
      el.textContent = 'Electrum ' + el.getAttribute('data-el') + (en() ? ' or later' : ' o successivo');
    });
  }
  document.addEventListener('safe21:lang', paint);

  document.querySelectorAll('.sw-card[data-repo]').forEach(function (card) {
    var repo = card.getAttribute('data-repo');
    function set(field, text) {
      var el = card.querySelector('[data-f="' + field + '"]');
      if (el) el.textContent = text;
    }
    function setRaw(field, attr, value) {
      var el = card.querySelector('[data-f="' + field + '"]');
      if (el) { el.setAttribute(attr, value); paint(); }
    }

    var app = card.getAttribute('data-umbrel');
    if (app) {
      fetch(RAW + repo + '/main/' + app + '/umbrel-app.yml')
        .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
        .then(function (yml) {
          var m = yml.match(/^version:\s*"?([^"\r\n]+)"?/m);
          if (m) set('ver', m[1]);
        })
        .catch(function () {});
      getJSON(API + repo + '/commits?per_page=1&path=' + encodeURIComponent(app))
        .then(function (list) {
          if (list[0]) setRaw('date', 'data-iso', list[0].commit.committer.date);
        })
        .catch(function () {});
      return;
    }

    if (card.hasAttribute('data-web')) {
      getJSON(API + repo)
        .then(function (d) { setRaw('date', 'data-iso', d.pushed_at); })
        .catch(function () {});
      return;
    }

    getJSON(API + repo + '/releases/latest')
      .then(function (rel) {
        // "ancora-v0.8.0" -> "0.8.0", "v1.0.12" -> "1.0.12"
        set('ver', rel.tag_name.replace(/^.*?v(?=\d)/, ''));
        setRaw('date', 'data-iso', rel.published_at);

        var zip = (rel.assets || []).filter(function (a) {
          return /\.zip$/i.test(a.name);
        })[0];
        if (zip) {
          var btn = card.querySelector('[data-f="dl"]');
          btn.href = zip.browser_download_url;
          btn.removeAttribute('target');      // a download, not a new tab
          setRaw('dl', 'data-mb', String(zip.size / 1048576));
        }

        var manifest = card.getAttribute('data-manifest');
        if (!manifest) return;
        return getJSON(RAW + repo + '/' + encodeURIComponent(rel.tag_name) + '/' + manifest)
          .then(function (m) {
            if (m.min_electrum_version) {
              setRaw('needs', 'data-el', m.min_electrum_version);
            }
          });
      })
      .catch(function () {});
  });

  document.querySelectorAll('[data-dialog]').forEach(function (link) {
    var dialog = document.getElementById(link.getAttribute('data-dialog'));
    if (!dialog || typeof dialog.showModal !== 'function') return;   // old browser: keep the href
    link.addEventListener('click', function (e) {
      e.preventDefault();
      dialog.showModal();
    });
    dialog.querySelectorAll('[data-close]').forEach(function (b) {
      b.addEventListener('click', function () { dialog.close(); });
    });
    // A click on the dark backdrop lands on the <dialog> element itself,
    // like one on its padding: only a click outside its box closes it.
    dialog.addEventListener('click', function (e) {
      if (e.target !== dialog) return;
      var r = dialog.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right ||
          e.clientY < r.top || e.clientY > r.bottom) dialog.close();
    });
  });

  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!navigator.clipboard) return;      // the address stays visible to copy by hand
      navigator.clipboard.writeText(btn.getAttribute('data-copy')).then(function () {
        btn.textContent = en() ? 'Copied' : 'Copiato';
        setTimeout(function () { btn.textContent = en() ? 'Copy' : 'Copia'; }, 2000);
      });
    });
  });
})();
