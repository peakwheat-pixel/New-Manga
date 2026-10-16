"""P16 rev 2.1 Core wire behavior and safety gates."""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import io
import json
from pathlib import Path
import sys
import threading
import time
import uuid
import zipfile

import pypdfium2 as pdfium
import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource
from bootstrap.core_service import PROTOCOL_MAJOR, PROTOCOL_MINOR, CoreServiceServer, assemble_production_core
from domain.regions.entities import BBox, RegionGeometry
from infrastructure.export.target_refs import ExportTargetGrantRegistry, ExportTargetRefError, ResolvedExportTarget
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore, initialize_namespace
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher
from infrastructure.sqlite.artifacts import SqliteArtifactRepository
from infrastructure.export.jobs import JsonExportJobStore
from ports.repositories.artifacts import ArtifactType, ContentProvider, NewArtifact, PendingArtifactCommit


NOW = "2026-01-01T00:00:00.000+00:00"
SESSION_ID = "p16-host-session"


def _png(width: int, height: int, color: tuple[int, int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGBA", (width, height), color).save(buffer, format="PNG")
    return buffer.getvalue()


def _sign_grant(
    key: bytes, grant_id: str, session_id: str, target: Path, fmt: str,
    replace_existing: bool, expires_at: float,
) -> str:
    """Independent wire signer for tests; production does not expose an issuer."""
    signed = "\0".join((
        grant_id, session_id, str(target), fmt,
        "1" if replace_existing else "0", f"{expires_at:.6f}",
    )).encode()
    return base64.urlsafe_b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode().rstrip("=")


def _make_grant(
    server: CoreServiceServer, target: Path, fmt: str, *,
    expires_at: float | None = None, replace_existing: bool = True,
) -> tuple[str, str]:
    grant_id = uuid.uuid4().hex
    key = bytes(range(32))
    target = target.absolute()
    expires_at = expires_at if expires_at is not None else time.time() + 120
    signature = _sign_grant(key, grant_id, SESSION_ID, target, fmt, replace_existing, expires_at)
    server._register_export_target({
        "grant_id": grant_id, "session_id": SESSION_ID, "target_path": str(target),
        "format": fmt, "replace_existing": replace_existing, "expires_at": expires_at,
        "signing_key": base64.urlsafe_b64encode(key).decode().rstrip("="),
        "signature": signature,
    })
    return f"etref1.{grant_id}.{signature}", grant_id


def _rpc(server: CoreServiceServer, command: str, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": uuid.uuid4().hex,
        "command": command,
        "payload": payload,
    })
    return server.dispatch_request(raw)[0]


def _server_for(core, tmp_path: Path) -> tuple[CoreServiceServer, ResourceCatalogStore]:
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    if not catalog_db.exists():
        initialize_namespace(catalog_db, derived_root)
    catalog = ResourceCatalogStore(catalog_db)
    return CoreServiceServer(
        core, stdout=io.StringIO(),
        render_previews=RenderPreviewPublisher(derived_root, catalog),
    ), catalog


def _commit_artifact(core, page, artifact_type: ArtifactType, payload: bytes, *, source_revision_id: str | None = None):
    repository = SqliteArtifactRepository(core.conn, core.storage)
    record = repository.create_artifact(NewArtifact(
        book_id="book", chapter_id=page.chapter_id, page_id=page.page_id,
        artifact_type=artifact_type,
    ))
    result = repository.commit_revision(PendingArtifactCommit(
        artifact_id=record.artifact_id, content_provider=ContentProvider(payload=payload),
        mime_type="image/png", expected_current_revision_id=None,
        source_artifact_revision_id=source_revision_id,
        width=page.width, height=page.height, file_suffix=".png",
    ))
    assert result.status.value == "committed", result.detail
    return result.revision


def _seed_core(tmp_path: Path, *, include_modes: bool = False):
    core = assemble_production_core(tmp_path / "data")
    chapters = [("chapter", "paged", "rtl")]
    if include_modes:
        chapters = [
            ("rtl-chapter", "paged", "rtl"),
            ("ltr-chapter", "paged", "ltr"),
            ("toon-chapter", "webtoon", "vertical"),
        ]
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,author,description,created_at,updated_at)"
            " VALUES ('book','Test Manga','Author','Description',?,?)", (NOW, NOW),
        )
        for chapter_id, chapter_type, direction in chapters:
            core.conn.execute(
                "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,chapter_type,reading_direction,created_at,updated_at)"
                " VALUES (?, 'book', ?, '1', 0, ?, ?, ?, ?)",
                (chapter_id, chapter_id, chapter_type, direction, NOW, NOW),
            )

    pages: dict[str, list] = {}
    chapter_data = {
        "chapter": [("page-a.png", 64, 48, (220, 20, 30, 255)), ("page-b.png", 72, 52, (30, 80, 220, 255))],
        "rtl-chapter": [("rtl-a.png", 64, 48, (220, 20, 30, 255)), ("rtl-b.png", 72, 52, (30, 80, 220, 255))],
        "ltr-chapter": [("ltr-a.png", 80, 60, (40, 160, 70, 255))],
        "toon-chapter": [("long-strip.png", 80, 6000, (80, 80, 180, 255))],
    }
    for chapter_id, items in chapter_data.items():
        if chapter_id not in {item[0] for item in chapters}:
            continue
        imported = []
        for filename, width, height, color in items:
            original_bytes = _png(width, height, color)
            report = core.importer.import_files(chapter_id, [ImportSource(filename, lambda b=original_bytes: b)])
            assert not report.failed and len(report.imported) == 1
            page = core.repository.get_page(report.imported[0].page.page_id)
            assert page is not None
            original_revision = _commit_artifact(core, page, ArtifactType.ORIGINAL, original_bytes)
            translated_color = (240, 30, 30, 255) if Path(filename).stem.endswith("a") else (30, 30, 240, 255)
            translated_bytes = _png(width, height, translated_color)
            translated_revision = _commit_artifact(
                core, page, ArtifactType.TRANSLATED, translated_bytes,
                source_revision_id=original_revision.artifact_revision_id,
            )
            imported.append({
                "page": page, "original_revision": original_revision,
                "translated_revision": translated_revision,
                "original_bytes": original_bytes, "translated_bytes": translated_bytes,
            })
        pages[chapter_id] = imported

    server, catalog = _server_for(core, tmp_path)
    return core, server, catalog, pages


