"""Run the eight looker-audit-validate checks, append a Validation section to audit/looker_audit.md, print results.

Usage (from the repo root):
    python3 validate_audit.py <audit_out_dir> <lookml_snapshot_dir> <status_counts_json> <today>
<status_counts_json> is the JSON of the values written to status.md (view_count ... drop_count, usage_source).
"""
import csv
import json
import re
import sys
from collections import defaultdict

OUT = sys.argv[1].rstrip("/") + "/"
SNAP = sys.argv[2].rstrip("/") + "/"
STATUS = json.loads(sys.argv[3]) if sys.argv[3].startswith("{") else json.load(open(sys.argv[3]))
TODAY = sys.argv[4]

MODEL_COLS = ["object_type", "object_uri", "view_name", "explore_name", "field_name", "construct", "translation_class", "complexity", "reason", "lkml_file", "line", "lookml_commit"]
CONTENT_COLS = ["object_type", "object_uri", "id", "title", "folder", "owner", "last_viewed", "views_90d", "source_updated_at", "tile_count", "explore_refs", "fields_refs", "has_text_tile", "translation_class", "reason"]
SECTIONS = ["## Summary", "## Classification breakdown", "## Usage distribution", "## Redesign register", "## Explore to content map", "## Unresolved references", "## Text and markdown tiles", "## Usage source and access gaps"]

results = []


def check(name, ok, gaps, note=""):
    results.append({"check": name, "result": "PASS" if ok else "FAIL", "gaps": gaps[:25], "gap_count": len(gaps), "note": note})


report = open(OUT + "looker_audit.md").read()
mf = open(OUT + "looker_model_catalog.csv")
mr = csv.reader(mf)
mhead = next(mr)
model = [dict(zip(mhead, row)) for row in mr]
cf = open(OUT + "looker_content_catalog.csv")
cr = csv.reader(cf)
chead = next(cr)
content = [dict(zip(chead, row)) for row in cr]

# Step 1: structure
missing_sections = [s for s in SECTIONS if s not in report]
check("Report sections and catalog columns", not missing_sections and mhead == MODEL_COLS and chead == CONTENT_COLS,
      missing_sections + ([f"model columns: {mhead}"] if mhead != MODEL_COLS else []) + ([f"content columns: {chead}"] if chead != CONTENT_COLS else []))

# Check 1
bad = [r["object_uri"] for r in model if r["translation_class"] not in ("mechanical", "assisted", "redesign")]
check("1 Every model row has a class", not bad, bad)

# Check 2
exp = {"mechanical": "Low", "assisted": "Medium", "redesign": "High"}
bad = []
for r in model:
    if r["reason"].startswith("unresolved reference") or "not found in project (unresolved reference)" in r["reason"]:
        if r["complexity"] != "High":
            bad.append(r["object_uri"])
    elif r["object_type"] == "view":
        continue  # a view's complexity follows its fields (feature_detection.md Complexity table), checked separately below
    elif exp[r["translation_class"]] != r["complexity"]:
        bad.append(f"{r['object_uri']} {r['translation_class']}/{r['complexity']}")
# view complexity rule: High if any redesign in view or the view row is redesign; Medium if any assisted; else Low
by_view = defaultdict(list)
for r in model:
    if r["object_type"] in ("dimension", "dimension_group", "measure", "filter", "parameter"):
        by_view[r["view_name"]].append(r)
for r in model:
    if r["object_type"] != "view":
        continue
    fs = by_view.get(r["view_name"], [])
    n_red = len([f for f in fs if f["translation_class"] == "redesign"]) + (1 if r["translation_class"] == "redesign" else 0)
    n_ass = len([f for f in fs if f["translation_class"] == "assisted"])
    want = "High" if n_red or (len(fs) > 30 and n_ass) else ("Medium" if n_ass else "Low")
    if r["complexity"] != want:
        bad.append(f"{r['object_uri']} view {r['complexity']} expected {want}")
check("2 Complexity consistent with class", not bad, bad, "view rows follow feature_detection.md's view complexity rule (fields decide)")

