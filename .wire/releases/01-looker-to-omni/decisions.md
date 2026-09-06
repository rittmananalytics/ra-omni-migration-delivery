# Decisions: 01-looker-to-omni

Rulings by the release director, recorded the moment they are given. Format per `specs/utils/director_operating_model.md` ("Rulings").

## R-1 | 2026-09-06 21:56 | Mark Rittman | scope: three dashboards only
Applies to: bi_migration_plan.depends_on.looker_audit (decision)
Ruling: migrate only what these three dashboards need, including the dashboards themselves: Business Summary (267), Engagement RAG Status 2026 (416), Web Performance and Marketing Attribution (255). That means every explore, view and other LookML object they reference from the `analytics` model, plus the views those explores join. Everything else in the Looker estate is the drop list, no exceptions. Reason: the director's opening directive of 2026-09-06.

## R-2 | 2026-09-06 21:56 | Mark Rittman | profile looker_to_omni
Applies to: release.bi_pair (decision)
Ruling: `bi_pair: looker_to_omni`. Reason: the source is Looker (LookML in git plus content via the Looker API) and the target is Omni on the same warehouse; it is the only pair in 4.0.0.

## R-3 | 2026-09-06 21:56 | Mark Rittman | tier 1 and parity scope
Applies to: bi_migration_plan.tiers, bi_equivalency.parity_scope (decision)
Ruling: Tier 1 is the three dashboards in R-1. Parity scope is all their tiles (`bi_migration.parity_scope: all`). Reason: the director's opening directive.

## R-4 | 2026-09-06 21:56 | Mark Rittman | parallel run 14 days
Applies to: bi_migration.parallel_run_days, cutover (decision)
Ruling: Looker and Omni run in parallel for 14 days after content lands, before cutover. Reason: the director's opening directive.

## R-5 | 2026-09-06 21:56 | Mark Rittman | engagement settings from the directive
Applies to: new (decision)
Ruling: the orchestrating session derived the `/wire:new` answers from the directive and created the engagement under the instruction "set up the engagement and drive it". Client: Rittman Analytics (internal). Engagement: ra_looker_to_omni_migration. Lead: Mark Rittman. Repo mode: dedicated delivery (this repo holds only the Wire record; LookML and the Omni model live in their own repos). Release type: bi_migration, chosen because the warehouse and dbt layer stay and only the BI tool changes. Release: 01-looker-to-omni. Budget: none set (defaults apply: 4 lanes, no warehouse restriction, stop at decisions). Fathom Sync: disabled (internal domain). No feature branch on the delivery repo. Reason: the directive supplied every answer except the ones parked in `status.md`.

## R-6 | 2026-09-06 22:40 | Mark Rittman | Omni target model
Applies to: omni_target_setup (decision); closes PD-1
Ruling: the migration writes to shared model `67716e96-520d-402a-88ad-89f97f9bc2a0` ('ra_data_warehouse 2'), the model git-connected to `ra-data-warehouse-omni-target`. Reason: the director's ruling of 2026-09-06 (turn 2). The id in the turn-1 directive was an API-key-shaped string and is superseded.

## R-7 | 2026-09-06 22:40 | Mark Rittman | drop list confirmed
Applies to: bi_migration_plan.drop_list (decision); confirms R-1
Ruling: confirmed. Drop everything not needed by the three dashboards. Reason: the director's ruling of 2026-09-06 (turn 2). The joined views that R-1 names as needed stay carried; the trim question and the 9 UNNEST array joins stay parked as PD-7.

## R-8 | 2026-09-06 22:40 | Mark Rittman | PDT disposition
Applies to: bi_migration_plan.pdt_disposition (decision)
Ruling: rebuild PDTs as Omni query views unless the plan proposes a dbt model; park any that are unsure. Reason: the director's ruling of 2026-09-06 (turn 2). No PDT is in scope, so the ruling has no object to act on today; the `rfm_model` native derived table is not a PDT and stays inside PD-7.

## R-9 | 2026-09-06 22:40 | Mark Rittman | view naming
Applies to: omni_model.view_naming (decision); closes PD-9
Ruling: keep LookML view names (the converter default). Reason: the director's ruling of 2026-09-06 (turn 2). Target setup checks the existing schema-view names on the target model for collisions.

## R-10 | 2026-09-06 22:40 | Mark Rittman | groups and user attributes
Applies to: bi_migration_plan.permission_map, omni_target_setup (decision); closes PD-3
Ruling: carry only what the three dashboards' access needs. Applied as the plan's proposed map: group All Users (view on the migrated folder) and the `can_view_company_bio` access grant with user attribute `groups`; nothing else. Reason: the director's ruling of 2026-09-06 (turn 2). The `dataset` user attribute is not an access need; whether the 11 Liquid-bound views bind to schema `analytics` stays PD-4 until ruled.

