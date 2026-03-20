# D4D Election Heatmap Platform — HTML/CSS Code Audit

## Scope reviewed
- `/home/user/workspace/d4d-heatmap-platform/index.html`
- `/home/user/workspace/d4d-heatmap-platform/audit/extracted-css.css`
- Screenshots in `/audit/`

---

## Executive summary

The current UI is functional, but the structure is still a single-file prototype architecture rather than a maintainable application shell. The main problems are:

1. **Non-semantic page structure**: the app shell is almost entirely `<div>`-based, with no landmark elements (`header`, `main`, `nav`, `aside`, `footer`, `section`).
2. **Desktop-first CSS**: the base layer defines desktop layout, and mobile behavior is patched in one large `@media(max-width:768px)` override.
3. **Mobile toolbar collapse is height-capped, not content-driven**: `.toolbar.expanded { max-height: 500px; }` is fragile for dynamic content and directly explains the “0px height but 367px scrollHeight” symptom.
4. **Header and toolbar remain in the document flow above the map with high stacking order**: on mobile, when the collapsed toolbar still occupies the top of the viewport and the header stats row expands, pointer interactions near the top map area are intercepted by header descendants.
5. **Hidden-state CSS is incomplete**: `.hidden` is toggled on individual finance selects in JS, but there is no generic `.hidden { display:none; }` rule in the stylesheet. That means `selCommitteeA`, `selCommitteeB`, and `selFinancePrev` can remain visually present even when JS expects them hidden.
6. **Accessibility is partial**: there are very few ARIA attributes, no landmarks, no live region for dynamic stats, weak focus treatment, undersized touch targets, and several text contrast failures.
7. **Control density is too high for current layout model**: flex-wrap and ad hoc separators are doing work better handled by a structured sidebar/grid system.

---

## 1) HTML structure audit

### 1.1 Semantic structure

Current top-level app shell (`index.html:223-335`) is:

- `#app`
  - `.header`
  - `.toolbar`
  - `.map-wrap`
  - `.bottom-sheet`
  - `.footer`

Problems:

- `.header` at `index.html:224` should be a semantic `<header>`.
- `.toolbar` at `index.html:247` is effectively a filter/navigation/control region and should be an `<aside>` or `<nav>` depending on intent. In this product it is best modeled as **`<aside class="controls-panel">`** because it is a control surface, not site navigation.
- `.map-wrap` at `index.html:314` should be the primary `<main>` region.
- The map itself should sit in a labeled `<section>` or `<div role="region">` with an accessible name such as “Election map”.
- `.footer` at `index.html:331` should be a semantic `<footer>`.
- There are **zero** semantic landmarks in the file. A search of the full file found no `<header>`, `<main>`, `<nav>`, `<aside>`, `<section>`, or `<footer>` tags.

### 1.2 Control grouping and DOM nesting

The grouping is only visually implied, not structurally explicit.

Current nesting inside `.toolbar` (`index.html:247-311`):

- `.toolbar-controls`
  - label + `.layer-toggle`
  - `#electionControls`
    - label + `#selElection`
    - label + district selects
    - label + `#electionModes`
    - `#viewOpts`
    - label + `#selFocus`
  - `#financeControls`
    - label + `#selFinanceElection`
    - label + committee selects
    - label + `#financeModes`
  - export button

Issues:

- The toolbar uses plain `<span class="toolbar-label">` elements (`index.html:250, 258, 261, 265, 278, 284, 287, 292`) instead of semantic grouping with `<fieldset>` + `<legend>`.
- Related controls are not programmatically associated. For example, the “View” label at `index.html:265` is not tied to `#electionModes` in any accessible way.
- `#electionControls` and `#financeControls` are large flat clusters instead of smaller groups such as:
  - Data layer
  - Election selection
  - Geography selection
  - Metric selection
  - Comparison options
  - Focus/export
- `#viewOpts` (`index.html:276`) is injected dynamically, but there is no wrapper label relationship or `aria-live` guidance when its content changes.

### 1.3 Redundant wrappers / unnecessary nesting

Not severe, but there are several wrappers that are doing presentational work only:

- `.header-right` (`index.html:237`) exists only to hold stats + toggle, then switches to `display: contents` on mobile (`index.html:153`). Using `display: contents` on an important structural wrapper is fragile for accessibility and event targeting.
- `.toolbar-controls` (`index.html:248`) is only needed because `.toolbar` is overloaded as both shell and animated collapsible container.
- Multiple `.toolbar-sep` nodes (`index.html:260, 264, 277, 286, 291, 304`) exist only to simulate grouping. They should be replaced with actual grouped sections and spacing rules.

### 1.4 Tab order / keyboard flow

Source order is mostly logical, but the structure still creates friction.

Keyboard order from `index.html:239-305` is:

1. Filter toggle
2. Layer buttons
3. Election select
4. District type select
5. Race select
6. 8 election mode buttons
7. Focus select
8. Finance controls/selects/buttons when visible
9. Export button

Issues:

- Tab order is source-order correct, but **not hierarchy-aware**. Users must tab through a long undifferentiated list of controls.
- Because the header stats are not interactive, that is fine, but the filter toggle being in the header while the controlled region is outside creates a weak relationship. It needs `aria-controls="toolbar"` and `aria-expanded` updates.
- No skip link exists to move directly to the map or controls.
- Map features are pointer-driven only; there is no keyboard equivalent to inspect a precinct.
- The legend is clickable on mobile, but it is a `<div>` (`index.html:323`) rather than a button, so it is not keyboard accessible.

### 1.5 ARIA and missing accessibility semantics

The file contains only **two ARIA attributes total**:

- SVG logo `aria-label="D4D Logo"` at `index.html:226`
- Filter toggle `aria-label="Toggle filters"` at `index.html:239`

Missing ARIA / semantics:

- No `role="main"`, `role="region"`, or semantic landmarks.
- No `aria-controls` / `aria-expanded` on the filter toggle.
- No labels for selects via `<label for>` or `aria-labelledby`.
- No `aria-pressed` state on mode buttons or layer toggle buttons.
- No `aria-live` on `#headerStats` (`index.html:238`) despite dynamic updates at `index.html:1496` and `2233`.
- No accessible name/description on `#map` (`index.html:315`).
- No accessible semantics for the bottom sheet (`index.html:326-328`): should be `role="dialog"` or `role="region"` with label depending on intended behavior.
- No accessible semantics for the legend; on mobile it should be a button controlling a region.
- No `aria-hidden` on hidden panels.

---

## 2) CSS architecture audit

### 2.1 Media queries and breakpoints

There are exactly **2 media queries** in the stylesheet:

1. `@media (min-width:769px) and (max-width:1024px)` at `index.html:133-139`
2. `@media (max-width:768px)` at `index.html:142-205`

This is a **desktop-first** system:

- Base styles target desktop.
- Tablet and mobile both override desktop assumptions.
- Mobile is not the default mental model.

### 2.2 CSS custom properties

There is one small token block in `:root` (`index.html:28-32`):

- surface/background/text colors
- accent colors
- border color

What is good:
- Basic dark theme tokenization exists.

What is weak:
- No spacing scale tokens
- No radius tokens
- No z-index tokens
- No shadow tokens
- No typography scale tokens
- No breakpoint tokens
- No component tokens (`--header-height`, `--toolbar-max-height`, etc.)
- Many values are hard-coded repeatedly: `8px`, `10px`, `11px`, `12px`, `16px`, `30px`, `500px`

### 2.3 Specificity and `!important`

There are **14 `!important` uses**, concentrated in Leaflet overrides:

- `.leaflet-container` background (`index.html:70`)
- `.leaflet-control-zoom` and `.leaflet-control-zoom a` styles (`index.html:71-72`)
- `.leaflet-control-attribution{display:none!important}` (`index.html:73`)
- `.info-panel{display:none!important}` on mobile (`index.html:184`)

Assessment:
- Not catastrophic, but this is already a sign of CSS fighting third-party library defaults rather than isolating map-control theming in a dedicated layer.
- The mobile `display:none!important` on `.info-panel` is acceptable as a patch, but it indicates the component model is not cleanly separated by viewport/context.

### 2.4 Layout model in use

