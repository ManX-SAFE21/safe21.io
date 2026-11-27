"""SAFE21 site menu: the ONE place where the header menu is defined.

The desktop menu (Servizi / Strumenti / Blog / Chi siamo, with dropdown
panels), the phone drawer and the footer "Chi siamo" link of EVERY page
(root *.html and guide/*.html) are generated from the lists below.

    python tools/menu.py          rewrite the menus of all pages
    python tools/menu.py --check  only report pages whose menu differs
                                  (tools/audit.py runs the same check)

To change the menu, edit the lists here and run the script: never edit a
page's <nav> by hand, the audit would stop the push. The manual generators
(safe21-ancora/manuale/strumenti/pubblica_sul_sito.py and
easy-heirs-wallet/anteprima/manuale-esempi/gen_manuale_sito.py) call this
script at the end, so regenerating the manual never leaves an old menu.

index.html is bilingual: its labels carry data-i18n keys, and the English
texts (the EN columns below) are added to its EN dictionary. The same
English texts (plus FOOTER_EN) go to i18n-common.json for the pages that
switch language with i18n.js (chisiamo.html, strumenti.html).
Icons: owner's "proposal D" (22/11/2026), stylised line icons in a light
teal outline; Àncòra and Schȅi keep their own logos.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Icons (24x24, stroke = currentColor), keyed by menu item key.
# ---------------------------------------------------------------------------
ICONS = {
    # Servizi
    "svc1": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="13" width="4" height="6" rx="1.5"/><rect x="17" y="13" width="4" height="6" rx="1.5"/>',
    "svc2": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c2.5 2 9.5 2 12 0v-5"/>',
    "svc3": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "svc4": '<circle cx="8" cy="7" r="2.6"/><circle cx="16.5" cy="10" r="2"/><path d="M3 20c0-3 2.2-5.5 5-5.5s5 2.5 5 5.5"/><path d="M13 20c.3-2.3 1.7-3.8 3.5-3.8S19.7 17.7 20 20"/>',
    "svc5": '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h4"/>',
    # Strumenti
    "t3": '<circle cx="9" cy="7" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 8h5M16 12h5M18 16h3"/>',
    "t4": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01M11 7.5h6M11 16.5h6"/>',
    "t5": '<circle cx="4" cy="12" r="1.6"/><path d="M5.6 12H11M11 12l8-6M11 12h8M11 12l8 6"/>',
    "m1": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 7h7M8 11h7"/>',
    "m2": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 7h7M8 11h7"/>',
    "m3": '<rect x="3" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6"/>',
    # Chi siamo
    "a1": '<circle cx="12" cy="8" r="3.6"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>',
    "a3": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 7.7-1.5"/><circle cx="12" cy="15.5" r="1.2"/>',
    "p1": '<path d="M7 3h10M7 21h10M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9s8 4 8 9"/>',
    "p2": '<ellipse cx="12" cy="6.5" rx="7" ry="3"/><path d="M5 6.5v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5M5 11.5v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5"/>',
    "c1": '<path d="M3 7h18v3.5a2 2 0 0 0 0 4V18H3v-3.5a2 2 0 0 0 0-4z"/><path d="M15 7v11" stroke-dasharray="1.6 2.2"/>',
    "c2": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "b1": '<path d="M4 4h13v16H6a2 2 0 0 1-2-2z"/><path d="M17 8h3v10a2 2 0 0 1-2 2M8 8h5M8 12h5M8 16h3"/>',
    "k1": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "c3": '<circle cx="8" cy="15" r="4.2"/><path d="M11 12l9-9M16.5 6.5l3 3M14 9l2 2"/>',
}
# "21" stays text: the number is the meaning.
TEXT = {"a2": "21"}


def svg(key):
    """Inline SVG of a line icon."""
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[key]}</svg>')


CHEVRON = ('<svg class="dd-chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" '
           'stroke-width="1.8" aria-hidden="true"><path d="M2 4l4 4 4-4"/></svg>')

# (key, href, icon, IT label, IT note, EN label, EN note). icon: text badge or "img:path"
SERVIZI = [
    ("svc1", "index.html#services", "?", "Assistenza Bitcoin", "Aiuto personale su wallet e sicurezza",
     "Bitcoin support", "One-to-one help on wallets and security"),
    ("svc2", "corsi.html", "C", "Corsi Bitcoin", "Online e di persona",
     "Bitcoin courses", "Online and in person"),
    ("svc3", "index.html#services", "E", "Sicurezza Electrum", "Wallet, 2FA, cold storage",
     "Electrum security", "Wallets, 2FA, cold storage"),
    ("svc4", "index.html#inheritance", "₿", "Eredità Bitcoin", "Il piano per i tuoi eredi",
     "Bitcoin inheritance", "The plan for your heirs"),
    ("svc5", "index.html#payments", "€", "Pagamenti in Bitcoin", "Con Pago in Bitcoin",
     "Bitcoin payments", "With Pago in Bitcoin"),
]
PROGRAMMI = [
    ("t1", "ancora.html", "img:images/ancora-icon.svg", "Àncòra", "Plugin Electrum per l'eredità",
     "Àncòra", "Electrum plugin for inheritance"),
    ("t2", "schei.html", "img:images/schei-icon.png", "Schȅi Wallet", "Il wallet semplice per Android",
     "Schȅi Wallet", "The simple Android wallet"),
    ("t3", "strumenti.html#easy-heirs", "EH", "Easy Heirs", "La lista degli eredi, offline",
     "Easy Heirs", "The heir list, offline"),
    ("t4", "strumenti.html#will-executor", "WE", "Will-Executor per Umbrel OS", "Il tuo custode, sul tuo nodo",
     "Will-Executor for Umbrel OS", "Your executor, on your node"),
    ("t5", "strumenti.html#paytomany", "PM", "PaytoMany", "Paga tanti con una transazione",
     "PaytoMany", "Pay many in one transaction"),
]
MANUALI = [
    ("m1", "guide/index.html", "M", "Manuale Àncòra", "Il primo testamento, la riga di comando",
     "Àncòra manual", "First will, command line"),
    ("m2", "guide/schei-manuale.html", "M", "Manuale Schȅi", "Primi passi, ricevere, eredità",
     "Schȅi manual", "First steps, receiving, inheritance"),
    ("m3", "strumenti.html", "→", "Tutti gli strumenti", "Versioni e download sempre aggiornati",
     "All tools", "Always up-to-date versions and downloads"),
]
CHI = [
    ("a1", "chisiamo.html", "S", "Chi siamo", "La nostra storia, dal 2016",
     "About us", "Our story, since 2016"),
    ("a2", "chisiamo.html#nome", "21", "Perché SAFE21", "Il significato del nome",
     "Why SAFE21", "What the name means"),
    ("a3", "liberta.html", "L", "Moneta della libertà", "Perché Bitcoin serve all'umanità",
     "Freedom money", "Why Bitcoin matters to humanity"),
]
PARTNER = [
    ("p1", "https://bitcoin-after.life/", "B", "BAL Protocol", "", "BAL Protocol", ""),
    ("p2", "https://www.pagoinbitcoin.ch/", "P", "Pago in Bitcoin", "", "Pago in Bitcoin", ""),
]
CONTATTI = [
    ("c1", "https://ticket.safe21.io/?tema=scuro", "T", "Apri un ticket", "", "Open a ticket", ""),
    ("c2", "https://github.com/ManX-SAFE21", "&lt;/&gt;", "Codice open source", "", "Open-source code", ""),
    ("c3", "safe21-pgp.asc", "K", "Chiave PGP", "", "PGP key", ""),
]
GROUP_EN = {"grp.programs": ("I programmi", "Programs"), "grp.manuals": ("Manuali", "Manuals"),
            "grp.partner": ("Partner", "Partners"), "grp.contacts": ("Contatti e trasparenza", "Contacts and transparency")}
TOP_EN = {"nav.services": ("Servizi", "Services"), "nav.tools": ("Strumenti", "Tools"),
          "nav.blog": ("Blog", "Blog"), "nav.about": ("Chi siamo", "About us"),
          "nav.contact": ("Contattaci", "Contact us")}


# Footer phrases (IT -> EN) for the pages translated at runtime by i18n.js
# (chisiamo.html, strumenti.html). index.html has its own EN dictionary.
FOOTER_EN = [
    ("Sicurezza Bitcoin, self-custody ed eredità — con le tue chiavi sempre nelle tue mani.",
     "Bitcoin security, self-custody and inheritance — with your keys always in your hands."),
    ("Servizi", "Services"), ("Assistenza Bitcoin", "Bitcoin support"), ("Corsi Bitcoin", "Bitcoin courses"),
    ("Sicurezza Electrum", "Electrum security"), ("Eredità", "Inheritance"), ("Plugin Àncòra", "Àncòra plugin"),
    ("Pagamenti", "Payments"), ("Partner", "Partners"), ("BAL Protocol ↗", "BAL Protocol ↗"),
    ("Pago in Bitcoin ↗", "Pago in Bitcoin ↗"), ("Contatti", "Contact"), ("Chi siamo", "About us"),
    ("Apri un ticket ↗", "Open a ticket ↗"), ("Codice open source ↗", "Open-source code ↗"), ("Chiave PGP", "PGP key"),
    ("SAFE21 fornisce consulenza tecnica e formazione sulla self-custody di Bitcoin. Non si tratta di consulenza "
     "legale, fiscale o finanziaria, e SAFE21 non prende mai in custodia i tuoi fondi — le chiavi restano sempre "
     "sotto il tuo controllo. Le regole su successioni e tassazione variano da paese a paese: per la tua situazione "
     "specifica rivolgiti a un professionista qualificato. Le transazioni Bitcoin sono irreversibili.",
     "SAFE21 provides technical guidance and education on Bitcoin self-custody. It is not legal, tax or financial "
     "advice, and SAFE21 never takes custody of your funds — you always control your own keys. Inheritance and tax "
     "rules differ from country to country; please consult a qualified professional for your own situation. "
     "Bitcoin transactions are irreversible."),
    ("© 2026 SAFE21 — safe21.io. Tutti i diritti riservati.", "© 2026 SAFE21 — safe21.io. All rights reserved."),
]
COMMON_FILE = "i18n-common.json"

def url(href, up):
    """Relative link from the page's folder (guide/ is one level down)."""
    if re.match(r"https?:|mailto:", href):
        return href
    return up + href


