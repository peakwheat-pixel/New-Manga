"""AC11-9 evidence: the C-17 §7.2 binding-scoped v2 rendition key.

The legacy ``page-rendition-{page_id}`` key stays immutable; referenced
resolves select ``page-rendition-v2-<digest>`` over (page, binding, source,
version, entry, verified digest, rendition kind, decoder name/version, params
digest). A different binding or decoder profile necessarily selects a
different key, and a same-key/different-bytes publication is a typed refusal.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from bootstrap.core_service import CoreServiceServer
from application.importing.referenced.errors import SourceImportError


def _prepared(**overrides):
    binding = {
        "page_id": "p1",
        "binding_id": "pb1",
        "source_id": "s1",
        "accepted_source_version": "sv1",
        "entry_id": "se1",
        "verified_digest": "a" * 64,
    }
    prepared = {
        "binding": binding,
        "rendition_kind": "page_preview",
        "decoder_name": "pillow",
        "decoder_version": "1",
        "params_digest": "b" * 64,
    }
    prepared.update(overrides)
    return prepared


def _server():
    return object.__new__(CoreServiceServer)


def test_v2_key_is_deterministic_and_binding_scoped():
    server = _server()
    first = server._referenced_resource_id(_prepared())
    second = server._referenced_resource_id(_prepared())
    assert first == second
    assert first.startswith("page-rendition-v2-")
    assert len(first) == len("page-rendition-v2-") + 64

    # The binding is part of the key: switching bindings selects a new key.
    other_binding = dict(_prepared()["binding"], binding_id="pb2")
    assert server._referenced_resource_id(_prepared(binding=other_binding)) != first
    # The legacy key is never selected.
    assert server._referenced_resource_id(_prepared()) != "page-rendition-p1"


def test_key_changes_with_decoder_profile_and_version():
    server = _server()
    base = server._referenced_resource_id(_prepared())
    assert server._referenced_resource_id(_prepared(decoder_name="pdfium")) != base
    assert server._referenced_resource_id(_prepared(decoder_version="2")) != base
    assert server._referenced_resource_id(_prepared(params_digest="c" * 64)) != base
    assert server._referenced_resource_id(_prepared(rendition_kind="page_full")) != base


def test_verified_digest_participates_in_the_key():
    server = _server()
    base = server._referenced_resource_id(_prepared())
    binding = dict(_prepared()["binding"], verified_digest="d" * 64)
    assert server._referenced_resource_id(_prepared(binding=binding)) != base


def test_canonical_shape_matches_the_frozen_definition():
    """The digest input is exactly the C-17 §7.2 canonical object."""
    from application.sources.model import digest_of

    server = _server()
    prepared = _prepared()
    expected = "page-rendition-v2-" + digest_of(
        {
            "page_id": "p1",
            "binding_id": "pb1",
            "source_id": "s1",
            "version_id": "sv1",
            "entry_id": "se1",
            "verified_digest": "a" * 64,
            "rendition_kind": "page_preview",
            "decoder_name": "pillow",
            "decoder_version": "1",
            "params_digest": "b" * 64,
        }
    )
    assert server._referenced_resource_id(prepared) == expected


def test_same_key_different_bytes_is_a_typed_refusal(tmp_path):
    """C-17 §7.2: an already-published digest is never replaced."""
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import (
        RenderPreviewPublisher,
    )

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    publisher = RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db))

    server = _server()
    server._render_previews = publisher
    key = server._referenced_resource_id(_prepared())

    def png(color):
        import io

        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGBA", (4, 3), color + (255,)).save(buffer, format="PNG")
        return buffer.getvalue()

    published = server._publish_rendition_bytes(key, png((255, 0, 0)))
    assert published["resource_id"] == key
    # Same key, same bytes: idempotent.
    assert server._publish_rendition_bytes(key, png((255, 0, 0)))["resource_id"] == key
    # Same key, different bytes: typed refusal, original stays published.
    with pytest.raises(SourceImportError) as error:
        server._publish_rendition_bytes(key, png((0, 255, 0)))
    assert error.value.code == "SOURCE_ACCESS_DENIED"
    entry = publisher.lookup(key)
    assert entry is not None
    assert (derived_root / entry.rel_path).read_bytes() == png((255, 0, 0))
