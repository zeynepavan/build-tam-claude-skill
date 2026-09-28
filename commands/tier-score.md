---
description: Stage 4 of build-tam - apply the 3-tier scoring rules (similarity + workforce growth) to the lookalike TAM and tag every account A/B/C.
argument-hint: [optional thresholds, e.g. "score=0.80 growth=15"]
---

You are running **Stage 4 (Tier Score)** of the `build-tam` pipeline. Load the `build-tam` skill for the exact count calls.

Two signals stacked: **similarity** ("right company?") + **workforce growth** ("in-market now?").

Steps:
1. Ensure a **Tier Rules** table exists in the base, or `./tam-run/tier-rules.csv` in CSV mode (create + fill if missing), so you can point at the logic:
   - A - Hot: similarity ≥ 0.80 AND workforce growth y1 ≥ +15% → email first
   - B - Warm: similarity ≥ 0.80, growth < +15% → 2nd wave
   - C - Nurture: similarity < 0.80 → deprioritize
   (Thresholds tunable via `$ARGUMENTS`; state what you used.)
2. **Count each tier at `pageSize=1`:**
   - A+B: `find_similar_companies(domains=[...seeds], ...same filters..., minScore=0.8, pageSize=1)`
   - A: add `workforceGrowth={department:"overall", period:"y1", minPercent:15}`
   - Tier B = (A+B) − A ; Tier C = (full TAM) − (A+B).
3. **Get A+B membership (not just the count):** page `find_similar_companies(..., minScore=0.8, includeWorkforce=true, pageSize=100)` until you have `totalItems`. Never derive membership from the reported score in `metadata.scores` - it disagrees with `minScore`. Keep these `tool-results/` files: `/workforce-rank` reuses them, so the workforce data is paid for once.
4. **Backfill:** any A+B account missing from TAM Full (the reported-score materialization misses some) gets added as a row now.
5. Tag the **`<Segment> - TAM Full`** rows: A+B membership from step 3; within it, Tier A = y1 growth ≥ +15% computed from those same files with `compute_growth.py` (see `/workforce-rank` for the path). That set should equal the step-2 Tier A count - if it doesn't, stop and check before tagging. Set `Tier` (A-Hot / B-Warm / C-Nurture) and re-rank tier-first (A 1..n, then B, then C; similarity as tiebreaker). Airtable: a singleSelect, bulk-updated with the REST PATCH-by-key method from the skill. CSV: add a `Tier` column to `./tam-run/<segment>-tam-full.csv`.
6. Report the funnel, e.g. `6,133 → 157 (≥0.80) → 30 (Tier A)`.

If using Airtable, tell the user: create filtered **A / B / C views** in the Airtable UI (the API can't create grid views) - one table, three lenses.

End with: `Next: /workforce-rank` (rank the in-market accounts by real hiring growth).
