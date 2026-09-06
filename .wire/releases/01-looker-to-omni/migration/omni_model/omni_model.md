# Omni Model: 01-looker-to-omni

Model batches are translated by `scripts/lookml_to_omni.py` (converter 1.1.0) from the LookML snapshot at commit `82b3ab594f0d8f518072f3e1cc4f4ce8ac1d576e` and written to Omni model `67716e96-520d-402a-88ad-89f97f9bc2a0`, branch `wire-01-looker-to-omni` (`13dc8819-655b-4f36-9ccc-04f748c1ba80`). Nothing merges before the cutover ruling.

Working rule for this release (R-15): each batch's needs_human items are shown to the release director with a proposed resolution before any resolution is applied. A batch is written to the branch once the director has seen its items.

## Batch summary

| Batch | Views emitted | Topics emitted | Relationships | needs_human open | needs_human resolved | Lint | On branch | Written |
|---|---|---|---|---|---|---|---|---|
| b02 | 4 | 4 | 0 | 8 (plus 11 lint findings) | 0 | FAIL (L11 x11, see `lint_b02.md`) | no: held for the director's review of the resolutions | 2026-09-06 22:53 (local files only) |

## needs_human (open), batch b02

| Item | View.field | Class | Reason | Proposed resolution | Decision |
|---|---|---|---|---|---|
| nh-b02-01 | engagement_actions_fact (topic) | assisted | `always_filter` reporting_month_month "1 months": no mechanical Omni operator; not emitted | Add `default_filters` on the topic for `engagement_actions_fact.reporting_month[month]` covering the last 1 month, user-removable, exact operator confirmed at validate. Dashboard 416's own Reporting Month filter (default "1 months") also applies, so the topic default is a safety net | awaiting director |
| nh-b02-02 | engagement_health_fact (topic) | assisted | `always_filter` reporting_month_month "12 months"; not emitted | Same form, last 12 months | awaiting director |
| nh-b02-03 | engagement_sprint_burn_fact (topic) | assisted | `always_filter` reporting_month_month "1 months"; not emitted | Same form, last 1 month | awaiting director |
| nh-b02-04 | engagement_health_fact.client_status_block | redesign (html) | html uses Liquid; not emitted; the dimension itself is emitted as `sql: ${client_status}` | Keep as emitted. Recreate the RAG colour as table conditional formatting on the status text in content batch c03 (PD-8 proposal, hand_finish) | awaiting director (PD-8) |
| nh-b02-05 | engagement_health_fact.commercial_status_block | redesign (html) | as above | as above | awaiting director (PD-8) |
| nh-b02-06 | engagement_health_fact.delivery_status_block | redesign (html) | as above | as above | awaiting director (PD-8) |
| nh-b02-07 | engagement_health_fact.overall_status_block | redesign (html) | as above | as above | awaiting director (PD-8) |
| nh-b02-08 | engagement_sprint_burn_fact.sprint_budget_used_pct | assisted | `type: number` measure emitted without aggregate_type | Keep as emitted: `100 * SAFE_DIVIDE(${sprint_hours_to_date}, NULLIF(${sprint_budget_hours}, 0))` is a measure over two measures, which Omni supports. Confirm it resolves at validate, after the L11 fix to the two measures it references | awaiting director |

## Lint findings, batch b02 (`lint_b02.md`)

| Finding | Where | Count | Cause | Proposed resolution |
|---|---|---|---|---|
| L11 self-reference | `engagement_burn_up_fact` measures hours_in_week, cumulative_hours, projected_cumulative_hours, budget_line_hours, budget_hours, weekly_pace_hours; dimension group week_start. `engagement_sprint_burn_fact` measures sprint_budget_hours, sprint_hours_to_date, sprint_hours_in_month, sprint_fee_amount_gbp | 11 | Converter defect: LookML `sql: ${TABLE}.hours_in_week` on a measure named `hours_in_week` (no dimension of that name) becomes `sql: ${hours_in_week}`, which Omni reads as the measure referencing itself. `week_start` group: `${TABLE}.week_start_date` became `${week_start[date]}` | Deterministic post-converter patch (`audit/scripts/patch_converter_output.py`, to be written): where a field's `sql` references only its own name, replace `${name}` with the bare column name from the IR `source_sql` (`hours_in_week`, `week_start_date`). Omni's own auto-generated views use bare column names in `sql:`. Recorded in the batch manifest and re-applied on every converter run; reported to the Wire maintainers as a converter 1.1.0 defect |
| Dimension-group reference without timeframe | `engagement_health_fact.is_current_month`: `sql: ${reporting_month} = DATE_TRUNC(CURRENT_DATE(), MONTH)` | 1 | Same defect: `${TABLE}.reporting_month` became `${reporting_month}`, the dimension group's name | Same patch: bare column `reporting_month` |

## Assisted constructs emitted (for validate to confirm)

| View.field | Construct | Note |
|---|---|---|
| engagement_sprint_burn_fact.sprint_budget_used_pct | measure_number | measure of measures; resolves once L11 is fixed |

## Register

b02's 4 view rows and 4 topic rows stay `pending` until the batch is written to the branch.
