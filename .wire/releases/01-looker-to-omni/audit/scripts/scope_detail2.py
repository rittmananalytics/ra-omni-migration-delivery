"""More detail for the plan: user attribute defaults, which tiles use parameter-driven and period-over-period fields,
schedule targets, and an alerts count via the raw API. Read-only."""
import json
import warnings

warnings.filterwarnings("ignore")
OUT = ".wire/releases/01-looker-to-omni/audit/"
perms = json.load(open(OUT + "raw/looker_permissions.json"))
content = json.load(open(OUT + "raw/looker_content.json"))

print("## user attributes with defaults")
for u in perms["user_attributes"]:
    if not u["is_system"]:
        print(f"  {u['name']:50} type={u['type']:22} default={u['default_value']!r}")

print("\n## groups by id")
for g in perms["groups"]:
    print(f"  {g['id']:>4} {g['name']:35} users={g['user_count']}")

WATCH = {"consultant_revenue_attribution", "profit_and_loss_report_fact", "monthly_resource_revenue_forecast_fact", "web_sessions_fact", "rfm_model"}
print("\n## tiles using watched views / parameter-driven fields")
for did in ("267", "255", "416"):
    d = content["dashboards"][did]
    for t in d["tiles"]:
        hits = [f for f in t["fields"] if f.split(".")[0] in WATCH and (
            "prior" in f or "dynamic" in f or "selected" in f or "period" in f or "time_range" in f or "date_filter" in f or f.startswith("consultant_revenue_attribution") or f.startswith("rfm_model"))]
        if hits:
            print(f"  {did} tile {t['id']:6} {str(t.get('title'))[:45]:45} explores={t['explores']} merge={bool(t.get('merge_result_id'))}")
            print("        fields:", hits)
            if t["listens"]:
                print("        listens:", t["listens"])
    print(f"  {did} fields containing prior/dynamic/selected/period:", sorted(f for f in d["fields"] if any(k in f for k in ("prior", "dynamic", "selected", "period", "time_range", "date_filter"))))

print("\n## schedules")
for s in content["schedules"]:
    print("  ", s)

print("\n## alerts via raw API")
try:
    import requests  # noqa: E402
    import looker_sdk  # noqa: E402
    import os  # noqa: E402

    sdk = looker_sdk.init40()
    headers = sdk.auth.authenticate()
    base = os.environ["LOOKERSDK_BASE_URL"].rstrip("/")
    r = requests.get(f"{base}/api/4.0/alerts/search", params={"all_owners": "true"}, headers=headers, timeout=60)
    print("  status", r.status_code)
    data = r.json()
    print("  count", len(data) if isinstance(data, list) else data)
    for a in (data if isinstance(data, list) else [])[:20]:
        print("   ", {k: a.get(k) for k in ("id", "owner_id", "dashboard_element_id", "is_disabled", "cron", "custom_title", "description", "field")})
    json.dump(data, open(OUT + "raw/looker_alerts.json", "w"), indent=1)
except Exception as e:  # noqa: BLE001
    print("  alerts error:", str(e)[:300])
