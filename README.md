# build-tam

Turn a handful of your **closed-won accounts** into a ranked, named, emailable market - by example, not by keyword.

You feed the pipeline 7-10 of your best customers. It reverse-engineers the ICP from them, expands to the whole lookalike market, scores every account into Hot / Warm / Nurture using **similarity + real workforce growth**, attaches the decision makers, and resolves their work emails. Every stage is one exact CompanyEnrich call and one output table.

```
Closed-Won Deals  ->  Reverse-Engineered ICP  ->  TAM Full (lookalike)  ->  Tier Rules
   (seeds in)          (pattern out)               (whole market)           (scoring logic)
      ->  TAM by Workforce Signal  ->  Decision Makers  ->  People + Emails
             (in-market ranking)         (personas)          (contactable)
```

Runs inside Claude Code as a skill + seven slash commands. Structure it in Airtable, or fall back to CSV with zero extra setup.

---

## Requirements

| | |
|---|---|
| **[Claude Code](https://claude.com/claude-code)** | required - the pipeline is a skill + slash commands |
| **CompanyEnrich MCP** | **required** - all company/people data. Bundled in `.mcp.json`; first connect runs OAuth login. Get an account at [companyenrich.com](https://companyenrich.com) |
| **Airtable MCP** | **optional** - nicer storage with live A/B/C views. Without it, every stage writes CSVs under `./tam-run/`. See [Storage](#storage) |
| **Python 3** | for the bulk-load / growth scripts in `scripts/` (stdlib only, no pip) |

CompanyEnrich runs on credits. A full end-to-end run on ~1,600 companies (size the market, materialize the top few hundred, tier, rank, find ~120 buyers, resolve ~35 emails) costs on the order of **5,000 credits**. Sizing the market alone is 5 credits. See the credit table in the skill.

---

## Install

### As a plugin (recommended)
```
/plugin marketplace add zeynepavan/build-tam-claude-skill
/plugin install build-tam
```
This wires up the CompanyEnrich MCP and all seven commands together. On first use Claude Code opens the CompanyEnrich OAuth login.

### Manual (guaranteed to work anywhere)
Copy the two component dirs into your Claude config, and add the MCP server:
```
cp -r skills/build-tam   ~/.claude/skills/
cp    commands/*.md      ~/.claude/commands/
```
Then add the CompanyEnrich server from `.mcp.json` to your `~/.claude.json` (or project `.mcp.json`).

### Optional: Airtable
Merge `examples/airtable.mcp.json` into your MCP config and set `AIRTABLE_API_KEY` to a personal access token (scopes: `data.records:read/write`, `schema.bases:read/write`). Skip this entirely to run in CSV mode.

---

## Run it

Verify the connection, then fire the stages in order. Each command does ONE stage, reads the previous stage's output, writes its own, and prints the next command.

```
# 0. prove it's live (free, shows your credit balance)
ask Claude: "run get_current_user"

# 1-7. the pipeline
/intelligence-segment            # pick a segment, curate 7-10 clean seeds
/reverse-engineer                # derive the ICP from the seeds
/build-lookalike                 # expand to the TAM (+ keyword-vs-lookalike contrast)
/tier-score                      # A/B/C on similarity + workforce growth
/workforce-rank                  # rank the in-market accounts by real hiring
/find-buyers                     # decision makers per persona
/get-emails                      # work emails - narrow first, this stage is the costly one
```

Start from your own closed-won book: point `/intelligence-segment` at an Airtable table whose name contains "Closed-Won", or pass a CSV path. `examples/closed_won_seeds.csv` is a ready-made starter if you just want to watch it run.

Or run the whole thing in one shot: ask Claude to **"use the build-tam skill"** and give it your seed domains.

---

## Storage

Pick one backend at Stage 1 and keep it:

- **Airtable** (if the MCP is connected) - tables persist as shared state between stages, and you get filtered Hot/Warm/Nurture views in the UI. Note: the API can't create grid views, so you add the A/B/C filtered views yourself (one table, three lenses).
- **CSV** (default when Airtable is absent) - each stage writes `./tam-run/<segment>-<stage>.csv`. Identical compute, local files.

The big `find_similar_companies` / `search_people` responses land as JSON under `tool-results/` either way; `scripts/` parses them.

---

## Scripts

Stdlib-only Python for the parts worth doing outside the assistant loop. Auth reads `$AIRTABLE_API_KEY` or the airtable MCP env in `~/.claude.json`.

```
# bulk-load rows into Airtable (retry + verify; use for >50 rows)
python scripts/airtable_load.py <baseId> <tableId> records.json

# upsert by a key column (idempotent - re-run a half-finished load safely)
python scripts/airtable_load.py <baseId> <tableId> records.json --upsert PersonID

# rank A+B accounts by workforce growth from saved tool-results -> CSV
python scripts/compute_growth.py tool-results/* --min-score 0.8 --out tam-run/by-workforce.csv
```

---

## Things that will bite you (learned the hard way)

- **`minScore` is not the score in `metadata.scores`.** It filters the engine's internal similarity; the per-item reported score is a different, blended number. Get tier membership from the `minScore` filter, and don't materialize "top N by reported score" and assume it's your ≥0.80 set - it isn't. Re-pull with `minScore` and backfill.
- **Size cheap, materialize narrow.** `pageSize:1` gives you `totalItems` for 5 credits. Results are rank-ordered by similarity, so only page down to where you'll stop caring - the long tail is Tier C by construction.
- **Reuse the workforce pull.** Pull A+B once with `includeWorkforce=true` at the tier stage; that same file feeds the workforce ranking. Don't pay 5 credits/company twice.
- **`enrich_person_email` is the expensive stage** - one call per person through the assistant loop. Narrow to the people you'll actually email first.
- **`PersonID` is an integer** - stringify it before writing to a text column or Airtable 422s even with typecast.
- **Bulk REST loads are flaky** - wrap batches in retry, then page the table back and check the count. `scripts/` already does this.

Full detail, exact calls, and the persona map live in `skills/build-tam/SKILL.md` - the single source of truth. The commands stay thin and load it.

---

## License

MIT - see [LICENSE](LICENSE). CompanyEnrich and Airtable are their respective owners' products; you bring your own accounts.
