"""Page domain entity (D03 §5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from domain.books.entities import utc_now


@dataclass
class Page:
    """One logical page; an extra-long webtoon image is still one Page.

    ``source_order`` is frozen at import time; ``sort_order`` is the user's
    current ordering (D03 §5.3, AC-PAGE-001). ``managed_original_ref`` points
    at the Managed Copy of the original image and must exist before the page
    is committed (D07 §38, AC-IMPORT-003).

    FEA-09 (C-15 v7): ``source_mode`` splits managed pages from referenced
    pages. A referenced page binds to a source entry instead of a Managed
    Copy, so ``managed_original_ref`` may be empty in that mode; the
    binding itself lives in ``page_bindings`` (C-15 §2.6).
    """

    page_id: str
    chapter_id: str
    source_filename: str
    source_order: int
    sort_order: int
    source_hash: str
    source_size_bytes: int
    width: int
    height: int
    #: Managed Copy reference (managed mode). NULL for referenced pages
    #: (FEA-09/C-15 §3.1), which bind via ``page_bindings`` instead.
    managed_original_ref: str | None
    page_locked: bool = False
    review_state: str = "unreviewed"
    overall_status: str = "not_started"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    deleted_at: str | None = None
    #: FEA-09/C-15 §2.1: 'managed' (legacy Managed Copy) or 'referenced'.
    source_mode: str = "managed"
    #: FEA-09/C-15 §4.1: 'incomplete' until the same-transaction commit made
    #: the row data-complete; half-written/failing paths stay incomplete.
    integrity_status: str = "complete"

    def __post_init__(self) -> None:
        if not self.chapter_id:
            raise ValueError("page requires a chapter_id")
        if not self.source_hash:
            raise ValueError("page requires the source file hash")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("decoded image must have positive width/height")
        if self.source_mode not in ("managed", "referenced"):
            raise ValueError("page source_mode must be 'managed' or 'referenced'")
        if self.integrity_status not in ("incomplete", "complete"):
            raise ValueError("page integrity_status must be 'incomplete' or 'complete'")
        if self.source_mode == "managed" and not self.managed_original_ref:
            raise ValueError("page requires a managed copy reference for the original")
        if self.source_mode == "referenced" and not self.managed_original_ref:
            # referenced pages bind through page_bindings; managed_original_ref
            # stays empty (C-15 §3.1) and the binding is written by the
            # import orchestration in the same transaction.
            pass

    def reorder(self, sort_order: int) -> None:
        """User drag-and-drop reordering never touches source_order."""
        self.sort_order = int(sort_order)
        self.updated_at = utc_now()

    def soft_delete(self) -> None:
        self.deleted_at = utc_now()
        self.updated_at = self.deleted_at


@dataclass(frozen=True)
class PageView:
    """FEA-09/C-15 v1.1 §4.4: read-only projection for V-true rows that cannot
    be materialised as a full :class:`Page` (managed artifact-only witness,
    missing import columns, or superseded representation).

    It is **not** a write model: no path through the repository accepts a
    ``PageView`` for insert/update/import. Fields that are unknown stay None —
    in particular ``source_hash`` must only ever come from an eligible
    ORIGINAL revision (or ``pages.source_hash``), never from a thumbnail/clean
    artifact.
    """

    page_id: str
    chapter_id: str
    source_mode: str
    sort_order: int
    visibility_witness: str  # artifact | copy | artifact+copy | referenced
    original_available: bool
    integrity_status: str
    source_filename: str | None = None
    source_order: int | None = None
    created_at: str | None = None
    source_hash: str | None = None
    source_size_bytes: int | None = None
    managed_original_ref: str | None = None
    width: int | None = None
    height: int | None = None
    artifact_revision_id: str | None = None

    @property
    def deleted(self) -> bool:
        return False

    def reorder(self, _sort_order: int) -> None:
        raise TypeError("PageView is a read-only projection; reorder the Page")

    def soft_delete(self) -> None:
        raise TypeError("PageView is a read-only projection; soft-delete the Page")
