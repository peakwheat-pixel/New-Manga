"""M2-SFX-ANNOTATE-R2 AC1：BJ 域候选页渲染（vol01/03/05 已下载 PDF → PNG）。

fetch_bj.py 的 render 子命令只做每卷 4 页采样（sample_page_indices 固定
首/1/4/中/末，无法指定页），本脚本按 M2-SFX-ANNOTATE-R2 AC1 需要渲染任意
候选页：每卷均匀采样（避开 BJ01-15 已入池 source_id），DPI 150（与
fetch_bj.RENDER_DPI 及 cases.json render_dpi 口径一致）输出 RGB PNG，直接
落到 R2 worktree 素材树 日漫_JA/01_black_jack_official/volXX/pages/。
top-10 SFX 密集页由 material_scan_density.py 密度排序后在 cases.json 登记
BJ16-BJ25；未入选候选留同目录作扩标池。

PDF 源 = M2-TA2B-OPEN-ASSETS worktree（fetch_bj.py OUTPUT_DIR 同布局，
bj_download_manifest.json 已核 sha256）。需 pypdfium2 环境
（M2-DOCTR-QUAL-gpu-py312）。
"""

from __future__ import annotations

import json
import sys
import tempfile
import os
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
PDF_ROOT = Path(r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official")
OUT_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
RENDER_DPI = 150
PAGES_PER_VOLUME = 20

# cases.json BJ01-15 已入池 source_id（volXX_pYYYY → 1-based 页号）
USED_PAGES: dict[int, set[int]] = {
    1: {1, 53, 105, 209},
    3: {1, 48, 56, 60, 111, 159, 221},
    5: {1, 61, 122, 243},
}


def sample_pages(page_count: int, volume: int) -> list[int]:
    """均匀采样 PAGES_PER_VOLUME 个 1-based 页号，避开已入池页。"""
    step = (page_count - 1) / (PAGES_PER_VOLUME - 1)
    picked = sorted({1 + round(i * step) for i in range(PAGES_PER_VOLUME)})
    return [p for p in picked if p not in USED_PAGES.get(volume, set())]


def main() -> int:
    failures = 0
    total = 0
    plan: dict[str, dict] = {}
    for volume in (1, 3, 5):
        pdf_path = PDF_ROOT / f"vol{volume:02d}" / f"volume{volume:02d}.pdf"
        pages_dir = OUT_ROOT / f"vol{volume:02d}" / "pages"
        if not pdf_path.is_file():
            print(f"vol{volume:02d}\tRENDER_FAILED\tmissing {pdf_path}", file=sys.stderr)
            failures += 1
            continue
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            page_count = len(pdf)
            todo = sample_pages(page_count, volume)
            pages_dir.mkdir(parents=True, exist_ok=True)
            rendered = []
            for page_number in todo:
                output = pages_dir / f"vol{volume:02d}_p{page_number:04d}.png"
                if output.is_file():
                    rendered.append(page_number)
                    print(f"vol{volume:02d}\tEXISTS\tpage={page_number}/{page_count}")
                    continue
                pil_image = pdf[page_number - 1].render(scale=RENDER_DPI / 72).to_pil().convert("RGB")
                temp_name = None
                try:
                    with tempfile.NamedTemporaryFile(
                        prefix=f".{output.stem}.", suffix=".png.part", dir=pages_dir, delete=False
                    ) as temp:
                        temp_name = temp.name
                        pil_image.save(temp, format="PNG")
                    os.replace(temp_name, output)
                    temp_name = None
                finally:
                    if temp_name:
                        Path(temp_name).unlink(missing_ok=True)
                rendered.append(page_number)
                print(f"vol{volume:02d}\tRENDERED\tpage={page_number}/{page_count} {pil_image.width}x{pil_image.height}")
            plan[f"vol{volume:02d}"] = {"pdf_page_count": page_count, "candidate_pages": rendered}
            total += len(rendered)
        finally:
            pdf.close()
    plan_path = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "bj-candidates" / "render-plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        json.dumps({"tool": "experiments/M2-SFX-ANNOTATE-R2/material_bj_render.py", "dpi": RENDER_DPI,
                    "pages_per_volume": PAGES_PER_VOLUME,
                    "used_pages_excluded": {v: sorted(s) for v, s in USED_PAGES.items()}, "volumes": plan},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"SUMMARY\tcommand=render_bj candidates={total} failures={failures}")
    print(f"wrote {plan_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    Image.MAX_IMAGE_PIXELS = None
    sys.exit(main())
