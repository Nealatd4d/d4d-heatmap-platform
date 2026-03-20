# D4D Election Heatmap Platform — UX Audit

**Auditor:** Senior UX Designer (Perplexity Computer)  
**Date:** March 20, 2026  
**Scope:** Mobile-first UX audit covering information architecture, interaction patterns, and proposed redesign

---

## Executive Summary

The platform has a solid data model and strong visual identity, but its UI architecture was built for desktop-first feature accumulation — not for the mobile-first sharing use case that drives most real-world usage. The core problem is not any single control but the **flat hierarchy**: 27 controls at equal visual weight, all rendered simultaneously, with no concept of primary vs. secondary vs. contextual tasks.

The result is that a mobile user opening a shared link must navigate through a 44%-viewport toolbar before they can even see the map they were sent to look at. On desktop, 31% of a 1600px viewport is consumed by controls — 90% of which are irrelevant for any given session.

The fix is not cosmetic. It requires a structural rethink: **progressive disclosure, context-sensitive surfacing, and a sidebar layout on desktop.**

---

## 1. User Flow Analysis

### Current User Journey: Landing to "Viewing a Specific Race Heatmap"

#### Desktop (1600×900)

```
Step 1: Page loads
        → Header (50px) + Toolbar (275px) visible
        → Map shows "Select a Race" empty-state overlay
        → Cognitive orientation: user sees 6+ controls, no clear starting point

Step 2: Select DATA LAYER
        → Already defaulted to "Election Results" ✓ (often skippable)
        → 1 click if switching to Finance

Step 3: Select ELECTION
        → Dropdown: must choose election cycle
        → Pre-populated with default (2026 Gubernatorial Primary) — often correct, but
          users who want 2024 data must interact here
        → 1 click

Step 4: Select DISTRICT TYPE
        → "Select Type…" — blank, no default
        → User must know vocabulary: "Congressional" vs. "State House" vs. "Alderman"
        → 1 click

Step 5: Select RACE
        → Dependent on Step 4; disabled until type chosen
        → Long list of races — no grouping or search
        → 1 click

Step 6: Select VIEW MODE
        → 8 buttons visible; "Turnout" is default active
        → For first-time users: no explanation of what "Margin", "Vs", "Swing" mean
        → 0–1 clicks (default acceptable for quick viewing)

Step 7: Map renders with data
        → SUCCESS

Desktop click count: 3–4 required clicks, up to 5–6 if switching from defaults
```

#### Mobile (390×844)

```
Step 1: Page loads (or shared link opens)
        → Header row 1: Logo + "D4D Heatmap" + Filter [≡] icon (≈44px)
        → Header row 2: Stats bar — 5 stats scrollable horizontally (≈33px)
        → Map: visible but empty-state overlay ("Select a Race")
        → No indication controls are hidden

Step 2: Tap filter icon [≡]
        → Toolbar expands DOWN (not a sheet — a max-height:500px
          CSS transition) — takes ≈0.3s
        → Toolbar now 367px tall = 44% of 844px viewport
        → MAP IS MOSTLY HIDDEN behind the toolbar
        → 1 tap

Step 3: Scroll inside toolbar to find controls
        → Controls stack vertically: Layer → Election → District Type
          → District Race → VIEW (2 rows of 4 buttons) → Focus → Export PNG
        → User must scroll to see all 8 view mode buttons (2nd row cut off)
        → Problem: The toolbar's overflow context is the page itself, so
          zooming/scrolling the map also fights with toolbar scroll

Step 4–6: Same selections as desktop, but:
        → Touch targets: mode buttons are 4-column grid at ~82px wide each
          (≈adequate) but the ACTIVE button state (blue border) is hard to
          distinguish at mobile scale
        → "Turnout Δ" button label wraps to 2 lines — confusing
        → Playwright confirmed header/stat-bar intercepts clicks on mode buttons
          in row 2 — users can't tap "Vs", "Turnout Δ", "Swing", "Votes"
          because z-index: 1000 header sits over the expanded toolbar area

Step 7: Close toolbar
        → User must tap [≡] again (or does it auto-close? unclear)
        → Now only ≈430px of map visible above the still-visible stats bar

Mobile tap count: 5–8 taps, with at least 2 buttons physically unreachable
```

### Where Users Get Stuck

