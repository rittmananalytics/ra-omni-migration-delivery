# Looker Audit: 01-looker-to-omni

**Release**: 01-looker-to-omni (bi_migration, looker_to_omni)  
**Generated**: 2026-09-06  
**LookML source**: `rittmananalytics/ra_data_warehouse_lookml` at commit `82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e` (branch `master`; Looker production deploys the same commit)  
**Looker instance**: https://rittman.eu.looker.com (API 4.0; usage from System Activity `history` explore)  
**Connection**: `ra_dw_prod`, BigQuery (`bigquery_standard_sql`), project `ra-development`, default dataset `analytics`  
**Scope ruling in force**: R-1 (three dashboards and what they need; everything else is the drop list). The audit records the whole estate; the plan applies the ruling.

## Summary

| Object | Count | Notes |
|---|---|---|
| Views | 190 | 81 table-backed, 41 ephemeral derived tables, 4 PDTs, 1 native derived table, 29 with Liquid in sql_table_name, 3 with Liquid in derived SQL, 31 array-unnest views with no table, 0 extends-only |
| Explores | 39 | all in model `analytics`; 21 hidden |
| Joins | 155 |  |
| Dimensions | 2420 |  |
| Dimension groups | 288 |  |
| Measures | 804 |  |
| Filter-only fields | 4 |  |
| Parameters | 17 |  |
| Sets | 28 |  |
| Fields (dimensions + groups + measures + filters + parameters) | 3533 |  |
| Dashboards | 196 | 24 LookML dashboards, 87 in personal folders |
| Looks | 148 | 84 in personal folders |
| Tiles (dashboard elements) | 1636 | button: 37, extension: 5, filter: 4, text: 162, vis: 1428 |
| Schedules | 6 |  |
| Alerts | 3 | read through the raw API; the typed SDK call fails to deserialise on this instance |
| Folders | 64 | 47 personal |

## Classification breakdown

Model rows by object type and class (`drop` is not used for model rows):

| Object type | mechanical | assisted | redesign | total |
|---|---|---|---|---|
| view | 153 | 0 | 37 | 190 |
| explore | 34 | 5 | 0 | 39 |
| join | 31 | 111 | 13 | 155 |
| dimension | 2337 | 56 | 27 | 2420 |
| dimension_group | 252 | 36 | 0 | 288 |
| measure | 713 | 57 | 34 | 804 |
| filter | 0 | 0 | 4 | 4 |
| parameter | 0 | 0 | 17 | 17 |
| set | 28 | 0 | 0 | 28 |
| **total** | 3548 | 265 | 132 | 3945 |

