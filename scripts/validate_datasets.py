"""Validate OPSD training/evaluation dataset schemas without preprocessing.

The official training and evaluation scripts format examples at runtime:

- OPSD uses raw `problem` / `solution` rows in `data_collator.py`.
- SFT maps raw rows to `text` inside `sft_train.py`.
- GRPO maps raw rows to `prompt` / `Answer` inside `grpo_train.py`.
- Evaluation normalizes each benchmark in `eval/evaluate_math.py`.

This script therefore checks dataset availability and expected columns, but it
does not write a transformed training dataset.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"


@dataclasses.dataclass(frozen=True)
class DatasetSpec:
    purpose: str
    name: str
    split: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()
    trust_remote_code: bool = False


TRAIN_SPECS = [
    DatasetSpec(
        purpose="opsd/sft/grpo-train",
        name="siyanzhao/Openthoughts_math_30k_opsd",
        split="train",
        required_fields=("problem", "solution"),
        optional_fields=("Question", "Answer"),
    ),
]


EVAL_SPECS = [
    DatasetSpec("math500", "HuggingFaceH4/MATH-500", "test", ("problem", "solution")),
    DatasetSpec("aime24", "HuggingFaceH4/aime_2024", "train", ("problem", "answer")),
    DatasetSpec("aime25", "yentinglin/aime_2025", "train", ("problem", "answer"), trust_remote_code=True),
    DatasetSpec("hmmt25", "MathArena/hmmt_feb_2025", "train", ("problem", "answer"), trust_remote_code=True),
    DatasetSpec("amo-bench", "meituan-longcat/AMO-Bench", "test", ("prompt", "answer")),
    DatasetSpec("minerva", "math-ai/minervamath", "test", ("question", "answer")),
    DatasetSpec("amc23", "math-ai/amc23", "test", ("question", "answer")),
]


def configure_hf_endpoint(endpoint: str | None) -> None:
    if os.environ.get("USE_HF_MIRROR", "1") == "0":
        return
    os.environ.setdefault("HF_ENDPOINT", endpoint or DEFAULT_HF_ENDPOINT)
    os.environ.setdefault("HUGGINGFACE_CO_RESOLVE_ENDPOINT", os.environ["HF_ENDPOINT"])


def selected_specs(group: str) -> list[DatasetSpec]:
    if group == "train":
        return TRAIN_SPECS
    if group == "eval":
        return EVAL_SPECS
    return TRAIN_SPECS + EVAL_SPECS


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def validate_one(spec: DatasetSpec, cache_dir: str | None, max_examples: int) -> dict[str, Any]:
    from datasets import load_dataset

    result: dict[str, Any] = {
        "purpose": spec.purpose,
        "name": spec.name,
        "split": spec.split,
        "required_fields": list(spec.required_fields),
        "optional_fields": list(spec.optional_fields),
        "trust_remote_code": spec.trust_remote_code,
        "ok": False,
        "warnings": [],
        "errors": [],
    }
    try:
        dataset = load_dataset(
            spec.name,
            split=spec.split,
            cache_dir=cache_dir,
            trust_remote_code=spec.trust_remote_code,
        )
    except Exception as exc:
        result["errors"].append(f"load_dataset failed: {exc}")
        return result

    columns = list(dataset.column_names)
    result["num_rows"] = len(dataset)
    result["columns"] = columns

    missing_required = [field for field in spec.required_fields if field not in columns]
    missing_optional = [field for field in spec.optional_fields if field not in columns]
    if missing_required:
        result["errors"].append(f"missing required fields: {missing_required}")
    if missing_optional:
        result["warnings"].append(f"missing optional workflow fields: {missing_optional}")
    if len(dataset) == 0:
        result["errors"].append("dataset split is empty")

    non_empty_counts = {field: 0 for field in spec.required_fields if field in columns}
    checked = min(max_examples, len(dataset))
    for index in range(checked):
        row = dataset[index]
        for field in non_empty_counts:
            if is_present(row.get(field)):
                non_empty_counts[field] += 1
    result["checked_examples"] = checked
    result["non_empty_counts"] = non_empty_counts
    for field, count in non_empty_counts.items():
        if checked > 0 and count == 0:
            result["errors"].append(f"field `{field}` is empty in all {checked} checked examples")
        elif checked > 0 and count < checked:
            result["warnings"].append(f"field `{field}` is empty in {checked - count}/{checked} checked examples")

    result["ok"] = not result["errors"]
    return result


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    configure_hf_endpoint(args.hf_endpoint)
    rows = [validate_one(spec, args.cache_dir, args.max_examples) for spec in selected_specs(args.only)]
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hf_endpoint": os.environ.get("HF_ENDPOINT"),
        "cache_dir": args.cache_dir,
        "preprocessing_required": False,
        "preprocessing_reason": (
            "Official scripts perform prompt construction/tokenization or benchmark field mapping at runtime; "
            "offline preprocessing would duplicate that logic and risks changing the reproduction target."
        ),
        "datasets": rows,
        "ok": all(row["ok"] for row in rows),
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Dataset Validation Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- HF endpoint: `{report.get('hf_endpoint') or '<unset>'}`",
        f"- Cache dir: `{report.get('cache_dir') or '<default>'}`",
        f"- Preprocessing required: `{report['preprocessing_required']}`",
        f"- Reason: {report['preprocessing_reason']}",
        "",
        "## Datasets",
        "",
    ]
    for row in report["datasets"]:
        status = "OK" if row["ok"] else "FAIL"
        lines.extend(
            [
                f"### {row['purpose']} - {status}",
                "",
                f"- HF ID: `{row['name']}`",
                f"- Split: `{row['split']}`",
                f"- Rows: `{row.get('num_rows', 'unknown')}`",
                f"- Columns: `{', '.join(row.get('columns', []))}`",
                f"- Required fields: `{', '.join(row['required_fields'])}`",
                f"- Checked examples: `{row.get('checked_examples', 0)}`",
            ]
        )
        if row.get("non_empty_counts"):
            counts = ", ".join(f"{key}={value}" for key, value in row["non_empty_counts"].items())
            lines.append(f"- Non-empty counts: `{counts}`")
        for warning in row["warnings"]:
            lines.append(f"- Warning: {warning}")
        for error in row["errors"]:
            lines.append(f"- Error: {error}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OPSD dataset schemas without preprocessing.")
    parser.add_argument("--only", choices=["all", "train", "eval"], default="all")
    parser.add_argument("--cache-dir", default=None, help="Optional Hugging Face datasets cache directory.")
    parser.add_argument(
        "--hf-endpoint",
        default=None,
        help="Optional Hugging Face endpoint. Defaults to https://hf-mirror.com unless USE_HF_MIRROR=0.",
    )
    parser.add_argument("--max-examples", type=int, default=32, help="Examples per dataset to check for empty fields.")
    parser.add_argument("--output-dir", default="reproduction/dataset_reports")
    parser.add_argument("--no-write", action="store_true", help="Print only; do not write report files.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(markdown_report(report))

    if not args.no_write:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        (output_dir / f"dataset_validation_{timestamp}.json").write_text(
            json.dumps(report, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (output_dir / f"dataset_validation_{timestamp}.md").write_text(markdown_report(report), encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
