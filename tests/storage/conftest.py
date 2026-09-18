"""Shared fixtures for storage tests.

The suite imports application packages directly from ``src`` so the task
command ``python -m pytest tests/storage`` works without external env setup.
"""

from __future__ import annotations

import hashlib
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.repositories.artifacts import (  # noqa: E402
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)

LATEST_KNOWN = default_migrations()[-1].schema_version


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def new_id() -> str:
    return uuid.uuid4().hex


@pytest.fixture()
def storage_root(tmp_path: Path) -> Path:
    root = tmp_path / "storage"
    storage = ManagedFileStorage(root)
    storage.ensure_layout()
    return root


@pytest.fixture()
def db_conn(tmp_path: Path):
    conn, opened = open_database(
        tmp_path / "app.db", latest_known_schema_version=LATEST_KNOWN
    )
    runner = MigrationRunner(conn, default_migrations())
    runner.apply_pending()
    yield conn
    conn.close()


@pytest.fixture()
def repo(db_conn, storage_root: Path):
    return SqliteArtifactRepository(db_conn, ManagedFileStorage(storage_root))


@pytest.fixture()
def seeded_page(db_conn) -> dict[str, str]:
    """Insert the minimal book → chapter → page chain used by artifacts."""
    now = utc_now()
    ids = {"book_id": new_id(), "chapter_id": new_id(), "page_id": new_id()}
    with db_conn:
        db_conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (ids["book_id"], "Un livre", now, now),
        )
        db_conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (ids["chapter_id"], ids["book_id"], "Chapitre 1", now, now),
        )
        db_conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, ?, 0, ?, ?)",
            (ids["page_id"], ids["chapter_id"], now, now),
        )
    return ids


@pytest.fixture()
def make_commit(seeded_page):
    """Factory building PendingArtifactCommit payloads."""

    def _factory(
        artifact_id: str,
        content: bytes,
        *,
        expected_current: str | None,
        mime_type: str = "image/png",
        expected_sha256: str | None = None,
    ) -> PendingArtifactCommit:
        return PendingArtifactCommit(
            artifact_id=artifact_id,
            content_provider=ContentProvider(payload=content),
            mime_type=mime_type,
            expected_current_revision_id=expected_current,
            expected_sha256=expected_sha256,
            file_suffix=".png",
        )

    return _factory


@pytest.fixture()
def artifact_id(repo, seeded_page) -> str:
    return repo.create_artifact(
        NewArtifact(
            book_id=seeded_page["book_id"],
            chapter_id=seeded_page["chapter_id"],
            page_id=seeded_page["page_id"],
            artifact_type=ArtifactType.TRANSLATED,
        )
    ).artifact_id


NOW = "2026-09-19T02:00:00+00:00"


@pytest.fixture()
def trash_workspace(tmp_path: Path):
    """Real SQLite + real ManagedFileStorage trash construction (the
    TASK-021 subset shape), for the TASK-053 R-03/R-04 tests."""

    from application.maintenance import TrashService
    from application.maintenance.trash import _JsonTrashManifest
    from domain.pages.entities import Page
    from infrastructure.sqlite.library import SqliteLibraryRepository

    conn, _opened = open_database(
        tmp_path / "library.db", latest_known_schema_version=LATEST_KNOWN
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    repository = SqliteLibraryRepository(conn)

    user_source = tmp_path / "user-side" / "original-art.tiff"
    user_source.parent.mkdir(parents=True, exist_ok=True)
    user_source.write_bytes(b"USER SOURCE BYTES")

    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 'Book', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1', 'book-1', 'Chapter', ?, ?)",
            (NOW, NOW),
        )

    def make_page(page_id: str, payload: bytes) -> Page:
        relative = f"books/book-1/chapters/chapter-1/original/{page_id}.png"
        managed_file = tmp_path / "managed" / Path(relative)
        managed_file.parent.mkdir(parents=True, exist_ok=True)
        managed_file.write_bytes(payload)
        page = Page(
            page_id=page_id,
            chapter_id="chapter-1",
            source_filename=f"{page_id}.png",
            source_order=int(page_id[-1]),
            sort_order=int(page_id[-1]),
            source_hash=hashlib.sha256(payload).hexdigest(),
            source_size_bytes=len(payload),
            width=4,
            height=3,
            managed_original_ref=relative,
        )
        repository.add_page(page)
        return page

    manifest = _JsonTrashManifest(tmp_path / "managed" / "trash-manifest.json")
    service = TrashService(repository, storage, manifest)

    def read_pending() -> list[dict]:
        return manifest.read_manifest().get("pending_purges", [])

    yield {
        "conn": conn,
        "repository": repository,
        "storage": storage,
        "service": service,
        "make_page": make_page,
        "user_source": user_source,
        "managed": tmp_path / "managed",
        "with_remover": lambda remover: TrashService(repository, remover, manifest),
        "read_pending": read_pending,
        "live_page_ids": lambda: {
            page.page_id for page in repository.list_pages("chapter-1")
        },
    }
    conn.close()
