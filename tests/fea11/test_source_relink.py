"""AC11-6 evidence: relink / repoint / resync are distinct operations.

relink = the SAME physical file renamed/moved (content unchanged): binding,
PageId and user order survive; only the location baseline is refreshed.
repoint = point at ANOTHER file: entry identity changes; changed content
requires the resync confirmation.  A changed container never passes relink.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

import pytest

from tests.fea11.conftest import (
    NOW,
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


def _scan_with_container(
    stack, registry, path, *, kind, registry_id="reg-1", generation=1
):
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(path, path.name, 0)],
        registry_id=registry_id,
        generation=generation,
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


# ---------------------------------------------------------------------------
# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A): in-place location auth refresh
# ---------------------------------------------------------------------------


def _iso_timestamp(value: str) -> datetime:
    text = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    assert parsed.tzinfo is not None
    return parsed


def _current_location(conn, source_id: str = "s1"):
    return conn.execute(
        "SELECT * FROM source_locations WHERE source_id = ? AND is_current = 1",
        (source_id,),
    ).fetchone()


def _all_locations(conn, source_id: str = "s1"):
    return conn.execute(
        "SELECT * FROM source_locations WHERE source_id = ? ORDER BY location_id",
        (source_id,),
    ).fetchall()


def _refresh(repo, location, *, registry_id, generation, last_verified_at):
    return repo.refresh_source_location_auth(
        location["source_id"],
        location["content_digest"],
        int(location["volume_serial"]),
        int(location["file_id"]),
        registry_id,
        generation,
        last_verified_at,
    )


def test_refresh_source_location_auth_is_the_single_implementation() -> None:
    """AC-LS4-1: the in-place refresh has exactly ONE SQL implementation.

    Discriminators: restoring the old inline ``UPDATE source_locations`` in
    ``service.py`` (or any second copy) makes the SQL count 2; deleting the
    production call sites drops the caller count below the required two.
    """
    src = Path(__file__).resolve().parents[2] / "src"
    sql_sites: list[str] = []
    call_sites: list[str] = []
    for path in sorted(src.rglob("*.py")):
        relative = path.relative_to(src.parent).as_posix()
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if "UPDATE source_locations SET registry_id" in line:
                sql_sites.append(f"{relative}:{number}")
            if "refresh_source_location_auth(" in line and "def " not in line:
                call_sites.append(f"{relative}:{number}")
    assert len(sql_sites) == 1, sql_sites
    assert sql_sites[0].startswith("src/infrastructure/sqlite/library.py:"), sql_sites
    # ≥2 production callers outside the definition (the import page unit and
    # its D-2 standalone write unit live in library.py; the C-17 apply face
    # calls the repository directly).
    assert any(item.startswith("src/application/sources/service.py:") for item in call_sites)
    assert len([item for item in call_sites if item.startswith("src/")]) >= 3
    service_text = (
        src / "application" / "sources" / "service.py"
    ).read_text(encoding="utf-8")
    assert "UPDATE source_locations SET registry_id" not in service_text
    runtime_text = (
        src / "application" / "importing" / "referenced" / "runtime.py"
    ).read_text(encoding="utf-8")
    assert "UPDATE source_locations" not in runtime_text


def test_relink_refreshes_location_auth_in_place_cross_registry(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-LS4-2: the SAME physical file re-authorized under a NEW registry is
    re-registered in place: registry_id/last_verified_at updated, no new
    location row, identity columns and the binding untouched."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    before = _current_location(conn)
    assert before["registry_id"] == "reg-1"
    assert before["authorization_generation"] == 1
    assert before["last_verified_at"] is None
    binding_before = conn.execute(
        "SELECT authorization_generation, binding_version FROM page_bindings"
        " WHERE page_id = 'p1'"
    ).fetchone()

    renamed = scratch_dir / "old-renamed.zip"
    zip_path.rename(renamed)
    grant_id, scan = _scan_with_container(
        stack, registry, renamed, kind="relink", registry_id="reg-2"
    )
    _plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="relink", command="RelinkSource"
    )
    assert dispatch["state"] == "core-committed"

    after = _current_location(conn)
    assert after["location_id"] == before["location_id"]  # in place, same row
    assert after["registry_id"] == "reg-2"  # the live grant's registry
    assert after["authorization_generation"] == 1
    assert after["last_verified_at"] is not None
    _iso_timestamp(after["last_verified_at"])
    # The physical identity and the observation stay identical.
    for column in (
        "source_id", "content_digest", "volume_serial", "file_id",
        "size_bytes", "observed_at", "is_current", "created_at",
    ):
        assert after[column] == before[column], column
    assert len(_all_locations(conn)) == 1  # never a duplicate location row
    assert conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
    # The refresh never rewrites bindings (old binding generation stays ≤).
    binding_after = conn.execute(
        "SELECT authorization_generation, binding_version FROM page_bindings"
        " WHERE page_id = 'p1'"
    ).fetchone()
    assert tuple(binding_after) == tuple(binding_before)


def test_relink_refresh_follows_same_registry_generation_bump(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-LS4-2/5: a re-authorized generation on the SAME registry is followed
    and bindings are not lifted to the new generation."""
    zip_path, _page1, _page2, _digest_before = _seed(conn, scratch_dir)
    renamed = scratch_dir / "old-renamed.zip"
    zip_path.rename(renamed)
    grant_id, scan = _scan_with_container(
        stack, registry, renamed, kind="relink", generation=2
    )
    _plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="relink", command="RelinkSource"
    )
    assert dispatch["state"] == "core-committed"
    after = conn.execute(
        "SELECT registry_id, authorization_generation, last_verified_at"
        " FROM source_locations WHERE source_id = 's1' AND is_current = 1"
    ).fetchone()
    assert after["registry_id"] == "reg-1"
    assert after["authorization_generation"] == 2
    assert after["last_verified_at"] is not None
    bindings = conn.execute(
        "SELECT authorization_generation FROM page_bindings"
        " WHERE page_id IN ('p1', 'p2')"
    ).fetchall()
    assert [row["authorization_generation"] for row in bindings] == [1, 1]


