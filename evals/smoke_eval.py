#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "docs/agent-harness/index.md",
    "docs/agent-harness/project-intent.md",
    "docs/agent-harness/architecture.md",
    "docs/agent-harness/quality.md",
    "docs/agent-harness/tools.md",
    "docs/agent-harness/review.md",
    "agents/skills/README.md",
    "agents/skills/survey-reproduction/SKILL.md",
    "reproduction/opsd_runbook.md",
    "reproduction/dataset_download.md",
    "reproduction/dataset_preprocessing.md",
    "scripts/validate_datasets.py",
    "reproduction/hardware_analysis.md",
    "scripts/analyze_hardware.py",
    "notes/source_ledger.md",
    "papers/manifest.md",
]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        print("Missing harness files:")
        for path in missing:
            print(f"- {path}")
        return 1
    print("Harness smoke eval passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
