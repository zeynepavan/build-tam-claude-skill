---
description: Stage 5 of build-tam - rank the A+B accounts by REAL workforce growth (the buying signal) into an in-market list.
argument-hint: (none)
---

You are running **Stage 5 (Workforce Signal Ranking)** of the `build-tam` pipeline. Load the `build-tam` skill.

Steps:
1. Pull the A+B accounts with workforce insights:
   `find_similar_companies(domains=[...seeds], ...same filters..., minScore=0.8, includeWorkforce=true, pageSize=100)` (+5 credits/company; responses save to files - parse with Python).
2. For each company, compute real y1 growth from `workforce.history[]`: latest `observed_employee_count` vs the snapshot ~365 days earlier → `(latest-base)/base*100`. Also grab current headcount and 6-month growth.
3. Write a **`<Segment> - TAM by Workforce Signal`** table, sorted DESC by y1 growth, with Rank, Company, Domain, Tier, Workforce Growth y1 %, 6mo %, Headcount, Similarity.
4. Report the top ~10 and the punchline: sorting by growth floats all Tier-A to the top → this **validates the tier model** (both signals agreeing).

End with: `Next: /find-buyers` (attach decision makers to these accounts).
