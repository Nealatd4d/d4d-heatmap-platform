# Mobile-First Redesign Spec — Phase 1+2

## Goal
Restructure the CSS and HTML of the D4D Heatmap Platform to be mobile-first, with a bottom-sheet control pattern on mobile and a left sidebar on desktop. The map should be the hero element on all viewports.

## Critical Constraints
- **Do NOT modify any JavaScript logic** — only HTML structure and CSS. All JS selectors (`$('selElection')`, `$('toolbar')`, etc.) must continue to work. All element IDs must remain the same.
- **Do NOT rename any element IDs** — `selElection`, `selType`, `selRace`, `selFocus`, `toolbar`, `electionControls`, `financeControls`, `electionModes`, `financeModes`, `viewOpts`, `headerStats`, `filterToggle`, `map`, `legend`, `infoPanel`, `bottomSheet`, `bottomSheetContent`, `loader`, `landing`, `exportTitle`, etc.
- The `toggleToolbar()` function in JS toggles class `expanded` on `#toolbar`. This must still work on mobile (but the CSS animation should change from max-height to a bottom-sheet slide-up).
- The `setDataLayer()` function toggles between `#electionControls` and `#financeControls` visibility.
- The mode buttons (`.mode-btn`) are clicked to change view modes. Their `data-mode` and `data-fmode` attributes are used by JS.
- The export button calls `exportPNG()` which captures `.map-wrap`.

## Mobile Layout (≤768px)

### Structure (top to bottom)
```
┌─────────────────────────────────────┐
│ [D4D Logo] D4D Heatmap       [⚙]   │  ← 44px sticky header
│ Winner · Daniel Biss · +3.5pp  ▸   │  ← 28px context/stats strip
├─────────────────────────────────────┤
│                                     │
│            MAP (full bleed)         │  ← fills remaining space
│                                     │
│  [+]                     [Legend ▾] │
│  [-]                                │
│                                     │
├─────────────────────────────────────┤
│ [Winner][Turnout][Margin]    [⋮]   │  ← 48px sticky bottom mode strip
└─────────────────────────────────────┘
```

### When [⚙] (filter icon) is tapped:
The `#toolbar` slides up from the bottom as a sheet overlay (not pushing content down).
- `position: fixed; bottom: 48px; left: 0; right: 0;`
- Slides up with `transform: translateY(100%)` → `translateY(0)` when `.expanded`
- Max-height: 70vh, overflow-y: auto
- Contains all controls in scrollable sections
- Dark scrim behind it (optional)

### Bottom Mode Strip (NEW element or repurposed)
- Always visible at bottom of screen
- Shows 3 primary modes + a "more" (⋮) button
- This is a NEW persistent element. On mobile, the mode buttons inside #electionModes in the toolbar should be hidden (they'll be in the sheet). The bottom strip has its OWN buttons that call the same JS functions.
- ACTUALLY — simpler approach: keep the mode buttons in #electionModes but ALSO display a persistent bottom strip that clones/mirrors the active mode. When a bottom strip button is clicked, it clicks the corresponding mode button in the toolbar. This avoids duplicating JS logic.
- SIMPLEST approach: On mobile, move #electionModes out of the toolbar flow and position it fixed at the bottom. The toolbar (sheet) shows everything EXCEPT the mode buttons.

### Stats Strip
- Replace the current scrolling `#headerStats` with a compact single-line format on mobile
- Show: `Winner · Daniel Biss · +3.5pp` (or `Turnout 27.6%` depending on mode)
- Current JS writes to `#headerStats` with `.stat` divs — the CSS just needs to restyle these into a compact row

### Legend
- Starts closed (already works)
- Cap max-height at `min(300px, 40vh)`
- Must not conflict with bottom strip z-index

## Desktop Layout (≥769px)

### Structure
```
┌──────────┬─────────────────────────────────────────────┐
│ [Header] │ [Header continued — stats on right]          │  50px
├──────────┼─────────────────────────────────────────────┤
│          │                                              │
│ SIDEBAR  │              MAP                             │
│ 260px    │          (fills rest)                        │
│          │                                              │
│ Scrolls  │  [+]                          [Legend]       │
│ internally│  [-]                                        │
│          │                                              │
│          │                                              │
│          ├─────────────────────────────────────────────┤
│          │  Footer                                      │
└──────────┴─────────────────────────────────────────────┘
```

### Sidebar
- 260px wide, fixed height (fills from header to footer)
- Internal scroll for overflow
- Contains ALL toolbar controls in stacked sections:
  1. **DATA LAYER** — Election Results / Campaign Finance toggle
  2. **RACE** section — Election, Type, Race dropdowns (full-width within sidebar)
  3. **VIEW** section — Mode buttons in a vertical list or 2-column grid
  4. **VIEW OPTIONS** — #viewOpts (candidate selectors etc.)
  5. **FOCUS** — Municipality dropdown
  6. **FINANCE** section — #financeControls (when visible)
  7. **EXPORT** — Export PNG button (full-width)
- Subtle section dividers between groups
- The sidebar IS the `#toolbar` element, just restyled with CSS

### Header on Desktop
- Header spans full width (above both sidebar and map)
- Stats remain on the right side of header
- The filter-toggle button is hidden on desktop (display:none)

## CSS Architecture

