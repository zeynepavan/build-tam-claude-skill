---
description: Stage 7 of build-tam - resolve work emails for a chosen subset of decision makers (the token-heavy final stage - narrow first).
argument-hint: [subset, e.g. "P1" (GTM+Technical) or "top20"]
---

You are running **Stage 7 (Work Emails)** of the `build-tam` pipeline. Load the `build-tam` skill.

**Read the cost warning first:** `enrich_person_email` is one call PER person, each returns a large object, and there is no scriptable CompanyEnrich key (OAuth MCP), so every call flows through the assistant loop and burns Claude usage. NARROW before you run.

Steps:
1. From the **`<Segment> - Decision Makers (People)`** table, select the subset from `$ARGUMENTS`:
   - default `P1` = GTM Economic Buyer + Technical Champion (the budget holder + technical yes/no).
   - or `top20` = only people at the top-20 workforce-growth accounts.
   Confirm the count and rough credit cost (10 credits per *found* email; ~55-60% hit rate) before spending.
2. Call `enrich_person_email(id=<PersonID>, domain=<Domain>)` in big batches (~30/turn, not 5). Collect `status:found` emails; not-found is free.
3. Write the emails back onto the People rows, keyed by PersonID:
   - **Airtable:** upsert with `python <scripts dir>/airtable_load.py <base> <table> emails.json --upsert PersonID`, where `<scripts dir>` is `${CLAUDE_PLUGIN_ROOT}/scripts` for a plugin install or `~/.claude/skills/build-tam/scripts` for a manual one (REST PATCH, key is `fieldsToMergeOn` NOT `fieldIdsToMergeOn`).
   - **CSV:** fill the `Email` / `Email Status` columns in `./tam-run/<segment>-people.csv` for the matched PersonIDs.
4. Report: emails found / attempted, companies covered, credits spent.

This is the finish line: the TAM is now a named, contactable, prioritized list, ready to hand to your outreach tool or cold-email workflow.
