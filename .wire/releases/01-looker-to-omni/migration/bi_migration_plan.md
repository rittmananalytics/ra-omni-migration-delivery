# BI Migration Plan: 01-looker-to-omni

**Release**: 01-looker-to-omni (bi_migration, looker_to_omni)  
**Generated**: 2026-09-06  
**Built from**: `audit/looker_audit.md` (validate PASS), LookML commit `82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e`, Looker System Activity usage to 2026-09-06  
**Rulings on record**: R-1 scope, R-2 profile, R-3 tier 1 and parity scope, R-4 parallel run (`decisions.md`). Every ruling not on record is parked, not guessed.  
**Audit review**: not yet approved (PD-2). This plan was generated ahead of that approval at the director's instruction; see `status.md` `precondition_overrides`.

## Summary

| Measure | Value |
|---|---|
| Dashboards in scope | 3 (ids 267, 255, 416) of 196 |
| Tiles in scope (visualisation tiles, all compared for parity) | 62 of 1636 elements |
| Text tiles and filter elements on the three dashboards | 8 (text tiles recreated by hand; filter elements become controls) |
| Looks in scope | 0 of 148 (no in-scope dashboard embeds a Look) |
| Schedules in scope | 1 of 6 (id 91, Web Performance to Slack, weekly) |
| Alerts in scope | 1 of 3 (id 3, daily, on Business Summary element 2514) |
| Explores carried as topics | 15 of 39 |
| Views carried | 73 of 190 (base views plus every joined view, plus extends bases) |
| Fields carried | 1643 |
| Redesign rows in scope | 61 (dispositions proposed, PD-8) |
| Assisted rows in scope | 158 |
| Model batches | 6 plus 1 permissions batch |
| Content batches | 3 |
| Dropped | 193 dashboards, 148 Looks, 5 schedules, 2 alerts, 117 views, 24 explores |
| Register rows | 156 |
| Rulings made / parked | 4 made (R-1 to R-4), 9 parked (PD-3 to PD-11) |

## Usage ranking

Usage is System Activity dashboard runs in the 90 days to 2026-09-06 (Looks: query runs). Ranking is across dashboards and Looks together. `stale_after_days` is 180.

| Tier (by usage) | Count | Definition | Plan treatment |
|---|---|---|---|
| Tier 1 (80% of runs) | 4 | 267 Business Summary, 415 Project Profitability, 389 Utilisation & Recognised Attributed Revenue, 311 Engagement RAG Status Dashboard | R-1 keeps 267 and drops the others in this set: they are not one of the three dashboards |
| Tier 2 (remaining runs) | 47 | any run in 90 days, not tier 1 | 255 and 416 are carried by R-1; the rest are dropped by R-1 |
| Stale (0 runs in 90 days) | 293 | 159 dashboards, 134 Looks | dropped by R-1 |
| Usage unknown | 0 |  |  |

| Rank | Kind | Id | Title | Runs 90d | Last viewed | Ruling |
|---|---|---|---|---|---|---|
| 1 | dashboard | 267 | Business Summary | 488 | 2026-09-06 | parity (R-1, R-3) |
| 2 | dashboard | 415 | Project Profitability | 234 | 2026-08-28 | drop (R-1) |
| 3 | dashboard | 389 | Utilisation & Recognised Attributed Revenue | 102 | 2026-09-04 | drop (R-1) |
| 4 | dashboard | 311 | Engagement RAG Status Dashboard | 96 | 2026-08-30 | drop (R-1) |
| 5 | look | 366 | Client Profitability | 20 | 2026-08-05 | drop (R-1) |
| 6 | dashboard | 255 | Web Performance & Marketing Attribution | 18 | 2026-09-06 | parity (R-1, R-3) |
| 7 | look | 299 | Customer List | 13 | 2026-09-03 | drop (R-1) |
| 8 | look | 197 | usage | 13 | 2026-09-05 | drop (R-1) |
| 9 | dashboard | 409 | Financial Analytics 2026 | 11 | 2026-08-26 | drop (R-1) |
| 10 | dashboard | 411 | Sav's Metrics | 10 | 2026-06-10 | drop (R-1) |
| 11 | dashboard | 408 | Claude Code & Wire Session Diagnostics | 5 | 2026-07-21 | drop (R-1) |
| 12 | dashboard | 271 | Marketing Analytics: Performance Overview | 4 | 2026-07-02 | drop (R-1) |
| 13 | dashboard | 407 | Claude Code Analytics | 3 | 2026-08-25 | drop (R-1) |
| 14 | dashboard | 375 | End of 2025 Review | 3 | 2026-08-26 | drop (R-1) |
| 15 | dashboard | 349 | Financial Analytics 2025 | 3 | 2026-07-30 | drop (R-1) |

The director's ruling, not the usage cut, sets the scope: the three dashboards are tier 1 (R-3) and everything else is dropped (R-1). Usage is recorded so the cost of R-1 is visible: dashboards 415 (234 runs) and 389 (102 runs) are the second and third most used in the estate and are not carried.

## Rulings

| Ruling | Status | Reference | Decision |
|---|---|---|---|
| Parity or redesign, per tier | made | R-3, Mark Rittman, 2026-09-06 21:56 | Tier 1 (267, 255, 416): parity, rebuilt as-is with every tile compared. Tier 2: empty (R-1 drops everything else). |
| Drop list | made | R-1, Mark Rittman, 2026-09-06 21:56 | Everything not needed by the three dashboards: 193 dashboards, 148 Looks, 5 schedules, 2 alerts, 117 views, 24 explores. No exceptions. The stale set (0 runs in 180 days) is inside this list. |
| PDT disposition | not applicable |  | No PDT is in scope. The estate's 4 PDTs (cumulative_churned_clients, engagement_renewal_analysis, ga_multi_cycle_multi_touch_attribution, page_keyword_performance) are reached by no in-scope content and are dropped by R-1. |
| Permission mapping | made | R-10, Mark Rittman, 2026-09-06 22:40 | Carry only what the three dashboards' access needs: group All Users (view on the migrated folder), access grant can_view_company_bio with user attribute groups. Nothing else carried. The dataset user attribute is not an access need; its binding stays PD-4. |
| Topic architecture | default applied | stated default | One Omni topic per Looker explore: 15 topics. Confirm or amend at plan review. |
| Parallel-run window | made | R-4, Mark Rittman, 2026-09-06 21:56 | 14 days side by side after content lands, before cutover. |
| Parity scope | made | R-3, Mark Rittman, 2026-09-06 21:56 | All tiles of the three dashboards: 62 visualisation tiles. `bi_migration.parity_scope: all`. |

### Parked decisions raised by this plan

| Id | Question |
|---|---|
| PD-3 | Closed by R-10 (2026-09-06 22:40): carry group All Users and the can_view_company_bio access grant with user attribute groups; nothing else. |
| PD-4 | Dataset binding: 11 in-scope views select their BigQuery dataset with `{{ _user_attributes['dataset'] }}` (default `analytics`). Bind them to schema `analytics` in Omni and drop per-user dataset switching? |
| PD-5 | Parameter-driven tiles: Business Summary tile 3878 and its two dashboard filters (Selected Measure, Selected Split) run on two parameters and two Liquid fields; web_sessions_fact carries period_selector, time_range, period and date_filter. Rebuild as Omni field-selection controls, or as fixed measures and dimensions? |
| PD-6 | Merged-results tiles: 8 on Business Summary and 4 on Web Performance. Rebuild each as an Omni query view (SQL joining the source queries), or split into side-by-side tiles? |
| PD-7 | Unused joins carried by R-1: companies_dim has 65 joins; the Business Summary tiles use fields from 18 of its views. Keep all 73 joined views as ruled, or trim the companies_dim topic to the joins the tiles use? Inside this: 9 LEFT JOIN UNNEST array joins and the rfm_model native derived table have no Omni relationship form and no in-scope tile uses them (drop from the topic, or rebuild as flattened SQL views). |
| PD-8 | Redesign dispositions: confirm the proposed disposition table (html RAG blocks as conditional formatting; period_over_period as Omni period comparison; location dimensions and one date measure dropped; the rest deferred to PD-5 and PD-7). |
| PD-9 | Closed by R-9 (2026-09-06 22:40): keep LookML view names (the converter default). Target setup checks the existing schema-view names for collisions. |
| PD-10 | Omni audit (optional artifact): the target instance already holds a shared model and content. Run /wire:omni-audit-generate before target setup, or skip? |
| PD-11 | Business rules (optional artifact): skip for this like-for-like migration, or run /wire:business-rules-generate first? |

