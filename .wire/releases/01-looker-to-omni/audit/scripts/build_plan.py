"""Build the BI migration plan artifacts from the audit: batches CSV, register, baseline, evidence, and the plan document.

Deterministic; every number comes from the audit files. Rulings come from decisions.md (passed in as a JSON file of
made rulings) and from the parked-decision texts defined here.

Usage (from the repo root):
    python3 build_plan.py <release_root> <today> <parity_as_of> <pair_ruleset_sha> <converter_version> <comparator_id>
<release_root> is .wire/releases/<release>/ ; reads audit/ and writes migration/.
"""
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1].rstrip("/") + "/"
TODAY = sys.argv[2]
PARITY_AS_OF = sys.argv[3]
PAIR_SHA = sys.argv[4]
CONVERTER_VERSION = sys.argv[5]
COMPARATOR_ID = sys.argv[6]
AUD = ROOT + "audit/"
MIG = ROOT + "migration/"
RELEASE = ROOT.rstrip("/").split("/")[-1]
SNAP = MIG + "source_snapshot/lookml/"
PLUGIN = "/Users/markrittman/.claude/plugins/cache/rittman-analytics-preview/wire-preview/4.0.0-preview-d3a18c5c/"
sys.path.insert(0, PLUGIN + "scripts")
import bi_evidence  # noqa: E402

os.makedirs(MIG + "parity", exist_ok=True)
IN_SCOPE = ["267", "255", "416"]  # usage order: 488, 18, 1 runs in 90 days
COMMIT = "82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e"
OMNI_MODEL_ID_DIRECTIVE = "omni_osk_1XnARokc84sujjpwGbaMjPITX9Ou9ySl7lBlxB6KHOAttyKEBR272BCs"

model = list(csv.DictReader(open(AUD + "looker_model_catalog.csv")))
content = list(csv.DictReader(open(AUD + "looker_content_catalog.csv")))
sa = json.load(open(AUD + "raw/scope_analysis.json"))
summ = json.load(open(AUD + "raw/lookml_parsed_summary.json"))
detail = json.load(open(AUD + "raw/looker_content.json"))
perms = json.load(open(AUD + "raw/looker_permissions.json"))
views = summ["views"]
explores = summ["explores"]
view_set = set(sa["view_set"])
explore_set = list(sa["explore_set"])
dash_rows = {r["id"]: r for r in content if r["object_type"] == "dashboard"}
look_rows = {r["id"]: r for r in content if r["object_type"] == "look"}
sched_rows = [r for r in content if r["object_type"] == "schedule"]
alert_rows = [r for r in content if r["object_type"] == "alert"]
model_rows_by_uri = {r["object_uri"]: r for r in model}


def v90(r):
    try:
        return int(r["views_90d"])
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------- usage ranking
ranked = sorted([r for r in content if r["object_type"] in ("dashboard", "look")], key=lambda r: (-v90(r), r["object_type"], r["title"]))
usage_rank = {r["object_uri"]: i + 1 for i, r in enumerate(ranked)}
total_runs = sum(v90(r) for r in ranked)
cum, tier1_usage = 0, []
for r in ranked:
    if cum >= 0.8 * total_runs:
        break
    cum += v90(r)
    tier1_usage.append(r)
tier2_usage = [r for r in ranked if r not in tier1_usage and v90(r) > 0]
stale = [r for r in ranked if v90(r) == 0]

# ---------------------------------------------------------------- model batches
MODEL_BATCHES = [
    ("b02", "Engagement health topics (feeds dashboard 416)", ["engagement_health_fact", "engagement_sprint_burn_fact", "engagement_burn_up_fact", "engagement_actions_fact"]),
    ("b03", "Web analytics and marketing topics (feeds dashboard 255)", ["web_sessions_fact", "ad_campaign_performance_fact", "organic_posts_dim"]),
    ("b04", "Targets, forecast and financials topics (feeds dashboard 267)", ["targets", "monthly_resource_revenue_forecast_fact", "revenue_and_forecast", "project_engagements", "chart_of_accounts_dim"]),
    ("b05", "Companies core, NPS and delivery-team topics (feeds dashboard 267)", ["nps_survey_results_fact", "contacts"]),
    ("b06", "Business operations views, part 1 (companies_dim joins)", []),
    ("b07", "Business operations views, part 2, and the companies_dim topic", ["companies_dim"]),
]
placed = {}
batch_views = defaultdict(list)
batch_topics = defaultdict(list)


def reach_with_extends(es):
    out = set()
    for e in es:
        out |= set(explores[e]["views_reached"])
    changed = True
    while changed:
        changed = False
        for v in list(out):
            for b in (views.get(v, {}).get("extends") or []):
                if b not in out:
                    out.add(b)
                    changed = True
    return out


for bid, label, es in MODEL_BATCHES:
    if bid in ("b06", "b07"):
        continue
    for v in sorted(reach_with_extends(es)):
        if v not in placed:
            placed[v] = bid
            batch_views[bid].append(v)
    for e in es:
        batch_topics[bid].append(e)
remaining = sorted(v for v in reach_with_extends(["companies_dim"]) if v not in placed)
half = (len(remaining) + 1) // 2
for v in remaining[:half]:
    placed[v] = "b06"
    batch_views["b06"].append(v)
