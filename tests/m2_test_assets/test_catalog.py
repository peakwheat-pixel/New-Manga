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
    assert len(cases) == 68
    assert len({case["case_id"] for case in cases}) == 68
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


def test_source_registry_does_not_count_code_or_blocked_assets_as_ready():
    manifest = assets.load_manifest()
    sources = manifest["benchmark_sources"]
    assert len({source["id"] for source in sources}) == len(sources)
    assert all(case["source_id"] and case["source_url"].startswith("https://") for case in manifest["cases"])
    assert all(source["local_file_count"] > 0 for source in sources if source["status"] == "READY")
    assert all(source["local_file_count"] == 0 for source in sources if source["id"] in {
        "openmantra_candidate", "jmangabench", "text_mask", "artificial_manga", "ebdtheque", "public_domain_japan"
    })
    assert all(not case["image_available"] for case in manifest["cases"] if case["asset_type"] == "manga109_title")


def test_manifest_rejects_path_escape(tmp_path):
    source = json.loads(assets.MANIFEST_PATH.read_text(encoding="utf-8"))
    source["cases"][0]["local_path"] = "../outside"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(source), encoding="utf-8")
    with patch.object(assets, "MANIFEST_PATH", manifest_path):
        with pytest.raises(ValueError, match="escapes suite"):
            assets.load_manifest()


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
