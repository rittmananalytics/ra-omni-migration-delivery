"""Alerts via raw API, and the source queries behind Business Summary tile 2501. Read-only."""
import json
import os
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402
import requests  # noqa: E402
from looker_sdk.rtl import transport  # noqa: E402

OUT = ".wire/releases/01-looker-to-omni/audit/"
sdk = looker_sdk.init40()

print("## alerts via raw API")
try:
    headers = sdk.auth.authenticate(transport.TransportOptions())
    base = os.environ["LOOKERSDK_BASE_URL"].rstrip("/")
    r = requests.get(f"{base}/api/4.0/alerts/search", params={"all_owners": "true"}, headers=dict(headers), timeout=60)
    print("  status", r.status_code)
    data = r.json()
    print("  count", len(data) if isinstance(data, list) else data)
    for a in (data if isinstance(data, list) else []):
        print("   ", {k: a.get(k) for k in ("id", "owner_id", "dashboard_element_id", "is_disabled", "cron", "custom_title", "description")}, (a.get("field") or {}).get("name"))
    json.dump(data, open(OUT + "raw/looker_alerts.json", "w"), indent=1)
except Exception as e:  # noqa: BLE001
    print("  alerts error:", str(e)[:300])

print("\n## tile 2501 (Business Summary) merge sources")
dd = json.load(open(OUT + "raw/dashboard_267.json"))
for e in dd["dashboard_elements"]:
    if str(e["id"]) == "2501":
        mid = e.get("merge_result_id") or (e.get("result_maker") or {}).get("merge_result_id")
        print("  merge_result_id", mid, "title", e.get("title"))
        m = sdk.merge_query(mid)
        for sq in m.source_queries or []:
            q = sdk.query(sq.query_id)
            print(f"   source query {sq.query_id}: model={q.model} explore={q.view} fields={list(q.fields or [])} filters={q.filters} dyn={(q.dynamic_fields or '')[:200]}")
        print("   merge fields:", [json.loads(json.dumps(sq.__dict__, default=str)).get("merge_fields") for sq in (m.source_queries or [])])

print("\n## explores that join consultant_revenue_attribution or project_attribution")
summ = json.load(open(OUT + "raw/lookml_parsed_summary.json"))
for e, x in summ["explores"].items():
    if "consultant_revenue_attribution" in x["views_reached"] or e == "project_attribution":
        print("  ", e, x["base_view"], x["views_reached"][:10], "hidden", x["hidden"])
print("  view consultant_revenue_attribution:", summ["views"].get("consultant_revenue_attribution", {}).get("construct"), summ["views"].get("consultant_revenue_attribution", {}).get("file"))
