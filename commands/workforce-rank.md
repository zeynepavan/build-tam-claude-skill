---
description: Stage 5 of build-tam - rank the A+B accounts by REAL workforce growth (the buying signal) into an in-market list.
argument-hint: (none)
---

You are running **Stage 5 (Workforce Signal Ranking)** of the `build-tam` pipeline. Load the `build-tam` skill.

Steps:
1. **Reuse the A+B pull from `/tier-score`** (the `minScore=0.8, includeWorkforce=true` files in `tool-results/`). Only if those files are missing, pull them now: `find_similar_companies(domains=[...seeds], ...same filters..., minScore=0.8, includeWorkforce=true, pageSize=100)` (+5 credits/company).
2. Compute real y1 and 6-month growth with the bundled script, which picks the baseline snapshot within a tolerance window and skips non-company files:
   `python <scripts dir>/compute_growth.py tool-results/* --out tam-run/<segment>-by-workforce.csv`
   (`<scripts dir>` is `${CLAUDE_PLUGIN_ROOT}/scripts` for a plugin install, `~/.claude/skills/build-tam/scripts` for a manual one.)
3. Write a **`<Segment> - TAM by Workforce Signal`** table (in CSV mode the script's output is that table; add the Tier column from TAM Full), sorted DESC by y1 growth, with Rank, Company, Domain, Tier, Workforce Growth y1 %, 6mo %, Headcount, Similarity.
4. Report the top ~10 and the punchline: sorting by growth floats all Tier-A to the top → this **validates the tier model** (both signals agreeing).

End with: `Next: /find-buyers` (attach decision makers to these accounts).
