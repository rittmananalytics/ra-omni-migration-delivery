"""Print the in-scope redesign register grouped by construct, per-explore field usage from the three dashboards,
and the whole-estate view redesign breakdown. Read-only helper for writing the audit and plan."""
import json
from collections import Counter, defaultdict

OUT = ".wire/releases/01-looker-to-omni/audit/"
sa = json.load(open(OUT + "raw/scope_analysis.json"))
summ = json.load(open(OUT + "raw/lookml_parsed_summary.json"))

print("## redesign in scope, by construct")
by = defaultdict(list)
for r in sa["redesign_in_scope"]:
    by[r["construct"]].append(r)
for c, items in sorted(by.items()):
    print(f"\n### {c} ({len(items)})")
    for r in items:
        print(f"  {r['type']:15} {r['view'] or r['explore']:45} {r['field']:45} {r['file']}:{r['line']}  {r['reason'][:110]}")

print("\n## whole-estate view redesign reasons")
print(Counter(v["construct"] for v in summ["views"].values() if v["class"] == "redesign"))
print("PDT views (whole estate):", sorted(n for n, v in summ["views"].items() if v.get("pdt")))

print("\n## per dashboard: fields by view (which joined views are actually used)")
for did, d in sa["in_scope_dashboards"].items():
    byv = Counter(f.split(".")[0] for f in d["fields"])
    print(f"\n{did} {d['title']}: explores={d['explores']} other_models={d['explores_other_models']} looks={d['tiles_from_looks']} custom_vis={d['tiles_custom_vis']}")
    print("   vis_types:", d["vis_types"])
    print("   fields by view:", dict(byv))
    print("   filters:", [(f["name"], f["type"], f["dimension"], f.get("default")) for f in d["filters"]])

print("\n## explores in scope: joins and classes")
for e in sa["explore_set"]:
    x = sa["explores"][e]
    print(f"  {e:42} base={x['base_view']:40} joins={x['joins']:2} classes={x['join_classes']} hidden={x['hidden']} cls={x['class']} reason={x['reason'][:80]}")
    if x["redesign_joins"]:
        print("     redesign joins:", x["redesign_joins"])
    if x.get("always_filter") or x.get("sql_always_where") or x.get("access_filter"):
        print("     filters:", x.get("always_filter"), x.get("sql_always_where"), x.get("access_filter"))

print("\n## alias views:", sa["alias_views"])
print("\n## views in scope with class/complexity")
for v in sa["view_set"]:
    x = sa["views"][v]
    if "error" in x:
        print("  ", v, x)
        continue
    print(f"  {v:60} {x['class']:10} {x['complexity']:6} fields={x['fields']:3} {x['construct']:28} table={x.get('sql_table_name')}")
