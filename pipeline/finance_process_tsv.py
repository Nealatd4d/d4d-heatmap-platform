"""
Convert the background-downloaded receipts_all.tsv into contributions.csv
(the format expected by finance_geocode.py and the rest of the pipeline).

This replaces finance_download.py for when we already have the filtered TSV data.
"""

import csv, os, sys
from datetime import datetime
from finance_config import (
    TARGET_SBE_IDS, RECEIPT_COLUMNS, DATA_DIR,
    CONTRIBUTIONS_CSV, FINANCE_ELECTIONS, COMMITTEES
)


def assign_cycle(rcv_date_str):
    """Assign a contribution to an election cycle based on RcvDate."""
    if not rcv_date_str or not rcv_date_str.strip():
        return None
    rcv_date_str = rcv_date_str.strip()
    
    # Try multiple date formats
    d = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            d = datetime.strptime(rcv_date_str.split(" ")[0] if " " in rcv_date_str else rcv_date_str, 
                                  fmt.split(" ")[0] if " " in fmt else fmt).date()
            break
        except ValueError:
            continue
    
    if d is None:
        # Try with full datetime
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                d = datetime.strptime(rcv_date_str, fmt).date()
                break
            except ValueError:
                continue
    
    if d is None:
        return None
    
    for eid, cfg in FINANCE_ELECTIONS.items():
        start = datetime.strptime(cfg["cycle_start"], "%Y-%m-%d").date()
        end = datetime.strptime(cfg["cycle_end"], "%Y-%m-%d").date()
        if start <= d <= end:
            return eid
    
    return None  # Outside all target cycles


def process_tsv(input_path=None):
    """Convert filtered TSV to contributions CSV."""
    if input_path is None:
        input_path = os.path.join(DATA_DIR, "receipts_all.tsv")
    
    if not os.path.exists(input_path):
        print(f"ERROR: {input_path} not found")
        return 0
    
    print(f"Processing: {input_path}")
    
    matched = 0
    skipped_archived = 0
    skipped_no_cycle = 0
    skipped_no_amount = 0
    skipped_bad_committee = 0
    total = 0
    seen_ids = set()  # Dedup by SBE receipt ID
    
    with open(CONTRIBUTIONS_CSV, "w", newline="", encoding="utf-8") as outf:
        writer = csv.writer(outf)
        writer.writerow([
            "sbe_receipt_id", "committee_id", "finance_election_id",
            "donor_name", "donor_address", "donor_city", "donor_state", "donor_zip",
            "amount", "receipt_date", "occupation", "employer", "d2_part"
        ])
        
        with open(input_path, encoding="utf-8", errors="replace") as inf:
            for line in inf:
                line = line.strip().rstrip("\r")
                if not line:
                    continue
                total += 1
                
                fields = line.split("\t")
                
                # Pad to expected column count
                while len(fields) < len(RECEIPT_COLUMNS):
                    fields.append("")
                
                row = dict(zip(RECEIPT_COLUMNS, [f.strip() for f in fields]))
                
                # Skip header line if present
                if row.get("ID", "").upper() == "ID":
                    continue
                
                # Verify committee ID
                committee_sbe_id = row.get("CommitteeID", "")
                if committee_sbe_id not in TARGET_SBE_IDS:
                    skipped_bad_committee += 1
                    continue
                
                # Dedup by SBE receipt ID
                sbe_id = row.get("ID", "")
                if sbe_id in seen_ids:
                    continue
                seen_ids.add(sbe_id)
                
                # Skip archived/amended records
                archived = row.get("Archived", "").lower()
                if archived in ("1", "true", "yes"):
                    skipped_archived += 1
                    continue
                
                # Assign election cycle
                rcv_date = row.get("RcvDate", "")
                cycle = assign_cycle(rcv_date)
                if not cycle:
                    skipped_no_cycle += 1
                    continue
                
                # Map SBE committee ID to our committee_id
                our_committee_id = None
                for cid, cfg in COMMITTEES.items():
                    if str(cfg["sbe_id"]) == committee_sbe_id:
                        our_committee_id = cid
                        break
                if not our_committee_id:
                    continue
                
                # Parse amount
                amount_str = row.get("Amount", "0").replace(",", "").replace("$", "")
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0
                if amount <= 0:
                    skipped_no_amount += 1
                    continue
                
                donor_name = f"{row.get('LastOnlyName', '')}, {row.get('FirstName', '')}".strip(", ")
                
                # Normalize date format
                date_clean = rcv_date
                if " " in date_clean:
                    date_clean = date_clean.split(" ")[0]
                
                writer.writerow([
                    sbe_id,
                    our_committee_id,
                    cycle,
                    donor_name,
                    row.get("Address1", ""),
                    row.get("City", ""),
                    row.get("State", ""),
                    row.get("Zip", "").strip()[:5],
                    amount,
                    date_clean,
                    row.get("Occupation", ""),
                    row.get("Employer", ""),
                    row.get("D2Part", ""),
                ])
                matched += 1
    
    print(f"\nResults:")
    print(f"  Total lines in TSV: {total}")
    print(f"  Contributions in target cycles: {matched}")
    print(f"  Skipped (archived): {skipped_archived}")
    print(f"  Skipped (outside cycles): {skipped_no_cycle}")
    print(f"  Skipped (zero/negative amount): {skipped_no_amount}")
    print(f"  Skipped (wrong committee): {skipped_bad_committee}")
    print(f"  Output: {CONTRIBUTIONS_CSV}")
    
    # Show breakdown by cycle and committee
    print(f"\n  By cycle/committee:")
    breakdown = {}
    with open(CONTRIBUTIONS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["finance_election_id"], row["committee_id"])
            if key not in breakdown:
                breakdown[key] = {"count": 0, "total": 0.0}
            breakdown[key]["count"] += 1
            breakdown[key]["total"] += float(row["amount"])
    
    for (eid, cid), stats in sorted(breakdown.items()):
        print(f"    {eid} / {cid}: {stats['count']} contributions, ${stats['total']:,.2f}")
    
    return matched


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else None
    process_tsv(input_path)
