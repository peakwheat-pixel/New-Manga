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
        # R-A4: reject only values that EXIST and are not a directory (the
        # docTR-era misconfiguration where the var points at a .pt *file*).
        # A dotted name like "weights.v2" is a legal directory and must not
        # be rejected on its suffix; a not-yet-existing path is left to the
        # normal mkdir/download flow.
        if candidate.exists() and not candidate.is_dir():
            print(
                f"ERROR: NEWMANGA_DETECTOR_WEIGHTS={override!r} exists and "
                f"is not a directory, but the manga detector needs a "
                f"DIRECTORY snapshot (config.json + model.safetensors + "
                f"preprocessor_config.json); if it still points at the "
                f"docTR fast_base .pt file, pass --dest <dir> explicitly "
                f"or clear the variable",
                file=sys.stderr,
            )
            raise SystemExit(2)
        return candidate
    return default_data_root() / "models" / "detector" / WEIGHTS_DIRNAME


def file_url(filename: str, revision: str) -> str:
    return f"https://huggingface.co/{HF_REPO}/resolve/{revision}/{filename}"


def download_file(url: str, tmp: Path) -> None:
    """Stream one file into ``tmp`` (a ``.part`` scratch path) — nothing else.

    Uses the DEFAULT urllib opener so the HTTP(S)_PROXY environment
    variables stay in charge; redirects (HF resolve 302s to its CDN) are
    followed by the default handler. Raises on any HTTP/network error —
    the caller reports and exits non-zero. On ANY failure (including
    KeyboardInterrupt) the partial ``.part`` is deleted so no multi-MB
    debris is left in the weights directory; the destination is never
    touched by this function (R-A1: verification happens on ``tmp`` and
    only a verified file is promoted by the caller).
    """
    if tmp.exists():
        tmp.unlink()  # stale partial download from an earlier run
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(  # noqa: S310 - pinned https host
            request, timeout=DOWNLOAD_TIMEOUT_S
        ) as response, open(tmp, "wb") as out:
            while True:
                chunk = response.read(DOWNLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                out.write(chunk)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def download_and_verify(
    dest: Path,
    revision: str,
    pins: tuple[tuple[str, str], ...],
    force: bool = False,
) -> int:
    """Fetch each pinned file; skip the ones already verified (idempotent).

    Install discipline (R-A1, mirroring ``fetch_doctr_weights.py``): the
    fresh bytes land in a ``.part`` scratch file and are SHA-256-verified
    THERE — ``tmp.replace(target)`` runs only after the pin matches, so no
    unverified bytes ever reach the destination. On a mismatch the
    ``.part`` is deleted, the destination keeps its previous content (if
    any) and the failure is reported with the real on-disk facts.

    A file that exists but fails its pin (truncated / corrupted /
    substituted) is re-downloaded the same way. Any persistent mismatch or
    network failure exits non-zero with the offending file named.

    Drift mode (``revision !=`` pinned, ``expected is None``) has NO pin
    to verify against, so there it requires an empty (or absent)
    destination unless ``--force`` is given, and ``--force`` re-downloads
    EVERY file instead of trusting existing ones — a stale or truncated
    leftover can never silently pass as a complete fetch (R-A3).
    """
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except (FileExistsError, NotADirectoryError) as error:
        # R-A7: a file (or unreadable path) at dest is a USAGE error —
        # exit 2 with guidance, never a bare traceback.
        print(
            f"ERROR: destination {dest} cannot be used: {error!r} "
            "(a file exists there, but the manga weights need a directory); "
            "pass a different --dest",
            file=sys.stderr,
        )
        return 2
    failures: list[str] = []
    for filename, pin in pins:
        target = dest / filename
        expected = pin if revision == HF_REVISION else None
        if target.is_file():
            actual = sha256_file(target)
            if expected is not None and actual == expected:
                print(f"already fetched and verified: {target}")
                continue
            if expected is None and not force:
                # Unreachable via main() (drift mode gates on an empty
                # destination before reaching this loop) — kept as a
                # guard for direct callers.
                print(
                    f"already present (UNVERIFIED revision drift): {target} "
                    f"sha256={actual}"
                )
                continue
            print(
                f"existing file has wrong sha256, re-downloading: {target} "
                + (
                    f"(actual {actual}, expected {expected})"
                    if expected is not None
                    else f"(drift --force: re-fetching, old sha256 {actual})"
                )
            )
        url = file_url(filename, revision)
        print(f"downloading {url}")
        tmp = target.with_suffix(target.suffix + ".part")
        try:
            download_file(url, tmp)
        except (urllib.error.URLError, OSError) as error:
            failures.append(f"{filename}: download failed: {error!r}")
            continue
        actual = sha256_file(tmp)
        if expected is not None and actual != expected:
            tmp.unlink()
            failures.append(
                f"{filename}: sha256 mismatch after download: {actual} != "
                f"{expected}; the mismatched bytes were DELETED and nothing "
                f"was installed — {target} is unchanged (delete it manually "
                f"and retry if a stale copy remains); if this persists "
                f"treat it as a supply-chain incident — the production pins "
                f"in detection_manga.py are the authority"
            )
            continue
        tmp.replace(target)  # verified bytes only — never install unverified
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
        help=(
            "offline mode: verify the pinned SHA-256s without network "
            "(--source-revision is ignored in this mode)"
        ),
    )
    parser.add_argument(
        "--source-revision",
        default=HF_REVISION,
        help=(
            "HuggingFace revision to fetch (default: the pinned "
            f"{HF_REVISION}); a different revision is NEVER installed as "
            "production weights — it requires an explicit --dest outside "
            "the default production layout, an EMPTY destination (or "
            "--force), and a re-pin slice"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "drift mode only: allow a NON-EMPTY destination and "
            "re-download every file instead of trusting existing ones "
            "(ignored in pinned/verify modes, which verify pins anyway)"
        ),
    )
    args = parser.parse_args()

    if args.verify_only:
        # R-A6: verify-only never touches the network and always checks
        # the PINS, so the drift gate/warning below would only produce a
        # self-contradicting diagnosis — skip it entirely.
        dest = resolve_dest(args.dest)
        return verify_only(dest, PINNED_FILES)

    revision = args.source_revision.strip()
    unverified_drift = revision != HF_REVISION
    if unverified_drift:
        if args.dest is None:
            parser.error(
                f"--source-revision {revision} != pinned {HF_REVISION} "
                "requires an explicit --dest: drifted weights must never "
                "land in the default production layout unverified"
            )
        dest = resolve_dest(args.dest)
        existing = [p.name for p in dest.iterdir()] if dest.is_dir() else []
        if existing and not args.force:
            # R-A3: without pins to verify against, reusing a directory
            # could silently accept stale/truncated files — require a
            # clean target or an explicit --force (which re-downloads
            # every file).
            parser.error(
                f"--source-revision {revision} with a NON-EMPTY destination "
                f"{dest} ({len(existing)} entry/entries) requires --force: "
                "drifted revisions have no pin to verify existing files "
                "against; prefer a fresh empty directory per drift fetch"
            )
        print(
            f"WARNING: fetching revision {revision}, which is NOT the "
            f"pinned production revision {HF_REVISION}; the per-file SHA-256 "
            "pins do not apply — files are reported UNVERIFIED and must go "
            "through a re-pin slice (update detection_manga.py pins first) "
            "before production use",
            file=sys.stderr,
        )
    else:
        dest = resolve_dest(args.dest)

    proxies = urllib.request.getproxies()
    if proxies:
        print(f"proxy environment in effect: {proxies}")
    else:
        print("no proxy environment variables detected")

    return download_and_verify(dest, revision, PINNED_FILES, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
