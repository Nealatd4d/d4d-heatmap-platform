"""
Step 4: Load aggregated finance data into Supabase.
All tables use upsert (ON CONFLICT) for idempotent re-loads.
"""

import csv, json, ssl, urllib.request
from finance_config import (
    SUPA_URL, SUPA_KEY,
    FINANCE_ELECTIONS, COMMITTEES,
    CONTRIBUTIONS_CSV, GEOCODED_CSV, SUMMARY_CSV, RACE_SUMMARY_CSV
)


def supa_post(table, rows, upsert_cols=None):
    """POST rows to Supabase REST API."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"{SUPA_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" if upsert_cols else "return=minimal",
    }

    # Batch in chunks of 500
    BATCH = 500
    total = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        data = json.dumps(batch).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                resp.read()
            total += len(batch)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  Error loading {table} batch {i//BATCH}: {e.code} {body[:300]}")
            raise

    return total


def supa_rpc(fn, params=None):
    """Call Supabase RPC function."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"{SUPA_URL}/rest/v1/rpc/{fn}"
    data = json.dumps(params or {}).encode("utf-8")
    headers = {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read())


def load_finance_elections():
    """Seed finance_elections table."""
    rows = []
    for eid, cfg in FINANCE_ELECTIONS.items():
        rows.append({
            "id": eid,
            "name": cfg["name"],
            "race_label": cfg["race_label"],
            "year": cfg["year"],
            "type": cfg["type"],
            "cycle_start": cfg["cycle_start"],
            "cycle_end": cfg["cycle_end"],
        })
    n = supa_post("finance_elections", rows, upsert_cols=["id"])
    print(f"  finance_elections: {n} rows loaded")
    return n


def load_finance_committees():
    """Seed finance_committees table."""
    rows = []
    for cid, cfg in COMMITTEES.items():
        rows.append({
            "id": cid,
            "sbe_id": cfg["sbe_id"],
            "committee_name": cfg["committee_name"],
            "candidate_name": cfg["candidate_name"],
            "party": cfg["party"],
            "status": cfg["status"],
        })
    n = supa_post("finance_committees", rows, upsert_cols=["id"])
    print(f"  finance_committees: {n} rows loaded")
    return n


def load_contributions():
    """Load geocoded contributions to finance_contributions."""
    rows = []
    with open(GEOCODED_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row.get("amount", 0))
            if amount <= 0:
                continue

            # Parse lat/lng
            lat = None
            lng = None
            if row.get("latitude"):
                try:
                    lat = float(row["latitude"])
                except (ValueError, TypeError):
                    pass
            if row.get("longitude"):
                try:
                    lng = float(row["longitude"])
                except (ValueError, TypeError):
                    pass

            # Fix date format for Postgres
            rcv = row.get("receipt_date", "")
            if rcv and "/" in rcv:
                parts = rcv.split("/")
                if len(parts) == 3:
                    m, d, y = parts
                    if len(y) == 2:
                        y = "20" + y if int(y) < 50 else "19" + y
                    rcv = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

            # All rows must have the SAME keys for Supabase bulk insert
            entry = {
                "finance_election_id": row["finance_election_id"],
                "committee_id": row["committee_id"],
                "donor_name": row.get("donor_name", ""),
                "donor_address": row.get("donor_address", ""),
                "donor_city": row.get("donor_city", ""),
                "donor_state": row.get("donor_state", ""),
                "donor_zip": row.get("donor_zip", ""),
                "amount": amount,
                "receipt_date": rcv,
                "sbe_receipt_id": row.get("sbe_receipt_id", ""),
                "geocode_status": row.get("geocode_status", "pending"),
                "precinct_id": row.get("precinct_id") or None,
                "latitude": lat,
                "longitude": lng,
            }

            rows.append(entry)

    n = supa_post("finance_contributions", rows, upsert_cols=["sbe_receipt_id"])
    print(f"  finance_contributions: {n} rows loaded")
    return n


def load_precinct_summary():
    """Load precinct summary data."""
    rows = []
    with open(SUMMARY_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "finance_election_id": row["finance_election_id"],
                "committee_id": row["committee_id"],
                "precinct_id": row["precinct_id"],
                "total_dollars": float(row["total_dollars"]),
                "donor_count": int(row["donor_count"]),
                "avg_donation": float(row["avg_donation"]),
                "max_donation": float(row["max_donation"]),
            })

    n = supa_post("finance_precinct_summary", rows, upsert_cols=["finance_election_id", "committee_id", "precinct_id"])
    print(f"  finance_precinct_summary: {n} rows loaded")
    return n


def load_race_summary():
    """Load race-level summary data."""
    rows = []
    with open(RACE_SUMMARY_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "finance_election_id": row["finance_election_id"],
                "precinct_id": row["precinct_id"],
                "total_dollars": float(row["total_dollars"]),
                "total_donors": int(row["total_donors"]),
                "top_committee_id": row["top_committee_id"],
                "dollar_margin": float(row["dollar_margin"]),
                "donor_margin": float(row["donor_margin"]),
            })

    n = supa_post("finance_precinct_race_summary", rows, upsert_cols=["finance_election_id", "precinct_id"])
    print(f"  finance_precinct_race_summary: {n} rows loaded")
    return n


def refresh_materialized_view():
    """Refresh the pre-joined materialized view."""
    import subprocess
    result = subprocess.run(
        ["psql", SUPA_URL.replace("https://", "postgresql://postgres:@") + ":5432/postgres"],
        input="REFRESH MATERIALIZED VIEW mv_finance_precinct;",
        capture_output=True, text=True
    )
    # Use direct PG connection instead
    from finance_config import PG_CONN
    import os
    env = os.environ.copy()
    env["PGPASSWORD"] = "D4dHeatmap2026!Pg"
    result = subprocess.run(
        ["psql", PG_CONN, "-c", "REFRESH MATERIALIZED VIEW mv_finance_precinct;"],
        capture_output=True, text=True, env=env
    )
    if result.returncode == 0:
        print("  Materialized view refreshed")
    else:
        print(f"  MV refresh warning: {result.stderr}")


def load_all():
    """Load everything in dependency order."""
    print("Loading finance data to Supabase...")

    # 1. Reference tables
    load_finance_elections()
    load_finance_committees()

    # 2. Fact table
    load_contributions()

    # 3. Summary tables
    load_precinct_summary()
    load_race_summary()

    # 4. Refresh MV
    refresh_materialized_view()

    print("\nDone! All finance data loaded.")


if __name__ == "__main__":
    load_all()