def test_refresh_source_location_auth_fail_closed_guards(conn, repo):
    """AC-LS4-4/5: identity/is_current/generation guards are fail-closed and a
    refresh is idempotent, monotonic and audited."""
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest="a" * 64,
        entries=[("e1", "001.png", "b" * 64)],
    )  # reg-1 / generation 1 / volume 7 / file 8 / last_verified NULL
    location = _current_location(conn)
    now = "2026-11-07T00:00:00.000+00:00"

    def snapshot():
        return [tuple(row) for row in conn.execute(
            "SELECT * FROM source_locations ORDER BY location_id"
        ).fetchall()]

    baseline = snapshot()

    # P2 identity mismatch: wrong digest / volume / file → zero write.
    assert repo.refresh_source_location_auth(
        "s1", "c" * 64, 7, 8, "reg-2", 9, now
    ) == 0
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 99, 8, "reg-2", 9, now
    ) == 0
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 7, 99, "reg-2", 9, now
    ) == 0
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 7, 8, "reg-2", 9, now
    ) == 1  # control: the real identity DOES refresh
    assert snapshot() != baseline
    baseline = snapshot()

    # C2 idempotent: same three values → matched 0 rows, no side effect.
    refreshed = _current_location(conn)
    assert _refresh(
        repo, refreshed, registry_id="reg-2", generation=9,
        last_verified_at=now,
    ) == 0
    assert snapshot() == baseline

    # C1 monotonic on the SAME registry: generation cannot go backwards.
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 7, 8, "reg-2", 15, "2026-11-07T00:00:01.000+00:00"
    ) == 1
    baseline = snapshot()
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 7, 8, "reg-2", 14, "2026-11-07T00:00:02.000+00:00"
    ) == 0
    assert snapshot() == baseline
    row = _current_location(conn)
    assert row["authorization_generation"] == 15
    assert row["last_verified_at"] == "2026-11-07T00:00:01.000+00:00"
    _iso_timestamp(row["last_verified_at"])

    # A NEW registry is a new registration: generation 1 is legal (cross-reg).
    assert repo.refresh_source_location_auth(
        "s1", "a" * 64, 7, 8, "reg-3", 1, "2026-11-07T00:00:03.000+00:00"
    ) == 1
    row = _current_location(conn)
    assert (row["registry_id"], row["authorization_generation"]) == ("reg-3", 1)

    # P3 is_current: a superseded row (same identity keys, distinct row) is
    # never refreshed.
    with conn:
        conn.execute(
            "INSERT INTO source_locations (location_id, source_id, registry_id,"
            " authorization_generation, content_digest, volume_serial, file_id,"
            " size_bytes, observed_at, is_current, created_at)"
            " VALUES ('loc-old', 's1', 'reg-1', 1, ?, 1, 2, 10, ?, 0, ?)",
            ("d" * 64, now, now),
        )
    baseline = snapshot()
    assert repo.refresh_source_location_auth(
        "s1", "d" * 64, 1, 2, "reg-9", 1, now
    ) == 0
    assert snapshot() == baseline
    old = conn.execute(
        "SELECT last_verified_at, registry_id FROM source_locations"
        " WHERE location_id = 'loc-old'"
    ).fetchone()
    assert old["last_verified_at"] is None
    assert old["registry_id"] == "reg-1"
    # Identity + observation columns were never rewritten by any refresh above:
    # only registry_id/authorization_generation/last_verified_at ever move.
    row = _current_location(conn)
    assert row["location_id"] == location["location_id"]
    assert row["source_id"] == "s1"
    assert row["content_digest"] == "a" * 64
    assert (row["volume_serial"], row["file_id"]) == (7, 8)
    assert (row["size_bytes"], row["observed_at"], row["created_at"], row["is_current"]) == (
        location["size_bytes"], location["observed_at"],
        location["created_at"], location["is_current"],
    )