def _export_payload(chapter_id: str, page_ids: list[str], fmt: str, options: dict, ref: str, *, stale: str = "abort") -> dict:
    return {
        "book_id": "book", "chapter_ids": [chapter_id], "ordered_page_ids": page_ids,
        "format": fmt, "format_options": options, "stale_policy": stale,
        "target_ref": ref,
    }


def _wait_export(server: CoreServiceServer, export_id: str) -> dict:
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        response = _rpc(server, "GetExportSnapshot", {"export_id": export_id})
        if response["error"] is not None:
            return server._exports.snapshot(export_id)
        snapshot = response["result"]
        if snapshot["status"] in {"completed", "cancelled", "failed"}:
            return snapshot
        time.sleep(0.01)
    raise AssertionError(f"export {export_id} did not finish")


def _assert_clean_target(target: Path, before: bytes) -> None:
    assert target.read_bytes() == before
    assert list(target.parent.glob(f".{target.name}.*.tmp")) == []


def _assert_sources_unchanged(core, page_items: list[dict]) -> None:
    for item in page_items:
        page = item["page"]
        original = Path(core.storage.absolute_path(page.managed_original_ref))
        translated = Path(core.storage.absolute_path(item["translated_revision"].managed_path))
        assert original.read_bytes() == item["original_bytes"]
        assert translated.read_bytes() == item["translated_bytes"]