| Friction Point | Device | Severity |
|---|---|---|
| Unreachable mode buttons (header intercepts touch events) | Mobile | **Critical** — functionality broken |
| Toolbar covers 44% of map while open | Mobile | **High** — user can't see map to understand context |
| No default race selected; empty map on load | Both | **High** — zero data value until 3–4 interactions |
| 8 view mode buttons with no descriptions | Both | **Medium** — vocabulary unfamiliar to non-analysts |
| "Select Type…" and "Select Race…" both blank | Both | **Medium** — forced sequential interaction, no smart defaults |
| Legend with 15 candidates takes 60vh | Mobile | **Medium** — overwhelms bottom of screen when open |
| No way to share/bookmark current map state via URL | Both | **High** — core use case (sharing with others) has no direct path |
| Finance controls appear only after toggling layer | Both | **Low** — appropriate progressive disclosure already in place |

### Cognitive Load of 27 Controls

Miller's Law (7±2 items per chunk) has been violated at every layer.

- **Labels in current toolbar:** DATA LAYER, ELECTION, DISTRICT, VIEW, FOCUS — 5 section labels that are not scannable because they're rendered at the same visual weight as the controls
- **8 view mode buttons** in one group, with no visual clustering to indicate "comparative" (Vs, Swing) vs. "single-race" (Turnout, Winner, Margin) modes
- **27 controls visible simultaneously** (or only 1 tap away) means users face the entire decision tree at once

A user opening this on mobile to answer "who won my precinct?" must mentally parse 27 options to accomplish a 2-step task.

---

## 2. Information Architecture Critique

### Control Classification

#### Primary Controls (used every session — must be immediately accessible)

| Control | Why Primary |
|---|---|
| Election dropdown | Entry point — gates all other data |
| District Type dropdown | Entry point — must select before race |
| Race dropdown | Entry point — the core selection |
| View mode: Winner | Most common "what happened" view |
| View mode: Turnout | Second most common view |
| View mode: Margin | Third most common |

**Implication:** Only 6 of 27 controls are truly primary. These should be always-visible, high-contrast, and in logical sequence.

#### Secondary Controls (used occasionally — need quick access but not persistent display)

| Control | Why Secondary |
|---|---|
| Data Layer toggle (Election/Finance) | Most sessions use one layer only |
| View mode: Candidate | Useful for primaries, not generals |
| View mode: Vs | Comparative — requires extra config |
| View mode: Turnout Δ | Advanced: requires 2 elections to compare |
| View mode: Swing | Advanced: same |
| View mode: Votes | Raw data view — analyst-specific |
| Focus (municipality filter) | Used to filter geography; occasional |
| Export PNG | Per-session workflow ender |

#### Contextual Controls (only relevant in certain states — should be hidden by default)

| Control | Context Required |
|---|---|
| All Finance controls (5) | Only when Finance layer is active |
| Committee A/B dropdowns | Only in Finance > Vs or Comparison modes |
| Previous Election dropdown | Only in Turnout Δ or Swing modes |
| Candidate selector (view opts) | Only in Candidate mode |
| Vs checklist | Only in Vs mode |

**Current problem:** Contextual controls are either always hidden (Finance) or always shown with blank/disabled states (view opts). There's no intermediate state that says "this becomes available when you choose X."

### The Missing Context: What Mode Requires What

The current UI doesn't communicate dependencies:

- "Vs" mode needs a race selected AND 2 candidates chosen — but the candidate selectors only appear after you've already clicked Vs
- "Turnout Δ" needs a second election — but there's no second election dropdown in the main flow (it appears somewhere in Finance controls?)
- "Swing" similarly needs prior-election context

Users are expected to discover these dependencies through trial and error.

### Proposed Control Grouping

```
GROUP A — Race Selector (always visible, sequential)
  [Election] → [District Type] → [Race]

GROUP B — View Mode (always visible after race selected, segmented)
  Primary tier:  [Winner] [Turnout] [Margin]
  Secondary tier (expandable): [Candidate] [Vs] [Turnout Δ] [Swing] [Votes]

GROUP C — Comparative Config (contextual, appears only in Δ/Vs/Swing modes)
  [Compare To Election] or [Candidate A vs B]

GROUP D — Layer & Filter (secondary, collapsed)
  [Data Layer: Election | Finance]
  [Focus: All Precincts | Municipality filter]

GROUP E — Actions (always visible but low-prominence)
  [Export PNG] [Share Link]
```

