---
project_id: "20260906"
project_name: "01-looker-to-omni"
project_type: "bi_migration"
client_name: "Rittman Analytics"
engagement_name: "ra_looker_to_omni_migration"
created_date: "2026-09-06"
last_updated: "2026-09-06"
current_phase: "model"

# Profile: which tool pair this release migrates. Read by precondition_gate.md Step 0
# and by runnable_set.md. looker_to_omni is the only pair in 4.0.0.
bi_pair: looker_to_omni

bi_migration:
  source_tool: looker
  target_tool: omni
  lookml_repo_path: ".wire/releases/01-looker-to-omni/migration/source_snapshot/lookml/"   # the refreshed snapshot; no manual checkout
  looker_base_url: "https://rittman.eu.looker.com"
  omni_base_url: "https://rittmananalytics.omniapp.co"
  omni_model_id: "67716e96-520d-402a-88ad-89f97f9bc2a0"   # R-6: shared model 'ra_data_warehouse 2', git-connected to ra-data-warehouse-omni-target
  omni_profile: "rittmananalytics"
  omni_branch: "13dc8819-655b-4f36-9ccc-04f748c1ba80"   # branch wire-01-looker-to-omni, created 2026-09-06 22:45 by omni-target-setup-generate; all model writes go here
  parallel_run_days: 14
  cutover_date: null
  parity_scope: all                        # R-3: every tile on all three in-scope dashboards
  parity_as_of: "2026-09-05T23:59:59Z"    # set by the plan (baseline b001): end of the last complete day before the plan, UTC; a later as-of is a re-baseline
  stale_after_days: 180
  warehouse: bigquery                      # Looker connection ra_dw_prod: bigquery_standard_sql, project ra-development, dataset analytics
  client_repos:
    - role: bi_target_model
      url: "https://github.com/rittmananalytics/ra-data-warehouse-omni-target"
      base_branch: main

# Upstream and downstream repos registered with /wire:migration-source-register and pulled with
# /wire:migration-source-refresh. Every audit, model and drift command reads the local snapshot, never the live repo.
migration_sources:
  lookml:
    git_repo: "https://github.com/rittmananalytics/ra_data_warehouse_lookml"
    branch: master
    subfolder: ""
    local_snapshot_path: ".wire/releases/01-looker-to-omni/migration/source_snapshot/lookml/"
    last_refreshed: "2026-09-06"
    last_commit: "82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e"
  omni_model:
    git_repo: "https://github.com/rittmananalytics/ra-data-warehouse-omni-target"
    branch: main
    subfolder: ""
    local_snapshot_path: ".wire/releases/01-looker-to-omni/migration/source_snapshot/omni_model/"
    last_refreshed: "2026-09-06"
    last_commit: "733f71f019dc0239d6d2a2482bea7e0f8dab1795"

