"""Publish committed render PNGs into the resource channel's derived scope."""

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from pathlib import Path

from infrastructure.resource_channel.catalog_store import ResourceCatalogStore


class RenderPreviewPublisher:
    def __init__(self, derived_root: Path | str, catalog: ResourceCatalogStore) -> None:
        self._root = Path(derived_root)
        self._catalog = catalog

    def lookup(self, resource_id: str):
        """Catalog read-through for deterministic publish keys (idempotent resolve)."""
        return self._catalog.lookup(resource_id)

    def publish(self, managed_png: Path | str, revision: str) -> dict[str, str]:
        root = self._root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        preview_dir = root / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        if not preview_dir.resolve().is_relative_to(root):
            raise OSError("preview directory escaped derived root")

        resource_id = f"preview-{uuid.uuid4().hex}"
        rel_path = f"previews/{resource_id}.png"
        target = root / rel_path
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=preview_dir, delete=False) as temp:
                temp_path = Path(temp.name)
                with Path(managed_png).open("rb") as source:
                    shutil.copyfileobj(source, temp)
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(temp_path, target)
            self._catalog.upsert(resource_id, "derived-read-only", rel_path)
        except Exception:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            raise
        return {"resource_id": resource_id, "revision": revision}

    def publish_original(self, managed_file: Path | str, resource_id: str, suffix: str) -> dict[str, str]:
        """Publish one immutable managed-original page image under a
        deterministic catalog key (M2-PAGE-RESOURCE-RESOLVE-1).

        Unlike :meth:`publish` (random per-render preview ids), the caller
        owns the resource id so repeated resolves of the same page return
        the same catalog key: the managed original is immutable, so the
        first publish wins and later resolves are catalog lookups. The
        file is copied byte-for-byte (no transcode) into ``pages/`` under
        the derived read-only root with the same temp+fsync+replace and
        escape checks as preview publication.
        """
        root = self._root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        pages_dir = root / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        if not pages_dir.resolve().is_relative_to(root):
            raise OSError("pages directory escaped derived root")

        rel_path = f"pages/{resource_id}{suffix}"
        target = root / rel_path
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=pages_dir, delete=False) as temp:
                temp_path = Path(temp.name)
                with Path(managed_file).open("rb") as source:
                    shutil.copyfileobj(source, temp)
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(temp_path, target)
            self._catalog.upsert(resource_id, "derived-read-only", rel_path)
        except Exception:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            raise
        return {"resource_id": resource_id, "revision": "original"}


__all__ = ["RenderPreviewPublisher"]
