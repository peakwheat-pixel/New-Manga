import json
import struct
import sys
import zlib
import zipfile
from unittest.mock import patch

import pytest

from test_assets.comic_golden_suite.tools import assets


def make_png():
    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return assets.PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(b"\0\0\0\0")) + chunk(b"IEND", b"")


def make_webtoon_case(local_path="ko/test"):
    return {
        "case_id": "K-test",
        "language": "ko",
        "local_path": local_path,
        "asset_profile": {"kind": "hf_cleaned_webtoon", "files": ["page.png"]},
    }


def test_manifest_has_unique_cases_and_exact_taxonomy():
    manifest = assets.load_manifest()
    cases = manifest["cases"]
    assert len(cases) == 97
    assert len({case["case_id"] for case in cases}) == 97
    assert manifest["taxonomy"]["difficulty_tags"] == [
        "normal_dialogue", "dense_dialogue", "tiny_text", "huge_text",
        "vertical_text", "horizontal_text", "rotated_text", "curved_text",
        "fragmented_sfx", "overlapping_text", "complex_background", "low_contrast",
        "narration", "multi_speaker", "unusual_balloon", "extreme_size",
    ]
    assert len(assets.selected(manifest, "ko", "smoke")) == 10
    assert len(assets.selected(manifest, "ja", "smoke")) == 10
    assert {case["case_id"] for case in cases if case["case_id"] in {"K11", "K12", "K13"}} == {"K11", "K12", "K13"}
    assert all(case["levels"] == ["regression", "full"] for case in cases if case["case_id"] in {"K11", "K12", "K13"})
    assert all(case["pipeline_status"] == {stage: "NOT_RUN" for stage in case["expected_pipeline"]} for case in cases)


def test_black_jack_official_cases_are_registered_with_attribution():
    # M2-TA2B AC3/AC7: 12 BJ cases from the author's official free channel,
    # Japanese, RTL, attribution-bearing, regression/full only.
    manifest = assets.load_manifest()
    cases = {case["case_id"]: case for case in manifest["cases"]}
    bj_ids = [f"BJ{n:02d}" for n in range(1, 13)]
    assert all(case_id in cases for case_id in bj_ids)
    bj_cases = [cases[case_id] for case_id in bj_ids]
    assert all(case["language"] == "ja" for case in bj_cases)
    assert all(case["reading_direction"] == "right_to_left" for case in bj_cases)
    assert all(case["source_name"] == "Black Jack Official Free (Sato Manga Seisakusho)" for case in bj_cases)
    assert all(case["license_class"] == "commercial_use_permitted_attribution" for case in bj_cases)
    assert all(case["source_url"] == "https://densho810.com/free/" for case in bj_cases)
    assert all(case["attribution"] == "ブラックジャックによろしく　佐藤秀峰" for case in bj_cases)
    assert all("densho810.com" in case["attribution_note"] for case in bj_cases)
    assert all(case["asset_profile"]["kind"] == "manual_source_page" for case in bj_cases)
    assert all(case["levels"] == ["regression", "full"] for case in bj_cases)
    assert all(len(case["page_sha256"]) == 64 and case["render_dpi"] == 150 for case in bj_cases)
    assert {case["volume"] for case in bj_cases} == {1, 3, 5}
    # JASRAC volumes must never be selected.
    assert all(case["volume"] not in {2, 7, 11} for case in bj_cases)
    # Feature-matrix coverage across the 12 inspected pages.
    tagged = {tag for case in bj_cases for tag in case["tags"]}
    assert {
        "vertical_text", "horizontal_text", "normal_dialogue", "dense_dialogue", "tiny_text",
        "huge_text", "rotated_text", "fragmented_sfx", "complex_background", "low_contrast",
        "narration", "multi_speaker",
    } <= tagged


def test_manga109_scope_is_cancelled_by_user_ruling_2026_09_30():
    # M2-TA2B AC6: the 37 Manga109 title definitions and the related benchmark
    # sources stay as historical evidence with a cancellation marker; every other
    # field must remain untouched (frozen definitions).
    manifest = assets.load_manifest()
    m109 = [case for case in manifest["cases"] if case["asset_type"] == "manga109_title"]
    assert len(m109) == 37
    assert all(case.get("removed_from_scope_2026-09-30") is True for case in m109)
    assert all(case["asset_status"] == "MISSING_GATED_ASSET" for case in m109)
    by_id = {source["id"]: source for source in manifest["benchmark_sources"]}
    for source_id in ("manga109_selected_or_full", "jmangabench", "text_mask"):
        assert by_id[source_id].get("removed_from_scope_2026-09-30") is True, source_id


