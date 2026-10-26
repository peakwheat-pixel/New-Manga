"""Fetch, verify, and render official free Black Jack volumes (densho810.com).

M2-TA2B AC1/AC2 helper. Downloads the official free Japanese ZIP editions of
"Give My Regards to Black Jack" (ブラックジャックによろしく, © 佐藤秀峰 / Sato Manga
Seisakusho) published by the author's company at https://densho810.com/free/,
unpacks the DRM-free PDF, verifies it with pypdfium2, and renders sampled pages
to PNG (DPI 150) for the golden suite.

License obligations (author's terms on the download page):
- free for commercial and non-commercial use, no prior permission needed;
- mandatory attribution: title "ブラックジャックによろしく" + author "佐藤秀峰";
- report by e-mail to info@densho810.com within 1 month after public use;
- volumes 2/7/11 contain JASRAC-managed song pages (avoided by default).

Only the standard library is required for `fetch`; `render` additionally uses
the production dependency pypdfium2 (+ Pillow). Downloaded pixels stay in the
gitignored asset directory and never enter Git.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

# Reuse the hardened ZIP member / PNG helpers from the suite's main tool.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import assets  # noqa: E402  (same tools/ directory, plain import by design)


ROOT = assets.ROOT
OUTPUT_DIR = ROOT / "日漫_JA" / "01_black_jack_official"
SOURCE_URL = "https://densho810.com/free/"
ARCHIVE_URL_TEMPLATE = "https://densho810.com/free/dl/{num:03d}bj.zip"
DOWNLOAD_HOST = "densho810.com"
ARCHIVE_PATH_RE = re.compile(r"^/free/dl/\d{3}bj\.zip$")
USER_AGENT = "NewManga-TestAssets/1.0"
RETRY_ATTEMPTS = 3  # 1 initial attempt + 2 retries
TIMEOUT = 120
MAX_ARCHIVE_BYTES = 600 * 1024 * 1024  # observed volumes are ~330-370 MB
MAX_PDF_BYTES = 600 * 1024 * 1024
LICENSE_CLASS = "commercial_use_permitted_attribution"
ATTRIBUTION = "ブラックジャックによろしく　佐藤秀峰"
ATTRIBUTION_NOTE = (
    "Source: densho810.com (official free channel by Sato Manga Seisakusho); "
    "free secondary-use license with mandatory attribution; report to info@densho810.com "
    "within 1 month of public use."
)
JASRAC_VOLUMES = {2, 7, 11}
DEFAULT_VOLUMES = (1, 3, 5)
SAMPLE_PAGES_PER_VOLUME = 4
RENDER_DPI = 150


def is_allowed_archive_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    return (
        parsed.scheme.lower() == "https"
        and parsed.hostname is not None
        and parsed.hostname.lower() == DOWNLOAD_HOST
        and parsed.port in (None, 443)
        and parsed.username is None
        and parsed.password is None
        and ARCHIVE_PATH_RE.fullmatch(parsed.path) is not None
    )


class RedirectGuard(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        target = urllib.parse.urljoin(request.full_url, new_url)
        if not is_allowed_archive_url(target):
            raise urllib.error.HTTPError(
                request.full_url, code, "redirect target is outside the approved densho810.com path", headers, response
            )
        return super().redirect_request(request, response, code, message, headers, target)


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(assets.COPY_BLOCK):
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def valid_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return len(archive.infolist()) > 0
    except (OSError, zipfile.BadZipFile):
        return False


def download_archive(url: str, destination: Path) -> tuple[bool, str, int, int]:
    """Download `url` to `destination` atomically. Returns (downloaded, reason, sha256, size)."""
    if destination.is_symlink():
        raise OSError(f"existing path is a symlink; left untouched: {destination.name}")
    if destination.exists():
        if valid_zip(destination):
            digest, size = sha256_file(destination)
            return False, "already present and valid", digest, size
        raise OSError(f"existing file is not a valid ZIP; left untouched: {destination.name}")

    last_error: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        temp_name = None
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            opener = urllib.request.build_opener(RedirectGuard())
            with opener.open(request, timeout=TIMEOUT) as response:
                final = urllib.parse.urlsplit(response.geturl())
                if final.hostname is None or final.hostname.lower() != DOWNLOAD_HOST or final.scheme.lower() != "https":
                    raise OSError("final download URL is outside the approved HTTPS host")
                content_length = response.headers.get("Content-Length")
                if not content_length or not content_length.isdecimal():
                    raise OSError("response has no verifiable Content-Length")
                expected_size = int(content_length)
                if expected_size <= 0 or expected_size > MAX_ARCHIVE_BYTES:
                    raise OSError(f"remote file size is outside limits: {expected_size} bytes")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                    prefix=f".{destination.name}.", suffix=".part", dir=destination.parent, delete=False
                ) as temp:
                    temp_name = temp.name
                    written = 0
                    while chunk := response.read(assets.COPY_BLOCK):
                        written += len(chunk)
                        if written > expected_size:
                            raise OSError("download exceeds declared Content-Length")
                        temp.write(chunk)
            temp_path = Path(temp_name)
            try:
                if written != expected_size:
                    raise OSError(f"incomplete download: expected {expected_size} bytes, received {written}")
                if not valid_zip(temp_path):
                    raise OSError("downloaded payload is not a valid ZIP")
                try:
                    os.link(temp_path, destination)
                except FileExistsError:
                    if not valid_zip(destination):
                        raise OSError("destination appeared with invalid content; left untouched")
                    digest, size = sha256_file(destination)
                    return False, "published concurrently", digest, size
                digest, size = sha256_file(destination)
                return True, "downloaded", digest, size
            finally:
                # The hard link keeps the published file alive when the temp name goes away.
                temp_path.unlink(missing_ok=True)
        except (OSError, urllib.error.URLError) as exc:
            last_error = exc
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
            if attempt < RETRY_ATTEMPTS:
                time.sleep(2 * attempt)
    raise OSError(f"download failed after {RETRY_ATTEMPTS} attempts: {last_error}")


def extract_pdf(archive_path: Path, volume_dir: Path, volume: int) -> tuple[str, str, int]:
    """Extract the single PDF member to a fixed name. Returns (filename, sha256, byte_size)."""
    pdf_members: list[zipfile.ZipInfo] = []
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            parts = assets.zip_parts(info)  # raises ValueError on unsafe paths
            # Skip macOS archive metadata members (__MACOSX/._x.pdf AppleDouble files).
            if "__MACOSX" in parts[:-1] or PurePosixName(parts[-1]).startswith("._"):
                continue
            if PurePosixName(parts[-1]).lower().endswith(".pdf"):
                if info.file_size > MAX_PDF_BYTES:
                    raise ValueError(f"PDF member exceeds size limit: {info.filename}")
                if info.flag_bits & 1:
                    raise ValueError(f"encrypted ZIP member is not accepted: {info.filename}")
                pdf_members.append(info)
        if len(pdf_members) != 1:
            raise ValueError(f"expected exactly one PDF member, found {len(pdf_members)}")
        member = pdf_members[0]
        destination = volume_dir / f"volume{volume:02d}.pdf"
        if destination.exists():
            if destination.is_symlink():
                raise OSError(f"existing path is a symlink; left untouched: {destination.name}")
            digest, size = sha256_file(destination)
            return destination.name, digest, size
        temp_name = None
        try:
            with archive.open(member) as source:
                with tempfile.NamedTemporaryFile(
                    prefix=f".volume{volume:02d}.pdf.", suffix=".part", dir=volume_dir, delete=False
                ) as temp:
                    temp_name = temp.name
                    written = 0
                    while chunk := source.read(assets.COPY_BLOCK):
                        written += len(chunk)
                        if written > member.file_size:
                            raise OSError("ZIP member expands beyond its declared size")
                        temp.write(chunk)
            temp_path = Path(temp_name)
            if written != member.file_size:
                raise OSError(f"ZIP member size mismatch: {member.filename}")
            try:
                os.link(temp_path, destination)
            except FileExistsError:
                pass
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
    digest, size = sha256_file(destination)
    return destination.name, digest, size


def PurePosixName(name: str) -> str:
    from pathlib import PurePosixPath

    return PurePosixPath(name).name


def verify_pdf(pdf_path: Path) -> int:
    """Open with pypdfium2; require a decrypted document with pages. Returns page count."""
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit("render/verify requires the production dependency pypdfium2 (pip install pypdfium2==5.13.0)") from exc
    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as exc:  # pypdfium2.PdfiumError subclasses Exception
        raise OSError(f"PDF failed to open (possibly DRM-protected): {type(exc).__name__}: {exc}") from exc
    try:
        page_count = len(pdf)
        if page_count <= 0:
            raise OSError("PDF has no pages")
        # Touch the first page to prove the content decodes without a DRM failure.
        pdf[0].get_size()
        return page_count
    finally:
        pdf.close()


def fetch_volumes(volumes: list[int]) -> int:
    failures = 0
    for volume in volumes:
        if volume <= 0 or volume > 999:
            print(f"vol{volume:03d}\tFETCH_FAILED\tinvalid volume number", file=sys.stderr)
            failures += 1
            continue
        volume_dir = OUTPUT_DIR / f"vol{volume:02d}"
        volume_dir.mkdir(parents=True, exist_ok=True)
        url = ARCHIVE_URL_TEMPLATE.format(num=volume)
        try:
            if not is_allowed_archive_url(url):
                raise ValueError(f"generated URL is outside the approved pattern: {url}")
            print(f"vol{volume:02d}\tFETCH\t{url}")
            downloaded, reason, archive_sha, archive_size = download_archive(url, volume_dir / f"{volume:03d}bj.zip")
            pdf_name, pdf_sha, pdf_size = extract_pdf(volume_dir / f"{volume:03d}bj.zip", volume_dir, volume)
            page_count = verify_pdf(volume_dir / pdf_name)
        except (OSError, ValueError, zipfile.BadZipFile, urllib.error.URLError) as exc:
            print(f"vol{volume:02d}\tFETCH_FAILED\t{type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue
        manifest = {
            "volume": volume,
            "source_url": SOURCE_URL,
            "archive_url": url,
            "license_class": LICENSE_CLASS,
            "attribution": ATTRIBUTION,
            "attribution_note": ATTRIBUTION_NOTE,
            "jasrac_volume": volume in JASRAC_VOLUMES,
            "downloaded_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "files": [
                {"filename": f"{volume:03d}bj.zip", "sha256": archive_sha, "byte_size": archive_size,
                 "downloaded_this_run": downloaded, "status": reason},
                {"filename": pdf_name, "sha256": pdf_sha, "byte_size": pdf_size,
                 "pdf_page_count": page_count, "drm_checked": True},
            ],
        }
        manifest_path = volume_dir / "bj_download_manifest.json"
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix=".bjmanifest.", suffix=".part", dir=volume_dir, delete=False
            ) as temp:
                temp_name = temp.name
                json.dump(manifest, temp, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(temp_name, manifest_path)
            temp_name = None
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
        print(
            f"vol{volume:02d}\tFETCH_OK\tzip={archive_size}B sha256={archive_sha[:16]}... "
            f"pdf_pages={page_count} {'downloaded' if downloaded else 'reused'}"
        )
    return failures


def sample_page_indices(page_count: int, count: int) -> list[int]:
    """First / quarter / middle / last sampling over 0-based page indices."""
    if page_count <= count:
        return list(range(page_count))
    return sorted({0, page_count // 4, page_count // 2, page_count - 1})[:count]


def render_volumes(volumes: list[int]) -> int:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit("render requires the production dependency pypdfium2 (pip install pypdfium2==5.13.0)") from exc
    failures = 0
    scale = RENDER_DPI / 72
    for volume in volumes:
        volume_dir = OUTPUT_DIR / f"vol{volume:02d}"
        pdf_path = volume_dir / f"volume{volume:02d}.pdf"
        pages_dir = volume_dir / "pages"
        if not pdf_path.is_file():
            print(f"vol{volume:02d}\tRENDER_SKIPPED\tmissing {pdf_path.name}; run fetch first", file=sys.stderr)
            failures += 1
            continue
        pages_dir.mkdir(parents=True, exist_ok=True)
        try:
            pdf = pdfium.PdfDocument(pdf_path)
        except Exception as exc:
            print(f"vol{volume:02d}\tRENDER_FAILED\t{type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue
        page_entries: list[dict] = []
        duplicates: list[dict] = []
        seen_hashes: dict[str, str] = {}
        try:
            page_count = len(pdf)
            for index in sample_page_indices(page_count, SAMPLE_PAGES_PER_VOLUME):
                pil_image = pdf[index].render(scale=scale).to_pil().convert("RGB")
                output = pages_dir / f"vol{volume:02d}_p{index + 1:04d}.png"
                if output.is_symlink():
                    raise OSError(f"existing path is a symlink; left untouched: {output.name}")
                temp_name = None
                try:
                    with tempfile.NamedTemporaryFile(
                        prefix=f".{output.stem}.", suffix=".png.part", dir=pages_dir, delete=False
                    ) as temp:
                        temp_name = temp.name
                        pil_image.save(temp, format="PNG")
                    os.replace(temp_name, output)
                    temp_name = None
                finally:
                    if temp_name:
                        Path(temp_name).unlink(missing_ok=True)
                digest, size = sha256_file(output)
                entry = {
                    "pdf_page_index": index,
                    "pdf_page_number": index + 1,
                    "filename": f"pages/{output.name}",
                    "sha256": digest,
                    "byte_size": size,
                    "width": pil_image.width,
                    "height": pil_image.height,
                }
                if digest in seen_hashes:
                    duplicates.append({**entry, "duplicate_of": seen_hashes[digest]})
                    output.unlink()
                else:
                    seen_hashes[digest] = entry["filename"]
                    page_entries.append(entry)
                print(f"vol{volume:02d}\tRENDERED\tpage={index + 1}/{page_count} {pil_image.width}x{pil_image.height}")
        finally:
            pdf.close()
        manifest = {
            "volume": volume,
            "source_url": SOURCE_URL,
            "license_class": LICENSE_CLASS,
            "attribution": ATTRIBUTION,
            "attribution_note": ATTRIBUTION_NOTE,
            "dpi": RENDER_DPI,
            "pdf_page_count": page_count,
            "sampled_pages": [entry["pdf_page_number"] for entry in page_entries],
            "pages": page_entries,
            "duplicates_removed": duplicates,
        }
        manifest_path = volume_dir / "bj_pages_manifest.json"
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix=".bjpages.", suffix=".part", dir=volume_dir, delete=False
            ) as temp:
                temp_name = temp.name
                json.dump(manifest, temp, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(temp_name, manifest_path)
            temp_name = None
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
        print(f"vol{volume:02d}\tRENDER_OK\tpages={len(page_entries)} duplicates={len(duplicates)}")
    return failures


def verify_rendered_pages() -> int:
    """Recompute page SHA-256 for every BJ case in cases.json (M2-TA2B P2-1 closure).

    The BJ pages live outside the runtime inventory by design (gitignored
    pixels), so this command is their automated integrity path.
    """
    manifest = assets.load_manifest()
    cases = [c for c in manifest["cases"] if re.fullmatch(r"BJ\d{2}", c.get("case_id", ""))]
    if not cases:
        print("VERIFY_FAILED\tno BJ cases found in cases.json", file=sys.stderr)
        return 1
    failures = 0
    for case in cases:
        page_rel = case.get("page_file")
        expected = case.get("page_sha256")
        if not page_rel or not expected:
            print(f"{case['case_id']}\tVERIFY_FAILED\tmissing page_file/page_sha256 fields", file=sys.stderr)
            failures += 1
            continue
        base = assets.ROOT / case["local_path"]
        page_path = base / page_rel
        if not page_path.is_file() and page_rel.startswith(f"{base.name}/"):
            # cases.json local_path ends with the same segment that prefixes page_file
            # (…/vol01/pages + pages/vol01_p0001.png); de-duplicate that segment.
            page_path = base.parent / page_rel
        if not page_path.is_file():
            print(f"{case['case_id']}\tVERIFY_FAILED\tmissing file: {page_rel}", file=sys.stderr)
            failures += 1
            continue
        digest, size = sha256_file(page_path)
        if digest != expected:
            print(f"{case['case_id']}\tVERIFY_FAILED\tsha256 mismatch: {page_rel}", file=sys.stderr)
            failures += 1
        else:
            print(f"{case['case_id']}\tVERIFY_OK\t{page_rel} sha256={digest[:16]}... size={size}")
    print(f"SUMMARY\tcommand=verify cases={len(cases)} failures={failures}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("fetch", "render", "verify"))
    parser.add_argument("--volumes", type=int, nargs="+", default=list(DEFAULT_VOLUMES),
                        help="volume numbers to process (default: 1 3 5, avoiding JASRAC volumes 2/7/11)")
    args = parser.parse_args()
    if args.command == "verify":
        return verify_rendered_pages()
    if any(volume in JASRAC_VOLUMES for volume in args.volumes):
        print("refusing JASRAC-managed volumes (2/7/11) by default policy", file=sys.stderr)
        return 2
    failures = fetch_volumes(args.volumes) if args.command == "fetch" else render_volumes(args.volumes)
    print(f"SUMMARY\tcommand={args.command} volumes={len(args.volumes)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