# Check 3
bad = [r["object_uri"] for r in model if r["translation_class"] == "redesign" and not r["reason"].strip()]
check("3 Every redesign row has a reason", not bad, bad)

# Check 4: feature detection agrees with class (field, join and view rows)
LIQUID = re.compile(r"\{%|%\}|\{\{|\}\}")
REDESIGN_FIELD = [re.compile(r"^[ \t]*parameter:\s*\w+", re.M), re.compile(r"^[ \t]*html\s*:", re.M), re.compile(r"^[ \t]*type\s*:\s*(location|distance|bin)\b", re.M)]
REDESIGN_MEASURE_TYPE = re.compile(r"^[ \t]*type\s*:\s*(running_total|percent_of_total|percent_of_previous|period_over_period|date|string|yesno)\b", re.M)
PDT = re.compile(r"^[ \t]*(datagroup_trigger|sql_trigger_value|persist_for|materialized_view|increment_key|cluster_keys|partition_keys|indexes|distribution)\s*:", re.M)
ASSISTED = [re.compile(p, re.M) for p in (r"^[ \t]*link\s*:\s*\{", r"^[ \t]*case\s*:\s*\{", r"^[ \t]*type\s*:\s*duration", r"^[ \t]*type\s*:\s*number", r"^[ \t]*filters\s*:", r"^[ \t]*value_format\s*:",
                                          r"^[ \t]*value_format_name\s*:", r"^[ \t]*sql_always_where\s*:", r"^[ \t]*(always_filter|conditionally_filter)\s*:", r"^[ \t]*access_filter\s*:",
                                          r"^[ \t]*relationship\s*:\s*one_to_many", r"^[ \t]*type\s*:\s*(inner|full_outer)", r"^[ \t]*from\s*:", r"^[ \t]*sql_where\s*:", r"\$\{\w+\.\w+\}",
                                          r"^[ \t]*drill_fields\s*:", r"^[ \t]*timeframes\s*:", r"^[ \t]*sql_distinct_key\s*:", r"^[ \t]*type\s*:\s*\w+_distinct\b", r"^[ \t]*type\s*:\s*(sum|average|median|percentile)_distinct\b")]
DECL = re.compile(r"^[ \t]*(view|explore|join|dimension|dimension_group|measure|filter|parameter|set)\s*:\s*\+?\w+\s*\{")
file_cache = {}


def block(path, line):
    if path not in file_cache:
        file_cache[path] = open(SNAP + path, errors="replace").read().splitlines()
    lines = file_cache[path]
    i = int(line) - 1
    out = [lines[i]]
    start_indent = len(lines[i]) - len(lines[i].lstrip())
    j = i + 1
    while j < len(lines):
        ln = lines[j]
        indent = len(ln) - len(ln.lstrip())
        stripped = ln.strip()
        # stop at the next declaration (a field block never nests another declaration), or at the enclosing block's closing brace
        if stripped and (DECL.match(ln) or (stripped == "}" and indent <= start_indent)):
            break
        out.append(ln)
        j += 1
    return out


def strip_links_and_html(lines):
    """Remove link: {...} blocks and html: lines so their Liquid does not count."""
    out, depth = [], 0
    for ln in lines:
        if depth > 0:
            depth += ln.count("{") - ln.count("}")
            continue
        if re.match(r"^[ \t]*link\s*:\s*\{", ln):
            depth = ln.count("{") - ln.count("}")
            continue
        if re.match(r"^[ \t]*(html|description|group_label|view_label)\s*:", ln):
            continue
        out.append(ln)
    return out


LIQUID_LABEL = re.compile(r"^[ \t]*(group_label|view_label|description)\s*:.*(\{%|\{\{)", re.M)