The app uses a mix of:

- Fixed viewport shell: `html, body` and `#app` are fixed to the viewport (`index.html:34-35`)
- Flex column layout for overall shell (`#app` at `index.html:35`)
- Flex-wrap inside header and toolbar (`index.html:36, 45`)
- CSS Grid only for mobile mode buttons (`index.html:174`)
- Absolute positioning for overlay panels (`.info-panel`, `.legend`, `.landing-overlay`, `.export-title-overlay` at `index.html:74, 88, 92, 214`)
- Fixed positioning for bottom sheet (`index.html:126`)

This creates too many overlapping stacking contexts for a control-heavy app.

### 2.5 Z-index / stacking review

Explicit z-index usage:

- `.header` = `1000` (`index.html:36`)
- `.toolbar` = `1000` (`index.html:45`)
- `.footer` = `1000` (`index.html:107`)
- `.loading-indicator` = `900` (`index.html:110`)
- `.export-title-overlay` = `850` (`index.html:214`)
- `.info-panel` = `800` (`index.html:74`)
- `.legend` = `800` (`index.html:88`)
- `.landing-overlay` = `700` (`index.html:92`)
- `.bottom-sheet` = `1100` (`index.html:126`)

Problems:

- No z-index scale token system; values are ad hoc.
- Header and toolbar share `1000`, so ordering falls back to DOM order and browser paint rules rather than explicit layer design.
- The map is not given a layer boundary relative to the shell; instead the shell pieces simply sit above it.
- The bottom sheet correctly wins at `1100`, but the rest of the shell still competes unnecessarily.

### 2.6 Exact CSS causing mobile overlap / interception

The mobile overlap is not one single rule. It is the interaction of these rules:

1. `html, body { overflow:hidden; position:fixed; width:100%; height:100%; }` at `index.html:34`
   - Locks the entire document to the viewport and removes natural page scrolling.

2. `#app { display:flex; flex-direction:column; height:100%; height:100dvh; overflow:hidden; position:fixed; top:0; left:0; right:0; bottom:0; }` at `index.html:35`
   - Creates a fixed shell where header and toolbar always sit above the map in the same viewport box.

3. `.header { z-index:1000; flex-shrink:0; }` at `index.html:36`
   - Keeps header permanently above the map.

4. `.toolbar { z-index:1000; flex-shrink:0; }` at `index.html:45`
   - Same for toolbar.

5. Mobile override `.header { padding:6px 12px; flex-wrap:wrap; gap:0; }` at `index.html:144`
   - Allows the header to grow vertically when stats are present.

6. Mobile override `.header-right { display:contents }` at `index.html:153`
   - Removes a stable layout wrapper and lets the stats row become a direct participant in header flow.

7. Mobile override `.header-stats { width:100%; order:3; overflow-x:auto; padding-top:4px; border-top:1px solid var(--border); margin-top:4px; }` at `index.html:156`
   - Forces a full-width second row beneath the title, increasing header height and extending the header’s hit area across the screen.

8. Mobile override `.toolbar { padding:0; overflow:hidden; max-height:0; border-bottom:none; transition:max-height 0.3s ease,padding 0.3s ease; }` at `index.html:164`
   - Collapses visually, but does not move the control region off-canvas; it remains in layout between header and map.

9. Mobile override `.toolbar.expanded { max-height:500px; padding:8px 12px; border-bottom:1px solid var(--border); }` at `index.html:165`
   - Expansion is capped, not measured. If real content exceeds 500px, controls become partially hidden and scroll/interaction gets awkward.

10. `.map-wrap { flex:1; position:relative; min-height:0; overflow:hidden; touch-action:none; }` at `index.html:68`
    - The map only gets leftover height after header + toolbar consume space.

11. Header stats content is injected dynamically into `#headerStats` (`index.html:1479-1492` and `2229-2231`), so the mobile header height is state-dependent.

Why Playwright saw `.header` intercepting clicks:

- On mobile, the **top strip of the viewport remains occupied by the expanded header**, including the stats row generated in `#headerStats`.
- Since `.header` has `z-index:1000` and sits above `.map-wrap`, any map interaction attempted in the vertical area still covered by the header will hit header descendants first.
- The specific descendant reported, `.stat-label`, is created dynamically inside `headerStats.innerHTML` in `updateStats()` (`index.html:1479-1492`) and `updateFinanceStats()` (`index.html:2229-2231`).
- In other words: the header is not “mysteriously floating”; it is **actually occupying that top viewport area**, and because the app uses a fixed-height shell, the map begins only below it.

### 2.7 Why toolbar height is 0px on mobile but `scrollHeight` is 367px

This is expected from the current collapse technique:

- Collapsed mobile toolbar sets `max-height:0; overflow:hidden; padding:0;` (`index.html:164`)
- The toolbar still contains real child content in `.toolbar-controls` (`index.html:248`) and those children still compute intrinsic layout height.
- So:
  - **Rendered height / client height** can be 0 because max-height clamps it.
  - **scrollHeight** still reports the total height of the children, which matches the ~367px reported in the brief.

This is exactly why max-height-based collapses are brittle for dynamic control panels.

### 2.8 Hidden-state bug in CSS/JS coupling

There is a significant implementation bug:

- `selCommitteeB`, `selFinancePrev`, and conditionally `selCommitteeA` get `.hidden` toggled in JS (`index.html:2031-2035`)
- Markup also initially sets `class="hidden"` on `selCommitteeB` and `selFinancePrev` (`index.html:289-290`)
- But there is **no generic `.hidden { display:none; }` rule** in the stylesheet.

The only matching hidden rule is `.finance-controls.hidden { display:none }` at `index.html:103`, which applies only when the **finance controls wrapper** has class `hidden`.

Impact:
- The individual hidden selects are not actually hidden by CSS.
- JS assumes a hidden utility class exists, but CSS does not define it.
- This contributes to dynamic-height unpredictability in the toolbar and makes the mobile max-height cap even more fragile.

---

## 3) Responsive issues

### 3.1 Every CSS rule contributing to the “toolbar eats the map” problem

These are the exact selectors/rules involved:

1. `html,body` (`index.html:34`)
   - `overflow:hidden`
   - `position:fixed`
   - `height:100%`
   - `width:100%`

2. `#app` (`index.html:35`)
   - `display:flex`
   - `flex-direction:column`
   - `height:100dvh`
   - `overflow:hidden`
   - `position:fixed`

3. `.header` (`index.html:36`)
   - `flex-shrink:0`
   - `z-index:1000`

4. `.toolbar` (`index.html:45`)
   - `flex-shrink:0`
   - `flex-wrap:wrap`
   - `z-index:1000`

5. Mobile `.header` (`index.html:144`)
   - `flex-wrap:wrap`
   - tighter padding, but still multi-row

6. Mobile `.header-right` (`index.html:153`)
   - `display:contents`

7. Mobile `.header-stats` (`index.html:156`)
   - `width:100%`
   - `order:3`
   - `overflow-x:auto`
   - row padding/border/margin that add vertical height

8. Mobile `.toolbar` (`index.html:164`)
   - `max-height:0`
   - `overflow:hidden`
   - `padding:0`

9. Mobile `.toolbar.expanded` (`index.html:165`)
   - `max-height:500px`
   - `padding:8px 12px`

10. Mobile `.toolbar-controls` (`index.html:166`)
    - `display:flex`
    - `flex-direction:column`
    - `gap:8px`
    - `width:100%`

11. Mobile `.mode-group` (`index.html:174`)
    - `display:grid`
    - `grid-template-columns:repeat(4,1fr)`
    - increases fixed vertical space when button labels wrap

12. Mobile `.mode-btn` (`index.html:175`)
    - `padding:8px 4px`
    - `white-space:normal`
    - `line-height:1.2`
    - button height increases based on label wrapping

13. Mobile `.finance-controls select` / `.toolbar-controls select` (`index.html:169, 204`)
    - larger mobile padding increases total toolbar height

14. Missing `.hidden` utility
    - hidden finance subcontrols can still consume space if JS toggles `.hidden` on them.

### 3.2 Why the header intercepts pointer events on mobile

Root cause chain:

