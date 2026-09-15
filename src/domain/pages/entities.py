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
    managed_original_ref: str
    page_locked: bool = False
    review_state: str = "unreviewed"
    overall_status: str = "not_started"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    deleted_at: str | None = None

    def __post_init__(self) -> None:
        if not self.chapter_id:
            raise ValueError("page requires a chapter_id")
        if not self.source_hash:
            raise ValueError("page requires the source file hash")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("decoded image must have positive width/height")
        if not self.managed_original_ref:
            raise ValueError("page requires a managed copy reference for the original")

    def reorder(self, sort_order: int) -> None:
        """User drag-and-drop reordering never touches source_order."""
        self.sort_order = int(sort_order)
        self.updated_at = utc_now()

    def soft_delete(self) -> None:
        self.deleted_at = utc_now()
        self.updated_at = self.deleted_at

    @property
    def deleted(self) -> bool:
        return self.deleted_at is not None
