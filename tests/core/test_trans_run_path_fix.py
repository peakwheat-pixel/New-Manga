"""TRANS-RUN-PATH-FIX (L1-T-B) AC1: the reason behind the Host StartRun INVALID_REQUEST.

REAL-TRANSLATE-PROVIDER-1 reported "Host ``library_start_run`` returns INVALID_REQUEST while
Core direct with the same payload accepts it", and it was never triaged because the wire answer
is flat: ``core_service`` maps ``EMPTY_TARGET_SELECTION`` onto the frozen ``INVALID_REQUEST``
code with the generic message "Run request is invalid"
(``src/bootstrap/core_service.py:6810-6811,6826``), so the precise reason never leaves the
process. These tests pin both halves:

* the Host-identical payload is *shape*-valid (the refusal is about targets, not about shape);
* the precise reason now reaches stderr (the Host captures Core stderr), which is what makes the
  next occurrence diagnosable without touching the frozen error surface.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    CoreServiceServer,
    assemble_production_core,
)

#: Exactly the payload HostCommandDispatcher builds for ``library_start_run``:
#: {command, scope, overrides(provider_bindings from RunBindingDefaults), idempotency_key}
#: at the Core minor the Host registry binds (StartRun -> 3).
HOST_PAYLOAD_MINOR = 3


@pytest.fixture()
def env(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    server = CoreServiceServer(core)
    try:
        book = core.library.create_book("T-B")
        chapter = core.library.create_chapter(book.book_id, "C1")
        yield core, server, book, chapter
    finally:
        server.close()
        core.conn.close()


def dispatch(server, command: str, payload: dict, *, minor: int = HOST_PAYLOAD_MINOR) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": minor},
        "request_id": "tb-run-path",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def test_host_start_run_payload_is_refused_for_targets_with_a_precise_stderr_reason(
    env, capsys
) -> None:
    """AC1: INVALID_REQUEST on the wire, ``EMPTY_TARGET_SELECTION`` in the captured stderr."""
    _core, server, _book, chapter = env
    response = dispatch(server, "StartRun", {
        "command": "translate_all",
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id},
        "overrides": {"provider_bindings": {"ocr": "manga-ocr"}},
        "idempotency_key": "tb-empty-chapter",
    })

    # The frozen wire answer stays exactly what the Host saw (contract untouched).
    assert response["error"] is not None
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["message"] == "Run request is invalid"

    # ... but the precise cause is now observable, which is what was missing.
    stderr = capsys.readouterr().err
    assert "[core.run]" in stderr
    assert "EMPTY_TARGET_SELECTION" in stderr
    assert "scope expands to no active pages" in stderr


def test_scope_shape_errors_log_a_different_reason_than_target_errors(env, capsys) -> None:
    """AC1: the log distinguishes a malformed scope from an empty target set."""
    _core, server, _book, _chapter = env
    response = dispatch(server, "StartRun", {
        "command": "translate_all",
        "scope": {"kind": "chapter"},
        "idempotency_key": "tb-bad-scope",
    })

    assert response["error"] is not None
    assert response["error"]["code"] == "INVALID_REQUEST"
    stderr = capsys.readouterr().err
    assert "scope does not match a frozen PipelineScope variant" in stderr
    assert "EMPTY_TARGET_SELECTION" not in stderr
