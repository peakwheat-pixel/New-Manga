"""TASK-045 AC ⑤ (F-13 / F-14) check: comments must match the implementation.

F-13 (TASK-042 review): the module used to claim ``setClipRect`` bounded peak
memory to one tile, contradicting the repo's own finding that the Qt handler
allocates the whole image first. TASK-042 removed Qt from the module entirely;
this script pins that the claim is gone and the root cause is stated instead.

F-14: the cache key used to be described as containing a "source hash" while it
was path + size + geometry. It now really is content-addressed; this script
pins both the wording and the code path.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGING = REPO_ROOT / "src" / "infrastructure" / "imaging"
TILES = IMAGING / "webtoon_tiles.py"

print("== F-13: the setClipRect claim ==")
offenders: list[str] = []
for path in sorted(IMAGING.rglob("*.py")):
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "setClipRect" in line:
            offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
print("  occurrences of setClipRect under src/infrastructure/imaging:",
      len(offenders))
for entry in offenders:
    print("   ", entry)
assert not offenders, "the setClipRect claim must not come back"

module_doc = TILES.read_text(encoding="utf-8").split('"""')[1]
root_cause = [line for line in module_doc.splitlines() if "whole image" in line]
print("  module docstring states the whole-image root cause:", bool(root_cause))
for line in root_cause:
    print("    ", line.strip())
assert root_cause

print()
print("== R-002: the 'at most one rewind' claim ==")
#: The class docstring must not repeat the retracted claim; the measured
#: wording lives in the same docstring (R-002, TASK-045 revision).
forbidden = "at most one rewind"
hits = [
    f"{path.relative_to(REPO_ROOT)}:{number}"
    for path in sorted(IMAGING.rglob("*.py"))
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
    if forbidden in line.lower()
]
print(f"  occurrences of {forbidden!r} under src/infrastructure/imaging:", len(hits))
for entry in hits:
    print("   ", entry)
assert not hits, "the retracted 'at most one rewind' claim returned"

source = TILES.read_text(encoding="utf-8")
class_doc = source.split("class TiledPageRasterizer:")[1].split('"""')[1]
print("  TiledPageRasterizer docstring mentions both terms:",
      "rewind" in class_doc.lower() and "overlap" in class_doc.lower())
assert "rewind" in class_doc.lower() and "overlap" in class_doc.lower()
for line in class_doc.strip().splitlines():
    if "rewind" in line.lower() or "overlap" in line.lower():
        print("    ", line.strip())

print()
print("== F-14: the cache key ==")
source = TILES.read_text(encoding="utf-8")
key_doc = source.split("def _cache_key")[1].split('"""')[1]
print("  _cache_key docstring:")
for line in key_doc.strip().splitlines():
    print("    ", line.strip())
assert "content-addressed" in key_doc.lower()
assert "source hash" not in key_doc, "the stale 'source hash' wording returned"
assert "self._source_digest" in source, "the digest must come from the source bytes"
assert "hashlib.sha256(source_bytes)" in source, "the digest must hash the content"
print("  digest source: hashlib.sha256 over the resident source bytes")
print("  format marker :", re.search(r'_TILE_CACHE_FORMAT = "([^"]+)"', source).group(1))
print()
print("OK: comments and implementation agree")
