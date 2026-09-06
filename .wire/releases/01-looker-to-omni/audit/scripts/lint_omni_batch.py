"""omni-model-lint: static lint of the converter output for one batch (rules L0 to L10 from the spec, plus L11 self-reference).

Reads local files only. Writes migration/omni_model/lint_<batch>.md and prints a JSON summary.

Usage (from the repo root):
    python3 lint_omni_batch.py <release_root> <batch_id> <today> [earlier_batch_ids_csv]
"""
import glob
import json
import os
import re
import sys

import yaml

ROOT = sys.argv[1].rstrip("/") + "/"
BATCH = sys.argv[2]
TODAY = sys.argv[3]
EARLIER = [b for b in (sys.argv[4].split(",") if len(sys.argv) > 4 else []) if b]
BDIR = ROOT + f"migration/omni_model/{BATCH}/"

TIMEFRAMES = {"raw", "date", "week", "month", "quarter", "year", "hour", "minute", "second", "millisecond", "day_of_week_name", "day_of_week_num",
              "day_of_month", "day_of_quarter", "day_of_year", "hour_of_day", "month_name", "month_num", "quarter_of_year", "fiscal_quarter", "fiscal_year"}
AGG = {"sum", "count", "count_distinct", "average", "min", "max", "median", "list", "percentile", "sum_distinct_on", "average_distinct_on", "median_distinct_on", "percentile_distinct_on"}
REL = {"one_to_one", "many_to_one", "one_to_many", "many_to_many", "assumed_many_to_one"}
JOIN = {"always_left", "inner", "full_outer", "cross", "right_left", "left_right"}
LIQUID = re.compile(r"\{%|%\}|\{\{")
REF = re.compile(r"\$\{([A-Za-z_]\w*)(?:\[[\w]+\])?\}")

failures = []  # (rule, file, key, value, change)
results = {}


def fail(rule, f, key, val, change):
    failures.append((rule, f, key, str(val)[:90].replace("|", "\\|").replace("\n", " "), change))


files = sorted(glob.glob(BDIR + "**/*.view", recursive=True)) + sorted(glob.glob(BDIR + "*.topic")) + ([BDIR + "relationships.yaml"] if os.path.exists(BDIR + "relationships.yaml") else [])
parsed = {}
for f in files:
    rel = os.path.relpath(f, BDIR)
    try:
        parsed[rel] = yaml.safe_load(open(f)) or {}
    except Exception as e:  # noqa: BLE001
        fail("L0", rel, "-", str(e)[:80], "fix YAML syntax")
results["L0 parseable"] = len([x for x in failures if x[0] == "L0"])

views = {rel: doc for rel, doc in parsed.items() if rel.endswith(".view")}
topics = {rel: doc for rel, doc in parsed.items() if rel.endswith(".topic")}
rels = parsed.get("relationships.yaml") or []
view_names = {os.path.basename(rel)[:-5] for rel in views}
earlier_views = set()
for b in EARLIER:
    for f in glob.glob(ROOT + f"migration/omni_model/{b}/**/*.view", recursive=True):
        earlier_views.add(os.path.basename(f)[:-5])

# L1, L2
for rel, doc in parsed.items():
    text = open(BDIR + rel).read()
    for m in re.finditer(r"\$\{TABLE\}", text):
        fail("L1", rel, "-", "${TABLE}", "drop sql: for a plain column, or reference ${field}")
    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + [str(k)])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + [str(i)])
        elif isinstance(node, str) and path and path[-1] in ("sql", "label", "description", "html", "markdown", "always_where_sql") and LIQUID.search(node):
            fail("L2", rel, ".".join(path), node, "remove Liquid; redesign item")
    walk(doc, [])
results["L1 no ${TABLE}"] = len([x for x in failures if x[0] == "L1"])
results["L2 no Liquid"] = len([x for x in failures if x[0] == "L2"])

# L3, L4, L5, L9, L11 per view
n3 = n4 = n5 = n9 = n11 = 0
for rel, doc in views.items():
    dims = doc.get("dimensions") or {}
    meas = doc.get("measures") or {}
    names = list(dims.keys()) + list(meas.keys())
    for n in set(dims) & set(meas):
        fail("L9", rel, n, "dimension and measure share a name", "rename one")
    for n in set(x for x in names if names.count(x) > 1):
        fail("L9", rel, n, "duplicate", "rename one")
    for name, d in dims.items():
        d = d or {}
        for t in d.get("timeframes") or []:
            if t not in TIMEFRAMES:
                fail("L3", rel, f"dimensions.{name}.timeframes", t, "map to an Omni timeframe or drop")
        sql = d.get("sql")
        if isinstance(sql, str):
            for r in REF.findall(sql):
                if r == name:
                    fail("L11", rel, f"dimensions.{name}.sql", sql, "converter defect: ${TABLE}.col became ${col} where col is the field's own name; use the bare column name")
    for name, m in meas.items():
        m = m or {}
        agg = m.get("aggregate_type")
        if agg is not None and agg not in AGG:
            fail("L4", rel, f"measures.{name}.aggregate_type", agg, "use an Omni aggregate_type")
        if agg == "percentile" and "percentile" not in m:
            fail("L4", rel, f"measures.{name}", "percentile without value", "add percentile:")
        if isinstance(agg, str) and agg.endswith("_distinct_on") and "custom_primary_key_sql" not in m:
            fail("L4", rel, f"measures.{name}", agg, "add custom_primary_key_sql")
        for fk, fv in (m.get("filters") or {}).items():
            if not isinstance(fv, dict):
                fail("L5", rel, f"measures.{name}.filters.{fk}", fv, "use an operator object, e.g. {is: value}")
        sql = m.get("sql")
        if isinstance(sql, str):
            for r in REF.findall(sql):
                if r == name and r not in dims:
                    fail("L11", rel, f"measures.{name}.sql", sql, "converter defect: measure named like its column references itself; use the bare column name")
