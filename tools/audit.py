#!/usr/bin/env python3
"""
SAFE21 site audit — run before every push.

    python tools/audit.py

Read-only: it never edits a file. Exits 0 when the site is clean, 1 when there
is at least one ERRORE, so it can be wired into CI later.

Two output levels:
  ERRORE    something is actually broken and must be fixed before pushing.
  AVVISO    worth a look, but not necessarily wrong (e.g. an over-long meta
            description). Never fails the run.

Design note: known-correct exceptions are listed in EXPECTED below and are
skipped explicitly. A checker that always reports the same three harmless
"errors" trains people to ignore it, which defeats the point.

Image dimension checks need Pillow (`pip install Pillow`). Without it the rest
of the audit still runs and that single check is reported as skipped.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

# --------------------------------------------------------------------------
# Known-correct exceptions. Each one is a deliberate choice, not an oversight.
# --------------------------------------------------------------------------
EXPECTED = {
    # The homepage ships in English with a runtime EN/IT switcher that rewrites
    # the lang attribute, so lang="en" in the source is correct.
    'lang_not_it': {'index.html'},
    # The homepage is served from the bare root, so its canonical and og:url are
    # "https://safe21.io/" rather than ".../index.html".
    'canonical_root': {'index.html'},
}

# Pages that are not blog articles and so have no byline/eyebrow/article body.
NON_ARTICLE = {'index.html', 'blog.html'}

MONTHS = {'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5,
          'giugno': 6, 'luglio': 7, 'agosto': 8, 'settembre': 9, 'ottobre': 10,
          'novembre': 11, 'dicembre': 12}

VOID_TAGS = {'meta', 'link', 'img', 'br', 'hr', 'input', 'area', 'base', 'col',
             'embed', 'source', 'track', 'wbr'}

errors, warnings, skipped = [], [], []


def err(page, msg):
    errors.append((page, msg))


def warn(page, msg):
    warnings.append((page, msg))


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


def unescape_basic(s):
    for a, b in (('&middot;', '·'), ('&amp;', '&'), ('&nbsp;', ' '),
                 ('&rarr;', '→'), ('&larr;', '←'), ('&nearr;', '↗')):
        s = s.replace(a, b)
    return s


def style_of(src):
    """The page's <style> block with comments stripped."""
    m = re.search(r'<style>(.*?)</style>', src, re.S)
    return re.sub(r'/\*.*?\*/', '', m.group(1), flags=re.S) if m else ''


# --------------------------------------------------------------------------
# 1. HTML tag nesting
# --------------------------------------------------------------------------
class NestingChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.problems.append(f'</{tag}> di troppo (nessun tag aperto)')
        elif self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            i = len(self.stack) - 1 - self.stack[::-1].index(tag)
            self.problems.append(
                f'</{tag}> chiude fuori ordine: era aperto <{self.stack[-1]}> '
                f'(annidamento: {self.stack[i:]})')
            self.stack = self.stack[:i]
        else:
            self.problems.append(f'</{tag}> non ha un tag di apertura')


def check_nesting(page, src):
    c = NestingChecker()
    try:
        c.feed(src)
    except Exception as e:                       # noqa: BLE001
        err(page, f'HTML non analizzabile: {e}')
        return
    for p in c.problems:
        err(page, f'annidamento HTML: {p}')
    if c.stack:
        err(page, f'tag non chiusi a fine file: {c.stack}')


# --------------------------------------------------------------------------
# 2. JSON-LD
# --------------------------------------------------------------------------
def check_jsonld(page, src):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                        src, re.S)
    if not blocks:
        err(page, 'manca il blocco JSON-LD')
        return
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', src)
    for i, b in enumerate(blocks):
        try:
            data = json.loads(b)
        except json.JSONDecodeError as e:
            err(page, f'JSON-LD non valido (blocco {i}): {e}')
            continue
        if canonical and data.get('url') and data['url'] != canonical.group(1):
            err(page, f'JSON-LD url ({data["url"]}) diverso dal canonical '
                      f'({canonical.group(1)})')
        if data.get('@type') == 'Article':
            h1 = re.search(r'<h1>(.*?)</h1>', src, re.S)
            if h1:
                h1_text = unescape_basic(strip_tags(h1.group(1)))
                headline = unescape_basic(data.get('headline', '').strip())
                if headline != h1_text:
                    err(page, 'JSON-LD headline diverso da <h1>:\n'
                              f'      headline: {headline!r}\n'
                              f'      h1:       {h1_text!r}')
            if 'image' in data:
                og = re.search(r'<meta property="og:image" content="([^"]+)"', src)
                if not og:
                    err(page, 'JSON-LD ha "image" ma manca <meta og:image>')
                elif og.group(1) != data['image']:
                    err(page, f'og:image ({og.group(1)}) diverso da JSON-LD '
                              f'image ({data["image"]})')


