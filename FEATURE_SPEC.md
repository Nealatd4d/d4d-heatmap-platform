# Feature Spec: Municipality Focus + PNG Export

## Architecture Overview
- `index.html` is a single-page Leaflet map app (~2280 lines)
- Uses Supabase RPC for data, Leaflet for rendering, inline `<script>` block
- GeoJSON loaded from Supabase Storage, features get `_pid`, `_label`, `_muni` (new) computed
- The IIFE starts at line 313: `(function(){ 'use strict'; ...})();`
- All state variables are declared starting line 380
- Key DOM refs at line 407-410

## Key Variables (all inside the IIFE)
- `geoFeatures[]` — all GeoJSON features with `._pid` and `._label`
- `currentElectionId`, `currentRaceType`, `currentRaceId`, `currentMode`
- `raceMapCache{}` — race_id → {pid: {total_votes, candidates}}
- `turnoutCache{}` — election_id → {pid: {registered_voters, ballots_cast, turnout_pct}}
- `precinctLayer` — current active Leaflet GeoJSON layer
- `bgLayer` — gray background layer for context precincts
- `map` — the Leaflet map instance
- `candidateColorMap{}` — candidate name → hex color
- `dataLayer` — 'election' or 'finance'

## GeoJSON Feature Properties
- Chicago: `{ward, precinct, name: "Ward 2 Precinct 15", jur: "chicago"}` → `_label = name`
- Suburban: `{precinctid: "7501003", name: "EVANSTON 3-3", jur: "suburban"}` → `_label = name`

## Municipality Extraction from `_label`
- Chicago features: municipality = "Chicago" (could also group by "Ward X")
- Suburban features: extract from label using regex `/^([A-Z\s]+?)\s+\d/` 
  - "EVANSTON 3-3" → "EVANSTON"
  - "BARRINGTON 11" → "BARRINGTON"  
  - "NEW TRIER 5" → "NEW TRIER"
- 30 suburban townships + Chicago = 31 total municipalities

## Evanston Precincts
- 45 precincts, codes 7501001-7509005 (9 wards × ~5 precincts each)
- All in jurisdiction `cook_suburban`

## Key Functions
- `loadGeoJSON()` (line 619) — loads and processes both GeoJSON files, computes `_pid` and `_label`
- `render()` (line 1134) — main render function, builds active/bg features, creates Leaflet layers
- `updateLegend()` (line 1393) — updates legend HTML
- `updateStats()` (line 1357) — updates header stats
- `onRaceSelected()` (line 1277) — called when race dropdown changes
- `aggregateCandidates(raceData)` — returns sorted [[name, totalVotes], ...] array

## CSS Classes Used
- `.toolbar` — toolbar container
- `.toolbar-label` — small uppercase labels
- `.toolbar-sep` — vertical separator
- `.mode-btn` / `.mode-btn.active` — mode toggle buttons  
- `.toolbar select` — styled select dropdowns
- Mobile: toolbar collapses, uses `.filter-toggle` button to expand

## What Needs to Be Built

### Feature 1: Municipality Focus (saves to focus_feature.js)
1. Add `_muni` property to each geoFeature during `loadGeoJSON()` 
2. Add state variable: `let focusMunicipality = '';`
3. Add `<select id="selFocus">` dropdown in toolbar HTML (after the View mode group, before finance controls)
4. Add `<span class="toolbar-label">Focus</span>` label
5. Function `updateFocusOptions()` — populate dropdown with municipalities that have precincts in current active race data
6. In `render()`, after computing `activeFeats`, apply focus filter:
   - If `focusMunicipality` is set, filter `activeFeats` to only features where `_muni === focusMunicipality`
   - Also filter `bgFeats` similarly  
   - Force `pidsChanged = true` so fitBounds fires on focus change
7. Call `updateFocusOptions()` from `onRaceSelected()` and when election changes
8. On focus change: `focusMunicipality = selFocus.value; render();`

### Feature 2: PNG Export (saves to export_feature.js)
1. Add html-to-image library: `<script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js"></script>`
2. Add export button in toolbar (an SVG download icon button)
3. CSS for `.export-btn` and `.export-title-overlay`  
4. `exportPNG()` function:
   a. Create a temporary title overlay div on top of the map with: Election name, Race name, Mode, Focus municipality (if set)
   b. Hide UI chrome (toolbar, header, zoom controls)
   c. Use `htmlToImage.toPng()` on `.map-wrap` element (which contains #map + legend + title overlay)
   d. Create download link, trigger click
   e. Clean up: remove title overlay, restore UI

## Integration Points
Both features modify `index.html`. The sub-agents should write their code to separate files:
- Sub-agent 1: `/home/user/workspace/d4d-heatmap-platform/patches/focus_patch.md` — describes exact edits
- Sub-agent 2: `/home/user/workspace/d4d-heatmap-platform/patches/export_patch.md` — describes exact edits
Parent agent will integrate both.
