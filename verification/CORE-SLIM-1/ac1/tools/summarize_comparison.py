"""CORE-SLIM-1 / AC1 — render ``comparison.json`` as a human-readable gap table.

Reads the machine comparison produced by
``verification/CORE-SLIM-1/ac1/tools/capture_decode_paths.py --compare`` and
writes ``comparison/COMPARISON.md`` (matrix + parity tables + the documented
AVIF capability note).
"""

from __future__ import annotations

import json
from pathlib import Path

AC1 = Path(__file__).resolve().parents[1]
report = json.loads((AC1 / "comparison.json").read_text(encoding="utf-8"))

lines: list[str] = []
lines.append("# AC1 — Qt 参考 vs Pillow 替代：解码/像素等价报告")
lines.append("")
lines.append(
    "采集方式：`tools/capture_decode_paths.py --impl qt`（改前，PySide6 实现）与 "
    "`--impl pillow`（改后，Pillow 实现）跑同一批确定性 fixtures，"
    "再由 `--compare` 逐项比较；原始数据见 `qt/results.json`、`pillow/results.json`、"
    "`comparison.json`，输入指纹见 `fixtures-manifest.json`。"
)
lines.append("")
summary = report["summary"]
lines.append("## 汇总")
lines.append("")
lines.append("| 维度 | 结果 |")
lines.append("|---|---|")
lines.append(f"| 解码矩阵（尺寸/MIME/成败） | **{summary['decode_matrix_equal']}** |")
lines.append(f"| 像素产物（frame 原始字节 + page/crop/bridge PNG） | **{summary['pixel_artifacts_equal']}** |")
lines.append(f"| PDF 光栅页（2 页逐像素） | **{summary['pdf_pages_equal']}** |")
lines.append("")

lines.append("## 解码矩阵（`QtImageDecoder` → `PillowImageDecoder`）")
lines.append("")
lines.append("| fixture | 期望 | Qt | Pillow | 判定 |")
lines.append("|---|---|---|---|---|")
for name, entry in report["decode"].items():
    qt = entry["qt"]
    pillow = entry["pillow"]
    def cell(side: dict) -> str:
        if side.get("ok"):
            return f"OK {side['width']}x{side['height']} {side['mime_type']}"
        return f"FAIL {side.get('detail', side.get('error', ''))[:56]}"
    verdict = "一致" if entry["equal"] else "**差异（见备注）**"
    lines.append(f"| `{name}` | — | {cell(qt)} | {cell(pillow)} | {verdict} |")
lines.append("")
lines.append(
    "**唯一差异（能力增益，非回归）**：`still.avif` 在 Qt 闭包里无 AVIF 插件，改前是"
    "“已声明后缀但解码失败”；Pillow 12.3 自带 AVIF 解码，改后成功。`heic/heif` 两侧都不支持"
    "（Pillow 需 pillow-heif，非依赖）——即**没有任何解码能力被删除**。"
)
lines.append("")

lines.append("## 像素路径（逐像素相等，字节差异仅来自 PNG 编码器）")
lines.append("")
lines.append("| 样例 | `page_frame`（rgb32 原始字节） | `page_png` | `region_crop` | `_render_content_decoder` |")
lines.append("|---|---|---|---|---|")
artifact_label = {
    "frame": "frame",
    "page_png": "page_png",
    "crop_png": "crop_png",
    "bridge_png": "bridge_png",
}
for name, cases in report["pixels"].items():
    cells = []
    for key in ("frame", "page_png", "crop_png", "bridge_png"):
        case = cases[key]
        if case["pixel_equal"]:
            cells.append("✅ 像素相等" + ("" if case["byte_identical"] else "（字节不同）"))
        else:
            cells.append("❌ 不一致")
    lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
lines.append("")
lines.append(
    "`page_frame` 是字节级完全相等（`Format_RGB32` 的 BGRA little-endian 内存布局，alpha 固定 0xff）；"
    "`page_png`/`region_crop`/`_render_content_decoder` 的 PNG **字节**不同是编码器实现差异"
    "（Qt vs libpng/zlib 设置），**解码后像素逐字节相等**。下游只消费像素或把 PNG 作为自产 Managed Copy "
    "保存，不跨版本比对 PNG 字节，因此无兼容性影响。"
)
lines.append("")

lines.append("## PDF 光栅（真实 pypdfium2 渲染 → PNG）")
lines.append("")
lines.append("| 页 | 尺寸 | 像素 | 字节 |")
lines.append("|---|---|---|---|")
for key, entry in report["pdf"].items():
    pixel = "✅ 相等" if entry["pixel_equal"] else "❌ 不一致"
    byte = "相同" if entry["byte_identical"] else "不同（编码器）"
    lines.append(f"| {key} | {entry['width']}x{entry['height']} | {pixel} | {byte} |")
lines.append("")

lines.append("## SourceStyle 分析器等价（`PixelSourceStyleAnalyzer` → `PillowSourceStyleAnalyzer`）")
lines.append("")
lines.append(
    "以 `tests/infrastructure/test_pillow_source_style.py` 锁定：同一 crop 上 "
    "`detected_source_font_size` / `source_font_size_confidence` / `text_color` / "
    "`background_color` / `direction_hint` 与 Qt 实现逐字段相等（该测试在 Qt 可用的开发环境运行；"
    "打包闭包内不再需要 Qt）。"
)
lines.append("")

(AC1 / "COMPARISON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", AC1 / "COMPARISON.md")
