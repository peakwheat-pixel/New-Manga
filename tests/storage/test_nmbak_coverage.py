"""FEA-13-COV-2: backup/2 coverage phase 2 (C-09 SC-B01a).

Covers: settings/drafts/plugins/trash-manifest are packaged with digest+size;
catalog/derived/external originals/OS vault are explicitly excluded with a
reason; a present-but-uncollectable category fails the create with no package;
restore defers the extra categories (byte-identical, reported) until the merge
slice lands.
"""

from __future__ import annotations

import hashlib
import json
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
)

NOW = "2026-11-09T13:00:00+00:00"


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

    # Covered categories (SC-B01a).
    settings = data_root / "settings"
    settings.mkdir(parents=True, exist_ok=True)
    (settings / "provider_profiles.json").write_text(
        json.dumps({"format_version": 1, "profiles": []}), encoding="utf-8"
    )
    (settings / "network_profiles.json").write_text(
        json.dumps({"format_version": 1, "profiles": []}), encoding="utf-8"
    )
    (settings / "provider_capability_bindings.json").write_text(
        json.dumps({"format_version": 1, "bindings": []}), encoding="utf-8"
    )
    drafts = data_root / "drafts"
    (drafts / "book-1").mkdir(parents=True, exist_ok=True)
    (drafts / "book-1" / "draft-1.json").write_text('{"text":"草稿"}', encoding="utf-8")
    plugins = data_root / "plugins"
    (plugins / "demo").mkdir(parents=True, exist_ok=True)
    (plugins / "demo" / "plugin.json").write_text('{"name":"demo"}', encoding="utf-8")
    (managed_root / "trash-manifest.json").write_text(
        '{"entries":[],"pending_cleanups":{}}', encoding="utf-8"
    )

    # Excluded categories (must never enter the package).
    (data_root / "catalog").mkdir(parents=True, exist_ok=True)
    (data_root / "catalog" / "catalog.sqlite").write_bytes(b"NOT-A-BACKUP")
    (data_root / "derived").mkdir(parents=True, exist_ok=True)
    (data_root / "derived" / "cache.bin").write_bytes(b"CACHE")

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
    }


def _create(workspace):
    created = workspace["service"].create("manual", "coverage")
    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))
        names = set(archive.namelist())
    return package, manifest, names


def test_covered_categories_are_packaged_with_digest_and_size(workspace):
    package, manifest, names = _create(workspace)

    assert manifest["included_categories"] == [
        "drafts",
        "plugins",
        "settings",
        "trash-manifest",
    ]
    extras = manifest["extras"]
    assert {item["category"] for item in extras} == {
        "drafts",
        "plugins",
        "settings",
        "trash-manifest",
    }
    for item in extras:
        member = f"{EXTRAS_PREFIX}{item['category']}/{item['relative_path']}"
        assert member in names, member
        with zipfile.ZipFile(package) as archive:
            payload = archive.read(member)
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]
        assert len(payload) == item["size_bytes"]

    # Excluded categories are recorded with a reason and never packaged.
    excluded = {entry["category"] for entry in manifest["excluded_categories"]}
    assert {"catalog", "derived", "external_source_files", "os_credential_vault"} <= excluded
    for entry in manifest["excluded_categories"]:
        assert entry["reason"]
    assert not any(name.startswith(EXTRAS_PREFIX + "catalog/") for name in names)
    assert not any(name.startswith(EXTRAS_PREFIX + "derived/") for name in names)


def test_uncollectable_category_fails_create_and_leaves_no_package(workspace, monkeypatch):
    def boom():  # pragma: no cover - exercised through the monkeypatch
        raise OSError("drafts directory is unreadable")

    monkeypatch.setattr(workspace["service"], "_collect_extras", boom)
    before = sorted(p.name for p in workspace["backup_root"].iterdir())

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].create("manual", "broken coverage")

    assert caught.value.code == "BACKUP_CREATE_FAILED"
    assert sorted(p.name for p in workspace["backup_root"].iterdir()) == before


