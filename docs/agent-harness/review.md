# Review Workflow

## Self-Review

Before claiming completion:

- Inspect the diff.
- Check that upstream OPSD code was not changed unintentionally.
- Check that docs and runbooks were updated when workflows changed.
- Run fast canonical checks or explain why they could not run.
- Confirm no paper/README claim was relabeled as `[My reproduced result]`.

## Research Review

For survey or paper-note changes:

- Every factual claim should have a source label.
- Paper summaries should separate method, objective, datasets, results, limitations, and inference.
- Slides should preserve evidence provenance even when wording is concise.
- New papers should be added to `papers/manifest.md` and, if used substantively, `notes/source_ledger.md`.

## Reproduction Review

For code or experiment changes:

- Record commit, command, environment, dataset cache, model path, and hardware.
- Put durable setup changes in `reproduction/`.
- Put per-run facts in `experiments/`.
- Store raw logs in ignored paths and reference them from experiment records.

## Human Review

- Surface tradeoffs, residual risks, skipped checks, and decisions that require judgment.
- Do not hide uncertainty behind confident prose.

## PR Response Loop

- Read comments.
- Map each actionable comment to a change or explicit non-change rationale.
- Re-run affected checks.
