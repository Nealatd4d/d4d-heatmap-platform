# Redesign Re-Review

## Verdict

**PASS** — All 5 previously-blocking issues appear to be fixed correctly, and the pointer-events hardening was applied. I did not find any new bugs from these fixes that would break the redesigned experience.

## Findings

### 1. `aria-expanded` state
**PASS**

- `toggleToolbar()` now toggles the toolbar, syncs the visual active state, and explicitly writes `aria-expanded` using the real expansion result.
- The mobile race-selection collapse path now removes `.expanded`, removes the toggle’s `.active`, and sets `aria-expanded='false'`.
- The resize transition handler also clears `.expanded`, removes `.active`, and sets `aria-expanded='false'` when collapsing into mobile mode.
- I did not find the old `patchToggleToolbar` wrapper anymore, which is correct because the actual `toggleToolbar()` implementation now owns the ARIA update directly.

### 2. Finance mode handler calls `syncModeStrip()`
**PASS**

- The finance mode button click handler now updates `currentFinanceMode`, refreshes finance control visibility, calls `renderFinance()`, and then calls `syncModeStrip()`.
- That closes the prior active-state mismatch between toolbar finance buttons and the mobile mode strip.

### 3. Dynamic mode strip
**PASS**

- There is now an `updateModeStripButtons()` function that rebuilds the strip contents from JavaScript instead of relying on fixed election-only markup.
- The code defines both `ELECTION_STRIP_MODES` and `FINANCE_STRIP_MODES`.
- `updateModeStripButtons()` switches between those constants based on `dataLayer`, rebuilds the buttons, appends the trailing “more” button, and then re-syncs active state.
- `setDataLayer()` now calls `updateModeStripButtons()` and `syncModeStrip()` after changing layers.

### 4. `map.invalidateSize()` on layout transitions
**PASS**

- The resize handler now calls `map.invalidateSize()` when `wasMobile !== isMobile`.
- There is also an `orientationchange` listener that calls `map.invalidateSize()` after a short delay.
- This addresses the prior risk of Leaflet sizing glitches when the layout changes between desktop and mobile forms.

### 5. Mobile stats strip
**PASS**

- On mobile, `.header-stats` is no longer hidden.
- The mobile media block sets it to `display:flex` and enables horizontal scrolling with `overflow-x:auto` and touch scrolling behavior.
- This matches the intended compact, scrollable mobile stats row.

### 6. Toolbar pointer-events behavior
**PASS**

- The base `.toolbar` style now uses `pointer-events:none`.
- `.toolbar.expanded` restores `pointer-events:auto`.
- The desktop media-query override sets the always-visible sidebar toolbar back to `pointer-events:auto`.
- That should prevent the collapsed mobile sheet from blocking taps on the mode strip underneath it.

## Regression check

### No new blocking bugs found from these fixes

I specifically checked for likely side effects from the changes above and did not find a new functional regression:

- The new dynamic strip still routes election buttons to `data-mode` buttons and finance buttons to `data-fmode` buttons through `handleStripClick()`.
- The finance strip only surfaces three primary finance modes plus the “more” button, but that is not inherently a bug: the strip remains functional in finance mode, and the remaining finance controls are still reachable through the toolbar.
- The direct ARIA updates are implemented in the real close/open paths rather than through a wrapper, which is the safer architecture.
- The added `map.invalidateSize()` calls are scoped to layout transitions and orientation changes, so they should not create unnecessary redraw churn during every resize event.

## Conclusion

This re-review clears the original five required fixes plus the pointer-events improvement. I would mark the redesign review as **PASS** based on the current `index.html` implementation.
