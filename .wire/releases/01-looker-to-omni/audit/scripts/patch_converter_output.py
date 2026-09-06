"""Deterministic post-converter patch for one omni_model batch (release 01-looker-to-omni).

Re-applied after every converter run; never hand-edits what the converter could emit.
Every change is recorded in <batch>/patch_log.json and summarised in the batch manifest.

Rules (each cites the ruling or defect it applies):
  P1 self-reference (converter 1.1.0 defect, lint L11): a dimension, dimension group or
     measure whose emitted `sql` references its own name (`${name}` or `${name[tf]}`), or
     references a dimension group of the same view without a timeframe, gets the bare
     column name recovered from the IR `source_sql` (`${TABLE}.<col>` -> `<col>`), which is
     how Omni's own generated views write a column in `sql:`.
  P2 dataset binding (R-16): a view whose LookML `sql_table_name` carried
     `{{ _user_attributes['dataset'] }}` is bound to `schema: <schema>` with the plain
     table name read from the LookML source file.
  P3 catalog (Omni generated views carry `catalog:`): every view gets `catalog: <catalog>`
     read from the LookML `project.dataset.table` form, else the connection default.
  P4 default_filters (translation guide: always_filter -> default_filters, user-removable):
     an `always_filter` needs_human item of the form "<N> months" on <view>.<field>_month
     becomes `default_filters: {<view>.<field>[month]: {time_for_duration: [<N> complete
     months ago, <N> months]}}` on the topic. Looker's "N months" means the N complete
     months before the current one.

Usage:
    python3 patch_converter_output.py <release_root> <batch_id> --catalog ra-development --schema analytics
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import OrderedDict

import yaml


class OD(yaml.SafeDumper):
    pass


def _repr_od(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


OD.add_representer(OrderedDict, _repr_od)


def _construct_od(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


class OL(yaml.SafeLoader):
    pass


OL.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_od)

TABLE_COL = re.compile(r"\$\{TABLE\}\.(\"?)([A-Za-z_][A-Za-z0-9_]*)\1")
REF = re.compile(r"\$\{([A-Za-z_]\w*)(?:\[(\w+)\])?\}")
LIQUID_TABLE = re.compile(r"sql_table_name\s*:\s*`?([^;`]+)`?\s*;;", re.S)


def dump(doc):
    return yaml.dump(doc, Dumper=OD, sort_keys=False, allow_unicode=True, width=1000)


def load(path):
    with open(path) as fh:
        return yaml.load(fh, Loader=OL) or OrderedDict()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("release_root")
    ap.add_argument("batch_id")
    ap.add_argument("--catalog", required=True, help="connection default project, used when the LookML table has none")
    ap.add_argument("--schema", required=True, help="schema for Liquid-bound views (R-16)")
    ap.add_argument("--lookml", default=None, help="LookML snapshot root (default: migration/source_snapshot/lookml/)")
    a = ap.parse_args()

    root = a.release_root.rstrip("/") + "/"
    bdir = f"{root}migration/omni_model/{a.batch_id}/"
    lookml = a.lookml or f"{root}migration/source_snapshot/lookml/"
    log = []

    def note(rule, file, key, before, after, ref):
        log.append({"rule": rule, "file": os.path.relpath(file, bdir), "key": key, "before": before, "after": after, "ref": ref})

    # ---- views: P1, P2, P3 ----
    for vf in sorted(glob.glob(bdir + "**/*.view", recursive=True)):
        vname = os.path.basename(vf)[:-5]
        ir_path = f"{bdir}ir/views/{vname}.json"
        if not os.path.exists(ir_path):
            print(f"warn: no IR for {vname}; skipped", file=sys.stderr)
            continue
        ir = json.load(open(ir_path))
        fields = {f["name"]: f for f in ir.get("fields", [])}
        groups = {n for n, f in fields.items() if f.get("kind") == "dimension_group"}
        doc = load(vf)
        changed = False

        # P1 self-reference and bare dimension-group references
        for section in ("dimensions", "measures"):
            for name, body in (doc.get(section) or {}).items():
                if not isinstance(body, dict) or not isinstance(body.get("sql"), str):
                    continue
                sql = body["sql"]
                src = (fields.get(name) or {}).get("source_sql") or ""
                src_cols = {m.group(2) for m in TABLE_COL.finditer(src)}

                def fix(m):
                    ref, tf = m.group(1), m.group(2)
                    if ref == name:
                        col = f"{ref}_{tf}" if tf else ref
                        if col in src_cols:
                            return col
                    if tf is None and ref in groups and ref in src_cols:
                        return ref
                    return m.group(0)

                new = REF.sub(fix, sql)
                if new != sql:
                    body["sql"] = new
                    changed = True
                    note("P1", vf, f"{section}.{name}.sql", sql, new, "converter 1.1.0 self-reference defect; lint L11")

        # P2 dataset binding for Liquid-bound views
        liquid = any(u.get("construct") == "sql_table_name_liquid" for u in ir.get("unsupported", []))
        if liquid:
            src_file = os.path.join(lookml, ir.get("source", {}).get("file", ""))
            table = None
            if os.path.exists(src_file):
                m = LIQUID_TABLE.search(open(src_file).read())
                if m:
                    table = m.group(1).strip().strip("`").split(".")[-1].strip()
            table = table or ir.get("table_name") or vname
            before = {k: doc.get(k) for k in ("schema", "table_name")}
            new_doc = OrderedDict()
            new_doc["schema"] = a.schema
            new_doc["table_name"] = table
            for k, v in doc.items():
                if k not in ("schema", "table_name"):
                    new_doc[k] = v
            doc = new_doc
            changed = True
            note("P2", vf, "schema,table_name", before, {"schema": a.schema, "table_name": table}, "R-16")

        # P3 catalog
        if "catalog" not in doc:
            catalog = a.catalog
            src_file = os.path.join(lookml, ir.get("source", {}).get("file", ""))
            if os.path.exists(src_file) and not liquid:
                m = LIQUID_TABLE.search(open(src_file).read())
                if m:
                    parts = [p for p in m.group(1).strip().strip("`").split(".") if p]
                    if len(parts) == 3:
                        catalog = parts[0]
            new_doc = OrderedDict([("catalog", catalog)])
            for k, v in doc.items():
                new_doc[k] = v
            doc = new_doc
            changed = True
            note("P3", vf, "catalog", None, catalog, "Omni generated views carry catalog; connection project")

        if changed:
            open(vf, "w").write(dump(doc))

    # ---- topics: P4 default_filters from withheld always_filter items ----
    nh_path = bdir + "needs_human.json"
    items = json.load(open(nh_path)) if os.path.exists(nh_path) else []
    items = items if isinstance(items, list) else items.get("items", [])
    month_re = re.compile(r"'(\d+) months' on ([A-Za-z_]\w*)\.([A-Za-z_]\w*)_month")
    for it in items:
        if it.get("construct") != "always_filter":
            continue
        m = month_re.search(it.get("reason", ""))
        tf = f"{bdir}{it.get('name')}.topic"
        if not m or not os.path.exists(tf):
            print(f"warn: always_filter item on {it.get('name')} not in the N-months form; left for hand review", file=sys.stderr)
            continue
        n, view, field = int(m.group(1)), m.group(2), m.group(3)
        doc = load(tf)
        key = f"{view}.{field}[month]"
        filt = OrderedDict([("time_for_duration", [f"{n} complete months ago", f"{n} months"])])
        before = doc.get("default_filters")
        df = doc.get("default_filters") or OrderedDict()
        df[key] = filt
        doc["default_filters"] = df
        open(tf, "w").write(dump(doc))
        note("P4", tf, f"default_filters.{key}", before, dict(filt), "translation guide: always_filter -> default_filters (user-removable); Looker 'N months' = N complete months before this one")
        it["status"] = "resolved"
        it["resolution"] = f"default_filters {key}: time_for_duration [{n} complete months ago, {n} months]"
        it["ruling_ref"] = "R-19" if a.batch_id == "b02" else "translation guide"
    if items and os.path.exists(nh_path):
        json.dump(items, open(nh_path, "w"), indent=2)

    json.dump({"batch_id": a.batch_id, "patch_version": "1.0.0", "rules": ["P1", "P2", "P3", "P4"], "changes": log},
              open(bdir + "patch_log.json", "w"), indent=2)
    by_rule = {}
    for c in log:
        by_rule[c["rule"]] = by_rule.get(c["rule"], 0) + 1
    print(json.dumps({"batch": a.batch_id, "changes": len(log), "by_rule": by_rule}))


if __name__ == "__main__":
    main()
