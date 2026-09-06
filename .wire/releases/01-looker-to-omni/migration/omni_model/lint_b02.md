# Omni Model Lint: batch b02

Run 2026-09-06 by `/wire:omni-model-lint` on `migration/omni_model/b02/` (4 views, 4 topics, 0 relationships). Result: **PASS**.

| Rule | Result | Failures |
|---|---|---|
| L0 parseable | PASS | 0 |
| L1 no ${TABLE} | PASS | 0 |
| L2 no Liquid | PASS | 0 |
| L3 timeframes | PASS | 0 |
| L4 aggregate types | PASS | 0 |
| L5 filter objects | PASS | 0 |
| L9 unique names | PASS | 0 |
| L6 primary keys on joined views | PASS | 0 |
| L8 relationship and join types | PASS | 0 |
| L7 topic views resolve | PASS | 0 |
| L10 redesign items not emitted | PASS | 0 |
| L11 self-reference (beyond the catalogue) | PASS | 0 |

L10 note: the 4 `html` redesign items name dimensions that are emitted without their html, as the translation guide specifies; they are not counted as emitted redesigns.

L11 is not in the spec's catalogue. It catches a converter defect the catalogue does not: a measure (or dimension group) whose LookML `sql` was `${TABLE}.<col>` where `<col>` equals the field's own name is emitted as `sql: ${<col>}`, which Omni reads as a reference to the field itself.

## Failures

| Rule | File | Key | Value | Change |
|---|---|---|---|---|
| - | - | - | - | none |
