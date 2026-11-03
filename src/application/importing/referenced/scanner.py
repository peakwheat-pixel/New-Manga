"""FEA-09 five-kind source scanner (single image / folder / ZIP / CBZ / PDF).

Reads only grant-provided paths with strict identity verification
(C-16 §2/§7.5), enforces the read/decompression budgets, classifies
encrypted and AES-ZIP sources (C-16 §3) and produces ordered entries with
content digests per C-15 §3.1.
"""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import stat
import zipfile

from application.importing.images.sorting import IMAGE_EXTENSIONS
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import (
    GrantFacts,
    ResolvedSourceRead,
    ScannedEntry,
    ScannedSource,
    folder_manifest_digest,
    pdf_page_identity_digest,
    sha256_hex,
    stable_sort_key,
    validate_locator,
)

#: Member/page formats accepted inside archive and folder sources. Members
#: outside this set are reported per-entry unsupported, not fatal for the
#: container (C-16 §4 ``unsupported_entries``).
ARCHIVE_IMAGE_EXTENSIONS = IMAGE_EXTENSIONS

#: PKZIP compression method 99 = WinZip AES (C-16 §3: typed unsupported).
_ZIP_METHOD_AES_99 = 99


def _reject_reparse(path: Path) -> None:
    """Refuse to traverse any symlink/junction component (SC-22/C-16 §7)."""
    probe = Path(path.anchor)
    for part in path.parts[1:]:
        probe /= part
        try:
            info = os.lstat(probe)
        except OSError as error:
            raise SourceImportError(
                "SOURCE_ENTRY_MISSING", "granted source path cannot be inspected"
            ) from error
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "granted source path crosses a reparse point"
            )


_verified_reader = None


def install_verified_reader(reader) -> None:
    """Inject the strict-read adapter (bootstrap owns infra wiring)."""
    global _verified_reader
    _verified_reader = reader


def read_verified_bytes(path: str, facts: GrantFacts, *, max_bytes: int) -> bytes:
    """Strict verified read of one granted file (H4/C-16 §2).

    The lease implementation lives in the infrastructure adapter and is
    injected by bootstrap; the application layer must not import
    infrastructure directly.
    """
    if _verified_reader is None:
        raise SourceImportError(
            "SOURCE_REGISTRY_UNAVAILABLE", "strict source reader is not installed"
        )
    return _verified_reader(path, facts, max_bytes)


def _stat_folder_entry(path: str, root: str) -> tuple[int, int, int]:
    """Volume/file identity + size for one folder member (pre-verify)."""
    target = Path(path)
    _reject_reparse(target)
    try:
        info = target.stat()
    except OSError as error:
        raise SourceImportError(
            "SOURCE_ENTRY_MISSING", "granted folder member is missing"
        ) from error
    root_norm = os.path.normcase(os.path.normpath(str(root)))
    target_norm = os.path.normcase(os.path.normpath(str(target)))
    if not target_norm.startswith(root_norm.rstrip("\\/") + os.sep):
        raise SourceImportError(
            "SOURCE_ACCESS_DENIED", "granted folder member escapes its root"
        )
    return int(info.st_dev), int(info.st_ino), int(info.st_size)


def scan_image(resolved: ResolvedSourceRead) -> ScannedSource:
    facts = resolved.container_facts
    if facts is None or not resolved.container_path:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "image grant is malformed")
    data = read_verified_bytes(
        resolved.container_path, facts, max_bytes=resolved.budget.max_bytes
    )
    name = Path(resolved.container_path).name
    if Path(name).suffix.lower() not in IMAGE_EXTENSIONS:
        return ScannedSource(
            grant_id=resolved.grant_id,
            registry_id=resolved.registry_id,
            generation=resolved.generation,
            source_kind="image",
            source_name=name,
            container_digest=None,
            status="unsupported",
            reason_code="SOURCE_FORMAT_UNSUPPORTED",
        )
    return ScannedSource(
        grant_id=resolved.grant_id,
        registry_id=resolved.registry_id,
        generation=resolved.generation,
        source_kind="image",
        source_name=name,
        container_digest=facts.sha256,
        status="ok",
        entries=[
            ScannedEntry(
                locator=name,
                ordinal=0,
                size_bytes=facts.size,
                content_digest=facts.sha256,
                content_digest_kind="encoded",
            )
        ],
    )


