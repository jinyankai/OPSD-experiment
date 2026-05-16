---
name: survey-reproduction
description: "Project-local workflow for the OPSD self-distillation/on-policy distillation survey and reproduction. Use when updating paper notes, source ledgers, slides, dataset setup, reproduction runbooks, experiment records, or claims about local results."
---

# Survey and Reproduction Workflow

## Use When

- Adding or updating self-distillation / on-policy distillation papers.
- Editing survey notes, taxonomy, comparison matrices, or slide outlines.
- Planning or running OPSD/SFT/GRPO reproduction commands.
- Updating dataset acquisition or experiment logs.
- Answering questions about what has actually been reproduced in this fork.

## Core Rules

1. Read `AGENTS.md` and `docs/agent-harness/project-intent.md` first.
2. Preserve evidence labels exactly:
   - `[Paper claim]`
   - `[Official blog / repo README claim]`
   - `[My reproduced result]`
   - `[My inference]`
3. Never report local reproduction success without a saved command, commit, and output artifact.
4. Keep upstream OPSD code changes narrow and justified by reproduction needs.
5. Update docs when workflows change:
   - paper/source changes: `papers/manifest.md`, `notes/source_ledger.md`;
   - data changes: `reproduction/dataset_download.md`, `scripts/prefetch_datasets.py`;
   - hardware changes: `reproduction/hardware_analysis.md`, `scripts/analyze_hardware.py`;
   - run changes: `reproduction/opsd_runbook.md`;
   - experiment facts: `experiments/`.

## Survey Workflow

1. Prefer local PDFs under `papers/`.
2. Verify current metadata online when the date, code availability, or latest status matters.
3. Write summaries with method, objective, teacher/student/context relation, datasets, results, limitations, and narrative role.
4. Label every factual result with its evidence source.
5. Update `slides/survey_outline.md` when the narrative or slide plan changes.

## Reproduction Workflow

1. Check branch and commit:
   `git -c safe.directory=E:/AlphaLab/OPSD-experiment status --short --branch`
2. Verify dataset availability:
   `python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets`
3. For Hugging Face access, keep the default mirror or override it explicitly:
   `source scripts/hf_mirror_env.sh`
4. On a new server, analyze hardware:
   `python scripts/analyze_hardware.py --output-dir reproduction/hardware_reports`
5. Verify imports/environment before training.
6. Start with smoke tests before full training or evaluation.
7. Record every run using `experiments/experiment_log_template.md`.

## Fast Checks

```powershell
python evals/smoke_eval.py
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile scripts/prefetch_datasets.py scripts/analyze_hardware.py
```

If `bash` is installed:

```powershell
bash -n scripts/hf_mirror_env.sh scripts/run_opsd_1b.sh scripts/run_opsd_4b.sh scripts/run_opsd_4b_nonthink.sh scripts/run_opsd_8b.sh scripts/run_opsd_8b_nonthink.sh scripts/run_sft.sh scripts/run_grpo.sh eval/run_eval.sh eval/run_eval_nonthink.sh
```

For training/eval code changes:

```powershell
python -m py_compile opsd_train.py sft_train.py grpo_train.py eval/evaluate_math.py data_collator.py
```
