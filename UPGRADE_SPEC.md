# Upgrade Spec: Mobile Redesign + Multi-Candidate Visualization

## 1. Multi-Candidate "Vs" Mode Fix

### Problem
The current "Vs" mode only lets you compare 2 candidates. For races with 3-5 candidates (e.g., 9th Congressional District primary), this is insufficient.

### Solution: Two new/enhanced view modes

#### A) Winner Color Map (enhance existing "Winner" mode)
- Already works with multi-candidate — each candidate gets a unique color from CANDIDATE_PALETTE
- **Enhancement**: Add intensity/opacity based on margin of victory
  - Landslide (>20pp margin): full opacity 0.9
  - Clear win (10-20pp): opacity 0.8  
  - Competitive (<10pp): opacity 0.65
  - This makes it visually obvious where races were close vs blowouts

#### B) Single-Candidate Focus (enhance existing "Candidate" mode)  
- Already exists as "Candidate" mode with a dropdown
- This already works for multi-candidate races
- **No changes needed** — it already lets you pick any candidate and see their vote share across precincts

#### C) Fix "Vs" Mode for 3+ Candidates
- Current: Only shows two dropdowns, auto-selects candidates[0] and candidates[1]
- **Fix**: This is actually fine — "Vs" means comparing any 2 of the N candidates. The user picks which 2 to compare. The dropdowns already list all candidates.
- **The real issue**: The "Vs" button may be hidden/disabled when there are 3+ candidates. Check and fix this.
- Actually looking at the code, the Vs mode works fine with any number of candidates — it just shows 2 dropdowns and the user picks. No code fix needed.

### Actual Problem Found
The Vs mode currently works correctly for multi-candidate races. The user may have been confused because:
1. You must select a race first before Vs dropdowns appear
2. The mode-btn for "Vs" is always visible but view opts only populate when a race is selected

No code changes needed for Vs mode logic — it already handles N candidates.

## 2. Mobile Redesign

### Breakpoints
- **Mobile**: < 768px (phones)
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px (current design, mostly unchanged)

### Mobile Layout (< 768px)

#### Collapsible Toolbar
- Show a compact top bar with: D4D logo + current election name + filter icon (☰ or funnel)
- Tap filter icon → toolbar slides down revealing:
  - Election dropdown (full width)
  - Type dropdown (full width)
  - Race dropdown (full width)
  - View mode buttons (wrapped, 2 rows)
  - View options (candidate selectors etc)
- Tap filter icon again or tap map → collapse toolbar
- Stats bar: show below the compact top bar, horizontal scroll if needed
  - Registered | Ballots | Turnout% | Winner
  
#### Map Area
- Takes all remaining vertical space
- Touch interactions:
  - Tap precinct → opens bottom sheet (NOT hover popup)
  - Pinch to zoom works naturally with Leaflet
  - Pan works naturally
  
#### Bottom Sheet (Precinct Info)
- Replaces the hover info-panel on mobile
- On tap, sheet slides up from bottom covering ~40% of screen
- Contains all the same info: precinct name, registered, ballots, turnout, candidate bars
- Has a drag handle at top — can drag up to ~70% or down to dismiss
- Tap outside (on map) to dismiss
- Semi-transparent backdrop NOT needed (map still visible above)

#### Legend
- Move to bottom-left, smaller font
- Or: put inside the bottom sheet as a collapsible section
- Decision: Keep as small overlay bottom-left but make it collapsible (tap to expand/collapse)

#### Footer
- Hide on mobile (save vertical space). Data attribution can go in a settings/about panel.

### Tablet Layout (768px - 1024px)
- Similar to desktop but:
  - Toolbar wraps to 2 lines if needed (already does with flex-wrap)
  - Info panel slightly smaller
  - Stats bar: may need to wrap or reduce font sizes
  - Essentially the current responsive design but tuned

### Desktop Layout (> 1024px)
- Current design unchanged
- Hover interactions stay (mouseover/mouseout)

## 3. Implementation Details

### Touch vs Mouse Detection
```javascript
const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
```
Or better: use both event types but handle them differently:
- On touch devices: tap = select precinct → show bottom sheet
- On desktop: hover = show info panel (existing behavior)

### Bottom Sheet Implementation
Use CSS transforms for smooth sliding:
```css
.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-radius: 12px 12px 0 0;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  z-index: 1100;
  max-height: 70vh;
  overflow-y: auto;
}
.bottom-sheet.open {
  transform: translateY(0);
}
```

### Collapsible Toolbar
```css
.toolbar-mobile {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.toolbar-mobile.expanded {
  max-height: 400px;
}
```

### Key CSS Changes
- All existing styles remain for desktop
- Add media queries for mobile/tablet
- Use `display: none` / `display: flex` to swap between desktop info-panel and mobile bottom-sheet
- Header becomes compact on mobile with hamburger/filter toggle

### Touch Interaction Changes
In the Leaflet onEachFeature:
- Desktop: keep mouseover/mouseout → info-panel
- Mobile: use 'click' event → open bottom sheet with precinct data
- Remove `mouseout` hiding on mobile (that's what causes "precincts don't stay up and disappear instantly")

```javascript
onEachFeature: (f, l) => {
  if (isMobile) {
    l.on('click', (e) => {
      L.DomEvent.stopPropagation(e);
      // Highlight this precinct
      if (hoveredLayer) hoveredLayer.setStyle({ color: '#1a1d27', weight: 1 });
      hoveredLayer = l;
      l.setStyle({ color: '#fff', weight: 2.5 });
      l.bringToFront();
      openBottomSheet(f, turnout, raceData, turnout2, raceData2);
    });
  } else {
    l.on('mouseover', () => { ... existing ... });
    l.on('mouseout', () => { ... existing ... });
  }
}
```

## 4. Winner Mode Enhancement for Multi-Candidate

Update the "winner" style to include margin-based intensity:
```javascript
} else if (currentMode === 'winner') {
  if (rd && rd.candidates && rd.candidates.length) {
    const winner = rd.candidates[0].n;
    fill = candidateColorMap[winner] || CANDIDATE_PALETTE[0];
    // Intensity based on margin
    if (rd.candidates.length >= 2) {
      const margin = rd.candidates[0].p - rd.candidates[1].p;
      if (margin >= 20) fillOpacity = 0.9;
      else if (margin >= 10) fillOpacity = 0.8;
      else fillOpacity = 0.65;
    }
  }
}
```

## 5. File Structure
- Keep everything in single index.html (current pattern)
- All CSS in the <style> block
- All JS in the <script> block