PD-1 was closed by R-6 (2026-09-06 22:40): the target is shared model `67716e96-520d-402a-88ad-89f97f9bc2a0` ('ra_data_warehouse 2'). PD-2 (approve the Looker audit) is still open; it blocks nothing downstream.

## Model scope

In scope: every view and explore reached by the three dashboards, plus every view those explores join, plus extends bases (R-1). 73 views, 15 topics, 1643 fields. Hidden fields are carried hidden.

### Carried, by batch

**b02** Engagement health topics (feeds dashboard 416): 4 views, 4 topics  
Topics: `engagement_health_fact`, `engagement_sprint_burn_fact`, `engagement_burn_up_fact`, `engagement_actions_fact`  
Views: `engagement_actions_fact`, `engagement_burn_up_fact`, `engagement_health_fact`, `engagement_sprint_burn_fact`  

**b03** Web analytics and marketing topics (feeds dashboard 255): 11 views, 3 topics  
Topics: `web_sessions_fact`, `ad_campaign_performance_fact`, `organic_posts_dim`  
Views: `ad_campaign_performance_fact`, `ad_campaigns_dim`, `has_viewed_pricing`, `ips_enriched`, `is_conversion_session`, `organic_post_performance_fact`, `organic_posts_dim`, `page_first_published`, `web_events_fact`, `web_sessions_fact`, `wh_sessions_attribution`  

**b04** Targets, forecast and financials topics (feeds dashboard 267): 10 views, 5 topics  
Topics: `targets`, `monthly_resource_revenue_forecast_fact`, `revenue_and_forecast`, `project_engagements`, `chart_of_accounts_dim`  
Views: `bank_account_details`, `bank_transactions_fact`, `chart_of_accounts_dim`, `general_ledger_fact`, `monthly_resource_revenue_forecast_fact`, `profit_and_loss_report_fact`, `project_engagements`, `revenue_and_forecast`, `sales_targets`, `targets`  

**b05** Companies core, NPS and delivery-team topics (feeds dashboard 267): 15 views, 2 topics  
Topics: `nps_survey_results_fact`, `contacts`  
Views: `companies_dim`, `contacts_dim`, `customer_meetings`, `delivery_projects_dim`, `delivery_tasks_fact`, `engagements`, `exchange_rates`, `invoices_fact`, `meeting_contact_lines_fact`, `messages_fact`, `nps_survey_results_fact`, `payments_fact`, `timesheet_projects_dim`, `timesheet_tasks_dim`, `timesheets_fact`  

**b06** Business operations views, part 1 (companies_dim joins): 17 views, 0 topics  
Topics: none  
Views: `client_prospect_status_dim`, `companies_dim__all_company_ids`, `company_converted_projects`, `company_deal_value_attribute`, `contact_companies_fact`, `contact_meetings_fact`, `contracts_fact`, `customer_first_deal_cohorts`, `customer_first_order_segments`, `deal_pipeline_history`, `deals_fact`, `delivery_project_docs_dim`, `delivery_task_history`, `engagement_details`, `engagement_details__deliverables`, `engagement_details__objectives`, `persons_dim`  

**b07** Business operations views, part 2, and the companies_dim topic: 16 views, 1 topics  
Topics: `companies_dim`  
Views: `projects_delivered_is_ontime`, `recognized_revenue_fact`, `rfm_model`, `src_control_daily_metrics_fact`, `src_control_pull_requests_fact`, `src_control_repos_dim`, `team_revenue_targets`, `timesheet_project_costs_fact`, `timesheet_project_engagement_rag_status_fact`, `timesheet_project_engagement_rag_status_fact__client_action_points`, `timesheet_project_engagement_rag_status_fact__month_timeline_events`, `timesheet_project_engagement_rag_status_fact__ra_action_points`, `timesheet_project_engagements_dim__projects`, `timesheet_project_stakeholder_jtbd_fact`, `timesheet_project_stakeholder_jtbd_fact__identified_jtbds`, `timesheet_project_stakeholder_jtbd_fact__keywords`  

### Views used by the tiles versus views carried

| Dashboard | Title | Explores | Views (or join aliases) the tiles reference | Names |
|---|---|---|---|---|
| 267 | Business Summary | 8 | 18 | companies_dim, consultant_revenue_attribution, contacts, customer_meetings, deal_pipeline_history, deals_fact, engagements, monthly_resource_revenue_forecast_fact, nps_survey_results_fact, profit_and_loss_report_fact, project_engagements, projects_delivered, recognized_project_revenue, recognized_revenue_contact, revenue_and_forecast, targets, team_revenue_targets, timesheets_fact |
| 255 | Web Performance & Marketing Attribution | 3 | 7 | ad_campaign_performance_fact, ad_campaigns_dim, organic_post_performance_fact, organic_posts_dim, web_events_fact, web_sessions_fact, wh_sessions_attribution |
| 416 | Engagement RAG Status 2026 | 4 | 4 | engagement_actions_fact, engagement_burn_up_fact, engagement_health_fact, engagement_sprint_burn_fact |

### Model not carried

117 views and 24 explores, each with the reason `no in-scope content references it` (R-1). Full list in the Drop list section and in `bi_migration_batches.csv` (`ruling: drop`, empty `batch_id`).

### Redesign dispositions (proposed, PD-8)

| Construct | Rows in scope | Proposed disposition | Note | Decision |
|---|---|---|---|---|
| dimension:html | 11 | redesign in Omni | RAG status colour blocks: emit the dimension, recreate the colour as Omni table conditional formatting on the status text | PD-8 |
| dimension:liquid | 2 | defer | dynamic_split (forecast split selector) and web_sessions_fact.period: rebuild with Omni controls or fixed dimensions | PD-5 |
| dimension:location | 2 | drop | ips_enriched.ip_location and web_events_fact.map_location: no in-scope tile uses them; Omni has no location type | PD-8 |
| filter_field | 1 | defer | web_sessions_fact.date_filter: dashboard 255 filters on session_start_ts_date directly; rebuild as a dashboard control if any tile needs it | PD-5 |
| join:one_to_many:left_outer | 9 | defer | 9 LEFT JOIN UNNEST array joins in companies_dim; no in-scope tile uses their fields; drop from the topic or rebuild as flattened SQL views | PD-7 |
| measure:date | 1 | drop | timesheets_fact.last_timesheet_billing_date: no in-scope tile uses it | PD-8 |
| measure:number | 1 | defer | monthly_resource_revenue_forecast_fact.dynamic_measure: parameter-driven measure on the forecast tile | PD-5 |
| measure:period_over_period | 16 | redesign in Omni | 16 prior-period measures on profit_and_loss_report_fact: use Omni period-over-period comparison on the tile; not used by an in-scope tile directly | PD-8 |
| measure:sum | 1 | defer | profit_and_loss_report_fact.revenue_dynamic_prior_period: Liquid over comparison_period parameter | PD-8 |
| parameter | 5 | defer | 5 parameters: selected_measure, selected_split (dashboard 267 filters), comparison_period, period_selector, time_range; Omni templated filters or field-selection controls | PD-5 |
| view:native_derived_table | 1 | defer | rfm_model: native derived table joined to companies_dim; no in-scope tile uses it; rebuild as an Omni query view only if PD-7 keeps the join | PD-7 |
| view:sql_table_name_liquid | 11 | redesign in Omni | bind to schema `analytics` with the plain table name (the `dataset` user attribute default); no Liquid in Omni | PD-4 |