def scan_folder(resolved: ResolvedSourceRead) -> ScannedSource:
    root = resolved.folder_root
    if not root or not resolved.folder_entries:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "folder grant is malformed")
    if len(resolved.folder_entries) > resolved.budget.max_entries:
        raise SourceImportError(
            "SOURCE_BUDGET_EXCEEDED", "folder grant exceeds the entry budget"
        )
    root_path = Path(root)
    _reject_reparse(root_path)
    manifest: list[dict] = []
    members: list[tuple[str, GrantFacts, int, int, str]] = []
    for path, facts in resolved.folder_entries:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            validate_locator(rel)
        except ValueError as error:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "folder member name is unsafe"
            ) from error
        dev, ino, size = _stat_folder_entry(path, root)
        expected_volume = facts.volume_serial
        if os.name == "nt":
            dev &= 0xffffffff
            expected_volume &= 0xffffffff
        if dev != expected_volume or ino != facts.file_id or size != facts.size:
            raise SourceImportError(
                "FILE_IDENTITY_CHANGED", "granted folder member identity drifted"
            )
        if size > resolved.budget.max_bytes:
            raise SourceImportError(
                "SOURCE_BUDGET_EXCEEDED", "folder member exceeds the read budget"
            )
        manifest.append(
            {"rel_path": rel, "size_bytes": facts.size, "sha256": facts.sha256}
        )
        members.append((rel, facts, dev, ino, facts.sha256))
    digest = folder_manifest_digest(manifest)
    members.sort(key=lambda item: stable_sort_key(item[0], 0))
    entries: list[ScannedEntry] = []
    for ordinal, (rel, facts, _dev, _ino, member_digest) in enumerate(members):
        supported = Path(rel).suffix.lower() in IMAGE_EXTENSIONS
        entries.append(
            ScannedEntry(
                locator=rel,
                ordinal=ordinal,
                size_bytes=facts.size,
                content_digest=member_digest if supported else None,
                content_digest_kind="encoded",
            )
        )
    return ScannedSource(
        grant_id=resolved.grant_id,
        registry_id=resolved.registry_id,
        generation=resolved.generation,
        source_kind="folder",
        source_name=root_path.name,
        container_digest=digest,
        status="ok",
        entries=entries,
    )


def _zip_classify(info: zipfile.ZipInfo) -> str | None:
    """Return an entry classification code, or None when importable."""
    name = info.filename
    # zipfile already decodes cp437/utf-8 flagged names; validate the result.
    stripped = name[:-1] if name.endswith("/") else name
    if stripped:
        try:
            validate_locator(stripped)
        except ValueError as error:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "archive member name is unsafe"
            ) from error
    if info.compress_type == _ZIP_METHOD_AES_99:
        return "SOURCE_FORMAT_UNSUPPORTED"  # AES ZIP: typed unsupported (C-16 §3)
    return None


def ordered_archive_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    """Archive members in scan order: natural name sort, stable duplicates.

    Shared by the plan scan and the per-entry reads so an ``ordinal`` always
    resolves to the same member, including for duplicated names (occurrences
    keep their central-directory relative order — C-15 §3.2).
    """
    members = [info for info in archive.infolist() if not info.is_dir()]
    return sorted(members, key=lambda info: stable_sort_key(info.filename, 0))


