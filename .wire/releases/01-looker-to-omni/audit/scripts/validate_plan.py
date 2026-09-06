"""Run the nine bi-migration-plan-validate checks, append a Validation section to migration/bi_migration_plan.md, print results.

Usage (from the repo root):
    python3 validate_plan.py <release_root> <today> <register_rows_in_status> <parked_ids_csv> <ruling_ids_csv>
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1].rstrip("/") + "/"
TODAY = sys.argv[2]
STATUS_REGISTER_ROWS = int(sys.argv[3])
PARKED = set(sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[4] else set()
RULINGS = set(sys.argv[5].split(",")) if len(sys.argv) > 5 and sys.argv[5] else set()
AUD, MIG = ROOT + "audit/", ROOT + "migration/"

plan = open(MIG + "bi_migration_plan.md").read()
bf = open(MIG + "bi_migration_batches.csv")
br = csv.reader(bf)
bhead = next(br)
batches = [dict(zip(bhead, r)) for r in br]
reg = list(csv.DictReader(open(MIG + "migration_register.csv")))
model = list(csv.DictReader(open(AUD + "looker_model_catalog.csv")))
content = list(csv.DictReader(open(AUD + "looker_content_catalog.csv")))
decisions = open(ROOT + "decisions.md").read()
summ = json.load(open(AUD + "raw/lookml_parsed_summary.json"))
results = []


def check(name, ok, gaps, note=""):
    results.append({"check": name, "result": "PASS" if ok else "FAIL", "gaps": gaps[:25], "gap_count": len(gaps), "note": note})


SECTIONS = ["## Summary", "## Usage ranking", "## Rulings", "## Model scope", "## Permission map", "## Topic architecture", "## Batches", "## Parallel run and parity", "## Reference key"]
COLS = ["batch_id", "batch_kind", "object_type", "object_id", "object_name", "explore_or_topic", "usage_rank", "ruling", "depends_on_batch"]
missing = [s for s in SECTIONS if s not in plan]
check("Plan sections and batches columns", not missing and bhead == COLS, missing + ([f"columns {bhead}"] if bhead != COLS else []))

# Check 1: every content object placed exactly once
cnt = Counter((r["object_type"], r["object_id"]) for r in batches if r["object_type"] in ("dashboard", "look", "schedule", "alert"))
gaps = []
for r in content:
    if r["object_type"] in ("dashboard", "look", "schedule", "alert"):
        n = cnt.get((r["object_type"], r["id"]), 0)
        if n != 1:
            gaps.append(f"{r['object_type']} {r['id']} placed {n} times")
for (t, i), n in cnt.items():
    if n > 1:
        gaps.append(f"{t} {i} duplicated")
bad_drop = [f"{r['object_type']} {r['object_id']}" for r in batches if r["ruling"] == "drop" and r["batch_id"]]
bad_place = [f"{r['object_type']} {r['object_id']}" for r in batches if r["ruling"] != "drop" and not r["batch_id"]]
check("1 Every content object is placed exactly once", not gaps and not bad_drop and not bad_place, gaps + bad_drop + bad_place)

# Check 2: every in-scope model object placed exactly once; every not-carried view has a reason
carried_views = [r for r in batches if r["object_type"] == "view" and r["batch_id"]]
carried_topics = [r for r in batches if r["object_type"] == "topic" and r["batch_id"]]
dup = [k for k, n in Counter(r["object_id"] for r in carried_views).items() if n > 1] + [k for k, n in Counter(r["object_id"] for r in carried_topics).items() if n > 1]
all_views = {r["view_name"] for r in model if r["object_type"] == "view"}
all_explores = {r["explore_name"] for r in model if r["object_type"] == "explore"}
placed_views = {r["object_id"] for r in batches if r["object_type"] == "view"}
placed_topics = {r["object_id"] for r in batches if r["object_type"] == "topic"}
gaps = dup + [f"view {v} not in batches CSV" for v in sorted(all_views - placed_views)] + [f"explore {e} not in batches CSV" for e in sorted(all_explores - placed_topics)]
if "no in-scope content references it" not in plan:
    gaps.append("plan lacks the not-carried reason")
check("2 Every in-scope model object is placed exactly once; not-carried views have a reason", not gaps, gaps)

# Check 3: every drop has a reason in the plan's drop list
gaps = []
if "## Drop list" not in plan:
    gaps.append("no Drop list section")
for r in batches:
    if r["ruling"] == "drop":
        if r["object_type"] in ("dashboard", "look", "schedule", "alert") and f"| {r['object_id']} |" not in plan and f"| {r['object_type']} | {r['object_id']} |" not in plan:
            gaps.append(f"{r['object_type']} {r['object_id']} not listed")
        if r["object_type"] in ("view", "topic") and f"`{r['object_id']}`" not in plan:
            gaps.append(f"{r['object_type']} {r['object_id']} not listed")
        if r["object_type"] == "tile" and f"| {r['object_id'].split('/')[1]} |" not in plan:
            gaps.append(f"tile {r['object_id']} not listed")
check("3 Every drop has a reason", not gaps, gaps)

# Check 4: content batches depend on the right model batch
topic_batch = {r["object_id"]: r["batch_id"] for r in carried_topics}
gaps = []
crefs = {r["id"]: r for r in content if r["object_type"] == "dashboard"}
for r in batches:
    if r["object_type"] == "dashboard" and r["batch_id"]:
        refs = [x.split("/", 1)[1] for x in crefs[r["object_id"]]["explore_refs"].split(";") if x.startswith("analytics/")]
        for e in refs:
            tb = topic_batch.get(e)
            if tb is None or tb > r["depends_on_batch"]:
                gaps.append(f"dashboard {r['object_id']} needs {e} in {tb}, depends_on {r['depends_on_batch']}")
check("4 Content batches depend on the right model batch", not gaps, gaps)

# Check 5: model batch order respects view dependencies; no batch id with two kinds
view_batch = {r["object_id"]: r["batch_id"] for r in carried_views}
gaps = []
for t, tb in topic_batch.items():
    for v in summ["explores"][t]["views_reached"]:
        vb = view_batch.get(v)
        if vb is None or vb > tb:
            gaps.append(f"topic {t} in {tb} joins view {v} in {vb}")
kinds = defaultdict(set)
for r in batches:
    if r["batch_id"]:
        kinds[r["batch_id"]].add(r["batch_kind"])
gaps += [f"batch {b} has kinds {sorted(k)}" for b, k in kinds.items() if len(k) > 1]
check("5 Model batch order respects view dependencies", not gaps, gaps)

# Check 6: register rows match scope
expected = set()
for r in batches:
    if not r["batch_id"]:
        continue
    if r["object_type"] in ("view", "topic", "dashboard", "look", "schedule", "alert"):
        expected.add(f"{r['object_type']}:{r['object_id']}")
    elif r["object_type"] == "tile":
        expected.add(f"tile:{r['object_id']}")
    elif r["object_type"] == "group":
        expected.add("group:" + r["object_id"].lower().replace(" ", "_"))
have = {r["model"] for r in reg}
gaps = [f"missing {m}" for m in sorted(expected - have)] + [f"unexpected {m}" for m in sorted(have - expected)]
gaps += [f"{r['model']} state {r['state']}" for r in reg if r["state"] not in ("pending", "in_progress", "translated", "validated", "published")]
if STATUS_REGISTER_ROWS != len(reg):
    gaps.append(f"status register_rows {STATUS_REGISTER_ROWS} vs {len(reg)}")
dropped = {f"{r['object_type']}:{r['object_id']}" for r in batches if r["ruling"] == "drop"}
gaps += [f"dropped object in register: {m}" for m in sorted(have & dropped)]
check("6 Register rows match scope", not gaps, gaps)

# Check 7: every ruling made or parked
RULING_ROWS = ["Parity or redesign, per tier", "Drop list", "PDT disposition", "Permission mapping", "Topic architecture", "Parallel-run window", "Parity scope"]
gaps = []
for name in RULING_ROWS:
    m = re.search(r"\| " + re.escape(name) + r" \| (\w[\w ]*) \| ([^|]*) \|", plan)
    if not m:
        gaps.append(f"{name}: not in Rulings table")
        continue
    status, ref = m.group(1).strip(), m.group(2).strip()
    if status == "made":
        rid = ref.split(",")[0].strip()
        if rid not in RULINGS or f"## {rid} " not in decisions:
            gaps.append(f"{name}: cites {rid} which is not in decisions.md")
    elif status == "parked":
        if ref not in PARKED:
            gaps.append(f"{name}: parked as {ref} but {ref} not in status.md parked_decisions")
    elif status == "default applied" and name not in ("Topic architecture", "Permission mapping"):
        gaps.append(f"{name}: defaulted but no default is allowed")
    elif status == "not applicable" and name != "PDT disposition":
        gaps.append(f"{name}: marked not applicable")
check("7 Every ruling is made or parked", not gaps, gaps)

# Check 8: PDT dispositions
pdts = [n for n, v in summ["views"].items() if v.get("pdt")]
gaps = [p for p in pdts if not re.search(r"\| " + re.escape(p) + r" \| \w+ \| (dbt|omni_query_view|drop|parked)", plan)]
check("8 PDT dispositions", not gaps, gaps)

# Check 9: reference key
ids = set(re.findall(r"\b([bc]\d{2})\b", plan)) | set(re.findall(r"\b(R-\d+)\b", plan)) | {"PD-1 to PD-11"}
key = plan.split("## Reference key")[-1]
gaps = [i for i in sorted(ids) if f"| {i} |" not in key and not i.startswith("PD")]
if "PD-1 to PD-11" not in key:
    gaps.append("PD range")
check("9 Reference key", not gaps, gaps)

overall = all(r["result"] == "PASS" for r in results)
sec = ["", "## Validation", "", f"Run {TODAY} by `/wire:bi-migration-plan-validate`. Result: **{'PASS' if overall else 'FAIL'}**.", "",
       "| Check | Result | Gaps | Note |", "|---|---|---|---|"]
for r in results:
    sec.append(f"| {r['check']} | {r['result']} | {r['gap_count']} | {r['note']} |")
sec += ["", "### Gaps to address", ""]
gapl = [(r["check"], g) for r in results for g in r["gaps"]]
sec += [f"- {c}: {g}" for c, g in gapl] or ["- none"]
plan = re.sub(r"\n## Validation\n.*\Z", "\n", plan, flags=re.S)
open(MIG + "bi_migration_plan.md", "w").write(plan.rstrip() + "\n" + "\n".join(sec) + "\n")
print(json.dumps({"overall": "PASS" if overall else "FAIL", "checks": [{k: v for k, v in r.items() if k != "gaps"} for r in results], "gaps": {r["check"]: r["gaps"] for r in results if r["gaps"]}}, indent=1))
