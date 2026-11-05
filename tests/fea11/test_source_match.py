"""FEA-11-MATCH-1 evidence: pixel profile extraction, comparability,
duplicate groups, honest degradation and the real v7 import fixture.

Coverage map (card AC-M1…AC-M5):

* pure matcher matrix — rows in / classified pairs out, no DB, no files
  (7-dim comparability, duplicate occurrences, counterpart-less members,
  v7 ``missing_old`` / ``incomparable``, ``changed`` preconditions);
* scan integration over real zip containers, real HMAC-signed grants and the
  strict verified-read path (independent Pillow re-computation + golden);
* scan read-only proof (full DB snapshot before/after);
* two-generation resync (pixel matching becomes reachable from generation 2);
* real v7 fixture: ``default_migrations()[:7]`` + real
  ``ReferencedImportPlanner``/``ReferencedImportRuntime`` import → v8 migration
  → scan/degrade/apply/second generation;
* apply persists the live candidate's canonical params.

All scratch data lives under pytest ``tmp_path``; no tracked evidence is
rewritten by these tests.
"""

from __future__ import annotations

import hashlib
import io
import sqlite3
import time

import pytest
from PIL import Image

from application.sources.matcher import _profiles_comparable, match_entries
from application.sources.scanner import (
    PIXEL_DECODER_NAME,
    PIXEL_DECODER_VERSION,
    PIXEL_PARAMS,
    PIXEL_PROFILE_ALGORITHM,
    canonical_pixel_params_json,
)
from application.sources.service import _publication_relation
from tests.fea09.support import FakeSourceReadAccess, build_runtime
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    build_plan_body,
    default_decisions,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)
from tests.fea11.test_source_sync import _seed_complete_pixel_profiles

#: Independent EXIF-orientation mapping (Pillow transpose ops; deliberately
#: not ``ImageOps.exif_transpose`` so the normalisation wiring is proven).
_ORIENTATION_OPS = {
    2: Image.Transpose.FLIP_LEFT_RIGHT,
    3: Image.Transpose.ROTATE_180,
    4: Image.Transpose.FLIP_TOP_BOTTOM,
    5: Image.Transpose.TRANSPOSE,
    6: Image.Transpose.ROTATE_270,
    7: Image.Transpose.TRANSVERSE,
    8: Image.Transpose.ROTATE_90,
}

#: Hard-coded golden (2x2, row-major: red/green/blue/white).
GOLDEN_PNG_PIXEL_DIGEST = (
    "53b800d918da60fdb8150f357ebacc7815c38c5698622926de3ce71d2b6b6c71"
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pattern_image(width: int = 4, height: int = 3, *, variant: int = 0):
    """An asymmetric raster so rotations and mirrors are distinguishable."""
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                (13 + x * 29 + variant * 41) % 233,
                (7 + y * 37 + variant * 11) % 241,
                (90 + x * 3 + y * 5) % 251,
            )
    return image


def _pattern_png(
    width: int = 4,
    height: int = 3,
    *,
    variant: int = 0,
    orientation: int | None = None,
    compress_level: int = 6,
    mode: str = "RGB",
    color=(250, 30, 60, 0),
) -> bytes:
    if mode == "RGB":
        image = _pattern_image(width, height, variant=variant)
    else:
        image = Image.new(mode, (width, height), color)
    buffer = io.BytesIO()
    kwargs = {"compress_level": compress_level}
    if orientation is not None:
        exif = Image.Exif()
        exif[0x0112] = orientation
        kwargs["exif"] = exif.tobytes()
    image.save(buffer, format="PNG", **kwargs)
    return buffer.getvalue()


def _expected_profile(png: bytes) -> dict:
    """Independent C1–C8 re-computation of the frozen profile fields."""
    with Image.open(io.BytesIO(png)) as image:
        image.load()
        orientation = int(image.getexif().get(0x0112, 1))
        operation = _ORIENTATION_OPS.get(orientation)
        normalised = (
            image.transpose(operation)
            if operation is not None
            else image.copy()
        )
        try:
            rgb = (
                normalised
                if normalised.mode == "RGB"
                else normalised.convert("RGB")
            )
            width, height = rgb.size
            pixels = rgb.tobytes()
        finally:
            normalised.close()
    params = canonical_pixel_params_json()
    return {
        "algorithm": PIXEL_PROFILE_ALGORITHM,
        "decoder": PIXEL_DECODER_NAME,
        "decoder_version": PIXEL_DECODER_VERSION,
        "params_digest": _sha256(params.encode("utf-8")),
        "width": width,
        "height": height,
        "orientation": 1,
        "pixel_digest": _sha256(
            f"{width}x{height}".encode("ascii") + b"\x00" + pixels
        ),
    }


def _evidence_pixel(entry: dict) -> dict | None:
    return entry.get("pixel")


