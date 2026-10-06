"""RC-4 production stdio rerender through NMFR, Managed Copy and preview channel."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
REPO_ROOT = SRC_ROOT.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource
from bootstrap.core_service import PROTOCOL_MAJOR, PROTOCOL_MINOR, assemble_production_core
from domain.regions.entities import BBox, RegionGeometry, RegionType, SfxPolicy
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.sqlite.artifacts import SqliteArtifactRepository
from ports.inpaint.ports import ImageFrame
from ports.repositories.artifacts import (
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)
from infrastructure.providers.step_writes import artifact_payload_from_frame


NOW = "2026-01-01T00:00:00.000+00:00"


def _seed_book_and_chapter(core) -> None:
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('chapter','book','c',?,?)",
            (NOW, NOW),
        )


def _commit_artifact(core, page, artifact_type: ArtifactType, payload: bytes, mime: str):
    artifacts = SqliteArtifactRepository(core.conn, core.storage)
    record = artifacts.create_artifact(
        NewArtifact(
            book_id="book",
            chapter_id=page.chapter_id,
            page_id=page.page_id,
            artifact_type=artifact_type,
        )
    )
    result = artifacts.commit_revision(
        PendingArtifactCommit(
            artifact_id=record.artifact_id,
            content_provider=ContentProvider(payload=payload),
            mime_type=mime,
            expected_current_revision_id=None,
            file_suffix=".bin" if mime == "application/x-newmanga-frame" else ".png",
        )
    )
    assert result.status.value == "committed", result.detail


def _rpc(command: str, request_id: str, payload: dict) -> str:
    return json.dumps(
        {
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id,
            "command": command,
            "payload": payload,
        }
    )


def test_production_stdio_decodes_nmfr_renders_text_and_publishes_readable_preview(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    source_path = tmp_path / "source.png"
    original = Image.new("RGBA", (300, 180), (24, 50, 210, 255))
    original.save(source_path, format="PNG")

    core = assemble_production_core(data_root)
    _seed_book_and_chapter(core)
    report = core.importer.import_files(
        "chapter",
        [ImportSource("source.png", source_path.read_bytes)],
    )
    assert not report.failed and len(report.imported) == 1
    page = core.repository.get_page(report.imported[0].page.page_id)
    assert page is not None and page.managed_original_ref

    # This is the same provider artifact container consumed by production
    # rerendering: NMFR header + rgb32 payload, rather than a test-only PNG.
    # RGB32 in QImage memory is BGRA on this Windows product host. A colored
    # clean base makes the NMFR channel order observable outside all regions.
    frame = ImageFrame(300, 180, "rgb32", b"\x20\x40\xf0\xff" * (300 * 180))
    clean_payload, clean_mime, _, _ = artifact_payload_from_frame(frame)
    _commit_artifact(core, page, ArtifactType.CLEAN, clean_payload, clean_mime)

    speech = core.editing.create_region(
        page.page_id,
        RegionGeometry(bbox=BBox(20, 20, 130, 100)),
    )
    core.editing.save_manual_translation(speech.region_id, "VISIBLE TEXT")
    core.editing.confirm_final(speech.region_id)
    sfx = core.editing.create_region(
        page.page_id,
        RegionGeometry(bbox=BBox(180, 20, 80, 80)),
        region_type=RegionType.SFX,
        sfx_policy=SfxPolicy.SKIP,
        reading_order=2,
    )
    core.editing.save_manual_translation(sfx.region_id, "DO NOT DRAW SFX")
    core.editing.confirm_final(sfx.region_id)

    # Normal import owns the source in Page.managed_original_ref; no ORIGINAL
    # media_artifacts row is fabricated for this fixture.
    assert core.conn.execute(
        "SELECT COUNT(*) FROM media_artifacts WHERE page_id=? AND artifact_type='original'",
        (page.page_id,),
    ).fetchone()[0] == 0
    core.conn.close()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["NEWMANGA_DATA_ROOT"] = str(data_root)
    env["M2RC1_DERIVED_ROOT"] = str(derived_root)
    env["M2RC2_CATALOG_DB"] = str(catalog_db)
    completed = subprocess.run(
        [sys.executable, "-m", "bootstrap.core_service"],
        cwd=REPO_ROOT,
        env=env,
        input=(
            _rpc("rerender_page", "render-1", {"page_id": page.page_id})
            + "\n"
            + _rpc("core.shutdown", "shutdown-1", {})
            + "\n"
        ),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    responses = [json.loads(line) for line in completed.stdout.splitlines() if line]
    assert len(responses) == 2, completed.stdout
    response = responses[0]
    assert response["error"] is None, response
    result = response["result"]
    assert result["page_id"] == page.page_id
    assert result["revision_no"] == 1
    assert result["preview_error"] is None
    assert result["preview"] is not None
    assert set(result["preview"]) == {"resource_id", "revision"}
    assert result["preview"]["revision"] == "rev-1"
    by_region = {item["region_id"]: item for item in result["reports"]}
    assert by_region[speech.region_id]["status"] == "rendered"
    assert by_region[sfx.region_id]["status"] == "skipped"
    assert by_region[sfx.region_id]["skip_reason"] == "skip_policy"

    # The real resource-channel stdio bridge issues/resolves the opaque
    # catalog entry; preview bytes stay out of JSON and are read by the host.
    catalog = ResourceCatalogStore(catalog_db)
    try:
        entry = catalog.lookup(result["preview"]["resource_id"])
        assert entry is not None
        assert entry.scope_class == "derived-read-only"
        channel_env = env.copy()
        channel_env["M2RC1_MANAGED_ROOT"] = str(data_root / "managed")
        bridge = subprocess.Popen(
            [sys.executable, "-m", "infrastructure.resource_channel.host_bridge"],
            cwd=REPO_ROOT,
            env=channel_env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert bridge.stdin is not None and bridge.stdout is not None
            bridge.stdin.write(json.dumps({
                "id": 1,
                "method": "issue",
                "params": {
                    "resource_id": entry.resource_id,
                    "revision_fingerprint": result["preview"]["revision"],
                },
            }) + "\n")
            bridge.stdin.flush()
            issued = json.loads(bridge.stdout.readline())
            assert "result" in issued, issued
            opaque_id = issued["result"]["id"]
            bridge.stdin.write(json.dumps({
                "id": 2, "method": "resolve", "params": {"id": opaque_id}
            }) + "\n")
            bridge.stdin.flush()
            resolved = json.loads(bridge.stdout.readline())["result"]
            bridge.stdin.write(json.dumps({"id": 3, "method": "shutdown", "params": {}}) + "\n")
            bridge.stdin.flush()
            bridge.stdin.close()
            bridge.wait(timeout=10)
            assert bridge.returncode == 0
        finally:
            if bridge.poll() is None:
                bridge.kill()
                bridge.wait(timeout=5)
        preview_path = (derived_root / resolved["rel_path"]).resolve()
        preview_path.relative_to(derived_root.resolve())
        preview_bytes = preview_path.read_bytes()
        assert len(preview_bytes) == resolved["size"]
        assert hashlib.sha256(preview_bytes).hexdigest() == resolved["sha256"]
    finally:
        catalog.close()

    with Image.open(preview_path) as rendered:
        rendered.load()
        with Image.open(source_path) as source:
            source.load()
            assert ImageChops.difference(
                    rendered.crop((180, 20, 260, 100)).convert("RGB"),
                    source.crop((180, 20, 260, 100)).convert("RGB"),
            ).getbbox() is None
        assert ImageChops.difference(
            rendered.crop((20, 20, 150, 120)).convert("RGB"),
            Image.new("RGB", (130, 100), (240, 64, 32)),
        ).getbbox() is not None
        # RC4-02: "not the bare background" is too weak -- a composition bug
        # could pass it with any stray pixel. The confirmed speech region must
        # carry real glyph ink; 400 is ~30% of the measured 1389 ink pixels
        # for "VISIBLE TEXT", far above the ~0 of an empty composition.
        ink = sum(
            1
            for px in rendered.crop((20, 20, 150, 120)).convert("RGB").getdata()
            if px != (240, 64, 32)
        )
        assert ink >= 400, ink
        assert rendered.getpixel((100, 160)) == (240, 64, 32, 255)
