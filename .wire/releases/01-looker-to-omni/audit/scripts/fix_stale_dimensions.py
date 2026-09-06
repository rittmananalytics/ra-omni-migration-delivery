"""R-13: remove the stale `start_end_ts` dimension from 10 auto-generated views on the migration branch only.

Each file is fetched from the branch, saved before and after under migration/omni_target_setup_fixes/, edited, and
written back with the Omni CLI (yaml-create, branch-aware). Then the branch is re-validated.

Usage (from the repo root):
    python3 fix_stale_dimensions.py <model_id> <branch_id> <release_root>
"""
import json
import os
import re
import subprocess
import sys

MODEL, BRANCH, ROOT = sys.argv[1], sys.argv[2], sys.argv[3].rstrip("/") + "/"
OUT = ROOT + "migration/omni_target_setup_fixes/"
os.makedirs(OUT + "before", exist_ok=True)
os.makedirs(OUT + "after", exist_ok=True)
FILES = [
    "ra-development.analytics/delivery_tasks_fact.view",
    "ra-development.analytics_integration/int_delivery_tasks.view",
    "ra-development.analytics_staging/stg_jira_booksy_projects_tasks.view",
    "ra-development.analytics_staging/stg_jira_hkm_projects_tasks.view",
    "ra-development.analytics_staging/stg_jira_projects_tasks.view",
    "omni_dbt/delivery_tasks_fact.view",
    "omni_dbt_integration/int_delivery_tasks.view",
    "omni_dbt_staging/stg_jira_booksy_projects_tasks.view",
    "omni_dbt_staging/stg_jira_hkm_projects_tasks.view",
    "omni_dbt_staging/stg_jira_projects_tasks.view",
]
DIM_LINE = re.compile(r"^  start_end_ts:\s*\{\}\s*\n", re.M)
DIM_BLOCK = re.compile(r"^  start_end_ts:\s*\n(?:    .*\n)+", re.M)


def omni(*args, body=None):
    cmd = ["omni", *args]
    if body is not None:
        cmd += ["--body", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:3])} failed: {r.stderr[:400] or r.stdout[:400]}")
    return json.loads(r.stdout) if r.stdout.strip().startswith(("{", "[")) else r.stdout


log = []
for path in FILES:
    res = omni("models", "yaml-get", MODEL, "--branch-id", BRANCH, "--file-name", path, "--mode", "combined")
    text = res["files"].get(path)
    if text is None:
        log.append({"file": path, "result": "not found on branch"})
        continue
    safe = path.replace("/", "__")
    open(OUT + "before/" + safe + ".yaml", "w").write(text)
    new, n = DIM_LINE.subn("", text)
    if n == 0:
        new, n = DIM_BLOCK.subn("", text)
    if n == 0:
        log.append({"file": path, "result": "dimension start_end_ts not found in file; no change"})
        continue
    open(OUT + "after/" + safe + ".yaml", "w").write(new)
    w = omni("models", "yaml-create", MODEL, body={"fileName": path, "yaml": new, "branchId": BRANCH, "mode": "combined",
                                                    "commitMessage": "wire 01-looker-to-omni R-13: remove stale start_end_ts dimension"})
    back = omni("models", "yaml-get", MODEL, "--branch-id", BRANCH, "--file-name", path, "--mode", "combined")["files"].get(path)
    log.append({"file": path, "result": "removed start_end_ts" if back == new else "WRITE MISMATCH on read-back", "removed_lines": n,
                "write_response_keys": sorted(w.keys()) if isinstance(w, dict) else str(w)[:80]})

issues = omni("models", "validate", MODEL, "--branch-id", BRANCH, "--limit", "1000")
issues = issues if isinstance(issues, list) else issues.get("issues", [])
blocking = [i for i in issues if not i.get("is_warning")]
summary = {"files": log, "validate_after": {"issues": len(issues), "blocking": len(blocking), "warnings": len(issues) - len(blocking)},
           "remaining": [i.get("message", "")[:120] for i in issues][:20]}
json.dump(summary, open(OUT + "fix_log.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