def test_reader_projection_progress_modes_layouts_and_restart(tmp_path: Path) -> None:
    core, server, catalog, pages = _seed_core(tmp_path, include_modes=True)
    data_root = core.data_root
    observed_progress_at_emit: list[dict] = []
    real_emit = server._emit_p16_event
    def check_persisted_before_reading_event(event_type, payload):
        if event_type == "ReadingProgressChanged":
            snapshot = core.reading.progress_snapshot(
                payload["book_id"], payload["chapter_id"], payload["mode"],
            )
            observed_progress_at_emit.append(snapshot)
        real_emit(event_type, payload)
    server._emit_p16_event = check_persisted_before_reading_event
    try:
        for chapter_id, expected_layout in (("rtl-chapter", "rtl"), ("ltr-chapter", "ltr"), ("toon-chapter", "webtoon_vertical")):
            response = _rpc(server, "GetReaderProjection", {
                "chapter_id": chapter_id, "mode": "original", "start_position": "beginning",
            })
            assert response["error"] is None, response["error"]
            projection = response["result"]
            assert projection["layout"] == expected_layout
            expected_pages = pages[chapter_id]
            assert [page["page_id"] for page in projection["pages"]] == [item["page"].page_id for item in expected_pages]
            assert len(projection["pages"]) == (1 if chapter_id == "toon-chapter" else len(expected_pages))
            assert all("resource_ref" in page["original"] and "sha256" in page["original"] for page in projection["pages"])
            assert all(page["translated"]["resource_ref"] is not None for page in projection["pages"])
            assert all("path" not in json.dumps(page).lower() for page in projection["pages"])

        rtl_pages = pages["rtl-chapter"]
        saved_original = _rpc(server, "SaveReadingProgress", {
            "chapter_id": "rtl-chapter", "mode": "original",
            "page_id": rtl_pages[1]["page"].page_id, "elapsed_seconds_delta": 3.5,
        })
        assert saved_original["error"] is None, saved_original["error"]
        saved_translated = _rpc(server, "SaveReadingProgress", {
            "chapter_id": "rtl-chapter", "mode": "translated",
            "page_id": rtl_pages[0]["page"].page_id, "elapsed_seconds_delta": 1.25,
        })
        assert saved_translated["error"] is None, saved_translated["error"]
        assert saved_original["result"]["total_read_seconds"] == 3.5
        assert saved_translated["result"]["total_read_seconds"] == 1.25
        assert saved_original["result"]["mode"] == "original"
        assert saved_translated["result"]["mode"] == "translated"

        toon_page = pages["toon-chapter"][0]["page"]
        toon_saved = _rpc(server, "SaveReadingProgress", {
            "chapter_id": "toon-chapter", "mode": "original",
            "page_id": toon_page.page_id, "scroll_offset_y": 2345.5,
        })
        assert toon_saved["error"] is None, toon_saved["error"]
        assert toon_saved["result"]["scroll_offset_y"] == 2345.5
        invalid_offset = _rpc(server, "SaveReadingProgress", {
            "chapter_id": "rtl-chapter", "mode": "original",
            "page_id": rtl_pages[0]["page"].page_id, "scroll_offset_y": 1,
        })
        assert invalid_offset["error"]["code"] == "INVALID_REQUEST"
        invalid_toon = _rpc(server, "SaveReadingProgress", {
            "chapter_id": "toon-chapter", "mode": "original",
            "page_id": toon_page.page_id, "scroll_offset_y": 6001,
        })
        assert invalid_toon["error"]["code"] == "INVALID_REQUEST"

        events = [json.loads(line) for line in server._stdout.getvalue().splitlines() if line]
        reading_events = [item for item in events if item.get("event_type") == "ReadingProgressChanged"]
        assert len(reading_events) == 3
        assert all(set(item) == {"protocol", "version", "event_id", "event_type", "emitted_at", "payload"} for item in reading_events)
        assert all(set(item["payload"]) == {"book_id", "chapter_id", "mode"} for item in reading_events)
        assert all("path" not in json.dumps(item).lower() and "target_ref" not in json.dumps(item) for item in reading_events)
        assert len(observed_progress_at_emit) == 3
        assert all(snapshot is not None for snapshot in observed_progress_at_emit)
        assert [snapshot["last_page_id"] for snapshot in observed_progress_at_emit] == [
            rtl_pages[1]["page"].page_id, rtl_pages[0]["page"].page_id, toon_page.page_id,
        ]

        server.close()
        catalog.close()
        core.conn.close()

        reopened = assemble_production_core(data_root)
        reopened_server, reopened_catalog = _server_for(reopened, tmp_path)
        try:
            resumed = _rpc(reopened_server, "GetReaderProjection", {
                "chapter_id": "toon-chapter", "mode": "original", "start_position": "resume",
            })
            assert resumed["error"] is None, resumed["error"]
            assert resumed["result"]["initial_position"] == {"page_id": toon_page.page_id, "scroll_offset_y": 2345.5}
            original_resume = _rpc(reopened_server, "GetReaderProjection", {
                "chapter_id": "rtl-chapter", "mode": "original", "start_position": "resume",
            })
            translated_resume = _rpc(reopened_server, "GetReaderProjection", {
                "chapter_id": "rtl-chapter", "mode": "translated", "start_position": "resume",
            })
            assert original_resume["result"]["initial_position"]["page_id"] == rtl_pages[1]["page"].page_id
            assert translated_resume["result"]["initial_position"]["page_id"] == rtl_pages[0]["page"].page_id
            beginning = _rpc(reopened_server, "GetReaderProjection", {
                "chapter_id": "rtl-chapter", "mode": "original", "start_position": "beginning",
            })
            assert beginning["result"]["initial_position"] == {"page_id": rtl_pages[0]["page"].page_id, "scroll_offset_y": 0.0}
            assert beginning["result"]["saved_progress"]["last_page_id"] == rtl_pages[1]["page"].page_id
        finally:
            reopened_server.close()
            reopened_catalog.close()
            reopened.conn.close()
    finally:
        # The successful restart branch already closed these handles.
        try:
            server.close()
            catalog.close()
            core.conn.close()
        except Exception:
            pass


