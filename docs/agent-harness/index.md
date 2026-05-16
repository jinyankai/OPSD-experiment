# Agent Harness Index

This directory is the system of record for how agents should work in this OPSD survey/reproduction fork.

## Read Order

1. `project-intent.md`: why this repository exists and what success looks like.
2. `architecture.md`: boundaries between upstream code, research notes, reproduction assets, and harness files.
3. `quality.md`: canonical checks and what counts as evidence.
4. `tools.md`: network, Git, Hugging Face, filesystem, and safety rules.
5. `review.md`: self-review and human-review workflow.

## Project Systems of Record

- Source ledger: `notes/source_ledger.md`.
- Paper inventory: `papers/manifest.md`.
- OPSD runbook: `reproduction/opsd_runbook.md`.
- Dataset acquisition: `reproduction/dataset_download.md`.
- Dataset preprocessing decision: `reproduction/dataset_preprocessing.md`.
- Hardware analysis: `reproduction/hardware_analysis.md`.
- Experiment template: `experiments/experiment_log_template.md`.
- Survey deck outline: `slides/survey_outline.md`.

## Maintenance

- Update this directory when a repeated workflow becomes durable policy.
- Keep `AGENTS.md` short and route details here.
- Keep project-specific reusable instructions under `agents/skills/`.
