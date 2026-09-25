"""M2-R1 supplementary probe: can a font-less QPA platform be given fonts?

The main matrix (``02/03/04-probe-*.log``) establishes the *default* state:
``offscreen`` and ``minimal`` ship an empty ``QFontDatabase``. This probe
measures the boundary of that finding — whether a fontless platform can be
made to render real glyphs, and by which mechanism:

  ``baseline``  no remediation (control; must reproduce the matrix result)
  ``fontdir``   ``QT_QPA_FONTDIR`` pointed at a real font directory *before*
                ``QGuiApplication`` is constructed
  ``appfont``   ``QFontDatabase.addApplicationFont()`` with one real font file

This is a feasibility boundary measurement only. It chooses no production
font strategy (AD-001 §34) and changes no production code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from qt_platform_probe import (  # noqa: E402
    PAGE_H,
    PAGE_W,
    TEXT,
    VERTICAL_TEXT,
    image_diff_stats,
    make_png,
    sha256,
    window_census,
)


def render_probe(workdir: Path, label: str) -> dict:
    """Run the production layout + compositor path and measure the output."""
    from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics, QImage

    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine
    from ports.rendering.direction import TextDirection
    from ports.rendering.ports import LayoutRequest, RenderOp

    catalog = QtFontCatalog()
    resolved = catalog.resolve("Source Han Sans K Bold")

    font = QFont(resolved.resolved_family)
    font.setPixelSize(32)
    fm = QFontMetrics(font)

    engine = QtTextLayoutEngine(catalog)
    horizontal = engine.layout(
        LayoutRequest(
            text=TEXT,
            font_family="Source Han Sans K Bold",
            font_size=32.0,
            direction=TextDirection.HORIZONTAL,
            box_width=PAGE_W - 40,
            box_height=80,
            stroke_width=2.0,
        )
    )
    vertical = engine.layout(
        LayoutRequest(
            text=VERTICAL_TEXT,
            font_family="Source Han Sans K Bold",
            font_size=28.0,
            direction=TextDirection.VERTICAL,
            box_width=120,
            box_height=PAGE_H - 40,
            stroke_width=2.0,
        )
    )

    base_png = make_png(PAGE_W, PAGE_H, (255, 255, 255))
    op_h = RenderOp(
        items=horizontal.items,
        region_x=20,
        region_y=20,
        region_width=520,
        region_height=90,
        font_family=resolved.resolved_family,
        font_size=32.0,
        text_color="#000000",
        stroke_enabled=True,
        stroke_color="#ffffff",
        stroke_width=2.0,
        direction=TextDirection.HORIZONTAL,
        text_align="start",
    )
    page_png = QtImageCompositor().compose_page(base_png, (op_h,))
    (workdir / f"output_page_{label}.png").write_bytes(page_png)
    page_img = QImage.fromData(page_png)
    base_img = QImage.fromData(base_png)

    return {
        "label": label,
        "families_count": len(list(QFontDatabase.families())),
        "hasFamily_MicrosoftYaHei": bool(QFontDatabase.hasFamily("Microsoft YaHei")),
        "hasFamily_Arial": bool(QFontDatabase.hasFamily("Arial")),
        "resolved_family_for_requested": resolved.resolved_family,
        "font_available_flag": bool(resolved.available),
        "metrics": {
            "family": font.family(),
            "height": fm.height(),
            "ascent": fm.ascent(),
            "descent": fm.descent(),
            "advance_cjk_4chars": fm.horizontalAdvance("漫画排版"),
            "advance_latin_Manga": fm.horizontalAdvance("Manga"),
            "inFont_cjk": bool(fm.inFont("漫")),
        },
        "layout_horizontal": {
            "item_count": len(horizontal.items),
            "extents_width": horizontal.extents_width,
            "extents_height": horizontal.extents_height,
            "fits": bool(horizontal.fits),
            "font_available": bool(horizontal.font_available),
        },
        "layout_vertical": {
            "item_count": len(vertical.items),
            "extents_width": vertical.extents_width,
            "extents_height": vertical.extents_height,
        },
        "compose_page": {
            "output_png_sha256": sha256(page_png),
            "output_png_bytes": len(page_png),
            "diff_vs_white_input": image_diff_stats(base_img, page_img),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True)
    parser.add_argument("--mode", required=True, choices=("baseline", "fontdir", "appfont"))
    parser.add_argument("--fontdir", default=r"C:\Windows\Fonts")
    parser.add_argument("--font", default=r"C:\Windows\Fonts\msyh.ttc")
    parser.add_argument("--json", required=True)
    parser.add_argument("--workdir", required=True)
    args = parser.parse_args()

    os.environ["QT_QPA_PLATFORM"] = args.platform
    if args.mode == "fontdir":
        os.environ["QT_QPA_FONTDIR"] = args.fontdir
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "probe": "M2-R1 supplementary font-remediation probe",
        "platform": args.platform,
        "mode": args.mode,
        "fontdir_env": os.environ.get("QT_QPA_FONTDIR"),
        "font_file": args.font if args.mode == "appfont" else None,
        "pid": os.getpid(),
        "python": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "errors": [],
        "exit_code": None,
    }
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    try:
        import PySide6
        from PySide6.QtCore import qVersion
        from PySide6.QtGui import QFontDatabase, QGuiApplication

        report["PySide6.__version__"] = PySide6.__version__
        report["qVersion"] = qVersion()

        app = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
        report["platformName"] = app.platformName()
        report["screen_count"] = len(app.screens())

        report["after_app_construction"] = {
            "families_count": len(list(QFontDatabase.families())),
            "families_sample": list(QFontDatabase.families())[:10],
        }

        if args.mode == "appfont":
            font_id = QFontDatabase.addApplicationFont(args.font)
            report["addApplicationFont"] = {
                "font_id": font_id,
                "loaded": font_id != -1,
                "families_for_id": QFontDatabase.applicationFontFamilies(font_id) if font_id != -1 else [],
                "families_count_after": len(list(QFontDatabase.families())),
                "font_file_exists": Path(args.font).exists(),
                "font_file_bytes": Path(args.font).stat().st_size if Path(args.font).exists() else None,
            }

        report["render"] = render_probe(workdir, f"{args.platform}_{args.mode}")
        report["window_census"] = window_census(report["pid"])
    except BaseException as exc:  # noqa: BLE001
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["traceback"] = traceback.format_exc()

    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    report["exit_code"] = 0 if not report["errors"] else 2
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"[supp] platform={args.platform} mode={args.mode} "
        f"errors={len(report['errors'])} exit_code={report['exit_code']}"
    )
    for err in report["errors"]:
        print(f"[supp] ERROR {err}")
    return report["exit_code"]


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        code = 3
    sys.exit(code)