def _seed_source(
    conn,
    scratch_dir,
    images: list[tuple[str, bytes]],
    *,
    name: str = "old.zip",
    source_id: str = "s1",
    version_id: str = "sv1",
    legacy_v7_evidence: bool = True,
    page_ids: tuple[str, ...] | None = None,
    bind_entries: int | None = None,
) -> tuple:
    """Seed the recorded old container + one bound page per bound image."""
    zip_path = write_zip(scratch_dir / name, images)
    container_digest = _sha256(zip_path.read_bytes())
    entries = [
        (f"e{index}", locator, _sha256(payload))
        for index, (locator, payload) in enumerate(images, start=1)
    ]
    add_source_tree(
        conn,
        source_id=source_id,
        version_id=version_id,
        digest=container_digest,
        entries=entries,
        legacy_v7_evidence=legacy_v7_evidence,
    )
    if not legacy_v7_evidence:
        _seed_complete_pixel_profiles(conn, version_id, dict(images))
    bound = (
        len(images) if bind_entries is None else min(bind_entries, len(images))
    )
    for index, (locator, payload) in enumerate(images[:bound], start=1):
        page_id = (
            page_ids[index - 1] if page_ids is not None else f"p{index}"
        )
        add_referenced_page(
            conn,
            page_id,
            "c1",
            "b1",
            order=index,
            source_id=source_id,
            version_id=version_id,
            entry_id=f"e{index}",
            digest=_sha256(payload),
        )
    return zip_path, container_digest


def _scan(stack, registry, path, *, source_id: str = "s1", kind: str = "resync"):
    grant_id, _facts = mint_grant(
        registry, source_id=source_id, kind="zip",
        entries=[(path, path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": source_id,
            "project_ids": ["b1"],
            "scope": "current",
            "kind": kind,
            "grant_ids": [grant_id],
            "missing": [],
        }
    )
    return grant_id, scan


def _source_rows(conn, version_id: str) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            "SELECT * FROM source_entries WHERE version_id = ?"
            " ORDER BY ordinal",
            (version_id,),
        )
    )


#: Tables the read-only snapshot covers (same set as the scanner tests).
_SNAPSHOT_TABLES = (
    "sources", "source_locations", "source_versions", "source_entries",
    "page_bindings", "pages", "books", "chapters", "regions",
    "region_revisions", "artifact_revisions", "pipeline_runs",
    "pipeline_tasks", "source_sync_plans", "source_operations",
    "source_binding_publications", "source_revision_lineage",
)


def _snapshot(conn) -> dict:
    snapshot = {}
    for table in _SNAPSHOT_TABLES:
        try:
            rows = list(conn.execute(f"SELECT * FROM {table}"))
        except sqlite3.OperationalError:
            continue
        snapshot[table] = [
            tuple(sorted((key, repr(value)) for key, value in dict(row).items()))
            for row in rows
        ]
    return snapshot


# ---------------------------------------------------------------------------
# ① pure matcher matrix (no DB, no files)
# ---------------------------------------------------------------------------


def _row(
    entry_id: str,
    locator: str,
    ordinal: int,
    *,
    content_digest: str | None = None,
    pixel_digest: str | None = None,
    width: int | None = 4,
    height: int | None = 3,
    orientation: int | None = 1,
    decoder: str = PIXEL_DECODER_NAME,
    decoder_version: str = PIXEL_DECODER_VERSION,
    params: str | None = None,
    algorithm: str | None = PIXEL_PROFILE_ALGORITHM,
) -> dict:
    return {
        "entry_id": entry_id,
        "locator": locator,
        "ordinal": ordinal,
        "content_digest": content_digest or _sha256(entry_id.encode()),
        "pixel_digest": pixel_digest,
        "pixel_digest_algorithm": algorithm if pixel_digest else None,
        "width": width,
        "height": height,
        "orientation": orientation,
        "decoder_name": decoder,
        "decoder_version": decoder_version,
        "decoder_params_json": (
            params if params is not None else canonical_pixel_params_json()
        ),
    }


def _match(old: list[dict], new: list[dict]):
    return match_entries(old, new, same_container=False)


def _evidence_of(result, old_entry_id: str) -> tuple[str, str]:
    for item in result.items:
        if item.old_entry is not None and item.old_entry["entry_id"] == (
            old_entry_id
        ):
            return (item.classification, item.evidence)
    raise AssertionError(f"old entry {old_entry_id} not classified")


def test_profiles_comparable_requires_all_seven_dimensions() -> None:
    """AC-M2: algorithm/decoder/version/params/width/height/orientation."""
    base_old = _row("old", "001.png", 0, pixel_digest="a" * 64)
    base_new = _row("new", "001.png", 0, pixel_digest="b" * 64)
    assert _profiles_comparable(base_old, base_new)
    variants = {
        "algorithm": {"algorithm": "pixel-digest/2"},
        "decoder": {"decoder": "other-decoder"},
        "decoder_version": {"decoder_version": "2"},
        "params": {
            "params": canonical_pixel_params_json().replace(
                '"alpha":"opaque-only"', '"alpha":"allow"'
            )
        },
        "width": {"width": 5},
        "height": {"height": 4},
        "orientation": {"orientation": 3},
    }
    for dimension, override in variants.items():
        changed = _row("new", "001.png", 0, pixel_digest="b" * 64, **override)
        assert not _profiles_comparable(base_old, changed), dimension
    # params compare as canonical objects, not raw strings (C8)
    reordered = _row(
        "new",
        "001.png",
        0,
        pixel_digest="b" * 64,
        params='{ "profile" : "fea11-match-rgb/1", "alpha": "opaque-only",'
        ' "color_management": "none", "exif_transpose": true, "frame": 0,'
        ' "mode": "RGB", "pillow_version": "12.3.0" }',
    )
    assert _profiles_comparable(base_old, reordered)


