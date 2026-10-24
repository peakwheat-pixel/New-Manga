"""TASK-050 AC ①③: production assembly injects the persisted defaults.

The read face: a configured ``pipeline_defaults`` row reaches the runs'
frozen snapshots through the real assembly (no second settings parse);
an unconfigured install keeps the pre-TASK-050 bootstrap (empty row,
typed fail-closed).  The end-to-end face (AC ③): after the write face
binds a *local deterministic* provider (registered into the production
registry inside the test — no dependency, no real endpoint), an
``OCR_REGION`` command advances past ``PROVIDER_NOT_CONFIGURED`` and its
``ocr`` step completes over real SQLite and real managed files.
"""

from __future__ import annotations

import json

import pytest
from application.importing.images.ports import ImportSource
from bootstrap.app import assemble_services
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.providers.registry import ProviderDescriptor
from ports.ocr.ports import OcrResult

from tests.core.test_bootstrap import _make_png


class _EchoOcr:
    """A deterministic local OCR double registered into the production
    registry by the test itself (AC ③: no dependency, no endpoint)."""

    provider_id = "test-local-ocr"
    provider_type = "deterministic-test"

    def recognize(self, request) -> OcrResult:
        return OcrResult(
            region_id=request.region_id,
            text="echo",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


def _imported_page(services, chapter_id: str) -> str:
    report = services.importer.import_files(
        chapter_id,
        [ImportSource(filename="p1.png", data_provider=lambda: _make_png(40, 60))],
    )
    return report.imported[0].page.page_id


def _region_on(services, page_id: str) -> str:
    geometry = RegionGeometry(
        bbox=BBox(4, 4, 30, 40),
        polygon=((4, 4), (34, 4), (34, 44), (4, 44)),
    )
    region = services.editing.create_region(
        page_id, geometry, reading_order=1, origin=RegionOrigin.USER
    )
    return region.region_id


def test_assembly_seeds_run_snapshots_from_persisted_defaults(tmp_path) -> None:
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        # persisted configuration written before startup (the write face
        # or a previous session may have produced it)
        services.conn.execute(
            "INSERT INTO pipeline_defaults (defaults_id, settings_json,"
            " provider_bindings_json, constraint_snapshot_ref, context_policy_json,"
            " updated_at) VALUES (1, ?, ?, 'snap-7', ?, '2026')"
            " ON CONFLICT(defaults_id) DO UPDATE SET settings_json=excluded.settings_json,"
            " provider_bindings_json=excluded.provider_bindings_json,"
            " constraint_snapshot_ref=excluded.constraint_snapshot_ref,"
            " context_policy_json=excluded.context_policy_json",
            (
                json.dumps({"ocr": {"script": "ja"}}),
                json.dumps({"color": "test-color-id"}),
                json.dumps({"max_context": 2}),
            ),
        )
        services.conn.commit()

        # re-assemble over the same storage: the read face must project
        # the persisted row into the pipeline (idempotent re-projection)
        services2 = assemble_services(tmp_path / "library.db", tmp_path / "managed")
        try:
            book = services2.library.create_book("绑定书")
            chapter = services2.library.create_chapter(book.book_id, "第1话")
            page_id = _imported_page(services2, chapter.chapter_id)
            run = services2.pipeline.create_run(
                CommandType.RERENDER_SINGLE,
                PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
            )
            services2.pipeline.plan_run(run.run_id)
            assert run.settings_snapshot == {"ocr": {"script": "ja"}}
            assert run.provider_binding_snapshot == {"color": "test-color-id"}
            assert run.constraint_snapshot_ref == "snap-7"
        finally:
            services2.conn.close()
    finally:
        services.conn.close()


def test_unconfigured_install_keeps_the_empty_fail_closed_bootstrap(tmp_path) -> None:
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        row = services.conn.execute(
            "SELECT settings_json, provider_bindings_json FROM pipeline_defaults"
            " WHERE defaults_id = 1"
        ).fetchone()
        assert json.loads(row[0]) == {}
        assert json.loads(row[1]) == {}

        book = services.library.create_book("空配置书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        page_id = _imported_page(services, chapter.chapter_id)
        region_id = _region_on(services, page_id)
        run = services.pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
        )
        services.pipeline.plan_run(run.run_id)
        assert run.provider_binding_snapshot == {}
        services.pipeline.execute_run(run.run_id)
        ocr = next(s for s in run.step_runs if s.step_type == "ocr")
        assert ocr.status is StepRunStatus.FAILED
        assert ocr.error_code == "PROVIDER_NOT_CONFIGURED"
    finally:
        services.conn.close()


def test_bound_local_provider_advances_ocr_past_not_configured(tmp_path) -> None:
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        services.providers.registry.register(
            ProviderDescriptor(
                provider_id="test-local-ocr",
                provider_type="deterministic-test",
                capabilities=frozenset({"ocr"}),
                note="TASK-050 AC ③ in-test local deterministic provider",
            ),
            _EchoOcr,
        )
        services.pipeline_defaults.save_provider_binding("ocr", "test-local-ocr")

        book = services.library.create_book("绑定书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        page_id = _imported_page(services, chapter.chapter_id)
        region_id = _region_on(services, page_id)

        run = services.pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
        )
        services.pipeline.plan_run(run.run_id)
        assert run.provider_binding_snapshot == {"ocr": "test-local-ocr"}
        run = services.pipeline.execute_run(run.run_id)

        ocr = next(s for s in run.step_runs if s.step_type == "ocr")
        assert ocr.status is StepRunStatus.COMPLETED
        assert run.status is PipelineRunStatus.COMPLETED

        # the recognized text really landed through the pipeline seam
        revisions = services.conn.execute(
            "SELECT snapshot_json FROM region_revisions WHERE region_id = ?",
            (region_id,),
        ).fetchall()
        assert any("echo" in (row[0] or "") for row in revisions)
    finally:
        services.conn.close()