artifacts:
  business_rules:
    generate: not_started
    validate: not_started
    review: not_started
    file: null
    domains_covered: []
    generated_date: null

  looker_audit:
    generate: complete
    validate: pass
    review: not_started
    file: audit/looker_audit.md
    generated_date: "2026-09-06"
    validated_date: "2026-09-06"
    lookml_commit: "82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e"
    view_count: 190
    explore_count: 39
    field_count: 3533
    dashboard_count: 196
    look_count: 148
    tile_count: 1636
    mechanical_count: 3548
    assisted_count: 265
    redesign_count: 132
    drop_count: 162
    usage_source: system_activity
    generated_files:
      - audit/looker_audit.md
      - audit/looker_model_catalog.csv
      - audit/looker_content_catalog.csv
      - audit/dependencies.jsonl
      - audit/model_dependencies.jsonl
      - audit/scripts/lookml_audit_parse.py
      - audit/scripts/looker_content_extract.py
      - audit/scripts/augment_content_catalog.py
      - audit/scripts/scope_analysis.py
      - audit/scripts/build_audit_report.py
      - audit/scripts/validate_audit.py
    revision_history:
      - date: "2026-09-06"
        change: "first audit of the whole estate at LookML commit 82b3ab5; validate PASS (8 checks)"

  omni_audit:
    generate: not_started
    validate: not_started
    review: not_started
    file: null
    generated_date: null
    connection_count: null
    topic_count: null
    view_count: null
    folder_count: null
    workbook_count: null
    tile_count: null
    raw_sql_tile_count: null
    resolved_view_count: null
    unresolved_view_count: null
    source_resolution_coverage_pct: null
    generated_files: []
    revision_history: []

  bi_migration_plan:
    generate: complete
    validate: pass
    review: approved
    reviewed_by: "Mark Rittman"
    reviewed_date: "2026-09-06"
    gate_overridden: true      # looker_audit.review required approved, was not_started; see precondition_overrides
    file: migration/bi_migration_plan.md
    data_file: migration/bi_migration_batches.csv
    generated_date: "2026-09-06"
    validated_date: "2026-09-06"
    batch_count: 10            # b01 permissions, b02 to b07 model, c01 to c03 content
    objects_in_scope: 159
    objects_dropped: 497
    register_rows: 156
    rulings_parked: 7          # PD-4 to PD-8, PD-10, PD-11 open at approval (R-12); each tied to the step it blocks
    baseline_id: b001
    generated_files:
      - migration/bi_migration_plan.md
      - migration/bi_migration_batches.csv
      - migration/migration_register.csv
      - migration/baseline.yaml
      - migration/parity/evidence.csv
      - audit/scripts/build_plan.py
      - audit/scripts/validate_plan.py
    revision_history:
      - date: "2026-09-06"
        change: "first plan from the audit at LookML commit 82b3ab5; rulings R-1 to R-4 applied, 9 decisions parked"

  migration_drift:
    generate: not_started
    validate: not_started
    file: null
    generated_date: null
    last_run_date: null
    drift_head: null
    views_drifted: null
    views_reclassified: null
    topics_impacted: null
    dashboards_impacted: null
    content_drifted: null
    generated_files: []
    revision_history: []

  omni_target_setup:
    generate: complete
    validate: pass              # second run 22:52 after R-13 (10 stale dimensions removed on the branch) and R-14 (grant bound to omni_user_groups)
    review: approved
    reviewed_by: "Mark Rittman"
    reviewed_date: "2026-09-06"
    file: migration/omni_target_setup.md
    generated_date: "2026-09-06"
    validated_date: "2026-09-06"
    connection_verified: true
    schema_refreshed: true      # soft refresh of 3 in-scope datasets, job 5b7f1237 COMPLETED 2026-09-06 21:45 UTC
    branch_created: true        # 13dc8819-655b-4f36-9ccc-04f748c1ba80 wire-01-looker-to-omni
    groups_created: 0           # All Users maps to the organisation default; SCIM refused the user-scoped key
    user_attributes_created: 0  # CLI cannot create user attributes; PD-14
    model_git_connected: true
    generated_files:
      - migration/omni_target_setup.md
      - migration/omni_dashboard_theme.json
      - migration/omni_validate_branch_baseline.json
    revision_history:
      - date: "2026-09-06"
        change: "branch created, 3 schemas soft-refreshed, connection verified; 10 pre-existing validation errors found on the model (PD-13)"

  omni_model:
    generate: in_progress
    lint: fail                  # b02: 11 self-reference findings (L11, converter defect), catalogue rules L0 to L10 all pass
    validate: not_started
    review: not_started
    file: migration/omni_model/omni_model.md
    generated_date: "2026-09-06"
    lint_date: "2026-09-06"
    lint_batch: b02
    batches_total: 6            # b02 to b07 (b01 permissions was handled by target setup)
    batches_complete: []        # b02 is emitted locally (migration/omni_model/b02/) but not yet written to the branch: held for the director's review of its needs_human resolutions (R-15)
    batches_emitted: [b02]
    batches_validated: []
    views_emitted: 4
    topics_emitted: 4
    needs_human_open: 8
    smoke_queries_run: null
    last_reverse_port: null
    reverse_port_conflicts: null
    generated_files: []
    revision_history: []

  omni_content:
    generate: not_started
    validate: not_started
    review: not_started
    file: null
    generated_date: null
    plan_validated: null
    batches_total: null
    batches_complete: null
    batches_validated: []
    dashboards_planned: null
    dashboards_created: null
    tiles_skipped: null
    hand_finish_open: null
    generated_files: []
    revision_history: []

  bi_equivalency:
    validate: not_started
    last_run_date: null
    run_count: 0
    tiles_checked: null
    passing: null
    pass_qualified: null
    failing: null
    unresolved: null
    blocked: null
    inconclusive: null
    accepted_differences: null
    contracts: null
    stale_evidence: null
    dashboards_passing: null

  cutover:
    generate: not_started
    validate: not_started
    review: not_started
    file: null
    generated_date: null
    generated_files: []
    revision_history: []

  training:
    generate: not_started
    validate: not_started
    review: not_started
    session_plans: []
    generated_date: null
    generated_files: []
    revision_history: []

  documentation:
    generate: not_started
    validate: not_started
    review: not_started
    file: null
    generated_date: null
    generated_files: []
    revision_history: []