Model rows by class and complexity (mechanical is Low, assisted is Medium, redesign is High; a view's complexity follows its fields, so a mechanical view with redesign fields is High):

| Class | Low | Medium | High |
|---|---|---|---|
| mechanical | 3513 | 15 | 20 |
| assisted | 0 | 265 | 0 |
| redesign | 0 | 0 | 132 |

Content rows by class (every content row is `mechanical` at audit stage except text tiles, which are `drop`; the plan re-rules):

| Object type | mechanical | drop |
|---|---|---|
| dashboard | 196 | 0 |
| look | 148 | 0 |
| tile | 1474 | 162 |
| schedule | 6 | 0 |
| alert | 3 | 0 |
| folder | 64 | 0 |

## Usage distribution

Source: System Activity `history` explore, `history.dashboard_run_count` per `history.real_dash_id`, window `history.created_date` = 90 days ending 2026-09-06; `last_viewed` = `history.most_recent_query_date` over all history. Looks use `history.count` per `look.id`. A dashboard or Look with no history row is recorded as `never` / 0.

| Measure | Value |
|---|---|
| Dashboard runs in the last 90 days (all dashboards) | 1016 |
| Dashboards with at least one run in 90 days | 37 |
| Dashboards carrying 80% of runs | 3 of 196 |
| Dashboards with zero runs in 90 days | 159 |
| Dashboards with usage unknown | 0 |
| Look runs in the last 90 days (all Looks) | 62 |
| Looks with zero runs in 90 days | 134 |

Top 25 dashboards by runs in 90 days (the three in-scope dashboards are marked):

| Rank | Id | Title | Folder | Runs 90d | Last viewed | In scope |
|---|---|---|---|---|---|---|
| 1 | 267 | Business Summary | Shared | 488 | 2026-09-06 | yes |
| 2 | 415 | Project Profitability | Users/Mark Rittman | 234 | 2026-08-28 |  |
| 3 | 389 | Utilisation & Recognised Attributed Revenue | Shared | 102 | 2026-09-04 |  |
| 4 | 311 | Engagement RAG Status Dashboard | Shared | 96 | 2026-08-30 |  |
| 5 | 255 | Web Performance & Marketing Attribution | Shared | 18 | 2026-09-06 | yes |
| 6 | 409 | Financial Analytics 2026 | Shared | 11 | 2026-08-26 |  |
| 7 | 411 | Sav's Metrics | Users/Saverro Suseno | 10 | 2026-06-10 |  |
| 8 | 408 | Claude Code & Wire Session Diagnostics | Shared | 5 | 2026-07-21 |  |
| 9 | 271 | Marketing Analytics: Performance Overview | Users/Lewis Baker | 4 | 2026-07-02 |  |
| 10 | 407 | Claude Code Analytics | Users/Mark Rittman | 3 | 2026-08-25 |  |
| 11 | 375 | End of 2025 Review | Shared | 3 | 2026-08-26 |  |
| 12 | 349 | Financial Analytics 2025 | Shared | 3 | 2026-07-30 |  |
| 13 | 87 | Web Traffic | Shared/Rittman Analytics/Operations | 3 | 2026-07-17 |  |
| 14 | 352 | Analytics Examples | Shared/Delivery Team Examples | 2 | 2026-06-25 |  |
| 15 | 229 | Business Summary 2023 | Shared | 2 | 2026-08-26 |  |
| 16 | 142 | Client Concentration | Shared/Customer Success | 2 | 2026-07-30 |  |
| 17 | 305 | Deal Analysis | Shared | 2 | 2026-07-30 |  |
| 18 | 403 | Delivery Performance | Shared | 2 | 2026-09-03 |  |
| 19 | 404 | Delivery Status | Shared | 2 | 2026-08-26 |  |
| 20 | 335 | Google Search Performance | Shared | 2 | 2026-07-30 |  |
| 21 | 181 | Marketing Channel Effectiveness | Shared/Marketing | 2 | 2026-08-19 |  |
| 22 | 132 | RFM Analysis | Shared/Customer Success | 2 | 2026-07-30 |  |
| 23 | 412 | Rapha — Analytics Modernisation: Hours, Cost & Profit (CY2026) | Users/Mark Rittman | 2 | 2026-06-11 |  |
| 24 | 366 | Retail | Shared/Delivery Team Examples | 2 | 2026-06-25 |  |
| 25 | 133 | Revenue Analysis | Shared/Customer Success | 2 | 2026-07-30 |  |

Top 10 Looks by runs in 90 days:

| Id | Title | Folder | Runs 90d | Last viewed | Explore |
|---|---|---|---|---|---|
| 366 | Client Profitability | Shared/Operations | 20 | 2026-08-05 | analytics/companies_dim |
| 299 | Customer List | Shared/Customer Success | 13 | 2026-09-03 | analytics/companies_dim |
| 197 | usage | Users/Mark Rittman | 13 | 2026-09-05 | system__activity/history |
| 425 | Claude and Wire Usage | Shared | 3 | 2026-08-13 | analytics/coding_agent_prompts_fact |
| 429 | Engagement Metrics | Shared | 2 | 2026-08-28 | analytics/companies_dim |
| 426 | Engagement Profitability | Users/Mark Rittman | 2 | 2026-08-19 | analytics/companies_dim |
| 423 | Sprint Burndown Chart | Shared | 2 | 2026-07-30 | analytics/companies_dim |
| 389 | 2026 Open Pipeline — Deal Amount and Weighted Value | Users/Mark Rittman | 1 | 2026-08-25 | analytics/companies_dim |
| 337 | Booked Revenue | Shared/Operations | 1 | 2026-08-05 | analytics/companies_dim |
| 403 | COM_03 — Revenue by Client (Top Client Concentration) | Users/Mark Rittman | 1 | 2026-08-25 | analytics/companies_dim |

## In-scope dashboards (R-1)

The three dashboards named in the director's scope ruling, with what each reaches. Tile counts exclude the dashboard-level filter elements Looker returns as elements of type `filter`.

| Id | Title | Folder | Kind | Updated | Runs 90d | Last viewed | Vis tiles | Text tiles | Filter elements | Merged-result tiles | Tiles with table calcs or custom fields | Custom vis | Explores | Filters |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 267 | Business Summary | Shared | user-defined | 2026-08-29 | 488 | 2026-09-06 | 17 | 1 | 4 | 8 | 13 | 1 | 8 | 4 |
| 416 | Engagement RAG Status 2026 | Shared | LookML `analytics::engagement_health` | 2026-08-28 | 1 | 2026-08-28 | 17 | 0 | 0 | 0 | 0 | 0 | 4 | 3 |
| 255 | Web Performance & Marketing Attribution | Shared | user-defined | 2026-08-30 | 18 | 2026-09-06 | 28 | 3 | 0 | 4 | 23 | 0 | 3 | 8 |

**267 Business Summary**  
Explores: `chart_of_accounts_dim`, `companies_dim`, `contacts`, `monthly_resource_revenue_forecast_fact`, `nps_survey_results_fact`, `project_engagements`, `revenue_and_forecast`, `targets`  
Filters: Selected Measure on `monthly_resource_revenue_forecast_fact.selected_measure` (default `total^_forecast^_revenue^_gbp`); Selected Split on `monthly_resource_revenue_forecast_fact.selected_split` (default `forecast^_type`); Budget Confirmed? on `monthly_resource_revenue_forecast_fact.buyer_confirmed_budget_available`; Spend Agreed? on `monthly_resource_revenue_forecast_fact.spend_agreed_with_buyer`  
Visualisation types: looker_column x5, looker_grid x1, looker_line x4, marketplace_viz_calendar_heatmap::calendar_heatmap-marketplace x1, single_value x6  
Custom visualisations: element 2682 `marketplace_viz_calendar_heatmap::calendar_heatmap-marketplace`  

**416 Engagement RAG Status 2026**  
Explores: `engagement_actions_fact`, `engagement_burn_up_fact`, `engagement_health_fact`, `engagement_sprint_burn_fact`  
Filters: Company Name on `engagement_health_fact.company_name`; Engagement Name on `engagement_health_fact.engagement_name`; Reporting Month on `engagement_health_fact.reporting_month_month` (default `1 months`)  
Visualisation types: looker_column x1, looker_grid x7, looker_line x1, looker_timeline x1, single_value x7  

**255 Web Performance & Marketing Attribution**  
Explores: `ad_campaign_performance_fact`, `organic_posts_dim`, `web_sessions_fact`  
Filters: Session Start Date on `web_sessions_fact.session_start_ts_date` (default `90 day`); Channel on `web_sessions_fact.channel`; Session UTM Source on `web_sessions_fact.session_utm_source`; Channel Category on `web_sessions_fact.channel_category`; Session UTM Medium on `web_sessions_fact.session_utm_medium`; Session UTM Campaign on `web_sessions_fact.session_utm_campaign`; Entrance Page Category on `web_sessions_fact.first_page_category`; Exit Page Category on `web_sessions_fact.last_page_category`  
Visualisation types: looker_bar x4, looker_column x3, looker_grid x4, looker_pie x7, single_value x10  

Model reach of the three dashboards: **15 explores**, **73 views** (base views plus every view those explores join, plus extends bases), **1643 fields**. In that reach: 61 redesign rows and 158 assisted rows. The other 24 explores and 117 views are reached by no in-scope content.

Views reached, by explore:

| Explore | Base view | Hidden | Joins | Join classes | Views reached | Explore-level notes |
|---|---|---|---|---|---|---|
| ad_campaign_performance_fact | ad_campaign_performance_fact | yes | 1 | mechanical: 1 | 2 | hidden: yes |
| chart_of_accounts_dim | chart_of_accounts_dim |  | 4 | assisted: 4 | 5 |  |
| companies_dim | companies_dim |  | 65 | assisted: 45, mechanical: 11, redesign: 9 | 49 |  |
| contacts | contacts_dim | yes | 13 | assisted: 12, mechanical: 1 | 13 | sql_always_where: confirm references resolve on the topic (always_where_sql); hidden: yes |
| engagement_actions_fact | engagement_actions_fact |  | 0 |  | 1 | always_filter: becomes default_filters; date expressions are never mechanical |
| engagement_burn_up_fact | engagement_burn_up_fact |  | 0 |  | 1 |  |
| engagement_health_fact | engagement_health_fact |  | 0 |  | 1 | always_filter: becomes default_filters; date expressions are never mechanical |
| engagement_sprint_burn_fact | engagement_sprint_burn_fact |  | 0 |  | 1 | always_filter: becomes default_filters; date expressions are never mechanical |
| monthly_resource_revenue_forecast_fact | monthly_resource_revenue_forecast_fact | yes | 0 |  | 1 | hidden: yes |
| nps_survey_results_fact | nps_survey_results_fact | yes | 3 | assisted: 1, mechanical: 2 | 4 | hidden: yes |
| organic_posts_dim | organic_posts_dim |  | 1 | assisted: 1 | 2 |  |
| project_engagements | project_engagements | yes | 0 |  | 1 | hidden: yes |
| revenue_and_forecast | revenue_and_forecast | yes | 0 |  | 1 | hidden: yes |
| targets | targets |  | 1 | mechanical: 1 | 2 |  |
| web_sessions_fact | web_sessions_fact |  | 6 | assisted: 2, mechanical: 4 | 7 |  |

## Redesign register

Every `redesign` model row, grouped by construct. `In scope` marks rows inside the three dashboards' model reach. The converter emits nothing for these; the plan rules each one.

**dimension:html** (16 rows, 11 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| dimension | engagement_health_fact | client_status_block | html (Liquid) withheld; the dimension itself is still emitted | views/engagement_health_fact.view.lkml:159 | yes |
| dimension | engagement_health_fact | commercial_status_block | html (Liquid) withheld; the dimension itself is still emitted | views/engagement_health_fact.view.lkml:149 | yes |
| dimension | engagement_health_fact | delivery_status_block | html (Liquid) withheld; the dimension itself is still emitted | views/engagement_health_fact.view.lkml:139 | yes |
| dimension | engagement_health_fact | overall_status_block | html (Liquid) withheld; the dimension itself is still emitted | views/engagement_health_fact.view.lkml:169 | yes |
| dimension | kpi_scorecard | kpi_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/kpi_scorecard.view.lkml:190 |  |
| dimension | performance_narrative_fact | overall_summary | html (Liquid) withheld; the dimension itself is still emitted | views/performance_narrative_fact.view.lkml:34 |  |
| dimension | staff_event_timeline_fact | event_source | html (Liquid) withheld; the dimension itself is still emitted | views/staff_event_timeline_fact.view.lkml:72 |  |
| dimension | staff_event_timeline_fact | event_url | html (Liquid) withheld; the dimension itself is still emitted | views/staff_event_timeline_fact.view.lkml:116 |  |
| dimension | staff_weekly_engagement_fact | activity_score_band | html (Liquid) withheld; the dimension itself is still emitted | views/staff_weekly_engagement_fact.view.lkml:320 |  |
| dimension | timesheet_project_engagement_rag_status_fact | data_quality_qa_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:123 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | financials_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:79 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | overall_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:21 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | resourcing_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:57 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | schedule_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:137 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | scope_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:101 | yes |
| dimension | timesheet_project_engagement_rag_status_fact | technology_rag_status | html (Liquid) withheld; the dimension itself is still emitted | views/timesheet_project_engagement_rag_status_fact.view.lkml:170 | yes |

**dimension:liquid** (9 rows, 2 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| dimension | ad_roi_summary_fact | group_a_yesno | Liquid in sql or label: templated filter or dashboard control | views/ad_roi_summary_fact.view.lkml:662 |  |
| dimension | ad_roi_summary_fact | group_b_yesno | Liquid in sql or label: templated filter or dashboard control | views/ad_roi_summary_fact.view.lkml:688 |  |
| dimension | ad_roi_summary_fact | timeframe_duration | Liquid in sql or label: templated filter or dashboard control | views/ad_roi_summary_fact.view.lkml:677 |  |
| dimension | anomaly_detection | is_metric_anomalous | Liquid in sql or label: templated filter or dashboard control | views/anomaly_detection.view.lkml:261 |  |
| dimension | companies_dim_ideal_customer | ideal_customer_x_group | Liquid in sql or label: templated filter or dashboard control | views/companies_dim_ideal_customer.view.lkml:99 |  |
| dimension | companies_dim_ideal_customer | ideal_customer_y_group | Liquid in sql or label: templated filter or dashboard control | views/companies_dim_ideal_customer.view.lkml:132 |  |
| dimension | fct_boost_transactions | is_current_period | Liquid in sql or label: templated filter or dashboard control | views/booksy_demo.view.lkml:112 |  |
| dimension | monthly_resource_revenue_forecast_fact | dynamic_split | Liquid in sql or label: templated filter or dashboard control | views/monthly_resource_revenue_forecast_fact.view.lkml:80 | yes |
| dimension | web_sessions_fact | period | Liquid in sql or label: templated filter or dashboard control | views/web_sessions_fact.view.lkml:46 | yes |

**dimension:location** (2 rows, 2 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| dimension | ips_enriched | ip_location | type: location has no Omni equivalent | views/ips_enriched.view.lkml:61 | yes |
| dimension | web_events_fact | map_location | type: location has no Omni equivalent | views/web_events_fact.view.lkml:93 | yes |

**filter_field** (4 rows, 1 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| filter | ad_roi_summary_fact | timeframe_a | filter-only field: becomes a dashboard filter control or templated filter | views/ad_roi_summary_fact.view.lkml:652 |  |
| filter | dynamic_web_stats | channel_filter | filter-only field: becomes a dashboard filter control or templated filter | views/dynamic_web_stat.view.lkml:88 |  |
| filter | fct_boost_transactions | current_period_filter | filter-only field: becomes a dashboard filter control or templated filter | views/booksy_demo.view.lkml:107 |  |
| filter | web_sessions_fact | date_filter | filter-only field: becomes a dashboard filter control or templated filter | views/web_sessions_fact.view.lkml:38 | yes |

**join:one_to_many:left_outer** (13 rows, 9 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| join | companies_dim__all_company_ids | companies_dim__all_company_ids | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:737 | yes |
| join | engagement_details__deliverables | engagement_details__deliverables | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:607 | yes |
| join | engagement_details__objectives | engagement_details__objectives | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:602 | yes |
| join | timesheet_project_engagement_rag_status_fact__client_action_points | timesheet_project_engagement_rag_status_fact__client_action_points | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:634 | yes |
| join | timesheet_project_engagement_rag_status_fact__month_timeline_events | timesheet_project_engagement_rag_status_fact__month_timeline_events | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:624 | yes |
| join | timesheet_project_engagement_rag_status_fact__ra_action_points | timesheet_project_engagement_rag_status_fact__ra_action_points | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:629 | yes |
| join | timesheet_project_engagements_dim__projects | timesheet_project_engagements_dim__projects | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:575 | yes |
| join | timesheet_project_stakeholder_jtbd_fact__identified_jtbds | timesheet_project_stakeholder_jtbd_fact__identified_jtbds | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:670 | yes |
| join | timesheet_project_stakeholder_jtbd_fact__keywords | timesheet_project_stakeholder_jtbd_fact__keywords | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:665 | yes |
| join | dbt_slack__slack_channels | dbt_slack__slack_channels | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | views/dbt_slack.view.lkml:5 |  |
| join | contact_meetings_fact__all_attendee_person_pk | contact_meetings_fact__all_attendee_person_pk | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | models/analytics.model.lkml:334 |  |
| join | timesheet_project_stakeholder_jtbd_fact__identified_jtbds | timesheet_project_stakeholder_jtbd_fact__identified_jtbds | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | views/timesheet_project_stakeholder_jtbd_fact.view.lkml:9 |  |
| join | timesheet_project_stakeholder_jtbd_fact__keywords | timesheet_project_stakeholder_jtbd_fact__keywords | join without sql_on (custom sql join, e.g. LEFT JOIN UNNEST): no Omni relationship form | views/timesheet_project_stakeholder_jtbd_fact.view.lkml:4 |  |

**measure:average** (5 rows, 0 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| measure | anomaly_detection | metric_iqr | Liquid in measure sql or label | views/anomaly_detection.view.lkml:237 |  |
| measure | anomaly_detection | metric_lower_bound | Liquid in measure sql or label | views/anomaly_detection.view.lkml:245 |  |
| measure | anomaly_detection | metric_q1 | Liquid in measure sql or label | views/anomaly_detection.view.lkml:221 |  |
| measure | anomaly_detection | metric_q3 | Liquid in measure sql or label | views/anomaly_detection.view.lkml:229 |  |
| measure | anomaly_detection | metric_upper_bound | Liquid in measure sql or label | views/anomaly_detection.view.lkml:253 |  |

**measure:date** (1 rows, 1 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| measure | timesheets_fact | last_timesheet_billing_date | type: date has no Omni aggregate_type: table calculation on the tile | views/timesheets_fact.view.lkml:68 | yes |

**measure:number** (4 rows, 1 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| measure | ad_roi_summary_fact | ad_metric_choice | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:146 |  |
| measure | ad_roi_summary_fact | ad_metric_choice_2 | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:194 |  |
| measure | companies_dim_ideal_customer | ideal_customer_measure | Liquid in measure sql or label | views/companies_dim_ideal_customer.view.lkml:116 |  |
| measure | monthly_resource_revenue_forecast_fact | dynamic_measure | Liquid in measure sql or label | views/monthly_resource_revenue_forecast_fact.view.lkml:57 | yes |

**measure:period_over_period** (16 rows, 16 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| measure | profit_and_loss_report_fact | cost_of_delivery_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:164 | yes |
| measure | profit_and_loss_report_fact | cost_of_delivery_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:238 | yes |
| measure | profit_and_loss_report_fact | cost_of_delivery_prior_year | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:312 | yes |
| measure | profit_and_loss_report_fact | dividends_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:200 | yes |
| measure | profit_and_loss_report_fact | dividends_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:274 | yes |
| measure | profit_and_loss_report_fact | overheads_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:176 | yes |
| measure | profit_and_loss_report_fact | overheads_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:250 | yes |
| measure | profit_and_loss_report_fact | overheads_prior_year | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:324 | yes |
| measure | profit_and_loss_report_fact | retained_earnings_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:212 | yes |
| measure | profit_and_loss_report_fact | retained_earnings_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:286 | yes |
| measure | profit_and_loss_report_fact | retained_earnings_prior_year | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:336 | yes |
| measure | profit_and_loss_report_fact | revenue_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:152 | yes |
| measure | profit_and_loss_report_fact | revenue_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:226 | yes |
| measure | profit_and_loss_report_fact | revenue_prior_year | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:300 | yes |
| measure | profit_and_loss_report_fact | taxation_prior_month | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:188 | yes |
| measure | profit_and_loss_report_fact | taxation_prior_quarter | measure type 'period_over_period' has no Omni aggregate_type | views/profit_and_loss_report_fact.view.lkml:262 | yes |

**measure:sum** (8 rows, 1 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| measure | actuals_v_targets | actual | Liquid in measure sql or label | views/actuals_v_targets.view.lkml:68 |  |
| measure | actuals_v_targets | target | Liquid in measure sql or label | views/actuals_v_targets.view.lkml:82 |  |
| measure | ad_roi_summary_fact | conversions | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:61 |  |
| measure | ad_roi_summary_fact | first_plan | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:41 |  |
| measure | ad_roi_summary_fact | new_trials | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:80 |  |
| measure | ad_roi_summary_fact | predicted_ltv | Liquid in measure sql or label | views/ad_roi_summary_fact.view.lkml:21 |  |
| measure | anomaly_detection | metric | Liquid in measure sql or label | views/anomaly_detection.view.lkml:213 |  |
| measure | profit_and_loss_report_fact | revenue_dynamic_prior_period | Liquid in measure sql or label | views/profit_and_loss_report_fact.view.lkml:372 | yes |

**parameter** (17 rows, 5 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| parameter | actuals_v_targets | measure_group | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/actuals_v_targets.view.lkml:52 |  |
| parameter | actuals_v_targets | target_group | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/actuals_v_targets.view.lkml:60 |  |
| parameter | ad_roi_summary_fact | ad_metric | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/ad_roi_summary_fact.view.lkml:100 |  |
| parameter | ad_roi_summary_fact | ad_metric_2 | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/ad_roi_summary_fact.view.lkml:123 |  |
| parameter | ad_roi_summary_fact | attribution_model | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/ad_roi_summary_fact.view.lkml:12 |  |
| parameter | anomaly_detection | anomaly_metric | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/anomaly_detection.view.lkml:168 |  |
| parameter | anomaly_detection | lower_bound_multiplier | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/anomaly_detection.view.lkml:195 |  |
| parameter | anomaly_detection | upper_bound_multiplier | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/anomaly_detection.view.lkml:183 |  |
| parameter | companies_dim_ideal_customer | ideal_customer_analysis_measure | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/companies_dim_ideal_customer.view.lkml:88 |  |
| parameter | companies_dim_ideal_customer | ideal_customer_x_slicer | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/companies_dim_ideal_customer.view.lkml:15 |  |
| parameter | companies_dim_ideal_customer | ideal_customer_y_slicer | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/companies_dim_ideal_customer.view.lkml:51 |  |
| parameter | dynamic_web_stats | channel_selector | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/dynamic_web_stat.view.lkml:95 |  |
| parameter | monthly_resource_revenue_forecast_fact | selected_measure | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/monthly_resource_revenue_forecast_fact.view.lkml:7 | yes |
| parameter | monthly_resource_revenue_forecast_fact | selected_split | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/monthly_resource_revenue_forecast_fact.view.lkml:36 | yes |
| parameter | profit_and_loss_report_fact | comparison_period | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/profit_and_loss_report_fact.view.lkml:352 | yes |
| parameter | web_sessions_fact | period_selector | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/web_sessions_fact.view.lkml:24 | yes |
| parameter | web_sessions_fact | time_range | parameter: templated filter (Mustache) or a FIELD_SELECTION control | views/web_sessions_fact.view.lkml:129 | yes |

**view:derived_table_liquid** (3 rows, 0 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| view | anomaly_detection |  | Liquid in derived_table sql | views/anomaly_detection.view.lkml:1 |  |
| view | company_hubspot_id |  | Liquid in derived_table sql | views/company_hubspot_id.view.lkml:1 |  |
| view | dynamic_web_stats |  | Liquid in derived_table sql | views/dynamic_web_stat.view.lkml:2 |  |

**view:native_derived_table** (1 rows, 1 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| view | rfm_model |  | native derived table (explore_source): rebuild as Omni query view | views/rfm_model.view.lkml:1 | yes |

**view:pdt** (4 rows, 0 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| view | cumulative_churned_clients |  | PDT (datagroup_trigger): plan rules dbt model or Omni query view | views/cumulative_churned_clients.view.lkml:5 |  |
| view | engagement_renewal_analysis |  | PDT (datagroup_trigger): plan rules dbt model or Omni query view | views/engagement_renewal_analysis.view.lkml:7 |  |
| view | ga_multi_cycle_multi_touch_attribution |  | PDT (persist_for): plan rules dbt model or Omni query view | views/ga_multi_cycle_multi_touch_attribution.view.lkml:1 |  |
| view | page_keyword_performance |  | PDT (persist_for): plan rules dbt model or Omni query view | views/page_keyword_performance.view.lkml:1 |  |

**view:sql_table_name_liquid** (29 rows, 11 in scope)

| Object | View / explore | Field | Reason | Source | In scope |
|---|---|---|---|---|---|
| view | ad_campaign_performance_fact |  | Liquid in sql_table_name | views/ad_campaign_performance_fact.view.lkml:1 | yes |
| view | ad_campaigns_dim |  | Liquid in sql_table_name | views/ad_campaigns_dim.view.lkml:1 | yes |
| view | ad_performance_snapshot_fact |  | Liquid in sql_table_name | views/ad_performance_snapshot_fact.view.lkml:1 |  |
| view | ad_roi_summary_fact |  | Liquid in sql_table_name | views/ad_roi_summary_fact.view.lkml:1 |  |
| view | ads_dim |  | Liquid in sql_table_name | views/ads_dim.view.lkml:1 |  |
| view | adsets_dim |  | Liquid in sql_table_name | views/adsets_dim.view.lkml:1 |  |
| view | attribution_fact |  | Liquid in sql_table_name | views/attribution_fact.view.lkml:1 |  |
| view | companies_dim |  | Liquid in sql_table_name | views/companies_dim.view.lkml:1 | yes |
| view | companies_dim_ideal_customer |  | Liquid in sql_table_name | views/companies_dim_ideal_customer.view.lkml:1 |  |
| view | contact_companies_fact |  | Liquid in sql_table_name | views/contact_companies_fact.view.lkml:1 | yes |
| view | contact_deals_fact |  | Liquid in sql_table_name | views/contact_deals_fact.view.lkml:1 |  |
| view | contacts_influencer_list_xa |  | Liquid in sql_table_name | views/contacts_influencer_list_xa.view.lkml:1 |  |
| view | contacts_segments_xa |  | Liquid in sql_table_name | views/contacts_segments_xa.view.lkml:1 |  |
| view | contacts_web_event_history_xa |  | Liquid in sql_table_name | views/contacts_web_event_history_xa.view.lkml:1 |  |
| view | contacts_web_interests_xa |  | Liquid in sql_table_name | views/contacts_web_interests_xa.view.lkml:1 |  |
| view | currency_dim |  | Liquid in sql_table_name | views/currency_dim.view.lkml:1 |  |
| view | deals_fact |  | Liquid in sql_table_name | views/deals_fact.view.lkml:1 | yes |
| view | delivery_projects_dim |  | Liquid in sql_table_name | views/delivery_projects_dim.view.lkml:1 | yes |
| view | email_lists_dim |  | Liquid in sql_table_name | views/email_lists_dim.view.lkml:1 |  |
| view | email_send_outcomes_fact |  | Liquid in sql_table_name | views/email_send_outcomes_fact.view.lkml:1 |  |
| view | email_sends_dim |  | Liquid in sql_table_name | views/email_sends_dim.view.lkml:1 |  |
| view | invoices_fact |  | Liquid in sql_table_name | views/invoices_fact.view.lkml:1 | yes |
| view | looker_usage_fact |  | Liquid in sql_table_name | views/looker_usage_fact.view.lkml:1 |  |
| view | timesheet_projects_dim |  | Liquid in sql_table_name | views/timesheet_projects_dim.view.lkml:1 | yes |
| view | timesheet_tasks_dim |  | Liquid in sql_table_name | views/timesheet_tasks_dim.view.lkml:1 | yes |
| view | timesheets_fact |  | Liquid in sql_table_name | views/timesheets_fact.view.lkml:1 | yes |
| view | transactions_fact |  | Liquid in sql_table_name | views/transactions_fact.view.lkml:1 |  |
| view | users_dim |  | Liquid in sql_table_name | views/users_dim.view.lkml:1 |  |
| view | web_sessions_fact |  | Liquid in sql_table_name | views/web_sessions_fact.view.lkml:1 | yes |

## Assisted constructs in scope

| Construct | Rows in scope |
|---|---|
| dimension | 49 |
| dimension_group:time | 27 |
| explore | 4 |
| join:many_to_one:inner | 3 |
| join:many_to_one:left_outer | 9 |
| join:one_to_many:inner | 8 |
| join:one_to_many:left_outer | 41 |
| join:one_to_one:inner | 3 |
| join:one_to_one:left_outer | 1 |
| measure:average | 1 |
| measure:average_distinct | 1 |
| measure:count_distinct | 1 |
| measure:number | 7 |
| measure:sum_distinct | 2 |
| measure:untyped | 1 |

## Explore to content map

| Explore | Dashboards | Dashboard ids | Looks | In scope |
|---|---|---|---|---|
| ad_campaign_performance_fact | 1 | 255 | 0 | yes |
| chart_of_accounts_dim | 33 | 143, 144, 169, 178, 184, 190, 192, 193, 194, 197, 201, 215, 225, 229, 246 ... | 16 | yes |
| coding_agent_prompts_fact | 3 | 407, 408, analytics::developer_tooling_claude_code | 1 |  |
| companies_dim | 76 | 91, 112, 117, 132, 133, 136, 142, 143, 145, 171, 172, 177, 178, 184, 185 ... | 59 | yes |
| company_comparison | 2 | 276, 330 | 1 |  |
| contact_utilization_fact | 17 | 159, 178, 184, 190, 192, 194, 201, 225, 229, 257, 291, 307, 328, 367, 386 ... | 1 |  |
| contacts | 12 | 185, 193, 197, 211, 229, 257, 267, 284, 291, 307, 328, 367 | 2 | yes |
| cumulative_churned_clients | 1 | 373 | 0 |  |
| dbt_slack | 0 |  | 0 |  |
| engagement_actions_fact | 2 | 416, analytics::engagement_health | 0 | yes |
| engagement_burn_up_fact | 2 | 416, analytics::engagement_health | 0 | yes |
| engagement_context_attribution | 1 | analytics::engagement_health | 0 |  |
| engagement_health_fact | 2 | 416, analytics::engagement_health | 0 | yes |
| engagement_renewal_analysis | 1 | 373 | 0 |  |
| engagement_sprint_burn_fact | 2 | 416, analytics::engagement_health | 0 | yes |
| fathom_meetings | 1 | 306 | 0 |  |
| icp_lookalike_audience_uk_ie_eu_only | 0 |  | 0 |  |
| kpi_scorecard | 0 |  | 0 |  |
| looker_usage_stats | 1 | 256 | 0 |  |
| marketing_email_sends | 0 |  | 0 |  |
| monthly_resource_revenue_forecast_fact | 7 | 229, 267, 303, 307, 328, 350, 367 | 2 | yes |
| monzo_bank_transactions_enriched | 5 | 291, 331, 349, 367, 409 | 0 |  |
| nps_survey_results_fact | 8 | 267, 291, 307, 308, 311, 328, 342, 367 | 0 | yes |
| organic_posts_dim | 1 | 255 | 0 | yes |
| page_keyword_performance | 0 |  | 0 |  |
| page_report | 1 | 399 | 0 |  |
| people | 2 | 315, 320 | 0 |  |
| persons_dim | 0 |  | 2 |  |
| project_attribution | 10 | 178, 184, 190, 192, 194, 225, 257, 386, 387, 388 | 1 |  |
| project_engagements | 10 | 267, 290, 291, 293, 307, 308, 328, 349, 367, 409 | 0 | yes |
| revenue_and_forecast | 10 | 229, 246, 267, 291, 307, 327, 328, 349, 367, 409 | 4 | yes |
| site_report_by_site | 1 | 212 | 0 |  |
| src_control_repos_dim | 0 |  | 0 |  |
| staff_weekly_engagement_fact | 0 |  | 1 |  |
| targets | 23 | 177, 178, 184, 190, 192, 193, 194, 225, 229, 246, 264, 267, 284, 291, 297 ... | 0 | yes |
| timesheet_project_monthly_forecast_billing_fact | 0 |  | 0 |  |
| timesheet_project_stakeholder_jtbd_fact | 0 |  | 0 |  |
| web_sessions_fact | 47 | 87, 175, 178, 181, 193, 194, 197, 211, 217, 225, 226, 229, 230, 232, 233 ... | 33 | yes |
| website_leads | 11 | 193, 197, 229, 251, 252, 262, 308, 309, 315, 320, 370 | 2 |  |

Content on explores outside the `analytics` model (out of scope; listed so the drop list is complete):

| Model/explore | Dashboards | Looks |
|---|---|---|
| attribution/attribution | 4 | 0 |
| cortex/ap_invoices_headers | 1 | 0 |
| cortex_salesforce/opportunity_pipeline | 1 | 0 |
| data_report/stories | 1 | 0 |
| delivery_analytics/wh_delivery__issues_fact_explore | 3 | 6 |
| ecommerce_demo/attribution_analysis | 1 | 0 |
| ecommerce_demo/marketing_performance | 1 | 0 |
| ecommerce_demo/order_items | 2 | 2 |
| ecommerce_demo/orders | 1 | 0 |
| finance/revenue_attribution | 2 | 0 |
| hifly_looker_training/airlinedelaycauses | 1 | 2 |
| hn_bigquery/hacker_news_all | 1 | 0 |
| hn_firebolt/authors | 1 | 0 |
| hn_firebolt/comments_fact | 2 | 0 |
| hn_firebolt/hacker_news_all | 1 | 0 |
| home_assistant/device_mappings | 1 | 0 |
| kurban_test/tree_census_1995 | 1 | 0 |
| kurban_test/tree_census_2005 | 1 | 0 |
| kurban_test/tree_census_2015 | 1 | 0 |
| looker-gen-ai/wh_transactions_fact | 1 | 0 |
| looker-linkedin-ads/linkedin_ads__creative_report | 1 | 0 |
| marketing_analysis/wh_commerce_attribution_fintech_xa_explore | 1 | 0 |
| marketing_analysis/wh_commerce_attribution_xa_explore | 1 | 2 |
| marketing_analysis/wh_commerce_rfm_segments_explore | 0 | 2 |
| markr/bank_transactions_fact | 2 | 0 |
| marks_health/daily_health_metrics | 1 | 2 |
| model_demo_ra_snowflake/google_search_console | 1 | 0 |
| personal_data_dashboard/application_usage | 1 | 0 |
| personal_data_dashboard/weekly_productivity | 1 | 0 |
| product_events/product_events_fact | 1 | 0 |
| strava_stats/strava_activities | 1 | 0 |
| strava_stats/strava_segments | 1 | 0 |
| system__activity/dashboard_performance | 1 | 0 |
| system__activity/history | 0 | 1 |
| teamtailor_looker/wh_teamtailor_recruitment_fct | 1 | 1 |
| thelook_ecommerce/order_items | 2 | 0 |

## Unresolved references

Model side: 0 rows reference a view the parser could not find in the project.

Content side: 161 dashboard and Look rows reference explores outside the `analytics` model or fields that do not exist in the parsed project. Each carries `reason: references field outside the parsed repo`. In-scope cases:

| Dashboard | Reference | Finding |
|---|---|---|
| 267 | consultant_revenue_attribution.attributed_project_cost_gbp | field exists but its view is not joined to any explore the dashboard queries |
| 267 | consultant_revenue_attribution.attributed_project_revenue_gbp | field exists but its view is not joined to any explore the dashboard queries |
| 267 | deals_fact.total_oppportunity_deal_amount | field not in LookML project |
| 255 | web_sessions_fact.total_web_sessions_pk | field not in LookML project |

## Text and markdown tiles

57 dashboards carry text tiles (162 tiles). Text tiles are `drop` at audit stage and are recreated by hand where the plan carries the dashboard.

| Dashboard | Title | Text tiles | In scope |
|---|---|---|---|
| 255 | Web Performance & Marketing Attribution | 3 | yes |
| 267 | Business Summary | 1 | yes |
| 307 | Business Summary 2024 - Jordan Dev | 7 |  |
| 184 | Business Summary 2023 | 6 |  |
| 190 | Business Summary 2022 v3 (imported 2) | 6 |  |
| 192 | Business Summary 2022 v3 (imported 3) | 6 |  |
| 143 | Review of 2021 | 5 |  |
| 178 | Business Summary 2022 v4 | 5 |  |
| 336 | Visual Elements | 5 |  |
| 194 | Business Summary 2022 v6 | 4 |  |
| 201 | Project Performance | 4 |  |
| 225 | Business Summary 2022 v6 (imported) | 4 |  |
| 229 | Business Summary 2023 | 4 |  |
| 246 | Rittman Analytics Forecast Performance for 2023 | 4 |  |
| 262 | Website Leads | 4 |  |
| 291 | Business Summary 2024 | 4 |  |
| 328 | Business Summary | 4 |  |
| 343 | Dashboard Headers - Tabbed browsing | 4 |  |
| 344 | Platform Analytics \| Conversion Cycle Framework \| 1. Acquisition | 4 |  |
| 361 | Mark's health data | 4 |  |
| 367 | Business Summary | 4 |  |
| 373 | Renewals, Churns and Reactivations | 4 |  |
| analytics::engagement_health | Engagement Health and Commentary | 4 |  |
| 248 | Opportunity Trends & Pipeline | 3 |  |
| 266 | Website Charts Dev | 3 |  |
| 272 | FinTech - Performance Analysis | 3 |  |
| 290 | Pipeline Narrative | 3 |  |
| 293 | Pipeline Narrative | 3 |  |
| 312 | Dashboard of Highcharts | 3 |  |
| 349 | Financial Analytics 2025 | 3 |  |
| 409 | Financial Analytics 2026 | 3 |  |
| 182 | Case Study Ecommerce | 2 |  |
| 193 | Sales Dashboard | 2 |  |
| 276 | Competitor Benchmarking | 2 |  |
| 296 | test2 | 2 |  |
| 299 | Monthly Project Status Report | 2 |  |
| 326 | Platform KPI Dashboard Example | 2 |  |
| 345 | Platform Analytics \| Conversion Cycle Framework \| 2. Activation | 2 |  |
| 346 | Platform Analytics \| Conversion Cycle Framework \| 3. Retention | 2 |  |
| 347 | Platform Analytics \| Conversion Cycle Framework \| 4. Referral | 2 |  |

## Permissions in play

Read for the plan's permission map. Content access on the `Shared` folder (where all three dashboards live) is `view` for group `All Users`. No in-scope explore has an `access_filter`. One access grant is defined in the model.

| Item | Value |
|---|---|
| Groups | All Users (40), Can See Financial Data (3), Can See HR Data (3), ConversionIA Team (0), Embed Shared Group 1 (1), Gemini Default Users (21), Hifly Team (1), Looker CI Users (10), Netsuite Data App (1), Pepkor (0), Pleo External (1), RA Staff (19), Self-Service Explore Users (0), User (11) |
| Users | 39 total, 33 active |
| Access grant `can_view_company_bio` | user attribute `groups`, allowed values Pepkor IT, Google, Brighton SST; applied to `companies_dim.company_description` |
| User attribute `dataset` | default `analytics`; drives `sql_table_name` on 29 views (11 in scope) through Liquid |
| User attributes with group values | can_see_financial_data: [{'group_id': '11', 'value': 'yes'}], can_see_hr_data: [{'group_id': '12', 'value': 'yes'}] |

## Usage source and access gaps

| Item | Status |
|---|---|
| System Activity | accessible; `usage_source: system_activity` |
| Looker API | API 4.0 with `LOOKERSDK_*` credentials (user Mark Rittman); Looker MCP not used |
| Alerts | 3 read through the raw `/alerts/search` endpoint; the typed SDK call fails to deserialise |
| LookML project | snapshot commit `82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e`; Looker production branch `master` at the same commit |
| Dashboards outside the `analytics` model | 36 model/explore combinations, all out of scope |

## Classification notes

- Classification follows `bi_pairs/looker_to_omni/feature_detection.md` and `translation_guide.md`. Two constructs met in this estate are not in the pair's detection table and were classified from the translation guide's rules: measures of `type: period_over_period` (16 rows, no Omni `aggregate_type`; treated as an unsupported measure type) and joins with a custom `sql:` and no `sql_on` (13 rows, all `LEFT JOIN UNNEST` array joins; the guide rules a join without `sql_on` as redesign).
- Joins are classified from the detection table (`one_to_many`, `inner`, `full_outer`, aliased `from:` and `sql_where` are assisted). The translation guide's explore table says the converter emits these mechanically; the audit keeps the stricter class so the plan sees where fan-out and aliasing need a primary-key check.
- A dimension with `html:` is `redesign` for the html only; the dimension itself is emitted. Eleven such rows are in scope (RAG status colour blocks).
- Liquid inside `link:` blocks does not make a field redesign; the link is assisted per the guide.
- Liquid in `group_label`, `view_label` or `description` (a templated label, not templated SQL) is classified `assisted`: the field is a plain column and the label resolves to one literal per view. The detection table's Liquid rule is written for `sql`, `html` and `label`. The `deals_fact` view carries this pattern on 58 fields.
- `object_uri` uses the LookML project name `analytics` for every content row, including the few dashboards that query other models; their `explore_refs` name the real model.

## Reference key

| Code | Meaning | Defined in |
|---|---|---|
| mechanical | the converter emits it with no human entry | bi_pairs/looker_to_omni/translation_guide.md |
| assisted | the converter emits a best effort plus a needs_human entry, or withholds it with a note | bi_pairs/looker_to_omni/translation_guide.md |
| redesign | no emission; the row carries the reason and the plan rules it | bi_pairs/looker_to_omni/translation_guide.md |
| drop | content row not migrated programmatically (text tiles at audit stage) | specs/migration/looker_audit/generate.md |
| Low / Medium / High | complexity: only mechanical tags / any assisted tag / any redesign tag or an unresolved reference | bi_pairs/looker_to_omni/feature_detection.md |
| looker:analytics:view:<name> | object identity used across audit, plan, drift and parity | specs/migration/looker_audit/generate.md Step 6 |
| R-1 | scope ruling: three dashboards and what they need | .wire/releases/01-looker-to-omni/decisions.md |
| views_90d / last_viewed | System Activity dashboard runs in 90 days / most recent query date | this document, Usage distribution |

## Validation

Run 2026-09-06 by `/wire:looker-audit-validate`. Result: **PASS**.

| Check | Result | Gaps | Note |
|---|---|---|---|
| Report sections and catalog columns | PASS | 0 |  |
| 1 Every model row has a class | PASS | 0 |  |
| 2 Complexity consistent with class | PASS | 0 | view rows follow feature_detection.md's view complexity rule (fields decide) |
| 3 Every redesign row has a reason | PASS | 0 |  |
| 4 Feature detection agrees with the class | PASS | 0 | patterns from feature_detection.md plus the translation guide's join-without-sql_on and period_over_period rules; Liquid inside link:, html:, group_label, view_label and description is not a redesign trigger (see Classification notes) |
| 5 Every content row has usage or explicit unknown | PASS | 0 |  |
| 6 Text tiles recorded | PASS | 0 |  |
| 7 Content references resolve to the model (or carry the outside-repo reason) | PASS | 0 |  |
| 8 Counts match status.md | PASS | 0 |  |

### Gaps to address

- none
