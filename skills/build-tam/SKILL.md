---
name: build-tam
description: Build and prioritize a real TAM from a handful of best-customer (closed-won) seed accounts using the CompanyEnrich MCP, then structure it in Airtable (or CSV). Expands seeds into a lookalike market, widens/narrows with structured filters, layers a workforce-growth buying signal, scores into a 3-tier (Hot/Warm/Nurture) ranked list, finds decision makers, and resolves work emails - each stage with an exact call. Use to turn good customers into a prioritized, contactable outbound list, size a market, or run a live terminal demo.
---

# Build TAM - closed-won seeds → ranked, contactable outbound list

Turn a small set of best customers into a prioritized, named, emailable market using the CompanyEnrich MCP (`mcp__companyenrich__*`), structured in Airtable (`mcp__*Airtable__*`) or exported to CSV.

**The one line:** feed the engine *examples of your best customers* (not keywords), expand to the whole lookalike market, narrow with real buying signals into a ranked list, then attach the actual people to email.

## Two ways to run this
- **All at once:** invoke `build-tam` and walk the stages below end to end.
- **Live, stage by stage (for demos):** each stage is also a **slash command** you fire in order. Each command does ONE stage, reads its input from the previous stage's Airtable table or `./tam-run/` CSV (either way, the stored output is the shared state), writes its output table, and prints the next command. This lets you run the whole thing live on a fresh closed-won book:

  | Command | Stage | Produces |
  |---------|-------|----------|
  | `/intelligence-segment [name]` | 1 - pick a segment + curate seeds | `<Segment> (Seeds)` |
  | `/reverse-engineer` | 2 - ICP from the seeds | `<Segment> - Reverse-Engineered ICP` |
  | `/build-lookalike` | 3 - expand to the TAM | `<Segment> - TAM Full` |
  | `/tier-score` | 4 - A/B/C scoring | Tier tags + `Tier Rules` |
  | `/workforce-rank` | 5 - in-market ranking | `<Segment> - TAM by Workforce Signal` |
  | `/find-buyers [set]` | 6 - decision makers | `<Segment> - Decision Makers (People)` |
  | `/get-emails [subset]` | 7 - work emails | Email column filled |

  Command files live in the plugin's `commands/` (or `~/.claude/commands/` for a manual install). Each one loads THIS skill for the exact calls and gotchas, so the skill stays the single source of truth and the commands stay thin. The stage detail below is what each command executes.

## The pipeline (each stage = one table + one exact call)

```
Closed-Won Deals  →  Reverse-Engineered ICP  →  TAM Full (lookalike)  →  Tier Rules
   (seeds in)          (pattern out)              (whole market)          (scoring logic)
      →  TAM by Workforce Signal  →  Decision Makers  →  People + Emails
           (in-market ranking)         (personas)         (contactable)
```

Run it top to bottom. Every stage below gives the **exact call** and the **gotcha** that will bite you if you skip it.

---

