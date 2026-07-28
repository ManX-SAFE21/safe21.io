# CHANGELOG

All notable changes to the SAFE21 website are documented here.
One numbered entry per task.

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