# --------------------------------------------------------------------------
# 3. canonical / og:url
# --------------------------------------------------------------------------
def check_canonical(page, src):
    if page in EXPECTED['canonical_root']:
        return
    m = re.search(r'<link rel="canonical" href="https://safe21\.io/([^"]*)"', src)
    if not m:
        err(page, 'manca il <link rel="canonical"> o è malformato')
    elif m.group(1) != page:
        err(page, f'canonical punta a "{m.group(1)}" ma il file è "{page}"')

    og = re.search(r'<meta property="og:url" content="https://safe21\.io/([^"]*)"', src)
    if og and og.group(1) not in (page, page[:-5]):
        err(page, f'og:url "{og.group(1)}" non corrisponde a "{page}" '
                  f'né a "{page[:-5]}"')


# --------------------------------------------------------------------------
# 4. internal links and assets resolve
# --------------------------------------------------------------------------
def check_links(page, src):
    for m in re.finditer(r'(?:href|src)="([^"]+)"', src):
        url = m.group(1)
        if url.startswith(('http://', 'https://', 'mailto:', '#', 'data:', 'tel:')):
            continue
        target = url.split('#')[0].split('?')[0]
        if target and not (ROOT / target).exists():
            err(page, f'riferimento locale rotto: "{url}"')


# --------------------------------------------------------------------------
# 5. images: alt text, and declared size == real size
# --------------------------------------------------------------------------
def check_images(page, src):
    for m in re.finditer(r'<img\s+([^>]+?)/?>', src):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        src_attr = attrs.get('src', '')
        if not src_attr:
            continue                              # lightbox placeholder
        if 'alt' not in attrs:
            err(page, f'<img src="{src_attr}"> senza attributo alt')
        elif not attrs['alt'].strip():
            warn(page, f'<img src="{src_attr}"> ha alt vuoto')
        w, h = attrs.get('width'), attrs.get('height')
        if not (w and h):
            warn(page, f'<img src="{src_attr}"> senza width/height '
                       '(la pagina può saltare al caricamento)')
            continue
        if not HAVE_PIL or src_attr.startswith('http'):
            continue
        fp = ROOT / src_attr
        if not fp.exists():
            continue                              # already reported by check_links
        try:
            with Image.open(fp) as im:
                real = im.size
        except Exception as e:                    # noqa: BLE001
            err(page, f'immagine illeggibile {src_attr}: {e}')
            continue
        if (int(w), int(h)) != real:
            err(page, f'<img src="{src_attr}"> dichiara {w}x{h} ma il file è '
                      f'{real[0]}x{real[1]} — la pagina salterà al caricamento')


# --------------------------------------------------------------------------
# 6. structure: one h1, no heading level skips, no duplicate ids, safe links
# --------------------------------------------------------------------------
def check_structure(page, src):
    ids = re.findall(r'\sid="([^"]+)"', src)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        err(page, f'attributi id duplicati: {dupes}')

    if page not in EXPECTED['lang_not_it'] and not re.search(r'<html lang="it">', src):
        tag = re.search(r'<html[^>]*>', src)
        err(page, f'lang non è "it": {tag.group(0) if tag else "manca <html>"}')

    body = re.search(r'<body.*?</body>', src, re.S)
    body = body.group(0) if body else ''
    h1s = re.findall(r'<h1[^>]*>', body)
    if len(h1s) != 1:
        err(page, f'servono esattamente 1 <h1>, trovati {len(h1s)}')

    art = re.search(r'<article class="article-body">(.*?)</article>', src, re.S)
    if art:
        prev = 2
        for m in re.finditer(r'<h([2-6])[^>]*>', art.group(1)):
            lv = int(m.group(1))
            if lv > prev + 1:
                err(page, f'salto di livello nei titoli: h{prev} → h{lv}')
            prev = lv

    for m in re.finditer(r'<a\s+([^>]*target="_blank"[^>]*)>', src):
        if 'noopener' not in m.group(1):
            href = re.search(r'href="([^"]+)"', m.group(1))
            err(page, 'target="_blank" senza rel="noopener": '
                      f'{href.group(1) if href else m.group(1)[:60]}')

    for m in re.finditer(r'<button\s+([^>]*)>(.*?)</button>', body, re.S):
        if not strip_tags(m.group(2)) and 'aria-label' not in m.group(1):
            err(page, f'<button> senza testo né aria-label: {m.group(1)[:60]}')


