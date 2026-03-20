# PNG Export Feature — Patch for index.html

This patch describes all edits required to add the PNG Export feature to `index.html`.
Apply edits in order (Edit 1 → Edit 7).

---

### Edit 1: Add html-to-image library
**File:** index.html
**Find (exact text to match):**
```
<script src="https://cdn.jsdelivr.net/npm/spark-md5@3.0.2/spark-md5.min.js"></script>
```
**Replace with:**
```
<script src="https://cdn.jsdelivr.net/npm/spark-md5@3.0.2/spark-md5.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js"></script>
```

---

### Edit 2: Add CSS for export button and title overlay
**File:** index.html
**Find (exact text to match):**
```
  .finance-controls select{width:100%;min-width:unset;font-size:13px;padding:8px 28px 8px 10px}
}

</style>
```
**Replace with:**
```
  .finance-controls select{width:100%;min-width:unset;font-size:13px;padding:8px 28px 8px 10px}
  .export-btn{width:100%;justify-content:center;padding:10px;font-size:13px}
}

/* Export PNG button */
.export-btn{background:var(--surface-alt);border:1px solid var(--border);color:var(--text-muted);border-radius:4px;padding:5px 10px;cursor:pointer;display:flex;align-items:center;gap:5px;font-size:11px;font-family:inherit;transition:all .15s;white-space:nowrap}
.export-btn:hover{border-color:var(--blue-dim);color:var(--blue);background:var(--surface-hover)}
.export-btn svg{width:14px;height:14px;flex-shrink:0}

/* Export title overlay (temporarily shown during capture) */
.export-title-overlay{position:absolute;top:0;left:0;right:0;z-index:850;background:rgba(15,17,23,0.92);padding:16px 20px;pointer-events:none;display:none}
.export-title-overlay.visible{display:block}
.export-title-overlay h2{font-size:16px;font-weight:700;color:#e8eaed;margin:0 0 4px 0;letter-spacing:-0.01em}
.export-title-overlay .export-subtitle{font-size:12px;color:#9aa0a6;margin:0}
.export-title-overlay .export-branding{font-size:9px;color:#6b7280;margin-top:6px;letter-spacing:.03em}

</style>
```

---

### Edit 3: Add export button in the toolbar
**File:** index.html
**Find (exact text to match):**
```
          <button class="mode-btn" data-fmode="votes">Total $</button>
        </div>
      </div>
    </div>
  </div>
```
**Replace with:**
```
          <button class="mode-btn" data-fmode="votes">Total $</button>
        </div>
      </div>
      <div class="toolbar-sep"></div>
      <button class="export-btn" onclick="exportPNG()" title="Export current view as PNG">
        <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 2v8M8 10L5 7M8 10l3-3M3 12h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Export PNG
      </button>
    </div>
  </div>
```

---

### Edit 4: Add export title overlay div in map-wrap
**File:** index.html
**Find (exact text to match):**
```
  <div class="map-wrap">
    <div id="map"></div>
    <div class="loading-indicator" id="loader"><div class="spinner"></div><span>Loading…</span></div>
    <div class="landing-overlay" id="landing">
      <h2>Select a Race</h2>
      <p>Choose an election, district type, and race from the toolbar to view precinct-level data.</p>
    </div>
    <div class="info-panel" id="infoPanel"></div>
    <div class="legend" id="legend"></div>
  </div>
```
**Replace with:**
```
  <div class="map-wrap">
    <div id="map"></div>
    <div class="loading-indicator" id="loader"><div class="spinner"></div><span>Loading…</span></div>
    <div class="landing-overlay" id="landing">
      <h2>Select a Race</h2>
      <p>Choose an election, district type, and race from the toolbar to view precinct-level data.</p>
    </div>
    <div class="export-title-overlay" id="exportTitle"></div>
    <div class="info-panel" id="infoPanel"></div>
    <div class="legend" id="legend"></div>
  </div>
```

---

