# Omni Target Setup: 01-looker-to-omni

**Release**: 01-looker-to-omni (bi_migration, looker_to_omni)  
**Generated**: 2026-09-06 22:45 (local), by `/wire:omni-target-setup-generate`, orchestrating session 7bb027f9  
**Authorised by**: R-12 (plan approved; continue with target setup) and R-6 (target model)  
**Omni instance**: https://rittmananalytics.omniapp.co  
**CLI**: Omni CLI 1.2.1, profile `rittmananalytics` (OAuth, user-scoped key; identity ORG_ADMIN, CONNECTION_ADMIN on the target model)

## Data safety statement

Writes made to the live Omni instance by this command, in order, each with its reversing action:

| # | Write | Reversing action |
|---|---|---|
| 1 | Created model branch `wire-01-looker-to-omni` (id `13dc8819-655b-4f36-9ccc-04f748c1ba80`) on shared model `67716e96-520d-402a-88ad-89f97f9bc2a0` | `omni models delete-branch 13dc8819-655b-4f36-9ccc-04f748c1ba80` |
| 2 | Soft schema refresh (`--hard-refresh false`) of three schemas on the shared model: `ra-development.analytics`, `ra-development.analytics_seed`, `ra-development.analytics_docai_europe_west2` (job `5b7f1237-faf3-49bc-9a02-e84285056254`, COMPLETED 2026-09-06 21:45 UTC) | none needed: a soft refresh merges current table metadata; it does not delete views or edit model YAML |

Nothing else was written. No production model YAML was edited, no branch merged, no document touched, no connection changed, no user added to any group, no group or user attribute created (see Groups and user attributes).

## Connection verification

| Side | Connection | Warehouse | Project / catalog | Default dataset | Notes |
|---|---|---|---|---|---|
| Looker | `ra_dw_prod` (model `analytics`) | BigQuery (`bigquery_standard_sql`) | `ra-development` | `analytics` | from `looker_project_revision.py` (Looker API `connection`) |
| Omni | `ra_data_warehouse` (`961a7db6-9219-4426-875b-a3e75fc243b1`) | BigQuery (`bigquery`) | `ra-development` | `analytics` | region europe-west2, service account `omni-942@ra-development.iam.gserviceaccount.com`, `alwaysScopeViewNames: true` |

Same warehouse, same project, same default dataset. `connection_verified: true`.

## Model and git state

| Item | Value |
|---|---|
| Target model | `67716e96-520d-402a-88ad-89f97f9bc2a0` ('ra_data_warehouse 2', SHARED), ruling R-6 |
| Git connection | GitHub app, `https://github.com/rittmananalytics/ra-data-warehouse-omni-target.git`, base branch `main`, `requirePullRequest: never`, `branchPerPullRequest: false` |
| Merge path at omni-model-review | git-connected: `omni models commit` on the branch, then a pull request in the target repo |
| Existing views on the model | 998, all auto-generated schema views named `<catalog>_<schema>__<table>` (for example `ra_development_analytics__companies_dim`); 0 topics |
| Name collisions with in-scope LookML views (R-9 keeps LookML names) | 0 exact collisions. 84 schema views end with an in-scope table name (`..._analytics__companies_dim` and the like); they keep their prefixed names, so the converter's `companies_dim` view is a second view over the same table, as the translation guide expects |
| Omni audit | not run (PD-10); the collision check above stands in for the brownfield listing |

## Branch

`omni models create-branch 67716e96-520d-402a-88ad-89f97f9bc2a0 --name wire-01-looker-to-omni`

| Field | Value |
|---|---|
| Branch id | `13dc8819-655b-4f36-9ccc-04f748c1ba80` |
| Name | `wire-01-looker-to-omni` |
| Created | 2026-09-06 21:45:02 UTC |
| hasGit | true |
| Pre-existing branches on the model | none |

All model writes in this release go to this branch. Nothing merges without a ruling recorded at `omni-model-review`.

## Schema refresh