- The app is a fixed viewport shell (`index.html:34-35`), not a scroll document.
- Header is always on top with `z-index:1000` (`index.html:36`).
- On mobile, header becomes a two-row component (`index.html:144-161`).
- The second row is the full-width stats strip (`index.html:156-161`).
- Those stats are dynamically generated HTML (`index.html:1479-1492`, `2229-2231`), including `.stat-label` spans.
- So any map click attempted inside the vertical zone still occupied by the header row will target the header subtree first.

In short: **the map begins lower than it appears conceptually, and the header keeps a real clickable box over the top portion of the viewport.**

### 3.3 Why the toolbar can be visually collapsed but still contain 367px of content

Because `max-height:0` hides overflow instead of removing content from intrinsic layout measurement.

Collapsed state (`index.html:164`):

- `max-height:0`
- `overflow:hidden`
- `padding:0`

But children still exist:

- stacked selects
- 4-column mode grid
- focus select
- export button
- possibly finance controls not truly hidden because of missing `.hidden`

That produces a nonzero `scrollHeight` even while visible height is zero.

### 3.4 How the stat bar breaks on small screens

The mobile stats strip uses this rule (`index.html:156-161`):

- `display:flex`
- `flex-wrap:nowrap`
- `overflow-x:auto`
- `gap:10px`
- child labels at `font-size:8px`
- values at `font-size:12px; max-width:120px`

Breakages:

- The row does not reflow into multiple lines; it becomes a horizontally scrolling strip.
- Important data like winner and margin are visually compressed and easy to miss.
- `font-size:8px` for `.stat-label` is below practical mobile readability and below WCAG-friendly expectations.
- Because the strip is still inside the header, it increases header height and competes with the toolbar for the same scarce vertical space.
- Long winner names are truncated by `max-width:120px` on `.stat-val` (`index.html:160`) and `max-width:180px` desktop (`index.html:43`).

---

## 4) Accessibility audit

### 4.1 Color contrast

Using the declared theme tokens:

Passes:
- `--text` `#e8eaed` on `--bg` `#0f1117`: ~15.66:1
- `--text-muted` `#9aa0a6` on `--surface` `#1a1d27`: ~6.37:1
- `--blue` `#4fc3f7` on `--surface`: ~8.39:1

Failures / concerns:
- `--text-dim` `#6b7280` on `--surface` `#1a1d27`: ~3.48:1 → **fails normal text AA**
- `--text-dim` `#6b7280` on `--bg` `#0f1117`: ~3.9:1 → **fails normal text AA**
- White `#fff` on `--blue-dim` `#2196f3`: ~3.12:1 → **fails normal text AA**

Affected UI:
- `.header-stats .stat-label` (`index.html:44`) uses `--text-dim`
- `.toolbar-label` (`index.html:51`) uses `--text-dim`
- `.cand-votes` (`index.html:87`) uses `--text-dim`
- Active layer button text `.layer-btn.active { color:#fff; background:var(--blue-dim) }` (`index.html:101`) has insufficient contrast for 11-12px text
- Mobile stat labels at `font-size:8px` (`index.html:161`) are especially problematic

### 4.2 Focus indicators

Current focus styling:
- `select:focus` only changes border color (`index.html:48, 106`)
- Buttons rely mostly on hover/active visual states; there are no explicit `:focus-visible` styles for `.mode-btn`, `.layer-btn`, `.export-btn`, `.filter-toggle`

Problems:
- Border-color-only focus is too subtle on dark UI.
- No consistent focus ring token.
- No keyboard focus treatment for mobile legend because it is not focusable.

### 4.3 Screen reader support

Weak overall.

Missing:
- Form labels
- Landmarks
- state announcements
- map region labeling
- semantic toggles
- accessible legend toggle
- accessible dialog semantics for bottom sheet

Also, `headerStats.innerHTML = h` (`index.html:1496`, `2233`) replaces live content without any live-region support.

### 4.4 Keyboard navigation

What works:
- Native buttons and selects are tabbable.

What does not:
- No keyboard mechanism for map precinct inspection.
- No keyboard control for legend toggle because it is a `<div>`.
- Bottom sheet has no focus management when opened.
- No Escape-key close behavior for bottom sheet or toolbar.
- No skip link to move between controls and map.

