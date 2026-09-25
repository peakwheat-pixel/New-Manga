"""M2-R1 isolated Qt runtime probe (research only; no production code path).

One process = one QT_QPA_PLATFORM. The probe imports the *production* Qt
adapters read-only (``infrastructure.rendering.{font_catalog,qt_layout,
qt_compositor}``) and exercises, in order:

  1. ``QGuiApplication`` construction on the requested platform
  2. ``QFontDatabase`` family coverage and the production ``QtFontCatalog``
  3. the production ``QtTextLayoutEngine`` (horizontal + vertical)
  4. the production ``QtImageCompositor`` (page + region composition)
  5. visible-window census for this PID (no-visible-GUI evidence)

Nothing here touches the user data root, the SQLite database or
``bootstrap.app``. Output is a single JSON document plus optional PNG
artifacts under ``--workdir``.

Run only with the isolated experiment interpreter; see
``01-environment.log``.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import struct
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"

PAGE_W, PAGE_H = 600, 200
TEXT = "漫画排版テスト Manga"
VERTICAL_TEXT = "縦書きテスト"


# ----------------------------------------------------------------------
# deterministic PNG fixture (stdlib only, byte-identical every run)
# ----------------------------------------------------------------------
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def make_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    row = bytes(rgb) * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ----------------------------------------------------------------------
# no-visible-GUI evidence
# ----------------------------------------------------------------------
def window_census(pid: int) -> dict:
    """Top-level HWND census for this process (Windows only)."""
    user32 = ctypes.windll.user32
    total = 0
    visible = 0
    details: list[str] = []
    proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def _cb(hwnd, _lparam):  # noqa: ANN001
        nonlocal total, visible
        wpid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid:
            total += 1
            if user32.IsWindowVisible(hwnd):
                visible += 1
                length = user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                details.append(f"hwnd={int(hwnd):#x} visible title={buf.value!r}")
        return True

    user32.EnumWindows(proc(_cb), 0)
    return {"top_level_windows": total, "visible_windows": visible, "visible_details": details}


# ----------------------------------------------------------------------
# pixel comparison helpers
# ----------------------------------------------------------------------
def image_diff_stats(a, b) -> dict:  # noqa: ANN001 - QImage
    from PySide6.QtGui import QImage

    a = a.convertToFormat(QImage.Format.Format_ARGB32)
    b = b.convertToFormat(QImage.Format.Format_ARGB32)
    if a.size() != b.size():
        return {"comparable": False, "size_a": [a.width(), a.height()], "size_b": [b.width(), b.height()]}
    stride_a, stride_b = a.bytesPerLine(), b.bytesPerLine()
    raw_a, raw_b = bytes(a.constBits()), bytes(b.constBits())
    width, height = a.width(), a.height()
    differing = 0
    for y in range(height):
        row_a = raw_a[y * stride_a : y * stride_a + width * 4]
        row_b = raw_b[y * stride_b : y * stride_b + width * 4]
        if row_a == row_b:
            continue
        for x in range(width):
            if row_a[x * 4 : x * 4 + 4] != row_b[x * 4 : x * 4 + 4]:
                differing += 1
    # non-background (non-white) pixels in b, using the same ARGB32 buffer
    non_white = 0
    for y in range(height):
        row_b = raw_b[y * stride_b : y * stride_b + width * 4]
        for x in range(width):
            px = row_b[x * 4 : x * 4 + 4]
            if px[:3] != b"\xff\xff\xff":
                non_white += 1
    return {
        "comparable": True,
        "width": width,
        "height": height,
        "total_pixels": width * height,
        "differing_pixels": differing,
        "non_white_pixels_in_b": non_white,
    }


# ----------------------------------------------------------------------
# main probe
# ----------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--workdir", required=True)
    args = parser.parse_args()

    os.environ["QT_QPA_PLATFORM"] = args.platform
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "probe": "M2-R1 qt_platform_probe",
        "platform_requested": args.platform,
        "pid": os.getpid(),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "python": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "frozen": bool(getattr(sys, "frozen", False)),
        "cwd": os.getcwd(),
        "steps": [],
        "errors": [],
        "exit_code": None,
    }

    def step(name: str, fn):  # noqa: ANN001, ANN202
        t0 = time.perf_counter()
        entry = {"step": name}
        try:
            entry["result"] = fn()
            entry["ok"] = True
        except BaseException as exc:  # noqa: BLE001 - a probe must capture everything
            entry["ok"] = False
            entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["traceback"] = traceback.format_exc()
            report["errors"].append({"step": name, "error": entry["error"]})
        entry["seconds"] = round(time.perf_counter() - t0, 4)
        report["steps"].append(entry)
        return entry.get("result")

    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    # ---- 1. QGuiApplication -------------------------------------------
    state: dict = {}

    def build_app() -> dict:
        import PySide6
        from PySide6.QtCore import qVersion
        from PySide6.QtGui import QGuiApplication

        info = {
            "PySide6.__version__": PySide6.__version__,
            "qVersion": qVersion(),
        }
        app = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
        info["app_created_by_probe"] = QGuiApplication.instance() is not None
        info["platformName"] = app.platformName()
        info["screens"] = [
            {
                "name": s.name(),
                "geometry": [s.geometry().x(), s.geometry().y(), s.geometry().width(), s.geometry().height()],
                "devicePixelRatio": s.devicePixelRatio(),
            }
            for s in app.screens()
        ]
        info["screen_count"] = len(app.screens())
        info["topLevelWindows"] = len(app.topLevelWindows())
        state["app"] = app
        return info

    step("QGuiApplication", build_app)

    # ---- 2. QFontDatabase + production QtFontCatalog -------------------
    def font_database() -> dict:
        from PySide6.QtGui import QFont, QFontDatabase

        families = list(QFontDatabase.families())
        probe_families = [
            "Source Han Sans K Bold",
            "Source Han Sans Bold",
            "Microsoft YaHei",
            "SimSun",
            "Arial",
        ]
        return {
            "family_count": len(families),
            "families_sample": families[:15],
            "hasFamily": {name: bool(QFontDatabase.hasFamily(name)) for name in probe_families},
            "default_QFont_family": QFont().family(),
            "systemFont_GeneralFont": QFontDatabase.systemFont(
                QFontDatabase.SystemFont.GeneralFont
            ).family(),
            "writingSystems": len(QFontDatabase.writingSystems()),
        }

    step("QFontDatabase", font_database)

    def font_catalog() -> dict:
        from infrastructure.rendering.font_catalog import QtFontCatalog

        catalog = QtFontCatalog()
        state["catalog"] = catalog
        out = {}
        for wanted in ("Source Han Sans K Bold", "Missing Family XYZ"):
            resolved = catalog.resolve(wanted)
            out[wanted] = {
                "requested_family": resolved.requested_family,
                "resolved_family": resolved.resolved_family,
                "available": bool(resolved.available),
            }
        return out

    step("QtFontCatalog.resolve", font_catalog)

    # ---- 3. production QtTextLayoutEngine ------------------------------
    def metrics_probe() -> dict:
        from PySide6.QtGui import QFont, QFontMetrics

        catalog = state.get("catalog")
        family = None
        if catalog is not None:
            family = catalog.resolve("Source Han Sans K Bold").resolved_family
        font = QFont(family or "")
        font.setPixelSize(32)
        fm = QFontMetrics(font)
        return {
            "family_used": font.family(),
            "pixel_size": 32,
            "height": fm.height(),
            "ascent": fm.ascent(),
            "descent": fm.descent(),
            "advance_latin": fm.horizontalAdvance("Manga"),
            "advance_cjk": fm.horizontalAdvance("漫画排版"),
            "advance_space": fm.horizontalAdvance(" "),
            "inFont_cjk": fm.inFont("漫"),
        }

    step("QFontMetrics", metrics_probe)

    def text_layout() -> dict:
        from infrastructure.rendering.qt_layout import QtTextLayoutEngine
        from ports.rendering.direction import TextDirection
        from ports.rendering.ports import LayoutRequest

        engine = QtTextLayoutEngine(state["catalog"])
        out = {}
        for label, request in (
            (
                "horizontal",
                LayoutRequest(
                    text=TEXT,
                    font_family="Source Han Sans K Bold",
                    font_size=32.0,
                    direction=TextDirection.HORIZONTAL,
                    box_width=PAGE_W - 40,
                    box_height=80,
                    stroke_width=2.0,
                ),
            ),
            (
                "vertical",
                LayoutRequest(
                    text=VERTICAL_TEXT,
                    font_family="Source Han Sans K Bold",
                    font_size=28.0,
                    direction=TextDirection.VERTICAL,
                    box_width=120,
                    box_height=PAGE_H - 40,
                    stroke_width=2.0,
                ),
            ),
        ):
            t0 = time.perf_counter()
            layout = engine.layout(request)
            out[label] = {
                "wall_seconds": round(time.perf_counter() - t0, 5),
                "item_count": len(layout.items),
                "extents_width": layout.extents_width,
                "extents_height": layout.extents_height,
                "fits": bool(layout.fits),
                "font_available": bool(layout.font_available),
                "resolved_family": layout.resolved_family,
                "first_items": [
                    {"text": i.text, "x": i.x, "y": i.y, "per_char": bool(i.per_char)}
                    for i in layout.items[:5]
                ],
            }
            state[f"layout_{label}"] = layout
        return out

    step("QtTextLayoutEngine.layout", text_layout)

    # ---- 4. production QtImageCompositor -------------------------------
    def composite() -> dict:
        from PySide6.QtGui import QImage

        from infrastructure.rendering.qt_compositor import QtImageCompositor
        from ports.rendering.direction import TextDirection
        from ports.rendering.ports import RenderOp

        base_png = make_png(PAGE_W, PAGE_H, (255, 255, 255))
        clean_png = make_png(PAGE_W, PAGE_H, (255, 255, 255))
        (workdir / "input_base.png").write_bytes(base_png)
        (workdir / "input_clean.png").write_bytes(clean_png)

        compositor = QtImageCompositor()
        resolved_family = state["catalog"].resolve("Source Han Sans K Bold").resolved_family
        horizontal = state["layout_horizontal"]
        vertical = state["layout_vertical"]

        op_h = RenderOp(
            items=horizontal.items,
            region_x=20,
            region_y=20,
            region_width=520,
            region_height=90,
            font_family=resolved_family,
            font_size=32.0,
            text_color="#000000",
            stroke_enabled=True,
            stroke_color="#ffffff",
            stroke_width=2.0,
            direction=TextDirection.HORIZONTAL,
            text_align="start",
        )
        op_v = RenderOp(
            items=vertical.items,
            region_x=460,
            region_y=110,
            region_width=120,
            region_height=80,
            font_family=resolved_family,
            font_size=28.0,
            text_color="#000000",
            stroke_enabled=False,
            stroke_color="#ffffff",
            stroke_width=0.0,
            direction=TextDirection.VERTICAL,
            text_align="start",
        )

        out: dict = {
            "input_base_png_sha256": sha256(base_png),
            "input_base_png_bytes": len(base_png),
            "input_clean_png_sha256": sha256(clean_png),
        }

        t0 = time.perf_counter()
        page_png = compositor.compose_page(base_png, (op_h, op_v))
        out["compose_page"] = {
            "wall_seconds": round(time.perf_counter() - t0, 5),
            "output_png_bytes": len(page_png),
            "output_png_sha256": sha256(page_png),
            "identical_to_input": sha256(page_png) == sha256(base_png),
        }
        (workdir / "output_page.png").write_bytes(page_png)

        base_img = QImage.fromData(base_png)
        page_img = QImage.fromData(page_png)
        out["compose_page"]["decoded_size"] = [page_img.width(), page_img.height()]
        out["compose_page"]["image_diff_vs_input"] = image_diff_stats(base_img, page_img)

        t0 = time.perf_counter()
        region_png = compositor.compose_region(base_png, clean_png, (20, 20, 520, 90), op_h)
        out["compose_region"] = {
            "wall_seconds": round(time.perf_counter() - t0, 5),
            "output_png_bytes": len(region_png),
            "output_png_sha256": sha256(region_png),
            "identical_to_input": sha256(region_png) == sha256(base_png),
        }
        (workdir / "output_region.png").write_bytes(region_png)
        region_img = QImage.fromData(region_png)
        out["compose_region"]["image_diff_vs_input"] = image_diff_stats(base_img, region_img)

        # deterministic re-run inside one process (idempotence signal)
        page_png_2 = compositor.compose_page(base_png, (op_h, op_v))
        out["compose_page"]["same_process_rerun_sha256_equal"] = (
            sha256(page_png_2) == sha256(page_png)
        )
        return out

    step("QtImageCompositor", composite)

    # ---- 5. no-visible-GUI census --------------------------------------
    step("window_census", lambda: window_census(report["pid"]))

    def qt_windows() -> dict:
        app = state.get("app")
        if app is None:
            return {"available": False}
        app.processEvents()
        return {
            "available": True,
            "topLevelWindows_after": len(app.topLevelWindows()),
        }

    step("eventLoopDrain", qt_windows)

    report["qt_log_platform_env"] = {
        "QT_QPA_PLATFORM": os.environ.get("QT_QPA_PLATFORM"),
        "QT_QPA_PLATFORM_PLUGIN_PATH": os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"),
        "QT_LOGGING_RULES": os.environ.get("QT_LOGGING_RULES"),
        "QT_QPA_FONTDIR": os.environ.get("QT_QPA_FONTDIR"),
    }
    report["workdir"] = str(workdir)
    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    report["exit_code"] = 0 if not report["errors"] else 2

    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # human-readable summary on stdout
    print(f"[probe] platform={args.platform} platformName={report['steps'][0].get('result', {}).get('platformName')}")
    for entry in report["steps"]:
        status = "OK  " if entry["ok"] else "FAIL"
        print(f"[probe] {status} {entry['step']} ({entry['seconds']}s){'' if entry['ok'] else ' -> ' + entry.get('error', '')}")
    print(f"[probe] errors={len(report['errors'])} exit_code={report['exit_code']}")
    return report["exit_code"]


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        code = 3
    sys.exit(code)
