"""FEA-11 real-IPC seed: one isolated v8 library with a referenced page.

Opt-in support for ``Fea11SourceIpcTests`` (``NEWMANGA_FEA11_IPC=1``). The
script writes two zip containers under an isolated workspace directory, opens
the library through the production migration chain (v1..v8), seeds one
referenced page bound to the first container, and drops a receipt JSON. It
never touches real user data.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "fea11"))

from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
import conftest as fea11_conftest  # noqa: E402


def _png(color: tuple[int, int, int]) -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGBA", (4, 3), color + (255,)).save(buffer, format="PNG")
    return buffer.getvalue()


def _zip(path: Path, pages: list[bytes]) -> str:
    with zipfile.ZipFile(path, "w") as archive:
        for index, data in enumerate(pages, start=1):
            archive.writestr(f"{index:03d}.png", data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()

    root = args.data_root.resolve()
    fixture_root = (REPO.parent / f"{REPO.name}.workspace" / "FEA-11" / "fixtures").resolve()
    if not root.is_relative_to(fixture_root) or args.db.resolve() != root / "library.db":
        parser.error("only an isolated FEA-11 fixture library.db is allowed")
    root.mkdir(parents=True, exist_ok=True)

    old_pages = [_png((255, 0, 0)), _png((0, 255, 0))]
    new_pages = [_png((0, 0, 255)), _png((0, 255, 0))]
    old_zip = root / "source-v1.zip"
    new_zip = root / "source-v2.zip"
    old_digest = _zip(old_zip, old_pages)
    new_digest = _zip(new_zip, new_pages)
    old_entries = [
        ("se-001", "001.png", hashlib.sha256(old_pages[0]).hexdigest()),
        ("se-002", "002.png", hashlib.sha256(old_pages[1]).hexdigest()),
    ]

    conn = sqlite3.connect(args.db, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(conn, default_migrations()).apply_pending()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'FEA-11 IPC', ?, ?)", (fea11_conftest.NOW, fea11_conftest.NOW))
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)", (fea11_conftest.NOW, fea11_conftest.NOW))
    conn.commit()
    fea11_conftest.add_source_tree(
        conn, source_id="s1", version_id="sv1", digest=old_digest,
        entries=list(old_entries), legacy_v7_evidence=False,
    )
    fea11_conftest.add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="se-001", digest=old_entries[0][2],
    )
    row = conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations"
    ).fetchone()
    schema_version = int(row[0]) if row else 0
    conn.close()

    receipt = {
        "data_root": str(root),
        "db": str(args.db),
        "schema_version": schema_version,
        "page_id": "p1",
        "source_id": "s1",
        "version_id": "sv1",
        "entry_id": "se-001",
        "old_zip": str(old_zip),
        "new_zip": str(new_zip),
        "old_digest": old_digest,
        "new_digest": new_digest,
        "old_page_digest": old_entries[0][2],
    }
    (root / "ipc-seed-receipt.json").write_text(
        json.dumps(receipt, indent=1), encoding="utf-8")
    print("FEA11_IPC_SEED_OK " + json.dumps({"schema_version": schema_version}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
