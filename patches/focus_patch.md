# Municipality Focus Feature — Patch for index.html

This patch describes every exact edit needed to implement the Municipality Focus dropdown feature. Edits are meant to be applied in order.

---

### Edit 1: Add `focusMunicipality` state variable

**File:** index.html

**Find (exact text to match):**
```
let vsCandidates = []; // multi-candidate vs mode
let candidateColorMap = {};
```

**Replace with:**
```
let vsCandidates = []; // multi-candidate vs mode
let candidateColorMap = {};
let focusMunicipality = ''; // municipality focus filter
```

---

### Edit 2: Add `lastFocusKey` tracker and `selFocus` DOM reference

**File:** index.html

**Find (exact text to match):**
```
const $ = id => document.getElementById(id);
const selElection = $('selElection'), selType = $('selType'), selRace = $('selRace');
const infoPanel = $('infoPanel'), headerStats = $('headerStats'), legendEl = $('legend');
const landing = $('landing'), loader = $('loader'), viewOpts = $('viewOpts');
```

**Replace with:**
```
const $ = id => document.getElementById(id);
const selElection = $('selElection'), selType = $('selType'), selRace = $('selRace');
const infoPanel = $('infoPanel'), headerStats = $('headerStats'), legendEl = $('legend');
const landing = $('landing'), loader = $('loader'), viewOpts = $('viewOpts');
const selFocus = $('selFocus');
```

---

### Edit 3: Add `lastFocusKey` tracker near `lastActivePidKey`

**File:** index.html

**Find (exact text to match):**
```
let bgLayer = null; // gray background precincts outside current race
let lastActivePidKey = ''; // track if precinct set changed (for fitBounds)
```

**Replace with:**
```
let bgLayer = null; // gray background precincts outside current race
let lastActivePidKey = ''; // track if precinct set changed (for fitBounds)
let lastFocusKey = ''; // track if municipality focus changed (for fitBounds)
```

---

### Edit 4: Add HTML for Focus dropdown in the toolbar (inside `#electionControls`, after `viewOpts` div)

**File:** index.html

**Find (exact text to match):**
```
        <div class="view-opts" id="viewOpts"></div>
      </div>

      <!-- Campaign Finance controls (hidden by default) -->
```

**Replace with:**
```
        <div class="view-opts" id="viewOpts"></div>
        <div class="toolbar-sep"></div>
        <span class="toolbar-label">Focus</span>
        <select id="selFocus"><option value="">All Precincts</option></select>
      </div>

      <!-- Campaign Finance controls (hidden by default) -->
```

---

### Edit 5: Add `_muni` property for Chicago features in `loadGeoJSON()`

**File:** index.html

**Find (exact text to match):**
```
  // Chicago
  for (const f of chiRes.features) {
    const p = f.properties;
    const pid = chicagoPrecinctId(p.ward, p.precinct);
    f._pid = pid;
    f._label = p.name;
    pidToFeatureIdx[pid] = geoFeatures.length;
    geoFeatures.push(f);
  }
```

**Replace with:**
```
  // Chicago
  for (const f of chiRes.features) {
    const p = f.properties;
    const pid = chicagoPrecinctId(p.ward, p.precinct);
    f._pid = pid;
    f._label = p.name;
    f._muni = 'CHICAGO';
    pidToFeatureIdx[pid] = geoFeatures.length;
    geoFeatures.push(f);
  }
```

---

### Edit 6: Add `_muni` property for Suburban features in `loadGeoJSON()`

**File:** index.html

**Find (exact text to match):**
```
  // Suburban
  for (const f of subRes.features) {
    const p = f.properties;
    const pid = suburbanPrecinctId(p.precinctid);
    f._pid = pid;
    f._label = p.name;
    pidToFeatureIdx[pid] = geoFeatures.length;
    geoFeatures.push(f);
  }
```

**Replace with:**
```
  // Suburban
  for (const f of subRes.features) {
    const p = f.properties;
    const pid = suburbanPrecinctId(p.precinctid);
    f._pid = pid;
    f._label = p.name;
    const _muniMatch = p.name.match(/^([A-Z\s]+?)\s+\d/);
    f._muni = _muniMatch ? _muniMatch[1].trim() : p.name;
    pidToFeatureIdx[pid] = geoFeatures.length;
    geoFeatures.push(f);
  }
```

---

### Edit 7: Add `updateFocusOptions()` function after `updateViewOpts()`

**File:** index.html

**Find (exact text to match):**
```
/* ═══════════════════ STYLE PER FEATURE ═══════════════════ */
function getStyle(pid, turnout, raceData, turnout2, raceData2) {
```

