# Self-Distilled Reasoner Reproduction Runbook

Status: initialized, not yet executed.

## Reproduction Target

- Paper: Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models.
- Official repo: https://github.com/siyan-zhao/OPSD
- Local fork: https://github.com/jinyankai/OPSD-experiment.git
- Upstream commit locked on 2026-05-16: `7448751f307a9cdbcc1246dd1565a1a605b443df`
- Target claim to reproduce first: OPSD improves math reasoning over the base model on AIME-style benchmarks using Qwen3-1.7B with LoRA and a fixed teacher.

Evidence policy:

- `[Paper claim]` for paper numbers and method descriptions.
- `[Official blog / repo README claim]` for README tables and scripts.
- `[My reproduced result]` only after local logs and eval JSON exist.
- `[My inference]` for analysis and likely causes of differences.

## Repository Map

- `opsd_train.py`: OPSD training entry point; loads `siyanzhao/Openthoughts_math_30k_opsd`, tokenizer, model config, and `OPSDTrainer`.
- `opsd_trainer.py`: core trainer; builds student rollouts, computes teacher/student distributions, supports full-vocabulary JSD, sampled-token objective, fixed teacher, EMA teacher, top-k loss, and JSD clipping.
- `data_collator.py`: creates student and teacher inputs, including privileged solution context and Qwen3 thinking-mode controls.
- `sft_train.py`: SFT baseline on the same broad data family.
- `grpo_train.py`: GRPO baseline with verifiable outcome rewards.
- `scripts/run_opsd_1b.sh`: official quick-start style launch for Qwen3-1.7B.
- `eval/evaluate_math.py`: vLLM-based math evaluation on MATH500, AIME24, AIME25, HMMT25, Minerva, AMC23, and AMO-Bench.

## Training Pipeline

1. Load math problem-solution pairs from `siyanzhao/Openthoughts_math_30k_opsd`.
2. Student policy sees the question only and samples an on-policy trajectory.
3. Teacher policy sees question plus privileged solution and scores the student's prefix/token distribution.
4. Loss is computed as generalized JSD or sampled-token policy-gradient style distillation.
5. Gradients flow only through the student side.
6. With `--fixed_teacher --use_peft`, the base model without LoRA adapters acts as the fixed teacher and the LoRA adapters are the student update.
7. Save checkpoints every configured interval.
8. Evaluate base and checkpointed adapters through vLLM on math benchmarks.

## Environment

Official `environment.yml` pins:

```bash
conda env create -f environment.yml
conda activate opsd
pip install flash-attn==2.8.3 --no-build-isolation
```

Key packages:

- Python 3.10
- torch 2.8.0
- accelerate 1.11.0
- transformers 4.57.1
- trl 0.26.0
- datasets 3.6.0
- deepspeed 0.18.2
- peft 0.17.1
- bitsandbytes 0.48.2
- vllm 0.11.0
- xformers 0.0.32.post1
- math-verify 0.8.0

Compatibility risks:

- `flash-attn` must match installed CUDA, PyTorch, and GPU architecture.
- vLLM and LoRA adapter loading can fail if checkpoint files are missing or ZeRO-3 shards are not consolidated.
- Qwen3 chat template and `enable_thinking` must match training/evaluation assumptions.
- Long-context evaluation can require substantially more GPU memory than short training rollouts.

## Dataset Preparation

The official scripts use Hugging Face `datasets` and download lazily at first use. For reproducibility, prefetch them before training/evaluation and keep the cache path fixed.

Primary training dataset:

- `siyanzhao/Openthoughts_math_30k_opsd`, split `train`, loaded in `opsd_train.py`.

Evaluation datasets:

- `HuggingFaceH4/MATH-500`, split `test`.
- `HuggingFaceH4/aime_2024`, split `train`.
- `yentinglin/aime_2025`, split `train`, `trust_remote_code=True`.
- `MathArena/hmmt_feb_2025`, split `train`, `trust_remote_code=True`.
- `meituan-longcat/AMO-Bench`, split `test`.
- `math-ai/minervamath`, split `test`.
- `math-ai/amc23`, split `test`.

Recommended prefetch command:

```bash
python scripts/prefetch_datasets.py --cache-dir .cache/hf_datasets
```

Training-set-only smoke check:

```bash
python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets
```

Eval-set-only smoke check:

```bash
python scripts/prefetch_datasets.py --only eval --cache-dir .cache/hf_datasets
```

For full details, including Windows PowerShell environment variables, offline reuse, and expected columns, see `reproduction/dataset_download.md`.

## Hardware Analysis

Before selecting model size, GPU count, batch size, completion length, or vLLM tensor parallelism on a new server, run:

```bash
python scripts/analyze_hardware.py --output-dir reproduction/hardware_reports
```

The generated report recommends one of these profiles:

- `official_1p7b_or_larger`: start with official Qwen3-1.7B commands; larger models may be feasible after smoke tests.
- `reduced_1p7b`: reduce batch size, completion length, and evaluation parallelism.
- `single_gpu_smoke`: use only for environment validation and tiny debug runs.
- `insufficient_for_training` or `cpu_or_unknown`: do not run OPSD training; use docs/static checks/dataset preflight.

Use the report to update concrete experiment logs and any server-specific command variants. Hardware reports are setup evidence, not model-quality results.

## Minimal Reproduction

Recommended first target: Qwen3-1.7B, LoRA, fixed teacher, 4 GPUs if available.

Official-style command:

```bash
bash scripts/run_opsd_1b.sh
```

Equivalent command shape to adapt paths:

```bash
accelerate launch \
  --config_file accelerate.yaml \
  --num_processes 4 \
  --gradient_accumulation_steps 2 \
  --main_process_port 12949 \
  opsd_train.py \
  --model_name_or_path /path/to/Qwen3-1.7B \
  --learning_rate 5e-6 \
  --max_grad_norm 0.1 \
  --per_device_train_batch_size 4 \
  --gradient_checkpointing \
  --gradient_accumulation_steps 2 \
  --output_dir outputs/opsd \
  --run_config qwen31b_gen1024_fixteacher_temp11_forwardbeta0_clip005 \
  --num_train_epochs 30 \
  --max_completion_length 1024 \
  --save_steps 25 \
  --logging_steps 2 \
  --attn_implementation flash_attention_2 \
  --torch_dtype bfloat16 \
  --max_length 20000 \
  --beta 0 \
  --use_vllm \
  --vllm_mode colocate \
  --vllm_gpu_memory_utilization 0.6 \
  --vllm_tensor_parallel_size 1 \
  --use_peft \
  --lora_r 64 \
  --lora_alpha 128 \
  --lora_target_modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --temperature 1.1 \
  --top_p 0.95 \
  --top_k 20 \
  --lmbda 1 \
  --fixed_teacher \
  --jsd_token_clip 0.05 \
  --wandb_project OPSD
```

Base evaluation:

```bash
cd eval
CUDA_VISIBLE_DEVICES=0,1,2,3 python evaluate_math.py \
  --base_model /path/to/Qwen3-1.7B \
  --dataset aime24 \
  --val_n 12 \
  --temperature 1.0 \
  --tensor_parallel_size 4
```

Checkpoint evaluation:

```bash
cd eval
CUDA_VISIBLE_DEVICES=0,1,2,3 python evaluate_math.py \
  --base_model /path/to/Qwen3-1.7B \
  --checkpoint_dir ../outputs/opsd/qwen31b_gen1024_fixteacher_temp11_forwardbeta0_clip005/checkpoint-100 \
  --dataset aime24 \
  --val_n 12 \
  --temperature 1.0 \
  --tensor_parallel_size 4
```

## Smoke-Test Plan

1. Verify environment import:
   `python -c "import torch, transformers, trl, vllm, math_verify; print(torch.__version__)"`
2. Verify dataset access:
   `python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets`
3. Run base eval with `--num_samples 2 --val_n 1`.
4. Run OPSD for a tiny debug run with `--max_steps 1`, smaller batch, and local `output_dir`.
5. Only after smoke tests, run 25/50/75/100-step checkpoints.

## Claims That Remain Unverified

- No local training result has been produced.
- No local evaluation JSON has been produced.
- README benchmark tables have not been reproduced.
- Hardware availability is unknown.
