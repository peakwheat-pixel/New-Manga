import json
import zipfile
from unittest.mock import patch

import pytest

from test_assets.comic_golden_suite.tools import assets


def test_manifest_has_unique_cases_and_exact_taxonomy():
    manifest = assets.load_manifest()
    cases = manifest["cases"]
    assert len(cases) == 65
    assert len({case["case_id"] for case in cases}) == 65
    assert manifest["taxonomy"]["difficulty_tags"] == [
        "normal_dialogue", "dense_dialogue", "tiny_text", "huge_text",
        "vertical_text", "horizontal_text", "rotated_text", "curved_text",
        "fragmented_sfx", "overlapping_text", "complex_background", "low_contrast",
        "narration", "multi_speaker", "unusual_balloon", "extreme_size",
    ]
    assert len(assets.selected(manifest, "ko", "smoke")) == 10
    assert len(assets.selected(manifest, "ja", "smoke")) == 10


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
