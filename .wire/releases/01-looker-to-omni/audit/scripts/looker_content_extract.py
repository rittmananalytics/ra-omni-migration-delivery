"""Catalog Looker content (dashboards, Looks, tiles, filters, schedules, alerts, folders) with usage from System Activity.

Read-only against the Looker API 4.0 (LOOKERSDK_* environment variables). Deterministic output ordering.

Usage (from the repo root):
    python3 looker_content_extract.py <audit_out_dir> <lookml_project_name> <in_scope_dashboard_ids_csv>

Writes:
    <audit_out_dir>/looker_content_catalog.csv
    <audit_out_dir>/dependencies.jsonl          (content-side edges: contains, uses_explore, references, listens)
    <audit_out_dir>/raw/looker_content.json     (compact per-object detail for every dashboard and Look)
    <audit_out_dir>/raw/dashboard_<id>.json     (full API payload for each in-scope dashboard)
"""
import csv
import json
import os
import re
import sys
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402
from looker_sdk import models40 as mdl  # noqa: E402

OUT = sys.argv[1].rstrip("/") + "/"
PROJECT = sys.argv[2] if len(sys.argv) > 2 else "analytics"
IN_SCOPE = set((sys.argv[3] if len(sys.argv) > 3 else "").split(",")) - {""}
os.makedirs(OUT + "raw", exist_ok=True)

sdk = looker_sdk.init40()
FIELD_REF = re.compile(r"\$\{([A-Za-z_][\w]*)\.([A-Za-z_]\w*)\}")


def to_dict(obj):
    """Recursively convert an SDK model object to plain JSON-safe Python values."""
    import datetime
    import enum

    def conv(o):
        if o is None or isinstance(o, (str, int, float, bool)):
            return o
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple, set)):
            return [conv(v) for v in o]
        if hasattr(o, "__dict__"):
            return {k: conv(v) for k, v in vars(o).items() if not k.startswith("_") and v is not None}
        return str(o)

    return conv(obj)


def uri_dash(i):
    return f"looker:{PROJECT}:dashboard:{i}"


def uri_el(d, e):
    return f"looker:{PROJECT}:dashboard:{d}/element:{e}"


def uri_dfilter(d, name):
    return f"looker:{PROJECT}:dashboard:{d}/filter:{name}"


def uri_look(i):
    return f"looker:{PROJECT}:look:{i}"


def uri_explore(model, explore):
    return f"looker:{PROJECT}:explore:{explore}" if model == PROJECT else f"looker:{model}:explore:{explore}"


def uri_field(model, view, field):
    return f"looker:{PROJECT}:field:{view}:{field}" if model == PROJECT else f"looker:{model}:field:{view}:{field}"


def qfields(q):
    """Return (explore_ref, set of 'view.field' refs, dynamic field notes, vis_type, limit) for a Query object/dict."""
    if q is None:
        return None, set(), [], None
    qd = q if isinstance(q, dict) else to_dict(q)
    refs = set()
    for f in qd.get("fields") or []:
        refs.add(f)
    for f in (qd.get("filters") or {}).keys():
        refs.add(f)
    for f in qd.get("pivots") or []:
        refs.add(f)
    for f in qd.get("fill_fields") or []:
        refs.add(f)
    for s in qd.get("sorts") or []:
        refs.add(s.split(" ")[0])
    dyn_notes = []
    dyn = qd.get("dynamic_fields")
    if dyn:
        try:
            dyn_list = json.loads(dyn) if isinstance(dyn, str) else dyn
        except Exception:  # noqa: BLE001
            dyn_list = []
        for d in dyn_list or []:
            cat = d.get("category") or ("table_calculation" if "table_calculation" in d else "custom")
            expr = d.get("expression") or d.get("filter_expression") or ""
            for m in FIELD_REF.finditer(str(expr)):
                refs.add(f"{m.group(1)}.{m.group(2)}")
            if d.get("based_on"):
                refs.add(d["based_on"])
            for k, v in (d.get("filters") or {}).items() if isinstance(d.get("filters"), dict) else []:
                refs.add(k)
            dyn_notes.append(f"{cat}:{d.get('label') or d.get('table_calculation') or d.get('measure') or d.get('dimension')}")
    vis_type = (qd.get("vis_config") or {}).get("type")
    explore_ref = f"{qd.get('model')}/{qd.get('view')}" if qd.get("model") and qd.get("view") else None
    return explore_ref, {r for r in refs if r and "." in r}, dyn_notes, vis_type


