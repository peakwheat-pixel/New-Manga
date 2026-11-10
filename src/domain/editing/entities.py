"""Issue-marker domain: the EDIT slice's "problem markers" (FEA-14-EDIT-1).

A marker flags a place a human wants to revisit: either a whole page
(``position_x``/``position_y`` are ``None``) or one relative point on a page
(both coordinates present, 0.0-1.0). Markers are user work product, not
protected content: deleting one only removes the marker row.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IssueMarkerState(str, Enum):
    """PREQ §8 P16 state values; the list face defaults to ``open``."""

    OPEN = "open"
    RESOLVED = "resolved"


@dataclass
class IssueMarker:
    marker_id: str
    book_id: str
    chapter_id: str
    page_id: str
    kind: str
    state: IssueMarkerState = IssueMarkerState.OPEN
    note: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    created_at: str = ""
    resolved_at: str | None = None

    @property
    def position(self) -> dict[str, float] | None:
        """PREQ §8 ``position``: both coordinates or neither, never half."""
        if self.position_x is None or self.position_y is None:
            return None
        return {"x": float(self.position_x), "y": float(self.position_y)}
