# -*- coding: utf-8 -*-
"""AC2 manifest exclusion scan for Build 2 dist (read-only)."""
import json

P = r"G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\build2\dist\artifact-manifest.sha256"
lines = open(P, encoding="utf-8", errors="replace").read().splitlines()
print("total manifest lines:", len(lines))
paths = []
for ln in lines:
    parts = ln.split("  ", 1)
    if len(parts) == 2:
        paths.append(parts[1].strip().lstrip("*"))

bad_patterns = [
    "tests", "pytest", "venv", "virtualenv", ".git", "verification",
    "library.db", "managed/", "site-packages/pip", "setuptools", "wheel",
    "__pycache__", "conftest",
]
hits = {}
for pat in bad_patterns:
    m = [x for x in paths if pat in x.lower()]
    if m:
        hits[pat] = m[:5] + (["...total %d" % len(m)] if len(m) > 5 else [])
print(json.dumps(hits, indent=1, ensure_ascii=False))

abs_paths = [x for x in paths if (":" in x and "://" not in x)]
print("absolute-path entries:", len(abs_paths), abs_paths[:5])

tops = {}
for x in paths:
    t = x.replace("\\", "/").split("/")[0]
    tops[t] = tops.get(t, 0) + 1
print("top-level:", json.dumps(dict(sorted(tops.items(), key=lambda kv: -kv[1])), ensure_ascii=False, indent=1))
