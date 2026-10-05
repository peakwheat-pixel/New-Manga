"""M2-SFX-GATE-T3 AC3 npd 分歧仲裁预览生成（contact sheet，只读输入）。

对 gate-t3/npd-judgments/divergence.json 每个分歧单元裁原页局部（框扩边 70px），
放大标准化 tile 高 360px，红框描候选，页内拼网格 contact sheet 落
gate-t3/npd-judgments/previews/。KO 长条页（690 宽×5 万+px 高）直接 PIL crop。
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
NPJ = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-judgments"
PREV = NPJ / "previews"
R3M = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode/training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json")

TILE_H = 360
PAD = 70


def main() -> int:
    m3 = json.loads(R3M.read_text(encoding="utf-8"))
    pages = {s["sample_id"]: s["image"]["path"] for s in m3}
    d = json.loads((NPJ / "divergence.json").read_text(encoding="utf-8"))
    by_page: dict[str, list[dict]] = {}
    for u in d["divergence"]:
        by_page.setdefault(u["page"], []).append(u)

    for pg, units in sorted(by_page.items()):
        im = Image.open(pages[pg])
        tiles = []
        for u in units:
            x1, y1, x2, y2 = u["xyxy"]
            cx1, cy1 = max(0, int(x1 - PAD)), max(0, int(y1 - PAD))
            cx2, cy2 = min(im.width, int(x2 + PAD)), min(im.height, int(y2 + PAD))
            crop = im.crop((cx1, cy1, cx2, cy2)).convert("RGB")
            sc = TILE_H / crop.height
            crop = crop.resize((max(1, int(crop.width * sc)), TILE_H), Image.LANCZOS)
            dr = ImageDraw.Draw(crop)
            rx1, ry1 = (x1 - cx1) * sc, (y1 - cy1) * sc
            rx2, ry2 = (x2 - cx1) * sc, (y2 - cy1) * sc
            for w, col in ((6, (255, 255, 255)), (3, (255, 0, 0))):
                dr.rectangle([rx1 - w, ry1 - w, rx2 + w, ry2 + w], outline=col, width=w)
            dr.rectangle([4, 4, 4 + 9 * len(u["id"]), 34], fill=(0, 0, 0))
            dr.text((10, 8), u["id"], fill=(255, 255, 0))
            tiles.append((u, crop))
        # 网格 4 列
        cols = 4
        rows = (len(tiles) + cols - 1) // cols
        cw = max(t[1].width for t in tiles)
        sheet = Image.new("RGB", (cols * cw, rows * TILE_H), (40, 40, 40))
        for i, (_u, crop) in enumerate(tiles):
            sheet.paste(crop, ((i % cols) * cw, (i // cols) * TILE_H))
        out = PREV / f"{pg}__divergence_sheet.png"
        PREV.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        print(f"{out} units={len(units)} ids={[u['id'] for u in units]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