`omni models refresh 67716e96-520d-402a-88ad-89f97f9bc2a0 --hard-refresh false --schemas "ra-development.analytics,ra-development.analytics_seed,ra-development.analytics_docai_europe_west2"`

| Field | Value |
|---|---|
| Job | `5b7f1237-faf3-49bc-9a02-e84285056254`, type `refresh_schema`, status COMPLETED |
| Started | 2026-09-06 21:45:23 UTC |
| Scope | the three datasets the 73 in-scope views read (`sql_table_name` values in the audit); a soft refresh was chosen over the default hard refresh so the 998 existing views were merged, not discarded and rebuilt |
| Schemas available on the model after refresh | 356 (BigQuery datasets in `ra-development` plus the `omni_dbt*` schemas); the three in-scope datasets are present |

## Model validation on the branch (pre-existing state)

`omni models validate 67716e96-520d-402a-88ad-89f97f9bc2a0 --branch-id 13dc8819-655b-4f36-9ccc-04f748c1ba80` returns 10 blocking issues, all `column_not_found`: dimension `start_end_ts` is declared in 10 auto-generated views (`delivery_tasks_fact`, `int_delivery_tasks` and three `stg_jira_*_projects_tasks` views, each in both the `ra_development_*` and `omni_dbt*` schema families) but the column no longer exists in the warehouse. The base model (`main`) returns the same 10 issues, so they pre-date this release and are not caused by the refresh. Omni offers an auto-fix (remove the dimension) for each. Full list: `migration/omni_validate_branch_baseline.json`. Disposition is a parked decision (PD-13).

## Groups and user attributes (permission map, R-10)

| Kind | Object | Action taken | State |
|---|---|---|---|
| Group | All Users (Looker group 1, view on Shared) | none needed: maps to the Omni organisation default | existing (organisation) |
| Access grant | `can_view_company_bio` | none here: declared in model YAML by `omni_model` (`required_access_grants` on `companies_dim.company_description`) | pending model batch b05 |
| User attribute | `groups` (for the access grant) | **not created**: Omni CLI 1.2.1 has no user-attribute create command (`omni user-attributes` lists only). Existing attributes on the instance are the 12 system ones, including `omni_user_groups` | parked decision PD-14: create `groups` by hand in Omni Admin, or bind the grant to the system attribute `omni_user_groups` |
| User attribute | `dataset` | not carried (R-10); binding of the 11 Liquid views stays PD-4 | n/a |
| Groups via API | `omni scim groups-list` | refused: "User-scoped API keys are not allowed to access the SCIM API" (403). Group reads and writes need an organisation-scoped API key | access gap, recorded |

No users were added to any group.

## Dashboard theme

Derived from colour usage across the three in-scope dashboards and written to `migration/omni_dashboard_theme.json`: key colour `#4a80bc` (the most used non-status series colour), white background, text `#3a4245`, RAG green/red/amber kept as series colours for status tiles. The dashboards set no font, background or title colour, so those are defaults. Import per dashboard through the editor's Import button; the property names follow `omni_patterns.md` (Dashboard themes) and must be confirmed against the instance before the first content batch relies on them.

## Reference key

| Code | Meaning | Defined in |
|---|---|---|
| R-6, R-9, R-10, R-12 | rulings this setup applied | `.wire/releases/01-looker-to-omni/decisions.md` |
| PD-4, PD-10, PD-13, PD-14 | parked decisions touched or raised here | `.wire/releases/01-looker-to-omni/status.md` |
| `13dc8819-655b-4f36-9ccc-04f748c1ba80` | the model branch every model write targets | this document, Branch |
| `5b7f1237-faf3-49bc-9a02-e84285056254` | the schema refresh job | this document, Schema refresh |
| soft refresh | Omni `--hard-refresh false`: merge current metadata, keep existing views | `omni models refresh --help` |

## Validation

Run 2026-09-06 22:48 by `/wire:omni-target-setup-validate` against the live instance. Result: **FAIL** (2 of 7 checks).

