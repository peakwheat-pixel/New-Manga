# -*- coding: utf-8 -*-
"""Compare protected declarations between the pre-remediation and current parser.

Reads the old tool from the sibling Task worktree (read-only) and the current
tool, both against the real main repository.  Writes
``evidence/protection-delta.json`` and fails if any dropped declaration names an
existing path (i.e. if remediation lost real protection).
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = r"G:\CODEX\New Manga"
WS = r"G:\CODEX\New Manga.workspace"
OLD = (r"G:\CODEX\New Manga.workspace\worktrees"
       r"\WORKSPACE-CLEANUP-TOOL-HARDENING-1\tools\governance\clean_workspace.py")
NEW = os.path.join(MAIN, "..", "New Manga.workspace", "worktrees",
                   "WORKSPACE-DECLARATION-REMEDIATION-1", "tools",
                   "governance", "clean_workspace.py")
NEW = os.path.normpath(NEW)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect(module):
    index, scanned = module.scan_repo_declarations(MAIN, WS)
    rows = [{"raw": item.raw, "disposition": item.disposition,
             "file": item.source_file, "locator": item.locator,
             "normalized": item.normalized} for item in index.declarations]
    return rows, scanned, len(index.protected)


old_rows, old_scan, old_roots = collect(load(OLD, "old_cw"))
new_rows, new_scan, new_roots = collect(load(NEW, "new_cw"))
old_keys = {(r["file"], r["locator"], r["raw"]): r for r in old_rows}
new_keys = {(r["file"], r["locator"], r["raw"]) for r in new_rows}
dropped = [old_keys[key] for key in sorted(old_keys.keys() - new_keys)]
added = [r for r in new_rows
         if (r["file"], r["locator"], r["raw"]) not in old_keys]

problems = []
for item in dropped:
    raw = item["raw"].strip()
    absolute = os.path.isabs(raw) or (len(raw) > 2 and raw[1] == ":")
    path = raw if absolute else os.path.join(MAIN, raw.replace("/", os.sep))
    exists = os.path.exists(path)
    item["exists_as_a_path"] = exists
    if exists:
        problems.append(item)

report = {
    "old": {"declarations": old_scan["declarations"],
            "protected_roots": old_roots},
    "new": {"declarations": new_scan["declarations"],
            "protected_roots": new_roots},
    "dropped_declarations": dropped,
    "added_declarations": added,
    "dropped_that_exist_as_paths": problems,
    "verdict": ("OK: every dropped declaration is prose that does not exist as "
                "a path; no real protected identity was lost"
                if not problems else
                "FAIL: a dropped declaration names an existing path"),
}
target = os.path.join(HERE, "evidence", "protection-delta.json")
json.dump(report, open(target, "w", encoding="utf-8"), ensure_ascii=False,
          indent=2)
print(json.dumps({"old": report["old"], "new": report["new"],
                  "dropped": len(dropped), "verdict": report["verdict"]},
                 ensure_ascii=False, indent=1))
sys.exit(0 if not problems else 1)
