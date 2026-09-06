# Test script: Looker to Omni migration under the release director model

**Purpose.** Exercise two Wire 4.0.0 features end to end: the `bi_migration` release type (`bi_pair: looker_to_omni`) and the release director working method (directive in, parked decisions out, orchestrator dispatches the commands).

**Scope under test.** Migrate from the Looker instance at `https://rittman.eu.looker.com` to the Omni instance at `https://rittmananalytics.omniapp.co`: only the LookML explores, views and other objects from `analytics.model.lkml` (repo `rittmananalytics/ra_data_warehouse_lookml`) that are required by three dashboards, plus the dashboards themselves:

| Dashboard | URL |
|---|---|
| Business Summary | https://rittman.eu.looker.com/dashboards/267 |
| Engagement RAG Status 2026 | https://rittman.eu.looker.com/dashboards/416 |
| Web Performance and Marketing Attribution | https://rittman.eu.looker.com/dashboards/255 |

The Omni-side git repo is `rittmananalytics/ra-data-warehouse-omni-target`.

---

## Part A: Prerequisites

Do these once, before opening Claude Code. Steps 4 and 5 need admin access to the Looker and Omni instances.

### 1. Engagement workspace and repos

**This repository (`rittmananalytics/ra-omni-migration-delivery`) is the engagement workspace.** Wire creates its `.wire/` state here, and this is the directory you run Claude Code from:

```bash
git clone https://github.com/rittmananalytics/ra-omni-migration-delivery
cd ra-omni-migration-delivery
```

You do not clone the LookML repo or the Omni target repo by hand. Turn 1 registers both as migration sources, and `/wire:migration-source-refresh` clones each into `.wire/releases/<release>/migration/source_snapshot/` itself; every audit and migration command reads those snapshots and stamps the commit they were taken from (that commit is what drift detection diffs against). The snapshots are gitignored here since they are reproducible from the recorded commit.

The one requirement is that your git credentials can clone both repos from this machine. Test:

```bash
git ls-remote https://github.com/rittmananalytics/ra_data_warehouse_lookml
git ls-remote https://github.com/rittmananalytics/ra-data-warehouse-omni-target
```

(A manual local checkout via `bi_migration.lookml_repo_path` exists as a fallback for repos Wire cannot clone; it is not needed here.)

### 2. Install the Wire preview plugin

In Claude Code, from any directory:

```
/plugin marketplace add rittmananalytics/wire-plugin-preview
/plugin install wire-preview@rittman-analytics-preview
/reload-plugins
```

Confirm with `/wire:help` (any output means the commands are loaded). The preview build you want is `4.0.0-preview+d3a18c5c` or later; `/wire:start` will report the installed version if you want to check it explicitly.

### 3. Install the upstream Omni agent skills

Wire's `omni` skill drives Omni through the official `exploreomni/omni-agent-skills` package (model builder, content builder, query, admin). In Claude Code:

```
/plugin marketplace add exploreomni/omni-agent-skills
/plugin install omni-analytics@omni-analytics
/reload-plugins
```

Do not install the `omni-integrations` sub-plugin; it is for Databricks/Snowflake semantic-view targets, not this migration.

### 4. Looker API credentials

The audit reads dashboards, tiles, filters and usage through the Looker API 4.0.

1. In Looker (`https://rittman.eu.looker.com`): **Admin, Users**, find your user (or a dedicated service user), **Edit**, **API keys**, **New API Key**. Record the client id and client secret.
2. The user needs permission to read content and, for the usage columns, access to the System Activity explores. Without System Activity the audit still runs and writes `unknown` in the usage columns.
3. Export the three variables the specs name, in the shell you launch Claude Code from (add to `~/.zshrc` or a project `.envrc` to persist):

```bash
export LOOKERSDK_BASE_URL="https://rittman.eu.looker.com"
export LOOKERSDK_CLIENT_ID="<client id>"
export LOOKERSDK_CLIENT_SECRET="<client secret>"
```

4. Verify before starting:

```bash
pip install looker-sdk
python3 -c "import looker_sdk; sdk = looker_sdk.init40(); print(sdk.me().display_name)"
```

Your display name printing back means the credentials work. (If your setup uses the Looker MCP server instead, connect it via `claude mcp` and skip the env vars; the audit spec accepts either.)

### 5. Omni CLI, API token and model id

1. Install the Omni CLI. The source is https://github.com/exploreomni/cli; the simplest route is to let Claude Code do it, from any directory:

   ```
   Install the Omni CLI from https://github.com/exploreomni/cli
   ```

   Verify with `omni --version`. Optionally also `npm install -g @omni-co/model-local-editor` for `omni-sync`, useful during `needs_human` work but not required.
2. In Omni (`https://rittmananalytics.omniapp.co`): create an API key from your user/admin settings (API keys). The key needs model write and admin (groups, user attributes) scope, because target setup creates the branch, groups and attributes.
3. Configure a named profile (preferred over per-command flags):

```bash
omni config init
# base URL: https://rittmananalytics.omniapp.co
# token:    <the API key>
omni config show
```

4. Find the shared model's id. The migration writes to one **shared model** (the model attached to the warehouse connection, editable in Omni's IDE), never a workbook model. Two ways to get its UUID:

   **CLI (preferred):**
   ```bash
   omni models list
   ```
   Each row shows the model's id (a UUID) and name. Pick the shared model for the RA warehouse connection. If several models list, cross-check by name in the UI as below.

   **UI:** in `https://rittmananalytics.omniapp.co`, open **Develop** (the model IDE) and select the model. The browser URL contains the id:
   ```
   https://rittmananalytics.omniapp.co/models/<model-uuid>/...
   ```
   The `<model-uuid>` segment is the value the directive needs. A URL of the form `/w/<workbook-id>/...` is a workbook, not the shared model; navigate to the model IDE instead.

   Record it now and substitute it for `<MODEL_ID>` in turn 1. It is the one answer the opening directive cannot derive for you.
5. Verify: `omni models list` returns without an auth error.

### 6. Verification checklist

| Check | Command | Expect |
|---|---|---|
| Plugin loaded | `/wire:help` | Command catalog prints |
| Omni skills loaded | `/plugin` | `omni-analytics` listed as enabled |
| Looker API | the python one-liner above | your name |
| Omni CLI | `omni models list` | model list incl. the target model |
| Repos cloneable | `git ls-remote` both repos | refs print (Wire clones its own snapshots) |

---

## Part B: The script

Type these into Claude Code, from the root of this repo (`ra-omni-migration-delivery`). Turn 1 is deliberately not a slash command: on Claude Code 4.0.0 a directive is the entry point, and the orchestrating session runs `/wire:new` itself, deriving the answers from your words and asking only for what is missing (expect it to ask for the Omni model id if you omit it, and nothing else).

### Turn 1: the opening directive

```
I want to migrate part of our Looker estate to Omni. Set up the engagement and drive it;
I am the release director, park anything that needs a ruling.

Source: the Looker instance at https://rittman.eu.looker.com, LookML in
https://github.com/rittmananalytics/ra_data_warehouse_lookml, model analytics.model.lkml.

Target: the Omni instance at https://rittmananalytics.omniapp.co, model id <MODEL_ID>.
The git-connected Omni model repo is
https://github.com/rittmananalytics/ra-data-warehouse-omni-target.

Scope ruling: migrate only what these three dashboards need, including the dashboards
themselves:
- Business Summary, https://rittman.eu.looker.com/dashboards/267
- Engagement RAG Status 2026, https://rittman.eu.looker.com/dashboards/416
- Web Performance and Marketing Attribution, https://rittman.eu.looker.com/dashboards/255
That means every explore, view and other LookML object they reference from the analytics
model, plus the views those explores join. Everything else in the Looker estate is the
drop list, no exceptions. Tier 1 is these three dashboards; parity scope is all their
tiles; parallel run 14 days.

Register both repos as migration sources, refresh them, run the Looker audit, and bring
me the migration plan with the parked decisions.
```

