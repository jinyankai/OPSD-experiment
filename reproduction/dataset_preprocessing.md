# Dataset Preprocessing Decision

Status: no offline preprocessing required; validation script added.

## Decision

No separate offline preprocessing step is required for the current OPSD reproduction path.

Reasons:

- `opsd_train.py` loads `siyanzhao/Openthoughts_math_30k_opsd` and passes raw rows into `OPSDTrainer`.
- `data_collator.py` reads raw `problem` and `solution` fields, then constructs student/teacher prompts and tokenizes them dynamically per batch.
- `sft_train.py` performs its SFT text formatting in-process with `train_dataset.map(make_format_fn(tokenizer))`.
- `grpo_train.py` performs its prompt/reward-field formatting in-process with `train_dataset.map(make_format_prompt(tokenizer), remove_columns=...)`.
- `eval/evaluate_math.py` maps each benchmark's fields to a common prompt/answer format at evaluation time.

Because prompt construction depends on the tokenizer chat template, thinking mode, and training/evaluation flags, pre-materializing prompts offline would risk diverging from the official reproduction target.

## Required Preflight Instead

Run schema validation before training/evaluation:

```bash
python scripts/validate_datasets.py --cache-dir .cache/hf_datasets
```

Training-only validation:

```bash
python scripts/validate_datasets.py --only train --cache-dir .cache/hf_datasets
```

Evaluation-only validation:

```bash
python scripts/validate_datasets.py --only eval --cache-dir .cache/hf_datasets
```

The script checks:

- dataset can be downloaded through the configured Hugging Face endpoint;
- expected columns exist;
- selected required fields are non-empty in sampled examples;
- GRPO helper fields `Question` and `Answer` are present when available.

## When Offline Preprocessing Would Become Necessary

Add a preprocessing script only if one of these happens:

- the upstream dataset schema changes and no longer exposes fields expected by the official scripts;
- a server cannot access Hugging Face during jobs and needs exported JSONL snapshots;
- tokenizer/chat-template materialization must be frozen for an ablation;
- SFT/GRPO baselines are intentionally changed to use a different normalized schema.

Until then, use validation and cache prefetching rather than preprocessing.