### 4.5 Touch targets

WCAG target goal is about **44-48px**. Current controls fall short.

Undersized controls:
- `.leaflet-control-zoom a` is `30x30` (`index.html:71`) → too small
- `.filter-toggle` has `padding:6px 8px` and no explicit min-size (`index.html:116`, mobile shown at `150`) → likely under 44px tall/wide depending on icon box
- Desktop `.mode-btn` padding `5px 9px` (`index.html:53`) is too small
- Mobile `.mode-btn` padding `8px 4px` (`index.html:175`) still produces many buttons below 44px height, especially single-line labels
- `.layer-btn` mobile padding `8px 4px` (`index.html:202`) also likely below 44px minimum
- Desktop/mixed selects use small font and tight padding (`index.html:46, 104`)

---

## 5) Proposed CSS architecture

### 5.1 Recommended breakpoint system

Use mobile-first breakpoints and keep them simple:

- `0-767px`: mobile
- `768-1023px`: tablet
- `1024px+`: desktop
- Optional large desktop: `1280px+`

Implementation pattern:

```css
/* base = mobile */

@media (min-width: 48rem) { /* 768px */ }
@media (min-width: 64rem) { /* 1024px */ }
@media (min-width: 80rem) { /* 1280px */ }
```

Do not mix min/max range queries as the primary architecture. Build the narrow-screen layout first.

### 5.2 Recommended design token structure

```css
:root {
  /* color */
  --color-bg: #0f1117;
  --color-surface: #1a1d27;
  --color-surface-2: #242836;
  --color-border: #2d3140;
  --color-text: #e8eaed;
  --color-text-muted: #b0b6c2;
  --color-text-subtle: #8f96a3;
  --color-accent: #4fc3f7;
  --color-accent-strong: #1d8fe0;

  /* type */
  --font-ui: 'Inter', system-ui, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-md: 1rem;
  --text-lg: 1.125rem;

  /* spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;

  /* radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* elevation */
  --shadow-overlay: 0 4px 20px rgba(0,0,0,.4);

  /* layering */
  --z-map: 0;
  --z-overlay: 10;
  --z-shell: 20;
  --z-drawer: 30;
  --z-modal: 40;

  /* component sizes */
  --header-h: 3.5rem;
  --stats-h: auto;
  --controls-w: 22rem;
  --touch-min: 2.75rem;
}
```

### 5.3 Recommended layout strategy

Yes: use **CSS Grid** for the app shell.

#### Desktop

Two-column grid:

```css
.app-shell {
  display: grid;
  grid-template-columns: minmax(18rem, 24rem) minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "controls map"
    "footer footer";
  min-height: 100dvh;
}
```

- Header spans top
- Controls live in a real left rail
- Map gets full remaining area
- No toolbar row consuming map height

#### Mobile

Single-column grid:

```css
.app-shell {
  display: grid;
  grid-template-rows: auto 1fr;
  grid-template-areas:
    "header"
    "map";
}
```

Controls become an off-canvas drawer, not an inline collapsing row.

### 5.4 Recommended semantic HTML structure

```html
<div class="app-shell">
  <header class="app-header">
    ...branding...
    <button
      class="controls-toggle"
      aria-expanded="false"
      aria-controls="controlsPanel"
      aria-label="Open filters">
    </button>
  </header>

  <aside class="controls-panel" id="controlsPanel" aria-label="Map controls">
    <form class="controls-form">
      <fieldset>
        <legend>Data layer</legend>
        ...
      </fieldset>
      <fieldset>
        <legend>Election</legend>
        ...
      </fieldset>
      <fieldset>
        <legend>District</legend>
        ...
      </fieldset>
      <fieldset>
        <legend>View</legend>
        ...
      </fieldset>
    </form>
  </aside>

  <main class="map-main">
    <section class="stats-strip" aria-live="polite" aria-atomic="true"></section>
    <section class="map-region" aria-label="Election precinct map">
      <div id="map"></div>
    </section>
  </main>

  <footer class="app-footer">...</footer>
</div>
```