# --------------------------------------------------------------------------
# 7. SEO lengths + date consistency + reading time
# --------------------------------------------------------------------------
def check_meta(page, src):
    d = re.search(r'<meta name="description" content="([^"]*)"', src)
    if not d:
        err(page, 'manca la meta description')
    elif len(d.group(1)) > 160:
        warn(page, f'meta description di {len(d.group(1))} caratteri '
                   '(>160, Google la tronca)')
    elif len(d.group(1)) < 50:
        warn(page, f'meta description molto corta: {len(d.group(1))} caratteri')

    t = re.search(r'<title>(.*?)</title>', src, re.S)
    if t and len(t.group(1)) > 70:
        warn(page, f'<title> di {len(t.group(1))} caratteri '
                   '(>70, può essere troncato nei risultati di ricerca)')

    byline = re.search(r'<p class="byline">(.*?)</p>', src, re.S)
    ld = re.search(r'"datePublished":\s*"(\d{4})-(\d{2})-(\d{2})"', src)
    if byline and ld:
        dm = re.search(r'(\d{1,2})\s+(' + '|'.join(MONTHS) + r')\s+(\d{4})',
                       byline.group(1))
        if dm:
            shown = (int(dm.group(1)), MONTHS[dm.group(2)], int(dm.group(3)))
            meta = (int(ld.group(3)), int(ld.group(2)), int(ld.group(1)))
            if shown != meta:
                err(page, f'data mostrata {shown[0]}/{shown[1]}/{shown[2]} '
                          f'diversa da JSON-LD datePublished '
                          f'{meta[0]}/{meta[1]}/{meta[2]}')

    art = re.search(r'<article class="article-body">(.*?)</article>', src, re.S)
    rt = re.search(r'(\d+)\s*min di lettura', src)
    if art and rt:
        words = len(strip_tags(art.group(1)).split())
        est = max(1, round(words / 200))
        if abs(int(rt.group(1)) - est) > 2:
            warn(page, f'dichiara {rt.group(1)} min ma ~{words} parole '
                       f'suggeriscono ~{est} min')


# --------------------------------------------------------------------------
# 8. footer must be identical everywhere
# --------------------------------------------------------------------------
def check_footers(pages):
    baseline, baseline_page = None, None
    for page in pages:
        src = read(page)
        m = re.search(r'<h4[^>]*>\s*(?:Contatti|.*?footer\.contact.*?)\s*</h4>(.*?)</div>',
                      src, re.S)
        if not m:
            err(page, 'colonna "Contatti" del footer non trovata')
            continue
        hrefs = re.findall(r'href="([^"]+)"', m.group(1))
        if baseline is None:
            baseline, baseline_page = hrefs, page
        elif hrefs != baseline:
            err(page, f'link del footer diversi da {baseline_page}:\n'
                      f'      atteso:  {baseline}\n'
                      f'      trovato: {hrefs}')


