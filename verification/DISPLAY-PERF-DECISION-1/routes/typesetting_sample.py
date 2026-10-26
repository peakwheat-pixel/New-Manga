"""AC5 typesetting comparison: current Pillow renderer vs Edge/WebView2 (Chromium) vertical-rl.

Runs entirely against the real product render path:

* "current" = ``PillowTextLayoutEngine.layout()`` + ``PillowFontCatalog.resolve()`` +
  ``PillowImageCompositor.compose_page()`` (the exact adapters wired in
  ``src/bootstrap/core_service.py``), including ``resolve_font_size()`` from
  ``src/application/rendering/style.py``.
* "alternative" = Edge headless, `writing-mode: vertical-rl` (same Chromium/DirectWrite
  stack WebView2 ships), same page, same box, same font family / size.

Both sides start from the same synthesized "clean plate": the real page
``test_assets/comic_golden_suite/日漫_JA/oc material/17/050.jpg`` with the interior of one
speech bubble white-filled (the product would use its CLEAN artifact here; we do not have
one for this asset, so the flat white bubble interior is an explicit stand-in).

Outputs (all under verification/DISPLAY-PERF-DECISION-1/routes/):
  sample_current_pillow.png            current adapter output on the real page
  sample_webview2_vertical_rl.png      Chromium vertical-rl output on the same page
  sample_webview2_tuned.png            Chromium + explicit column breaks + justify + JP font
  typesetting_side_by_side.png         labelled side-by-side + zoom crops
  punctuation_probe.png                vertical punctuation / tate-chu-yoko cell probe
  kinsoku_probe.png                    controlled line-start/line-end prohibition probe
  stroke_aa_probe.png                  stroke + antialiasing probe on dark ground
  page_clean_plate.png                 the shared base image
  metrics.json                         every measured number
  html/*.html                          the generated pages (re-runnable evidence)

Usage:  python verification/DISPLAY-PERF-DECISION-1/routes/typesetting_sample.py
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROUTES = Path(__file__).resolve().parent
ROOT = ROUTES.parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from application.rendering.style import RenderTextStyle, resolve_font_size  # noqa: E402
from infrastructure.rendering.pillow_rendering import (  # noqa: E402
    PillowFontCatalog,
    PillowImageCompositor,
    PillowTextLayoutEngine,
)
from ports.rendering.direction import TextDirection  # noqa: E402
from ports.rendering.ports import LayoutRequest, RenderOp  # noqa: E402

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
PAGE = ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17" / "050.jpg"
HTML_DIR = ROUTES / "html"

# Bubble detected on page 050 (see _probe_bubble.py): bbox (959, 780, 1308, 1393).
BUBBLE_BBOX = (959, 780, 1308, 1393)
SEARCH_WIN = (950, 760, 1340, 1560)
# Inner text box inside the ellipse (inset from the bubble bbox).
TEXT_BOX = (1013, 823, 232, 536)  # x, y, w, h

# Production default style (src/application/rendering/style.py §D03 11.6).
FONT_FAMILY = "Source Han Sans K Bold"
FONT_SIZE_FALLBACK = 26.0
STROKE_WIDTH = 3.0
LINE_SPACING = 1.0

MAIN_TEXT = (
    "「そうか……本当に、ここで終わりか。まだだ、諦めない！"
    "12番目の階層で待つ奴がいる。」"
)
JP_FONT = "Yu Gothic"

# --- Japanese line-breaking prohibition tables (JIS X 4051 / JTF rules, subset) -------------
KINSOKU_START = set("、。，．・：；？！ー」』）〕】〉》…‥ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ")
KINSOKU_END = set("「『（〔【〈《")


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------------------------
# base page / clean plate
# ---------------------------------------------------------------------------------------------
def build_clean_plate() -> tuple[Image.Image, dict]:
    page = Image.open(PAGE).convert("RGB")
    arr = np.asarray(page)
    x0, y0, x1, y1 = SEARCH_WIN
    win = arr[y0:y1, x0:x1]
    white = (win[..., 0] >= 235) & (win[..., 1] >= 235) & (win[..., 2] >= 235)
    labels, count = ndimage.label(white)
    sizes = ndimage.sum(white, labels, range(1, count + 1))
    best = int(np.argmax(sizes)) + 1
    filled = ndimage.binary_fill_holes(labels == best)
    ys, xs = np.nonzero(filled)
    bbox = (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()) + 1, y0 + int(ys.max()) + 1)
    mask = np.zeros(arr.shape[:2], dtype=bool)
    mask[y0:y1, x0:x1] = ndimage.binary_dilation(filled, iterations=2)
    clean = arr.copy()
    clean[mask] = 255
    image = Image.fromarray(clean)
    return image, {
        "page": str(PAGE.relative_to(ROOT)).replace("\\", "/"),
        "bubble_bbox": list(bbox),
        "bubble_mask_pixels": int(mask.sum()),
        "clean_plate_method": "largest near-white component inside search window, holes filled, 2px AA dilation, flat white fill",
    }


def png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def jpeg_data_uri(image: Image.Image, quality: int = 95) -> str:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality, subsampling=0)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------------------------
# current path (Pillow adapters, verbatim product wiring)
# ---------------------------------------------------------------------------------------------
def current_layout(text: str, box: tuple[int, int, int, int], catalog, font_family: str):
    engine = PillowTextLayoutEngine(catalog)
    x, y, width, height = box
    style = RenderTextStyle(
        font_family=font_family,
        stroke_enabled=True,
        stroke_width=STROKE_WIDTH,
        line_spacing=LINE_SPACING,
        text_direction=TextDirection.VERTICAL,
    )
    resolved = catalog.resolve(style.font_family)

    def fits(size: float) -> bool:
        return engine.layout(
            LayoutRequest(
                text=text,
                font_family=style.font_family,
                font_size=size,
                direction=TextDirection.VERTICAL,
                box_width=width,
                box_height=height,
                stroke_width=style.stroke_width if style.stroke_enabled else 0.0,
                line_spacing=style.line_spacing,
            )
        ).fits

    resolution = resolve_font_size(style, fits)
    layout = engine.layout(
        LayoutRequest(
            text=text,
            font_family=style.font_family,
            font_size=resolution.final_font_size,
            direction=TextDirection.VERTICAL,
            box_width=width,
            box_height=height,
            stroke_width=style.stroke_width if style.stroke_enabled else 0.0,
            line_spacing=style.line_spacing,
        )
    )
    op = RenderOp(
        items=layout.items,
        region_x=x,
        region_y=y,
        region_width=width,
        region_height=height,
        font_family=resolved.resolved_family,
        font_size=resolution.final_font_size,
        text_color="#000000",
        stroke_enabled=True,
        stroke_color="#FFFFFF",
        stroke_width=STROKE_WIDTH,
        direction=TextDirection.VERTICAL,
        text_align="start",
    )
    return {
        "engine": engine,
        "catalog": catalog,
        "style": style,
        "resolved": resolved,
        "resolution": resolution,
        "layout": layout,
        "op": op,
    }


def columns_from_items(items) -> list[list[str]]:
    """Rebuild the column structure from DrawItem x positions (as the engine emits them)."""
    xs = sorted({round(item.x, 3) for item in items})
    by_x: dict[float, list[tuple[float, str]]] = {x: [] for x in xs}
    for item in items:
        by_x[round(item.x, 3)].append((item.y, item.text))
    columns: list[list[str]] = []
    # Engine orders columns right-to-left (x decreasing = later column), but we only need
    # reading order: rightmost column first.
    for x in sorted(by_x, reverse=True):
        column = [text for _, text in sorted(by_x[x])]
        if column:
            columns.append(column)
    return columns


def measure_font_metrics(catalog, family: str, size: float) -> dict:
    font = catalog.load(family, size)
    ascent, descent = font.getmetrics()
    return {
        "resolved_family": catalog.resolve(family).resolved_family,
        "requested_family": family,
        "available": catalog.resolve(family).available,
        "preview_family": font.getname()[0],
        "ascent": ascent,
        "descent": descent,
        "vertical_char_pitch_px": ascent + descent,
        "advance_1em_px": float(font.getlength("あ")),
        "advance_punctuation_px": float(font.getlength("。")),
        "kerning_probe_AV": float(font.getlength("AV")),
        "kerning_probe_A_plus_V": float(font.getlength("A")) + float(font.getlength("V")),
        "ligature_probe_fi": float(font.getlength("fi")),
        "ligature_probe_f_plus_i": float(font.getlength("f")) + float(font.getlength("i")),
    }


# ---------------------------------------------------------------------------------------------
# Chromium (Edge headless) side
# ---------------------------------------------------------------------------------------------
def html_page(body: str, *, width: int, height: int, styles: str = "") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; width: {width}px; height: {height}px; overflow: hidden;
               background: #ffffff; }}
  * {{ box-sizing: border-box; }}
  {styles}
</style></head><body>
{body}
</body></html>
"""


def sample_html(background_uri: str, box: tuple[int, int, int, int], text: str, css: dict) -> str:
    x, y, w, h = box
    body = f"""
<img src="{background_uri}" width="1350" height="1920"
     style="position:absolute;left:0;top:0;width:1350px;height:1920px">
<div id="box" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;
     display:flex;justify-content:center;align-items:flex-start;overflow:hidden">
  <div id="text" style="writing-mode:vertical-rl;height:100%;
       font-family:'{css['font_family']}';font-size:{css['font_size']}px;
       line-height:{css['line_height']};letter-spacing:{css.get('letter_spacing', '0px')};
       color:#000000;{css.get('extra', '')}">{text}</div>
</div>
"""
    return html_page(body, width=1350, height=1920)


MEASURE_JS = r"""
const out = {};
const textEl = document.getElementById('text');
out.userAgent = navigator.userAgent;
out.supports = {
  writingModeVerticalRl: CSS.supports('writing-mode', 'vertical-rl'),
  textCombineUprightAll: CSS.supports('text-combine-upright', 'all'),
  lineBreakStrict: CSS.supports('line-break', 'strict'),
  textSpacingTrim: CSS.supports('text-spacing-trim', 'trim-start'),
  textAutospace: CSS.supports('text-autospace', 'normal'),
  paintOrder: CSS.supports('paint-order', 'stroke fill'),
  webkitTextStroke: CSS.supports('-webkit-text-stroke', '1px'),
  textAlignJustify: CSS.supports('text-align', 'justify'),
};
const cs = getComputedStyle(textEl);
out.computed = {
  fontFamily: cs.fontFamily, fontSize: cs.fontSize, lineHeight: cs.lineHeight,
  writingMode: cs.writingMode, letterSpacing: cs.letterSpacing,
};
const node = textEl.firstChild;
const chars = [];
for (let i = 0; i < node.length; i++) {
  if (node.data[i] === '\n') continue;
  const r = document.createRange();
  r.setStart(node, i); r.setEnd(node, i + 1);
  const rect = r.getBoundingClientRect();
  chars.push({ch: node.data[i], x: rect.left, y: rect.top, w: rect.width, h: rect.height});
}
const columns = [];
for (const c of chars) {
  let col = columns.find(k => Math.abs(k.x - c.x) < 1.5);
  if (!col) { col = {x: c.x, chars: []}; columns.push(col); }
  col.chars.push(c);
}
columns.sort((a, b) => a.x - b.x);
for (const col of columns) col.chars.sort((a, b) => a.y - b.y);
out.charCount = chars.length;
out.columnCount = columns.length;
out.columns = columns.map(col => col.chars.map(c => c.ch));
out.columnGeometry = columns.map((col, i) => ({
  indexFromLeft: i, x: col.x,
  firstCharTop: col.chars[0].y, lastCharBottom: col.chars[col.chars.length - 1].y,
  chars: col.chars.length,
}));
out.blockLeft = Math.min(...columns.map(c => c.x));
out.blockRight = Math.max(...columns.map(c => c.x + c.chars[0].w));
out.firstCharTop = chars[0].y;
out.lastCharBottom = chars[chars.length - 1].y;
out.overflow = {scrollWidth: textEl.scrollWidth, clientWidth: textEl.clientWidth,
                scrollHeight: textEl.scrollHeight, clientHeight: textEl.clientHeight,
                overflowsBox: textEl.scrollWidth > textEl.clientWidth + 0.5};
const comb = document.getElementById('combine');
if (comb) {
  const r = comb.getBoundingClientRect();
  out.combineUpright = {width: r.width, height: r.height, text: comb.textContent};
}
const cv = document.createElement('canvas');
const ctx = cv.getContext('2d');
ctx.font = cs.fontSize + " '" + cs.fontFamily.replace(/"/g, '') + "'";
out.canvasText = {};
for (const s of ['AV', 'A', 'V', 'fi', 'f', 'i', 'あ', '。']) out.canvasText[s] = ctx.measureText(s).width;
const narrow = document.getElementById('narrow');
if (narrow) {
  out.narrowBox = {clientWidth: narrow.clientWidth, scrollWidth: narrow.scrollWidth,
                   clientHeight: narrow.clientHeight, scrollHeight: narrow.scrollHeight,
                   overflows: narrow.scrollWidth > narrow.clientWidth + 0.5};
}
document.getElementById('result').textContent =
  '<<<JSON' + JSON.stringify(out) + 'JSON>>>';
"""


def measure_html() -> str:
    x, y, w, h = TEXT_BOX
    body = f"""
<div id="box" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;
     display:flex;justify-content:center;align-items:flex-start;overflow:hidden">
  <div id="text" style="writing-mode:vertical-rl;height:100%;
       font-family:'Microsoft YaHei';font-size:26px;line-height:26px;
       line-break:strict;text-combine-upright:all;color:#000000">{MAIN_TEXT}</div>
</div>
<div style="position:absolute;left:20px;top:20px;writing-mode:vertical-rl;font-size:26px;
     line-height:26px;font-family:'Microsoft YaHei'"><span id="combine"
     style="text-combine-upright:all">12</span></div>
<div id="narrow" style="position:absolute;left:700px;top:800px;width:72px;height:536px;
     display:flex;justify-content:center;align-items:flex-start;overflow:hidden">
  <div id="textNarrow" style="writing-mode:vertical-rl;height:100%;font-family:'Microsoft YaHei';
       font-size:26px;line-height:26px;line-break:strict">{MAIN_TEXT}</div>
</div>
<pre id="result" style="position:absolute;left:0;top:1900px;font-size:1px"></pre>
<script>{MEASURE_JS}</script>
"""
    return html_page(body, width=1350, height=1920)


def parse_dump_dom(dom: str) -> dict:
    match = re.search(r"<<<JSON(.*?)JSON>>>", dom, re.S)
    if not match:
        raise RuntimeError("measurement JSON not found in dump-dom output")
    return json.loads(match.group(1))

def _edge_run(html_path: Path, extra_args: list[str], artifact_name: str | None,
              timeout: int = 150) -> tuple[Path | None, str, str]:
    """Run Edge headless and poll for its artifact.

    This machine's msedge.exe is a launcher that hands the real browser to a child
    process, and ``Start-Process -ArgumentList`` does not quote arguments for us, so
    both the HTML file and every output path are staged under a space-free temp
    directory; only then are the artifacts copied back into the repo.
    """
    work = Path(tempfile.mkdtemp(prefix="nm-edge-"))
    html_dir = work / "html"
    shutil.copytree(HTML_DIR, html_dir)
    uri = (html_dir / html_path.name).as_uri()
    artifact = work / artifact_name if artifact_name else None
    command = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--force-device-scale-factor=1",
        "--user-data-dir=" + str(work / "profile"),
        *extra_args,
    ]
    if artifact is not None:
        command.append(f"--screenshot={artifact}")
    command.append(uri)
    quoted = ", ".join("'" + arg.replace("'", "''") + "'" for arg in command)
    stdout_path = work / "stdout.txt"
    stderr_path = work / "stderr.txt"
    artifact_name_capture = artifact_name or ""
    condition = (
        f"Test-Path -LiteralPath '{artifact}'" if artifact is not None
        else f"((Get-Content -LiteralPath '{stdout_path}' -Raw -ErrorAction SilentlyContinue) -match '</html>')"
    )
    script = f"""$ErrorActionPreference = 'Continue'
$argsList = @({quoted})
if ('{artifact_name_capture}' -eq '') {{
    $p = Start-Process -FilePath '{EDGE}' -ArgumentList $argsList -PassThru `
        -RedirectStandardOutput '{stdout_path}' -RedirectStandardError '{stderr_path}'
}} else {{
    # Redirecting the launcher's stdio breaks the child-browser handoff on this host
    # (observed: launcher exits 0, browser never writes the screenshot).
    $p = Start-Process -FilePath '{EDGE}' -ArgumentList $argsList -PassThru -WindowStyle Hidden
}}
$deadline = (Get-Date).AddSeconds({timeout})
while ((Get-Date) -lt $deadline) {{
    if ({condition}) {{ break }}
    Start-Sleep -Milliseconds 300
}}
Start-Sleep -Milliseconds 800
"""
    ps1 = work / "run.ps1"
    ps1.write_text(script, encoding="utf-8")
    try:
        subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1)],
            capture_output=True, text=True, timeout=timeout + 60,
        )
        text_out = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
        text_err = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    finally:
        pass
    moved: Path | None = None
    if artifact is not None and artifact.exists():
        moved = ROUTES / ("_edge_" + artifact.name)
        shutil.copy(artifact, moved)
    shutil.rmtree(work, ignore_errors=True)
    return moved, text_out, text_err


def screenshot(html_path: Path, png_path: Path, width: int = 1350, height: int = 1920) -> None:
    if png_path.exists():
        png_path.unlink()
    artifact, _, stderr = _edge_run(
        html_path,
        [f"--window-size={width},{height}", "--virtual-time-budget=5000"],
        "shot.png",
    )
    if artifact is None or not artifact.exists():
        raise RuntimeError(f"Edge screenshot failed: {stderr[-2000:]}")
    shutil.copy(artifact, png_path)
    image = Image.open(png_path)
    if image.size != (width, height):
        raise RuntimeError(f"unexpected screenshot size {image.size}")


def run_edge_dump_dom(html_path: Path, timeout: int = 150) -> str:
    _, dom, stderr = _edge_run(
        html_path, ["--dump-dom", "--virtual-time-budget=4000"], None, timeout=timeout
    )
    if "</html>" not in dom[-400:]:
        raise RuntimeError(f"Edge --dump-dom failed: {stderr[-2000:]}")
    return dom


def analyze_text_png(png_path: Path, box: tuple[int, int, int, int]) -> dict:
    image = np.asarray(Image.open(png_path).convert("L"))
    x, y, w, h = box
    crop = image[y : y + h, x : x + w]
    ink = crop < 200
    ys, xs = np.nonzero(ink)
    if len(xs) == 0:
        return {"ink_pixels": 0}
    values = crop[ink]
    # gray levels that are neither paper (>=250) nor solid ink (<=8)
    mid = values[(values > 8) & (values < 250)]
    return {
        "ink_pixels": int(ink.sum()),
        "ink_bbox_in_box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "ink_coverage": round(float(ink.mean()), 5),
        "distinct_gray_levels_in_ink": int(len(np.unique(values))),
        "antialias_mid_gray_pixels": int(len(mid)),
        "antialias_mid_gray_ratio": round(float(len(mid) / max(1, ink.sum())), 5),
        "mean_ink_darkness": round(float(values.mean()), 2),
    }


def cell_ink_centroid(png_path: Path, cells: list[tuple[int, int, int, int]]) -> list[dict]:
    image = np.asarray(Image.open(png_path).convert("L"))
    result = []
    for (cx, cy, cw, ch) in cells:
        crop = image[cy : cy + ch, cx : cx + cw]
        ink = crop < 200
        total = int(ink.sum())
        if total == 0:
            result.append({"ink_pixels": 0, "centroid_dx": None, "centroid_dy": None})
            continue
        ys, xs = np.nonzero(ink)
        cxm, cym = cw / 2.0, ch / 2.0
        result.append(
            {
                "ink_pixels": total,
                "centroid_dx": round(float(xs.mean() - cxm), 2),
                "centroid_dy": round(float(ys.mean() - cym), 2),
                "ink_bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            }
        )
    return result


def kinsoku_violations(columns: list[list[str]]) -> dict:
    starts, ends = [], []
    for index, column in enumerate(columns):
        if not column:
            continue
        if column[0] in KINSOKU_START:
            starts.append({"column": index, "char": column[0]})
        if column[-1] in KINSOKU_END:
            ends.append({"column": index, "char": column[-1]})
    return {
        "start_prohibited_violations": starts,
        "end_prohibited_violations": ends,
        "total": len(starts) + len(ends),
    }


# ---------------------------------------------------------------------------------------------
# figure helpers
# ---------------------------------------------------------------------------------------------
def label_font(size: int = 22) -> ImageFont.FreeTypeFont:
    for name in ("msyh.ttc", "YuGothR.ttc", "arial.ttf"):
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int = 22) -> None:
    font = label_font(size)
    draw.rectangle([xy[0] - 6, xy[1] - 4, xy[0] + font.getlength(text) + 6, xy[1] + size + 6], fill=(255, 255, 255))
    draw.text(xy, text, font=font, fill=(20, 20, 20))


def zooms(image: Image.Image, box: tuple[int, int, int, int], scale: float = 1.6) -> Image.Image:
    x, y, w, h = box
    crop = image.crop((x, y, x + w, y + h))
    return crop.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


# ---------------------------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------------------------
def make_punctuation_probe(chars: list[str]) -> tuple[Path, dict]:
    cell = 64
    pad = 6
    cols = len(chars)
    width = cols * cell + (cols + 1) * pad
    height = 2 * cell + 3 * pad + 30
    cells_pillow = []
    cells_web = []
    catalog = PillowFontCatalog()
    engine = PillowTextLayoutEngine(catalog)
    compositor = PillowImageCompositor(catalog)
    # --- web side: one vertical-rl cell per character (rendered first) ---
    web_cells = []
    body = ""
    for index, char in enumerate(chars):
        x = pad + index * (cell + pad)
        body += (
            f'<div style="position:absolute;left:{x}px;top:{pad + cell + pad}px;'
            f'width:{cell}px;height:{cell}px;writing-mode:vertical-rl;'
            f'font-family:\'Microsoft YaHei\';font-size:40px;line-height:1;'
            f'display:flex;justify-content:center;align-items:center;color:#000">{char}</div>'
        )
        web_cells.append((x, pad + cell + pad, cell, cell))
    html_path = HTML_DIR / "punctuation_probe.html"
    html_path.write_text(html_page(body, width=width, height=height), encoding="utf-8")
    shot = ROUTES / "_probe_punctuation_web.png"
    screenshot(html_path, shot, width=width, height=height)
    # Web screenshot first: it already carries the Chromium cell row at the bottom.
    canvas = Image.open(shot).convert("RGB")
    for index, char in enumerate(chars):
        x = pad + index * (cell + pad)
        request = LayoutRequest(
            text=char,
            font_family=FONT_FAMILY,
            font_size=40.0,
            direction=TextDirection.VERTICAL,
            box_width=cell,
            box_height=cell,
            stroke_width=0.0,
        )
        layout = engine.layout(request)
        op = RenderOp(
            items=layout.items,
            region_x=0,
            region_y=0,
            region_width=cell,
            region_height=cell,
            font_family=catalog.resolve(FONT_FAMILY).resolved_family,
            font_size=40.0,
            text_color="#000000",
            stroke_enabled=False,
            stroke_color="#FFFFFF",
            stroke_width=0.0,
            direction=TextDirection.VERTICAL,
        )
        composed = compositor.compose_page(png_bytes(Image.new("RGB", (cell, cell), "white")), (op,))
        canvas.paste(Image.open(io.BytesIO(composed)).convert("RGB"), (x, pad))
    ImageDraw.Draw(canvas).line(
        [(0, cell + 2 * pad), (width, cell + 2 * pad)], fill=(200, 200, 200), width=1
    )
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (pad, height - 26), f"Pillow (current) / Chromium vertical-rl — chars: {''.join(chars)}", 16)
    path = ROUTES / "punctuation_probe.png"
    canvas.save(path)
    return path, {
        "cells_pillow": cell_ink_centroid(canvas, cells_pillow),
        "cells_web": cell_ink_centroid(Image.open(shot).convert("L"), web_cells),
    }


def make_kinsoku_probe() -> tuple[Path, dict]:
    # Controlled: easiest layout geometry makes column starts deterministic.
    text = "あ" * 7 + "、" + "い" * 7 + "。" + "う" * 7
    cell = 60
    box_w, box_h = 150, 260
    catalog = PillowFontCatalog()
    current = current_layout(text, (0, 0, box_w, box_h), catalog, FONT_FAMILY)
    size = current["resolution"].final_font_size
    columns = columns_from_items(current["layout"].items)
    pillow_v = kinsoku_violations(columns)

    left = Image.new("RGB", (box_w, box_h), "white")
    compositor = PillowImageCompositor(catalog)
    op = RenderOp(
        items=current["layout"].items,
        region_x=0,
        region_y=0,
        region_width=box_w,
        region_height=box_h,
        font_family=current["resolved"].resolved_family,
        font_size=size,
        text_color="#000000",
        stroke_enabled=False,
        stroke_color="#FFFFFF",
        stroke_width=0.0,
        direction=TextDirection.VERTICAL,
    )
    left = Image.open(io.BytesIO(compositor.compose_page(png_bytes(left), (op,)))).convert("RGB")

    body = f"""
<div style="position:absolute;left:8px;top:8px;width:{box_w}px;height:{box_h}px;
     display:flex;justify-content:center;align-items:flex-start;overflow:hidden">
  <div style="writing-mode:vertical-rl;height:100%;font-family:'Microsoft YaHei';
       font-size:{size:g}px;line-height:{size:g}px;line-break:strict;
       text-align:start;color:#000">{text}</div>
</div>
"""
    html_path = HTML_DIR / "kinsoku_probe.html"
    html_path.write_text(html_page(body, width=box_w + 16, height=box_h + 16), encoding="utf-8")
    shot = ROUTES / "_probe_kinsoku_web.png"
    screenshot(html_path, shot, width=box_w + 16, height=box_h + 16)
    right = Image.open(shot).convert("RGB").crop((8, 8, 8 + box_w, 8 + box_h))

    # measure HTML columns through a second pass with the same text/box
    measure = kinsoku_measure_html(text, size, box_w, box_h)
    html_columns = measure["columns"]

    canvas = Image.new("RGB", (box_w * 2 + 40, box_h + 70), "white")
    canvas.paste(left, (10, 10))
    canvas.paste(right, (box_w + 30, 10))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (10, box_h + 24), f"Pillow 列首{'/'.join(c[0] for c in columns)} 违例{pillow_v['total']}", 16)
    draw_label(draw, (box_w + 30, box_h + 24), f"Chromium 列首{'/'.join(c[0] for c in html_columns)} 违例{kinsoku_violations(html_columns)['total']}", 16)
    draw_label(draw, (10, box_h + 48), f"font-size {size:g}px, box {box_w}x{box_h}, controlled string: あx7 、 いx7 。 うx7", 14)
    path = ROUTES / "kinsoku_probe.png"
    canvas.save(path)
    return path, {
        "text": text,
        "box": [box_w, box_h],
        "font_size": size,
        "pillow_columns": columns,
        "pillow_violations": pillow_v,
        "web_columns": html_columns,
        "web_violations": kinsoku_violations(html_columns),
    }


def kinsoku_measure_html(text: str, size: float, box_w: int, box_h: int) -> dict:
    js = MEASURE_JS.replace(
        """const boxEl = document.getElementById('box');
const textEl = document.getElementById('text');""",
        """const boxEl = document.getElementById('box');
const textEl = document.getElementById('text');
if (!textEl) { throw new Error('no text'); }""",
    )
    body = f"""
<div id="box" style="position:absolute;left:0;top:0;width:{box_w}px;height:{box_h}px;
     display:flex;justify-content:center;align-items:flex-start;overflow:hidden">
  <div id="text" style="writing-mode:vertical-rl;height:100%;font-family:'Microsoft YaHei';
       font-size:{size:g}px;line-height:{size:g}px;line-break:strict">{text}</div>
</div>
<pre id="result" style="font-size:1px"></pre>
<script>{js}</script>
"""
    html_path = HTML_DIR / "kinsoku_measure.html"
    html_path.write_text(html_page(body, width=box_w, height=box_h), encoding="utf-8")
    dom = run_edge_dump_dom(html_path, timeout=120)
    return parse_dump_dom(dom)


def make_stroke_probe() -> tuple[Path, dict]:
    text = "縦組あア漢"
    size = 44.0
    width, height = 560, 200
    cell_w, cell_h = 540, 170
    # current
    catalog = PillowFontCatalog()
    engine = PillowTextLayoutEngine(catalog)
    layout = engine.layout(
        LayoutRequest(
            text=text,
            font_family=FONT_FAMILY,
            font_size=size,
            direction=TextDirection.VERTICAL,
            box_width=cell_w,
            box_height=cell_h,
            stroke_width=STROKE_WIDTH,
        )
    )
    op = RenderOp(
        items=layout.items,
        region_x=10,
        region_y=10,
        region_width=cell_w,
        region_height=cell_h,
        font_family=catalog.resolve(FONT_FAMILY).resolved_family,
        font_size=size,
        text_color="#000000",
        stroke_enabled=True,
        stroke_color="#FFFFFF",
        stroke_width=STROKE_WIDTH,
        direction=TextDirection.VERTICAL,
    )
    base = Image.new("RGB", (cell_w + 20, cell_h + 20), (128, 128, 128))
    composed = Image.open(
        io.BytesIO(PillowImageCompositor(catalog).compose_page(png_bytes(base), (op,)))
    ).convert("RGB")
    body = f"""
<div style="position:absolute;left:10px;top:10px;width:{cell_w}px;height:{cell_h}px;
     background:#808080;display:flex;justify-content:center;align-items:flex-start">
  <div style="writing-mode:vertical-rl;height:100%;font-family:'Microsoft YaHei';
       font-size:{size:g}px;line-height:{size:g}px;color:#000;
       -webkit-text-stroke:{STROKE_WIDTH:g}px #fff;paint-order:stroke fill">{text}</div>
</div>
"""
    html_path = HTML_DIR / "stroke_probe.html"
    html_path.write_text(html_page(body, width=cell_w + 20, height=cell_h + 20), encoding="utf-8")
    shot = ROUTES / "_probe_stroke_web.png"
    screenshot(html_path, shot, width=cell_w + 20, height=cell_h + 20)
    web = Image.open(shot).convert("RGB")
    canvas = Image.new("RGB", (cell_w * 2 + 50, cell_h + 90), "white")
    canvas.paste(composed, (10, 10))
    canvas.paste(web, (cell_w + 40, 10))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (10, cell_h + 24), "Pillow: stroke_width=3 (stroke under fill)", 16)
    draw_label(draw, (cell_w + 40, cell_h + 24), "Chromium: -webkit-text-stroke 3px + paint-order:stroke fill", 16)
    path = ROUTES / "stroke_aa_probe.png"
    canvas.save(path)
    return path, {
        "text": text,
        "font_size": size,
        "pillow_analysis": analyze_dark_text(composed, (10, 10, cell_w, cell_h)),
        "web_analysis": analyze_dark_text(web, (10, 10, cell_w, cell_h)),
    }


def analyze_dark_text(image: Image.Image, box: tuple[int, int, int, int]) -> dict:
    arr = np.asarray(image.convert("L"))
    x, y, w, h = box
    crop = arr[y : y + h, x : x + w]
    dark = crop < 60  # glyph fill (black)
    bright = crop > 200  # white stroke on dark ground
    mid = (crop >= 60) & (crop <= 200)
    ys, xs = np.nonzero(dark)
    return {
        "fill_pixels": int(dark.sum()),
        "stroke_pixels": int(bright.sum()),
        "mid_pixels": int(mid.sum()),
        "ink_bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
        "distinct_gray_levels": int(len(np.unique(crop))),
    }


