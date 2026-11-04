"""AC11-1/AC11-2 evidence: scan/diff classification, totals=details, plan
binding and the stale-apply zero-write baseline.

Real SQLite (v8), real HMAC-signed grants over real zip files, real strict
verified reads — no fakes on the scan/diff path.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    build_plan_body,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)

pytestmark = pytest.mark.usefixtures()


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed_two_page_source(conn, scratch_dir):
    """Old zip container with pages 1/2 bound to book b1."""
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(scratch_dir / "old.zip", [("001.png", page1), ("002.png", page2)])
    container_digest = _digest(zip_path.read_bytes())
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=container_digest,
        entries=[("e1", "001.png", _digest(page1)), ("e2", "002.png", _digest(page2))],
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return zip_path, page1, page2, container_digest


def test_scan_same_container_direct_continuation(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-3 path 1: same container digest → every item unchanged/direct."""
    zip_path, _p1, _p2, container_digest = _seed_two_page_source(conn, scratch_dir)
    grant_id, _facts = mint_grant(
        registry,
        source_id="s1",
        kind="zip",
        entries=[(zip_path, "old.zip", 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1",
            "project_ids": ["b1"],
            "scope": "current",
            "kind": "resync",
            "grant_ids": [grant_id],
            "missing": [],
        }
    )
    assert scan["source"]["status"] == "ok"
    assert scan["source"]["content_digest"] == container_digest
    assert scan["source"]["version_id"] == "sv1"  # committed version reused
    assert scan["totals"] == {"unchanged": 2, "added": 0, "missing": 0,
                              "changed": 0, "ambiguous": 0}
    for item in scan["diff"]:
        assert item["classification"] == "unchanged"
        assert item["evidence"] == "direct"
        assert item["old_entry_id"] == item["new_entry_id"]
    # totals must equal the detailed classification counts (AC11-2)
    counts = {key: 0 for key in scan["totals"]}
    for item in scan["diff"]:
        counts[item["classification"]] += 1
    assert counts == scan["totals"]


def test_scan_changed_container_diff_classifications(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-2/AC11-3: added / missing / unchanged(unique_pixel) all appear."""
    zip_path, page1, page2, _digest_old = _seed_two_page_source(conn, scratch_dir)
    # New container: page1 kept (same bytes), page2 removed, page3 added.
    new_zip = write_zip(
        scratch_dir / "new.zip",
        [("001.png", page1), ("003.png", png_bytes(color=(0, 0, 255)))],
    )
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(new_zip, "new.zip", 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    assert scan["source"]["content_digest"] == _digest(new_zip.read_bytes())
    assert scan["source"]["version_id"] != "sv1"  # Core assigned a new id
    by_class = {}
    for item in scan["diff"]:
        by_class.setdefault(item["classification"], []).append(item)
    assert len(by_class["unchanged"]) == 1
    assert by_class["unchanged"][0]["evidence"] == "unique_pixel"
    assert by_class["unchanged"][0]["page_id"] == "p1"
    assert len(by_class["missing"]) == 1
    assert by_class["missing"][0]["page_id"] == "p2"
    assert by_class["missing"][0]["new_entry_id"] is None
    assert len(by_class["added"]) == 1
    assert by_class["added"][0]["page_id"] is None
    assert scan["totals"] == {"unchanged": 1, "added": 1, "missing": 1,
                              "changed": 0, "ambiguous": 0}


def test_scan_same_mtime_size_bytes_changed_discovered(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-1: same mtime/size but different bytes must be discovered (the
    strong verification is a digest, never a stat hint)."""
    page1 = png_bytes(color=(255, 0, 0))
    zip_path = write_zip(scratch_dir / "same.zip", [("001.png", page1)])
    container_digest = _digest(zip_path.read_bytes())
    add_source_tree(
        conn, source_id="s1", version_id="sv1", digest=container_digest,
        entries=[("e1", "001.png", _digest(page1))],
        legacy_v7_evidence=False,
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    # Same length, same name, different bytes.
    replaced = write_zip(
        scratch_dir / "same.zip", [("001.png", png_bytes(color=(9, 9, 9)))]
    )
    assert replaced.stat().st_size == zip_path.stat().st_size
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip", entries=[(replaced, "same.zip", 0)]
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    assert scan["source"]["content_digest"] != container_digest
    assert scan["totals"]["changed"] == 1
    assert scan["totals"]["unchanged"] == 0


def test_scan_expired_grant_typed_refusal(conn, registry, stack, book_chapter, scratch_dir):
    """AC11-1: the strong verification is a live lease+digest, not a cache."""
    zip_path, page1 = None, png_bytes()
    del zip_path, page1
    from tests.fea11.conftest import file_facts

    target = write_zip(scratch_dir / "x.zip", [("001.png", png_bytes())])
    grant_id, _ = mint_grant(
        registry, source_id="s1", kind="zip", entries=[(target, "x.zip", 0)]
    )
    registry.revoke_grant_ids([grant_id])
    with pytest.raises(Exception) as caught:
        stack["scanner"].scan(
            {
                "source_id": "s1", "project_ids": ["b1"], "scope": "current",
                "kind": "resync", "grant_ids": [grant_id], "missing": [],
            }
        )
    assert caught.value.code == "SOURCE_GRANT_REVOKED"
    del file_facts


def test_scan_scope_all_requires_frozen_reference_books(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-2/§5.3: scope=all project set must equal the frozen reference
    set's distinct books."""
    zip_path, page1, page2, digest = _seed_two_page_source(conn, scratch_dir)
    grant_id, _ = mint_grant(
        registry, source_id="s1", kind="zip", entries=[(zip_path, "old.zip", 0)]
    )
    with pytest.raises(Exception) as caught:
        stack["scanner"].scan(
            {
                "source_id": "s1", "project_ids": ["b1", "b2"],
                "scope": "all", "kind": "resync",
                "grant_ids": [grant_id], "missing": [],
            }
        )
    assert caught.value.code == "SOURCE_PLAN_STALE"
    assert caught.value.details["cause"] == "scope"
    del page2


def test_missing_source_observation_path(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-7 prerequisite: a Host missing observation cross-checked against
    the Core rows yields a missing SourceObservation with no grants."""
    zip_path, page1, _p2, digest = _seed_two_page_source(conn, scratch_dir)
    from application.sources.model import identity_digest_of

    location = stack["store"].get_source_location_current("s1")
    identity = identity_digest_of(
        location["content_digest"], location["volume_serial"],
        location["file_id"], location["size_bytes"],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [],
            "missing": [
                {
                    "source_id": "s1", "registry_id": "reg-1", "generation": 1,
                    "expected_identity_digest": identity,
                    "observed_at": "2026-11-04T00:00:00.000Z",
                }
            ],
        }
    )
    assert scan["source"]["status"] == "missing"
    assert scan["source"]["reason_code"] == "SOURCE_ENTRY_MISSING"
    assert scan["source"]["entries"] == []
    # Wrong identity digest → typed stale refusal (no forgery).
    with pytest.raises(Exception) as caught:
        stack["scanner"].scan(
            {
                "source_id": "s1", "project_ids": ["b1"], "scope": "current",
                "kind": "resync", "grant_ids": [],
                "missing": [
                    {
                        "source_id": "s1", "registry_id": "reg-1",
                        "generation": 1,
                        "expected_identity_digest": "0" * 64,
                        "observed_at": "2026-11-04T00:00:00.000Z",
                    }
                ],
            }
        )
    assert caught.value.code == "SOURCE_PLAN_STALE"
    del zip_path, page1, digest


def test_stale_apply_zero_write_baseline(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-4/AC11-2: a stale apply writes NOTHING — the §6.2 zero-write
    comparison set is checked table-by-table."""
    from application.sources.model import request_digest_of

    from tests.fea11.conftest import host_authorization

    zip_path, page1, _page2, _digest = _seed_two_page_source(conn, scratch_dir)
    new_zip = write_zip(
        scratch_dir / "new.zip",
        [("001.png", page1), ("002.png", png_bytes(color=(9, 9, 9)))],
    )
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip", entries=[(new_zip, "new.zip", 0)]
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    body = build_plan_body(scan)
    plan = stack["planner"].create(body)
    stack["planner"].preview(
        {"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]}
    )
    stack["planner"].confirm(
        {
            "plan_id": body["plan_id"], "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )

    def snapshot() -> dict:
        rows = {}
        for table in (
            "pages", "page_bindings", "source_locations", "source_versions",
            "source_entries", "regions", "region_revisions",
            "source_sync_plans", "source_operations",
            "source_binding_publications", "source_revision_lineage",
        ):
            rows[table] = sorted(
                tuple(row) for row in conn.execute(
                    f"SELECT * FROM {table}"
                ).fetchall()
            )
        return rows

    before = snapshot()
    # Tamper: drift the binding between confirm and apply → stale, zero write.
    conn.execute(
        "UPDATE pages SET source_order = 99 WHERE page_id = 'p1'"
    )
    conn.commit()
    operation_id = "op-stale-00000001"
    request_digest = request_digest_of(
        operation_id, body["plan_id"], plan["plan_digest"], "resync"
    )
    with pytest.raises(Exception) as caught:
        stack["service"].apply(
            "ResyncSource",
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
    assert caught.value.code == "SOURCE_PLAN_STALE"
    after_drift = snapshot()
    # Revert the tamper and prove the failed apply itself changed nothing
    # beyond the pre-apply tamper row (pages row differs only by tamper).
    conn.execute("UPDATE pages SET source_order = 1 WHERE page_id = 'p1'")
    conn.commit()
    assert snapshot() == before
    del after_drift


def test_full_sync_publishes_new_generation_and_gates(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-5 smoke: one resync keeps PageId, bumps binding generation,
    inserts pending publications and preserves user order."""
    zip_path, page1, _p2, _digest = _seed_two_page_source(conn, scratch_dir)
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip", entries=[(new_zip, "new.zip", 0)]
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="resync"
    )
    assert dispatch["accepted"] is True
    assert dispatch["state"] == "core-committed"
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    assert operation["commit_digest"]
    new_binding = stack["store"].current_binding_of_page("p1")
    assert new_binding["binding_version"] == 2
    assert new_binding["previous_binding_id"] == "pb-p1"
    gate = stack["store"].gate_of_binding(new_binding["binding_id"])
    assert gate["read_gate"] == "pending"
    assert gate["relation"] == "same_content"
    # plan is applied; a second apply of the same operation replays.
    replay = stack["service"].apply(
        "ResyncSource",
        {
            "operation_id": dispatch["operation_id"],
            "plan_id": plan["body"]["plan_id"],
            "plan_digest": plan["plan_digest"],
            "grant_ids": [grant_id],
            "authorization": host_authorization_for_replay(
                stack, dispatch, plan, grant_id, scan
            ),
        },
    )
    assert replay["state"] == "core-committed"
    # Only one binding generation beyond the original (no second publish).
    assert conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
    ).fetchone()[0] == 2


def host_authorization_for_replay(stack, dispatch, plan, grant_id, scan):
    from tests.fea11.conftest import host_authorization

    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    return host_authorization(
        operation_id=dispatch["operation_id"],
        request_digest=operation["request_digest"],
        authorizations=scan["authorizations"],
    )
