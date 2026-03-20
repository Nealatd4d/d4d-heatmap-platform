"""
Step 2: Geocode donor addresses → assign to precincts via point-in-polygon.

Strategy:
1. Deduplicate addresses to minimize geocoding calls
2. Use Census Bureau batch geocoder (free, handles IL addresses well)
3. Point-in-polygon against our GeoJSON precincts
4. Compute MD5 precinct_id matching the frontend's SparkMD5 logic
"""

import os, csv, json, hashlib, time, ssl, math
import urllib.request, urllib.parse
from collections import defaultdict

from finance_config import (
    CONTRIBUTIONS_CSV, GEOCODED_CSV, DATA_DIR,
    GEOJSON_CHICAGO, GEOJSON_SUBURBAN
)


def md5_16(s):
    """Same as frontend: MD5(input.lower())[:16]"""
    return hashlib.md5(s.lower().encode()).hexdigest()[:16]


def chicago_precinct_id(ward, precinct):
    """Match frontend: makeId('chicago', `Ward ${pad2(ward)} Precinct ${pad2(precinct)}`)"""
    name = f"Ward {str(ward).zfill(2)} Precinct {str(precinct).zfill(2)}"
    return md5_16(f"chicago|{name}")


def suburban_precinct_id(precinctid):
    """Match frontend: makeId('cook_suburban', precinctid)"""
    return md5_16(f"cook_suburban|{precinctid}")


def load_geojson_polygons():
    """Load GeoJSON features and build polygon lookup structures."""
    print("Loading GeoJSON precinct boundaries...")
    polygons = []

    # Chicago precincts
    if os.path.exists(GEOJSON_CHICAGO):
        with open(GEOJSON_CHICAGO) as f:
            chicago = json.load(f)
        for feat in chicago["features"]:
            props = feat.get("properties", {})
            ward = props.get("ward", props.get("WARD", ""))
            precinct = props.get("precinct", props.get("PRECINCT", ""))
            if ward and precinct:
                pid = chicago_precinct_id(ward, precinct)
                polygons.append({
                    "pid": pid,
                    "geometry": feat["geometry"],
                    "bbox": compute_bbox(feat["geometry"]),
                    "jurisdiction": "chicago"
                })

    # Suburban precincts
    if os.path.exists(GEOJSON_SUBURBAN):
        with open(GEOJSON_SUBURBAN) as f:
            suburban = json.load(f)
        for feat in suburban["features"]:
            props = feat.get("properties", {})
            precinctid = props.get("PRECINCTID", props.get("precinctid", ""))
            if precinctid:
                pid = suburban_precinct_id(precinctid)
                polygons.append({
                    "pid": pid,
                    "geometry": feat["geometry"],
                    "bbox": compute_bbox(feat["geometry"]),
                    "jurisdiction": "suburban"
                })

    print(f"  Loaded {len(polygons)} precinct polygons")
    return polygons


def compute_bbox(geometry):
    """Compute bounding box [min_lng, min_lat, max_lng, max_lat] for a GeoJSON geometry."""
    coords = extract_all_coords(geometry)
    if not coords:
        return None
    lngs = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [min(lngs), min(lats), max(lngs), max(lats)]


def extract_all_coords(geometry):
    """Extract all coordinate pairs from a GeoJSON geometry."""
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates", [])

    if gtype == "Polygon":
        return [c for ring in coords for c in ring]
    elif gtype == "MultiPolygon":
        return [c for poly in coords for ring in poly for c in ring]
    return []


def point_in_polygon(lng, lat, geometry):
    """Test if a point is inside a GeoJSON polygon using ray casting."""
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates", [])

    if gtype == "Polygon":
        return _point_in_rings(lng, lat, coords)
    elif gtype == "MultiPolygon":
        for poly in coords:
            if _point_in_rings(lng, lat, poly):
                return True
    return False


def _point_in_rings(lng, lat, rings):
    """Ray casting for polygon with holes."""
    if not rings:
        return False
    # Must be inside outer ring
    if not _ray_cast(lng, lat, rings[0]):
        return False
    # Must NOT be inside any hole
    for hole in rings[1:]:
        if _ray_cast(lng, lat, hole):
            return False
    return True