# --------------------------------------------------------------------------
# 9. blog.html cards <-> JSON-LD <-> article files (and matching metadata)
# --------------------------------------------------------------------------
def check_index(pages):
    src = read('blog.html')
    cards = re.findall(r'<a class="post-card" href="([^"]+)">', src)
    articles = set(pages) - NON_ARTICLE

    missing = sorted(articles - set(cards))
    if missing:
        err('blog.html', f'articoli senza card nell\'indice: {missing}')
    dangling = sorted(set(cards) - articles)
    if dangling:
        err('blog.html', f'card che puntano a file inesistenti: {dangling}')
    if len(cards) != len(set(cards)):
        err('blog.html', 'ci sono card duplicate')

    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?"@type":\s*"Blog".*?\})\s*</script>',
                  src, re.S)
    if m:
        try:
            urls = [b['url'].replace('https://safe21.io/', '')
                    for b in json.loads(m.group(1)).get('blogPost', [])]
            if set(urls) != set(cards):
                err('blog.html', 'la lista JSON-LD non corrisponde alle card:\n'
                                 f'      JSON-LD: {urls}\n'
                                 f'      card:    {cards}')
            elif urls != cards:
                err('blog.html', 'JSON-LD e card hanno lo stesso contenuto ma '
                                 'ordine diverso — devono coincidere')
        except (json.JSONDecodeError, KeyError) as e:
            err('blog.html', f'JSON-LD del blog non leggibile: {e}')

    # each card's metadata must match the article page it links to
    pattern = (r'<a class="post-card" href="([^"]+)">.*?<span class="tag">(.*?)</span>\s*'
               r'<span>(.*?)</span>\s*<span>(.*?)</span>.*?<h2>(.*?)</h2>')
    for href, tag, date, rtime, title in re.findall(pattern, src, re.S):
        if not (ROOT / href).exists():
            continue
        asrc = read(href)
        h1 = re.search(r'<h1>(.*?)</h1>', asrc, re.S)
        if h1:
            a_title = unescape_basic(strip_tags(h1.group(1)))
            c_title = unescape_basic(strip_tags(title))
            if a_title != c_title:
                err('blog.html', f'titolo della card diverso dall\'<h1> di {href}:\n'
                                 f'      card:     {c_title!r}\n'
                                 f'      articolo: {a_title!r}')
        byline = re.search(r'<p class="byline">(.*?)</p>', asrc, re.S)
        if byline:
            bt = strip_tags(byline.group(1))
            if date.strip() not in bt:
                err('blog.html', f'data della card "{date.strip()}" non trovata '
                                 f'nella byline di {href} ("{bt}")')
            if rtime.strip() not in bt:
                err('blog.html', f'minuti di lettura della card "{rtime.strip()}" '
                                 f'non corrispondono alla byline di {href} ("{bt}")')
        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', asrc, re.S)
        if eyebrow:
            a_tag = unescape_basic(strip_tags(eyebrow.group(1))).lower()
            c_tag = unescape_basic(strip_tags(tag)).lower()
            if a_tag != c_tag:
                err('blog.html', f'categoria della card diversa da quella di {href}: '
                                 f'card={c_tag!r} articolo={a_tag!r}')


# --------------------------------------------------------------------------
# 10. sitemap, robots, security.txt, PGP key, CHANGELOG
# --------------------------------------------------------------------------
def check_site_files(pages):
    sm = read('sitemap.xml')
    try:
        import xml.dom.minidom
        xml.dom.minidom.parseString(sm.encode())
    except Exception as e:                        # noqa: BLE001
        err('sitemap.xml', f'XML non valido: {e}')

    listed = {(u or 'index.html') for u in
              re.findall(r'<loc>https://safe21\.io/([^<]*)</loc>', sm)}
    missing = sorted(set(pages) - listed)
    if missing:
        err('sitemap.xml', f'pagine assenti dalla sitemap: {missing}')
    extra = sorted(listed - set(pages))
    if extra:
        err('sitemap.xml', f'la sitemap elenca file inesistenti: {extra}')

    for loc, lastmod in re.findall(
            r'<loc>https://safe21\.io/([^<]*)</loc>\s*<lastmod>([^<]+)</lastmod>', sm):
        fname = loc or 'index.html'
        if (ROOT / fname).exists():
            dp = re.search(r'"datePublished":\s*"([\d-]+)"', read(fname))
            if dp and lastmod < dp.group(1):
                err('sitemap.xml', f'{fname}: lastmod {lastmod} precede '
                                   f'datePublished {dp.group(1)}')

    if 'Sitemap:' not in read('robots.txt'):
        err('robots.txt', 'manca la direttiva Sitemap:')

    sec = read('.well-known/security.txt')
    for field in ('Contact:', 'Expires:'):
        if field not in sec:
            err('security.txt', f'manca il campo obbligatorio {field}')

    pgp = read('safe21-pgp.asc')
    if 'PRIVATE KEY' in pgp:
        err('safe21-pgp.asc', '*** CONTIENE UNA CHIAVE PRIVATA — NON PUBBLICARE ***')
    if 'PUBLIC KEY' not in pgp:
        err('safe21-pgp.asc', 'non sembra una chiave pubblica')

    cl = read('CHANGELOG.md')
    nums = [int(n) for n in re.findall(r'^## \[(\d+)\]', cl, re.M)]
    if nums and nums != list(range(nums[0], nums[0] - len(nums), -1)):
        err('CHANGELOG.md', f'numerazione non consecutiva: {nums[:12]}...')
    for n in re.findall(r'^## \[(\d+)\].*?\n\n\*\*Date:\*\*[^\n]*\n\*\*Status:\*\*[^\n]*'
                        r'(?:non ancora|not yet|awaiting)[^\n]*', cl, re.M | re.S):
        warn('CHANGELOG.md', f'la voce #{n} risulta ancora non pubblicata')

    titles = {}
    for page in pages:
        t = re.search(r'<title>(.*?)</title>', read(page))
        if t:
            titles.setdefault(t.group(1), []).append(page)
    for t, ps in titles.items():
        if len(ps) > 1:
            err('generale', f'<title> duplicato su {ps}: {t!r}')