@pytest.mark.parametrize(
    "case,expected",
    [
        ("malformed", "REF_MALFORMED"),
        ("signature_invalid", "REF_SIGNATURE_INVALID"),
        ("expired", "REF_EXPIRED"),
        ("unknown_id", "REF_UNKNOWN_ID"),
        ("revoked", "REF_REVOKED"),
        ("already_consumed", "REF_ALREADY_CONSUMED"),
    ],
)
def test_export_target_ref_rejections_make_zero_target_writes(tmp_path: Path, case: str, expected: str) -> None:
    core, server, catalog, pages = _seed_core(tmp_path)
    target = tmp_path / "outputs" / f"{case}.png"
    target.parent.mkdir(parents=True)
    before = f"sentinel:{case}".encode()
    target.write_bytes(before)
    now = [1000.0]
    core.export_target_refs = ExportTargetGrantRegistry(clock=lambda: now[0])
    try:
        ref = "not-an-export-ref"
        grant_id = None
        if case != "malformed":
            expires = 1001.0 if case == "expired" else 1100.0
            ref, grant_id = _make_grant(server, target, "png", expires_at=expires)
        if case == "signature_invalid":
            prefix, identity, signature = ref.split(".")
            # Preserve the fixed-width base64url wire shape while corrupting a byte.
            ref = f"{prefix}.{identity}.{signature[:-1]}{'A' if signature[-1] != 'A' else 'B'}"
        elif case == "expired":
            now[0] = 1001.0
        elif case == "unknown_id":
            key = bytes(range(32))
            unknown_id = uuid.uuid4().hex
            expires = 1100.0
            signature = _sign_grant(key, unknown_id, SESSION_ID, target.absolute(), "png", True, expires)
            ref = f"etref1.{unknown_id}.{signature}"
        elif case == "revoked":
            server._revoke_export_target({"grant_id": grant_id})
        elif case == "already_consumed":
            core.export_target_refs.resolve_and_consume(ref, "png")

        response = _rpc(server, "StartExport", _export_payload(
            "chapter", [pages["chapter"][0]["page"].page_id], "png", {}, ref,
        ))
        assert response["error"]["code"] == expected
        assert str(target) not in json.dumps(response["error"])
        _assert_clean_target(target, before)
        _assert_sources_unchanged(core, pages["chapter"])
    finally:
        server.close()
        catalog.close()
        core.conn.close()


def test_export_target_ref_scope_denial_and_atomic_concurrent_consumption(tmp_path: Path) -> None:
    core, server, catalog, _pages = _seed_core(tmp_path)
    target = tmp_path / "outputs" / "scope.png"
    target.parent.mkdir(parents=True)
    try:
        ref, _ = _make_grant(server, target, "png", replace_existing=False)
        target.write_bytes(b"protected")
        with pytest.raises(ExportTargetRefError, match="REF_SCOPE_DENIED"):
            core.export_target_refs.resolve_and_consume(ref, "png")
        assert target.read_bytes() == b"protected"

        wrong_format_target = tmp_path / "outputs" / "wrong-format.png"
        wrong_format_ref, _ = _make_grant(server, wrong_format_target, "png")
        with pytest.raises(ExportTargetRefError, match="REF_SCOPE_DENIED"):
            core.export_target_refs.resolve_and_consume(wrong_format_ref, "zip")
        assert not wrong_format_target.exists()

        fresh_target = tmp_path / "outputs" / "concurrent.png"
        token, _ = _make_grant(server, fresh_target, "png")
        def consume():
            try:
                core.export_target_refs.resolve_and_consume(token, "png")
                return "consumed"
            except ExportTargetRefError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=12) as pool:
            outcomes = list(pool.map(lambda _i: consume(), range(12)))
        assert outcomes.count("consumed") == 1
        assert outcomes.count("REF_ALREADY_CONSUMED") == 11
        assert not fresh_target.exists()
    finally:
        server.close()
        catalog.close()
        core.conn.close()


