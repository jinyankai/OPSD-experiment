# Tool and MCP Constraints

## Source Priority

Use sources in this order:

1. Local repo files and project docs.
2. Paper PDFs in `papers/`.
3. Official arXiv pages, official blogs, official repositories, dataset/model cards.
4. Third-party summaries only as clearly labeled secondary context.

## Network Use

- Network is appropriate for paper verification, GitHub upstream sync, Hugging Face dataset/model access, and official documentation checks.
- If information may have changed, verify before stating it as current.
- Record download dates in `papers/manifest.md` or the relevant runbook.

## Git Rules

- Preserve user changes and unrelated work.
- Use non-interactive Git commands.
- Do not run destructive commands such as hard resets or broad deletes unless explicitly requested and approved.
- Keep upstream OPSD sync separate from research/harness commits when practical.

## Hugging Face and Model Artifacts

- Use `scripts/prefetch_datasets.py` for dataset preflight checks.
- Do not commit model weights, checkpoints, cache directories, or raw logs.
- If authentication is required, ask the user to provide login through the appropriate CLI or environment; do not request secrets in chat.

## Evidence

When using tools, record the important outputs in the final response:

- checks run and pass/fail;
- files changed;
- source URLs or local file paths;
- experiment logs or eval output paths when applicable.