Every in-scope redesign row is listed with its source in `audit/looker_audit.md` (Redesign register, `In scope: yes`).

### PDT dispositions

| PDT view | In scope | Disposition | Reason |
|---|---|---|---|
| cumulative_churned_clients | no | drop | no in-scope content references it (R-1) |
| engagement_renewal_analysis | no | drop | no in-scope content references it (R-1) |
| ga_multi_cycle_multi_touch_attribution | no | drop | no in-scope content references it (R-1) |
| page_keyword_performance | no | drop | no in-scope content references it (R-1) |

### Unresolved references to carry into the content batch

| Dashboard | Reference | Finding | Plan |
|---|---|---|---|
| 267 | consultant_revenue_attribution.attributed_project_cost_gbp | field exists but its view is not joined to any explore the dashboard queries | confirm the tile renders in Looker before parity; if it errors there, record as accepted difference at the director's ruling |
| 267 | consultant_revenue_attribution.attributed_project_revenue_gbp | field exists but its view is not joined to any explore the dashboard queries | confirm the tile renders in Looker before parity; if it errors there, record as accepted difference at the director's ruling |
| 267 | deals_fact.total_oppportunity_deal_amount | field not in LookML project | confirm the tile renders in Looker before parity; if it errors there, record as accepted difference at the director's ruling |
| 255 | web_sessions_fact.total_web_sessions_pk | field not in LookML project | confirm the tile renders in Looker before parity; if it errors there, record as accepted difference at the director's ruling |

## Permission map (proposed, PD-3)

| Kind | Looker object | Looker side | Omni side | Action | Batch |
|---|---|---|---|---|---|
| group | All Users | Looker group 1, view access on the Shared folder (all 3 dashboards) | Omni organisation default: every member can view the migrated folder | carry | b01 |
| access_grant | can_view_company_bio | user attribute `groups` in [Pepkor IT, Google, Brighton SST]; on companies_dim.company_description | Omni access grant on the same field, user attribute `groups` | carry | b01 |
| user_attribute | groups | advanced_filter_string, default empty; read by can_view_company_bio | R-14: bound to Omni's system attribute `omni_user_groups`; no new attribute created | carry | b01 |
| user_attribute | dataset | default `analytics`; selects the BigQuery dataset in 11 in-scope views through Liquid | not carried: bind the 11 views to schema `analytics` (PD-4) | bind_constant | b01 |
| group | RA Staff (19), Can See Financial Data (3), Can See HR Data (3), User (11), others | no in-scope dashboard, explore or field depends on them | not carried | drop |  |
| user_attribute | can_see_financial_data, can_see_hr_data, company_name, client_id_rep, project_id, others | no in-scope explore has an access_filter; not referenced by in-scope LookML | not carried | drop |  |

Content access: all three dashboards sit in the `Shared` folder, viewable by group `All Users` (40 users, 33 active). No in-scope explore carries an `access_filter`.

## Topic architecture

One topic per explore (default; confirm at review): 15 topics. Four are single-view topics (the engagement_* facts). `companies_dim` is the largest, with 65 joins (PD-7). Topic default filters: `engagement_health_fact`, `engagement_sprint_burn_fact` and `engagement_actions_fact` carry `always_filter` on reporting month (12, 1 and 1 months); `contacts` carries `sql_always_where` on staff or contractor flags.

| Topic | Base view | Joins | Hidden in Looker | Batch | Feeds dashboards |
|---|---|---|---|---|---|
| ad_campaign_performance_fact | ad_campaign_performance_fact | 1 | yes | b03 | 255 |
| chart_of_accounts_dim | chart_of_accounts_dim | 4 |  | b04 | 267 |
| companies_dim | companies_dim | 65 |  | b07 | 267 |
| contacts | contacts_dim | 13 | yes | b05 | 267 |
| engagement_actions_fact | engagement_actions_fact | 0 |  | b02 | 416 |
| engagement_burn_up_fact | engagement_burn_up_fact | 0 |  | b02 | 416 |
| engagement_health_fact | engagement_health_fact | 0 |  | b02 | 416 |
| engagement_sprint_burn_fact | engagement_sprint_burn_fact | 0 |  | b02 | 416 |
| monthly_resource_revenue_forecast_fact | monthly_resource_revenue_forecast_fact | 0 | yes | b04 | 267 |
| nps_survey_results_fact | nps_survey_results_fact | 3 | yes | b05 | 267 |
| organic_posts_dim | organic_posts_dim | 1 |  | b03 | 255 |
| project_engagements | project_engagements | 0 | yes | b04 | 267 |
| revenue_and_forecast | revenue_and_forecast | 0 | yes | b04 | 267 |
| targets | targets | 1 |  | b04 | 267 |
| web_sessions_fact | web_sessions_fact | 6 |  | b03 | 255 |

## Batches

Model batches run in id order; a topic sits in the batch that carries its last view. Content batches run in usage order and each waits on the last model batch its dashboard needs. Batch sizes above the 5 to 15 view target (b06, b07) come from the single `companies_dim` explore; splitting it further would put the topic in a later batch than its views for no benefit.

| Batch | Kind | Scope | Contents | Usage rank | Depends on |
|---|---|---|---|---|---|
| b01 | model | permissions | 1 group, 1 access grant, 2 user attributes |  |  |
| b02 | model | Engagement health topics (feeds dashboard 416) | 4 views, 4 topics |  | b01 |
| b03 | model | Web analytics and marketing topics (feeds dashboard 255) | 11 views, 3 topics |  | b01 |
| b04 | model | Targets, forecast and financials topics (feeds dashboard 267) | 10 views, 5 topics |  | b01 |
| b05 | model | Companies core, NPS and delivery-team topics (feeds dashboard 267) | 15 views, 2 topics |  | b01 |
| b06 | model | Business operations views, part 1 (companies_dim joins) | 17 views, 0 topics |  | b01 |
| b07 | model | Business operations views, part 2, and the companies_dim topic | 16 views, 1 topics |  | b01 |
| c01 | content | 267 Business Summary | 17 vis tiles, alert 3 | 1 | b07 |
| c02 | content | 255 Web Performance & Marketing Attribution | 28 vis tiles, schedule 91 | 6 | b03 |
| c03 | content | 416 Engagement RAG Status 2026 | 17 vis tiles | 39 | b02 |

Run order: b01, b02, b03, b04, b05, b06, b07, then c01 (after b07), c02 (after b03; can start once b03 validates), c03 (after b02; can start once b02 validates). Parity sweeps follow each content batch.

## Parallel run and parity

| Item | Value |
|---|---|
| Parallel-run window | 14 days (R-4), starting when the last content batch lands |
| Parity scope | all tiles of the three dashboards: 62 visualisation tiles (R-3); text tiles and filter elements are not compared |
| Pinned as-of | `2026-09-05T23:59:59Z` (UTC, BigQuery); recorded in `migration/baseline.yaml` as baseline b001 |
| Evidence | `migration/parity/evidence.csv`: 135 rows (one per tile and view register row), fingerprints from `scripts/bi_evidence.py` v1 |
| Tiles expected to need a ruling before PASS | 13 redesign tiles (merged results, custom visualisation) plus tiles that reference stale fields |
| Cutover | refused until bi_equivalency passes on every in-scope tile; schedule 91 and alert 3 are recreated at cutover |

## Drop list

Every dropped object with its reason. Reasons: `R-1` = director ruling, not needed by the three dashboards; `no in-scope content references it` = model object reached by no in-scope dashboard; `text tile` = recreated by hand; `filter element` = becomes a dashboard control.

**Dashboards dropped (193)**, reason R-1:

| Id | Title | Folder | Runs 90d |
|---|---|---|---|
| 415 | Project Profitability | Users/Mark Rittman | 234 |
| 389 | Utilisation & Recognised Attributed Revenue | Shared | 102 |
| 311 | Engagement RAG Status Dashboard | Shared | 96 |
| 409 | Financial Analytics 2026 | Shared | 11 |
| 411 | Sav's Metrics | Users/Saverro Suseno | 10 |
| 408 | Claude Code & Wire Session Diagnostics | Shared | 5 |
| 271 | Marketing Analytics: Performance Overview | Users/Lewis Baker | 4 |
| 349 | Financial Analytics 2025 | Shared | 3 |
| 375 | End of 2025 Review | Shared | 3 |
| 407 | Claude Code Analytics | Users/Mark Rittman | 3 |
| 87 | Web Traffic | Shared/Rittman Analytics/Operations | 3 |
| 132 | RFM Analysis | Shared/Customer Success | 2 |
| 133 | Revenue Analysis | Shared/Customer Success | 2 |
| 142 | Client Concentration | Shared/Customer Success | 2 |
| 181 | Marketing Channel Effectiveness | Shared/Marketing | 2 |
| 229 | Business Summary 2023 | Shared | 2 |
| 305 | Deal Analysis | Shared | 2 |
| 335 | Google Search Performance | Shared | 2 |
| 352 | Analytics Examples | Shared/Delivery Team Examples | 2 |
| 366 | Retail | Shared/Delivery Team Examples | 2 |
| 403 | Delivery Performance | Shared | 2 |
| 404 | Delivery Status | Shared | 2 |
| 412 | Rapha — Analytics Modernisation: Hours, Cost & Profit (CY2026) | Users/Mark Rittman | 2 |
| 201 | Project Performance | Users/Lewis Baker | 1 |
| 254 | Delivery Performance | Users/Lewis Baker | 1 |
| 270 | Web Analytics (GenAI Demo Small) | Shared | 1 |
| 331 | Cashflow | Shared | 1 |
| 338 | Executive Overview | Shared | 1 |
| 362 | Bonus Info | Users/Saverro Suseno | 1 |
| 378 | Productivity | Users/Mark Rittman | 1 |
| 388 | Consultant KPI Performance Dashboard v5 | Users/Mark Rittman | 1 |
| 401 | Delivery Analysis | Shared | 1 |
| 406 | HubSpot Deals Pipeline — Revenue, Duration, Sprints & Likelihood | Users/Mark Rittman | 1 |
| analytics::engagement_health | Engagement Health and Commentary | LookML Dashboards | 1 |
| 112 | 2020 vs 2019 | Shared/Analysis | 0 |
| 117 | Sprint Pipeline & Revenue Cash Projection | Shared/Rittman Analytics/Operations | 0 |
| 136 | Forecast | Shared/Rittman Analytics/Operations | 0 |
| 143 | Review of 2021 | Shared/Analysis | 0 |
| 144 | 2022 Planning | Users/Toby Sexton | 0 |
| 145 | Ideal Customer | Shared/Customer Success | 0 |
| 155 | Test Dashboard | Users/Andras Zimmer/kurban | 0 |
| 158 | Hifly - Airline Delays | Users/Andras Zimmer | 0 |
| 159 | Utilization | Shared/Rittman Analytics/Operations | 0 |
| 162 | Hacker News | Users/Mark Rittman | 0 |
| 163 | Hacker News Authors | Users/Mark Rittman | 0 |
| 164 | HN Firebolt Demo | Users/Mark Rittman | 0 |
| 165 | HN BigQuery Demo | Users/Mark Rittman | 0 |
| 166 | Firebolt Performance Comparison | Users/Mark Rittman | 0 |
| 169 | Profit & Loss Report | Users/Mark Rittman | 0 |
| 171 | Sales Forecast | Users/Mark Rittman | 0 |
| 172 | Start the Week | Users/Mark Rittman | 0 |
| 173 | Delivery Update | Users/Lewis Baker | 0 |
| 175 | Test | Users/Jordan Ilyat | 0 |
| 177 | temo | Users/Mark Rittman | 0 |
| 178 | Business Summary 2022 v4 | Users/Mark Rittman | 0 |
| 182 | Case Study Ecommerce | Users/Jordan Ilyat | 0 |
| 183 | Case study wip | Users/Jordan Ilyat | 0 |
| 184 | Business Summary 2023 | Users/Mark Rittman | 0 |
| 185 | Contact Interests | Shared | 0 |
| 186 | Product Events | Users/Mark Rittman | 0 |
| 190 | Business Summary 2022 v3 (imported 2) | Users/Mark Rittman | 0 |
| 192 | Business Summary 2022 v3 (imported 3) | Users/Mark Rittman | 0 |
| 193 | Sales Dashboard | Shared/Rittman Analytics/Operations | 0 |
| 194 | Business Summary 2022 v6 | Users/Mark Rittman | 0 |
| 195 | New or Existing Business Breakdown | Shared/Sales | 0 |
| 196 | Customer Spread | Users/Mark Rittman | 0 |
| 197 | Monthly Performance Snapshot | Shared/Rittman Analytics/Operations | 0 |
| 199 | New Dashboard | Users/Jordan Ilyat | 0 |
| 200 | project_overview | Users/Lewis Baker | 0 |
| 211 | Modern Data Stack Campaign | Shared/Marketing | 0 |
| 212 | Organic Search Performance | Shared/Rittman Analytics/Operations | 0 |
| 215 | Finance Analysis Dec 2022 | Shared/Finance | 0 |
| 216 | Client First Order Segment Analysis | Shared/Customer Success | 0 |
| 217 | Session Analysis for Week 45 L4Y | Shared/Analysis | 0 |
| 219 | Ticket Completion | Shared/Analysis | 0 |
| 225 | Business Summary 2022 v6 (imported) | Users/Mark Rittman | 0 |
| 226 | Session Journey Explorer | Shared | 0 |
| 230 | Traffic Analysis | Shared | 0 |
| 231 | Q1 Review 2023 | Shared | 0 |
| 232 | Visitor Journey | Users/Mark Rittman | 0 |
| 233 | Visitor Journey | Shared/Marketing | 0 |
| 234 | % of Users Viewing Pricing Page by Channel | Shared/Marketing | 0 |
| 235 | Customer Dashboard | Shared/Customer Success | 0 |
| 236 | Marketing Attribution | Users/Mark Rittman | 0 |
| 237 | Content Marketing | Users/Mark Rittman | 0 |
| 239 | Strava | Users/Mark Rittman | 0 |
| 241 | Marketing Attribution | Users/Jordan Ilyat | 0 |
| 243 | Client Details | Users/Mark Rittman | 0 |
| 244 | Client List | Shared/Customer Success | 0 |
| 246 | Rittman Analytics Forecast Performance for 2023 | Shared | 0 |
| 248 | Opportunity Trends & Pipeline | Users/Jordan Ilyat | 0 |
| 249 | Deal Project Revenue | Shared/Sales | 0 |
| 250 | Invoice Payments | Users/Mark Rittman | 0 |
| 251 | Leads | Shared/Sales | 0 |
| 252 | Company Quarterly Stats Since 2022 | Shared/Analysis | 0 |
| 253 | Campaign Effectiveness | Users/Mark Rittman | 0 |
| 256 | Query Performance Benchmarking | Shared | 0 |
| 257 | Review of 2023 | Shared | 0 |
| 258 | Transactions | Users/Mark Rittman | 0 |
| 259 | Spend | Users/Mark Rittman | 0 |
| 262 | Website Leads | Shared/Sales | 0 |
| 264 | Review of 2023 Final | Shared | 0 |
| 265 | Review | Users/Mark Rittman | 0 |
| 266 | Website Charts Dev | Users/Jordan Ilyat | 0 |
| 269 | Web Analytics (GenAI Demo) | Users/Mark Rittman | 0 |
| 272 | FinTech - Performance Analysis | Users/Lewis Baker | 0 |
| 273 | Web Performance | Shared | 0 |
| 275 | Financial Analysis 2024 | Shared/Analysis | 0 |
| 276 | Competitor Benchmarking | Shared | 0 |
| 277 | Financial Analysis & Benchmarking Examples | Users/Mark Rittman | 0 |
| 278 | Website Visitor Analysis | Shared | 0 |
| 280 | Home Assistant | Users/Mark Rittman | 0 |
| 282 | Performance Stats | Shared | 0 |
| 283 | Monthly Performance Metrics | Users/Mark Rittman | 0 |
| 284 | GenAI Monthly Performance Summary | Users/Mark Rittman | 0 |
| 288 | Deal Pipeline Analysis | Users/Mark Rittman | 0 |
| 290 | Pipeline Narrative | Shared | 0 |
| 291 | Business Summary 2024 | Users/Lydia Blackley | 0 |
| 292 | Consultant Attribution | Users/Lydia Blackley | 0 |
| 293 | Pipeline Narrative | Users/Lydia Blackley | 0 |
| 294 | Transaction Analysis Dashboard | Users/Lydia Blackley | 0 |
| 295 | Sales Performance | Users/Lewis Baker | 0 |
| 296 | test2 | Users/Jordan Ilyat | 0 |
| 297 | test | Users/Bailey Sharp-Ledger | 0 |
| 299 | Monthly Project Status Report | Shared | 0 |
| 301 | New Dashboard | Users/Lydia Blackley | 0 |
| 302 | Total Cost of Ownership | Users/John Haynes | 0 |
| 303 | Revenue and Resource Need Forecast | Shared | 0 |
| 306 | Fathom Meeting Analytics | Shared | 0 |
| 307 | Business Summary 2024 - Jordan Dev | Users/Jordan Ilyat | 0 |
| 308 | Years in Numbers | Shared | 0 |
| 309 | SQL and MQL Value Calculations | Shared/Marketing | 0 |
| 310 | Meeting Analytics | Shared | 0 |
| 312 | Dashboard of Highcharts | Shared/Delivery Team Examples | 0 |
| 313 | Staff Revenue & Time Breakdown | Shared | 0 |
| 314 | Project Objectives | Shared/Customer Success | 0 |
| 315 | Marketing Activity | Shared | 0 |
| 320 | Marketing Activity Last 30 Days | Shared | 0 |
| 322 | Conversion & Contact Us Visitor Path | Shared | 0 |
| 323 | LinkedIn Ads | Users/Saverro Suseno | 0 |
| 324 | Mobile Example : Sessions Rolling 7-Days | Shared/Delivery Team Examples | 0 |
| 325 | Financial Review End Q1 2025 | Shared | 0 |
| 326 | Platform KPI Dashboard Example | Shared/Delivery Team Examples | 0 |
| 327 | Financial Revenue Q1 2025 | Shared | 0 |
| 328 | Business Summary | Users/Mark Rittman | 0 |
| 330 | Benchmarking 2025 | Shared | 0 |
| 333 | Mobile Explore Assistant | Shared/Delivery Team Examples | 0 |
| 334 | ICP Analysis 2025 | Shared/Analysis | 0 |
| 336 | Visual Elements | Shared/Delivery Team Examples | 0 |
| 339 | Marketing Attribution | Users/Mark Rittman | 0 |
| 340 | Marketing & Attribution Analysis | Users/Mark Rittman | 0 |
| 341 | Website Event Anomalies | Shared | 0 |
| 342 | Engagement RAG Status Dashboard (copy) | Users/Jordan Ilyat | 0 |
| 343 | Dashboard Headers - Tabbed browsing | Shared/Delivery Team Examples | 0 |
| 344 | Platform Analytics \| Conversion Cycle Framework \| 1. Acquisition | Shared/Delivery Team Examples/Product Analytics Recipes | 0 |
| 345 | Platform Analytics \| Conversion Cycle Framework \| 2. Activation | Shared/Delivery Team Examples/Product Analytics Recipes | 0 |
| 346 | Platform Analytics \| Conversion Cycle Framework \| 3. Retention | Shared/Delivery Team Examples/Product Analytics Recipes | 0 |
| 347 | Platform Analytics \| Conversion Cycle Framework \| 4. Referral | Shared/Delivery Team Examples/Product Analytics Recipes | 0 |
| 348 | Platform Analytics \| Conversion Cycle Framework \| 5. Revenue | Shared/Delivery Team Examples/Product Analytics Recipes | 0 |
| 350 | Resource Planning | Shared | 0 |
| 351 | Embedded Dashboard Test | Shared/Delivery Team Examples | 0 |
| 353 | Customer Lifecycle Dashboard | Users/Mark Rittman | 0 |
| 354 | Profit & Loss Report - Q3 2025 (Jul-Sep) | Users/Mark Rittman | 0 |
| 355 | Website Traffic Analysis - Past 90 Days vs Previous Period | Users/Mark Rittman | 0 |
| 356 | Social Media Commercial Impact Dashboard | Users/Mark Rittman | 0 |
| 357 | Teamtailor Recruitment | Users/Alex Caldwell/Teamtailor | 0 |
| 358 | P&L by Account Category & Subcategory - Multi-Period Analysis | Users/Mark Rittman | 0 |
| 360 | RA - Client Retention & Value Extraction | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 361 | Mark's health data | Users/Timothy Griew | 0 |
| 363 | Time Breakdown | Users/Mark Rittman | 0 |
| 364 | HKM Issue Cycle Times | Shared/Analysis | 0 |
| 367 | Business Summary | Users/Jordan Ilyat | 0 |
| 368 | HKM Example Dashboard | Shared | 0 |
| 369 | HKM Example Retail Dashboard | Shared | 0 |
| 370 | Pipeline at End of Year | Shared | 0 |
| 371 | SoWs This Year | Shared | 0 |
| 373 | Renewals, Churns and Reactivations | Users/Mark Rittman | 0 |
| 383 | Organic Leads Analysis | Users/Mark Rittman | 0 |
| 386 | Consultant KPI Performance Dashboard v3 | Users/Mark Rittman | 0 |
| 387 | Consultant KPI Performance Dashboard v4 | Users/Mark Rittman | 0 |
| 390 | Sales Performance Last 5 Years | Shared | 0 |
| 392 | Client Activity | Shared | 0 |
| 399 | SEO Performance | Shared | 0 |
| 400 | Provider Revenue Dashboard | Shared | 0 |
| 402 | test | Users/Lydia Blackley | 0 |
| 405 | Utilisation & Recognised Attributed Revenue (MTD) | Shared | 0 |
| 91 | Historical Deals, Opportunities and Wins | Shared/Rittman Analytics/Operations | 0 |
| analytics::developer_tooling_claude_code | Claude Code Analytics | LookML Dashboards | 0 |
| analytics::hkm_example_retail_dashboard | HKM Example Retail Dashboard | LookML Dashboards | 0 |
| analytics::hkm_pop_dashboard | HKM Example PoP Dashboard | LookML Dashboards | 0 |
| analytics::hkm_pop_dashboard_custom | HKM Example PoP (Custom) Dashboard | LookML Dashboards | 0 |
| attribution::marketing_attribution | Marketing Attribution | LookML Dashboards | 0 |
| data_report::stories_discussions_overview | Stories & Discussions Overview | LookML Dashboards | 0 |

