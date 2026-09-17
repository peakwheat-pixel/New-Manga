"""TASK-018 inpainting route probe + baseline measurement (revision slice).

Revision scope (Review R-001/R-002/R-003/R-006/R-007):

* **R-007 fail-closed** — routing dispatches through an explicit
  ``FILLERS`` mapping. A route with no registered implementation is
  ``BLOCKED`` with ``blocked_stage="not_implemented"`` **even when every
  dependency is satisfied**; there is no fallback to ``edge_bleed_fill``.
* **R-002 real probing** — ``requirements`` are *descriptors* probed at run
  time (``module`` via ``importlib.util.find_spec``, ``weight`` via the
  existence of the local file named by an environment variable). The route
  status is derived from probe results, never from a static boolean.
  ``blocked_stage`` distinguishes ``dependency`` from ``not_implemented``.
* **R-003 out-of-root output dir** — an output directory outside the
  experiment root no longer raises; the recorded path falls back to an
  absolute path and the fact is recorded explicitly.
* **R-006 data labels** — no unverified size annotations ("several GB",
  "10GB+") remain in requirement keys or notes. ``size_class`` is retained
  only as a *relative, unmeasured* tier and is labelled as such.
* **R-001 residual** — every ``protected_boxes`` entry from the manifest is
  asserted individually; each measured record carries
  ``protected_box_violations``.

Only dependency-free baselines are executed. Learned routes are never run and
never produce an output image here.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
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

#: R-007: the ONLY routes this harness can execute. Anything absent from this
#: mapping is fail-closed — there is deliberately no default implementation.
FILLERS = {
    "simple-fill": lambda pixels, mask: simple_fill(pixels, mask, fill=(255, 255, 255)),
    "edge-bleed": lambda pixels, mask: edge_bleed_fill(pixels, mask, iterations=8),
}

#: R-002: requirement descriptors. ``module`` is probed with
#: ``importlib.util.find_spec``; ``weight`` is probed by testing whether the
#: path named by ``env`` exists on this machine.
REQ_MODULE = "module"
REQ_WEIGHT = "weight"


def _module_req(name: str) -> dict[str, str]:
    return {"type": REQ_MODULE, "name": name}


def _weight_req(env: str, label: str) -> dict[str, str]:
    return {"type": REQ_WEIGHT, "env": env, "label": label}


#: candidate routes required by TASK-018 AC-1. ``size_class`` is a **relative,
#: unmeasured** tier used only for the resource discussion (AC-3); it is never
#: a measured figure and carries no volume number.
ROUTES: dict[str, dict[str, object]] = {
    "simple-fill": {
        "label": "Simple Fill (constant colour)",
        "kind": "baseline",
        "learned": False,
        "implementation": "simple_fill",
        "requirements": [],
        "size_class": "none (unmeasured tier)",
        "default_eligible": True,
        "note": "纯几何填充；无模型、无权重、无 GPU 需求",
    },
    "edge-bleed": {
        "label": "Edge bleed (orthogonal-neighbour mean diffusion)",
        "kind": "baseline",
        "learned": False,
        "implementation": "edge_bleed_fill",
        "requirements": [],
        "size_class": "none (unmeasured tier)",
        "default_eligible": True,
        "note": "非模型基线，仅用于结构对照；不得当作学习型修复结果",
    },
    "manga-lama": {
        "label": "Manga LaMa",
        "kind": "learned",
        "learned": True,
        "implementation": None,
        "requirements": [
            _module_req("torch"),
            _weight_req("TASK018_MANGA_LAMA_WEIGHTS", "manga-lama weights"),
        ],
        "size_class": "medium (unmeasured tier)",
        "default_eligible": False,
        "note": "漫画专用 LaMa 权重；需要 torch 与本地权重文件。本 harness 未实现该路线。",
    },
    "aot": {
        "label": "AOT-GAN",
        "kind": "learned",
        "learned": True,
        "implementation": None,
        "requirements": [
            _module_req("torch"),
            _weight_req("TASK018_AOT_WEIGHTS", "aot weights"),
        ],
        "size_class": "medium (unmeasured tier)",
        "default_eligible": False,
        "note": "AOT-GAN 修复权重；需要 torch 与本地权重文件。本 harness 未实现该路线。",
    },
    "brushnet-powerpaint": {
        "label": "BrushNet / PowerPaint",
        "kind": "learned",
        "learned": True,
        "implementation": None,
        "requirements": [
            _module_req("torch"),
            _module_req("diffusers"),
            _weight_req("TASK018_BRUSHNET_WEIGHTS", "brushnet weights"),
        ],
        "size_class": "large (unmeasured tier)",
        "default_eligible": False,
        "note": "扩散式修复；需要 torch、diffusers 与本地权重文件。本 harness 未实现该路线。",
    },
    "flux": {
        "label": "FLUX (inpaint / fill)",
        "kind": "learned",
        "learned": True,
        "implementation": None,
        "requirements": [
            _module_req("torch"),
            _module_req("diffusers"),
            _weight_req("TASK018_FLUX_WEIGHTS", "flux weights"),
        ],
        "size_class": "very-large (unmeasured tier)",
        "default_eligible": False,
        "note": "大型扩散模型；需要 torch、diffusers 与本地权重文件。本 harness 未实现该路线。",
    },
}

BLOCKED_STAGE_DEPENDENCY = "dependency"
BLOCKED_STAGE_NOT_IMPLEMENTED = "not_implemented"


def probe_requirement(requirement: dict[str, str]) -> dict[str, object]:
    """R-002: probe one descriptor against the real environment."""
    kind = requirement.get("type")
    if kind == REQ_MODULE:
        name = str(requirement["name"])
        try:
            present = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            present = False
        return {"descriptor": dict(requirement), "satisfied": present, "probe": "importlib.util.find_spec"}
    if kind == REQ_WEIGHT:
        env = str(requirement["env"])
        value = os.environ.get(env)
        path = Path(value) if value else None
        present = bool(value) and path is not None and path.exists()
        return {
            "descriptor": dict(requirement),
            "satisfied": present,
            "probe": "local file existence via environment variable",
            "env_var_set": bool(value),
        }
    return {"descriptor": dict(requirement), "satisfied": False, "probe": "unknown descriptor type"}


def route_gate(route: str) -> dict[str, object]:
    """R-002 + R-007: decide runnability from probes, fail closed on implementability.

    Order matters: **implementability is checked first**, so a route whose
    dependencies happen to be satisfied is still blocked while this harness has
    no implementation for it (R-007). The result never authorises a fallback.
    """
    if route not in ROUTES:
        return {
            "route": route,
            "runnable": False,
            "blocked_stage": BLOCKED_STAGE_NOT_IMPLEMENTED,
            "reason": f"unknown route: {route}",
            "probes": [],
            "missing": [],
        }
    info = ROUTES[route]
    probes = [probe_requirement(req) for req in info["requirements"]]  # type: ignore[arg-type]
    missing = [p["descriptor"].get("label") or p["descriptor"].get("name") or p["descriptor"].get("env") for p in probes if not p["satisfied"]]

    if info["implementation"] is None:
        return {
            "route": route,
            "runnable": False,
            "blocked_stage": BLOCKED_STAGE_NOT_IMPLEMENTED,
            "reason": "not implemented in this harness (no registered filler); dependency state is irrelevant",
            "probes": probes,
            "missing": missing,
        }
    if missing:
        return {
            "route": route,
            "runnable": False,
            "blocked_stage": BLOCKED_STAGE_DEPENDENCY,
            "reason": "missing dependency/weight: " + ", ".join(str(m) for m in missing),
            "probes": probes,
            "missing": missing,
        }
    return {
        "route": route,
        "runnable": True,
        "blocked_stage": None,
        "reason": "ready",
        "probes": probes,
        "missing": [],
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


def _sha256_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _display_path(path: Path) -> tuple[str, bool]:
    """R-003: never raise for an out-of-root output path.

    Returns ``(display_path, inside_experiment_root)``. When the path cannot be
    expressed relative to the experiment root, the absolute path is recorded
    instead of raising ``ValueError``.
    """
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/"), True
    except ValueError:
        return str(path.resolve()).replace("\\", "/"), False


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


def protected_box_violations(
    before, after, protected_boxes
) -> list[dict[str, object]]:
    """R-001 residual: assert every manifest ``protected_boxes`` entry.

    Reports one record per box with the number of changed pixels inside it, so
    the AC-2 protection evidence is per-box rather than a single aggregate.
    """
    results: list[dict[str, object]] = []
    for box in protected_boxes:
        x0, y0, x1, y1 = (int(v) for v in box)
        changed = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                if before[y][x] != after[y][x]:
                    changed += 1
        results.append({"box": [x0, y0, x1, y1], "changed_pixels": changed, "violated": changed > 0})
    return results


def _evaluate_route(route: str, pixels, mask, *, repeat: int) -> dict[str, object]:
    """Execute a route through the explicit ``FILLERS`` mapping (R-007).

    The lookup is unconditional: an unregistered route raises instead of
    silently falling back to another implementation.
    """
    filler = FILLERS.get(route)
    if filler is None:
        raise KeyError(f"no registered filler for route {route!r}; refusing to substitute another implementation")
    ink_before = ink_pixels_inside(pixels, mask)
    peak_before = _rss_mb()
    durations: list[float] = []
    after = pixels
    for _ in range(max(1, repeat)):
        started = time.perf_counter()
        after = filler(pixels, mask)
        durations.append(round((time.perf_counter() - started) * 1000, 3))
    peak_after = _rss_mb()
    return {
        "status": "MEASURED",
        "filler": ROUTES[route]["implementation"],
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
    out_display, out_in_root = _display_path(out_dir)
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
        protected_boxes = sample.get("protected_boxes", [])
        for route in routes:
            info = ROUTES.get(route)
            gate = route_gate(route)
            record: dict[str, object] = {
                "sample_id": sample["sample_id"],
                "sample_kind": sample["kind"],
                "sample_sha256": sample["sha256"],
                "route": route,
                "route_label": (info or {}).get("label"),
                "route_kind": (info or {}).get("kind", "unknown"),
                "learned_model": (info or {}).get("learned", False),
                "size_class": (info or {}).get("size_class", "unknown"),
                "default_eligible": (info or {}).get("default_eligible", False),
                "mask": mask_meta,
                "parameters": {
                    **DEFAULT_MASK_PARAMS,
                    "fill_colour": [255, 255, 255],
                    "edge_bleed_iterations": 8,
                },
                "protected_boxes": [list(box) for box in protected_boxes],
            }
            if not gate["runnable"]:
                record.update({
                    "status": "BLOCKED",
                    "blocked_stage": gate["blocked_stage"],
                    "reason": gate["reason"],
                    "requirement_probes": gate["probes"],
                    "latency_ms": None,
                    "peak_rss_mb_after": None,
                    "vram_peak_mb": None,
                    "residual_text_pixels_after": "NOT_RUN",
                    "protected_violations": "NOT_RUN",
                    "protected_box_violations": "NOT_RUN",
                    "output_image": None,
                })
                records.append(record)
                continue

            measured = _evaluate_route(route, pixels, final_mask, repeat=repeat)
            after = measured.pop("_after")
            out_image = out_dir / f"{sample['sample_id']}__{route}.png"
            _save_pixels(after, out_image)
            image_display, image_in_root = _display_path(out_image)
            record.update(measured)
            record["output_image"] = image_display
            record["output_image_in_experiment_root"] = image_in_root
            record["output_sha256"] = _sha256(out_image)
            record["mask_sha256"] = _sha256_json(mask_meta)
            record["protected_box_violations"] = protected_box_violations(pixels, after, protected_boxes)
            records.append(record)

    report = {
        "schema": "task018-experiment-v2",
        "harness": "experiments/TASK-018/run_experiment.py",
        "manifest_sha256": _sha256(manifest_path),
        "repeat": repeat,
        "output_dir": out_display,
        "output_dir_in_experiment_root": out_in_root,
        "routes": {
            name: {
                **{k: v for k, v in info.items() if k != "requirements"},
                "requirements": [dict(req) for req in info["requirements"]],
                "gate": route_gate(name),
                "runnable_here": route_gate(name)["runnable"],
                "blocked_stage": route_gate(name)["blocked_stage"],
                "blocked_reason": None if route_gate(name)["runnable"] else route_gate(name)["reason"],
            }
            for name, info in ROUTES.items()
        },
        "records": records,
    }
    out_path = out_dir / "experiment.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[str(record["status"])] = counts.get(str(record["status"]), 0) + 1
    print(json.dumps({
        "output": str(out_path),
        "counts": counts,
        "output_dir_in_experiment_root": out_in_root,
    }, ensure_ascii=False))
    return report


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
