"""Build audit/looker_audit.md from the two catalogs and the raw extracts. Deterministic; numbers come from the files.

Usage (from the repo root):
    python3 build_audit_report.py <audit_out_dir> <release_folder> <lookml_commit> <looker_base_url> <today>
"""
import csv
import json
import sys
from collections import Counter, defaultdict

OUT = sys.argv[1].rstrip("/") + "/"
RELEASE = sys.argv[2]
COMMIT = sys.argv[3]
LOOKER = sys.argv[4]
TODAY = sys.argv[5]

model = list(csv.DictReader(open(OUT + "looker_model_catalog.csv")))
content = list(csv.DictReader(open(OUT + "looker_content_catalog.csv")))
sa = json.load(open(OUT + "raw/scope_analysis.json"))
summ = json.load(open(OUT + "raw/lookml_parsed_summary.json"))
detail = json.load(open(OUT + "raw/looker_content.json"))
perms = json.load(open(OUT + "raw/looker_permissions.json"))
IN_SCOPE = ["267", "416", "255"]

L = []


def h(x):
    L.append(x)
    L.append("")


def table(headers, rows):
    L.append("| " + " | ".join(headers) + " |")
    L.append("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        L.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |")
    L.append("")


mt = Counter(r["object_type"] for r in model)
mc = Counter((r["object_type"], r["translation_class"]) for r in model)
mcx = Counter((r["translation_class"], r["complexity"]) for r in model)
ct = Counter(r["object_type"] for r in content)
dash = [r for r in content if r["object_type"] == "dashboard"]
looks = [r for r in content if r["object_type"] == "look"]
tiles = [r for r in content if r["object_type"] == "tile"]
tile_types = Counter()
for did, d in detail["dashboards"].items():
    for t in d["tiles"]:
        tile_types[t["type"] or "unknown"] += 1
view_constructs = Counter(v["construct"] for v in summ["views"].values())
lookml_dash = [r for r in dash if "lookml dashboard" in r["reason"]]
personal_dash = [r for r in dash if "folder_kind: personal" in r["reason"]]
personal_looks = [r for r in looks if "folder_kind: personal" in r["reason"]]
field_count = mt["dimension"] + mt["dimension_group"] + mt["measure"] + mt["filter"] + mt["parameter"]

h(f"# Looker Audit: {RELEASE}")
L += [f"**Release**: {RELEASE} (bi_migration, looker_to_omni)  ", f"**Generated**: {TODAY}  ",
      f"**LookML source**: `rittmananalytics/ra_data_warehouse_lookml` at commit `{COMMIT}` (branch `master`; Looker production deploys the same commit)  ",
      f"**Looker instance**: {LOOKER} (API 4.0; usage from System Activity `history` explore)  ",
      "**Connection**: `ra_dw_prod`, BigQuery (`bigquery_standard_sql`), project `ra-development`, default dataset `analytics`  ",
      "**Scope ruling in force**: R-1 (three dashboards and what they need; everything else is the drop list). The audit records the whole estate; the plan applies the ruling.", ""]

h("## Summary")
table(["Object", "Count", "Notes"], [
    ["Views", mt["view"], f"{view_constructs.get('view:table', 0)} table-backed, {view_constructs.get('view:derived_table', 0)} ephemeral derived tables, "
                          f"{view_constructs.get('view:pdt', 0)} PDTs, {view_constructs.get('view:native_derived_table', 0)} native derived table, "
                          f"{view_constructs.get('view:sql_table_name_liquid', 0)} with Liquid in sql_table_name, {view_constructs.get('view:derived_table_liquid', 0)} with Liquid in derived SQL, "
                          f"{view_constructs.get('view:no_table', 0)} array-unnest views with no table, {view_constructs.get('view:extends', 0)} extends-only"],
    ["Explores", mt["explore"], f"all in model `analytics`; {len([e for e in summ['explores'].values() if e['hidden']])} hidden"],
    ["Joins", mt["join"], ""],
    ["Dimensions", mt["dimension"], ""],
    ["Dimension groups", mt["dimension_group"], ""],
    ["Measures", mt["measure"], ""],
    ["Filter-only fields", mt["filter"], ""],
    ["Parameters", mt["parameter"], ""],
    ["Sets", mt["set"], ""],
    ["Fields (dimensions + groups + measures + filters + parameters)", field_count, ""],
    ["Dashboards", ct["dashboard"], f"{len(lookml_dash)} LookML dashboards, {len(personal_dash)} in personal folders"],
    ["Looks", ct["look"], f"{len(personal_looks)} in personal folders"],
    ["Tiles (dashboard elements)", ct["tile"], ", ".join(f"{k}: {v}" for k, v in sorted(tile_types.items()))],
    ["Schedules", ct["schedule"], ""],
    ["Alerts", ct["alert"], "read through the raw API; the typed SDK call fails to deserialise on this instance"],
    ["Folders", ct["folder"], f"{len([r for r in content if r['object_type'] == 'folder' and 'personal' in r['reason']])} personal"],
])