**Looks dropped (148)**, reason R-1:

| Id | Title | Folder | Runs 90d |
|---|---|---|---|
| 366 | Client Profitability | Shared/Operations | 20 |
| 197 | usage | Users/Mark Rittman | 13 |
| 299 | Customer List | Shared/Customer Success | 13 |
| 425 | Claude and Wire Usage | Shared | 3 |
| 423 | Sprint Burndown Chart | Shared | 2 |
| 426 | Engagement Profitability | Users/Mark Rittman | 2 |
| 429 | Engagement Metrics | Shared | 2 |
| 279 | Medium Blog Performance | Shared/Customer Success/Analysis | 1 |
| 337 | Booked Revenue | Shared/Operations | 1 |
| 382 | Invoices with Date, Due Date and Paid Date | Shared | 1 |
| 389 | 2026 Open Pipeline — Deal Amount and Weighted Value | Users/Mark Rittman | 1 |
| 403 | COM_03 — Revenue by Client (Top Client Concentration) | Users/Mark Rittman | 1 |
| 409 | DEL_04 — On-Time vs Total Project Deliveries | Users/Mark Rittman | 1 |
| 427 | Project Profitability | Shared | 1 |
| 203 | Campaign Effectiveness | Shared/Marketing | 0 |
| 204 | Customer Retention L12M | Shared/Customer Success/Analysis | 0 |
| 208 | Monthly Revenue and Client Concentration | Shared/Customer Success/Analysis | 0 |
| 242 | Team Recruitment and Utilisation Timeline Chart | Shared/Customer Success/Analysis | 0 |
| 245 | 6 Month Avg. Revenue | Users/Toby Sexton | 0 |
| 271 | Airline Delays - By Quartiles | Users/Andras Zimmer | 0 |
| 272 | Airline Delays - Cancellations by State | Users/Andras Zimmer | 0 |
| 273 | Utilization | Shared/Rittman Analytics/Operations | 0 |
| 274 | Project Profitability - Thrive Capital | Shared/Rittman Analytics/Operations | 0 |
| 275 | Invoice History - Thrive Capital | Shared/Rittman Analytics/Operations | 0 |
| 276 | Net Profit after Tax & Dividends | Shared/Rittman Analytics/Operations | 0 |
| 277 | Cumulative Referral Session Page Views from Blog Posts | Shared/Marketing | 0 |
| 278 | Cumulative Referral Session Visitor Value from Blog Posts | Shared/Marketing | 0 |
| 280 | Year on Year Net Profit | Shared/Customer Success/Analysis | 0 |
| 281 | Referrer Source Relative Performance | Shared/Customer Success/Analysis | 0 |
| 282 | Sessions vs. Conversions Bubble | Shared/Customer Success/Analysis | 0 |
| 283 | Referrer Source Conversion Rate | Shared/Customer Success/Analysis | 0 |
| 284 | Historic Visitor Value | Shared/Customer Success/Analysis | 0 |
| 285 | Historic Non-Direct Conversions | Shared/Customer Success/Analysis | 0 |
| 286 | Medium vs. Squarespace on How Rittman Analytics... | Shared/Customer Success/Analysis | 0 |
| 287 | Lifetime Value Histogram | Shared/Customer Success/Analysis | 0 |
| 288 | Forecast Test Report | Shared/Customer Success/Analysis | 0 |
| 289 | Site Traffic Rolling 4-Weekly Avg | Shared/Customer Success/Analysis | 0 |
| 290 | story_point_duration_corr | Users/Lewis Baker | 0 |
| 293 | Sprint Pricing | Shared/Analysis | 0 |
| 296 | Converting Sessions | Shared/Marketing | 0 |
| 297 | Visitor Events | Shared/Marketing | 0 |
| 298 | Page Conversion Rates | Users/Mark Rittman | 0 |
| 301 | Visitors Viewing Pricing Page | Shared/Marketing | 0 |
| 302 | Influencer Status | Shared/Customer Success | 0 |
| 303 | Customer Contacts | Shared/Customer Success | 0 |
| 304 | Column Pyramid Chart | Shared/Delivery Team Examples | 0 |
| 305 | Synchronised axis line chart | Shared/Delivery Team Examples | 0 |
| 306 | Website Leads by Outcome | Shared/Sales | 0 |
| 307 | Leads by Category L12M | Shared/Sales | 0 |
| 309 | Burn Rate Forecasting | Users/Lewis Baker | 0 |
| 310 | Hourly Rate vs Actuals | Users/Lewis Baker | 0 |
| 311 | Story Point vs Hours - Accuracy | Users/Lewis Baker | 0 |
| 312 | Story Point vs Hours - Accuracy by Team Member | Users/Lewis Baker | 0 |
| 313 | Today's Sessions | Users/Mark Rittman | 0 |
| 315 | Ideal Customer Slice-and-Dicer | Shared/Analysis | 0 |
| 316 | session by channel 28 days | Users/Jordan Ilyat | 0 |
| 317 | CAC/LTV By Channel | Users/Lewis Baker | 0 |
| 318 | CAC/LTV By Customer Cohort | Users/Lewis Baker | 0 |
| 319 | First Click By Cannel | Users/Lewis Baker | 0 |
| 320 | First Click by persona | Users/Lewis Baker | 0 |
| 321 | Software Spend Breakdown | Shared/Finance | 0 |
| 323 | Client Decay | Users/Mark Rittman | 0 |
| 325 | Example 1 | Users/Lewis Baker | 0 |
| 327 | Blog Page Effectiveness | Users/Mark Rittman | 0 |
| 328 | Benchmark Analysis | Shared | 0 |
| 329 | Project Costs | Users/Mark Rittman | 0 |
| 330 | Unique Visitors  Chg % | Users/Mark Rittman | 0 |
| 331 | Budget Report 2025 | Users/Mark Rittman | 0 |
| 334 | test | Users/Jordan Ilyat | 0 |
| 335 | Deal Outcomes | Shared | 0 |
| 336 | BSL animation test | Users/Bailey Sharp-Ledger | 0 |
| 338 | Consultant Revenue | Users/Jordan Ilyat | 0 |
| 339 | Total Sessions Tile | Shared/Marketing | 0 |
| 340 | Bounce Rate % | Shared/Marketing | 0 |
| 341 | Total Page Views Tile | Shared/Marketing | 0 |
| 342 | Total Visitors Tile | Shared/Marketing | 0 |
| 343 | Sessions vs Last 30 Days | Shared/Marketing | 0 |
| 344 | Top 20 Landing Page & Session Pageviews | Shared/Marketing | 0 |
| 345 | Traffic by Channel Last 30 Days | Shared/Marketing | 0 |
| 346 | Visitor Journey Starburst Tile | Shared/Marketing | 0 |
| 347 | Visitor Journeys | Shared | 0 |
| 348 | Booked and Forecast Revenue vs. Target CY | Shared | 0 |
| 349 | Profit & Loss Report | Shared | 0 |
| 350 | Sadie P&L report | Users/Sadie Mitchell | 0 |
| 351 | Violin Plot Example | Shared/Delivery Team Examples | 0 |
| 352 | Scatter Quadrant | Shared/Delivery Team Examples | 0 |
| 354 | Rejection Reason Table | Users/Alex Caldwell/Teamtailor | 0 |
| 355 | KPI Tile Current Month Consultant Utilisation % to Target | Shared/Operations | 0 |
| 357 | KPI Tile Current Month Revenue (Forecast+Booked) to Target | Shared/Operations | 0 |
| 358 | KPI Tile Current Month Forecast Retained Earnings to Target % | Shared/Operations | 0 |
| 359 | KPI Chart Expected Monthly (Forecast+Booked) Revenue vs Target for Current Year | Shared/Operations | 0 |
| 360 | KPI Chart Sales Team Revenue Forecast by Month for Duration of Pipeline | Shared/Operations | 0 |
| 361 | KPI Tile Current Month Closed Deal Value to Target | Shared/Operations | 0 |
| 362 | Monthly P&L Comparison - Full View | Users/Mark Rittman | 0 |
| 363 | Quarterly P&L Comparison - Full View | Users/Mark Rittman | 0 |
| 364 | P&L Budget Variance - Actual vs Target | Users/Mark Rittman | 0 |
| 365 | Client Metrics | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 367 | Spend by Month by Cohort | Users/Alex Caldwell/Teamtailor | 0 |
| 368 | Cumulative Revenue by Cohort over First 12 Months | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 369 | First Quarter Revenue by Cohort | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 370 | Cohort Analysis - Average First 3 Months Spend by Quarter | Users/Mark Rittman | 0 |
| 373 | Retention Rate (Decay Curve) | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 374 | Customer Lifetime | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 375 | Converted and Unconverted Clients | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 376 | Vendor Spend by Month (6 Months) | Users/Mark Rittman | 0 |
| 377 | No Revenue in M5 2025 Check | Users/Alex Caldwell/Client Retention & Value Extraction | 0 |
| 378 | Billed Revenue and Hours by Year and Consultant | Shared/Analysis | 0 |
| 379 | Mark's steps and weight over time | Users/Timothy Griew | 0 |
| 380 | Average daily sleep by quarter | Users/Timothy Griew | 0 |
| 381 | Budgeted vs Actual Hourly Rate / Month | Users/Mark Rittman | 0 |
| 383 | Multi-Role Person Analysis | Users/Mark Rittman | 0 |
| 384 | Multi-Role Relationship Analysis | Users/Mark Rittman | 0 |
| 385 | HKM Sprint Stats | Shared | 0 |
| 386 | Revenue 25/26 | Users/Sadie Mitchell | 0 |
| 387 | 2026 YTD — Revenue and Retained Earnings vs Budget | Users/Mark Rittman | 0 |
| 388 | 2026 YTD — Revenue by Consultant vs Target | Users/Mark Rittman | 0 |
| 390 | Deal Segmentation by RFM Segment - Last 2 Years | Users/Mark Rittman | 0 |
| 391 | Bonus Calcs | Users/Saverro Suseno | 0 |
| 392 | Consultant Economics | Users/Mark Rittman | 0 |
| 393 | Invoicing Stats | Users/Mark Rittman | 0 |
| 394 | Sales Statistics | Users/Mark Rittman | 0 |
| 395 | Payments | Users/Mark Rittman | 0 |
| 396 | FIN_01 — Monthly Revenue vs Plan | Users/Mark Rittman | 0 |
| 397 | FIN_02 — Retained Earnings vs Budget | Users/Mark Rittman | 0 |
| 398 | FIN_03 — Invoiced Revenue vs Payments Received | Users/Mark Rittman | 0 |
| 399 | FIN_04 — Bank Balance vs Monthly Operating Costs | Users/Mark Rittman | 0 |
| 400 | FIN_05 — Monthly Recognised Revenue (12-Month Run Rate) | Users/Mark Rittman | 0 |
| 401 | COM_01 — Closed Won Revenue vs Target | Users/Mark Rittman | 0 |
| 402 | COM_02 — New Business Deals at Proposal Stage+ | Users/Mark Rittman | 0 |
| 404 | COM_04 — Open Deal Pipeline Activity by Month | Users/Mark Rittman | 0 |
| 405 | COM_05 — Closed Won Deals vs Total Deals at Proposal Stage | Users/Mark Rittman | 0 |
| 406 | DEL_01 — Billable vs Total Timesheet Hours | Users/Mark Rittman | 0 |
| 407 | DEL_02 — Cost of Delivery vs Revenue | Users/Mark Rittman | 0 |
| 408 | DEL_03 — Engagements by Overall RAG Status | Users/Mark Rittman | 0 |
| 410 | DEL_05 — Delivery Team Revenue vs Target | Users/Mark Rittman | 0 |
| 411 | PPL_01 — Billable Headcount by Month | Users/Mark Rittman | 0 |
| 412 | PPL_02 — Non-Billable vs Total Timesheet Hours (Bench Days) | Users/Mark Rittman | 0 |
| 413 | PPL_03 — Attributed Revenue by Consultant (Wire Adoption Proxy) | Users/Mark Rittman | 0 |
| 414 | MKT_01 — Organic Sessions by Month | Users/Mark Rittman | 0 |
| 415 | MKT_03 — Content Items Published (First Session by Referrer Article) | Users/Mark Rittman | 0 |
| 416 | MKT_04 — Average NPS Score by Month | Users/Mark Rittman | 0 |
| 417 | On-Time Project Delivery by Company 2025-2026 | Users/Mark Rittman | 0 |
| 418 | HubSpot Deals Pipeline — Customer, Revenue, Duration, Sprints & Likelihood | Users/Mark Rittman | 0 |
| 419 | HubSpot Open Deals — Revenue, Duration, Sprints & Likelihood Score | Users/Mark Rittman | 0 |
| 420 | Team Weekly Availability — Hours Booked vs Capacity | Users/Mark Rittman | 0 |
| 421 | Team Forecast Availability — Weekly Hours Booked by Engagement | Users/Mark Rittman | 0 |
| 422 | Bonus Calc | Users/Saverro Suseno | 0 |
| 424 | Staff Engagement | Users/Mark Rittman | 0 |

