# Migrating from Looker to Omni with the Wire Framework

Three Looker dashboards, and the LookML behind them, move to Omni in six messages typed into Claude Code, one of them repeated once per model batch. The warehouse does not change. The Omni model is built on a branch, every dashboard tile is checked against its Looker original before any user is switched, and every decision is recorded in files inside a git repo.

The run below used the Wire Framework, Rittman Analytics' delivery framework, installed as a Claude Code plugin, against our own Looker estate. The prompts are reproduced as typed. The counts and timings are from the run's execution log.

## Source, target and scope

| | |
|---|---|
| Source | Looker at `rittman.eu.looker.com`; LookML project `ra_data_warehouse_lookml` on GitHub; model `analytics.model.lkml` |
| Target | Omni at `rittmananalytics.omniapp.co`; a git-connected shared model, repo `ra-data-warehouse-omni-target` |
| Warehouse | BigQuery, project `ra-development`, dataset `analytics`. Unchanged. |
| Scope | Three dashboards and every LookML object they reach. Everything else is dropped. |
| Parallel run | 14 days |
| Parity | Every tile on the three dashboards |

The three dashboards:

| Id | Dashboard | Runs in 90 days | Visual tiles | Explores used |
|---|---|---|---|---|
| 267 | Business Summary | 488 | 17 | 8 |
| 416 | Engagement RAG Status 2026 | 1 | 17 | 4 |
| 255 | Web Performance and Marketing Attribution | 18 | 28 | 3 |

The estate is larger. The audit in turn 1 counted 196 dashboards, 148 Looks, 1,636 tiles, 190 views and 39 explores. 3 of the 196 dashboards carry 80 percent of the runs in the last 90 days. 159 have not been opened in that window. Those figures are why the scope is three dashboards and not the estate.

## Before you start

Six things, done once. Steps 4 and 5 need admin access to Looker and Omni.

**1. An engagement repo.** Clone an empty repo (ours is `ra-omni-migration-delivery`) and open Claude Code in it. Wire writes its record under `.wire/` here. Do not clone the LookML or Omni repos by hand. Wire snapshots both itself in turn 1. Check that your git credentials can reach them:

```bash
git ls-remote https://github.com/rittmananalytics/ra_data_warehouse_lookml
git ls-remote https://github.com/rittmananalytics/ra-data-warehouse-omni-target
```

Each command should print lines of commit hashes and branch names.

**2. The Wire plugin.** In Claude Code:

```
/plugin marketplace add rittmananalytics/wire-plugin-preview
/plugin install wire-preview@rittman-analytics-preview
/reload-plugins
```

`/wire:help` prints the command list once the plugin has loaded. The build used here is the 4.0.0 preview.

**3. Omni's agent skills.** Wire drives Omni through Omni's own open-source skills package, which covers the model builder, the content builder, queries and admin:

```
/plugin marketplace add exploreomni/omni-agent-skills
/plugin install omni-analytics@omni-analytics
/reload-plugins
```

**4. Looker API credentials.** Create an API key in Looker under Admin, Users. The user needs to read content and, for the usage figures, to query System Activity. Export three variables in the shell you start Claude Code from:

```bash
export LOOKERSDK_BASE_URL="https://rittman.eu.looker.com"
export LOOKERSDK_CLIENT_ID="<client id>"
export LOOKERSDK_CLIENT_SECRET="<client secret>"
```

Check them:

```bash
python3 -m pip install looker-sdk
python3 -c "import looker_sdk; sdk = looker_sdk.init40(); print(sdk.me().display_name)"
```

**5. Omni CLI, token and model id.** Install the Omni CLI (source: `github.com/exploreomni/cli`), create an API key in Omni with model write and admin scope, and set up a named profile:

```bash
omni config init
omni config show
omni models list
```

The last command lists every model with its id. The id you need is the UUID of the shared model on the warehouse connection. It is not the API key, and it is not a workbook id. In our run the directive carried a string in API-key format by mistake. The session did not guess. It parked the question with the two candidate models listed, and target setup waited on the answer.

**6. Check everything.**

