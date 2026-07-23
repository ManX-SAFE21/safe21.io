# CHANGELOG

All notable changes to the SAFE21 website are documented here.
One numbered entry per task.

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