def test_unique_pixel_requires_single_occurrence_on_both_sides() -> None:
    """AC-M2/AC-M3: 1:1 unique pixel continues; 1:2 and 2:1 freeze."""
    pixel = "c" * 64
    new = _row("new1", "001.png", 0, pixel_digest=pixel)
    old = _row("old1", "001.png", 0, pixel_digest=pixel)
    result = _match([old], [new])
    assert ("unchanged", "unique_pixel") == (
        result.items[0].classification,
        result.items[0].evidence,
    )
    assert result.totals["unchanged"] == 1

    duplicate_new = [
        _row("new1", "001.png", 0, pixel_digest=pixel),
        _row("new2", "002.png", 1, pixel_digest=pixel),
    ]
    result = _match([old], duplicate_new)
    assert result.totals == {
        "unchanged": 0, "added": 1, "missing": 0, "changed": 0,
        "ambiguous": 1,
    }
    pair = [item for item in result.items if item.old_entry is not None][0]
    assert (pair.classification, pair.evidence) == (
        "ambiguous", "duplicate_group",
    )
    assert pair.new_entry is not None  # never a one-sided ambiguous row

    duplicate_old = [
        _row("old1", "001.png", 0, pixel_digest=pixel),
        _row("old2", "002.png", 1, pixel_digest=pixel),
    ]
    result = _match(duplicate_old, [new])
    assert result.totals == {
        "unchanged": 0, "added": 0, "missing": 1, "changed": 0,
        "ambiguous": 1,
    }
    for item in result.items:
        if item.classification == "ambiguous":
            assert item.old_entry is not None and item.new_entry is not None


def test_byte_identity_does_not_bypass_a_duplicate_pixel_group() -> None:
    """AC-M3: the unique-content branch must still freeze pixel duplicates."""
    pixel = "d" * 64
    old = _row("old1", "001.png", 0, pixel_digest=pixel)
    same_bytes = _row(
        "new1", "001.png", 0,
        content_digest=old["content_digest"], pixel_digest=pixel,
    )
    other_pixels = _row("new2", "002.png", 1, pixel_digest=pixel)
    result = _match([old], [same_bytes, other_pixels])
    pair = [item for item in result.items if item.old_entry is not None][0]
    assert (pair.classification, pair.evidence) == (
        "ambiguous", "duplicate_group",
    )
    assert pair.new_entry is not None


def test_counterpart_less_duplicate_members_are_missing_and_added() -> None:
    """AC-M4: no cross-side counterpart → missing/none (old) or added/none."""
    pixel = "e" * 64
    old = [
        _row("old1", "001.png", 0, pixel_digest=pixel),
        _row("old2", "002.png", 1, pixel_digest=pixel),
    ]
    new = [_row("new1", "001.png", 0, pixel_digest=pixel)]
    result = _match(old, new)
    assert result.totals == {
        "unchanged": 0, "added": 0, "missing": 1, "changed": 0,
        "ambiguous": 1,
    }
    for item in result.items:
        if item.classification == "ambiguous":
            assert item.old_entry and item.new_entry
        if item.classification == "missing":
            assert item.old_entry and item.new_entry is None

    # repeated LOCATOR (not pixels) is the same rule: 2 old names vs 1 new
    old_named = [
        _row("old1", "same.png", 0, content_digest="1" * 64),
        _row("old2", "same.png", 1, content_digest="2" * 64),
    ]
    new_named = [_row("new1", "same.png", 0, content_digest="3" * 64)]
    result = _match(old_named, new_named)
    assert result.totals["ambiguous"] == 1
    assert result.totals["missing"] == 1


def test_old_v7_evidence_degrades_to_missing_old() -> None:
    """AC-M4 discriminator: W/H-only old row never yields changed/unique_pixel."""
    old = _row(
        "old1", "001.png", 0,
        pixel_digest=None, width=4, height=3,
    )
    new = _row("new1", "001.png", 0, pixel_digest="f" * 64)
    result = _match([old], [new])
    assert _evidence_of(result, "old1") == ("ambiguous", "missing_old")

    old_no_geometry = _row("old1", "001.png", 0, pixel_digest=None, width=None,
                           height=None)
    result = _match([old_no_geometry], [new])
    assert _evidence_of(result, "old1") == ("ambiguous", "missing_old")

    # byte-identical member still continues (防回归)
    same = _row(
        "new1", "001.png", 0, content_digest=old["content_digest"],
        pixel_digest="a" * 64,
    )
    result = _match([old], [same])
    pair = [item for item in result.items if item.old_entry is not None][0]
    assert (pair.classification, pair.evidence) == ("unchanged", "unique_pixel")