def test_openmantra_stays_isolated_noncommercial_optional():
    # M2-TA2B AC5: OpenMantra (CC BY-NC 4.0) may exist locally in an isolated
    # gitignored directory, but must never join the production licensing
    # baseline, ordinary levels, or Git.
    manifest = assets.load_manifest()
    by_id = {source["id"]: source for source in manifest["benchmark_sources"]}
    om = by_id["openmantra_candidate"]
    assert om.get("optional_noncommercial_baseline_excluded") is True
    assert om["status"] == "READY_OPTIONAL_ISOLATED"
    assert om["local_path"] == "日漫_JA/99_optional_openmantra"
    assert om["local_file_count"] > 0
    assert om["checksum_inventory"] is None
    assert not any(
        case["local_path"].startswith("日漫_JA/99_optional_openmantra") for case in manifest["cases"]
    )


def test_peppercarrot_additions_extend_ja_ko_open_pool():
    # M2-TA2B AC4: previously unregistered language-pack pages are registered
    # and downloaded through the existing Pepper&Carrot channel.
    manifest = assets.load_manifest()
    cases = {case["case_id"]: case for case in manifest["cases"]}
    ja_new = [f"J{n}" for n in range(48, 53)]
    ko_new = [f"K{n}" for n in range(14, 26)]
    assert all(case_id in cases for case_id in ja_new + ko_new)
    for case_id in ja_new:
        case = cases[case_id]
        assert case["language"] == "ja"
        assert case["asset_profile"]["transcript_member"].startswith("lang/ja/")
        assert case["asset_status"] == "READY"
    for case_id in ko_new:
        case = cases[case_id]
        assert case["language"] == "ko"
        assert case["asset_profile"]["transcript_member"].startswith("lang/kr/")
        assert case["asset_profile"]["image_filename"].startswith("kr_Pepper-and-Carrot")
        assert case["asset_status"] == "READY"


def test_source_registry_does_not_count_code_or_blocked_assets_as_ready():
    manifest = assets.load_manifest()
    sources = manifest["benchmark_sources"]
    by_id = {source["id"]: source for source in sources}
    assert len({source["id"] for source in sources}) == len(sources)
    assert all(case["source_id"] and case["source_url"].startswith("https://") for case in manifest["cases"])
    assert all(source["local_file_count"] > 0 for source in sources if source["status"] == "READY")
    assert all(source["local_file_count"] == 0 for source in sources if source["id"] in {
        "jmangabench", "text_mask", "artificial_manga", "ebdtheque", "public_domain_japan"
    })
    assert all(not case["image_available"] for case in manifest["cases"] if case["asset_type"] == "manga109_title")
    assert by_id["ko_sfx_dialogue_cleaned_webtoon"]["status"] == "READY"
    assert all(by_id[source_id]["checksum_inventory"] == "test_assets/comic_golden_suite/manifests/local_asset_inventory.json" for source_id in (
        "coo_and_manga109_dialog", "peppercarrot_japanese_localized_pages", "peppercarrot_korean_localized_pages"
    ))


def test_manifest_rejects_path_escape(tmp_path):
    source = json.loads(assets.MANIFEST_PATH.read_text(encoding="utf-8"))
    source["cases"][0]["local_path"] = "../outside"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(source), encoding="utf-8")
    with patch.object(assets, "MANIFEST_PATH", manifest_path):
        with pytest.raises(ValueError, match="escapes suite"):
            assets.load_manifest()


@pytest.mark.parametrize("url", [
    "https://evil.example/x",
    "http://www.peppercarrot.com/kr/webcomic-sources/ep06_The-Potion-Contest.html",
])
def test_manifest_rejects_non_whitelisted_source_url(tmp_path, url):
    source = json.loads(assets.MANIFEST_PATH.read_text(encoding="utf-8"))
    source["cases"][0]["source_url"] = url
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(source), encoding="utf-8")
    with patch.object(assets, "MANIFEST_PATH", manifest_path):
        with pytest.raises(ValueError, match="whitelist"):
            assets.load_manifest()