**Schedules dropped (5)** and **alerts dropped (2)**, reason R-1:

| Kind | Id | Title | Target |
|---|---|---|---|
| schedule | 32 | usage | look:197 |
| schedule | 60 | Sprint Schedule & Revenue Pipeline | dashboard:117 |
| schedule | 72 | Sales & Marketing Dashboard | dashboard:193 |
| schedule | 81 | Customer List | look:299 |
| schedule | 100 | Pleo Monthly RAG Status Dashboard | dashboard:311 |
| alert | 1 | alert on element 324 | element:324 |
| alert | 2 | @Mike Calleja  Rixo Load Errors | element:830 |

**Tiles on the three dashboards not migrated programmatically**:

| Dashboard | Element | Kind | Reason |
|---|---|---|---|
| 267 | 2520 | text element 2520 | text tile, recreate by hand |
| 267 | 3879 | filter element 3879 | filter element, becomes a dashboard control |
| 267 | 3880 | filter element 3880 | filter element, becomes a dashboard control |
| 267 | 3883 | filter element 3883 | filter element, becomes a dashboard control |
| 267 | 3884 | filter element 3884 | filter element, becomes a dashboard control |
| 255 | 2426 | text element 2426 | text tile, recreate by hand |
| 255 | 2427 | text element 2427 | text tile, recreate by hand |
| 255 | 2428 | text element 2428 | text tile, recreate by hand |