**Replace with:**
```
/* ═══════════════════ MUNICIPALITY FOCUS ═══════════════════ */
function updateFocusOptions() {
  if (!selFocus) return;

  // Determine which pids are currently active
  let activePids = null;
  if (dataLayer === 'finance') {
    // For finance layer, derive from financeMapCache using current key
    const key = currentFinanceElectionId + '|' + currentFinanceMode + '|' +
      (selectedCommitteeA || '') + '|' + (selectedCommitteeB || '') + '|' + (selectedFinancePrev || '');
    const cached = financeMapCache[key];
    if (cached) activePids = new Set(cached.map(r => r.precinct_id));
  } else {
    // Election layer
    if (currentRaceId && raceMapCache[currentRaceId]) {
      activePids = new Set(Object.keys(raceMapCache[currentRaceId]));
    } else if (currentElectionId && turnoutCache[currentElectionId]) {
      activePids = new Set(Object.keys(turnoutCache[currentElectionId]));
    }
  }

  if (!activePids || !activePids.size) {
    // No active data — reset to just "All Precincts"
    selFocus.innerHTML = '<option value="">All Precincts</option>';
    focusMunicipality = '';
    return;
  }

  // Collect unique municipality names from active features
  const munis = new Set();
  for (const pid of activePids) {
    const idx = pidToFeatureIdx[pid];
    if (idx != null) {
      const f = geoFeatures[idx];
      if (f && f._muni) munis.add(f._muni);
    }
  }

  const sortedMusis = [...munis].sort((a, b) => {
    // CHICAGO always first, then alphabetical
    if (a === 'CHICAGO' && b !== 'CHICAGO') return -1;
    if (b === 'CHICAGO' && a !== 'CHICAGO') return 1;
    return a.localeCompare(b);
  });

  // Preserve current selection if still valid
  const prevFocus = focusMunicipality;

  selFocus.innerHTML = '<option value="">All Precincts</option>';
  for (const muni of sortedMusis) {
    const o = document.createElement('option');
    o.value = muni;
    o.textContent = muni === 'CHICAGO' ? 'Chicago' : muni.charAt(0) + muni.slice(1).toLowerCase();
    selFocus.appendChild(o);
  }

  // Restore prior selection if still available, otherwise clear
  if (prevFocus && munis.has(prevFocus)) {
    selFocus.value = prevFocus;
    focusMunicipality = prevFocus;
  } else {
    selFocus.value = '';
    focusMunicipality = '';
  }
}

/* ═══════════════════ STYLE PER FEATURE ═══════════════════ */
function getStyle(pid, turnout, raceData, turnout2, raceData2) {
```

---

### Edit 8: Apply focus filter in `render()` — replace `activeFeats`/`bgFeats` block and update `pidsChanged` logic

**File:** index.html

**Find (exact text to match):**
```
    const activeFeats = geoFeatures.filter(f => activePids.has(f._pid));
    const bgFeats = racePids.size > 0
      ? geoFeatures.filter(f => !racePids.has(f._pid) && turnoutPids.has(f._pid))
      : [];

    // Check if precinct set changed (for fitBounds)
    const pidKey = currentRaceId || currentElectionId;
    const pidsChanged = pidKey !== lastActivePidKey;
    lastActivePidKey = pidKey;
```

**Replace with:**
```
    const activeFeats = geoFeatures.filter(f => activePids.has(f._pid));
    const bgFeats = racePids.size > 0
      ? geoFeatures.filter(f => !racePids.has(f._pid) && turnoutPids.has(f._pid))
      : [];

    // Apply municipality focus filter
    const focusedActiveFeats = focusMunicipality
      ? activeFeats.filter(f => f._muni === focusMunicipality)
      : activeFeats;
    const focusedBgFeats = focusMunicipality
      ? bgFeats.filter(f => f._muni !== focusMunicipality)
      : bgFeats;

    // Check if precinct set changed (for fitBounds)
    const pidKey = currentRaceId || currentElectionId;
    const pidsChanged = pidKey !== lastActivePidKey || focusMunicipality !== lastFocusKey;
    lastActivePidKey = pidKey;
    lastFocusKey = focusMunicipality;
```

---

### Edit 9: Use `focusedBgFeats` in the background layer inside `render()`

**File:** index.html

**Find (exact text to match):**
```
    // Background layer (gray, non-interactive) for context
    if (bgFeats.length > 0) {
      bgLayer = L.geoJSON({ type: 'FeatureCollection', features: bgFeats }, {
        style: () => ({ fillColor: '#1e2028', color: '#1a1d27', weight: 0.5, fillOpacity: 0.4 }),
        interactive: false
      }).addTo(map);
    }

    // Active precinct layer
    precinctLayer = L.geoJSON({ type: 'FeatureCollection', features: activeFeats }, {
```

