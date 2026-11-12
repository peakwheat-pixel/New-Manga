"""Repeatable synthetic microbenchmarks for the active Core image paths."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import io
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image, ImageDraw, __version__ as pillow_version

from infrastructure.providers.inpaint_routes import SimpleFillProvider
from infrastructure.rendering.pillow_rendering import (
    PillowFontCatalog,
    PillowImageCompositor,
    PillowTextLayoutEngine,
)
from ports.inpaint.ports import BooleanMask, ImageFrame, InpaintRequest, MaskRecord
from ports.rendering.direction import TextDirection
from ports.rendering.ports import LayoutRequest, RenderOp


def _git_value(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _measure(
    name, operation, *, repeats: int, iterations_per_sample: int, warmups: int = 2
) -> dict:
    for _ in range(warmups):
        for _ in range(iterations_per_sample):
            operation()
    wall_ms: list[float] = []
    cpu_ms: list[float] = []
    cpu_wall_percent: list[float] = []
    for _ in range(repeats):
        wall_start = time.perf_counter_ns()
        cpu_start = time.process_time_ns()
        for _ in range(iterations_per_sample):
            operation()
        cpu_elapsed = time.process_time_ns() - cpu_start
        wall_elapsed = time.perf_counter_ns() - wall_start
        cpu_ms.append(cpu_elapsed / iterations_per_sample / 1_000_000)
        wall_ms.append(wall_elapsed / iterations_per_sample / 1_000_000)
        cpu_wall_percent.append(cpu_elapsed / wall_elapsed * 100 if wall_elapsed else 0)
    ordered = sorted(wall_ms)
    p95 = ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]
    median_wall = statistics.median(wall_ms)
    median_cpu = statistics.median(cpu_ms)
    return {
        "name": name,
        "samples": repeats,
        "warmups": warmups,
        "operations_per_timed_sample": iterations_per_sample,
        "wall_ms": {
            "median": round(median_wall, 3),
            "p95_nearest_rank": round(p95, 3),
            "min": round(min(wall_ms), 3),
            "max": round(max(wall_ms), 3),
        },
        "process_cpu_ms_median": round(median_cpu, 3),
        "process_cpu_to_wall_percent_median": round(
            statistics.median(cpu_wall_percent), 1
        ),
        "operations_per_second_median": round(
            1000 / median_wall if median_wall else 0, 2
        ),
    }


def _system_memory() -> dict:
    try:
        import psutil

        process = psutil.Process()
        info = process.memory_info()
        memory = psutil.virtual_memory()
        return {
            "provider": "psutil",
            "process_rss_bytes": int(info.rss),
            "process_peak_rss_bytes": int(getattr(info, "peak_wset", info.rss)),
            "system_total_physical_bytes": int(memory.total),
            "system_available_physical_bytes_at_capture": int(memory.available),
        }
    except ImportError:
        return {"provider": "unavailable", "status": "NOT_MEASURED"}


def run(repeats: int, output: Path) -> dict:
    width, height = 720, 1080
    page = Image.new("RGBA", (width, height), (248, 248, 248, 255))
    draw = ImageDraw.Draw(page)
    for y in range(0, height, 120):
        draw.line((0, y, width, y), fill=(232, 232, 232, 255), width=1)
    stream = io.BytesIO()
    page.save(stream, format="PNG", optimize=False)
    page_png = stream.getvalue()
    page.close()

    catalog = PillowFontCatalog()
    layout_engine = PillowTextLayoutEngine(catalog)
    compositor = PillowImageCompositor(catalog)
    texts = ["合成測試 123 漫画ページ" for _ in range(8)]
    requests = [
        LayoutRequest(
            text=text,
            font_family="Arial",
            font_size=24,
            direction=TextDirection.HORIZONTAL,
            box_width=150,
            box_height=76,
            stroke_width=1,
            line_spacing=1.0,
            text_align="center",
        )
        for text in texts
    ]

    def layout_once():
        results = [layout_engine.layout(request) for request in requests]
        if len(results) != 8 or not all(result.items for result in results):
            raise RuntimeError("synthetic text layout produced an empty result")
        return results

    # Keep the font index/cache cold for this first call, then report warm repeats separately.
    cold_start = time.perf_counter_ns()
    cold_layout = layout_once()
    cold_layout_wall_ms = (time.perf_counter_ns() - cold_start) / 1_000_000
    if not all(result.fits for result in cold_layout):
        raise RuntimeError("synthetic text did not fit its declared region")

    ops = tuple(
        RenderOp(
            items=layout.items,
            region_x=30 + (index % 2) * 370,
            region_y=60 + (index // 2) * 240,
            region_width=300,
            region_height=120,
            font_family=layout.resolved_family,
            font_size=24,
            text_color="#202020",
            stroke_enabled=True,
            stroke_color="#ffffff",
            stroke_width=1,
            direction=TextDirection.HORIZONTAL,
            text_align="center",
        )
        for index, layout in enumerate(cold_layout)
    )

    pixels = bytes((245, 245, 245)) * (width * height)
    x0, x1 = 300, 420
    y0, y1 = 360, 600
    rows = tuple(
        tuple(x0 <= x < x1 and y0 <= y < y1 for x in range(width))
        for y in range(height)
    )
    mask = BooleanMask(width, height, rows)
    frame = ImageFrame(width, height, "rgb24", pixels)
    bbox = mask.bbox()
    if bbox is None:
        raise RuntimeError("synthetic inpaint mask is empty")
    record = MaskRecord(
        parameters=(("fixture", "synthetic-rectangle"),),
        raw_area=mask.area,
        final_area=mask.area,
        raw_bbox=bbox,
        final_bbox=bbox,
        final_covers_raw=True,
        source="audit10-synthetic",
    )
    request = InpaintRequest(
        page_id="audit10-synthetic-page",
        region_id="audit10-synthetic-region",
        image=frame,
        raw_mask=mask,
        final_mask=mask,
        route="simple-fill",
        mask_record=record,
    )
    provider = SimpleFillProvider()

    def decode_once():
        decoded = compositor._open(page_png)
        size = decoded.size
        decoded.close()
        if size != (width, height):
            raise RuntimeError(f"decoded image has unexpected dimensions: {size}")

    def layout_warm_once():
        layout_once()

    def render_once():
        rendered = compositor.compose_page(page_png, ops)
        if not rendered.startswith(b"\x89PNG") or len(rendered) == 0:
            raise RuntimeError("production compositor returned an invalid PNG")

    def inpaint_once():
        result = provider.inpaint(request)
        offset = (y0 * width + x0) * 3
        if result.image.data[offset:offset + 3] == pixels[offset:offset + 3]:
            raise RuntimeError("simple-fill left the masked sample unchanged")

    results = [
        _measure("decode_png_720x1080", decode_once, repeats=repeats, iterations_per_sample=32),
        _measure("layout_8_cjk_regions_cached_font", layout_warm_once, repeats=repeats, iterations_per_sample=32),
        _measure("compose_page_8_regions_720x1080", render_once, repeats=repeats, iterations_per_sample=8),
        _measure("simple_fill_720x1080_3_7pct_mask", inpaint_once, repeats=repeats, iterations_per_sample=4),
    ]
    return {
        "audit": "AUDIT-10",
        "status": "MEASURED_SYNTHETIC_MICROBENCH_ONLY",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "generated_head": _git_value("rev-parse", "HEAD"),
        "branch": _git_value("branch", "--show-current"),
        "command": [sys.executable, str(Path(__file__).relative_to(ROOT)), "--samples", str(repeats), "--output", str(output)],
        "environment": {
            "platform": platform.platform(),
            "processor": platform.processor() or "UNKNOWN",
            "logical_cpu_count": os.cpu_count(),
            "python": sys.version,
            "pillow": pillow_version,
            "memory": _system_memory(),
        },
        "fixture": {
            "source": "generated in memory by this audit script; no user files read",
            "page_dimensions": [width, height],
            "page_png_bytes": len(page_png),
            "render_regions": len(ops),
            "inpaint_mask_pixels": mask.area,
            "inpaint_mask_percent": round(mask.area / (width * height) * 100, 3),
        },
        "font_cold_start": {
            "operation": "layout_8_cjk_regions_first_call_in_fresh_process",
            "wall_ms": round(cold_layout_wall_ms, 3),
            "process_cpu_ms": "NOT_MEASURED (single-call timer resolution is too coarse)",
        },
        "warm_workloads": results,
        "memory_after_workloads": _system_memory(),
        "excluded": [
            "GUI, database/disk I/O, image import/export, OCR/translation models, network APIs, learned inpaint models, multi-hour soak, user libraries",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.samples < 5:
        parser.error("--samples must be >= 5")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = run(args.samples, args.output)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