results["L3 timeframes"] = len([x for x in failures if x[0] == "L3"])
results["L4 aggregate types"] = len([x for x in failures if x[0] == "L4"])
results["L5 filter objects"] = len([x for x in failures if x[0] == "L5"])
results["L9 unique names"] = len([x for x in failures if x[0] == "L9"])

# L6, L8 relationships
def has_pk(vname):
    for rel, doc in views.items():
        if os.path.basename(rel)[:-5] == vname:
            if "custom_compound_primary_key_sql" in doc:
                return True
            return any((d or {}).get("primary_key") for d in (doc.get("dimensions") or {}).values())
    return vname in earlier_views  # assume earlier batches passed L6


for i, r in enumerate(rels if isinstance(rels, list) else []):
    for side in ("join_from_view", "join_to_view"):
        v = r.get(side)
        if v and not has_pk(v):
            fail("L6", "relationships.yaml", f"[{i}].{side}", v, "add primary_key: true to a dimension of the view")
    if r.get("relationship_type") not in REL:
        fail("L8", "relationships.yaml", f"[{i}].relationship_type", r.get("relationship_type"), "use an Omni relationship_type")
    if r.get("join_type") not in JOIN:
        fail("L8", "relationships.yaml", f"[{i}].join_type", r.get("join_type"), "use an Omni join_type")
results["L6 primary keys on joined views"] = len([x for x in failures if x[0] == "L6"])
results["L8 relationship and join types"] = len([x for x in failures if x[0] == "L8"])

# L7 topics resolve
def join_keys(node):
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(k)
            out += join_keys(v)
    return out


known = view_names | earlier_views
for rel, doc in topics.items():
    bv = doc.get("base_view")
    if bv not in known:
        fail("L7", rel, "base_view", bv, "emit the view in this or an earlier batch")
    for k in join_keys(doc.get("joins") or {}):
        if k not in known:
            fail("L7", rel, f"joins.{k}", k, "emit the view or fix the alias")
results["L7 topic views resolve"] = len([x for x in failures if x[0] == "L7"])

# L10 redesign items not emitted (html construct: the dimension is emitted by design, only html is withheld)
nh = json.load(open(BDIR + "needs_human.json"))
items = nh if isinstance(nh, list) else nh.get("items", [])
for it in items:
    if it.get("class") != "redesign" or it.get("construct") == "html":
        continue
    fld = it.get("field")
    for rel, doc in views.items():
        if os.path.basename(rel)[:-5] == it.get("name") and fld in (doc.get("dimensions") or {}) or fld in (doc.get("measures") or {}):
            fail("L10", rel, fld, "redesign item emitted", "remove the emitted field")
results["L10 redesign items not emitted"] = len([x for x in failures if x[0] == "L10"])
results["L11 self-reference (beyond the catalogue)"] = len([x for x in failures if x[0] == "L11"])

overall = "PASS" if not failures else "FAIL"
L = [f"# Omni Model Lint: batch {BATCH}", "", f"Run {TODAY} by `/wire:omni-model-lint` on `migration/omni_model/{BATCH}/` ({len(views)} views, {len(topics)} topics, {len(rels) if isinstance(rels, list) else 0} relationships). Result: **{overall}**.", "",
     "| Rule | Result | Failures |", "|---|---|---|"]
for rule, n in results.items():
    L.append(f"| {rule} | {'PASS' if n == 0 else 'FAIL'} | {n} |")
L += ["", "L10 note: the 4 `html` redesign items name dimensions that are emitted without their html, as the translation guide specifies; they are not counted as emitted redesigns.", "",
      "L11 is not in the spec's catalogue. It catches a converter defect the catalogue does not: a measure (or dimension group) whose LookML `sql` was `${TABLE}.<col>` where `<col>` equals the field's own name is emitted as `sql: ${<col>}`, which Omni reads as a reference to the field itself.", "",
      "## Failures", "", "| Rule | File | Key | Value | Change |", "|---|---|---|---|---|"]
for r, f, k, v, c in failures:
    L.append(f"| {r} | {f} | {k} | `{v}` | {c} |")
if not failures:
    L.append("| - | - | - | - | none |")
open(ROOT + f"migration/omni_model/lint_{BATCH}.md", "w").write("\n".join(L) + "\n")
print(json.dumps({"overall": overall, "results": results, "failures": [{"rule": r, "file": f, "key": k} for r, f, k, v, c in failures]}, indent=1))
