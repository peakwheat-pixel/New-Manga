"""Fetch and verify the pinned T1.1.1 docTR detection weights (one-time).

This is the ONLY sanctioned way to obtain the weights; the production
adapter never downloads (missing weights are a typed PROVIDER_NOT_CONFIGURED).
The file is verified against the pinned SHA-256 before it lands in the docTR
cache where the tests (and, via NEWMANGA_DETECTOR_WEIGHTS, the app) find it.

Usage (any Python 3.12 env with network access):
    python verification/T1.1.1/scripts/fetch_doctr_weights.py
    python verification/T1.1.1/scripts/fetch_doctr_weights.py --dest <dir>

Default destination is the docTR cache ~/.cache/doctr/models/.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

WEIGHTS_FILENAME = "fast_base-688a8b34.pt"
WEIGHTS_URL = (
    "https://doctr-static.mindee.com/models?id=v0.8.1/fast_base-688a8b34.pt&src=0"
)
WEIGHTS_SHA256 = (
    "688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path.home() / ".cache" / "doctr" / "models",
        help="target directory (default: docTR cache)",
    )
    args = parser.parse_args()
    dest: Path = args.dest
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / WEIGHTS_FILENAME

    if target.is_file():
        actual = sha256_file(target)
        if actual == WEIGHTS_SHA256:
            print(f"already fetched and verified: {target}")
            return 0
        print(
            f"refusing existing file with wrong sha256 at {target}: {actual}",
            file=sys.stderr,
        )
        return 1

    print(f"downloading {WEIGHTS_URL}")
    tmp = target.with_suffix(".part")
    urllib.request.urlretrieve(WEIGHTS_URL, tmp)
    actual = sha256_file(tmp)
    if actual != WEIGHTS_SHA256:
        print(
            f"sha256 mismatch after download: {actual} != {WEIGHTS_SHA256}; "
            f"keeping nothing ({tmp})",
            file=sys.stderr,
        )
        return 1
    tmp.replace(target)
    print(f"verified and installed: {target} ({WEIGHTS_SHA256})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
