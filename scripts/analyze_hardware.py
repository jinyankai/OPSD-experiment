"""Analyze server resources and recommend OPSD reproduction settings.

The script is intentionally dependency-light so it can run before the OPSD
conda environment is fully installed. It uses standard-library probes first,
then enriches the report with `nvidia-smi`, PyTorch, and package versions when
they are available.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import subprocess
import sys
from typing import Any


PACKAGE_NAMES = [
    "torch",
    "transformers",
    "accelerate",
    "trl",
    "datasets",
    "deepspeed",
    "peft",
    "bitsandbytes",
    "vllm",
    "xformers",
    "flash-attn",
    "math-verify",
]


@dataclasses.dataclass
class ProbeResult:
    ok: bool
    value: Any = None
    error: str | None = None


def run_command(args: list[str], timeout: int = 15) -> ProbeResult:
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return ProbeResult(False, error=f"not found: {exc.filename}")
    except Exception as exc:  # pragma: no cover - defensive probe
        return ProbeResult(False, error=str(exc))
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        return ProbeResult(False, error=stderr)
    return ProbeResult(True, completed.stdout.strip())


def bytes_to_gib(value: int | float | None) -> float | None:
    if value is None:
        return None
    return round(float(value) / (1024**3), 2)


def parse_meminfo() -> dict[str, float | None]:
    path = Path("/proc/meminfo")
    if not path.exists():
        return {"total_gib": None, "available_gib": None}
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            values[parts[0].rstrip(":")] = int(parts[1]) * 1024
    return {
        "total_gib": bytes_to_gib(values.get("MemTotal")),
        "available_gib": bytes_to_gib(values.get("MemAvailable")),
    }


def memory_info() -> dict[str, float | None]:
    linux_mem = parse_meminfo()
    if linux_mem["total_gib"] is not None:
        return linux_mem
    if platform.system().lower() == "windows":
        windows_mem = windows_memory_info()
        if windows_mem["total_gib"] is not None:
            return windows_mem
    if hasattr(os, "sysconf"):
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            return {"total_gib": bytes_to_gib(pages * page_size), "available_gib": None}
        except (OSError, ValueError):
            pass
    return {"total_gib": None, "available_gib": None}


def windows_memory_info() -> dict[str, float | None]:
    try:
        import ctypes
    except Exception:
        return {"total_gib": None, "available_gib": None}

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    try:
        success = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    except Exception:
        return {"total_gib": None, "available_gib": None}
    if not success:
        return {"total_gib": None, "available_gib": None}
    return {
        "total_gib": bytes_to_gib(status.ullTotalPhys),
        "available_gib": bytes_to_gib(status.ullAvailPhys),
    }


def cpu_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "logical_cpus": os.cpu_count(),
        "processor": platform.processor(),
        "machine": platform.machine(),
    }
    lscpu = run_command(["lscpu"])
    if lscpu.ok:
        for line in lscpu.value.splitlines():
            if ":" not in line:
                continue
            key, value = [part.strip() for part in line.split(":", 1)]
            if key in {"Model name", "Socket(s)", "Core(s) per socket", "Thread(s) per core", "NUMA node(s)"}:
                info[key.lower().replace(" ", "_").replace("(", "").replace(")", "")] = value
    return info


def disk_info(paths: list[str]) -> list[dict[str, Any]]:
    rows = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        target = path if path.exists() else path.parent
        try:
            usage = shutil.disk_usage(target)
            rows.append(
                {
                    "path": str(path),
                    "probe_path": str(target),
                    "total_gib": bytes_to_gib(usage.total),
                    "used_gib": bytes_to_gib(usage.used),
                    "free_gib": bytes_to_gib(usage.free),
                }
            )
        except Exception as exc:  # pragma: no cover - defensive probe
            rows.append({"path": str(path), "error": str(exc)})
    return rows


def parse_nvidia_smi_csv(text: str) -> list[dict[str, Any]]:
    gpus = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 5:
            continue
        gpu: dict[str, Any] = {
            "index": parts[0],
            "name": parts[1],
            "memory_total_mib": parse_number(parts[2]),
            "memory_free_mib": parse_number(parts[3]),
            "driver_version": parts[4],
        }
        if len(parts) >= 6:
            gpu["compute_capability"] = parts[5]
        gpus.append(gpu)
    return gpus


def parse_number(value: str) -> float | None:
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    number = float(match.group(0))
    return int(number) if number.is_integer() else number


def nvidia_smi_info() -> dict[str, Any]:
    version = run_command(["nvidia-smi"])
    query = run_command(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.free,driver_version,compute_cap",
            "--format=csv,noheader,nounits",
        ]
    )
    if not query.ok:
        query = run_command(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.free,driver_version",
                "--format=csv,noheader,nounits",
            ]
        )
    return {
        "available": version.ok or query.ok,
        "raw_version": version.value if version.ok else None,
        "version_error": version.error if not version.ok else None,
        "gpus": parse_nvidia_smi_csv(query.value) if query.ok else [],
        "query_error": query.error if not query.ok else None,
    }


def torch_info() -> dict[str, Any]:
    try:
        import torch  # type: ignore
    except Exception as exc:
        return {"available": False, "error": str(exc)}
    cuda_available = torch.cuda.is_available()
    devices = []
    if cuda_available:
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            devices.append(
                {
                    "index": index,
                    "name": props.name,
                    "total_memory_gib": bytes_to_gib(props.total_memory),
                    "capability": f"{props.major}.{props.minor}",
                    "multi_processor_count": props.multi_processor_count,
                }
            )
    return {
        "available": True,
        "version": torch.__version__,
        "cuda_available": cuda_available,
        "cuda_version": torch.version.cuda,
        "device_count": torch.cuda.device_count() if cuda_available else 0,
        "devices": devices,
    }


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def git_info(repo: Path) -> dict[str, str | None]:
    def git(args: list[str]) -> str | None:
        result = run_command(["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo), *args])
        return result.value if result.ok else None

    return {
        "branch": git(["branch", "--show-current"]),
        "commit": git(["rev-parse", "HEAD"]),
        "status_short": git(["status", "--short"]),
    }


def gpu_summary(report: dict[str, Any]) -> tuple[int, float | None, list[str]]:
    gpus = report["torch"].get("devices") or []
    if gpus:
        memories = [gpu.get("total_memory_gib") for gpu in gpus if gpu.get("total_memory_gib") is not None]
        names = [gpu.get("name", "unknown") for gpu in gpus]
        return len(gpus), min(memories) if memories else None, names
    smi_gpus = report["nvidia_smi"].get("gpus") or []
    memories = [
        round(float(gpu["memory_total_mib"]) / 1024, 2)
        for gpu in smi_gpus
        if gpu.get("memory_total_mib") is not None
    ]
    names = [gpu.get("name", "unknown") for gpu in smi_gpus]
    return len(smi_gpus), min(memories) if memories else None, names


def recommendations(report: dict[str, Any]) -> dict[str, Any]:
    gpu_count, min_vram_gib, gpu_names = gpu_summary(report)
    disks = report.get("disk", [])
    free_disk_gib = max((row.get("free_gib") or 0 for row in disks), default=0)
    ram_gib = report["memory"].get("total_gib")
    recs: list[str] = []
    commands: list[str] = []
    profile = "cpu_or_unknown"

    commands.append("source scripts/hf_mirror_env.sh")
    commands.append("python scripts/prefetch_datasets.py --cache-dir .cache/hf_datasets")

    if gpu_count == 0:
        recs.append("No CUDA GPU detected. Limit work to docs, dataset prefetch, static checks, and CPU-only script validation.")
        recs.append("Do not attempt OPSD training or vLLM evaluation on this machine.")
    elif min_vram_gib is None:
        recs.append(f"Detected {gpu_count} GPU(s), but VRAM could not be determined. Run nvidia-smi manually before choosing a config.")
    elif gpu_count >= 4 and min_vram_gib >= 75:
        profile = "official_1p7b_or_larger"
        recs.append("Good fit for official Qwen3-1.7B OPSD LoRA run and multi-sample vLLM evaluation.")
        recs.append("Qwen3-4B/8B experiments may be feasible; start with official scripts and monitor VRAM.")
        commands.append("bash scripts/run_opsd_1b.sh")
        commands.append("cd eval && CUDA_VISIBLE_DEVICES=0,1,2,3 python evaluate_math.py --base_model /path/to/Qwen3-1.7B --dataset aime24 --val_n 12 --temperature 1.0 --tensor_parallel_size 4")
    elif gpu_count >= 2 and min_vram_gib >= 40:
        profile = "reduced_1p7b"
        recs.append("Likely suitable for Qwen3-1.7B LoRA smoke training with reduced batch/rollout settings.")
        recs.append("Use smaller `max_completion_length`, lower vLLM GPU utilization, and evaluate one benchmark at a time.")
        commands.append("accelerate launch --num_processes 2 opsd_train.py --model_name_or_path /path/to/Qwen3-1.7B --use_peft --fixed_teacher --per_device_train_batch_size 1 --gradient_accumulation_steps 8 --max_completion_length 512 --output_dir outputs/opsd_smoke")
    elif gpu_count >= 1 and min_vram_gib >= 24:
        profile = "single_gpu_smoke"
        recs.append("Use this machine for environment validation, dataset prefetch, base-model eval smoke tests, and very short LoRA debug runs.")
        recs.append("Full OPSD training with colocated vLLM may be unstable on a single GPU; avoid reporting performance numbers from tiny debug runs.")
        commands.append("CUDA_VISIBLE_DEVICES=0 python scripts/prefetch_datasets.py --only train --cache-dir .cache/hf_datasets")
        commands.append("CUDA_VISIBLE_DEVICES=0 python -m py_compile opsd_train.py opsd_trainer.py data_collator.py")
    else:
        profile = "insufficient_for_training"
        recs.append("GPU VRAM appears too small for meaningful OPSD training. Prefer docs, CPU checks, or request a larger GPU node.")

    if ram_gib is not None and ram_gib < 64:
        recs.append("System RAM is below 64 GiB; avoid large parallel dataset/model cache operations.")
    elif ram_gib is not None and ram_gib >= 128:
        recs.append("System RAM is comfortable for dataset preprocessing and multi-worker evaluation.")

    if free_disk_gib < 50:
        recs.append("Free disk is below 50 GiB; this is likely insufficient for model weights, HF caches, and checkpoints.")
    elif free_disk_gib < 150:
        recs.append("Free disk is tight. Keep only one model/checkpoint family locally and clean caches deliberately.")
    else:
        recs.append("Free disk looks adequate for datasets, one or more Qwen checkpoints, and experiment outputs.")

    return {
        "profile": profile,
        "gpu_count": gpu_count,
        "min_vram_gib": min_vram_gib,
        "gpu_names": gpu_names,
        "recommendations": recs,
        "suggested_commands": commands,
    }


def build_report(paths: list[str], repo: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "python": sys.version,
            "python_executable": sys.executable,
        },
        "repo": git_info(repo),
        "cpu": cpu_info(),
        "memory": memory_info(),
        "disk": disk_info(paths),
        "nvidia_smi": nvidia_smi_info(),
        "torch": torch_info(),
        "packages": package_versions(),
    }
    report["opsd_recommendation"] = recommendations(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    rec = report["opsd_recommendation"]
    lines = [
        "# Hardware Analysis Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Hostname: `{report['hostname']}`",
        f"- Repo branch: `{report['repo'].get('branch')}`",
        f"- Repo commit: `{report['repo'].get('commit')}`",
        f"- Recommended profile: `{rec['profile']}`",
        "",
        "## System",
        "",
        f"- OS: {report['platform']['system']} {report['platform']['release']}",
        f"- Python: `{report['platform']['python_executable']}`",
        f"- Logical CPUs: {report['cpu'].get('logical_cpus')}",
        f"- RAM total GiB: {report['memory'].get('total_gib')}",
        f"- RAM available GiB: {report['memory'].get('available_gib')}",
        "",
        "## GPUs",
        "",
    ]
    if rec["gpu_count"] == 0:
        lines.append("- No CUDA GPU detected by PyTorch or `nvidia-smi`.")
    else:
        lines.append(f"- GPU count: {rec['gpu_count']}")
        lines.append(f"- Minimum VRAM GiB: {rec['min_vram_gib']}")
        for name in rec["gpu_names"]:
            lines.append(f"- GPU: {name}")
    lines.extend(["", "## Disk", ""])
    for row in report["disk"]:
        if "error" in row:
            lines.append(f"- `{row['path']}`: error: {row['error']}")
        else:
            lines.append(
                f"- `{row['path']}`: free {row['free_gib']} GiB / total {row['total_gib']} GiB"
            )
    lines.extend(["", "## Package Versions", ""])
    for name, version in report["packages"].items():
        lines.append(f"- `{name}`: {version}")
    lines.extend(["", "## OPSD Recommendations", ""])
    for item in rec["recommendations"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Suggested Commands", ""])
    for command in rec["suggested_commands"]:
        lines.extend(["```bash", command, "```"])
    lines.extend(
        [
            "",
            "## Evidence Note",
            "",
            "This report is a hardware/setup probe. It is not a training or evaluation result and must not be labeled `[My reproduced result]` unless tied to a completed experiment log.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze hardware resources for OPSD reproduction.")
    parser.add_argument(
        "--output-dir",
        default="reproduction/hardware_reports",
        help="Directory for JSON and Markdown reports.",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=None,
        help="Additional path whose disk usage should be probed. Can be repeated.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print Markdown to stdout without writing report files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON to stdout instead of Markdown.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(__file__).resolve().parents[1]
    paths = args.path or [str(repo), str(repo / ".cache"), str(repo / "outputs")]
    report = build_report(paths, repo)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(markdown_report(report))

    if not args.no_write:
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = repo / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"hardware_report_{timestamp}.json"
        md_path = output_dir / f"hardware_report_{timestamp}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(markdown_report(report), encoding="utf-8")
        print(f"\nWrote JSON report: {json_path}")
        print(f"Wrote Markdown report: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