| Check | Result | Evidence |
|---|---|---|
| 1 Branch exists | PASS | `omni models list --model-kind BRANCH --base-model-id 67716e96...` lists `13dc8819-655b-4f36-9ccc-04f748c1ba80` `wire-01-looker-to-omni` |
| 2 Model validates on the branch | FAIL | 10 blocking `column_not_found` issues (`start_end_ts` in 10 auto-generated views); identical on the base model `main`, so pre-existing |
| 3 Schema is fresh | PASS | refresh job COMPLETED 2026-09-06 21:45 UTC, after the branch was created; `ra-development.analytics`, `analytics_seed` and `analytics_docai_europe_west2` all present in the 356 schemas |
| 4 Groups exist | PASS | the permission map needs no Omni group to exist: All Users maps to the organisation default. SCIM group listing itself is refused for a user-scoped key (recorded as an access gap) |
| 5 User attributes exist | FAIL | `groups` is not on the instance (12 system attributes only); the CLI cannot create it |
| 6 No users were added | PASS | no membership write was made by this command |
| 7 Connection unchanged | PASS | `ra_data_warehouse` still BigQuery, `ra-development`, default dataset `analytics`, last updated 2026-08-06 |

### Gaps to address

- Check 2: rule on the 10 pre-existing validation errors (PD-13): apply Omni's auto-fix on the branch only (remove the 10 stale `start_end_ts` dimensions, carried to `main` when the branch merges), have the model owners fix `main` first, or accept them as known and proceed. Re-run validate after.
- Check 5: rule on the `groups` user attribute (PD-14): create it by hand in Omni Admin (String, default empty), or bind the `can_view_company_bio` grant to the system attribute `omni_user_groups`. Re-run validate after.

## Validation (second run, after R-13 and R-14)

Run 2026-09-06 22:52 by `/wire:omni-target-setup-validate`. Result: **PASS** (7 of 7).

Write 3 added to the data safety list by R-13: the `start_end_ts` dimension was removed from 10 auto-generated view files on branch `13dc8819` only (`audit/scripts/fix_stale_dimensions.py`; before and after copies under `migration/omni_target_setup_fixes/`; commit message "wire 01-looker-to-omni R-13: remove stale start_end_ts dimension"). Reversal: write the `before/` copies back with `omni models yaml-create` on the branch, or delete the branch. `main` is untouched.

| Check | Result | Evidence |
|---|---|---|
| 1 Branch exists | PASS | unchanged |
| 2 Model validates on the branch | PASS | `omni models validate ... --branch-id 13dc8819...` returns 0 issues after the 10 removals (`migration/omni_target_setup_fixes/fix_log.json`) |
| 3 Schema is fresh | PASS | unchanged |
| 4 Groups exist | PASS | unchanged |
| 5 User attributes exist | PASS | R-14 binds the grant to the system attribute `omni_user_groups`, which exists (String, system); no `groups` attribute is needed |
| 6 No users were added | PASS | no membership write |
| 7 Connection unchanged | PASS | unchanged |

### Gaps to address

- none

## Review

**Reviewed by**: Mark Rittman (release director; "Approved. Continue to the next batch.", 2026-09-06 22:50, recorded by the orchestrating session 7bb027f9)
**Review date**: 2026-09-06
**Decision**: approved

### Reviewer notes

- Model `67716e96-520d-402a-88ad-89f97f9bc2a0`, branch `13dc8819-655b-4f36-9ccc-04f748c1ba80` (R-6, R-15).
- Permission objects per R-10 and R-14: no group created (All Users is the organisation default), no user attribute created (grant bound to `omni_user_groups`).
- No name collisions: existing schema views carry the `ra_development_analytics__` prefix; LookML names are kept (R-9).
- The director's "Approved" was read as approving the recommended resolutions of PD-13 and PD-14 (R-13, R-14). Both are branch-only and reversible; the director can overturn either.
