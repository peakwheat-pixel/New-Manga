"""TASK-018 inpainting route probe + Simple Fill measurement.

Runs the *fixed* five samples through every candidate route. A route that lacks
its dependency or weights is recorded ``BLOCKED`` with a concrete reason and
**no** fabricated image, timing or quality number.

The only routes actually executed here are dependency-free baselines:

* ``simple-fill``      — constant-colour fill (the document's "Simple Fill")
* ``edge-bleed``       — nearest-neighbour diffusion, an explicit **non-model**
                         structural baseline used for comparison only

Everything else (Manga LaMa, AOT, BrushNet/PowerPaint, FLUX) is a learned model
that cannot be fetched in this environment; those are reported as ``BLOCKED``.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import time
from pathlib import Path

from PySide6.QtGui import QColor, QImage

from mask_protocol import (
    DEFAULT_MASK_PARAMS,
    edge_bleed_fill,
    ink_pixels_inside,
    mask_records,
    protected_pixels,
    rect_mask,
    refine_mask,
    residual_text_pixels,
    simple_fill,
)

ROOT = Path(__file__).resolve().parent

#: candidate routes required by TASK-018 AC-1. ``kind`` distinguishes the
#: dependency-free baselines from learned models; ``size_class`` feeds the
#: resource discussion (AC-3).
ROUTES: dict[str, dict[str, object]] = {
    "simple-fill": {
        "label": "Simple Fill (constant colour)",
        "kind": "baseline",
        "learned": False,
        "requirements": {},
        "size_class": "none",
        "default_eligible": True,
        "note": "纯几何填充；无模型、无权重、无 GPU 需求",
    },
    "edge-bleed": {
        "label": "Edge bleed (nearest-neighbour diffusion)",
        "kind": "baseline",
        "learned": False,
        "requirements": {},
        "size_class": "none",
        "default_eligible": True,
        "note": "非模型基线，仅用于结构对照；不得当作学习型修复结果",
    },
    "manga-lama": {
        "label": "Manga LaMa",
        "kind": "learned",
        "learned": True,
        "requirements": {"torch": False, "manga_lama weights (HF)": False},
        "size_class": "medium",
        "default_eligible": False,
        "note": "漫画专用 LaMa 权重；需要 torch 与 HF 权重下载",
    },
    "aot": {
        "label": "AOT-GAN",
        "kind": "learned",
        "learned": True,
        "requirements": {"torch": False, "aot weights": False},
        "size_class": "medium",
        "default_eligible": False,
        "note": "AOT-GAN 修复权重；需要 torch 与权重文件",
    },
    "brushnet-powerpaint": {
        "label": "BrushNet / PowerPaint",
        "kind": "learned",
        "learned": True,
        "requirements": {"torch": False, "diffusers": False, "brushnet weights (HF)": False},
        "size_class": "large",
        "default_eligible": False,
        "note": "扩散式修复；依赖 diffusers 与数 GB 权重",
    },
    "flux": {
        "label": "FLUX (inpaint / fill)",
        "kind": "learned",
        "learned": True,
        "requirements": {"torch": False, "diffusers": False, "flux weights (HF, 10GB+)": False},
        "size_class": "very-large",
        "default_eligible": False,
        "note": "大型扩散模型；显存与权重规模远超本机可验证范围",
    },
}


def _rss_mb() -> float | None:
    """Peak working-set of this process on Windows.

    ``ctypes.windll.psapi.GetProcessMemoryInfo`` returns 0 (failure) on this
    platform; ``K32GetProcessMemoryInfo`` exported from ``kernel32`` works, so
    that entry point is used explicitly. Returns ``None`` when the call fails,
    in which case the record must report the metric as NOT_RUN rather than 0.
    """
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    try:
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        func = ctypes.WinDLL("kernel32").K32GetProcessMemoryInfo
        func.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        func.restype = ctypes.c_int
        if not func(handle, ctypes.byref(counters), counters.cb):
            return None
        return round(counters.PeakWorkingSetSize / 1024 / 1024, 2)
    except (AttributeError, OSError):
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _load_pixels(path: Path) -> tuple[list[list[tuple[int, int, int]]], int, int]:
    image = QImage(str(path))
    if image.isNull():
        raise RuntimeError(f"cannot read {path}")
    width, height = image.width(), image.height()
    pixels = [
        [(image.pixelColor(x, y).red(), image.pixelColor(x, y).green(), image.pixelColor(x, y).blue())
         for x in range(width)]
        for y in range(height)
    ]
    return pixels, width, height


def _save_pixels(pixels: list[list[tuple[int, int, int]]], path: Path) -> None:
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    image = QImage(width, height, QImage.Format_RGB32)
    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[y][x]
            image.setPixelColor(x, y, QColor(red, green, blue))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path), "PNG"):
        raise RuntimeError(f"failed to write {path}")


def _route_status(route: str) -> tuple[bool, str]:
    info = ROUTES[route]
    missing = [name for name, ok in dict(info["requirements"]).items() if not ok]
    if missing:
        return False, "missing dependency/weight: " + ", ".join(sorted(missing))
    return True, "ready"


def _evaluate_baseline(
    route: str, pixels, mask, *, repeat: int
) -> dict[str, object]:
    """Actually run a dependency-free baseline and measure it."""
    ink_before = ink_pixels_inside(pixels, mask)
    peak_before = _rss_mb()
    durations: list[float] = []
    after = pixels
    for _ in range(max(1, repeat)):
        started = time.perf_counter()
        if route == "simple-fill":
            after = simple_fill(pixels, mask, fill=(255, 255, 255))
        else:
            after = edge_bleed_fill(pixels, mask, iterations=8)
        durations.append(round((time.perf_counter() - started) * 1000, 3))
    peak_after = _rss_mb()
    return {
        "status": "MEASURED",
        "repeats": max(1, repeat),
        "latency_ms": durations,
        "latency_ms_min": min(durations),
        "latency_ms_max": max(durations),
        "peak_rss_mb_before": peak_before,
        "peak_rss_mb_after": peak_after,
        "vram_peak_mb": None,
        "vram_note": "baseline is CPU-only; no GPU allocation is made or measured",
        "ink_pixels_inside_mask_before": ink_before,
        "residual_text_pixels_after": residual_text_pixels(pixels, after, mask),
        "protected_violations": protected_pixels(pixels, after, mask),
        "_after": after,
    }


def run(manifest_path: Path, out_dir: Path, repeat: int, routes: list[str]) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    for sample in manifest["samples"]:
        sample_path = manifest_path.parent / sample["path"]
        pixels, width, height = _load_pixels(sample_path)
        raw_mask = rect_mask(width, height, sample["target_box"])
        final_mask = refine_mask(
            raw_mask,
            erode_radius=0,
            dilate_radius=int(DEFAULT_MASK_PARAMS["dilate_radius"]),
        )
        mask_meta = mask_records(raw_mask, final_mask, DEFAULT_MASK_PARAMS)
        for route in routes:
            info = ROUTES[route]
            runnable, reason = _route_status(route)
            record: dict[str, object] = {
                "sample_id": sample["sample_id"],
                "sample_kind": sample["kind"],
                "sample_sha256": sample["sha256"],
                "route": route,
                "route_label": info["label"],
                "route_kind": info["kind"],
                "learned_model": info["learned"],
                "size_class": info["size_class"],
                "default_eligible": info["default_eligible"],
                "mask": mask_meta,
                "parameters": {
                    **DEFAULT_MASK_PARAMS,
                    "fill_colour": [255, 255, 255],
                    "edge_bleed_iterations": 8,
                },
            }
            if not runnable:
                record.update({
                    "status": "BLOCKED",
                    "reason": reason,
                    "latency_ms": None,
                    "peak_rss_mb_after": None,
                    "vram_peak_mb": None,
                    "residual_text_pixels_after": "NOT_RUN",
                    "protected_violations": "NOT_RUN",
                    "output_image": None,
                })
                records.append(record)
                continue

            measured = _evaluate_baseline(route, pixels, final_mask, repeat=repeat)
            after = measured.pop("_after")
            out_image = out_dir / f"{sample['sample_id']}__{route}.png"
            _save_pixels(after, out_image)
            record.update(measured)
            record["output_image"] = str(out_image.relative_to(ROOT)).replace("\\", "/")
            record["output_sha256"] = _sha256(out_image)
            record["mask_sha256"] = _sha256_json(mask_meta)
            records.append(record)

    report = {
        "schema": "task018-experiment-v1",
        "harness": "experiments/TASK-018/run_experiment.py",
        "manifest_sha256": _sha256(manifest_path),
        "repeat": repeat,
        "routes": {
            name: {k: v for k, v in info.items() if k != "requirements"}
            | {"requirements": dict(info["requirements"]), "runnable_here": _route_status(name)[0], "blocked_reason": (None if _route_status(name)[0] else _route_status(name)[1])}
            for name, info in ROUTES.items()
        },
        "records": records,
    }
    out_path = out_dir / "experiment.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[str(record["status"])] = counts.get(str(record["status"]), 0) + 1
    print(json.dumps({"output": str(out_path), "counts": counts}, ensure_ascii=False))
    return report


def _sha256_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "samples" / "manifest.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--repeat", type=int, default=3, help="repetitions per measured route")
    parser.add_argument("--route", action="append", choices=[*ROUTES], default=None)
    args = parser.parse_args()
    routes = args.route or list(ROUTES)
    run(args.manifest, args.output_dir, args.repeat, routes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