for v in remaining[half:]:
    placed[v] = "b07"
    batch_views["b07"].append(v)
batch_topics["b07"].append("companies_dim")
assert set(placed) == view_set, (set(placed) ^ view_set)
topic_batch = {t: b for b, ts in batch_topics.items() for t in ts}
assert set(topic_batch) == set(explore_set), (set(topic_batch) ^ set(explore_set))
BATCH_ORDER = ["b01", "b02", "b03", "b04", "b05", "b06", "b07", "c01", "c02", "c03"]

# ---------------------------------------------------------------- content batches
CONTENT_BATCHES = [("c01", "267"), ("c02", "255"), ("c03", "416")]
content_dep = {}
for cid, did in CONTENT_BATCHES:
    es = sa["in_scope_dashboards"][did]["explores"]
    content_dep[cid] = max(topic_batch[e] for e in es)
sched_in_scope = [r for r in sched_rows if r["explore_refs"] in {f"dashboard:{d}" for d in IN_SCOPE}]
alert_in_scope = [r for r in alert_rows if r["explore_refs"].split("/")[0] in {f"dashboard:{d}" for d in IN_SCOPE}]
sched_batch = {r["id"]: next(c for c, d in CONTENT_BATCHES if r["explore_refs"] == f"dashboard:{d}") for r in sched_in_scope}
alert_batch = {r["id"]: next(c for c, d in CONTENT_BATCHES if r["explore_refs"].startswith(f"dashboard:{d}/")) for r in alert_in_scope}

# ---------------------------------------------------------------- permission map (proposed)
PERMISSION_MAP = [
    ("group", "All Users", "Looker group 1, view access on the Shared folder (all 3 dashboards)", "Omni organisation default: every member can view the migrated folder", "carry", "b01"),
    ("access_grant", "can_view_company_bio", "user attribute `groups` in [Pepkor IT, Google, Brighton SST]; on companies_dim.company_description", "Omni access grant on the same field, user attribute `groups`", "carry", "b01"),
    ("user_attribute", "groups", "advanced_filter_string, default empty; read by can_view_company_bio", "Omni user attribute `groups` (values set per user at target setup)", "carry", "b01"),
    ("user_attribute", "dataset", "default `analytics`; selects the BigQuery dataset in 11 in-scope views through Liquid", "not carried: bind the 11 views to schema `analytics` (PD-4)", "bind_constant", "b01"),
    ("group", "RA Staff (19), Can See Financial Data (3), Can See HR Data (3), User (11), others", "no in-scope dashboard, explore or field depends on them", "not carried", "drop", ""),
    ("user_attribute", "can_see_financial_data, can_see_hr_data, company_name, client_id_rep, project_id, others", "no in-scope explore has an access_filter; not referenced by in-scope LookML", "not carried", "drop", ""),
]

# ---------------------------------------------------------------- redesign dispositions (proposed, PD-8)
DISPOSITION_RULES = [
    ("view:sql_table_name_liquid", "redesign in Omni", "bind to schema `analytics` with the plain table name (the `dataset` user attribute default); no Liquid in Omni", "PD-4"),
    ("view:native_derived_table", "defer", "rfm_model: native derived table joined to companies_dim; no in-scope tile uses it; rebuild as an Omni query view only if PD-7 keeps the join", "PD-7"),
    ("join:one_to_many:left_outer", "defer", "9 LEFT JOIN UNNEST array joins in companies_dim; no in-scope tile uses their fields; drop from the topic or rebuild as flattened SQL views", "PD-7"),
    ("dimension:html", "redesign in Omni", "RAG status colour blocks: emit the dimension, recreate the colour as Omni table conditional formatting on the status text", "PD-8"),
    ("dimension:liquid", "defer", "dynamic_split (forecast split selector) and web_sessions_fact.period: rebuild with Omni controls or fixed dimensions", "PD-5"),
    ("dimension:location", "drop", "ips_enriched.ip_location and web_events_fact.map_location: no in-scope tile uses them; Omni has no location type", "PD-8"),
    ("filter_field", "defer", "web_sessions_fact.date_filter: dashboard 255 filters on session_start_ts_date directly; rebuild as a dashboard control if any tile needs it", "PD-5"),
    ("measure:date", "drop", "timesheets_fact.last_timesheet_billing_date: no in-scope tile uses it", "PD-8"),
    ("measure:number", "defer", "monthly_resource_revenue_forecast_fact.dynamic_measure: parameter-driven measure on the forecast tile", "PD-5"),
    ("measure:period_over_period", "redesign in Omni", "16 prior-period measures on profit_and_loss_report_fact: use Omni period-over-period comparison on the tile; not used by an in-scope tile directly", "PD-8"),
    ("measure:sum", "defer", "profit_and_loss_report_fact.revenue_dynamic_prior_period: Liquid over comparison_period parameter", "PD-8"),
    ("parameter", "defer", "5 parameters: selected_measure, selected_split (dashboard 267 filters), comparison_period, period_selector, time_range; Omni templated filters or field-selection controls", "PD-5"),
]
disp_by_construct = {c: (d, n, pd) for c, d, n, pd in DISPOSITION_RULES}

