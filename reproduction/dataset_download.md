# Dataset Download and Cache Guide

Status: documented, not yet executed in this fork.

This repo uses Hugging Face `datasets`. The official scripts download data lazily at first use, but for reproducibility it is better to prefetch all datasets into a known cache directory before training or evaluation.

By default, project scripts use the Hugging Face mirror:

```bash
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
```

Disable this default with `USE_HF_MIRROR=0` if the server can access `https://huggingface.co` directly.

## Dataset Inventory

| Use | Code path | HF dataset ID | Split | Trust remote code? | Expected fields |
|---|---|---|---|---|---|
| OPSD training | `opsd_train.py` | `siyanzhao/Openthoughts_math_30k_opsd` | `train` | no | `problem`, `solution` |
| MATH500 eval | `eval/evaluate_math.py --dataset math500` | `HuggingFaceH4/MATH-500` | `test` | no | `problem`, `solution` |
| AIME24 eval | `eval/evaluate_math.py --dataset aime24` | `HuggingFaceH4/aime_2024` | `train` | no | `problem`, `answer` |
| AIME25 eval | `eval/evaluate_math.py --dataset aime25` | `yentinglin/aime_2025` | `train` | yes | `problem`, `answer` |
| HMMT25 eval | `eval/evaluate_math.py --dataset hmmt25` | `MathArena/hmmt_feb_2025` | `train` | yes | `problem`, `answer` |
| AMO-Bench eval | `eval/evaluate_math.py --dataset amo-bench` | `meituan-longcat/AMO-Bench` | `test` | no | `prompt`, `answer` |
| Minerva eval | `eval/evaluate_math.py --dataset minerva` | `math-ai/minervamath` | `test` | no | `question`, `answer` |
| AMC23 eval | `eval/evaluate_math.py --dataset amc23` | `math-ai/amc23` | `test` | no | `question`, `answer` |

## Option A: Lazy Download

The simplest route is to let `datasets.load_dataset(...)` download each dataset on first use:

```bash
python -c "from datasets import load_dataset; print(load_dataset('siyanzhao/Openthoughts_math_30k_opsd')['train'])"
```

This stores data in the default Hugging Face cache. On Linux this is usually `~/.cache/huggingface/datasets`; on Windows it is usually under the user's cache directory.

## Option B: Prefetch to a Known Cache Directory

Recommended for experiments:

```bash
python scripts/prefetch_datasets.py --cache-dir .cache/hf_datasets
```

Use a different mirror/endpoint:

```bash
python scripts/prefetch_datasets.py --cache-dir .cache/hf_datasets --hf-endpoint https://hf-mirror.com
```

Prefetch only the training set:

```bash
python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets
```

Prefetch only eval sets:

```bash
python scripts/prefetch_datasets.py --only eval --cache-dir .cache/hf_datasets
```

The script prints the dataset length and column names. Treat that output as a setup check, not as an experiment result.

## Preprocessing Decision

No offline preprocessing is required for the default reproduction. The official code formats rows at runtime:

- OPSD constructs student/teacher prompts in `data_collator.py`.
- SFT formats rows inside `sft_train.py`.
- GRPO formats rows inside `grpo_train.py`.
- Evaluation maps benchmark fields inside `eval/evaluate_math.py`.

Run validation, not preprocessing:

```bash
python scripts/validate_datasets.py --cache-dir .cache/hf_datasets
```

See `reproduction/dataset_preprocessing.md` for the decision record.

## Option C: Environment Variables

Linux/macOS:

```bash
export HF_HOME="$PWD/.cache/huggingface"
export HF_DATASETS_CACHE="$PWD/.cache/hf_datasets"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
python scripts/prefetch_datasets.py --cache-dir "$HF_DATASETS_CACHE"
```

Windows PowerShell:

```powershell
$env:HF_HOME = "$PWD\.cache\huggingface"
$env:HF_DATASETS_CACHE = "$PWD\.cache\hf_datasets"
$env:HF_ENDPOINT = "https://hf-mirror.com"
python scripts/prefetch_datasets.py --cache-dir $env:HF_DATASETS_CACHE
```

## Authentication

The listed datasets are expected to be public, but Hugging Face rate limits or policy changes can still require authentication.

```bash
huggingface-cli login
```

If a dataset is gated or unavailable, record the exact error in `experiments/experiment_log_template.md` under "Observations" and do not mark any reproduced result.

## Offline Reuse

After prefetching, a cluster job can be run in offline mode if the same cache is mounted:

```bash
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

For Windows PowerShell:

```powershell
$env:HF_DATASETS_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
```

Offline mode should only be used after the prefetch script has successfully printed all required dataset schemas.

## Model Weights Are Separate

Dataset prefetching does not download Qwen3 model weights. The official scripts use local model paths such as `/data0/shared/Qwen3-1.7B`. On a new machine, download or mount the model separately and pass its path through `--model_name_or_path` / `--base_model`. If a script uses a Hugging Face model ID instead of a local path, `scripts/hf_mirror_env.sh` makes transformers/vLLM resolve it through `https://hf-mirror.com` by default.
