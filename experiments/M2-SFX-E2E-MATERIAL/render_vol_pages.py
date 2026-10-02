"""M2-SFX-E2E-MATERIAL: render pages of a BJ official volume PDF.

Serves AC2 (SFX-density visual scan via thumbnail grids) and the final
asset render (DPI 150, byte-identical discipline to the TA2B renders:
pypdfium2 draw, PNG, no resampling).  The PDF input is the TA2B-downloaded
official file (read-only); outputs go to the target directory given on the
command line (thumbnails: git-external task-env tree; final pages: the
gitignored suite directory in THIS worktree).

Examples:
  # thumbnail grid of the whole volume (5x7 pages per sheet, ~40 dpi)
  python experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py \
    --pdf "G:/.../vol03/volume03.pdf" --out-dir "G:/.../thumbs" --dpi 40 --grid 35

  # final asset render of chosen pages at production DPI
  python experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py \
    --pdf "G:/.../vol03/volume03.pdf" --out-dir ".../vol03/pages" \
    --dpi 150 --pages 121 --pages 134 --name-prefix vol03_p
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_pages(spec: list[str], total: int) -> list[int]:
    pages: set[int] = set()
    for item in spec:
        if "-" in item:
            lo, hi = item.split("-", 1)
            pages.update(range(int(lo), int(hi) + 1))
        else:
            pages.add(int(item))
    out = sorted(p for p in pages if 1 <= p <= total)
    dropped = sorted(pages - set(out))
    if dropped:
        print(f"NOTE: page numbers outside 1..{total} dropped: {dropped}", file=sys.stderr)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--pages", action="append", default=[],
                        help="1-based page number or lo-hi range; repeatable; default=all")
    parser.add_argument("--grid", type=int, default=0,
                        help="if >0, additionally emit contact-sheet grids with this many pages each")
    parser.add_argument("--name-prefix", default="page_p")
    parser.add_argument("--manifest", default="", help="optional path for a JSON render manifest")
    args = parser.parse_args()

    import pypdfium2 as pdfium
    from PIL import Image

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        print(f"FATAL: pdf missing: {pdf_path}", file=sys.stderr)
        return 2
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scale = args.dpi / 72.0
    pdf = pdfium.PdfDocument(str(pdf_path))
    total = len(pdf)
    wanted = parse_pages(args.pages, total) if args.pages else list(range(1, total + 1))
    print(f"pdf={pdf_path} pages_total={total} dpi={args.dpi} rendering={len(wanted)} page(s)")

    manifest = {
        "tool": "experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pdf": str(pdf_path),
        "pdf_sha256": sha256_file(pdf_path),
        "dpi": args.dpi,
        "pages": [],
    }
    thumbs: dict[int, Path] = {}
    for number in wanted:
        page = pdf[number - 1]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        target = out_dir / f"{args.name_prefix}{number:04d}.png"
        image.save(target, format="PNG")
        entry = {
            "pdf_page_number": number,
            "file": target.name,
            "width": image.width,
            "height": image.height,
            "sha256": sha256_file(target),
            "size": target.stat().st_size,
        }
        manifest["pages"].append(entry)
        thumbs[number] = target
        print(f"  p{number:04d} -> {target.name} {image.width}x{image.height}")
        page.close()
    pdf.close()

    if args.grid > 0:
        per = args.grid
        cols, rows = 5, (per + 4) // 5
        ordered = sorted(thumbs)
        for sheet_index in range(0, len(ordered), per):
            chunk = ordered[sheet_index:sheet_index + per]
            first = Image.open(thumbs[chunk[0]])
            cell_w, cell_h = first.size
            sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
            for slot, number in enumerate(chunk):
                with Image.open(thumbs[number]) as im:
                    sheet.paste(im, ((slot % cols) * cell_w, (slot // cols) * cell_h))
            grid_name = f"grid_{args.name_prefix}{chunk[0]:04d}-{chunk[-1]:04d}.png"
            grid_path = out_dir / grid_name
            sheet.save(grid_path, format="PNG")
            print(f"  grid -> {grid_name} ({len(chunk)} pages)")

    if args.manifest:
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