---

## 3. Mobile Interaction Patterns

### Current Mobile Layout Issues

#### Issue 1: Toolbar-as-Overlay (Critical)
The current pattern expands the toolbar **downward** using `max-height` CSS transition. This pushes the map down rather than overlaying it — but the fixed header at `z-index: 1000` still physically sits above where the toolbar buttons render. The Playwright click-blocking confirms this: `header` at 77px tall is intercepting touch events on the mode button rows when the toolbar is expanded.

**Root cause:** The toolbar is in document flow (flex column), but the header is `position: fixed` or effectively so via `z-index: 1000`. When the toolbar expands, the mode buttons in row 2 of the 4-column grid land at vertical position ≈ 77px + 367px – (row height), which is obscured by the header.

**Correct fix:** Move mobile controls entirely out of document flow into a true bottom sheet or slide-up panel. The header should never intersect interactive controls.

#### Issue 2: No Visual Anchor for Current State
When the toolbar closes, there's no persistent indicator of what race/view is active except the header stats bar. A user who closes the filter panel and then wants to change just the View mode has to reopen the entire panel.

**Comparable pattern to reference:** iOS Weather app uses a persistent bottom summary card that shows current data without requiring the settings panel to be open. Google Maps shows the current "mode" chip (Driving/Transit/Walking) permanently without requiring the full panel.

#### Issue 3: Legend Positioning Conflict
The legend (bottom-left, `z-index: 800`) and the bottom sheet (`z-index: 1100`) can overlap. With 15 candidates, the legend at `max-height: 300px` when open takes most of the lower screen. This is already correctly flagged as needing tap-to-open behavior — but the open state needs a maximum height cap at ~40% of viewport, with internal scroll.

#### Issue 4: Stats Bar as Dead Weight
The horizontal-scrolling stats bar (Registered, Ballots, Turnout, Winner, Margin) is correct data but inaccessible on mobile due to scroll indicator suppression (`scrollbar-width: none`). Users don't know it scrolls. Consider showing the 2–3 most important stats (Winner + Margin) always-visible, with a tap-to-expand for the rest.

### Best Practices from Reference Apps

**Google Maps (mobile):**
- Primary interaction is the map itself — everything else is secondary UI
- Bottom sheet for place details: 3 snap points (peek/mid/full)
- Search bar permanently at top (≈56px), but recedes on map interaction
- Zero persistent controls obscure the map during browsing

**Zillow (mobile):**
- Map fills screen edge-to-edge
- Filter controls behind a "Filters" button that opens a full-screen modal
- Current filter state shown as chips/pills on the map view (e.g., "3+ beds · $400k–$600k")
- Map and list toggle as a persistent segmented control at top

**Weather.com / Dark Sky:**
- Current conditions shown as a persistent strip at top (temperature + condition)
- Detail in bottom-sheet that snaps to 3 heights
- No settings ever overlay the map/visualization

**Mapbox Datasets / Felt.com:**
- Left sidebar for layer controls on desktop
- On mobile: floating FAB (Floating Action Button) to open a bottom drawer
- Layer visibility controlled by simple toggles, not mode buttons

### Proposed Mobile Interaction Model

**Recommended: Sticky Header + Bottom Control Strip + Bottom Sheet**

```
┌─────────────────────────────────────┐
│ [D4D]  CD-9 · 2026 Primary  [≡]    │  ← 44px: branding + current context + settings icon
│ Winner · Daniel Bliss · 3.5pp ▸    │  ← 32px: current-state strip (tappable → stats sheet)
├─────────────────────────────────────┤
│                                     │
│                                     │
│           MAP (full bleed)          │
│                                     │
│  [+]                    [Legend ▾] │  ← Leaflet zoom (left), legend pill (bottom-right)
│  [-]                               │
│                                     │
├─────────────────────────────────────┤
│ [Winner] [Turnout] [Margin] [···]  │  ← 48px: primary view mode strip (4-col, always visible)
└─────────────────────────────────────┘
```

- The **bottom strip** shows the 3 primary view modes + a "···" more button
- Tapping "···" opens a **bottom sheet** (half-height, swipeable) with full controls:
  - Section: Race → Election / Type / Race
  - Section: View → all 8 modes with brief descriptions
  - Section: Filter → Focus municipality
  - Section: Data Layer → Election Results / Campaign Finance
  - Section: Export