def test_five_export_formats_preserve_order_hash_lineage_and_pdf_text(tmp_path: Path) -> None:
    core, server, catalog, pages = _seed_core(tmp_path)
    page_a, page_b = (item["page"] for item in pages["chapter"])
    region = core.editing.create_region(page_a.page_id, RegionGeometry(bbox=BBox(8, 12, 28, 20)))
    core.editing.save_manual_translation(region.region_id, "P16 文本")
    core.editing.confirm_final(region.region_id)
    observed_persisted_events: list[bool] = []
    real_event_sink = server._exports._event_sink
    def observe_persisted_event(event):
        persisted = core.export_job_store.read()
        matching = next(job for job in persisted if job["snapshot"]["export_id"] == event["export_id"])
        observed_persisted_events.append(matching["snapshot"]["status"] == event["status"])
        real_event_sink(event)
    server._exports._event_sink = observe_persisted_event
    try:
        cases = [
            ("png", "png", {}, [page_a.page_id], ".png"),
            ("zip", "zip", {"compression": "standard"}, [page_b.page_id, page_a.page_id], ".zip"),
            ("zip-fast", "zip", {"compression": "fast"}, [page_b.page_id, page_a.page_id], ".zip"),
            ("zip-store", "zip", {"compression": "store"}, [page_b.page_id, page_a.page_id], ".zip"),
            ("cbz", "cbz", {}, [page_b.page_id, page_a.page_id], ".cbz"),
            ("pdf-image", "pdf", {"pdf_content": "image_only"}, [page_b.page_id, page_a.page_id], ".pdf"),
            ("pdf-text", "pdf", {"pdf_content": "searchable_dual_layer"}, [page_a.page_id], ".pdf"),
            ("text", "text", {"text_representation": "json"}, [page_b.page_id, page_a.page_id], ".json"),
            ("text-txt", "text", {"text_representation": "txt"}, [page_b.page_id, page_a.page_id], ".txt"),
            ("text-markdown", "text", {"text_representation": "markdown"}, [page_b.page_id, page_a.page_id], ".md"),
        ]
        results = {}
        for name, fmt, options, page_ids, suffix in cases:
            target = tmp_path / "exports" / (name + suffix)
            target.parent.mkdir(parents=True, exist_ok=True)
            ref, _ = _make_grant(server, target, fmt, replace_existing=(name != "png"))
            response = _rpc(server, "StartExport", _export_payload("chapter", page_ids, fmt, options, ref))
            assert response["error"] is None, response["error"]
            accepted = response["result"]
            assert accepted["status"] == "pending"
            assert accepted["ordered_page_ids"] == page_ids
            assert "output_path" not in accepted and "target_ref" not in accepted
            snapshot = _wait_export(server, accepted["export_id"])
            assert snapshot["status"] == "completed", [
                (row["export_id"], row["status"], row["detail"], row["file_hash"], row["output_path"])
                for row in core.export_history_store.read()
            ]
            output_bytes = target.read_bytes()
            assert hashlib.sha256(output_bytes).hexdigest() == snapshot["output"]["sha256"]
            assert [row["page_id"] for row in snapshot["lineage"]] == page_ids
            for row, page_id in zip(snapshot["lineage"], page_ids):
                data = next(item for item in pages["chapter"] if item["page"].page_id == page_id)
                assert row["source_sha256"] == hashlib.sha256(data["translated_bytes"]).hexdigest()
                assert row["order"] == page_ids.index(page_id)
            results[name] = (target, snapshot)

        png_target, png_snapshot = results["png"]
        with Image.open(png_target) as image:
            assert image.size == (page_a.width, page_a.height)
            assert image.getpixel((0, 0))[:3] == (240, 30, 30)

        zip_target, zip_snapshot = results["zip"]
        with zipfile.ZipFile(zip_target) as archive:
            names = archive.namelist()
            assert names[:2] == ["0001_page-b.png", "0002_page-a.png"]
            with Image.open(io.BytesIO(archive.read(names[0]))) as first_image:
                assert first_image.getpixel((0, 0))[:3] == (30, 30, 240)
            with Image.open(io.BytesIO(archive.read(names[1]))) as second_image:
                assert second_image.getpixel((0, 0))[:3] == (240, 30, 30)
            manifest = json.loads(archive.read("manifest.json"))
            assert [row["page_id"] for row in manifest["pages"]] == [page_b.page_id, page_a.page_id]
            assert manifest["lineage"] == zip_snapshot["lineage"]
            assert [row["sha256"] for row in manifest["pages"]] == [
                hashlib.sha256(pages["chapter"][1]["translated_bytes"]).hexdigest(),
                hashlib.sha256(pages["chapter"][0]["translated_bytes"]).hexdigest(),
            ]

        cbz_target, _ = results["cbz"]
        with zipfile.ZipFile(cbz_target) as archive:
            assert archive.namelist()[:2] == ["0001_page-b.png", "0002_page-a.png"]
            assert b"<Series>Test Manga</Series>" in archive.read("ComicInfo.xml")

        pdf_image_target, _ = results["pdf-image"]
        pdf_image = pdfium.PdfDocument(pdf_image_target.read_bytes())
        assert len(pdf_image) == 2
        first_pdf_pixel = pdf_image[0].render(scale=1).to_pil().getpixel((0, 0))
        second_pdf_pixel = pdf_image[1].render(scale=1).to_pil().getpixel((0, 0))
        assert first_pdf_pixel[:3] == (30, 30, 240)
        assert second_pdf_pixel[:3] == (240, 30, 30)
        pdf_text_target, _ = results["pdf-text"]
        pdf_text = pdfium.PdfDocument(pdf_text_target.read_bytes())
        text = pdf_text[0].get_textpage().get_text_range()
        assert "P16 文本" in text

        text_target, _ = results["text"]
        text_data = json.loads(text_target.read_text(encoding="utf-8"))
        assert [row["page_id"] for row in text_data["pages"]] == [page_b.page_id, page_a.page_id]
        first_region = text_data["pages"][1]["regions"][0]
        assert first_region["ocr_text"] == ""
        assert first_region["translated_text"] == "P16 文本"
        assert first_region["geometry"]["bbox"] == [8, 12, 28, 20]
        txt_target, _ = results["text-txt"]
        txt = txt_target.read_text(encoding="utf-8")
        assert txt.index("[page-b.png]") < txt.index("[page-a.png]")
        markdown_target, _ = results["text-markdown"]
        markdown = markdown_target.read_text(encoding="utf-8")
        assert markdown.index("# page-b.png") < markdown.index("# page-a.png")
        assert "P16 文本" in markdown

        for item in results.values():
            assert item[1]["output"]["format"] in {"png", "zip", "cbz", "pdf", "text"}
        events = [json.loads(line) for line in server._stdout.getvalue().splitlines() if line]
        export_events = [item for item in events if item.get("event_type") == "ExportProgressChanged"]
        assert export_events
        assert all(set(item) == {"protocol", "version", "event_id", "event_type", "emitted_at", "payload"} for item in export_events)
        assert all("output_path" not in item["payload"] and "target_ref" not in item["payload"] for item in export_events)
        assert observed_persisted_events and all(observed_persisted_events)

        history = _rpc(server, "GetExportHistory", {})
        assert history["error"] is None
        by_id = {row["export_id"]: row for row in history["result"]["exports"]}
        for _, snapshot in results.values():
            row = by_id[snapshot["export_id"]]
            assert row["status"] == "completed"
            assert row["ordered_page_ids"] == [line["page_id"] for line in snapshot["lineage"]]
            assert row["sha256"] == snapshot["output"]["sha256"]
            assert row["lineage"] == snapshot["lineage"]
        _assert_sources_unchanged(core, pages["chapter"])
    finally:
        server.close()
        catalog.close()
        core.conn.close()


