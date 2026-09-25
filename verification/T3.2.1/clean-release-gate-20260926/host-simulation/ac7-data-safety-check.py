# -*- coding: utf-8 -*-
"""AC7 data-safety read-only checks: fixture hash, managed copy, lock,
revision, manual-review state, export history, secret scan."""
import hashlib
import json
import os
import re
import sqlite3

ART = r"G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926"
DB = ART + r"\host-simulation-20260926-rerun1\用户配置隔离\AppData\Local\New Manga\library.db"
FIXTURE = ART + r"\host-simulation-20260926-rerun1\fixture\漫画页-测试.png"
EXPORT = ART + r"\host-simulation-20260926-rerun2\exports\recovery-chapter-1-original.zip"
LOG_DIRS = [
    ART + r"\host-simulation-20260926-rerun1\logs",
    ART + r"\host-simulation-20260926-rerun2\logs",
    ART + r"\host-simulation-20260926-rerun3\logs",
    ART + r"\cold-start-benchmark\logs",
    ART + r"\default-data-root-probe",
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

out = {}
out["fixture"] = {
    "path": FIXTURE,
    "sha256_now": sha256(FIXTURE),
    "sha256_expected": "05026a0531c0f053ec7d58db35849338c93ddd70edbf9185f354663567c16430",
}
out["fixture"]["unchanged"] = out["fixture"]["sha256_now"] == out["fixture"]["sha256_expected"]

con = sqlite3.connect("file:" + DB.replace("\\", "/") + "?mode=ro", uri=True)
cur = con.cursor()
pages = cur.execute("SELECT page_id, page_locked, review_state, overall_status, source_hash, managed_original_ref FROM pages").fetchall()
out["pages"] = [{"page_id": r[0], "page_locked": r[1], "review_state": r[2],
                 "overall_status": r[3], "source_hash": r[4], "managed_ref": r[5]} for r in pages]
managed = ART + r"\host-simulation-20260926-rerun1\用户配置隔离\AppData\Local\New Manga\managed"
mpath = os.path.join(managed, pages[0][5].replace("/", os.sep))
out["managed_copy"] = {"path": mpath, "exists": os.path.exists(mpath)}
if out["managed_copy"]["exists"]:
    out["managed_copy"]["sha256"] = sha256(mpath)
    out["managed_copy"]["matches_source_hash"] = out["managed_copy"]["sha256"] == pages[0][4]

out["revisions"] = {
    "artifact_revisions": cur.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0],
    "region_revisions": cur.execute("SELECT COUNT(*) FROM region_revisions").fetchone()[0],
}
out["export_history"] = [dict(zip([d[0] for d in cur.execute("SELECT * FROM export_history LIMIT 0").description], r))
                         for r in cur.execute("SELECT * FROM export_history").fetchall()]
con.close()

# Secret scan: credential-ish tokens must not appear in any captured log/diagnostic.
SECRET_PAT = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s|password|secret|sk-[a-z0-9]{8,})")
hits = []
for d in LOG_DIRS:
    if not os.path.isdir(d):
        continue
    for root, _dirs, files in os.walk(d):
        for name in files:
            p = os.path.join(root, name)
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in SECRET_PAT.finditer(text):
                ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                hits.append({"file": os.path.relpath(p, ART), "match": m.group(0), "context": ctx})
out["secret_scan"] = {"pattern": SECRET_PAT.pattern, "files_scanned_dirs": LOG_DIRS, "hits": hits,
                      "verdict": "NO_CREDENTIAL_MATERIAL_IN_LOGS" if not hits else "REVIEW_HITS"}

print(json.dumps(out, ensure_ascii=False, indent=1))
