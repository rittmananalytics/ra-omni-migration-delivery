"""Extract Looker groups, user attributes, roles and folder access for the permission map. Read-only.

Usage (from the repo root):
    python3 looker_permissions_extract.py <audit_out_dir>
Writes <audit_out_dir>/raw/looker_permissions.json
"""
import json
import sys
import warnings

warnings.filterwarnings("ignore")
import looker_sdk  # noqa: E402

OUT = sys.argv[1].rstrip("/") + "/"
sdk = looker_sdk.init40()
out = {}

groups = sdk.all_groups(fields="id,name,user_count,externally_managed,include_by_default")
out["groups"] = [{"id": g.id, "name": g.name, "user_count": g.user_count, "externally_managed": g.externally_managed, "include_by_default": g.include_by_default} for g in groups]

uas = sdk.all_user_attributes(fields="id,name,label,type,default_value,is_system,user_can_view,user_can_edit,hidden_value_domain_whitelist")
out["user_attributes"] = [{"id": u.id, "name": u.name, "label": u.label, "type": u.type, "default_value": u.default_value, "is_system": u.is_system} for u in uas]

# Group values for the user attributes an access grant or access filter would read
out["user_attribute_group_values"] = {}
for u in uas:
    if u.is_system:
        continue
    try:
        vals = sdk.all_user_attribute_group_values(u.id)
        if vals:
            out["user_attribute_group_values"][u.name] = [{"group_id": v.group_id, "value": v.value} for v in vals]
    except Exception as e:  # noqa: BLE001
        out["user_attribute_group_values"][u.name] = f"error: {str(e)[:120]}"

roles = sdk.all_roles(fields="id,name,permission_set(name),model_set(name,models)")
out["roles"] = [{"id": r.id, "name": r.name, "permission_set": r.permission_set.name if r.permission_set else None,
                 "model_set": r.model_set.name if r.model_set else None, "models": list(r.model_set.models or []) if r.model_set else []} for r in roles]

# Content access on the folders that hold the in-scope dashboards (Shared root)
out["folder_access"] = {}
for f in sdk.all_folders(fields="id,name,is_shared_root,parent_id,content_metadata_id"):
    if f.is_shared_root or f.name == "Shared":
        try:
            accesses = sdk.all_content_metadata_accesses(content_metadata_id=str(f.content_metadata_id))
            out["folder_access"][f.name] = [{"group_id": a.group_id, "user_id": a.user_id, "permission_type": a.permission_type} for a in accesses]
        except Exception as e:  # noqa: BLE001
            out["folder_access"][f.name] = f"error: {str(e)[:120]}"

users = sdk.all_users(fields="id,display_name,email,is_disabled,group_ids,role_ids")
out["users"] = [{"id": u.id, "name": u.display_name, "email": u.email, "disabled": u.is_disabled, "group_ids": list(u.group_ids or []), "role_ids": list(u.role_ids or [])} for u in users]

json.dump(out, open(OUT + "raw/looker_permissions.json", "w"), indent=1, default=str)
print(json.dumps({"groups": [(g["name"], g["user_count"]) for g in out["groups"]], "user_attributes": [(u["name"], u["type"], u["is_system"]) for u in out["user_attributes"]],
                  "roles": [(r["name"], r["permission_set"], r["model_set"]) for r in out["roles"]], "users": len(out["users"]),
                  "active_users": len([u for u in out["users"] if not u["disabled"]]), "folder_access": out["folder_access"],
                  "ua_group_values": out["user_attribute_group_values"]}, indent=1, default=str))
