# Redesign Code Review

## Critical Issues

1. **FAIL — `aria-expanded` never updates when the inline filter button is clicked.** The button still calls the global `toggleToolbar()` via inline `onclick` (`#filterToggle` at lines 550–554), but the local function only toggles `.expanded` and `.active` and never writes the ARIA state (lines 1910–1916). The later `patchToggleToolbar()` wraps `window.toggleToolbar`, not the lexical `toggleToolbar` function referenced by the inline handler inside the same document, so the wrapper does not fix the inline click path (lines 2857–2864). Result: the control visually opens/closes, but `aria-expanded` stays stale at its initial value.

2. **FAIL — finance mode strip active state is not synchronized when finance mode changes inside the toolbar.** `syncModeStrip()` understands finance state by comparing strip button keys to `currentFinanceMode` (lines 2819–2829), but the finance mode button handler only updates `currentFinanceMode`, calls `updateFinanceControlVisibility()`, and re-renders (lines 2718–2725). It never calls `syncModeStrip()`, so after switching finance modes inside the sheet/sidebar, the persistent strip can show the wrong active button.

3. **FAIL — the mobile mode strip does not cover most finance modes.** The strip only provides `turnout`, `winner`, `margin`, and `more` buttons in markup (lines 643–647), while finance modes are `supporters`, `whales`, `donor_margin`, `candidate`, `vs`, `money_delta`, `swing`, and `votes` (lines 604–612). In finance layer, strip clicks look for matching `data-fmode` values using those election-mode keys (lines 2841–2844), which means the first three buttons have no finance targets and effectively do nothing. This breaks the requirement to keep the strip functional when finance is active.

## Bugs Found

1. **Mobile stats-strip behavior does not match the redesign spec.** The spec called for a compact mobile stats strip rather than removing stats from the header, but the redesign hides `#headerStats` on mobile (`.header-stats{display:none}` at lines 349–350). The JS still updates `headerStats.innerHTML` for both election and finance layers (lines 1783–1815 and 2541–2553), but that content is invisible until the toolbar is opened.

2. **Toolbar-closing code leaves ARIA stale in other paths too.** Race selection collapses the toolbar on mobile by directly removing `.expanded` and `.active` (lines 2041–2047), and the resize handler also directly removes those classes when entering mobile (lines 665–672). Neither path updates `aria-expanded`, so assistive state can drift even if the wrapper were fixed.

3. **Orientation/layout changes do not trigger a Leaflet size recalculation.** The app listens for viewport changes and flips `isMobile`, closes the bottom sheet, and removes toolbar classes (lines 661–674), but there is no `map.invalidateSize()` call anywhere near resize/orientation handling. Because the map container changes between full-width mobile flex layout and desktop grid/sidebar layout, this omission risks clipped tiles or incorrect interaction bounds after rotation/resizing.

4. **The desktop sidebar width is not always 260px.** The main desktop grid uses `--sidebar-w:260px` (lines 49–52 and 434–441), but a tablet override reduces it to `220px` at lines 522–523. That directly contradicts the checklist item asking whether desktop keeps a 260px sidebar.

5. **The mobile map is not strictly “full bleed between header and mode strip” when the toolbar is open.** The toolbar is a fixed sheet above the strip (`bottom:var(--mode-strip-h)` and `z-index:var(--z-toolbar-sheet)` at lines 146–157), so the map remains full-size behind it rather than resizing. That is fine as an overlay pattern, but it means the visible map area is partially obscured whenever controls are open.

6. **The spec said “Do NOT modify any JavaScript logic,” but JS was materially changed.** New mobile-detection logic was added at lines 660–674, `syncModeStrip()` and mode-strip delegation were added at lines 2817–2853, and `window.toggleToolbar` is patched at lines 2855–2865. Some of those additions are useful, but they violate the stated implementation constraint.

## Warnings

1. **`transform: translateY(100%)` is probably sufficient to hide the toolbar sheet, but only because the sheet is anchored above the mode strip.** The toolbar is fixed at `bottom:48px` and translated by its own height (lines 146–157), so it should move fully below the viewport edge in normal cases. I do not see an extra bottom safe-area guard, so on devices with unusual browser chrome or inset behavior this is worth manual testing.

2. **Z-index ordering is mostly coherent, but the export overlay still uses a hard-coded value instead of the token scale.** Header = 500, mode strip = 600, toolbar = 700, bottom sheet = 800, and map overlays = 100 (lines 38–52, 236, 252, 265, 281), which is clean. `#exportTitle` still uses `z-index:850` at lines 330–335, so it sits outside the declared scale and should be documented as intentional.

3. **Desktop sidebar scroll behavior looks correct, but the toolbar content container relies on inherited flow rather than a stronger section layout.** The sidebar is `height:100%` with `overflow-y:auto` (lines 464–477), and controls/selects are widened to fill the column (lines 484–505). That should work, but long `viewOpts` / Vs checklists still merit manual verification because `.vs-checklist` only gets `max-width:100%` on desktop (line 495) and no dedicated height cap there.

4. **The mobile Vs checklist should fit, but it may feel cramped.** The checklist gets `max-height:120px` and `overflow-y:auto` on mobile (lines 377–378), which prevents runaway growth. That is good defensively, but it may still be tight for long candidate lists inside a 70vh toolbar sheet.

