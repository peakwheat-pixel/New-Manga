"""M2-SFX-TILE-WIDTH-CALIB-1 AC1: build the multi-width evaluation pages.

INPUTS.md registered the inventory hard fact: NO native KO/webtoon page with
width other than 600/690 exists in any material tree, so the evaluation set
is built from the two Task-contract-authorized compensation paths:

1. resampled variants of known-truth KO pages (pre-k08/pre-k09/pre-k02,
   R2 final GT) — uniform LANCZOS scale, GT polygon coords scaled by the
   same factor (an exact similarity transform; the resampling pixel loss is
   declared per source in INPUTS.md §3);
2. programmatically synthesized long-strip pages (rectangular text blocks —
   Korean onomatopoeia + Latin onomatopoeia with stroke+fill) with EXACT
   ground-truth boxes captured at draw time; block sizes are scaled by
   page_w/690 so the block-to-page width ratio matches the KO GT median
   across width bins (mechanical cross-width comparison, declared
   directional).

Everything lands in the gitignored external tree
``G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`` — nothing here
enters Git. Output: pages/*.png + pages-manifest.json (sha256, page size,
gt boxes xyxy, gt type, provenance per page).

Wording discipline: directional evidence; the word "significant" is banned.
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None  # KO 超长 webtoon（T3/tile_calib/parity 先例）

R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data"
    r"/sfx-v1/annotate-r2/final"
)
OUT = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1")
PAGES = OUT / "pages"

#: 原生锚点页（R2 final val/test；sha 对 manifest 断言）。
NATIVE = {
    "pre-k08": "val",
    "pre-k09": "val",
    "pre-k02": "test",
}

#: 重采样档：sample_id -> 目标宽列表（scale = target_w / native_w）。
RESAMPLE = {
    "pre-k08": [640, 480, 320, 800, 1024],
    "pre-k09": [640, 480, 320],
}

#: 合成档：页宽 -> 页高（aspect 均 >= 8.0，域内）。
SYNTH = {
    384: 40960,
    560: 40960,
    680: 40960,
}

#: 合成页基字号池（690 域准；按 page_w/690 缩放保持相对块尺寸一致）。
BASE_FONT_SIZES = [40, 80, 120, 160, 200, 260]
WORDS_KO = ["쾅", "빵", "펑", "두웅", "쨍", "즈직"]
WORDS_LAT = ["BOOM", "BANG", "CRASH", "POW", "ZAP", "THUD"]
FILL_COLORS = [(200, 30, 30), (230, 170, 20), (240, 240, 240)]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def poly_to_xyxy(polygon) -> list[float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def load_native_pages() -> dict[str, dict]:
    """R2 final native pages with manifest sha/size assertions
    (verify_tile_parity.py load_ko_pages 数据面逐字纪律)."""
    import numpy

    pages: dict[str, dict] = {}
    for sid, split in NATIVE.items():
        m = json.loads((R2_FINAL / f"manifest.{split}.json").read_text(encoding="utf-8"))
        s = next(x for x in m["samples"] if x["sample_id"] == sid)
        img = s["image"]
        p = Path(img["path"])
        assert p.is_file(), f"{sid}: 页面缺失 {p}"
        assert sha256_file(p) == img["sha256"], f"{sid}: 图像 sha256 与 manifest 不一致"
        rgb = Image.open(p).convert("RGB")
        w, h = rgb.size
        assert (w, h) == (img["width"], img["height"]), f"{sid}: 尺寸 {w}x{h} != manifest"
        gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
        pages[sid] = {
            "sample_id": sid,
            "img": p,
            "pil": rgb,
            "w": w,
            "h": h,
            "gts": gts,
        }
        print(f"[prepare] native {sid} {w}x{h} boxes={len(gts)}", flush=True)
    assert pages["pre-k08"]["w"] == 690 and pages["pre-k02"]["w"] == 600
    _ = numpy  # 装载自检（与评测脚本同依赖面）
    return pages


def resample(pages: dict[str, dict], manifest: list[dict]) -> None:
    for sid, targets in RESAMPLE.items():
        src = pages[sid]
        w0, h0 = src["w"], src["h"]
        for tw in targets:
            scale = tw / w0
            th = round(h0 * scale)
            out_path = PAGES / f"{sid}@{tw}.png"
            if out_path.is_file():
                print(f"[prepare] skip existing {out_path.name}", flush=True)
            else:
                resized = src["pil"].resize((tw, th), Image.LANCZOS)
                resized.save(out_path, format="PNG")
                resized.close()
            gts = [
                [round(v * scale, 2) for v in box] for box in src["gts"]
            ]
            manifest.append(
                {
                    "page_id": f"{sid}@{tw}",
                    "source": sid,
                    "gt_type": "resampled_derived",
                    "provenance": (
                        f"LANCZOS uniform scale {scale:.4f} ({tw}/{w0}); GT polygon "
                        "coords x scale (exact similarity transform; pixel resampling "
                        "loss declared in INPUTS.md §3)"
                    ),
                    "path": str(out_path),
                    "sha256": sha256_file(out_path),
                    "width": tw,
                    "height": th,
                    "boxes": gts,
                }
            )
            print(f"[prepare] {sid}@{tw}: {tw}x{th} boxes={len(gts)}", flush=True)


def _pick_font(size: int, korean: bool) -> ImageFont.FreeTypeFont:
    candidates = (
        ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf"]
        if korean
        else ["C:/Windows/Fonts/ariblk.ttf", "C:/Windows/Fonts/arialbd.ttf"]
    )
    for c in candidates:
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    raise FileNotFoundError(f"no usable font among {candidates}")


def synth_pages(manifest: list[dict]) -> None:
    """Synthesized exact-GT long-strip pages (directional mechanical face)."""
    for page_w, page_h in SYNTH.items():
        rng = random.Random(20261004 + page_w)
        img = Image.new("RGB", (page_w, page_h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        boxes: list[list[float]] = []
        k = 1.0 * page_w / 690.0  # 相对块尺寸与 KO GT 中位对齐（登记声明）
        y = 60
        n_blocks = 0
        while y < page_h - 400:
            size = max(18, int(rng.choice(BASE_FONT_SIZES) * k))
            korean = rng.random() < 0.5
            word = rng.choice(WORDS_KO if korean else WORDS_LAT)
            font = _pick_font(size, korean)
            fill = rng.choice(FILL_COLORS)
            # 文字 bbox 外扩描边半径+margin，登记为精确 GT
            stroke_w = max(2, size // 14)
            pad = stroke_w + 6
            tmp_bbox = draw.textbbox((0, 0), word, font=font)
            bw = tmp_bbox[2] - tmp_bbox[0]
            bh = tmp_bbox[3] - tmp_bbox[1]
            if bw + 2 * pad > page_w - 8:
                y += bh + 400
                continue
            x = rng.randint(4, page_w - bw - 2 * pad - 4)
            ty = y + pad - tmp_bbox[1]
            tx = x + pad - tmp_bbox[0]
            draw.text(
                (tx, ty),
                word,
                font=font,
                fill=fill,
                stroke_width=stroke_w,
                stroke_fill=(20, 20, 20),
            )
            boxes.append(
                [
                    float(x),
                    float(y),
                    float(x + bw + 2 * pad),
                    float(y + bh + 2 * pad),
                ]
            )
            n_blocks += 1
            y += bh + 2 * pad + rng.randint(400, 1000)
        out_path = PAGES / f"synth-{page_w}.png"
        img.save(out_path, format="PNG")
        img.close()
        manifest.append(
            {
                "page_id": f"synth-{page_w}",
                "source": "programmatic-synth",
                "gt_type": "synthetic_exact",
                "provenance": (
                    "rectangular text blocks (KO/Latin onomatopoeia, stroke+fill) "
                    "drawn at native resolution; GT captured at draw time "
                    "(textbbox + stroke pad); block/page width ratio aligned to "
                    "KO GT median (base sizes x page_w/690); white background"
                ),
                "path": str(out_path),
                "sha256": sha256_file(out_path),
                "width": page_w,
                "height": page_h,
                "boxes": boxes,
            }
        )
        print(f"[prepare] synth-{page_w}: {page_w}x{page_h} blocks={n_blocks}", flush=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "pages-manifest.json"
    native = load_native_pages()
    manifest: list[dict] = []
    # 原生锚点页也入 manifest（GT=真实 R2 final 派生框）
    for sid, src in native.items():
        manifest.append(
            {
                "page_id": f"{sid}@{src['w']}",
                "source": sid,
                "gt_type": "real_r2_final",
                "provenance": "native page; R2 final manifest boxes (sha asserted)",
                "path": str(src["img"]),
                "sha256": sha256_file(src["img"]),
                "width": src["w"],
                "height": src["h"],
                "boxes": src["gts"],
            }
        )
    resample(native, manifest)
    synth_pages(manifest)
    doc = {
        "task": "M2-SFX-TILE-WIDTH-CALIB-1 AC1 evaluation pages",
        "generated_at_utc": now_iso(),
        "generated_by": "experiments/M2-SFX-TILE-WIDTH-CALIB-1/prepare_pages.py",
        "external_tree": str(OUT),
        "wording_discipline": "directional 证据，统计功效低；禁用「显著」",
        "pages": manifest,
    }
    manifest_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"[prepare] wrote {manifest_path} pages={len(manifest)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
