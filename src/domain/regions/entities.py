"""Region domain entities (D03 §6~11, §15; TASK-002 §2; D06 §87~90).

Pure domain: no sqlite3/PySide6 imports (TASK-005 architecture guards).
One Region is the single unit for OCR/translation/mask/inpaint/render/
proofreading/rerun (D03 §6.1) — geometry, four-level text, style, locks,
review state and revisions all live on this one model (AC-REGION-001).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class RegionType(str, Enum):
    """D03 §6.2."""

    SPEECH = "speech"
    NARRATION = "narration"
    SFX = "sfx"
    TITLE = "title"
    NOTE = "note"
    OTHER = "other"


class RegionOrigin(str, Enum):
    """TASK-002 §2.2."""

    MACHINE = "machine"
    USER = "user"
    IMPORTED = "imported"
    RESTORED = "restored"


class ReviewState(str, Enum):
    """TASK-002 §2.2 / D03 §6.6."""

    UNREVIEWED = "unreviewed"
    NEEDS_REVIEW = "needs_review"
    CONFIRMED = "confirmed"


class SfxPolicy(str, Enum):
    """D03 §7: skip (default) / translate / manual."""

    SKIP = "skip"
    TRANSLATE = "translate"
    MANUAL = "manual"


# ----------------------------------------------------------------------
# geometry (D03 §6.3)
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class BBox:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("bbox width/height must be positive")

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)

    @staticmethod
    def covering(*boxes: "BBox") -> "BBox":
        """Smallest bbox containing all inputs (used by merge)."""
        if not boxes:
            raise ValueError("covering() needs at least one bbox")
        left = min(b.x for b in boxes)
        top = min(b.y for b in boxes)
        right = max(b.x + b.width for b in boxes)
        bottom = max(b.y + b.height for b in boxes)
        return BBox(left, top, right - left, bottom - top)


@dataclass(frozen=True)
class RegionGeometry:
    """BBox is the fast query shortcut; polygon is the formal geometry."""

    bbox: BBox
    polygon: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if self.polygon and len(self.polygon) < 3:
            raise ValueError("polygon needs at least 3 points when present")

    def as_jsonable(self) -> dict:
        return {
            "bbox": list(self.bbox.as_tuple()),
            "polygon": [list(point) for point in self.polygon],
        }

    @staticmethod
    def from_jsonable(data: dict) -> "RegionGeometry":
        return RegionGeometry(
            bbox=BBox(*data["bbox"]),
            polygon=tuple(tuple(point) for point in data.get("polygon", ())),
        )

    def union(self, other: "RegionGeometry") -> "RegionGeometry":
        """Merge geometry: covering bbox; polygons concatenated (D03 §6.4)."""
        polygons = self.polygon + other.polygon
        return RegionGeometry(bbox=BBox.covering(self.bbox, other.bbox), polygon=polygons)


# ----------------------------------------------------------------------
# text (D03 §8) and style (D03 §11, minimal)
# ----------------------------------------------------------------------


@dataclass
class RegionText:
    """Four-level text model (D03 §8.1) with manual-edit protection (§8.4).

    final resolution (D03 §8.3): a non-blank *confirmed* edited translation
    wins; otherwise the machine translation; otherwise empty. A manual save
    without explicit confirmation stays at needs_review and therefore does
    not become final yet (AC-TRANS-001 test hint: 空字符串/未确认 → machine).
    """

    ocr_text: str = ""
    machine_translation: str = ""
    edited_translation: str = ""
    final_translation: str = ""
    final_source: str = "none"  # none | edited | machine
    edited_confirmed: bool = False
    manual_edited: bool = False
    translation_locked: bool = False

    def _has_confirmed_manual_edit(self) -> bool:
        return bool(self.edited_translation.strip()) and self.edited_confirmed

    def resolve_final(self) -> tuple[str, str]:
        if self._has_confirmed_manual_edit():
            return self.edited_translation, "edited"
        if self.machine_translation.strip():
            return self.machine_translation, "machine"
        return "", "none"

    def refresh_final(self) -> None:
        self.final_translation, self.final_source = self.resolve_final()

    def apply_ocr(self, ocr_text: str) -> bool:
        """Re-OCR updates ocr_text only; manual译文/final stay (AC-OCR-002).

        Returns True when the source text changed, which callers surface as
        "原文已变化，现有译文可能需要重译".
        """
        changed = ocr_text != self.ocr_text
        self.ocr_text = ocr_text
        self.refresh_final()
        return changed

    def apply_machine_translation(self, translation: str) -> None:
        """Machine result; must never run while translation_locked (§89)."""
        if self.translation_locked:
            raise PermissionError("translation_locked: machine result must not overwrite")
        self.machine_translation = translation
        self.refresh_final()

    def save_manual_translation(self, edited: str) -> None:
        """User save: edited set, protection armed; final resolution waits
        for explicit confirmation (needs_review, D03 §8.3/§8.4)."""
        self.edited_translation = edited
        self.manual_edited = True
        self.translation_locked = True
        self.refresh_final()

    def confirm_edited_translation(self) -> None:
        """Explicit proofread confirmation → edited becomes final."""
        if not self.edited_translation.strip():
            raise ValueError("nothing to confirm: edited_translation is blank")
        self.edited_confirmed = True
        self.refresh_final()

    def unlock_translation(self) -> None:
        """User may explicitly release the Translation Lock (D03 §8.4)."""
        self.translation_locked = False


@dataclass
class TextStyle:
    """Minimal style snapshot stored in revisions (D03 §11 subset)."""

    font_family: str = ""
    font_size: int | None = None
    text_color: str = ""
    stroke_color: str = ""
    stroke_width: float = 0.0
    auto_font_size_enabled: bool = True

    def as_jsonable(self) -> dict:
        return dict(self.__dict__)

    @staticmethod
    def from_jsonable(data: dict) -> "TextStyle":
        return TextStyle(**data)


# ----------------------------------------------------------------------
# Region and revision (D03 §6/§15)
# ----------------------------------------------------------------------


@dataclass
class Region:
    """Unified region model (AC-REGION-001): geometry + text + style + locks
    + review + revisions on one object."""

    region_id: str
    page_id: str
    region_type: RegionType = RegionType.SPEECH
    reading_order: int = 0
    geometry: RegionGeometry = field(
        default_factory=lambda: RegionGeometry(bbox=BBox(0, 0, 1, 1))
    )
    text: RegionText = field(default_factory=RegionText)
    style: TextStyle = field(default_factory=TextStyle)
    sfx_policy: SfxPolicy = SfxPolicy.SKIP
    region_locked: bool = False
    translation_locked: bool = False
    inpaint_locked: bool = False
    current_revision_id: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    deleted_at: str | None = None

    def __post_init__(self) -> None:
        self.region_type = RegionType(self.region_type)
        self.sfx_policy = SfxPolicy(self.sfx_policy)

    def apply_type(self, region_type: RegionType) -> None:
        self.region_type = RegionType(region_type)
        self.updated_at = utc_now()

    def apply_sfx_policy(self, policy: SfxPolicy) -> None:
        self.sfx_policy = SfxPolicy(policy)
        self.updated_at = utc_now()

    def set_region_locked(self, locked: bool) -> None:
        self.region_locked = bool(locked)
        self.updated_at = utc_now()

    def set_inpaint_locked(self, locked: bool) -> None:
        self.inpaint_locked = bool(locked)
        self.updated_at = utc_now()

    def soft_delete(self) -> None:
        self.deleted_at = utc_now()
        self.updated_at = self.deleted_at

    @property
    def deleted(self) -> bool:
        return self.deleted_at is not None

    def snapshot_state(self) -> dict:
        """Serializable state covered by a revision (D03 §15.1)."""
        return {
            "region_type": self.region_type.value,
            "reading_order": self.reading_order,
            "geometry": self.geometry.as_jsonable(),
            "text": {
                "ocr_text": self.text.ocr_text,
                "machine_translation": self.text.machine_translation,
                "edited_translation": self.text.edited_translation,
                "final_translation": self.text.final_translation,
                "final_source": self.text.final_source,
                "edited_confirmed": self.text.edited_confirmed,
                "manual_edited": self.text.manual_edited,
                "translation_locked": self.text.translation_locked,
            },
            "style": self.style.as_jsonable(),
            "sfx_policy": self.sfx_policy.value,
            "region_locked": self.region_locked,
            "translation_locked": self.translation_locked,
            "inpaint_locked": self.inpaint_locked,
        }

    def restore_from_snapshot(self, snapshot: dict) -> None:
        self.region_type = RegionType(snapshot["region_type"])
        self.reading_order = snapshot["reading_order"]
        self.geometry = RegionGeometry.from_jsonable(snapshot["geometry"])
        text_state = snapshot["text"]
        self.text = RegionText(
            ocr_text=text_state["ocr_text"],
            machine_translation=text_state["machine_translation"],
            edited_translation=text_state["edited_translation"],
            final_translation=text_state["final_translation"],
            final_source=text_state["final_source"],
            edited_confirmed=text_state["edited_confirmed"],
            manual_edited=text_state["manual_edited"],
            translation_locked=text_state["translation_locked"],
        )
        self.style = TextStyle.from_jsonable(snapshot["style"])
        self.sfx_policy = SfxPolicy(snapshot["sfx_policy"])
        self.region_locked = snapshot["region_locked"]
        self.translation_locked = snapshot["translation_locked"]
        self.inpaint_locked = snapshot["inpaint_locked"]
        self.updated_at = utc_now()


@dataclass(frozen=True)
class RegionRevision:
    """Immutable revision (TASK-002 §2.2, D03 §15)."""

    region_revision_id: str
    region_id: str
    revision_no: int
    snapshot: dict
    origin: RegionOrigin
    review_state: ReviewState
    is_pinned: bool = False
    source_run_id: str | None = None
    source_step_run_id: str | None = None
    restored_from_revision_id: str | None = None
    created_at: str = field(default_factory=utc_now)
