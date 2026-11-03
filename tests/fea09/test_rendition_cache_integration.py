"""R1-I008: production resolve uses the constrained rendition cache."""

from __future__ import annotations

import hashlib
import io
import time
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from support import FakeSourceReadAccess, HookDecoder, build_runtime

GRANT = "g-img-0000000001"
OP = "op-0000000000000040"


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _import_page(tmp_path, repo, decoder):
    access = FakeSourceReadAccess()
    source = tmp_path / "page.png"
    source.write_bytes(Path("tests/fea09/support.py").read_bytes()[:0] or b"")
    # Use the shared PNG generator through a tiny in-memory image.
    buffer = io.BytesIO()
    Image.new("RGB", (6, 4), (12, 200, 40)).save(buffer, format="PNG")
    source.write_bytes(buffer.getvalue())
    access.add_file(GRANT, "image", source)
    runtime = build_runtime(repo, access, decoder=decoder)
    plan = runtime._planner.plan(chapter_id="c1", grants=[GRANT], duplicate_policy="skip")
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=[GRANT], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    page = repo.list_pages("c1")[0]
    return access, page


def _build_server(tmp_path, repo, access, decoder):
    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher
    from infrastructure.resource_channel.rendition_cache import RenditionCache

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived = tmp_path / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived)
    publisher = RenderPreviewPublisher(derived, ResourceCatalogStore(catalog_db))
    cache = RenditionCache(
        data_root=tmp_path, derived_root=derived, connection=repo._conn
    )
    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        repository=repo,
        source_read_refs=access,
        rendition_cache=cache,
        image_decoder=decoder,
        document_raster=None,
        managed_root_trust=None,
    )
    server._render_previews = publisher
    return server, cache, derived


def test_resolve_uses_rendition_cache_and_rebuilds_corruption(
    tmp_path, repo, book_chapter
):
    decoder = HookDecoder()
    access, page = _import_page(tmp_path, repo, decoder)
    server, cache, derived = _build_server(tmp_path, repo, access, decoder)
    import application.importing.referenced.resolve as resolve_module

    produce_calls: list[int] = []
    original_render = resolve_module.render_prepared_rendition

    def _counting_render(prepared, **kwargs):
        produce_calls.append(1)
        return original_render(prepared, **kwargs)

    resolve_module.render_prepared_rendition = _counting_render

    first = server.handle_resolve_page_resource({"page_id": page.page_id})
    assert first["resource_id"] == f"page-rendition-{page.page_id}"
    assert len(produce_calls) == 1

    rows = repo._conn.execute(
        "SELECT cache_key,rel_path,size_bytes,content_digest,source_id,"
        "version_id,entry_id,rendition_kind FROM rendition_cache"
    ).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert len(row["cache_key"]) == 64
    assert row["rel_path"] == f"source-renditions/{row['cache_key']}.bin"
    cached_path = derived / row["rel_path"]
    data = cached_path.read_bytes()
    assert len(data) == row["size_bytes"]
    assert hashlib.sha256(data).hexdigest() == row["content_digest"]
    binding = repo.get_page_binding(page.page_id)
    assert (row["source_id"], row["version_id"], row["entry_id"]) == (
        binding["source_id"], binding["accepted_source_version"],
        binding["entry_id"],
    )
    assert row["rendition_kind"] == "page_preview"

    # Second resolve is a cache hit: no second decode, same catalog key.
    second = server.handle_resolve_page_resource({"page_id": page.page_id})
    assert second["resource_id"] == first["resource_id"]
    assert len(produce_calls) == 1

    # A corrupted cache file is dropped and rebuilt by the cache itself.
    cached_path.write_bytes(b"corrupted")
    third = server.handle_resolve_page_resource({"page_id": page.page_id})
    assert third["resource_id"] == first["resource_id"]
    assert len(produce_calls) == 2
    rebuilt = repo._conn.execute(
        "SELECT rel_path,size_bytes,content_digest FROM rendition_cache"
    ).fetchone()
    assert rebuilt["size_bytes"] == len((derived / rebuilt["rel_path"]).read_bytes())
    assert (
        hashlib.sha256((derived / rebuilt["rel_path"]).read_bytes()).hexdigest()
        == rebuilt["content_digest"]
    )
