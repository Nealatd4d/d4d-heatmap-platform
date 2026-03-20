# D4D Election Heatmap Platform — UI Visual Audit

**Auditor:** Senior UI Designer  
**Date:** March 20, 2026  
**Scope:** Visual design, responsive layout, component consistency, and design system proposal  
**Reference builds:** Vercel Dashboard, Linear, Figma, Bloomberg Terminal

---

## Executive Summary

The platform has a solid technical foundation and a coherent dark-theme direction. The core problems are not about taste — they are structural. The toolbar is a linear list of 27 controls with no visual grouping, causing it to consume 31% of desktop viewport and 44%+ of mobile viewport when open. Typography runs at 10–11px throughout, making the entire interface feel like fine print. The stat bar is the most data-dense element but gets the least visual weight. The color palette is functional but cold — it reads as generic "developer dark mode" rather than a purpose-built civic data tool.

**Priority order for fixes:**
1. Mobile toolbar architecture (blocks map interaction — critical)
2. Toolbar visual hierarchy (27 undifferentiated controls)
3. Stat bar elevation (key data buried at 10–13px)
4. Type scale (everything at 10–11px is illegible at arm's length)
5. Color system refinement (palette is inconsistent — two blues, no semantic palette)

---

## 1. Current Visual Design Critique

### 1.1 Typography

**Issues identified:**

| Element | Current Size | Problem |
|---|---|---|
| `toolbar-label` | 10px uppercase | Below legibility floor; 12px is absolute minimum |
| `mode-btn` | 11px | Too small for a tap target label; 13px minimum |
| `toolbar select` | 11px | Undersized for an interactive control |
| `stat-label` | 10px (mobile: 8px) | 8px is indefensible — invisible on phone screens |
| `stat-val` | 13px (mobile: 12px) | Key numbers should be 16–20px |
| `legend-row` | 10px | Map labels must be readable at distance |
| `info-panel` body | 11px | Bottom-of-barrel readability |
| `cand-votes` | 10px | Floor violation |

**Root problem:** The entire interface was scaled down uniformly, as if trying to fit more on screen. This is a false economy — you fit more but users read less. The Bloomberg Terminal ships at 12–13px minimum for a reason: traders glance at screens from 18 inches and need to absorb data at speed.

**Recommendations:**
- Set a hard floor of **12px** for any rendered text (12px = WCAG minimum, industry floor)
- Promote `stat-val` to **18–20px** — these are headline numbers
- Promote `mode-btn` labels to **12–13px**
- `toolbar-label` section headers: **11px** (uppercase with tracking is acceptable at 11px for section dividers only, not interactive text)
- `info-panel` body text: **12px minimum**
- `legend-row` labels: **11px minimum**

**Font choice:** Inter is a solid, highly-legible grotesque — keep it. However, consider loading the `--font-feature-settings: "cv11" on` (single-story 'a') and `"ss01" on` (geometric digits) variants for cleaner numerics in the stat bar. The current `font-variant-numeric: tabular-nums` on stat values is correct and should be applied universally to any number that changes or aligns with other numbers.

---

### 1.2 Color

**Current palette:**
```
--bg:          #0f1117  (near-black, blue-shifted)
--surface:     #1a1d27  (dark navy)
--surface-alt: #242836  (mid navy)
--surface-hover: #2a2e3d
--text:        #e8eaed  (near-white, slightly cool)
--text-muted:  #9aa0a6  (blue-grey)
--text-dim:    #6b7280  (grey)
--blue:        #4fc3f7  (light cyan — primary interactive)
--blue-dim:    #2196f3  (Material Blue 500 — active state background)
--yellow:      #fdd835  (winner highlight)
--border:      #2d3140
```

**Problems:**

1. **Two blues with contradictory semantics.** `--blue` (`#4fc3f7`) is light cyan — used for text color on active state. `--blue-dim` (`#2196f3`) is Material Blue — used as the background fill for active state. These are from different design systems and should never coexist. On `.layer-btn.active`, the active button gets `background: var(--blue-dim); color: #fff` — that's a Material Design component sitting inside what should be a custom design system. On `.mode-btn.active`, the active button gets `border-color: var(--blue-dim); color: var(--blue)` — a different treatment entirely. Pick one accent and apply it consistently.

2. **No semantic palette.** There is no defined error, warning, or success color. When a race has "No data," the legend just shows a grey swatch. There is no visual signal when an async operation fails. The map's own candidate colors (blues, pinks, oranges, yellows) will visually compete with the UI accent `#4fc3f7` — the map canvas becomes an extension of the interface accent, causing confusion.

3. **Background elevation is backwards.** The header and toolbar use `--surface` (`#1a1d27`) which is lighter than `--bg` (`#0f1117`). This correctly lifts chrome above map background. However, `--surface-alt` is used for interactive control fills (selects, mode buttons), which makes them feel like third-level surfaces rather than interactive affordances. Controls should have a distinct treatment — a subtle 1px inset shadow or a slightly different hue — to read as "things you can interact with."

4. **`--yellow: #fdd835`** is a saturated lemon yellow on dark background. It achieves reasonable contrast (~10:1 on `--bg`) but looks harsh and unpolished. It functions as a "winner" highlight in the info panel but doesn't appear in the legend or stat bar. Inconsistent application weakens it as a semantic signal.

5. **Contrast check on critical paths:**
   - `--text-muted` (`#9aa0a6`) on `--surface` (`#1a1d27`): ~5.1:1 — passes AA ✓
   - `--text-dim` (`#6b7280`) on `--surface` (`#1a1d27`): ~3.4:1 — **fails AA for body text** ✗ (passes only for large text ≥18px)
   - `--text-dim` on `--surface-alt` (`#242836`): ~3.1:1 — **fails AA** ✗
   - `--blue` (`#4fc3f7`) on `--surface` (`#1a1d27`): ~9.8:1 — passes ✓
   - `stat-label` uses `--text-dim` at 8px on mobile: **critical failure** — ~3.1:1 at 8px ✗✗

**The `--text-dim` color (`#6b7280`) is used too broadly.** It should only appear at ≥18px or for purely decorative separators. Move functional text at small sizes to `--text-muted` minimum.

---

### 1.3 Spacing

**Current situation:**

The toolbar has `padding: 6px 16px` and a `gap: 8px` between controls. This is workable but the vertical rhythm is broken by the `toolbar-label` elements (uppercase section headers) that sit inline in the flex row. The result is a jumbled strip where controls and their labels have no clear parent-child relationship.

**Desktop toolbar height:** ~275px for 27 controls in a wrapping flex row. This is caused by:
- All controls in a single flat `flex-wrap: wrap` container
- No section grouping with visual separators
- `toolbar-sep` elements (`width: 1px; height: 20px`) are invisible at the gaps — they don't create meaningful sections

**Specific spacing problems:**
- `mode-group` has `gap: 2px` between buttons — this is so tight the buttons appear to touch. At 2px, the visual grouping is lost because you can't tell where one ends and the next begins on dark backgrounds. Minimum should be **4px**; 6px is better.
- `cand-bar-wrap` height is `5px` — this sparkline-style bar is too narrow to convey meaningful percentage data. **8px minimum** for bar charts that encode actual vote percentages.
- `info-panel` padding `12px 14px` is fine but the internal `padding: 2px 0` on info rows is too compressed. Use **4px 0** for cleaner breathing room.
- Legend `padding: 10px 12px` with `padding: 1px 0` on rows — legend rows need **3px 0** minimum to be scannable.

---

### 1.4 Components

**Button hierarchy — current state:** There are essentially three button styles that are not formally differentiated:

| Component | Intent | Current Style |
|---|---|---|
| `.layer-btn.active` | Primary toggle | Blue filled (`#2196f3` bg, white text) |
| `.mode-btn.active` | Secondary toggle | Subtle (border + text color) |
| `.export-btn` | Action | Ghost (surface-alt bg, muted text) |
| `.filter-toggle` | Utility | Icon-only ghost |

The problem: `layer-btn.active` uses Material's filled blue — a "primary" treatment. `mode-btn.active` uses a subtle "secondary" treatment. But these controls are semantically equivalent (both are mutually exclusive mode selectors). They should use the same active state style. The current inconsistency suggests two different components were built at different times without shared tokens.

**Select dropdowns:** The custom dropdown arrow SVG is correctly implemented with `appearance: none`. However:
- Min-width of 110px means the "U.S. Representative, 9th District - DEM" option gets truncated — this is visible in the desktop screenshot
- Font-size 11px is too small for a control that users must read to make selections
- There is no `height` set, so the control height is implicit from padding (`5px 8px` = ~30px with line-height). Should be explicit: `min-height: 32px` desktop, `44px` mobile

**Labels (`.toolbar-label`):** These uppercase section labels are styled identically to tertiary text everywhere else. They have no visual weight difference from a disabled state or a placeholder. Consider giving them more separation from the controls they label — they should feel like section headers, not inline decorations.

---

### 1.5 Stat Bar Analysis

The stat bar (Registered, Ballots, Turnout, Winner, Margin) lives in `.header-stats` at the right side of the header on desktop, and in a scrollable second row on mobile.

**Desktop state (from `desktop-cd9-winner.png`):**
- Values shown: `425,963` / `117,404` / `27.6%` / `Daniel Bliss` / `3.5pp`
- Font size: 13px value, 10px label
- Right-aligned column layout — values align to right edge

**Problems:**
1. **These are the most important data on the page.** When a race is loaded, the stat bar answers "who won, by how much" at a glance. Yet they sit at 13px in the top-right corner, competing with the header title. They should be the dominant type on the page after the map itself.
2. **Label sizes (10px uppercase) are genuinely difficult to read.** "REGISTERED" in 10px caps with letter-spacing needs ~14in viewing distance to parse. 
3. **The Winner stat mixes concepts** — it shows `Daniel Bliss` (name) and `29.4%` (vote share) in a single `stat-val` that can overflow with `text-overflow: ellipsis`. On mobile at `max-width: 120px`, "Daniel Bliss 29.4%" will always truncate.
4. **Mobile stat bar is scrollable.** A horizontally scrollable stat bar where only 2-3 stats are visible at once defeats the purpose of a stat bar (overview at a glance).
5. **No visual distinction between data types** — a vote count (`117,404`) and a percentage (`27.6%`) and a name (`Daniel Bliss`) all look identical. Color, size, or weight coding would help differentiation.

---

## 2. Responsive Layout Analysis

### 2.1 Desktop Layout (1600×900)

From the audit brief and screenshots:
- Header: 50px
- Toolbar: 275px
- Map: 575px (64% of viewport height)
- Footer: ~24px

**The toolbar uses 30%+ of vertical viewport.** This is the primary spatial problem. The toolbar is designed as a vertical strip on mobile but a horizontal strip on desktop — yet it still behaves like a mobile vertical list because of `flex-wrap: wrap`. 27 controls wrapping in a flex container will always produce multi-line layouts.

**There is no sidebar layout.** This is a missed opportunity. At 1600px width, there is ~1,200px of horizontal real estate that goes unused for controls. The toolbar could be a fixed-width left sidebar (280px) and the map could be full-height minus the header. This would recover the 275px of vertical toolbar height and give the map ~826px instead of ~575px — a **44% increase in map viewport** at no cost to controls.

### 2.2 Mobile Layout (390×844)

**Header state (toolbar closed):** Header is 77px (two-row layout: title row + stat row). This is reasonable.

**Toolbar open state (from `mobile-cd9-toolbar-open.png`):** The expanded toolbar is ~367px tall, leaving only ~400px for the map. Critically, the audit brief notes that "mode buttons [are] unreachable — header intercepts." This is a z-index/positioning bug compounding the layout issue: the toolbar expands downward and overlaps the map, but something in the header z-index chain is intercepting taps on the lower toolbar buttons.

**Specific mobile layout measurements (from screenshot analysis):**
- Header row 1 (logo + title + filter button): ~44px
- Header row 2 (stat bar): ~33px  
- Total header: ~77px
- Toolbar when open: ~367px
- Map area when toolbar open: ~400px = 47% of 844px viewport
- Map area when toolbar closed: ~767px = 91% of viewport

**Touch target audit:**
- `.filter-toggle` padding: `6px 8px` with 18×18px SVG = ~30×30px total — **fails 44px minimum** ✗
- `.mode-btn` mobile padding: `8px 4px` — height ~34px if font is 11px — **borderline fail** ✗ (especially "Vs" button which has minimal text)
- `.toolbar select` mobile padding: `8px 28px 8px 10px` — height ~38px — marginal ✗
- `.layer-btn` mobile: `padding: 8px 4px` — ~34px — **fails** ✗
- Zoom controls: `30×30px` — **fails** ✗

**No control meets the 44px iOS HIG / WCAG 2.5.5 minimum touch target.** Mobile selects come closest at ~38–40px but still fall short.

### 2.3 Breakpoint Strategy

**Current breakpoints:**
- `≤768px` — mobile
- `769px–1024px` — tablet  
- `>1024px` — desktop (no explicit breakpoint, just the default)

**Gaps:**
1. **No breakpoint at 1280px+** where a sidebar layout becomes viable
2. **768px breakpoint** is dated — iPhones in landscape mode are 844px+ wide, meaning they get the desktop layout (single-row toolbar) on a screen that can't really accommodate it
3. **No 375px breakpoint** for the smallest current iPhones where the stat bar is most likely to overflow
4. **Tablet (768–1024px)** only adjusts font sizes — it doesn't change the layout architecture. At 900px wide, the toolbar still wraps across multiple lines but with smaller text, which is worse than the desktop experience.

**Recommended breakpoints:**
- `≤480px` — small phone
- `481px–768px` — large phone / small tablet  
- `769px–1024px` — tablet (keep)
- `1025px–1279px` — laptop (new: narrow sidebar or horizontal toolbar)
- `≥1280px` — desktop (new: full sidebar layout)

---

## 3. Visual Hierarchy Problems

### 3.1 What draws the eye first

**On desktop (`desktop-landing.png`):** The eye goes to:
1. The "Select a Race" overlay text (centered, 20px — largest text on screen)
2. The "Election Results" active button (filled blue, stands out in toolbar)
3. The legend (bottom-left — contrast between colored swatches and dark bg)

**The toolbar draws more attention than the map on desktop.** The toolbar's vertical extent and the active blue button pull the eye left/up, away from the map canvas. On a data visualization tool, the map should be the hero element.

**On mobile (`mobile-cd9-current.png`):** The eye goes to:
1. The orange/red precinct clusters (strong chromatic contrast)
2. The stat numbers (the "Daniel Bliss" and "3.5pp" values stand out despite small size because they're on the cleaner header bg)
3. The legend chip (bottom-left, high-contrast colored bg)

**Mobile is actually better** for visual hierarchy than desktop — the toolbar is collapsed, the map dominates, and the stat bar anchors data context at top. The problem is interaction (the toolbar open state), not resting hierarchy.

### 3.2 Label vs. Value Competition

In the stat bar, **labels and values fight for attention.** Both are all-caps, same color family, similar weight. The correct pattern (borrowed from Bloomberg Terminal, Vercel analytics, Linear metrics) is:

- **Value:** Large, white/full-brightness, bold or semibold — dominant
- **Label:** Small, muted grey, uppercase with tracking — recessive

Current implementation comes close but breaks down at small sizes — the 10px uppercase label approaches the optical weight of the 13px value.

In the toolbar section headers (`.toolbar-label`), the same inversion occurs. The labels `DATA LAYER`, `ELECTION`, `DISTRICT`, `VIEW`, `FOCUS` appear to have similar visual weight to the control labels. A user scanning for the "View" section must read, not scan.

### 3.3 Legend vs. Map Content

The legend sits in the bottom-left of the map canvas with `position: absolute`. On desktop, this works because the map is large and the legend is compact. However:

- On the "Winner by Precinct" view with 15+ candidates, the legend grows to fill the bottom-left quadrant of the map, obscuring actual precinct data
- The legend uses `10px` text and `14×10px` swatches — the swatches are smaller than a standard radio button. At this size, distinguishing between similar colors (two shades of blue, two shades of pink in the CD-9 view) is nearly impossible
- The legend has no interaction affordance on desktop (it's `pointer-events: none`) — users can't click a candidate to highlight their precincts

**In `desktop-cd9-winner.png`:** The legend obscures the Cook County/Chicago border area in the bottom-left. This is exactly where "No data" precincts appear and where suburban Chicago precincts cluster — directly competing with legend content.

### 3.4 Primary vs. Secondary Controls

The current toolbar has no visual differentiation between:
- **Tier 1 (context-setting):** Data layer, election, district type, race — these define what you're looking at
- **Tier 2 (view mode):** Turnout/Winner/Margin/etc. — these change how you see it
- **Tier 3 (utility):** Focus/filter, export — secondary actions

All 27 controls use the same visual weight. The result: a user opening the tool for the first time must read all controls to understand what controls what. Compare Linear's command palette or Figma's toolbar — both use size, grouping, and weight to make hierarchy self-evident.

---

## 4. Design System Proposal

### 4.1 Token Set

```css
:root {
  /* ── Spatial Foundation ── */
  --bg:            #0c0e14;   /* Deepened from #0f1117 — richer, less grey */
  --surface:       #13161f;   /* Header/toolbar chrome */
  --surface-raised: #1a1d27; /* Cards, panels, dropdowns */
  --surface-ctrl:  #1f2335;   /* Interactive control fills — distinct from surface */
  --surface-hover: #252940;   /* Hover state on controls */
  --surface-active: #2a2e3d; /* Pressed/active fill */

  /* ── Borders ── */
  --border:        #252836;   /* Default border */
  --border-strong: #343850;   /* Focus rings, active borders */
  --border-subtle: #1a1d27;   /* Dividers, hairlines */

  /* ── Text Scale ── */
  --text:          #eceef2;   /* Slightly warmer than #e8eaed */
  --text-muted:    #8b919c;   /* Secondary text — min 12px usage */
  --text-dim:      #525868;   /* Tertiary — 18px+ ONLY or decorative */
  --text-disabled: #3d4152;   /* Disabled states */

  /* ── Accent (single accent — no more two blues) ── */
  --accent:        #4AADCA;   /* Electric blue-cyan — primary interactive */
  --accent-dim:    #2A6E84;   /* Subdued accent for borders, active fills */
  --accent-bg:     rgba(74, 173, 202, 0.10); /* Active background tint */
  --accent-bg-strong: rgba(74, 173, 202, 0.18); /* Hover on active */

  /* ── Semantic ── */
  --success:       #5FB568;   /* Positive margins, high turnout */
  --warning:       #E09A3F;   /* Data quality alerts */
  --error:         #C95F6F;   /* Load failures */
  --dem:           #4A90D9;   /* Democrat candidate color */
  --rep:           #D95F5F;   /* Republican candidate color */

  /* ── Election Colors (winner highlighting) ── */
  --highlight:     #F2C94C;   /* Winner/leader highlight — warmer than #fdd835 */

  /* ── Type Scale ── */
  --text-xs:    11px;  /* Section labels ONLY (uppercase + tracking) */
  --text-sm:    12px;  /* Captions, legend labels, info-panel secondary */
  --text-base:  13px;  /* Body, control labels, mode buttons */
  --text-md:    14px;  /* Toolbar selects, info panel headers */
  --text-lg:    16px;  /* Stat bar values (secondary stats) */
  --text-xl:    20px;  /* Stat bar hero value (winner name, turnout) */
  --text-2xl:   24px;  /* Landing overlay headline */

  /* ── Spacing Scale ── */
  --sp-1:   4px;
  --sp-2:   8px;
  --sp-3:  12px;
  --sp-4:  16px;
  --sp-5:  20px;
  --sp-6:  24px;
  --sp-8:  32px;
  --sp-10: 40px;

  /* ── Radii ── */
  --r-sm:  4px;   /* Buttons, badges */
  --r-md:  6px;   /* Controls, cards */
  --r-lg:  8px;   /* Panels, modals */
  --r-xl: 12px;   /* Bottom sheets */
  --r-full: 9999px; /* Pills */

  /* ── Shadows ── */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);

  /* ── Motion ── */
  --duration-fast:   100ms;
  --duration-base:   150ms;
  --duration-slow:   250ms;
  --duration-sheet:  300ms;
  --easing-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-decel:    cubic-bezier(0.0, 0.0, 0.2, 1);

  /* ── Touch Targets ── */
  --touch-min: 44px;  /* iOS HIG / WCAG 2.5.5 */
  --touch-sm:  36px;  /* Desktop minimum (mouse-first contexts) */
}
```

### 4.2 Button Hierarchy

**Three levels, clearly differentiated:**

```css
/* ── PRIMARY: Single most important action per context ── */
/* Use for: Data layer active state */
.btn-primary {
  background: var(--accent);
  color: #0c0e14;              /* Dark text on light accent — higher contrast than white */
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  padding: 0 var(--sp-3);
  height: var(--touch-sm);     /* 36px desktop */
  font-size: var(--text-base);
  font-weight: 600;
  letter-spacing: -0.01em;
  transition: background var(--duration-base) var(--easing-standard),
              transform var(--duration-fast);
}
.btn-primary:hover {
  background: #5DC5E0;         /* 10% lighter */
}
.btn-primary:active {
  transform: scale(0.98);
}

/* ── SECONDARY: Active mode buttons, selected states ── */
/* Use for: mode-btn.active, layer-btn.active (when primary isn't appropriate) */
.btn-secondary {
  background: var(--accent-bg);
  color: var(--accent);
  border: 1px solid var(--accent-dim);
  border-radius: var(--r-sm);
  padding: 0 var(--sp-2);
  height: var(--touch-sm);
  font-size: var(--text-base);
  font-weight: 600;
  transition: background var(--duration-base), border-color var(--duration-base);
}
.btn-secondary:hover {
  background: var(--accent-bg-strong);
}

/* ── GHOST: Default (inactive) mode buttons, export ── */
/* Use for: mode-btn (inactive), export-btn, utility actions */
.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  padding: 0 var(--sp-2);
  height: var(--touch-sm);
  font-size: var(--text-base);
  font-weight: 400;
  transition: background var(--duration-base), color var(--duration-base),
              border-color var(--duration-base);
}
.btn-ghost:hover {
  background: var(--surface-hover);
  color: var(--text);
  border-color: var(--border);
}

/* ── ICON-ONLY: filter-toggle, zoom controls ── */
.btn-icon {
  background: var(--surface-ctrl);
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  width: var(--touch-sm);
  height: var(--touch-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--duration-base), color var(--duration-base);
}
.btn-icon:hover {
  background: var(--surface-hover);
  color: var(--text);
}
/* Mobile override — full 44px touch target */
@media (max-width: 768px) {
  .btn-icon {
    width: var(--touch-min);
    height: var(--touch-min);
  }
}
```

### 4.3 Form Controls

```css
/* ── SELECT ── */
.ctrl-select {
  background: var(--surface-ctrl);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 0 28px 0 var(--sp-2);   /* Right padding for custom chevron */
  height: var(--touch-sm);          /* 36px desktop */
  font-size: var(--text-base);      /* 13px — legible */
  font-family: inherit;
  cursor: pointer;
  outline: none;
  appearance: none;
  /* Custom chevron */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%238b919c' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  min-width: 120px;
  transition: border-color var(--duration-base);
}
.ctrl-select:hover { border-color: var(--accent-dim); }
.ctrl-select:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-bg); }

/* Mobile override */
@media (max-width: 768px) {
  .ctrl-select {
    height: var(--touch-min);   /* 44px */
    font-size: 15px;            /* Larger on mobile — prevents iOS zoom */
    padding: 0 32px 0 12px;
    width: 100%;
    min-width: unset;
  }
}

/* ── SEGMENTED TOGGLE (replaces layer-toggle) ── */
/* Replaces the current two-button layer toggle with a proper pill-segmented control */
.ctrl-segmented {
  display: flex;
  background: var(--surface-ctrl);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  overflow: hidden;
  height: var(--touch-sm);
}
.ctrl-segmented-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: var(--text-base);
  font-family: inherit;
  font-weight: 500;
  padding: 0 var(--sp-3);
  cursor: pointer;
  transition: background var(--duration-base), color var(--duration-base);
  border-right: 1px solid var(--border);
  white-space: nowrap;
}
.ctrl-segmented-btn:last-child { border-right: none; }
.ctrl-segmented-btn:hover { background: var(--surface-hover); color: var(--text); }
.ctrl-segmented-btn.active {
  background: var(--accent);
  color: #0c0e14;
  font-weight: 600;
}

/* Mobile override */
@media (max-width: 768px) {
  .ctrl-segmented { height: var(--touch-min); }
  .ctrl-segmented-btn { font-size: 14px; }
}
```

### 4.4 Mobile-Specific Tokens

```css
/* Applied via media query — mobile-first override layer */
@media (max-width: 768px) {
  :root {
    --text-xs:    12px;   /* Bump section labels on mobile */
    --text-sm:    13px;
    --text-base:  15px;   /* iOS prevents zoom at 16px — use 15px as safe floor */
    --text-md:    16px;
    --text-lg:    18px;   /* Stat secondary values */
    --text-xl:    22px;   /* Stat hero value */
    
    --touch-sm:   44px;   /* All controls use full 44px on mobile */
    
    --sp-1:   4px;
    --sp-2:  10px;   /* Slightly more generous mobile spacing */
    --sp-3:  14px;
    --sp-4:  16px;
  }
}
```

---

## 5. Specific UI Recommendations

### 5.1 Desktop Layout: Sidebar Architecture

**Problem:** The current horizontal toolbar is consuming 275px of vertical viewport. The solution is a **fixed-width sidebar** that runs the full height of the viewport beside the map.

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (50px — logo, title only; stat bar moves into sidebar│
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   SIDEBAR    │                MAP                           │
│   260px      │                full height                   │
│   fixed      │                (100% minus header 50px)     │
│              │                                              │
│   overflow-y │   Legend: bottom-left of map canvas          │
│   auto       │   Info panel: bottom-right of map canvas     │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

**Exact dimensions:**
- Header: `height: 48px` (reduced from 50px — tighten the logo/title area)
- Sidebar: `width: 260px; flex-shrink: 0; height: calc(100dvh - 48px); overflow-y: auto`
- Map: `flex: 1; height: calc(100dvh - 48px)`
- Stat bar: Move from header into sidebar top — treat as a **KPI card block** at top of sidebar

**Sidebar layout (top to bottom):**
1. **KPI block** — Stat bar redesigned as KPI cards (see Section 5.4) — 90–100px
2. **Divider**
3. **Section: Data Layer** — segmented control — 60px
4. **Section: Election** — label + select — 64px
5. **Section: District** — label + type select + race select — 96px
6. **Section: View** — label + 8 mode buttons (2×4 grid) — 96px
7. **Section: Focus** — label + select — 64px
8. **Divider**
9. **Export button** — full-width — 44px
10. Sidebar total: ~494px if content doesn't scroll. For longer configurations (finance mode), it scrolls.

**Sidebar CSS sketch:**
```css
@media (min-width: 1025px) {
  .main-layout {
    display: flex;
    flex-direction: row;
    height: calc(100dvh - 48px);
  }
  .sidebar {
    width: 260px;
    flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
    padding: var(--sp-4);
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
  }
  .map-wrap {
    flex: 1;
    height: 100%;
  }
  /* Hide legacy toolbar when sidebar is active */
  .toolbar { display: none; }
}
```

### 5.2 Mobile Layout

**Proposed architecture:**

```
┌─────────────────────────────┐
│  HEADER (48px)              │
│  Logo · Title · Filter btn  │
├─────────────────────────────┤
│  STAT BAR (44px)            │
│  Scrollable horizontal strip│
├─────────────────────────────┤
│                             │
│  MAP (full remaining)       │
│  (~752px on 844px device)   │
│                             │
│  [Legend: bottom-left chip] │
└─────────────────────────────┘
↕  (BOTTOM SHEET — slides up when filter-toggle tapped)
┌─────────────────────────────┐  ← 70% of viewport max = ~591px
│  ▬ (drag handle)            │
│  Controls                   │
│  (scrollable)               │
└─────────────────────────────┘
```

**Key changes from current:**
1. **Stat bar becomes its own fixed strip**, not part of the header. This prevents the header from becoming 77px tall and gives the stat bar a dedicated, non-scrollable home.
2. **Filter toggle button: full 44×44px** with visible label "Filters" on ≥375px screens
3. **Bottom sheet replaces the expanding toolbar** — bottom sheet is the correct mobile pattern for contextual controls. The current implementation already has `.bottom-sheet` but it's only used for the info panel (precinct detail), not for controls. Use it for controls too.
4. **Remove zoom controls from map** on mobile (too small, native pinch-zoom suffices). This frees the left side of map canvas from the 30px Leaflet buttons.

**Exact mobile measurements:**
```
Header:    height: 48px; padding: 0 16px;
Stat bar:  height: 44px; overflow-x: auto; padding: 0 16px;
Map:       height: calc(100dvh - 92px);  /* 48px header + 44px stats */
Bottom sheet: max-height: 72dvh; (≤600px); border-radius: 16px 16px 0 0;
```

**Header on mobile:**
```css
@media (max-width: 768px) {
  .header {
    height: 48px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;       /* NEVER wrap — causes height increase */
  }
  .stat-bar {
    /* Separate component — not inside header */
    height: 44px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: var(--sp-4);
    padding: 0 var(--sp-4);
    overflow-x: auto;
    scrollbar-width: none;
    flex-shrink: 0;
  }
  .filter-toggle {
    width: 44px;
    height: 44px;
    /* Or with label on wider phones: */
    min-width: 44px;
    padding: 0 var(--sp-2);
    gap: var(--sp-1);
  }
}
```

### 5.3 Legend Redesign

**Desktop legend (current: position:absolute, bottom-left, 10px text):**

**Problems:**
- Overlaps map content in multi-candidate races (15+ legend items)
- `pointer-events: none` means no interactivity
- 10px text for candidate names in a multi-candidate race is too small

**Proposed desktop legend:**
Move the legend into the **sidebar** (for the sidebar layout) or keep it floating but with these improvements:

```css
/* Compact chip legend — desktop */
.legend {
  position: absolute;
  bottom: var(--sp-4);
  left: var(--sp-4);
  z-index: 800;
  background: rgba(19, 22, 31, 0.92);   /* --surface with opacity */
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border-strong);
  border-radius: var(--r-lg);
  padding: var(--sp-2) var(--sp-3);
  max-width: 200px;
  max-height: 280px;           /* Prevents legend from dominating */
  overflow-y: auto;
  scrollbar-width: thin;
  pointer-events: auto;        /* Enable hover interactions */
  box-shadow: var(--shadow-md);
}
.legend-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: .07em;
  margin-bottom: var(--sp-2);
}
.legend-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 12px;             /* Up from 10px */
  color: var(--text-muted);
  padding: 3px 0;
  cursor: pointer;             /* Enable click-to-highlight */
  border-radius: var(--r-sm);
  transition: color var(--duration-base), background var(--duration-fast);
}
.legend-row:hover {
  color: var(--text);
  background: var(--surface-hover);
  padding-left: var(--sp-1);
}
.legend-swatch {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}
```

**Mobile legend — tap-to-toggle chip (keep existing behavior, improve styling):**

```css
@media (max-width: 768px) {
  .legend {
    bottom: var(--sp-3);
    left: var(--sp-3);
    padding: var(--sp-2) var(--sp-3);
    max-width: 140px;
    cursor: pointer;
  }
  /* Collapsed: show only title + chevron */
  .legend-body {
    overflow: hidden;
    max-height: 0;
    transition: max-height var(--duration-slow) var(--easing-decel);
    margin-top: 0;
  }
  .legend.legend-open .legend-body {
    max-height: 260px;   /* Enough for ~15 candidates */
    margin-top: var(--sp-1);
  }
  /* Legend toggle indicator */
  .legend-title::after {
    content: '';
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid var(--text-dim);
    margin-left: var(--sp-1);
    vertical-align: middle;
    transition: transform var(--duration-base);
  }
  .legend.legend-open .legend-title::after {
    transform: rotate(180deg);
  }
  /* Row density on mobile — tighter */
  .legend-row { font-size: 11px; padding: 2px 0; }
}
```

### 5.4 Stat Bar Redesign

**Current:** Flat right-aligned columns in header with 13px values and 10px labels.

**Proposed: Elevated KPI card strip** (inspired by Vercel analytics and Linear metrics header)

On **desktop** (sidebar layout): KPI block at top of sidebar.

```css
/* Desktop: sidebar KPI block */
.kpi-block {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-2);
  padding: var(--sp-3);
  background: var(--surface-raised);
  border-radius: var(--r-lg);
  border: 1px solid var(--border);
}
.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.kpi-value {
  font-size: var(--text-lg);    /* 16px */
  font-weight: 600;
  color: var(--text);
  font-variant-numeric: tabular-nums lining-nums;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.kpi-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: .06em;
}
/* Winner card: full-width, larger value */
.kpi-card.kpi-winner {
  grid-column: 1 / -1;
  flex-direction: row;
  justify-content: space-between;
  align-items: baseline;
  padding-top: var(--sp-2);
  border-top: 1px solid var(--border);
  margin-top: var(--sp-1);
}
.kpi-winner .kpi-value {
  font-size: var(--text-xl);   /* 20px — the headline number */
  color: var(--highlight);
}
.kpi-winner .kpi-pct {
  font-size: var(--text-lg);
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
```

On **mobile** (horizontal scroll strip):

```css
@media (max-width: 768px) {
  .stat-bar {
    /* Defined in Section 5.2 */
  }
  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 1px;
    flex-shrink: 0;
    padding-right: var(--sp-4);
    border-right: 1px solid var(--border);
    margin-right: 0;
  }
  .stat-item:last-child { border-right: none; }
  .stat-val {
    font-size: 15px;            /* Up from 12px — legible */
    font-weight: 600;
    color: var(--text);
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    letter-spacing: -0.01em;
  }
  .stat-val.stat-winner {
    color: var(--highlight);
    font-size: 14px;            /* Slightly smaller since it's a name */
  }
  .stat-label {
    font-size: 10px;            /* 10px is acceptable for uppercase label under visible value */
    font-weight: 700;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: .05em;
  }
  /* Split Winner: name and pct on separate lines, both readable */
  .stat-winner-wrap {
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .stat-winner-pct {
    font-size: 11px;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }
}
```

### 5.5 Export Button Placement and Styling

**Current:** Inline in the toolbar, ghost style with icon. On mobile: full-width bottom of expanded toolbar.

**Problems:**
1. Export is an **action**, not a filter. It should be visually separated from all the filter controls.
2. On mobile, "Export PNG" gets the same full-width treatment as `All Precincts` (Focus dropdown) — these are categorically different actions.

**Proposed placement:**

*Desktop sidebar:* Pin to the bottom of the sidebar (sticky bottom), separated from filter controls by a divider line.

```css
.sidebar-footer {
  margin-top: auto;          /* Push to bottom */
  padding-top: var(--sp-4);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.export-btn-new {
  width: 100%;
  height: 36px;
  background: var(--surface-ctrl);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-2);
  font-size: var(--text-base);
  font-family: inherit;
  cursor: pointer;
  transition: border-color var(--duration-base), color var(--duration-base),
              background var(--duration-base);
}
.export-btn-new:hover {
  border-color: var(--accent-dim);
  color: var(--accent);
  background: var(--accent-bg);
}
```

*Mobile:* Export button lives in the **top-right of the header** as an icon-only button (download icon) — always visible without opening the controls panel. Tapping it exports immediately from whatever state the map is in.

```css
@media (max-width: 768px) {
  .header-export {
    /* Placed between title and filter toggle in header */
    width: 44px;
    height: 44px;
    background: transparent;
    border: none;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--r-md);
    transition: color var(--duration-base), background var(--duration-base);
  }
  .header-export:hover {
    background: var(--surface-hover);
    color: var(--text);
  }
}
```

---

## 6. Toolbar Information Architecture Redesign

The most impactful single change is reorganizing the 27 controls into a **three-tier hierarchy** with clear visual separators. This is the fix that most directly addresses the mobile interaction bug and the desktop space problem.

### Current Flat List:
```
[Data Layer] [Election] [District Type] [Race] [View: 8 buttons] [Focus] [Export]
```

### Proposed Grouped Architecture:

```
GROUP 1: CONTEXT (what data are you looking at?)
  ├── Data Layer toggle (Election / Finance)
  ├── Election cycle
  ├── District type
  └── Race

GROUP 2: VIEW (how do you visualize it?)
  └── Mode buttons (Turnout / Winner / Margin / etc.)
      + conditional view-specific controls (Candidate select, Vs checkboxes)

GROUP 3: FILTER (narrow the geography)
  └── Focus / Municipality

GROUP 4: ACTIONS
  └── Export PNG
```

**Visual separators between groups:** Not just `toolbar-sep` (1px hairline, invisible), but a **section header chip** with a subtle background:

```css
.toolbar-section {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}
.toolbar-section-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: .08em;
  padding-bottom: var(--sp-1);
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--sp-1);
}
```

In the **sidebar layout** (desktop ≥1025px), each group becomes a visually distinct section with `padding: 16px` and a 1px border-bottom separator.

On **mobile bottom sheet**, each group is a collapsible accordion panel — only the "View" group is open by default (most frequently changed control), Context group is open if no race is selected.

---

## 7. Specific Contrast & Accessibility Fixes

| Current | Fix |
|---|---|
| `.stat-label` at 8px on mobile | Raise to 10px minimum; ensure `--text-muted` not `--text-dim` |
| `.toolbar-label` at 10px | Acceptable only at uppercase + tracking; ensure min `--text-muted` color |
| `--text-dim` (`#6b7280`) at small sizes | Restrict to ≥18px only; replace with `--text-muted` at small sizes |
| `cand-votes` at 10px | Raise to 11px minimum |
| `.mode-btn` at 11px on desktop | Raise to 13px (current desktop target is `var(--text-base)`) |
| Zoom control buttons at 30×30px | 36px on desktop minimum; or hide on mobile |
| `filter-toggle` at ~30×30px | 44×44px on mobile — non-negotiable |
| Focus outline: `outline: none` on selects | Restore `:focus-visible` with custom ring: `box-shadow: 0 0 0 2px var(--accent-bg)` |
| `layer-btn.active` white text on `#2196f3` | Contrast is ~3.4:1 — marginal pass for large text but border-line. Using dark text on `--accent` is safer. |

---

## 8. Reference Design Patterns

These interfaces solve similar density/data problems and are worth studying directly:

| Reference | Pattern to Borrow |
|---|---|
| **Vercel Analytics** | KPI card layout for stat bar; clean sidebar hierarchy |
| **Linear** | Section headers with uppercase labels; ghost→secondary→primary button progression |
| **Figma** | Icon+label toolbar patterns; floating panel with `backdrop-filter: blur` |
| **Bloomberg Terminal** | Density at legibility; tabular numbers; status bar context |
| **Mapbox Studio** | Layer panel sidebar; legend with interactive row hover |
| **Flourish** | Clean export UI; chart + controls separation |

---

## 9. Implementation Priority Order

### P0 — Fix broken mobile (immediate, 1–2 days)
1. Fix the z-index interception on mode buttons — ensure `.toolbar` z-index < `.header` z-index, and the toolbar expands below not over any fixed header content
2. Increase all mobile touch targets to 44px minimum (filter-toggle, mode-btn, layer-btn, selects)
3. Separate stat bar from header into its own `<div class="stat-bar">` at 44px height
4. Fix `--text-dim` usage at `stat-label` 8px — change to `--text-muted` and min 10px

### P1 — Visual system consistency (1–3 days)
5. Replace dual-blue with single accent `--accent: #4AADCA`
6. Unify mode-btn.active and layer-btn.active to same secondary button treatment
7. Raise all text floors to 12px minimum
8. Increase `stat-val` to 15px mobile / 16px desktop
9. Increase `mode-btn` text to 13px desktop / 15px mobile

### P2 — Layout architecture (3–5 days)
10. Implement sidebar layout at ≥1025px breakpoint
11. Move stat bar into sidebar KPI block on desktop
12. Move export button to sidebar footer on desktop, header icon on mobile
13. Add `backdrop-filter: blur(8px)` to legend and info-panel for depth

### P3 — Polish and hierarchy (2–3 days)
14. Implement toolbar section grouping (Context / View / Filter / Actions)
15. Redesign legend with larger swatches (10×10px) and 12px text
16. Add `pointer-events: auto` + hover interactions to legend rows
17. Add `:focus-visible` rings across all interactive elements

---

*End of audit. Total estimated implementation effort for all P0–P3 changes: 7–13 developer-days depending on refactor scope.*
