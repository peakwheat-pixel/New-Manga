"""Fetch and verify the pinned T1.1.1 docTR detection weights (one-time).

This is the ONLY sanctioned way to obtain the weights; the production
adapter never downloads (missing weights are a typed PROVIDER_NOT_CONFIGURED).
The file is verified against the pinned SHA-256 before it lands at its
destination.

Destination resolution (aligned with ``bootstrap.app``, Review fix):

1. ``NEWMANGA_DETECTOR_WEIGHTS`` set → that exact file path (the same
   environment variable the production assembly reads);
2. ``--dest <dir>`` → weights land in that directory;
3. otherwise → ``./models/detector/`` under the current directory, i.e.
   the ``<data root>/models/detector/`` layout the bootstrap looks up by
   default — run this script from the app's data root and no configuration
   is needed.

Usage (any Python 3.12 env with network access):
    python verification/T1.1.1/scripts/fetch_doctr_weights.py
    python verification/T1.1.1/scripts/fetch_doctr_weights.py --dest <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import os
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
        default=None,
        help="target directory (default: ./models/detector, or the exact "
        "file NEWMANGA_DETECTOR_WEIGHTS points at)",
    )
    args = parser.parse_args()

    override = os.environ.get("NEWMANGA_DETECTOR_WEIGHTS")
    if override:
        target = Path(override)
    else:
        dest: Path = args.dest if args.dest is not None else Path("models/detector")
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