# Users for owner names
users = {}
try:
    for u in sdk.all_users(fields="id,display_name,email,is_disabled"):
        users[str(u.id)] = {"name": u.display_name or u.email or str(u.id), "disabled": bool(u.is_disabled)}
except Exception as e:  # noqa: BLE001
    print("all_users failed:", e)


def owner_name(uid):
    if uid is None:
        return ""
    u = users.get(str(uid))
    if not u:
        return str(uid)
    return u["name"] + (" (disabled)" if u["disabled"] else "")


# Folders
folders = {}
for f in sdk.all_folders(fields="id,name,parent_id,is_personal,is_personal_descendant,is_shared_root,is_users_root,creator_id,content_metadata_id"):
    folders[str(f.id)] = {"id": str(f.id), "name": f.name, "parent_id": f.parent_id, "is_personal": bool(f.is_personal),
                          "is_personal_descendant": bool(f.is_personal_descendant), "creator_id": f.creator_id}


def folder_path(fid):
    parts, seen = [], set()
    while fid and str(fid) in folders and str(fid) not in seen:
        seen.add(str(fid))
        parts.append(folders[str(fid)]["name"])
        fid = folders[str(fid)]["parent_id"]
    return "/".join(reversed(parts))


# System Activity usage
usage_source = "system_activity"
dash_usage, look_usage = {}, {}


def run_sa(view, fields, filters):
    q = mdl.WriteQuery(model="system__activity", view=view, fields=fields, filters=filters, limit="50000")
    res = sdk.run_inline_query("json", q)
    return json.loads(res)


def clean_id(v):
    if v is None:
        return None
    s = str(v)
    return s[:-2] if s.endswith(".0") else s


try:
    # history.real_dash_id resolves both user-defined (numeric) and LookML (model::name) dashboards. No id filter:
    # the field is a string and Looker rejects number-filter syntax on it; None keys are skipped instead.
    for r in run_sa("history", ["history.real_dash_id", "history.dashboard_run_count", "history.most_recent_query_date"], {}):
        k = clean_id(r.get("history.real_dash_id"))
        if k:
            dash_usage[k] = {"views_all": r["history.dashboard_run_count"], "last_viewed": r["history.most_recent_query_date"], "views_90d": 0}
    for r in run_sa("history", ["history.real_dash_id", "history.dashboard_run_count"], {"history.created_date": "90 days"}):
        k = clean_id(r.get("history.real_dash_id"))
        if k:
            dash_usage.setdefault(k, {"views_all": None, "last_viewed": None})["views_90d"] = r["history.dashboard_run_count"]
    for r in run_sa("history", ["look.id", "history.count", "history.most_recent_query_date"], {}):
        k = clean_id(r.get("look.id"))
        if k:
            look_usage[k] = {"views_all": r["history.count"], "last_viewed": r["history.most_recent_query_date"], "views_90d": 0}
    for r in run_sa("history", ["look.id", "history.count"], {"history.created_date": "90 days"}):
        k = clean_id(r.get("look.id"))
        if k:
            look_usage.setdefault(k, {"views_all": None, "last_viewed": None})["views_90d"] = r["history.count"]
except Exception as e:  # noqa: BLE001
    usage_source = "unavailable"
    print("System Activity unavailable:", e)


def usage_for(kind, i):
    src = dash_usage if kind == "dashboard" else look_usage
    if usage_source != "system_activity":
        return "unknown", "unknown"
    u = src.get(str(i))
    if not u:
        return "never", 0
    return (u.get("last_viewed") or "never"), (u.get("views_90d") or 0)


rows, edges, detail = [], [], {"dashboards": {}, "looks": {}, "folders": folders, "schedules": [], "alerts": None, "usage_source": usage_source}
merge_cache, query_cache = {}, {}


def get_query(qid):
    if qid not in query_cache:
        query_cache[qid] = to_dict(sdk.query(qid))
    return query_cache[qid]


def merge_sources(mid):
    if mid not in merge_cache:
        try:
            m = to_dict(sdk.merge_query(mid))
            merge_cache[mid] = [get_query(sq["query_id"]) for sq in (m.get("source_queries") or []) if sq.get("query_id")]
        except Exception as e:  # noqa: BLE001
            merge_cache[mid] = []
            print("merge_query failed", mid, e)
    return merge_cache[mid]


# Dashboards
all_dash = sdk.all_dashboards(fields="id,title")
for base in sorted(all_dash, key=lambda d: (len(str(d.id)), str(d.id))):
    did = str(base.id)
    try:
        d = sdk.dashboard(did)
    except Exception as e:  # noqa: BLE001
        print("dashboard failed", did, e)
        continue
    dd = to_dict(d)
    if did in IN_SCOPE:
        json.dump(dd, open(OUT + f"raw/dashboard_{did}.json", "w"), indent=1, sort_keys=True)
    els = dd.get("dashboard_elements") or []
    filters = dd.get("dashboard_filters") or []
    explore_refs, field_refs = set(), set()
    has_text = False
    tiles = []
    for e in els:
        etype = e.get("type")
        eid = str(e.get("id"))
        el_explores, el_fields, el_dyn, vis_type, reasons = set(), set(), [], None, []
        if etype == "text":
            has_text = True
        q = e.get("query") or ((e.get("result_maker") or {}).get("query"))
        if q is None and e.get("look") and e["look"].get("query"):
            q = e["look"]["query"]
        if q:
            ex, fr, dyn, vt = qfields(q)
            if ex:
                el_explores.add(ex)
            el_fields |= fr
            el_dyn += dyn
            vis_type = vt or vis_type
        mid = e.get("merge_result_id") or (e.get("result_maker") or {}).get("merge_result_id")
        if mid:
            reasons.append("merged_results")
            for sq in merge_sources(mid):
                ex, fr, dyn, vt = qfields(sq)
                if ex:
                    el_explores.add(ex)
                el_fields |= fr
                el_dyn += dyn
            rm_vis = (e.get("result_maker") or {}).get("vis_config") or {}
            vis_type = vis_type or rm_vis.get("type")
        if e.get("look_id"):
            reasons.append(f"look:{e['look_id']}")
        listens = []
        for fa in ((e.get("result_maker") or {}).get("filterables") or []):
            for li in (fa.get("listen") or []):
                listens.append((li.get("dashboard_filter_name"), li.get("field")))
                if li.get("field"):
                    el_fields.add(li["field"])
        if el_dyn:
            reasons.append("dynamic_fields:" + ";".join(el_dyn)[:200])
        if vis_type and not vis_type.startswith(("looker_", "single_value", "table")) and vis_type not in ("text", "button"):
            reasons.append(f"custom_vis:{vis_type}")
        cls, reason = "mechanical", "; ".join(reasons)
        if etype == "text":
            cls, reason = "drop", "text tile, recreate by hand"
        elif etype not in ("vis", None):
            reason = (reason + "; " if reason else "") + f"element type {etype}"
        rows.append({"object_type": "tile", "object_uri": uri_el(did, eid), "id": eid, "title": e.get("title") or e.get("title_text") or "",
                     "folder": folder_path((dd.get("folder") or {}).get("id")), "owner": owner_name(dd.get("user_id")),
                     "last_viewed": "", "views_90d": "", "source_updated_at": dd.get("updated_at"), "tile_count": "",
                     "explore_refs": ";".join(sorted(el_explores)), "fields_refs": ";".join(sorted(el_fields)),
                     "has_text_tile": str(etype == "text").lower(), "translation_class": cls, "reason": reason.replace("|", "—")})
        edges.append({"from": uri_dash(did), "to": uri_el(did, eid), "kind": "contains"})
        for ex in el_explores:
            m, v = ex.split("/", 1)
            edges.append({"from": uri_el(did, eid), "to": uri_explore(m, v), "kind": "uses_explore"})
        for fr in el_fields:
            v, f = fr.split(".", 1)
            m = next(iter(el_explores)).split("/")[0] if el_explores else PROJECT
            edges.append({"from": uri_el(did, eid), "to": uri_field(m, v, f), "kind": "references"})
        for fname, fld in listens:
            edges.append({"from": uri_el(did, eid), "to": uri_dfilter(did, fname), "kind": "listens"})
        explore_refs |= el_explores
        field_refs |= el_fields
        tiles.append({"id": eid, "title": e.get("title"), "type": etype, "vis_type": vis_type, "explores": sorted(el_explores),
                      "fields": sorted(el_fields), "dynamic_fields": el_dyn, "merge_result_id": mid, "look_id": e.get("look_id"),
                      "listens": listens, "body_text": (e.get("body_text") or "")[:500] if etype == "text" else None})
    for f in filters:
        edges.append({"from": uri_dash(did), "to": uri_dfilter(did, f.get("name")), "kind": "contains"})
        if f.get("dimension"):
            field_refs.add(f["dimension"])
    last_viewed, views_90d = usage_for("dashboard", dd.get("lookml_link_id") or did)
    if dd.get("lookml_link_id"):
        lv2, v2 = usage_for("dashboard", did)
        if v2 and v2 != "unknown" and (views_90d == 0 or views_90d == "unknown"):
            last_viewed, views_90d = lv2, v2
    folder = dd.get("folder") or {}
    fpath = folder_path(folder.get("id"))
    reason = []
    if dd.get("lookml_link_id"):
        reason.append(f"lookml dashboard {dd['lookml_link_id']}")
    if folders.get(str(folder.get("id")), {}).get("is_personal") or folders.get(str(folder.get("id")), {}).get("is_personal_descendant"):
        reason.append("folder_kind: personal")
    if users.get(str(dd.get("user_id")), {}).get("disabled"):
        reason.append("owner_active: false")
    if dd.get("deleted"):
        reason.append("deleted")
    rows.append({"object_type": "dashboard", "object_uri": uri_dash(did), "id": did, "title": dd.get("title") or "", "folder": fpath,
                 "owner": owner_name(dd.get("user_id")), "last_viewed": last_viewed, "views_90d": views_90d,
                 "source_updated_at": dd.get("updated_at"), "tile_count": len([t for t in tiles if t["type"] != "filter"]),
                 "explore_refs": ";".join(sorted(explore_refs)), "fields_refs": ";".join(sorted(field_refs)),
                 "has_text_tile": str(has_text).lower(), "translation_class": "mechanical", "reason": "; ".join(reason).replace("|", "—")})
    detail["dashboards"][did] = {"id": did, "title": dd.get("title"), "folder": fpath, "folder_id": folder.get("id"), "owner": owner_name(dd.get("user_id")),
                                 "lookml_link_id": dd.get("lookml_link_id"), "updated_at": dd.get("updated_at"), "view_count_api": dd.get("view_count"),
                                 "last_viewed": last_viewed, "views_90d": views_90d, "deleted": dd.get("deleted"), "hidden": dd.get("hidden"),
                                 "filters": [{"name": f.get("name"), "type": f.get("type"), "dimension": f.get("dimension"), "default": f.get("default_value"),
                                              "model": f.get("model"), "explore": f.get("explore"), "ui_config": f.get("ui_config")} for f in filters],
                                 "explores": sorted(explore_refs), "fields": sorted(field_refs), "tiles": tiles}