def _ray_cast(px, py, ring):
    """Ray casting algorithm for point-in-polygon."""
    n = len(ring)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def geocode_batch_census(addresses):
    """
    Batch geocode via US Census Bureau geocoder.
    Accepts list of (id, address, city, state, zip) tuples.
    Returns dict: id → (lat, lng) or id → None
    """
    results = {}
    # Census batch geocoder accepts up to 10,000 at a time via CSV upload
    BATCH_SIZE = 1000

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for batch_start in range(0, len(addresses), BATCH_SIZE):
        batch = addresses[batch_start:batch_start + BATCH_SIZE]

        # Create CSV for batch
        csv_lines = []
        for uid, addr, city, state, zipcode in batch:
            # Clean fields
            addr_clean = addr.replace(",", " ").replace("\t", " ").strip()
            city_clean = city.replace(",", " ").strip()
            state_clean = state.strip()
            zip_clean = zipcode.strip()[:5]
            csv_lines.append(f"{uid},{addr_clean},{city_clean},{state_clean},{zip_clean}")

        csv_content = "\n".join(csv_lines)

        # Submit to Census batch geocoder
        url = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
        boundary = "----FormBoundary" + str(int(time.time()))
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="addressFile"; filename="addresses.csv"\r\n'
            f"Content-Type: text/csv\r\n\r\n"
            f"{csv_content}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="benchmark"\r\n\r\n'
            f"Public_AR_Current\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="vintage"\r\n\r\n'
            f"Current_Current\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "D4D-Finance-Pipeline/1.0"
        })

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                response_text = resp.read().decode("utf-8", errors="replace")

            for line in response_text.strip().split("\n"):
                if not line.strip():
                    continue
                # Parse Census response: "id","input_addr","match_status","match_type","matched_addr","coords","tiger_id","side"
                parts = line.split('","')
                if len(parts) < 6:
                    parts = line.replace('"', '').split(",")

                uid = parts[0].strip().strip('"')
                # Look for coordinates in the response
                for part in parts:
                    part = part.strip().strip('"')
                    if "," in part:
                        try:
                            # Census returns lng,lat
                            coords = part.split(",")
                            if len(coords) == 2:
                                lng = float(coords[0].strip())
                                lat = float(coords[1].strip())
                                if -180 <= lng <= 0 and 30 <= lat <= 50:  # Reasonable US coords
                                    results[uid] = (lat, lng)
                                    break
                        except ValueError:
                            continue

            print(f"    Census batch {batch_start//BATCH_SIZE + 1}: {len([r for r in batch if str(batch.index(r)) in results or batch[batch.index(r)][0] in results])}/{len(batch)} geocoded")

        except Exception as e:
            print(f"    Census batch geocode error: {e}")

        # Rate limiting
        time.sleep(1)

    return results