def badge(key, fallback):
    """Stylised line icon for the item (proposal D), else its text badge."""
    if key in TEXT:
        return TEXT[key]
    return svg(key) if key in ICONS else fallback


def item(it, up, i18n):
    key, href, icon, lab, note, _, _ = it
    ext = href.startswith("http")
    attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    if icon.startswith("img:"):
        # width/height = the file's real size (audit: no layout jump); CSS shows it at 30 px
        wh = 'width="192" height="192"' if icon.endswith(".png") else 'width="30" height="30"'
        ico = f'<span class="dd-ico"><img src="{url(icon[4:], up)}" alt="" {wh}></span>'
    else:
        ico = f'<span class="dd-ico" aria-hidden="true">{badge(key, icon)}</span>'
    l_attr = f' data-i18n="menu.{key}"' if i18n else ""
    n_attr = f' data-i18n="menu.{key}.n"' if i18n else ""
    arrow = " &nearr;" if ext else ""
    small = f"<small{n_attr}>{note}</small>" if note else ""
    return (f'<a href="{url(href, up)}"{attrs}>{ico}<span><span{l_attr}>{lab}</span>{arrow}{small}</span></a>')


def grp(key, i18n):
    a = f' data-i18n="{key}"' if i18n else ""
    return f'<p class="dd-grp"{a}>{GROUP_EN[key][0]}</p>'