## Inputs to collect first
1. **Seed domains** - 7-10 closed-won / best-customer domains (max 10 per lookalike call). This IS the ICP, by example. Root domains only (`ycharts.com`, not `https://www.ycharts.com`).
2. **Geography** - 2-letter codes (`US`, `GB`). Optional; omit for global.
3. **Size band(s)** - `11-50`, `51-200`, `201-500`, `501-1K`, `1K-5K`, `5K-10K`, `over-10K`.
4. **Category** - usually `saas`, or `["saas","b2b"]` with `categoryOperator:"Or"` for a wider net.
5. **Where to store it** - Airtable base (preferred; it's a source AND a sink) or CSV.

If given company names, resolve to domains first. If given a sheet, read the domain column.

## Storage: Airtable OR CSV (Airtable is optional)
Every stage reads its input from the previous stage's output and writes one artifact. Two backends:
- **Airtable (preferred):** tables persist = shared state across stages, and you get filtered A/B/C views in the UI. Requires the Airtable MCP + a PAT.
- **CSV / local files (no Airtable):** write each stage's table as a CSV under `./tam-run/`, using these names:
  - Stage 1: `<segment>-seeds.csv`
  - Stage 2: `<segment>-icp.csv`
  - Stage 3: `<segment>-tam-full.csv` (Stage 4 adds the `Tier` column in place)
  - Stage 4: `tier-rules.csv`
  - Stage 5: `<segment>-by-workforce.csv`
  - Stage 6 and 7: `<segment>-people.csv` (Stage 7 fills the `Email` column in place)

  All the compute is identical; only the sink changes. The huge `find_similar_companies` / `search_people` responses already land as JSON files under `tool-results/` - parse those with Python and emit CSVs. Use this path whenever the Airtable MCP is absent.

Pick the backend once at Stage 1 and keep it for the whole run.

---

## Stage 0 - Prove it's live (demo opener)
```
get_current_user()
```
Shows the authed account + credit balance. Free, deducts nothing. Great trust-builder on stage.

## Stage 1 - Seeds table + curate
Load the seeds (from an Airtable table, a Google Sheet, or pasted). Then **sanity-check**: drop anything off-ICP (a VC firm, a mis-tagged company). A clean 7 beats a noisy 10 - say which you dropped and why. That curation is the human-in-the-loop moment and a strong demo beat.

**Airtable source:** `list_records_for_table(baseId, tableId, fieldIds:["Domain"])` → pull the domain column.

## Stage 2 - Reverse-engineer the ICP (optional but high-impact)
Pull the full records for the seeds and synthesize the shared pattern - vertical, size band, funding stage, geo, tech maturity, core need. Write it to a **Reverse-Engineered ICP** table (Dimension / Pattern / Evidence). The point on stage: *"we didn't write the ICP - we reverse-engineered it from the deals."*
```
enrich_company(domain="acme.com")   # 1 credit per seed, or read the items already returned by find_similar_companies
```

## Stage 3 - Expand to the lookalike market (the TAM number)
**Exact call - cheap count first:**
```
find_similar_companies(
  domains=[...seeds],
  categories=["saas"],
  countries=["US","GB"],
  employees=["51-200","201-500"],
  pageSize=1
)
```
Read `totalItems` = the TAM. Read `metadata.scores` for the top result's similarity.
**Cost:** 5 credits/company returned (5 min). A `pageSize:1` count = 5 credits.

**Contrast beat (powerful):** run the same ICP as a keyword search and compare:
```
search_companies(keywords=["fintech"], categories=["saas","b2b"], countries=["US","GB"],
                 employees=["51-200","201-500"], pageSize=1)
```
Keyword almost always returns a tiny fraction and lets noise in (it only catches companies that literally use the word). Lookalike finds companies that *resemble* your customers - often 10-15× more. **Keyword filtering hides most of the TAM.**

**Materialize only what you'll act on.** Results come back **strictly rank-ordered by similarity** and the decay is steep, so you don't need the whole market as rows. Size it with the `pageSize:1` count (cheap), then page `pageSize:100` only down to where you'll stop caring (usually a few hundred). Ranks far past the tier cutoff are Tier C by construction - pulling them costs 5 credits each to materialize rows the scoring discards. Say "TAM = N (sized), top M materialized" and move on.

**Hold-out validation (the strongest confidence beat there is).** If the closed-won book has more accounts in the segment than you seeded, hold the rest back, then check how many the lookalike rediscovered in the materialized set. Seeding 10 and rediscovering ~75% of a 60-account hold-out - several in the top 30 - proves the engine reconstructed a book it never saw. Every *other* company on the list has the same claim to attention. Do this whenever you can; it's more persuasive than any single number.

### Grow or shrink the TAM (two knobs)
The TAM is whatever the frame allows. Too few? WIDEN. Too broad is fine - you narrow with signals next.

**Levers to grow (biggest first):** add employee bands → add countries → `categories:["saas","b2b"]` + `categoryOperator:"Or"` → add more seeds → lower `minScore` / raise `similarityWeight`.

**Gotcha:** `totalItems` display caps at 10,000 even when the real universe is larger (account search limit is far higher). Hit 10,000 → say "10,000+" and narrow.

## Stage 4 - Tier Rules table + 3-tier score
Two signals stacked: **similarity** ("right company?") + **workforce growth** ("in-market now?"). Companies hiring have budget and pain. Write the rules to a **Tier Rules** table so you can point at it and say "here are the rules":

| Tier | Similarity | Workforce y1 | Action |
|------|-----------|--------------|--------|
| A - Hot | ≥ 0.80 | ≥ +15% | Email first |
| B - Warm | ≥ 0.80 | < +15% | 2nd wave / nurture |
| C - Nurture | < 0.80 | any | Deprioritize |

**Exact calls - count each tier at `pageSize:1`:**
```
# score>=0.80 count (A+B):
find_similar_companies(domains=[...], categories=["saas"], countries=["US","GB"],
  employees=["51-200","201-500"], minScore=0.8, pageSize=1)

# Tier A count (score>=0.80 AND hiring):
find_similar_companies(domains=[...], ...same..., minScore=0.8,
  workforceGrowth={department:"overall", period:"y1", minPercent:15}, pageSize=1)
```
- Tier A = second call's `totalItems`.
- Tier B = (A+B count) − (A count).
- Tier C = (full TAM) − (A+B count).
Report the funnel, e.g. `6,133 → 157 → 30`. Thresholds are tunable - state the ones you used.

**CRITICAL gotcha - `minScore` ≠ the score in `metadata.scores`.** `minScore` filters on the engine's *internal* similarity, which is **not** the blended score returned per-item in `metadata.scores`. In a real run the `minScore=0.8` set had reported scores running from 0.85 all the way down to 0.53. Consequences:
- **Get tier membership from the `minScore` filter, never by post-filtering the reported score.** They disagree.
- **A "top-N by reported score" materialization will MISS accounts that pass `minScore`.** In one run, 26 of 168 A+B accounts sat outside a top-500-by-reported-score pull. If you materialized the TAM by reported score in Stage 3, re-pull the A+B set with `minScore` and **backfill the ones you're missing** before tagging.
- To get the actual A+B membership (not just the count), page the `minScore=0.8` call at `pageSize:100`.

**Reuse this pull for Stage 5.** Pull the A+B set **once** with `includeWorkforce=true` here - that same response carries the workforce histories Stage 5 ranks on. Don't re-fetch the same companies next stage (saves 5 credits/company).

## Stage 5 - Rank by the workforce signal (the in-market list)
To rank A+B by *real* hiring growth (not just the yes/no threshold), pull them with workforce insights:
```
find_similar_companies(domains=[...], ...same..., minScore=0.8, includeWorkforce=true,
  pageSize=100, page=1)   # +5 credits/company
```
If you already pulled A+B with `includeWorkforce=true` in Stage 4, **reuse that file - don't call again.** Each item has a `workforce` object with `history[]` (monthly `observed_employee_count` snapshots). **Compute growth yourself:** latest count vs the snapshot closest to ~365 days earlier → `(latest-base)/base*100`.
- **Pick the baseline within a tolerance window** (~±75-120 days of the 365-day target) and skip the row if the nearest snapshot is outside it or the base count is 0 - otherwise a company with only 6 months of history reports a garbage number. Do a 6-month figure too (~182 days) for momentum.
- **Sanity-check against the API:** your locally computed `y1 ≥ 15%` set should reproduce the Stage-4 `workforceGrowth` Tier-A membership exactly. If it does (it matched 26/26 in a real run), you've validated the method the ranking rests on. If it doesn't, your baseline-picking window is off.
- Sort desc. Write to a **TAM by Workforce Signal** table. On stage: sorting by growth floats all Tier-A to the top. The real finding to call out: a chunk of your "right company" accounts are *shrinking* (a third, in one run) - firmographics alone would have sequenced them; the workforce signal is what separates "looks like our customer" from "is buying now."

## Stage 6 - Decision Makers: personas + search_people
First write a **Decision Makers** table mapping buyer personas to `search_people` params, then run the search per persona. Persona → params mapping that works for a B2B-data ICP:

| Persona | seniority | department |
|---------|-----------|-----------|
| GTM Economic Buyer | `vp,head,director` | `marketing`, `marketing/demand-generation`, `sales/revenue-operations` |
| Technical Champion | `c-suite,vp,head` | `engineering-technical`, `engineering-technical/data-science`, `information-technology` |
| Product Buyer | `vp,head,director` | `product-management` |
| Risk/Compliance Buyer | `c-suite,head,director` | `legal/compliance`, `operations` |

**Exact call (one per persona):**
```
search_people(
  domains=[...up to 100 target domains...],
  seniority=["vp","head","director"],
  department=["marketing","marketing/demand-generation","sales/revenue-operations"],
  pageSize=100
)
```
**Cost:** 2 credits/person (2 min). Each person has `experiences[]`; find the one where `isMatched && isCurrent && company.domain ∈ targets` to get their title/seniority/department at the target account. Derive the persona from that matched `department`. Cap ~1-2 per company per persona to keep it clean.

**Gotcha:** `domains` max 100 per call - chunk larger lists (e.g. 157 → 100 + 57) and loop personas over each chunk.

**Scope the hot tier into its OWN chunk.** `pageSize` caps at 100 results per call. If you pool all A+B into one chunk, the 100-result cap gets eaten by whichever accounts happen to rank first, and your Tier-A accounts - the ones actually getting emails next stage - can come back thin or missing. Run Tier A as a standalone chunk (≤100 domains) per persona; add B as separate chunks only if you'll work them. Verify each persona call came back under the 100 cap, or you silently lost people.

**Gotcha:** `PersonID` comes back as an **integer**. If your People table's ID column is text (`singleLineText`), the Airtable REST load **422s even with `typecast:true`** - cast the id to a string before writing.

## Stage 7 - Work emails (do this LAST, only for who you'll actually contact)
```
enrich_person_email(id=<PersonID>, domain="acme.com")
```
Returns `status: found|not-found` and `email`. **Cost:** 10 credits per *newly found* email (not-found = free). Typical hit rate ~55-60%.

**Biggest gotcha - this is the token-heavy stage.** It's one call *per person*, each returns a large object, and there is **no scriptable CompanyEnrich API key** (the MCP is OAuth; token isn't in config), so every call flows through the assistant loop and burns Claude usage. To conserve:
- **Narrow first:** only enrich the top workforce accounts, or a single persona (GTM = the budget holder).
- **Only enrich people you'll actually email.** `search_people` already gave you name + title + LinkedIn - that's enough to reach many via LinkedIn without spending emails.
- **Big batches, few turns.** Do ~30 per turn, not 5.

