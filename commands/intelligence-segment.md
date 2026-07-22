---
description: Stage 1 of build-tam - use AI to isolate ONE coherent segment from the Closed-Won Deals book and select clean seed companies for the lookalike build.
argument-hint: [segment name, or leave blank for AI to pick]
---

You are running **Stage 1 (Intelligence: Segment + Seeds)** of the `build-tam` pipeline. Load the `build-tam` skill for shared conventions and exact CompanyEnrich/Airtable calls.

Goal: from the full closed-won book, isolate one segment and produce a curated seed list that feeds the lookalike.

Steps:
1. Locate the **closed-won book** and read its records (Company, Domain, Segment if present):
   - If `$ARGUMENTS` includes a CSV path, or the Airtable MCP is not connected, read the closed-won deals from that CSV (columns: Company, Domain, and optionally Segment, Deal Size, Close Date).
   - Otherwise use Airtable: find the table whose name contains "Closed-Won" via `search_bases` → `list_tables_for_base`; do not hardcode IDs. If more than one base has such a table, ask which one.
2. Pick the target segment:
   - If `$ARGUMENTS` names a segment, use it.
   - Else, use AI judgement: if a `Segment` field exists, list the segments with counts and pick the richest / most coherent one; if there is NO segment field, cluster the accounts by profile (vertical, size, keywords) and propose 2-3 segment labels, then pick one. State your reasoning in one line.
3. From that segment, select **7-10 clean seed companies** that best represent the ICP by example. Drop obvious outliers (a VC firm, a mis-tagged company) and say which you dropped and why - that curation is the point.
4. Write the seeds to **`<Segment> (Seeds)`** (Airtable table if connected, else `./tam-run/<segment>-seeds.csv`) with fields Company, Domain, and any deal metadata available. This is the single source of truth for the downstream stages. See the skill's "Storage: Airtable OR CSV" section.
5. Report: the chosen segment, the seed domains, and what you dropped.

End with: `Next: /reverse-engineer` (build the ICP from these seeds).

Keep it read-only against CompanyEnrich in this stage - this is selection from data you already have, no credits needed unless you must resolve names to domains.
