"""P09-MANAGED-READ-ROOT-TRUST-1: per-site managed-root trust tests.

The task exists because the read/export paths verified a *resolved* value
against another *resolved* value: a junction injected above the configured
managed root moved both sides together, containment passed and outside bytes
were served (R5b P2).  The fix freezes the expected identity from a handle
opened at assembly time and reads through verifying handles.

Every site below is tested individually (AC3 forbids "same pattern, one test"):

1-4 ``src/bootstrap/core_service.py`` — ``read_original_page``,
    ``handle_resolve_page_resource``, ``_checked_managed_path``/``_reader_sha256``,
    ``_is_protected_export_target``
5-7 ``src/bootstrap/core_assembly.py`` — ``_ManagedPageCatalog.image_state``,
    ``_ManagedPageCatalog._uri_within``, ``_ManagedPageImageSource._page_image``
8   ``src/infrastructure/resource_channel/handle_resolver.resolve_namespace_identity``

Harness semantics: the configured data root's **ancestor** is a directory
junction from the start (``live -> real``), so every legal read also proves the
documented "ancestor links are allowed while the object identity matches"
policy (AC2).  ``swap()`` repoints that ancestor to an outside mirror tree — the
R5b injection.  Each site first performs a legal read through the stable
junction, then asserts refusal after the swap.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows junction/handle semantics")

OUTSIDE = b"OUTSIDE - must never be served"


def _make_png(width: int = 30, height: int = 20) -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGBA", (width, height), (12, 34, 56, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


class TrustHarness:
    """Production Core assembled under a junction ancestor, with a repoint swap."""

    def __init__(self, tmp_path: Path) -> None:
        import _winapi

        from bootstrap.core_service import assemble_production_core

        self.tmp = tmp_path
        self.real = tmp_path / "real"
        self.live = tmp_path / "live"
        self.payload = tmp_path / "payload"
        self.real.mkdir()
        _winapi.CreateJunction(str(self.real), str(self.live))
        self.core = assemble_production_core(self.live / "data")
        self.managed = Path(self.core.storage.root)
        self.real_managed = self.real / "data" / "managed"
        self.payload_managed = self.payload / "data" / "managed"
        self.page_id = self._import_page()

    def _import_page(self) -> str:
        from application.importing.images.ports import ImportSource

        book = self.core.library.create_book("P09 read-root trust")
        chapter = self.core.library.create_chapter(book.book_id, "chapter")
        report = self.core.importer.import_files(
            chapter.chapter_id, [ImportSource("page.png", _make_png)]
        )
        assert report.failed == ()
        assert len(report.imported) == 1
        page = report.imported[0].page
        assert page.managed_original_ref
        return page.page_id

    # ------------------------------------------------------------ references

    def ref(self) -> str:
        page = self.core.repository.get_page(self.page_id)
        assert page is not None and page.managed_original_ref
        return page.managed_original_ref

    def live_path(self) -> Path:
        """The reference spelled through the configured (junction) root."""

        return self.managed.joinpath(*self.ref().split("/"))

    def real_path(self) -> Path:
        """The same object spelled through its real location."""

        return self.real_managed.joinpath(*self.ref().split("/"))

    def legal_bytes(self) -> bytes:
        return self.real_path().read_bytes()

    def mirror_outside(self, payload: bytes = OUTSIDE) -> Path:
        target = self.payload_managed.joinpath(*self.ref().split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target

    # ---------------------------------------------------------------- swap

    def swap(self) -> None:
        import _winapi

        os.rmdir(str(self.live))  # removes the junction itself, never `real`
        _winapi.CreateJunction(str(self.payload), str(self.live))

    def close(self) -> None:
        try:
            self.core.conn.close()
        finally:
            if self.live.exists():
                try:
                    os.rmdir(str(self.live))
                except OSError:
                    pass
            shutil.rmtree(self.real, ignore_errors=True)
            shutil.rmtree(self.payload, ignore_errors=True)


@pytest.fixture
def harness(tmp_path):
    instance = TrustHarness(tmp_path)
    try:
        yield instance
    finally:
        instance.close()


def _server_with_previews(core, tmp_path: Path):
    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    catalog = ResourceCatalogStore(catalog_db)
    server = CoreServiceServer(
        core, render_previews=RenderPreviewPublisher(derived_root, catalog)
    )
    return server, catalog, derived_root


def _derived_bytes(derived_root: Path) -> list[bytes]:
    pages = derived_root / "pages"
    if not pages.is_dir():
        return []
    return [path.read_bytes() for path in pages.iterdir() if path.is_file()]


# ---------------------------------------------------------------------------
# Site 1 — assemble_production_core.read_original_page (core_service.py)
# ---------------------------------------------------------------------------


def test_site1_read_original_page_reader_refuses_repointed_ancestor(harness):
    reader = harness.core.render._original_page_reader
    assert reader(harness.page_id) == harness.legal_bytes()

    outside = harness.mirror_outside()
    harness.swap()
    with pytest.raises(ValueError):
        reader(harness.page_id)
    assert outside.read_bytes() == OUTSIDE, "the outside file must be untouched"


# ---------------------------------------------------------------------------
# Site 2 — handle_resolve_page_resource (core_service.py)
# ---------------------------------------------------------------------------


def test_site2_resolve_page_resource_refuses_repointed_ancestor(harness, tmp_path):
    server, catalog, derived_root = _server_with_previews(harness.core, tmp_path)
    try:
        first = server.handle_resolve_page_resource({"page_id": harness.page_id})
        assert first == {
            "resource_id": f"page-original-{harness.page_id}",
            "revision": "original",
        }
        assert harness.legal_bytes() in _derived_bytes(derived_root)

        harness.mirror_outside()
        harness.swap()
        with pytest.raises(RuntimeError):
            server.handle_resolve_page_resource({"page_id": harness.page_id})
        assert all(OUTSIDE not in payload for payload in _derived_bytes(derived_root)), (
            "outside bytes must never be published into the derived root"
        )
    finally:
        catalog.close()


# ---------------------------------------------------------------------------
# Site 3 — _checked_managed_path / _reader_sha256 (core_service.py)
# ---------------------------------------------------------------------------


def test_site3_checked_managed_path_refuses_repointed_ancestor(harness):
    from bootstrap.core_service import CoreServiceServer, P16WireError

    server = CoreServiceServer(harness.core)
    live = str(harness.live_path())
    assert server._checked_managed_path(live).read_bytes() == harness.legal_bytes()

    page = harness.core.repository.get_page(harness.page_id)
    assert page is not None
    reader_page = next(
        item
        for item in harness.core.reader_catalog.list_pages(page.chapter_id)
        if item.page_id == harness.page_id
    )
    assert (
        server._reader_sha256(reader_page.original_path, reader_page.original_sha256)
        == reader_page.original_sha256
    )

    harness.mirror_outside()
    harness.swap()
    with pytest.raises(P16WireError):
        server._checked_managed_path(live)
    with pytest.raises(P16WireError):
        server._reader_sha256(reader_page.original_path, reader_page.original_sha256)


# ---------------------------------------------------------------------------
# Site 4 — _is_protected_export_target (core_service.py)
# ---------------------------------------------------------------------------


def test_site4_protected_export_target_uses_frozen_managed_baseline(harness):
    from bootstrap.core_service import CoreServiceServer

    server = CoreServiceServer(harness.core)
    assert server._is_protected_export_target(harness.live_path()) is True

    harness.mirror_outside()
    harness.swap()
    # The real managed original must stay protected even though the configured
    # root name now resolves to the attacker mirror (the old code resolved the
    # managed side and lost this match -> the export could overwrite it).
    assert server._is_protected_export_target(harness.real_path()) is True
    # The outside mirror is not a managed file any more.
    assert (
        server._is_protected_export_target(
            harness.payload_managed.joinpath(*harness.ref().split("/"))
        )
        is False
    )


# ---------------------------------------------------------------------------
# Site 5 — _ManagedPageCatalog.image_state (core_assembly.py)
# ---------------------------------------------------------------------------


def test_site5_image_state_refuses_repointed_ancestor(harness):
    catalog = harness.core.page_catalog
    assert catalog.image_state(harness.page_id, "original") == "ok"

    harness.mirror_outside()
    harness.swap()
    assert catalog.image_state(harness.page_id, "original") == "invalid"


# ---------------------------------------------------------------------------
# Site 6 — _ManagedPageCatalog._uri_within / image_url (core_assembly.py)
# ---------------------------------------------------------------------------


def test_site6_uri_within_refuses_repointed_ancestor(harness):
    from urllib.parse import urlparse
    from urllib.request import url2pathname

    catalog = harness.core.page_catalog
    ref = harness.ref()
    uri = catalog._uri_within(ref)
    assert uri.startswith("file:")
    assert Path(url2pathname(urlparse(uri).path)) == harness.real_path()
    assert catalog.image_url(harness.page_id, "original") == uri

    harness.mirror_outside()
    harness.swap()
    assert catalog._uri_within(ref) == ""
    assert catalog.image_url(harness.page_id, "original") == ""


# ---------------------------------------------------------------------------
# Site 7 — _ManagedPageImageSource._page_image (core_assembly.py)
# ---------------------------------------------------------------------------


def test_site7_page_image_source_decodes_verified_handle_bytes(harness):
    from bootstrap.core_assembly import _ManagedPageImageSource
    from infrastructure.sqlite.regions import SqliteRegionRepository
    from ports.providers.errors import ProviderInputError

    source = _ManagedPageImageSource(
        harness.core.repository,
        harness.core.storage,
        SqliteRegionRepository(harness.core.conn),
    )
    frame = source.page_frame(harness.page_id)
    assert (frame.width, frame.height) == (30, 20)

    harness.mirror_outside(payload=_make_png(11, 7))
    harness.swap()
    with pytest.raises(ProviderInputError):
        source.page_frame(harness.page_id)


# ---------------------------------------------------------------------------
# Site 8 — resolve_namespace_identity (handle_resolver.py)
# ---------------------------------------------------------------------------


def test_site8_resolve_namespace_identity_refuses_swap_between_walk_and_open(
    tmp_path, monkeypatch
):
    import _winapi

    from infrastructure.resource_channel import handle_resolver as resolver

    base = tmp_path / "inside"
    derived = base / "derived"
    derived.mkdir(parents=True)
    (derived / "marker.txt").write_bytes(b"INSIDE")
    payload = tmp_path / "payload"
    (payload / "derived").mkdir(parents=True)
    (payload / "derived" / "marker.txt").write_bytes(OUTSIDE)

    # Legal call first: no injection, canonical path + identity are returned.
    canonical, identity = resolver.resolve_namespace_identity(derived)
    assert Path(canonical) == derived.resolve()
    assert identity[1] > 0

    renamed = tmp_path / "inside-original"
    fired: list[str] = []
    real_walk = resolver._lstat_reparse_walk

    def walk_then_swap(path):
        real_walk(path)
        if not fired:
            fired.append(str(path))
            # R6 order: the pre-open walk has passed, then the ancestor is
            # replaced by a junction to the outside tree, then the open runs.
            os.rename(base, renamed)
            _winapi.CreateJunction(str(payload), str(base))

    monkeypatch.setattr(resolver, "_lstat_reparse_walk", walk_then_swap)
    try:
        with pytest.raises(resolver.TypedResourceChannelError):
            resolver.resolve_namespace_identity(derived)
    finally:
        if base.exists():
            os.rmdir(str(base))  # remove the junction only
    assert fired, "injection never fired -> the test would be inconclusive"


# ---------------------------------------------------------------------------
# Link policy (AC2 decision): external ancestor link = allowed while identity
# stays the same; internal link below the root = refused.
# ---------------------------------------------------------------------------


def test_ancestor_junction_is_allowed_for_legal_reads(harness):
    """The stable ``live -> real`` ancestor junction is legal usage (AC2)."""

    reader = harness.core.render._original_page_reader
    assert reader(harness.page_id) == harness.legal_bytes()
    assert harness.core.page_catalog.image_state(harness.page_id, "original") == "ok"
    assert harness.core.page_catalog.image_url(harness.page_id, "original")


def test_internal_link_below_the_root_is_refused(harness):
    """A link inside the managed layout must not alias another managed file."""

    import _winapi

    from bootstrap.core_service import CoreServiceServer, P16WireError

    original_dir = harness.live_path().parent
    sibling_dir = original_dir.parent / "masks"
    sibling_dir.mkdir(parents=True, exist_ok=True)
    sibling = sibling_dir / harness.live_path().name
    sibling.write_bytes(b"SIBLING - a different managed file")
    moved = harness.live_path().parent.with_name(original_dir.name + "-real")
    os.rename(original_dir, moved)
    _winapi.CreateJunction(str(sibling_dir), str(original_dir))
    try:
        live = str(harness.live_path())
        with pytest.raises(P16WireError):
            CoreServiceServer(harness.core)._checked_managed_path(live)
        # The sibling file is untouched and the reference was not re-pointed.
        assert sibling.read_bytes() == b"SIBLING - a different managed file"
    finally:
        os.rmdir(str(original_dir))


# ---------------------------------------------------------------------------
# Primitive unit checks (shared by all sites)
# ---------------------------------------------------------------------------


def test_trust_snapshot_reads_legal_reference_and_refuses_outside(harness, tmp_path):
    from infrastructure.resource_channel.handle_resolver import (
        E_OUT_OF_SCOPE,
        ManagedRootTrust,
        TypedResourceChannelError,
    )

    trust = ManagedRootTrust.capture(harness.managed)
    assert trust.read_bytes(harness.ref()) == harness.legal_bytes()
    assert Path(trust.canonical_of(harness.ref())) == harness.real_path()
    assert Path(trust.verify_existing(str(harness.live_path()))) == harness.real_path()

    outside_file = tmp_path / "outside.png"
    outside_file.write_bytes(b"outside")
    with pytest.raises(TypedResourceChannelError) as excinfo:
        trust.read_bytes(str(outside_file))
    assert excinfo.value.code == E_OUT_OF_SCOPE

    with pytest.raises(TypedResourceChannelError) as excinfo:
        trust.read_bytes("../outside.png")
    assert excinfo.value.code == E_OUT_OF_SCOPE