- The **top context strip** ("Winner · Daniel Bliss · 3.5pp") replaces the scrolling stats bar; tapping it opens a stats bottom sheet
- **Legend:** tap `[Legend ▾]` pill to toggle — starts closed. Open state max-height 40vh, scrollable

This eliminates the header intercept bug entirely (controls never in document flow behind the header) and keeps the map visible at all times.

### Legend on Mobile: Tap-to-Open Model

Current implementation is close but has gaps:

```css
/* Current — correct structure */
.legend { pointer-events: auto; cursor: pointer; }
.legend-body { max-height: 0; transition: max-height 0.25s ease; }
.legend.legend-open .legend-body { max-height: 300px; }
```

**Issues:**
1. `max-height: 300px` is not capped relative to viewport — on mobile this could cover most of the lower map
2. The `▾` / `▴` indicator is a CSS `::after` pseudo-element — fine, but not accessible (no `aria-expanded`)
3. Legend is `position: absolute` inside `.map-wrap` — correct, but z-index 800 means it can be obscured by the bottom sheet at 1100

**Recommended changes:**
- Cap at `max-height: min(300px, 40vh)`
- Add `aria-expanded` toggle in JS
- Render legend as a **pill button** (not an always-visible block): `[▪▪ Legend ▾]` — 28px tall, bottom-right, only body expands
- On open: legend expands upward from the pill, with internal scroll for >6 items

---

## 4. Desktop Layout Proposal

### Current State Analysis

At 1600×900:
- Header: 50px (5.6% of viewport height)
- Toolbar: 275px (30.6%) — **this is the problem**
- Map: 575px (63.9%)
- Footer: ~30px (hidden in screenshots, exists in CSS)

The toolbar wraps into multiple rows because all controls are in a single flex row with `flex-wrap: wrap`. With the Finance layer active, this could be 5+ rows.

The map gets only **64% of the viewport** on a large monitor. On a 13" laptop at 1280×800, the numbers are worse.

Critically, the horizontal space (1600px wide) is almost entirely wasted by the toolbar — it could display all controls in a single narrow column while giving the map 85%+ of screen real estate.

### Proposed Desktop Layout: Left Sidebar

**Recommendation: Collapsible left sidebar, 240px default / 48px collapsed (icon rail)**

```
┌──────────┬──────────────────────────────────────────┐
│ D4D      │                                          │
│ Heatmap  │                                          │
│          │                                          │
│ ──────── │                                          │
│ RACE     │                                          │
│ [2026    │                                          │
│  Primary]│                                          │
│ [Congres]│           MAP (fills remaining           │
│ [CD-9   ]│             viewport ~85%)               │
│          │                                          │
│ ──────── │  [+]                                     │
│ VIEW     │  [-]              [Legend ▾]             │
│ ●Winner  │                                          │
│ ○Turnout │                                          │
│ ○Margin  │                                          │
│ ○More ▾  │                                          │
│          ├──────────────────────────────────────────┤
│ ──────── │  Registered: 425,963 · Ballots: 117,404  │
│ FILTER   │  Turnout: 27.6% · Winner: D.Bliss · 3.5pp│
│ [All     └──────────────────────────────────────────┘
│  Precincts]
│ ────────
│ Layer
│ [Results]
│ [Finance]
│ ────────
│ [⬇ Export]
│
└──────────
  240px
```

**Why left sidebar wins over top toolbar for this app:**

1. **Controls are vertical lists, not horizontal navigation.** Dropdowns and button groups stack naturally in a 240px column. The toolbar wraps into 3–5 horizontal rows because controls fight for width they don't have.

2. **Map gets 85%+ of viewport.** 240px sidebar on a 1600px-wide screen leaves 1360px for the map — 85% vs. 64% today. On a 1280px laptop, 240px leaves 1040px map — still ~81%.

3. **Sidebar scales with content.** Adding Finance controls (5 more selects + 8 buttons) adds scroll to the sidebar, not new rows that push the map down. Today, enabling Finance mode expands the toolbar and further crushes map height.

4. **Sidebar can collapse to icon rail.** When users want maximum map, they collapse to a 48px icon strip. The rail shows: `[⎒ Race] [👁 View] [⊞ Layer] [⊕ Filter] [⬇ Export]` as icon buttons that expand panels on hover/click.