5. **Loading spinner centering remains correct relative to `.map-wrap`, not necessarily to the currently visible map area.** The loader is absolutely centered with `top:50%; left:50%; transform:translate(-50%,-50%)` inside `.map-wrap` (lines 317–321). Since mobile overlays sit on top of the map rather than changing map dimensions, the spinner can appear visually under an open sheet if loading occurs while controls are expanded.

6. **Keyboard accessibility is only partial for the mode strip.** Using real `<button>` elements inside a `<nav>` is a good baseline (lines 643–647), so tab/focus/Enter/Space should work. But there are no explicit focus-visible styles for `.strip-btn`, and the active-state mismatch in finance mode reduces usability for keyboard users too.

## Good Decisions

1. **All critical legacy IDs appear preserved.** The redesigned markup still contains every required ID: `selElection`, `selType`, `selRace`, `selFocus`, `toolbar`, `electionControls`, `financeControls`, `electionModes`, `financeModes`, `viewOpts`, `headerStats`, `filterToggle`, `map`, `legend`, `infoPanel`, `bottomSheet`, `bottomSheetContent`, `loader`, `landing`, `exportTitle`, `selFinanceElection`, `selCommitteeA`, `selCommitteeB`, `selFinancePrev`, and `modeStrip` (lines 549–647). That means the `$()` helper (`document.getElementById`) should still resolve the expected nodes (lines 752–757 and 2166–2169).

2. **`toggleToolbar()` still toggles `.expanded` on `#toolbar` exactly as required.** The function does `tb.classList.toggle('expanded')` on the toolbar (lines 1910–1916), and the mobile CSS uses `.toolbar.expanded { transform:translateY(0); padding:16px; }` against a hidden base state of `translateY(100%)` (lines 144–162). That preserves the original contract while switching to a sheet animation.

3. **`setDataLayer()` still preserves the expected election/finance visibility model.** It grabs `#electionControls` and `#financeControls` by ID (lines 2242–2243), hides election controls with `style.display = 'none'`, and toggles the finance panel through the `.hidden` class (lines 2244–2258). The added utility rule `.hidden{display:none!important}` at line 60 is the right compatibility fix for JS that toggles `.hidden` on finance selectors.

4. **`exportPNG()` remains compatible with `.map-wrap` capture.** The export function still queries `.map-wrap` directly (line 2734) and passes that node to `htmlToImage.toPng()` (lines 2791–2799). Keeping `#exportTitle` inside `.map-wrap` (lines 625–634) also preserves the export-title overlay behavior.

5. **The mobile-first CSS architecture is real in the final file.** Base styles define the mobile shell and components first (lines 73–335), then desktop overrides are applied with `@media(min-width:769px)` (lines 432–519). That is a substantial improvement over the old desktop-first structure shown in the pre-redesign file, where the main mobile behavior lived under `@media(max-width:768px)` and the toolbar still collapsed via `max-height` instead of becoming a fixed sheet.

6. **Desktop grid conversion is structurally solid.** `#app` switches to CSS Grid with `grid-template-columns:var(--sidebar-w) 1fr` and named areas `header / sidebar / map / footer` (lines 434–448). The toolbar becomes static with internal scrolling (lines 464–477), the filter-toggle is hidden on desktop (line 461), the mode strip is hidden on desktop (line 507), and the bottom sheet is also disabled on desktop (line 510).

7. **Touch target work is generally good.** The filter toggle is sized to the 44px token (lines 126–137), Leaflet zoom controls are increased to 44×44 (lines 227–231), strip buttons use the 48px strip height (lines 285–305), and mobile mode buttons, selects, layer buttons, checklist labels, and export button all get `min-height:var(--touch-min)` in the mobile block (lines 354–419).

8. **Map-overlay stacking is mostly well organized.** Map overlays use the lower token layer (`--z-map-overlay` / `--z-loading`), the header sits at 500, the persistent mode strip at 600, toolbar sheet at 700, and precinct bottom sheet at 800 (lines 38–52, 236, 252, 265, 281, 317). That correctly ensures a tapped precinct’s bottom sheet opens above the toolbar sheet.

9. **Semantic HTML upgrades are sensible and low-risk.** Converting the shell to `<header>`, `<aside>`, `<main>`, and `<footer>` at lines 535, 558, 625, and 650 improves semantics without breaking ID-based JS.

## Pass/Fail Verdict

**Verdict: FAIL (needs fixes before merge).**

The redesign gets the big structural pieces mostly right: preserved IDs, mobile-first CSS, a legitimate desktop grid/sidebar, a real bottom-sheet toolbar, and export compatibility. But it misses two functional requirements that are central to the redesign: the new mode strip breaks in finance mode, and the new ARIA-expanded behavior is not actually wired correctly. I would block merge until at least these are fixed:

1. Update the real `toggleToolbar()` implementation to write `aria-expanded` directly, and also sync ARIA anywhere the toolbar is closed programmatically.
2. Call `syncModeStrip()` from the finance mode handler.
3. Decide what the strip should do in finance mode, then implement matching strip buttons/labels or a finance-aware fallback.
4. Add `map.invalidateSize()` on resize/orientation transitions.
5. Reconcile the mobile stats-strip behavior with the redesign spec (either restore a compact visible stats row or explicitly change the spec).