def geocode_single_nominatim(address, city, state, zipcode):
    """Fallback: single address via Nominatim (OpenStreetMap)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    query = f"{address}, {city}, {state} {zipcode}"
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1&countrycodes=us"

    req = urllib.request.Request(url, headers={"User-Agent": "D4D-Finance-Pipeline/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def geocode_contributions():
    """Main geocoding flow: deduplicate → batch geocode → point-in-polygon."""

    # Load contributions
    contributions = []
    with open(CONTRIBUTIONS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contributions.append(row)

    print(f"Loaded {len(contributions)} contributions to geocode")

    # Deduplicate addresses
    addr_map = {}  # normalized_addr → list of contribution indices
    for i, c in enumerate(contributions):
        addr = c.get("donor_address", "").strip()
        city = c.get("donor_city", "").strip()
        state = c.get("donor_state", "").strip()
        zipcode = c.get("donor_zip", "").strip()[:5]

        if not addr or not city:
            contributions[i]["geocode_status"] = "missing_address"
            continue

        # Only geocode IL addresses (HD-18 is in Cook County / north suburbs)
        if state and state.upper() not in ("IL", "ILLINOIS", ""):
            contributions[i]["geocode_status"] = "out_of_area"
            continue

        key = f"{addr}|{city}|{state}|{zipcode}".lower()
        if key not in addr_map:
            addr_map[key] = []
        addr_map[key].append(i)

    unique_addrs = list(addr_map.keys())
    print(f"Unique addresses to geocode: {len(unique_addrs)}")

    # Prepare batch for Census geocoder
    batch_input = []
    for uid_idx, key in enumerate(unique_addrs):
        parts = key.split("|")
        batch_input.append((str(uid_idx), parts[0], parts[1], parts[2] or "IL", parts[3]))

    # Geocode via Census
    print("Geocoding via Census Bureau batch geocoder...")
    geocode_results = geocode_batch_census(batch_input)

    # Map results back
    geocoded_count = 0
    for uid_idx, key in enumerate(unique_addrs):
        uid = str(uid_idx)
        if uid in geocode_results:
            lat, lng = geocode_results[uid]
            for ci in addr_map[key]:
                contributions[ci]["latitude"] = lat
                contributions[ci]["longitude"] = lng
                contributions[ci]["geocode_status"] = "geocoded"
            geocoded_count += 1

    print(f"Census geocoded: {geocoded_count}/{len(unique_addrs)} unique addresses")

    # Fallback: Nominatim for remaining (limit to avoid rate limits)
    remaining = [(i, k) for i, k in enumerate(unique_addrs)
                 if str(i) not in geocode_results]
    if remaining:
        print(f"Trying Nominatim for {min(len(remaining), 200)} remaining addresses...")
        for idx, (uid_idx, key) in enumerate(remaining[:200]):
            parts = key.split("|")
            result = geocode_single_nominatim(parts[0], parts[1], parts[2] or "IL", parts[3])
            if result:
                lat, lng = result
                for ci in addr_map[key]:
                    contributions[ci]["latitude"] = lat
                    contributions[ci]["longitude"] = lng
                    contributions[ci]["geocode_status"] = "geocoded"
                geocoded_count += 1
            time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
            if (idx + 1) % 50 == 0:
                print(f"    Nominatim: {idx+1}/{min(len(remaining), 200)}")

    print(f"Total geocoded: {geocoded_count}/{len(unique_addrs)} unique addresses")

    # Point-in-polygon: assign precincts
    polygons = load_geojson_polygons()
    print("Running point-in-polygon assignment...")

    pip_matched = 0
    for i, c in enumerate(contributions):
        if c.get("geocode_status") != "geocoded":
            continue

        lat = float(c["latitude"])
        lng = float(c["longitude"])

        # Find precinct
        matched_pid = None
        for poly in polygons:
            bbox = poly["bbox"]
            if bbox and bbox[0] <= lng <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                if point_in_polygon(lng, lat, poly["geometry"]):
                    matched_pid = poly["pid"]
                    break

        if matched_pid:
            contributions[i]["precinct_id"] = matched_pid
            contributions[i]["geocode_status"] = "matched"
            pip_matched += 1
        else:
            contributions[i]["geocode_status"] = "no_precinct_match"

    print(f"Point-in-polygon matches: {pip_matched}/{sum(1 for c in contributions if c.get('geocode_status') in ('geocoded', 'matched', 'no_precinct_match'))}")

    # Write geocoded CSV
    fieldnames = [
        "sbe_receipt_id", "committee_id", "finance_election_id",
        "donor_name", "donor_address", "donor_city", "donor_state", "donor_zip",
        "amount", "receipt_date", "occupation", "employer", "d2_part",
        "latitude", "longitude", "geocode_status", "precinct_id"
    ]
    with open(GEOCODED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for c in contributions:
            writer.writerow(c)

    print(f"Output: {GEOCODED_CSV}")

    # Stats
    status_counts = defaultdict(int)
    for c in contributions:
        status_counts[c.get("geocode_status", "unknown")] += 1
    print("\nGeocoding stats:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    return pip_matched


if __name__ == "__main__":
    geocode_contributions()