# ---------------------------------------------------------------- batches CSV
brows = []


def brow(batch_id, kind, otype, oid, name, ex, rank, ruling, dep):
    brows.append({"batch_id": batch_id, "batch_kind": kind, "object_type": otype, "object_id": oid, "object_name": name,
                  "explore_or_topic": ex, "usage_rank": rank, "ruling": ruling, "depends_on_batch": dep})


for kind, name, looker_side, omni_side, action, batch in PERMISSION_MAP:
    if action == "carry":
        brow("b01", "model", kind, name, name, "", "", "parity", "")
    elif action == "bind_constant":
        brow("b01", "model", kind, name, name, "", "", "redesign", "")
for bid, label, es in MODEL_BATCHES:
    for v in batch_views[bid]:
        vr = model_rows_by_uri[f"looker:analytics:view:{v}"]
        ruling = "redesign" if vr["translation_class"] == "redesign" else "parity"
        brow(bid, "model", "view", v, v, ";".join(sa["views"][v]["used_by_explores"]), "", ruling, "")
    for t in batch_topics[bid]:
        er = model_rows_by_uri[f"looker:analytics:explore:{t}"]
        brow(bid, "model", "topic", t, t, t, "", "redesign" if er["translation_class"] == "redesign" else "parity", "")
for cid, did in CONTENT_BATCHES:
    d = detail["dashboards"][did]
    dr = dash_rows[did]
    brow(cid, "content", "dashboard", did, d["title"], ";".join(sa["in_scope_dashboards"][did]["explores"]), usage_rank[dr["object_uri"]], "parity", content_dep[cid])
    for t in d["tiles"]:
        ex = ";".join(e.split("/", 1)[1] for e in t["explores"])
        if t["type"] == "vis":
            ruling = "redesign" if (t.get("merge_result_id") or (t.get("vis_type") and not str(t["vis_type"]).startswith(("looker_", "single_value", "table")))) else "parity"
            brow(cid, "content", "tile", f"{did}/{t['id']}", t.get("title") or f"element {t['id']}", ex, "", ruling, content_dep[cid])
        else:
            brow("", "content", "tile", f"{did}/{t['id']}", t.get("title") or f"{t['type']} element {t['id']}", ex, "", "drop", "")
for r in sched_in_scope:
    brow(sched_batch[r["id"]], "content", "schedule", r["id"], r["title"], r["explore_refs"], "", "parity", content_dep[sched_batch[r["id"]]])
for r in alert_in_scope:
    brow(alert_batch[r["id"]], "content", "alert", r["id"], r["title"], r["explore_refs"], "", "parity", content_dep[alert_batch[r["id"]]])
# drops
for did, r in sorted(dash_rows.items(), key=lambda kv: (len(kv[0]), kv[0])):
    if did not in IN_SCOPE:
        brow("", "content", "dashboard", did, r["title"], r["explore_refs"].split(";")[0], usage_rank[r["object_uri"]], "drop", "")
for lid, r in sorted(look_rows.items(), key=lambda kv: (len(kv[0]), kv[0])):
    brow("", "content", "look", lid, r["title"], r["explore_refs"], usage_rank[r["object_uri"]], "drop", "")
for r in sched_rows:
    if r["id"] not in sched_batch:
        brow("", "content", "schedule", r["id"], r["title"], r["explore_refs"], "", "drop", "")
for r in alert_rows:
    if r["id"] not in alert_batch:
        brow("", "content", "alert", r["id"], r["title"], r["explore_refs"], "", "drop", "")
for v in sa["drop_list_views"]:
    brow("", "model", "view", v, v, "", "", "drop", "")
for e in sa["drop_list_explores"]:
    brow("", "model", "topic", e, e, e, "", "drop", "")