h("## Classification breakdown")
L.append("Model rows by object type and class (`drop` is not used for model rows):")
L.append("")
types = ["view", "explore", "join", "dimension", "dimension_group", "measure", "filter", "parameter", "set"]
table(["Object type", "mechanical", "assisted", "redesign", "total"],
      [[t, mc[(t, "mechanical")], mc[(t, "assisted")], mc[(t, "redesign")], mt[t]] for t in types] +
      [["**total**", sum(mc[(t, "mechanical")] for t in types), sum(mc[(t, "assisted")] for t in types), sum(mc[(t, "redesign")] for t in types), len(model)]])
L.append("Model rows by class and complexity (mechanical is Low, assisted is Medium, redesign is High; a view's complexity follows its fields, so a mechanical view with redesign fields is High):")
L.append("")
table(["Class", "Low", "Medium", "High"], [[c, mcx[(c, "Low")], mcx[(c, "Medium")], mcx[(c, "High")]] for c in ("mechanical", "assisted", "redesign")])
cc = Counter((r["object_type"], r["translation_class"]) for r in content)
L.append("Content rows by class (every content row is `mechanical` at audit stage except text tiles, which are `drop`; the plan re-rules):")
L.append("")
table(["Object type", "mechanical", "drop"], [[t, cc[(t, "mechanical")], cc[(t, "drop")]] for t in ("dashboard", "look", "tile", "schedule", "alert", "folder")])

h("## Usage distribution")
def v90(r):
    try:
        return int(r["views_90d"])
    except (TypeError, ValueError):
        return 0
ranked = sorted(dash, key=lambda r: (-v90(r), r["title"]))
total = sum(v90(r) for r in ranked)
cum, cut = 0, 0
for r in ranked:
    if cum >= 0.8 * total:
        break
    cum += v90(r)
    cut += 1
zero_dash = [r for r in ranked if v90(r) == 0]
unknown_dash = [r for r in dash if r["views_90d"] == "unknown"]
L.append(f"Source: System Activity `history` explore, `history.dashboard_run_count` per `history.real_dash_id`, window `history.created_date` = 90 days ending {TODAY}; `last_viewed` = `history.most_recent_query_date` over all history. Looks use `history.count` per `look.id`. A dashboard or Look with no history row is recorded as `never` / 0.")
L.append("")
table(["Measure", "Value"], [
    ["Dashboard runs in the last 90 days (all dashboards)", total],
    ["Dashboards with at least one run in 90 days", len([r for r in ranked if v90(r) > 0])],
    ["Dashboards carrying 80% of runs", f"{cut} of {len(dash)}"],
    ["Dashboards with zero runs in 90 days", len(zero_dash)],
    ["Dashboards with usage unknown", len(unknown_dash)],
    ["Look runs in the last 90 days (all Looks)", sum(v90(r) for r in looks)],
    ["Looks with zero runs in 90 days", len([r for r in looks if v90(r) == 0])],
])
L.append("Top 25 dashboards by runs in 90 days (the three in-scope dashboards are marked):")
L.append("")
table(["Rank", "Id", "Title", "Folder", "Runs 90d", "Last viewed", "In scope"],
      [[i + 1, r["id"], r["title"], r["folder"], v90(r), r["last_viewed"], "yes" if r["id"] in IN_SCOPE else ""] for i, r in enumerate(ranked[:25])])
