"""Font library store port (FEA-14-FONT-1)."""

from __future__ import annotations

from typing import Protocol

from application.fonts.service import FontAsset


class FontAssetStore(Protocol):
    def list_assets(self, state: str | None = None) -> list[FontAsset]: ...

    def get_asset(self, asset_id: str) -> FontAsset | None: ...

    def find_by_sha(self, sha256: str) -> FontAsset | None: ...

    def add_asset(self, asset: FontAsset) -> None: ...

    def soft_delete(self, asset_id: str, deleted_at: str) -> None: ...