### Edit 5: Add exportPNG() function inside the IIFE
**File:** index.html
**Find (exact text to match):**
```
// Finance mode buttons
document.querySelectorAll('#financeModes .mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#financeModes .mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFinanceMode = btn.dataset.fmode;
    updateFinanceControlVisibility();
    renderFinance();
  });
});

})();
```
**Replace with:**
```
// Finance mode buttons
document.querySelectorAll('#financeModes .mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#financeModes .mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFinanceMode = btn.dataset.fmode;
    updateFinanceControlVisibility();
    renderFinance();
  });
});

/* ═══════════════════ PNG EXPORT ═══════════════════ */
async function exportPNG() {
  if (!precinctLayer) { alert('Load a race first'); return; }

  const mapWrap = document.querySelector('.map-wrap');
  const exportTitle = $('exportTitle');

  // Build title text from current state
  let title = '';
  let subtitle = '';

  if (dataLayer === 'election') {
    // Get election name
    const elOpt = selElection.options[selElection.selectedIndex];
    const elName = elOpt ? elOpt.textContent : '';

    // Get race name
    const raceOpt = selRace.options[selRace.selectedIndex];
    const raceName = raceOpt && raceOpt.value ? raceOpt.textContent : '';

    // Get mode name
    const modeBtn = document.querySelector('#electionModes .mode-btn.active');
    const modeName = modeBtn ? modeBtn.textContent : '';

    // Get candidate name if in candidate mode
    let candInfo = '';
    if (currentMode === 'candidate' && selectedCandidate) {
      candInfo = ` · ${selectedCandidate}`;
    } else if (currentMode === 'vs' && vsCandidates.length >= 2) {
      candInfo = ` · ${vsCandidates.join(' vs ')}`;
    }

    title = raceName || elName;
    subtitle = `${elName}${raceName ? '' : ''} · ${modeName}${candInfo}`;
  } else {
    // Finance layer
    const fElOpt = selFinanceElection ? selFinanceElection.options[selFinanceElection.selectedIndex] : null;
    const fElName = fElOpt ? fElOpt.textContent : '';
    const commOpt = selCommitteeA ? selCommitteeA.options[selCommitteeA.selectedIndex] : null;
    const commName = commOpt && commOpt.value ? commOpt.textContent : '';
    const fModeBtn = document.querySelector('#financeModes .mode-btn.active');
    const fModeName = fModeBtn ? fModeBtn.textContent : '';

    title = commName || 'Campaign Finance';
    subtitle = `${fElName} · ${fModeName}`;
  }

  // Add focus municipality to subtitle if active
  if (typeof focusMunicipality !== 'undefined' && focusMunicipality) {
    const muniTitle = focusMunicipality.charAt(0) + focusMunicipality.slice(1).toLowerCase();
    subtitle += ` · ${muniTitle}`;
  }

  // Show title overlay
  exportTitle.innerHTML = `<h2>${title}</h2><p class="export-subtitle">${subtitle}</p><p class="export-branding">D4D Election Heatmap Platform · digital4dems.com</p>`;
  exportTitle.classList.add('visible');

  // Hide UI elements that shouldn't be in the export
  const hideEls = [
    document.querySelector('.leaflet-control-zoom'),
    $('infoPanel'),
  ];
  const origDisplay = hideEls.map(el => el ? el.style.display : '');
  hideEls.forEach(el => { if (el) el.style.display = 'none'; });

  // Make legend fully visible (not pointer-events:none) for capture
  const legend = $('legend');

  try {
    // Small delay to let DOM settle
    await new Promise(r => setTimeout(r, 200));

    const dataUrl = await htmlToImage.toPng(mapWrap, {
      backgroundColor: '#0f1117',
      pixelRatio: 2, // 2x for crisp exports
      filter: (node) => {
        // Filter out the loading indicator
        if (node.id === 'loader') return false;
        if (node.id === 'landing') return false;
        return true;
      }
    });

    // Trigger download
    const link = document.createElement('a');
    const safeName = (title + '_' + subtitle).replace(/[^a-zA-Z0-9]+/g, '_').replace(/_+/g, '_').substring(0, 80);
    link.download = `d4d_heatmap_${safeName}.png`;
    link.href = dataUrl;
    link.click();

  } catch (err) {
    console.error('Export failed:', err);
    alert('Export failed: ' + err.message);
  } finally {
    // Restore hidden elements
    hideEls.forEach((el, i) => { if (el) el.style.display = origDisplay[i]; });
    exportTitle.classList.remove('visible');
  }
}

})();
```

---

### Edit 6: Expose exportPNG globally for onclick handler
**File:** index.html
**Find (exact text to match):**
```
window.setDataLayer = setDataLayer;
```
**Replace with:**
```
window.setDataLayer = setDataLayer;
window.exportPNG = exportPNG;
```

---

## Notes

- **`financeLayer` does not exist** in the current codebase. The guard condition in `exportPNG()` checks only `precinctLayer`. The finance render path uses `precinctLayer` as well (same variable), so this single check covers both data layers.
- **`focusMunicipality`** is not yet present in `index.html` — the `typeof` guard ensures the export function works both before and after the Municipality Focus patch (Edit 1 in `focus_patch.md`) is applied.
- **Mobile CSS** for `.export-btn` is included inline in Edit 2 (inside the `@media(max-width:768px)` block that already exists), rather than as a separate edit, to keep the mobile rules co-located with all other mobile overrides.
- **Edit order matters**: Apply Edit 2 before Edit 3, and Edit 5 before Edit 6. The rest are independent.
- The `htmlToImage` global is the correct name exposed by the html-to-image CDN UMD build (`window.htmlToImage`).
