"""Fetch and verify the pinned manga detector weights (one-time, stdlib-only).

Model: ``ogkalu/comic-text-and-bubble-detector`` (HuggingFace, RT-DETR-v2,
Apache-2.0), pinned revision ``16e8a622``. This is the ONLY sanctioned way
to obtain the manga weights outside a release package; the production
adapter never downloads at run time (``detection_manga.py`` resolves a
local directory and calls ``from_pretrained(local_files_only=True)`` — a
missing snapshot is a typed PROVIDER_NOT_CONFIGURED, never a network fetch).

PIN AUTHORITY: the per-file SHA-256 pins in
``src/infrastructure/providers/detection_manga.py`` are the AUTHORITY.
The pins below are a deployment-convenience copy taken from the same
source (the M2-DOCTR-QUAL-C4 weights manifest). If the two ever disagree,
the script FAILS the affected file (fail-closed) — it never installs
bytes that do not match the production pins.

Destination resolution (mirrors the production lookup order of
``bootstrap.core_assembly._resolve_detector_weights_path`` /
``bootstrap.core_assembly.default_data_root`` — the script reimplements
the two tiny env rules locally on purpose so it stays importable in a
bare stdlib-only venv with no ``src`` on the path):

1. ``--dest <dir>`` → weights land in that directory (highest priority);
2. ``NEWMANGA_DETECTOR_WEIGHTS`` set → that directory (the same override
   the production assembly reads for the manga adapter); a *file* value
   there is the docTR-style misconfiguration and is rejected with guidance;
3. otherwise → ``<default data root>/models/detector/ogkalu-comic-text-
   and-bubble-detector/``. The default data root replicates
   ``bootstrap.core_assembly.default_data_root`` verbatim:
   ``NEWMANGA_DATA_ROOT`` if set, else ``%LOCALAPPDATA%`` (Windows) or
   ``$HOME``, plus ``New Manga`` — i.e. by default
   ``%LOCALAPPDATA%/New Manga/models/detector/ogkalu-comic-text-and-bubble-detector/``.

Proxy behaviour: stdlib ``urllib`` honors the ``HTTP_PROXY`` /
``HTTPS_PROXY`` / ``ALL_PROXY`` environment variables through its default
opener (the script never installs a custom opener, so nothing can shadow
that). The effective proxies are printed at startup for auditability. See
``verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`` (scenario D) for the
full proxy SOP.

Idempotence: a file that already exists with the pinned SHA-256 is
skipped; a missing, truncated or corrupted file is re-downloaded (the
stale copy is only replaced after the freshly downloaded bytes verify).

Exit codes: 0 success (or all verified under --verify-only); 1 download
or SHA-256 failure; 2 usage error.

Usage (any Python 3.10+ with network access; torch/transformers NOT
required by this script):

    python verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py
    python verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py --dest <dir>
    python verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py --verify-only --dest <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# -- pinned snapshot identity (deployment-convenience copy) -----------------
# Source of truth: src/infrastructure/providers/detection_manga.py
# (MANGA_HF_REPO / MANGA_HF_REVISION / MANGA_*_SHA256), which itself comes
# from the M2-DOCTR-QUAL-C4 weights manifest. The code pins are the
# AUTHORITY; if these copies ever disagree with them, this script fails
# (fail-closed) — update the code pins FIRST through a re-pin slice, then
# mirror them here.
HF_REPO = "ogkalu/comic-text-and-bubble-detector"
HF_REVISION = "16e8a622"
WEIGHTS_DIRNAME = HF_REPO.replace("/", "-")

MODEL_FILENAME = "model.safetensors"
CONFIG_FILENAME = "config.json"
PREPROCESSOR_FILENAME = "preprocessor_config.json"

MODEL_SHA256 = (
    "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d"
)
CONFIG_SHA256 = (
    "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072"
)
PREPROCESSOR_SHA256 = (
    "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca"
)

# (filename, sha256 pin) — the exact snapshot the production loader checks.
PINNED_FILES: tuple[tuple[str, str], ...] = (
    (MODEL_FILENAME, MODEL_SHA256),
    (CONFIG_FILENAME, CONFIG_SHA256),
    (PREPROCESSOR_FILENAME, PREPROCESSOR_SHA256),
)

DOWNLOAD_CHUNK_BYTES = 1024 * 1024
DOWNLOAD_TIMEOUT_S = 60.0
USER_AGENT = "newmanga-fetch-manga-weights/1.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(DOWNLOAD_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_data_root() -> Path:
    """Replicates ``bootstrap.core_assembly.default_data_root`` verbatim.

    Kept in local copy form (instead of importing ``src``) so the script
    runs in any bare Python env; if the production default ever moves, the
    SOP and this function must move with it (the module docstring notes
    the mirror duty).
    """
    root = os.environ.get("NEWMANGA_DATA_ROOT")
    if root:
        return Path(root)
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home()
    return base / "New Manga"


def resolve_dest(explicit_dest: Path | None) -> Path:
    """--dest > NEWMANGA_DETECTOR_WEIGHTS (directory) > default layout."""
    if explicit_dest is not None:
        return explicit_dest
    override = os.environ.get("NEWMANGA_DETECTOR_WEIGHTS")
    if override:
        candidate = Path(override)
        if candidate.is_file() or candidate.suffix:
            # docTR-style misconfiguration: NEWMANGA_DETECTOR_WEIGHTS
            # points at a .pt *file* — the manga adapter needs a directory.
            print(
                f"ERROR: NEWMANGA_DETECTOR_WEIGHTS={override!r} looks like a "
                f"file, but the manga detector needs a DIRECTORY snapshot "
                f"(config.json + model.safetensors + "
                f"preprocessor_config.json); pass --dest <dir> explicitly "
                f"or clear the variable",
                file=sys.stderr,
            )
            raise SystemExit(2)
        return candidate
    return default_data_root() / "models" / "detector" / WEIGHTS_DIRNAME


def file_url(filename: str, revision: str) -> str:
    return f"https://huggingface.co/{HF_REPO}/resolve/{revision}/{filename}"


def download_file(url: str, target: Path) -> None:
    """Stream one file to ``target`` via a ``.part`` temp file.

    Uses the DEFAULT urllib opener so the HTTP(S)_PROXY environment
    variables stay in charge; redirects (HF resolve 302s to its CDN) are
    followed by the default handler. Raises on any HTTP/network error —
    the caller reports and exits non-zero.
    """
    tmp = target.with_suffix(target.suffix + ".part")
    if tmp.exists():
        tmp.unlink()  # stale partial download from an earlier run
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(  # noqa: S310 - pinned https host
        request, timeout=DOWNLOAD_TIMEOUT_S
    ) as response, open(tmp, "wb") as out:
        while True:
            chunk = response.read(DOWNLOAD_CHUNK_BYTES)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(target)


def download_and_verify(
    dest: Path, revision: str, pins: tuple[tuple[str, str], ...]
) -> int:
    """Fetch each pinned file; skip the ones already verified (idempotent).

    A file that exists but fails its pin (truncated / corrupted /
    substituted) is re-downloaded; the replacement only lands after the
    fresh bytes verify. Any persistent mismatch or network failure exits
    non-zero with the offending file named.
    """
    dest.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for filename, pin in pins:
        target = dest / filename
        expected = pin if revision == HF_REVISION else None
        if target.is_file():
            actual = sha256_file(target)
            if expected is not None and actual == expected:
                print(f"already fetched and verified: {target}")
                continue
            if expected is None:
                print(
                    f"already present (UNVERIFIED revision drift): {target} "
                    f"sha256={actual}"
                )
                continue
            print(
                f"existing file has wrong sha256, re-downloading: {target} "
                f"(actual {actual}, expected {expected})"
            )
        url = file_url(filename, revision)
        print(f"downloading {url}")
        try:
            download_file(url, target)
        except (urllib.error.URLError, OSError) as error:
            failures.append(f"{filename}: download failed: {error!r}")
            continue
        actual = sha256_file(target)
        if expected is not None and actual != expected:
            failures.append(
                f"{filename}: sha256 mismatch after download: {actual} != "
                f"{expected} (kept nothing; delete {target} and retry, and "
                f"if this persists treat it as a supply-chain incident — "
                f"the production pins in detection_manga.py are the "
                f"authority)"
            )
            continue
        print(
            f"verified and installed: {target} ({actual}"
            + ("" if expected is not None else ", UNVERIFIED revision drift")
            + ")"
        )
    if failures:
        print("\nFAILED file(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


def verify_only(dest: Path, pins: tuple[tuple[str, str], ...]) -> int:
    """Offline check: every pinned file exists and matches its pin.

    Purely local — this mode never touches the network, so it doubles as
    the acceptance probe for release packages and preflight installs.
    """
    if not dest.is_dir():
        print(
            f"FAIL: weights directory {dest} does not exist (run without "
            f"--verify-only to fetch the pinned snapshot first)",
            file=sys.stderr,
        )
        return 1
    failures: list[str] = []
    for filename, pin in pins:
        target = dest / filename
        if not target.is_file():
            failures.append(f"{filename}: MISSING at {target}")
            continue
        actual = sha256_file(target)
        if actual != pin:
            failures.append(
                f"{filename}: sha256 {actual} != pinned {pin} at {target}"
            )
        else:
            print(f"ok: {target} ({pin})")
    if failures:
        print("\nFAILED file(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(
        f"all {len(pins)} pinned files verified in {dest} "
        f"(snapshot {HF_REPO} @ {HF_REVISION})"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch and SHA-256-verify the pinned manga detector weights "
            f"({HF_REPO} @ {HF_REVISION}); stdlib-only, proxy-aware."
        )
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help=(
            "target directory (default: <data root>/models/detector/"
            f"{WEIGHTS_DIRNAME}; the data root is NEWMANGA_DATA_ROOT or "
            "%%LOCALAPPDATA%%\\New Manga)"
        ),
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="offline mode: verify the pinned SHA-256s without network",
    )
    parser.add_argument(
        "--source-revision",
        default=HF_REVISION,
        help=(
            "HuggingFace revision to fetch (default: the pinned "
            f"{HF_REVISION}); a different revision is NEVER installed as "
            "production weights — it requires an explicit --dest outside "
            "the default production layout and a re-pin slice"
        ),
    )
    args = parser.parse_args()

    revision = args.source_revision.strip()
    unverified_drift = revision != HF_REVISION
    if unverified_drift:
        if args.dest is None:
            parser.error(
                f"--source-revision {revision} != pinned {HF_REVISION} "
                "requires an explicit --dest: drifted weights must never "
                "land in the default production layout unverified"
            )
        print(
            f"WARNING: fetching revision {revision}, which is NOT the "
            f"pinned production revision {HF_REVISION}; the per-file SHA-256 "
            "pins do not apply — files are reported UNVERIFIED and must go "
            "through a re-pin slice (update detection_manga.py pins first) "
            "before production use",
            file=sys.stderr,
        )

    proxies = urllib.request.getproxies()
    if proxies:
        print(f"proxy environment in effect: {proxies}")
    else:
        print("no proxy environment variables detected")

    dest = resolve_dest(args.dest)
    pins = PINNED_FILES
    if args.verify_only:
        return verify_only(dest, pins)
    return download_and_verify(dest, revision, pins)


if __name__ == "__main__":
    sys.exit(main())