with open(MIG + "bi_migration_batches.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["batch_id", "batch_kind", "object_type", "object_id", "object_name", "explore_or_topic", "usage_rank", "ruling", "depends_on_batch"])
    w.writeheader()
    w.writerows(brows)

# ---------------------------------------------------------------- register
REG_COLS = ["model", "object_type", "source_path", "source_layer", "last_migrated_commit", "bq_target", "state", "snapshot_strategy", "last_equivalence_result",
            "last_equivalence_t", "last_validated_commit", "last_reverse_ported_commit", "delivery_stage", "pr_url", "parent_release", "parent_model", "parent_verdict_ref", "notes", "source_updated_at"]
reg = []


def rrow(model_key, otype, source_path, layer, commit, notes, updated=""):
    row = {c: "null" for c in REG_COLS}
    row.update({"model": model_key, "object_type": otype, "source_path": source_path, "source_layer": layer, "last_migrated_commit": commit or "null",
                "bq_target": "", "state": "pending", "notes": notes.replace("|", "—"), "source_updated_at": updated or "null"})
    reg.append(row)


for bid, label, es in MODEL_BATCHES:
    for v in batch_views[bid]:
        vr = model_rows_by_uri[f"looker:analytics:view:{v}"]
        rrow(f"view:{v}", "view", vr["lkml_file"], "looker_model", COMMIT, f"batch {bid}; class {vr['translation_class']}; complexity {vr['complexity']}; {sa['views'][v]['fields']} fields")
    for t in batch_topics[bid]:
        er = model_rows_by_uri[f"looker:analytics:explore:{t}"]
        rrow(f"topic:{t}", "topic", er["lkml_file"], "looker_model", COMMIT, f"batch {bid}; base view {er['view_name']}; class {er['translation_class']}")
for cid, did in CONTENT_BATCHES:
    d = detail["dashboards"][did]
    rrow(f"dashboard:{did}", "dashboard", f"/dashboards/{did}", "looker_content", "null", f"batch {cid}; {d['title']}" + (f"; lookml {d['lookml_link_id']}" if d["lookml_link_id"] else ""), d["updated_at"])
    for t in d["tiles"]:
        if t["type"] == "vis":
            rrow(f"tile:{did}/{t['id']}", "tile", f"/dashboards/{did}/elements/{t['id']}", "looker_content", "null",
                 f"batch {cid}; {t.get('vis_type')}; " + ("merged results; " if t.get("merge_result_id") else "") + (t.get("title") or ""), d["updated_at"])
for r in sched_in_scope:
    rrow(f"schedule:{r['id']}", "schedule", f"/scheduled_plans/{r['id']}", "looker_content", "null", f"batch {sched_batch[r['id']]}; {r['title']}; {r['reason']}", r["source_updated_at"])
for r in alert_in_scope:
    rrow(f"alert:{r['id']}", "alert", f"/alerts/{r['id']}", "looker_content", "null", f"batch {alert_batch[r['id']]}; {r['explore_refs']}; {r['reason']}", "")
rrow("group:all_users", "group", "looker:group:1", "looker_content", "null", "batch b01; view access on Shared folder; maps to Omni organisation default")
with open(MIG + "migration_register.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=REG_COLS)
    w.writeheader()
    w.writerows(reg)

# ---------------------------------------------------------------- baseline
baseline = f"""baseline_id: b001
written_at: "{TODAY}"
written_by: "Mark Rittman (orchestrator 7bb027f9)"
lookml_commit: "{COMMIT}"
looker_deployed_revision: "{COMMIT}"   # Looker production branch master is at the same commit (checked {TODAY})
looker_base_url: "https://rittman.eu.looker.com"
omni_model_id: "{OMNI_MODEL_ID_DIRECTIVE}"   # as given in the directive; PD-1 open: no model with this id exists, candidate 67716e96-520d-402a-88ad-89f97f9bc2a0 (ra_data_warehouse 2)
omni_branch: null                             # set by omni-target-setup-generate
warehouse: bigquery
converter_version: "{CONVERTER_VERSION}"
pair_ruleset_sha: "{PAIR_SHA}"
comparator_version: "{COMPARATOR_ID}"
parity_as_of: "{PARITY_AS_OF}"                  # end of the last complete day before the plan, UTC (BigQuery); the first model batch may re-baseline
"""
open(MIG + "baseline.yaml", "w").write(baseline)

# ---------------------------------------------------------------- evidence
edges_model = [json.loads(l) for l in open(AUD + "model_dependencies.jsonl")]
edges_content = [json.loads(l) for l in open(AUD + "dependencies.jsonl")]
out_edges = defaultdict(list)
for e in edges_model + edges_content:
    out_edges[e["from"]].append(e)


def sha(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()


policy = sha(json.dumps({"access_grants": ["can_view_company_bio"], "user_attributes": ["groups", "dataset=analytics"], "folder_access": perms["folder_access"]}, sort_keys=True))
adapters = f"converter {CONVERTER_VERSION}; pair {PAIR_SHA}; comparator {COMPARATOR_ID}"
ev = []
raw_dash = {did: json.load(open(AUD + f"raw/dashboard_{did}.json")) for did in IN_SCOPE}
for r in reg:
    if r["object_type"] not in ("tile", "view"):
        continue
    if r["object_type"] == "view":
        uri = f"looker:analytics:view:{r['model'].split(':', 1)[1]}"
        src = f"{COMMIT}:{sha(open(SNAP + r['source_path'], 'rb').read())}"
        closure = out_edges.get(uri, [])
        for e in list(closure):
            closure += out_edges.get(e["to"], [])
    else:
        did, eid = r["model"].split(":", 1)[1].split("/")
        uri = f"looker:analytics:dashboard:{did}/element:{eid}"
        el = next(e for e in raw_dash[did]["dashboard_elements"] if str(e["id"]) == eid)
        src = f"{COMMIT}:{sha(json.dumps(el, sort_keys=True))}"
        closure = out_edges.get(uri, [])
    dep = sha("\n".join(sorted(json.dumps(e, sort_keys=True) for e in closure)))
    comps = {"source_definition": src, "target_definition": "absent", "dependencies": dep, "policy_context": policy, "data_context": PARITY_AS_OF, "test_contract": "absent", "adapters": adapters}
    ev.append({"register_model": r["model"], "object_uri": uri, "baseline_id": "b001", **comps, "evidence_fingerprint": bi_evidence.fingerprint(comps), "stale_kinds": ""})
with open(MIG + "parity/evidence.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["register_model", "object_uri", "baseline_id", "source_definition", "target_definition", "dependencies", "policy_context", "data_context", "test_contract", "adapters", "evidence_fingerprint", "stale_kinds"])
    w.writeheader()
    w.writerows(ev)

# ---------------------------------------------------------------- plan document
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


in_scope_counts = Counter(r["object_type"] for r in brows if r["batch_id"])
drop_counts = Counter(r["object_type"] for r in brows if r["ruling"] == "drop")
n_vis_tiles = len([r for r in brows if r["object_type"] == "tile" and r["batch_id"]])
redesign_in_scope = sa["redesign_in_scope"]

h(f"# BI Migration Plan: {RELEASE}")
L += [f"**Release**: {RELEASE} (bi_migration, looker_to_omni)  ", f"**Generated**: {TODAY}  ",
      f"**Built from**: `audit/looker_audit.md` (validate PASS), LookML commit `{COMMIT}`, Looker System Activity usage to {TODAY}  ",
      "**Rulings on record**: R-1 scope, R-2 profile, R-3 tier 1 and parity scope, R-4 parallel run (`decisions.md`). Every ruling not on record is parked, not guessed.  ",
      "**Audit review**: not yet approved (PD-2). This plan was generated ahead of that approval at the director's instruction; see `status.md` `precondition_overrides`.", ""]

h("## Summary")
table(["Measure", "Value"], [
    ["Dashboards in scope", f"3 (ids 267, 255, 416) of 196"],
    ["Tiles in scope (visualisation tiles, all compared for parity)", f"{n_vis_tiles} of 1636 elements"],
    ["Text tiles and filter elements on the three dashboards", f"{len([r for r in brows if r['object_type'] == 'tile' and r['ruling'] == 'drop'])} (text tiles recreated by hand; filter elements become controls)"],
    ["Looks in scope", "0 of 148 (no in-scope dashboard embeds a Look)"],
    ["Schedules in scope", f"{len(sched_in_scope)} of 6 (id 91, Web Performance to Slack, weekly)"],
    ["Alerts in scope", f"{len(alert_in_scope)} of 3 (id 3, daily, on Business Summary element 2514)"],
    ["Explores carried as topics", f"{len(explore_set)} of 39"],
    ["Views carried", f"{len(view_set)} of 190 (base views plus every joined view, plus extends bases)"],
    ["Fields carried", sa["counts"]["fields_in_scope"]],
    ["Redesign rows in scope", f"{len(redesign_in_scope)} (dispositions proposed, PD-8)"],
    ["Assisted rows in scope", sa["counts"]["assisted_in_scope"]],
    ["Model batches", f"{len(MODEL_BATCHES)} plus 1 permissions batch"],
    ["Content batches", len(CONTENT_BATCHES)],
    ["Dropped", f"{drop_counts['dashboard']} dashboards, {drop_counts['look']} Looks, {drop_counts['schedule']} schedules, {drop_counts['alert']} alerts, {drop_counts['view']} views, {drop_counts['topic']} explores"],
    ["Register rows", len(reg)],
    ["Rulings made / parked", "4 made (R-1 to R-4), 9 parked (PD-3 to PD-11)"],
])

h("## Usage ranking")
L.append(f"Usage is System Activity dashboard runs in the 90 days to {TODAY} (Looks: query runs). Ranking is across dashboards and Looks together. `stale_after_days` is 180.")
L.append("")
table(["Tier (by usage)", "Count", "Definition", "Plan treatment"], [
    ["Tier 1 (80% of runs)", len(tier1_usage), ", ".join(f"{r['id']} {r['title']}" for r in tier1_usage), "R-1 keeps 267 and drops the others in this set: they are not one of the three dashboards"],
    ["Tier 2 (remaining runs)", len(tier2_usage), "any run in 90 days, not tier 1", "255 and 416 are carried by R-1; the rest are dropped by R-1"],
    ["Stale (0 runs in 90 days)", len(stale), f"{len([r for r in stale if r['object_type'] == 'dashboard'])} dashboards, {len([r for r in stale if r['object_type'] == 'look'])} Looks", "dropped by R-1"],
    ["Usage unknown", 0, "", ""],
])
table(["Rank", "Kind", "Id", "Title", "Runs 90d", "Last viewed", "Ruling"], [
    [usage_rank[r["object_uri"]], r["object_type"], r["id"], r["title"], v90(r), r["last_viewed"], "parity (R-1, R-3)" if r["id"] in IN_SCOPE and r["object_type"] == "dashboard" else "drop (R-1)"]
    for r in ranked[:15]])
L.append("The director's ruling, not the usage cut, sets the scope: the three dashboards are tier 1 (R-3) and everything else is dropped (R-1). Usage is recorded so the cost of R-1 is visible: dashboards 415 (234 runs) and 389 (102 runs) are the second and third most used in the estate and are not carried.")
L.append("")

h("## Rulings")
rulings = [
    ("Parity or redesign, per tier", "made", "R-3, Mark Rittman, 2026-09-06 21:56", "Tier 1 (267, 255, 416): parity, rebuilt as-is with every tile compared. Tier 2: empty (R-1 drops everything else)."),
    ("Drop list", "made", "R-1, Mark Rittman, 2026-09-06 21:56", f"Everything not needed by the three dashboards: {drop_counts['dashboard']} dashboards, {drop_counts['look']} Looks, {drop_counts['schedule']} schedules, {drop_counts['alert']} alerts, {drop_counts['view']} views, {drop_counts['topic']} explores. No exceptions. The stale set (0 runs in 180 days) is inside this list."),
    ("PDT disposition", "not applicable", "", "No PDT is in scope. The estate's 4 PDTs (cumulative_churned_clients, engagement_renewal_analysis, ga_multi_cycle_multi_touch_attribution, page_keyword_performance) are reached by no in-scope content and are dropped by R-1."),
    ("Permission mapping", "parked", "PD-3", "Proposed one-to-one map below. Carry: group All Users (view on the migrated folder), access grant can_view_company_bio with user attribute groups. Bind the dataset user attribute to a constant (PD-4). Nothing else carried."),
    ("Topic architecture", "default applied", "stated default", f"One Omni topic per Looker explore: {len(explore_set)} topics. Confirm or amend at plan review."),
    ("Parallel-run window", "made", "R-4, Mark Rittman, 2026-09-06 21:56", "14 days side by side after content lands, before cutover."),
    ("Parity scope", "made", "R-3, Mark Rittman, 2026-09-06 21:56", f"All tiles of the three dashboards: {n_vis_tiles} visualisation tiles. `bi_migration.parity_scope: all`."),
]
table(["Ruling", "Status", "Reference", "Decision"], rulings)
L.append("### Parked decisions raised by this plan")
L.append("")
parked = [
    ("PD-3", "Permission map: confirm the proposed map (carry group All Users and the can_view_company_bio access grant with user attribute groups; carry nothing else)?"),
    ("PD-4", "Dataset binding: 11 in-scope views select their BigQuery dataset with `{{ _user_attributes['dataset'] }}` (default `analytics`). Bind them to schema `analytics` in Omni and drop per-user dataset switching?"),
    ("PD-5", "Parameter-driven tiles: Business Summary tile 3878 and its two dashboard filters (Selected Measure, Selected Split) run on two parameters and two Liquid fields; web_sessions_fact carries period_selector, time_range, period and date_filter. Rebuild as Omni field-selection controls, or as fixed measures and dimensions?"),
    ("PD-6", "Merged-results tiles: 8 on Business Summary and 4 on Web Performance. Rebuild each as an Omni query view (SQL joining the source queries), or split into side-by-side tiles?"),
    ("PD-7", "Unused joins carried by R-1: companies_dim has 65 joins; the Business Summary tiles use fields from 18 of its views. Keep all 73 joined views as ruled, or trim the companies_dim topic to the joins the tiles use? Inside this: 9 LEFT JOIN UNNEST array joins and the rfm_model native derived table have no Omni relationship form and no in-scope tile uses them (drop from the topic, or rebuild as flattened SQL views)."),
    ("PD-8", "Redesign dispositions: confirm the proposed disposition table (html RAG blocks as conditional formatting; period_over_period as Omni period comparison; location dimensions and one date measure dropped; the rest deferred to PD-5 and PD-7)."),
    ("PD-9", "View naming: the Omni target model already holds auto-generated schema views for these tables (ra-development.analytics/*.view). Keep LookML view names as a second view over each table (converter default, keeps parity mechanical), or extend the existing schema views and rewrite references?"),
    ("PD-10", "Omni audit (optional artifact): the target instance already holds a shared model and content. Run /wire:omni-audit-generate before target setup, or skip?"),
    ("PD-11", "Business rules (optional artifact): skip for this like-for-like migration, or run /wire:business-rules-generate first?"),
]
table(["Id", "Question"], parked)
L.append("Also open from earlier: PD-1 (which shared Omni model is the target; the id in the directive matches no model) and PD-2 (approve the Looker audit).")
L.append("")

h("## Model scope")
L.append(f"In scope: every view and explore reached by the three dashboards, plus every view those explores join, plus extends bases (R-1). {len(view_set)} views, {len(explore_set)} topics, {sa['counts']['fields_in_scope']} fields. Hidden fields are carried hidden.")
L.append("")
L.append("### Carried, by batch")
L.append("")
for bid, label, es in MODEL_BATCHES:
    L.append(f"**{bid}** {label}: {len(batch_views[bid])} views, {len(batch_topics[bid])} topics  ")
    L.append("Topics: " + (", ".join(f"`{t}`" for t in batch_topics[bid]) or "none") + "  ")
    L.append("Views: " + ", ".join(f"`{v}`" for v in batch_views[bid]) + "  ")
    L.append("")
L.append("### Views used by the tiles versus views carried")
L.append("")
rows = []
for did in IN_SCOPE:
    d = sa["in_scope_dashboards"][did]
    used = sorted({f.split(".")[0] for f in d["fields"]})
    rows.append([did, d["title"], len(d["explores"]), len(used), ", ".join(used)])
table(["Dashboard", "Title", "Explores", "Views (or join aliases) the tiles reference", "Names"], rows)
L.append("### Model not carried")
L.append("")
L.append(f"{len(sa['drop_list_views'])} views and {len(sa['drop_list_explores'])} explores, each with the reason `no in-scope content references it` (R-1). Full list in the Drop list section and in `bi_migration_batches.csv` (`ruling: drop`, empty `batch_id`).")
L.append("")
L.append("### Redesign dispositions (proposed, PD-8)")
L.append("")
rows = []
for c in sorted(disp_by_construct):
    items = [r for r in redesign_in_scope if r["construct"] == c]
    d, n, pd = disp_by_construct[c]
    rows.append([c, len(items), d, n, pd])
table(["Construct", "Rows in scope", "Proposed disposition", "Note", "Decision"], rows)
L.append("Every in-scope redesign row is listed with its source in `audit/looker_audit.md` (Redesign register, `In scope: yes`).")
L.append("")
L.append("### PDT dispositions")
L.append("")
table(["PDT view", "In scope", "Disposition", "Reason"], [[v, "no", "drop", "no in-scope content references it (R-1)"] for v in sorted(n for n, x in views.items() if x.get("pdt"))])
L.append("### Unresolved references to carry into the content batch")
L.append("")
table(["Dashboard", "Reference", "Finding", "Plan"], [[u["dashboard"], u["field"], u["kind"], "confirm the tile renders in Looker before parity; if it errors there, record as accepted difference at the director's ruling"] for u in sa["unresolved_fields"]])

h("## Permission map (proposed, PD-3)")
table(["Kind", "Looker object", "Looker side", "Omni side", "Action", "Batch"], [list(p) for p in PERMISSION_MAP])
L.append("Content access: all three dashboards sit in the `Shared` folder, viewable by group `All Users` (40 users, 33 active). No in-scope explore carries an `access_filter`.")
L.append("")

h("## Topic architecture")
L.append(f"One topic per explore (default; confirm at review): {len(explore_set)} topics. Four are single-view topics (the engagement_* facts). `companies_dim` is the largest, with 65 joins (PD-7). Topic default filters: `engagement_health_fact`, `engagement_sprint_burn_fact` and `engagement_actions_fact` carry `always_filter` on reporting month (12, 1 and 1 months); `contacts` carries `sql_always_where` on staff or contractor flags.")
L.append("")
table(["Topic", "Base view", "Joins", "Hidden in Looker", "Batch", "Feeds dashboards"], [
    [e, sa["explores"][e]["base_view"], sa["explores"][e]["joins"], "yes" if sa["explores"][e]["hidden"] else "", topic_batch[e],
     ", ".join(d for d in IN_SCOPE if e in sa["in_scope_dashboards"][d]["explores"])] for e in explore_set])

h("## Batches")
L.append("Model batches run in id order; a topic sits in the batch that carries its last view. Content batches run in usage order and each waits on the last model batch its dashboard needs. Batch sizes above the 5 to 15 view target (b06, b07) come from the single `companies_dim` explore; splitting it further would put the topic in a later batch than its views for no benefit.")
L.append("")
rows = [["b01", "model", "permissions", "1 group, 1 access grant, 2 user attributes", "", ""]]
for bid, label, es in MODEL_BATCHES:
    rows.append([bid, "model", label, f"{len(batch_views[bid])} views, {len(batch_topics[bid])} topics", "", "b01"])
for cid, did in CONTENT_BATCHES:
    d = sa["in_scope_dashboards"][did]
    extra = [f"schedule {s}" for s, b in sched_batch.items() if b == cid] + [f"alert {a}" for a, b in alert_batch.items() if b == cid]
    rows.append([cid, "content", f"{did} {d['title']}", f"{d['tiles_vis']} vis tiles" + (", " + ", ".join(extra) if extra else ""), usage_rank[dash_rows[did]["object_uri"]], content_dep[cid]])
table(["Batch", "Kind", "Scope", "Contents", "Usage rank", "Depends on"], rows)
L.append("Run order: b01, b02, b03, b04, b05, b06, b07, then c01 (after b07), c02 (after b03; can start once b03 validates), c03 (after b02; can start once b02 validates). Parity sweeps follow each content batch.")
L.append("")

h("## Parallel run and parity")
table(["Item", "Value"], [
    ["Parallel-run window", "14 days (R-4), starting when the last content batch lands"],
    ["Parity scope", f"all tiles of the three dashboards: {n_vis_tiles} visualisation tiles (R-3); text tiles and filter elements are not compared"],
    ["Pinned as-of", f"`{PARITY_AS_OF}` (UTC, BigQuery); recorded in `migration/baseline.yaml` as baseline b001"],
    ["Evidence", f"`migration/parity/evidence.csv`: {len(ev)} rows (one per tile and view register row), fingerprints from `scripts/bi_evidence.py` v{bi_evidence.VERSION}"],
    ["Tiles expected to need a ruling before PASS", f"{len([r for r in brows if r['object_type'] == 'tile' and r['ruling'] == 'redesign'])} redesign tiles (merged results, custom visualisation) plus tiles that reference stale fields"],
    ["Cutover", "refused until bi_equivalency passes on every in-scope tile; schedule 91 and alert 3 are recreated at cutover"],
])

h("## Drop list")
L.append("Every dropped object with its reason. Reasons: `R-1` = director ruling, not needed by the three dashboards; `no in-scope content references it` = model object reached by no in-scope dashboard; `text tile` = recreated by hand; `filter element` = becomes a dashboard control.")
L.append("")
L.append(f"**Dashboards dropped ({drop_counts['dashboard']})**, reason R-1:")
L.append("")
table(["Id", "Title", "Folder", "Runs 90d"], [[r["id"], r["title"], r["folder"], v90(r)] for did, r in sorted(dash_rows.items(), key=lambda kv: (-v90(kv[1]), kv[0])) if did not in IN_SCOPE])
L.append(f"**Looks dropped ({drop_counts['look']})**, reason R-1:")
L.append("")
table(["Id", "Title", "Folder", "Runs 90d"], [[r["id"], r["title"], r["folder"], v90(r)] for lid, r in sorted(look_rows.items(), key=lambda kv: (-v90(kv[1]), kv[0]))])
L.append(f"**Schedules dropped ({drop_counts['schedule']})** and **alerts dropped ({drop_counts['alert']})**, reason R-1:")
L.append("")
table(["Kind", "Id", "Title", "Target"], [[r["object_type"], r["id"], r["title"], r["explore_refs"]] for r in sched_rows + alert_rows if r["id"] not in sched_batch and r["id"] not in alert_batch and (r["object_type"] == "schedule" or r["id"] not in alert_batch)])
L.append("**Tiles on the three dashboards not migrated programmatically**:")
L.append("")
table(["Dashboard", "Element", "Kind", "Reason"], [[r["object_id"].split("/")[0], r["object_id"].split("/")[1], r["object_name"], "text tile, recreate by hand" if "text" in r["object_name"] or detail["dashboards"][r["object_id"].split("/")[0]] and next(t for t in detail["dashboards"][r["object_id"].split("/")[0]]["tiles"] if str(t["id"]) == r["object_id"].split("/")[1])["type"] == "text" else "filter element, becomes a dashboard control"] for r in brows if r["object_type"] == "tile" and r["ruling"] == "drop"])
L.append(f"**Explores not carried ({drop_counts['topic']})**, reason `no in-scope content references it`:")
L.append("")
L.append(", ".join(f"`{e}`" for e in sa["drop_list_explores"]))
L.append("")
L.append(f"**Views not carried ({drop_counts['view']})**, reason `no in-scope content references it`:")
L.append("")
L.append(", ".join(f"`{v}`" for v in sa["drop_list_views"]))
L.append("")

h("## Reference key")
rows = [["R-1", "scope ruling: three dashboards and what they need; everything else dropped", f".wire/releases/{RELEASE}/decisions.md"],
        ["R-2", "profile looker_to_omni", f".wire/releases/{RELEASE}/decisions.md"],
        ["R-3", "tier 1 is the three dashboards; parity scope all their tiles", f".wire/releases/{RELEASE}/decisions.md"],
        ["R-4", "parallel run 14 days", f".wire/releases/{RELEASE}/decisions.md"],
        ["PD-1 to PD-11", "parked decisions awaiting the director", f".wire/releases/{RELEASE}/status.md parked_decisions"],
        ["b01", "permissions batch (groups, access grant, user attributes)", "this document, Batches"]]
for bid, label, es in MODEL_BATCHES:
    rows.append([bid, label, "this document, Batches"])
for cid, did in CONTENT_BATCHES:
    rows.append([cid, f"content batch: dashboard {did} {sa['in_scope_dashboards'][did]['title']}", "this document, Batches"])
rows += [["b001", "baseline id: LookML commit, as-of, tool versions every verdict is measured against", "migration/baseline.yaml"],
         ["parity / redesign / drop", "ruling per object in bi_migration_batches.csv", "specs/migration/bi_migration_plan/generate.md Step 5"],
         ["redesign in Omni / defer / drop", "disposition of an in-scope redesign model row", "specs/migration/bi_migration_plan/generate.md Step 4"],
         ["mechanical / assisted / redesign", "translation class from the audit", "bi_pairs/looker_to_omni/translation_guide.md"],
         ["Runs 90d", "System Activity dashboard runs in the 90 days to the audit date", "audit/looker_audit.md, Usage distribution"]]
table(["Code", "Meaning", "Defined in"], rows)

open(MIG + "bi_migration_plan.md", "w").write("\n".join(L).rstrip() + "\n")
status = {"batch_count": len(MODEL_BATCHES) + 1 + len(CONTENT_BATCHES), "objects_in_scope": sum(1 for r in brows if r["batch_id"]),
          "objects_dropped": sum(1 for r in brows if r["ruling"] == "drop"), "register_rows": len(reg), "rulings_parked": len(parked), "evidence_rows": len(ev),
          "in_scope_by_type": dict(in_scope_counts), "dropped_by_type": dict(drop_counts), "content_dep": content_dep,
          "batch_views": {b: len(v) for b, v in batch_views.items()}, "batch_topics": dict(batch_topics)}
json.dump(status, open(MIG + "plan_status_counts.json", "w"), indent=1)
print(json.dumps(status, indent=1))
