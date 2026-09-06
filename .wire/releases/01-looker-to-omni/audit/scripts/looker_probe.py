"""Probe the Looker instance: counts, the three in-scope dashboards, and System Activity field names.

Read-only. Uses LOOKERSDK_* environment variables. Run from the repo root:
    python3 .wire/releases/01-looker-to-omni/audit/scripts/looker_probe.py
"""
import json
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402

sdk = looker_sdk.init40()

IN_SCOPE = ["267", "416", "255"]

dashboards = sdk.all_dashboards(fields="id,title,folder(id,name,is_personal),user_id,lookml_link_id,view_count,hidden,deleted")
looks = sdk.all_looks(fields="id,title,folder(id,name),user_id,view_count,model(id),query_id,deleted,public")
folders = sdk.all_folders(fields="id,name,parent_id,is_personal,is_personal_descendant,is_shared_root,is_users_root,creator_id")
plans = sdk.all_scheduled_plans(all_users=True, fields="id,name,user_id,dashboard_id,look_id,lookml_dashboard_id,enabled,crontab,destinations")
try:
    alerts = sdk.search_alerts(all_owners=True, fields="id,owner_id,dashboard_element_id,is_disabled,cron")
except Exception as e:  # noqa: BLE001
    alerts = f"error: {e}"
models = sdk.all_lookml_models(fields="name,project_name,explores(name,hidden,label),allowed_db_connection_names")

print("dashboards:", len(dashboards), " looks:", len(looks), " folders:", len(folders), " scheduled_plans:", len(plans),
      " alerts:", (len(alerts) if not isinstance(alerts, str) else alerts))
print("models:", [(m.name, m.project_name, len(m.explores or []), list(m.allowed_db_connection_names or [])) for m in models])
lookml_dash = [d for d in dashboards if d.lookml_link_id]
print("lookml-linked dashboards:", [(d.id, d.title, d.lookml_link_id) for d in lookml_dash][:20])

for did in IN_SCOPE:
    d = sdk.dashboard(did)
    els = d.dashboard_elements or []
    types = {}
    explores = set()
    models_used = set()
    for e in els:
        t = e.type
        types[t] = types.get(t, 0) + 1
        q = e.query or (e.result_maker.query if e.result_maker and e.result_maker.query else None)
        if q is not None:
            explores.add(f"{q.model}/{q.view}")
            models_used.add(q.model)
        if e.look and e.look.query:
            explores.add(f"{e.look.query.model}/{e.look.query.view}")
            models_used.add(e.look.query.model)
        if e.result_maker and e.result_maker.merge_result_id:
            types["merge_result"] = types.get("merge_result", 0) + 1
    print(f"\n== dashboard {did}: {d.title!r} folder={d.folder.name if d.folder else None} lookml_link_id={d.lookml_link_id} "
          f"updated_at={d.updated_at} view_count={d.view_count} elements={len(els)} filters={len(d.dashboard_filters or [])}")
    print("   element types:", types)
    print("   models:", sorted(models_used), " explores:", sorted(explores))
    print("   filters:", [(f.name, f.type, f.dimension, f.field and f.field.get('name') if isinstance(f.field, dict) else None) for f in (d.dashboard_filters or [])])

# System Activity field discovery
try:
    ex = sdk.lookml_model_explore("system__activity", "history", fields="fields")
    dims = [f.name for f in ex.fields.dimensions]
    meas = [f.name for f in ex.fields.measures]
    print("\nsystem__activity/history dims (subset):", [d for d in dims if d.startswith(("dashboard.", "look.", "history.")) and any(k in d for k in ("id", "date", "title", "run"))][:40])
    print("system__activity/history measures:", meas[:40])
    ex2 = sdk.lookml_model_explore("system__activity", "content_usage", fields="fields")
    print("system__activity/content_usage dims:", [f.name for f in ex2.fields.dimensions][:40])
    print("system__activity/content_usage measures:", [f.name for f in ex2.fields.measures][:40])
except Exception as e:  # noqa: BLE001
    print("\nSystem Activity not accessible:", e)
