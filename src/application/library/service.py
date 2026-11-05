"""Bookshelf use cases: Book/Chapter CRUD, tags, favorite/archive.

Favorite and archive are plain system flags on Book (D03 §3.3) — they never
create or consume Tag rows (AC-LIB-003). Tag deletion unlinks associations
only; books survive (AC-LIB-002, D04 §6).
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid

from application.library.errors import (
    BookNotFound,
    ChapterNotFound,
    DuplicateTagName,
    TagNotFound,
)
from application.library.ports import LibraryRepository
from domain.books.entities import Book, Chapter, ChapterType, ReadingDirection, Tag


def _new_id() -> str:
    return uuid.uuid4().hex


class LibraryService:
    def __init__(self, repository: LibraryRepository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # books (AC-LIB-001)
    # ------------------------------------------------------------------

    def create_book(
        self,
        title: str,
        *,
        original_title: str = "",
        author: str = "",
        publisher: str = "",
        series_title: str = "",
        description: str = "",
        source_language: str = "",
        target_language: str = "",
        source_url: str = "",
        notes: str = "",
        default_chapter_type: ChapterType = ChapterType.PAGED,
        default_reading_direction: ReadingDirection = ReadingDirection.RTL,
    ) -> Book:
        book = Book(
            book_id=_new_id(),
            title=title,
            original_title=original_title,
            author=author,
            publisher=publisher,
            series_title=series_title,
            description=description,
            source_language=source_language,
            target_language=target_language,
            source_url=source_url,
            notes=notes,
            default_chapter_type=ChapterType(default_chapter_type),
            default_reading_direction=ReadingDirection(default_reading_direction),
        )
        self._repo.add_book(book)
        return book

    def get_book(self, book_id: str) -> Book:
        book = self._repo.get_book(book_id)
        if book is None or book.deleted:
            raise BookNotFound(book_id)
        return book

    def list_books(self) -> list[Book]:
        """Shelf contents: every book not soft-deleted (archived included,
        the UI filters views)."""
        return [book for book in self._repo.list_books() if not book.deleted]

    def list_deleted_books(self) -> list[Book]:
        """Recycle bin contents: every book that is soft-deleted."""
        return [book for book in self._repo.list_books() if book.deleted]

    def list_recycle_bin_books(self) -> list[Book]:
        """Alias for list_deleted_books."""
        return self.list_deleted_books()

    def count_all_books(self) -> int:
        """Total existing books in the repository (active + soft-deleted)."""
        return len(self._repo.list_books())

    def update_book(self, book_id: str, **changes: str) -> Book:
        book = self.get_book(book_id)
        book.apply_edit(**changes)
        self._repo.update_book(book)
        return book

    def delete_book(self, book_id: str) -> None:
        book = self.get_book(book_id)
        book.soft_delete()
        self._repo.update_book(book)

    def set_favorite(self, book_id: str, favorite: bool) -> Book:
        book = self.get_book(book_id)
        book.set_favorite(favorite)
        self._repo.update_book(book)
        return book

    def set_archived(self, book_id: str, archived: bool) -> Book:
        book = self.get_book(book_id)
        book.set_archived(archived)
        self._repo.update_book(book)
        return book

    # ------------------------------------------------------------------
    # chapters (AC-CH-001..004)
    # ------------------------------------------------------------------

    def create_chapter(
        self,
        book_id: str,
        title: str,
        *,
        chapter_number: str = "",
        subtitle: str = "",
        chapter_type: ChapterType | None = None,
        reading_direction: ReadingDirection | None = None,
        notes: str = "",
    ) -> Chapter:
        book = self.get_book(book_id)
        resolved_type = ChapterType(chapter_type) if chapter_type else book.default_chapter_type
        if reading_direction is not None:
            direction = ReadingDirection(reading_direction)
        elif resolved_type is ChapterType.WEBTOON:
            direction = ReadingDirection.VERTICAL
        elif book.default_reading_direction is not ReadingDirection.VERTICAL:
            direction = book.default_reading_direction
        else:
            direction = ReadingDirection.RTL

        existing = [
            chapter for chapter in self._repo.list_chapters(book_id) if not chapter.deleted
        ]
        next_order = (
            max((chapter.import_order for chapter in existing), default=0) + 1
        )
        chapter = Chapter(
            chapter_id=_new_id(),
            book_id=book_id,
            title=title,
            chapter_number=chapter_number,
            subtitle=subtitle,
            import_order=next_order,
            sort_order=next_order,
            chapter_type=resolved_type,
            reading_direction=direction,
            notes=notes,
        )
        self._repo.add_chapter(chapter)
        return chapter

    def get_chapter(self, chapter_id: str) -> Chapter:
        chapter = self._repo.get_chapter(chapter_id)
        if chapter is None or chapter.deleted:
            raise ChapterNotFound(chapter_id)
        return chapter

    def list_chapters(self, book_id: str) -> list[Chapter]:
        self.get_book(book_id)  # existence + not deleted
        chapters = [
            chapter for chapter in self._repo.list_chapters(book_id) if not chapter.deleted
        ]
        return sorted(chapters, key=lambda chapter: chapter.sort_order)

    def update_chapter(self, chapter_id: str, **changes: str) -> Chapter:
        chapter = self.get_chapter(chapter_id)
        chapter.apply_edit(**changes)
        self._repo.update_chapter(chapter)
        return chapter

    def delete_chapter(self, chapter_id: str) -> None:
        chapter = self.get_chapter(chapter_id)
        chapter.soft_delete()
        self._repo.update_chapter(chapter)

    def reorder_chapters(self, book_id: str, ordered_chapter_ids: list[str]) -> list[Chapter]:
        """Apply a user ordering; import_order values stay frozen (D03 §5.3)."""
        chapters = {chapter.chapter_id: chapter for chapter in self.list_chapters(book_id)}
        missing = [cid for cid in ordered_chapter_ids if cid not in chapters]
        if missing:
            raise ChapterNotFound(missing[0])
        reordered = []
        for position, chapter_id in enumerate(ordered_chapter_ids, start=1):
            chapter = chapters[chapter_id]
            chapter.reorder(position)
            self._repo.update_chapter(chapter)
            reordered.append(chapter)
        return reordered

    # ------------------------------------------------------------------
    # tags (AC-LIB-002)
    # ------------------------------------------------------------------

    def create_tag(self, name: str) -> Tag:
        if self._repo.find_tag_by_name(name) is not None:
            raise DuplicateTagName(name)
        tag = Tag(tag_id=_new_id(), name=name)
        self._repo.add_tag(tag)
        return tag

    def rename_tag(self, tag_id: str, new_name: str) -> Tag:
        tag = self._require_tag(tag_id)
        clash = self._repo.find_tag_by_name(new_name)
        if clash is not None and clash.tag_id != tag_id:
            raise DuplicateTagName(new_name)
        tag.rename(new_name)
        self._repo.update_tag(tag)
        return tag

    def delete_tag(self, tag_id: str) -> None:
        self._require_tag(tag_id)
        # Associations are removed with the tag; books are untouched
        # (AC-LIB-002: deleting a tag never deletes a book).
        self._repo.delete_tag(tag_id)

    def list_tags(self) -> list[Tag]:
        return self._repo.list_tags()

    def add_tag_to_book(self, book_id: str, tag_id: str) -> None:
        self.get_book(book_id)
        self._require_tag(tag_id)
        self._repo.add_book_tag(book_id, tag_id)

    def remove_tag_from_book(self, book_id: str, tag_id: str) -> None:
        self.get_book(book_id)
        self._require_tag(tag_id)
        self._repo.remove_book_tag(book_id, tag_id)

    def tags_of_book(self, book_id: str) -> list[Tag]:
        self.get_book(book_id)
        return self._repo.list_tags_of_book(book_id)

    def _require_tag(self, tag_id: str) -> Tag:
        tag = self._repo.get_tag(tag_id)
        if tag is None:
            raise TagNotFound(tag_id)
        return tag


# ----------------------------------------------------------------------
# FEA-12 (C-04b §2.1 / M2-C1 §5.13): deletion-preview inventory digest
# ----------------------------------------------------------------------
#
# The digest must be computed by Core from its own authoritative inventory
# and re-computed at confirmation time (ADJ-001 PD-02/PD-04).  The canonical
# form below is the one frozen for this implementation task: object keys are
# recursively sorted, UTF-8, no whitespace; the collection digest is the
# SHA-256 of the concatenated *lowercase hex* per-book digests in request
# order.  ``title`` is deliberately excluded (display-only per C-04b).

INVENTORY_DIGEST_PREFIX = "sha256:"
_SHA256_HEX_LENGTH = 64
_MAX_TRASH_ENTRIES = 200


def is_inventory_digest(value: object) -> bool:
    """``sha256:<64 lowercase hex>`` only; anything else is INVALID_REQUEST."""
    if not isinstance(value, str):
        return False
    if not value.startswith(INVENTORY_DIGEST_PREFIX):
        return False
    hex_part = value[len(INVENTORY_DIGEST_PREFIX):]
    return len(hex_part) == _SHA256_HEX_LENGTH and all(
        character in "0123456789abcdef" for character in hex_part
    )


def canonical_inventory_payload(inventory: dict) -> dict:
    """The frozen canonical payload for one book (C-04b **v1.1** §2.1).

    v1.1 (CONTRACT-UNFREEZE-2026-11-05 §A2) replaces the single
    ``currentRevisionId`` binding value with the *complete* current sets:

    * ``currentRegionRevisionIds`` — every lineage-visible region current;
    * ``currentArtifactRevisionIds`` — every artifact current.

    The DTO keeps ``currentRevisionId`` as a representative display value, but
    it is deliberately **not** part of the digest (it does not bind anything).
    Arrays are lexicographically sorted inside the canonical form so the digest
    is independent of the DTO reading order.
    """
    return {
        "bookId": inventory["book_id"],
        "lockCount": inventory["lock_count"],
        "currentRegionRevisionIds": sorted(inventory["current_region_revision_ids"]),
        "currentArtifactRevisionIds": sorted(
            inventory["current_artifact_revision_ids"]
        ),
        "pinnedRevisionIds": sorted(inventory["pinned_revision_ids"]),
        "activeRunIds": sorted(inventory["active_run_ids"]),
        "draftPageCount": inventory["draft_page_count"],
        "manualRegionCount": inventory["manual_region_count"],
        "chapters": inventory["chapters"],
        "pages": inventory["pages"],
        "artifacts": inventory["artifacts"],
        "deletedFiles": inventory["deleted_files"],
        "deletedBytes": inventory["deleted_bytes"],
        "sharedFileRefs": [
            {
                "fileId": ref["fileId"],
                "otherProjectCount": ref["otherProjectCount"],
            }
            for ref in sorted(inventory["shared_file_refs"], key=lambda item: item["fileId"])
        ],
    }


def canonical_payload_digest(canonical: dict) -> str:
    """``sha256:`` + SHA-256 over an already-canonical payload object.

    Used both by ``inventory_digest`` (building the canonical object from the
    inventory) and by the PD-07 retry path to re-verify a digest persisted in
    the cleanup manifest from the persisted binding inputs (tamper detection).
    """
    encoded = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return INVENTORY_DIGEST_PREFIX + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def inventory_digest(inventory: dict) -> str:
    """``sha256:`` + SHA-256 of the canonical JSON of one book inventory."""
    return canonical_payload_digest(canonical_inventory_payload(inventory))


def collection_inventory_digest(book_ids: list[str], digests: dict[str, str]) -> str:
    """SHA-256 over the per-book digest hex strings concatenated in order."""
    parts = []
    for book_id in book_ids:
        digest = digests[book_id]
        parts.append(digest[len(INVENTORY_DIGEST_PREFIX):].lower())
    return INVENTORY_DIGEST_PREFIX + hashlib.sha256(
        "".join(parts).encode("ascii")
    ).hexdigest()


def shared_file_refs(
    shared_managed: dict[str, int] | None = None,
    shared_source_entries: dict[str, int] | None = None,
) -> list[dict]:
    """Build the frozen ``sharedFileRefs`` projection (PD-01/PD-08).

    * managed physical files shared with other books get an opaque, stable,
      path-free id: ``managed:`` + the first 16 hex of SHA-256 over the
      managed relative path (the actual path never reaches the wire);
    * referenced-source files use the stable ``source_entries.entry_id``;
    * ``otherProjectCount`` is the number of *other* books still referencing
      the file/entry (0 is never emitted — a 0 reference is not shared).
    """
    refs: list[dict] = []
    for relative_path, other_count in (shared_managed or {}).items():
        count = int(other_count)
        if count <= 0:
            continue
        path_digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:16]
        refs.append({"fileId": "managed:" + path_digest, "otherProjectCount": count})
    for entry_id, other_count in (shared_source_entries or {}).items():
        count = int(other_count)
        if count <= 0:
            continue
        refs.append({"fileId": entry_id, "otherProjectCount": count})
    refs.sort(key=lambda item: item["fileId"])
    return refs


def normalize_trash_entries(raw_entries: object) -> tuple[list[str] | None, str | None]:
    """Closed-shape validation for ``TrashEntryRef[1..N]``.

    Returns ``(book_ids, error_code)``.  Order is preserved and never
    deduplicated (the caller reports per entry, in order, and a duplicate is
    request validation like the delete commands' duplicate-ID rule).
    """
    if not isinstance(raw_entries, list) or not raw_entries:
        return None, "INVALID_REQUEST"
    if len(raw_entries) > _MAX_TRASH_ENTRIES:
        return None, "INVALID_REQUEST"
    book_ids: list[str] = []
    for entry in raw_entries:
        if not isinstance(entry, dict) or set(entry) != {"book_id"}:
            return None, "INVALID_REQUEST"
        book_id = entry.get("book_id")
        if not isinstance(book_id, str) or not book_id.strip():
            return None, "INVALID_REQUEST"
        book_ids.append(book_id)
    if len(book_ids) != len(set(book_ids)):
        return None, "INVALID_REQUEST"
    return book_ids, None


def is_valid_idempotency_key(value: object) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= 128


def encode_trash_cursor(deleted_at: str, book_id: str) -> str:
    """Opaque, path-free, order-preserving pagination cursor (base64url JSON)."""
    raw = json.dumps([deleted_at, book_id], separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_trash_cursor(cursor: str) -> tuple[str, str] | None:
    if not isinstance(cursor, str) or not cursor:
        return None
    padding = "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode((cursor + padding).encode("ascii"))
        decoded = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, TypeError):
        return None
    if (
        not isinstance(decoded, list)
        or len(decoded) != 2
        or not all(isinstance(item, str) and item for item in decoded)
    ):
        return None
    return decoded[0], decoded[1]
