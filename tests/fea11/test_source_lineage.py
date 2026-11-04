"""AC11-5 evidence: the first sync switch captures the current region
revision onto the OLD binding (captured_v7); historical revisions stay
legacy_unverified (read diagnosis only) and later switches keep the frozen
attribution instead of re-writing lineage."""

from __future__ import annotations

import hashlib
import json

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed_with_region(conn, scratch_dir):
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(
        scratch_dir / "old.zip", [("001.png", page1), ("002.png", page2)]
    )
    digest = _digest(zip_path.read_bytes())
    add_source_tree(
        conn, source_id="s1", version_id="sv1", digest=digest,
        entries=[("e1", "001.png", _digest(page1)),
                 ("e2", "002.png", _digest(page2))],
        legacy_v7_evidence=False,
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    now = "2026-11-04T00:00:00.000+00:00"
    geometry = json.dumps({
        "x": 0.1, "y": 0.1, "width": 0.5, "height": 0.4,
    }, separators=(",", ":"))
    snapshot = json.dumps({"text": "旧翻译"}, ensure_ascii=False,
                          separators=(",", ":"))
    conn.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order,"
        " geometry_json, text_json, style_json, sfx_policy, region_locked,"
        " translation_locked, inpaint_locked, created_at, updated_at)"
        " VALUES ('rg1', 'p1', 'speech', 0, ?, '{}', '{}', 'skip', 0, 0, 0, ?, ?)",
        (geometry, now, now),
    )
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id,"
        " revision_no, snapshot_json, origin, review_state, is_pinned,"
        " created_at) VALUES ('rv1', 'rg1', 1, ?, 'machine', 'confirmed', 0, ?)",
        (snapshot, now),
    )
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id,"
        " revision_no, snapshot_json, origin, review_state, is_pinned,"
        " created_at) VALUES ('rv2', 'rg1', 2, ?, 'user', 'confirmed', 0, ?)",
        (snapshot, now),
    )
    conn.execute(
        "UPDATE regions SET current_revision_id = 'rv2' WHERE region_id = 'rg1'"
    )
    conn.commit()
    return zip_path, page1, page2, digest


def _scan_changed(stack, registry, scratch_dir, *, base_color):
    new_zip = write_zip(
        scratch_dir / "new.zip",
        [("001.png", png_bytes(color=base_color)), ("002.png", png_bytes())],
    )
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(new_zip, new_zip.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    return grant_id, scan


def test_first_switch_captures_current_revision_on_old_binding(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-5: the first switch snapshots the current revision onto the old
    binding and marks earlier revisions legacy_unverified."""
    _zip_path, _page1, _page2, _digest_before = _seed_with_region(
        conn, scratch_dir
    )
    grant_id, scan = _scan_changed(
        stack, registry, scratch_dir, base_color=(0, 0, 255)
    )
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    operation_id = dispatch["operation_id"]
    binding = stack["store"].current_binding_of_page("p1")
    assert binding["binding_version"] == 2
    assert binding["previous_binding_id"] == "pb-p1"

    current = stack["store"].lineage_of_revision("rv2")
    assert current is not None
    assert current["binding_id"] == "pb-p1"
    assert current["provenance"] == "captured_v7"
    assert current["operation_id"] == operation_id

    historical = stack["store"].lineage_of_revision("rv1")
    assert historical is not None
    assert historical["binding_id"] is None
    assert historical["provenance"] == "legacy_unverified"

    # The old binding keeps its lineage; the new binding starts clean.
    old_lineage = stack["store"].lineage_for_binding("pb-p1")
    assert [row["revision_id"] for row in old_lineage] == ["rv2"]
    assert stack["store"].lineage_for_binding(binding["binding_id"]) == []


def test_second_switch_keeps_existing_lineage_attribution(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-5: a later switch must not re-attribute already captured lineage."""
    _zip_path, _page1, _page2, _digest_before = _seed_with_region(
        conn, scratch_dir
    )
    grant_id, scan = _scan_changed(
        stack, registry, scratch_dir, base_color=(0, 0, 255)
    )
    _plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    first_operation = dispatch["operation_id"]
    # Second switch (same container bytes for the kept page): the run is a
    # fresh operation but the lineage attribution must stay frozen.
    second = write_zip(
        scratch_dir / "new2.zip",
        [("001.png", png_bytes(color=(0, 0, 255)))],
    )
    grant2, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(second, second.name, 0)],
    )
    scan2 = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant2], "missing": [],
        }
    )
    _plan2, dispatch2 = run_full_sync(stack, scan2, grant_ids=[grant2])
    assert dispatch2["operation_id"] != first_operation
    current = stack["store"].lineage_of_revision("rv2")
    assert current["binding_id"] == "pb-p1"  # attribution frozen
    assert current["operation_id"] == first_operation
    historical = stack["store"].lineage_of_revision("rv1")
    assert historical["binding_id"] is None
    assert historical["provenance"] == "legacy_unverified"
