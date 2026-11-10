"""SQLite font asset store (FEA-14-FONT-1, schema v11)."""

from __future__ import annotations

import sqlite3

from application.fonts.service import FontAsset


class SqliteFontAssetStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_asset(self, row) -> FontAsset:
        return FontAsset(
            asset_id=str(row[0]),
            family=str(row[1]),
            subfamily=str(row[2]),
            format=str(row[3]),
            sha256=str(row[4]),
            size_bytes=int(row[5]),
            managed_path=str(row[6]),
            license_note=str(row[7]),
            state=str(row[8]),
            created_at=str(row[9]),
            deleted_at=(str(row[10]) if row[10] is not None else None),
        )

    def list_assets(self, state: str | None = None) -> list[FontAsset]:
        if state is None:
            rows = self._conn.execute(
                "SELECT asset_id, family, subfamily, format, sha256, size_bytes, managed_path,"
                " license_note, state, created_at, deleted_at FROM font_assets"
                " ORDER BY created_at, asset_id"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT asset_id, family, subfamily, format, sha256, size_bytes, managed_path,"
                " license_note, state, created_at, deleted_at FROM font_assets"
                " WHERE state = ? ORDER BY created_at, asset_id",
                (state,),
            ).fetchall()
        return [self._row_to_asset(row) for row in rows]

    def get_asset(self, asset_id: str) -> FontAsset | None:
        row = self._conn.execute(
            "SELECT asset_id, family, subfamily, format, sha256, size_bytes, managed_path,"
            " license_note, state, created_at, deleted_at FROM font_assets WHERE asset_id = ?",
            (asset_id,),
        ).fetchone()
        return self._row_to_asset(row) if row is not None else None

    def find_by_sha(self, sha256: str) -> FontAsset | None:
        row = self._conn.execute(
            "SELECT asset_id, family, subfamily, format, sha256, size_bytes, managed_path,"
            " license_note, state, created_at, deleted_at FROM font_assets"
            " WHERE sha256 = ? AND state != 'deleted'",
            (sha256,),
        ).fetchone()
        return self._row_to_asset(row) if row is not None else None

    def add_asset(self, asset: FontAsset) -> None:
        self._conn.execute(
            "INSERT INTO font_assets (asset_id, family, subfamily, format, sha256, size_bytes,"
            " managed_path, license_note, state, created_at, deleted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                asset.asset_id,
                asset.family,
                asset.subfamily,
                asset.format,
                asset.sha256,
                asset.size_bytes,
                asset.managed_path,
                asset.license_note,
                asset.state,
                asset.created_at,
                asset.deleted_at,
            ),
        )
        self._conn.commit()

    def soft_delete(self, asset_id: str, deleted_at: str) -> None:
        self._conn.execute(
            "UPDATE font_assets SET state = 'deleted', deleted_at = ? WHERE asset_id = ?",
            (deleted_at, asset_id),
        )
        self._conn.commit()
