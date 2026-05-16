# Project Intent

## Mission

This repository supports two linked goals:

- Part A: build a 30-minute survey presentation on self-distillation / on-policy distillation for a research-group audience.
- Part B: reproduce and explain the official Self-Distilled Reasoner / OPSD codebase without mixing paper claims, README claims, and local results.

The intended audience has machine-learning background and wants a technical, source-backed view of method evolution, failure modes, and reproduction feasibility.

## Research Narrative

The central story is that OPD-style methods try to combine:

- the relevance of on-policy rollouts, where training states match the student's actual behavior;
- the density of distillation feedback, where a teacher can provide token-level or step-level information;
- the reliability constraints of RLVR, where outcome signals help decide which samples or directions are trustworthy.

Key comparison axes:

- OPCD: context-conditioned teacher distills privileged or reusable context into a context-free student.
- OPSD: the same base model acts as question-only student and privileged-solution teacher.
- SDPO: feedback-conditioned self-teacher converts execution/runtime/text feedback into dense learning signal.
- RLSD/SRPO-style hybrids: combine RLVR direction with distillation magnitude or route samples by correctness.

## Evidence Labels

Use exactly these labels:

- `[Paper claim]`: the paper itself states it.
- `[Official blog / repo README claim]`: official blog, project page, repository README, or official code comment states it.
- `[My reproduced result]`: this fork actually ran the command and produced logs/eval artifacts.
- `[My inference]`: synthesis or interpretation from checked sources.

Do not weaken this rule for slides. Slide notes and tables must still keep claim provenance clear.

## Current Reproduction Status

- The official OPSD code has been forked and project scaffolding has been added.
- Papers and the Thinking Machines blog have been saved under `papers/`.
- Dataset acquisition has been documented but not executed as of this harness bootstrap.
- No local OPSD training or evaluation result has been produced yet.

## Default Work Style

- Prefer primary sources: paper PDF, official blog, official repository, dataset card.
- When changing reproduction code, update `reproduction/opsd_runbook.md` if the run procedure changes.
- When adding or revising survey content, update `notes/source_ledger.md` or a dedicated paper note so future agents can trace the claim.
- When running experiments, create an entry from `experiments/experiment_log_template.md` and store raw logs under `logs/` or an ignored output directory.
