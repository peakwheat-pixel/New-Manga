"""Text direction resolution (D03 §11.5 ``text_direction=auto``).

Pure decision helper: explicit settings win, then the SourceStyle hint
(D06 §8 辅助判断横排/竖排), then the region aspect ratio.
"""

from __future__ import annotations

from application.rendering.style import TextDirection
from ports.rendering.ports import SourceStyle

#: A region at least this much taller than wide defaults to vertical.
VERTICAL_ASPECT_THRESHOLD = 1.5


def resolve_direction(
    setting: TextDirection,
    box_width: int,
    box_height: int,
    source_hint: SourceStyle | None = None,
) -> TextDirection:
    if setting is not TextDirection.AUTO:
        return setting
    hint = source_hint.direction_hint if source_hint is not None else None
    if hint is not None:
        return hint
    if box_width <= 0:
        return TextDirection.VERTICAL
    return (
        TextDirection.VERTICAL
        if box_height / box_width >= VERTICAL_ASPECT_THRESHOLD
        else TextDirection.HORIZONTAL
    )
