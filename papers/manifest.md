# Paper Manifest

Retrieval date: 2026-05-16

Evidence labels used throughout this project:

- `[Paper claim]`: Claims made in the paper itself.
- `[Official blog / repo README claim]`: Claims from official blogs, project pages, repository READMEs, or official code comments.
- `[My reproduced result]`: Results actually run and verified in this fork.
- `[My inference]`: My interpretation or synthesis from cited sources.

## Required Sources

| Status | File | Title | Source | Notes |
|---|---|---|---|---|
| downloaded | `thinking-machines-on-policy-distillation.html` | On-Policy Distillation | https://thinkingmachines.ai/blog/on-policy-distillation/ | Official blog, not a paper PDF. |
| downloaded | `2602.12275-opcd.pdf` | On-Policy Context Distillation for Language Models | https://arxiv.org/abs/2602.12275 | Required survey paper. |
| downloaded | `2601.18734-opsd.pdf` | Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models | https://arxiv.org/abs/2601.18734 | Required survey paper and reproduction target. |
| downloaded | `2601.20802-sdpo.pdf` | Reinforcement Learning via Self-Distillation | https://arxiv.org/abs/2601.20802 | Required survey paper. |

## Optional / Added Sources

| Status | File | Title | Source | Why included |
|---|---|---|---|---|
| downloaded | `2306.13649-gkd.pdf` | On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes | https://arxiv.org/abs/2306.13649 | Seminal on-policy KD / GKD. |
| downloaded | `2306.08543-minillm.pdf` | MiniLLM: Knowledge Distillation of Large Language Models | https://arxiv.org/abs/2306.08543 | Reverse-KL foundation for generative KD. |
| downloaded | `2603.16856-oel.pdf` | Online Experiential Learning for Language Models | https://arxiv.org/abs/2603.16856 | Online loop built on OPCD. |
| downloaded | `2603.24093-dgo.pdf` | Towards Effective Experiential Learning: Dual Guidance for Utilization and Internalization | https://arxiv.org/abs/2603.24093 | Experience bank + RLVR guidance. |
| downloaded | `2603.24472-self-distillation-degrade.pdf` | Why Does Self-Distillation (Sometimes) Degrade the Reasoning Capability of LLMs? | https://arxiv.org/abs/2603.24472 | Failure mode: uncertainty suppression. |
| downloaded | `2603.25562-revisiting-opd.pdf` | Revisiting On-Policy Distillation: Empirical Failure Modes and Simple Fixes | https://arxiv.org/abs/2603.25562 | Failure modes and top-K local support fix. |
| downloaded | `2604.03128-rlsd.pdf` | Self-Distilled RLVR | https://arxiv.org/abs/2604.03128 | RLVR + self-distillation hybrid. |
| downloaded | `2604.02288-srpo.pdf` | Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing | https://arxiv.org/abs/2604.02288 | Sample routing fix for SDPO/GRPO. |
| downloaded | `2603.07079-entropy-aware-opd.pdf` | Entropy-Aware On-Policy Distillation of Language Models | https://arxiv.org/abs/2603.07079 | Uncertainty-aware objective. |
| downloaded | `2511.10643-black-box-opd.pdf` | Black-Box On-Policy Distillation of Large Language Models | https://arxiv.org/abs/2511.10643 | Black-box OPD branch. |
| downloaded | `2604.03873-soda.pdf` | SODA: Semi On-Policy Black-Box Distillation for Large Language Models | https://arxiv.org/abs/2604.03873 | Semi-on-policy black-box distillation. |
| downloaded | `2604.00626-opd-survey.pdf` | A Survey of On-Policy Distillation for Large Language Models | https://arxiv.org/abs/2604.00626 | Survey/taxonomy source. |
| downloaded | `2605.11182-many-faces-opd.pdf` | The Many Faces of On-Policy Distillation: Pitfalls, Mechanisms, and Fixes | https://arxiv.org/abs/2605.11182 | Latest empirical pitfalls and fixes. |
| downloaded | `2605.10781-rlrt.pdf` | Rebellious Student: Reversing Teacher Signals for Reasoning Exploration with Self-Distilled RLVR | https://arxiv.org/abs/2605.10781 | Latest RLVR/self-distillation exploration direction. |

## Local Download Policy

- PDFs were initially configured for Git LFS, but GitHub rejected LFS uploads to this public fork during the first push attempt.
- Current branch fallback: PDFs are committed directly as binary files because the largest file is below GitHub's normal file-size limit.
- If repository size becomes a problem, move PDFs back to Git LFS after enabling LFS uploads for the fork or use a manifest-only branch.
- Do not mark a source as downloaded until the file exists locally.
- Do not copy benchmark numbers into notes without a nearby source label.