**Replace with:**
```
    // Background layer (gray, non-interactive) for context
    if (focusedBgFeats.length > 0) {
      bgLayer = L.geoJSON({ type: 'FeatureCollection', features: focusedBgFeats }, {
        style: () => ({ fillColor: '#1e2028', color: '#1a1d27', weight: 0.5, fillOpacity: 0.4 }),
        interactive: false
      }).addTo(map);
    }

    // Active precinct layer
    precinctLayer = L.geoJSON({ type: 'FeatureCollection', features: focusedActiveFeats }, {
```

---

### Edit 10: Add focus filter and `pidsChanged` tracking in `renderFinance()`

**File:** index.html

**Find (exact text to match):**
```
    const activePids = new Set(Object.keys(financeData));
    const activeFeats = geoFeatures.filter(f => activePids.has(f._pid));
    const bgFeats = geoFeatures.filter(f => !activePids.has(f._pid));

    // Check if set changed for fitBounds
    const pidKey = 'finance_' + currentFinanceElectionId + '_' + currentFinanceMode;
    const pidsChanged = pidKey !== lastActivePidKey;
    lastActivePidKey = pidKey;
```

**Replace with:**
```
    const activePids = new Set(Object.keys(financeData));
    const activeFeats = geoFeatures.filter(f => activePids.has(f._pid));
    const bgFeats = geoFeatures.filter(f => !activePids.has(f._pid));

    // Apply municipality focus filter
    const focusedActiveFeats = focusMunicipality
      ? activeFeats.filter(f => f._muni === focusMunicipality)
      : activeFeats;
    const focusedBgFeats = focusMunicipality
      ? bgFeats.filter(f => f._muni !== focusMunicipality)
      : bgFeats;

    // Check if set changed for fitBounds
    const pidKey = 'finance_' + currentFinanceElectionId + '_' + currentFinanceMode;
    const pidsChanged = pidKey !== lastActivePidKey || focusMunicipality !== lastFocusKey;
    lastActivePidKey = pidKey;
    lastFocusKey = focusMunicipality;
```

---

### Edit 11: Use `focusedBgFeats` and `focusedActiveFeats` in `renderFinance()` background/active layers

**File:** index.html

**Find (exact text to match):**
```
    // Background layer
    if (bgFeats.length > 0) {
      bgLayer = L.geoJSON({ type: 'FeatureCollection', features: bgFeats }, {
        style: () => ({ fillColor: '#1e2028', color: '#1a1d27', weight: 0.5, fillOpacity: 0.4 }),
        interactive: false
      }).addTo(map);
    }

    // Active precinct layer
    precinctLayer = L.geoJSON({ type: 'FeatureCollection', features: activeFeats }, {
      style: f => getFinanceStyle(f._pid, financeData),
```

**Replace with:**
```
    // Background layer
    if (focusedBgFeats.length > 0) {
      bgLayer = L.geoJSON({ type: 'FeatureCollection', features: focusedBgFeats }, {
        style: () => ({ fillColor: '#1e2028', color: '#1a1d27', weight: 0.5, fillOpacity: 0.4 }),
        interactive: false
      }).addTo(map);
    }

    // Active precinct layer
    precinctLayer = L.geoJSON({ type: 'FeatureCollection', features: focusedActiveFeats }, {
      style: f => getFinanceStyle(f._pid, financeData),
```

---

### Edit 12: Call `updateFocusOptions()` at end of `onRaceSelected()`

**File:** index.html

**Find (exact text to match):**
```
async function onRaceSelected() {
  selectedCandidate = '';
  vsCandidate1 = '';
  vsCandidate2 = '';
  vsCandidates = [];

  if (currentRaceId) {
    await fetchRaceMap(currentRaceId);
  }
  await updateViewOpts();
  render();
}
```

**Replace with:**
```
async function onRaceSelected() {
  selectedCandidate = '';
  vsCandidate1 = '';
  vsCandidate2 = '';
  vsCandidates = [];

  if (currentRaceId) {
    await fetchRaceMap(currentRaceId);
  }
  await updateViewOpts();
  updateFocusOptions();
  render();
}
```

---

### Edit 13: Add `selFocus` change event listener and call `updateFocusOptions()` in `selElection` change handler

**File:** index.html

**Find (exact text to match):**
```
selElection.addEventListener('change', async () => {
  currentElectionId = selElection.value;
  currentRaceType = '';
  currentRaceId = '';
  selectedCandidate = ''; vsCandidate1 = ''; vsCandidate2 = ''; vsCandidates = [];
  viewOpts.innerHTML = '';
  await populateTypeDropdown();
  selRace.innerHTML = '<option value="">Select Race…</option>';
  selRace.disabled = true;
  clearMap();
});
```

