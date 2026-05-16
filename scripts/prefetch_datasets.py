"""Prefetch OPSD training and evaluation datasets into a Hugging Face cache.

This script intentionally does not train or evaluate anything. It only verifies
that the datasets used by the official OPSD scripts are reachable and prints
their split sizes and column names.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os

DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"


def configure_hf_endpoint(endpoint: str | None) -> None:
    if os.environ.get("USE_HF_MIRROR", "1") == "0":
        return
    os.environ.setdefault("HF_ENDPOINT", endpoint or DEFAULT_HF_ENDPOINT)
    os.environ.setdefault("HUGGINGFACE_CO_RESOLVE_ENDPOINT", os.environ["HF_ENDPOINT"])


@dataclass(frozen=True)
class DatasetSpec:
    purpose: str
    name: str
    split: str
    trust_remote_code: bool = False


TRAIN_DATASETS = [
    DatasetSpec("opsd-train", "siyanzhao/Openthoughts_math_30k_opsd", "train"),
]

EVAL_DATASETS = [
    DatasetSpec("math500", "HuggingFaceH4/MATH-500", "test"),
    DatasetSpec("aime24", "HuggingFaceH4/aime_2024", "train"),
    DatasetSpec("aime25", "yentinglin/aime_2025", "train", trust_remote_code=True),
    DatasetSpec("hmmt25", "MathArena/hmmt_feb_2025", "train", trust_remote_code=True),
    DatasetSpec("amo-bench", "meituan-longcat/AMO-Bench", "test"),
    DatasetSpec("minerva", "math-ai/minervamath", "test"),
    DatasetSpec("amc23", "math-ai/amc23", "test"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prefetch OPSD Hugging Face datasets.")
    parser.add_argument(
        "--only",
        choices=["all", "train", "eval"],
        default="all",
        help="Which dataset group to prefetch.",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Optional Hugging Face datasets cache directory.",
    )
    parser.add_argument(
        "--hf-endpoint",
        default=None,
        help="Optional Hugging Face endpoint. Defaults to https://hf-mirror.com unless USE_HF_MIRROR=0.",
    )
    return parser.parse_args()


def selected_specs(group: str) -> list[DatasetSpec]:
    if group == "train":
        return TRAIN_DATASETS
    if group == "eval":
        return EVAL_DATASETS
    return TRAIN_DATASETS + EVAL_DATASETS


def main() -> None:
    args = parse_args()
    configure_hf_endpoint(args.hf_endpoint)
    from datasets import load_dataset

    print(f"HF_ENDPOINT={os.environ.get('HF_ENDPOINT', '<unset>')}")
    for spec in selected_specs(args.only):
        print(f"\nLoading {spec.purpose}: {spec.name} split={spec.split}")
        dataset = load_dataset(
            spec.name,
            split=spec.split,
            cache_dir=args.cache_dir,
            trust_remote_code=spec.trust_remote_code,
        )
        print(f"  rows: {len(dataset)}")
        print(f"  columns: {list(dataset.column_names)}")


if __name__ == "__main__":
    main()
