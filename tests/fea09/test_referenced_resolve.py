"""FEA-09 AC-6/AC-7: referenced production resolve path.

Pins the C-15 §4.2 rule: a referenced page resolves only through a live
source-read grant, renders a decoded/re-encoded PNG rendition (never raw
user-source bytes), and stays typed when the grant is missing/revoked.
"""

from __future__ import annotations

import io
import time

import pytest
from PIL import Image

from support import FakeSourceReadAccess, build_runtime, png_bytes
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.resolve import resolve_referenced_rendition

OP = "op-0000000000000010"
GRANT = "g-img-0000000001"


def _jpeg_bytes(width: int = 6, height: int = 4) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (10, 120, 200)).save(buffer, format="JPEG")
    return buffer.getvalue()


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _imported_image_page(tmp_path, repo):
    access = FakeSourceReadAccess()
    path = tmp_path / "photo.jpg"
    path.write_bytes(_jpeg_bytes())
    access.add_file(GRANT, "image", path)
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=[GRANT], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1",
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=[GRANT],
        duplicate_policy="skip",
        operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    pages = repo.list_pages("c1")
    assert len(pages) == 1
    return access, pages[0]


def test_referenced_resolve_renders_png_through_grant(tmp_path, repo, book_chapter):
    access, page = _imported_image_page(tmp_path, repo)
    binding = repo.get_page_binding(page.page_id)
    assert binding["status"] == "healthy"
    access._grant_sources[GRANT] = binding["source_id"]

    result = resolve_referenced_rendition(
        page.page_id, repository=repo, access=access
    )
    assert result["png"].startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(io.BytesIO(result["png"])) as image:
        assert image.size == (6, 4)
    assert result["verified_digest"] == binding["verified_digest"]
    assert result["entry_id"] == binding["entry_id"]
    # Re-encoded rendition, not raw user-source bytes (JPEG -> PNG).
    assert result["png"] != (tmp_path / "photo.jpg").read_bytes()


def test_referenced_resolve_without_grant_is_typed_denied(tmp_path, repo, book_chapter):
    _access, page = _imported_image_page(tmp_path, repo)
    # A fresh access with no grant at all: neither source-id nor physical
    # identity matching can authorize the read.
    empty = FakeSourceReadAccess()
    with pytest.raises(SourceImportError) as caught:
        resolve_referenced_rendition(page.page_id, repository=repo, access=empty)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


def test_referenced_resolve_revoked_grant_is_typed(tmp_path, repo, book_chapter):
    access, page = _imported_image_page(tmp_path, repo)
    binding = repo.get_page_binding(page.page_id)
    access._grant_sources[GRANT] = binding["source_id"]
    access.revoke(GRANT)
    with pytest.raises(SourceImportError) as caught:
        resolve_referenced_rendition(page.page_id, repository=repo, access=access)
    assert caught.value.code == "SOURCE_GRANT_REVOKED"


def test_core_resolve_publishes_referenced_rendition(tmp_path, repo, book_chapter):
    """Core wire face: referenced resolve publishes a deterministic rendition key."""
    from types import SimpleNamespace

    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher

    access, page = _imported_image_page(tmp_path, repo)
    binding = repo.get_page_binding(page.page_id)
    access._grant_sources[GRANT] = binding["source_id"]

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    publisher = RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db))

    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        repository=repo, source_read_refs=access,
        image_decoder=None, document_raster=None,
    )
    server._render_previews = publisher

    result = server.handle_resolve_page_resource({"page_id": page.page_id})
    resource_id = f"page-rendition-{page.page_id}"
    assert result == {"resource_id": resource_id, "revision": "original"}
    entry = publisher.lookup(resource_id)
    assert entry is not None and publisher.artifact_exists(entry.rel_path)
    published = (derived_root / entry.rel_path).read_bytes()
    assert published.startswith(b"\x89PNG\r\n\x1a\n")
    # Idempotent: the second resolve is a catalog hit (no new publication).
    again = server.handle_resolve_page_resource({"page_id": page.page_id})
    assert again == result
    assert len(list((derived_root / "pages").iterdir())) == 1