def test_densho810_is_whitelisted_and_lookalikes_stay_rejected():
    # M2-TA2B AC7: the author's official free channel joined the fail-closed
    # whitelist. validate_source_url is host-level (path-agnostic), so any
    # https path on the exact host is accepted, while lookalike hosts, plain
    # HTTP, and non-standard ports stay rejected.
    assert "densho810.com" in assets.SOURCE_URL_HOSTS
    assets.validate_source_url("BJ-test", "https://densho810.com/free/")
    assets.validate_source_url("BJ-test", "https://densho810.com/free/dl/001bj.zip")
    for url in (
        "https://densho810.com.evil.example/free/",
        "http://densho810.com/free/",
        "https://densho810.com:8443/free/",
    ):
        with pytest.raises(ValueError, match="whitelist"):
            assets.validate_source_url("BJ-test", url)


def benchmark_inventory_params():
    manifest = assets.load_manifest()
    return [
        pytest.param(source["id"], source["checksum_inventory"], id=source["id"])
        for source in manifest["benchmark_sources"]
        if isinstance(source.get("checksum_inventory"), str) and source["checksum_inventory"]
    ]


@pytest.mark.parametrize(("source_id", "inventory_path"), benchmark_inventory_params())
def test_benchmark_checksum_inventory_paths_exist(source_id, inventory_path):
    # Runtime consumption for benchmark_sources[*].checksum_inventory (TA2C P3-10):
    # every non-empty path must exist relative to the repository root.
    assert (assets.REPO_ROOT / inventory_path).is_file(), (
        f"benchmark source {source_id} checksum_inventory is missing: {inventory_path}"
    )


def test_ko_sfx_dialogue_cleaned_webtoon_inventory_semantics():
    # README semantics: checksum_inventory == null means "no locally verifiable
    # files for this source". Reconnaissance (2026-09-29) shows this entry is NOT
    # null: it pins the KO Cleaned Webtoon audit manifest, so assert the concrete
    # value and its presence instead of a null assertion.
    manifest = assets.load_manifest()
    by_id = {source["id"]: source for source in manifest["benchmark_sources"]}
    inventory_path = by_id["ko_sfx_dialogue_cleaned_webtoon"]["checksum_inventory"]
    assert inventory_path == "verification/M2-TA2C/ko-webtoon-audit.json"
    assert (assets.REPO_ROOT / inventory_path).is_file()


def test_benchmark_inventory_missing_path_detection_demo():
    # Discriminative demo (TA2C P3-10): a checksum_inventory pointing at a
    # nonexistent path must be reported as a failure by the runtime consumer,
    # while the real manifest stays green. The "red" side is demonstrated by
    # calling the checker directly on a mutated copy, not by breaking CI.
    manifest = assets.load_manifest()
    healthy_failures, healthy_checked = assets.verify_benchmark_source_inventories(manifest)
    assert healthy_failures == []
    assert healthy_checked == sum(
        1 for source in manifest["benchmark_sources"]
        if isinstance(source.get("checksum_inventory"), str) and source["checksum_inventory"]
    )

    broken = json.loads(json.dumps(manifest))
    next(source for source in broken["benchmark_sources"] if source["id"] == "ko_sfx_dialogue_cleaned_webtoon")[
        "checksum_inventory"
    ] = "verification/M2-TA2C/does-not-exist.json"
    failures, checked = assets.verify_benchmark_source_inventories(broken)
    assert failures == [
        "ko_sfx_dialogue_cleaned_webtoon: checksum_inventory file is missing: verification/M2-TA2C/does-not-exist.json"
    ]
    assert checked == healthy_checked - 1


