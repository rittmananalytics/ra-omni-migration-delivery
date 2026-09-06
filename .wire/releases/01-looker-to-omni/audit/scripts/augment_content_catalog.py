"""Post-process the content catalog: add alert rows from raw/looker_alerts.json and flag content rows whose
explore or field references fall outside the parsed LookML project (reason: references field outside the parsed repo).

Deterministic. Rewrites looker_content_catalog.csv in place with the same column contract and sort order.
Usage (from the repo root):
    python3 augment_content_catalog.py <audit_out_dir> <lookml_project_name>
"""
import csv
import json
import os
import sys
from collections import defaultdict

OUT = sys.argv[1].rstrip("/") + "/"
PROJECT = sys.argv[2] if len(sys.argv) > 2 else "analytics"
COLS = ["object_type", "object_uri", "id", "title", "folder", "owner", "last_viewed", "views_90d", "source_updated_at",
        "tile_count", "explore_refs", "fields_refs", "has_text_tile", "translation_class", "reason"]

content = list(csv.DictReader(open(OUT + "looker_content_catalog.csv")))
model = list(csv.DictReader(open(OUT + "looker_model_catalog.csv")))
summ = json.load(open(OUT + "raw/lookml_parsed_summary.json"))
detail = json.load(open(OUT + "raw/looker_content.json"))

fields = defaultdict(set)
groups = defaultdict(set)
for r in model:
    if r["object_type"] in ("dimension", "dimension_group", "measure", "filter", "parameter"):
        fields[r["view_name"]].add(r["field_name"])
        if r["object_type"] == "dimension_group":
            groups[r["view_name"]].add(r["field_name"])
explores = summ["explores"]
alias = defaultdict(dict)  # explore -> alias -> view
for e, x in explores.items():
    for j in x["joins"]:
        alias[e][j["join"]] = j["view"]


def field_exists(view, field):
    if field in fields.get(view, ()):
        return True
    return any(field.startswith(g + "_") for g in groups.get(view, ()))


def resolve(ref, dash_explores):
    if "." not in ref:
        return True
    v, f = ref.split(".", 1)
    if field_exists(v, f):
        return True
    for e in dash_explores:
        t = alias.get(e, {}).get(v)
        if t and field_exists(t, f):
            return True
    return False


def annotate(row):
    refs = [x for x in row["explore_refs"].split(";") if x]
    dash_explores = {x.split("/", 1)[1] for x in refs if x.startswith(PROJECT + "/")}
    outside = [x for x in refs if not x.startswith(PROJECT + "/")]
    outside += [x.split("/", 1)[1] for x in refs if x.startswith(PROJECT + "/") and x.split("/", 1)[1] not in explores]
    bad_fields = [f for f in row["fields_refs"].split(";") if f and not resolve(f, dash_explores)]
    if outside or bad_fields:
        note = "references field outside the parsed repo"
        det = []
        if outside:
            det.append("explores: " + ", ".join(sorted(set(outside))[:6]))
        if bad_fields:
            det.append("fields: " + ", ".join(sorted(set(bad_fields))[:6]))
        note += " (" + "; ".join(det) + ")"
        row["reason"] = (row["reason"] + "; " if row["reason"] else "") + note.replace("|", "—")
    return row


rows = []
for r in content:
    if r["object_type"] == "alert":
        continue  # rebuilt below
    if r["object_type"] in ("dashboard", "look", "tile"):
        r["reason"] = "; ".join(p for p in r["reason"].split("; ") if not p.startswith("references field outside the parsed repo"))
        r = annotate(r)
    rows.append(r)

users = {}
for did, d in detail["dashboards"].items():
    users[did] = d["owner"]
alerts_path = OUT + "raw/looker_alerts.json"
alerts = json.load(open(alerts_path)) if os.path.exists(alerts_path) else []
el_to_dash = {}
for did, d in detail["dashboards"].items():
    for t in d["tiles"]:
        el_to_dash[str(t["id"])] = did
for a in alerts:
    did = el_to_dash.get(str(a.get("dashboard_element_id")), "")
    rows.append({"object_type": "alert", "object_uri": f"looker:{PROJECT}:alert:{a.get('id')}", "id": str(a.get("id")),
                 "title": a.get("custom_title") or a.get("description") or f"alert on element {a.get('dashboard_element_id')}",
                 "folder": detail["dashboards"].get(did, {}).get("folder", ""), "owner": str(a.get("owner_id")),
                 "last_viewed": "", "views_90d": "", "source_updated_at": "", "tile_count": "",
                 "explore_refs": f"dashboard:{did}/element:{a.get('dashboard_element_id')}" if did else f"element:{a.get('dashboard_element_id')}",
                 "fields_refs": (a.get("field") or {}).get("name", "") if isinstance(a.get("field"), dict) else "",
                 "has_text_tile": "false", "translation_class": "mechanical",
                 "reason": f"cron {a.get('cron')}; disabled {a.get('is_disabled')}; threshold {a.get('comparison_type')} {a.get('threshold')}".replace("|", "—")})
detail["alerts"] = alerts
json.dump(detail, open(OUT + "raw/looker_content.json", "w"), indent=1, sort_keys=True, default=str)

ORDER = ["dashboard", "look", "tile", "schedule", "alert", "folder"]
rows.sort(key=lambda r: (ORDER.index(r["object_type"]), len(str(r["id"])), str(r["id"]), r["object_uri"]))
with open(OUT + "looker_content_catalog.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
from collections import Counter  # noqa: E402

print(json.dumps({"rows_by_type": dict(Counter(r["object_type"] for r in rows)),
                  "rows_flagged_outside_repo": len([r for r in rows if "references field outside the parsed repo" in r["reason"]]),
                  "dashboards_flagged": [r["id"] for r in rows if r["object_type"] == "dashboard" and "references field outside the parsed repo" in r["reason"]][:60]}, indent=1))