def test_rendition_cache_row_written_on_resolve(tmp_path, repo, book_chapter):
    from types import SimpleNamespace

    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher

    access, page = _imported_image_page(tmp_path, repo)
    binding = repo.get_page_binding(page.page_id)
    access._grant_sources[GRANT] = binding["source_id"]

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    publisher = RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db))
    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        repository=repo, source_read_refs=access,
        image_decoder=None, document_raster=None,
    )
    server._render_previews = publisher

    server.handle_resolve_page_resource({"page_id": page.page_id})
    row = repo._conn.execute(
        "SELECT cache_key, source_id, version_id, entry_id, rendition_kind,"
        " decoder_name, params_digest, rel_path, size_bytes, content_digest"
        " FROM rendition_cache"
    ).fetchone()
    assert row is not None
    assert row["source_id"] == binding["source_id"]
    assert row["version_id"] == binding["accepted_source_version"]
    assert row["entry_id"] == binding["entry_id"]
    assert row["rendition_kind"] == "page_preview"
    assert row["decoder_name"] == "pillow"
    assert len(row["params_digest"]) == 64
    assert row["rel_path"].startswith("pages/")
    assert row["size_bytes"] > 0 and len(row["content_digest"]) == 64


def test_render_entry_png_enforces_decode_budget(tmp_path):
    from support import capture_facts
    from application.importing.referenced.model import (
        ResolvedSourceRead,
        ScannedEntry,
        SourceReadBudget,
    )
    from application.importing.referenced.reader import render_entry_png

    path = tmp_path / "photo.jpg"
    path.write_bytes(_jpeg_bytes())
    resolved = ResolvedSourceRead(
        grant_id="g-img-0000000001",
        registry_id="reg-1",
        generation=1,
        source_kind="image",
        budget=SourceReadBudget(
            max_bytes=1024 * 1024, max_decode_bytes=8, max_entries=10
        ),
        expires_at=1e12,
        container_path=str(path),
        container_facts=capture_facts(path),
    )
    entry = ScannedEntry(
        locator="photo.jpg", ordinal=0, size_bytes=path.stat().st_size,
        content_digest=None, content_digest_kind="encoded",
    )
    with pytest.raises(SourceImportError) as caught:
        render_entry_png(resolved, entry)
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"


def test_dual_read_managed_and_referenced_resolve(tmp_path, repo, book_chapter):
    """AC-7: managed and referenced pages coexist and both resolve."""
    from types import SimpleNamespace

    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher
    from conftest import add_managed_page

    access = FakeSourceReadAccess()
    source = tmp_path / "ref.jpg"
    source.write_bytes(_jpeg_bytes())
    access.add_file(GRANT, "image", source)
    runtime = build_runtime(repo, access)
    # Import one referenced page into c1.
    plan = runtime._planner.plan(chapter_id="c1", grants=[GRANT], duplicate_policy="skip")
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=[GRANT], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    referenced = repo.list_pages("c1")[-1]
    binding = repo.get_page_binding(referenced.page_id)
    access._grant_sources[GRANT] = binding["source_id"]
    managed_id = "p-managed-dual"
    add_managed_page(repo._conn, managed_id)

    class _Trust:
        def read_bytes(self, ref):
            return png_bytes(4, 4)

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    publisher = RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db))
    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        repository=repo, source_read_refs=access, managed_root_trust=_Trust(),
        image_decoder=None, document_raster=None,
    )
    server._render_previews = publisher

    managed_result = server.handle_resolve_page_resource({"page_id": managed_id})
    referenced_result = server.handle_resolve_page_resource(
        {"page_id": referenced.page_id}
    )
    assert managed_result["resource_id"] == f"page-original-{managed_id}"
    assert referenced_result["resource_id"] == f"page-rendition-{referenced.page_id}"
    assert publisher.artifact_exists(
        publisher.lookup(managed_result["resource_id"]).rel_path
    )
    assert publisher.artifact_exists(
        publisher.lookup(referenced_result["resource_id"]).rel_path
    )