def test_ko_ground_truth_directory_naming_snapshot():
    # Known observation (TA2C DSH r2 P3-6): the two KO Pepper&Carrot families use
    # different directory naming prefixes (02_open_ for O01-O08 manual source
    # pages, 02_public_ for the K11-K13 localized pages), while JA pages always
    # use 02_open_. On-disk renames are deliberately out of scope (local asset
    # path stability); this snapshot pins the current naming so any drift turns
    # red, and each affected case carries a naming_note field in cases.json.
    manifest = assets.load_manifest()
    cases = {case["case_id"]: case for case in manifest["cases"]}
    for case_id in [f"O{n:02d}" for n in range(1, 9)]:
        assert cases[case_id]["local_path"].startswith("韩漫_KO/02_open_ground_truth_peppercarrot/"), case_id
        assert "naming_note" in cases[case_id], case_id
    for case_id in [f"K{n}" for n in range(11, 26)]:
        assert cases[case_id]["local_path"].startswith("韩漫_KO/02_public_ground_truth_peppercarrot/"), case_id
        assert "naming_note" in cases[case_id], case_id
    for case_id in ("J38", "J39", "J40"):
        assert cases[case_id]["local_path"].startswith("日漫_JA/02_open_ground_truth_peppercarrot/"), case_id


def test_download_skips_existing_file_without_network(tmp_path):
    case = {
        "case_id": "K-test",
        "source_id": "test",
        "asset_profile": {
            "kind": "hf_cleaned_webtoon",
            "repo_subpath": "examples",
            "resolve_url": "https://huggingface.co/datasets/example/resolve/main",
            "files": ["base.png"],
        },
    }
    existing = tmp_path / "base.png"
    existing.write_bytes(b"keep")
    with patch.object(assets, "local_dir", return_value=tmp_path), patch.object(assets.urllib.request, "urlopen") as fetch:
        downloaded, skipped, failed = assets.download_case(case)
    fetch.assert_not_called()
    assert (downloaded, skipped) == (0, 1)
    assert not failed
    assert existing.read_bytes() == b"keep"


def test_failed_download_cleans_partial_file(tmp_path):
    case = {
        "case_id": "K-test",
        "source_id": "test",
        "asset_profile": {
            "kind": "hf_cleaned_webtoon",
            "repo_subpath": "examples",
            "resolve_url": "https://huggingface.co/datasets/example/resolve/main",
            "files": ["base.png"],
        },
    }

    class BrokenResponse:
        headers = {"Content-Length": "100"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, _size):
            raise OSError("simulated network interruption")

    with patch.object(assets, "local_dir", return_value=tmp_path), patch.object(
        assets.urllib.request, "urlopen", return_value=BrokenResponse()
    ):
        downloaded, skipped, failed = assets.download_case(case)
    assert (downloaded, skipped) == (0, 0)
    assert failed
    assert not (tmp_path / "base.png").exists()
    assert not list(tmp_path.glob("*.part"))


def test_gated_cases_are_not_fetched(tmp_path):
    case = {
        "case_id": "J-test",
        "asset_profile": {"kind": "manga109_title"},
    }
    with patch.object(assets, "local_dir", return_value=tmp_path), patch.object(assets.urllib.request, "urlopen") as fetch:
        downloaded, skipped, failed = assets.download_case(case)
    fetch.assert_not_called()
    assert (downloaded, skipped) == (0, 0)
    assert not failed
    assert assets.status({"asset_profile": {"kind": "manga109_title"}, "local_path": "absent"}) == "MISSING_GATED_ASSET"


def test_clean_eof_before_content_length_does_not_publish_asset(tmp_path):
    case = {
        "case_id": "K-test",
        "source_id": "123_1",
        "asset_profile": {
            "kind": "hf_cleaned_webtoon",
            "repo_subpath": "examples",
            "resolve_url": "https://huggingface.co/datasets/example/resolve/main",
            "files": ["base.png"],
        },
    }

    class ShortResponse:
        headers = {"Content-Length": "100"}

        def __init__(self):
            self.reads = iter((b"partial", b""))

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, _size):
            return next(self.reads)

    with patch.object(assets, "local_dir", return_value=tmp_path), patch.object(
        assets.urllib.request, "urlopen", return_value=ShortResponse()
    ):
        downloaded, skipped, failed = assets.download_case(case)
    assert (downloaded, skipped, failed) == (0, 0, True)
    assert not (tmp_path / "base.png").exists()
    assert not list(tmp_path.glob("*.part"))


