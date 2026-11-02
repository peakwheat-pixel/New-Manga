"""REALUSE-DATA-SAFETY-1 AC1: a copied/restored/relocated data root re-binds.

A whole-directory copy of the data root (backup restore, new machine, moving
``%APPDATA%``) carries the preview-namespace lock and catalog binding of the
ORIGINAL volume/file identities. The frozen first-bind initializer refuses such
a binding, and that refusal used to abort the Core sidecar before it could
serve. These tests pin the migration path: the Core re-binds the namespace to
the CURRENT identities, keeps every catalog row, and still fails closed on
structural anomalies.
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import _ensure_preview_namespace  # noqa: E402
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    initialize_namespace,
    verify_binding_for_root,
)
from infrastructure.resource_channel.handle_resolver import (  # noqa: E402
    TypedResourceChannelError,
    read_lock_binding_if_any,
    resolve_namespace_identity,
)

SCOPE_CLASS = "managed-read-only"


def _bind_new_root(root: Path) -> tuple[Path, Path]:
    catalog_db = root / "catalog" / "catalog.sqlite"
    derived_root = root / "derived"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    return catalog_db, derived_root


def _insert_catalog_row(catalog_db: Path, resource_id: str, rel_path: str) -> None:
    connection = sqlite3.connect(str(catalog_db))
    try:
        connection.execute(
            "INSERT INTO resource_catalog(resource_id, scope_class, rel_path) VALUES(?, ?, ?)",
            (resource_id, SCOPE_CLASS, rel_path),
        )
        connection.commit()
    finally:
        connection.close()


def _catalog_rows(catalog_db: Path) -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(f"file:{catalog_db.as_posix()}?mode=ro", uri=True)
    try:
        return [
            (row[0], row[1], row[2])
            for row in connection.execute(
                "SELECT resource_id, scope_class, rel_path FROM resource_catalog"
                " ORDER BY resource_id"
            )
        ]
    finally:
        connection.close()


def _namespace_row(catalog_db: Path) -> tuple:
    connection = sqlite3.connect(f"file:{catalog_db.as_posix()}?mode=ro", uri=True)
    try:
        return connection.execute(
            "SELECT protocol_version, derived_root, derived_identity_volume,"
            " derived_identity_index, catalog_root, catalog_identity_volume,"
            " catalog_identity_index FROM preview_namespace WHERE singleton = 1"
        ).fetchone()
    finally:
        connection.close()


def _copy_root(source: Path, destination: Path) -> tuple[Path, Path]:
    shutil.copytree(source, destination)
    return destination / "catalog" / "catalog.sqlite", destination / "derived"


def test_copied_data_root_rebinds_without_abort(tmp_path: Path) -> None:
    """AC1: the exact real-use failure (whole-directory copy) now succeeds."""

    source = tmp_path / "source"
    source_catalog, source_derived = _bind_new_root(source)
    _insert_catalog_row(source_catalog, "res-1", "pages/one.png")
    _insert_catalog_row(source_catalog, "res-2", "pages/two.png")

    copied_catalog, copied_derived = _copy_root(source, tmp_path / "copy")

    stale_binding = read_lock_binding_if_any(str(copied_derived))
    assert stale_binding is not None
    # The copied lock still describes the ORIGINAL identities.
    with pytest.raises(TypedResourceChannelError):
        verify_binding_for_root(stale_binding, copied_catalog, copied_derived)

    _ensure_preview_namespace(copied_catalog, copied_derived)  # must not raise

    derived_str, derived_identity = resolve_namespace_identity(copied_derived)
    catalog_str, catalog_identity = resolve_namespace_identity(copied_catalog)

    rebound = read_lock_binding_if_any(str(copied_derived))
    assert rebound is not None
    assert rebound.protocol_version == 1
    assert rebound.derived_root == derived_str
    assert rebound.derived_identity == derived_identity
    assert rebound.catalog_root == catalog_str
    assert rebound.catalog_identity == catalog_identity

    row = _namespace_row(copied_catalog)
    assert row[0] == 1
    assert row[1] == derived_str
    assert (row[2], row[3]) == derived_identity
    assert row[4] == catalog_str
    assert (row[5], row[6]) == catalog_identity

    # The catalog rows (and therefore runtime resource resolution) survive.
    assert _catalog_rows(copied_catalog) == [
        ("res-1", SCOPE_CLASS, "pages/one.png"),
        ("res-2", SCOPE_CLASS, "pages/two.png"),
    ]

    # A verified binding must now pass and a second startup must be a no-op.
    verify_binding_for_root(rebound, copied_catalog, copied_derived)
    _ensure_preview_namespace(copied_catalog, copied_derived)
    assert _namespace_row(copied_catalog) == row


def test_missing_lock_after_migration_fails_closed(tmp_path: Path) -> None:
    """AC1 boundary: without a readable lock nothing proves this is a migration.

    The self-heal requires BOTH halves of the binding to travel together. A
    copy whose lock was deleted (or is unreadable) carries a catalog binding
    with stale identities, but that is indistinguishable from a rewritten
    catalog -- so it must keep failing closed instead of silently re-binding.
    """

    source = tmp_path / "source"
    source_catalog, _ = _bind_new_root(source)
    _insert_catalog_row(source_catalog, "res-1", "pages/one.png")

    copied_catalog, copied_derived = _copy_root(source, tmp_path / "copy")
    (copied_derived / ".preview-lifecycle.lock").unlink()

    with pytest.raises(TypedResourceChannelError):
        _ensure_preview_namespace(copied_catalog, copied_derived)

    # Nothing was rewritten: the catalog still holds the original rows and the
    # rebuild left no NEW binding behind (restore may leave the empty lock file
    # it opened, but it must never be bound to the current identities).
    assert _catalog_rows(copied_catalog) == [("res-1", SCOPE_CLASS, "pages/one.png")]
    rebound = read_lock_binding_if_any(str(copied_derived))
    assert rebound is None


def test_rebind_fails_closed_on_non_canonical_namespace_table(tmp_path: Path) -> None:
    """AC1 negative: a foreign/corrupt binding table is not silently rewritten."""

    source = tmp_path / "source"
    source_catalog, _ = _bind_new_root(source)
    _insert_catalog_row(source_catalog, "res-1", "pages/one.png")
    copied_catalog, copied_derived = _copy_root(source, tmp_path / "copy")

    connection = sqlite3.connect(str(copied_catalog))
    try:
        connection.execute("DELETE FROM preview_namespace")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(TypedResourceChannelError):
        _ensure_preview_namespace(copied_catalog, copied_derived)

    # Nothing was rewritten: the catalog still holds the original rows.
    assert _catalog_rows(copied_catalog) == [("res-1", SCOPE_CLASS, "pages/one.png")]


def test_rebind_refuses_unbound_namespace(tmp_path: Path) -> None:
    """A catalog with no namespace row cannot be re-bound implicitly."""

    from infrastructure.resource_channel.catalog_store import rebind_namespace

    source = tmp_path / "source"
    source_catalog, source_derived = _bind_new_root(source)
    connection = sqlite3.connect(str(source_catalog))
    try:
        connection.execute("DELETE FROM preview_namespace")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(TypedResourceChannelError):
        rebind_namespace(source_catalog, source_derived, reason="unbound")
