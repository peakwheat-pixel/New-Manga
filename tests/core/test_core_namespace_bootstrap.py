from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pytest

from bootstrap.core_service import _ensure_preview_namespace
from application.resource_channel.dto import TypedResourceChannelError
from infrastructure.resource_channel.catalog_store import initialize_namespace
from infrastructure.resource_channel.handle_resolver import (
    PREVIEW_NAMESPACE_LOCK_NAME,
    acquire_shared_lease,
    resolve_namespace_identity,
)


def _assert_bound(catalog_db: Path, derived_root: Path) -> None:
    binding = acquire_shared_lease(
        derived_root,
        expected_catalog_identity=resolve_namespace_identity(catalog_db)[1],
    )
    try:
        assert binding.binding.catalog_root == str(catalog_db.resolve())
        assert binding.binding.derived_root == str(derived_root.resolve())
    finally:
        binding.release()


def test_catalog_exists_with_empty_derived_root_gets_controlled_first_binding(tmp_path: Path) -> None:
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root = tmp_path / "derived"
    catalog_db.parent.mkdir()
    derived_root.mkdir()
    # A valid, empty catalog schema with no namespace row models an interrupted
    # first bind: the file exists, but the derived root has never been bound.
    initialize_namespace(catalog_db, derived_root)
    with sqlite3.connect(catalog_db) as connection:
        connection.execute("DELETE FROM preview_namespace")
    (derived_root / PREVIEW_NAMESPACE_LOCK_NAME).unlink()

    _ensure_preview_namespace(catalog_db, derived_root)

    assert catalog_db.is_file()
    assert list(derived_root.iterdir()) == [derived_root / PREVIEW_NAMESPACE_LOCK_NAME]
    _assert_bound(catalog_db, derived_root)


def test_missing_lock_fails_closed_with_typed_resource_error(tmp_path: Path) -> None:
    derived_root = tmp_path / "derived"
    derived_root.mkdir()

    with pytest.raises(TypedResourceChannelError, match="namespace lock file is missing"):
        acquire_shared_lease(derived_root)


@pytest.mark.parametrize(
    "damaged_lock",
    [b"", b"not-json", b'{"protocol_version":1}', b"not-json" * 1024],
)
def test_damaged_lock_is_restored_from_verified_catalog_binding(
    tmp_path: Path, damaged_lock: bytes
) -> None:
    catalog_db = tmp_path / "catalog.sqlite"
    derived_root = tmp_path / "derived"
    derived_root.mkdir()
    initialize_namespace(catalog_db, derived_root)
    (derived_root / PREVIEW_NAMESPACE_LOCK_NAME).write_bytes(damaged_lock)

    _ensure_preview_namespace(catalog_db, derived_root)

    lock_bytes = (derived_root / PREVIEW_NAMESPACE_LOCK_NAME).read_bytes()
    assert lock_bytes.endswith(b"\n")
    lock_value = json.loads(lock_bytes.decode("utf-8"))
    assert lock_bytes == (json.dumps(lock_value, sort_keys=True) + "\n").encode("utf-8")
    _assert_bound(catalog_db, derived_root)


def test_damaged_lock_does_not_rebind_catalog_to_a_different_derived_identity(
    tmp_path: Path,
) -> None:
    catalog_db = tmp_path / "catalog.sqlite"
    derived_root = tmp_path / "derived"
    derived_root.mkdir()
    initialize_namespace(catalog_db, derived_root)
    lock_path = derived_root / PREVIEW_NAMESPACE_LOCK_NAME
    lock_path.write_bytes(b"not-json")
    with sqlite3.connect(catalog_db) as connection:
        connection.execute(
            "UPDATE preview_namespace SET derived_identity_index = derived_identity_index + 1"
        )

    with pytest.raises(TypedResourceChannelError):
        _ensure_preview_namespace(catalog_db, derived_root)

    assert lock_path.read_bytes() == b"not-json"