5. **Sidebar supports future features.** Bookmarked views, share links, layer presets — these all fit naturally in a sidebar with sections. A top toolbar that's already at 275px has nowhere to go.

### Header on Desktop

Current desktop header (50px) is efficient: logo, title, subtitle left; stats right. **Keep this.** The stats bar (Registered, Ballots, Turnout, Winner, Margin) is the right place for race-level summary data.

**One improvement:** Make the stats bar clickable to a "Race Summary" panel that shows full results table for the selected race — currently this data lives only in the precinct-click bottom sheet / info panel.

### Map as Hero: Rules for Desktop

1. The map must always be at least **80% of viewport width** and **100% of remaining height** (header to footer)
2. No control panels should ever float over the map on desktop — sidebar and header are the designated UI zones
3. Info panel (precinct hover detail) stays at `position: absolute` bottom-right inside `.map-wrap` — correct current behavior
4. Legend stays `position: absolute` bottom-left inside `.map-wrap` — correct current behavior
5. The "Select a Race" empty-state overlay is well-designed; keep it

---

## 5. Proposed IA Restructure

### The 27 Controls Mapped to a New Hierarchy

#### Tier 1: Always Visible (Race Context — the "headline" of every view)

These appear in both desktop sidebar (top section) and mobile header strip:

```
[Election Cycle ▾]  [District Type ▾]  [Race ▾]
```

Three dropdowns in sequence. On mobile, rendered as a compact "context chip" in the header:
`CD-9 · 2026 Primary ▾` → tap to open race selector bottom sheet.

Currently these are spread across 3 separate toolbar sections with ELECTION / DISTRICT labels. Consolidate into a single "RACE" section.

#### Tier 2: Always Visible (View Mode — changes meaning without changing context)

The 3 primary view modes as a segmented control, always visible:

```
[ Winner | Turnout | Margin ]
```

Plus a "More" button that reveals the full set. On mobile, this lives in the bottom strip. On desktop, this lives in the sidebar under "VIEW".

**Rationale for only 3 primary:** 80% of sessions will use Winner, Turnout, or Margin. The other 5 modes (Candidate, Vs, Turnout Δ, Swing, Votes) require additional configuration and serve specific analytical tasks.

#### Tier 3: Expanded View Modes (secondary — visible behind "More" button)

```
[ Candidate ]  → reveals: Candidate A selector
[ Vs        ]  → reveals: Candidate A + B selectors (or multi-checklist)
[ Turnout Δ ]  → reveals: Compare-To Election selector
[ Swing     ]  → reveals: Compare-To Election selector (same as Δ)
[ Votes     ]  → no additional config needed
```

The key change: **contextual sub-controls appear inline, immediately after selecting the mode**, rather than being permanently visible in a `viewOpts` div that shows empty/disabled states when no mode requires them.

#### Tier 4: Filter (secondary — collapsed by default, 1 tap)

```
FILTER
[Focus: All Precincts ▾]  ← municipality filter
```

On mobile: inside the full-controls bottom sheet.
On desktop: collapsible section in sidebar.

#### Tier 5: Data Layer (secondary — most sessions use one layer)

```
DATA LAYER
[● Election Results]  [○ Campaign Finance]
```

On mobile: at top of full-controls bottom sheet.
On desktop: near bottom of sidebar, since switching layers is an infrequent global action.

When Finance is active, Finance controls replace Election controls entirely (current behavior is good — just needs to be carried forward into the new layout structure).

#### Tier 6: Actions (always visible but low-prominence)

```
[⬇ Export PNG]  [🔗 Share Link ← NEW]
```

On mobile: bottom of controls sheet, full-width.
On desktop: bottom of sidebar.

**The Share Link button is missing from the current UI and is arguably the most important missing feature.** The core use case ("shared with people who pull it up on their phones") requires a shareable URL that encodes the current state: `?election=2026_gov_primary&type=congress&race=cd9&view=winner`.

### Full Progressive Disclosure Model

