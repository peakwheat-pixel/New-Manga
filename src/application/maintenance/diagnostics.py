"""Diagnostics report assembly (TASK-021 frozen subset 1, TASK-055).

The report is *whitelist-first*: it only ever contains sections and
fields the caller explicitly hands over, so credential objects cannot
reach this module by construction. A defensive redaction pass screens
collected key names and value shapes anyway, so a misconfigured summary
cannot leak a secret into an exported bundle (AC 1: zero credential
leakage).

The service layer only; wiring it into the production assembly (and any
UI entry point) stays out of this slice: QML surfaces are behind the
TASK-047 design gate, and assembly injection is coordinated with the
threaded-SQLite assembly slice.
"""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Protocol

_SECTION_ORDER = (
    "application",
    "database",
    "settings_summary",
    "recent_errors",
    "environment_paths",
)

_SENSITIVE_KEY = re.compile(
    r"(?:^|[._\-])(?:token|secret|password|passwd|credential(?:s)?|api[._\-]?key|"
    r"access[._\-]?key|private[._\-]?key|authorization)(?:$|[._\-])",
    re.IGNORECASE,
)
_REDACTED = "[redacted]"

#: Value shapes that look like bearer credentials even under a benign key
#: name (TASK-062 AC ①: the screen must also catch a credential **embedded**
#: in a longer string, not only one that starts the value).
#:
#: Both patterns keep a left guard so ordinary path segments do not match:
#: ``.../task-live-run`` never matches ``sk-`` because the ``s`` follows an
#: alphanumeric. The screen stays deliberately coarse for a real ``sk-`` run
#: (>= 8 token characters) — masking a bizarre path that literally contains
#: ``.../sk-…`` is the safe direction, and the boundary is documented in
#: :func:`redact_value`.
_BEARER = re.compile(r"(?<![A-Za-z0-9])Bearer\s+[A-Za-z0-9._~+/=\-]{6,}", re.IGNORECASE)
_OPENAI_STYLE = re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{8,}")


def redact_value(key: str, value: str) -> str:
    """Mask values whose *key name* is sensitive, or whose value contains a
    credential shape (a ``Bearer …`` run or an ``sk-…`` key), **anywhere** in
    the string; everything else passes through.

    Boundary (documented, tested): the screen is name-based plus two narrow
    value shapes. It does **not** try to scrub arbitrary free text — a secret
    written as, say, ``password=hunter2`` inside a message is the collector's
    responsibility to digest away. A path segment that literally starts with
    ``sk-`` followed by eight or more token characters *is* masked; that is the
    intended safe direction.
    """
    if _SENSITIVE_KEY.search(key):
        return _REDACTED
    # ``search``, not ``match``: the credential may be embedded in a longer
    # string (TASK-062 AC ①) - the patterns carry their own left guard.
    if _BEARER.search(value) or _OPENAI_STYLE.search(value):
        return _REDACTED
    return value


@dataclass(frozen=True)
class RecentError:
    """One bounded, already-summary error entry (typed code + message)."""

    occurred_at: str
    source: str
    code: str
    message: str


@dataclass(frozen=True)
class DiagnosticsReport:
    """Field list is fixed (AC 1) and recorded in the Task/Handoff:

    application  - app_version, platform_python
    database     - schema_version, database_path (display path only)
    settings_summary - caller-supplied effective settings digest
    recent_errors    - caller-supplied bounded error summaries
    environment_paths- data root / managed root / log directory display paths

    Every value **and every key** passes the redaction screen before entering
    the report (TASK-062 AC ①); see :func:`redact_value` for what that screen
    does and does not cover.
    """

    generated_at: str
    app_version: str
    schema_version: int
    sections: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()

    def section(self, name: str) -> tuple[tuple[str, str], ...]:
        for section_name, fields in self.sections:
            if section_name == name:
                return fields
        return ()

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            **{name: dict(fields) for name, fields in self.sections},
        }

    def to_json_bytes(self) -> bytes:
        return (
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        ).encode("utf-8")