def top_button(key, label, panel_id, current, i18n):
    cur = " current" if current else ""
    a = f' data-i18n="{key}"' if i18n else ""
    return (f'<button type="button" class="dd-btn{cur}" aria-expanded="false" aria-controls="{panel_id}">'
            f'<span{a}>{label}</span>{CHEVRON}</button>')


def desktop(up, current, i18n):
    I = "        "
    L = []
    L.append('      <nav class="nav-links" aria-label="Principale">')
    L.append(I + '<!-- Grouped menu (#79+): each button opens a panel (blog.js / index script). -->')
    L.append(I + '<div class="dd">')
    L.append(I + "  " + top_button("nav.services", "Servizi", "dd-servizi", current == "servizi", i18n))
    L.append(I + '  <div class="dd-panel" id="dd-servizi">')
    L += [I + "    " + item(x, up, i18n) for x in SERVIZI]
    L.append(I + "  </div>")
    L.append(I + "</div>")
    L.append(I + '<div class="dd">')
    L.append(I + "  " + top_button("nav.tools", "Strumenti", "dd-strumenti", current == "strumenti", i18n))
    L.append(I + '  <div class="dd-panel dd-wide" id="dd-strumenti">')
    L.append(I + "    <div>")
    L.append(I + "      " + grp("grp.programs", i18n))
    L += [I + "      " + item(x, up, i18n) for x in PROGRAMMI]
    L.append(I + "    </div>")
    L.append(I + "    <div>")
    L.append(I + "      " + grp("grp.manuals", i18n))
    L += [I + "      " + item(x, up, i18n) for x in MANUALI[:2]]
    L.append(I + "      <hr>")
    L.append(I + "      " + item(MANUALI[2], up, i18n))
    L.append(I + "    </div>")
    L.append(I + "  </div>")
    L.append(I + "</div>")
    cur = ' class="current"' if current == "blog" else ""
    a = ' data-i18n="nav.blog"' if i18n else ""
    L.append(I + f'<a href="{url("blog.html", up)}"{cur}{a}>Blog</a>')
    L.append(I + '<div class="dd">')
    L.append(I + "  " + top_button("nav.about", "Chi siamo", "dd-chisiamo", current == "chisiamo", i18n))
    L.append(I + '  <div class="dd-panel dd-right" id="dd-chisiamo">')
    L += [I + "    " + item(x, up, i18n) for x in CHI]
    L.append(I + "    <hr>" + grp("grp.partner", i18n))
    L += [I + "    " + item(x, up, i18n) for x in PARTNER]
    L.append(I + "    <hr>" + grp("grp.contacts", i18n))
    L += [I + "    " + item(x, up, i18n) for x in CONTATTI]
    L.append(I + "  </div>")
    L.append(I + "</div>")
    L.append("      </nav>")
    return "\n".join(L)