def test_stale_abort_consumes_ref_and_continue_records_frozen_lineage(tmp_path: Path) -> None:
    core, server, catalog, pages = _seed_core(tmp_path)
    page_data = pages["chapter"][0]
    page = page_data["page"]
    try:
        newer_original = _png(page.width, page.height, (10, 20, 30, 255))
        artifact_repository = SqliteArtifactRepository(core.conn, core.storage)
        result = artifact_repository.commit_revision(PendingArtifactCommit(
            artifact_id=page_data["original_revision"].artifact_id,
            content_provider=ContentProvider(payload=newer_original), mime_type="image/png",
            expected_current_revision_id=page_data["original_revision"].artifact_revision_id,
            width=page.width, height=page.height, file_suffix=".png",
        ))
        assert result.status.value == "committed"
        target = tmp_path / "exports" / "stale.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"prior")
        stale_ref, _ = _make_grant(server, target, "png")
        stale_response = _rpc(server, "StartExport", _export_payload(
            "chapter", [page.page_id], "png", {}, stale_ref, stale="abort",
        ))
        assert stale_response["error"]["code"] == "EXPORT_STALE"
        assert stale_response["error"]["details"] == [{"page_id": page.page_id, "reason": "stale"}]
        assert target.read_bytes() == b"prior"
        with pytest.raises(ExportTargetRefError, match="REF_ALREADY_CONSUMED"):
            core.export_target_refs.resolve_and_consume(stale_ref, "png")

        continue_target = tmp_path / "exports" / "continue.png"
        continue_ref, _ = _make_grant(server, continue_target, "png")
        accepted = _rpc(server, "StartExport", _export_payload(
            "chapter", [page.page_id], "png", {}, continue_ref, stale="continue_existing",
        ))
        assert accepted["error"] is None, accepted["error"]
        snapshot = _wait_export(server, accepted["result"]["export_id"])
        assert snapshot["status"] == "completed"
        assert snapshot["lineage"][0]["stale"] is True
        assert snapshot["lineage"][0]["rendered_from_revision_id"] == page_data["original_revision"].artifact_revision_id
        assert snapshot["lineage"][0]["current_source_revision_id"] == result.revision.artifact_revision_id
    finally:
        server.close()
        catalog.close()
        core.conn.close()