**Explores not carried (24)**, reason `no in-scope content references it`:

`coding_agent_prompts_fact`, `company_comparison`, `contact_utilization_fact`, `cumulative_churned_clients`, `dbt_slack`, `engagement_context_attribution`, `engagement_renewal_analysis`, `fathom_meetings`, `icp_lookalike_audience_uk_ie_eu_only`, `kpi_scorecard`, `looker_usage_stats`, `marketing_email_sends`, `monzo_bank_transactions_enriched`, `page_keyword_performance`, `page_report`, `people`, `persons_dim`, `project_attribution`, `site_report_by_site`, `src_control_repos_dim`, `staff_weekly_engagement_fact`, `timesheet_project_monthly_forecast_billing_fact`, `timesheet_project_stakeholder_jtbd_fact`, `website_leads`

**Views not carried (117)**, reason `no in-scope content references it`:

`actuals_v_targets`, `ad_performance_snapshot_fact`, `ad_roi_summary_fact`, `ads_dim`, `ads_dim__ad_conversion_specs`, `ads_dim__ad_creative`, `ads_dim__ad_recommendations`, `ads_dim__ad_targeting`, `ads_dim__ad_targeting__geo_locations`, `ads_dim__ad_targeting__geo_locations__cities`, `ads_dim__ad_targeting__geo_locations__regions`, `ads_dim__ad_tracking_specs`, `adsets_dim`, `adsets_dim__adset_targeting`, `adsets_dim__adset_targeting__geo_locations`, `adsets_dim__adset_targeting__geo_locations__cities`, `adsets_dim__adset_targeting__geo_locations__regions`, `anomaly_detection`, `attribution_fact`, `certification_progress`, `coding_agent_commands_dim`, `coding_agent_prompts_fact`, `companies_dim__all_company_addresses`, `companies_dim_ideal_customer`, `company_comparison`, `company_hubspot_id`, `consultant_revenue_attribution`, `consulting_companies`, `contact_bio`, `contact_deals_fact`, `contact_engagements_fact`, `contact_meetings_fact__all_attendee_person_pk`, `contact_meetings_fact__all_company_pk`, `contact_nps_survey_fact`, `contact_utilization_fact`, `contacts_influencer_list_xa`, `contacts_segments_xa`, `contacts_web_event_history_xa`, `contacts_web_interests_xa`, `content_performance`, `cumulative_churned_clients`, `currency_dim`, `date_spine_dim`, `dates`, `dbt_slack`, `dbt_slack__slack_channels`, `delivery_project_cycle_times`, `delivery_project_cycle_times_hkm`, `delivery_team_fact_xa`, `dim_countries`, `dim_dates`, `dim_providers`, `dynamic_monthly_stats`, `dynamic_web_stats`, `email_contacts_dim`, `email_lists_dim`, `email_send_outcomes_fact`, `email_sends_dim`, `employee_pto`, `engagement_context_attribution`, `engagement_renewal_analysis`, `fathom_meeting_actions`, `fathom_meetings`, `fct_boost_transactions`, `ga_multi_cycle_multi_touch_attribution`, `gcp_billing_fact`, `hr_survey_results_fact`, `icp_lookalike_audience_uk_ie_eu_only`, `ideal_customer_2025`, `ideal_customers`, `journals_fact`, `keyword_page_report`, `kpi_scorecard`, `linkedin_company_pages`, `looker_usage_fact`, `looker_usage_stats`, `marketing_content_dim`, `marketing_interactions_fact`, `monthly_performance_fact`, `monzo_bank_transactions_enriched`, `page_keyword_performance`, `page_report`, `performance_narrative_fact`, `persons_dim__all_addresses`, `persons_dim__all_emails`, `persons_dim__current_roles`, `pipeline_history`, `pl_reports`, `podcast_transcriptions`, `product_usage_fact`, `products_dim`, `profit_and_loss_demo_fact`, `profit_and_loss_report_account_group`, `project_attribution`, `project_metrics`, `recruiting_application_stages_dim`, `recruiting_job_applications_fact`, `recruiting_jobs_dim`, `revenue_attribution`, `sales_funnel_xa`, `site_report_by_page`, `site_report_by_site`, `src_control_commits_fact`, `src_control_issues_fact`, `staff_daily_engagement_fact`, `staff_dim`, `staff_event_timeline_fact`, `staff_weekly_engagement_fact`, `timesheet_project_engagement_progress_fact`, `timesheet_project_engagement_progress_fact__deliverables`, `timesheet_project_engagement_progress_fact__objectives`, `timesheet_project_monthly_forecast_billing_fact`, `timesheets_forecast_fact`, `transactions_fact`, `users_dim`, `website_leads`, `workstations_dim`

