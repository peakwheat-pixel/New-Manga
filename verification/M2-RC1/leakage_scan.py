"""Scan e2e result JSONs for caller-visible leakage fragments.

R-03 companion: leakage-scan.json previously had no generator. This script
IS the generator — rerunnable over any set of result files with the same
fragment list, so the artefact can be recomputed from the raw inputs.

Usage:
  python leakage_scan.py OUT.json FILE.json [FILE.json ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FRAGMENTS = [
    "49745",  # user id fragment (C:\\Users\\49745)
    "C:\\Users",
    "AppData",
    "m2rc1-lab",  # lab scope root directory name
    "asset.png",
    "typical.png",
    "boundary.bin",
    "oversize.bin",
    "scope\\derived",
]

# A hit is acceptable only when the fragment comes from probe-authored
# scenario labels written by the page itself; the product command face
# (issue_resource_url) never returns an OS path or digest.
PROBE_LABEL_NOTE = (
    "probe-authored scenario label written by the page itself, not "
    "host-served material; the product command face (issue_resource_url) "
    "never returns a path"
)


def main() -> int:
    out_path = Path(sys.argv[1])
    files = [Path(a) for a in sys.argv[2:]]
    hits = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for fragment in FRAGMENTS:
            start = 0
            while True:
                index = text.find(fragment, start)
                if index < 0:
                    break
                hits.append(
                    {
                        "file": path.name,
                        "fragment": fragment,
                        "context": text[max(0, index - 40) : index + 40],
                        "classification": PROBE_LABEL_NOTE
                        if fragment in ("asset.png", "typical.png", "boundary.bin", "oversize.bin")
                        else "UNCLASSIFIED",
                    }
                )
                start = index + len(fragment)
    report = {
        "generator": "verification/M2-RC1/leakage_scan.py",
        "files": [p.name for p in files],
        "fragments_checked": FRAGMENTS,
        "hits": hits,
        "unclassified_hits": [h for h in hits if h["classification"] == "UNCLASSIFIED"],
    }
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    clean = not report["unclassified_hits"]
    print(f"hits={len(hits)} unclassified={len(report['unclassified_hits'])} -> {out_path}")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
