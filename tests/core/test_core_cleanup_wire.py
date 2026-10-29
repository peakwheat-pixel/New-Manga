"""SETTINGS-OPEN-B-2 AC1: the cache/Revision cleanup wire on the production Core.

Exercises the three new application-channel commands at the
``dispatch_request`` level on a real production assembly
(``assemble_production_core``):

- ``cleanup.preview``  -> ``CleanupPreview.to_dict()`` + the persisted
  ``pending_cleanups`` count (read-only: previewing removes nothing);
- ``cleanup.run``      -> ``CleanupOutcome.to_dict()`` + removed/failed/
  skipped counts, idempotent, failed removals persisted as pending;
- ``cleanup.retry_pending`` -> the same outcome projection; settled
  entries leave the ledger, files that fail again stay pending.

Safety pins (same boundary as tests/maintenance/test_cleanup.py, which this
file must not weaken):

- target paths outside the ``cache/`` safe prefixes are ``skipped`` and the
  file survives (including a ``..`` traversal under a safe prefix);
- the projections contain relative paths only -- never an OS path;
- a path-shaped ``request_id`` is redacted (SEC-FIX-PATH-ECHO-1 precedent);
- the commands are NOT host-control operations: the application channel
  accepts them while the frozen host-control envelope still refuses them
  (contract §5.7 set stays closed);
- an assembly without the injected ``CleanupService`` fails closed with
  CORE_UNAVAILABLE/unavailable instead of crashing the sidecar.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance.cleanup import (  # noqa: E402
    CleanupService,
    CleanupTarget,
)
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    _CLEANUP_COMMANDS,
    _HOST_CONTROL_COMMANDS,
    assemble_production_core,
)
from infrastructure.imaging.tile_cache_sweep import (  # noqa: E402
    WebtoonTileCacheSweeper,
)

CLEANUP_COMMANDS = (
    "cleanup.preview",
    "cleanup.run",
    "cleanup.retry_pending",
)


class StaticInventory:
    """Fixed population for boundary tests (bypasses the real sweeper)."""

    def __init__(self, *targets: CleanupTarget) -> None:
        self._targets = tuple(targets)

    def list_cache_files(self) -> tuple[CleanupTarget, ...]:
        return self._targets


class FlakyRemover:
    """Fails the first N removal attempts, then delegates to the storage."""

    def __init__(self, inner, failures: int) -> None:
        self._inner = inner
        self._remaining = failures

    def remove_managed(self, relative_path: str) -> None:
        if self._remaining > 0:
            self._remaining -= 1
            raise OSError(f"transient storage fault on {relative_path}")
        self._inner.remove_managed(relative_path)


@pytest.fixture()
def core(tmp_path: Path):
    """One real production assembly on a temp data root."""
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _managed_root(core) -> Path:
    return Path(core.storage.root)


def _tile_dir(core) -> Path:
    return _managed_root(core) / "cache" / "webtoon-tiles"


def _make_tile(core, name: str, payload: bytes) -> Path:
    tile_dir = _tile_dir(core)
    tile_dir.mkdir(parents=True, exist_ok=True)
    path = tile_dir / name
    path.write_bytes(payload)
    return path


def _manifest(core) -> _JsonTrashManifest:
    return _JsonTrashManifest(_managed_root(core) / "trash-manifest.json")


def _request(
    server: CoreServiceServer,
    command: str,
    payload,
    request_id: str = "req-cleanup-1",
    *,
    channel: str | None = None,
) -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }
    if channel is not None:
        request["channel"] = channel
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _no_absolute_paths(value) -> bool:
    text = json.dumps(value)
    return ":\\" not in text and ":/" not in text and "\\\\" not in text


# ---------------------------------------------------------------------------
# command surface / protocol pin
# ---------------------------------------------------------------------------


def test_cleanup_commands_are_application_commands_not_host_control() -> None:
    # SETTINGS-OPEN-B-2 r1 ruling: the host-control envelope is frozen to the
    # HOST-ISSUER-1 set (contract §5.7). The cleanup faces must ride the
    # ordinary application channel the Tauri bridge uses, otherwise every
    # production invoke would be refused with HOST_ONLY_REQUIRED.
    assert _CLEANUP_COMMANDS == frozenset(CLEANUP_COMMANDS)
    assert not _CLEANUP_COMMANDS & _HOST_CONTROL_COMMANDS


def test_protocol_version_is_unchanged_by_the_cleanup_surface(core) -> None:
    # The additive production-only command surface follows the later-family
    # precedent: the envelope version stays at the frozen 2.3.
    assert (PROTOCOL_MAJOR, PROTOCOL_MINOR) == (2, 3)
    server = CoreServiceServer(core, cleanup=core.cleanup)
    ping = _request(server, "core.ping", {}, request_id="req-ping")
    assert ping["error"] is None
    assert ping["result"]["protocol_version"] == {"major": 2, "minor": 3}


# ---------------------------------------------------------------------------
# cleanup.preview
# ---------------------------------------------------------------------------


def test_preview_empty_cache_reports_zero_and_removes_nothing(core) -> None:
    server = CoreServiceServer(core, cleanup=core.cleanup)
    response = _request(server, "cleanup.preview", {})
    assert response["error"] is None
    assert response["result"] == {
        "targets": [],
        "total_bytes": 0,
        "pending_cleanups": 0,
    }


def test_preview_lists_targets_bytes_and_pending_count(core) -> None:
    tile_a = _make_tile(core, "tile-aaaa-00000.png", b"x" * 10)
    _make_tile(core, "tile-bbbb-00001.png", b"y" * 20)
    _manifest(core).write_manifest(
        {
            "batches": [],
            "pending_cleanups": ["cache/webtoon-tiles/tile-ghost-00000.png"],
        }
    )
    server = CoreServiceServer(core, cleanup=core.cleanup)

    response = _request(server, "cleanup.preview", {})

    assert response["error"] is None
    result = response["result"]
    assert result["pending_cleanups"] == 1
    assert result["total_bytes"] == 30
    assert result["targets"] == [
        {
            "relative_path": "cache/webtoon-tiles/tile-aaaa-00000.png",
            "size_bytes": 10,
        },
        {
            "relative_path": "cache/webtoon-tiles/tile-bbbb-00001.png",
            "size_bytes": 20,
        },
    ]
    assert tile_a.is_file(), "preview must never delete"
    assert _no_absolute_paths(result), "preview must not echo OS paths"


# ---------------------------------------------------------------------------
# cleanup.run
# ---------------------------------------------------------------------------


def test_run_removes_cache_generations_and_returns_structured_counts(core) -> None:
    tile_a = _make_tile(core, "tile-aaaa-00000.png", b"old-generation")
    tile_b = _make_tile(core, "tile-bbbb-00000.png", b"new-generation")
    server = CoreServiceServer(core, cleanup=core.cleanup)

    response = _request(server, "cleanup.run", {})

    assert response["error"] is None
    result = response["result"]
    assert result["removed"] == 2
    assert result["failed"] == 0
    assert result["skipped"] == 0
    assert result["items"] == {
        "cache/webtoon-tiles/tile-aaaa-00000.png": {"status": "ok", "reason": ""},
        "cache/webtoon-tiles/tile-bbbb-00000.png": {"status": "ok", "reason": ""},
    }
    assert not tile_a.exists() and not tile_b.exists()
    assert _no_absolute_paths(result)

    preview = _request(server, "cleanup.preview", {})
    assert preview["result"]["targets"] == []
    assert preview["result"]["pending_cleanups"] == 0


def test_run_is_idempotent(core) -> None:
    _make_tile(core, "tile-aaaa-00000.png", b"payload")
    server = CoreServiceServer(core, cleanup=core.cleanup)

    first = _request(server, "cleanup.run", {})
    second = _request(server, "cleanup.run", {})

    assert first["result"]["removed"] == 1
    assert second["result"]["removed"] == 0
    assert second["result"]["failed"] == 0
    assert second["result"]["items"] == {}


def test_failed_removal_is_persisted_as_pending(core) -> None:
    tile = _make_tile(core, "tile-fault-00000.png", b"payload")
    flaky = CleanupService(
        WebtoonTileCacheSweeper(_tile_dir(core), _managed_root(core)),
        FlakyRemover(core.storage, failures=1),
        _manifest(core),
    )
    server = CoreServiceServer(core, cleanup=flaky)

    response = _request(server, "cleanup.run", {})

    assert response["error"] is None
    result = response["result"]
    assert result["failed"] == 1
    assert result["removed"] == 0
    assert result["items"]["cache/webtoon-tiles/tile-fault-00000.png"][
        "status"
    ] == "failed"
    # review-b2 P2-1: never project an OSError text (it may embed an absolute
    # managed-root path) -- the wire reason is a fixed, path-free sentence.
    assert (
        result["items"]["cache/webtoon-tiles/tile-fault-00000.png"]["reason"]
        == "remove failed"
    )
    assert "\\" not in result["items"]["cache/webtoon-tiles/tile-fault-00000.png"]["reason"]
    assert "/" not in result["items"]["cache/webtoon-tiles/tile-fault-00000.png"]["reason"]
    # the failure is never silent: the shared ledger sees it immediately
    assert flaky.pending_cleanup_count() == 1
    assert tile.is_file(), "a failed removal must not pretend to succeed"

    preview = _request(server, "cleanup.preview", {})
    assert preview["result"]["pending_cleanups"] == 1


# ---------------------------------------------------------------------------
# cleanup.retry_pending
# ---------------------------------------------------------------------------


def test_retry_clears_pending_after_the_fault_is_gone(core) -> None:
    tile = _make_tile(core, "tile-retry-00000.png", b"payload")
    flaky = CleanupService(
        WebtoonTileCacheSweeper(_tile_dir(core), _managed_root(core)),
        FlakyRemover(core.storage, failures=1),
        _manifest(core),
    )
    server = CoreServiceServer(core, cleanup=flaky)
    failed = _request(server, "cleanup.run", {})
    assert failed["result"]["failed"] == 1

    retried = _request(server, "cleanup.retry_pending", {})

    assert retried["error"] is None
    result = retried["result"]
    assert result["removed"] == 1
    assert result["failed"] == 0
    assert result["items"]["cache/webtoon-tiles/tile-retry-00000.png"][
        "status"
    ] == "ok"
    assert not tile.exists()
    assert flaky.pending_cleanup_count() == 0
    assert _request(server, "cleanup.preview", {})["result"]["pending_cleanups"] == 0


def test_retry_with_empty_ledger_is_an_empty_outcome(core) -> None:
    server = CoreServiceServer(core, cleanup=core.cleanup)
    response = _request(server, "cleanup.retry_pending", {})
    assert response["error"] is None
    assert response["result"] == {
        "items": {},
        "removed": 0,
        "failed": 0,
        "skipped": 0,
    }


def test_retry_rechecks_the_never_clean_predicate(core) -> None:
    tile = _make_tile(core, "tile-ok-00001.png", b"payload")
    _manifest(core).write_manifest(
        {
            "batches": [],
            "pending_cleanups": [
                "cache/webtoon-tiles/" + tile.name,
                "../../escape.png",
            ],
        }
    )
    server = CoreServiceServer(core, cleanup=core.cleanup)

    response = _request(server, "cleanup.retry_pending", {})

    result = response["result"]
    assert result["removed"] == 1
    assert result["skipped"] == 1
    assert result["items"]["../../escape.png"]["status"] == "skipped"
    assert not tile.exists(), "the safe pending entry should have been swept"
    assert core.cleanup.pending_cleanup_count() == 0


# ---------------------------------------------------------------------------
# safety boundary: only safe cache prefixes are ever addressed
# ---------------------------------------------------------------------------


def test_run_skips_business_files_and_dotdot_traversal(core) -> None:
    managed = _managed_root(core)
    original = managed / "books" / "b1" / "chapters" / "c1" / "original" / "p1.png"
    original.parent.mkdir(parents=True, exist_ok=True)
    original.write_bytes(b"ORIGINAL BYTES")
    tile = _tile_dir(core) / "tile-safe-00000.png"
    tile.parent.mkdir(parents=True, exist_ok=True)
    tile.write_bytes(b"tile")
    sneaky = "cache/webtoon-tiles/../../books/b1/chapters/c1/original/p1.png"
    inventory = StaticInventory(
        CleanupTarget("books/b1/original/p1.png", 8),
        CleanupTarget(sneaky, 14),
        CleanupTarget("cache/webtoon-tiles/tile-safe-00000.png", 4),
    )
    service = CleanupService(inventory, core.storage, _manifest(core))
    server = CoreServiceServer(core, cleanup=service)

    response = _request(server, "cleanup.run", {})

    result = response["result"]
    assert result["removed"] == 1
    assert result["skipped"] == 2
    assert result["items"]["books/b1/original/p1.png"]["status"] == "skipped"
    assert result["items"][sneaky]["status"] == "skipped"
    assert original.is_file(), "a business file must survive"
    assert not tile.exists()


# ---------------------------------------------------------------------------
# request validation / redaction / fail-closed construction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", CLEANUP_COMMANDS)
@pytest.mark.parametrize("payload", [["cache"], "cache", None, 3])
def test_non_object_payload_is_typed_invalid_request(core, command, payload) -> None:
    server = CoreServiceServer(core, cleanup=core.cleanup)
    response = _request(server, command, payload)
    assert response["result"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["category"] == "validation"
    assert response["error"]["retryable"] is False


def test_path_shaped_request_id_is_redacted_on_success_and_rejection(core) -> None:
    windows_path = "C:/private/shelf.db secret-marker"
    server = CoreServiceServer(core, cleanup=core.cleanup)

    accepted = _request(server, "cleanup.preview", {}, request_id=windows_path)
    assert accepted["error"] is None
    assert accepted["request_id"] == "[redacted]"

    rejected = _request(
        server, "cleanup.run", payload="not-an-object", request_id=windows_path
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert rejected["request_id"] == "[redacted]"
    serialized = json.dumps(rejected)
    assert "private" not in serialized and "secret-marker" not in serialized


@pytest.mark.parametrize("command", CLEANUP_COMMANDS)
def test_missing_service_fails_closed_with_core_unavailable(core, command) -> None:
    # no cleanup= injection: the assembly forgot to wire the service. The
    # faces refuse with the existing CORE_UNAVAILABLE family, retryable --
    # and the server keeps answering other commands (no crash).
    server = CoreServiceServer(core)
    response = _request(server, command, {})
    assert response["result"] is None
    assert response["error"]["code"] == "CORE_UNAVAILABLE"
    assert response["error"]["category"] == "unavailable"
    assert response["error"]["retryable"] is True
    ping = _request(server, "core.ping", {})
    assert ping["error"] is None


def test_cleanup_commands_are_not_accepted_on_the_frozen_host_control_envelope(
    core,
) -> None:
    server = CoreServiceServer(core, cleanup=core.cleanup)
    _make_tile(core, "tile-hostctl-00000.png", b"payload")

    response = _request(server, "cleanup.run", {}, channel="host-control")

    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["message"] == "Host control request is invalid"
    assert _tile_dir(core).joinpath("tile-hostctl-00000.png").is_file()
    assert core.cleanup.pending_cleanup_count() == 0
