"""FEA-11-LINEAGE-1 assembly-level evidence (r1 P1-4 / P1-5).

The production ``assemble_core_services`` must ALWAYS wire the C-17 §7.1
lineage isolation guard — an assembly that forgets it would silently keep the
pre-LINEAGE-1 behaviour (the r1 P1-4 "opt-in + fail-open" finding). These
tests build the REAL Core assembly over a real file-backed v8 database and
prove:

* every consumer (region repository, editing service, render service, draft
  service, Run target catalog) shares the SAME guard object;
* the start-up stock backfill call point runs and marks missing lineage rows
  on already switched pages ``legacy_unverified`` (no guessed attribution);
* the wire faces answer typed: a changed-binding page's ListRegions hides the
  old-coordinate region and an edit through the old binding is refused with
  ``LINEAGE_BINDING_CHANGED``/conflict (never UNKNOWN).
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import assemble_core_services
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    PROTOCOL_NAME,
    CoreServiceServer,
)
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from tests.fea11.conftest import add_source_tree, add_sync_switch

NOW = "2026-11-05T00:00:00.000+00:00"
DIGEST = "b" * 64
_TEXT_EMPTY = {
    "ocr_text": "",
    "machine_translation": "",
    "edited_translation": "",
    "final_translation": "",
    "final_source": "none",
    "edited_confirmed": False,
    "manual_edited": False,
    "translation_locked": False,
}


class _PassthroughDecoder:
    """Injection marker only — these tests never import a page."""

    def decode(self, data: bytes):  # pragma: no cover - never called
        raise AssertionError("the lineage assembly test does not import pages")


class _StubStyleAnalyzer:
    """Qt-free stand-in for the ``SourceStyleAnalyzer`` port."""

    def analyze(self, original_png: bytes, box):  # pragma: no cover
        raise AssertionError("the lineage assembly test does not render")


def _assemble(database_path, managed_root):
    return assemble_core_services(
        database_path,
        managed_root,
        image_decoder=_PassthroughDecoder(),
        font_catalog=object(),
        layout_engine=object(),
        compositor=object(),
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
    )


def _seed_pre_assembly_database(database_path) -> None:
    """A v8 database as an OLD binary leaves it: one switched page whose
    region revision has no lineage row (the pre-fix write paths)."""
    connection = sqlite3.connect(str(database_path), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(connection, default_migrations()).apply_pending()
    connection.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    connection.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    connection.execute(
        "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
        " sort_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref, source_mode, integrity_status, created_at,"
        " updated_at) VALUES ('p1', 'c1', '001.png', 1, 1, ?, 10, 4, 3,"
        " 'original/001.png', 'referenced', 'complete', ?, ?)",
        (DIGEST, NOW, NOW),
    )
    add_source_tree(
        connection, source_id="s1", version_id="sv1", digest="a" * 64,
        entries=[("e1", "001.png", DIGEST), ("e2", "002.png", "c" * 64)],
        legacy_v7_evidence=False,
    )
    connection.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, authorization_generation, authorized_at, verified_digest,"
        " created_at, updated_at)"
        " VALUES ('pb-p1', 'p1', 'b1', 1, 's1', 'e1', 'sv1', 'healthy', 1,"
        " ?, ?, ?, ?)",
        (NOW, DIGEST, NOW, NOW),
    )
    connection.commit()
    connection.execute("BEGIN IMMEDIATE")
    connection.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order,"
        " geometry_json, text_json, style_json, sfx_policy, region_locked,"
        " translation_locked, inpaint_locked, current_revision_id, created_at,"
        " updated_at) VALUES ('rg1', 'p1', 'speech', 1,"
        " '{\"bbox\": [0, 0, 4, 3], \"polygon\": []}', ?, '{}', 'skip',"
        " 0, 0, 0, 'rv1', ?, ?)",
        (json.dumps(_TEXT_EMPTY, sort_keys=True), NOW, NOW),
    )
    connection.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id,"
        " revision_no, snapshot_json, origin, review_state, is_pinned,"
        " created_at) VALUES ('rv1', 'rg1', 1, ?, 'machine', 'confirmed', 0, ?)",
        (
            json.dumps(
                {
                    "region_type": "speech",
                    "reading_order": 1,
                    "geometry": {"bbox": [0, 0, 4, 3], "polygon": []},
                    "text": _TEXT_EMPTY,
                    "style": {},
                    "sfx_policy": "skip",
                    "region_locked": False,
                    "translation_locked": False,
                    "inpaint_locked": False,
                },
                sort_keys=True,
            ),
            NOW,
        ),
    )
    connection.commit()
    add_sync_switch(
        connection, page_id="p1", old_binding_id="pb-p1",
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    connection.close()


def _wire_request(server, command: str, payload: dict) -> dict:
    line = json.dumps(
        {
            "protocol": PROTOCOL_NAME,
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": "req-lineage-1",
            "command": command,
            "payload": payload,
        }
    )
    response, _should_exit = server._dispatch_request(line)
    return response


def test_assembly_wires_the_same_guard_into_every_consumer(tmp_path):
    core = _assemble(tmp_path / "library.db", tmp_path / "managed")
    try:
        guard = core.lineage_guard
        assert guard is not None
        assert core.editing._lineage_guard is guard
        assert core.editing._repo._lineage_guard is guard
        assert core.render._lineage_guard is guard
        assert core.drafts._lineage_binding is not None
        assert core.pipeline._catalog.lineage_guard is guard
        assert callable(core.pipeline._catalog.lineage_binding)
    finally:
        core.close()


def test_startup_backfill_runs_and_marks_legacy_unverified(tmp_path):
    database_path = tmp_path / "library.db"
    _seed_pre_assembly_database(database_path)

    core = _assemble(database_path, tmp_path / "managed")
    try:
        row = core.source_sync["store"].lineage_of_revision("rv1")
        assert row is not None
        assert row["binding_id"] is None
        assert row["provenance"] == "legacy_unverified"
    finally:
        core.close()

    # Second assembly over the same database: the backfill stays idempotent,
    # the row is not rewritten and no attribution is guessed.
    core = _assemble(database_path, tmp_path / "managed")
    try:
        rows = core.conn.execute(
            "SELECT revision_id, binding_id, provenance"
            " FROM source_revision_lineage WHERE revision_id = 'rv1'"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]["binding_id"] is None
        assert rows[0]["provenance"] == "legacy_unverified"
    finally:
        core.close()


def test_backfill_failure_is_logged_and_does_not_block_assembly(
    tmp_path, monkeypatch, capsys
):
    """r3 R2-03(c): a stock-backfill failure is recorded and the assembly
    still succeeds (DSH r2 裁决 ④: 失败不得让装配崩溃，记录并继续)."""
    from infrastructure.sqlite.source_sync import SourceSyncStore

    def _explode(self, *, now=None):
        raise RuntimeError("injected stock-backfill failure")

    monkeypatch.setattr(
        SourceSyncStore, "backfill_legacy_unverified_lineage", _explode
    )
    core = _assemble(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert core.lineage_guard is not None
        assert core.editing._lineage_guard is core.lineage_guard
        assert core.render._lineage_guard is core.lineage_guard
    finally:
        core.close()
    captured = capsys.readouterr()
    assert "legacy lineage backfill failed" in captured.err
    assert "injected stock-backfill failure" in captured.err


def test_wire_faces_refuse_a_changed_binding_typed(tmp_path):
    core = _assemble(tmp_path / "library.db", tmp_path / "managed")
    try:
        from domain.regions.entities import BBox, RegionGeometry

        connection = core.conn
        connection.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b1', 'Book', ?, ?)",
            (NOW, NOW),
        )
        connection.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('c1', 'b1', 'Ch', ?, ?)",
            (NOW, NOW),
        )
        connection.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename,"
            " source_order, sort_order, source_hash, source_size_bytes, width,"
            " height, managed_original_ref, source_mode, integrity_status,"
            " created_at, updated_at) VALUES ('p2', 'c1', '002.png', 2, 2, ?,"
            " 10, 4, 3, 'original/002.png', 'referenced', 'complete', ?, ?)",
            (DIGEST, NOW, NOW),
        )
        add_source_tree(
            connection, source_id="s1", version_id="sv1", digest="a" * 64,
            entries=[("e1", "001.png", DIGEST), ("e2", "002.png", "c" * 64)],
            legacy_v7_evidence=False,
        )
        connection.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id,"
            " binding_version, source_id, entry_id, accepted_source_version,"
            " status, authorization_generation, authorized_at,"
            " verified_digest, created_at, updated_at)"
            " VALUES ('pb-p2', 'p2', 'b1', 1, 's1', 'e2', 'sv1', 'healthy',"
            " 1, ?, ?, ?, ?)",
            (NOW, DIGEST, NOW, NOW),
        )
        connection.commit()
        region = core.editing.create_region(
            "p2", RegionGeometry(bbox=BBox(0, 0, 4, 3))
        )
        lineage = core.source_sync["store"].lineage_of_revision(
            region.current_revision_id
        )
        assert lineage is not None
        assert lineage["binding_id"] == "pb-p2"
        assert lineage["provenance"] == "native"

        core.pipeline.set_scheduler_owner(True)
        server = CoreServiceServer(core)
        # Export text face: the region is exported while the binding is
        # current (ordinary read path) ...
        assert [row["region_id"] for row in server._export_regions("p2")] == [
            region.region_id
        ]

        # The page switches to a CUT (changed) binding.
        add_sync_switch(
            connection, page_id="p2", old_binding_id="pb-p2",
            new_binding_id="pb-p2-b2", relation="changed", seq=2,
        )

        # ... and is excluded from the export text face afterwards (C-17 §7.1:
        # old coordinates/text never ride the new image's ordinary read paths).
        assert server._export_regions("p2") == []

        listed = _wire_request(server, "list_regions", {"page_id": "p2"})
        assert listed["error"] is None
        assert listed["result"]["regions"] == []

        texts = _wire_request(
            server,
            "list_page_region_texts",
            {"page_id": "p2", "region_ids": [region.region_id]},
        )
        assert texts["error"]["code"] == "TARGET_NOT_FOUND"

        refused = _wire_request(
            server,
            "save_manual_translation",
            {"region_id": region.region_id, "edited_translation": "不应写入"},
        )
        assert refused["error"] is not None
        assert refused["error"]["code"] == "LINEAGE_BINDING_CHANGED"
        assert refused["error"]["category"] == "conflict"
        assert refused["error"]["retryable"] is False

        # r3 R2-03(d): page render exposes the lineage exclusion in its
        # reports (typed skip code, not a silent short list) and refuses the
        # page typed when EVERY live region is hidden ...
        render_outcome = core.render.rerender_page("p2")
        assert render_outcome.status == "blocked"
        assert render_outcome.error_code == "LINEAGE_BINDING_CHANGED"
        skipped = [
            report
            for report in render_outcome.reports
            if report.skip_reason == "LINEAGE_BINDING_CHANGED"
        ]
        assert [report.region_id for report in skipped] == [region.region_id]
        assert [report.status for report in skipped] == ["skipped"]
        # ... and the wire face projects it as the typed conflict envelope.
        from bootstrap.core_service import RenderCommandError

        with pytest.raises(RenderCommandError) as raised:
            server.handle_rerender_page({"page_id": "p2"})
        assert raised.value.code == "LINEAGE_BINDING_CHANGED"
        assert raised.value.category == "conflict"

        # Zero write: the current revision is still the one created above.
        current = connection.execute(
            "SELECT current_revision_id FROM regions WHERE region_id = ?",
            (region.region_id,),
        ).fetchone()["current_revision_id"]
        assert current == region.current_revision_id
    finally:
        core.close()