```
LEVEL 0 — Page load, no race selected
  Visible: Race Selector (3 dropdowns) + empty-state map overlay
  Hidden: All view modes, filters, export (nothing to act on yet)

LEVEL 1 — Race selected, first map renders
  Visible: Race Selector + [Winner|Turnout|Margin] + map
  Visible: Export + Share buttons activate
  Hidden: Advanced view modes, Finance controls, per-mode config

LEVEL 2 — User expands to secondary view mode
  Visible: All above + expanded mode selector
  If mode requires config: relevant config appears inline (candidate picker, etc.)
  Hidden: Finance controls (unless layer switched)

LEVEL 3 — Finance layer activated
  Replaces: Election controls → Finance controls (same structure, different data)
  Shows: Finance-specific modes
  Hidden: Election controls (but race context "CD-9" shown in header for reference)
```

### Control Inventory Remapped

| # | Control | Current Location | Proposed Location | Tier |
|---|---|---|---|---|
| 1 | Data Layer: Election | Toolbar (top) | Sidebar / Sheet (bottom section) | 5 |
| 2 | Data Layer: Finance | Toolbar (top) | Sidebar / Sheet (bottom section) | 5 |
| 3 | Election dropdown | Toolbar | Sidebar top / Race Selector | 1 |
| 4 | District Type dropdown | Toolbar | Sidebar top / Race Selector | 1 |
| 5 | Race dropdown | Toolbar | Sidebar top / Race Selector | 1 |
| 6 | View: Turnout | Toolbar | Segmented control (primary) | 2 |
| 7 | View: Winner | Toolbar | Segmented control (primary) | 2 |
| 8 | View: Margin | Toolbar | Segmented control (primary) | 2 |
| 9 | View: Candidate | Toolbar | "More" expanded / Sheet | 3 |
| 10 | View: Vs | Toolbar | "More" expanded / Sheet | 3 |
| 11 | View: Turnout Δ | Toolbar | "More" expanded / Sheet | 3 |
| 12 | View: Swing | Toolbar | "More" expanded / Sheet | 3 |
| 13 | View: Votes | Toolbar | "More" expanded / Sheet | 3 |
| 14 | Focus dropdown | Toolbar | Sidebar / Sheet (Filter section) | 4 |
| 15 | Export PNG | Toolbar | Sidebar / Sheet (Actions) | 6 |
| 16 | Finance: Election | Toolbar (hidden) | Sidebar / Sheet (Finance section) | 5 |
| 17 | Finance: Supporters | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 18 | Finance: Whales | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 19 | Finance: Donor Margin | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 20 | Finance: Candidate $ | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 21 | Finance: Vs | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 22 | Finance: Money Δ | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 23 | Finance: Swing | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 24 | Finance: Total $ | Toolbar (hidden) | Sidebar / Sheet (Finance modes) | 5 |
| 25 | Committee A | Toolbar (hidden) | Sidebar / Sheet (contextual) | 3/5 |
| 26 | Committee B | Toolbar (hidden) | Sidebar / Sheet (contextual) | 3/5 |
| 27 | Previous Election | Toolbar (hidden) | Sidebar / Sheet (contextual) | 3/5 |

---

## 6. Detailed Wireframes

### Mobile: Default State (Race Loaded)

```
┌───────────────────────────────────┐  390px wide
│ [D4D]  CD-9 · 2026 Primary     [⋮]│  44px header
│ Winner · Daniel Bliss · +3.5pp  ▸ │  32px context strip (tappable)
├───────────────────────────────────┤
│                                   │
│                                   │
│                                   │
│       MAP (full bleed)            │  ≈ 680px available
│                                   │
│ [+]                               │
│ [-]                    [▪ Key ▾] │
│                                   │
├───────────────────────────────────┤
│  [Winner] [Turnout] [Margin] [···]│  48px bottom strip (primary modes)
└───────────────────────────────────┘

Notes:
- [⋮] opens full controls bottom sheet
- Context strip tap → stats sheet (Registered/Ballots/Turnout)
- [▪ Key ▾] = legend pill, starts closed, expands upward
- [···] = "More modes" → expands bottom strip to show all 8 modes
```

### Mobile: Controls Sheet (open via [⋮])