# ---------------------------------------------------------------------------
# FEA-11-RESIDUAL-4A AC-R3-3 (AC11-6): folder sources, SC-S11 reorder and
# multi-project confirmation scope.
# ---------------------------------------------------------------------------


def _folder_seed(conn, scratch_dir):
    """One REAL folder source: two member PNGs + the recorded
    ``folder-manifest/1`` content digest of those very bytes (C-15 §3.1)."""
    from application.importing.referenced.model import folder_manifest_digest

    folder = scratch_dir / "folder-source"
    folder.mkdir(parents=True, exist_ok=True)
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    members = {"001.png": page1, "002.png": page2}
    for name, data in members.items():
        (folder / name).write_bytes(data)
    manifest = [
        {"rel_path": name, "size_bytes": len(data), "sha256": _digest(data)}
        for name, data in sorted(members.items())
    ]
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=folder_manifest_digest(manifest),
        entries=[
            ("e1", "001.png", _digest(page1)),
            ("e2", "002.png", _digest(page2)),
        ],
        legacy_v7_evidence=False,
        source_kind="folder",
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return folder, members


def _scan_with_folder(stack, registry, folder, *, kind, names):
    """Scan a folder source through a REAL folder grant over its members."""
    entries = [
        (Path(folder) / name, name, index) for index, name in enumerate(names)
    ]
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="folder", entries=entries
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": kind, "grant_ids": [grant_id], "missing": [],
        }
    )
    return grant_id, scan


def _page_order(conn, page_ids=("p1", "p2")):
    marks = ",".join("?" for _ in page_ids)
    return {
        row["page_id"]: (row["sort_order"], row["source_order"])
        for row in conn.execute(
            f"SELECT page_id, sort_order, source_order FROM pages"
            f" WHERE page_id IN ({marks})",
            list(page_ids),
        ).fetchall()
    }


def _binding_snapshot(conn):
    return [
        tuple(row)
        for row in conn.execute(
            "SELECT * FROM page_bindings ORDER BY binding_id"
        ).fetchall()
    ]


def test_folder_relink_is_typed_refused(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-R3-3 ①/R7-05: a folder source's relink is a TYPED refusal.

    A folder grant carries per-member identity only (no ``container_facts``),
    so "the SAME physical directory" cannot be proven; the frozen contract
    sends the caller to repoint/resync (C-17 §5.3) instead of silently
    keeping a binding it cannot stand behind. Zero writes on refusal.
    """
    folder, _members = _folder_seed(conn, scratch_dir)
    before = _binding_snapshot(conn)
    grant_id, scan = _scan_with_folder(
        stack, registry, folder, kind="relink", names=["001.png", "002.png"]
    )
    assert scan["totals"] == {
        "unchanged": 2, "added": 0, "missing": 0, "changed": 0, "ambiguous": 0,
    }
    with pytest.raises(SourceSyncError) as error:
        run_full_sync(
            stack, scan, grant_ids=[grant_id], kind="relink",
            command="RelinkSource",
        )
    assert error.value.code == "SOURCE_SYNC_STATE_CONFLICT"
    assert "folder relink cannot prove" in str(error.value)
    # The refusal wrote nothing: every binding row is byte-identical.
    assert _binding_snapshot(conn) == before


def test_folder_resync_is_a_real_escape_path(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-R3-3 ②: the escape path the refusal points at really works.

    After the relink refusal the SAME folder source goes through resync: the
    new member is added, a new source version is published and the already
    bound pages keep their user order. (The folder identity defect itself,
    ``L-S4-2``, is registered as a defect — not fixed here.)
    """
    folder, _members = _folder_seed(conn, scratch_dir)
    before = _page_order(conn)
    assert before == {"p1": (1, 1), "p2": (2, 2)}
    (folder / "003.png").write_bytes(png_bytes(color=(0, 0, 255)))

    grant_id, scan = _scan_with_folder(
        stack, registry, folder, kind="resync",
        names=["001.png", "002.png", "003.png"],
    )
    assert scan["totals"]["added"] == 1
    _plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="resync",
        command="ResyncSource",
    )
    assert dispatch["state"] == "core-committed"

    # A real new version was published and the added member became a page.
    versions = conn.execute(
        "SELECT version_id FROM source_versions WHERE source_id = 's1'"
    ).fetchall()
    assert len(versions) == 2
    assert conn.execute(
        "SELECT COUNT(*) FROM pages WHERE chapter_id = 'c1'"
    ).fetchone()[0] == 3
    # The already-bound pages were never reordered by the folder resync.
    assert _page_order(conn) == before