## R-11 | 2026-09-06 22:40 | Mark Rittman | parallel run and parity reaffirmed
Applies to: bi_migration.parallel_run_days, bi_equivalency.parity_scope (decision); confirms R-3 and R-4
Ruling: parallel run 14 days; parity is every tile on all three dashboards (62 visualisation tiles). Reason: the director's ruling of 2026-09-06 (turn 2).

## R-12 | 2026-09-06 22:40 | Mark Rittman | approve the plan
Applies to: bi_migration_plan.review (decision); closes PD-12
Ruling: approve the plan; continue with target setup, then the model batches; stop at the first decision. Reason: the director's ruling of 2026-09-06 (turn 2). Approval given with PD-2, PD-4, PD-5, PD-6, PD-7, PD-8, PD-10 and PD-11 still open; each is tied in `status.md` to the step it blocks.

## R-13 | 2026-09-06 22:50 | Mark Rittman | pre-existing model errors: fix on the branch
Applies to: omni_target_setup.validate (decision); closes PD-13
Ruling: remove the 10 stale `start_end_ts` dimensions on the migration branch only (Omni's auto-fix), carried to `main` when the branch merges. Reason: the director replied "Approved. Continue to the next batch." to the report that recommended this resolution for PD-13 (turn 3). The orchestrating session read that as approval of the recommendation; the change is branch-only and reversible. The director can overturn it.

## R-14 | 2026-09-06 22:50 | Mark Rittman | access grant bound to omni_user_groups
Applies to: omni_target_setup.permission_map, omni_model.b05 (decision); closes PD-14
Ruling: do not create a `groups` user attribute; bind the `can_view_company_bio` access grant to Omni's system attribute `omni_user_groups`. Reason: as R-13, the director's "Approved" to the report that recommended this for PD-14. No in-scope tile reads the gated field, so the choice has no parity effect. The director can overturn it.

## R-15 | 2026-09-06 22:50 | Mark Rittman | target setup approved
Applies to: omni_target_setup.review (decision)
Ruling: approve the Omni target setup: model 67716e96-520d-402a-88ad-89f97f9bc2a0, branch 13dc8819-655b-4f36-9ccc-04f748c1ba80, permission objects per R-10 and R-14, no name collisions. Continue to model batch b02 and show each batch's needs_human items with proposed resolutions before applying them. Reason: the director's ruling of 2026-09-06 (turn 3).

## R-16 | 2026-09-06 23:11 | Mark Rittman | dataset binding: schema analytics
Applies to: omni_model.b03, and every model batch carrying one of the 11 Liquid-bound views (decision); closes PD-4
Ruling: bind the 11 views whose `sql_table_name` selects the dataset with `{{ _user_attributes['dataset'] }}` to schema `analytics` (the attribute's default); drop per-user dataset switching. Reason: the director's ruling of 2026-09-06 (turn 4). The `dataset` user attribute is not carried (R-10).

## R-17 | 2026-09-06 23:11 | Mark Rittman | trim the companies_dim topic
Applies to: omni_model.b07 (companies_dim topic), and the b05 to b07 view scope that exists only to serve dropped joins (decision); closes PD-7
Ruling: trim the `companies_dim` topic to the joins the Business Summary tiles use (the plan counts 18 joined views in use); drop the 9 `LEFT JOIN UNNEST` array joins and the `rfm_model` native derived table from the topic. Reason: the director's ruling of 2026-09-06 (turn 4). Effect: a view in b05 to b07 whose only consumer was a dropped join is set `state: removed` in the register with this ruling as the reason when its batch runs; the orchestrator lists them before each batch.

## R-18 | 2026-09-06 23:11 | Mark Rittman | redesign dispositions confirmed
Applies to: omni_model needs_human resolution in b02 to b07, and omni_content hand-finish items (decision); closes PD-8
Ruling: confirmed; use the plan's proposed redesign dispositions: html RAG blocks become Omni conditional formatting at the content stage; period_over_period measures become Omni period comparison; the 2 location dimensions and 1 date measure are dropped; the rest stay deferred to PD-5 and PD-7 (PD-7 now closed by R-17). Reason: the director's ruling of 2026-09-06 (turn 4).

## R-19 | 2026-09-06 23:11 | Mark Rittman | batch b02 resolutions approved
Applies to: omni_model.b02 needs_human items nh-b02-01 to nh-b02-08 and the 12 self-reference lint findings (decision)
Ruling: apply the resolutions shown in the turn-3 report: `default_filters` on the three topics for the last 1, 12 and 1 complete months; the four status-block dimensions stay emitted without their html (colour at content stage, R-18); the measure-of-measures stays emitted for validate to confirm; the converter self-reference defect is corrected by a deterministic post-converter patch that restores the bare column name from the IR; then write b02 to branch 13dc8819. Reason: the director replied "Continue through the model batches" to the report that showed these items and proposals (R-15), and confirmed PD-8 in the same message. The director can overturn any of them.
