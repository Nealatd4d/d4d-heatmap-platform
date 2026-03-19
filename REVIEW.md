# Critical Bugs

1. **Race-condition / stale-state risk across async UI changes.** `populateRaceDropdown()`, `onRaceSelected()`, and `render()` all await network work, but none use a request token or snapshot of the initiating state. If the user switches election, type, race, or mode quickly, an older async call can finish later and overwrite the newer selection with stale race options, stale comparison data, or a stale map render. This is most visible in `populateRaceDropdown()` (`417-466`), `onRaceSelected()` (`726-735`), the election/type/race change handlers (`905-948`), and `render()` (`630-723`).

2. **Candidate-mode deselection leaves stale colors on the map.** In `updateViewOpts()`, the candidate/swing dropdown change handler only calls `render()` when `selectedCandidate` is truthy (`530-531`). If the user switches back to the placeholder `Select Candidate…`, the map does not re-render, so the previous candidate shading remains visible even though no candidate is selected.

3. **Loader state is not concurrency-safe.** `render()` calls `showLoading(true)` and also triggers `fetchTurnout()` / `fetchRaceMap()`, which independently call `showLoading(true/false)` in `finally` blocks (`362-399`, `630-723`). With overlapping requests, one request can hide the loader while another is still in flight, producing misleading loading feedback and flicker.

4. **Errors are swallowed without UI recovery.** `render()` and `init()` catch errors and only log them to the console (`719-721`, `977-979`). The user gets no visible failure state, retry path, or explanatory message. Combined with the async race issues above, this can leave the app appearing idle or partially updated.

# Warnings

1. **Info-panel candidate colors can be inconsistent unless winner mode has already run.** `candidateColorMap` is only built inside winner-mode rendering (`664-667`), but `showInfo()` uses it in all modes (`770-779`). If the user opens candidate/vs/swing before ever visiting winner mode, colors fall back to `CANDIDATE_PALETTE[i]`, where `i` is the precinct-local rank order. Because candidates are sorted by votes within each precinct, the same candidate can appear with different swatch colors in different precincts.

2. **`swing` comparison can silently fail for valid cross-election matches.** The comparison race lookup requires exact `race_type` and exact `race_name` equality across elections (`651-659`). Any naming drift such as `District 5` vs `5th District`, runoff labels, or formatting differences will produce a full `No data` swing map even when a logical counterpart exists.

3. **`margin` mode assumes a one-candidate race should render as max margin.** When there is exactly one candidate, `getStyle()` assigns the top margin bucket (`576-577`). That may be acceptable for uncontested races, but it conflates “100-point margin because uncontested” with “40pp+ competitive landslide,” which may mislead users.

4. **`votes` mode mixes concepts in code, even if the current flow usually avoids it.** `getStyle()` uses `rd.totalVotes` when race data exists, otherwise `t.ballots` (`618-621`). Those are not always equivalent. Today the render path generally uses race precincts when a race is selected and blocks votes mode without a race, so the fallback is mostly dead, but the code still encodes two different metrics under one legend.

5. **No guards around GeoJSON fetch success or shape assumptions.** `loadGeoJSON()` directly does `fetch(...).then(r => r.json())` and assumes `chiRes.features` / `subRes.features` exist (`308-338`). A 404, bad JSON, or schema drift would throw and stop initialization.

6. **Potential precinct-ID mismatch risk is unvalidated.** The client computes MD5 IDs from GeoJSON properties (`186-199`, `317-335`) and trusts that they match the server-side IDs returned from RPCs. There is no instrumentation for unmatched IDs, so a formatting drift in `ward`, `precinct`, or `precinctid` would quietly drop precincts from the map.

7. **Rapid election/type changes can leave the race dropdown in a misleading state.** `populateRaceDropdown()` sets `selRace.disabled = true` at the top, but some early-return paths do not explicitly restore the correct disabled state after async completion (`417-466`). In practice this can combine with stale async completions and briefly show options for the wrong election/type.

8. **`bgLayer` context is based only on turnout presence, not geographic completeness.** Non-race precincts are shown as gray only when they also have turnout data (`678-681`). If turnout is missing for otherwise valid precinct geometry, those precincts disappear completely from context rather than appearing as gray/no-data geography.

# Suggestions

1. **Add a render generation token.** Increment a global `renderSeq` on every election/type/race/mode change, capture it at the start of `populateRaceDropdown()`, `onRaceSelected()`, and `render()`, and abort post-await DOM/layer updates when the token is stale.

2. **Deduplicate in-flight fetches in caches.** Store promises in `raceMapCache` / `turnoutCache` while requests are pending, not only resolved objects. That prevents duplicate RPCs when the same race/election is requested multiple times during rapid interaction.

3. **Separate loader state from request helpers.** Use either a reference-counted loader or keep loading control only in top-level flows like `render()` / `init()`. Nested helpers should not independently hide the loader.

4. **Avoid full layer rebuilds for pure style changes.** Mode changes such as turnout/winner/margin/candidate/vs/swing/votes often only need new styles. Reusing the existing `precinctLayer` and calling `setStyle()` would reduce garbage creation and repeated GeoJSON parsing work on large files.

5. **Avoid O(n) restyling on every hover.** `mouseover` and `mouseout` call `precinctLayer.eachLayer(...)` across all active precincts (`698-707`). On large datasets this will feel heavy. Track the previously hovered layer and only reset that one.

6. **Do not auto-fit bounds on every render.** `fitBounds()` runs after every mode/candidate/view change (`712-713`), which can feel jumpy and expensive. Fit only on initial race selection or when the active precinct set changes materially.

7. **Build a stable candidate color map whenever race data loads, not only in winner mode.** That will make the info panel and any future legends consistent across all modes.

8. **Let deselection re-render.** In candidate/swing controls, always call `render()` on change, including when the placeholder option is chosen.

9. **Consider validating and logging unmatched precinct IDs.** After loading turnout/race data, compare returned precinct IDs against `pidToFeatureIdx` and log counts of unmatched rows. That will catch subtle MD5/input-format drift quickly.

10. **Surface user-visible errors.** A small banner or status line for failed data loads would make debugging and production support much easier than relying on the console.

11. **Security posture is acceptable for a public reader, with standard caveats.** Keeping the Supabase anon key in the frontend is normal for public read-only access. The real controls must remain in RLS / RPC authorization, and only intended functions should be exposed. Rate limiting and monitoring are still worth adding because the key allows anyone to call those public endpoints.

# Overall Assessment

The file is generally well organized and readable, and the main data flow is straightforward. The biggest weakness is **state management under rapid interaction**: async responses can arrive out of order, loader behavior is not request-safe, and some UI controls can leave stale visual state behind. Data rendering logic for the eight modes is mostly sensible, but there are a few correctness risks around candidate color consistency, swing race matching, and the semantics of one-candidate margins. Performance is likely acceptable for moderate usage because RPC results are cached, but large GeoJSON layers will pay unnecessary costs from full layer rebuilds, repeated full-dataset filtering, all-layer hover restyling, and repeated `fitBounds()` calls.

**Bottom line:** not a rewrite, but it does need a pass focused on async state guards, loader discipline, and lighter-weight rendering before I would consider it robust for production-heavy use.