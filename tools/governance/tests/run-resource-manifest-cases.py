# -*- coding: utf-8 -*-
"""Offline cases for external Resource Manifest support.

Case definitions live in fixtures/resource-manifest/cases.json (versioned data, not code).
Each case runs against the real checker inside a throwaway task under doc/tasks/, which is
removed in a finally block - nothing is committed, and no fixture Task is left behind.

Why the real tree instead of a synthetic repo root: the checker validates eleven fixed
governance files plus many doc/** cross-references, so a minimal synthetic tree produces
40+ unrelated errors that drown the signal. Inside the real tree any FAIL is attributable.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "resource-manifest", "cases.json")
TID = "ZZ-MANIFEST-FIXTURE"
TPATH = os.path.join(WT, "doc", "tasks", TID + ".md")
VDIR = os.path.join(WT, "verification", TID)

# A real commit and a real on-disk hash so evidence checks pass and cannot mask manifest results.
REAL_COMMIT = "bb3abad16fc16aa7fc263718e182304a7fd84344"
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


def subst(obj):
    """Replace the @TID@ token throughout a case definition."""
    if isinstance(obj, str):
        return obj.replace("@TID@", TID)
    if isinstance(obj, list):
        return [subst(x) for x in obj]
    if isinstance(obj, dict):
        return {k: subst(v) for k, v in obj.items()}
    return obj


def write_case(manifest, section):
    os.makedirs(VDIR, exist_ok=True)
    if manifest is not None:
        io.open(os.path.join(VDIR, "resource-manifest.json"), "w", encoding="utf-8").write(
            json.dumps(manifest, ensure_ascii=False, indent=2))
    io.open(TPATH, "w", encoding="utf-8").write(TASK_TMPL.format(
        tid=TID, commit=REAL_COMMIT, sha=AGENTS_SHA, section=section))


def run():
    r = subprocess.run(["pwsh", "-NoProfile", "-File",
                        os.path.join(WT, "tools", "governance", "check.ps1"),
                        "-TaskPath", TPATH],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WT)
    out = (r.stdout or "") + (r.stderr or "")
    fails = [l.strip()[6:] for l in out.split("\n") if l.strip().startswith("FAIL:")]
    summ = [l.strip() for l in out.split("\n") if "Governance check" in l]
    return (summ[0] if summ else "(none)"), fails


MANIFEST_KEYS = ("Manifest", "manifest", "Resource", "ALREADY_ABSENT", "NOT_APPLICABLE",
                 "closeout_counts")


def main():
    doc = json.load(io.open(FIXTURES, encoding="utf-8"))
    cases = subst(doc["cases"])
    results = []
    try:
        for c in cases:
            write_case(c["manifest"], c["section"])
            summary, fails = run()
            rel = [f for f in fails if any(k in f for k in MANIFEST_KEYS)]
            other = [f for f in fails if f not in rel]
            ok = (len(rel) > 0) == c["expect_manifest_fail"] and not other
            print("%-2s %2d %-40s %s" % ("OK" if ok else "XX", c["id"], c["name"], summary))
            for f in rel[:3]:
                print("        -> " + f[:150])
            if other:
                print("        !! unrelated failures: %s" % other[:2])
            results.append(ok)
    finally:
        if os.path.exists(TPATH):
            os.remove(TPATH)
        if os.path.exists(VDIR):
            shutil.rmtree(VDIR, ignore_errors=True)
        print("\ncleaned: task=%s dir=%s" % (not os.path.exists(TPATH), not os.path.exists(VDIR)))

    print("%d/%d cases behaved as expected" % (sum(results), len(results)))
    if os.path.exists(TPATH) or os.path.exists(VDIR):
        print("WARNING: fixture not fully cleaned")
        return 1
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
