"""Derived-cache scope root management (M2-RC1, infrastructure).

The channel serves exactly one scope class family: derived cache and managed
copies (``derived-read-only`` / ``managed-read-only``). ``user-source`` has no
frontend-visible implementation and this module refuses to build a scope root
for it (Contract 1.1 T5.3).
"""

from __future__ import annotations

from pathlib import Path

from application.resource_channel.dto import (
    TypedResourceChannelError,
    E_SCOPE_DENIED,
)


class ScopeRoots:
    """Resolves scope classes to absolute scope roots on this machine."""

    def __init__(self, derived_root: Path, managed_root: Path) -> None:
        self._roots = {
            "derived-read-only": Path(derived_root).resolve(),
            "managed-read-only": Path(managed_root).resolve(),
        }

    def root_for(self, scope_class: str) -> Path:
        root = self._roots.get(scope_class)
        if root is None:
            raise TypedResourceChannelError(
                E_SCOPE_DENIED, f"no servable scope root for {scope_class}"
            )
        return root

    def reader_for(self, scope_class: str):
        from infrastructure.resource_channel.handle_resolver import (
            HandleVerifiedFileReader,
        )

        return HandleVerifiedFileReader(self.root_for(scope_class))
