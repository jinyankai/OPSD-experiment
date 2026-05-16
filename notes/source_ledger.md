# Source Ledger

This ledger separates claims by evidence type. It is the single place to record what has been checked, what is only claimed by authors, and what this fork has actually reproduced.

## Official Repository Baseline

- `[Official blog / repo README claim]` Fork source: https://github.com/jinyankai/OPSD-experiment.git
- `[Official blog / repo README claim]` Upstream source: https://github.com/siyan-zhao/OPSD.git
- `[Official blog / repo README claim]` Baseline upstream commit checked on 2026-05-16: `7448751f307a9cdbcc1246dd1565a1a605b443df`
- `[Official blog / repo README claim]` OPSD README says Qwen3-1.7B training takes about 15 minutes on 4xH100 and peaks within about 100 steps.
- `[Official blog / repo README claim]` OPSD README says the key implementation files are `opsd_train.py`, `opsd_trainer.py`, `data_collator.py`, baseline scripts, and `eval/evaluate_math.py`.
- `[My reproduced result]` None yet. No training or evaluation has been run in this fork.

## Claim Buckets

### [Paper claim]

- OPD addresses train-test distribution mismatch by training on student-generated trajectories and using teacher feedback on those trajectories.
- OPCD trains a context-free student on its own rollouts against a context-conditioned teacher to internalize context into parameters.
- OPSD uses one model as both student and teacher under different contexts; the teacher receives privileged solutions/traces while the student sees only the question.
- SDPO treats the current model conditioned on feedback as a self-teacher and distills feedback-informed predictions into the policy.
- Recent 2026 failure-mode papers argue self-distillation can collapse, suppress uncertainty, or become unreliable under support mismatch.

### [Official blog / repo README claim]

- Thinking Machines describes OPD as combining on-policy relevance with dense distillation feedback.
- OPSD README reports updated code on 2026-03-18, including chat-template/ZeRO-2 fixes and per-token point-wise KL clipping.
- OPSD README reports evaluation settings with Qwen3 thinking mode, temperature 1.0, max new tokens 38912, and multiple samples per problem.

### [My reproduced result]

- Empty until a command has been run, logs are saved, and outputs are checked.

### [My inference]

- OPCD, OPSD, and SDPO can be organized as the same template: student rollout plus a better-informed conditional policy used as dense supervision.
- The main axis separating them is the source of information asymmetry: reusable context, privileged ground-truth solution, or environment feedback.
- 2026 fixes are converging on selective trust: route samples, mask special tokens, use local teacher support, and downweight uncertain teacher distributions.

## Open Verification Items

- Confirm exact arXiv IDs for the OPD survey and May 2026 follow-up papers from primary arXiv pages.
- Download PDFs and update `papers/manifest.md` from `pending download` to `downloaded`.
- Run at least one base-model evaluation smoke test before writing any `[My reproduced result]`.
