"""Report the LookML project's production git revision as Looker sees it, for baseline.yaml. Read-only."""
import json
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402

sdk = looker_sdk.init40()
out = {}
try:
    p = sdk.project("analytics")
    out["git_remote_url"] = p.git_remote_url
    out["git_production_branch_name"] = p.git_production_branch_name
except Exception as e:  # noqa: BLE001
    out["project_error"] = str(e)[:200]
try:
    sdk.update_session(looker_sdk.models40.WriteApiSession(workspace_id="production"))
    b = sdk.git_branch("analytics")
    out["production_branch"] = {"name": b.name, "ref": b.ref, "remote_ref": b.remote_ref, "ahead_count": b.ahead_count, "behind_count": b.behind_count}
except Exception as e:  # noqa: BLE001
    out["branch_error"] = str(e)[:200]
try:
    conn = sdk.connection("ra_dw_prod", fields="name,dialect_name,database,host,schema")
    out["connection"] = {"name": conn.name, "dialect": conn.dialect_name, "database": conn.database, "host": conn.host, "schema": conn.schema}
except Exception as e:  # noqa: BLE001
    out["connection_error"] = str(e)[:200]
print(json.dumps(out, indent=1, default=str))
