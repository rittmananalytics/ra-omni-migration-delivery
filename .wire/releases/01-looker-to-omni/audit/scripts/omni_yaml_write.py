"""Write a batch's emitted Omni YAML files to the model branch and verify each one (release 01-looker-to-omni).

Order: views, then relationships.yaml (if present and non-empty), then topics, so every topic's
base_view and joins already exist. Each file is written with `omni models yaml-create` (branch-aware,
mode combined), read back with `omni models yaml-get`, and compared as parsed YAML. A write whose
read-back differs is reported and stops the run. Never merges or commits the branch.

Usage:
    python3 omni_yaml_write.py <model_id> <branch_id> <batch_dir> <commit_prefix> [--map SRC_PREFIX=DST_PREFIX]

--map rewrites the on-branch file name prefix (e.g. `analytics/=` puts the analytics views at the model root).
Prints one JSON line per file and a summary. Exit code 1 on any mismatch.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import yaml


def omni(*args, body=None):
    cmd = ["omni", *args, "-o", "json"]
    if body is not None:
        cmd += ["--body", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"omni {' '.join(args[:3])} failed: {r.stderr[:400] or r.stdout[:400]}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def main():
    model, branch, bdir, prefix = sys.argv[1], sys.argv[2], sys.argv[3].rstrip("/") + "/", sys.argv[4]
    maps = []
    for a in sys.argv[5:]:
        if a.startswith("--map"):
            continue
        if "=" in a:
            src, dst = a.split("=", 1)
            maps.append((src, dst))

    def branch_name(rel):
        for src, dst in maps:
            if rel.startswith(src):
                return dst + rel[len(src):]
        return rel

    views = sorted(glob.glob(bdir + "**/*.view", recursive=True))
    rels = [bdir + "relationships.yaml"] if os.path.exists(bdir + "relationships.yaml") and (yaml.safe_load(open(bdir + "relationships.yaml")) or []) else []
    topics = sorted(glob.glob(bdir + "*.topic"))
    written = []
    for f in views + rels + topics:
        rel = os.path.relpath(f, bdir)
        name = branch_name(rel)
        text = open(f).read()
        omni("models", "yaml-create", model, body={"fileName": name, "yaml": text, "branchId": branch, "mode": "combined",
                                                   "commitMessage": f"{prefix}: {name}"})
        back = omni("models", "yaml-get", model, "--branch-id", branch, "--file-name", name, "--mode", "combined").get("files", {}).get(name)
        ok = back is not None and yaml.safe_load(back) == yaml.safe_load(text)
        entry = {"path": name, "local": rel, "emitted_sha": hashlib.sha256(text.encode()).hexdigest(),
                 "written_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "read_back_matches": ok}
        print(json.dumps(entry))
        written.append(entry)
        if not ok:
            print(json.dumps({"error": "read-back differs", "path": name}))
            sys.exit(1)
    print(json.dumps({"summary": {"files": len(written), "views": len(views), "relationships": len(rels), "topics": len(topics)}}))
    json.dump(written, open(bdir + "write_log.json", "w"), indent=2)


if __name__ == "__main__":
    main()