def test_changed_requires_complete_comparable_pixel_evidence() -> None:
    """AC-M4: `changed` is only asserted when both sides are complete/equal."""
    old = _row("old1", "001.png", 0, pixel_digest="a" * 64)
    differ = _row("new1", "001.png", 0, pixel_digest="b" * 64)
    assert _evidence_of(_match([old], [differ]), "old1") == (
        "changed", "direct",
    )
    # old present, new missing the profile (decode failure) → incomparable
    new_missing = _row(
        "new1", "001.png", 0, pixel_digest=None, width=4, height=3,
    )
    assert _evidence_of(_match([old], [new_missing]), "old1") == (
        "ambiguous", "incomparable",
    )
    # same pixel digest but a different orientation is NOT comparable
    same_pixels_other_orientation = _row(
        "new1", "001.png", 0, pixel_digest="a" * 64, orientation=6,
    )
    assert _evidence_of(
        _match([old], [same_pixels_other_orientation]), "old1"
    ) == ("ambiguous", "incomparable")
    # different canonical decoder params → incomparable (never guess)
    other_params = _row(
        "new1", "001.png", 0, pixel_digest="a" * 64,
        params=canonical_pixel_params_json().replace(
            '"frame":0', '"frame":1'
        ),
    )
    assert _evidence_of(_match([old], [other_params]), "old1") == (
        "ambiguous", "incomparable",
    )


def test_publication_relation_branches_are_both_asserted() -> None:
    """AC-M2: `_publication_relation` direct/unique_pixel/geometry branches."""
    new_entry = {"width": 4, "height": 3}
    assert _publication_relation({"evidence": "direct"}, new_entry, None) == (
        "same_content"
    )
    assert _publication_relation(
        {"evidence": "unique_pixel"}, new_entry, {"width": 4, "height": 3}
    ) == "same_content"
    # unique byte path: the v7 old row has no geometry → (None, None) fallback
    assert _publication_relation(
        {"evidence": "unique_pixel"}, new_entry, None
    ) == "same_content"
    assert _publication_relation(
        {"evidence": "unique_pixel"}, new_entry, {"width": 5, "height": 2}
    ) == "changed"
    for evidence in ("duplicate_group", "missing_old", "incomparable", "none"):
        assert _publication_relation(
            {"evidence": evidence}, new_entry, {"width": 4, "height": 3}
        ) == "changed"


def test_same_container_path_stays_direct() -> None:
    """Path 1 is untouched: direct continuation, no re-decode (C12)."""
    old = [_row("old1", "001.png", 0, pixel_digest="a" * 64)]
    new = [_row("old1", "001.png", 0, pixel_digest="a" * 64)]
    result = match_entries(old, new, same_container=True)
    assert [(item.classification, item.evidence) for item in result.items] == [
        ("unchanged", "direct")
    ]


def test_entry_profile_failure_reason_mapping_is_closed() -> None:
    """AC-M1 C10/D5: only profile extraction failures degrade, and typed."""
    from application.importing.referenced.errors import SourceImportError
    from application.sources.scanner import _reason_for_import_error

    assert _reason_for_import_error(
        SourceImportError("SOURCE_PASSWORD_REQUIRED", "x")
    ) == "encrypted"
    assert _reason_for_import_error(
        SourceImportError("SOURCE_PASSWORD_INVALID", "x")
    ) == "encrypted"
    assert _reason_for_import_error(
        SourceImportError("SOURCE_FORMAT_UNSUPPORTED", "x")
    ) == "unsupported"
    assert _reason_for_import_error(
        SourceImportError("SOURCE_BUDGET_EXCEEDED", "x")
    ) == "unsupported"
    # Grant/lease/identity/integrity failures are never swallowed (C11).
    for code in (
        "SOURCE_ACCESS_DENIED",
        "SOURCE_LEASE_LOST",
        "SOURCE_ENTRY_MISSING",
        "SOURCE_VERSION_MISMATCH",
    ):
        assert _reason_for_import_error(SourceImportError(code, "x")) is None


