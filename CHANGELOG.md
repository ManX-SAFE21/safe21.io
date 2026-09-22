# CHANGELOG

All notable changes to the SAFE21 website are documented here.
One numbered entry per task.

## [43] — Product renamed from "BAL Easy Heirs" to "Easy Heirs"

**Date:** 2026-09-22
**Status:** Delivered and live (commit `d3b8b4c`, pushed to `main`)

Client asked for the plugin to be called simply **Easy Heirs** everywhere, on
the site and in the plugin's own repository. Only the product name changed:
every reference to **BAL** as the partner protocol ("la lista eredi per BAL",
"BAL — Bitcoin After Life") was left untouched — 7 of them survive in the
article, as intended.

- **`blog-bal-easy-heirs.html`** (11 replacements) — `<title>`, `<h1>`,
  `og:title`, JSON-LD `headline`, the body copy, the image `alt` and the file
  header comments.
- **`blog.html`** (2) — the card heading and the matching JSON-LD entry.

Three things deliberately NOT renamed, agreed with the client beforehand:

- **The article URL** stays `blog-bal-easy-heirs.html`. It is already
  published and indexed; renaming it would break the live link, the canonical
  and the sitemap entry for no reader-visible gain.
- **The plugin's package folder** stays `bal_easy_heirs/`. It is the
  identifier Electrum keys the plugin by: renaming it would force everyone
  who already installed it to remove and re-add the plugin.
- **The infographic itself** still reads "BAL Easy Heirs" — the client chose
  to keep the image as it is. Its `alt` was updated anyway, so the article
  text stays consistent for screen readers.

Verified: `<title>`, `<h1>`, `og:title` and JSON-LD headline all match; the
index card and its JSON-LD entry match each other; zero "BAL Easy" left on
either page; audit clean.

## [42] — Extract the blog's shared CSS and JS into two files

**Date:** 2026-09-22
**Status:** Delivered and live (commit `456c49f`, pushed to `main`)

Client asked whether the code could be simplified and made shorter. Measured
first: the Electrum plugin had almost no duplication worth removing (~2% of
3,765 lines), but the blog carried ~525 identical lines in every page — the
same stylesheet, header, footer and scripts copied ten times over.

Extracted the two parts that can be shared without a build step:

- **New `blog.css`** (599 lines) — the union of every blog page's inline
  stylesheet. Built by comparing all ten pages rule by rule: 148 distinct
  selectors, of which only 6 differed. An automated coverage check confirmed
  no declaration was lost.
- **New `blog.js`** (150 lines) — mobile menu, theme switch and image
  lightbox. Each is guarded, so pages without a figure simply skip the
  lightbox.
- **All 10 blog pages** now load those two files instead of inlining them.
  The pre-paint theme script stays inline in every `<head>`: moving it out
  would reintroduce the theme flash on load.
- **Header and footer stay duplicated** — deduplicating them would need a
  build step or client-side injection, and injecting them hurts SEO and
  no-JS readers. That trade-off is deliberate.

Per-article differences preserved with modifier classes rather than being
flattened: `figure.source.inline` (mid-article figure margins) and
`.article-body.dense` (tighter lists), both applied to `blog-dadi-semplicita`
and `blog-seed-mai-online`.

Three deliberate harmonizations, each verified as an improvement rather than
a regression: callouts now carry the light-theme card shadow on every page
(previously 3 of 9); `.callout p:last-child` drops its trailing margin on two
more pages; and `<code>` renders as a monospace chip on
`blog-bitcoin-persi-dovere` (the rule previously lived only in the password
article).

Verified by loading each page's pre-change version from git in an iframe
beside the new one at identical width and diffing the computed styles of
every rendered element across 34 properties: 7 of 10 pages matched exactly,
and the only differences on the other 3 were the three harmonizations above.
All 10 pages: blog.css applied, no inline `<style>` left, menu/theme/lightbox
working, zero JS errors.

Net effect: the blog went from 10,303 lines to 6,162 (-4,141).

Docs and tooling brought in line with the new structure:

- **`CONTRIBUTING.md`** — §1 no longer claims the pages are self-contained and
  now warns of the opposite hazard (editing blog.css changes every page at
  once); §3's per-page CSS table is replaced, since every block is now
  available everywhere; §2 and §5 point at blog.css instead of a per-page
  `<style>`.
- **`tools/audit.py`** — `style_of()` reads blog.css for pages that link it,
  the `<article class="article-body">` match now tolerates modifier classes
  (otherwise the heading-level check would have silently stopped running on
  the two pages that gained `.dense`), and `--css-matrix` is repurposed to
  confirm the shared stylesheet covers every block.

## [41] — Blog index: cover thumbnails on each article card

**Date:** 2026-09-13
**Status:** Delivered and live (commit `c4a2606`, pushed to `main`)

Client asked to show each article's own image on the right side of its card
in the blog list (`blog.html`).

- Each `.post-card article` is now a flex row: the existing text wrapped in a
  new `.post-text` div on the left, and a `.post-thumb` `<img>` on the right
  showing the article's own cover.
- **7 of 9 articles have a cover; the 2 without an image were left as
  full-width text on the client's explicit choice** (`blog-bitcoin-persi-dovere`
  and `blog-cosa-succede-ai-tuoi-bitcoin`) — the layout degrades gracefully.
- Thumbnail is a fixed **16:9 box** (`clamp(200px, 30%, 300px)` wide),
  `object-fit: cover`, vertically centred. All covers are ~16:9 except
  `articolo-x-sparkkitty.jpg` (portrait) which crops cleanly.
- On mobile (≤760px) the row becomes `column-reverse`: cover on top at 16:9,
  text below.
- `.post-thumb` added to the theme-transition list (it has a themed border);
  not to the box-shadow list (it sits inside the card that already carries the
  shadow).

**Two flexbox/grid min-size gotchas hit and fixed during build** (both caught
in the browser, computed styles not screenshots):
1. `min-width: 0` on `.post-thumb` — without it the flex default
   `min-width:auto` = the image's intrinsic width (~1376px) ignored
   `flex-basis` and blew the thumbnail up to full size.
2. `min-width: 0` on `.post-card` — as a grid item its default
   `min-width:auto` held it open at the flex row's min-content width (~2400px),
   overflowing the page with a horizontal scrollbar.
   Also: `aspect-ratio` + `height:auto` on the img override the presentational
   `height` attribute (which otherwise forced a 768px-tall card).

The `width`/`height` attributes on each thumbnail document the source ratio
for the audit; CSS controls the rendered box.

**alt="" on all 7 thumbnails is deliberate** and correct: each thumbnail sits
inside a card that is one link whose `<h2>` already names the destination, so
a non-empty alt would double-announce for screen-reader users. `tools/audit.py`
flags these as 7 "alt vuoto" advisories — expected, non-blocking.

**Verified** at 1200px and 375px in a fresh browser tab: no horizontal
scroll; thumbnails render at 300×169 (desktop) / full-width 16:9 (mobile);
the 2 image-less cards render as clean full-width text; light theme borders
and card shadow correct; no console errors; audit clean (0 errors).

## [40] — Small wording revision in "Il tema di fondo"

**Date:** 2026-09-12
**Status:** Delivered and live (commit `1b59cf6`, pushed to `main`)

Client sent another small revision of the same draft, changing a few words
in the closing "Il tema di fondo: dati contro comodità" section:

- "paghi poco *oggi* in commissioni" &rarr; "paghi poco in fatica e
  commissioni adesso"
- "paghi potenzialmente tanto *domani*" &rarr; "paghi potenzialmente tanto in
  futuro"
- "quel \"domani\"" &rarr; "quel futuro"

Compared the new draft against the one used for #38 word-by-word; this was
the only change. Single-paragraph edit, no structural change.

## [39] — Shared links now carry the theme they were copied in

**Date:** 2026-09-12
**Status:** Delivered and live (commit `458d5a4`, pushed to `main`)

Client asked: when sharing an article link in light or dark mode, could the
person opening it see the same mode automatically?

- **Clicking the toggle now stamps the choice into the address bar** via
  `history.replaceState` (no reload): `...html` &rarr; `...html?theme=light`
  (or `?theme=dark`). Copying the link at that moment carries the theme.
- **The pre-paint script now reads `?theme=` first**, before falling back to
  `sessionStorage`. A link opened with no session state of its own (a fresh
  visitor, a different browser) renders in the linked theme immediately, no
  flash. An explicit link choice is also written into `sessionStorage`, so it
  survives navigating to another page within the same visit exactly like a
  manual toggle would.
- **Only an explicit click rewrites the URL** — the pre-paint sync on
  ordinary page load never does, so a plain link keeps working exactly as
  before (opens dark, the default).
- **`canonical` and `og:url` are untouched**, deliberately: they are static
  tags with no query string, so `?theme=` never creates a second indexable
  URL for the same page.

Applied identically to **all 9 article pages** — both the pre-paint script
and the click-handler block were byte-identical across every one of them,
hashed before editing.

**Known limitation, not addressed:** the theme in the URL does not propagate
to internal links (e.g. "&larr; Tutti gli articoli") — clicking through loses
it, since sessionStorage from the current visit is the only thing carrying a
choice between pages. Flagged to the client; left as-is since it wasn't
asked for and would need every internal link on every page changed.

**Verified**, each in a fresh browser tab (avoiding the stale-screenshot
harness quirk from #38): clicking the toggle twice on
`blog-comprare-bitcoin-kyc-p2p` updated the URL to `?theme=light` then
`?theme=dark`; opening `?theme=light` cold (never clicked, no session state)
rendered light immediately (`bodyBg` correct, screenshot confirmed);
opening `?theme=dark` cold rendered dark; `canonical`/`og:url` unchanged in
both cases; no console errors. `tools/audit.py` clean, 0 errors, no new
advisories.

## [38] — "Comprare Bitcoin nel 2026": article expanded with client's revised draft

**Date:** 2026-09-12
**Status:** Delivered and live (commit `4751252`, pushed to `main`)

Client sent a more detailed revision of the same article
(comprare-bitcoin-kyc-vs-p2p.md, updated), asking to publish it. Same cover
and infographic as #36 (confirmed byte-identical against the originals
before reusing them — no reconversion needed).

