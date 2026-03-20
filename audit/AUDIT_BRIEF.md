# D4D Heatmap Platform — UI/UX Audit Brief

## Product
Interactive election heatmap platform for Cook County & Chicago. Shows precinct-level election results, turnout, campaign finance data across multiple elections and races.

## Current Metrics
- **Desktop (1600x900):** Header 50px + Toolbar 275px = 325px overhead. Map gets 575px (64%). Toolbar is 31% of viewport.
- **Mobile (390x844):** Header 77px + stat bar. Toolbar hidden behind filter icon but when open is 367px tall — takes 44% of viewport. Map interaction is blocked by overlapping elements.
- **Total interactive controls in toolbar:** 27 (8 selects, 19 buttons)
- **Index.html:** ~2500 lines, single file with inline CSS and JS

## User (Neal) Requirements
- **Mobile-first design** — this will be shared with people who pull it up on their phones
- **Controls must be OFF the map** — in toolbar, not floating overlays (existing requirement)
- **Legend on mobile should only open/close when explicitly tapped** (existing requirement)
- Tool for creating and sharing maps — not just viewing one

## Current Control Inventory (what the toolbar contains)
1. **DATA LAYER toggle** — Election Results | Campaign Finance (2 buttons)
2. **ELECTION dropdown** — select which election cycle (1 select)
3. **DISTRICT section** — Type dropdown + Race dropdown (2 selects)
4. **VIEW mode buttons** — Turnout, Winner, Margin, Candidate, Vs, Turnout Δ, Swing, Votes (8 buttons)
5. **FOCUS dropdown** — Municipality filter (1 select)
6. **Export PNG button** (1 button)
7. **Finance-specific controls** (when finance layer active):
   - Finance Election dropdown (1 select)
   - Finance mode buttons: Donor Margin, Candidate $, Vs, $ Delta, Swing (5 buttons)
   - Committee A dropdown (1 select)
   - Committee B dropdown (1 select)
   - Previous Election dropdown (1 select)

## Screenshots Available
- `audit/desktop-landing.png` — Desktop initial state
- `audit/desktop-cd9-winner.png` — Desktop with CD-9 DEM Winner loaded
- `audit/mobile-cd9-current.png` — Mobile with toolbar closed
- `audit/mobile-cd9-toolbar-open.png` — Mobile with toolbar open

## CSS
- `audit/extracted-css.css` — Current full CSS

## Key Problems Observed
1. Mobile: toolbar overlaps map elements, mode buttons unreachable (Playwright couldn't click them — header intercepts)
2. Desktop: 31% of screen is toolbar — map feels cramped
3. 27 controls don't scale — every feature adds another row
4. No visual hierarchy among controls — everything is equally prominent
5. Legend on mobile with 15 candidates takes up massive space
6. Stat bar (Registered, Ballots, Turnout, Winner, Margin) competes with toolbar for space