def build_diagnostics_report(
    *,
    generated_at: str,
    app_version: str,
    platform_python: str,
    schema_version: int,
    database_path: str,
    settings_summary: dict[str, str],
    recent_errors: Iterable[RecentError],
    environment_paths: dict[str, str],
) -> DiagnosticsReport:
    """Assemble the fixed-section report; **every** supplied value and key is
    screened through :func:`redact_value` — including the application,
    database and recent-errors sections, which previously passed through raw
    (TASK-062 AC ①). Defence in depth only: the collector is still expected to
    pass digests, never raw credentials."""
    settings_fields = tuple(
        (key, redact_value(key, value)) for key, value in sorted(settings_summary.items())
    )
    error_fields = tuple(
        (
            redact_value("recent_error", f"{error.occurred_at} {error.source}"),
            redact_value("recent_error", f"[{error.code}] {error.message}"),
        )
        for error in recent_errors
    )
    path_fields = tuple(
        (key, redact_value(key, value)) for key, value in sorted(environment_paths.items())
    )
    sections = (
        (
            "application",
            tuple(
                (key, redact_value(key, value))
                for key, value in (
                    ("app_version", app_version),
                    ("platform_python", platform_python),
                )
            ),
        ),
        (
            "database",
            tuple(
                (key, redact_value(key, value))
                for key, value in (
                    ("schema_version", str(schema_version)),
                    ("database_path", database_path),
                )
            ),
        ),
        ("settings_summary", settings_fields),
        ("recent_errors", error_fields),
        ("environment_paths", path_fields),
    )
    return DiagnosticsReport(
        generated_at=generated_at,
        app_version=app_version,
        schema_version=schema_version,
        sections=sections,
    )


class BoundedErrorLog:
    """In-process ring buffer of :class:`RecentError` entries with a hard
    cap; the newest entry wins, the oldest is dropped silently (bounded
    retention, AC 2 semantics applied to in-memory errors)."""

    def __init__(self, max_entries: int = 50) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._entries: deque[RecentError] = deque(maxlen=max_entries)

    def record(self, error: RecentError) -> None:
        self._entries.append(error)

    def recent(self, limit: int | None = None) -> tuple[RecentError, ...]:
        entries = tuple(self._entries)
        if limit is not None and limit >= 0:
            entries = entries[-limit:] if limit else ()
        return entries

    def __len__(self) -> int:
        return len(self._entries)


class DiagnosticsSnapshotProvider(Protocol):
    """Everything the report needs, already digested by the caller."""

    def app_version(self) -> str: ...

    def platform_python(self) -> str: ...

    def schema_version(self) -> int: ...

    def database_path(self) -> str: ...

    def settings_summary(self) -> dict[str, str]: ...

    def environment_paths(self) -> dict[str, str]: ...


class DiagnosticsBundleSink(Protocol):
    """Where the exported bundle goes (production: the log/diagnostics
    directory under the data root). Must not be inside any user source
    tree; enforcing that is the sink implementation's job."""

    def write_report(self, payload: bytes, generated_at: str) -> str: ...


@dataclass(frozen=True)
class DiagnosticsService:
    """One-call export (AC 1 "one-click" is this single call; any UI
    entry point is out of scope for this slice)."""

    _provider: DiagnosticsSnapshotProvider
    _sink: DiagnosticsBundleSink
    _errors: BoundedErrorLog

    def export(self, *, generated_at: str) -> str:
        report = build_diagnostics_report(
            generated_at=generated_at,
            app_version=self._provider.app_version(),
            platform_python=self._provider.platform_python(),
            schema_version=self._provider.schema_version(),
            database_path=self._provider.database_path(),
            settings_summary=self._provider.settings_summary(),
            recent_errors=self._errors.recent(),
            environment_paths=self._provider.environment_paths(),
        )
        return self._sink.write_report(report.to_json_bytes(), generated_at)