Content roughly doubled (1,375 &rarr; 2,748 words; 7 &rarr; 14 min):

- New material folded into the existing sections: EU KYC-exemption threshold
  context, data-retention/authority-sharing detail, and a closing line that
  P2P is "the original way" Bitcoin was built for.
- New subsections: **"Un inciso sul rapimento da chiave inglese"** (the xkcd
  $5-wrench-attack origin and real-world pattern), **"Come funziona uno
  scambio P2P, in breve"** (7-step walkthrough + dispute handling), **"Le
  varianti del P2P"** (on-chain / Lightning / in-person), **"Perché il P2P
  costa di più (e a volte di meno)"** (the 5% premium flips in the seller's
  favour).
- New sections: **"Un esempio di truffa indiretta"** (a worked Mario/Luigi
  story), **"Un consiglio pratico importante"** inside the "cosa fare"
  section (never self-return a mistaken transfer — use the bank's formal
  chargeback channel instead), **"Scenari d'uso"** (5 reader profiles),
  **"Obiezioni comuni"** (3 myths addressed), **"Il tema di fondo: dati
  contro comodità"**, and a closing **glossary** of 11 terms.
- The comparison table stays represented by the infographic (unchanged from
  #36); the extra "In sintesi" bullet about combining both channels was
  folded in.

**Structure and both images unchanged** from #36 — only the article body was
rebuilt; `<head>`, site header, footer and the two images were preserved
byte-for-byte. `blog.html` card reading time bumped 7&rarr;14 min to match.

**Verified:** `tools/audit.py` clean (0 errors, 11 pages, no new advisories).
`<h1>` = JSON-LD headline; 13 `<h2>` + 5 new `<h3>`; still exactly one
`.callout` and one `.footnote`; both images still load at their real pixel
size; lightbox still opens/closes correctly; 375px no sideways scroll; no
console errors. Light/dark theme re-verified in a clean tab (an earlier
check in a heavily-reused test tab showed a stale, dark screenshot with
correct-looking light-theme computed styles underneath — closing that tab
and opening a fresh one confirmed the page itself was always correct; the
staleness was the test harness, not the site).

## [37] — Lightbox: images now fit the screen instead of overflowing it

**Date:** 2026-09-12
**Status:** Delivered and live (commit `95ebc99`, pushed to `main`)

Client noticed that clicking the mid-article infographic on the new KYC/P2P
article (2391&times;1341 px) opened it larger than the screen, forcing a
scroll to see the whole thing.

The lightbox showed every image at its exact natural pixel size
(`max-width: none`), a deliberate choice from earlier in the project. That is
fine for an image smaller than the viewport, but breaks down for a large one
on a small screen.

**Fix:** `.lightbox-overlay img` now caps at `calc(100vw - 48px)` /
`calc(100vh - 48px)` (the -48px matches the overlay's own 24px padding on
each side) instead of `max-width: none`, with `width/height: auto` still in
place so the aspect ratio is preserved. Net effect: an image smaller than the
screen still renders 1:1 exactly as before; one larger than the screen now
scales down to fit, never up.

Applied identically to **all 7 pages that have a lightbox** — this CSS block
was byte-identical across every one of them, checked before editing:
`blog-password-electrum`, `blog-safe21-will-executor`, `blog-bal-easy-heirs`,
`blog-dadi-semplicita`, `blog-seed-mai-online`, `blog-caso-liquid`,
`blog-comprare-bitcoin-kyc-p2p`.

**Verified:** the 2391&times;1341 infographic on a 1000&times;700 viewport now
renders at 952&times;534 with no scroll needed; the same image on a
375&times;812 mobile viewport fits at 327&times;183. A smaller image
(1376&times;768) on a 1600&times;1000 viewport still renders at its exact
natural size (1:1 unchanged). `tools/audit.py` clean; no console errors.

## [36] — New blog article: "Comprare Bitcoin nel 2026: KYC o peer-to-peer?"

**Date:** 2026-09-12
**Status:** Delivered and live (commit `7a9e422`, pushed to `main`)

Client supplied a finished draft (comprare-bitcoin-kyc-vs-p2p.md) plus a cover
illustration and a 16:9 comparison infographic, asking to publish it with the
cover at the top and the infographic "a metà articolo".

- **New `blog-comprare-bitcoin-kyc-p2p.html`.** Tag "Guide · Comprare
  Bitcoin", 12 settembre 2026, 7 min (1,375 words). Sections: why this matters
  now (MiCA/CASP licensing) → the KYC channel (pros/cons) → the P2P channel
  (pros/cons) → **comparison infographic** → good P2P habits → what to do if
  something goes wrong → tax obligations → summary.
- **The draft's disclaimer blockquote became the article's one `.callout`**
  ("Nota importante" — descriptive only, not tax/legal advice), placed right
  after the cover, and its closing tax-obligations paragraph became the
  `.footnote`.
- **The draft's own "Vantaggi e svantaggi a confronto" Markdown table was
  dropped in favour of the supplied infographic image**, placed at exactly
  that point in the article (the literal midpoint of its section list) —
  showing the same comparison twice, once as prose-table and once as image,
  would have been redundant. The infographic's `alt` text spells out every
  row for accessibility and search, since the data itself only exists as
  pixels.
- **Both images converted to WebP** with the size-appropriate method per
  `CONTRIBUTING.md` §4: the cover (soft-gradient illustration) as lossy
  quality 95 → 44 KB; the infographic (flat colour + text) as **lossless** →
  71 KB, chosen because it was smaller than every lossy setting tried and
  keeps the on-image text pixel-perfect.
- **Template: `blog-safe21-will-executor.html`** (figure + lightbox, one
  callout, footnote, inline links — no dead CSS introduced).
- **`blog.html`** — new `.post-card` at the top + matching `BlogPosting`
  prepended to the JSON-LD list. **`sitemap.xml`** — new `<url>`; `blog.html`
  lastmod bumped to 2026-09-12.

**Verified:** `tools/audit.py` — 0 errors across 11 pages, no new advisories.
In the browser: `<h1>` = JSON-LD headline; both images load at their real
pixel size; exactly one callout and one footnote; lightbox opens the
infographic at 2391×1341 and closes on Escape; light theme gives the callout
and figure the same `--card-shadow`; at 375 px no sideways scroll; no console
errors. On `blog.html` the new card is first and its date, category and
reading time match the article.

## [35] — New blog article: "Il caso Liquid: perché per l'eredità consigliamo BAL Protocol"

**Date:** 2026-09-12
**Status:** Delivered and live (commit `0825b83`, pushed to `main`)

Client asked to adapt the Bitcoin After Life article "Liquid Network's $320M
Lesson: Why BAL Only Builds on Bedrock" (bitcoin-after.life, 12 September 2026)
for the SAFE21 blog: in Italian, as simple as the other articles, with the
angle that this incident is exactly why SAFE21 recommends Bitcoin After Life as
its inheritance service, and why SAFE21 chose to build its own Will-Executor
server. Cover image to follow the blog's visual style (reference given:
`blog-password-electrum`).