def test_restore_defers_extras_and_leaves_them_byte_identical(workspace):
    package, manifest, _names = _create(workspace)
    data_root = workspace["data_root"]

    # Change the live copies after the backup: a deferred restore must not
    # overwrite them (merge semantics belong to FEA-13-RESTORE-4).
    (data_root / "settings" / "provider_profiles.json").write_text(
        json.dumps({"format_version": 1, "profiles": ["CHANGED"]}), encoding="utf-8"
    )
    (data_root / "drafts" / "book-1" / "draft-1.json").write_text(
        '{"text":"changed"}', encoding="utf-8"
    )
    (data_root / "plugins" / "demo" / "plugin.json").write_text(
        '{"name":"changed"}', encoding="utf-8"
    )
    (data_root / "managed" / "trash-manifest.json").write_text(
        '{"entries":[],"pending_cleanups":{"x":1}}', encoding="utf-8"
    )
    before = {
        path.relative_to(data_root).as_posix(): path.read_bytes()
        for path in data_root.rglob("*")
        if path.is_file() and path.suffix in {".json"}
    }

    report = workspace["service"].restore(package.stem, confirm_restore=True)

    assert report["deferred_categories"] == [
        "drafts",
        "plugins",
        "settings",
        "trash-manifest",
    ]
    after = {
        path.relative_to(data_root).as_posix(): path.read_bytes()
        for path in data_root.rglob("*")
        if path.is_file() and path.suffix in {".json"}
    }
    # Only library.db may change; every JSON byte stays exactly as it was.
    for relative, payload in before.items():
        if relative == "library.db":
            continue
        assert after[relative] == payload, relative


def test_tampered_extras_member_is_corrupt(workspace):
    package, _manifest, _names = _create(workspace)
    with zipfile.ZipFile(package) as archive:
        infos = archive.infolist()
        payloads = {info.filename: archive.read(info.filename) for info in infos}
    target = next(
        name for name in payloads if name.startswith(EXTRAS_PREFIX + "settings/")
    )
    # Same length, different bytes: only the sha256 check can catch this, so the
    # test discriminates the digest validation itself (not just the size check).
    original = payloads[target]
    payloads[target] = bytes([original[0] ^ 0x01]) + original[1:]
    temporary = package.with_name(".tampered.nmbak")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for info in infos:
            archive.writestr(info, payloads[info.filename])
    temporary.replace(package)

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].restore(package.stem, confirm_restore=True)

    assert caught.value.code == "BACKUP_CORRUPT"


def _rewrite_manifest(package: Path, mutate) -> None:
    with zipfile.ZipFile(package) as archive:
        infos = archive.infolist()
        payloads = {info.filename: archive.read(info.filename) for info in infos}
    manifest = json.loads(payloads[MANIFEST_NAME])
    mutate(manifest)
    payloads[MANIFEST_NAME] = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    temporary = package.with_name(".rewrite.nmbak")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for info in infos:
            archive.writestr(info, payloads[info.filename])
    temporary.replace(package)


def test_empty_category_roots_are_included_with_zero_files(workspace):
    """R-001: a clean shutdown leaves an EMPTY drafts/ -- that must still backup."""
    data_root = workspace["data_root"]
    for directory in (data_root / "drafts", data_root / "plugins"):
        for path in directory.rglob("*"):
            if path.is_file():
                path.unlink()

    _package, manifest, names = _create(workspace)

    assert manifest["included_categories"] == [
        "drafts",
        "plugins",
        "settings",
        "trash-manifest",
    ]
    assert manifest["skipped_categories"] == []
    assert not any(name.startswith(EXTRAS_PREFIX + "drafts/") for name in names)
    assert not any(name.startswith(EXTRAS_PREFIX + "plugins/") for name in names)


def test_running_journal_lock_is_not_packaged(workspace):
    """R-002: `.lock/pid` is transient process state, not user data."""
    data_root = workspace["data_root"]
    lock_dir = data_root / "drafts" / ".lock"
    lock_dir.mkdir(parents=True, exist_ok=True)
    (lock_dir / "pid").write_text("12345", encoding="utf-8")
    (data_root / "drafts" / "book-1" / "draft-1.json.tmp").write_text("x", encoding="utf-8")

    _package, manifest, names = _create(workspace)

    assert not any(".lock" in name for name in names)
    assert not any(name.endswith(".tmp") for name in names)
    assert "drafts" in manifest["included_categories"]


def test_included_categories_mismatch_is_corrupt(workspace):
    """R-007: declared categories must match the packaged members."""
    package, _manifest, _names = _create(workspace)
    _rewrite_manifest(
        package,
        lambda manifest: manifest.__setitem__("included_categories", ["settings"]),
    )

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].restore(package.stem, confirm_restore=True)

    assert caught.value.code == "BACKUP_CORRUPT"


def test_unknown_extras_category_is_forward_compatible(workspace):
    """R-007: a newer package with a new category is unsupported, not corrupt."""
    package, _manifest, _names = _create(workspace)

    def add_future(manifest: dict) -> None:
        manifest["extras"].append(
            {
                "category": "future",
                "relative_path": "x.json",
                "sha256": "0" * 64,
                "size_bytes": 0,
            }
        )

    _rewrite_manifest(package, add_future)

    with pytest.raises(NmbakBackupError) as caught:
        workspace["service"].restore(package.stem, confirm_restore=True)

    assert caught.value.code == "BACKUP_FORMAT_UNSUPPORTED"
