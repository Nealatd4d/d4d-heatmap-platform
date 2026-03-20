"""
Step 3: Aggregate geocoded contributions into precinct-level summaries.
Produces:
  - finance_precinct_summary: per (precinct, election, committee)
  - finance_precinct_race_summary: cross-candidate metrics per (precinct, election)
"""

import csv
from collections import defaultdict
from finance_config import GEOCODED_CSV, SUMMARY_CSV, RACE_SUMMARY_CSV, COMMITTEES


def aggregate():
    """Build precinct summaries from geocoded contributions."""

    # Load geocoded contributions (only those with precinct matches)
    contributions = []
    with open(GEOCODED_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("geocode_status") == "matched" and row.get("precinct_id"):
                contributions.append(row)

    print(f"Aggregating {len(contributions)} precinct-matched contributions")

    # ── Build precinct_summary ──
    # Key: (election_id, committee_id, precinct_id) → {total_dollars, donor_count, max_donation, donors_set}
    summary = defaultdict(lambda: {"total_dollars": 0.0, "donor_count": 0, "max_donation": 0.0, "donors": set()})

    for c in contributions:
        key = (c["finance_election_id"], c["committee_id"], c["precinct_id"])
        amt = float(c["amount"])
        summary[key]["total_dollars"] += amt
        summary[key]["donors"].add(c.get("donor_name", ""))
        summary[key]["max_donation"] = max(summary[key]["max_donation"], amt)

    # Finalize donor counts
    for key in summary:
        summary[key]["donor_count"] = len(summary[key]["donors"])
        total = summary[key]["total_dollars"]
        count = summary[key]["donor_count"]
        summary[key]["avg_donation"] = round(total / count, 2) if count > 0 else 0

    # Write precinct_summary CSV
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "finance_election_id", "committee_id", "precinct_id",
            "total_dollars", "donor_count", "avg_donation", "max_donation"
        ])
        for (eid, cid, pid), data in sorted(summary.items()):
            writer.writerow([
                eid, cid, pid,
                round(data["total_dollars"], 2),
                data["donor_count"],
                data["avg_donation"],
                round(data["max_donation"], 2)
            ])

    print(f"  Precinct summary rows: {len(summary)}")
    print(f"  Output: {SUMMARY_CSV}")

    # ── Build precinct_race_summary ──
    # Key: (election_id, precinct_id) → {committee_totals, committee_donors}
    race_summary = defaultdict(lambda: {"committee_dollars": defaultdict(float), "committee_donors": defaultdict(set)})

    for c in contributions:
        key = (c["finance_election_id"], c["precinct_id"])
        race_summary[key]["committee_dollars"][c["committee_id"]] += float(c["amount"])
        race_summary[key]["committee_donors"][c["committee_id"]].add(c.get("donor_name", ""))

    # Compute cross-candidate metrics
    race_rows = []
    for (eid, pid), data in race_summary.items():
        total_dollars = sum(data["committee_dollars"].values())
        all_donors = set()
        for donors in data["committee_donors"].values():
            all_donors.update(donors)
        total_donors = len(all_donors)

        # Find top committee by dollars
        top_cid = max(data["committee_dollars"], key=data["committee_dollars"].get)
        top_party = COMMITTEES.get(top_cid, {}).get("party", "")

        # Dollar margin: difference between D and R totals
        d_dollars = sum(v for k, v in data["committee_dollars"].items()
                       if COMMITTEES.get(k, {}).get("party") == "D")
        r_dollars = sum(v for k, v in data["committee_dollars"].items()
                       if COMMITTEES.get(k, {}).get("party") == "R")
        dollar_margin = d_dollars - r_dollars

        # Donor margin: normalized -1 to +1 (positive = D lead)
        d_donors = sum(len(v) for k, v in data["committee_donors"].items()
                      if COMMITTEES.get(k, {}).get("party") == "D")
        r_donors = sum(len(v) for k, v in data["committee_donors"].items()
                      if COMMITTEES.get(k, {}).get("party") == "R")
        if total_donors > 0:
            donor_margin = round((d_donors - r_donors) / total_donors, 4)
        else:
            donor_margin = 0

        race_rows.append({
            "finance_election_id": eid,
            "precinct_id": pid,
            "total_dollars": round(total_dollars, 2),
            "total_donors": total_donors,
            "top_committee_id": top_cid,
            "dollar_margin": round(dollar_margin, 2),
            "donor_margin": donor_margin,
        })

    # Write race_summary CSV
    with open(RACE_SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "finance_election_id", "precinct_id", "total_dollars", "total_donors",
            "top_committee_id", "dollar_margin", "donor_margin"
        ])
        writer.writeheader()
        for row in sorted(race_rows, key=lambda r: (r["finance_election_id"], r["precinct_id"])):
            writer.writerow(row)

    print(f"  Race summary rows: {len(race_rows)}")
    print(f"  Output: {RACE_SUMMARY_CSV}")

    # Stats by election
    for eid in sorted(set(r["finance_election_id"] for r in race_rows)):
        cycle_rows = [r for r in race_rows if r["finance_election_id"] == eid]
        total = sum(r["total_dollars"] for r in cycle_rows)
        donors = sum(r["total_donors"] for r in cycle_rows)
        print(f"\n  {eid}:")
        print(f"    Precincts with data: {len(cycle_rows)}")
        print(f"    Total dollars: ${total:,.2f}")
        print(f"    Total donors: {donors}")

    return len(summary), len(race_rows)


if __name__ == "__main__":
    aggregate()
