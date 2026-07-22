#!/usr/bin/env python3
"""
Bulk-load or upsert records into an Airtable table via the REST API.
Use this instead of the Airtable MCP for anything over ~50 rows - the MCP write
path is slow and drops the socket on big loads. Each batch retries on transient
SSL/DNS errors, and the load is verified by paging the table back afterward.

Usage:
  # insert
  python scripts/airtable_load.py <baseId> <tableId> records.json
  # upsert by a key column (idempotent - safe to re-run a half-finished load)
  python scripts/airtable_load.py <baseId> <tableId> records.json --upsert PersonID

records.json is a list of {"fields": {...}} objects. Field NAMES or IDs both work.
Stringify integer IDs (e.g. PersonID) before writing to a text column, or Airtable
422s even with typecast. Auth: $AIRTABLE_API_KEY, or the airtable MCP env in ~/.claude.json.
"""
import json
import sys

import tam_lib

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, table, records_file = argv[0], argv[1], argv[2]
    merge_on = None
    if "--upsert" in argv:
        merge_on = argv[argv.index("--upsert") + 1]

    records = json.load(open(records_file))
    if records and "fields" not in records[0]:
        records = [{"fields": r} for r in records]  # accept bare dicts too

    if merge_on:
        sent = tam_lib.airtable_upsert(base, table, records, [merge_on])
    else:
        sent = tam_lib.airtable_create(base, table, records)
    print(f"sent {sent} of {len(records)} records")

    rows = tam_lib.page_table(base, table)
    print(f"table now holds {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
