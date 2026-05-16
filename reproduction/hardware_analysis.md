# Hardware Analysis Workflow

Status: documented and script added; server analysis not yet run.

Run this after uploading the project to a training/evaluation server. The goal is to collect enough machine facts to choose a realistic OPSD reproduction profile before editing training scripts or launching expensive jobs.

## Quick Command

```bash
python scripts/analyze_hardware.py --output-dir reproduction/hardware_reports
```

Print only, without writing files:

```bash
python scripts/analyze_hardware.py --no-write
```

Print JSON:

```bash
python scripts/analyze_hardware.py --json --no-write
```

Probe extra storage mounts:

```bash
python scripts/analyze_hardware.py \
  --path . \
  --path /data \
  --path /scratch \
  --output-dir reproduction/hardware_reports
```

## What It Collects

- OS, hostname, Python executable, branch, commit, and Git status.
- CPU count and `lscpu` details when available.
- System RAM from `/proc/meminfo` or platform fallback.
- Disk space for the repo, `.cache`, `outputs`, and any extra `--path`.
- GPU inventory from `nvidia-smi` when available.
- CUDA/GPU details from PyTorch when installed.
- Package versions for torch, transformers, accelerate, trl, datasets, deepspeed, peft, bitsandbytes, vLLM, xformers, flash-attn, and math-verify.
- A heuristic OPSD profile and suggested next commands.

## How to Use the Report

1. Run the script on the target server.
2. Save the generated Markdown and JSON report under `reproduction/hardware_reports/`.
3. Do not commit server-specific report files unless the user explicitly wants them shared.
4. Use the report to update:
   - `reproduction/opsd_runbook.md` for recommended training/eval commands;
   - `experiments/experiment_log_template.md` or a concrete experiment log for hardware fields;
   - shell scripts under `scripts/` only if the server profile justifies stable project defaults.

## Recommendation Profiles

- `official_1p7b_or_larger`: typically 4+ GPUs with about 80 GiB VRAM each. Start with `scripts/run_opsd_1b.sh`; consider 4B/8B only after the 1.7B path is validated.
- `reduced_1p7b`: typically 2+ GPUs with about 40 GiB VRAM each. Prefer reduced batch, shorter completion length, and one benchmark at a time.
- `single_gpu_smoke`: typically one GPU with about 24 GiB VRAM. Use for environment validation and tiny debug runs, not performance claims.
- `insufficient_for_training`: GPU VRAM too small for meaningful OPSD training.
- `cpu_or_unknown`: no CUDA GPU detected. Use for docs, static checks, and dataset preflight only.

## Evidence Policy

Hardware reports are setup evidence. They do not count as `[My reproduced result]` for model quality. A model result requires a completed experiment record with command, commit, model path, dataset cache, hardware, logs, and eval outputs.
