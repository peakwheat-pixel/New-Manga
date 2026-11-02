"""Shared fixtures for the M2-RC1 resource-channel tests.

Deterministic synthetic fixtures only (M2-S1/S2 method): RGB-noise PNGs from
fixed seeds, sealed to pytest's tmp_path. Nothing here touches a user
library, credentials or model caches. Scope-internal assets are independent
copies, never hardlinks (M2-S2 lesson: content writes traverse hardlinks).
"""

from __future__ import annotations

import hashlib
import struct
import sys
import zlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.resource_channel import (  # noqa: E402
    ResourceChannelService,
    ResourceFacts,
)
from infrastructure.resource_channel.handle_resolver import (  # noqa: E402
    HandleVerifiedFileReader,
)


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_noise_png(path: Path, width: int, height: int, seed: int) -> bytes:
    import random

    rng = random.Random(seed)
    stride = width * 3
    compressor = zlib.compressobj(6)
    parts = []
    for _ in range(height):
        parts.append(compressor.compress(b"\x00" + rng.randbytes(stride)))
    parts.append(compressor.flush())
    payload = b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            _png_chunk(b"IDAT", b"".join(parts)),
            _png_chunk(b"IEND", b""),
        )
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ScopeLayout:
    """Lab scope layout: derived-cache scope root + adversary outside tree."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.derived = root / "scope" / "derived"
        self.managed = root / "scope" / "managed"
        self.outside = root / "outside"
        for directory in (self.derived, self.managed, self.outside):
            directory.mkdir(parents=True, exist_ok=True)

    def place_copy(self, rel_path: str, payload: bytes) -> Path:
        target = self.derived.joinpath(*rel_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target

    def place_outside(self, name: str, payload: bytes) -> Path:
        target = self.outside / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target


@pytest.fixture()
def scope(tmp_path: Path) -> ScopeLayout:
    layout = ScopeLayout(tmp_path / "lab")
    small = write_noise_png(layout.derived / "asset.png", 64, 64, seed=4101)
    write_noise_png(layout.derived / "typical.png", 128, 128, seed=4202)
    write_noise_png(layout.derived / "pages" / "page-002.png", 64, 64, seed=4303)
    write_noise_png(layout.outside / "outside_secret.png", 64, 64, seed=4404)
    layout.small_payload = small  # type: ignore[attr-defined]
    layout.small_sha = sha256_hex(small)  # type: ignore[attr-defined]
    return layout


@pytest.fixture()
def reader(scope: ScopeLayout) -> HandleVerifiedFileReader:
    return HandleVerifiedFileReader(scope.derived)


@pytest.fixture()
def service() -> ResourceChannelService:
    return ResourceChannelService()


def issue_for(reader: HandleVerifiedFileReader, service: ResourceChannelService,
              scope: ScopeLayout, rel_path: str = "asset.png",
              resource_id: str = "res-001", revision: str = "rev-1",
              scope_class: str = "derived-read-only") -> str:
    facts = reader.capture_facts(rel_path)
    return service.issue(
        scope_class=scope_class,
        resource_id=resource_id,
        revision_fingerprint=revision,
        rel_path=rel_path,
        facts=facts,
    )


__all__ = [
    "ScopeLayout",
    "issue_for",
    "sha256_hex",
    "write_noise_png",
    "ResourceChannelService",
    "ResourceFacts",
    "HandleVerifiedFileReader",
]
