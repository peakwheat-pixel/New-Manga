"""FEA-11-RENDITION-1 (I-2): provider pixels come from the CURRENT binding.

Every fixture here is REAL: two/three genuinely different PNG images generated
with Pillow, a real zip container, a real HMAC-signed source-read grant over
that container, a real v8 SQLite library and the REAL production
``_ManagedPageImageSource`` class (no stub image source anywhere — the
``_StubImages`` pattern of ``test_source_lineage_run.py`` is deliberately not
used).

Discriminators:
* the OLD Managed Copy ``A`` (30x20, red with a black top-left block) and the
  current binding's entry ``B`` (12x7, green with a blue bottom-right block)
  differ in BOTH dimensions and pixels, so "size matches" alone cannot pass;
* a third entry ``C`` (20x9) proves the reader follows the binding, not the
  first archive member;
* the managed page sentinel fails on ANY grant/gate access, so the managed
  branch provably reads neither;
* the referenced refusals are typed, path-free, and provably happen BEFORE the
  entry bytes are read (spy counter on the reader).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import inspect
import io
from pathlib import Path

import pytest

from application.importing.referenced import reader as referenced_reader
from application.importing.referenced import resolve as resolve_module
from bootstrap.core_assembly import _ManagedPageImageSource
from domain.regions.entities import BBox, Region, RegionGeometry
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.resource_channel import rendition_cache as rendition_cache_module
from infrastructure.resource_channel.handle_resolver import ManagedRootTrust
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.regions import SqliteRegionRepository
from ports.inpaint.ports import ImageFrame
from ports.providers.errors import ProviderInputError
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    mint_grant,
    write_zip,
)

#: The OLD image A: 30x20 red with a black block at the top-left. It is what a
#: Managed-Copy-only reader would return (L10②).
OLD_A = {
    "width": 30,
    "height": 20,
    "background": (210, 30, 30),
    "block": (0, 0, 8, 6),
    "block_color": (5, 5, 5),
}
#: Entry 1: an older archive member C, 20x9 yellow with a magenta block.
OLD_ENTRY_C = {
    "width": 20,
    "height": 9,
    "background": (225, 195, 20),
    "block": (1, 1, 5, 5),
    "block_color": (190, 20, 190),
}
#: Entry 2, the CURRENT binding: B, 12x7 green with a blue block at (8, 2).
NEW_B = {
    "width": 12,
    "height": 7,
    "background": (20, 190, 40),
    "block": (8, 2, 4, 4),
    "block_color": (25, 55, 215),
}


# ---------------------------------------------------------------------------
# real fixtures
# ---------------------------------------------------------------------------


def png_of(spec: dict) -> bytes:
    """A real PNG whose pixels carry a discriminating marker block."""
    from PIL import Image

    image = Image.new("RGB", (spec["width"], spec["height"]), spec["background"])
    x, y, width, height = spec["block"]
    for px in range(x, x + width):
        for py in range(y, y + height):
            image.putpixel((px, py), spec["block_color"])
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def frame_image(frame: ImageFrame):
    """``rgb32`` payload (BGRA, alpha forced) back to a Pillow RGB image."""
    from PIL import Image

    rgba = Image.frombytes(
        "RGBA", (frame.width, frame.height), frame.data, "raw", "BGRA"
    )
    return rgba.convert("RGB")


def png_image(data: bytes):
    from PIL import Image

    image = Image.open(io.BytesIO(data))
    image.load()
    return image.convert("RGB")


@dataclass
class RenditionSite:
    """A real referenced page whose CURRENT binding is archive entry 2 (B)."""

    conn: object
    page_id: str
    chapter_id: str
    book_id: str
    managed_root: Path
    archive_path: Path
    b_digest: str
    c_digest: str
    grant_id: str
    registry: SourceReadGrantRegistry
    storage: ManagedFileStorage
    repository: SqliteLibraryRepository
    regions: SqliteRegionRepository
    gate_state: dict[str, str] = field(default_factory=lambda: {"value": "open"})

    def gate(self, page_id: str) -> str:
        return self.gate_state["value"]

    def image_source(
        self,
        *,
        access=None,
        gate=None,
        image_decoder=None,
    ) -> _ManagedPageImageSource:
        return _ManagedPageImageSource(
            self.repository,
            self.storage,
            self.regions,
            root_trust=ManagedRootTrust.capture(self.managed_root),
            source_access=self.registry if access is None else access,
            read_gate=self.gate if gate is None else gate,
            image_decoder=image_decoder,
        )

    def add_page(self, page_id: str, *, source_mode: str = "managed") -> None:
        """A page row with a real Managed Copy file under the managed root."""
        ref = f"legacy/{page_id}.png"
        (self.managed_root / "legacy").mkdir(parents=True, exist_ok=True)
        (self.managed_root / ref).write_bytes(png_of(OLD_A))
        self.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
            " updated_at, source_filename, source_order, source_hash,"
            " source_size_bytes, width, height, managed_original_ref,"
            " source_mode, integrity_status)"
            " VALUES (?, ?, 2, ?, ?, ?, 2, ?, 10, ?, ?, ?, ?, 'complete')",
            (
                page_id,
                self.chapter_id,
                NOW,
                NOW,
                f"{page_id}.png",
                "b" * 64,
                OLD_A["width"],
                OLD_A["height"],
                ref,
                source_mode,
            ),
        )
        self.conn.commit()


def build_rendition_site(
    conn,
    book_chapter,
    tmp_path: Path,
    registry: SourceReadGrantRegistry,
    *,
    new_member_bytes: bytes | None = None,
    budget: dict | None = None,
    bind_grant: bool = True,
    publish_gate: str | None = None,
    managed_copy: bool = True,
) -> RenditionSite:
    """Real library + managed root + source zip + grant over one archive."""
    book_id, chapter_id = book_chapter
    managed_root = tmp_path / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    storage = ManagedFileStorage(managed_root)
    storage.ensure_layout()
    (managed_root / "legacy").mkdir(parents=True, exist_ok=True)
    (managed_root / "legacy" / "old-a.png").write_bytes(png_of(OLD_A))

    current_bytes = png_of(NEW_B) if new_member_bytes is None else new_member_bytes
    archive_path = write_zip(
        tmp_path / "current-source.zip",
        [
            ("001-old.png", png_of(OLD_ENTRY_C)),
            ("002-current.png", current_bytes),
        ],
    )
    b_digest = hashlib.sha256(current_bytes).hexdigest()
    c_digest = hashlib.sha256(png_of(OLD_ENTRY_C)).hexdigest()
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest="a" * 64,
        entries=[
            ("se1", "001-old.png", c_digest),
            ("se2", "002-current.png", b_digest),
        ],
        legacy_v7_evidence=False,
    )
    add_referenced_page(
        conn,
        "pr",
        chapter_id,
        book_id,
        order=1,
        source_id="s1",
        version_id="sv1",
        entry_id="se2",
        digest=b_digest,
        width=NEW_B["width"],
        height=NEW_B["height"],
    )
    # Mixed page shape (L-R5): the referenced page ALSO has a stale managed
    # copy. The provider must ignore it; the Run target gate keeps the old
    # admission for it byte for byte. ``managed_copy=False`` builds the PURE
    # referenced shape instead (add_referenced_page's default) — that is the
    # shape the new Run-target admission is about.
    if managed_copy:
        conn.execute(
            "UPDATE pages SET managed_original_ref = 'legacy/old-a.png'"
            " WHERE page_id = 'pr'"
        )
        conn.commit()
    if publish_gate is not None:
        conn.execute(
            "INSERT INTO source_binding_publications (binding_id, operation_id,"
            " previous_binding_id, relation, read_gate, opened_at)"
            " VALUES ('pb-pr', NULL, NULL, 'initial', ?, ?)",
            (publish_gate, NOW),
        )
        conn.commit()
    grant_id, _facts = mint_grant(
        registry,
        source_id="s1",
        version="sv1",
        kind="zip",
        entries=[(str(archive_path), "002-current.png", 1)],
        budget=budget,
    )
    if bind_grant:
        registry.bind_imported_entry(grant_id, "s1", "sv1", "se2")
    return RenditionSite(
        conn=conn,
        page_id="pr",
        chapter_id=chapter_id,
        book_id=book_id,
        managed_root=managed_root,
        archive_path=archive_path,
        b_digest=b_digest,
        c_digest=c_digest,
        grant_id=grant_id,
        registry=registry,
        storage=storage,
        repository=SqliteLibraryRepository(conn),
        regions=SqliteRegionRepository(conn),
    )


@pytest.fixture()
def site(conn, book_chapter, tmp_path, registry) -> RenditionSite:
    return build_rendition_site(conn, book_chapter, tmp_path, registry)


# ---------------------------------------------------------------------------
# AC-R2: pixels and geometry come from the current binding's rendition
# ---------------------------------------------------------------------------


def test_page_frame_pixels_are_the_binding_rendition_not_the_managed_copy(site):
    frame = site.image_source().page_frame(site.page_id)

    # Dimension discriminator: 12x7 (B) vs 30x20 (the stale managed copy A).
    assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])
    image = frame_image(frame)
    assert image.getpixel((0, 0)) == NEW_B["background"]
    x, y, _width, _height = NEW_B["block"]
    assert image.getpixel((x, y)) == NEW_B["block_color"]
    # Pixel discriminator: the managed copy's marker (black at 0,0) is absent.
    assert image.getpixel((0, 0)) != OLD_A["block_color"]


def test_page_png_is_the_rendition_png_of_the_current_binding(site):
    png = site.image_source().page_png(site.page_id)

    assert png.startswith(b"\x89PNG")
    image = png_image(png)
    assert image.size == (NEW_B["width"], NEW_B["height"])
    assert image.getpixel((0, 0)) == NEW_B["background"]
    x, y, _width, _height = NEW_B["block"]
    assert image.getpixel((x, y)) == NEW_B["block_color"]


def test_region_crop_is_taken_in_the_rendition_coordinate_system(site):
    block_x, block_y, block_w, block_h = NEW_B["block"]
    site.regions.add_region(
        Region(
            region_id="rg-blue",
            page_id=site.page_id,
            geometry=RegionGeometry(
                bbox=BBox(block_x, block_y, block_w, block_h),
                polygon=(
                    (block_x, block_y),
                    (block_x + block_w, block_y),
                    (block_x + block_w, block_y + block_h),
                    (block_x, block_y + block_h),
                ),
            ),
            reading_order=1,
        )
    )

    crop, width, height = site.image_source().region_crop(site.page_id, "rg-blue")

    assert (width, height) == (block_w, block_h)
    image = png_image(crop)
    assert image.size == (block_w, block_h)
    assert image.getpixel((0, 0)) == NEW_B["block_color"]


def test_mixed_page_never_reads_the_stale_managed_copy(site, monkeypatch):
    """The stale managed original is UNREADABLE yet the pixels are still B."""

    def _forbidden(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("a referenced page must never read the managed copy")

    monkeypatch.setattr(ManagedRootTrust, "read_bytes", _forbidden)

    frame = site.image_source().page_frame(site.page_id)

    assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])


def test_repointing_the_binding_changes_the_pixels(site):
    """The reader follows the CURRENT binding, not the first archive member."""
    source = site.image_source()
    assert source.page_frame(site.page_id).width == NEW_B["width"]

    site.conn.execute(
        "UPDATE page_bindings SET entry_id = 'se1', verified_digest = ?"
        " WHERE page_id = ?",
        (site.c_digest, site.page_id),
    )
    site.conn.commit()
    site.registry.bind_imported_entry(site.grant_id, "s1", "sv1", "se1")

    frame = source.page_frame(site.page_id)

    assert (frame.width, frame.height) == (
        OLD_ENTRY_C["width"],
        OLD_ENTRY_C["height"],
    )
    assert frame_image(frame).getpixel((0, 0)) == OLD_ENTRY_C["background"]


# ---------------------------------------------------------------------------
# AC-R3: the managed branch is untouched and never touches grant/gate
# ---------------------------------------------------------------------------


class _ForbiddenAccess:
    """Any grant-registry access from a managed page is a test failure."""

    def __getattr__(self, name):  # noqa: ANN001, ANN204
        raise AssertionError(f"managed page must not touch the grant registry ({name})")


def _forbidden_gate(page_id: str) -> str:
    raise AssertionError("managed page must not consult the publication gate")


def test_managed_page_reads_the_managed_copy_and_never_touches_grant_or_gate(site):
    site.add_page("pm", source_mode="managed")

    source = site.image_source(
        access=_ForbiddenAccess(), gate=_forbidden_gate
    )
    frame = source.page_frame("pm")
    png = source.page_png("pm")

    assert (frame.width, frame.height) == (OLD_A["width"], OLD_A["height"])
    image = frame_image(frame)
    assert image.getpixel((0, 0)) == OLD_A["block_color"]
    assert png_image(png).getpixel((0, 0)) == OLD_A["block_color"]


def test_managed_page_without_a_managed_original_stays_the_historical_refusal(
    site,
):
    site.add_page("pm", source_mode="managed")
    site.conn.execute(
        "UPDATE pages SET managed_original_ref = NULL WHERE page_id = 'pm'"
    )
    site.conn.commit()

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame("pm")

    assert info.value.detail == "page 'pm' has no managed original"
    assert info.value.error_code == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# AC-R4: typed refusals happen BEFORE the source bytes are read
# ---------------------------------------------------------------------------


def _spy_reader(monkeypatch) -> list[tuple]:
    calls: list[tuple] = []
    original = referenced_reader.read_entry_bytes

    def spy(*args, **kwargs):  # noqa: ANN002, ANN003
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(referenced_reader, "read_entry_bytes", spy)
    return calls


def test_pending_gate_refuses_before_reading_the_source(site, monkeypatch):
    calls = _spy_reader(monkeypatch)
    site.gate_state["value"] = "pending"

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert "pending" in info.value.detail
    assert calls == [], "no source byte may be read while the gate is pending"


def test_unavailable_gate_refuses_before_reading_the_source(site, monkeypatch):
    calls = _spy_reader(monkeypatch)
    site.gate_state["value"] = "unavailable"

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert "unavailable" in info.value.detail
    assert calls == []


def test_missing_live_grant_is_typed_and_reads_zero_bytes(site, monkeypatch):
    calls = _spy_reader(monkeypatch)

    with pytest.raises(ProviderInputError) as info:
        site.image_source(access=SourceReadGrantRegistry()).page_frame(site.page_id)

    assert "SOURCE_ACCESS_DENIED" in info.value.detail
    assert calls == []


def test_revoked_session_grant_is_typed_and_reads_zero_bytes(site, monkeypatch):
    calls = _spy_reader(monkeypatch)
    site.registry.revoke_all_for_session()

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert any(
        code in info.value.detail
        for code in ("SOURCE_ACCESS_DENIED", "SOURCE_GRANT_REVOKED")
    )
    assert calls == []


def test_page_whose_bound_entry_disappeared_is_typed_and_reads_zero_bytes(
    conn, book_chapter, tmp_path, registry, monkeypatch
):
    site = build_rendition_site(conn, book_chapter, tmp_path, registry)
    # The entry content no longer matches the binding witness: V(p,t) is false,
    # so the page is not even readable — a typed refusal, never a KeyError.
    conn.execute(
        "UPDATE source_entries SET content_digest = ?, encoded_digest = ?"
        " WHERE entry_id = 'se2'",
        ("0" * 64, "0" * 64),
    )
    conn.commit()
    calls = _spy_reader(monkeypatch)

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert info.value.error_code == "INVALID_INPUT"
    assert calls == []


def test_corrupt_entry_is_a_typed_refusal(conn, book_chapter, tmp_path, registry):
    site = build_rendition_site(
        conn,
        book_chapter,
        tmp_path,
        registry,
        new_member_bytes=b"this is not an image",
    )

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert "SOURCE_FORMAT_UNSUPPORTED" in info.value.detail


def test_decode_budget_refusal_is_typed(conn, book_chapter, tmp_path, registry):
    site = build_rendition_site(
        conn,
        book_chapter,
        tmp_path,
        registry,
        budget={"max_bytes": 8 * 1024 * 1024, "max_decode_bytes": 1, "max_entries": 10},
    )

    with pytest.raises(ProviderInputError) as info:
        site.image_source().page_frame(site.page_id)

    assert "SOURCE_BUDGET_EXCEEDED" in info.value.detail


def test_refusal_detail_never_leaks_a_path_or_entry_name(site):
    with pytest.raises(ProviderInputError) as info:
        site.image_source(access=SourceReadGrantRegistry()).page_frame(site.page_id)

    detail = info.value.detail
    assert "SOURCE_ACCESS_DENIED" in detail
    assert str(site.archive_path) not in detail
    assert site.archive_path.name not in detail
    assert "002-current.png" not in detail


# ---------------------------------------------------------------------------
# AC-R5: one selection rule, no cache, no publication
# ---------------------------------------------------------------------------


def test_provider_reuses_the_single_selection_function_and_never_caches(site, monkeypatch):
    selections: list[tuple] = []
    original = resolve_module.prepare_referenced_rendition

    def spy(page_id, *, repository, access):
        prepared = original(page_id, repository=repository, access=access)
        selections.append(
            (
                prepared["source_id"],
                prepared["version_id"],
                prepared["entry_id"],
                prepared["decoder_name"],
                prepared["decoder_version"],
                prepared["params_digest"],
                prepared["verified_digest"],
                prepared["rendition_kind"],
            )
        )
        return prepared

    monkeypatch.setattr(resolve_module, "prepare_referenced_rendition", spy)

    def _no_cache(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("the provider must not touch rendition_cache")

    monkeypatch.setattr(rendition_cache_module.RenditionCache, "acquire", _no_cache)

    before_artifacts = site.conn.execute(
        "SELECT count(*) AS n FROM media_artifacts"
    ).fetchone()["n"]
    frame = site.image_source().page_frame(site.page_id)

    assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])
    assert len(selections) == 1, "the provider must go through the ONE selection entry point"
    expected = original(site.page_id, repository=site.repository, access=site.registry)
    assert selections[0] == (
        expected["source_id"],
        expected["version_id"],
        expected["entry_id"],
        expected["decoder_name"],
        expected["decoder_version"],
        expected["params_digest"],
        expected["verified_digest"],
        expected["rendition_kind"],
    )
    # No rendition cache row, no published artifact, no second rendition kind.
    assert site.conn.execute(
        "SELECT count(*) AS n FROM rendition_cache"
    ).fetchone()["n"] == 0
    assert site.conn.execute(
        "SELECT count(*) AS n FROM media_artifacts"
    ).fetchone()["n"] == before_artifacts == 0
    # L-R7: the prepared cache-key field is a DIFFERENT derivation from
    # ``RenditionCache.rendition_key`` and must never be adopted here.
    assert '"cache_key"' not in inspect.getsource(_ManagedPageImageSource)