def scan_archive(resolved: ResolvedSourceRead, *, password: bytes | None = None) -> ScannedSource:
    """ZIP/CBZ scan: member safety, budget, encryption classification.

    With ``password`` (ZipCrypto only; AES stays typed unsupported) member
    contents are decrypted to compute the per-entry digests that the
    structural encrypted preview could not provide (C-16 §3).
    """
    facts = resolved.container_facts
    if facts is None or not resolved.container_path:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "archive grant is malformed")
    data = read_verified_bytes(
        resolved.container_path, facts, max_bytes=resolved.budget.max_bytes
    )
    kind = resolved.source_kind
    name = Path(resolved.container_path).name
    container_digest = facts.sha256
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except (zipfile.BadZipFile, OSError, ValueError) as error:
        return ScannedSource(
            grant_id=resolved.grant_id,
            registry_id=resolved.registry_id,
            generation=resolved.generation,
            source_kind=kind,
            source_name=name,
            container_digest=container_digest,
            status="error",
            reason_code="SOURCE_FORMAT_UNSUPPORTED",
        )
    with archive:
        infos = archive.infolist()
        if len(infos) > resolved.budget.max_entries:
            raise SourceImportError(
                "SOURCE_BUDGET_EXCEEDED", "archive exceeds the entry budget"
            )
        encrypted_members = 0
        aes_members = 0
        total_uncompressed = 0
        classified: list[tuple[zipfile.ZipInfo, str | None]] = []
        for info in infos:
            if info.is_dir():
                continue
            code = _zip_classify(info)
            if code == "SOURCE_FORMAT_UNSUPPORTED":
                aes_members += 1
            if info.flag_bits & 0x1:
                encrypted_members += 1
            total_uncompressed += info.file_size
            classified.append((info, code))
        if aes_members and aes_members == sum(1 for _ in classified):
            # Every member is AES — the whole source is typed unsupported.
            return ScannedSource(
                grant_id=resolved.grant_id,
                registry_id=resolved.registry_id,
                generation=resolved.generation,
                source_kind=kind,
                source_name=name,
                container_digest=container_digest,
                status="unsupported",
                reason_code="SOURCE_FORMAT_UNSUPPORTED",
            )
        if total_uncompressed > resolved.budget.max_decode_bytes:
            raise SourceImportError(
                "SOURCE_BUDGET_EXCEEDED", "archive decompression budget exceeded"
            )
        if encrypted_members and password is None:
            # ZipCrypto sources plan as encrypted: structural metadata only
            # (member names/ordinals); no content digests before the password
            # is confirmed at start time (C-16 §3).
            ordered = ordered_archive_members(archive)
            entries = [
                ScannedEntry(
                    locator=info.filename,
                    ordinal=ordinal,
                    size_bytes=info.file_size,
                    content_digest=None,
                    content_digest_kind="encoded",
                    encrypted=True,
                )
                for ordinal, info in enumerate(ordered)
            ]
            return ScannedSource(
                grant_id=resolved.grant_id,
                registry_id=resolved.registry_id,
                generation=resolved.generation,
                source_kind=kind,
                source_name=name,
                container_digest=container_digest,
                status="encrypted",
                entries=entries,
                structural_only=True,
            )
        ordered = ordered_archive_members(archive)
        entries: list[ScannedEntry] = []
        for ordinal, info in enumerate(ordered):
            supported = (
                Path(info.filename).suffix.lower() in ARCHIVE_IMAGE_EXTENSIONS
            )
            if supported:
                try:
                    payload = archive.read(info, pwd=password)
                except (zipfile.BadZipFile, RuntimeError, OSError, ValueError) as error:
                    if password is not None:
                        # A confirmed-password rescan failing to decrypt is a
                        # password failure, not an unsupported member.
                        raise SourceImportError(
                            "SOURCE_PASSWORD_INVALID",
                            "archive password was rejected",
                        ) from error
                    entries.append(ScannedEntry(
                        locator=info.filename, ordinal=ordinal,
                        size_bytes=info.file_size, content_digest=None,
                        content_digest_kind="encoded",
                    ))
                    continue
                if len(payload) > resolved.budget.max_decode_bytes:
                    raise SourceImportError(
                        "SOURCE_BUDGET_EXCEEDED",
                        "archive member decompression budget exceeded",
                    )
                entries.append(ScannedEntry(
                    locator=info.filename, ordinal=ordinal,
                    size_bytes=info.file_size,
                    content_digest=sha256_hex(payload),
                    content_digest_kind="encoded",
                ))
            else:
                entries.append(ScannedEntry(
                    locator=info.filename, ordinal=ordinal,
                    size_bytes=info.file_size, content_digest=None,
                    content_digest_kind="encoded",
                ))
    return ScannedSource(
        grant_id=resolved.grant_id,
        registry_id=resolved.registry_id,
        generation=resolved.generation,
        source_kind=kind,
        source_name=name,
        container_digest=container_digest,
        status="ok",
        entries=entries,
    )


def scan_pdf(resolved: ResolvedSourceRead, *, pdf_open, password: bytes | None = None) -> ScannedSource:
    """PDF scan: page-identity entries; encrypted PDFs plan structurally.

    ``pdf_open(data, password)`` returns a handle exposing ``page_count`` and
    ``page_size(index)``; a password-protected document raises
    ``SourceImportError("SOURCE_PASSWORD_REQUIRED")`` for the empty password
    (the planner never decrypts — C-16 §3).
    """
    facts = resolved.container_facts
    if facts is None or not resolved.container_path:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "pdf grant is malformed")
    data = read_verified_bytes(
        resolved.container_path, facts, max_bytes=resolved.budget.max_bytes
    )
    name = Path(resolved.container_path).name
    container_digest = facts.sha256
    try:
        handle = pdf_open(data, password)
    except SourceImportError as error:
        if error.code == "SOURCE_PASSWORD_REQUIRED" and password is None:
            return ScannedSource(
                grant_id=resolved.grant_id,
                registry_id=resolved.registry_id,
                generation=resolved.generation,
                source_kind="pdf",
                source_name=name,
                container_digest=container_digest,
                status="encrypted",
                structural_only=True,
            )
        raise
    try:
        page_count = handle.page_count
        entries = [
            ScannedEntry(
                locator=str(page + 1),
                ordinal=page,
                size_bytes=facts.size,
                content_digest=pdf_page_identity_digest(container_digest, page),
                content_digest_kind="page-identity",
            )
            for page in range(page_count)
        ]
    finally:
        handle.close()
    return ScannedSource(
        grant_id=resolved.grant_id,
        registry_id=resolved.registry_id,
        generation=resolved.generation,
        source_kind="pdf",
        source_name=name,
        container_digest=container_digest,
        status="ok",
        entries=entries,
    )


def scan_source(
    resolved: ResolvedSourceRead,
    *,
    pdf_open,
    password: bytes | None = None,
) -> ScannedSource:
    if resolved.source_kind == "image":
        return scan_image(resolved)
    if resolved.source_kind == "folder":
        return scan_folder(resolved)
    if resolved.source_kind in {"zip", "cbz"}:
        return scan_archive(resolved, password=password)
    if resolved.source_kind == "pdf":
        return scan_pdf(resolved, pdf_open=pdf_open, password=password)
    raise SourceImportError(
        "SOURCE_FORMAT_UNSUPPORTED", "source kind is not supported"
    )