def test_cancel_before_publish_keeps_existing_target_and_cleans_temporary_file(tmp_path: Path, monkeypatch) -> None:
    core, server, catalog, pages = _seed_core(tmp_path)
    target = tmp_path / "exports" / "cancel.png"
    target.parent.mkdir(parents=True)
    before = b"previous complete output"
    target.write_bytes(before)
    started, release = threading.Event(), threading.Event()
    real_build_payload = core.export_service._build_payload

    def blocking_build(request):
        started.set()
        assert release.wait(5)
        return real_build_payload(request)

    monkeypatch.setattr(core.export_service, "_build_payload", blocking_build)
    try:
        ref, _ = _make_grant(server, target, "png", replace_existing=True)
        accepted = _rpc(server, "StartExport", _export_payload(
            "chapter", [pages["chapter"][0]["page"].page_id], "png", {}, ref,
        ))
        assert accepted["error"] is None, accepted["error"]
        export_id = accepted["result"]["export_id"]
        assert started.wait(5)
        cancel_response = _rpc(server, "CancelExport", {"export_id": export_id})
        assert cancel_response["error"] is None
        release.set()
        snapshot = _wait_export(server, export_id)
        assert snapshot["status"] == "cancelled"
        _assert_clean_target(target, before)
        history = _rpc(server, "GetExportHistory", {})["result"]["exports"]
        row = next(item for item in history if item["export_id"] == export_id)
        assert row["status"] == "cancelled"
    finally:
        release.set()
        server.close()
        catalog.close()
        core.conn.close()


def test_replayed_ref_is_never_reconsumed_after_successful_export(tmp_path: Path) -> None:
    core, server, catalog, pages = _seed_core(tmp_path)
    target = tmp_path / "exports" / "replay.png"
    target.parent.mkdir(parents=True)
    try:
        ref, _ = _make_grant(server, target, "png")
        payload = _export_payload("chapter", [pages["chapter"][0]["page"].page_id], "png", {}, ref)
        accepted = _rpc(server, "StartExport", payload)
        assert accepted["error"] is None, accepted["error"]
        snapshot = _wait_export(server, accepted["result"]["export_id"])
        assert snapshot["status"] == "completed"
        before = target.read_bytes()
        replay = _rpc(server, "StartExport", payload)
        assert replay["error"]["code"] == "REF_ALREADY_CONSUMED"
        assert target.read_bytes() == before
        assert list(target.parent.glob(f".{target.name}.*.tmp")) == []
    finally:
        server.close()
        catalog.close()
        core.conn.close()
