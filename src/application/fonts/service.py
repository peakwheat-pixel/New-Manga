"""Font library ports and service (FEA-14-FONT-1; PREQ FONT P1-P4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import uuid

FONT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
FONT_MAGIC = {
    b"\x00\x01\x00\x00": ".ttf",
    b"OTTO": ".otf",
    b"true": ".ttf",
    b"wOFF": ".woff",
    b"wOF2": ".woff2",
}
MAX_FONT_BYTES = 50 * 1024 * 1024
MAX_ACTIVE_ASSETS = 200


class FontLibraryError(RuntimeError):
    """Typed font library failure (wire code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class FontAsset:
    asset_id: str
    family: str
    subfamily: str
    format: str
    sha256: str
    size_bytes: int
    managed_path: str
    license_note: str
    state: str
    created_at: str
    deleted_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "family": self.family,
            "subfamily": self.subfamily,
            "format": self.format,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "managed_path": self.managed_path,
            "license_note": self.license_note,
            "state": self.state,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _font_format(path: Path) -> str:
    with path.open("rb") as handle:
        head = handle.read(4)
    suffix = path.suffix.lower()
    return FONT_MAGIC.get(head) or (suffix if suffix in FONT_EXTENSIONS else "")


def _family_from_stem(stem: str) -> tuple[str, str]:
    """Heuristic family/subfamily split (no fontTools dependency)."""
    subfamily = ""
    family = stem
    for token in ("-Regular", "-Bold", "-Italic", "-BoldItalic", "-Light", "-Medium", "-Black", "-Thin"):
        if stem.endswith(token):
            family = stem[: -len(token)].replace("-", " ").strip() or stem
            subfamily = token.lstrip("-")
            break
    return family, subfamily


class FontLibraryService:
    """User-imported font assets only (no bundled fonts; PREQ §2)."""

    def __init__(self, store, data_root: Path) -> None:
        self._store = store
        self._data_root = Path(data_root)
        self._fonts_root = self._data_root / "fonts"

    @property
    def fonts_root(self) -> Path:
        return self._fonts_root

    def list_assets(self) -> list[dict]:
        return [asset.to_dict() for asset in self._store.list_assets()]

    def import_asset(self, source_path: str, license_note: str | None = None) -> dict:
        path = Path(source_path)
        if not path.is_absolute() or not path.is_file():
            raise FontLibraryError("FONT_SOURCE_INVALID", f"font source is not a readable file: {source_path}")
        size = path.stat().st_size
        if size <= 0 or size > MAX_FONT_BYTES:
            raise FontLibraryError("FONT_SOURCE_INVALID", "font file size is outside the allowed range")
        fmt = _font_format(path)
        if fmt not in FONT_EXTENSIONS:
            raise FontLibraryError("FONT_FORMAT_UNSUPPORTED", "font format is not supported")
        if len(self._store.list_assets(state="active")) >= MAX_ACTIVE_ASSETS:
            raise FontLibraryError("FONT_LIMIT_REACHED", "font library limit reached")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        existing = self._store.find_by_sha(digest)
        if existing is not None:
            return existing.to_dict()
        self._fonts_root.mkdir(parents=True, exist_ok=True)
        managed = self._fonts_root / f"{digest[:16]}{fmt}"
        if not managed.exists():
            shutil.copyfile(path, managed)
        family, subfamily = _family_from_stem(path.stem)
        asset = FontAsset(
            asset_id=uuid.uuid4().hex,
            family=family,
            subfamily=subfamily,
            format=fmt.lstrip("."),
            sha256=digest,
            size_bytes=size,
            managed_path=managed.name,
            license_note=license_note or "",
            state="active",
            created_at=_now(),
        )
        self._store.add_asset(asset)
        return asset.to_dict()

    def delete_asset(self, asset_id: str) -> bool:
        asset = self._store.get_asset(asset_id)
        if asset is None or asset.state == "deleted":
            return False
        self._store.soft_delete(asset_id, _now())
        return True

    def refresh_assets(self) -> dict:
        available = 0
        failed: list[dict] = []
        for asset in self._store.list_assets(state="active"):
            path = self._fonts_root / asset.managed_path
            if not path.is_file():
                failed.append({"path": asset.managed_path, "code": "FONT_FILE_MISSING"})
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != asset.sha256:
                failed.append({"path": asset.managed_path, "code": "FONT_SHA256_MISMATCH"})
                continue
            available += 1
        if self._fonts_root.is_dir():
            known = {asset.managed_path for asset in self._store.list_assets()}
            for path in sorted(self._fonts_root.iterdir()):
                if not path.is_file() or path.name in known:
                    continue
                try:
                    self.import_asset(str(path), "refresh-import")
                except FontLibraryError as error:
                    failed.append({"path": path.name, "code": error.code})
        return {"available": available, "failed": failed}
