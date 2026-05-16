# Architecture Map

## Domains

- Upstream OPSD implementation:
  - `opsd_train.py`: OPSD training entry point and dataset loading.
  - `opsd_trainer.py`: on-policy rollout, teacher/student distribution logic, JSD/KL-style objectives, PEFT/fixed-teacher support.
  - `data_collator.py`: student and teacher prompt construction, including privileged solution context.
  - `sft_train.py` and `grpo_train.py`: baseline training entry points.
  - `eval/evaluate_math.py`: vLLM math evaluation harness.
- Research artifacts:
  - `papers/`: local PDFs/HTML plus `manifest.md`.
  - `notes/`: source ledger, paper cards, taxonomy, comparison notes.
  - `slides/`: presentation outline and eventually slide sources.
- Reproduction artifacts:
  - `reproduction/`: runbooks, dataset instructions, environment notes.
  - `experiments/`: experiment records and structured summaries.
  - `logs/`: placeholder only; real logs are ignored by Git.
  - `scripts/prefetch_datasets.py`: lightweight dataset prefetch/check utility.
  - `scripts/validate_datasets.py`: dataset schema and non-empty-field validation; it does not preprocess.
  - `scripts/analyze_hardware.py`: server resource probe and OPSD config recommender.
- Agent harness:
  - `AGENTS.md`, `docs/agent-harness/`, `agents/skills/`, `evals/`, `tests/`.

## Boundaries

- Treat upstream OPSD code as reproducibility-critical. Do not refactor it for style only.
- Keep survey/presentation edits outside upstream training files unless a code change is necessary for reproduction.
- Do not commit large checkpoints, model weights, raw training outputs, WandB directories, or Hugging Face caches.
- Do not mark experiment outputs as `[My reproduced result]` without local artifacts.

## Data Flow

Training:

1. Hugging Face dataset `siyanzhao/Openthoughts_math_30k_opsd`.
2. Student question-only prompt.
3. On-policy student rollout.
4. Teacher prompt with privileged solution/context.
5. OPSD loss in `opsd_trainer.py`.
6. LoRA/checkpoint output.

Evaluation:

1. Math benchmark dataset loaded in `eval/evaluate_math.py`.
2. vLLM generation with Qwen3 thinking-mode assumptions.
3. Answer extraction and math verification.
4. JSON/log output.

## Agent Notes

- If dataset IDs or expected fields change, update `reproduction/dataset_download.md`, `reproduction/dataset_preprocessing.md`, `scripts/prefetch_datasets.py`, and `scripts/validate_datasets.py`.
- If hardware-driven defaults change, update `reproduction/hardware_analysis.md`, `reproduction/opsd_runbook.md`, and any affected shell scripts.
- If training flags change, update `reproduction/opsd_runbook.md`.
- If survey scope changes, update `papers/manifest.md`, `notes/source_ledger.md`, and `slides/survey_outline.md`.
