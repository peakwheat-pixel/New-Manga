"""Core-side tile emission (CORE-TILE-EMIT-1).

Aligns with the frozen Host contract ``apps/desktop-avalonia/docs/TILE-CHANNEL-CONTRACT-V1.md``:
a rendered page is cut into horizontal bands (default 2048 px tall), the bands are concatenated
into one derived byte stream, and a manifest lists ``resource_id/revision/size/tiles[index,offset,length,sha256]``.

Backward compatibility: this is a new, standalone module. It adds no field to protocol 2.3 and does
not change any existing command/DTO; the manifest is additive data handed to the trusted Host layer.

Unicode: paths are handled with ``pathlib`` (no locale-dependent encoding); manifests are written with
``ensure_ascii=True`` so every non-ASCII path/name appears as ``\\uXXXX`` and the bytes stay pure ASCII.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

CONTRACT_SCHEMA = "tile-channel-contract/v1"
DEFAULT_TILE_HEIGHT = 2048
DEFAULT_TTL_MS = 300_000
REQUIRED_MANIFEST_FIELDS = (
    "schema",
    "resource_id",
    "revision",
    "size",
    "absolute_path",
    "allowed_root",
    "tiles",
)
REQUIRED_TILE_FIELDS = ("index", "offset", "length", "sha256")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_page_bands(source: Path, tile_height: int = DEFAULT_TILE_HEIGHT) -> list[bytes]:
    """Cut a rendered page into horizontal PNG bands (whole width, ``tile_height`` rows)."""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - Pillow is a Core dependency
        raise TileEmitError("TILE_PIL_UNAVAILABLE", "Pillow is required") from exc

    bands: list[bytes] = []
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        for top in range(0, rgb.height, tile_height):
            bottom = min(top + tile_height, rgb.height)
            band = rgb.crop((0, top, rgb.width, bottom))
            buffer = io.BytesIO()
            band.save(buffer, format="PNG", optimize=False)
            bands.append(buffer.getvalue())
    if not bands:
        raise TileEmitError("TILE_EMPTY_IMAGE", "source image has no rows")
    return bands


class TileEmitError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def emit_tiles(
    source: str | Path,
    out_dir: str | Path,
    *,
    resource_id: str | None = None,
    revision: str | None = None,
    tile_height: int = DEFAULT_TILE_HEIGHT,
) -> dict[str, Any]:
    """Emit one page's tiles and return the contract-shaped manifest."""
    started = time.perf_counter()
    source_path = Path(source)
    out = Path(out_dir)
    if not source_path.is_file():
        raise TileEmitError("TILE_SOURCE_MISSING", "source render is not a file")
    out.mkdir(parents=True, exist_ok=True)

    bands = split_page_bands(source_path, tile_height)
    page_bytes = b"".join(bands)
    derived_path = out / "page.bin"
    derived_path.write_bytes(page_bytes)

    digest_started = time.perf_counter()
    tiles: list[dict[str, Any]] = []
    offset = 0
    for index, band in enumerate(bands):
        tiles.append({"index": index, "offset": offset, "length": len(band), "sha256": sha256_hex(band)})
        offset += len(band)
    digest_ms = (time.perf_counter() - digest_started) * 1000.0

    page_digest = sha256_hex(page_bytes)
    manifest: dict[str, Any] = {
        "schema": CONTRACT_SCHEMA,
        "resource_id": resource_id or f"page:{page_digest[:16]}",
        "revision": revision or page_digest,
        "size": len(page_bytes),
        "absolute_path": str(derived_path.resolve()),
        "allowed_root": str(out.resolve()),
        "ttl_ms": DEFAULT_TTL_MS,
        "tiles": tiles,
    }
    violations = validate_manifest(manifest)
    if violations:
        raise TileEmitError("TILE_MANIFEST_INVALID", "; ".join(violations))

    manifest_path = out / "tile-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="ascii")
    (out / "emit.json").write_text(
        json.dumps(
            {
                "schema": CONTRACT_SCHEMA,
                "tile_height": tile_height,
                "tile_count": len(tiles),
                "source_width": _image_size(source_path)[0],
                "source_height": _image_size(source_path)[1],
                "page_bytes": len(page_bytes),
                "emit_ms": round((time.perf_counter() - started) * 1000.0, 3),
                "digest_ms": round(digest_ms, 3),
                "source_name_ascii_escaped": _ascii_escaped(source_path.name),
                "manifest_ascii_only": True,
            },
            ensure_ascii=True,
            indent=2,
        ),
        encoding="ascii",
    )
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return contract violations (empty list = valid). Mirrors the frozen Host contract."""
    violations: list[str] = []
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            violations.append(f"missing field: {field}")
    if violations:
        return violations
    if manifest["schema"] != CONTRACT_SCHEMA:
        violations.append("schema mismatch")
    if not isinstance(manifest["resource_id"], str) or not manifest["resource_id"].startswith("page:"):
        violations.append("resource_id must be page:<id>")
    if not isinstance(manifest["size"], int) or manifest["size"] <= 0:
        violations.append("size must be a positive int")
    tiles = manifest["tiles"]
    if not isinstance(tiles, list) or not tiles:
        return violations + ["tiles must be a non-empty list"]
    expected_offset = 0
    for index, tile in enumerate(tiles):
        if not isinstance(tile, dict):
            violations.append(f"tile {index} is not an object")
            continue
        for field in REQUIRED_TILE_FIELDS:
            if field not in tile:
                violations.append(f"tile {index} missing {field}")
        if violations:
            return violations
        if tile["index"] != index:
            violations.append(f"tile index gap at {index}")
        if tile["offset"] != expected_offset:
            violations.append(f"tile {index} offset not contiguous")
        if not isinstance(tile["length"], int) or tile["length"] <= 0:
            violations.append(f"tile {index} length invalid")
        digest = tile["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            violations.append(f"tile {index} digest is not 64-hex lower-case")
        expected_offset += tile["length"]
    if expected_offset != manifest["size"]:
        violations.append("tiles do not cover size")
    return violations


def _image_size(source: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(source) as image:
        return image.width, image.height


def _ascii_escaped(text: str) -> str:
    return json.dumps(text, ensure_ascii=True)[1:-1]


def _synthetic_source(out: Path, width: int, height: int) -> Path:
    from PIL import Image, ImageDraw

    out.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (width, height), (248, 246, 242))
    draw = ImageDraw.Draw(image)
    for y in range(0, height, 64):
        draw.rectangle([0, y, width - 1, min(y + 31, height - 1)], fill=(225, 219, 235))
    for x in range(0, width, width // 8 or 1):
        draw.rectangle([x, 0, min(x + 7, width - 1), height - 1], fill=(196, 178, 214))
    path = out / "日漫_合成页_テスト.png"
    image.save(path, "PNG")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit Core tiles according to TILE-CHANNEL-CONTRACT-V1")
    parser.add_argument("--source", type=Path, help="rendered page image")
    parser.add_argument("--out", type=Path, required=True, help="derived output directory")
    parser.add_argument("--synthetic", help="generate synthetic page, e.g. 1200x2400")
    parser.add_argument("--tile-height", type=int, default=DEFAULT_TILE_HEIGHT)
    args = parser.parse_args(argv)
    try:
        source = args.source
        if source is None:
            if not args.synthetic:
                parser.error("either --source or --synthetic is required")
            width_text, _, height_text = args.synthetic.partition("x")
            source = _synthetic_source(args.out, int(width_text), int(height_text))
        manifest = emit_tiles(source, args.out, tile_height=args.tile_height)
        print(json.dumps({"ok": True, "manifest": str(args.out / "tile-manifest.json"), "size": manifest["size"], "tiles": len(manifest["tiles"]), "resource_id": manifest["resource_id"]}, ensure_ascii=True))
        return 0
    except TileEmitError as error:
        print(json.dumps({"ok": False, "code": error.code, "message": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