def mobile(up, i18n):
    """Drawer: the same groups, shorter (partners and code stay in the footer)."""
    def a(href, label, key, ico):
        # The label sits in its own span: index.html's language switch
        # replaces innerHTML of [data-i18n], which must not wipe the icon.
        k = f' data-i18n="{key}"' if i18n else ""
        if ico.startswith("img:"):
            wh = 'width="192" height="192"' if ico.endswith(".png") else 'width="30" height="30"'
            i = f'<span class="dd-ico"><img src="{url(ico[4:], up)}" alt="" {wh}></span>'
        else:
            i = f'<span class="dd-ico" aria-hidden="true">{badge(ico, "")}</span>'
        return f'        <a href="{url(href, up)}">{i}<span{k}>{label}</span></a>'

    def g(label, key):
        k = f' data-i18n="{key}"' if i18n else ""
        return f'        <p class="mm-grp"{k}>{label}</p>'
    L = ['      <nav aria-label="Mobile">']
    L.append(g("Servizi", "nav.services"))
    L += [a(x[1], x[3], f"menu.{x[0]}", x[0]) for x in SERVIZI]
    L.append(g("Strumenti", "nav.tools"))
    L += [a(x[1], x[3], f"menu.{x[0]}", x[2] if x[2].startswith("img:") else x[0])
          for x in (MANUALI[2], PROGRAMMI[0], PROGRAMMI[1], MANUALI[0], MANUALI[1])]
    L.append(g("SAFE21", "grp.safe21"))
    L.append(a("chisiamo.html", "Chi siamo", "menu.a1", "a1"))
    L.append(a("chisiamo.html#nome", "Perché SAFE21", "menu.a2", "a2"))
    L.append(a("liberta.html", "Moneta della libertà", "menu.a3", "a3"))
    L.append(a("blog.html", "Blog", "nav.blog", "b1"))
    L.append(a("mailto:info@safe21.io", "Contattaci", "nav.contact", "k1"))
    L.append("      </nav>")
    return "\n".join(L)


def current_of(name):
    base = os.path.basename(name)
    if name.replace("\\", "/").startswith("guide/") or base in ("ancora.html", "schei.html", "strumenti.html"):
        return "strumenti"
    if base.startswith("blog"):
        return "blog"
    if base == "corsi.html":
        return "servizi"
    if base in ("chisiamo.html", "liberta.html"):
        return "chisiamo"
    return ""


def en_dict_lines():
    """Extra EN dictionary entries for index.html."""
    out = []
    for k, (it, en) in TOP_EN.items():
        if k in ("nav.blog", "nav.contact"):
            continue
        out.append((k, en))
    for k, (it, en) in GROUP_EN.items():
        out.append((k, en))
    out.append(("grp.safe21", "SAFE21"))
    for lst in (SERVIZI, PROGRAMMI, MANUALI, CHI, PARTNER, CONTATTI):
        for key, _, _, _, note, en_l, en_n in lst:
            out.append((f"menu.{key}", en_l))
            if note:
                out.append((f"menu.{key}.n", en_n))
    out.append(("footer.about", "About us"))
    return out