def test_partial_manual_and_gated_titles_never_report_ready(tmp_path):
    with patch.object(assets, "ROOT", tmp_path):
        manual = {"case_id": "O-test", "local_path": "open/O-test", "asset_profile": {"kind": "manual_source_page"}}
        assets.local_dir(manual).mkdir(parents=True)
        (assets.local_dir(manual) / "one-file.bin").write_bytes(b"partial")
        assert assets.status(manual) == "PARTIAL"

        manga = {"case_id": "J-test", "source_id": "Title", "local_path": "ja/Title", "asset_profile": {"kind": "manga109_title"}}
        image_dir = assets.local_dir(manga) / "images"
        image_dir.mkdir(parents=True)
        (image_dir / "Title_001.jpg").write_bytes(b"\xff\xd8\xff\xd9")
        assert assets.status(manga) == "PARTIAL"


def test_webtoon_list_status_checks_png_structure(tmp_path, capsys):
    case = make_webtoon_case()
    with patch.object(assets, "ROOT", tmp_path):
        image = assets.local_dir(case) / "page.png"
        image.parent.mkdir(parents=True)
        valid = make_png()
        image.write_bytes(valid)
        assert assets.status(case) == "READY"

        damaged = bytearray(valid)
        damaged[-1] ^= 0x01
        image.write_bytes(damaged)
        statuses = assets.print_cases([case])

    assert statuses["K-test"] == "PARTIAL"
    assert "K-test\tko\tPARTIAL" in capsys.readouterr().out


def test_verify_fails_when_public_smoke_page_is_missing(tmp_path, capsys):
    manifest = assets.load_manifest()
    case = next(case.copy() for case in manifest["cases"] if case["case_id"] == "J38")
    case["local_path"] = "ja/absent"
    manifest["cases"] = [case]
    manifest_path = tmp_path / "cases.json"
    inventory_path = tmp_path / "local_asset_inventory.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    inventory_path.write_text(json.dumps({"assets": []}), encoding="utf-8")

    with patch.object(assets, "ROOT", tmp_path), patch.object(assets, "MANIFEST_PATH", manifest_path), patch.object(
        assets, "INVENTORY_PATH", inventory_path
    ), patch.object(sys, "argv", ["assets.py", "verify", "--language", "ja", "--level", "smoke"]):
        assert assets.main() == 1

    output = capsys.readouterr().out
    assert "J38\tja\tMISSING" in output
    assert "INVALID\tJ38" in output


def test_official_manga_archive_import_is_selective_and_idempotent(tmp_path):
    case = {
        "case_id": "J-test",
        "source_id": "Title",
        "local_path": "ja/Title",
        "asset_profile": {"kind": "manga109_title"},
    }
    archive_path = tmp_path / "Manga109.zip"
    xml = b'<book title="Title"><pages><page index="3" /></pages></book>'
    jpeg = b"\xff\xd8\xff\xd9"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("release/images/Title/003.jpg", jpeg)
        archive.writestr("release/annotations/Title.xml", xml)
        archive.writestr("release/images/Other/Other_001.jpg", jpeg)

    with patch.object(assets, "ROOT", tmp_path / "suite"):
        with zipfile.ZipFile(archive_path) as archive:
            imported, skipped = assets.import_manga_case(archive, case, archive_path.name)
            assert (imported, skipped) == (3, 0)
        assert assets.status(case) == "READY"
        assert assets.validate_manga_case(case) == (True, "title images and annotations present")
        with zipfile.ZipFile(archive_path) as archive:
            imported, skipped = assets.import_manga_case(archive, case, archive_path.name)
        assert (imported, skipped) == (0, 3)
        assert len(list((assets.local_dir(case) / "images").glob("*.jpg"))) == 1
        (assets.local_dir(case) / "annotations.xml").write_text(
            '<book title="Title"><pages><page index="invalid" /></pages></book>', encoding="utf-8"
        )
        assert not assets.validate_manga_case(case)[0]


def test_manga_archive_rejects_zip_slip_paths(tmp_path):
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("release/images/Title/../../escape.jpg", b"bad")
    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(ValueError, match="unsafe path"):
            assets.manga_members(archive, "Title")
    assert not (tmp_path / "escape.jpg").exists()


def test_manga_archive_page_names_must_match_annotation_indices(tmp_path):
    archive_path = tmp_path / "mismatch.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("images/Title/000.jpg", b"\xff\xd8\xff\xd9")
        archive.writestr("annotations/Title.xml", b'<book title="Title"><pages><page index="3" /></pages></book>')
    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(ValueError, match="page names do not match"):
            assets.manga_members(archive, "Title")