| Check | Command | Expect |
|---|---|---|
| Wire loaded | `/wire:help` | Command list |
| Omni skills loaded | `/plugin` | `omni-analytics` enabled |
| Looker API | The Python one-liner above | Your display name |
| Omni CLI | `omni models list` | The target model in the list |
| Repos reachable | `git ls-remote` on both | Refs print |

## How Wire runs a migration

### The release type

Every Wire engagement has one or more releases, and every release has a release type: a YAML file listing the phases of the work, the artifacts (documents and data files) each phase produces, and the conditions each artifact needs before it can be produced. The release type for this work is `bi_migration`, with the tool pair `looker_to_omni`.

| Phase | Artifact | Commands | Can start when |
|---|---|---|---|
| Audit | `looker_audit` | `/wire:looker-audit-generate`, `-validate`, `-review` | Sources registered and refreshed |
| Plan | `bi_migration_plan` | `/wire:bi-migration-plan-generate`, `-validate`, `-review` | Audit review approved |
| Target setup | `omni_target_setup` | `/wire:omni-target-setup-generate`, `-validate`, `-review` | Plan review approved |
| Model | `omni_model` | `/wire:omni-model-generate`, `-lint`, `-validate`, `-review`, per batch | Target setup review approved |
| Content | `omni_content` | `/wire:omni-content-generate`, `-validate`, then `--write`, per batch | Model validate passed |
| Parity | `bi_equivalency` | `/wire:bi-equivalency-validate`, repeatable | Content batch created |
| Cutover | `cutover` | `/wire:cutover-generate`, `-validate`, `-review` | Every in-scope tile passes parity |

Two optional phases sit either side: business rules discovery before the audit, and training and documentation after cutover. Neither was used here.

Each command takes the release folder name as its argument, for example `/wire:looker-audit-generate 01-looker-to-omni`. Each writes its files under `.wire/releases/01-looker-to-omni/`, updates `status.md` in that folder, and appends one row to `execution_log.md`. The "can start when" column is enforced by the command: run the plan before the audit is approved and it stops and says which condition is unmet.

In Claude Code each `/wire:` command is a skill: a markdown file in the plugin holding the command's full specification, which the session loads and follows step by step. The Omni-side steps inside those specifications call Omni's own skills, installed in step 3, for model YAML, documents, queries and admin.

### The Looker to Omni pair

The translation rules live in one folder of the plugin, `bi_pairs/looker_to_omni/`. Two pieces matter most.

**The translation guide** lists every LookML construct with the Omni construct it becomes and one of three classes:

| Class | What the converter does | What the agent does |
|---|---|---|
| mechanical | Writes the Omni YAML. Nothing to review. | Nothing |
| assisted | Writes a best effort and records a `needs_human` item. Where a wrong translation would change a number, writes nothing and records why. | Confirms or corrects before the batch is validated |
| redesign | Writes nothing. Records the Omni alternative. | Applies the plan's ruling or parks a decision |