```
┌───────────────────────────────────┐
│ ────────── drag handle ─────────  │  10px
│ Controls                      [×] │  44px
├───────────────────────────────────┤
│ RACE                              │
│ [2026 Gubernatorial Primary    ▾] │
│ [Congressional                 ▾] │
│ [U.S. Rep, 9th District – DEM  ▾] │
├───────────────────────────────────┤
│ VIEW MODE                         │
│ [●Winner] [Turnout] [Margin]      │
│ [Candidate][Vs][Turnout Δ]       │
│ [Swing   ][Votes  ]               │
│                                   │
│ ┌ Contextual (only when Vs active)┐│
│ │ Candidate A [Select…        ▾] ││
│ │ Candidate B [Select…        ▾] ││
│ └──────────────────────────────── ┘│
├───────────────────────────────────┤
│ FILTER                            │
│ [All Precincts                 ▾] │
├───────────────────────────────────┤
│ DATA LAYER                        │
│ [● Election Results] [○ Finance]  │
├───────────────────────────────────┤
│ [⬇ Export PNG] [🔗 Share Link]   │
└───────────────────────────────────┘
max-height: 75vh, internally scrollable
```

### Desktop: Sidebar Layout (1600px)

```
┌──────────────────────────────────────────────────────────────────┐
│ [D4D] D4D Election Heatmap Platform     Registered 425,963       │  50px header
│       Precinct-Level · Cook County                Ballots 117,404│
│                                                   Turnout 27.6%  │
│                                         Winner D.Bliss · 3.5pp   │
├──────────┬───────────────────────────────────────────────────────┤
│ RACE     │                                                        │
│          │                                                        │
│ 2026     │                                                        │
│ Guber.   │                                                        │
│ Primary  │                                                        │
│ ─────    │              MAP                                       │
│ Congres- │          (fills ≈1360px × 810px)                      │
│ sional   │                                                        │
│ ─────    │                                                        │
│ CD-9     │  [+]                                                   │
│ DEM      │  [-]                          [▪ Legend ▾]            │
│          │                                                        │
│ ──────── │                                                        │
│ VIEW     │                                                        │
│          │                                                        │
│ ●Winner  ├───────────────────────────────────────────────────────┤
│ ○Turnout │ Data: IL SBE · Chicago BOE · Cook County Clerk        │
│ ○Margin  └───────────────────────────────────────────────────────┘
│ ⌄ More
│
│ ────────
│ FILTER
│ All
│ Precincts
│
│ ────────
│ LAYER
│ ●Results
│ ○Finance
│
│ ────────
│ [⬇ Export]
│ [🔗 Share ]
│
│ [◀ Collapse]
└──────────
  240px
```

### Desktop: Sidebar Collapsed (Icon Rail)

```
┌────┬──────────────────────────────────────────────────────────────┐
│[D4D│ D4D Election Heatmap ...                  stats stats stats  │ header
├────┼──────────────────────────────────────────────────────────────┤
│[⎒] │                                                              │
│[👁]│                                                              │
│[⊞] │              MAP (≈1552px wide)                              │
│[⊕] │                                                              │
│[⬇] │                                                              │
│    │                                                              │
│[▶] │                                                              │
└────┴──────────────────────────────────────────────────────────────┘
  48px
```

Icon rail: ⎒ = Race, 👁 = View, ⊞ = Layer, ⊕ = Filter, ⬇ = Export. Each icon click opens a popover panel anchored to the rail.

---

## 7. Specific Bug Fixes Required

### Bug 1: Header Intercepts Mobile Toolbar Clicks (Critical)

**Root cause:** The `.header` has `z-index: 1000` and is effectively fixed. The `.toolbar.expanded` is in document flow below it but can render its lower content at Y coordinates that overlap with the header due to how the viewport/scroll context works when the toolbar max-height animates.

**Fix:**
```css
/* Remove toolbar from document flow on mobile */
@media (max-width: 768px) {
  .toolbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1050; /* above header */
    transform: translateY(-100%);
    transition: transform 0.3s ease;
    max-height: none; /* remove max-height animation */
  }
  .toolbar.expanded {
    transform: translateY(77px); /* below header */
  }
}
```

Or better yet: replace the toolbar entirely with a bottom sheet as proposed in Section 3.

### Bug 2: Mode Button Touch Targets Too Small

Current mode buttons in 4-column grid: `width = (390 - 24px padding - 12px gaps) / 4 ≈ 87px`. At `padding: 8px 4px`, the tap target height is approximately `11px × 1.2 line-height + 16px padding ≈ 29px`. This is below the WCAG 2.1 minimum of 44×44px.

**Fix:** Minimum 44px height on all touch targets on mobile.

```css
@media (max-width: 768px) {
  .mode-btn {
    min-height: 44px;
    padding: 12px 4px;
  }
}
```

