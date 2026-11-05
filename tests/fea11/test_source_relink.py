"""AC11-6 evidence: relink / repoint / resync are distinct operations.

relink = the SAME physical file renamed/moved (content unchanged): binding,
PageId and user order survive; only the location baseline is refreshed.
repoint = point at ANOTHER file: entry identity changes; changed content
requires the resync confirmation.  A changed container never passes relink.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    build_plan_body,
    file_facts,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)
from application.sources.errors import SourceSyncError
from application.sources.model import request_digest_of


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed(conn, scratch_dir):
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(
        scratch_dir / "old.zip", [("001.png", page1), ("002.png", page2)]
    )
    digest = _digest(zip_path.read_bytes())
    facts = file_facts(zip_path)
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=digest,
        entries=[
            ("e1", "001.png", _digest(page1)),
            ("e2", "002.png", _digest(page2)),
        ],
        legacy_v7_evidence=False,
        volume_serial=facts["volume_serial"],
        file_id=facts["file_id"],
    )
    # DSH 2026-11-06 窄批 W1b: the repoint/changed device needs a genuinely
    # complete old pixel profile (AC-M4 makes W/H-only evidence missing_old).
    from tests.fea11.test_source_sync import _seed_complete_pixel_profiles

    _seed_complete_pixel_profiles(
        conn, "sv1", {"001.png": page1, "002.png": page2}
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return zip_path, page1, page2, digest


def _scan_with_container(stack, registry, path, *, kind):
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(path, path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": kind, "grant_ids": [grant_id], "missing": [],
        }
    )
    return grant_id, scan


def test_relink_renamed_same_container_keeps_binding_and_page(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-6: renaming/moving the SAME container is a relink — PageId,
    binding generation and user order survive; the location baseline is
    refreshed to the live grant."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    renamed = scratch_dir / "old-renamed.zip"
    zip_path.rename(renamed)  # really the same file: same inode, new path
    grant_id, scan = _scan_with_container(stack, registry, renamed, kind="relink")
    assert scan["totals"] == {
        "unchanged": 2, "added": 0, "missing": 0, "changed": 0, "ambiguous": 0,
    }
    plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="relink", command="RelinkSource"
    )
    assert dispatch["state"] == "core-committed"
    binding = stack["store"].current_binding_of_page("p1")
    assert binding["binding_version"] == 1  # no new generation on relink
    assert binding["page_id"] == "p1"
    page = conn.execute(
        "SELECT source_order FROM pages WHERE page_id = 'p1'"
    ).fetchone()
    assert page["source_order"] == 1  # user order untouched
    location = stack["store"].get_source_location_current("s1")
    assert location["location_id"] == "sl-s1"
    assert location["authorization_generation"] == 1
    # The plan itself is applied and the operation carries a receipt.
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    assert operation["state"] == "core-committed"
    assert operation["commit_digest"]


def test_relink_rejects_an_identical_copy_as_a_new_physical_file(
    conn, registry, stack, book_chapter, scratch_dir
):
    """R-006 (FEA-11 r1): same bytes, different physical file = a copy, not a
    relink; it must be repointed/resynced instead."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    copied = scratch_dir / "old-copied.zip"
    copied.write_bytes(zip_path.read_bytes())
    grant_id, scan = _scan_with_container(stack, registry, copied, kind="relink")
    with pytest.raises(SourceSyncError) as error:
        run_full_sync(
            stack, scan, grant_ids=[grant_id], kind="relink",
            command="RelinkSource",
        )
    assert error.value.code == "SOURCE_SYNC_STATE_CONFLICT"


def test_relink_rejects_changed_container(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-6: relink never accepts a changed container — that is resync."""
    zip_path, page1, _page2, _digest_before = _seed(conn, scratch_dir)
    changed = write_zip(
        scratch_dir / "changed.zip", [("001.png", png_bytes(color=(7, 7, 7)))]
    )
    grant_id, scan = _scan_with_container(stack, registry, changed, kind="relink")
    with pytest.raises(Exception) as caught:
        run_full_sync(
            stack, scan, grant_ids=[grant_id], kind="relink", command="RelinkSource"
        )
    assert caught.value.code == "SOURCE_SYNC_STATE_CONFLICT"


def test_repoint_changed_content_requires_resync_confirmation(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-6/C-14: repointing to a different file whose content changed is
    only allowed together with the explicit resync confirmation."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    other = write_zip(
        scratch_dir / "other.zip",
        [("001.png", png_bytes(color=(0, 0, 255))),
         ("002.png", png_bytes(color=(128, 0, 128)))],
    )
    grant_id, scan = _scan_with_container(stack, registry, other, kind="repoint")
    body = build_plan_body(scan, kind="repoint", resync_content=False)
    with pytest.raises(Exception) as caught:
        stack["planner"].create(body)
    assert caught.value.code == "INVALID_REQUEST"
    return
    plan = stack["planner"].create(body)
    stack["planner"].preview(
        {"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]}
    )
    stack["planner"].confirm(
        {
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )
    operation_id = "op-repoint-noconfirm"
    request_digest = request_digest_of(
        operation_id, body["plan_id"], plan["plan_digest"], "repoint"
    )
    with pytest.raises(Exception) as caught:
        stack["service"].apply(
            "RepointSource",
            {
                "operation_id": operation_id,
                "plan_id": body["plan_id"],
                "plan_digest": plan["plan_digest"],
                "grant_ids": [grant_id],
                "authorization": host_authorization(
                    operation_id=operation_id,
                    request_digest=request_digest,
                    authorizations=scan["authorizations"],
                ),
            },
        )
    assert caught.value.code in (
        "INVALID_REQUEST", "SOURCE_SYNC_STATE_CONFLICT", "SOURCE_PLAN_STALE",
    )


def test_repoint_with_resync_confirmation_publishes_new_binding(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-6: an explicitly confirmed repoint publishes the new file."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    other = write_zip(
        scratch_dir / "other.zip",
        [("001.png", png_bytes(color=(5, 5, 5))), ("002.png", png_bytes())],
    )
    grant_id, scan = _scan_with_container(stack, registry, other, kind="repoint")
    plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="repoint",
        command="RepointSource",
    )
    assert dispatch["state"] == "core-committed"
    binding = stack["store"].current_binding_of_page("p1")
    assert binding["binding_version"] == 2
    assert binding["previous_binding_id"] == "pb-p1"
