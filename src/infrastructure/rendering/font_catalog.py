"""Qt-based font catalog (D03 §11.6, AC: 缺字体诊断).

The frozen default font (Source Han Sans K Bold) may be absent on a given
machine; rendering must continue on an installed fallback and report the
substitution so the UI can surface it. Fallback chain targets the
project's Windows boundary.
"""

from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase

from ports.rendering.ports import FontCatalog, ResolvedFont

#: First installed family wins; product boundary is Windows (D01).
_FALLBACK_CHAIN: tuple[str, ...] = (
    "Source Han Sans K Bold",
    "Source Han Sans Bold",
    "Source Han Sans SC Bold",
    "Microsoft YaHei",
    "SimSun",
    "Arial",
)


class QtFontCatalog(FontCatalog):
    def resolve(self, family: str) -> ResolvedFont:
        if family and QFontDatabase.hasFamily(family):
            return ResolvedFont(family, family, True)
        for candidate in _FALLBACK_CHAIN:
            if candidate != family and QFontDatabase.hasFamily(candidate):
                return ResolvedFont(family, candidate, False)
        # Last resort: whatever Qt considers the default family.
        system_default = QFont().family()
        return ResolvedFont(family, system_default, False)
