# Agent Operating Contract

This fork is a research workspace for a self-distillation / on-policy distillation survey and an OPSD reproduction. Keep this file short: it routes agents to the real system of record.

## Start Here

- Read `docs/agent-harness/index.md` before substantial work.
- Read `docs/agent-harness/project-intent.md` before summarizing papers, editing slides, or changing reproduction code.
- Treat `notes/source_ledger.md`, `papers/manifest.md`, `reproduction/opsd_runbook.md`, and `reproduction/dataset_download.md` as canonical project context.
- Preserve upstream OPSD behavior unless the task explicitly asks for a reproduction change.

## Evidence Contract

- Use these labels exactly: `[Paper claim]`, `[Official blog / repo README claim]`, `[My reproduced result]`, `[My inference]`.
- Never report a training or evaluation result as reproduced unless logs or eval outputs were generated in this fork.
- Keep paper claims, README claims, and local results separate in notes, slides, runbooks, and final answers.

## Repository Map

- Upstream OPSD code: `opsd_train.py`, `opsd_trainer.py`, `data_collator.py`, `sft_train.py`, `grpo_train.py`, `eval/`.
- Research layer: `papers/`, `notes/`, `slides/`.
- Reproduction layer: `reproduction/`, `experiments/`, `logs/`, `scripts/prefetch_datasets.py`, `scripts/analyze_hardware.py`.
- Agent harness: `docs/agent-harness/`, `agents/skills/`, `evals/`, `tests/`.

## Canonical Checks

- Harness sanity: `python evals/smoke_eval.py`.
- Baseline tests: `python -m unittest discover -s tests -p "test_*.py"`.
- Script syntax: `python -m py_compile scripts/prefetch_datasets.py scripts/analyze_hardware.py`; run `bash -n` on experiment shell scripts when bash is available.
- Heavy training/evaluation is not a default check; run it only when requested and record commands, hardware, logs, and outputs.

## Review Policy

- Use `docs/agent-harness/review.md` before claiming completion.
- Include changed files, checks run, skipped checks, and residual risk in final answers.
- If a claim depends on the current internet or Hugging Face/GitHub state, verify it before stating it as fact.