def test_unparseable_params_are_incomparable_never_disguised_as_empty() -> None:
    """AC-M1 C8: illegal/unknown params must not pretend to be ``{}``."""
    from application.sources.scanner import _entry_evidence
    from application.sources.scanner import _params_digest

    entry = _row("e1", "001.png", 0, pixel_digest="a" * 64)
    entry["decoder_params_json"] = "not json at all"
    assert _params_digest(entry) is None
    evidence = _entry_evidence(entry)
    assert evidence["pixel"] is None
    assert evidence["reason"] == "incomparable"
    # valid JSON that is not an OBJECT is not a profile either (C8)
    for non_object in ("0", "[]", "null", "true"):
        entry["decoder_params_json"] = non_object
        assert _params_digest(entry) is None, non_object
        assert _entry_evidence(entry)["reason"] == "incomparable", non_object

    # key order/whitespace equivalence still yields the same digest (C8)
    canonical = canonical_pixel_params_json()
    reordered = (
        '{ "profile":"fea11-match-rgb/1", "alpha":"opaque-only",'
        ' "color_management":"none", "exif_transpose":true, "frame":0,'
        ' "mode":"RGB", "pillow_version":"12.3.0" }'
    )
    left = dict(entry, decoder_params_json=canonical)
    right = dict(entry, decoder_params_json=reordered)
    assert _params_digest(left) == _params_digest(right)
    # the fixed double-encoding bug: digest is over the object, not the string
    assert _params_digest(left) != _sha256(
        __import__("json").dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def test_ambiguous_evidence_can_never_be_unchanged() -> None:
    """AC-M1 negative: an incomplete target cannot confirm content change."""
    from application.sources.errors import SourceSyncError
    from application.sources.model import validate_diff_item

    base = {
        "item_id": "di-000001",
        "classification": "unchanged",
        "page_id": "p1",
        "old_entry_id": "e1",
        "new_entry_id": "e2",
    }
    for evidence in ("duplicate_group", "missing_old", "incomparable"):
        with pytest.raises(SourceSyncError):
            validate_diff_item(dict(base, evidence=evidence))
    # and the matcher itself never emits unchanged with those evidence labels
    result = match_entries(
        [_row("e1", "001.png", 0, pixel_digest="a" * 64)],
        [_row("e2", "002.png", 1, pixel_digest="b" * 64)],
        same_container=False,
    )
    for item in result.items:
        if item.classification == "unchanged":
            assert item.evidence in ("direct", "unique_pixel")


# ---------------------------------------------------------------------------
# ② scan integration: real zip + real grants + strict reads
# ---------------------------------------------------------------------------


def test_scan_extracts_frozen_profile_and_apply_persists_canonical_params(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-M1: independent recomputation, golden, persistence."""
    buffer = io.BytesIO()
    image = Image.new("RGB", (2, 2))
    pixels = image.load()
    pixels[0, 0] = (255, 0, 0)
    pixels[1, 0] = (0, 255, 0)
    pixels[0, 1] = (0, 0, 255)
    pixels[1, 1] = (255, 255, 255)
    image.save(buffer, format="PNG")
    golden_png = buffer.getvalue()

    image_a = _pattern_png(4, 3)
    # The old container also carries an unbound member: dropping it changes the
    # container digest without inventing a page-level difference.
    old_zip, _old_container = _seed_source(
        conn, scratch_dir,
        [("001.png", image_a), ("pad.txt", b"padding")],
        legacy_v7_evidence=True,
        bind_entries=1,
    )
    # Same image bytes → unique_pixel byte-identity continuation (keep).
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", image_a)])
    assert _sha256(new_zip.read_bytes()) != _sha256(old_zip.read_bytes())
    _grant_id, scan = _scan(stack, registry, new_zip)

    assert scan["totals"] == {
        "unchanged": 1, "added": 0, "missing": 0, "changed": 0,
        "ambiguous": 0,
    }
    evidence = scan["source"]["entries"][0]
    expected = _expected_profile(image_a)
    assert evidence["pixel"] == expected
    assert evidence["pixel"]["pixel_digest"] == _expected_profile(image_a)[
        "pixel_digest"
    ]
    # C8: digest is over the canonical OBJECT, never over the JSON string
    params_digest = _sha256(canonical_pixel_params_json().encode("utf-8"))
    doubled = _sha256(
        __import__("json")
        .dumps(canonical_pixel_params_json(), sort_keys=True,
               separators=(",", ":"))
        .encode("utf-8")
    )
    assert evidence["pixel"]["params_digest"] == params_digest
    assert evidence["pixel"]["params_digest"] != doubled

    plan, _dispatch = run_full_sync(stack, scan, grant_ids=[_grant_id])
    new_version = scan["source"]["version_id"]
    persisted = _source_rows(conn, new_version)[0]
    assert persisted["pixel_digest"] == expected["pixel_digest"]
    assert persisted["pixel_digest_algorithm"] == PIXEL_PROFILE_ALGORITHM
    assert (persisted["width"], persisted["height"]) == (4, 3)
    assert persisted["orientation"] == 1
    assert persisted["decoder_name"] == PIXEL_DECODER_NAME
    assert persisted["decoder_version"] == PIXEL_DECODER_VERSION
    assert persisted["decoder_params_json"] == canonical_pixel_params_json()
    assert __import__("json").loads(persisted["decoder_params_json"]) == (
        PIXEL_PARAMS
    )
    assert plan["body"]["totals"] == scan["totals"]

    # hard-coded golden: the C7 formula on a fixed 2x2 raster
    golden_expected = _expected_profile(golden_png)["pixel_digest"]
    assert golden_expected == GOLDEN_PNG_PIXEL_DIGEST


def test_scan_normalises_exif_orientations_and_refuses_invalid(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-M1 C4/C5: orientations 1..8 including mirrors; 9/0 → unsupported."""
    _seed_source(
        conn, scratch_dir, [("001.png", _pattern_png(4, 3))],
        legacy_v7_evidence=True,
    )
    members = [
        (f"o{orientation}.png", _pattern_png(4, 3, orientation=orientation))
        for orientation in range(1, 9)
    ]
    # invalid orientation 9 and a corrupt image both degrade honestly
    members.append(("o9.png", _pattern_png(4, 3, orientation=9)))
    members.append(("broken.png", b"not-an-image"))
    new_zip = write_zip(scratch_dir / "new.zip", members)
    _grant_id, scan = _scan(stack, registry, new_zip)

    by_locator = {
        entry["locator"]: entry for entry in scan["source"]["entries"]
    }
    for orientation in range(1, 9):
        entry = by_locator[f"o{orientation}.png"]
        expected = _expected_profile(members[orientation - 1][1])
        assert entry["pixel"] == expected, f"orientation {orientation}"
        if orientation in (5, 6, 7, 8):
            assert expected["width"] == 3 and expected["height"] == 4
        else:
            assert expected["width"] == 4 and expected["height"] == 3
        # mirrors really mirror: 2/4/5/7 must differ from the un-mirrored base
        if orientation in (2, 4, 5, 7):
            base = _expected_profile(members[0][1])["pixel_digest"]
            assert expected["pixel_digest"] != base
    assert by_locator["o9.png"]["pixel"] is None
    assert by_locator["o9.png"]["reason"] == "unsupported"
    assert by_locator["broken.png"]["pixel"] is None
    assert by_locator["broken.png"]["reason"] == "unsupported"
    assert sum(scan["totals"].values()) == len(scan["diff"])


def test_scan_degrades_unsupported_and_missing_evidence_without_writing(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-M1 C10 + AC-M5 ③: typed reasons, totals=details, zero DB writes."""
    _seed_source(
        conn, scratch_dir, [("001.png", _pattern_png(4, 3))],
        legacy_v7_evidence=True,
    )
    good = _pattern_png(5, 2, variant=1)
    rgba = _pattern_png(4, 3, mode="RGBA", color=(9, 9, 9, 0))
    members = [
        ("001.png", good),
        ("note.txt", b"plain text"),
        ("alpha.png", rgba),
        ("broken.png", b"\x89PNG-not-really"),
    ]
    new_zip = write_zip(scratch_dir / "new.zip", members)

    before = _snapshot(conn)
    _grant_id, scan = _scan(stack, registry, new_zip)
    after = _snapshot(conn)
    assert before == after, "scan must not write to the database"

    by_locator = {entry["locator"]: entry for entry in scan["source"]["entries"]}
    assert by_locator["001.png"]["pixel"] is not None
    assert by_locator["note.txt"]["pixel"] is None
    assert by_locator["note.txt"]["reason"] == "missing_evidence"
    assert by_locator["alpha.png"]["pixel"] is None
    assert by_locator["alpha.png"]["reason"] == "unsupported"
    assert by_locator["broken.png"]["pixel"] is None
    assert by_locator["broken.png"]["reason"] == "unsupported"
    assert sum(scan["totals"].values()) == len(scan["diff"])


def test_scan_decode_budget_degrades_that_entry_only(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-M1 C3: an over-budget image is unsupported, the scan still succeeds."""
    _seed_source(
        conn, scratch_dir, [("001.png", _pattern_png(4, 3))],
        legacy_v7_evidence=True,
    )
    big = _pattern_png(40, 30)
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", big)])
    grant_id, _unused = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(new_zip, new_zip.name, 0)],
        budget={"max_bytes": 8 * 1024 * 1024, "max_decode_bytes": 2000,
                "max_entries": 100},
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    entry = scan["source"]["entries"][0]
    assert scan["source"]["status"] == "ok"
    assert entry["pixel"] is None
    assert entry["reason"] == "unsupported"
    assert sum(scan["totals"].values()) == len(scan["diff"])


# ---------------------------------------------------------------------------
# ④ two-generation resync: pixel matching reachable from generation 2
# ---------------------------------------------------------------------------


def test_two_generation_resync_reaches_pixel_matching(
    conn, registry, stack, book_chapter, scratch_dir
):
    image = _pattern_png(4, 3)
    _seed_source(
        conn, scratch_dir, [("001.png", image)],
        legacy_v7_evidence=False,  # generation 1 has a complete profile
    )
    # Generation 2: same pixels, different encoded bytes (re-encode).
    reencoded = _pattern_png(4, 3, variant=0, compress_level=0)
    assert _sha256(reencoded) != _sha256(image)
    gen2_zip = write_zip(scratch_dir / "gen2.zip", [("001.png", reencoded)])
    grant2, scan2 = _scan(stack, registry, gen2_zip)
    assert scan2["diff"][0]["evidence"] == "unique_pixel"
    assert scan2["diff"][0]["classification"] == "unchanged"
    run_full_sync(stack, scan2, grant_ids=[grant2])

    # Generation 3: another re-encode; the committed gen-2 rows now carry the
    # profile, so pixel matching stays reachable.
    reencoded_again = _pattern_png(4, 3, variant=0, compress_level=1)
    assert _sha256(reencoded_again) != _sha256(reencoded)
    gen3_zip = write_zip(
        scratch_dir / "gen3.zip", [("001.png", reencoded_again)]
    )
    _grant3, scan3 = _scan(stack, registry, gen3_zip)
    assert scan3["diff"][0]["evidence"] == "unique_pixel"
    assert scan3["diff"][0]["classification"] == "unchanged"
    persisted = _source_rows(conn, scan3["source"]["version_id"])
    assert persisted == []  # scan itself writes nothing


# ---------------------------------------------------------------------------
# AC-M3 scan → plan → apply chain for duplicate pixel occurrences
# ---------------------------------------------------------------------------


def test_duplicate_pixel_occurrences_scan_plan_defer_chain(
    conn, registry, stack, book_chapter, scratch_dir
):
    same_pixels = _pattern_png(4, 3, variant=0)
    variant_a = _pattern_png(4, 3, variant=0, compress_level=0)
    variant_b = _pattern_png(4, 3, variant=0, compress_level=1)
    _seed_source(
        conn, scratch_dir,
        [("001.png", variant_a), ("002.png", variant_b)],
        legacy_v7_evidence=False,
    )
    new_zip = write_zip(
        scratch_dir / "dup.zip",
        [("001.png", same_pixels),
         ("002.png", _pattern_png(4, 3, variant=0, compress_level=9))],
    )
    _grant_id, scan = _scan(stack, registry, new_zip)
    assert scan["totals"] == {
        "unchanged": 0, "added": 0, "missing": 0, "changed": 0,
        "ambiguous": 2,
    }
    for item in scan["diff"]:
        assert item["classification"] == "ambiguous"
        assert item["evidence"] == "duplicate_group"
        assert item["old_entry_id"] and item["new_entry_id"]

    body = build_plan_body(scan)
    decisions = default_decisions(scan)
    assert {decision["action"] for decision in decisions} == {"defer"}
    plan = stack["planner"].create(body)
    assert plan["body"]["totals"] == scan["totals"]
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
    bindings_before = conn.execute(
        "SELECT COUNT(*) FROM page_bindings"
    ).fetchone()[0]
    plan2, dispatch2 = run_full_sync(
        stack, scan, grant_ids=[_grant_id], decisions=decisions
    )
    assert dispatch2["state"] == "core-committed"
    assert plan2["body"]["totals"] == scan["totals"]
    bindings_after = conn.execute(
        "SELECT COUNT(*) FROM page_bindings"
    ).fetchone()[0]
    assert bindings_after == bindings_before, "defer never publishes a binding"
    for page_id in ("p1", "p2"):
        status = conn.execute(
            "SELECT status FROM page_bindings WHERE page_id = ?", (page_id,)
        ).fetchone()
        assert status["status"] == "healthy"


def test_apply_with_a_lost_scan_commits_no_content_binding_or_profile(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC-M5 ⑤: when the live scan is gone, apply cannot publish anything.

    A second stack sharing the same store has an empty live-scan registry, so
    the apply re-take fails typed and the frozen zero-write baseline holds.
    """
    from application.sources.ports import build_source_sync_stack
    from tests.fea11.test_source_sync import _freeze_plan, _op_payload

    _seed_source(
        conn, scratch_dir, [("001.png", _pattern_png(4, 3))],
        legacy_v7_evidence=True,
    )
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", _pattern_png(5, 2))])
    grant_id, scan = _scan(stack, registry, new_zip)
    body, plan = _freeze_plan(stack, scan)
    payload = _op_payload(
        scan, [grant_id], plan_id=body["plan_id"],
        plan_digest=plan["plan_digest"], operation_id="op-lost-scan-0001",
    )
    right = build_source_sync_stack(
        store=stack["store"], access=registry, repository=None
    )
    before = _snapshot(conn)
    with pytest.raises(Exception) as caught:
        right["service"].apply("ResyncSource", payload)
    assert getattr(caught.value, "code", ""), "apply must fail typed"
    after = _snapshot(conn)
    assert before == after, (
        "a lost scan must commit no content, binding or profile row"
    )


# ---------------------------------------------------------------------------
# ⑤ real v7 import fixture (production migrations + real import) → v8
# ---------------------------------------------------------------------------

def _wait_terminal(runtime, operation_id: str, timeout: float = 20.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two(
    tmp_path, scratch_dir, book_chapter
):
    """AC-M5: production v7 migrations + real import → v8 → scan/match.

    The v7 import writes the honest legacy shape (pixel/orientation NULL,
    width/height only on bound entries, decoder name on bound entries).  A
    changed container must degrade the bound W/H-only entry to
    ``ambiguous/missing_old`` while a byte-identical member still continues;
    after one resync generation the committed profiles make pixel matching
    reachable for the next generation.
    """
    from infrastructure.resource_channel.source_read_refs import (
        SourceReadGrantRegistry,
    )
    from infrastructure.sqlite.library import SqliteLibraryRepository
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations
    from infrastructure.sqlite.source_sync import SourceSyncStore

    migrations = default_migrations()
    conn = sqlite3.connect(
        ":memory:", check_same_thread=False, isolation_level=None
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(conn, migrations[:7]).apply_pending()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
        " updated_at) VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()

    image_one = _pattern_png(4, 3)
    image_two = _pattern_png(5, 2, variant=1)
    imported_zip = write_zip(
        scratch_dir / "imported.zip",
        [("001.png", image_one), ("002.png", image_two),
         ("notes.txt", b"plain notes")],
    )
    repo = SqliteLibraryRepository(conn)
    access = FakeSourceReadAccess()
    access.add_file("g-import-0000001", "zip", imported_zip, source_id="imported")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-import-0000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1",
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=["g-import-0000001"],
        duplicate_policy="skip",
        operation_id="op-v7-import-0001",
    )
    receipt = _wait_terminal(runtime, "op-v7-import-0001")
    assert receipt["state"] == "completed"

    # Honest legacy shape: pixel/orientation NULL, W/H only when bound, and a
    # non-empty decoder name on bound entries (never assert "all empty").
    legacy_rows = list(
        conn.execute(
            "SELECT locator, pixel_digest, pixel_digest_algorithm, width,"
            " height, orientation, decoder_name FROM source_entries"
            " ORDER BY ordinal"
        )
    )
    assert all(row["pixel_digest"] is None for row in legacy_rows)
    assert all(row["pixel_digest_algorithm"] is None for row in legacy_rows)
    assert all(row["orientation"] is None for row in legacy_rows)
    bound = [row for row in legacy_rows if row["decoder_name"]]
    assert bound, "real import must write DECODER_NAME on bound entries"
    assert all(row["width"] and row["height"] for row in bound)
    unbound = [row for row in legacy_rows if not row["decoder_name"]]
    assert unbound, "the plain-text member is not bound"
    assert all(row["width"] is None and row["height"] is None for row in unbound)

    MigrationRunner(conn, migrations).apply_pending()
    source_id = conn.execute("SELECT source_id FROM sources").fetchone()[0]
    registry = SourceReadGrantRegistry()
    store = SourceSyncStore(conn)
    from application.sources.ports import build_source_sync_stack

    stack = build_source_sync_stack(
        store=store, access=registry, repository=repo
    )

    # Generation 2: 001.png keeps the exact bytes (unique_pixel), 002.png
    # changes (v7 evidence is W/H-only → missing_old), notes.txt removed.
    changed_two = _pattern_png(5, 2, variant=2)
    gen2_zip = write_zip(
        scratch_dir / "gen2.zip",
        [("001.png", image_one), ("002.png", changed_two)],
    )
    grant2, scan2 = _scan(stack, registry, gen2_zip, source_id=source_id)
    assert scan2["totals"] == {
        "unchanged": 1, "added": 0, "missing": 0, "changed": 0,
        "ambiguous": 1,
    }
    by_new_locator = {
        entry["locator"]: entry for entry in scan2["source"]["entries"]
    }
    assert by_new_locator["001.png"]["pixel"] is not None
    assert by_new_locator["002.png"]["pixel"] is not None
    evidence_by_old = {
        item["old_entry_id"]: item["evidence"] for item in scan2["diff"]
    }
    assert "missing_old" in evidence_by_old.values()
    assert "unique_pixel" in evidence_by_old.values()

    # Apply with an explicit user decision: keep 001.png (byte identity) and
    # bind the now-degraded 002.png to its existing page (the honest repair a
    # user performs after reviewing a missing_old finding).  This publishes a
    # new generation whose rows carry the extracted profiles.
    decisions = []
    for item in scan2["diff"]:
        decisions.append(
            {
                "item_id": item["item_id"],
                "action": (
                    "bind"
                    if item["classification"] == "ambiguous"
                    else "keep"
                ),
                "target_page_id": item["page_id"],
                "target_chapter_id": None,
                "new_source_order": None,
                "new_sort_order": None,
                "migrate_revision_ids": [],
            }
        )
    run_full_sync(
        stack, scan2, grant_ids=[grant2], decisions=decisions
    )
    latest = store.latest_source_version(source_id)
    committed = {
        row["locator"]: row
        for row in _source_rows(conn, latest["version_id"])
    }
    assert committed["001.png"]["pixel_digest"]
    assert committed["002.png"]["pixel_digest"]
    assert committed["002.png"]["decoder_params_json"] == (
        canonical_pixel_params_json()
    )
    for page_id in {
        item["page_id"] for item in scan2["diff"] if item["page_id"]
    }:
        binding = conn.execute(
            "SELECT status FROM page_bindings WHERE page_id = ?"
            " AND status <> 'superseded'",
            (page_id,),
        ).fetchone()
        assert binding is not None and binding["status"] == "healthy"

    # Generation 3: 002.png re-encoded with the same pixels as generation 2;
    # the committed profile now makes pixel matching reachable for both pages.
    reencoded_two = _pattern_png(5, 2, variant=2, compress_level=0)
    assert _sha256(reencoded_two) != _sha256(changed_two)
    gen3_zip = write_zip(
        scratch_dir / "gen3.zip",
        [("001.png", image_one), ("002.png", reencoded_two)],
    )
    _grant3, scan3 = _scan(stack, registry, gen3_zip, source_id=source_id)
    assert scan3["totals"]["unchanged"] == 2, scan3["diff"]
    assert scan3["totals"]["ambiguous"] == 0, scan3["diff"]
    assert {item["evidence"] for item in scan3["diff"]} == {"unique_pixel"}
    conn.close()