### Turn 2: rule on the parked decisions

When the plan comes back, it will list parked decisions rather than guesses. Adjust to what it actually parks; the typical set:

```
Rulings:
- Drop list: confirmed, drop everything not needed by the three dashboards.
- PDTs: rebuild as Omni query views unless the plan proposes a dbt model; park any you are unsure about.
- View naming: keep LookML view names (the converter default).
- Groups and user attributes: carry only what the three dashboards' access needs.
- Parallel run: 14 days. Parity: every tile on all three dashboards.
Approve the plan. Continue: target setup, then the model batches. Stop at the first decision.
```

### Turn 3: model batches

After target setup and each model batch report:

```
Approved. Continue to the next batch. Show me each batch's needs_human items with your
proposed resolution before you apply them.
```

### Turn 4: content

```
Model batches approved. Build the three dashboards as Omni documents on the branch, then
run tile parity against a pinned as-of and bring me the equivalency report.
```

### Turn 5: parity

```
Walk me through every tile that is not PASS, with your proposed fix or an
accepted-difference justification. Do not mark anything ACCEPTED_DIFFERENCE without my ruling.
```

### Turn 6: cutover (only when equivalency is green)

```
Ruling: approve cutover. Merge the model branch, publish the documents, recreate
schedules, and record everything in the register and execution log.
```

### At any point

```
/wire:status
/wire:status-sync <release-folder>
I'll drive.          <- takes control back; "you drive" hands it forward again
```

Typing any `/wire:` command yourself mid-flow always works; the orchestrator re-reads state afterwards and continues.

---

## Part C: What to observe (the test assertions)

1. **Directive entry.** Turn 1 alone produces a created engagement (`.wire/` with a `bi_migration` release), registered and refreshed sources, an audit and a plan, without you typing `/wire:new`. The orchestrator asks only for genuinely missing inputs.
2. **Claim.** `status.md` carries `agents.coordinator_session`; a second Claude Code session opened on the same repo offers join or take-over rather than dispatching.
3. **Parked decisions, not guesses.** The plan's rulings section shows your turn 1 scope ruling applied, and open questions parked with their exact question text.
4. **Scope correctness.** The plan's "Model not carried" list contains every view no in-scope dashboard reaches, each with the reason `no in-scope content references it`. Spot-check one view you know only feeds an out-of-scope dashboard.
5. **Record.** `execution_log.md` rows show `Session: orchestrator [id]` (or lane labels) for dispatched work and `typed` for your own commands; a `mode` row appears when you say "I'll drive". On this preview build each row also carries Duration, Tokens and Cost (backfilled after each turn; `n/a` means not measured, never estimated).
6. **Branch discipline.** All model writes land on the branch `omni-target-setup` created; nothing merges before turn 6. The theme JSON `migration/omni_dashboard_theme.json` exists after target setup.
7. **Converter contract.** `needs_human.json` items are resolved by the agent with reference to `bi_pairs/looker_to_omni/omni_patterns.md`; the agent never hand-edits what the converter emitted.
8. **Parity gate.** Cutover is refused until `bi_equivalency` passes on the tier 1 tiles; a non-PASS tile appears in the register with a verdict, not silently dropped.

**Ending the test early:** say `Stop. Park everything and summarise where we are`, then `/wire:status-sync <release-folder>` to confirm the record matches the work done. Nothing has merged to the Omni model or touched Looker, so abandoning the release folder is safe at any point before turn 6.

---

## Part D: Automated harness (headless, no screen driving)

For an unattended mechanics run of turns 1 to 5, feed the same turns to Claude Code headlessly instead of typing them. This tests the flow end to end; it does not test the director's judgment, and cutover stays human by design.

### How it works

`claude -p "<text>"` runs one non-interactive turn in the current directory and prints the result; `claude -p -c "<text>"` continues the same conversation. Each script turn becomes one invocation, gated on the previous turn's output. All Part A prerequisites must already be in place, including credentials, since headless runs cannot mint keys.

