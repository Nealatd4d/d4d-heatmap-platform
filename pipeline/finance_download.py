"""
Step 1: Download & filter Receipts.txt from IL SBE
Streams the ~1GB file and extracts only rows for target committee IDs.
"""

import os, csv, sys, ssl, urllib.request
from datetime import datetime
from finance_config import (
    SBE_RECEIPTS_URL, TARGET_SBE_IDS, RECEIPT_COLUMNS,
    DATA_DIR, RECEIPTS_RAW, CONTRIBUTIONS_CSV,
    FINANCE_ELECTIONS, COMMITTEES
)


def assign_cycle(rcv_date_str):
    """Assign a contribution to an election cycle based on RcvDate."""
    try:
        # Try multiple date formats
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
            try:
                d = datetime.strptime(rcv_date_str.strip(), fmt).date()
                break
            except ValueError:
                continue
        else:
            return None

        for eid, cfg in FINANCE_ELECTIONS.items():
            start = datetime.strptime(cfg["cycle_start"], "%Y-%m-%d").date()
            end = datetime.strptime(cfg["cycle_end"], "%Y-%m-%d").date()
            if start <= d <= end:
                return eid
        return None  # outside all cycles
    except Exception:
        return None


def download_and_filter():
    """Stream Receipts.txt, filter to target committees, write filtered CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Downloading Receipts.txt from IL SBE (streaming ~1GB)...")
    print(f"Filtering for committee IDs: {TARGET_SBE_IDS}")

    # Create SSL context that doesn't verify (IL SBE has cert issues)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(SBE_RECEIPTS_URL, headers={
        "User-Agent": "D4D-Finance-Pipeline/1.0"
    })

    matched = 0
    skipped_archived = 0
    skipped_no_cycle = 0
    total_lines = 0
    errors = 0

    with urllib.request.urlopen(req, context=ctx) as resp:
        # Write filtered contributions to CSV
        with open(CONTRIBUTIONS_CSV, "w", newline="", encoding="utf-8") as outf:
            writer = csv.writer(outf)
            writer.writerow([
                "sbe_receipt_id", "committee_id", "finance_election_id",
                "donor_name", "donor_address", "donor_city", "donor_state", "donor_zip",
                "amount", "receipt_date", "occupation", "employer", "d2_part"
            ])

            # Read line by line to avoid loading 1GB into memory
            buffer = b""
            for chunk in iter(lambda: resp.read(1024 * 256), b""):
                buffer += chunk
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    total_lines += 1

                    if total_lines == 1:
                        # Skip header if present
                        line_str = line_bytes.decode("utf-8", errors="replace").strip()
                        if line_str.startswith("ID\t") or line_str.startswith('"ID"'):
                            continue

                    try:
                        line_str = line_bytes.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue

                        fields = line_str.split("\t")
                        if len(fields) < len(RECEIPT_COLUMNS):
                            fields.extend([""] * (len(RECEIPT_COLUMNS) - len(fields)))

                        row = dict(zip(RECEIPT_COLUMNS, fields))

                        # Filter: only target committees
                        committee_sbe_id = row.get("CommitteeID", "").strip()
                        if committee_sbe_id not in TARGET_SBE_IDS:
                            continue

                        # Skip archived/amended records
                        archived = row.get("Archived", "").strip()
                        if archived and archived.lower() in ("1", "true", "yes"):
                            skipped_archived += 1
                            continue

                        # Assign election cycle
                        rcv_date = row.get("RcvDate", "").strip()
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
                        amount_str = row.get("Amount", "0").strip().replace(",", "").replace("$", "")
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            amount = 0.0

                        if amount <= 0:
                            continue

                        donor_name = f"{row.get('LastOnlyName', '').strip()}, {row.get('FirstName', '').strip()}".strip(", ")
                        donor_address = row.get("Address1", "").strip()
                        donor_city = row.get("City", "").strip()
                        donor_state = row.get("State", "").strip()
                        donor_zip = row.get("Zip", "").strip()

                        writer.writerow([
                            row.get("ID", "").strip(),  # sbe_receipt_id
                            our_committee_id,
                            cycle,
                            donor_name,
                            donor_address,
                            donor_city,
                            donor_state,
                            donor_zip,
                            amount,
                            rcv_date,
                            row.get("Occupation", "").strip(),
                            row.get("Employer", "").strip(),
                            row.get("D2Part", "").strip(),
                        ])
                        matched += 1

                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            print(f"  Error on line {total_lines}: {e}")

                    if total_lines % 500000 == 0:
                        print(f"  Processed {total_lines:,} lines, {matched} contributions matched...")

            # Process remaining buffer
            if buffer.strip():
                total_lines += 1
                try:
                    line_str = buffer.decode("utf-8", errors="replace").strip()
                    fields = line_str.split("\t")
                    if len(fields) >= 7:
                        # Same logic as above
                        if len(fields) < len(RECEIPT_COLUMNS):
                            fields.extend([""] * (len(RECEIPT_COLUMNS) - len(fields)))
                        row = dict(zip(RECEIPT_COLUMNS, fields))
                        committee_sbe_id = row.get("CommitteeID", "").strip()
                        if committee_sbe_id in TARGET_SBE_IDS:
                            archived = row.get("Archived", "").strip()
                            if not (archived and archived.lower() in ("1", "true", "yes")):
                                rcv_date = row.get("RcvDate", "").strip()
                                cycle = assign_cycle(rcv_date)
                                if cycle:
                                    for cid, cfg in COMMITTEES.items():
                                        if str(cfg["sbe_id"]) == committee_sbe_id:
                                            our_committee_id = cid
                                            break
                                    else:
                                        our_committee_id = None
                                    if our_committee_id:
                                        amount_str = row.get("Amount", "0").strip().replace(",", "").replace("$", "")
                                        try:
                                            amount = float(amount_str)
                                        except ValueError:
                                            amount = 0.0
                                        if amount > 0:
                                            donor_name = f"{row.get('LastOnlyName', '').strip()}, {row.get('FirstName', '').strip()}".strip(", ")
                                            with open(CONTRIBUTIONS_CSV, "a", newline="", encoding="utf-8") as outf2:
                                                writer2 = csv.writer(outf2)
                                                writer2.writerow([
                                                    row.get("ID", "").strip(),
                                                    our_committee_id, cycle, donor_name,
                                                    row.get("Address1", "").strip(),
                                                    row.get("City", "").strip(),
                                                    row.get("State", "").strip(),
                                                    row.get("Zip", "").strip(),
                                                    amount, rcv_date,
                                                    row.get("Occupation", "").strip(),
                                                    row.get("Employer", "").strip(),
                                                    row.get("D2Part", "").strip(),
                                                ])
                                            matched += 1
                except Exception:
                    pass

    print(f"\nDone!")
    print(f"  Total lines processed: {total_lines:,}")
    print(f"  Contributions matched: {matched}")
    print(f"  Skipped (archived): {skipped_archived}")
    print(f"  Skipped (outside cycles): {skipped_no_cycle}")
    print(f"  Errors: {errors}")
    print(f"  Output: {CONTRIBUTIONS_CSV}")
    return matched


if __name__ == "__main__":
    download_and_filter()
