"""
Master orchestrator for the campaign finance ETL pipeline.
Usage: python finance_pipeline.py [--step download|geocode|aggregate|load|all]
"""

import sys
import time


def run_pipeline(step="all"):
    start = time.time()
    print("=" * 60)
    print("D4D Campaign Finance Pipeline")
    print("Target: HD-18 (Gabel vs Hutchinson, 2022 & 2024)")
    print("=" * 60)

    if step in ("all", "download"):
        print("\n── Step 1: Download & Filter SBE Receipts ──")
        from finance_download import download_and_filter
        matched = download_and_filter()
        if matched == 0:
            print("WARNING: No contributions found! Check committee IDs.")
            if step != "all":
                return

    if step in ("all", "geocode"):
        print("\n── Step 2: Geocode Donors ──")
        from finance_geocode import geocode_contributions
        pip_matched = geocode_contributions()
        if pip_matched == 0:
            print("WARNING: No precinct matches! Check GeoJSON files.")
            if step != "all":
                return

    if step in ("all", "aggregate"):
        print("\n── Step 3: Aggregate Metrics ──")
        from finance_aggregate import aggregate
        aggregate()

    if step in ("all", "load"):
        print("\n── Step 4: Load to Supabase ──")
        from finance_load import load_all
        load_all()

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"Pipeline complete in {elapsed:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    step = "all"
    if len(sys.argv) > 1 and sys.argv[1] == "--step":
        step = sys.argv[2] if len(sys.argv) > 2 else "all"
    run_pipeline(step)
