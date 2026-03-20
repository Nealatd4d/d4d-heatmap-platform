# Mobile-First Redesign — Change Log

**Implementer:** Perplexity Computer (senior frontend engineer subagent)  
**Date:** March 20, 2026  
**File modified:** `/home/user/workspace/d4d-heatmap-platform/index.html`  
**Pre-redesign backup:** `index.html.pre-redesign`

---

## Summary

A complete mobile-first CSS rewrite plus minimal HTML restructuring to implement the redesign spec. No JavaScript logic was altered. All existing element IDs, data attributes, and JS function references are preserved exactly.

---

## A. CSS Changes (lines 26–530)

### New Design Tokens (`:root`)
- Added complete **z-index scale** as CSS custom properties:
  - `--z-map: 1`, `--z-map-overlay: 100`, `--z-loading: 200`, `--z-header: 500`
  - `--z-mode-strip: 600`, `--z-toolbar-sheet: 700`, `--z-bottom-sheet: 800`, `--z-scrim: 650`
- Added **component dimension tokens**: `--header-h: 44px`, `--mode-strip-h: 48px`, `--sidebar-w: 260px`, `--touch-min: 44px`
- All z-index values throughout stylesheet now reference these tokens (removed ad-hoc magic numbers)

### Bug Fix: `.hidden` Utility
- **Added** `.hidden { display: none !important; }` — this was missing and caused `#selCommitteeB` and `#selFinancePrev` to remain visible when JS toggled `.hidden` on them

### Mobile-First Architecture
- **Was:** Desktop-first with a single `@media (max-width: 768px)` override block
- **Now:** Base styles = mobile layout, `@media (min-width: 769px)` = desktop overrides
- The `#app` base style uses `display: flex; flex-direction: column` (mobile)

### Toolbar: Bottom Sheet on Mobile
- **Was:** Toolbar in document flow; max-height collapse (brittle; caused header to intercept map clicks)
- **Now:** `position: fixed; bottom: var(--mode-strip-h); left: 0; right: 0; transform: translateY(100%)` — completely off-canvas when collapsed
- `.toolbar.expanded` → `transform: translateY(0); padding: 16px` — slides up over the mode strip
- `z-index: var(--z-toolbar-sheet)` (700) — above mode strip (600), below bottom sheet (800)
- `max-height: 70vh; overflow-y: auto` — internally scrollable

### Desktop Layout: CSS Grid Sidebar
- `@media (min-width: 769px)` converts `#app` to CSS Grid:
  ```
  grid-template-areas: "header header" / "sidebar map" / "sidebar footer"
  grid-template-columns: 260px 1fr
  grid-template-rows: 44px 1fr auto
  ```
- `.header` → `grid-area: header` (full width)
- `.toolbar` → `grid-area: sidebar` (260px static column, `position: static; height: 100%; overflow-y: auto`)
- `.map-wrap` → `grid-area: map` (fills remaining space)
- `.footer` → `grid-area: footer`
- Tablet override: `--sidebar-w: 220px` at `(min-width: 769px) and (max-width: 1024px)`

### Toolbar Separators
- `toolbar-sep` is `display: none` by default (mobile base)
- On desktop: `display: block; width: 100%; height: 1px; background: var(--border); margin: 8px 0` — becomes real horizontal dividers in the sidebar

### Typography Fixes (minimum 12px floor)
- `stat-label`: `10px` → `12px`
- `toolbar-label`: `10px` → `11px` (desktop), `12px` (mobile)
- `mode-btn`: `11px` → `12px`
- `layer-btn`: `11px` → `12px`
- `toolbar select`: `11px` → `12px`
- `finance-controls select`: `11px` → `12px`
- `info-row`, `cand-row`, `cand-votes`, `legend-row`, `legend-title`: all raised to `12px`
- `loading-indicator span`: `11px` → `12px`
- `export-btn`: `11px` → `12px`

### Touch Target Fixes (44px minimum on mobile)
- All mobile `.mode-btn`: `min-height: var(--touch-min)` + `padding: 10px 4px`
- Mobile `.layer-btn`: `min-height: var(--touch-min)` + `padding: 10px 4px`
- Mobile toolbar `select`: `min-height: var(--touch-min)` + `padding: 10px 28px 10px 10px`
- Mobile `.view-opts select`: `min-height: var(--touch-min)`
- Mobile `.vs-checklist label`: `min-height: var(--touch-min)`
- Mobile `.export-btn`: `min-height: var(--touch-min)` + `padding: 12px`
- `.filter-toggle`: `min-width: var(--touch-min); min-height: var(--touch-min)`
- Leaflet zoom buttons: `44×44px` (was `30×30px`)

### Header: Compact Single Row on Mobile
- Mobile header is exactly `44px` (fixed by `height: var(--header-h)`)
- `header-stats` is `display: none` on mobile — stats are accessible in the toolbar bottom sheet (no more two-row expanding header that intercepts map clicks)
- Desktop header shows full title, subtitle, and stats as before

### Legend
- Mobile legend positioned at `bottom: calc(var(--mode-strip-h) + 10px)` — clears the mode strip
- Open state capped at `max-height: min(300px, 40vh)` — viewport-relative cap (was fixed 300px)
- Same tap-to-open behavior preserved
- Desktop legend: same cap applied, positioned `bottom: 16px`

