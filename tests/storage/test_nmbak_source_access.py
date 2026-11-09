"""FEA-13-SRC-6: source-access metadata rides the backup package (C-09 SC-B01 / SC-B07 ④).

The Host-private ``registry.v1.dat`` is opaque DPAPI ciphertext. Core copies the bytes
verbatim (it has no DPAPI dependency) and, after an overwrite restore, hands the segment
to the Host through ``<backup_root>/restore-handoff/<backup_id>/``. The Host is the only
party that decrypts/merges it (covered by the Host-side tests).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.nmbak import (  # noqa: E402
    EXTRAS_PREFIX,
    MANIFEST_NAME,
    NmbakBackupError,
    NmbakBackupService,
    SOURCE_ACCESS_CATEGORY,
    SOURCE_ACCESS_FILE,
)

#: A realistic-shaped ciphertext: ``NMSAR1\0`` + little-endian length + opaque bytes.
MAGIC = b"NMSAR1\x00"


def _snapshot(payload: bytes = b"opaque-dpapi-ciphertext-0f3c") -> bytes:
    import struct

    return MAGIC + struct.pack("<I", len(payload)) + payload


@pytest.fixture()
def workspace(tmp_path: Path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    data_root = tmp_path / "data"
    managed_root = data_root / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    db_path = data_root / "library.db"
    conn, _opened = open_database(
        db_path,
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()

    registry_dir = data_root / "host" / "source-access"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry = registry_dir / SOURCE_ACCESS_FILE
    registry.write_bytes(_snapshot())

    service = NmbakBackupService(
        conn,
        data_root / "backups",
        managed_root,
        app_version="0.1.0",
        data_root=data_root,
    )
    yield {
        "conn": conn,
        "service": service,
        "data_root": data_root,
        "managed_root": managed_root,
        "backup_root": data_root / "backups",
        "registry": registry,
    }


def _create(workspace) -> tuple[Path, dict, set[str]]:
    created = workspace["service"].create("manual", "source-access")
    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))
        names = set(archive.namelist())
    return package, manifest, names


def test_registry_is_packaged_verbatim(workspace):
    """AC1: bytes verbatim, manifest digest/size, no plaintext leak, source untouched."""
    registry = workspace["registry"]
    before_bytes = registry.read_bytes()
    before_mtime = registry.stat().st_mtime_ns

    package, manifest, names = _create(workspace)

    member = f"{EXTRAS_PREFIX}{SOURCE_ACCESS_CATEGORY}/{SOURCE_ACCESS_FILE}"
    assert member in names
    with zipfile.ZipFile(package) as archive:
        packed = archive.read(member)
    assert packed == before_bytes
    assert packed.startswith(MAGIC)

    extras = [item for item in manifest["extras"] if item["category"] == SOURCE_ACCESS_CATEGORY]
    assert len(extras) == 1
    assert extras[0]["relative_path"] == SOURCE_ACCESS_FILE
    assert extras[0]["sha256"] == hashlib.sha256(before_bytes).hexdigest()
    assert extras[0]["size_bytes"] == len(before_bytes)
    assert SOURCE_ACCESS_CATEGORY in manifest["included_categories"]

    # The packaged member must not contain a decrypted JSON body.
    assert b'{"entries"' not in packed and b'{"format_version"' not in packed

    # AC1: creating a package never mutates the live registry.
    assert registry.read_bytes() == before_bytes
    assert registry.stat().st_mtime_ns == before_mtime


def test_absent_registry_means_no_segment(workspace):
    """AC2(b): an absent registry is a legitimate empty state, not a failure."""
    workspace["registry"].unlink()

    _package, manifest, names = _create(workspace)

    assert not any(SOURCE_ACCESS_CATEGORY in name for name in names)
    assert SOURCE_ACCESS_CATEGORY not in manifest["included_categories"]
    assert not [item for item in manifest["extras"] if item["category"] == SOURCE_ACCESS_CATEGORY]


def test_empty_registry_is_still_packaged(workspace):
    """AC2(c): an existing-but-empty snapshot is packaged (presence is what matters)."""
    workspace["registry"].write_bytes(_snapshot(b""))

    _package, manifest, names = _create(workspace)

    member = f"{EXTRAS_PREFIX}{SOURCE_ACCESS_CATEGORY}/{SOURCE_ACCESS_FILE}"
    assert member in names
    extras = [item for item in manifest["extras"] if item["category"] == SOURCE_ACCESS_CATEGORY]
    assert extras and extras[0]["size_bytes"] == len(_snapshot(b""))


def test_unreadable_registry_fails_the_create(workspace, monkeypatch):
    """AC2(a): a present-but-unreadable registry fails create with a typed error."""
    original_open = Path.open

    def denied(self, *args, **kwargs):
        if self.name == SOURCE_ACCESS_FILE:
            raise PermissionError("denied by test")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied)

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].create("manual", "unreadable")
    assert caught.value.code == "BACKUP_CREATE_FAILED"
    # No package is left behind.
    assert list((workspace["backup_root"]).glob("*.nmbak")) == []


def test_oversized_registry_is_refused(workspace):
    """AC1: the 4 MiB cap keeps the package honest (Host Load has the same limit)."""
    workspace["registry"].write_bytes(_snapshot(b"x" * (4 * 1024 * 1024 + 1)))

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].create("manual", "oversized")
    assert caught.value.code == "BACKUP_CREATE_FAILED"


def test_overwrite_restore_writes_the_host_handoff(workspace):
    """AC3: after a successful overwrite restore the segment lands in the handoff dir."""
    created = workspace["service"].create("manual", "handoff")
    backup_id = created["backup_id"]

    report = workspace["service"].restore(backup_id, confirm_restore=True)

    handoff_root = workspace["backup_root"] / "restore-handoff" / backup_id
    segment = handoff_root / SOURCE_ACCESS_CATEGORY / SOURCE_ACCESS_FILE
    assert segment.is_file()
    assert segment.read_bytes() == workspace["registry"].read_bytes()
    handoff = json.loads((handoff_root / "handoff.json").read_text(encoding="utf-8"))
    assert handoff["backup_id"] == backup_id
    assert handoff["member"] == f"{EXTRAS_PREFIX}{SOURCE_ACCESS_CATEGORY}/{SOURCE_ACCESS_FILE}"
    assert handoff["sha256"] == hashlib.sha256(segment.read_bytes()).hexdigest()
    assert report["source_access_handoff"]["sha256"] == handoff["sha256"]


def test_restore_without_the_segment_writes_no_handoff(workspace):
    """AC2(b) restore side: a package without the segment produces no handoff."""
    workspace["registry"].unlink()
    created = workspace["service"].create("manual", "no-segment")

    report = workspace["service"].restore(created["backup_id"], confirm_restore=True)

    assert "source_access_handoff" not in report
    assert not (workspace["backup_root"] / "restore-handoff" / created["backup_id"]).exists()
