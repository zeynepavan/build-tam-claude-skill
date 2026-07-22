"""
Shared helpers for the build-tam pipeline. Standard library only - no pip installs.

Covers the two things worth scripting outside the assistant loop:
  1. Loading / upserting thousands of rows into Airtable via the REST API (the MCP
     write path is slow and drops the socket on big loads).
  2. Computing workforce growth from the CompanyEnrich `workforce.history[]` snapshots.

The CompanyEnrich MCP is OAuth (no scriptable key), so all *company/people* calls go
through the assistant. These helpers only touch Airtable + local tool-results files.
"""
import datetime
import json
import os
import ssl
import time
import urllib.request

API = "https://api.airtable.com/v0"


# --- auth -------------------------------------------------------------------
def get_airtable_pat():
    """PAT from $AIRTABLE_API_KEY, else the airtable MCP server's env in ~/.claude.json."""
    pat = os.environ.get("AIRTABLE_API_KEY")
    if pat:
        return pat
    cfg = os.path.expanduser("~/.claude.json")
    if os.path.exists(cfg):
        d = json.load(open(cfg))
        srv = d.get("mcpServers", {}).get("airtable", {})
        pat = srv.get("env", {}).get("AIRTABLE_API_KEY")
        if pat:
            return pat
    raise SystemExit("No Airtable PAT. Set AIRTABLE_API_KEY or add the airtable MCP server.")


def _ctx():
    # Cert verification stays ON. Some machines hit a local CERTIFICATE_VERIFY_FAILED;
    # only then, opt out explicitly with TAM_INSECURE_SSL=1.
    if os.environ.get("TAM_INSECURE_SSL") == "1":
        c = ssl.create_default_context()
        c.check_hostname = False
        c.verify_mode = ssl.CERT_NONE
        return c
    return ssl.create_default_context()


def _req(method, url, pat, body=None):
    data = json.dumps(body).encode() if body is not None else None
    hdr = {"Authorization": f"Bearer {pat}", "Content-Type": "application/json"}
    return urllib.request.Request(url, data=data, headers=hdr, method=method)


# --- Airtable write path ----------------------------------------------------
def _send_batches(base, table, records, pat, method, extra):
    """POST/PATCH records in batches of 10, each with retry+backoff. Returns count sent."""
    url = f"{API}/{base}/{table}"
    ctx = _ctx()
    done = 0
    for i in range(0, len(records), 10):
        batch = records[i:i + 10]
        body = {"records": batch, "typecast": True, **extra}
        req = _req(method, url, pat, body)
        for attempt in range(5):
            try:
                urllib.request.urlopen(req, timeout=45, context=ctx).read()
                done += len(batch)
                break
            except urllib.error.HTTPError as e:
                # 4xx won't fix itself - surface it.
                raise SystemExit(f"HTTP {e.code} at row {i}: {e.read().decode()[:300]}")
            except Exception as e:
                if attempt == 4:
                    print(f"  FAILED batch at row {i}: {type(e).__name__}")
                else:
                    time.sleep(2 * (attempt + 1))  # transient SSL/DNS - back off
        time.sleep(0.2)
    return done


def airtable_create(base, table, records, pat=None):
    """Insert rows. records = [{'fields': {...}}]. Stringify integer IDs first."""
    pat = pat or get_airtable_pat()
    return _send_batches(base, table, records, pat, "POST", {})


def airtable_upsert(base, table, records, merge_on, pat=None):
    """Upsert by a key column. merge_on = ['ColumnName']. Idempotent - safe to re-run.
    NOTE the REST key is `fieldsToMergeOn` (NOT fieldIdsToMergeOn, which 422s)."""
    pat = pat or get_airtable_pat()
    return _send_batches(base, table, records, pat, "PATCH",
                         {"performUpsert": {"fieldsToMergeOn": merge_on}})


def page_table(base, table, pat=None):
    """Read every row back (for post-load verification). Returns list of records."""
    pat = pat or get_airtable_pat()
    ctx = _ctx()
    out, offset = [], None
    while True:
        url = f"{API}/{base}/{table}?pageSize=100" + (f"&offset={offset}" if offset else "")
        d = json.loads(urllib.request.urlopen(_req("GET", url, pat), timeout=45, context=ctx).read())
        out += d["records"]
        offset = d.get("offset")
        if not offset:
            break
    return out


# --- workforce growth -------------------------------------------------------
def compute_growth(workforce, days=365, tol_days=120):
    """y-o-y style growth from a CompanyEnrich `workforce` object.
    latest observed count vs the snapshot closest to `days` ago. Returns % or None.
    None when there is no snapshot within tol_days of the target, or the base is 0
    (a company with only 6 months of history must not report a fake number)."""
    if not workforce:
        return None
    pts = sorted(
        (str(p["date"])[:10], p["observed_employee_count"])
        for p in (workforce.get("history") or [])
        if p.get("date") and p.get("observed_employee_count") is not None
    )
    if len(pts) < 2:
        return None
    last_d = datetime.date.fromisoformat(pts[-1][0])
    target = last_d - datetime.timedelta(days=days)
    base = min(pts, key=lambda p: abs((datetime.date.fromisoformat(p[0]) - target).days))
    if abs((datetime.date.fromisoformat(base[0]) - target).days) > tol_days or base[1] == 0:
        return None
    return round((pts[-1][1] - base[1]) / base[1] * 100, 1)


# --- tool-results parsing ---------------------------------------------------
def load_items(paths):
    """Dedupe CompanyEnrich items by id across one or more saved tool-results JSON files.
    Returns {id: {'score': float|None, 'item': {...}}}. `totalItems` is stable across
    pages, so the first file tells you the market size."""
    rows = {}
    for path in paths:
        d = json.load(open(path))
        scores = (d.get("metadata") or {}).get("scores", {})
        for it in d.get("items", []):
            rows.setdefault(it["id"], {"score": scores.get(it["id"]), "item": it})
    return rows