# --------------------------------------------------------------------------
def css_matrix():
    """Regenerate the per-page CSS table used in CONTRIBUTING.md.

    The <style> blocks diverged when unused CSS was trimmed page by page, so a
    template picked at random may be missing what a new article needs. Printed
    as Markdown, ready to paste over the table in the guide.
    """
    feats = [('.callout', '`.callout`'), ('figure.source', '`figure.source`'),
             ('.table-wrap', '`.table-wrap`'), ('a.inline', '`a.inline`'),
             ('.footnote', '`.footnote`'), ('.lightbox-overlay', 'lightbox'),
             ('.article-body code', '`code`')]
    rows = []
    for page in sorted(ROOT.glob('blog-*.html')):
        style = style_of(page.read_text(encoding='utf-8'))
        cells = ['✅' if re.search(re.escape(sel) + r'\s*[,{:]', style) else '—'
                 for sel, _ in feats]
        # sort by how complete the page is: the fullest one is the best template
        rows.append((cells.count('✅'), page.stem, cells))
    rows.sort(reverse=True)

    print('| Pagina | ' + ' | '.join(label for _, label in feats) + ' |')
    print('|---|' + ':--:|' * len(feats))
    for _, name, cells in rows:
        print(f'| `{name}` | ' + ' | '.join(cells) + ' |')
    print(f'\nTemplate consigliato: `{rows[0][1]}.html` '
          f'({rows[0][0]}/{len(feats)} blocchi).')
    return 0


def main():
    if '--css-matrix' in sys.argv:
        return css_matrix()

    pages = sorted(p.name for p in ROOT.glob('*.html'))
    if not pages:
        print(f'Nessuna pagina HTML trovata in {ROOT}')
        return 1

    for page in pages:
        src = read(page)
        check_nesting(page, src)
        check_jsonld(page, src)
        check_canonical(page, src)
        check_links(page, src)
        check_images(page, src)
        check_structure(page, src)
        check_meta(page, src)

    check_footers(pages)
    check_index(pages)
    check_site_files(pages)

    if not HAVE_PIL:
        skipped.append('dimensioni immagini (manca Pillow: pip install Pillow)')

    print(f'\nSAFE21 — audit di {len(pages)} pagine\n' + '=' * 60)

    if errors:
        print(f'\nERRORI ({len(errors)}) — da correggere prima del push\n')
        for page, msg in errors:
            print(f'  [{page}] {msg}')
    if warnings:
        print(f'\nAVVISI ({len(warnings)}) — da valutare, non bloccanti\n')
        for page, msg in warnings:
            print(f'  [{page}] {msg}')
    if skipped:
        print(f'\nCONTROLLI SALTATI ({len(skipped)})\n')
        for s in skipped:
            print(f'  {s}')

    print()
    if errors:
        print(f'✗ {len(errors)} errori da correggere.')
    else:
        print('✓ Nessun errore. Si può pushare.'
              + (f' ({len(warnings)} avvisi da valutare.)' if warnings else ''))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
