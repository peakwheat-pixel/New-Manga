"""List, verify, and explicitly download/import the shared JA/KO comic assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import struct
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path, PurePosixPath, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests" / "cases.json"
INVENTORY_PATH = ROOT / "manifests" / "local_asset_inventory.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COPY_BLOCK = 1024 * 1024
MAX_ANNOTATION_BYTES = 32 * 1024 * 1024
MAX_IMAGE_BYTES = 128 * 1024 * 1024
MAX_PUBLIC_ZIP_BYTES = 64 * 1024 * 1024
MAX_PUBLIC_ZIP_ENTRIES = 10000
MAX_PUBLIC_ZIP_TOTAL_BYTES = 128 * 1024 * 1024
MAX_PUBLIC_ZIP_ENTRY_BYTES = 16 * 1024 * 1024
MAX_PUBLIC_XML_BYTES = 8 * 1024 * 1024
PUBLIC_COMIC_HOST = "www.peppercarrot.com"
# Frozen from the set of https hosts actually present in manifests/cases.json
# source_url values (reconnaissance 2026-09-29: 47 cases on huggingface.co,
# 21 cases on www.peppercarrot.com; M2-TA2B 2026-09-30: 12 cases on
# densho810.com, the author's official free-download channel for "Give My
# Regards to Black Jack"). Adding a host requires an explicit change here;
# unknown hosts fail closed at manifest load time.
SOURCE_URL_HOSTS = frozenset({"www.peppercarrot.com", "huggingface.co", "densho810.com"})


def validate_source_url(case_id: str, url: str) -> None:
    try:
        parsed = urllib.parse.urlsplit(url)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid source_url: {case_id}") from exc
    accepted = (
        parsed.scheme.lower() == "https"
        and parsed.hostname is not None
        and parsed.hostname.lower() in SOURCE_URL_HOSTS
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443)
    )
    if not accepted:
        raise ValueError(f"source_url host is outside the approved whitelist: {case_id}")


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    allowed_tags = set(manifest["taxonomy"]["difficulty_tags"])
    required = {
        "case_id", "language", "source", "source_id", "source_type", "layout_type",
        "reading_direction", "text_type", "orientation", "difficulty", "tags",
        "local_path", "license_class", "redistributable", "expected_pipeline",
        "ground_truth_available", "levels", "asset_status",
    }
    for case in manifest["cases"]:
        if required - case.keys():
            raise ValueError(f"missing case fields: {case.get('case_id', '<unknown>')}")
        if case["case_id"] in ids:
            raise ValueError(f"duplicate case_id: {case['case_id']}")
        ids.add(case["case_id"])
        if case["language"] not in {"ja", "ko"}:
            raise ValueError(f"invalid language: {case['case_id']}")
        if not set(case["tags"]) <= allowed_tags:
            raise ValueError(f"unknown difficulty tag: {case['case_id']}")
        if not set(case["levels"]) <= {"smoke", "regression", "full"}:
            raise ValueError(f"invalid level: {case['case_id']}")
        if not isinstance(case.get("image_available"), bool) or not isinstance(case.get("annotation_available"), bool):
            raise ValueError(f"invalid local availability snapshot: {case['case_id']}")
        pipeline = case.get("pipeline_status")
        if not isinstance(pipeline, dict) or set(pipeline) != set(case["expected_pipeline"]) or not set(pipeline.values()) <= {
            "NOT_RUN", "PASS", "FAIL", "BLOCKED_BY_ASSET_ACCESS", "BLOCKED_BY_ENV"
        }:
            raise ValueError(f"invalid pipeline status: {case['case_id']}")
        if not all(isinstance(case.get(key), str) and case[key] for key in ("source_name", "asset_type", "source_url", "license")):
            raise ValueError(f"missing source metadata: {case['case_id']}")
        validate_source_url(case["case_id"], case["source_url"])
        if not isinstance(case.get("ground_truth_types"), list) or not all(isinstance(item, str) for item in case["ground_truth_types"]):
            raise ValueError(f"invalid ground truth types: {case['case_id']}")
        local = (ROOT / Path(case["local_path"])).resolve()
        if not local.is_relative_to(ROOT.resolve()):
            raise ValueError(f"local_path escapes suite: {case['case_id']}")
        profile = case.get("asset_profile", {})
        if profile.get("kind") == "hf_cleaned_webtoon":
            if not re.fullmatch(r"\d+_\d+", case.get("source_id", "")):
                raise ValueError(f"invalid Webtoon source_id: {case['case_id']}")
            if profile.get("repo_subpath") != "examples":
                raise ValueError(f"invalid Webtoon repo_subpath: {case['case_id']}")
            if any(Path(name).name != name or "\\" in name for name in profile.get("files", [])):
                raise ValueError(f"invalid asset filename: {case['case_id']}")
        if profile.get("kind") == "open_public_comic_page":
            validate_public_profile(profile, case["language"])
    return manifest


def selected(manifest: dict, language: str | None, level: str) -> list[dict]:
    return [
        case for case in manifest["cases"]
        if (language is None or case["language"] == language) and level in case["levels"]
    ]


def local_dir(case: dict) -> Path:
    path = (ROOT / Path(case["local_path"])).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"local_path escapes suite: {case['case_id']}")
    return path


def required_files(case: dict) -> list[Path]:
    directory = local_dir(case)
    kind = case.get("asset_profile", {}).get("kind")
    if kind == "hf_cleaned_webtoon":
        return [directory / name for name in case["asset_profile"]["files"]]
    if kind == "manga109_title":
        return [*sorted((directory / "images").glob("*.jpg")), directory / "annotations.xml"]
    if kind == "open_public_comic_page":
        profile = case["asset_profile"]
        validate_public_profile(profile)
        return [directory / profile["image_filename"], directory / profile["transcript_zip_filename"]]
    if kind == "manual_source_page":
        return [path for path in directory.iterdir() if path.is_file()] if directory.is_dir() else []
    return []


def manga_marker(case: dict) -> Path:
    return local_dir(case) / ".asset-complete.json"


def status(case: dict, invalid_inventory_paths: set[str] | None = None) -> str:
    kind = case.get("asset_profile", {}).get("kind")
    paths = required_files(case)
    if kind == "manga109_title":
        marker = manga_marker(case)
        if marker.is_file() and all(path.is_file() and path.stat().st_size > 0 for path in paths):
            try:
                data = json.loads(marker.read_text(encoding="utf-8"))
                images = sorted(path.name for path in paths if path.suffix.lower() == ".jpg")
                if data.get("case_id") == case["case_id"] and data.get("images") == images:
                    ok, _ = validate_manga_case(case)
                    return "READY" if ok else "PARTIAL"
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                pass
        return "PARTIAL" if any(path.is_file() for path in paths) else "MISSING_GATED_ASSET"
    if kind == "manual_source_page":
        return "PARTIAL" if any(path.is_file() and path.stat().st_size > 0 for path in paths) else "MISSING"
    if kind == "open_public_comic_page":
        if not any(path.exists() for path in paths):
            return "MISSING"
        if invalid_inventory_paths and any(
            path.relative_to(ROOT).as_posix() in invalid_inventory_paths for path in paths
        ):
            return "PARTIAL"
        ok, _ = validate_public_case(case)
        return "READY" if ok else "PARTIAL"
    if paths and all(path.is_file() and path.stat().st_size > 0 for path in paths):
        if kind == "hf_cleaned_webtoon":
            ok, _ = validate_present(case)
            return "READY" if ok else "PARTIAL"
        return "READY"
    return "MISSING"


def print_cases(
    cases: list[dict],
    show_missing_only: bool = False,
    invalid_inventory_paths: set[str] | None = None,
) -> dict[str, str]:
    counts: dict[str, int] = {}
    statuses: dict[str, str] = {}
    for case in cases:
        current = status(case, invalid_inventory_paths)
        statuses[case["case_id"]] = current
        counts[current] = counts.get(current, 0) + 1
        if not show_missing_only or current != "READY":
            print(f"{case['case_id']}\t{case['language']}\t{current}\t{case['local_path']}")
    print("SUMMARY\t" + " ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    return statuses


def verify_inventory_files() -> tuple[list[str], int, int, set[str]]:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    checked = 0
    missing = 0
    invalid_paths: set[str] = set()
    root = ROOT.resolve()
    for asset in inventory["assets"]:
        for item in asset.get("files", []):
            name = item["path"]
            relative = PurePosixPath(name)
            if (
                "\\" in name or ":" in name or PureWindowsPath(name).drive
                or relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name
            ):
                failures.append(f"{asset['asset_id']}: unsafe inventory path {item['path']}")
                continue
            candidate = ROOT / Path(*relative.parts)
            if candidate.is_symlink():
                failures.append(f"{asset['asset_id']}: inventory path is a symlink: {item['path']}")
                continue
            path = candidate.resolve()
            if not path.is_relative_to(root):
                failures.append(f"{asset['asset_id']}: inventory path escapes suite: {item['path']}")
                continue
            if not path.exists():
                missing += 1
                if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".zip", ".cbz"}:
                    failures.append(f"{asset['asset_id']}: required inventory file is missing: {item['path']}")
                    invalid_paths.add(name)
                continue
            if not path.is_file():
                failures.append(f"{asset['asset_id']}: inventory path is not a regular file: {item['path']}")
                continue
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as stream:
                while chunk := stream.read(COPY_BLOCK):
                    size += len(chunk)
                    digest.update(chunk)
            checked += 1
            if size != item["byte_size"] or digest.hexdigest() != item["sha256"]:
                failures.append(f"{asset['asset_id']}: size or SHA-256 mismatch: {item['path']}")
                invalid_paths.add(name)
    return failures, checked, missing, invalid_paths


def verify_benchmark_source_inventories(manifest: dict) -> tuple[list[str], int]:
    """Existence check for every non-empty benchmark_sources checksum_inventory path.

    Paths are repository-root relative (see README). The per-file hash recheck for
    local_asset_inventory.json is performed once by verify_inventory_files(); this
    pass adds the previously unconsumed benchmark_sources entries to that flow.
    """
    failures: list[str] = []
    checked = 0
    for source in manifest.get("benchmark_sources", []):
        raw = source.get("checksum_inventory")
        if not isinstance(raw, str) or not raw:
            continue
        source_id = source.get("id", "<unknown>")
        relative = PurePosixPath(raw)
        if (
            "\\" in raw or ":" in raw or PureWindowsPath(raw).drive
            or relative.is_absolute() or ".." in relative.parts or relative.as_posix() != raw
        ):
            failures.append(f"{source_id}: unsafe checksum_inventory path {raw}")
            continue
        candidate = REPO_ROOT / Path(*relative.parts)
        if candidate.is_symlink() or not candidate.is_file():
            failures.append(f"{source_id}: checksum_inventory file is missing: {raw}")
            continue
        # For local_asset_inventory.json entries the full per-file hash recheck is
        # performed by verify_inventory_files() in the same command run; other audit
        # files (e.g. verification/M2-TA2C/ko-webtoon-audit.json) are consumed at
        # existence level per the frozen plan.
        checked += 1
    return failures, checked


def valid_png(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            if stream.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
                return False
            first_chunk = True
            while True:
                raw_length = stream.read(4)
                chunk_type = stream.read(4)
                if len(raw_length) != 4 or len(chunk_type) != 4:
                    return False
                length = struct.unpack(">I", raw_length)[0]
                if first_chunk and (chunk_type != b"IHDR" or length != 13):
                    return False
                first_chunk = False
                crc = zlib.crc32(chunk_type)
                remaining = length
                while remaining:
                    chunk = stream.read(min(remaining, COPY_BLOCK))
                    if not chunk:
                        return False
                    remaining -= len(chunk)
                    crc = zlib.crc32(chunk, crc)
                raw_crc = stream.read(4)
                if len(raw_crc) != 4:
                    return False
                if (crc & 0xFFFFFFFF) != struct.unpack(">I", raw_crc)[0]:
                    return False
                if chunk_type == b"IEND":
                    return length == 0 and not stream.read(1)
    except OSError:
        return False


def valid_jpeg(path: Path) -> bool:
    try:
        if path.stat().st_size < 4:
            return False
        with path.open("rb") as stream:
            if stream.read(2) != b"\xff\xd8":
                return False
            stream.seek(-2, os.SEEK_END)
            return stream.read(2) == b"\xff\xd9"
    except (OSError, ValueError):
        return False


def is_public_comic_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlsplit(url)
        return (
            parsed.scheme.lower() == "https"
            and parsed.hostname is not None
            and parsed.hostname.lower() == PUBLIC_COMIC_HOST
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
        )
    except (TypeError, ValueError):
        return False


class PublicComicRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        target = urllib.parse.urljoin(request.full_url, new_url)
        if not is_public_comic_url(target):
            raise urllib.error.HTTPError(request.full_url, code, "redirect target is outside the approved HTTPS host", headers, response)
        return super().redirect_request(request, response, code, message, headers, target)


def open_public_comic_url(request):
    opener = urllib.request.build_opener(PublicComicRedirectHandler())
    return opener.open(request, timeout=60)


def validate_public_filename(name: str) -> bool:
    return bool(
        name
        and name not in {".", ".."}
        and "/" not in name
        and "\\" not in name
        and ":" not in name
        and "\x00" not in name
        and PureWindowsPath(name).name == name
    )


def validate_public_profile(profile: dict, language: str | None = None) -> None:
    fields = ("image_url", "image_filename", "transcript_zip_url", "transcript_zip_filename", "transcript_member")
    if any(not isinstance(profile.get(key), str) or not profile[key] for key in fields):
        raise ValueError("public comic profile is missing required fields")
    if not is_public_comic_url(profile["image_url"]) or not is_public_comic_url(profile["transcript_zip_url"]):
        raise ValueError("public comic URLs must use HTTPS www.peppercarrot.com")
    if not validate_public_filename(profile["image_filename"]) or not profile["image_filename"].lower().endswith((".jpg", ".jpeg")):
        raise ValueError("public comic image filename must be a local JPEG filename")
    if not validate_public_filename(profile["transcript_zip_filename"]) or not profile["transcript_zip_filename"].lower().endswith(".zip"):
        raise ValueError("public comic transcript filename must be a local ZIP filename")
    member = profile["transcript_member"]
    if "\\" in member or "\x00" in member or ":" in member or PureWindowsPath(member).drive:
        raise ValueError("unsafe public comic transcript member")
    member_path = PurePosixPath(member)
    if member_path.is_absolute() or any(part in {"", ".", ".."} for part in member.split("/")):
        raise ValueError("unsafe public comic transcript member")
    if member_path.suffix.lower() not in {".svg", ".xml"}:
        raise ValueError("public comic transcript member must be SVG or XML")
    if language is not None and not member.startswith(f"lang/{'kr' if language == 'ko' else language}/"):
        raise ValueError("public comic transcript member does not match case language")


def public_xml_valid(data: bytes, name: str) -> tuple[bool, str]:
    if len(data) > MAX_PUBLIC_XML_BYTES:
        return False, "SVG/XML member exceeds size limit"
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        return False, "DTD/entity declarations are not accepted"
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return False, "invalid SVG/XML member"
    if name.lower().endswith(".svg") and root.tag.rsplit("}", 1)[-1].lower() != "svg":
        return False, "SVG member root element is not svg"
    return True, "ok"


def inspect_public_transcript_zip(path: Path, required_member: str) -> tuple[bool, str]:
    if not path.is_file() or path.stat().st_size == 0:
        return False, "transcript ZIP is missing or empty"
    if path.stat().st_size > MAX_PUBLIC_ZIP_BYTES:
        return False, "transcript ZIP exceeds size limit"
    try:
        with zipfile.ZipFile(path) as archive:
            if len(archive.infolist()) > MAX_PUBLIC_ZIP_ENTRIES:
                return False, "transcript ZIP has too many entries"
            seen: set[str] = set()
            total_size = 0
            found_member = False
            for info in archive.infolist():
                parts = zip_parts(info)
                folded_name = "/".join(parts).casefold()
                if folded_name in seen:
                    return False, f"duplicate ZIP entry: {info.filename}"
                seen.add(folded_name)
                mode = (info.external_attr >> 16) & 0xF000
                if mode == stat.S_IFLNK or mode not in {0, stat.S_IFREG, stat.S_IFDIR}:
                    return False, f"unsupported ZIP entry type: {info.filename}"
                if info.is_dir():
                    continue
                if info.flag_bits & 1:
                    return False, f"encrypted ZIP entry is not accepted: {info.filename}"
                if info.file_size > MAX_PUBLIC_ZIP_ENTRY_BYTES:
                    return False, f"ZIP entry exceeds size limit: {info.filename}"
                total_size += info.file_size
                if total_size > MAX_PUBLIC_ZIP_TOTAL_BYTES:
                    return False, "transcript ZIP uncompressed size exceeds limit"
                if info.filename == required_member:
                    found_member = True
                check_xml = info.filename.lower().endswith((".svg", ".xml"))
                check_json = info.filename.startswith("lang/") and info.filename.endswith("/info.json")
                if not (check_xml or check_json):
                    # Still read each member to verify its ZIP CRC without extracting it.
                    data = None
                else:
                    data = bytearray()
                size = 0
                with archive.open(info) as stream:
                    while chunk := stream.read(COPY_BLOCK):
                        size += len(chunk)
                        if size > info.file_size:
                            return False, f"ZIP entry expands beyond its declared size: {info.filename}"
                        if data is not None:
                            data.extend(chunk)
                if size != info.file_size:
                    return False, f"ZIP entry size mismatch: {info.filename}"
                if data is not None and check_xml:
                    ok, reason = public_xml_valid(bytes(data), info.filename)
                    if not ok:
                        return False, f"{info.filename}: {reason}"
                if data is not None and check_json:
                    try:
                        json.loads(data.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        return False, f"{info.filename} is invalid"
            if not found_member:
                return False, f"required transcript member is missing: {required_member}"
    except (OSError, RuntimeError, EOFError, NotImplementedError, zipfile.BadZipFile, zlib.error, ValueError) as exc:
        return False, f"invalid transcript ZIP: {type(exc).__name__}: {exc}"
    return True, "transcript ZIP and required SVG/XML member are valid"


def validate_public_case(case: dict) -> tuple[bool, str]:
    try:
        profile = case["asset_profile"]
        validate_public_profile(profile, case["language"])
        directory = local_dir(case)
        image = directory / profile["image_filename"]
        transcript_zip = directory / profile["transcript_zip_filename"]
        for path in (image, transcript_zip):
            if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory.resolve()):
                return False, f"missing or unsafe asset path: {path.name}"
        if not valid_jpeg(image):
            return False, "image is not a complete JPEG"
        return inspect_public_transcript_zip(transcript_zip, profile["transcript_member"])
    except (KeyError, OSError, ValueError) as exc:
        return False, f"invalid public comic profile or files: {exc}"


def manga_page_names(pages: ET.Element) -> list[str]:
    indices = []
    for page in pages.findall("page"):
        raw_index = page.get("index", "")
        if not raw_index.isdecimal():
            raise ValueError("Manga109 page has an invalid index")
        indices.append(int(raw_index))
    if len(indices) != len(set(indices)):
        raise ValueError("Manga109 annotation has duplicate page indices")
    return [f"{index:03d}.jpg" for index in sorted(indices)]


def validate_manga_case(case: dict) -> tuple[bool, str]:
    directory = local_dir(case)
    marker = manga_marker(case)
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        images = sorted((directory / "images").glob("*.jpg"))
        if data.get("case_id") != case["case_id"] or data.get("images") != [path.name for path in images]:
            return False, "completion marker does not match local images"
        if not images or not all(valid_jpeg(path) for path in images):
            return False, "missing or invalid JPEG page"
        annotation = directory / "annotations.xml"
        if annotation.stat().st_size > MAX_ANNOTATION_BYTES:
            return False, "annotation XML exceeds size limit"
        xml = annotation.read_bytes()
        if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
            return False, "DTD/entity declarations are not accepted"
        root = ET.fromstring(xml)
        pages = root.find("pages")
        if root.tag != "book" or root.get("title") != case["source_id"] or pages is None:
            return False, "annotation XML title/schema mismatch"
        expected_names = manga_page_names(pages)
        if [path.name for path in images] != expected_names or data.get("page_count") != len(expected_names):
            return False, "annotation page indices do not match images"
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ET.ParseError, ValueError):
        return False, "invalid completion marker or annotation XML"
    return True, "title images and annotations present"


def validate_present(case: dict) -> tuple[bool, str]:
    kind = case.get("asset_profile", {}).get("kind")
    if kind == "manga109_title":
        return validate_manga_case(case)
    if kind == "open_public_comic_page":
        return validate_public_case(case)
    paths = required_files(case)
    if not paths:
        return False, "required files are absent"
    for path in paths:
        if not path.is_file() or path.stat().st_size == 0:
            return False, f"missing or empty: {path.name}"
        if path.suffix.lower() == ".png" and not valid_png(path):
            return False, f"invalid or truncated PNG: {path.name}"
        if path.name == "info.json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return False, "invalid info.json"
    return True, "required files present and structurally valid"


def download_public_file(url: str, destination: Path, size_limit: int, validator) -> tuple[int, int]:
    if not is_public_comic_url(url):
        raise ValueError("download URL is outside the approved HTTPS host")
    if destination.is_symlink():
        raise OSError(f"existing path is a symlink; left untouched: {destination.name}")
    if destination.exists():
        valid, reason = validator(destination)
        if valid:
            return 0, 1
        raise OSError(f"existing file is invalid; left untouched: {destination.name}: {reason}")

    temp_name = None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "NewManga-TestAssets/1.0"})
        with open_public_comic_url(request) as response:
            if not is_public_comic_url(response.geturl()):
                raise OSError("redirected download is outside the approved HTTPS host")
            content_length = response.headers.get("Content-Length")
            if not content_length or not content_length.isdecimal():
                raise OSError("response has no verifiable Content-Length")
            expected_size = int(content_length)
            if expected_size <= 0 or expected_size > size_limit:
                raise OSError(f"remote file size is outside limits: {expected_size} bytes")
            with tempfile.NamedTemporaryFile(prefix=f".{destination.name}.", suffix=".part", dir=destination.parent, delete=False) as temp:
                temp_name = temp.name
                written = 0
                while chunk := response.read(COPY_BLOCK):
                    written += len(chunk)
                    if written > expected_size or written > size_limit:
                        raise OSError("download exceeds declared or allowed size")
                    temp.write(chunk)
        temp_path = Path(temp_name)
        if written != expected_size:
            raise OSError(f"incomplete download: expected {expected_size} bytes, received {written}")
        valid, reason = validator(temp_path)
        if not valid:
            raise OSError(reason)
        try:
            os.link(temp_path, destination)
        except FileExistsError:
            if destination.is_symlink():
                raise OSError(f"destination appeared as a symlink; left untouched: {destination.name}")
            valid, reason = validator(destination)
            if not valid:
                raise OSError(f"destination appeared with invalid content; left untouched: {destination.name}: {reason}")
            return 0, 1
        return 1, 0
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


def download_public_comic_case(case: dict) -> tuple[int, int, bool]:
    profile = case["asset_profile"]
    directory = local_dir(case)
    downloaded = skipped = 0
    try:
        validate_public_profile(profile, case["language"])
        directory.mkdir(parents=True, exist_ok=True)
        image = directory / profile["image_filename"]
        archive = directory / profile["transcript_zip_filename"]
        image_count, image_skipped = download_public_file(
            profile["image_url"], image, MAX_IMAGE_BYTES,
            lambda path: (valid_jpeg(path), "downloaded JPEG is invalid"),
        )
        downloaded += image_count
        skipped += image_skipped
        zip_count, zip_skipped = download_public_file(
            profile["transcript_zip_url"], archive, MAX_PUBLIC_ZIP_BYTES,
            lambda path: inspect_public_transcript_zip(path, profile["transcript_member"]),
        )
        downloaded += zip_count
        skipped += zip_skipped
        print(f"{case['case_id']}\tDOWNLOADED\tfiles={downloaded} existing={skipped}")
        return downloaded, skipped, False
    except (OSError, ValueError, urllib.error.URLError, zipfile.BadZipFile) as exc:
        print(f"{case['case_id']}\tDOWNLOAD_FAILED\t{type(exc).__name__}: {exc}", file=sys.stderr)
        return downloaded, skipped, True


def download_webtoon_case(case: dict) -> tuple[int, int, bool]:
    profile = case["asset_profile"]
    directory = local_dir(case)
    directory.mkdir(parents=True, exist_ok=True)
    downloaded = skipped = 0
    for name in profile["files"]:
        destination = directory / name
        if destination.exists():
            skipped += 1
            continue
        url = f"{profile['resolve_url'].rstrip('/')}/{profile['repo_subpath']}/{case['source_id']}/{name}?download=true"
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "huggingface.co":
            raise ValueError("download URL is outside the approved HTTPS host")
        temp_name = None
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "NewManga-TestAssets/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                content_length = response.headers.get("Content-Length")
                if not content_length or not content_length.isdecimal():
                    raise OSError("response has no verifiable Content-Length")
                expected_size = int(content_length)
                if expected_size > MAX_IMAGE_BYTES:
                    raise OSError(f"remote file exceeds size limit: {expected_size} bytes")
                with tempfile.NamedTemporaryFile(prefix=f".{name}.", suffix=".part", dir=directory, delete=False) as temp:
                    temp_name = temp.name
                    written = 0
                    while chunk := response.read(COPY_BLOCK):
                        temp.write(chunk)
                        written += len(chunk)
            temp_path = Path(temp_name)
            if written != expected_size:
                raise OSError(f"incomplete download: expected {expected_size} bytes, received {written}")
            valid, reason = validate_download_file(temp_path, name)
            if not valid:
                raise OSError(reason)
            try:
                os.link(temp_path, destination)
            except FileExistsError:
                skipped += 1
            else:
                downloaded += 1
            finally:
                temp_path.unlink(missing_ok=True)
        except (OSError, urllib.error.URLError) as exc:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
            print(f"{case['case_id']}\tDOWNLOAD_FAILED\t{name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return downloaded, skipped, True
    return downloaded, skipped, False


def validate_download_file(path: Path, name: str) -> tuple[bool, str]:
    if not path.is_file() or path.stat().st_size == 0:
        return False, "server returned an empty file"
    if name.lower().endswith(".png") and not valid_png(path):
        return False, "downloaded PNG is truncated or invalid"
    if name == "info.json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False, "downloaded info.json is invalid"
    return True, "ok"


def zip_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    name = info.filename
    path = PurePosixPath(name)
    clean_name = name[:-1] if info.is_dir() and name.endswith("/") else name
    if (
        not clean_name or "\\" in name or "\x00" in name or ":" in name
        or path.is_absolute() or PureWindowsPath(name).drive
        or any(part in {"", ".", ".."} for part in clean_name.split("/"))
    ):
        raise ValueError(f"unsafe path in ZIP archive: {name!r}")
    return path.parts


def manga_members(archive: zipfile.ZipFile, title: str) -> tuple[list[zipfile.ZipInfo], zipfile.ZipInfo, int]:
    images: list[zipfile.ZipInfo] = []
    annotations: list[zipfile.ZipInfo] = []
    for info in archive.infolist():
        parts = zip_parts(info)
        if info.is_dir():
            continue
        for index, part in enumerate(parts[:-1]):
            tail = parts[index + 1:]
            if part == "images" and tail[0] == title and len(tail) == 2:
                name = tail[1]
                if re.fullmatch(r"\d{3,}\.jpg", name):
                    if info.file_size > MAX_IMAGE_BYTES:
                        raise ValueError(f"image exceeds size limit in archive: {info.filename}")
                    images.append(info)
            if part == "annotations" and tail in {(f"{title}.xml",), (title, f"{title}.xml")}:
                annotations.append(info)
    if not images or len(annotations) != 1:
        raise ValueError(f"archive is missing images or one annotation XML for {title}")
    image_names = [PurePosixPath(info.filename).name for info in images]
    if len(image_names) != len(set(image_names)):
        raise ValueError(f"duplicate image filenames in archive for {title}")
    annotation = annotations[0]
    if annotation.file_size > MAX_ANNOTATION_BYTES:
        raise ValueError(f"annotation XML exceeds size limit for {title}")
    with archive.open(annotation) as stream:
        xml = stream.read(MAX_ANNOTATION_BYTES + 1)
    if len(xml) > MAX_ANNOTATION_BYTES:
        raise ValueError(f"annotation XML exceeds size limit for {title}")
    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError(f"DTD/entity declarations are not accepted: {annotation.filename}")
    root = ET.fromstring(xml)
    pages = root.find("pages")
    if root.tag != "book" or root.get("title") != title or pages is None:
        raise ValueError(f"annotation XML title/schema mismatch for {title}")
    expected_names = manga_page_names(pages)
    image_names = [PurePosixPath(info.filename).name for info in images]
    if sorted(image_names) != expected_names:
        raise ValueError(f"archive page names do not match annotation indices for {title}")
    by_name = {PurePosixPath(info.filename).name: info for info in images}
    return [by_name[name] for name in expected_names], annotation, len(expected_names)


def copy_zip_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, destination: Path, image: bool) -> bool:
    size_limit = MAX_IMAGE_BYTES if image else MAX_ANNOTATION_BYTES
    if info.file_size > size_limit:
        raise ValueError(f"archive member exceeds size limit: {info.filename}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        with destination.open("rb") as stream:
            crc = 0
            size = 0
            while chunk := stream.read(COPY_BLOCK):
                crc = zlib.crc32(chunk, crc)
                size += len(chunk)
        if size != info.file_size or (crc & 0xFFFFFFFF) != info.CRC:
            raise OSError(f"existing file differs from archive; left untouched: {destination.name}")
        return False

    temp_name = None
    try:
        with archive.open(info) as source:
            with tempfile.NamedTemporaryFile(prefix=f".{destination.name}.", suffix=".part", dir=destination.parent, delete=False) as temp:
                temp_name = temp.name
                size = 0
                crc = 0
                while chunk := source.read(COPY_BLOCK):
                    temp.write(chunk)
                    size += len(chunk)
                    crc = zlib.crc32(chunk, crc)
        temp_path = Path(temp_name)
        if size != info.file_size or (crc & 0xFFFFFFFF) != info.CRC:
            raise OSError(f"archive member failed size/CRC verification: {info.filename}")
        if image and not valid_jpeg(temp_path):
            raise OSError(f"invalid JPEG in archive: {info.filename}")
        if not image:
            xml = temp_path.read_bytes()
            if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
                raise OSError(f"DTD/entity declarations are not accepted: {info.filename}")
            root = ET.fromstring(xml)
            if root.tag != "book":
                raise OSError(f"invalid annotation XML: {info.filename}")
        try:
            os.link(temp_path, destination)
        except FileExistsError:
            raise OSError(f"destination appeared during import; left untouched: {destination.name}")
        return True
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


def import_manga_case(archive: zipfile.ZipFile, case: dict, archive_name: str) -> tuple[int, int]:
    images, annotation, page_count = manga_members(archive, case["source_id"])
    directory = local_dir(case)
    image_dir = directory / "images"
    moved = skipped = 0
    image_names = []
    for info in images:
        name = PurePosixPath(info.filename).name
        image_names.append(name)
        if copy_zip_member(archive, info, image_dir / name, image=True):
            moved += 1
        else:
            skipped += 1
    if copy_zip_member(archive, annotation, directory / "annotations.xml", image=False):
        moved += 1
    else:
        skipped += 1
    marker_data = {
        "case_id": case["case_id"], "source_id": case["source_id"],
        "archive": archive_name, "images": sorted(image_names), "page_count": page_count,
    }
    marker = manga_marker(case)
    if marker.exists():
        current = json.loads(marker.read_text(encoding="utf-8"))
        if current != marker_data:
            raise OSError(f"existing completion marker differs; left untouched: {case['case_id']}")
        skipped += 1
    else:
        marker.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".asset.", suffix=".part", dir=marker.parent, delete=False) as temp:
                temp_name = temp.name
                json.dump(marker_data, temp, ensure_ascii=False, sort_keys=True)
            os.link(temp_name, marker)
            moved += 1
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
    return moved, skipped


def import_manga_archive(cases: list[dict], archive_path: Path) -> tuple[int, int, int]:
    imported = skipped = failures = 0
    with zipfile.ZipFile(archive_path) as archive:
        for case in cases:
            try:
                moved, kept = import_manga_case(archive, case, archive_path.name)
            except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
                print(f"{case['case_id']}\tIMPORT_FAILED\t{type(exc).__name__}: {exc}", file=sys.stderr)
                failures += 1
                continue
            imported += moved
            skipped += kept
            print(f"{case['case_id']}\tIMPORTED\tfiles={moved} existing={kept}")
    return imported, skipped, failures


def download_case(case: dict) -> tuple[int, int, bool]:
    kind = case.get("asset_profile", {}).get("kind")
    if kind == "manga109_title":
        print(f"{case['case_id']}\tBLOCKED_BY_ASSET_ACCESS\tObtain the official gated ZIP, then pass --archive <path>.")
        return 0, 0, False
    if kind == "open_public_comic_page":
        return download_public_comic_case(case)
    if kind != "hf_cleaned_webtoon":
        print(f"{case['case_id']}\tMANUAL_SOURCE_REQUIRED\t{case['source']}")
        return 0, 0, False
    return download_webtoon_case(case)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("download", "verify", "list", "missing"))
    parser.add_argument("--language", choices=("ja", "ko"))
    parser.add_argument("--level", choices=("smoke", "regression", "full"), default="smoke")
    parser.add_argument("--case-id", action="append", help="limit the command to a named case; may be repeated")
    parser.add_argument("--archive", type=Path, help="official Manga109 ZIP to import selected titles from")
    args = parser.parse_args()

    if args.archive and (args.command != "download" or args.language != "ja"):
        parser.error("--archive is supported only with download --language ja")
    manifest = load_manifest()
    cases = selected(manifest, args.language, args.level)
    if args.case_id:
        requested = set(args.case_id)
        cases = [case for case in cases if case["case_id"] in requested]
        if {case["case_id"] for case in cases} != requested:
            parser.error("--case-id must name a case in the selected language and level")
    if args.command in {"verify", "list", "missing"}:
        inventory_failures, inventory_checked, inventory_missing, invalid_paths = verify_inventory_files()
        benchmark_failures, benchmark_checked = verify_benchmark_source_inventories(manifest)
        case_statuses = print_cases(cases, show_missing_only=args.command == "missing", invalid_inventory_paths=invalid_paths)
        print(f"INVENTORY\tchecked={inventory_checked} missing={inventory_missing} failures={len(inventory_failures)}")
        print(f"BENCHMARK_INVENTORY\tchecked={benchmark_checked} failures={len(benchmark_failures)}")
        for failure in inventory_failures:
            print(f"INVALID_INVENTORY\t{failure}")
        for failure in benchmark_failures:
            print(f"INVALID_BENCHMARK_INVENTORY\t{failure}")
        if inventory_failures or benchmark_failures:
            print("SUMMARY\tFAILED")
            return 1
        if args.command in {"list", "missing"}:
            return 0
        for case in cases:
            kind = case.get("asset_profile", {}).get("kind")
            case_status = case_statuses[case["case_id"]]
            if kind in {"open_public_comic_page", "hf_cleaned_webtoon"}:
                if case_status != "READY":
                    ok, reason = validate_present(case)
                    message = reason if not ok else f"asset status is {case_status}"
                    print(f"INVALID\t{case['case_id']}\t{message}")
                    return 1
                continue
            if kind == "manga109_title":
                if case_status == "PARTIAL":
                    ok, reason = validate_present(case)
                    message = reason if not ok else "asset status is PARTIAL"
                    print(f"INVALID\t{case['case_id']}\t{message}")
                    return 1
                continue
            if case_status == "READY":
                ok, reason = validate_present(case)
                if not ok:
                    print(f"INVALID\t{case['case_id']}\t{reason}")
                    return 1
        return 0

    if args.archive:
        if not args.archive.is_file():
            print(f"ARCHIVE_NOT_FOUND\t{args.archive}", file=sys.stderr)
            return 1
        try:
            imported, skipped, failures = import_manga_archive(cases, args.archive)
        except (OSError, zipfile.BadZipFile) as exc:
            print(f"ARCHIVE_INVALID\t{type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        print(f"SUMMARY\timported={imported} existing={skipped} failures={failures}")
        return 1 if failures else 0

    downloaded = skipped = blocked = failures = 0
    for case in cases:
        kind = case.get("asset_profile", {}).get("kind")
        if kind == "manga109_title":
            blocked += 1
        got, kept, failed = download_case(case)
        downloaded += got
        skipped += kept
        failures += failed
    print(f"SUMMARY\tdownloaded={downloaded} existing={skipped} gated_cases={blocked} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