# ---------------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------------
def main() -> int:
    ROUTES.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(exist_ok=True)
    metrics: dict = {"generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds")}

    clean, clean_meta = build_clean_plate()
    clean.save(ROUTES / "page_clean_plate.png")
    metrics["base"] = clean_meta
    metrics["base"]["text_box"] = list(TEXT_BOX)
    metrics["text"] = MAIN_TEXT
    metrics["environment"] = {
        "python": sys.version.split()[0],
        "pillow": Image.__version__,
        "pillow_features_raqm": bool(__import__("PIL.features", fromlist=["features"]).check("raqm")),
        "edge_version": subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"(Get-Item '{EDGE}').VersionInfo.ProductVersion"],
            capture_output=True, text=True,
        ).stdout.strip(),
    }

    catalog = PillowFontCatalog()
    metrics["font_current"] = measure_font_metrics(catalog, FONT_FAMILY, FONT_SIZE_FALLBACK)
    metrics["font_current_bold_check"] = {
        "requested": FONT_FAMILY,
        "note": "default D03 11.6 family is not installed on this machine; fallback chain has no Japanese family",
    }

    current = current_layout(MAIN_TEXT, TEXT_BOX, catalog, FONT_FAMILY)
    size = current["resolution"].final_font_size
    pillow_columns = columns_from_items(current["layout"].items)
    metrics["current_pillow"] = {
        "requested_family": FONT_FAMILY,
        "resolved_family": current["resolved"].resolved_family,
        "font_available": current["resolved"].available,
        "final_font_size": size,
        "resolution": current["resolution"].__dict__,
        "layout_fits": current["layout"].fits,
        "extents": [current["layout"].extents_width, current["layout"].extents_height],
        "column_count": len(pillow_columns),
        "columns": pillow_columns,
        "kinsoku": kinsoku_violations(pillow_columns),
        "items": len(current["layout"].items),
    }

    # newline handling test (vertical engine)
    nl_text = MAIN_TEXT + "\n" + "追記"
    nl_layout = current["engine"].layout(
        LayoutRequest(
            text=nl_text,
            font_family=FONT_FAMILY,
            font_size=size,
            direction=TextDirection.VERTICAL,
            box_width=TEXT_BOX[2],
            box_height=TEXT_BOX[3],
            stroke_width=STROKE_WIDTH,
        )
    )
    plain_layout = current["engine"].layout(
        LayoutRequest(
            text=MAIN_TEXT,
            font_family=FONT_FAMILY,
            font_size=size,
            direction=TextDirection.VERTICAL,
            box_width=TEXT_BOX[2],
            box_height=TEXT_BOX[3],
            stroke_width=STROKE_WIDTH,
        )
    )
    metrics["current_pillow"]["newline_and_space_handling"] = {
        "input_has_newline_and_appendix": True,
        "appendix_chars": "追記",
        "items_without_appendix": len(plain_layout.items),
        "items_with_appendix": len(nl_layout.items),
        "appendix_rendered": len(nl_layout.items) > len(plain_layout.items),
        "note": "vertical layout strips every character where str.isspace() is true (spaces + newlines)",
    }

    base_image = Image.open(ROUTES / "page_clean_plate.png").convert("RGB")
    # Large base64 data URIs made old-headless Edge fail silently on this machine, so the
    # HTML references a sibling JPEG file instead (small HTML, same pixels for both sides).
    base_image.save(HTML_DIR / "page_clean.jpg", format="JPEG", quality=95, subsampling=0)
    composed = PillowImageCompositor(catalog).compose_page(png_bytes(base_image), (current["op"],))
    current_page_path = ROUTES / "sample_current_pillow.png"
    current_page = Image.open(io.BytesIO(composed)).convert("RGB")
    current_page.save(current_page_path)

    # --- Chromium sample: identical page, box, font family and resolved font size ---
    background_uri = "page_clean.jpg"
    sample_path = HTML_DIR / "sample_webview2_vertical_rl.html"
    sample_path.write_text(
        sample_html(
            background_uri,
            TEXT_BOX,
            MAIN_TEXT,
            {
                "font_family": current["resolved"].resolved_family,
                "font_size": f"{size:g}",
                "line_height": f"{max(1.0, round((current['layout'].extents_width / max(1, len(pillow_columns)))))}px",
                "extra": "-webkit-text-stroke:3px #FFFFFF;paint-order:stroke fill;line-break:strict;text-combine-upright:all;",
            },
        ),
        encoding="utf-8",
    )
    web_page_path = ROUTES / "sample_webview2_vertical_rl.png"
    screenshot(sample_path, web_page_path)
    web_page = Image.open(web_page_path).convert("RGB")

    # --- tuned Chromium sample: explicit column distribution + justify + JP font ---
    per_col = max(1, int(np.ceil(len(MAIN_TEXT) / 4.0)))
    chunks = [MAIN_TEXT[i : i + per_col] for i in range(0, len(MAIN_TEXT), per_col)]
    tuned_text = "<br>".join(chunks)
    tuned_path = HTML_DIR / "sample_webview2_tuned.html"
    tuned_path.write_text(
        sample_html(
            background_uri,
            TEXT_BOX,
            tuned_text,
            {
                "font_family": JP_FONT,
                "font_size": f"{size:g}",
                "line_height": f"{size * 1.5:g}px",
                "extra": "-webkit-text-stroke:3px #FFFFFF;paint-order:stroke fill;line-break:strict;text-combine-upright:all;text-align:justify;",
            },
        ),
        encoding="utf-8",
    )
    tuned_page_path = ROUTES / "sample_webview2_tuned.png"
    screenshot(tuned_path, tuned_page_path)

    # --- measurement page (same text/box; no image, measures layout) ---
    measure_path = HTML_DIR / "measure.html"
    measure_path.write_text(measure_html(), encoding="utf-8")
    dom = run_edge_dump_dom(measure_path, timeout=120)
    measured = parse_dump_dom(dom)
    web_columns = measured.get("columns", [])
    metrics["webview2"] = {
        "css_supports": measured.get("supports"),
        "computed": measured.get("computed"),
        "column_count": measured.get("columnCount"),
        "columns": web_columns,
        "column_geometry": measured.get("columnGeometry"),
        "char_count": measured.get("charCount"),
        "kinsoku": kinsoku_violations(web_columns),
        "overflow": measured.get("overflow"),
        "combine_upright": measured.get("combineUpright"),
        "shrink_to_fit_probe": measured.get("narrowBox"),
        "canvas_measure_text": measured.get("canvasText"),
        "user_agent": measured.get("userAgent"),
        "shaping_probe": {
            "kerning_AV": measured.get("canvasText", {}).get("AV"),
            "kerning_A_plus_V": (
                (measured.get("canvasText", {}).get("A") or 0)
                + (measured.get("canvasText", {}).get("V") or 0)
            ),
            "ligature_fi": measured.get("canvasText", {}).get("fi"),
            "ligature_f_plus_i": (
                (measured.get("canvasText", {}).get("f") or 0)
                + (measured.get("canvasText", {}).get("i") or 0)
            ),
        },
    }

    metrics["pixel_analysis"] = {
        "pillow_text_region": analyze_text_png(current_page_path, TEXT_BOX),
        "webview2_text_region": analyze_text_png(web_page_path, TEXT_BOX),
        "tuned_text_region": analyze_text_png(tuned_page_path, TEXT_BOX),
    }

    # --- probes ---
    probe_path, probe_metrics = make_punctuation_probe(list("。、「」！？ーっ12"))
    metrics["punctuation_probe"] = probe_metrics
    kin_path, kin_metrics = make_kinsoku_probe()
    metrics["kinsoku_probe"] = kin_metrics
    stroke_path, stroke_metrics = make_stroke_probe()
    metrics["stroke_probe"] = stroke_metrics

    # --- side by side + zoom figure ---
    full_w, full_h = 1350, 1920
    scale = 0.42
    thumb_w, thumb_h = int(full_w * scale), int(full_h * scale)
    top_h = thumb_h + 46
    zoom_scale = 1.5
    zoom_w = int(TEXT_BOX[2] * zoom_scale)
    zoom_h = int(TEXT_BOX[3] * zoom_scale)
    bottom_h = zoom_h + 52
    canvas = Image.new("RGB", (max(2 * thumb_w + 60, 2 * zoom_w + 80), top_h + bottom_h + 20), "white")
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (20, 8), "current: PillowTextLayoutEngine + PillowImageCompositor (production adapters)", 18)
    draw_label(draw, (40 + thumb_w, 8), "alternative: Edge/WebView2 vertical-rl (same page, box, font, size)", 18)
    canvas.paste(current_page.resize((thumb_w, thumb_h), Image.LANCZOS), (20, 34))
    canvas.paste(web_page.resize((thumb_w, thumb_h), Image.LANCZOS), (40 + thumb_w, 34))
    zy = top_h + 6
    draw_label(draw, (20, zy), f"zoom x{zoom_scale:g}: Pillow", 16)
    draw_label(draw, (40 + zoom_w, zy), f"zoom x{zoom_scale:g}: Chromium", 16)
    canvas.paste(zooms(current_page, TEXT_BOX, zoom_scale), (20, zy + 26))
    canvas.paste(zooms(web_page, TEXT_BOX, zoom_scale), (40 + zoom_w, zy + 26))
    side_path = ROUTES / "typesetting_side_by_side.png"
    canvas.save(side_path)

    # row labels for probes are drawn inside each probe already
    metrics["outputs"] = {
        "page_clean_plate": str((ROUTES / "page_clean_plate.png").relative_to(ROOT)).replace("\\", "/"),
        "sample_current_pillow": str(current_page_path.relative_to(ROOT)).replace("\\", "/"),
        "sample_webview2_vertical_rl": str(web_page_path.relative_to(ROOT)).replace("\\", "/"),
        "sample_webview2_tuned": str(tuned_page_path.relative_to(ROOT)).replace("\\", "/"),
        "typesetting_side_by_side": str(side_path.relative_to(ROOT)).replace("\\", "/"),
        "punctuation_probe": str(probe_path.relative_to(ROOT)).replace("\\", "/"),
        "kinsoku_probe": str(kin_path.relative_to(ROOT)).replace("\\", "/"),
        "stroke_probe": str(stroke_path.relative_to(ROOT)).replace("\\", "/"),
        "html_dir": str(HTML_DIR.relative_to(ROOT)).replace("\\", "/"),
    }
    (ROUTES / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log(json.dumps({k: metrics[k] for k in ("environment", "current_pillow", "webview2")}, ensure_ascii=False, indent=2)[:6000])
    log("WROTE " + str(side_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



