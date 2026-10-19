"""Publish committed render PNGs into the resource channel's derived scope."""

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from pathlib import Path
from infrastructure.filesystem.win_unlink import unlink_by_handle

from infrastructure.resource_channel.catalog_store import PreviewOrigin, ResourceCatalogStore
from infrastructure.resource_channel.handle_resolver import handle_verified_delete

#: M2-PAGE-RESOURCE-RESOLVE-1 (DSH r1 PR-12): the opaque revision label for
#: deterministic managed-original keys; contract rev 1.7 freezes the
#: literal. Single source shared by the publish return and the catalog-hit
#: branch in bootstrap.core_service.
ORIGINAL_REVISION = "original"


class RenderPreviewPublisher:
    def __init__(self, derived_root: Path | str, catalog: ResourceCatalogStore) -> None:
        self._root = Path(derived_root)
        self._catalog = catalog

    def lookup(self, resource_id: str):
        """Catalog read-through for deterministic publish keys (idempotent resolve)."""
        return self._catalog.lookup(resource_id)

    def artifact_exists(self, rel_path: str) -> bool:
        """Cheap existence probe for a deterministic-key artifact.

        DSH r1 PR-07: a catalog row alone must not satisfy resolve -- if
        the derived artifact was lost (cache wipe, catalog db copied
        without the derived root), the caller re-publishes under the same
        key (byte-for-byte, deterministic) instead of returning a key
        whose file is gone.
        """
        return (self._root / rel_path).is_file()

    def publish(
        self,
        managed_png: Path | str,
        revision: str,
        origin: PreviewOrigin | None = None,
    ) -> dict[str, str]:
        """Publish one rotated preview copy.

        M2-DERIVED-GC-2: when ``origin`` is given (the production Core is the
        ONLY authority that mints one), the catalog row and its
        ``preview_lifecycle`` origin row (retired=0) commit in the SAME
        catalog SQLite transaction after the temp+fsync+replace -- never
        "return the key now, register later". ``origin=None`` keeps the
        catalog-only legacy behaviour (the copy can never be reclaimed by
        reference)."""

        # R5 P1: baseline must not be resolved - resolve() follows junctions, so a
        # link ABOVE the root drifts baseline and candidate together and containment
        # passes.  The candidate keeps resolve(), which is what makes an escape
        # visible.  Same defect class as N-004.
        root = Path(os.path.abspath(str(self._root)))
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
            if origin is None:
                self._catalog.upsert(resource_id, "derived-read-only", rel_path)
            else:
                self._catalog.register_preview_with_origin(resource_id, rel_path, origin)
        except Exception:
            # R6 P1: cleanup deleted by path; the chain re-verifies instead.
            if temp_path is not None:
                self._cleanup_quietly(temp_path)
            self._cleanup_quietly(target)
            raise
        return {"resource_id": resource_id, "revision": revision}

    def _cleanup_quietly(self, path: Path) -> None:
        """Delete a partial file during failure cleanup without re-resolving it.

        R6 P1: the two lines this replaces ran on every publish failure and deleted
        by path, so a directory repointed in between sent the delete outside the
        derived root - R6's probe reproduced exactly that and read outside bytes.
        The handle chain re-verifies each segment against the configured root; a
        path that cannot be expressed relative to that root is not touched at all.
        """
        try:
            rel = path.relative_to(self._root)
        except ValueError:
            return
        segments = [part for part in rel.parts if part]
        if not segments:
            return
        handled = unlink_by_handle(self._root, segments)
        if handled is None:
            # No handle chain on this platform: keep the previous behaviour.
            path.unlink(missing_ok=True)
        # handled True -> deleted; False -> refused, and cleanup must not force it.

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
        # R5 P1: baseline must not be resolved - resolve() follows junctions, so a
        # link ABOVE the root drifts baseline and candidate together and containment
        # passes.  The candidate keeps resolve(), which is what makes an escape
        # visible.  Same defect class as N-004.
        root = Path(os.path.abspath(str(self._root)))
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
            # R6 P1: cleanup deleted by path; the chain re-verifies instead.
            if temp_path is not None:
                self._cleanup_quietly(temp_path)
            self._cleanup_quietly(target)
            raise
        return {"resource_id": resource_id, "revision": ORIGINAL_REVISION}

    def collect_orphans(self) -> dict[str, int]:
        """M2-DERIVED-GC-1 (RC4-12 first slice, PARTIAL mitigation): startup
        sweep of the two managed directories under the derived read-only root.

        Precondition: ``self._root`` IS the derived read-only root and
        ``previews/``/``pages/`` are owned exclusively by this publisher --
        any other file dropped there unregistered will be removed.

        Two reclamation classes only (DSH r1 C-3 wording):

        - **orphan files**: a file under ``previews/`` or ``pages/`` whose
          stem is absent from the catalog. It can never be issued again
          (issue requires a catalog lookup), so deleting it changes no
          observable behaviour.
        - **dead rows**: a ``derived-read-only`` catalog row whose
          ``rel_path`` no longer resolves to a file. Equivalent to absence
          at the failure-CLASS level, not the literal level: a page-original
          key self-heals to the same key (rev 1.7), while a preview key's
          issue moves from ``REF_NOT_FOUND`` (404) to
          ``RESOURCE_NOT_CATALOGED`` (400) -- both typed hard failures that
          serve no bytes.

        Live files with live rows are NEVER touched (reference-aware
        reclamation of rotated previews -- the actual RC4-12 growth path --
        is a registered follow-up, out of scope; rows of other scopes such
        as ``managed-read-only`` are filtered out before any resolution).
        Nothing outside the derived root -- in particular no managed or
        user source file -- is deletable here: the directory gate and the
        per-row candidate check both escape-check before unlink.
        """
        # R5 P1: baseline must not be resolved - resolve() follows junctions, so a
        # link ABOVE the root drifts baseline and candidate together and containment
        # passes.  The candidate keeps resolve(), which is what makes an escape
        # visible.  Same defect class as N-004.
        root = Path(os.path.abspath(str(self._root)))
        root.mkdir(parents=True, exist_ok=True)
        rows = {entry.resource_id: entry for entry in self._catalog.entries()
                if entry.scope_class == "derived-read-only"}
        catalogued = set(rows)
        removed_files = 0
        removed_rows = 0
        for dirname in ("previews", "pages"):
            directory = root / dirname
            if not directory.exists():
                continue
            resolved_dir = directory.resolve()
            if not resolved_dir.is_relative_to(root):
                raise OSError(f"{dirname} directory escaped derived root")
            for item in sorted(resolved_dir.iterdir()):
                if not item.is_file():
                    continue
                if item.stem not in catalogued:
                    # R5b P1: unlink() resolved the name a third time - after the
                    # containment check and after the enumeration.  The probe won
                    # that race and the outside file was deleted while this function
                    # reported {'orphan_files_removed': 1}.  The chain works relative
                    # to the configured root and re-verifies each segment, so a
                    # directory repointed mid-enumeration is refused, not followed.
                    # Enumeration is one level deep, so the relative path is just
                    # <dirname>/<name>.
                    handled = unlink_by_handle(root, [dirname, item.name])
                    if handled is None:
                        item.unlink(missing_ok=True)
                    elif not handled:
                        # Refused.  Do NOT count it: returning a plausible removed
                        # count is exactly what the reproduction showed.
                        continue
                    removed_files += 1
        for resource_id, entry in rows.items():
            candidate = (root / entry.rel_path).resolve()
            if not candidate.is_relative_to(root):
                raise OSError(f"catalog rel_path escaped derived root: {entry.rel_path}")
            if not candidate.is_file():
                if self._catalog.remove(resource_id):
                    removed_rows += 1
        return {"orphan_files_removed": removed_files, "dead_rows_removed": removed_rows}

    def delete_retired_preview_copy(
        self,
        resource_id: str,
        *,
        expected_sha256: str,
        expected_size: int,
    ) -> tuple[bool, str]:
        """M2-DERIVED-GC-2: delete ONE verified retired preview copy by
        DELETE DISPOSITION on the verifying handle (design §2.4).

        The rel path is recomputed from the resource id (never taken from a
        catalog row), passed through the lexical gate, opened with
        read+write+DELETE and FILE_SHARE_READ only, and deleted only when
        the streaming hash/size match the immutable revision's recorded
        values from the product DB. Any refusal keeps the file; the reason
        string is diagnostics only and never a retryable error surface."""

        rel_path = f"previews/{resource_id}.png"
        return handle_verified_delete(
            self._root,
            rel_path,
            expected_sha256=expected_sha256,
            expected_size=expected_size,
        )


__all__ = ["RenderPreviewPublisher"]
