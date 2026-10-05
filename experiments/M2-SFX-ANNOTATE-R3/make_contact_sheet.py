"""M2-SFX-ANNOTATE-R3 AC1：候选池目检 contact sheet 生成（毛笔形态二次决胜输入）。

合同裁量点「密度并列时人工/AI 目检毛笔形态优先作为二次决胜」的执行工具。
产出多张小批 sheet（每批 3 列 × 4 行、格宽 700px，保证逐格毛笔形态可辨）：

- 批 1：R2 已 confirm 毛笔竖排正样本参照页（BJ16/17/18/23/24）+ 候选池
  kept=1 的 6 页（rank1-6，密度无并列直接入选；目检用于登记毛笔形态确认）。
- 批 2-5：kept=0 的 38 页（密度全并列，按机械序 = sha256(seed:source_id)
  升序；本批目检为二次决胜输入，逐页辨认毛笔竖排 SFX 形态）。

AI/人工逐页目检后由 material_select_r3.py 按 TIE_BREAK_VISUAL 登记执行。
产出落 training_data/sfx-v1/annotate-r3/selection/（gitignored）。
只读素材树；零 src。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[2]
R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
BJ_ASSET_ROOT_R2 = (
    R2_WORKTREE / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
)
SCAN_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "scan" / "density-scan-pool.json"
OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "selection"

SEED = 20261004

# R2 confirm 参照页（R2 双 AI 交叉审核 confirm 的毛笔竖排正样本，见 R2 stage2 留痕）
REFERENCE_PAGES = [
    ("REF-BJ16", "vol01_p0045"),
    ("REF-BJ17", "vol05_p0167"),
    ("REF-BJ18", "vol05_p0065"),
    ("REF-BJ23", "vol03_p0047"),
    ("REF-BJ24", "vol03_p0186"),
]

CELL_W = 700
LABEL_H = 34
COLS = 3
ROWS_PER_SHEET = 4


def thumb(source_id: str) -> Image.Image:
    path = BJ_ASSET_ROOT_R2 / source_id[:5] / "pages" / f"{source_id}.png"
    with Image.open(path) as im:
        w, h = im.size
        s = CELL_W / w
        return im.convert("RGB").resize((CELL_W, int(h * s)))


def rank_key(density: int, source_id: str):
    return (-density, hashlib.sha256(f"{SEED}:{source_id}".encode("utf-8")).hexdigest())


def render_sheet(entries: list[tuple[str, str]], out_path: Path) -> None:
    thumbs = [thumb(sid) for _label, sid in entries]
    cell_h = max(t.height for t in thumbs)
    nrows = (len(entries) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, nrows * (cell_h + LABEL_H)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for j, ((label, _sid), t) in enumerate(zip(entries, thumbs)):
        cx, cy = (j % COLS) * CELL_W, (j // COLS) * (cell_h + LABEL_H)
        sheet.paste(t, (cx, cy + LABEL_H))
        color = (120, 220, 120) if label.startswith("REF") else (
            (250, 210, 80) if "kept=1" in label else (235, 235, 235))
        draw.rectangle([cx, cy, cx + CELL_W - 1, cy + LABEL_H - 1], fill=(0, 0, 0))
        draw.text((cx + 6, cy + 9), label, fill=color)
    sheet.save(out_path)
    print(f"wrote {out_path} ({sheet.width}x{sheet.height}, {len(entries)} cells)")


def main() -> int:
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ranked = sorted(scan["pages"].values(), key=lambda p: rank_key(p["sfx_density_kept"], p["source_id"]))
    assert len(ranked) == 44
    kept1 = [p for p in ranked if p["sfx_density_kept"] >= 1]
    kept0 = [p for p in ranked if p["sfx_density_kept"] == 0]
    assert len(kept1) == 6 and len(kept0) == 38

    sheet_no = 1
    batch1 = [(f"REF {cid}", sid) for cid, sid in REFERENCE_PAGES]
    batch1 += [(f"r{i:02d} {p['source_id']} kept=1", p["source_id"]) for i, p in enumerate(kept1, 1)]
    for start in range(0, len(batch1), COLS * ROWS_PER_SHEET):
        render_sheet(batch1[start:start + COLS * ROWS_PER_SHEET], OUT_DIR / f"inspect-batch-{sheet_no}.png")
        sheet_no += 1
    for start in range(0, len(kept0), COLS * ROWS_PER_SHEET):
        chunk = kept0[start:start + COLS * ROWS_PER_SHEET]
        entries = [(f"r{ranked.index(p) + 1:02d} {p['source_id']} kept=0", p["source_id"]) for p in chunk]
        render_sheet(entries, OUT_DIR / f"inspect-batch-{sheet_no}.png")
        sheet_no += 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
