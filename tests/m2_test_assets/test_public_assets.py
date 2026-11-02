import hashlib
import io
import json
import struct
import urllib.error
import urllib.request
import zipfile
import pytest
from unittest.mock import patch

from test_assets.comic_golden_suite.tools import assets


IMAGE_URL = "https://www.peppercarrot.com/data/page.jpg"
ZIP_URL = "https://www.peppercarrot.com/data/lang-pack.zip"
MEMBER = "lang/ja/E01P00.svg"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"><text>page</text></svg>'
JPEG = b"\xff\xd8\xff\xd9"


def make_case():
    return {
        "case_id": "O-test",
        "language": "ja",
        "local_path": "ja/O-test",
        "asset_profile": {
            "kind": "open_public_comic_page",
            "image_url": IMAGE_URL,
            "image_filename": "page.jpg",
            "transcript_zip_url": ZIP_URL,
            "transcript_zip_filename": "lang-pack.zip",
            "transcript_member": MEMBER,
        },
    }


def make_zip(member=MEMBER, source=SVG, extra_members=()):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(member, source)
        for name, content in extra_members:
            archive.writestr(name, content)
        archive.writestr("lang/ja/info.json", '{"language":"ja"}')
    return stream.getvalue()


class Response:
    def __init__(self, body, url, content_length=None):
        self.body = body
        self.url = url
        self.headers = {"Content-Length": str(len(body) if content_length is None else content_length)}
        self.offset = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return self.url

    def read(self, size):
        chunk = self.body[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


def test_public_page_download_is_atomic_validated_and_idempotent(tmp_path):
    case = make_case()
    root = tmp_path / "suite"
    payloads = [Response(JPEG, IMAGE_URL), Response(make_zip(), ZIP_URL)]
    with patch.object(assets, "ROOT", root), patch.object(assets, "open_public_comic_url", side_effect=payloads) as fetch:
        assert assets.download_case(case) == (2, 0, False)
        assert assets.status(case) == "READY"
        assert assets.validate_present(case)[0]
        fetch.reset_mock()
        assert assets.download_case(case) == (0, 2, False)
        fetch.assert_not_called()
    assert not list(assets.local_dir(case).glob("*.part"))


def test_korean_public_page_uses_same_download_and_member_checks(tmp_path):
    case = make_case()
    case["language"] = "ko"
    case["asset_profile"]["transcript_member"] = "lang/kr/E01P00.svg"
    payloads = [Response(JPEG, IMAGE_URL), Response(make_zip(member="lang/kr/E01P00.svg"), ZIP_URL)]
    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(
        assets, "open_public_comic_url", side_effect=payloads
    ) as fetch:
        assert assets.download_case(case) == (2, 0, False)
        assert assets.status(case) == "READY"
        assert assets.download_case(case) == (0, 2, False)
        assert fetch.call_count == 2
        case["asset_profile"]["transcript_member"] = MEMBER
        assert assets.status(case) == "PARTIAL"


def test_cases_in_one_directory_reuse_and_validate_shared_transcript_zip(tmp_path):
    first = make_case()
    first["local_path"] = "ja/shared"
    second = make_case()
    second["local_path"] = "ja/shared"
    second["asset_profile"]["image_filename"] = "page-2.jpg"
    second["asset_profile"]["transcript_member"] = "lang/ja/E01P01.svg"
    archive_data = make_zip(extra_members=(("lang/ja/E01P01.svg", SVG),))
    responses = [Response(JPEG, IMAGE_URL), Response(archive_data, ZIP_URL), Response(JPEG, IMAGE_URL)]
    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(
        assets, "open_public_comic_url", side_effect=responses
    ) as fetch:
        assert assets.download_case(first) == (2, 0, False)
        assert assets.download_case(second) == (1, 1, False)
        assert fetch.call_count == 3
        assert assets.status(first) == "READY"
        assert assets.status(second) == "READY"


def test_public_page_requires_both_image_and_transcript_member(tmp_path):
    case = make_case()
    with patch.object(assets, "ROOT", tmp_path / "suite"):
        directory = assets.local_dir(case)
        directory.mkdir(parents=True)
        (directory / "page.jpg").write_bytes(JPEG)
        assert assets.status(case) == "PARTIAL"
        (directory / "lang-pack.zip").write_bytes(make_zip(member="lang/ja/E01P01.svg"))
        assert assets.status(case) == "PARTIAL"
        assert not assets.validate_present(case)[0]


def corrupt_stored_member(data, name):
    damaged = bytearray(data)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        info = archive.getinfo(name)
    filename_length = struct.unpack_from("<H", damaged, info.header_offset + 26)[0]
    extra_length = struct.unpack_from("<H", damaged, info.header_offset + 28)[0]
    data_offset = info.header_offset + 30 + filename_length + extra_length
    damaged[data_offset] ^= 0x01
    return bytes(damaged)


def test_corrupt_zip_crc_and_unsafe_entries_never_report_ready(tmp_path):
    case = make_case()
    with patch.object(assets, "ROOT", tmp_path / "suite"):
        directory = assets.local_dir(case)
        directory.mkdir(parents=True)
        (directory / "page.jpg").write_bytes(JPEG)
        (directory / "lang-pack.zip").write_bytes(corrupt_stored_member(make_zip(), MEMBER))
        assert assets.status(case) == "PARTIAL"
        assert not assets.validate_present(case)[0]

        (directory / "lang-pack.zip").write_bytes(make_zip(member="../escape.svg"))
        assert assets.status(case) == "PARTIAL"
        assert not assets.validate_present(case)[0]
        assert not (directory.parent / "escape.svg").exists()


def test_public_download_rejects_wrong_host_and_redirect_without_publishing(tmp_path):
    case = make_case()
    case["asset_profile"]["image_url"] = "https://peppercarrot.com/page.jpg"
    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(assets, "open_public_comic_url") as fetch:
        assert assets.download_case(case) == (0, 0, True)
        fetch.assert_not_called()

    case["asset_profile"]["image_url"] = IMAGE_URL
    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(
        assets, "open_public_comic_url", return_value=Response(JPEG, "https://evil.example/page.jpg")
    ):
        assert assets.download_case(case) == (0, 0, True)
    assert not list(assets.local_dir(case).glob("*"))
    assert not list(assets.local_dir(case).glob("*.part"))


def test_redirect_handler_blocks_cross_host_request_before_following():
    handler = assets.PublicComicRedirectHandler()
    request = urllib.request.Request(IMAGE_URL)
    with pytest.raises(urllib.error.HTTPError, match="outside the approved HTTPS host"):
        handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/collect")


def test_interrupted_or_short_download_leaves_no_published_file(tmp_path):
    case = make_case()

    class Interrupted(Response):
        def read(self, _size):
            raise OSError("simulated connection loss")

    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(
        assets, "open_public_comic_url", return_value=Interrupted(JPEG, IMAGE_URL)
    ):
        assert assets.download_case(case) == (0, 0, True)
    directory = assets.local_dir(case)
    assert not (directory / "page.jpg").exists()
    assert not list(directory.glob("*.part"))

    with patch.object(assets, "ROOT", tmp_path / "suite"), patch.object(
        assets, "open_public_comic_url", return_value=Response(JPEG, IMAGE_URL, content_length=10)
    ):
        assert assets.download_case(case) == (0, 0, True)
    assert not (directory / "page.jpg").exists()
    assert not list(directory.glob("*.part"))


def test_public_transcript_rejects_invalid_svg_xml(tmp_path):
    case = make_case()
    with patch.object(assets, "ROOT", tmp_path / "suite"):
        directory = assets.local_dir(case)
        directory.mkdir(parents=True)
        (directory / "page.jpg").write_bytes(JPEG)
        (directory / "lang-pack.zip").write_bytes(make_zip(source=b"<!DOCTYPE svg [<!ENTITY x SYSTEM 'file:///secret'>]><svg>&x;</svg>"))
        assert assets.status(case) == "PARTIAL"
        ok, reason = assets.validate_present(case)
        assert not ok
        assert "DTD/entity" in reason


def test_inventory_verifier_detects_checksum_drift(tmp_path):
    root = tmp_path / "suite"
    asset = root / "ja" / "page.jpg"
    asset.parent.mkdir(parents=True)
    original = b"public test asset"
    asset.write_bytes(original)
    inventory = root / "manifests" / "local_asset_inventory.json"
    inventory.parent.mkdir()
    inventory.write_text(json.dumps({"assets": [{"asset_id": "test", "files": [{
        "path": "ja/page.jpg", "byte_size": len(original), "sha256": hashlib.sha256(original).hexdigest()
    }]}]}), encoding="utf-8")

    with patch.object(assets, "ROOT", root), patch.object(assets, "INVENTORY_PATH", inventory):
        assert assets.verify_inventory_files() == ([], 1, 0, set())
        asset.write_bytes(b"modified test asset")
        failures, checked, missing, invalid_paths = assets.verify_inventory_files()
    assert checked == 1
    assert missing == 0
    assert len(failures) == 1
    assert "SHA-256 mismatch" in failures[0]
    assert invalid_paths == {"ja/page.jpg"}


def test_missing_media_is_counted_but_missing_annotation_fails(tmp_path):
    root = tmp_path / "suite"
    inventory = root / "manifests" / "local_asset_inventory.json"
    inventory.parent.mkdir(parents=True)
    inventory.write_text(json.dumps({"assets": [{"asset_id": "test", "files": [
        {"path": "ja/page.jpg", "byte_size": 4, "sha256": hashlib.sha256(JPEG).hexdigest()},
        {"path": "ja/annotations.xml", "byte_size": 4, "sha256": "0" * 64},
    ]}]}), encoding="utf-8")

    with patch.object(assets, "ROOT", root), patch.object(assets, "INVENTORY_PATH", inventory):
        failures, checked, missing, invalid_paths = assets.verify_inventory_files()

    assert checked == 0
    assert missing == 2
    assert len(failures) == 1
    assert "required inventory file is missing: ja/annotations.xml" in failures[0]
    assert invalid_paths == {"ja/annotations.xml"}


def test_checksum_drift_keeps_structurally_valid_public_page_out_of_ready(tmp_path):
    case = make_case()
    root = tmp_path / "suite"
    directory = root / "ja" / "O-test"
    directory.mkdir(parents=True)
    image = directory / "page.jpg"
    transcript = directory / "lang-pack.zip"
    image.write_bytes(JPEG)
    transcript.write_bytes(make_zip())
    inventory = root / "manifests" / "local_asset_inventory.json"
    inventory.parent.mkdir()
    inventory.write_text(json.dumps({"assets": [{"asset_id": "test", "files": [
        {"path": "ja/O-test/page.jpg", "byte_size": image.stat().st_size, "sha256": hashlib.sha256(image.read_bytes()).hexdigest()},
        {"path": "ja/O-test/lang-pack.zip", "byte_size": transcript.stat().st_size, "sha256": hashlib.sha256(transcript.read_bytes()).hexdigest()},
    ]}]}), encoding="utf-8")

    with patch.object(assets, "ROOT", root), patch.object(assets, "INVENTORY_PATH", inventory):
        assert assets.status(case) == "READY"
        transcript.write_bytes(make_zip(source=SVG.replace(b"page", b"other")))
        failures, checked, missing, invalid_paths = assets.verify_inventory_files()
        assert assets.status(case, invalid_paths) == "PARTIAL"

    assert checked == 2
    assert missing == 0
    assert len(failures) == 1
    assert invalid_paths == {"ja/O-test/lang-pack.zip"}
