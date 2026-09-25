# -*- coding: utf-8 -*-
"""R-007: content-level credential scan over the entire Build 2 package.

Scans every file under build2\\dist\\NewManga (2,475 entries) with the same
regex family used for the log-side scan in ac7-data-safety-check.py, reading
files as bytes so binary payloads are covered too. Match = a printable
credential-shaped token in raw bytes; every hit is printed with context for
human adjudication (expected benign class: PySide6/Qt sample strings).
"""
import hashlib
import json
import os
import re

DIST = (r"G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926"
        r"\build2\dist\NewManga")
PATTERNS = {
    "api_key": re.compile(rb"(?i)api[_-]?key"),
    "authorization": re.compile(rb"(?i)authorization"),
    "bearer": re.compile(rb"(?i)bearer\s"),
    "password": re.compile(rb"(?i)password"),
    "secret": re.compile(rb"(?i)secret"),
    "sk_token": re.compile(rb"sk-[A-Za-z0-9]{16,}"),
}

total_files = 0
total_bytes = 0
hits = []
by_pattern = {}
for root, _dirs, files in os.walk(DIST):
    for name in files:
        p = os.path.join(root, name)
        total_files += 1
        try:
            data = open(p, "rb").read()
        except OSError as e:
            hits.append({"file": os.path.relpath(p, DIST), "error": str(e)})
            continue
        total_bytes += len(data)
        for label, pat in PATTERNS.items():
            for m in pat.finditer(data):
                ctx = data[max(0, m.start() - 48):m.end() + 48]
                printable = "".join(chr(b) if 32 <= b < 127 else "." for b in ctx)
                rel = os.path.relpath(p, DIST)
                hits.append({"file": rel, "pattern": label, "context": printable})
                by_pattern[label] = by_pattern.get(label, 0) + 1

summary = {
    "package": DIST,
    "files_scanned": total_files,
    "bytes_scanned": total_bytes,
    "sha256_manifest_reference": "073B84F509685EFE636071DCA7794C2A45B0DBB2646E40A6C9E05FF2029D9608 (manifest covers the same file set)",
    "patterns": sorted(PATTERNS),
    "hit_counts_by_pattern": by_pattern,
    "hit_total": len(hits),
    "hits": hits,
    "method": "bytes-level scan of every packaged file (binary payloads included); each hit printed with 48-byte context for adjudication",
}
print(json.dumps(summary, ensure_ascii=False, indent=1))
