# CHANGELOG

All notable changes to the SAFE21 website are documented here.
One numbered entry per task.

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
