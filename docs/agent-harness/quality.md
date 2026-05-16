# Quality Gates

## Fast Canonical Checks

Run these before claiming a harness or documentation change is complete:

```powershell
python evals/smoke_eval.py
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile scripts/prefetch_datasets.py
```

For code changes touching upstream training/evaluation entry points, also run syntax checks:

```powershell
python -m py_compile opsd_train.py sft_train.py grpo_train.py eval/evaluate_math.py data_collator.py
```

## Dataset Checks

Dataset access is a setup check, not a reproduced model result:

```powershell
python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets
python scripts/prefetch_datasets.py --only eval --cache-dir .cache/hf_datasets
```

Record failures exactly. Hugging Face network, authentication, or policy failures are blockers, not reasons to invent local data.

## Heavy Experiment Checks

Do not run training or full benchmark evaluation as a default quality gate. When requested, record:

- exact command;
- branch and commit;
- model path and dataset cache path;
- hardware and CUDA/PyTorch/vLLM versions;
- output directory, logs, checkpoints, and eval JSON;
- whether the result is `[My reproduced result]`.

## Evidence Rules

- Include exact commands run and whether they passed.
- Include relevant logs, file paths, screenshots, traces, or changed files.
- Mark unrun checks and explain residual risk.
- Never merge paper numbers into local result tables without a source label.

## CI Strategy

- Keep harness smoke checks cheap and dependency-light.
- Do not add CI jobs that require GPUs, model weights, Hugging Face credentials, or large downloads.
- GPU runs should stay manual until a dedicated experiment runner exists.