# Looks
for base in sorted(sdk.all_looks(fields="id,title"), key=lambda l: (len(str(l.id)), str(l.id))):
    lid = str(base.id)
    try:
        lk = to_dict(sdk.look(lid))
    except Exception as e:  # noqa: BLE001
        print("look failed", lid, e)
        continue
    ex, fr, dyn, vt = qfields(lk.get("query"))
    last_viewed, views_90d = usage_for("look", lid)
    folder = lk.get("folder") or {}
    fpath = folder_path(folder.get("id"))
    reason = []
    if folders.get(str(folder.get("id")), {}).get("is_personal") or folders.get(str(folder.get("id")), {}).get("is_personal_descendant"):
        reason.append("folder_kind: personal")
    if users.get(str(lk.get("user_id")), {}).get("disabled"):
        reason.append("owner_active: false")
    if dyn:
        reason.append("dynamic_fields:" + ";".join(dyn)[:200])
    if vt and not vt.startswith(("looker_", "single_value", "table")):
        reason.append(f"custom_vis:{vt}")
    rows.append({"object_type": "look", "object_uri": uri_look(lid), "id": lid, "title": lk.get("title") or "", "folder": fpath,
                 "owner": owner_name(lk.get("user_id")), "last_viewed": last_viewed, "views_90d": views_90d,
                 "source_updated_at": lk.get("updated_at"), "tile_count": "", "explore_refs": ex or "", "fields_refs": ";".join(sorted(fr)),
                 "has_text_tile": "false", "translation_class": "mechanical", "reason": "; ".join(reason).replace("|", "—")})
    if ex:
        m, v = ex.split("/", 1)
        edges.append({"from": uri_look(lid), "to": uri_explore(m, v), "kind": "uses_explore"})
        for f in fr:
            vv, ff = f.split(".", 1)
            edges.append({"from": uri_look(lid), "to": uri_field(m, vv, ff), "kind": "references"})
    detail["looks"][lid] = {"id": lid, "title": lk.get("title"), "folder": fpath, "owner": owner_name(lk.get("user_id")), "updated_at": lk.get("updated_at"),
                            "explore": ex, "fields": sorted(fr), "dynamic_fields": dyn, "vis_type": vt, "last_viewed": last_viewed, "views_90d": views_90d,
                            "used_on_dashboards": []}

