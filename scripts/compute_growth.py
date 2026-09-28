#!/usr/bin/env python3
"""
Rank the A+B accounts by real workforce growth from saved find_similar_companies
tool-results (the ones pulled with includeWorkforce=true). Dedupes across pages,
computes y1 + 6mo growth per company, sorts desc, writes a CSV.

Usage:
  python scripts/compute_growth.py tool-results/*.txt --out tam-run/<segment>-by-workforce.csv
  python scripts/compute_growth.py tool-results/ --out out.csv

Feed it the minScore=0.8 + includeWorkforce=true pull - that set IS A+B, so there is
no score filter here. Never re-filter on the reported score in metadata.scores: it is a
different number from minScore (see the skill). Files that aren't company results
(search_people dumps, non-JSON output) are skipped.

Growth = latest observed headcount vs the snapshot ~365 days earlier (6mo = ~182d).
A company whose nearest snapshot is outside the tolerance window, or whose base is 0,
gets a blank rather than a fabricated number. Your y1>=15% set here should reproduce
the API's workforceGrowth Tier-A membership exactly - if it doesn't, the window is off.
"""
import argparse
import csv
import glob
import os
import sys

import tam_lib


def expand(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob.glob(os.path.join(p, "*"))
        else:
            files += glob.glob(p)
    return [f for f in files if os.path.isfile(f)]


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="tool-results files, globs or directories")
    ap.add_argument("--out", default="by-workforce.csv")
    opts = ap.parse_args(argv)
    out = os.path.abspath(opts.out)
    files = [f for f in expand(opts.inputs) if os.path.abspath(f) != out]
    if not files:
        ap.print_help()
        return 1

    rows = tam_lib.load_items(files)
    out_rows = []
    for _id, rec in rows.items():
        it, score = rec["item"], rec["score"]
        wf = it.get("workforce") or {}
        loc = it.get("location") or {}
        out_rows.append({
            "Company": it.get("name"),
            "Domain": it.get("domain"),
            "Workforce y1 %": tam_lib.compute_growth(wf, 365),
            "Workforce 6mo %": tam_lib.compute_growth(wf, 182, tol_days=60),
            "Headcount": wf.get("observed_employee_count"),
            "Similarity": round(score, 4) if score is not None else None,
            "Country": (loc.get("country") or {}).get("code"),
            "Funding Stage": (it.get("financial") or {}).get("funding_stage"),
            "LinkedIn": (it.get("socials") or {}).get("linkedin_url"),
        })

    out_rows.sort(key=lambda r: (r["Workforce y1 %"] is None, -(r["Workforce y1 %"] or 0)))
    for i, r in enumerate(out_rows, 1):
        r["Rank"] = i

    os.makedirs(os.path.dirname(opts.out) or ".", exist_ok=True)
    cols = ["Rank", "Company", "Domain", "Workforce y1 %", "Workforce 6mo %",
            "Headcount", "Similarity", "Country", "Funding Stage", "LinkedIn"]
    with open(opts.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k) for k in cols})

    have = sum(1 for r in out_rows if r["Workforce y1 %"] is not None)
    shrinking = sum(1 for r in out_rows if (r["Workforce y1 %"] or 0) < 0)
    print(f"wrote {len(out_rows)} rows to {opts.out} "
          f"({have} with a y1 figure, {shrinking} shrinking)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