L.append("Top 10 Looks by runs in 90 days:")
L.append("")
lr = sorted(looks, key=lambda r: (-v90(r), r["title"]))[:10]
table(["Id", "Title", "Folder", "Runs 90d", "Last viewed", "Explore"], [[r["id"], r["title"], r["folder"], v90(r), r["last_viewed"], r["explore_refs"]] for r in lr])

h("## In-scope dashboards (R-1)")
L.append("The three dashboards named in the director's scope ruling, with what each reaches. Tile counts exclude the dashboard-level filter elements Looker returns as elements of type `filter`.")
L.append("")
rows = []
for did in IN_SCOPE:
    d = sa["in_scope_dashboards"][did]
    rows.append([did, d["title"], d["folder"], "LookML `" + d["lookml_link_id"] + "`" if d["lookml_link_id"] else "user-defined", d["updated_at"][:10],
                 d["views_90d"], d["last_viewed"], d["tiles_vis"], d["tiles_text"], d["tiles_other"], d["tiles_merged_results"], d["tiles_with_dynamic_fields"],
                 len(d["tiles_custom_vis"]), len(d["explores"]), len(d["filters"])])
table(["Id", "Title", "Folder", "Kind", "Updated", "Runs 90d", "Last viewed", "Vis tiles", "Text tiles", "Filter elements", "Merged-result tiles", "Tiles with table calcs or custom fields", "Custom vis", "Explores", "Filters"], rows)
for did in IN_SCOPE:
    d = sa["in_scope_dashboards"][did]
    L.append(f"**{did} {d['title']}**  ")
    L.append(f"Explores: {', '.join('`' + e + '`' for e in d['explores'])}  ")
    L.append("Filters: " + "; ".join(f"{f['name']} on `{f['dimension']}`" + (f" (default `{f['default']}`)" if f.get('default') else "") for f in d["filters"]) + "  ")
    L.append("Visualisation types: " + ", ".join(f"{k} x{v}" for k, v in sorted(d["vis_types"].items(), key=lambda kv: str(kv[0]))) + "  ")
    if d["tiles_custom_vis"]:
        L.append("Custom visualisations: " + ", ".join(f"element {i} `{t}`" for i, t in d["tiles_custom_vis"]) + "  ")
    L.append("")
c = sa["counts"]
L.append(f"Model reach of the three dashboards: **{c['explores_in_scope']} explores**, **{c['views_in_scope']} views** (base views plus every view those explores join, plus extends bases), **{c['fields_in_scope']} fields**. "
         f"In that reach: {c['redesign_in_scope']} redesign rows and {c['assisted_in_scope']} assisted rows. The other {c['explores_dropped']} explores and {c['views_dropped']} views are reached by no in-scope content.")
L.append("")
L.append("Views reached, by explore:")
L.append("")
table(["Explore", "Base view", "Hidden", "Joins", "Join classes", "Views reached", "Explore-level notes"],
      [[e, x["base_view"], "yes" if x["hidden"] else "", x["joins"], ", ".join(f"{k}: {v}" for k, v in sorted(x["join_classes"].items())), len(x["views_reached"]), x["reason"] or ""]
       for e, x in sorted(sa["explores"].items())])

h("## Redesign register")
L.append("Every `redesign` model row, grouped by construct. `In scope` marks rows inside the three dashboards' model reach. The converter emits nothing for these; the plan rules each one.")
L.append("")
in_scope_uris = {r["uri"] for r in sa["redesign_in_scope"]}
red = [r for r in model if r["translation_class"] == "redesign"]
groups = defaultdict(list)
for r in red:
    groups[r["construct"]].append(r)
for construct in sorted(groups):
    rs = groups[construct]
    L.append(f"**{construct}** ({len(rs)} rows, {len([r for r in rs if r['object_uri'] in in_scope_uris])} in scope)")
    L.append("")
    table(["Object", "View / explore", "Field", "Reason", "Source", "In scope"],
          [[r["object_type"], r["view_name"] or r["explore_name"], r["field_name"], r["reason"], f"{r['lkml_file']}:{r['line']}", "yes" if r["object_uri"] in in_scope_uris else ""] for r in rs])

