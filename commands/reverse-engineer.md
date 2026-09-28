---
description: Stage 2 of build-tam - reverse-engineer the ICP from the current segment's seeds and write a Reverse-Engineered ICP table.
argument-hint: (none - reads the active Seeds table or CSV)
---

You are running **Stage 2 (Reverse-Engineer the ICP)** of the `build-tam` pipeline. Load the `build-tam` skill for conventions.

The point on stage: *we did not write the ICP - we reverse-engineered it from the deals.*

Steps:
1. Find the active **`<Segment> (Seeds)`** table in the base, or `./tam-run/<segment>-seeds.csv` in CSV mode (the one produced by `/intelligence-segment`; if several exist, use the most recently updated or ask which segment). Read the seed domains.
2. Pull the seeds' CompanyEnrich profiles - reuse the `items` already returned by any recent `find_similar_companies`/`search_companies` if available, otherwise call `enrich_company` per domain (1 credit each) or `find_similar_companies(domains=[...seeds], pageSize=1)` and read the seed data.
3. Synthesize the shared pattern across these dimensions (only what the data supports): Vertical/Category, Business model, Company size, Funding stage, Geography, Company age, Revenue, Tech maturity, Core need, and the Buying signal to prioritize on later.
4. Write a **`<Segment> - Reverse-Engineered ICP`** table (or `./tam-run/<segment>-icp.csv`) with columns Dimension / Pattern / Evidence, plus a top "ICP One-Liner" row. Cite the seeds as evidence (e.g. "6 US HQ, 1 UK").
5. Report the one-liner and the table.

End with: `Next: /build-lookalike` (expand these seeds into the whole lookalike market).