# Folders as rows
for fid, f in sorted(folders.items(), key=lambda kv: (len(kv[0]), kv[0])):
    rows.append({"object_type": "folder", "object_uri": f"looker:{PROJECT}:folder:{fid}", "id": fid, "title": f["name"], "folder": folder_path(f["parent_id"]),
                 "owner": owner_name(f["creator_id"]), "last_viewed": "", "views_90d": "", "source_updated_at": "", "tile_count": "",
                 "explore_refs": "", "fields_refs": "", "has_text_tile": "false", "translation_class": "mechanical",
                 "reason": "folder_kind: personal" if (f["is_personal"] or f["is_personal_descendant"]) else ""})

# Schedules
for p in sdk.all_scheduled_plans(all_users=True):
    pd = to_dict(p)
    target = pd.get("dashboard_id") or pd.get("look_id") or pd.get("lookml_dashboard_id")
    kind = "dashboard" if pd.get("dashboard_id") or pd.get("lookml_dashboard_id") else "look"
    dests = ";".join(f"{d.get('type')}:{d.get('address')}" for d in (pd.get("scheduled_plan_destination") or []))
    rows.append({"object_type": "schedule", "object_uri": f"looker:{PROJECT}:schedule:{pd.get('id')}", "id": str(pd.get("id")), "title": pd.get("name") or "",
                 "folder": "", "owner": owner_name(pd.get("user_id")), "last_viewed": pd.get("last_run_at") or "", "views_90d": "",
                 "source_updated_at": pd.get("updated_at"), "tile_count": "", "explore_refs": f"{kind}:{target}", "fields_refs": "",
                 "has_text_tile": "false", "translation_class": "mechanical",
                 "reason": f"crontab {pd.get('crontab')}; enabled {pd.get('enabled')}; destinations {dests}".replace("|", "—")})
    detail["schedules"].append({"id": pd.get("id"), "name": pd.get("name"), "target": f"{kind}:{target}", "owner": owner_name(pd.get("user_id")),
                                "crontab": pd.get("crontab"), "enabled": pd.get("enabled"), "destinations": dests, "last_run_at": pd.get("last_run_at")})

# Alerts (raw, the typed SDK call fails to deserialise on this instance)
try:
    raw = sdk.get("/alerts/search", None, {"all_owners": True})
    alerts = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
    detail["alerts"] = alerts
    for a in alerts or []:
        rows.append({"object_type": "alert", "object_uri": f"looker:{PROJECT}:alert:{a.get('id')}", "id": str(a.get("id")), "title": a.get("custom_title") or a.get("description") or "",
                     "folder": "", "owner": owner_name(a.get("owner_id")), "last_viewed": "", "views_90d": "", "source_updated_at": "",
                     "tile_count": "", "explore_refs": f"element:{a.get('dashboard_element_id')}", "fields_refs": (a.get("field") or {}).get("name", "") if isinstance(a.get("field"), dict) else "",
                     "has_text_tile": "false", "translation_class": "mechanical", "reason": f"cron {a.get('cron')}; disabled {a.get('is_disabled')}"})
except Exception as e:  # noqa: BLE001
    detail["alerts"] = f"unknown: {str(e)[:200]}"
    print("alerts unavailable:", str(e)[:200])

# Look usage on dashboards
for did, dd in detail["dashboards"].items():
    for t in dd["tiles"]:
        if t.get("look_id") and str(t["look_id"]) in detail["looks"]:
            detail["looks"][str(t["look_id"])]["used_on_dashboards"].append(did)

ORDER = ["dashboard", "look", "tile", "schedule", "alert", "folder"]
rows.sort(key=lambda r: (ORDER.index(r["object_type"]), len(str(r["id"])), str(r["id"]), r["object_uri"]))
with open(OUT + "looker_content_catalog.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["object_type", "object_uri", "id", "title", "folder", "owner", "last_viewed", "views_90d", "source_updated_at",
                                       "tile_count", "explore_refs", "fields_refs", "has_text_tile", "translation_class", "reason"])
    w.writeheader()
    w.writerows(rows)
uniq = sorted({json.dumps(e, sort_keys=True) for e in edges}, key=lambda s: (json.loads(s)["kind"], json.loads(s)["from"], json.loads(s)["to"]))
with open(OUT + "dependencies.jsonl", "w") as fh:
    for e in uniq:
        fh.write(e + "\n")
json.dump(detail, open(OUT + "raw/looker_content.json", "w"), indent=1, sort_keys=True, default=str)
from collections import Counter  # noqa: E402

print(json.dumps({"usage_source": usage_source, "rows_by_type": dict(Counter(r["object_type"] for r in rows)), "edges": len(uniq),
                  "users": len(users), "dash_usage_rows": len(dash_usage), "look_usage_rows": len(look_usage)}, indent=1))
