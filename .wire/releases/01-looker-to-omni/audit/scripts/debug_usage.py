"""Debug helper: try System Activity dashboard usage query variants and print row counts and samples. Read-only."""
import json
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402
from looker_sdk import models40 as mdl  # noqa: E402

sdk = looker_sdk.init40()


def run(fields, filters, limit="20"):
    q = mdl.WriteQuery(model="system__activity", view="history", fields=fields, filters=filters, limit=limit)
    try:
        rows = json.loads(sdk.run_inline_query("json", q))
        print(f"\n{fields} {filters} -> {len(rows)} rows; sample: {rows[:3]}")
        return rows
    except Exception as e:  # noqa: BLE001
        print(f"\n{fields} {filters} -> ERROR {str(e)[:300]}")
        return []


run(["history.real_dash_id", "history.dashboard_run_count"], {})
run(["dashboard.id", "history.dashboard_run_count", "history.most_recent_query_date"], {"dashboard.id": "NOT NULL"})
run(["history.dashboard_id", "history.dashboard_run_count"], {"history.dashboard_id": "-NULL"})
run(["dashboard.id", "history.dashboard_run_count"], {"history.created_date": "90 days", "dashboard.id": "NOT NULL"})
rows = run(["dashboard.id", "history.dashboard_run_count"], {"history.created_date": "90 days"}, limit="5000")
print("distinct dashboards with runs in 90d:", len({r["dashboard.id"] for r in rows if r.get("dashboard.id") is not None}))

detail = json.load(open(".wire/releases/01-looker-to-omni/audit/raw/looker_content.json"))
print("\nalerts:", str(detail["alerts"])[:300])
for did in ("267", "416", "255"):
    d = detail["dashboards"][did]
    types = {}
    for t in d["tiles"]:
        types[t["type"]] = types.get(t["type"], 0) + 1
    print(f"\n== {did} {d['title']!r}: tiles={len(d['tiles'])} types={types} explores={d['explores']} fields={len(d['fields'])} "
          f"last_viewed={d['last_viewed']} views_90d={d['views_90d']} api_view_count={d['view_count_api']}")
    for t in d["tiles"]:
        if t["type"] != "vis" or t.get("merge_result_id") or t.get("dynamic_fields") or (t.get("vis_type") and not str(t["vis_type"]).startswith(("looker_", "single_value", "table"))):
            print("   ", t["id"], t["type"], t.get("vis_type"), (t.get("title") or "")[:40], "merge" if t.get("merge_result_id") else "",
                  ("dyn:" + ";".join(t["dynamic_fields"])[:120]) if t.get("dynamic_fields") else "", "look:" + str(t["look_id"]) if t.get("look_id") else "")
