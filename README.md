# RA Looker to Omni migration: delivery repo

Engagement workspace for migrating three dashboards (Business Summary, Engagement RAG Status 2026, Web Performance and Marketing Attribution) and the LookML they depend on from `rittman.eu.looker.com` to `rittmananalytics.omniapp.co`, using the Wire Framework's `bi_migration` release type under the release director model. Wire's `.wire/` engagement state is created and committed in this repo.

## Contents

| Path | What it is |
|---|---|
| `docs/looker-to-omni-migration-test-script.md` | The full test script: prerequisites with install and configuration steps (Part A), the director-mode turns to type (Part B), the test assertions (Part C), and the headless harness (Part D) |
| `harness/run_test.sh` | Headless driver for turns 1 to 5; stops for a human at any unreached gate. Cutover is never automated |
| `harness/turns/turn1.txt` ... `turn5.txt` | The turn texts the driver sends; fill `<MODEL_ID>` in `turn1.txt` before running |
| `.claude/settings.json` | Permission allowlist for headless runs (acceptEdits plus explicit Bash allows; no blanket bypass) |

## Quick start

1. Work through Part A of `docs/looker-to-omni-migration-test-script.md` (plugins, Looker API key, Omni CLI and token, model id). Clone the LookML project into `./lookml` (gitignored).
2. Interactive test: open Claude Code in this directory and type the Part B turns, starting with the turn 1 directive. No `/wire:` command is needed to begin; the directive is the entry point.
3. Automated test: fill `<MODEL_ID>` in `harness/turns/turn1.txt`, then `bash harness/run_test.sh`. Review `harness_run.log` and the `.wire/` record against Part C's assertions.
4. Cutover (turn 6) is always given by a person, interactively, after reviewing the equivalency report.

## Related repos

| Repo | Role |
|---|---|
| `rittmananalytics/ra_data_warehouse_lookml` | Source LookML project (model `analytics.model.lkml`) |
| `rittmananalytics/ra-data-warehouse-omni-target` | Git-connected Omni model repo (migration target) |
| `rittmananalytics/wire-plugin-preview` | Wire preview plugin build under test |
