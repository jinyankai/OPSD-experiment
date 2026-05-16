# Experiment Log Template

## Metadata

- Experiment ID:
- Date:
- Operator:
- Git commit:
- Branch:
- Upstream commit:
- Machine / GPU:
- CUDA / driver:
- Conda env:

## Model and Data

- Base model:
- Tokenizer / chat template:
- Thinking mode:
- Dataset:
- Train split:
- Eval split:
- Max prompt length:
- Max completion length:

## Training Command

```bash

```

## Evaluation Command

```bash

```

## Resource Use

- GPUs:
- Peak VRAM:
- Wall-clock time:
- Tokens generated:
- Checkpoint interval:
- Output directory:
- Log directory:

## Metrics

| Step | Dataset | Val-N | Avg@N | Pass@N | Majority@N | Format rate | Avg length | Notes |
|---:|---|---:|---:|---:|---:|---:|---:|---|

## Observations

- Training stability:
- Loss / KL / JSD trend:
- Reward / accuracy trend:
- Early peak:
- Collapse:
- Over-shortening:
- Style-token domination:
- Formatting failures:

## Claim Comparison

- `[Paper claim]`:
- `[Official blog / repo README claim]`:
- `[My reproduced result]`:
- Difference:
- Plausible causes:

## Artifacts

- Training log:
- Eval JSON:
- Checkpoint:
- WandB / tracker:
- Plots:
