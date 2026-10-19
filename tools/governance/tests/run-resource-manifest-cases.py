# -*- coding: utf-8 -*-
"""Offline cases for external Resource Manifest support.

Runs against the real worktree so unrelated reference checks stay clean; only the fixture
Task's Manifest section varies. The fixture Task is written under doc/tasks/, exercised,
and removed in a finally block - nothing is committed.

Canonical Evidence pins AGENTS.md with the real commit and the real on-disk hash, so the
evidence checks pass and any FAIL line is attributable to the manifest logic under test.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess

# Repo root is derived from this file, so the suite runs in any checkout or worktree.
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TID = "ZZ-MANIFEST-FIXTURE"
TPATH = os.path.join(WT, "doc", "tasks", TID + ".md")
VDIR = os.path.join(WT, "verification", TID)

REAL_COMMIT = "bb3abad16fc16aa7fc263718e182304a7fd84344"
MANIFEST_SHA = "0" * 64
AGENTS_SHA = hashlib.sha256(io.open(os.path.join(WT, "AGENTS.md"), "rb").read()).hexdigest()

TASK_TMPL = """---
id: {tid}
governance_version: 2
status: done
owner: fixture-owner
reviewer: fixture-reviewer
integration_commit: {commit}
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/{tid}-evidence
---

# {tid}

## Acceptance Criteria

- [x] AC1: fixture

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1 | AC1 | `AGENTS.md` | `{commit}` | `{sha}` | `CANONICAL` |

## Resource Manifest

{section}

## Closeout Record

- fixture closeout
"""


def base_manifest():
    return {
        "schema_version": 1,
        "task_id": TID,
        "generated_at": "2026-10-19",
        "generated_by": "fixture",
        "resources": [{
            "resource_type": "evidence",
            "source_path": "verification/%s/resource-manifest.json" % TID,
            "disposition": "PRESERVE_REFERENCED",
            "destination_path": "verification/%s/resource-manifest.json" % TID,
            "sha256": "c" * 64,
            "process_check": "read only"}],
        "closeout_counts": {"deleted": 0, "moved": 0, "migrated": 0, "archived": 0},
    }


def write_case(manifest, section):
    global MANIFEST_SHA
    os.makedirs(VDIR, exist_ok=True)
    if manifest is not None:
        io.open(os.path.join(VDIR, "resource-manifest.json"), "w", encoding="utf-8").write(
            json.dumps(manifest, ensure_ascii=False, indent=2))
    mf = os.path.join(VDIR, "resource-manifest.json")
    MANIFEST_SHA = hashlib.sha256(io.open(mf, "rb").read()).hexdigest()
    io.open(TPATH, "w", encoding="utf-8").write(TASK_TMPL.format(
        tid=TID, commit=REAL_COMMIT, sha=AGENTS_SHA, msha=MANIFEST_SHA, section=section))


def run():
    r = subprocess.run(["pwsh", "-NoProfile", "-File",
                        os.path.join(WT, "tools", "governance", "check.ps1"),
                        "-TaskPath", TPATH],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WT)
    out = (r.stdout or "") + (r.stderr or "")
    fails = [l.strip()[6:] for l in out.split("\n") if l.strip().startswith("FAIL:")]
    summ = [l.strip() for l in out.split("\n") if "Governance check" in l]
    return (summ[0] if summ else "(none)"), fails


def case(name, manifest, section, expect_manifest_fail):
    write_case(manifest, section)
    summary, fails = run()
    rel = [f for f in fails if any(k in f for k in
                                   ("Manifest", "manifest", "Resource", "ALREADY_ABSENT", "NOT_APPLICABLE", "closeout_counts"))]
    other = [f for f in fails if f not in rel]
    ok = (len(rel) > 0) == expect_manifest_fail and not other
    print("%-2s %-34s %s" % ("OK" if ok else "XX", name, summary))
    for f in rel[:3]:
        print("        -> " + f[:150])
    if other:
        print("        !! unrelated failures: %s" % other[:2])
    return ok


def main():
    R = "见 `verification/%s/resource-manifest.json`。" % TID
    results = []
    try:
        results.append(case("1 valid external reference", base_manifest(), R, False))
        results.append(case("2 referenced file missing", base_manifest(),
                            "见 `verification/%s/nope.json`。" % TID, True))
        results.append(case("3 traversal", base_manifest(), "见 `verification/../doc/x.json`。", True))
        results.append(case("4 env var", base_manifest(), "见 `%APPDATA%/r.json`。", True))
        results.append(case("5 outside verification/", base_manifest(), "见 `doc/x.json`。", True))
        results.append(case("6 two references", base_manifest(),
                            "见 `verification/%s/a.json` 与 `verification/%s/b.json`。" % (TID, TID), True))
        m = base_manifest(); m["task_id"] = "OTHER"
        results.append(case("7 task_id mismatch", m, R, True))
        m = base_manifest(); m["schema_version"] = 2
        results.append(case("8 schema_version != 1", m, R, True))
        m = base_manifest(); m["closeout_counts"]["deleted"] = 3
        # A declared count that exceeds the booleans in resources is NOT an error: the real
        # P19-UI-FIX-1 manifest declares moved=6 for six logs renamed inside its evidence dir,
        # none of which are listed resources. Failing on it would condemn an accurate record.
        results.append(case("9 declared count != resources (allowed)", m, R, False))
        m = base_manifest(); m["resources"] = []
        results.append(case("10 empty resources", m, R, True))
        m = base_manifest(); m["resources"][0]["disposition"] = "BOGUS"
        results.append(case("11 invalid disposition", m, R, True))

        abs_ok = base_manifest()
        abs_ok["resources"] = [{
            "resource_type": "cache", "source_path": "C:/definitely/not/here-cache",
            "disposition": "ALREADY_ABSENT", "destination_path": "C:/definitely/not/here-cache",
            "process_check": "no references remain", "absent_evidence": "Test-Path false; no refs"}]
        results.append(case("12 ALREADY_ABSENT all conditions", abs_ok, R, False))

        b = json.loads(json.dumps(abs_ok)); b["resources"][0]["absent_evidence"] = ""
        results.append(case("13 ALREADY_ABSENT no evidence", b, R, True))
        b = json.loads(json.dumps(abs_ok))
        b["resources"][0]["source_path"] = "verification/%s/resource-manifest.json" % TID
        b["resources"][0]["destination_path"] = "verification/%s/resource-manifest.json" % TID
        results.append(case("14 ALREADY_ABSENT but exists", b, R, True))
        na = base_manifest(); na["resources"][0]["disposition"] = "NOT_APPLICABLE"
        na["resources"][0]["absent_evidence"] = "gone"
        results.append(case("15 NOT_APPLICABLE for vanished", na, R, True))
        b = json.loads(json.dumps(abs_ok)); b["resources"][0]["process_check"] = ""
        results.append(case("16 missing process_check", b, R, True))
    finally:
        if os.path.exists(TPATH):
            os.remove(TPATH)
        if os.path.exists(VDIR):
            shutil.rmtree(VDIR, ignore_errors=True)
        print("\ncleaned: task=%s dir=%s" % (not os.path.exists(TPATH), not os.path.exists(VDIR)))

    print("%d/%d cases behaved as expected" % (sum(results), len(results)))


if __name__ == "__main__":
    main()