## Reference key

| Code | Meaning | Defined in |
|---|---|---|
| R-1 | scope ruling: three dashboards and what they need; everything else dropped | .wire/releases/01-looker-to-omni/decisions.md |
| R-2 | profile looker_to_omni | .wire/releases/01-looker-to-omni/decisions.md |
| R-3 | tier 1 is the three dashboards; parity scope all their tiles | .wire/releases/01-looker-to-omni/decisions.md |
| R-4 | parallel run 14 days | .wire/releases/01-looker-to-omni/decisions.md |
| PD-1 to PD-11 | parked decisions awaiting the director | .wire/releases/01-looker-to-omni/status.md parked_decisions |
| b01 | permissions batch (groups, access grant, user attributes) | this document, Batches |
| b02 | Engagement health topics (feeds dashboard 416) | this document, Batches |
| b03 | Web analytics and marketing topics (feeds dashboard 255) | this document, Batches |
| b04 | Targets, forecast and financials topics (feeds dashboard 267) | this document, Batches |
| b05 | Companies core, NPS and delivery-team topics (feeds dashboard 267) | this document, Batches |
| b06 | Business operations views, part 1 (companies_dim joins) | this document, Batches |
| b07 | Business operations views, part 2, and the companies_dim topic | this document, Batches |
| c01 | content batch: dashboard 267 Business Summary | this document, Batches |
| c02 | content batch: dashboard 255 Web Performance & Marketing Attribution | this document, Batches |
| c03 | content batch: dashboard 416 Engagement RAG Status 2026 | this document, Batches |
| b001 | baseline id: LookML commit, as-of, tool versions every verdict is measured against | migration/baseline.yaml |
| parity / redesign / drop | ruling per object in bi_migration_batches.csv | specs/migration/bi_migration_plan/generate.md Step 5 |
| redesign in Omni / defer / drop | disposition of an in-scope redesign model row | specs/migration/bi_migration_plan/generate.md Step 4 |
| mechanical / assisted / redesign | translation class from the audit | bi_pairs/looker_to_omni/translation_guide.md |
| Runs 90d | System Activity dashboard runs in the 90 days to the audit date | audit/looker_audit.md, Usage distribution |

## Validation

Run 2026-09-06 by `/wire:bi-migration-plan-validate`. Result: **PASS**.

| Check | Result | Gaps | Note |
|---|---|---|---|
| Plan sections and batches columns | PASS | 0 |  |
| 1 Every content object is placed exactly once | PASS | 0 |  |
| 2 Every in-scope model object is placed exactly once; not-carried views have a reason | PASS | 0 |  |
| 3 Every drop has a reason | PASS | 0 |  |
| 4 Content batches depend on the right model batch | PASS | 0 |  |
| 5 Model batch order respects view dependencies | PASS | 0 |  |
| 6 Register rows match scope | PASS | 0 |  |
| 7 Every ruling is made or parked | PASS | 0 |  |
| 8 PDT dispositions | PASS | 0 |  |
| 9 Reference key | PASS | 0 |  |

### Gaps to address

- none

## Review

**Reviewed by**: Mark Rittman (release director; rulings given 2026-09-06 22:40, recorded by the orchestrating session 7bb027f9)
**Review date**: 2026-09-06
**Decision**: approved

### Rulings recorded

| Id | Decision | Reference |
|---|---|---|
| R-6 | Target Omni model is 67716e96-520d-402a-88ad-89f97f9bc2a0 ('ra_data_warehouse 2'); closes PD-1 | decisions.md |
| R-7 | Drop list confirmed: everything not needed by the three dashboards; confirms R-1 | decisions.md |
| R-8 | PDTs: rebuild as Omni query views unless the plan proposes a dbt model; park any unsure (no PDT in scope) | decisions.md |
| R-9 | View naming: keep LookML view names (converter default); closes PD-9 | decisions.md |
| R-10 | Groups and user attributes: carry only what the three dashboards' access needs; closes PD-3 | decisions.md |
| R-11 | Parallel run 14 days; parity every tile on all three dashboards; confirms R-3 and R-4 | decisions.md |
| R-12 | Plan approved; continue with target setup then model batches; stop at the first decision; closes PD-12 | decisions.md |

### Reviewer notes

- Approval was given with PD-2, PD-4, PD-5, PD-6, PD-7, PD-8, PD-10 and PD-11 still open. `status.md` ties each to the step it blocks: PD-4 blocks model batch b03, PD-7 blocks b07, PD-5 and PD-6 block the content batches, PD-8 shapes how needs_human items are closed, PD-2, PD-10 and PD-11 block nothing.
- No change to batches or the register was needed; the plan validate result stands.
- Rulings not covered by the director's message were not inferred. In particular, the `dataset` binding (PD-4) was left open even though the permission ruling makes the attribute itself out of scope.
