"""Diagnostics report assembly: fixed field list, redaction screen,
bounded recent-error retention, one-call export (TASK-055 AC 1/2/3)."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from application.maintenance.diagnostics import (
    BoundedErrorLog,
    DiagnosticsReport,
    DiagnosticsService,
    RecentError,
    build_diagnostics_report,
    redact_value,
)


PURE_DATA_ROOT = Path("D:/MangaData")


def _provider(app_version="0.1.0", schema_version=3):
    class _P:
        def app_version(self):
            return app_version

        def platform_python(self):
            return "CPython 3.12.3"

        def schema_version(self):
            return schema_version

        def database_path(self):
            return str(PURE_DATA_ROOT / "library.db")

        def settings_summary(self):
            return {
                "network.proxy_url": "http://127.0.0.1:7890",
                "translation.endpoint": "https://api.example.com/v1",
                "translation.api_key": "sk-should-never-appear",
                "translation.auth_token": "Bearer abc.def.ghi",
            }

        def environment_paths(self):
            return {
                "data_root": str(PURE_DATA_ROOT),
                "managed_root": str(PURE_DATA_ROOT / "managed"),
            }

    return _P()


def _report(**overrides):
    kwargs = dict(
        generated_at="2026-09-19T02:00:00",
        app_version="0.1.0",
        platform_python="CPython 3.12.3",
        schema_version=3,
        database_path=str(PURE_DATA_ROOT / "library.db"),
        settings_summary={"translation.endpoint": "https://api.example.com/v1"},
        recent_errors=(),
        environment_paths={"data_root": str(PURE_DATA_ROOT)},
    )
    kwargs.update(overrides)
    return build_diagnostics_report(**kwargs)


class TestFixedFieldList:
    def test_sections_are_exactly_the_documented_five(self):
        report = _report()
        assert [name for name, _ in report.sections] == [
            "application",
            "database",
            "settings_summary",
            "recent_errors",
            "environment_paths",
        ]

    def test_json_roundtrip_carries_versions_and_sorted_keys(self):
        payload = json.loads(_report().to_json_bytes().decode("utf-8"))
        assert payload["generated_at"] == "2026-09-19T02:00:00"
        assert payload["application"]["app_version"] == "0.1.0"
        assert payload["application"]["platform_python"] == "CPython 3.12.3"
        assert payload["database"]["schema_version"] == "3"
        assert payload["database"]["database_path"] == str(PURE_DATA_ROOT / "library.db")
        assert payload["environment_paths"]["data_root"] == str(PURE_DATA_ROOT)

    def test_to_dict_is_json_serialisable_and_matches_json_bytes(self):
        report = _report()
        assert json.loads(report.to_json_bytes().decode("utf-8")) == report.to_dict()


class TestRedaction:
    def test_sensitive_key_names_are_masked(self):
        assert redact_value("translation.api_key", "whatever") == "[redacted]"
        assert redact_value("auth_token", "whatever") == "[redacted]"
        assert redact_value("provider_secret", "whatever") == "[redacted]"
        assert redact_value("db_password", "hunter2") == "[redacted]"
        assert redact_value("Authorization", "Basic xyz") == "[redacted]"

    def test_credential_value_shapes_are_masked_under_benign_keys(self):
        assert redact_value("note", "sk-live-abc123") == "[redacted]"
        assert redact_value("header", "Bearer abc.def.ghi") == "[redacted]"

    def test_ordinary_paths_and_urls_pass_through(self):
        assert redact_value("data_root", "D:/MangaData") == "D:/MangaData"
        assert redact_value("endpoint", "https://api.example.com/v1") == (
            "https://api.example.com/v1"
        )

    def test_leaked_credential_in_settings_never_reaches_the_report(self):
        payload = json.loads(
            _report(
                settings_summary={
                    "translation.api_key": "sk-should-never-appear",
                    "network.proxy_url": "http://127.0.0.1:7890",
                }
            ).to_json_bytes()
        )
        assert "sk-should-never-appear" not in json.dumps(payload)
        assert payload["settings_summary"]["translation.api_key"] == "[redacted]"
        assert payload["settings_summary"]["network.proxy_url"] == "http://127.0.0.1:7890"


class TestBoundedErrorLog:
    def test_ring_buffer_drops_oldest_beyond_cap(self):
        log = BoundedErrorLog(max_entries=2)
        for i in range(5):
            log.record(RecentError(f"t{i}", "import", "E", f"m{i}"))
        assert len(log) == 2
        assert [error.message for error in log.recent()] == ["m3", "m4"]

    def test_recent_limit_is_bounded_request(self):
        log = BoundedErrorLog(max_entries=10)
        for i in range(3):
            log.record(RecentError("t", "import", "E", f"m{i}"))
        assert len(log.recent(limit=2)) == 2
        assert len(log.recent(limit=0)) == 0

    def test_cap_must_be_positive(self):
        with pytest.raises(ValueError):
            BoundedErrorLog(max_entries=0)


class TestServiceExport:
    def test_export_is_a_single_call_writing_json_via_the_sink(self):
        class _Sink:
            def __init__(self):
                self.written = None

            def write_report(self, payload, generated_at):
                self.written = (payload, generated_at)
                return "diag-20260919T020000.json"

        errors = BoundedErrorLog()
        errors.record(RecentError("t1", "import", "PROVIDER_AUTH_FAILED", "a.png"))
        sink = _Sink()
        service = DiagnosticsService(
            _provider=_provider(),
            _sink=sink,
            _errors=errors,
        )
        dest = service.export(generated_at="2026-09-19T02:00:00")
        assert dest == "diag-20260919T020000.json"
        payload, at = sink.written
        assert at == "2026-09-19T02:00:00"
        parsed = json.loads(payload.decode("utf-8"))
        assert any("PROVIDER_AUTH_FAILED" in value for value in parsed["recent_errors"].values())

    def test_report_is_frozen(self):
        report = _report()
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.app_version = "changed"


class TestRedactionReachesEverySection:
    """TASK-062 AC ①/②: the documented invariant must actually hold.

    Before this slice only ``settings_summary`` and ``environment_paths`` were
    screened; the application, database and recent-errors sections passed
    through raw, and the recent-error *key* (composed from caller-supplied
    ``occurred_at``/``source``) could never match the sensitive-name screen.
    """

    def test_credentials_are_masked_in_the_application_and_database_sections(self):
        payload = json.loads(
            _report(
                platform_python="Bearer eyJhbGciOi.payload.sig",
                database_path="D:/MangaData/sk-secretvalue1234.db",
            )
            .to_json_bytes()
            .decode("utf-8")
        )
        assert payload["application"]["platform_python"] == "[redacted]"
        assert payload["database"]["database_path"] == "[redacted]"

    def test_credentials_are_masked_in_recent_errors_values_and_keys(self):
        payload = json.loads(
            _report(
                recent_errors=(
                    RecentError(
                        "t1", "import", "PROVIDER_AUTH_FAILED", "rejected sk-abcdef123456"
                    ),
                    RecentError("t2", "Bearer abc.def.ghi", "E", "plain message"),
                )
            )
            .to_json_bytes()
            .decode("utf-8")
        )
        # The screen replaces the *whole* value rather than rewriting it in
        # place: one entry's diagnosability is sacrificed so no credential
        # fragment can survive. Pin both directions.
        serialized = json.dumps(payload, ensure_ascii=False)
        assert "sk-abcdef123456" not in serialized, "the token survived into the report"
        assert "Bearer abc.def.ghi" not in serialized, "the bearer survived into the report"
        assert "[redacted]" in payload["recent_errors"].values()
        assert any(key == "[redacted]" for key in payload["recent_errors"])

    def test_benign_values_survive_every_section(self):
        payload = json.loads(_report().to_json_bytes().decode("utf-8"))
        assert payload["application"] == {
            "app_version": "0.1.0",
            "platform_python": "CPython 3.12.3",
        }
        assert payload["database"]["database_path"].endswith("library.db")
        assert payload["environment_paths"]["data_root"] == str(PURE_DATA_ROOT)

    def test_embedded_credential_shapes_are_caught_anywhere_in_a_value(self):
        assert redact_value("note", "see sk-abcdefgh1234 for details") == "[redacted]"
        assert redact_value("note", "sent Bearer abc.def.ghi to the endpoint") == "[redacted]"

    def test_ordinary_paths_versions_and_words_pass_through(self):
        for value in (
            "D:/MangaData",
            "D:\\MangaData\\managed",
            "1.0.0+build.7",
            "CPython 3.12.3",
            "D:/workspace/task-live-run/comic-sketch.png",
        ):
            assert redact_value("data_root", value) == value

    def test_the_documented_boundary_is_the_actual_boundary(self):
        """Pin both directions of the documented boundary (AC ①/③).

        An ``sk-`` run of >= 8 token characters is masked even inside a path
        (coarse on purpose = safe direction), while a secret spelled inside
        free text is *not* scrubbed - that stays the collector's duty.
        """
        assert redact_value("data_root", "D:/workspace/sk-tools-market") == "[redacted]"
        assert redact_value("note", "password=hunter2") == "password=hunter2"
