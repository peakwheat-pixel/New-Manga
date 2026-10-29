"""Shared rendering direction value used by ports and adapters."""

from __future__ import annotations

from enum import Enum


class TextDirection(str, Enum):
    """D03 §11.5 ``text_direction``: auto / horizontal / vertical."""

    AUTO = "auto"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


__all__ = ["TextDirection"]