bad = []
for r in model:
    if not r["line"] or r["object_type"] == "set":
        continue
    if "unresolved reference" in r["reason"] or "not found in project" in r["reason"]:
        continue
    try:
        lines = block(r["lkml_file"], r["line"])
    except Exception as e:  # noqa: BLE001
        bad.append(f"{r['object_uri']} cannot read source: {e}")
        continue
    if r["object_type"] == "view":
        # only the view's own header: up to the first field declaration
        head = []
        for ln in lines[1:]:
            if DECL.match(ln):
                break
            head.append(ln)
        text = "\n".join(head)
        is_red = bool(LIQUID.search(text)) or bool(PDT.search(text)) or bool(re.search(r"^\s*explore_source\s*:", text, re.M))
        if is_red and r["translation_class"] != "redesign":
            bad.append(f"{r['object_uri']} view header matches a redesign pattern but is {r['translation_class']}")
        if not is_red and r["translation_class"] == "redesign":
            bad.append(f"{r['object_uri']} view is redesign with no redesign pattern")
        continue
    if r["object_type"] == "explore":
        text = "\n".join(strip_links_and_html(lines))
        is_red = bool(LIQUID.search(text))
        if is_red and r["translation_class"] != "redesign":
            bad.append(f"{r['object_uri']} explore has Liquid but is {r['translation_class']}")
        continue
    body = lines
    core = strip_links_and_html(body)
    text_core = "\n".join(core)
    text_all = "\n".join(body)
    is_red = bool(LIQUID.search(text_core))
    if r["object_type"] in ("dimension", "measure", "dimension_group"):
        is_red = is_red or any(p.search(text_all) for p in REDESIGN_FIELD[1:])  # html, unsupported dimension type
    if r["object_type"] == "measure" and REDESIGN_MEASURE_TYPE.search(text_all):
        is_red = True
    if r["object_type"] in ("parameter", "filter"):
        is_red = True
    if r["object_type"] == "join":
        has_on = bool(re.search(r"^\s*sql_on\s*:", text_all, re.M)) or bool(re.search(r"^\s*foreign_key\s*:", text_all, re.M))
        if not has_on or re.search(r"^\s*relationship\s*:\s*many_to_many", text_all, re.M) or re.search(r"^\s*type\s*:\s*cross\b", text_all, re.M):
            is_red = True
    is_ass = any(p.search(text_all) for p in ASSISTED) or bool(LIQUID_LABEL.search(text_all))
    if is_red and r["translation_class"] != "redesign":
        bad.append(f"{r['object_uri']} matches a redesign pattern but is {r['translation_class']}")
    if not is_red and not is_ass and r["translation_class"] == "redesign":
        bad.append(f"{r['object_uri']} is redesign with no redesign or assisted pattern: {r['reason'][:60]}")
check("4 Feature detection agrees with the class", not bad, bad,
      "patterns from feature_detection.md plus the translation guide's join-without-sql_on and period_over_period rules; Liquid inside link:, html:, group_label, view_label and description is not a redesign trigger (see Classification notes)")

# Check 5
bad = [r["object_uri"] for r in content if r["object_type"] in ("dashboard", "look") and (r["last_viewed"] == "" or r["views_90d"] == "")]
unknown = [r for r in content if r["object_type"] in ("dashboard", "look") and (r["last_viewed"] == "unknown" or r["views_90d"] == "unknown")]
ok = not bad and (not unknown or STATUS.get("usage_source") == "unavailable")
check("5 Every content row has usage or explicit unknown", ok, bad + ([f"{len(unknown)} unknown rows but usage_source={STATUS.get('usage_source')}"] if unknown and STATUS.get("usage_source") != "unavailable" else []))

# Check 6
tiles_by_dash = defaultdict(list)
for r in content:
    if r["object_type"] == "tile":
        tiles_by_dash[r["object_uri"].split("/element:")[0]].append(r)
bad = []
for r in content:
    if r["object_type"] == "dashboard" and r["has_text_tile"] == "true":
        ts = tiles_by_dash.get(r["object_uri"], [])
        if not any(t["translation_class"] == "drop" and t["reason"] == "text tile, recreate by hand" for t in ts):
            bad.append(r["object_uri"])