### Permissions

Do not use `--dangerously-skip-permissions` against live instances. Use `acceptEdits` plus an explicit allowlist so file writes inside the engagement repo are automatic while anything unexpected fails visibly. This repo ships the allowlist in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git clone:*)", "Bash(git -C lookml:*)", "Bash(git ls-remote:*)",
      "Bash(omni:*)", "Bash(python3:*)", "Bash(date:*)", "Bash(mkdir:*)", "Bash(ls:*)"
    ]
  }
}
```

Trim or extend from the first run's transcript; a denied call shows up in the turn output and tells you what to add.

### Driver skeleton

This repo ships the driver as `harness/run_test.sh` with the Part B turn texts in `harness/turns/turn1.txt` ... `harness/turns/turn5.txt`. Fill `<MODEL_ID>` in `harness/turns/turn1.txt` first, then run `bash harness/run_test.sh` from the repo root. The skeleton, for reference:

```bash
#!/usr/bin/env bash
set -euo pipefail
LOG=harness_run.log

run_turn() {  # run_turn <file> <expect-regex> <max-retries-of-status-poll>
  local file="$1" expect="$2"
  echo "=== $(date -u +%FT%TZ) turn: $file ===" | tee -a "$LOG"
  claude -p -c --permission-mode acceptEdits "$(cat "$file")" | tee -a "$LOG" > last_turn.txt
  if ! grep -qiE "$expect" last_turn.txt; then
    echo "GATE NOT REACHED after $file (expected /$expect/). Stopping for a human." | tee -a "$LOG"
    exit 1
  fi
}

# Turn 1 starts the conversation (no -c)
echo "=== $(date -u +%FT%TZ) turn: harness/turns/turn1.txt ===" | tee -a "$LOG"
claude -p --permission-mode acceptEdits "$(cat harness/turns/turn1.txt)" | tee -a "$LOG" > last_turn.txt
grep -qiE "parked|migration plan" last_turn.txt || { echo "Turn 1 did not reach the plan. Stopping."; exit 1; }

run_turn harness/turns/turn2.txt "target setup|model batch|branch"
run_turn harness/turns/turn3.txt "needs_human|batch .* (ready|complete|validated)"
run_turn harness/turns/turn4.txt "equivalency|parity"
run_turn harness/turns/turn5.txt "PASS|ACCEPTED|not PASS"

echo "Turns 1-5 complete. CUTOVER IS MANUAL: review the equivalency report, then run turn 6 yourself in an interactive session." | tee -a "$LOG"
```

Notes:

- The `expect` regexes are gate heuristics, not contracts. Tune them from your first transcript; a mismatch stops the harness rather than pressing on blind.
- Turn 3 may need to run several times (once per model batch). If the run stops there with more batches pending, re-invoke `run_turn harness/turns/turn3.txt ...` until the output reports the last batch, or loop it on a "remaining batches" marker.
- If the orchestrator parks a decision the canned rulings do not cover, the gate regex fails and the harness stops. That is correct behaviour: rulings belong to a person. Answer it in an interactive session (`claude -c`), then resume the harness at the next turn.
- The record does not care that the run was headless: `execution_log.md` shows the same rows, and the harness transcript in `harness_run.log` pairs with it as the test evidence.

### Verifying afterwards

```bash
claude -p -c "/wire:status"
claude -p -c "/wire:status-sync <release-folder>"
```

Both must reconcile cleanly against the work the harness drove.

### Alternative: a remote session

The same turns can be sent as messages to a Claude Code session on claude.ai/code pointed at the engagement repo (or via the Agent SDK). Same turn texts, same gates, no local terminal; credentials must then live in that environment's setup. Choose this when the run should survive your laptop sleeping.

### Turn 6 (always manual)

Open an interactive session in the engagement directory, satisfy yourself against the equivalency report, and give the cutover ruling from Part B yourself. Do not add it to the harness.
