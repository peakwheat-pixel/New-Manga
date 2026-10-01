"""M2-TA3-B2 phase-2 step-3: G1 SVG text-layer extraction (R8 formal count).

Extracts the OFFICIAL SVG text layer of the four native-GT cases from the
Pepper&Carrot lang-pack ZIPs that ship next to the page images:

  J46 = E20P06 (ja, partial SVG text layer - ``svg_text_layer_official_partial``)
  J47 = E20P07 (ja, same)
  K11 = E04P02 (ko, ``svg_text_layer_present_unaligned`` - the text layer
        exists as Inkscape ``flowRoot`` flow boxes WITHOUT a bbox alignment
        table; r2 N1 disclosure)
  K19 = E20P01 (ko, same)

Per case the script writes ``svg-gt-<case>.json`` into the phase-2 ocr dir:
canvas size, the formal ``.svg`` member count of the ZIP (R8: this dumped
manifest replaces the stage-1 reconnaissance number), and EVERY text
element with its canvas-space geometry (anchor / polygon after the
element transform) + raw text, so ``measure_cer.py`` can align elements to
detected regions reproducibly (alignment key = geometry intersection; the
human audit spot-checks the alignment per quality-thresholds §5 risk 2).

Standard library only.  Output is data, not judgements.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "experiments" / "M2-TA3-B" / "case-selection.json"
TA2B_SUITE = Path(
    r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite"
)
MAIN_SUITE = Path(r"G:/CODEX/New Manga/test_assets/comic_golden_suite")

#: case_id -> (zip path, svg member, svg language dir)
TARGETS: dict[str, tuple[Path, str, str]] = {
    "J46": (
        TA2B_SUITE / "日漫_JA/02_open_ground_truth_peppercarrot/ep20/ep20_The-Picnic_lang-pack.zip",
        "lang/ja/E20P06.svg",
        "ja",
    ),
    "J47": (
        TA2B_SUITE / "日漫_JA/02_open_ground_truth_peppercarrot/ep20/ep20_The-Picnic_lang-pack.zip",
        "lang/ja/E20P07.svg",
        "ja",
    ),
    "K11": (
        MAIN_SUITE / "韩漫_KO/02_public_ground_truth_peppercarrot/ep04/ep04_Stroke-of-genius_lang-pack.zip",
        "lang/kr/E04P02.svg",
        "kr",
    ),
    "K19": (
        TA2B_SUITE / "韩漫_KO/02_public_ground_truth_peppercarrot/ep20/ep20_The-Picnic_lang-pack.zip",
        "lang/kr/E20P01.svg",
        "kr",
    ),
}

SVG_NS = "{http://www.w3.org/2000/svg}"

_NUM = r"[-+]?[\d.]+(?:e[-+]?\d+)?"


def _parse_transform(tr: str | None):
    """Return a 6-tuple matrix (a,b,c,d,e,f) or identity."""
    if not tr:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    m = re.match(rf"matrix\(\s*({_NUM})\s*,\s*({_NUM})\s*,\s*({_NUM})\s*,\s*({_NUM})\s*,\s*({_NUM})\s*,\s*({_NUM})\s*\)", tr.strip())
    if m:
        return tuple(float(g) for g in m.groups())  # type: ignore[return-value]
    t = re.match(rf"translate\(\s*({_NUM})(?:\s*,\s*({_NUM}))?\s*\)", tr.strip())
    if t:
        return (1.0, 0.0, 0.0, 1.0, float(t.group(1)), float(t.group(2) or 0))
    raise ValueError(f"unsupported transform: {tr!r}")


def _apply(mat, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = mat
    return (a * x + c * y + e, b * x + d * y + f)


def _attr_order_free(elem: ET.Element, name: str) -> str | None:
    return elem.attrib.get(name)


def extract_case(case_id: str, zip_path: Path, member: str, lang: str) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        svg_members = [n for n in names if n.lower().endswith(".svg")]
        xml = zf.read(member).decode("utf-8")
    root = ET.fromstring(xml)
    canvas = (
        root.attrib.get("width", "").strip(),
        root.attrib.get("height", "").strip(),
    )

    elements: list[dict] = []
    # --- <text> elements: anchor (x, y) through the element transform ------
    for text_el in root.iter(f"{SVG_NS}text"):
        tr = _parse_transform(text_el.attrib.get("transform"))
        x = float(text_el.attrib.get("x", "0"))
        y = float(text_el.attrib.get("y", "0"))
        anchor = _apply(tr, x, y)
        content = "".join(text_el.itertext()).strip()
        if not content:
            continue
        elements.append(
            {
                "kind": "text",
                "anchor": list(anchor),
                "polygon": [list(anchor)],
                "text": content,
                "transform": text_el.attrib.get("transform", ""),
            }
        )
    # --- <flowRoot> elements: flowRegion/rect corners through the transform
    for flow in root.iter(f"{SVG_NS}flowRoot"):
        tr = _parse_transform(flow.attrib.get("transform"))
        rect = flow.find(f"{SVG_NS}flowRegion/{SVG_NS}rect")
        content = "".join(flow.itertext()).strip()
        if rect is None or not content:
            continue
        rx = float(rect.attrib.get("x", "0"))
        ry = float(rect.attrib.get("y", "0"))
        rw = float(rect.attrib.get("width", "0"))
        rh = float(rect.attrib.get("height", "0"))
        polygon = [
            list(_apply(tr, rx, ry)),
            list(_apply(tr, rx + rw, ry)),
            list(_apply(tr, rx + rw, ry + rh)),
            list(_apply(tr, rx, ry + rh)),
        ]
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        elements.append(
            {
                "kind": "flowRoot",
                "anchor": [sum(xs) / 4, sum(ys) / 4],
                "polygon": polygon,
                "text": content,
                "transform": flow.attrib.get("transform", ""),
            }
        )

    return {
        "case_id": case_id,
        "lang": lang,
        "zip": str(zip_path),
        "member": member,
        "zip_svg_member_count": len(svg_members),
        "canvas_wh": [canvas[0], canvas[1]],
        "n_text_elements": len(elements),
        "n_text_kind": sum(1 for e in elements if e["kind"] == "text"),
        "n_flowroot_kind": sum(1 for e in elements if e["kind"] == "flowRoot"),
        "text_elements": elements,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ocr"),
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "task": "M2-TA3-B2",
        "step": "G1 svg text-layer extraction (R8 formal count)",
        "generated_from": str(MANIFEST_PATH),
        "cases": {},
    }
    ok = True
    for case_id, (zip_path, member, lang) in TARGETS.items():
        if not zip_path.is_file():
            print(f"[{case_id}] FAIL zip missing: {zip_path}")
            ok = False
            continue
        record = extract_case(case_id, zip_path, member, lang)
        out = out_dir / f"svg-gt-{case_id}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["cases"][case_id] = {
            "file": out.name,
            "zip_svg_member_count": record["zip_svg_member_count"],
            "n_text_elements": record["n_text_elements"],
            "canvas_wh": record["canvas_wh"],
        }
        print(
            f"[{case_id}] {record['n_text_elements']} text elements "
            f"(text={record['n_text_kind']} flowRoot={record['n_flowroot_kind']}) "
            f"zip_svg_members={record['zip_svg_member_count']} -> {out.name}"
        )
    manifest_path = out_dir / "svg-gt-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest -> {manifest_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
