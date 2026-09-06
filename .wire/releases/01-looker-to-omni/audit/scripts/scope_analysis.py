"""Compute the in-scope model set for the three dashboards, the drop list, and unresolved references.

Deterministic. Reads the audit catalogs and raw extracts; writes raw/scope_analysis.json.

Usage (from the repo root):
    python3 scope_analysis.py <audit_out_dir> <in_scope_dashboard_ids_csv>
"""
import csv
import json
import sys
from collections import Counter, defaultdict

OUT = sys.argv[1].rstrip("/") + "/"
IN_SCOPE = [x for x in sys.argv[2].split(",") if x]

model = list(csv.DictReader(open(OUT + "looker_model_catalog.csv")))
summary = json.load(open(OUT + "raw/lookml_parsed_summary.json"))
content = json.load(open(OUT + "raw/looker_content.json"))

views = summary["views"]
explores = summary["explores"]
field_rows = defaultdict(dict)  # view -> field -> row
for r in model:
    if r["object_type"] in ("dimension", "dimension_group", "measure", "filter", "parameter"):
        field_rows[r["view_name"]][r["field_name"]] = r
dim_groups = {v: {r["field_name"] for r in fs.values() if r["object_type"] == "dimension_group"} for v, fs in field_rows.items()}


def resolve_field(ref):
    """Return (view, field, kind) for a 'view.field' reference, mapping timeframe names to their dimension group."""
    if "." not in ref:
        return None
    v, f = ref.split(".", 1)
    if v in field_rows and f in field_rows[v]:
        return v, f, field_rows[v][f]["object_type"]
    for g in sorted(dim_groups.get(v, ()), key=len, reverse=True):
        if f.startswith(g + "_"):
            return v, g, "dimension_group"
    return v, f, None


result = {"in_scope_dashboards": {}, "explores": {}, "views": {}, "unresolved_fields": [], "alias_views": {}, "drop_list_views": [],
          "redesign_in_scope": [], "assisted_in_scope": [], "counts": {}}

# 1. Explores reached by the three dashboards (including merged-result source queries)
explore_set = []
for did in IN_SCOPE:
    d = content["dashboards"][did]
    ex = sorted({e.split("/", 1)[1] for e in d["explores"] if e.startswith("analytics/")})
    other_models = sorted({e for e in d["explores"] if not e.startswith("analytics/")})
    vis_tiles = [t for t in d["tiles"] if t["type"] == "vis"]
    result["in_scope_dashboards"][did] = {
        "title": d["title"], "lookml_link_id": d["lookml_link_id"], "folder": d["folder"], "owner": d["owner"], "updated_at": d["updated_at"],
        "views_90d": d["views_90d"], "last_viewed": d["last_viewed"], "api_view_count": d["view_count_api"],
        "explores": ex, "explores_other_models": other_models, "filters": d["filters"],
        "tiles_total": len(d["tiles"]), "tiles_vis": len(vis_tiles), "tiles_text": len([t for t in d["tiles"] if t["type"] == "text"]),
        "tiles_other": len([t for t in d["tiles"] if t["type"] not in ("vis", "text")]),
        "tiles_merged_results": len([t for t in vis_tiles if t.get("merge_result_id")]),
        "tiles_with_dynamic_fields": len([t for t in vis_tiles if t.get("dynamic_fields")]),
        "tiles_custom_vis": [(t["id"], t["vis_type"]) for t in vis_tiles if t.get("vis_type") and not str(t["vis_type"]).startswith(("looker_", "single_value", "table"))],
        "tiles_from_looks": [(t["id"], t["look_id"]) for t in vis_tiles if t.get("look_id")],
        "vis_types": dict(Counter(t.get("vis_type") for t in vis_tiles)),
        "fields": d["fields"],
    }
    explore_set += ex
explore_set = sorted(set(explore_set))

# 2. Views each explore reaches (base + joined, then extends closure)
view_set = set()
alias_map = {}
for e in explore_set:
    info = explores.get(e)
    if not info:
        result["explores"][e] = {"error": "explore not found in parsed model"}
        continue
    reached = set(info["views_reached"])
    for j in info["joins"]:
        if j["join"] != j["view"]:
            alias_map[(e, j["join"])] = j["view"]
    result["explores"][e] = {"base_view": info["base_view"], "class": info["class"], "reason": info["reason"], "hidden": info["hidden"],
                             "label": info["label"], "joins": len(info["joins"]), "views_reached": sorted(reached),
                             "join_classes": dict(Counter(j["class"] for j in info["joins"])),
                             "redesign_joins": [(j["join"], j["view"], j["relationship"], j["type"]) for j in info["joins"] if j["class"] == "redesign"],
                             "always_filter": info.get("always_filter"), "sql_always_where": info.get("sql_always_where"),
                             "access_filter": info.get("access_filter"), "fields": info.get("fields")}
    view_set |= reached