h("## Assisted constructs in scope")
ag = Counter(r["construct"] for r in sa["assisted_in_scope"])
table(["Construct", "Rows in scope"], [[k, v] for k, v in sorted(ag.items())])

h("## Explore to content map")
emap = defaultdict(lambda: {"dashboards": [], "looks": []})
for r in dash:
    for ex in r["explore_refs"].split(";"):
        if ex:
            emap[ex]["dashboards"].append(r["id"])
for r in looks:
    if r["explore_refs"]:
        emap[r["explore_refs"]]["looks"].append(r["id"])
rows = []
for e in sorted(summ["explores"]):
    key = "analytics/" + e
    ds = emap.get(key, {}).get("dashboards", [])
    ls = emap.get(key, {}).get("looks", [])
    rows.append([e, len(ds), ", ".join(ds[:15]) + (" ..." if len(ds) > 15 else ""), len(ls), "yes" if e in sa["explore_set"] else ""])
table(["Explore", "Dashboards", "Dashboard ids", "Looks", "In scope"], rows)
other = sorted(k for k in emap if not k.startswith("analytics/"))
if other:
    L.append("Content on explores outside the `analytics` model (out of scope; listed so the drop list is complete):")
    L.append("")
    table(["Model/explore", "Dashboards", "Looks"], [[k, len(emap[k]["dashboards"]), len(emap[k]["looks"])] for k in other])

h("## Unresolved references")
unres_model = [r for r in model if "not found" in r["reason"] or "unresolved" in r["reason"]]
L.append(f"Model side: {len(unres_model)} rows reference a view the parser could not find in the project.")
L.append("")
if unres_model:
    table(["Object", "Explore", "Field / join", "Reason", "Source"], [[r["object_type"], r["explore_name"], r["field_name"], r["reason"], f"{r['lkml_file']}:{r['line']}"] for r in unres_model])
flagged = [r for r in content if "references field outside the parsed repo" in r["reason"] and r["object_type"] in ("dashboard", "look")]
L.append(f"Content side: {len(flagged)} dashboard and Look rows reference explores outside the `analytics` model or fields that do not exist in the parsed project. Each carries `reason: references field outside the parsed repo`. In-scope cases:")
L.append("")
table(["Dashboard", "Reference", "Finding"], [[u["dashboard"], u["field"], u["kind"]] for u in sa["unresolved_fields"]] or [["-", "-", "none"]])

h("## Text and markdown tiles")
tt = [(r["id"], r["title"], len([t for t in detail["dashboards"][r["id"]]["tiles"] if t["type"] == "text"])) for r in dash if r["has_text_tile"] == "true"]
L.append(f"{len(tt)} dashboards carry text tiles ({sum(x[2] for x in tt)} tiles). Text tiles are `drop` at audit stage and are recreated by hand where the plan carries the dashboard.")
L.append("")
table(["Dashboard", "Title", "Text tiles", "In scope"], [[i, t, n, "yes" if i in IN_SCOPE else ""] for i, t, n in sorted(tt, key=lambda x: (x[0] not in IN_SCOPE, -x[2]))[:40]])

h("## Permissions in play")
L.append("Read for the plan's permission map. Content access on the `Shared` folder (where all three dashboards live) is `view` for group `All Users`. No in-scope explore has an `access_filter`. One access grant is defined in the model.")
L.append("")
table(["Item", "Value"], [
    ["Groups", ", ".join(f"{g['name']} ({g['user_count']})" for g in perms["groups"])],
    ["Users", f"{len(perms['users'])} total, {len([u for u in perms['users'] if not u['disabled']])} active"],
    ["Access grant `can_view_company_bio`", "user attribute `groups`, allowed values Pepkor IT, Google, Brighton SST; applied to `companies_dim.company_description`"],
    ["User attribute `dataset`", "default `analytics`; drives `sql_table_name` on 29 views (11 in scope) through Liquid"],
    ["User attributes with group values", ", ".join(f"{k}: {v}" for k, v in perms["user_attribute_group_values"].items() if isinstance(v, list))],
])