**Replace with:**
```
selElection.addEventListener('change', async () => {
  currentElectionId = selElection.value;
  currentRaceType = '';
  currentRaceId = '';
  selectedCandidate = ''; vsCandidate1 = ''; vsCandidate2 = ''; vsCandidates = [];
  focusMunicipality = '';
  if (selFocus) { selFocus.innerHTML = '<option value="">All Precincts</option>'; }
  viewOpts.innerHTML = '';
  await populateTypeDropdown();
  selRace.innerHTML = '<option value="">Select Race…</option>';
  selRace.disabled = true;
  clearMap();
});

selFocus.addEventListener('change', () => {
  focusMunicipality = selFocus.value;
  render();
});
```

---

### Edit 14: Call `updateFocusOptions()` after `renderFinance()` completes successfully

**File:** index.html

**Find (exact text to match):**
```
    updateFinanceStats(financeData);
    updateFinanceLegend(financeData);
  } catch (err) {
    console.error('Finance render error:', err);
  } finally {
    popLoading();
  }
}
```

**Replace with:**
```
    updateFinanceStats(financeData);
    updateFinanceLegend(financeData);
    updateFocusOptions();
  } catch (err) {
    console.error('Finance render error:', err);
  } finally {
    popLoading();
  }
}
```

---

## Summary of Changes

| Edit | Location | What it does |
|------|----------|--------------|
| 1 | Line ~397 (after `vsCandidates`) | Adds `focusMunicipality` state variable |
| 2 | Line ~407 (DOM refs block) | Adds `selFocus` DOM reference |
| 3 | Line ~1132 (before `render()`) | Adds `lastFocusKey` tracker |
| 4 | Line ~262 (toolbar HTML) | Adds Focus separator, label, and `<select id="selFocus">` inside `#electionControls` |
| 5 | Line ~630–637 (Chicago loop in `loadGeoJSON`) | Sets `f._muni = 'CHICAGO'` for all Chicago features |
| 6 | Line ~640–647 (Suburban loop in `loadGeoJSON`) | Extracts municipality name via regex and sets `f._muni` |
| 7 | Line ~1038 (before `getStyle()`) | Adds `updateFocusOptions()` function that populates the dropdown from active race/finance data |
| 8 | Line ~1204 (inside `render()`) | Computes `focusedActiveFeats` / `focusedBgFeats`; updates `pidsChanged` to include focus changes |
| 9 | Line ~1220 (inside `render()`) | Uses `focusedBgFeats` and `focusedActiveFeats` for Leaflet layer creation |
| 10 | Line ~2150 (inside `renderFinance()`) | Same focus filter logic for finance render path |
| 11 | Line ~2164 (inside `renderFinance()`) | Uses focused feat arrays in finance Leaflet layer creation |
| 12 | Line ~1277 (`onRaceSelected()`) | Calls `updateFocusOptions()` after view opts update |
| 13 | Line ~1574 (`selElection` change handler) | Resets focus on election change; adds `selFocus` change event listener |
| 14 | Line ~2212 (end of `renderFinance()` try block) | Calls `updateFocusOptions()` after finance renders |

## Notes on Implementation

- **`_muni` for Chicago**: All Chicago precinct features get `_muni = 'CHICAGO'` (uppercase, consistent with the suburban naming convention where all names are uppercase).
- **`_muni` for Suburban**: The regex `/^([A-Z\s]+?)\s+\d/` extracts the municipality name before the first digit. E.g., `"EVANSTON 3-3"` → `"EVANSTON"`, `"NEW TRIER 5"` → `"NEW TRIER"`. The `?` makes it non-greedy so it stops at the first space+digit boundary.
- **Display name**: In the dropdown, `CHICAGO` is displayed as "Chicago" and suburban names (all caps) are title-cased by capitalizing first letter and lowercasing the rest (e.g. `"EVANSTON"` → `"Evanston"`).
- **Focus reset**: When the election changes, `focusMunicipality` is reset to `''` and the dropdown is cleared. The selection is preserved when switching races within the same election, but only if the municipality still has precincts in the new race data.
- **`pidsChanged` for fitBounds**: By comparing `focusMunicipality !== lastFocusKey`, switching the focus municipality triggers `fitBounds` on the filtered feature set, so the map zooms to the focused area.
- **Finance layer**: `updateFocusOptions()` checks `dataLayer === 'finance'` and uses the `financeMapCache` to determine active pids. It is called at the end of a successful `renderFinance()`.
- **Mobile**: The `selFocus` select element is inside `.toolbar-controls`, so the existing CSS rule `.toolbar-controls select{width:100%}` automatically makes it full-width on mobile — no additional CSS required.
- **`selFocus` DOM reference order**: `selFocus` is referenced via `$('selFocus')` after the element is defined in HTML and after the `$` helper is declared. Since the `<script>` block runs after the HTML is parsed, this is safe.
- **`dataLayer` variable**: `dataLayer` is declared later in the file (line ~1717). The `updateFocusOptions()` function references it but is only **called** after `dataLayer` is set up (from `onRaceSelected()` and `renderFinance()`), so there is no hoisting issue.