def test_member_reorder_keeps_bound_page_user_order(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-R3-3 ③ (SC-S11): a container member REORDER is not a page reorder.

    The same two members are written in the opposite order, so the container
    bytes (and therefore the version) change while the bound pages keep their
    PageId, ``sort_order`` and ``source_order``.
    """
    zip_path, page1, page2, _digest_before = _seed(conn, scratch_dir)
    before = _page_order(conn)
    assert before == {"p1": (1, 1), "p2": (2, 2)}
    reordered = write_zip(
        scratch_dir / "reordered.zip",
        [("002.png", page2), ("001.png", page1)],
    )
    assert reordered.read_bytes() != zip_path.read_bytes()

    grant_id, scan = _scan_with_container(stack, registry, reordered, kind="resync")
    assert scan["totals"]["unchanged"] == 2
    _plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="resync", command="ResyncSource"
    )
    assert dispatch["state"] == "core-committed"
    assert _page_order(conn) == before


def test_scope_current_resync_leaves_the_other_project_untouched(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-R3-3 ④: only the confirmed set moves.

    ``b1`` and ``b2`` share the source; a ``scope=current`` resync confirms
    only ``b1``'s pages. The new member lands in ``b1`` while ``b2``'s page,
    binding and order stay byte-identical.
    """
    zip_path, page1, page2, _digest_before = _seed(conn, scratch_dir)
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b2', 'Other', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'b2', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    add_referenced_page(
        conn, "p3", "c2", "b2", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    conn.commit()
    other_order_before = _page_order(conn, ("p3",))
    other_page_before = tuple(conn.execute(
        "SELECT sort_order, source_order, source_hash FROM pages"
        " WHERE page_id = 'p3'"
    ).fetchone())
    other_binding_before = [
        tuple(row) for row in conn.execute(
            "SELECT * FROM page_bindings WHERE page_id = 'p3'"
        ).fetchall()
    ]

    new_zip = write_zip(
        scratch_dir / "new.zip",
        [("001.png", page1), ("002.png", page2),
         ("003.png", png_bytes(color=(0, 0, 255)))],
    )
    grant_id, scan = _scan_with_container(stack, registry, new_zip, kind="resync")
    assert scan["totals"]["added"] == 1
    _plan, dispatch = run_full_sync(
        stack, scan, grant_ids=[grant_id], kind="resync", command="ResyncSource"
    )
    assert dispatch["state"] == "core-committed"

    # The confirmed project gained exactly one page...
    assert conn.execute(
        "SELECT COUNT(*) FROM pages WHERE chapter_id = 'c1'"
    ).fetchone()[0] == 3
    # ...and the project outside the confirmation set is untouched.
    assert _page_order(conn, ("p3",)) == other_order_before
    assert tuple(conn.execute(
        "SELECT sort_order, source_order, source_hash FROM pages"
        " WHERE page_id = 'p3'"
    ).fetchone()) == other_page_before
    assert [
        tuple(row) for row in conn.execute(
            "SELECT * FROM page_bindings WHERE page_id = 'p3'"
        ).fetchall()
    ] == other_binding_before
    assert stack["store"].current_binding_of_page("p3")["status"] == "healthy"
