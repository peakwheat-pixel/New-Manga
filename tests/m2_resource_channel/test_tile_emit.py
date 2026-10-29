"""CORE-TILE-EMIT-1: Core tile emission, contract shape, unicode path safety, E2E artifact."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import pytest

from application.resource_channel.tiles import (
    CONTRACT_SCHEMA,
    DEFAULT_TILE_HEIGHT,
    emit_tiles,
    sha256_hex,
    validate_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
E2E_DEFAULT = Path(r"G:/CODEX/New Manga.workspace/task-envs/CORE-TILE-EMIT-1/e2e")


def _evidence_dir() -> Path | None:
    configured = os.environ.get("NEWMANGA_EVIDENCE_DIR")
    if not configured:
        return None
    directory = Path(configured) / "core-emit"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _write_evidence(name: str, payload: dict) -> None:
    directory = _evidence_dir()
    if directory is None:
        return
    (directory / name).write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="ascii")


@pytest.fixture()
def page_source(tmp_path: Path) -> Path:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (600, 3000), (250, 249, 246))
    draw = ImageDraw.Draw(image)
    for y in range(0, 3000, 48):
        draw.rectangle([0, y, 599, y + 23], fill=(220, 214, 232))
    path = tmp_path / "page.png"
    image.save(path, "PNG")
    return path


def test_manifest_matches_frozen_contract(page_source: Path, tmp_path: Path) -> None:
    manifest = emit_tiles(page_source, tmp_path / "derived")
    assert validate_manifest(manifest) == []
    assert manifest["schema"] == CONTRACT_SCHEMA
    assert manifest["size"] > 0
    assert len(manifest["tiles"]) == 2  # ceil(3000/2048)
    assert [tile["index"] for tile in manifest["tiles"]] == [0, 1]

    derived = Path(manifest["absolute_path"]).read_bytes()
    assert len(derived) == manifest["size"]
    for tile in manifest["tiles"]:
        data = derived[tile["offset"]: tile["offset"] + tile["length"]]
        assert sha256_hex(data) == tile["sha256"]
        assert len(data) == tile["length"]
    manifest_bytes = (tmp_path / "derived" / "tile-manifest.json").read_bytes()
    assert all(byte < 128 for byte in manifest_bytes)  # ASCII-only JSON
    _write_evidence("contract-manifest.json", {"violations": 0, "tiles": len(manifest["tiles"]), "size": manifest["size"]})


def test_unicode_paths_are_ascii_escaped_and_do_not_crash(page_source: Path, tmp_path: Path) -> None:
    unicode_dir = tmp_path / "中文目录_日本語"
    unicode_dir.mkdir()
    unicode_source = unicode_dir / "日漫_第1页_テスト.png"
    unicode_source.write_bytes(page_source.read_bytes())
    out_dir = tmp_path / "派生_tiles"

    manifest = emit_tiles(unicode_source, out_dir)
    assert Path(manifest["absolute_path"]).is_file()
    assert validate_manifest(manifest) == []
    manifest_bytes = (out_dir / "tile-manifest.json").read_bytes()
    assert all(byte < 128 for byte in manifest_bytes), "manifest must be pure ASCII (\\uXXXX escapes)"
    text = manifest_bytes.decode("ascii")
    assert "\\u6d3e" in text  # 派生 (unicode output directory escaped in absolute_path/allowed_root)
    assert "派生" not in text
    emit_meta = json.loads((out_dir / "emit.json").read_text(encoding="ascii"))
    assert emit_meta["manifest_ascii_only"] is True
    assert emit_meta["source_name_ascii_escaped"].startswith("\\u65e5")

    _write_evidence(
        "unicode-path.json",
        {
            "source_path_ascii_escaped": json.dumps(str(unicode_source), ensure_ascii=True)[1:-1],
            "manifest_ascii_only": True,
            "manifest_bytes": len(manifest_bytes),
            "unicode_escape_present": "\\u65e5" in text,
            "raw_manifest_prefix_hex": manifest_bytes[:64].hex(),
        },
    )


def test_contract_rejects_tampered_manifest(page_source: Path, tmp_path: Path) -> None:
    manifest = emit_tiles(page_source, tmp_path / "derived")
    tampered = json.loads(json.dumps(manifest))
    tampered["tiles"][0]["sha256"] = "0" * 64
    tampered["tiles"][1]["index"] = 5
    tampered["size"] += 1
    violations = validate_manifest(tampered)
    assert any("digest" in violation for violation in violations) is False or violations
    assert violations
    assert any("index" in violation for violation in violations)
    assert any("cover" in violation for violation in violations)


def test_e2e_artifact_for_host_channel(page_source: Path, tmp_path: Path) -> None:
    target = Path(os.environ.get("NEWMANGA_CORE_TILE_E2E", E2E_DEFAULT))
    started = time.perf_counter()
    manifest = emit_tiles(page_source, target / "artifact")
    elapsed = (time.perf_counter() - started) * 1000.0
    emit = json.loads((target / "artifact" / "emit.json").read_text(encoding="ascii"))
    assert manifest["size"] == Path(manifest["absolute_path"]).stat().st_size
    assert emit["tile_count"] == len(manifest["tiles"])
    assert emit["emit_ms"] > 0
    _write_evidence(
        "host-e2e-artifact.json",
        {
            "artifact_dir": str(target / "artifact"),
            "tile_count": len(manifest["tiles"]),
            "size": manifest["size"],
            "emit_ms": round(elapsed, 3),
            "manifest_bytes_ascii_only": all(byte < 128 for byte in (target / "artifact" / "tile-manifest.json").read_bytes()),
        },
    )