agents:
  mode: orchestrated
  coordinator_session:
    user: "Mark Rittman"
    session_id: "cd516d5f"   # resumed by the same user in a new session; previous session 7bb027f9
    branch: "main"
    claimed_at: "2026-09-06 21:56"
    last_write: "2026-09-06 23:11"
  last_orchestrated: "2026-09-06 23:11"
  paused_at: null
  active_sessions: []
  completed_sessions: []

precondition_overrides:
  - artifact: bi_migration_plan
    action: bi-migration-plan-generate
    unmet_precondition: "looker_audit.review required approved, was not_started"
    overridden_by: "Mark Rittman"
    reason: "director's directive of 2026-09-06: run the Looker audit, and bring me the migration plan with the parked decisions; audit review parked as PD-2 to be ruled with the plan"
    date: "2026-09-06"

advisory_skips:
  - artifact: bi_migration_plan
    unmet_precondition: "business_rules.review required approved, was not_started (advisory)"
    reason: "not requested in the directive; like-for-like migration of three dashboards; parked as PD-11 for a ruling before target setup"
    date: "2026-09-06"
  - artifact: bi_migration_plan
    unmet_precondition: "omni_audit.review required approved, was not_started (advisory)"
    reason: "not requested in the directive; the target instance already holds a shared model with 998 schema views, so parked as PD-10 for a ruling before target setup"
    date: "2026-09-06"

parked_decisions:
  # Closed 2026-09-06 22:40 by rulings R-6 (PD-1), R-10 (PD-3), R-9 (PD-9), R-12 (PD-12); closed 2026-09-06 by R-16 (PD-4), R-17 (PD-7), R-18 (PD-8). Each remaining entry names the step it blocks.
  - id: PD-2
    artifact: looker_audit
    kind: review
    question: "Looker audit: approve now, request changes, or park for client sign-off? (validate PASS, 8 of 8 checks; audit/looker_audit.md)"
    parked_at: "2026-09-06 22:28"
    blocks: "nothing downstream (the plan it fed is approved); closes the record"
  - id: PD-5
    artifact: omni_content
    kind: ruling
    question: "Parameter-driven tiles: Business Summary tile 3878 and its two dashboard filters (Selected Measure, Selected Split) run on two parameters and two Liquid fields; web_sessions_fact carries period_selector, time_range, period and date_filter. Rebuild as Omni field-selection controls, or as fixed measures and dimensions?"
    parked_at: "2026-09-06 22:35"
    blocks: "content batch c01 (dashboard 267); the model batches carry these fields as needs_human items"
  - id: PD-6
    artifact: omni_content
    kind: ruling
    question: "Merged-results tiles: 8 on Business Summary and 4 on Web Performance. Rebuild each as an Omni query view (SQL joining the source queries), or split into side-by-side tiles?"
    parked_at: "2026-09-06 22:35"
    blocks: "content batches c01 and c02"
  - id: PD-10
    artifact: omni_audit
    kind: ruling
    question: "Omni audit (optional artifact): the target instance already holds a shared model and content. Run /wire:omni-audit-generate before the model batches, or skip?"
    parked_at: "2026-09-06 22:35"
    blocks: "nothing; optional artifact"
  - id: PD-11
    artifact: business_rules
    kind: ruling
    question: "Business rules (optional artifact): skip for this like-for-like migration, or run /wire:business-rules-generate first?"
    parked_at: "2026-09-06 22:35"
    blocks: "nothing; optional artifact"
  # PD-13 and PD-14 closed 2026-09-06 22:50 by R-13 and R-14 (the director's "Approved" to the report that recommended them).