# extends closure
changed = True
while changed:
    changed = False
    for v in list(view_set):
        for base in (views.get(v, {}).get("extends") or []):
            if base not in view_set:
                view_set.add(base)
                changed = True
view_set = sorted(view_set)
result["alias_views"] = {f"{e}.{a}": v for (e, a), v in sorted(alias_map.items())}

for v in view_set:
    info = views.get(v)
    if not info:
        result["views"][v] = {"error": "view referenced by an explore but not defined in the project"}
        continue
    result["views"][v] = {"class": info["class"], "complexity": info["complexity"], "fields": info["fields"], "field_classes": info["field_classes"],
                          "construct": info["construct"], "file": info["file"], "sql_table_name": info.get("sql_table_name"), "pdt": info.get("pdt"),
                          "used_by_explores": sorted(e for e in explore_set if v in explores.get(e, {}).get("views_reached", []))}

# 3. Fields referenced by the dashboards: resolve against the model, through join aliases
for did in IN_SCOPE:
    d = content["dashboards"][did]
    dash_explores = {e.split("/", 1)[1] for e in d["explores"] if e.startswith("analytics/")}
    for ref in d["fields"]:
        res = resolve_field(ref)
        if res is None:
            continue
        v, f, kind = res
        reachable = {vv for e in dash_explores for vv in explores.get(e, {}).get("views_reached", [])}
        reachable |= {a for (e, a) in alias_map if e in dash_explores}
        if kind is None:
            # try alias resolution: the view part may be a join alias in one of the dashboard's explores
            resolved = False
            for e in dash_explores:
                target = alias_map.get((e, v))
                if target and resolve_field(f"{target}.{f}")[2] is not None:
                    resolved = True
                    break
            if not resolved:
                result["unresolved_fields"].append({"dashboard": did, "field": ref, "kind": "field not in LookML project"})
        elif v not in reachable:
            result["unresolved_fields"].append({"dashboard": did, "field": ref, "kind": "field exists but its view is not joined to any explore the dashboard queries"})

# 4. Redesign and assisted constructs inside the in-scope model
for r in model:
    in_scope = (r["object_type"] in ("view", "dimension", "dimension_group", "measure", "filter", "parameter", "set") and r["view_name"] in view_set) or \
               (r["object_type"] in ("explore", "join") and r["explore_name"] in explore_set)
    if not in_scope:
        continue
    if r["translation_class"] == "redesign":
        result["redesign_in_scope"].append({"type": r["object_type"], "uri": r["object_uri"], "view": r["view_name"], "explore": r["explore_name"],
                                            "field": r["field_name"], "construct": r["construct"], "reason": r["reason"], "file": r["lkml_file"], "line": r["line"]})
    elif r["translation_class"] == "assisted":
        result["assisted_in_scope"].append({"type": r["object_type"], "uri": r["object_uri"], "view": r["view_name"], "explore": r["explore_name"],
                                            "field": r["field_name"], "construct": r["construct"], "reason": r["reason"]})

# 5. Drop list: every other view and explore
result["drop_list_views"] = sorted(v for v in views if v not in view_set)
result["drop_list_explores"] = sorted(e for e in explores if e not in explore_set)

# 6. Counts
in_scope_fields = sum(views[v]["fields"] for v in view_set if v in views)
result["counts"] = {"explores_in_scope": len(explore_set), "views_in_scope": len(view_set), "fields_in_scope": in_scope_fields,
                    "explores_dropped": len(result["drop_list_explores"]), "views_dropped": len(result["drop_list_views"]),
                    "redesign_in_scope": len(result["redesign_in_scope"]), "assisted_in_scope": len(result["assisted_in_scope"]),
                    "unresolved_fields": len(result["unresolved_fields"]),
                    "redesign_by_construct": dict(Counter(x["construct"] for x in result["redesign_in_scope"])),
                    "assisted_by_construct": dict(Counter(x["construct"] for x in result["assisted_in_scope"]))}
result["explore_set"] = explore_set
result["view_set"] = view_set
json.dump(result, open(OUT + "raw/scope_analysis.json", "w"), indent=1, sort_keys=True)
print(json.dumps({"counts": result["counts"], "explores": explore_set, "views": view_set, "unresolved": result["unresolved_fields"][:40],
                  "dashboards": {k: {kk: vv for kk, vv in v.items() if kk not in ("fields", "filters")} for k, v in result["in_scope_dashboards"].items()}}, indent=1))
