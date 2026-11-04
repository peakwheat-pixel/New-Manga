"""FEA-09 Phase B test support: fake grant access + fixture builders.

Shared by the scanner/flow/password tests. Real files on tmp_path, real
Pillow decoding, real pypdfium2 probing; only the grant channel is faked
(the production registry is wired in Phase C and covered separately).
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from application.importing.referenced.model import (  # noqa: E402
    GrantFacts,
    ResolvedSourceRead,
    SourceReadBudget,
)
from application.importing.referenced.errors import SourceImportError  # noqa: E402
from application.importing.referenced.planner import ReferencedImportPlanner  # noqa: E402
from application.importing.referenced.runtime import ReferencedImportRuntime  # noqa: E402

DEFAULT_BUDGET = SourceReadBudget(
    max_bytes=8 * 1024 * 1024,
    max_decode_bytes=8 * 1024 * 1024,
    max_entries=1000,
)


from application.importing.referenced.identity import normalize_identity


def capture_facts(path: str | Path) -> GrantFacts:
    info = os.stat(path)
    data = Path(path).read_bytes()
    return GrantFacts(
        volume_serial=normalize_identity(info.st_dev, info.st_ino)[0],
        file_id=normalize_identity(info.st_dev, info.st_ino)[1],
        size=int(info.st_size),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def png_bytes(width: int = 4, height: int = 3, color=(255, 0, 0)) -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, format="PNG")
    return buffer.getvalue()


def write_zip(path: str | Path, members: list[tuple[str, bytes]]) -> Path:
    import zipfile

    target = Path(path)
    with zipfile.ZipFile(target, "w") as archive:
        for name, data in members:
            archive.writestr(name, data)
    return target


class FakeSourceReadAccess:
    """In-memory grant registry honouring the SourceReadAccess port."""

    def __init__(self) -> None:
        self._grants: dict[str, ResolvedSourceRead] = {}
        self._grant_sources: dict[str, str] = {}
        self._bound: dict[str, dict] = {}
        self._revoked: set[str] = set()
        self._expired: set[str] = set()
        self._fail_verify: dict[str, str] = {}
        self.verify_calls: list[str] = []

    def add_file(self, grant_id: str, kind: str, path: str | Path, *,
                 generation: int = 1, registry_id: str = "reg-1",
                 budget: SourceReadBudget | None = None,
                 source_id: str | None = None) -> ResolvedSourceRead:
        facts = capture_facts(path)
        resolved = ResolvedSourceRead(
            grant_id=grant_id,
            registry_id=registry_id,
            generation=generation,
            source_kind=kind,
            budget=budget or DEFAULT_BUDGET,
            expires_at=1e12,
            container_path=str(path),
            container_facts=facts,
        )
        self._grants[grant_id] = resolved
        if source_id is not None:
            self._grant_sources[grant_id] = source_id
        return resolved

    def add_folder(self, grant_id: str, root: str | Path,
                   members: list[str], *, generation: int = 1,
                   registry_id: str = "reg-1",
                   budget: SourceReadBudget | None = None,
                   source_id: str | None = None) -> ResolvedSourceRead:
        resolved = ResolvedSourceRead(
            grant_id=grant_id,
            registry_id=registry_id,
            generation=generation,
            source_kind="folder",
            budget=budget or DEFAULT_BUDGET,
            expires_at=1e12,
            folder_root=str(root),
            folder_entries=tuple(
                (str(member), capture_facts(member)) for member in members
            ),
        )
        self._grants[grant_id] = resolved
        if source_id is not None:
            self._grant_sources[grant_id] = source_id
        return resolved

    def resolve(self, grant_id: str) -> ResolvedSourceRead:
        resolved = self._grants.get(grant_id)
        if resolved is None:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "grant is not registered"
            )
        if grant_id in self._revoked:
            raise SourceImportError(
                "SOURCE_GRANT_REVOKED", "grant was revoked"
            )
        if grant_id in self._expired:
            raise SourceImportError(
                "SOURCE_GRANT_EXPIRED", "grant expired"
            )
        return resolved

    def verify_before_commit(self, grant_id: str) -> None:
        self.verify_calls.append(grant_id)
        self.resolve(grant_id)
        code = self._fail_verify.get(grant_id)
        if code is not None:
            raise SourceImportError(code, "grant verification failed")

    def bind_imported_entry(self, grant_id, source_id, version_id, entry_id):
        self._bound.setdefault(
            grant_id, {"source_id": source_id, "version_id": version_id, "entry_ids": set()}
        )["entry_ids"].add(entry_id)
        self._bound[grant_id]["source_id"] = source_id
        self._bound[grant_id]["version_id"] = version_id

    def find_bound_for_source(self, source_id, version_id, entry_id):
        matching = [
            grant_id for grant_id, bound in self._bound.items()
            if bound["source_id"] == source_id
            and bound["version_id"] == version_id
            and entry_id in bound["entry_ids"]
        ]
        if not matching:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "no active grant is bound to this page binding"
            )
        grant_id = sorted(matching)[-1]
        return grant_id, self.resolve(grant_id)

    def find_for_source(self, source_id: str) -> tuple[str, ResolvedSourceRead]:
        matching = [
            grant_id for grant_id, bound in self._grant_sources.items()
            if bound == source_id
        ]
        if not matching:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "no active grant covers this source"
            )
        grant_id = sorted(matching)[-1]
        return grant_id, self.resolve(grant_id)

    def find_for_identity(self, *, content_digest, volume_serial, file_id):
        matching = []
        for grant_id, resolved in self._grants.items():
            facts = resolved.container_facts
            if (
                facts is not None
                and facts.sha256 == content_digest
                and facts.volume_serial == volume_serial
                and facts.file_id == file_id
            ):
                matching.append(grant_id)
        if not matching:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "no active grant covers this identity"
            )
        grant_id = sorted(matching)[-1]
        return grant_id, self.resolve(grant_id)

    def revoke_all_for_session(self) -> int:
        count = len(self._grants)
        self._revoked.update(self._grants)
        return count

    # -- test controls -----------------------------------------------------
    def revoke(self, grant_id: str) -> None:
        self._revoked.add(grant_id)

    def expire(self, grant_id: str) -> None:
        self._expired.add(grant_id)

    def fail_verify(self, grant_id: str, code: str) -> None:
        self._fail_verify[grant_id] = code


class HookDecoder:
    """Pillow decoder with a per-decode hook (cancel/failure injection)."""

    def __init__(self, hook=None) -> None:
        from infrastructure.importing import PillowImageDecoder

        self._inner = PillowImageDecoder()
        self._hook = hook
        self.calls: list[str] = []

    def decode(self, data: bytes):
        self.calls.append(data[:16].hex())
        if self._hook is not None:
            self._hook(len(self.calls), data)
        return self._inner.decode(data)


def build_pdf_open():
    from application.importing.referenced.pdf_probe import PdfiumSourceInspector

    return PdfiumSourceInspector().open


def build_planner(repo, access, *, pdf_open=None):
    return ReferencedImportPlanner(
        access=access,
        repository=repo,
        project_of_chapter=_project_of_chapter(repo),
        pdf_open=pdf_open or build_pdf_open(),
    )


def build_runtime(repo, access, *, planner=None, decoder=None,
                  pdf_open=None, secret_reader=None, enabled=None):
    from application.importing.referenced.secrets import read_secret

    return ReferencedImportRuntime(
        repository=repo,
        access=access,
        planner=planner or build_planner(repo, access, pdf_open=pdf_open),
        project_of_chapter=_project_of_chapter(repo),
        image_decoder=decoder or HookDecoder(),
        pdf_open=pdf_open or build_pdf_open(),
        secret_reader=secret_reader or read_secret,
        enabled=enabled,
    )


def _project_of_chapter(repo):
    def project_of_chapter(chapter_id: str):
        chapter = repo.get_chapter(chapter_id)
        if chapter is None:
            return None
        return getattr(chapter, "book_id", None) or (
            chapter["book_id"] if isinstance(chapter, dict) else None
        )

    return project_of_chapter


def add_managed_page(conn, page_id: str, chapter_id: str = "c1",
                     *, order: int = 1, digest: str | None = None,
                     soft_deleted: bool = False) -> str:
    """Direct-SQL managed page with complete import columns (C-15 §4.3)."""
    import sqlite3

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    digest = digest or (page_id.encode("utf-8").hex() * 4)[:64]
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, deleted_at,"
        " source_mode, integrity_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 4, 3, ?, ?, 'managed', 'complete')",
        (page_id, chapter_id, order, now, now, f"{page_id}.png", order, digest,
         10, f"managed/{page_id}.png", now if soft_deleted else None),
    )
    conn.commit()
    return digest