---

## Storing it in Airtable - exact mechanics + gotchas
- **Create base with tables:** `create_base(workspaceId, name, tables:[...])`. First field in each table = primary field. Get `workspaceId` from `list_workspaces`.
- **Add a table later:** `create_table(baseId, name, fields:[...])`. `singleSelect` needs `options.choices`.
- **Write rows:** `create_records_for_table(baseId, tableId, records:[{fields:{fldId: value}}])` - **max 50 records/call**, use field *IDs* not names.
- **Bulk load (thousands of rows):** the MCP write path is slow and can drop the socket. Instead build a CSV and load via the **Airtable REST API** in batches of 10:
  `POST https://api.airtable.com/v0/{baseId}/{tableId}` with `{"records":[...],"typecast":true}`, `Authorization: Bearer <PAT>`. Reading the PAT from `~/.claude.json` (the `AIRTABLE_API_KEY` env of the `airtable` MCP server) lets you script it. Resume by first fetching existing rows and skipping matched keys (foreground shells cap ~10 min - run long loads in the background).
- **Update / upsert by a key column:** `PATCH` with `{"performUpsert":{"fieldsToMergeOn":["fldPersonID"]}, "records":[...]}`. **Gotcha:** the REST key is `fieldsToMergeOn` (NOT `fieldIdsToMergeOn` - that 422s).
- **Bulk loads are flaky - wrap every batch in retry, then verify.** Long REST loops hit transient `SSL: CERTIFICATE_VERIFY_FAILED` and DNS `getaddrinfo` failures that kill a naive loop mid-run. Wrap each 10-record batch in ~3-5 retries with backoff; **after the load, page the table back and assert the row count / tier counts** - a dropped batch is silent otherwise. If a run half-completes, re-run: upsert-by-key is idempotent, plain POST duplicates.
- **Type-cast before writing:** integer IDs into a text column, and values into `singleSelect`/`date` fields, need `typecast:true` - and integers into text still fail even with it, so stringify those yourself (see the `PersonID` gotcha above).
- **A/B/C views:** the API/MCP **cannot create grid views.** Put all rows in one table with a `Tier` field, then have the user create filtered views in the UI (Filter `Tier is A` + Sort by Rank). A view is a live lens on the same table - same columns, no data copied.

## Handling huge MCP responses
`find_similar_companies`/`search_people` with `pageSize:100` + `includeWorkforce` can exceed the tool output limit; the harness saves the full JSON to a file under `tool-results/` and returns a path. Parse those files with Python (`json.load`) rather than trying to read them inline. Dedupe by `id` across pages; `totalItems` is stable across pages so you know when you've got them all.

## Credit reference
- `search_companies` / `find_similar_companies`: 1 / 5 credits per company returned (min 1 / 5).
- `includeWorkforce`: +5 credits/company.
- `search_people`: 2 credits/person (min 2).
- `enrich_person_email`: 10 credits per *found* email (not-found free).
- Counts: always `pageSize:1`. Never re-run an identical count live - the number won't change.

## Live-demo notes
- Rehearse and memorize the funnel numbers - if the API lags, narrate the answer while it loads.
- Read calls from a script; don't invent filter/department names live (they're strict enums).
- Keep it read-only until the final write/export; never trigger a blocking dialog.
- The meta-move: ask Claude to "use the build-tam skill" on stage - "this whole flow is a shareable skill," so the audience leaves with a tool, not just a recording.
