"""SETTINGS-OPEN-C-2-BACKUP AC1/AC2/AC3: the .nmbak wire on the production Core.

Exercises the four new application-channel commands at the
``dispatch_request`` level on a real production assembly:

- ``backup.create``  -> {backup_id, path, size_bytes, created_at, verified}
  and a real ``.nmbak`` file under ``<data_root>/backups/``;
- ``backup.list``    -> the package projection (verified flag included);
- ``backup.restore`` -> overwrite + pre_restore package + consistency report,
  ``BACKUP_RESTORE_BUSY`` while a Run is active, ``BACKUP_CORRUPT`` for a
  tampered package, ``BACKUP_NOT_FOUND`` for an unknown id;
- ``backup.delete``  -> {removed: true}, idempotent NOT_FOUND afterwards.

The commands are ordinary application-channel commands (cleanup precedent),
not HostControl: the frozen host-control envelope must keep refusing them.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import zipfile

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    _BACKUP_COMMANDS,
    _HOST_CONTROL_COMMANDS,
    assemble_production_core,
)

NOW = "2026-10-23T02:00:00+00:00"


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _request(server: CoreServiceServer, command: str, payload, request_id: str = "req-backup-1") -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _backup_root(core) -> Path:
    return Path(core.data_root) / "backups"


def _insert_running_run(core) -> None:
    with core.conn as conn:
        conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
            " requested_targets_json, settings_snapshot_json,"
            " provider_binding_snapshot_json, context_policy_json, status,"
            " run_json, updated_at)"
            " VALUES ('run-busy', 'translate', 'book', '[]', '{}', '{}', '{}',"
            " 'running', '{}', ?)",
            (NOW,),
        )


def test_backup_commands_are_application_commands_not_host_control() -> None:
    assert _BACKUP_COMMANDS == frozenset(
        {"backup.create", "backup.list", "backup.restore", "backup.delete"}
    )
    assert not _BACKUP_COMMANDS & _HOST_CONTROL_COMMANDS


def test_protocol_version_is_unchanged_by_the_backup_surface(core) -> None:
    assert (PROTOCOL_MAJOR, PROTOCOL_MINOR) == (2, 3)
    server = CoreServiceServer(core)
    ping = _request(server, "core.ping", {}, request_id="req-ping")
    assert ping["error"] is None
    assert ping["result"]["protocol_version"] == {"major": 2, "minor": 3}


def test_create_list_restore_delete_round_trip(core) -> None:
    server = CoreServiceServer(core)
    created = _request(server, "backup.create", {"backup_type": "manual"})
    assert created["error"] is None
    result = created["result"]
    backup_id = result["backup_id"]
    assert result["verified"] is True
    package = _backup_root(core) / f"{backup_id}.nmbak"
    assert package.is_file()
    with zipfile.ZipFile(package) as archive:
        assert "manifest.json" in archive.namelist()
        assert "library.db" in archive.namelist()

    listed = _request(server, "backup.list", {})
    assert listed["error"] is None
    assert backup_id in {item["backup_id"] for item in listed["result"]}
    assert all(item["verified"] for item in listed["result"])

    with core.conn as conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-after-backup', 'x', ?, ?)",
            (NOW, NOW),
        )
    assert _request(server, "backup.restore", {"backup_id": backup_id})["error"]["code"] == "BACKUP_RESTORE_REQUIRES_CONFIRMATION"
    restored = _request(
        server, "backup.restore", {"backup_id": backup_id, "confirm_restore": True}
    )
    assert restored["error"] is None
    report = restored["result"]
    assert report["restored_from"] == backup_id
    assert (_backup_root(core) / f"{report['pre_restore_backup_id']}.nmbak").is_file()
    remaining = {
        row["book_id"] for row in core.conn.execute("SELECT book_id FROM books")
    }
    assert "book-after-backup" not in remaining

    removed = _request(server, "backup.delete", {"backup_id": backup_id})
    assert removed["error"] is None
    assert removed["result"] == {"removed": True}
    missing = _request(server, "backup.delete", {"backup_id": backup_id})
    assert missing["error"]["code"] == "BACKUP_NOT_FOUND"
    assert missing["error"]["category"] == "not_found"


def test_restore_is_refused_while_a_run_is_active(core) -> None:
    server = CoreServiceServer(core)
    created = _request(server, "backup.create", {"backup_type": "manual"})
    backup_id = created["result"]["backup_id"]
    _insert_running_run(core)
    try:
        refused = _request(
            server, "backup.restore", {"backup_id": backup_id, "confirm_restore": True}
        )
    finally:
        with core.conn as conn:
            conn.execute("DELETE FROM pipeline_runs WHERE run_id = 'run-busy'")
    assert refused["error"]["code"] == "BACKUP_RESTORE_BUSY"
    assert refused["error"]["category"] == "conflict"
    assert refused["error"]["retryable"] is True


def test_tampered_package_is_rejected_as_corrupt(core) -> None:
    server = CoreServiceServer(core)
    created = _request(server, "backup.create", {"backup_type": "manual"})
    backup_id = created["result"]["backup_id"]
    package = _backup_root(core) / f"{backup_id}.nmbak"
    with zipfile.ZipFile(package) as archive:
        entries = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    entries["library.db"] = entries["library.db"] + b"TAMPERED"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)

    rejected = _request(
        server, "backup.restore", {"backup_id": backup_id, "confirm_restore": True}
    )
    assert rejected["error"]["code"] == "BACKUP_CORRUPT"
    assert rejected["error"]["category"] == "validation"


def test_malformed_payloads_are_typed(core) -> None:
    server = CoreServiceServer(core)
    not_an_object = _request(server, "backup.create", [1, 2, 3])
    assert not_an_object["error"]["code"] == "INVALID_REQUEST"
    wrong_type = _request(server, "backup.create", {"backup_type": "automatic"})
    assert wrong_type["error"]["code"] == "INVALID_REQUEST"
    bad_id = _request(
        server, "backup.restore", {"backup_id": "../library.db", "confirm_restore": True}
    )
    assert bad_id["error"]["code"] == "BACKUP_NOT_FOUND"


def test_assembly_without_the_service_fails_closed(core) -> None:
    import dataclasses

    without = dataclasses.replace(core, backup=None)
    server = CoreServiceServer(without)
    response = _request(server, "backup.list", {})
    assert response["error"]["code"] == "CORE_UNAVAILABLE"