- **New `blog-caso-liquid.html`.** Tag "Eredità Bitcoin", 12 settembre 2026,
  6 min (1,230 words). Sections: what happened on Liquid (6 Sept 2026, ~4,000
  BTC / ~$320M, most returned, ~$47M still held at the time of writing) → what
  broke, explained for beginners (a sidechain's cached crypto checks let
  unbacked L-BTC be minted and swapped for real BTC; Bitcoin itself held) →
  why this matters more for an inheritance, which must work for decades →
  **"Ecco perché consigliamo Bitcoin After Life"** (the single callout: BAL
  Protocol's four rules — no sidechains, no Layer 2, no experimental scripts,
  no new wallet — then its two pillars, Electrum and nLockTime) →
  **"Ed è per questo che abbiamo costruito un Will-Executor"** (what an
  attacker cannot do to an executor; on-chain fee paid only on confirmation;
  links to we.safe21.io and to the #29 article) → four practical takeaways →
  sources + disclaimer.
- **Editorial choices.** Title kept to exactly 70 characters with the
  "— SAFE21" suffix (the audit's limit) and uses "BAL Protocol" rather than
  bare "BAL", per the client's earlier instruction (#22). "Bitcoin After
  Life" and "Will-Executor" left untranslated. The source's "atomic bombs /
  AI" section is condensed into the fourth takeaway ("Verifica"). A sentence
  crediting Blockstream's response was kept, as in the source, so the piece
  is not read as an attack on them. Incident figures are **attributed to
  public reporting** (BAL article + Chainalysis analysis in the footnote), not
  independently verified; the footnote says the figures reflect reporting at
  the time of writing.
- **Cover image (`images/copertina-caso-liquid.webp`), drawn for this
  article.** Metaphor taken from the source's title: Bitcoin's base layer as
  bedrock that holds, with the Bitcoin coin resting on it, while a newer
  deck built on top of the same bedrock has snapped and is shedding
  fragments. Same language as the other covers: navy ground, teal line-art
  with a soft glow, one orange Bitcoin accent, teal corner glow, no text
  baked in. Built as SVG, rendered with headless Chrome at 2x (3200×1800) and
  downscaled to 1600×900 for clean edges; checked at 672 px, the real column
  width, for legibility. WebP quality 95 = **28 KB** (lossless was 115 KB —
  soft glows favour lossy here).
- **Template: `blog-safe21-will-executor.html`**, not the password article:
  it carries exactly the CSS blocks this page uses (figure + lightbox, one
  callout, footnote, inline links) and none it does not, so no dead CSS was
  introduced.
- **`blog.html`** — new `.post-card` at the top + matching `BlogPosting`
  prepended to the JSON-LD list. **`sitemap.xml`** — new `<url>`; `blog.html`
  lastmod bumped to 2026-09-12.

**Verified:** `tools/audit.py` — 0 errors across 10 pages; the new page raises
no advisories. In the browser: `<h1>` = JSON-LD headline; cover loads at
1600×900; exactly one callout; footer carries the 4 Contatti links; lightbox
opens the cover at 1:1 and closes on Escape with scroll unlocked; light theme
gives the callout and figure the same `--card-shadow`; at 375 px no sideways
scroll; no console errors. On `blog.html` the new card is first and its date,
category and reading time match the article.

## [34] — "Dadi o software?": added a hero cover image

**Date:** 2026-08-23
**Status:** Delivered and live (commit `a18dbd4`, pushed to `main`)

Client supplied a cover illustration (dice + phone/seed-phrase graphic, PNG
1200×675) and asked for it to be converted to WebP and placed at the top of
`blog-dadi-semplicita.html`, above the existing text.

- **Image conversion.** Tried lossless first (this image has soft glows/
  gradients, unlike the flat-colour chart in #31) — it came out at 387 KB,
  worse than every lossy setting. Lossy quality 90 won: 1200×675 PNG (642 KB)
  → **29.5 KB** WebP. Checked the title text at actual size after compression;
  no visible artifacts. Saved as `images/copertina-dadi-o-software.webp`.
- **New `<figure class="source">`** inserted as the first element inside
  `.article-body`, before the opening paragraph — same pattern as the hero
  figures in #29/#31. `loading="eager"` (it's above the fold), `alt` describes
  the illustration's content. The article's original mid-body infographic
  (`infografica-dadi-vs-software.png`, unchanged) still sits where it was.
- **`og:image` and JSON-LD `image`** added — this page had neither before,
  since it previously had no hero image. `dateModified` bumped to 2026-08-23.
  `sitemap.xml` `lastmod` bumped to match.

**Verified:** `tools/audit.py` clean (0 errors, same 9 pre-existing
advisories). Both figures render; lightbox opens the new cover at natural
1200×675 and closes on Escape. Checked in light and dark theme (the
illustration's own background is dark navy, so it does not visually clash with
the light theme). Checked at 375px — layout unaffected, no sideways scroll.
No console errors.

## [33] — tools/audit.py: automated pre-push checks, and one CSS inconsistency closed

**Date:** 2026-08-23
**Status:** Delivered and live (commit `77b3caf`, pushed to `main`)

Follow-up to #32. The guide told a reader what to check by hand; this makes the
machine do it, so the same mistakes cannot come back and cost time.

- **`tools/audit.py`** — read-only, no arguments, `python tools/audit.py`.
  Covers the failure modes that produce no visible error on their own: HTML
  nesting, JSON-LD validity and `headline` vs `<h1>`, canonical/`og:url`,
  unresolved links and assets, missing `alt`, declared `width`/`height` vs the
  real file, footer parity across every page, the card ↔ JSON-LD ↔ sitemap ↔
  file cross-check, card metadata vs the article's own byline and eyebrow,
  duplicate ids, `target="_blank"` without `rel="noopener"`, heading-level
  skips, CHANGELOG numbering, robots/security.txt fields, and a guard that
  `safe21-pgp.asc` never contains a PRIVATE KEY block.
- **Two output levels.** ERRORE fails the run (exit 1, so it can be wired into
  CI); AVVISO is advisory and never fails. Currently: 0 errors, 9 advisories,
  all of them genuine over-length meta descriptions/titles on older pages.
- **No false positives, by design.** The known-correct exceptions —
  `index.html`'s `lang="en"` and its root canonical/`og:url` — are declared in
  an `EXPECTED` constant with the reason, rather than being reported every run.
  A checker that always shows the same three harmless errors stops being read.
- **`--css-matrix`** regenerates the per-page CSS table in `CONTRIBUTING.md`
  (sorted by completeness, so the fullest page is named as the recommended
  template) instead of leaving it to drift by hand.
- **Verified by injecting failures, not just by passing.** Ten broken states
  were introduced into a throwaway copy — wrong image height, headline/`<h1>`
  mismatch, dead link, missing `alt`, card date out of sync, a footer link
  removed, `target="_blank"` without `noopener`, duplicate id, a sitemap entry
  renamed, malformed JSON-LD — and all ten were caught, exit code 1. (The
  `alt` case looked like a miss at first; the test had stripped the attribute
  from the lightbox placeholder `<img src="">`, which the script skips on
  purpose. Removing it from a real image was reported correctly.)

- **CSS inconsistency from #32 closed.** `.callout` carried the light-theme
  shadow on 5 of the 7 article pages; `blog-dadi-semplicita.html` and
  `blog-seed-mai-online.html` were missing it. Added there, so every panel
  (`.callout`, `figure.source`, `.table-wrap`, plus page-specific `.checklist`
  / `.rule`) is now in both theme rules everywhere. Verified in light theme on
  both pages: the callout's computed shadow is now byte-identical to
  `figure.source` (`rgba(10, 15, 28, 0.06) 0px 1px 3px 0px`) and nothing else
  gained or lost a shadow; dark theme still resolves to `none`.
- **`CONTRIBUTING.md`** updated: the shadow rule is now stated as a rule rather
  than an exception, the CSS table is the script's own output, and the
  checklist marks with 🤖 the items the script already covers so only the
  visual checks are left to a human.

## [32] — CONTRIBUTING.md: how to build and publish a blog article

**Date:** 2026-08-23
**Status:** Delivered and live (commit `83d778a`, pushed to `main`)

Client asked whether the repo already documented how to create blog pages. It
did not: the only prose in the repo was `CHANGELOG.md`, which records *what*
was done rather than *how* to do it. The knowledge lived in per-page HTML
comments and in scattered changelog entries, so anyone opening the repo — or
the owner in six months — would have had to reconstruct it from the code.

Added `CONTRIBUTING.md` (Italian, per the client's choice; the "code and
comments in English" rule covers code, not operator documentation). Contents:

- **The 4 coordinated edits** an article needs (page, post-card, JSON-LD entry,
  sitemap block) plus the CHANGELOG entry — and the warning that skipping one
  fails silently rather than erroring.
- **Per-page CSS matrix.** Since the audit in #30 trimmed unused CSS page by
  page, the `<style>` blocks have diverged; the table records which of
  `.callout` / `figure.source` / `.table-wrap` / `a.inline` / `.footnote` /
  lightbox / `code` each page actually carries, so a template chosen at random
  may be missing what the new article needs. `blog-password-electrum.html` is
  the only superset and is named as the recommended template.
- **Image rules**: WebP, ~60 KB target, and *when* lossless beats lossy
  (flat-colour charts) versus the reverse (photographs), with the #31 numbers
  as the worked example. Plus the requirement that `width`/`height` match the
  real file, citing the layout-shift bug fixed in #30.
- **Known traps**: media queries must follow the base rules or they are dead
  CSS at equal specificity; dark mode hides shadow mistakes because
  `--card-shadow` is `none`; `index.html`'s `lang="en"` and root canonical are
  correct and will trip naive linters.
- **Cloudflare behaviours** that look like bugs: the 308 redirect from `.html`
  to the extensionless URL, `mailto:` obfuscation, and the homepage-with-200
  response for a path whose build is still running.
- **A pre-push checklist** and the `curl` one-liner to confirm a page is live.

**Correction made while writing it.** A claim carried over from the #30 notes —
that `.callout` is deliberately excluded from the `box-shadow` list — turned out
to be false when checked against the source: `.callout` *is* in that list on 5
of the 7 article pages, and absent only on `blog-dadi-semplicita` and
`blog-seed-mai-online`. The guide now documents the real, inconsistent state
instead. (See the open item below.)

**Open item, not acted on:** that inconsistency is genuine — in light theme the
callout carries a 1px 3px 6%-opacity shadow on 5 pages and none on 2. It is
barely perceptible and touching it means editing 2 pages' theme rules, so it
was left alone pending the client's call.

**Verified:** every file path, internal link and page name referenced in the
guide checked against the working tree — all resolve. The per-page CSS matrix
and the "5 of 7" shadow claim were both generated by parsing the actual
`<style>` blocks, not written from memory.

## [31] — New blog article: "La password di Electrum: perché 8 caratteri non bastano"

**Date:** 2026-08-23
**Status:** Delivered and live (commit `7c9c954`, pushed to `main`)

Client supplied a ZIP (`safe21-password-article`) with a ready Markdown draft
(`password-electrum-security.md`) and two PNG images: an illustrated cover and
a two-panel chart on password length vs. brute-force time. Client asked to
publish it on the blog, to convert the images to WebP, and to add a closing
note stating that the figures are estimates rather than precise measurements.

- **Image conversion.** Cover: 1376×768 PNG (150 KB) → WebP quality 95,
  **48.8 KB**. Chart: 2086×980 PNG (200 KB) → **lossless** WebP, **60.4 KB**.
  Lossless beat every lossy setting here (q95 was 144 KB) because the chart is
  flat-colour vector-style content, so the text stays pixel-perfect when a
  reader zooms it in the lightbox. Saved as
  `images/copertina-password-electrum.webp` and
  `images/grafico-password-lunghezza.webp`.
- **Two corrections to the supplied material**, both reported to the client:
  1. *Chart annotation was wrong.* The label read "16 caratteri ≈ 10 milioni
     di anni", but the curve it points at plots ≈1.26×10⁹ years — the label
     contradicted its own data by a factor of ~126. Under the chart's stated
     model (36 symbols, 100M attempts/s, average = half the keyspace),
     36¹⁶ / 2 / 10⁸ / 31 557 600 = 1.26 billion years. The label was redrawn
     in the image as "≈ 1,3 miliardi di anni", matching the plotted point and
     both panels. The example table's 16-character row was changed from
     "milioni di anni" to "miliardi di anni" for internal consistency.
  2. *Italian large-number names were wrong on both scales.* The draft called
     36¹² (4.7×10¹⁸) "quadrilioni" and 36¹⁶ (8×10²⁴) "quintilioni"; on the
     Italian long scale those words mean 10²⁴ and 10³⁰, and on the English
     short scale they mean 10¹⁵ and 10¹⁸ — wrong either way. Replaced with
     plain, unambiguous wording ("4,7 miliardi di miliardi", "8 milioni di
     miliardi di miliardi"), which also reads better for the article's stated
     audience of Bitcoin beginners.
- **New `blog-password-electrum.html`.** Built from
  `blog-safe21-will-executor.html` (figure + click-to-zoom lightbox pattern).
  Tag "Sicurezza · Password", 23 agosto 2026, 7 min. Sections: short answer →
  what the password actually protects → what happens if the file is copied →
  why length grows exponentially (+ the chart) → concrete examples (table) →
  random vs. human passwords → how long to go → SAFE21 checklist (callout) →
  the client's requested note on the figures being estimates → sources +
  non-custodial disclaimer.
- **Client cut during review.** The draft's section "E un Intel Core i9 a 10
  core e circa 5 GHz?" (heading, three paragraphs and a six-item list on why
  clock speed is not attempts/s) was removed at the client's request and
  replaced with a three-line concrete example placed under the table: with the
  same 100M attempts/s model, `k7m2v9pa` ≈ 4 hours, `t4v8m2q9k7x3` ≈ 750
  years, a random 16-character password ≈ 1.3 billion years — all three
  consistent with the chart and the table. The now-uncited Intel spec sheet
  was dropped from the sources list, and the reading time went 8 → 7 min
  (1,432 words) in both the byline and the blog.html card.
- **First data table on the blog.** No page had one before, so the shared
  stylesheet gained `.table-wrap` (a horizontally scrollable panel, so a wide
  table never makes the page itself scroll sideways on a phone) plus
  `table/th/td` rules and a monospace `code` chip for the password samples.
  `.table-wrap` was added to the two existing theme rules (the crossfade
  transition list and the `--card-shadow` list) so it behaves like the other
  panels in light mode. Table padding/size tighten inside the 760px query.
- **`blog.html`** — new `.post-card` at the TOP of the list, and matching
  `BlogPosting` entry prepended to the JSON-LD `blogPost[]` array (verified:
  card order and JSON-LD order match exactly).
- **`sitemap.xml`** — new `<url>` for the article; `blog.html` lastmod bumped
  to 2026-08-23.

- **Bug caught during verification.** The mobile table override was first
  injected into the existing `@media (max-width: 760px)` block, which sits
  *above* the appended base table rules — equal specificity, so the base
  padding won on source order and the override was dead (only the font-size
  appeared to work, because the base sets that on `table`, not on `th/td`).
  Moved the media query below the base rules; mobile padding now resolves to
  11px 13px as intended.

**Verified:** both audit scripts clean on the new page (HTML nesting, JSON-LD
validity, canonical/og:url, internal links, image alt text, declared image
dimensions vs. real files, footer link consistency across all 9 pages, sitemap
bidirectional check, heading hierarchy, reading time vs. word count). Rendered
in dark and light themes; lightbox, theme toggle and mobile drawer all work;
no console errors.

## [30] — Site-wide audit: fix wrong image dimensions, remove dead CSS

**Date:** 2026-08-19
**Status:** Delivered and live (commit `724595a`, pushed to `main`)

Client asked for a general check of the whole site/code for errors. Ran a
custom read-only audit script against all 8 HTML pages, covering: HTML tag
nesting, JSON-LD validity (+ headline/canonical/og:image cross-checks),
canonical/og:url vs actual filename, every internal href/src resolving to a
real file, every `<img>` having alt text and its declared width/height
matching the real file, footer link consistency across all pages,
sitemap.xml vs actual pages (both directions), blog.html post-cards vs
JSON-LD `blogPost[]` vs actual article files, CHANGELOG entry numbering,
security.txt/robots.txt required fields, and a check that `safe21-pgp.asc`
contains no private-key material. Also grepped for leftover TODO/FIXME/merge
markers/placeholder text (none found) and diffed post-card counts between
the local repo and the live site (matched).

**One real bug found, pre-dating this project's AI-assisted work (task
[18]/[19], June–July 2026):** `blog-dadi-semplicita.html`'s infographic
`<img>` declared `height="804"`, but the actual PNG on disk is 1440×725, not
1440×804 — a ~79px mismatch. Browsers reserve layout space from the declared
height before the image loads, so this caused a visible reflow (layout
shift) once the real image rendered. Fixed the declared `height` to match
the real file exactly; the image itself was not touched.

**Three audit-script false positives, no site issue:** the homepage's
canonical/og:url legitimately point to the bare root `https://safe21.io/`
(no path segment), and `index.html`'s `<html lang="en">` is correct because
the homepage ships in English and its i18n script rewrites `lang` at runtime
when the reader switches to Italian. Both confirmed correct by inspection.

**Dead CSS removed** (second pass, at the client's request). All of it was
leftover from copying the shared per-article `<style>` block wholesale:
- `blog.html` — the theme-crossfade and box-shadow rules listed `.callout`,
  `.checklist`, `.rule`, `figure.source`, none of which the index renders;
  trimmed to `.post-card`. Also dropped the unused `.btn-ghost` pair (the
  index has only the header's `.btn-primary`).
- `blog-dadi-semplicita.html` — removed the unused `.rules`/`.rule`/
  `.checklist` blocks, the unused `.callout.btc` variant, and the
  `.checklist` line in the mobile media query; trimmed `.post-card` out of
  the crossfade/box-shadow rules.
- `blog-seed-mai-online.html` — removed the unused `.article-body a.inline`
  rule (this article's prose carries no inline links) and trimmed
  `.post-card` out of the crossfade/box-shadow rules.

**Verification that the cleanup changed nothing.** Each edited page was
fingerprinted before and after: ~40 computed CSS properties plus the
bounding box of every element in the document, hashed into one digest per
page (confirmed deterministic by re-running on an unchanged page). All three
digests matched exactly — `blog.html` 86362845 (149 elements), the dice
article 344786962 (174), the seed article 3030340794 (230). Because
`--card-shadow` is `none` in dark mode, the shadow changes could only show
in **light** mode, so the original files were additionally extracted from
git into a second local server and the two versions compared side by side
in light theme: identical `box-shadow`/`transition`/link-decoration
inventories on all three pages.

That comparison caught a genuine mistake mid-edit: while trimming the dice
article's box-shadow rule, `.callout` was briefly added to a list it had
never been in, which would have given the callout panel a shadow it never
had (visible only in light mode). Reverted before the check — the callout
is a tinted panel, not a card, and is correctly in the *transition* list but
not the *box-shadow* one.

Everything else checked out clean: no broken internal links, no missing alt
text, all JSON-LD blocks valid and consistent with their page's headline/
canonical, sitemap.xml lists exactly the 8 real pages both ways, all 6 blog
articles have a post-card + matching JSON-LD entry in `blog.html` (order
consistent), footer links (Contatti: email, Blog, GitHub, Chiave PGP)
identical across all 8 pages, CHANGELOG numbering sequential with no gaps
(#1-#30), `security.txt`/`robots.txt` have their required fields, and
`safe21-pgp.asc` contains only a public key.

## [29] — New blog article: "SAFE21 diventa Will-Executor"

**Date:** 2026-08-19
**Status:** Delivered and live (commit `d2bb21d`, pushed to `main`)

Client supplied a ready Markdown draft (`Articolo_5/articolo-safe21-will-executor.md`)
announcing that SAFE21 now runs its own BAL Protocol Will-Executor
(we.safe21.io) and contributed an Umbrel OS packaging of it, plus a hero
infographic (PNG) to accompany it. Client also asked, mid-task, for a
closing note clarifying that the Umbrel install is currently manual, not yet
a one-click App Store install — added at the very end of the article body,
deliberately left unreconciled with the earlier "pochi clic" / "installi
l'app" phrasing per the client's explicit choice.

- **Image conversion**: the supplied PNG (2752×1536, 6.9 MB) was resized to
  2200×1228 and re-encoded as WebP (quality 81) to hit the client's ~60 KB
  target — landed at 60.6 KB, a 99% size reduction. Saved as
  `images/infografica-safe21-will-executor.webp`.
- **New `blog-safe21-will-executor.html`.** Built from
  `blog-bal-easy-heirs.html` (image + click-to-zoom lightbox pattern). Tag
  "Eredità Bitcoin", 19 agosto 2026, 7 min. Sections: how BAL's time-lock
  inheritance works (recap, numbered list) → what a Will-Executor is (callout
  box: what it can/cannot do) → why SAFE21 runs one (three H3 subsections:
  belief in decentralization, favorable risk/benefit with the on-chain fee
  incentive, and the Umbrel OS packaging) → how a reader can start (prepare
  an inheritance, or become a Will-Executor) → the client's honesty note on
  Umbrel's current manual install → closing links + non-custodial disclaimer
  (reused `.footnote` styling with a `<ul>` of three links, consistent with
  existing CSS — no new classes needed). `og:image` set (this article has
  real artwork, unlike #22/#23/#25).
- **`blog.html`** — new `.post-card` at the TOP of the list, and matching
  `BlogPosting` entry prepended to the JSON-LD `blogPost[]` array.
- **`sitemap.xml`** — new `<url>` block; bumped `blog.html` lastmod to
  2026-08-19.
- Verified: JSON-LD (index + article) parses as valid JSON, sitemap is
  well-formed XML, image resolves at its real 2200×1228 size in the figure
  and lightbox, both external CTA links (we.safe21.io, bitcoin-after.life)
  correct, no console errors.

## [28] — Footer link to SAFE21 open-source code (GitHub)

**Date:** 2026-08-17
**Status:** Delivered and live (commit `9395f18`, pushed to `main`)

Client asked for a footer link pointing to SAFE21's GitHub
(https://github.com/ManX-SAFE21), where the open-source code lives. Chosen
label communicates the purpose rather than just naming the platform.

- Added an external link in the footer "Contatti/Contact" column (between the
  Blog and PGP-key links) on **all six** pages: `index.html` and the five blog
  pages that existed plus `blog-bal-easy-heirs.html` (added in [25] while this
  task was in progress). `target="_blank"` + `rel="noopener noreferrer"`, with
  a `&nearr;` arrow to mark it as leaving the site (same convention as the
  Partner links).
- Label "Codice open source" (IT) / "Open-source code" (EN). On `index.html`
  this uses a new `footer.github` i18n entry; the homepage i18n applies via
  `innerHTML`, so the arrow entity is included in the Italian value too. Blog
  pages are Italian-static, so the label is written directly.
- No new files; footer stays consistent site-wide.


## [27] — Replace BAL Easy Heirs infographic with a lighter version

**Date:** 2026-08-15
**Status:** Delivered and live (commit `04bb14b`, pushed to `main`)

Client swapped the infographic added in [26] for a smaller, lighter version
of the same artwork: 1600×893 (was 2752×1536), 75 KB (was 138 KB) — same
file path, so no HTML `src` change needed.

- **`images/infografica-bal-easy-heirs.webp`** — replaced in place.
- **`blog-bal-easy-heirs.html`** — updated the `<img>` `width`/`height`
  attributes to match the new intrinsic size (1600×893), so the layout
  doesn't reserve the wrong aspect ratio before the image loads.
- Verified in the in-app browser: image loads at the new natural size,
  lightbox still opens/closes correctly.

## [26] — Add lead infographic to the BAL Easy Heirs article

**Date:** 2026-08-15
**Status:** Delivered and live (commit `5063df8`, pushed to `main`)

Client supplied an infographic ("BAL Easy Heirs: l'eredità Bitcoin offline e
sicura") already cleaned of its generator watermark and converted to WebP, to
open the article. Wired it in reusing the existing lightbox pattern.

- **`images/infografica-bal-easy-heirs.webp`** — new asset (WebP, 2752×1536,
  ~138 KB).
- **`blog-bal-easy-heirs.html`** — added the `figure.source` + lightbox CSS,
  the lightbox overlay markup, the click-to-zoom JS, and a `<figure>` at the
  very top of the article body (before the first paragraph) with a descriptive
  `alt`. Matches the image treatment used in `blog-dadi-semplicita.html`.
- Verified in the in-app browser: image loads (natural 2752×1536), it is the
  first element in the article, lightbox opens on click and closes on the X,
  no console errors.

## [25] — New blog article: "BAL Easy Heirs: prepara l'eredità dei tuoi bitcoin senza mai andare online"

**Date:** 2026-08-15
**Status:** Delivered and live (commit `3fafd30`, pushed to `main`)

Client asked for a ~5-minute article explaining the BAL Easy Heirs Electrum
plugin (github.com/ManX-SAFE21/BALeasyHeirs, now public): what it does, why it
is safe, that it works fully offline, and that the sheets must only be printed
on directly-connected (non-network, non-public) printers. Written as an
original SAFE21 piece from the plugin's own README/SECURITY.md and design
decisions; BAL framed as the companion protocol.

- **New file `blog-bal-easy-heirs.html`** — cloned from
  `blog-bitcoin-persi-dovere.html` (no image → no lightbox). Tag "Eredità
  Bitcoin", 15 ago 2026, 5 min. Sections: the problem → what it does → security
  by construction (offline, no PDF of seeds, password-gated, protected paper) →
  the printer rule → open source / verifiable signed releases → summary. Links
  to BAL, the GitHub repo, SECURITY.md, and the existing "seed mai online"
  article.
- **`blog.html`** — new `.post-card` at the TOP of the list, and matching
  `blogPost[]` entry prepended to the JSON-LD.
- **`sitemap.xml`** — new `<url>` block for the article.
- **`.claude/launch.json`** — added a local static-server config for previewing
  the site (dev-only; not deployed content).
- Verified in the in-app browser: article renders with no console errors, all
  links correct, light/dark toggle works (--ink #0A0F1C ↔ #F4F6F9), JSON-LD
  parses on both files, and the new card is first on the index.

## [24] — Publish SAFE21 OpenPGP public key (footer + security.txt)

**Date:** 2026-08-15
**Status:** Delivered and live (commit `538fbea`, pushed to `main`)

Client asked whether SAFE21's newly generated GPG key should be published on
the site. Decision: publish the **public** key as a trust/transparency signal
(consistent with the "dice vs software" article, which teaches readers to
verify GPG signatures). It is not used to sign email or files yet — purely a
credibility signal — so it is placed discreetly, not in the hero.

Key verified before publishing: OpenPGP ed25519, created 2026-08-15, UID
`SAFE21dev <info@safe21.io>`, fingerprint
`33E3 393D FB10 F4C4 5AE6 F1E8 206C 2011 4CA9 6172`. Confirmed the copied file
is a PUBLIC key block and byte-identical to the owner's exported public key.
The matching SECRET key stays offline with the owner and is never touched.

- **New `safe21-pgp.asc`** at the site root — the armored public key. Linked,
  not embedded; browsers show it as text/plain.
- **New `.well-known/security.txt`** (RFC 9116): `Contact` (info@safe21.io),
  `Encryption` (the .asc URL), `Preferred-Languages: it, en`, `Canonical`,
  `Expires` (2027-08-15), and the key fingerprint as a comment. This is the
  standard, auto-discovered location security researchers/tools look for.
- **Footer "Contatti/Contact" column** — added a "Chiave PGP" / "PGP key" link
  on every page: `index.html` (with a new `footer.pgp` i18n entry so it reads
  "PGP key" in EN and "Chiave PGP" in IT) and all five blog pages
  (`blog.html` + the four articles, Italian static). Footer stays consistent
  site-wide.
- Not added to `sitemap.xml`: the key file and security.txt are utility
  resources, not indexable content pages.
- Verified: security.txt has the required RFC 9116 `Contact` + `Expires`
  fields; the .asc link resolves to the public key; the footer link appears
  once per page; homepage i18n still switches EN/IT including the new label.

## [23] — New blog article: "Perdere i propri bitcoin non è solo un danno personale"

**Date:** 2026-08-15
**Status:** Delivered and live (commit `dc56694`, pushed to `main`)

Client supplied a ready Markdown draft with front matter and explicit
publishing instructions (`Articolo_4/blog-bitcoin-persi-dovere.md`) for a
fourth blog article, arguing that lost bitcoin — often framed as a harmless
"gift" to everyone else via scarcity — becomes a long-term risk if quantum
computing ever catches up with dormant, exposed-pubkey wallets, since only
coins held by living owners with working backups can be moved to safer
addresses over time.

- **New `blog-bitcoin-persi-dovere.html`.** Built from the
  `blog-dadi-semplicita.html` template (header/footer/theme-toggle/tokens
  identical to the rest of the blog). Sections: the immediate scarcity
  effect, the quantum/dormant-wallet risk (legacy vs. modern address exposure
  explained), framed as a "duty" beyond personal interest, the BAL Protocol
  time-lock mechanism as the practical answer (how a Will-Executor works and
  what it can/cannot do), a mention that SAFE21 runs a public Will-Executor
  (`we.safe21.io`), and a closing summary + source footnote (Bitcointalk
  thread on the "Paradox of Lost Bitcoin"). Per the draft's own instruction
  ("no more than one callout"), only the three-responsibilities list in the
  "Il dovere" section is a `.callout` box (one of its bullets links internally
  to `blog-seed-mai-online.html`); the Bitcoin-orange `.callout.btc` variant
  is unused here, so its CSS was omitted rather than left dead. No image, so —
  like article #22 — the click-to-zoom lightbox is intentionally omitted (no
  dead markup/CSS/JS) and no `og:image`/JSON-LD image is advertised.
- **`blog.html`** — added a `.post-card` at the very TOP of the list (ahead of
  the 2026-08-15 article from #22, as the most recently added) and a matching
  `BlogPosting` entry at the top of the JSON-LD `blogPost[]` array. Eyebrow/tag:
  "Sovranità"; date 15 agosto 2026; 6 min read.
- **`sitemap.xml`** — added a `<url>` for the new article (lastmod 2026-08-15).
- Verified: JSON-LD (index + article) parses as valid JSON, sitemap is
  well-formed XML, internal link to blog-seed-mai-online.html present, all
  three external links (bitcoin-after.life, Bitcointalk thread, plus the
  existing BAL Protocol footer link) match the front matter exactly. Word
  count ≈ 1,086 words — below the front matter's ~1,200 target, since the
  article body is exactly what the client's draft contained; no padding was
  invented to hit the target.

## [22] — New blog article: "Cosa succede ai tuoi bitcoin quando non ci sei più?"

**Date:** 2026-08-15
**Status:** Delivered and live (commit `c2810af`, pushed to `main`)

Client asked to publish a third blog article, adapted for SAFE21 from an
internal Italian draft tied to the partner project **Bitcoin After Life (BAL)**.
The draft originated for BAL's own (English) blog and its internal note said not
to publish it there; the client explicitly repurposes it for the SAFE21
Italian-only blog instead, where BAL is presented as a partner tool. Only the
article body was used — the draft's internal HTML note and its "week-1 social
calendar" section were discarded as internal planning, not article content. The
names "Bitcoin After Life" and "Will-Executor" are kept untranslated per the
source's convention.

- **New `blog-cosa-succede-ai-tuoi-bitcoin.html`.** Built from the
  `blog-seed-mai-online.html` template so header, footer, theme toggle, fonts
  and tokens match the rest of the blog exactly. Sections: the lost-coins
  problem (with one sourced statistic and a footnote), why "just leave
  instructions" fails (four flawed approaches as a list), Bitcoin's own
  time-lock mechanism (highlighted in the Bitcoin-orange callout — the one
  Bitcoin-native idea), how BAL turns it into something usable, and a
  SAFE21-specific "Come ti aiuta SAFE21" section framing SAFE21's inheritance
  service (in partnership with BAL, non-custodial, keys stay with the user).
  Closing CTA links to the contact email and the homepage Eredità section; an
  inline link points to the BAL manual (bitcoin-after.life/docs).
  This article has **no image**, so the click-to-zoom lightbox present on
  image-bearing articles is intentionally omitted (no dead markup/CSS/JS), and
  no `og:image`/JSON-LD image is advertised.
- **`blog.html`** — added a `.post-card` at the TOP of the list (newest first)
  and a matching `BlogPosting` entry at the top of the JSON-LD `blogPost[]`
  array. Eyebrow/tag: "Eredità Bitcoin"; date 15 agosto 2026; 6 min read.
- **`sitemap.xml`** — added a `<url>` for the new article (lastmod 2026-08-15)
  and bumped `blog.html` lastmod to 2026-08-15.
- Verified in the in-app browser (dark + light theme): the article renders,
  the index card links correctly, both JSON-LD blocks parse as valid JSON, and
  the sitemap is well-formed XML with the new URL. No console errors.
- **Revision:** in the closing CTA, "impostare l'eredità con BAL" reworded to
  "impostare l'eredità con **BAL Protocol**" — the client noted bare "BAL"
  means nothing to a reader who hasn't seen the footer link, where the partner
  is already named "BAL Protocol". Now consistent across the page.

## [21] — SEO / AI-readiness baseline (sitemap, robots, canonical, JSON-LD)

Client asked whether the site is discoverable by Google and by AI assistants.
Audit of the live site found: no sitemap.xml and no robots.txt (both returned
the homepage with a 200 because Cloudflare Pages has no 404 for them), no
structured data, and no canonical tags. Content and meta tags were already
fine. This task adds the missing technical signals. No visual change.

- **New `sitemap.xml`** listing all four pages (homepage, blog index, both
  articles) with lastmod dates, so search engines don't have to discover
  pages purely by crawling links — important for a new site with few inbound
  links. Comment reminds to add a `<url>` block per future article.
- **New `robots.txt`** allowing the whole site and pointing to the sitemap.
  Named AI crawlers (GPTBot, ChatGPT-User, ClaudeBot, Claude-Web,
  PerplexityBot, Google-Extended) are listed explicitly, so it's unambiguous
  that SAFE21 wants its content read and cited by AI assistants, not only
  indexed by search engines.
- **Canonical tags** (`<link rel="canonical">`) added to all four pages,
  each pointing to its own https://safe21.io/ URL.
- **JSON-LD structured data** added to every page: `Organization` on the
  homepage; `Blog` (with both posts listed) on blog.html; `Article` on each
  post, with headline, description, datePublished/dateModified, inLanguage,
  and author/publisher both set to the SAFE21 **organization** (per client
  choice — brand, not a personal name). This is the part AI assistants use
  most to identify and cite a page accurately.
- Verified: sitemap is well-formed XML with the four correct URLs; robots.txt
  allows all, references the sitemap and names the AI crawlers; every page has
  exactly one canonical and one JSON-LD block that parses as valid JSON with
  @context schema.org; the article headline matches between <h1> and JSON-LD;
  and all prior features survived the edits (image zoom, session theme, 1024px
  menu on both articles; EN/IT switcher and blog i18n key on the homepage).
- Note conveyed to the client: these changes remove technical obstacles but
  don't guarantee ranking; discoverability still takes weeks/months and
  depends partly on off-site factors (inbound links).

## [20] — Title reworded: "La verità" → "Una riflessione"

Client felt "la verità" ("the truth") was too absolute/presumptuous for a
piece that invites the reader to reason rather than to believe.

- Title changed from *"Dadi o software? La verità sul seed generato a mano"*
  to *"Dadi o software? Una riflessione sul seed generato a mano"*, in all
  four places: `<title>`, `og:title`, the article `<h1>`, and the card `<h2>`
  on blog.html.
- Verified: no occurrence of the old wording remains in either file; the new
  wording is present in all four locations.

## [19] — Click-to-zoom lightbox for article images + caption removed

Two changes to both article pages (blog-seed-mai-online.html and
blog-dadi-semplicita.html); blog.html untouched (no large figures).

- **Click-to-zoom lightbox.** Clicking any article image now opens it in a
  full-screen overlay at its **natural pixel size (1:1)**, per the client's
  choice — the infographic (1440px wide) is shown at full resolution and the
  overlay scrolls if it exceeds the viewport, rather than being scaled to fit.
  Closes on backdrop click, the X button, or Escape; clicking the image itself
  does not close, so it can be scrolled/inspected. A `zoom-in` cursor on hover
  signals the image is clickable, and background scroll is locked while open.
  Implemented with hand-written CSS + a small vanilla script (a few KB, no
  external library, nothing to keep updated); the overlay markup and script
  are identical on both pages and use the existing theme tokens so the
  backdrop matches light/dark mode.
- **Removed the infographic caption** ("Il confronto in sintesi…") added in
  [18], at the client's request. The image and its descriptive alt text
  remain.
- Verified with jsdom on both pages: the overlay starts hidden; clicking a
  figure image opens it with the correct source and aria-hidden=false and
  locks page scroll; Escape, the X button and a backdrop click all close it
  and restore scroll; clicking the image itself does not close. Confirmed the
  1:1 CSS (`max-width:none`) and the zoom-in cursor are present, the caption
  is gone from the dice article, and the infographic image is still
  referenced. All checks pass.

## [18] — Infographic added to the dice article

**Client request:** add a client-supplied infographic ("Dadi o Software? La
Verità sulla Generazione del Seed Bitcoin") to blog-dadi-semplicita.html, with
advice on size/format to keep server weight low.

- **Format kept as PNG, not JPEG.** The infographic is flat-colour with crisp
  text (unlike the task [11] tweet screenshot, which was photographic and
  benefited from JPEG). JPEG on flat text/graphics produces visible haloing
  around letters; PNG does not.
- **Resized 2752×1536 → 1440×804** (2x the article's 720px content width, so
  it stays sharp on high-density phone screens without shipping pixels no
  browser will render) **and quantised to a 256-colour palette** — the
  effective lever for flat-colour PNGs, since truecolor is unnecessary when
  the source has a handful of distinct fills. **4.78 MB → 625 KB, a 87%
  reduction**, with no visible loss on the infographic's text or gradients
  (checked visually before delivery).
- Saved as `images/infografica-dadi-vs-software.png`. Inserted as a
  `<figure>` right after "I problemi sono tre, in ordine crescente di
  importanza", before the three <h3> subsections it summarises — same
  pattern as the sourced screenshot in the first article (explicit `width`/
  `height` to avoid layout shift, `loading="lazy"`, descriptive `alt` text).
- **Added a short caption** per client request, clarifying that the
  infographic's rounded "50-100 lanci" figure spans both seed lengths, while
  the article body gives the precise numbers (~50 for 12 words, ~100 for 24)
  — so a reader who only skims the image isn't misled into thinking every
  seed needs 100 rolls.
- Verified: image reference, dimensions, lazy-loading and alt text all present
  and correct; caption present; exactly one figure/caption pair for this
  image.

## [17] — New title + read-time correction for the dice article

**Context:** the client manually removed the "Come ti aiuta SAFE21" closing
section from blog-dadi-semplicita.html directly on GitHub (article now ends
on the car/driving-licence analogy; the generic "Non sei sicuro di come stai
custodendo..." CTA still follows, so a path to SAFE21 remains, just shorter).
This entry covers the follow-up requested in chat: a new title.

- New title, chosen from a shortlist: **"Dadi o software? La verità sul seed
  generato a mano"** — replaces "Non fidarti ciecamente — nemmeno di noi" in
  all four places: `<title>`, `og:title` (+ reworded `og:description` to
  match), the `<h1>`, and the card `<h2>` on blog.html.
- **Read-time corrected 8 → 7 min**, in the article byline and the blog.html
  card. The article is now 1,476 words (~7.4 min) after the section removal;
  8 min was left over from the longer version and no longer matched the text.
- Card summary on blog.html reworded to drop the reference to "la patente
  dell'auto" tying into a SAFE21 section that no longer exists in that form.
- Verified: no trace of the old title anywhere in either file; new title
  present in all four locations; read-time label matches the actual word
  count on both pages.

## [16] — Verifiability paragraph in the dice article

Client request: after the "solite regole" paragraph, add a short paragraph
explaining that the recommended open-source software is verifiable bit for
bit via cryptographic checks and developer signatures.

- Added one paragraph (~150 words): the recommended software isn't taken on
  trust but can be verified. Explains the developers' **GPG signature** (an
  electronic seal confirming who released the file — Electrum has several,
  from different people) and the published **SHA-256 hash** (a fingerprint of
  the file); recomputing and comparing it confirms the download is identical
  bit for bit to the open-source code reviewed worldwide. Notes that the
  technically able can do it themselves, and others can be guided step by step
  by SAFE21 or by an AI. Framed as "the difference between trusting and
  verifying", tying back to the article's open-source theme. Plain-language
  metaphors (seal, fingerprint); no unexplained jargon.
- **SHA-256 instead of the client's suggested MD5**, agreed beforehand: MD5 is
  collision-broken and unsuitable for integrity verification; Electrum in
  practice is verified with GPG signatures and SHA-256. The argument is
  unchanged and now technically correct.
- Read-time label raised 7 → 8 min on the article byline and the blog.html
  card (1,593 words, ~8 min). Verified: SHA-256 present, MD5 absent, GPG and
  "bit per bit" present, single h1, internal links resolve.

## [15] — Second article: dice-generated seeds vs simplicity

New `blog-dadi-semplicita.html` — *"Non fidarti ciecamente — nemmeno di
noi"*, developed from the client's own draft into a genuine 7-minute read
(1,431 words, ~7.2 min at 200 wpm), per the client's explicit choice after
the length discussion of task [14].

- Structure: don't trust anyone blindly (including SAFE21) → the
  dice-generated-seed fashion and why it appeals → three reasons it is harder
  than it looks (≈50 correctly-performed d6 rolls for 12 words, truly balanced
  dice, and the BIP39 checksum in the last word that requires a trusted
  computer anyway — so the weak link the dice were meant to remove returns) →
  the simple path: the device CSPRNG used by a battle-tested open-source
  wallet → the programmer's true story (kept brief and anonymous, as chosen) →
  simplicity = fewer human errors (direct tone kept, as chosen) → the
  car/driving-licence analogy as closer → SAFE21 section.
- Technical corrections vs the client's draft, agreed beforehand: the last
  word is not entirely "calculated" (it contains a 4-bit checksum computed
  cryptographically); the dice problem is the number of rolls and the
  conversion method rather than the die-face configuration. The deliberate
  editorial choice NOT to include a step-by-step dice procedure is kept: the
  article explains why it is hard, not how to do it.
- Wallet mentions per client instruction: Electrum foregrounded (open source
  since 2011, SAFE21's speciality), BlueWallet as the mobile alternative,
  Pocket removed.
- Built by cloning blog-seed-mai-online.html as the shell, so the light/dark
  theme (session-only), the 1024px menu breakpoint and the design tokens are
  inherited verbatim; only <head> metadata and the article region were
  replaced, and the og:image tag was dropped (no image in this article).
  Includes an internal link to the first article.
- blog.html: new card added on top (newest first), old card untouched.
- Verified: single h1, correct metadata, internal links resolve, Electrum
  emphasised, no Pocket, no emoji, theme and menu features present, all
  twelve themes from the client's draft covered, two cards in the right
  order. All checks pass.

## [14] — Shorter article

**Task:** the article was too long. Initial brief was −30%; the client then
asked for a 4-minute read, and after seeing the result settled on the
intermediate length.

- Rewrote the article body: **1,769 → 1,056 words, a 40% cut.** No topic was
  removed — the client had specified all of them. What went is repetition and
  elaboration, so each idea is stated once. Structural changes: "Cosa è
  successo" and "La lezione" merged into one section; callouts reduced from
  four to two (the seed rule and the sovereignty trade-off, the two that carry
  the argument); rule descriptions cut to a single line each; the delayed-theft
  story condensed from four paragraphs to two; the paper-backup bullets cut
  from four to three, keeping the most concrete.
- A second tightening pass took the text to 939 words (4.7 min) but the client
  preferred the 1,056-word version, so it was restored.
- **Corrected the read-time label from 7 to 5 minutes**, in the byline and on
  the blog.html card. The original "7 min" was wrong even before the cut: at
  ~200 words per minute the old text was a 9-minute read. 1,056 words is
  ~5.3 minutes, so 5 is the honest figure.
- Shortened the card summary on blog.html to match the new standfirst.
- Verified: the image, the X link, the four numbered rules, the six-item
  checklist, the Bitcoin callout, the sealed-envelope guidance, the open-source
  section and the SAFE21 section are all still present. The task [13] test
  suite still passes in full. (The older task [12] suite now reports three
  failures per page, all on `localStorage` assertions superseded by the
  sessionStorage change in [13] — expected, not a regression.)

## [13] — Tidy header menu + session-only theme memory

Two fixes to the blog pages (blog.html and blog-seed-mai-online.html);
index.html untouched.

- **Header menu wrapping.** The hamburger only appeared below 760px, so
  between roughly 760px and 1050px the full link row plus the "Contattaci"
  button no longer fit and "Blog" wrapped under the button (client
  screenshot). Raised the collapse breakpoint to **1024px**: below that width
  the inline links and the Contact button move into the existing drawer, and
  the tidy hamburger takes over. The phone-only tweaks (reduced logo/height,
  font sizes) stay at 760px, since they are about small screens rather than
  about when the menu collapses. The theme switch and hamburger remain visible
  at every width.
- **Theme starts dark every visit ("Variante A").** Storage moved from
  `localStorage` (persists for months) to `sessionStorage` (cleared when the
  tab/browser closes). Result: a fresh visit always starts dark, while a
  choice made with the switch still carries across pages within the same
  visit. Both the pre-paint no-flash script and the toggle's write call were
  updated; the key name (`safe21-blog-theme`) is unchanged, so it still can't
  collide with the homepage's language key.
- Verified with jsdom: the 1024px query hides the links / shows the hamburger
  / hides Contact; the 760px query no longer touches the links; the theme
  button is never hidden at any width; the theme uses sessionStorage and not
  localStorage; a fresh session starts dark even when a stale localStorage
  value from the previous build says "light"; the choice persists across
  pages within one session; and a new session reverts to dark. index.html has
  no 1024px query and no theme code. All checks pass on both pages.

## [12] — Optional light theme for the blog

**Task:** let readers switch the blog to a light background, because long
articles are uncomfortable to read on a dark screen. Scope is strictly the
blog — `index.html` stays dark and was verified unchanged.

- **Implementation.** Both blog pages already routed every colour through
  CSS custom properties, so the theme is a second token block scoped to
  `[data-theme="light"]` on `<html>`. Flipping one attribute repaints the
  whole page: no duplicated stylesheet, no per-element overrides. Four
  values were still hardcoded (header blur, body copy, callout tints,
  button hover) and were lifted into tokens first, otherwise they would
  have stayed dark. A verification check now fails the build if any dark
  literal reappears outside a token definition.
- **Toggle button** (`.theme-toggle`, sun/moon) sits in the header and
  **stays visible at every width**, unlike the "Contattaci" button which is
  hidden below 760px — the light theme matters most on a phone, so hiding
  the switch there would defeat the purpose. Below 400px the header gap and
  the two icon buttons shrink slightly so logo + theme + hamburger never
  collide.
- **Persistence + no flash.** The choice is stored under
  `safe21-blog-theme`, a key of its own so it cannot collide with the
  homepage's `safe21-lang`. A tiny inline script in `<head>` applies the
  saved theme *before* first paint; without it a returning reader would see
  a dark frame flip to light, which is very visible on mobile. The
  `<meta name="theme-color">` tag is updated too, so the mobile browser
  chrome matches the page instead of staying navy. Default remains dark.
- **Palette.** Not a generic light theme: the page background is a cool
  white tinted toward the brand navy (`#F4F6F9`) and the primary text
  colour *is* the dark theme's background (`#0A0F1C`), so the two modes
  mirror each other. The accent teal is darkened `#2DD4BF` → `#0A7568`
  because the bright teal fails contrast on white (measured 4.31:1 on the
  alternating section background); `#0A7568` clears 4.5:1 everywhere while
  staying in the same colour family. The Bitcoin orange is darkened to
  `#9A5B00` for the same reason.
- **Logo.** Rather than loading a second SVG file, the wordmark's two
  `<tspan>` fills became tokens. In light mode they resolve to `#0A0F1C` /
  `#0D9488` — the exact values already in `logos/safe21-logo-light.svg`, so
  the existing brand asset is honoured with no extra HTTP request. A test
  asserts the tokens still match that file byte-for-byte.
- **Verified.** Contrast ratios are re-read *from the patched stylesheet*
  rather than trusted from the patch script, then re-checked: all 15
  text/background pairings pass WCAG 2.1 AA (4.5:1 for body text, 3:1 for
  the large logo type). Lowest margin is the teal accent on the alternating
  background at 4.75:1; highest is body text at 17.67:1. Behavioural tests
  with jsdom cover: first load defaults to dark, click switches and updates
  `aria-pressed` plus the label (which describes the *next* action), the
  choice survives a reload and is applied pre-paint, and the mobile menu
  still opens and closes on Escape. 36/36 checks pass.

## [11] — Article image optimisation + preview build

**Trigger:** the client reported the image was missing from the article. It
was not: the chat preview renders a single HTML file in isolation, so the
relative path `images/...` cannot resolve there — the same reason the favicon
never appeared in previews. The markup was correct and the image displays
once deployed. Two improvements were made off the back of the report.

- **Optimised the screenshot.** The source PNG was 796 KB (970×1285, RGBA) —
  heavy enough to noticeably delay the article on a slow mobile connection.
  Converted to a progressive JPEG at quality 82: **186 KB, a 77% reduction**,
  at unchanged pixel dimensions and with no visible artefacts on the tweet
  text. The alpha channel was flattened onto the panel colour (#111B2E)
  rather than white, so any semi-transparent edge pixel blends into the
  figure's own background. `images/articolo-x-sparkkitty.png` was replaced by
  `images/articolo-x-sparkkitty.jpg`; the `og:image` meta tag was updated to
  match.
- **Added `width`, `height`, `loading="lazy"` and `decoding="async"`** to the
  `<img>`. The explicit dimensions let the browser reserve the right space
  before the file arrives, which prevents the text below from jumping as the
  image loads; lazy loading defers the download until the reader scrolls near
  the figure, so the article renders faster on first paint.
- **Preview-only build** (`ANTEPRIMA-articolo-con-immagine.html`, delivered
  outside the site folder): identical to the article but with the JPEG inlined
  as a base64 data URI, so the client can review the finished layout in the
  chat preview. **Not for deployment** — the data URI adds ~250 KB to the page
  and cannot be cached separately by the browser. A comment at the top of the
  file states this.
- Verified with jsdom: the deployable article points at the JPEG, the file
  exists, dimensions and lazy-loading attributes are set, no HTML file still
  references the removed PNG, and the preview copy carries the image inline
  while matching the article's title and paragraph count exactly. 10/10 checks
  pass.

## [10] — Blog section (Italian only) + first article 

**Task:** add a blog to safe21.io. Client decision: the blog is published in
**Italian only**, unlike the homepage which ships in English with a runtime
EN/IT switcher.

- New `blog.html` — article index. Single-column card list (a multi-column
  grid would leave visibly empty cells while the blog is small), intro
  header, and a note inviting topic suggestions by email. Instructions for
  adding future posts are in an HTML comment at the top of the file.
- New `blog-seed-mai-online.html` — first article, *"Il tuo SEED non deve mai
  toccare internet"*. Written for readers in their first year with Bitcoin
  who hold a small amount: no jargon, short sentences, concrete actions.
  Sections: the SparkKitty malware found on the official app stores; why the
  store badge is not a security guarantee; four numbered "never do this"
  rules (screenshot, photo, messaging apps, cloud files); the delayed-theft
  scenario (a seed stolen today can be drained years later, once the link to
  the original mistake is untraceable); physical protection of the paper
  backup (tamper-evident sealed envelope, opaque against a torch, signed and
  dated); open-source and battle-tested software only; security proportionate
  to the value held; sovereignty as both freedom and responsibility; how
  SAFE21 helps. Closes with a 6-point checklist and a contact CTA.
- Source attribution: the client-supplied screenshot of the @coinbureau post
  is embedded as a `<figure>` with descriptive `alt` text and a caption
  linking to the original X post (`target="_blank"` + `rel="noopener"`).
- New `images/` folder with `articolo-x-sparkkitty.png`.
- `index.html`: added a "Blog" link to the desktop nav, the mobile drawer and
  the footer contact column, plus the `nav.blog` i18n key. The label is
  identical in EN and IT because the blog itself is Italian-only; the key
  exists to keep the EN capture and the IT dictionary symmetrical.
- The blog pages deliberately carry **no** EN/IT switcher and no i18n
  dictionary — the Italian copy is written straight into the markup. Design
  tokens, header, footer and the mobile-menu script are copied from
  `index.html` so each page stays self-contained and visually identical.
- Verified with jsdom (`verify-blog.js`, not deployed): every internal link
  and asset resolves on disk, the Blog link appears in all three places, the
  homepage switcher is untouched, the blog pages contain no i18n leftovers,
  the X link and screenshot are present and correctly attributed, all eleven
  requested topics are covered, and the mobile menu opens, closes on link tap
  and closes on Escape. 46/46 checks pass.

## [9] — Fix: header "Contact us" wrapping on narrow phones

**Bug report:** on real phones (~360-390px wide) the header's "Contact us"
button wrapped onto two lines ("Contact" / "us"), because the mobile row now
has to fit language switch + Contact button + hamburger together and ran out
of horizontal space.

- Hidden the header's "Contact us" button at <=760px (`.nav .cta > a.btn-primary`).
  It is not removed from the page — only hidden by CSS, so it still shows on
  desktop — and the same action is already the last item in the hamburger
  drawer added in [8], so nothing is lost.
- Verified with jsdom: the media rule is present, the header button stays in
  the DOM for desktop, and the drawer still lists 5 links ending with
  "Contact us" -> mailto:info@safe21.io.

## [8] — Mobile navigation (hamburger menu)

**Task:** The header nav links were hidden below 760px with no replacement,
so mobile visitors lost all in-page navigation. Added a mobile menu.

- New hamburger button (`.menu-toggle`) in the header, shown only <=760px;
  animated hamburger/close icon swap driven by `aria-expanded`.
- New slide-down drawer (`.mobile-menu`, `#mobile-menu`) repeating the primary
  links (Services, Inheritance, Payments, Why SAFE21) plus Contact, using the
  same anchors and `data-i18n` keys as the desktop nav.
- JS: dependency-free toggle; closes on link tap, on Escape, and auto-resets
  when the viewport grows past the breakpoint. `aria-controls`/`aria-expanded`
  for accessibility.
- i18n: added `nav.menu` ("Apri menu") and `data-i18n-aria` handling so the
  button's `aria-label` is translated alongside the drawer links.
- Verified with a jsdom simulation: open/close, link-tap close, Escape close,
  and EN<->IT translation of the drawer all pass. No changes to desktop layout.

## [7] — Contact section cleanup + Italian wording fix

**Date:** 2026-07-19
**Status:** Delivered (pending review)

- Removed the plain-text `info@safe21.io` line under the "Email SAFE21"
  button in the Contact section — it duplicated the button (same mailto).
  The address is still shown in the footer's Contact column. The now-unused
  `.contact .email` CSS rule was removed as well.
- Italian copy fix (problem section): "due rischi ricadono" → "i rischi
  ricadono", as requested.

## [6] — Italian translation + EN/IT language switcher

**Date:** 2026-07-19
**Status:** Delivered (pending review)

- Added a compact **EN / IT** language switcher to the header, next to the
  Contact button. English remains the default language; the visitor's choice
  is remembered in the browser (localStorage) for future visits.
- Full Italian translation of every visible text (hero, problem, services,
  why, contact, footer, disclaimer) plus the page title and meta description.
  Implemented as a JavaScript i18n dictionary inside the same single file —
  no new files, no structural changes. English stays written in the markup
  (single source of truth); Italian strings live in the dictionary.
- Mobile refinements so the header fits comfortably on small screens:
  header bar 84px → 64px, logo 60px → 42px, smaller Contact button and
  switcher padding. The switcher stays visible at every screen size.
- Verified via automated DOM tests: EN → IT → EN round-trip restores the
  original English exactly; all 65 translatable elements switch; partner
  link icons and the hero accent survive the swap; language preference
  persists.

## [5] — Revert hero keyhole to original

**Date:** 2026-06-29
**Status:** Delivered (pending review)

- Reverted the hero background keyhole to its original two-shape version
  (circle + tapered neck), as requested. The clean key icon from [4] is kept.

## [4] — Fix key icon and hero keyhole

**Date:** 2026-06-29
**Status:** Delivered (pending review)

- Redrew the "Lose the keys, lose the coins" icon as a clean key (it previously
  looked malformed).
- Rebuilt the hero background keyhole as a single continuous outline (round head
  flowing into the tapered neck), removing the internal crossing lines so only
  the keyhole silhouette remains.

## [3] — Redraw inheritance icon (hourglass)

**Date:** 2026-06-29
**Status:** Delivered (pending review)

- Replaced the malformed hourglass icon on the "Bitcoin Inheritance" card with a
  clean, well-drawn hourglass (with sand at the bottom) to clearly signal the
  "time-locked" nature of the inheritance transactions. No other changes.

## [2] — Enlarge header logo

**Date:** 2026-06-29
**Status:** Delivered (pending review)

- Doubled the header logo size (30px → 60px height) for better visibility, as
  requested. Header bar height increased (70px → 84px) to keep vertical balance.
- No other sections or content changed.

## [1] — SAFE21 homepage + brand logo (initial build)

**Date:** 2026-06-29
**Status:** Delivered (pending review)

### Branding
- Designed and selected the SAFE21 logo: "Minimal Wordmark" concept, **Cyber Teal**
  palette (teal tile with a transparent keyhole, off-white "SAFE", teal "21").
- Produced logo assets:
  - `logos/safe21-logo.svg` — primary, for dark backgrounds.
  - `logos/safe21-logo-light.svg` — for light backgrounds (dark "SAFE").
  - `logos/safe21-favicon.svg` — square app icon / favicon.

### Homepage (`index.html`)
- Built a single, self-contained homepage (HTML + CSS + minimal vanilla JS),
  fully in English, responsive down to mobile.
- Visual direction: dark "vault" background, **teal** as the primary accent,
  small **Bitcoin-orange** touches reserved for the Bitcoin-native (partner)
  services. Typography: Space Grotesk (display), Inter (body), Space Mono (labels).
- Sections, in order: Header → Hero → Problem → Services (5) → Why SAFE21 →
  Contact → Footer.
- Five services presented: Bitcoin Assistance, Bitcoin Courses (online & in
  person), Electrum Wallet Security (standard, 2FA, hardware, cold/offline),
  Bitcoin Inheritance (Will Executor — **in partnership with BAL**,
  https://bitcoin-after.life/), and Accept Bitcoin Payments (**in partnership
  with Pago in Bitcoin**, https://www.pagoinbitcoin.ch/).
- Contact channel: email `info@safe21.io` (placeholder, ready for Cloudflare
  Email Routing).
- Footer includes a disclaimer (not legal/tax/financial advice; non-custodial;
  inheritance rules vary by country) appropriate for an inheritance-related site.
- Accessibility & quality: semantic HTML, visible keyboard focus, `aria` labels
  on icons/logos, and `prefers-reduced-motion` support for the scroll-reveal
  animation.

### Notes / open items
- `info@safe21.io` is a placeholder; set up Cloudflare Email Routing to receive
  mail (guide available on request).
- Logo wordmark uses the Space Grotesk webfont; for a fully font-independent
  logo file, the text can later be converted to vector outlines.
- Single-page scope only, as agreed. Additional pages can follow as new tasks.
