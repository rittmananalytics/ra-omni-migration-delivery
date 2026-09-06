"""Parse the LookML snapshot and classify every model construct for the Looker to Omni audit.

Deterministic: same snapshot, same output. Applies the four-class rule from
bi_pairs/looker_to_omni/translation_guide.md and the tags from feature_detection.md.

Usage (from the repo root):
    python3 lookml_audit_parse.py <lookml_snapshot_dir> <audit_out_dir> <lookml_commit> [project_name]

Writes:
    <audit_out_dir>/looker_model_catalog.csv
    <audit_out_dir>/model_dependencies.jsonl     (model-side edges: view contains field, field references field,
                                                   explore base_view, explore joins view)
    <audit_out_dir>/raw/lookml_parsed_summary.json
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

import lkml

SNAP = sys.argv[1].rstrip("/") + "/"
OUT = sys.argv[2].rstrip("/") + "/"
COMMIT = sys.argv[3] if len(sys.argv) > 3 else ""
PROJECT = sys.argv[4] if len(sys.argv) > 4 else "analytics"

LIQUID = re.compile(r"\{%|%\}|\{\{|\}\}")
FIELD_REF = re.compile(r"\$\{([A-Za-z_][\w]*)(?:\.([A-Za-z_]\w*))?\}")
DECL_RX = re.compile(r"^[ \t]*(view|explore|join|dimension|dimension_group|measure|filter|parameter|set)[ \t]*:[ \t]*(\+?\w+)[ \t]*\{", re.M)
PDT_KEYS = ("datagroup_trigger", "sql_trigger_value", "persist_for", "materialized_view", "increment_key",
            "cluster_keys", "partition_keys", "indexes", "distribution")
VALUE_FORMAT_NAMES = {"usd", "usd_2", "usd_0", "eur", "eur_0", "gbp", "gbp_0", "id",
                      "decimal_0", "decimal_1", "decimal_2", "decimal_3", "decimal_4",
                      "percent_0", "percent_1", "percent_2", "percent_3", "percent_4"}
VALUE_FORMATS = {"#,##0", "0", "#,##0.0", "0.0", "#,##0.00", "0.00", "0%", "0.0%", "0.00%",
                 "$#,##0", "$#,##0.00", "£#,##0", "£#,##0.00", "€#,##0", "€#,##0.00"}
TIMEFRAMES = {"raw", "time", "date", "week", "month", "quarter", "year", "hour", "minute", "second", "millisecond",
              "day_of_week", "day_of_week_index", "day_of_month", "day_of_year", "hour_of_day", "month_name",
              "month_num", "quarter_of_year", "fiscal_quarter", "fiscal_year"}
MEASURE_TYPES_MECH = {"sum", "count", "count_distinct", "average", "min", "max", "median", "list", "percentile",
                      "sum_distinct", "average_distinct", "median_distinct", "percentile_distinct"}
MEASURE_TYPES_REDESIGN = {"running_total", "percent_of_total", "percent_of_previous", "date", "string", "yesno"}
DATE_EXPR = re.compile(r"^(\d+\s+(second|minute|hour|day|week|month|quarter|year)s?(\s+ago)?|(last|this|next)\s+\w+|before\s.*|after\s.*|today|yesterday|tomorrow|\d{4}-\d{2}-\d{2}.*)$", re.I)
KIND_SINGULAR = {"dimensions": "dimension", "dimension_groups": "dimension_group", "measures": "measure", "filters": "filter", "parameters": "parameter", "sets": "set"}
FIELD_KINDS = tuple(KIND_SINGULAR)


class Locator:
    """Line numbers of declarations in one file, resolved within the span of the enclosing view or explore."""

    def __init__(self, text):
        self.decls = [(text.count("\n", 0, m.start()) + 1, m.group(1), m.group(2)) for m in DECL_RX.finditer(text)]
        self.tops = [(l, k, n) for l, k, n in self.decls if k in ("view", "explore")]

    def top_line(self, kind, name, occurrence=0):
        c = [l for l, k, n in self.tops if k == kind and n == name]
        return c[occurrence] if len(c) > occurrence else ""

    def span(self, start):
        if start == "":
            return (0, 10**9)
        nxt = [l for l, k, n in self.tops if l > start]
        return (start, min(nxt) if nxt else 10**9)

    def inner(self, span, kind, name):
        c = [l for l, k, n in self.decls if span[0] < l < span[1] and k == kind and n == name]
        return c[0] if c else ""


def has_liquid(*vals):
    return any(isinstance(v, str) and LIQUID.search(v) for v in vals)


def filter_expr_class(expr):
    """Return 'mechanical' or 'assisted' for one LookML filter expression string."""
    e = str(expr).strip()
    if DATE_EXPR.match(e):
        return "assisted"
    if e.upper() in ("NULL", "-NULL", "YES", "NO"):
        return "mechanical"
    if re.match(r"^(>=|<=|>|<)\s*-?[\d.]+$", e):
        return "mechanical"
    if re.match(r"^\[.*,.*\]$", e):
        return "mechanical"
    parts = [p.strip() for p in e.split(",")]
    neg = [p.startswith("-") for p in parts]
    if any(neg) and not all(neg):
        return "assisted"  # mixed include and exclude
    for p in parts:
        core = p[1:] if p.startswith("-") else p
        if "%" in core and not (core.startswith("%") and core.endswith("%") and core.count("%") == 2) \
                and not (core.count("%") == 1 and (core.startswith("%") or core.endswith("%"))):
            return "assisted"  # wildcard inside a value
    return "mechanical"


def measure_filters(m):
    """Yield (field, expression) pairs from either lkml filter representation."""
    out = []
    for blk in m.get("filters__all", []) or []:
        for f in blk:
            if isinstance(f, dict):
                if "field" in f:
                    out.append((f.get("field"), f.get("value")))
                else:
                    out += list(f.items())
    for f in m.get("filters", []) or []:
        if isinstance(f, dict):
            if "field" in f:
                out.append((f.get("field"), f.get("value")))
            else:
                out += list(f.items())
    return out


rows = []
edges = []
view_defs = {}        # name -> merged view dict
view_files = {}       # name -> (file, line)
refinements = defaultdict(list)
explore_defs = []     # (explore dict, file, line)
parse_errors = []
lkml_files = []

for root, dirs, files in os.walk(SNAP):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in sorted(files):
        if not f.endswith((".lkml", ".lookml")):
            continue
        if f.endswith(".dashboard.lookml") or "/dashboards/" in (root + "/"):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, SNAP)
        lkml_files.append(rel)
        text = open(path, errors="replace").read()
        try:
            parsed = lkml.load(text)
        except Exception as e:  # noqa: BLE001
            parse_errors.append((rel, str(e)[:200]))
            continue
        loc = Locator(text)
        seen = Counter()
        for v in parsed.get("views", []) or []:
            name = v["name"]
            line = loc.top_line("view", name, seen[("view", name)])
            seen[("view", name)] += 1
            span = loc.span(line)
            for kind in FIELD_KINDS:
                for fld in v.get(kind, []) or []:
                    fld["_src"] = (rel, loc.inner(span, KIND_SINGULAR[kind], fld["name"]))
            if name.startswith("+"):
                refinements[name[1:]].append((v, rel, line))
            else:
                if name in view_defs:
                    parse_errors.append((rel, f"duplicate view definition: {name}"))
                view_defs[name] = v
                view_files[name] = (rel, line)
        for e in parsed.get("explores", []) or []:
            line = loc.top_line("explore", e["name"], seen[("explore", e["name"])])
            seen[("explore", e["name"])] += 1
            span = loc.span(line)
            for j in e.get("joins", []) or []:
                j["_src_line"] = loc.inner(span, "join", j["name"])
            explore_defs.append((e, rel, line))

# Merge refinements into their base view (fields override by name)
refined_by = {}
for base, refs in refinements.items():
    if base not in view_defs:
        view_defs[base] = {"name": base, "_unresolved_base": True}
        view_files[base] = (refs[0][1], refs[0][2])
    v = view_defs[base]
    for rv, rel, line in refs:
        refined_by.setdefault(base, []).append(rel)
        for kind in FIELD_KINDS:
            if kind in rv:
                existing = {f["name"]: f for f in v.get(kind, [])}
                for f in rv[kind]:
                    existing[f["name"]] = {**existing.get(f["name"], {}), **f}
                v[kind] = list(existing.values())
        for k, val in rv.items():
            if k not in FIELD_KINDS and k != "name":
                v[k] = val


def uri_view(n):
    return f"looker:{PROJECT}:view:{n}"


def uri_field(v, f):
    return f"looker:{PROJECT}:field:{v}:{f}"


def uri_explore(n):
    return f"looker:{PROJECT}:explore:{n}"


def uri_join(e, j):
    return f"looker:{PROJECT}:join:{e}:{j}"


def add_row(object_type, object_uri, view_name, explore_name, field_name, construct, cls, complexity, reason, lkml_file, line):
    rows.append({
        "object_type": object_type, "object_uri": object_uri, "view_name": view_name or "", "explore_name": explore_name or "",
        "field_name": field_name or "", "construct": construct, "translation_class": cls, "complexity": complexity,
        "reason": reason.replace("|", "—"), "lkml_file": lkml_file, "line": line, "lookml_commit": COMMIT,
    })


def refs_in(sql, view_name, dim_group_names):
    """Return set of (view, field) referenced by ${...} in sql. Same-view refs use view_name."""
    out = set()
    for m in FIELD_REF.finditer(sql or ""):
        a, b = m.group(1), m.group(2)
        if a == "TABLE":
            continue
        if b:
            out.add((a, b))
        else:
            base = a
            for g in dim_group_names:
                if a.startswith(g + "_"):
                    base = g
                    break
            out.add((view_name, base))
    return out


CX = {"mechanical": "Low", "assisted": "Medium", "redesign": "High"}
view_summary = {}
for vname in sorted(view_defs):
    v = view_defs[vname]
    rel, line = view_files[vname]
    view_class, view_reason, construct = "mechanical", "", "view"
    dt = v.get("derived_table")
    if v.get("_unresolved_base"):
        view_class, view_reason, construct = "redesign", "refinement of a view not defined in this project", "view:refinement_orphan"
    elif dt is not None:
        pdt = [k for k in PDT_KEYS if k in dt]
        if pdt:
            view_class, view_reason, construct = "redesign", f"PDT ({', '.join(pdt)}): plan rules dbt model or Omni query view", "view:pdt"
        elif "explore_source" in dt:
            view_class, view_reason, construct = "redesign", "native derived table (explore_source): rebuild as Omni query view", "view:native_derived_table"
        elif has_liquid(dt.get("sql", "")):
            view_class, view_reason, construct = "redesign", "Liquid in derived_table sql", "view:derived_table_liquid"
        else:
            view_class, view_reason, construct = "mechanical", "ephemeral derived table: becomes an Omni sql view", "view:derived_table"
    elif "sql_table_name" in v:
        if has_liquid(v["sql_table_name"]):
            view_class, view_reason, construct = "redesign", "Liquid in sql_table_name", "view:sql_table_name_liquid"
        else:
            construct, view_reason = "view:table", f"sql_table_name {v['sql_table_name']}"
    elif v.get("extends__all") or v.get("extends"):
        construct, view_reason = "view:extends", "extends base view(s)"
    elif v.get("extension") == "required":
        construct, view_reason = "view:extension_required", "template view (extension: required)"
    else:
        construct, view_reason = "view:no_table", "no sql_table_name or derived_table: table name defaults to view name"
    if vname in refined_by:
        view_reason = (view_reason + "; " if view_reason else "") + "refined by " + ", ".join(refined_by[vname])

    dim_groups = v.get("dimension_groups", []) or []
    dg_names = [g["name"] for g in dim_groups]
    dim_names = {d["name"] for d in v.get("dimensions", []) or []}
    field_count = 0
    field_classes = Counter()

    for d in v.get("dimensions", []) or []:
        field_count += 1
        src = d.get("_src", (rel, ""))
        sql = d.get("sql", "") or ""
        typ = d.get("type", "string")
        cls, reason, con = "mechanical", "", "dimension"
        if has_liquid(sql, d.get("label", "")):
            cls, reason, con = "redesign", "Liquid in sql or label: templated filter or dashboard control", "dimension:liquid"
        elif typ in ("location", "distance", "bin"):
            cls, reason, con = "redesign", f"type: {typ} has no Omni equivalent", f"dimension:{typ}"
        elif "html" in d:
            cls, reason, con = "redesign", "html (Liquid) withheld; the dimension itself is still emitted", "dimension:html"
        else:
            notes = []
            if typ == "tier":
                con = "dimension:tier"
            if "case" in d:
                con = "dimension:case"
                whens = d["case"].get("whens", []) if isinstance(d["case"], dict) else []
                simple = all(re.match(r"^\s*\$\{[\w.]+\}\s*(=|IN\b)", str(w.get("sql", "")), re.I) for w in whens) if whens else False
                notes.append("case dimension: simple equality cases become groups; confirm labels and else bucket" if simple
                             else "case dimension with non-equality conditions: write Omni sql by hand")
            if d.get("links") or d.get("link"):
                notes.append("link: confirm Omni links syntax and Mustache tokens")
            if has_liquid(d.get("group_label", ""), d.get("view_label", ""), d.get("description", "")):
                notes.append("Liquid in group_label, view_label or description: resolve to a literal by hand")
            xrefs = {a for a, b in refs_in(sql, vname, dg_names) if a != vname}
            if xrefs:
                notes.append("cross-view field reference (" + ", ".join(sorted(xrefs)) + "): confirm every exposing topic joins it")
            if "value_format" in d and str(d["value_format"]).strip('"') not in VALUE_FORMATS:
                notes.append(f"custom value_format {d['value_format']!r} not in mapping table")
            if "value_format_name" in d and d["value_format_name"] not in VALUE_FORMAT_NAMES:
                notes.append(f"value_format_name {d['value_format_name']!r} not in mapping table")
            drills = d.get("drill_fields", []) or []
            if any("." in x and x.split(".")[0] != vname for x in drills):
                notes.append("drill_fields across views")
            if notes:
                cls, reason = "assisted", "; ".join(notes)
            elif not sql or re.fullmatch(r"\s*\$\{TABLE\}\.\w+\s*", sql):
                con = "dimension:column"
            else:
                con = "dimension:derived" if con == "dimension" else con
        field_classes[cls] += 1
        add_row("dimension", uri_field(vname, d["name"]), vname, "", d["name"], con, cls, CX[cls], reason, src[0], src[1])
        edges.append({"from": uri_view(vname), "to": uri_field(vname, d["name"]), "kind": "contains"})
        for a, b in refs_in(sql, vname, dg_names):
            edges.append({"from": uri_field(vname, d["name"]), "to": uri_field(a, b), "kind": "references"})

    for g in dim_groups:
        field_count += 1
        src = g.get("_src", (rel, ""))
        sql = g.get("sql", "") or ""
        typ = g.get("type", "time")
        cls, reason, con = "mechanical", "", "dimension_group:time"
        if has_liquid(sql, g.get("sql_start", ""), g.get("sql_end", ""), g.get("label", "")):
            cls, reason, con = "redesign", "Liquid in dimension_group sql", "dimension_group:liquid"
        elif typ == "duration":
            cls, reason, con = "assisted", "duration group: confirm Omni duration parameter shape before validate", "dimension_group:duration"
        else:
            notes = []
            tfs = g.get("timeframes", []) or []
            unmapped = [t for t in tfs if t not in TIMEFRAMES]
            if unmapped:
                notes.append("timeframes with no Omni equivalent dropped: " + ", ".join(unmapped))
            if g["name"] in dim_names:
                notes.append("dimension_group name collides with a dimension: rename one by hand")
            xrefs = {a for a, b in refs_in(sql, vname, dg_names) if a != vname}
            if xrefs:
                notes.append("cross-view field reference (" + ", ".join(sorted(xrefs)) + ")")
            if has_liquid(g.get("group_label", ""), g.get("view_label", ""), g.get("description", "")):
                notes.append("Liquid in group_label, view_label or description: resolve to a literal by hand")
            if notes:
                cls, reason = "assisted", "; ".join(notes)
        field_classes[cls] += 1
        add_row("dimension_group", uri_field(vname, g["name"]), vname, "", g["name"], con, cls, CX[cls], reason, src[0], src[1])
        edges.append({"from": uri_view(vname), "to": uri_field(vname, g["name"]), "kind": "contains"})
        for a, b in refs_in(sql, vname, dg_names):
            edges.append({"from": uri_field(vname, g["name"]), "to": uri_field(a, b), "kind": "references"})

    for m in v.get("measures", []) or []:
        field_count += 1
        src = m.get("_src", (rel, ""))
        sql = m.get("sql", "") or ""
        typ = m.get("type", "")
        cls, reason, con = "mechanical", "", f"measure:{typ or 'untyped'}"
        if has_liquid(sql, m.get("label", "")):
            cls, reason = "redesign", "Liquid in measure sql or label"
        elif typ in MEASURE_TYPES_REDESIGN:
            cls, reason = "redesign", f"type: {typ} has no Omni aggregate_type: table calculation on the tile"
        elif "html" in m:
            cls, reason = "redesign", "html (Liquid) withheld; the measure itself is still emitted"
        elif typ and typ not in MEASURE_TYPES_MECH and typ != "number":
            cls, reason = "redesign", f"measure type {typ!r} has no Omni aggregate_type"
        else:
            notes = []
            if typ == "number":
                notes.append("derived measure (type: number): validate confirms it resolves on the branch")
            if not typ:
                notes.append("measure without type: confirm intended aggregate")
            for fld, expr in measure_filters(m):
                if filter_expr_class(expr) != "mechanical":
                    notes.append(f"measure filter {fld}: {str(expr)!r} not mechanical: whole measure withheld")
            xrefs = {a for a, b in refs_in(sql, vname, dg_names) if a != vname}
            if xrefs:
                notes.append("cross-view field reference (" + ", ".join(sorted(xrefs)) + ")")
            if "value_format" in m and str(m["value_format"]).strip('"') not in VALUE_FORMATS:
                notes.append(f"custom value_format {m['value_format']!r} not in mapping table")
            if "value_format_name" in m and m["value_format_name"] not in VALUE_FORMAT_NAMES:
                notes.append(f"value_format_name {m['value_format_name']!r} not in mapping table")
            if m.get("links") or m.get("link"):
                notes.append("link: confirm Omni links syntax")
            if has_liquid(m.get("group_label", ""), m.get("view_label", ""), m.get("description", "")):
                notes.append("Liquid in group_label, view_label or description: resolve to a literal by hand")
            drills = m.get("drill_fields", []) or []
            if any("." in x and x.split(".")[0] != vname for x in drills):
                notes.append("drill_fields across views")
            if typ.endswith("_distinct") and "sql_distinct_key" not in m and typ != "count_distinct":
                notes.append("distinct measure without sql_distinct_key")
            if notes:
                cls, reason = "assisted", "; ".join(notes)
        field_classes[cls] += 1
        add_row("measure", uri_field(vname, m["name"]), vname, "", m["name"], con, cls, CX[cls], reason, src[0], src[1])
        edges.append({"from": uri_view(vname), "to": uri_field(vname, m["name"]), "kind": "contains"})
        for a, b in refs_in(sql, vname, dg_names):
            edges.append({"from": uri_field(vname, m["name"]), "to": uri_field(a, b), "kind": "references"})
        for fld, expr in measure_filters(m):
            if fld:
                a, b = (fld.split(".", 1) if "." in fld else (vname, fld))
                edges.append({"from": uri_field(vname, m["name"]), "to": uri_field(a, b), "kind": "references"})

    for f in v.get("filters", []) or []:
        field_count += 1
        field_classes["redesign"] += 1
        src = f.get("_src", (rel, ""))
        add_row("filter", uri_field(vname, f["name"]), vname, "", f["name"], "filter_field", "redesign", "High",
                "filter-only field: becomes a dashboard filter control or templated filter", src[0], src[1])
        edges.append({"from": uri_view(vname), "to": uri_field(vname, f["name"]), "kind": "contains"})
    for p in v.get("parameters", []) or []:
        field_count += 1
        field_classes["redesign"] += 1
        src = p.get("_src", (rel, ""))
        add_row("parameter", uri_field(vname, p["name"]), vname, "", p["name"], "parameter", "redesign", "High",
                "parameter: templated filter (Mustache) or a FIELD_SELECTION control", src[0], src[1])
        edges.append({"from": uri_view(vname), "to": uri_field(vname, p["name"]), "kind": "contains"})
    for s in v.get("sets", []) or []:
        src = s.get("_src", (rel, ""))
        add_row("set", f"looker:{PROJECT}:set:{vname}:{s['name']}", vname, "", s["name"], "set", "mechanical", "Low",
                f"{len(s.get('fields', []) or [])} members, expanded on use", src[0], src[1])

    if view_class == "redesign" or field_classes["redesign"] > 0 or (field_count > 30 and field_classes["assisted"] > 0):
        vcomplex = "High"
    elif field_classes["assisted"] > 0 or view_class == "assisted":
        vcomplex = "Medium"
    else:
        vcomplex = "Low"
    add_row("view", uri_view(vname), vname, "", "", construct, view_class, vcomplex, view_reason, rel, line)
    view_summary[vname] = {"class": view_class, "complexity": vcomplex, "fields": field_count, "field_classes": dict(field_classes),
                           "construct": construct, "file": rel, "line": line, "sql_table_name": v.get("sql_table_name"),
                           "derived": dt is not None, "pdt": bool(dt and any(k in dt for k in PDT_KEYS)),
                           "extends": v.get("extends__all") or v.get("extends") or []}

explore_summary = {}
for e, rel, line in explore_defs:
    ename = e["name"]
    if ename.startswith("+"):
        add_row("explore", uri_explore(ename[1:]), "", ename[1:], "", "explore:refinement", "mechanical", "Low", f"explore refinement in {rel}", rel, line)
        continue
    base = e.get("from") or e.get("view_name") or ename
    notes, cls = [], "mechanical"
    if base not in view_defs:
        cls, notes = "redesign", [f"base view {base!r} not found in project (unresolved reference)"]
    if "sql_always_where" in e:
        if has_liquid(e["sql_always_where"]):
            cls, notes = "redesign", notes + ["Liquid in sql_always_where"]
        else:
            notes.append("sql_always_where: confirm references resolve on the topic (always_where_sql)")
    if "sql_always_having" in e:
        notes.append("sql_always_having: no direct Omni equivalent, confirm")
    for k in ("always_filter", "conditionally_filter"):
        if k in e:
            notes.append(f"{k}: becomes default_filters; date expressions are never mechanical")
    if "access_filter" in e or "access_filters" in e:
        notes.append("access_filter: user attribute must exist in Omni (omni-target-setup)")
    if e.get("fields") and any(x.endswith("*") and x != "ALL_FIELDS*" for x in e["fields"]):
        notes.append("fields list references a set: hand expansion")
    if cls == "mechanical" and notes:
        cls = "assisted"
    reason = "; ".join(notes)
    if e.get("hidden") == "yes":
        reason = (reason + "; " if reason else "") + "hidden: yes"
    add_row("explore", uri_explore(ename), base, ename, "", "explore", cls, CX[cls], reason, rel, line)
    edges.append({"from": uri_explore(ename), "to": uri_view(base), "kind": "base_view"})
    reach = {base}
    join_rows = []
    for j in e.get("joins", []) or []:
        jname = j["name"]
        target = j.get("from") or jname
        rel_type = j.get("relationship", "many_to_one")
        jtype = j.get("type", "left_outer")
        jcls, jnotes = "mechanical", []
        if target not in view_defs:
            jcls, jnotes = "redesign", [f"joined view {target!r} not found in project (unresolved reference)"]
        elif "sql_on" not in j and "sql" in j:
            jcls, jnotes = "redesign", ["join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form"]
        elif "sql_on" not in j and "foreign_key" not in j:
            jcls, jnotes = "redesign", ["join without sql_on"]
        elif has_liquid(j.get("sql_on", "")):
            jcls, jnotes = "redesign", ["Liquid in sql_on"]
        elif rel_type == "many_to_many":
            jcls, jnotes = "redesign", ["relationship many_to_many"]
        elif jtype == "cross":
            jcls, jnotes = "redesign", ["type: cross"]
        else:
            if rel_type == "one_to_many":
                jnotes.append("relationship one_to_many: fan-out join, joined view needs primary_key")
            if jtype in ("inner", "full_outer"):
                jnotes.append(f"type: {jtype}")
            if "from" in j:
                jnotes.append(f"aliased join (from: {j['from']}): join_to_view_as")
            if "sql_where" in j:
                jnotes.append("sql_where on join: fold into on_sql or topic filter")
            if "foreign_key" in j:
                jnotes.append("foreign_key join: rewrite as on_sql")
            if jnotes:
                jcls = "assisted"
        add_row("join", uri_join(ename, jname), target, ename, jname, f"join:{rel_type}:{jtype}", jcls, CX[jcls], "; ".join(jnotes), rel, j.get("_src_line", ""))
        edges.append({"from": uri_explore(ename), "to": uri_view(target), "kind": "joins"})
        reach.add(target)
        join_rows.append({"join": jname, "view": target, "relationship": rel_type, "type": jtype, "class": jcls, "fields": j.get("fields"), "line": j.get("_src_line", "")})
    explore_summary[ename] = {"base_view": base, "class": cls, "reason": reason, "hidden": e.get("hidden") == "yes",
                              "label": e.get("label"), "file": rel, "line": line, "joins": join_rows, "views_reached": sorted(reach),
                              "always_filter": e.get("always_filter"), "conditionally_filter": e.get("conditionally_filter"),
                              "sql_always_where": e.get("sql_always_where"), "access_filter": e.get("access_filter") or e.get("access_filters"),
                              "fields": e.get("fields")}

ORDER = ["view", "explore", "join", "dimension", "dimension_group", "measure", "filter", "parameter", "set"]
rows.sort(key=lambda r: (ORDER.index(r["object_type"]), r["explore_name"], r["view_name"], r["field_name"]))
os.makedirs(OUT + "raw", exist_ok=True)
with open(OUT + "looker_model_catalog.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["object_type", "object_uri", "view_name", "explore_name", "field_name", "construct",
                                       "translation_class", "complexity", "reason", "lkml_file", "line", "lookml_commit"])
    w.writeheader()
    w.writerows(rows)
edges = sorted({json.dumps(e, sort_keys=True) for e in edges})
with open(OUT + "model_dependencies.jsonl", "w") as fh:
    for e in sorted(edges, key=lambda s: (json.loads(s)["kind"], json.loads(s)["from"], json.loads(s)["to"])):
        fh.write(e + "\n")
summary = {"lookml_commit": COMMIT, "files_parsed": len(lkml_files), "parse_errors": parse_errors,
           "counts": dict(Counter(r["object_type"] for r in rows)),
           "class_by_type": {t: dict(Counter(r["translation_class"] for r in rows if r["object_type"] == t)) for t in ORDER},
           "views": view_summary, "explores": explore_summary}
json.dump(summary, open(OUT + "raw/lookml_parsed_summary.json", "w"), indent=1, default=str)
missing_lines = len([r for r in rows if r["line"] == ""])
print(json.dumps({"files_parsed": len(lkml_files), "parse_errors": parse_errors, "counts": summary["counts"], "class_by_type": summary["class_by_type"], "rows_without_line": missing_lines}, indent=1))
