"""Inspect the exported Omni shared model in the target repo snapshot: schemas, topics, view naming, collisions with in-scope LookML views."""
import collections
import json
import os

p = ".wire/releases/01-looker-to-omni/migration/source_snapshot/omni_model/omni/ra_data_warehouse 2/"
print("model.yaml:")
print(open(p + "model.yaml").read()[:1500])
rel = open(p + "relationships.yaml").read()
print("relationships.yaml lines:", len(rel.splitlines()))
print(rel[:500])
for d in sorted(os.listdir(p)):
    q = p + d
    if os.path.isdir(q):
        files = sorted(os.listdir(q))
        exts = collections.Counter(os.path.splitext(f)[1] for f in files)
        print(d, len(files), "files", dict(exts), "sample", files[:6])
topics, views = [], []
for root, dirs, files in os.walk(p):
    for f in files:
        if ".topic" in f:
            topics.append(os.path.join(root, f))
        if ".view" in f:
            views.append(f)
print("topics:", len(topics), [os.path.basename(t) for t in topics[:15]])
print("view files:", len(views), views[:8])
sa = json.load(open(".wire/releases/01-looker-to-omni/audit/raw/scope_analysis.json"))
names = {f.split(".")[0] for f in views}
coll = [v for v in sa["view_set"] if v in names]
print("in-scope lookml view names present as omni view files:", len(coll), coll[:25])
an = p + "ra-development.analytics/"
if os.path.isdir(an):
    fs = sorted(os.listdir(an))
    target = [f for f in fs if f.startswith("companies_dim")] or fs[:1]
    print("=====", target[0])
    print(open(an + target[0]).read()[:900])