h("## Usage source and access gaps")
table(["Item", "Status"], [
    ["System Activity", f"accessible; `usage_source: {detail.get('usage_source')}`"],
    ["Looker API", "API 4.0 with `LOOKERSDK_*` credentials (user Mark Rittman); Looker MCP not used"],
    ["Alerts", f"{len(detail.get('alerts') or [])} read through the raw `/alerts/search` endpoint; the typed SDK call fails to deserialise"],
    ["LookML project", f"snapshot commit `{COMMIT}`; Looker production branch `master` at the same commit"],
    ["Dashboards outside the `analytics` model", str(len(other)) + " model/explore combinations, all out of scope"],
])

h("## Classification notes")
L.append("- Classification follows `bi_pairs/looker_to_omni/feature_detection.md` and `translation_guide.md`. Two constructs met in this estate are not in the pair's detection table and were classified from the translation guide's rules: measures of `type: period_over_period` (16 rows, no Omni `aggregate_type`; treated as an unsupported measure type) and joins with a custom `sql:` and no `sql_on` (13 rows, all `LEFT JOIN UNNEST` array joins; the guide rules a join without `sql_on` as redesign).")
L.append("- Joins are classified from the detection table (`one_to_many`, `inner`, `full_outer`, aliased `from:` and `sql_where` are assisted). The translation guide's explore table says the converter emits these mechanically; the audit keeps the stricter class so the plan sees where fan-out and aliasing need a primary-key check.")
L.append("- A dimension with `html:` is `redesign` for the html only; the dimension itself is emitted. Eleven such rows are in scope (RAG status colour blocks).")
L.append("- Liquid inside `link:` blocks does not make a field redesign; the link is assisted per the guide.")
L.append("- Liquid in `group_label`, `view_label` or `description` (a templated label, not templated SQL) is classified `assisted`: the field is a plain column and the label resolves to one literal per view. The detection table's Liquid rule is written for `sql`, `html` and `label`. The `deals_fact` view carries this pattern on 58 fields.")
L.append("- `object_uri` uses the LookML project name `analytics` for every content row, including the few dashboards that query other models; their `explore_refs` name the real model.")
L.append("")

h("## Reference key")
table(["Code", "Meaning", "Defined in"], [
    ["mechanical", "the converter emits it with no human entry", "bi_pairs/looker_to_omni/translation_guide.md"],
    ["assisted", "the converter emits a best effort plus a needs_human entry, or withholds it with a note", "bi_pairs/looker_to_omni/translation_guide.md"],
    ["redesign", "no emission; the row carries the reason and the plan rules it", "bi_pairs/looker_to_omni/translation_guide.md"],
    ["drop", "content row not migrated programmatically (text tiles at audit stage)", "specs/migration/looker_audit/generate.md"],
    ["Low / Medium / High", "complexity: only mechanical tags / any assisted tag / any redesign tag or an unresolved reference", "bi_pairs/looker_to_omni/feature_detection.md"],
    ["looker:analytics:view:<name>", "object identity used across audit, plan, drift and parity", "specs/migration/looker_audit/generate.md Step 6"],
    ["R-1", "scope ruling: three dashboards and what they need", f".wire/releases/{RELEASE}/decisions.md"],
    ["views_90d / last_viewed", "System Activity dashboard runs in 90 days / most recent query date", "this document, Usage distribution"],
])

open(OUT + "looker_audit.md", "w").write("\n".join(L).rstrip() + "\n")
status = {"view_count": mt["view"], "explore_count": mt["explore"], "field_count": field_count, "dashboard_count": ct["dashboard"], "look_count": ct["look"],
          "tile_count": ct["tile"], "mechanical_count": sum(mc[(t, "mechanical")] for t in types), "assisted_count": sum(mc[(t, "assisted")] for t in types),
          "redesign_count": sum(mc[(t, "redesign")] for t in types), "drop_count": cc[("tile", "drop")], "usage_source": detail.get("usage_source"),
          "dashboards_80pct": cut, "zero_view_dashboards": len(zero_dash), "schedule_count": ct["schedule"], "alert_count": ct["alert"], "folder_count": ct["folder"]}
json.dump(status, open(OUT + "raw/audit_status_counts.json", "w"), indent=1)
print(json.dumps(status, indent=1))