def pages():
    """Every page that carries the site menu, as paths relative to ROOT."""
    out = []
    for folder in ("", "guide"):
        d = os.path.join(ROOT, folder)
        for name in sorted(os.listdir(d)):
            if name.endswith(".html") and not name.startswith("_"):
                out.append(f"{folder}/{name}" if folder else name)
    return out


def render(rel, text):
    """The page text (LF line ends) with its menus and footer link as they must be."""
    s = text.replace("\r\n", "\n")
    up = "../" if rel.startswith("guide/") else ""
    i18n = rel == "index.html"
    d0 = s.index('      <nav class="nav-links"')
    d1 = s.index("      </nav>", d0) + len("      </nav>")
    s = s[:d0] + desktop(up, current_of(rel), i18n) + s[d1:]
    m0 = s.index('      <nav aria-label="Mobile">')
    m1 = s.index("      </nav>", m0) + len("      </nav>")
    s = s[:m0] + mobile(up, i18n) + s[m1:]
    # Footer: "Chi siamo" first in the Contatti column.
    foot = s.index("<footer")
    if 'chisiamo.html"' not in s[foot:]:
        k = ' data-i18n="footer.about"' if i18n else ""
        col = re.search(r'(\n\s*)<h4[^>]*>Contatti</h4>', s[foot:])
        pos = foot + col.end()
        s = s[:pos] + f'{col.group(1)}<a href="{up}chisiamo.html"{k}>Chi siamo</a>' + s[pos:]
    if i18n:
        anchor = "        'nav.tools': 'Tools',\n"
        add = "".join(f"        '{k}': '{v}',\n" for k, v in en_dict_lines() if f"'{k}':" not in s)
        s = s.replace(anchor, anchor + add, 1)
    return s


def common_json():
    """i18n-common.json: every menu and footer phrase, Italian -> English,
    for i18n.js (exact text match on header/footer text nodes)."""
    import json
    m = {}
    for k, (it, en) in TOP_EN.items():
        m[it] = en
    for k, (it, en) in GROUP_EN.items():
        m[it] = en
    for lst in (SERVIZI, PROGRAMMI, MANUALI, CHI, PARTNER, CONTATTI):
        for _, _, _, lab, note, en_l, en_n in lst:
            m[lab] = en_l
            if note:
                m[note] = en_n
    for it, en in FOOTER_EN:
        m[" ".join(it.split())] = en
    return json.dumps(m, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def read_common():
    """Current i18n-common.json (LF line ends), or "" if missing."""
    path = os.path.join(ROOT, COMMON_FILE)
    if not os.path.exists(path):
        return ""
    return open(path, encoding="utf-8").read().replace("\r\n", "\n")


def check():
    """Pages whose menu is not what this script produces: [(page, reason)]."""
    bad = []
    for rel in pages():
        text = open(os.path.join(ROOT, rel), encoding="utf-8", newline="").read()
        try:
            want = render(rel, text)
        except (ValueError, AttributeError):
            bad.append((rel, "menu or footer not found"))
            continue
        if want != text.replace("\r\n", "\n"):
            bad.append((rel, "menu differs from tools/menu.py (run: python tools/menu.py)"))
    if read_common() != common_json():
        bad.append((COMMON_FILE, "out of date (run: python tools/menu.py)"))
    return bad


def main():
    """Rewrite every page's menu, or with --check only report differences."""
    if "--check" in sys.argv:
        bad = check()
        for rel, why in bad:
            print(f"{rel}: {why}")
        sys.exit(1 if bad else 0)
    for rel in pages():
        path = os.path.join(ROOT, rel)
        raw = open(path, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        new = render(rel, raw)
        if new != raw.replace("\r\n", "\n"):
            open(path, "w", encoding="utf-8", newline="").write(new.replace("\n", nl))
            print("menu updated:", rel)
    if read_common() != common_json():
        path = os.path.join(ROOT, COMMON_FILE)
        open(path, "w", encoding="utf-8", newline="\n").write(common_json())
        print("updated:", COMMON_FILE)
    print("menu ok")


if __name__ == "__main__":
    main()
