"""List, verify, and explicitly download/import the shared JA/KO comic assets."""

from __future__ import annotations

import argparse
import json
import os
import re
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
MANIFEST_PATH = ROOT / "manifests" / "cases.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COPY_BLOCK = 1024 * 1024
MAX_ANNOTATION_BYTES = 32 * 1024 * 1024
MAX_IMAGE_BYTES = 128 * 1024 * 1024


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    allowed_tags = set(manifest["taxonomy"]["difficulty_tags"])
    required = {
        "case_id", "language", "source", "source_type", "layout_type",
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
    if kind == "manual_source_page":
        return [path for path in directory.iterdir() if path.is_file()] if directory.is_dir() else []
    return []


def manga_marker(case: dict) -> Path:
    return local_dir(case) / ".asset-complete.json"


def status(case: dict) -> str:
    kind = case.get("asset_profile", {}).get("kind")
    paths = required_files(case)
    if kind == "manga109_title":
        marker = manga_marker(case)
        if marker.is_file() and all(path.is_file() and path.stat().st_size > 0 for path in paths):
            try:
                data = json.loads(marker.read_text(encoding="utf-8"))
                images = sorted(path.name for path in paths if path.suffix.lower() == ".jpg")
                if data.get("case_id") == case["case_id"] and data.get("images") == images:
                    return "READY"
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                pass
        return "PARTIAL" if any(path.is_file() for path in paths) else "MISSING_GATED_ASSET"
    if kind == "manual_source_page":
        return "PARTIAL" if any(path.is_file() and path.stat().st_size > 0 for path in paths) else "MISSING"
    if paths and all(path.is_file() and path.stat().st_size > 0 for path in paths):
        return "READY"
    return "MISSING"


def print_cases(cases: list[dict], show_missing_only: bool = False) -> None:
    counts: dict[str, int] = {}
    for case in cases:
        current = status(case)
        counts[current] = counts.get(current, 0) + 1
        if not show_missing_only or current != "READY":
            print(f"{case['case_id']}\t{case['language']}\t{current}\t{case['local_path']}")
    print("SUMMARY\t" + " ".join(f"{key}={counts[key]}" for key in sorted(counts)))


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
    if not name or "\\" in name or "\x00" in name or path.is_absolute() or PureWindowsPath(name).drive or ".." in path.parts:
        raise ValueError(f"unsafe path in Manga109 archive: {name!r}")
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
    if kind != "hf_cleaned_webtoon":
        print(f"{case['case_id']}\tMANUAL_SOURCE_REQUIRED\t{case['source']}")
        return 0, 0, False
    return download_webtoon_case(case)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("download", "verify", "list", "missing"))
    parser.add_argument("--language", choices=("ja", "ko"))
    parser.add_argument("--level", choices=("smoke", "regression", "full"), default="smoke")
    parser.add_argument("--archive", type=Path, help="official Manga109 ZIP to import selected titles from")
    args = parser.parse_args()

    if args.archive and (args.command != "download" or args.language != "ja"):
        parser.error("--archive is supported only with download --language ja")
    manifest = load_manifest()
    cases = selected(manifest, args.language, args.level)
    if args.command in {"list", "missing"}:
        print_cases(cases, show_missing_only=args.command == "missing")
        return 0
    if args.command == "verify":
        print_cases(cases)
        for case in cases:
            if status(case) == "READY":
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
