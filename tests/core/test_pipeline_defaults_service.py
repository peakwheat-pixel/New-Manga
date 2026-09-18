"""TASK-050 AC ②: the application-layer pipeline-defaults channel.

The write face validates before persisting: an unknown step or a binding
shape the production fallback-chain reader could never accept must be a
typed error at the write face, not a surprise at run time.  Storage goes
through the *real* infrastructure snapshot provider (bridged exactly the
way assembly bridges it), so these tests also pin that no second
persistence implementation exists.
"""

from __future__ import annotations

import pytest
from application.settings.errors import BindingValidationError
from application.settings.pipeline_defaults import (
    PipelineDefaults,
    PipelineDefaultsService,
)
from bootstrap.app import _load_pipeline_defaults
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.pipeline import SqliteSnapshotProvider
from infrastructure.sqlite.schema import default_migrations

KNOWN_STEPS = frozenset(
    {"detect", "ocr", "color", "term_extract", "translate", "segment",
     "mask_refine", "inpaint", "render"}
)


def _service(conn) -> PipelineDefaultsService:
    return PipelineDefaultsService(
        load=lambda: PipelineDefaults(**_load_pipeline_defaults(conn)),
        save=lambda **kwargs: SqliteSnapshotProvider(conn, **kwargs),
        known_steps=KNOWN_STEPS,
    )


def _conn(tmp_path):
    conn, _ = open_database(
        tmp_path / "defaults.db",
        latest_known_schema_version=max(
            migration.schema_version for migration in default_migrations()
        ),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    return conn


def test_binding_roundtrips_through_the_real_defaults_row(tmp_path) -> None:
    conn = _conn(tmp_path)
    try:
        service = _service(conn)
        assert service.read().provider_bindings == {}

        saved = service.save_provider_binding("ocr", "manga-ocr")
        assert saved.provider_bindings == {"ocr": "manga-ocr"}

        # a second binding must merge, not replace the first
        service.save_provider_binding("color", {
            "provider_id": "vision-color", "fallback": ["local-color"],
        })
        assert service.read().provider_bindings == {
            "ocr": "manga-ocr",
            "color": {"provider_id": "vision-color", "fallback": ["local-color"]},
        }

        # settings sections persist on the same row
        service.save_settings_section("ocr", {"script": "ja", "direction": "horizontal"})
        defaults = service.read()
        assert defaults.settings == {"ocr": {"script": "ja", "direction": "horizontal"}}
        assert defaults.provider_bindings["ocr"] == "manga-ocr"

        # the row itself is the one the pipeline snapshots read
        row = conn.execute(
            "SELECT settings_json, provider_bindings_json FROM pipeline_defaults"
            " WHERE defaults_id = 1"
        ).fetchone()
        assert '"manga-ocr"' in row[1]

        service.clear_provider_binding("ocr")
        assert service.read().provider_bindings == {
            "color": {"provider_id": "vision-color", "fallback": ["local-color"]}
        }
    finally:
        conn.close()


def test_unknown_step_and_bad_shapes_are_typed_rejections(tmp_path) -> None:
    conn = _conn(tmp_path)
    try:
        service = _service(conn)
        for step_type, binding in (
            ("not_a_step", "manga-ocr"),
            ("ocr", ""),
            ("ocr", "   "),
            ("ocr", []),
            ("ocr", 42),
            ("ocr", {"fallback": ["manga-ocr"]}),  # names no provider
            ("ocr", {"provider_id": ""}),
        ):
            with pytest.raises(BindingValidationError):
                service.save_provider_binding(step_type, binding)
        with pytest.raises(BindingValidationError):
            service.clear_provider_binding("nope")
        with pytest.raises(BindingValidationError):
            service.save_settings_section("   ", {"a": 1})
        with pytest.raises(BindingValidationError):
            service.save_settings_section("ocr", ["not", "a", "mapping"])

        # nothing leaked into storage during the failed writes
        assert service.read() == PipelineDefaults({}, {}, None, {})
    finally:
        conn.close()


def test_corrupt_defaults_row_decodes_to_empty(tmp_path) -> None:
    conn = _conn(tmp_path)
    try:
        conn.execute(
            "INSERT INTO pipeline_defaults (defaults_id, settings_json,"
            " provider_bindings_json, constraint_snapshot_ref, context_policy_json,"
            " updated_at) VALUES (1, 'not-json', '', 'snap-1', 'also-bad', '2026')"
        )
        defaults = _load_pipeline_defaults(conn)
        assert defaults == {
            "settings": {},
            "provider_bindings": {},
            "constraint_snapshot_ref": "snap-1",
            "context_policy": {},
        }
        assert _service(conn).read() == PipelineDefaults({}, {}, "snap-1", {})
    finally:
        conn.close()
