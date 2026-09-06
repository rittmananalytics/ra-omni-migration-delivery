---
engagement_name: "ra_looker_to_omni_migration"
client_name: "Rittman Analytics"
created_date: "2026-09-06"
engagement_lead: "Mark Rittman"
repo_mode: "dedicated_delivery"  # combined | dedicated_delivery

# If repo_mode is dedicated_delivery, provide client repo details:
client_repo:
  github_url: "https://github.com/rittmananalytics/ra_data_warehouse_lookml"
  local_path: ".wire/releases/01-looker-to-omni/migration/source_snapshot/lookml"
  default_branch: "master"

docstore:
  provider: null  # confluence | notion | both | null
  confluence:
    space_key: null
    parent_page_url: null
  notion:
    parent_page_url: null

data_model_registry:
  vertical: null
  cross_vertical_schemas: []

# How Wire is driven on this engagement (specs/utils/director_operating_model.md).
orchestration:
  mode: orchestrated  # orchestrated | manual

fathom_sync:
  enabled: false  # internal Rittman Analytics engagement; Fathom Sync refuses to enable on the RA domain
  client_domain: null
  last_synced: null
---

# Engagement Context: ra_looker_to_omni_migration

**Client**: Rittman Analytics
**Engagement Lead**: Mark Rittman
**Created**: 2026-09-06
**Repo mode**: dedicated_delivery

---

## Engagement Overview

Rittman Analytics is moving part of its own reporting layer from Looker (`https://rittman.eu.looker.com`) to Omni (`https://rittmananalytics.omniapp.co`). The warehouse and the dbt layer stay where they are. Only the BI tool changes.

The scope is three dashboards and the LookML they depend on. Everything else in the Looker estate is on the drop list. The release director is Mark Rittman; the orchestrating session runs the Wire commands and parks any decision that needs a ruling.

## Business Objectives

1. Rebuild three Tier 1 dashboards in Omni with tile-level parity to Looker.
2. Carry across only the LookML views, explores and other objects those dashboards need, on a git branch of the shared Omni model.
3. Run Looker and Omni side by side for 14 days, then cut over.

## Key Stakeholders

| Name | Role | Responsibilities | Contact |
|------|------|------------------|---------|
| Mark Rittman | Release director, engagement lead | Rulings, approvals at gates, cutover decision | mark.rittman@rittmananalytics.com |

## Current State Architecture

- **Looker**: `https://rittman.eu.looker.com`, LookML project `ra_data_warehouse_lookml` (GitHub, default branch `master`), model `analytics.model.lkml`.
- **Omni**: `https://rittmananalytics.omniapp.co`, shared model on the `ra_data_warehouse` connection; git-connected model repo `ra-data-warehouse-omni-target` (GitHub, default branch `main`).
- **Warehouse**: unchanged by this migration; confirmed from the LookML connection during the audit.

**Key systems**:
- Looker API 4.0 (dashboards, tiles, filters, usage) via `LOOKERSDK_*` environment variables.
- Omni CLI, named profile `rittmananalytics`.

## Engagement Releases

| # | Release Name | Type | Status | Start | End |
|---|-------------|------|--------|-------|-----|
| 01 | looker-to-omni | bi_migration (looker_to_omni) | In progress | 2026-09-06 | |

## SOW Reference

No Statement of Work. The scope is the release director's directive of 2026-09-06, recorded as rulings R-1 to R-4 in `releases/01-looker-to-omni/decisions.md`. The test script in `docs/looker-to-omni-migration-test-script.md` describes the same scope.

## Working Agreements

- **Operating model**: release director (Mark Rittman) directs; the orchestrating session runs Wire commands and parks decisions.
- **Primary contact**: Mark Rittman.
- **Code review**: Omni model changes land on a branch created by target setup; nothing merges before the cutover ruling.
- **Access provisioning**: Looker API key and Omni CLI profile held locally by the engagement lead.

## Client Repo Details

This engagement uses a dedicated delivery repo. The source and target code repos are separate and are registered as migration sources on the release:

- **LookML source**: https://github.com/rittmananalytics/ra_data_warehouse_lookml (`master`)
- **Omni model target**: https://github.com/rittmananalytics/ra-data-warehouse-omni-target (`main`)

Wire clones both into `releases/01-looker-to-omni/migration/source_snapshot/` with `/wire:migration-source-refresh`; the snapshots are gitignored and reproducible from the recorded commit.

## Notes

- Internal engagement: Fathom Sync is disabled because the client domain is Rittman Analytics' own.
- The repo is on `main`; no feature branch was created for the delivery repo because its README states the `.wire/` record is committed here directly.