Liquid (Looker's templating language), parameters, persistent derived tables (PDTs: tables Looker builds and stores in the warehouse) and `html` blocks are all redesign. There is no automatic translation from Liquid to Mustache, Omni's templating language.

**The converter** is a Python script, `lookml_to_omni.py`, shipped with the plugin. It reads LookML and writes Omni view files, topic files (a topic is Omni's equivalent of an explore: a base view plus its joins) and a relationships file. Same input, same output, no AI call. The agent never hand-writes anything the script can emit, so every emitted field can be regenerated and tested.

Alongside these sit a content mapping (tile types to Omni chart types, dashboard filters to controls), a file of Omni idioms for the constructs the converter refuses, and six worked before-and-after examples that the plugin's tests check on every build.

### Who types the commands

You describe what you want in plain words. A skill in the plugin turns that into command runs, so the commands above are run for you, not typed by you. It activates in any repo with a `.wire/` folder, or when your first message asks to start an engagement.

On every message it re-reads three files before acting: the release's `status.md` (the state of each artifact and the decisions waiting), the release-type YAML (the table above), and `decisions.md` (the rulings on record). From those it works out which artifacts can run now, which are blocked and on what, and which are waiting for a decision.

Then it does four things:

- **Names the commands before running them.** The reply says, for example, "Running `/wire:looker-audit-generate 01-looker-to-omni`", so you learn the command behind each step.
- **Runs them.** Small steps run in the session. A model batch, a content batch or a parity sweep is handed to a specialist agent from the plugin, called a lane, with a written brief: the command to run, the folders it may write, a state file to update after each item, and an instruction to report once, when done, stalled or stuck on a decision. Lanes do not spawn further agents.
- **Writes the record.** Only the orchestrating session writes `status.md` and `execution_log.md`. Lanes write their own artifact files and their own state file. Before the session reports a lane's work as ready, it checks the files exist, checks validate ran and matches the lane's claim, and spot-checks a sample.
- **Parks decisions instead of guessing.** Anything that needs a ruling becomes an entry in `status.md` with the exact question. A review step never runs without your say-so. The first line of every reply is the count of decisions waiting.

Your rulings go into `decisions.md` the moment you give them, numbered R-1, R-2 and so on, with your name, the time and your reason. The plan and every later command read them from the file, not from the conversation, so a ruling survives the session ending.

You can type any `/wire:` command yourself at any point. The session re-reads the files afterwards and carries on. Saying "you drive" hands control back for the rest of the session. Saying "I'll drive", or giving any instruction, hands it forward again. Both are logged.

## The walkthrough

Open Claude Code in the engagement repo. No slash command is needed to begin.

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

The line "I am the release director" tells the session that you decide and it operates. The rest supplies every answer engagement setup would otherwise ask for: source, target, scope, tier, parity scope and the parallel-run window.

What ran, from the execution log:

| Command | Result | Time |
|---|---|---|
| `/wire:new` | Engagement and release `01-looker-to-omni` created | 2m 06s |
| `/wire:migration-source-register`, twice | LookML repo and Omni model repo registered as sources | |
| `/wire:migration-source-refresh`, twice | Both repos cloned into the release's snapshot folder, commit recorded | 39s |
| `/wire:looker-audit-generate` | Audit report, two catalogs, dependency graph | 27m 24s |
| `/wire:looker-audit-validate` | 8 of 8 checks passed | 1m 52s |
| `/wire:bi-migration-plan-generate` | Plan, batches, register with 156 rows, baseline `b001` | 4m 40s |
| `/wire:bi-migration-plan-validate` | 9 of 9 checks passed | 30s |

The whole turn took 46 minutes and cost $25.55 in API usage.

Setup wrote five rulings to `decisions.md`, R-1 to R-5: the scope, the tool pair, tier and parity scope, the parallel run, and the engagement settings it derived from the directive.

The audit read the LookML snapshot and the Looker API. It classified 3,945 model constructs: 3,548 mechanical, 265 assisted, 132 redesign. On the content side it recorded 196 dashboards, 148 Looks, 1,636 tiles, 6 schedules, 3 alerts and 64 folders, with 90-day usage per dashboard from System Activity. The audit does not decide what to migrate. It records what is there and what each thing would cost to move.

For the three in-scope dashboards it recorded what each one reaches:

| Id | Explores | Filters | Merged-result tiles | Tiles with table calculations | Custom visualisations |
|---|---|---|---|---|---|
| 267 | 8 | 4 | 8 | 13 | 1 |
| 416 | 4 | 3 | 0 | 0 | 0 |
| 255 | 3 | 8 | 4 | 23 | 0 |

Merged results, table calculations and custom visualisations are the three things the content step cannot rebuild automatically, so these counts size the hand-finishing work before anything is built.

The plan has a blocking condition: the audit review must be approved. The directive asked for the audit and the plan in one turn, so the session recorded a gate override in `status.md` under the director's name, quoting the directive as the reason, generated the plan, and parked both reviews for a ruling. It said so in its report and offered to hold the gate in later turns if preferred.

### What the plan contains

The plan does five things.

1. **Ranks content by usage.** Tier 1 is the smallest set of dashboards carrying 80 percent of runs. Tier 2 is the rest with any runs. Stale is zero runs in 180 days. Business Summary alone carries 48 percent of all dashboard runs in the window.
2. **Applies rulings, or parks them.** Rulings already in `decisions.md` are applied: parity for tier 1, the drop list, the 14-day parallel run and the all-tiles parity scope. Every other question is parked with its exact wording.
3. **Decides model scope.** Every view and explore any in-scope dashboard references, plus every view those explores join. Here that is 73 views, 15 explores and 1,643 fields. Every other view is listed under "Model not carried" with the reason "no in-scope content references it": 117 views and 24 explores.
4. **Cuts batches.** One permissions batch, six model batches (b02 to b07) in join order, and three content batches, one per dashboard in usage order. Each content batch names the model batch it depends on.
5. **Bootstraps the register and pins the baseline.** One pending row per in-scope object in `migration_register.csv`, 156 rows here. A `baseline.yaml` records the LookML commit, the converter version and the parity as-of instant. Every later parity verdict names this baseline.

One finding from the scope step shaped the parked questions. Business Summary reaches the `companies_dim` explore, which has 65 joins. Carrying every joined view, as the scope ruling says, brings in 49 views the tiles never touch. The tiles use fields from 18 of them.

The turn ended with 12 decisions waiting:

| Id | Question, shortened |
|---|---|
| PD-1 | Confirm the Omni model is `67716e96-520d-402a-88ad-89f97f9bc2a0`, the one git-connected to the target repo. The id in the directive was in API-key format and matched nothing. |
| PD-2 | Approve the Looker audit |
| PD-3 | Permission map: carry the All Users group and one access grant, nothing else? |
| PD-4 | 11 views pick their BigQuery dataset with a user attribute. Bind them to one schema and drop per-user switching? |
| PD-5 | Parameter-driven tiles: rebuild as Omni field-selection controls, or as fixed measures? |
| PD-6 | 12 merged-results tiles: rebuild each as a query view, or split into side-by-side tiles? |
| PD-7 | Keep all 73 joined views, or trim the 65-join explore to the 18 views the tiles use? |
| PD-8 | Confirm the proposed treatment of each redesign construct |
| PD-9 | View naming: 42 of the 73 view names already exist in the target model. Second view per table, or extend the existing ones? |
| PD-10 | Run the optional audit of existing Omni content, or skip? |
| PD-11 | Run the optional business rules phase, or skip? |
| PD-12 | Approve the migration plan |

Nothing was written to Looker or Omni, and nothing was committed to git.

### Turn 2: rule on the plan

```
Rulings:
- Drop list: confirmed, drop everything not needed by the three dashboards.
- PDTs: rebuild as Omni query views unless the plan proposes a dbt model; park any you are unsure about.
- View naming: keep LookML view names (the converter default).
- Groups and user attributes: carry only what the three dashboards' access needs.
- Parallel run: 14 days. Parity: every tile on all three dashboards.
Approve the plan. Continue: target setup, then the model batches. Stop at the first decision.
```

This text answers PD-2, PD-11 and PD-12 and restates the parity and parallel-run rulings. In this run the plan parked nine more questions, PD-1 and PD-3 to PD-10, and those go in the same message, one line each. The model id line, for example:

```
- Omni model (PD-1): 67716e96-520d-402a-88ad-89f97f9bc2a0, the shared model 'ra_data_warehouse 2'.
```

Every ruling is appended to `decisions.md`. The approval runs `/wire:looker-audit-review` and `/wire:bi-migration-plan-review`, both recorded under your name. "Continue" runs the next runnable artifact, `/wire:omni-target-setup-generate 01-looker-to-omni`.

Target setup is the first command that writes to the live Omni instance. Its specification carries a safety notice listing exactly what it writes:

| Action | Detail |
|---|---|
| Verify the connection | The Omni model's connection must read the same BigQuery project and dataset as Looker's. If not, the command stops. |
| Create a model branch | Named `wire-01-looker-to-omni`. Every model write in the release goes here. |
| Refresh the schema | So plain column dimensions resolve on the branch |
| Create groups and user attributes | From the plan's permission map. No users are added to groups. That is a cutover step. |
| Derive a dashboard theme | One JSON file, so every migrated dashboard is styled the same from its first draft |

It never edits the production model, merges a branch, or touches a document. Every write is listed in the output document with the action that reverses it.

Validate runs, then the session stops. Target setup has a review gate, and the directive said "Stop at the first decision".

### Turn 3: model batches

```
Approved. Continue to the next batch. Show me each batch's needs_human items with your
proposed resolution before you apply them.
```

"Approved" runs `/wire:omni-target-setup-review`. Then, per model batch, a lane runs three commands:

```
/wire:omni-model-generate 01-looker-to-omni --batch b01
/wire:omni-model-lint 01-looker-to-omni --batch b01
/wire:omni-model-validate 01-looker-to-omni --batch b01
```

Generate runs the converter over the batch's views and explores. It writes the view files, topic files and relationships to the batch folder and pushes them to the branch through the Omni CLI. Beside them it writes `needs_human.json`: every construct it did not emit, or emitted with a flag, each with its class, the LookML file and line, the reason, and the Omni alternative. Nothing is dropped silently.

A typical item:

```json
{"id": "nh-001", "class": "redesign", "construct": "liquid_in_sql",
 "view": "orders", "field": "region_label",
 "lkml_file": "views/orders.view.lkml", "line": 41,
 "reason": "Liquid template in sql",
 "omni_alternative": "templated filter on the topic, or a groups dimension",
 "status": "open"}
```

The agent works each item in order. A plan ruling that names the view or field resolves it; a PDT ruled to an Omni query view gets hand-written YAML, the one place hand-written YAML is expected. An assisted item that was emitted stays open until validate confirms it. Anything else is resolved from the Omni idioms file or parked for you.

Lint checks three Omni rules before validate spends a CLI call: no `${TABLE}` (Omni maps plain columns by name), a primary key on every view in a relationship (without one, aggregates fan out), and measure filters written as operator objects. Validate runs `omni models validate` on the branch.

Before reporting the batch, the session re-runs the validate itself and reads the open `needs_human` count from the file, not from the lane's summary. The reply lists each open item with a proposed resolution, as the prompt asked. Type the same turn 3 message once per batch. When the last batch is validated, "approved" runs `/wire:omni-model-review`.

### Turn 4: content and parity

```
Model batches approved. Build the three dashboards as Omni documents on the branch, then
run tile parity against a pinned as-of and bring me the equivalency report.
```

Content runs in two steps on purpose. `/wire:omni-content-generate 01-looker-to-omni --batch b0N` writes a plan and touches nothing in Omni. For each dashboard it reads the definition from the Looker API, maps every tile's fields to the emitted Omni views, converts filters to controls, and builds the layout. A tile it cannot rebuild is listed with a reason:

| Reason | Meaning |
|---|---|
| `unmapped_field` | A field is not on the branch. Fixed in the model batch, not here. |
| `unsupported_calc` | A table calculation using `pivot_where`, `offset` or another calculation |
| `liquid` | A text tile with Liquid tokens |
| `custom_vis` | A marketplace visualisation |
| `merged_results` | Two queries merged in Looker |
| `text_tile` | A text tile, recreated by hand |

`/wire:omni-content-validate` checks the plan against the branch. Then the same generate command with `--write` creates the documents through Omni's v2 documents API, in the folder the plan names. It creates new documents only. A title collision with an existing document is parked for you.

Business Summary has 8 merged-result tiles and 1 custom visualisation. Web Performance has 23 tiles with table calculations. Those are the tiles most likely to appear in the skipped list and the hand-finish list.

Then `/wire:bi-equivalency-validate 01-looker-to-omni` runs each tile twice: the Looker tile's saved query through the Looker API, and the Omni tile's query through `omni query run` against the branch. Both sides get a date filter bounded at the pinned as-of, the same row limit and the same timezone. Both are read-only. Results land as CSV pairs under `migration/parity/results/`, and the report is `migration/bi_equivalency_report_1.md`.

Every tile gets an outcome:

| Outcome | Meaning | Counts toward the gate |
|---|---|---|
| PASS | Equal under the tile's contract, or equal within a named tolerance | Yes |
| FAIL | Both sides ran clean and differ | No |
| ACCEPTED_DIFFERENCE | Differs, and a recorded ruling accepts it | Yes |
| BLOCKED | The Looker query failed. A source failure is never a target success. | No |
| INCONCLUSIVE | A side hit the row limit, or both sides were empty | No |
| NOT_RUN | Skipped tile, no contract, or evidence stale after drift | No |

### Turn 5: tiles that are not PASS

```
Walk me through every tile that is not PASS, with your proposed fix or an
accepted-difference justification. Do not mark anything ACCEPTED_DIFFERENCE without my ruling.
```

The reply lists each tile with the differing keys and columns, the likely cause and a proposed fix. A fix goes back to the model batch or the content plan, and the tile is re-run. An accepted difference needs your ruling: it is written to `decisions.md` and to `migration/parity/accepted_differences.yaml` with a named approver, a reason and a date. Only then does the tile's verdict change. An explanation qualifies a fail. It never upgrades one without a ruling.

### Turn 6: cutover

```
Ruling: approve cutover. Merge the model branch, publish the documents, recreate
schedules, and record everything in the register and execution log.
```

`/wire:cutover-generate` stops while any in-scope tile is not passing, and lists the tiles. When it runs, the runbook it writes is about access and content, because the warehouse did not change:

1. Parity gate confirmed from the register.
2. Parallel run: Looker and Omni both live for 14 days. Looker is unchanged.
3. Access switch, group by group, in the plan's order, with a check-in after each.
4. Schedules and alerts recreated against the Omni dashboards. Each Looker original is disabled once its Omni copy has delivered once.
5. Looker set read-only at the end of the parallel run. Nothing deleted.
6. Decommission as a separate, scheduled step: export and archive the LookML repo and content, then remove Looker access.

Merging the model branch on a git-connected model is `omni models commit` and a pull request in the Omni model repo. Rollback is re-enabling Looker access for the affected group.

## At any point

| You type | What happens |
|---|---|
| `/wire:status` | Where the release is, what is blocked, what is waiting |
| `/wire:status-sync 01-looker-to-omni` | Reconciles the record with the files on disk |
| Any `/wire:` command | Runs. The session re-reads state afterwards. |
| `I'll drive` | Control comes back to you for the session |
| `you drive` | Hands it forward again |
| `Stop. Park everything and summarise where we are` | Ends early. Nothing has merged or touched Looker before turn 6. |

## The record

After turn 1 the release folder holds:

```
.wire/
  engagement/context.md
  execution_log.md
  releases/01-looker-to-omni/
    status.md
    decisions.md
    execution_log.md
    audit/
      looker_audit.md
      looker_model_catalog.csv        3,945 rows
      looker_content_catalog.csv      2,053 rows
      dependencies.jsonl
      model_dependencies.jsonl
      scripts/
    migration/
      bi_migration_plan.md
      bi_migration_batches.csv
      migration_register.csv          156 rows
      baseline.yaml
      parity/evidence.csv
      source_snapshot/lookml/         gitignored
      source_snapshot/omni_model/     gitignored
```

Later turns add `migration/omni_target_setup.md`, `omni_dashboard_theme.json`, one folder per model batch under `omni_model/`, one per content batch under `omni_content/`, the parity results and contracts under `parity/`, the equivalency reports and `cutover_runbook.md`.

Two execution log rows from the run, showing the shape:

```
| 2026-09-06 21:58 | /wire:new                   | created  | Release created (type: bi_migration, profile: looker_to_omni); PD-1 parked | Mark Rittman | orchestrator [7bb027f9] | 2m 06s  |
| 2026-09-06 22:26 | /wire:looker-audit-generate | complete | 190 views, 39 explores, 3533 fields, 196 dashboards, 148 Looks              | Mark Rittman | orchestrator [7bb027f9] | 27m 24s |
```

The session column says who ran it: `orchestrator [id]` for dispatched work, `typed` for a command you typed yourself.

## Where a person decides

| Point | Decision |
|---|---|
| Turn 1 | Scope, tier, parity scope, parallel-run window |
| After turn 1 | Approve the audit and the plan; confirm the Omni model id; the plan's own questions: permission map, dataset binding, parameter-driven tiles, merged results, unused joins, redesign treatment, view naming, optional phases |
| After target setup | Approve what was created on the Omni instance |
| Each model batch | Each open `needs_human` item; approve the model when the last batch validates |
| Each content batch | Any title collision; the tile list for any redesigned dashboard |
| Parity | Every accepted difference, by name |
| Cutover | The ruling itself, then the decommission date |