### 5.5 Mobile sidebar/drawer pattern in pure CSS

Use transform-based off-canvas, not max-height collapse.

```css
.controls-panel {
  position: fixed;
  inset: var(--header-h) 0 0 auto;
  width: min(22rem, 100vw);
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  transform: translateX(100%);
  transition: transform 220ms ease;
  overflow: auto;
  z-index: var(--z-drawer);
}

.controls-panel[data-open="true"] {
  transform: translateX(0);
}

.drawer-backdrop {
  position: fixed;
  inset: var(--header-h) 0 0 0;
  background: rgba(0,0,0,.45);
  opacity: 0;
  pointer-events: none;
  transition: opacity 220ms ease;
}

.drawer-backdrop[data-open="true"] {
  opacity: 1;
  pointer-events: auto;
}
```

Benefits:
- Controls are fully off the map when closed.
- No fake `max-height` animation.
- No scrollHeight confusion.
- No extra map height consumed when drawer is closed.

### 5.6 How to make the toolbar collapsible without z-index nightmares

Principles:

1. **Separate app shell layers from map overlays**
   - Shell: header, drawer, footer
   - Map overlays: legend, popup/info, export title
   - Modal layer: bottom sheet/dialogs

2. **Never collapse a major control surface by max-height inside normal flow**
   - Use off-canvas translate or `visibility` + transform.

3. **Keep header height fixed on mobile**
   - Move stats out of header into a dedicated strip inside `main` or into the drawer.

4. **Use one drawer z-index token**
   - Header `z-shell`
   - Drawer/backdrop `z-drawer`
   - Bottom sheet `z-modal`

5. **Do not use `display: contents` for structural wrappers**
   - Keep `.header-right` real.

---

## 6) Refactoring priority list

### Priority 0 — Critical bugs / immediate fixes

#### A. Add a real `.hidden` utility
**Severity:** Critical  
**Effort:** Very low

Add:

```css
.hidden { display: none !important; }
```

Why first:
- JS already depends on it at `index.html:2031-2035`.
- Without it, finance subcontrols can remain present and distort layout.

#### B. Remove header-growth pressure on mobile
**Severity:** Critical  
**Effort:** Low-medium

Move `#headerStats` out of `.header` on mobile or entirely into `main`.

Why:
- Current mobile stats row is the direct cause of extra header height and pointer interception.

#### C. Replace mobile toolbar `max-height` collapse with drawer/off-canvas pattern
**Severity:** Critical  
**Effort:** Medium

Why:
- Current `max-height:0` / `max-height:500px` system is brittle and will keep breaking as controls change.

### Priority 1 — High-value layout cleanup

#### D. Convert shell to semantic landmarks
**Severity:** High  
**Effort:** Medium

Replace div shell with `header`, `aside`, `main`, `footer`.

#### E. Move to mobile-first CSS
**Severity:** High  
**Effort:** Medium-high

Rebuild base styles for narrow viewports, then add `min-width` enhancements.

#### F. Split toolbar into grouped sections/fieldsets
**Severity:** High  
**Effort:** Medium

Improves accessibility, maintainability, and visual hierarchy immediately.

### Priority 2 — Accessibility fixes

#### G. Add labels, ARIA relationships, and focus styles
**Severity:** High  
**Effort:** Low-medium

Include:
- `label[for]` for selects
- `aria-expanded` and `aria-controls` on filter toggle
- `aria-pressed` on toggle buttons
- `aria-live="polite"` on stats
- focus rings for all interactive controls

#### H. Increase touch target sizes
**Severity:** High  
**Effort:** Low

Start with:
- zoom controls to 44x44 minimum
- buttons min-height 44px
- selects min-height 44px

#### I. Fix contrast tokens
**Severity:** Medium-high  
**Effort:** Low

Raise contrast for `--text-dim` and active button foreground/background combinations.

### Priority 3 — Structural rewrite / maintainability

#### J. Split single-file architecture
**Severity:** Medium  
**Effort:** High

Recommended separation:
- `styles/tokens.css`
- `styles/base.css`
- `styles/layout.css`
- `styles/components/*.css`
- `scripts/ui-shell.js`
- `scripts/map.js`
- `scripts/data-election.js`
- `scripts/data-finance.js`

