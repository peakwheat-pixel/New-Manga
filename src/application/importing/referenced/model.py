"""FEA-09 referenced-import data model (C-15 §3 identity/order + C-16 wire shapes).

Locator safety, natural ordering keys and the shared dataclasses used by the
scanner, planner and operation runtime. Nothing here touches the database or
the filesystem — those live in ``scanner``/``runtime``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re

#: C-15 §3.1 locator safety envelope.
_LOCATOR_MAX_CHARS = 4096
_FORBIDDEN_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_NUMBER_SPLIT = re.compile(r"(\d+)")

#: Decoder identity written into source_entries for every imported entry.
#: The scan-side digests are decoder independent (C-15 §3.1); the decoder
#: observation columns are filled by the runtime at commit time.
DECODER_NAME = "referenced-import/1"


class LocatorError(ValueError):
    """A member/relative locator violates the C-15 §3.1 safety rules."""


def validate_locator(locator: str) -> str:
    """Validate a container-relative locator (C-15 §3.1).

    Rejects absolute paths, drive letters, UNC, ``..``/``.`` segments, NUL
    and control characters, backslashes and oversized names. Folder sources
    use ``/``-separated relative paths; archive members use their member
    name; PDF pages use their decimal page number.
    """
    if not isinstance(locator, str) or not locator:
        raise LocatorError("locator must be a non-empty string")
    if len(locator) > _LOCATOR_MAX_CHARS:
        raise LocatorError("locator exceeds the 4096 character limit")
    if "\\" in locator:
        raise LocatorError("locator must use '/' separators")
    if locator.startswith("/") or _DRIVE_RE.match(locator) or locator.startswith("//"):
        raise LocatorError("locator must be relative")
    if locator.startswith("~") or "\\\\" in locator:
        raise LocatorError("locator must not reference network paths")
    if _FORBIDDEN_CONTROL.search(locator):
        raise LocatorError("locator must not contain control characters")
    if locator in {".", ".."} or locator.endswith("/.") or locator.endswith("/.."):
        raise LocatorError("locator must not be a relative marker")
    for part in locator.split("/"):
        if part in {"", ".", ".."}:
            raise LocatorError("locator segments must not be empty or relative markers")
        if part.endswith(" ") or part.endswith("."):
            # Windows cannot round-trip these names; treat as unsafe members.
            raise LocatorError("locator segment has an unsafe trailing character")
    return locator


def natural_key_string(name: str) -> str:
    """Order-preserving string form of the natural (numeric-aware) sort key.

    Digits are zero padded to a fixed width so ``page2 < page10`` holds in
    plain string order and the key can be stored as ``stable_sort_key``
    (C-15 §2.5 requires a version-unique TEXT sort key). Case is folded the
    same way :func:`application.importing.images.sorting.natural_sort_key`
    folds it.
    """
    parts = _NUMBER_SPLIT.split(name)
    pieces: list[str] = []
    for index, part in enumerate(parts):
        if index % 2:  # digit capture group
            pieces.append(f"\x01N{int(part):020d}")
        elif part:
            pieces.append(f"\x02S{part.lower()}")
    return "".join(pieces) or "\x00"


def stable_sort_key(name: str, ordinal: int) -> str:
    """Version-unique stable sort key: natural key + ordinal tie-break.

    Duplicate member names keep independent entries (C-15 §3.2); the ordinal
    suffix guarantees uniqueness without folding occurrences together.
    """
    return f"{natural_key_string(name)}\x00{ordinal:012d}"


def canonical_json(value) -> str:
    """Compact sorted-key UTF-8 JSON (the wire/grant canonical form)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def folder_manifest_digest(entries: list[dict]) -> str:
    """folder-manifest/1 content digest (C-15 §3.1).

    ``entries`` items are ``{"rel_path", "size_bytes", "sha256"}`` dicts; the
    list is sorted by ``rel_path`` before hashing.
    """
    ordered = sorted(entries, key=lambda item: item["rel_path"])
    payload = {
        "format": "folder-manifest/1",
        "entries": [
            {
                "rel_path": item["rel_path"],
                "size_bytes": item["size_bytes"],
                "sha256": item["sha256"],
            }
            for item in ordered
        ],
    }
    return sha256_hex(canonical_json(payload).encode("utf-8"))


def pdf_page_identity_digest(container_digest: str, page_ordinal: int) -> str:
    """pdf-page/1 identity digest (C-15 §3.1): decoder/scale independent."""
    material = b"pdf-page/1\x00" + container_digest.encode("ascii") + b"\x00" + str(
        page_ordinal
    ).encode("ascii")
    return hashlib.sha256(material).hexdigest()


@dataclass(frozen=True)
class GrantFacts:
    """Host-collected physical identity facts (C-16 §2 ``facts``)."""

    volume_serial: int
    file_id: int
    size: int
    sha256: str


@dataclass(frozen=True)
class SourceReadBudget:
    max_bytes: int
    max_decode_bytes: int
    max_entries: int


@dataclass(frozen=True)
class ResolvedSourceRead:
    """One resolved source-read grant: the orchestrator's view of a source.

    ``container_path``/``container_facts`` are set for single-file sources
    (image/zip/cbz/pdf); ``folder_root``/``folder_entries`` for folder
    sources. Paths come from the grant only — never from UI/receipt payloads
    (C-16 §7.5).
    """

    grant_id: str
    registry_id: str
    generation: int
    source_kind: str  # image|folder|zip|cbz|pdf
    budget: SourceReadBudget
    expires_at: float
    container_path: str | None = None
    container_facts: GrantFacts | None = None
    folder_root: str | None = None
    folder_entries: tuple[tuple[str, GrantFacts], ...] = ()


@dataclass
class ScannedEntry:
    """One planned source entry (pre-dedup, pre-decode)."""

    locator: str
    ordinal: int
    size_bytes: int
    content_digest: str | None  # None for encrypted previews
    content_digest_kind: str  # 'encoded' | 'page-identity'
    encrypted: bool = False


@dataclass
class ScannedSource:
    """Scan outcome for one grant."""

    grant_id: str
    registry_id: str
    generation: int
    source_kind: str
    source_name: str
    container_digest: str | None  # None when the container cannot be read at all
    status: str  # ok | unsupported | encrypted | error
    reason_code: str | None = None
    entries: list[ScannedEntry] = field(default_factory=list)
    # Present only for non-encrypted sources: entry digests verified against
    # grant facts. Encrypted sources carry locator/ordinal only (C-16 §3).
    structural_only: bool = False  # True for encrypted previews


@dataclass
class PlannedPage:
    """One page unit inside a plan (used by the runtime)."""

    locator: str
    ordinal: int
    size_bytes: int
    content_digest: str | None
    content_digest_kind: str
    already_referenced: bool = False
    unsupported: bool = False