bad += [r["object_uri"] for r in content if r["object_type"] == "tile" and r["translation_class"] == "drop" and r["reason"] != "text tile, recreate by hand"]
check("6 Text tiles recorded", not bad, bad)

# Check 7
explores = {r["explore_name"] for r in model if r["object_type"] == "explore"}
fields = defaultdict(set)
groups = defaultdict(set)
for r in model:
    if r["object_type"] in ("dimension", "dimension_group", "measure", "filter", "parameter"):
        fields[r["view_name"]].add(r["field_name"])
        if r["object_type"] == "dimension_group":
            groups[r["view_name"]].add(r["field_name"])
summ = json.load(open(OUT + "raw/lookml_parsed_summary.json"))
alias = defaultdict(dict)
for e, x in summ["explores"].items():
    for j in x["joins"]:
        alias[e][j["join"]] = j["view"]


def field_exists(v, f):
    return f in fields.get(v, ()) or any(f.startswith(g + "_") for g in groups.get(v, ()))


bad = []
for r in content:
    if r["object_type"] not in ("dashboard", "look", "tile"):
        continue
    refs = [x for x in r["explore_refs"].split(";") if x]
    dash_ex = {x.split("/", 1)[1] for x in refs if x.startswith("analytics/")}
    unresolved = [x for x in refs if not x.startswith("analytics/") or x.split("/", 1)[1] not in explores]
    for f in [x for x in r["fields_refs"].split(";") if x and "." in x]:
        v, fld = f.split(".", 1)
        if field_exists(v, fld):
            continue
        if any(alias.get(e, {}).get(v) and field_exists(alias[e][v], fld) for e in dash_ex):
            continue
        unresolved.append(f)
    if unresolved and "references field outside the parsed repo" not in r["reason"]:
        bad.append(f"{r['object_uri']}: {unresolved[:3]}")
check("7 Content references resolve to the model (or carry the outside-repo reason)", not bad, bad)

# Check 8
from collections import Counter  # noqa: E402

mt = Counter(r["object_type"] for r in model)
ct = Counter(r["object_type"] for r in content)
mcls = Counter(r["translation_class"] for r in model)
want = {"view_count": mt["view"], "explore_count": mt["explore"], "field_count": mt["dimension"] + mt["dimension_group"] + mt["measure"] + mt["filter"] + mt["parameter"],
        "dashboard_count": ct["dashboard"], "look_count": ct["look"], "tile_count": ct["tile"], "mechanical_count": mcls["mechanical"], "assisted_count": mcls["assisted"],
        "redesign_count": mcls["redesign"], "drop_count": len([r for r in content if r["object_type"] == "tile" and r["translation_class"] == "drop"])}
bad = [f"{k}: status {STATUS.get(k)} vs catalog {v}" for k, v in want.items() if STATUS.get(k) != v]
check("8 Counts match status.md", not bad, bad)

overall = all(r["result"] == "PASS" for r in results)
sec = ["", "## Validation", "", f"Run {TODAY} by `/wire:looker-audit-validate`. Result: **{'PASS' if overall else 'FAIL'}**.", "",
       "| Check | Result | Gaps | Note |", "|---|---|---|---|"]
for r in results:
    sec.append(f"| {r['check']} | {r['result']} | {r['gap_count']} | {r['note']} |")
sec += ["", "### Gaps to address", ""]
gaps = [(r["check"], g) for r in results for g in r["gaps"]]
if gaps:
    for c, g in gaps:
        sec.append(f"- {c}: {g}")
else:
    sec.append("- none")
report = re.sub(r"\n## Validation\n.*\Z", "\n", report, flags=re.S)
open(OUT + "looker_audit.md", "w").write(report.rstrip() + "\n" + "\n".join(sec) + "\n")
print(json.dumps({"overall": "PASS" if overall else "FAIL", "checks": [{k: v for k, v in r.items() if k != "gaps"} for r in results],
                  "gaps": {r["check"]: r["gaps"] for r in results if r["gaps"]}}, indent=1))