#### K. Introduce component state classes/data attributes
**Severity:** Medium  
**Effort:** Medium-high

Prefer:
- `[data-open="true"]`
- `[data-layer="finance"]`
- `[data-mode="winner"]`

instead of mixed inline handlers + class toggles + direct style assignment.

---

## 7) Quick wins vs rewrite

### Quick wins (same day)

1. Add `.hidden { display:none!important; }`
2. Add `aria-controls`, `aria-expanded`, `aria-pressed`
3. Add visible `:focus-visible` styles
4. Increase touch target sizes to 44px minimum
5. Improve contrast for `--text-dim` and active blue buttons
6. Convert mobile legend title into a real button
7. Move `#headerStats` below header in DOM on mobile

### Short refactor (1-3 days)

1. Replace max-height toolbar with slide-in drawer
2. Convert shell to semantic elements
3. Rebuild toolbar into fieldsets and sections
4. Normalize z-index tokens
5. Remove `display: contents` from `.header-right`

### Larger rewrite (multi-day)

1. Full mobile-first CSS rewrite
2. Split CSS and JS into modules
3. Create explicit app-shell, controls-panel, map-main, overlays architecture
4. Introduce keyboard-accessible map interaction model

---

## 8) JS-coupled CSS issues that complicate refactoring

These are the biggest CSS/JS couplings to watch:

1. **Inline event handlers in markup**
   - `onclick="toggleToolbar()"` at `index.html:239`
   - `onclick="setDataLayer(...)"` at `index.html:252-253`
   - `onclick="exportPNG()"` at `index.html:305`

2. **Direct style mutation rather than state classes**
   - `ec.style.display = ''` and `ec.style.display = 'none'` in `setDataLayer()` (`index.html:1924-1932`)

3. **JS assumes CSS utility classes that do not exist**
   - `.hidden` on finance subcontrols (`index.html:2031-2035`)

4. **State-dependent layout inside header**
   - `headerStats.innerHTML = h` (`index.html:1496`, `2233`) changes header height dynamically

5. **Viewport mode logic duplicated in CSS and JS**
   - CSS breakpoint at `768px`
   - JS `matchMedia('(max-width: 768px)')` at `index.html:342, 345`
   - This is acceptable, but layout logic should be simplified so JS is not compensating for CSS structure.

6. **Legend markup shape changes by viewport**
   - `updateLegend()` and `updateFinanceLegend()` wrap content in `.legend-body` only when `isMobile` (`index.html:1573-1585`, `2208-2217`)
   - Better to keep a stable DOM structure and toggle only state/visibility.

---

## 9) Recommended target architecture

### Desktop
- Fixed top header, compact and single-row
- Left sidebar for all controls
- Map occupies the entire right pane
- Stats sit above map or inside sidebar summary block
- Legend and info panels remain map overlays

### Mobile
- Fixed compact header only: logo/title + filter button
- No stats row inside header
- Map fills remaining viewport immediately below header
- Controls open as right-side drawer or full-height sheet
- Stats move into drawer top section or a compact floating chip row inside `main`
- Legend stays closed by default and opens only on explicit tap using a button

---

## 10) Recommended first implementation steps

1. Add `.hidden` utility and verify finance control visibility logic.
2. Remove `#headerStats` from `.header`; place it below header or in drawer.
3. Replace `.toolbar` mobile collapse with off-canvas drawer.
4. Convert shell to `header` / `aside` / `main` / `footer`.
5. Add real labels and focus-visible styles.
6. Increase control sizes and fix contrast tokens.
7. After layout is stable, modularize CSS and JS.

---

## Bottom line

The mobile bug is not a Leaflet problem. It is an **app-shell layout problem** caused by a fixed viewport, a growing two-row header, a high-z-index toolbar/header stack, and a max-height-based mobile collapse. The fastest safe path is:

- fix `.hidden`
- pull stats out of the header
- replace the mobile toolbar with a drawer
- move to a semantic grid shell

That will remove the header interception issue, free vertical space for the map, and create a foundation that can scale beyond the current 27-control toolbar.