### Approach: Mobile-first
- Base styles = mobile layout
- `@media (min-width: 769px)` = desktop overrides

### Key CSS Changes

#### 1. App shell layout
```css
/* Mobile base */
#app {
  display: flex;
  flex-direction: column;
  height: 100dvh;
}

/* Desktop */
@media (min-width: 769px) {
  #app {
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 260px 1fr;
    grid-template-areas:
      "header header"
      "sidebar map"
      "sidebar footer";
  }
  .header { grid-area: header; }
  .toolbar { grid-area: sidebar; }
  .map-wrap { grid-area: map; }
  .footer { grid-area: footer; }
}
```

#### 2. Toolbar → sidebar on desktop, bottom-sheet on mobile
```css
/* Mobile: slide-up sheet */
.toolbar {
  position: fixed;
  bottom: 48px; /* above mode strip */
  left: 0;
  right: 0;
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-radius: 12px 12px 0 0;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  z-index: 1050;
  max-height: 70vh;
  overflow-y: auto;
  padding: 0;
}
.toolbar.expanded {
  transform: translateY(0);
  padding: 16px;
}

/* Desktop: static sidebar */
@media (min-width: 769px) {
  .toolbar {
    position: static;
    transform: none;
    border-radius: 0;
    border-top: none;
    border-right: 1px solid var(--border);
    max-height: none;
    overflow-y: auto;
    padding: 16px;
    z-index: auto;
  }
}
```

#### 3. Bottom mode strip (mobile only)
Need to either:
a) Create a new element `#modeStrip` in HTML, or
b) Use CSS to position `#electionModes` fixed at bottom on mobile

Option (b) is cleaner — no new HTML/JS needed:
```css
@media (max-width: 768px) {
  #electionModes {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1040;
    background: var(--surface);
    border-top: 1px solid var(--border);
    display: flex;
    padding: 6px 8px;
    gap: 4px;
  }
  /* Show only 3 primary + overflow */
  #electionModes .mode-btn:nth-child(n+4) { display: none; }
  /* Add a "more" indicator somehow */
}
```

PROBLEM: This removes modes from the toolbar sheet. Better approach:

Option (c): Add a NEW small HTML element for the mobile bottom strip with 3 buttons + more. These buttons programmatically click the real mode buttons. This is the cleanest separation.

Add to HTML (inside #app, after .bottom-sheet):
```html
<div class="mode-strip" id="modeStrip">
  <button class="strip-btn active" data-strip-mode="winner">Winner</button>
  <button class="strip-btn" data-strip-mode="turnout">Turnout</button>
  <button class="strip-btn" data-strip-mode="margin">Margin</button>
  <button class="strip-btn" data-strip-mode="more">⋮</button>
</div>
```

JS for the strip (add near bottom of script):
```javascript
/* ═══════════════════ MOBILE MODE STRIP ═══════════════════ */
const modeStrip = $('modeStrip');
if (modeStrip) {
  modeStrip.querySelectorAll('.strip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = btn.dataset.stripMode;
      if (m === 'more') {
        // Open the toolbar sheet
        toggleToolbar();
        return;
      }
      // Click the real mode button
      const realBtn = document.querySelector(
        dataLayer === 'finance'
          ? `.mode-btn[data-fmode="${m}"]`
          : `.mode-btn[data-mode="${m}"]`
      );
      if (realBtn) realBtn.click();
      // Update strip active state
      modeStrip.querySelectorAll('.strip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}
```

Also need to sync strip active state when mode changes via the toolbar. Add to existing mode button click handlers:
```javascript
// After setting currentMode, update strip
function syncModeStrip() {
  if (!modeStrip) return;
  modeStrip.querySelectorAll('.strip-btn').forEach(b => {
    const m = b.dataset.stripMode;
    if (m === 'more') return;
    b.classList.toggle('active', m === currentMode);
  });
}
```

## Typography Fixes (Phase 1)
- Minimum font size: 12px everywhere
- stat-label on mobile: 10px (was 8px)
- stat-val on mobile: 14px (was 12px)
- mode-btn: 12px (was 11px)
- toolbar-label: 11px (was 10px)

## Touch Target Fixes (Phase 1)
- All buttons and interactive elements on mobile: min-height 44px
- mode-btn on mobile: min-height 44px, padding 10px
- select on mobile: min-height 44px
- filter-toggle: min 44x44px

## Z-Index Scale
```css
:root {
  --z-map: 1;
  --z-map-overlay: 100;     /* legend, info-panel, landing */
  --z-loading: 200;
  --z-header: 500;
  --z-mode-strip: 600;      /* mobile bottom strip */
  --z-toolbar-sheet: 700;   /* mobile toolbar as sheet */
  --z-bottom-sheet: 800;    /* precinct detail bottom sheet */
  --z-scrim: 650;           /* optional scrim behind toolbar sheet */
}
```

## Missing CSS Rule (Bug Fix)
Add: `.hidden { display: none !important; }`
This is needed for `#selCommitteeB.hidden` and `#selFinancePrev.hidden`.

## What NOT to Change
- All JS logic, fetch calls, Supabase queries, render functions
- Element IDs
- Data attributes on buttons
- The existing bottom sheet for precinct details (#bottomSheet)
- The existing legend structure and behavior
- The existing info-panel structure
- The export overlay structure
- CDN imports
