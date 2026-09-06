"""Second probe: the three in-scope dashboards in detail, and System Activity field names.

Read-only. Run from the repo root:
    python3 .wire/releases/01-looker-to-omni/audit/scripts/looker_probe2.py
"""
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402

sdk = looker_sdk.init40()
IN_SCOPE = ["267", "416", "255"]

for did in IN_SCOPE:
    d = sdk.dashboard(did)
    els = d.dashboard_elements or []
    types = {}
    explores = set()
    for e in els:
        types[e.type] = types.get(e.type, 0) + 1
        q = e.query
        if q is None and e.result_maker is not None and e.result_maker.query is not None:
            q = e.result_maker.query
        if q is not None:
            explores.add(f"{q.model}/{q.view}")
        if e.look is not None and e.look.query is not None:
            explores.add(f"{e.look.query.model}/{e.look.query.view}")
        if e.result_maker is not None and e.result_maker.merge_result_id:
            types["merge_result"] = types.get("merge_result", 0) + 1
    print(f"== dashboard {did}: {d.title!r} folder={d.folder.name if d.folder else None} lookml_link_id={d.lookml_link_id} "
          f"updated_at={d.updated_at} view_count={d.view_count} elements={len(els)} filters={len(d.dashboard_filters or [])}")
    print("   element types:", types)
    print("   explores:", sorted(explores))
    print("   filters:", [(f.name, f.type, f.dimension) for f in (d.dashboard_filters or [])])

for explore in ("history", "content_usage"):
    try:
        ex = sdk.lookml_model_explore("system__activity", explore, fields="fields")
        dims = [f.name for f in ex.fields.dimensions]
        meas = [f.name for f in ex.fields.measures]
        keep = [n for n in dims if n.split(".")[0] in ("dashboard", "look", "history", "content_usage") and any(k in n for k in ("id", "date", "title", "count", "run", "view"))]
        print(f"\nsystem__activity/{explore} dimensions of interest:", keep)
        print(f"system__activity/{explore} measures:", meas)
    except Exception as e:  # noqa: BLE001
        print(f"\nSystem Activity {explore} not accessible:", e)