### Bug 3: Legend Z-Index Conflict with Bottom Sheet

Legend is at `z-index: 800`, bottom sheet at `z-index: 1100`. When the bottom sheet is at peek height (≈100px), the legend can show through at the corners.

**Fix:** When bottom sheet is open, set `legend { pointer-events: none; opacity: 0.3; }` to visually recede it. When bottom sheet closes, restore.

### Bug 4: Stats Bar Hidden Scroll

The stats bar is `overflow-x: auto; scrollbar-width: none` — invisible scroll. Users with 4+ stats (Registered, Ballots, Turnout, Winner, Margin) can't see them all.

**Fix:** Show first 3 stats always, add a `▸` indicator if more exist. Or replace with the context strip approach in the mobile redesign.

---

## 8. Implementation Priority

### Phase 1 — Fix Critical Bugs (Mobile Functionality) — 1–2 days

1. Fix header intercept bug (toolbar z-index / position fix)
2. Increase all mode button touch targets to min 44px height
3. Fix legend z-index conflict with bottom sheet

### Phase 2 — Mobile UX Restructure — 3–5 days

1. Replace toolbar expand with bottom sheet (slide up from bottom)
2. Add permanent bottom mode strip (Winner / Turnout / Margin / ···)
3. Replace scrolling stats bar with context strip chip
4. Implement tap-to-open legend pill with viewport-relative max-height

### Phase 3 — Desktop Sidebar — 3–5 days

1. Implement left sidebar at 240px, collapsible to 48px icon rail
2. Move all toolbar controls into sidebar sections
3. Remove horizontal toolbar entirely on desktop
4. Adjust map-wrap to account for sidebar width

### Phase 4 — Progressive Disclosure & State Sharing — 2–3 days

1. Contextual sub-controls (candidate/comparison selects) appear inline only when relevant mode is active
2. URL state encoding (`?election=...&type=...&race=...&view=...`)
3. Share Link button that copies URL to clipboard
4. Empty-state improvements: smart defaults (most recent election pre-selected)

### Phase 5 — Polish — 1–2 days

1. Mode buttons: add brief descriptions as `title` attributes / tooltips
2. Race selector: add count indicator ("9 races available")
3. Keyboard accessibility: tab order, focus indicators for sidebar
4. Reduce motion: `prefers-reduced-motion` for bottom sheet animation

---

## 9. What to Preserve

Not everything needs to change. These current design decisions are correct:

- **Dark theme** (`#0f1117` background, `#4fc3f7` accent) — appropriate for a data tool, reduces eye strain
- **Info panel (precinct hover)** — desktop `position: absolute` bottom-right with `opacity` transition works well
- **Bottom sheet for precinct detail on mobile** — architecture is right, just needs content refinement
- **Finance controls hidden by default** — this is correct progressive disclosure; keep it
- **Legend starts closed on mobile** — correct; just needs the visual pill treatment
- **Footer attribution** — keep on desktop, correctly hidden on mobile
- **Leaflet zoom controls** — correctly styled, correct position

---

## 10. Summary of Key Recommendations

| Recommendation | Impact | Effort |
|---|---|---|
| Fix header intercept bug on mobile | Critical | Low |
| Replace mobile toolbar with bottom sheet + bottom strip | High | Medium |
| Implement desktop left sidebar | High | Medium |
| Add URL state / Share Link | High | Medium |
| Progressive contextual sub-controls | Medium | Low |
| Context strip replaces stats bar scroll | Medium | Low |
| Legend as tap-to-open pill | Medium | Low |
| Smart default race selection | Medium | Low |
| Min 44px touch targets | Medium | Low |
| Reduce visible controls at landing to Race Selector only | Medium | Low |

The single highest-leverage change is **moving from a top toolbar to a left sidebar on desktop** — it gives back ~20% of vertical map space and removes the need for flex-wrap that creates unpredictable multi-row layouts. On mobile, the **bottom sheet + permanent mode strip** eliminates the click-blocking bug and makes the tool usable one-handed without the map disappearing.

---

*Audit prepared using screenshots, extracted CSS, HTML source review, and UX best-practice research including Nielsen Norman Group bottom sheet guidelines, Interaction Design Foundation progressive disclosure framework, and pattern analysis from Google Maps, Zillow, and Felt.com.*
