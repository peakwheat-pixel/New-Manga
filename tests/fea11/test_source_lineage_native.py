"""FEA-11-LINEAGE-1 AC1: region/draft write paths register native lineage in the
SAME SQLite transaction as the immutable revision (C-17 §7.1)."""

from __future__ import annotations

import json
import sqlite3

import pytest

from domain.regions.entities import Region, RegionOrigin, RegionRevision, ReviewState
from infrastructure.sqlite.regions import RevisionLineage, SqliteRegionRepository
from tests.fea11.conftest import add_source_tree


NOW = "2026-11-05T00:00:00.000+00:00"


@pytest.fixture()
def page(conn: sqlite3.Connection, book_chapter) -> str:
    book_id, chapter_id = book_chapter
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES ('p1', ?, 0, ?, ?)",
        (chapter_id, NOW, NOW),
    )
    conn.commit()
    return "p1"


DIGEST = "b" * 64


def _seed_binding(conn: sqlite3.Connection, binding_id: str = "b1", page_id: str = "p1") -> str:
    add_source_tree(
        conn, source_id="s1", version_id="sv1", digest="a" * 64,
        entries=[("e1", "001.png", DIGEST)], legacy_v7_evidence=False,
    )
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id, binding_version,"
        " source_id, entry_id, accepted_source_version, status,"
        " authorization_generation, authorized_at, verified_digest,"
        " created_at, updated_at)"
        " VALUES (?, ?, 'b1', 1, 's1', 'e1', 'sv1', 'healthy', 1, ?, ?, ?, ?)",
        (binding_id, page_id, NOW, DIGEST, NOW, NOW),
    )
    conn.commit()
    return binding_id


def _seed_region(conn: sqlite3.Connection, region_id: str = "rg1", page_id: str = "p1") -> Region:
    geometry = json.dumps({"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.4},
                          separators=(",", ":"))
    conn.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order,"
        " geometry_json, text_json, style_json, sfx_policy, region_locked,"
        " translation_locked, inpaint_locked, created_at, updated_at)"
        " VALUES (?, ?, 'speech', 0, ?, '{}', '{}', 'skip', 0, 0, 0, ?, ?)",
        (region_id, page_id, geometry, NOW, NOW),
    )
    conn.commit()
    region = Region(region_id=region_id, page_id=page_id)
    region.created_at = NOW
    region.updated_at = NOW
    return region


def _revision(region_id: str, revision_id: str) -> RegionRevision:
    return RegionRevision(
        region_revision_id=revision_id,
        region_id=region_id,
        revision_no=1,
        snapshot={"text": "x"},
        origin=RegionOrigin.USER,
        review_state=ReviewState.UNREVIEWED,
    )


def _lineage_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT revision_id, region_id, binding_id, provenance,"
        " from_revision_id, operation_id FROM source_revision_lineage"
    ).fetchall()


def test_commit_region_revision_writes_native_lineage_in_the_same_transaction(conn, page):
    repo = SqliteRegionRepository(conn)
    _seed_binding(conn)
    region = _seed_region(conn)

    result = repo.commit_region_revision(
        region, _revision(region.region_id, "rev-1"),
        lineage=RevisionLineage(binding_id="b1", provenance="native"),
    )

    assert result.status.value == "applied"
    rows = _lineage_rows(conn)
    assert len(rows) == 1
    assert rows[0]["revision_id"] == "rev-1"
    assert rows[0]["region_id"] == "rg1"
    assert rows[0]["binding_id"] == "b1"
    assert rows[0]["provenance"] == "native"
    assert rows[0]["operation_id"] is None


def test_commit_region_revision_without_lineage_stays_backward_compatible(conn, page):
    repo = SqliteRegionRepository(conn)
    _seed_binding(conn)
    region = _seed_region(conn)

    result = repo.commit_region_revision(region, _revision(region.region_id, "rev-1"))

    assert result.status.value == "applied"
    assert _lineage_rows(conn) == []


def test_commit_region_batch_writes_lineage_for_updated_regions(conn, page):
    repo = SqliteRegionRepository(conn)
    _seed_binding(conn)
    region = _seed_region(conn)

    result = repo.commit_region_batch(
        updated_regions=[(region, _revision(region.region_id, "rev-2"), None)],
        lineage_by_region={
            "rg1": RevisionLineage(binding_id="b1", provenance="native"),
        },
    )

    assert result.status.value == "applied"
    rows = _lineage_rows(conn)
    assert len(rows) == 1
    assert rows[0]["revision_id"] == "rev-2"
    assert rows[0]["binding_id"] == "b1"


def test_rolled_back_commit_leaves_no_orphan_lineage(conn, page):
    repo = SqliteRegionRepository(conn)
    _seed_binding(conn)
    region = _seed_region(conn)

    result = repo.commit_region_revision(
        region, _revision(region.region_id, "rev-3"),
        expected_current_revision_id="not-the-current",
        lineage=RevisionLineage(binding_id="b1", provenance="native"),
    )

    assert result.status.value == "input_revision_changed"
    assert _lineage_rows(conn) == []
