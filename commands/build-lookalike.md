---
description: Stage 3 of build-tam - expand the segment's seeds into the full lookalike market (the TAM), enrich, tier-tag, and write TAM Full.
argument-hint: [optional filters, e.g. "US,GB 51-500"]
---

You are running **Stage 3 (Lookalike TAM)** of the `build-tam` pipeline. Load the `build-tam` skill for the exact `find_similar_companies` calls, pagination, and the file-parsing gotcha.

Steps:
1. Read the active seed domains from the **`<Segment> (Seeds)`** table.
2. **Count first (cheap):** `find_similar_companies(domains=[...], categories=["saas"], countries=[...], employees=[...], pageSize=1)` → read `totalItems` = the TAM. Note the top similarity from `metadata.scores`.
3. **Contrast beat:** run the same ICP as a keyword `search_companies(keywords=[...], pageSize=1)` and compare - keyword finds a tiny fraction and hides most of the TAM. Report both numbers.
4. If too few, WIDEN per the skill's levers (employee bands → countries → `["saas","b2b"]` Or → more seeds). If huge, that's fine - you narrow next stage.
5. **Pull the market:** page through `pageSize=100` (responses save to `tool-results/` files - parse with Python, dedupe by `id`). Enrich each row with the fields you want (employees, revenue, funding, geo, tech, keywords, LinkedIn, similarity score).
6. Write a **`<Segment> - TAM Full`** table (bulk-load via the Airtable REST batch method from the skill for thousands of rows). Rank by similarity for now; tier-tagging happens next stage.
7. Report the funnel headline, e.g. `Keyword: 397  →  Lookalike TAM: 6,133`.

End with: `Next: /tier-score` (apply the Tier Rules).