---

# BI Migration Status: 01-looker-to-omni

**Client**: Rittman Analytics
**Project ID**: 20260906
**Type**: bi_migration (looker_to_omni)
**Created**: 2026-09-06
**Last Updated**: 2026-09-06

## Current Phase: Model Migration

## Next Action

Director confirms (or amends) the proposed resolutions for batch b02's 8 needs_human items and the 12 converter self-reference fixes (`migration/omni_model/omni_model.md`), then:
```
apply the patch, write b02 to branch 13dc8819
/wire:omni-model-lint 01-looker-to-omni --batch b02
/wire:omni-model-validate 01-looker-to-omni --batch b02
```
PD-4 is needed before b03 and PD-7 before b07.

## Precondition Overrides

| Date | Artifact | Action | Unmet Precondition | Overridden By | Reason |
|------|----------|--------|---------------------|---------------|--------|
| 2026-09-06 | bi_migration_plan | bi-migration-plan-generate | looker_audit.review required approved, was not_started | Mark Rittman | director's directive of 2026-09-06: run the Looker audit and bring me the migration plan with the parked decisions; audit review parked as PD-2 |

## Artifact Status Summary

| Phase | Artifact | Generate | Validate | Review | Ready |
|-------|----------|----------|----------|--------|-------|
| **Business Rules** (optional) | business_rules | ⏸️ | ⏸️ | ⏸️ | ❌ |
| **Audit** | looker_audit | ✅ | ✅ | ⏸️ (PD-2) | ❌ |
| | omni_audit (optional, brownfield target) | ⏸️ | ⏸️ | ⏸️ | ❌ |
| **Plan** | bi_migration_plan | ✅ (gate overridden) | ✅ | ✅ (R-12) | ✅ |
| **Target** | omni_target_setup | ✅ | ✅ | ✅ (R-15) | ✅ |
| **Model** | omni_model (per batch, plus lint) | 🔄 b02 emitted, not on branch | ❌ lint (L11 x11) | ⏸️ | ❌ |
| **Content** | omni_content (per batch) | ⏸️ | ⏸️ | ⏸️ | ❌ |
| **Parity** | bi_equivalency (loop) | - | ⏸️ | - | ❌ |
| **Cutover** | cutover | ⏸️ | ⏸️ | ⏸️ | ❌ |
| **Enablement** (optional) | training | ⏸️ | ⏸️ | ⏸️ | ❌ |
| | documentation | ⏸️ | ⏸️ | ⏸️ | ❌ |

## Session History

| Date | Consultant | Focus | Outcome | Next |
|------|-----------|-------|---------|------|
| 2026-09-06 | Mark Rittman (orchestrator 7bb027f9) | Engagement setup from the director's directive | Release created, claim written, PD-1 parked | Register and refresh sources, Looker audit, plan |
| 2026-09-06 | Mark Rittman (orchestrator 7bb027f9) | Sources registered and refreshed; Looker audit; migration plan | Audit validate PASS (8/8); plan validate PASS (9/9); 12 decisions parked (PD-1 to PD-12) | Director rulings, then audit review and plan review |
| 2026-09-06 | Mark Rittman (orchestrator 7bb027f9) | Rulings R-6 to R-12 recorded; plan review approved; Omni target setup | Branch 13dc8819 created, 3 schemas refreshed, connection verified; validate FAIL 2/7 (pre-existing model errors, user attribute); PD-13, PD-14 parked | Director rules PD-13, PD-14; re-validate; target setup review; then b02 |
| 2026-09-06 | Mark Rittman (orchestrator 7bb027f9) | R-13 to R-15; target setup validated and approved; batch b02 converter run and lint | 10 stale dimensions removed on the branch, model validates clean; b02: 4 views, 4 topics, 8 needs_human, 11 lint findings (converter self-reference defect); branch write held | Director confirms b02 resolutions; apply patch, write b02, lint, validate |