### Mobile Mode Strip (new)
- `.mode-strip`: `position: fixed; bottom: 0; height: 48px; z-index: var(--z-mode-strip)` — always visible on mobile
- `.strip-btn`: full 48px height, `flex: 1`, touch-accessible
- `.strip-btn.active`: blue accent treatment matching toolbar mode buttons
- `.strip-btn.more-btn`: larger font for `⋮` symbol
- Hidden on desktop (`display: none`)

### Bottom Sheet (precinct detail)
- Updated `z-index` to `var(--z-bottom-sheet)` (800)
- Mobile only (`display: none !important` on desktop via `@media (min-width: 769px)`)
- Unchanged behavior otherwise

### Header Stats
- Desktop: unchanged — appears in header right
- Mobile: hidden from header; available in toolbar sheet when opened

---

## B. HTML Changes (lines ~534–654)

### Semantic Elements
- `<div class="header">` → `<header class="header">` (closes with `</header>`)
- `<div class="toolbar" id="toolbar">` → `<aside class="toolbar" id="toolbar" aria-label="Map controls">` (closes with `</aside>`)
- `<div class="map-wrap">` → `<main class="map-wrap">` (closes with `</main>`)
- `<div class="footer">` → `<footer class="footer">` (closes with `</footer>`)

### Filter Toggle ARIA
- Added `aria-controls="toolbar"` and `aria-expanded="false"` to `#filterToggle`

### New `#modeStrip` Element
Added after `#bottomSheet`, before `<footer>`:
```html
<nav class="mode-strip" id="modeStrip" aria-label="View mode">
  <button class="strip-btn active" data-strip-mode="turnout">Turnout</button>
  <button class="strip-btn" data-strip-mode="winner">Winner</button>
  <button class="strip-btn" data-strip-mode="margin">Margin</button>
  <button class="strip-btn more-btn" data-strip-mode="more" title="More controls">⋮</button>
</nav>
```

### Preserved Exactly
- All element IDs: `toolbar`, `filterToggle`, `headerStats`, `bottomSheet`, `bottomSheetContent`, `modeStrip`, `legend`, `infoPanel`, `landing`, `loader`, `exportTitle`, `selElection`, `selType`, `selRace`, `selFocus`, `electionControls`, `financeControls`, `electionModes`, `financeModes`, `viewOpts`, `toolbarControls`, `selFinanceElection`, `selCommitteeA`, `selCommitteeB`, `selFinancePrev`
- All `data-mode` and `data-fmode` attributes
- All `onclick` inline handlers
- Perplexity Computer attribution block in `<head>`
- Footer attribution link

---

## C. JavaScript Changes (end of IIFE, before closing `})();`)

### `syncModeStrip()` function (new)
```javascript
function syncModeStrip() {
  if (!modeStrip) return;
  modeStrip.querySelectorAll('.strip-btn').forEach(b => {
    const m = b.dataset.stripMode;
    if (m === 'more') return;
    const isActive = (dataLayer === 'finance')
      ? m === currentFinanceMode
      : m === currentMode;
    b.classList.toggle('active', isActive);
  });
}
```
- Called after `currentMode = btn.dataset.mode` in the `#electionModes` click handler (one line added)
- Automatically syncs strip when mode is changed via toolbar controls

### Mode Strip Event Listeners (new)
- Each `.strip-btn` click: finds and clicks the corresponding real `.mode-btn` in `#electionModes` (for election layer) or `#financeModes` (for finance layer)
- The `⋮` (more) button calls `toggleToolbar()` to open the full controls sheet
- Delegates to real buttons to avoid duplicating JS logic

### `patchToggleToolbar()` (new, IIFE)
- Wraps `window.toggleToolbar` to also update `aria-expanded` on `#filterToggle` when toolbar state changes
- Non-breaking: calls the original function first, then updates ARIA

---

## D. What Was NOT Changed

- All JavaScript logic (fetch calls, Supabase queries, render functions, data processing)
- Element IDs and data attributes
- The existing `#bottomSheet` (precinct detail) structure and behavior
- The existing legend toggle logic in `initLegendToggle()`
- The existing iOS bounce prevention in `preventIOSBounce()`
- The `exportPNG()` function (still captures `.map-wrap`)
- CDN imports (Leaflet, SparkMD5, html-to-image)
- Perplexity Computer attribution

---

## E. Quality Verification

All critical checks passed:
- `.hidden { display: none !important; }` rule present — fixes JS-coupled visibility bug
- All required element IDs intact
- `toggleToolbar()` still toggles `.expanded` class on `#toolbar`
- `setDataLayer()` still switches `#electionControls` / `#financeControls` visibility
- `exportPNG()` still captures `.map-wrap`
- Mode strip buttons delegate to real `.mode-btn` elements
- `syncModeStrip()` called in election mode button click handler
- `window.toggleToolbar` exposed globally for inline `onclick` handlers
- Desktop: toolbar is `position: static` with `transform: none` — grid sidebar, always visible
- Mobile: toolbar is `position: fixed; transform: translateY(100%)` — bottom sheet, hidden until expanded
- `#modeStrip` is `display: none` on desktop, `display: flex` on mobile
