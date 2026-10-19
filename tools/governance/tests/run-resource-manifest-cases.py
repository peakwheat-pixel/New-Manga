# -*- coding: utf-8 -*-
"""Offline cases for external Resource Manifest support.

Case definitions live in fixtures/resource-manifest/cases.json (versioned data, not code).

Isolation (r7 §2.4 and this task's prohibitions): the fixture Task is written to a system
temporary directory, NEVER to the repository's doc/tasks/. The checker's -TaskPath accepts any
path, so the real task tree is never touched. Only the referenced manifest lives under
verification/, because manifest references are resolved relative to the repo root; that
directory is created and removed per case.

Why the real tree rather than a synthetic repo root: the checker validates eleven fixed
governance files plus many doc/** cross-references, so a minimal synthetic tree yields 40+
unrelated errors that drown the signal.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "resource-manifest", "cases.json")
TID = "ZZ-MANIFEST-FIXTURE"
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
    if isinstance(obj, str):
        return obj.replace("@TID@", TID)
    if isinstance(obj, list):
        return [subst(x) for x in obj]
    if isinstance(obj, dict):
        return {k: subst(v) for k, v in obj.items()}
    return obj


def write_case(manifest, section, taskdir):
    os.makedirs(VDIR, exist_ok=True)
    mf = os.path.join(VDIR, "resource-manifest.json")
    if manifest is not None:
        io.open(mf, "w", encoding="utf-8").write(
            json.dumps(manifest, ensure_ascii=False, indent=2))
    elif os.path.exists(mf):
        os.remove(mf)
    tp = os.path.join(taskdir, TID + ".md")
    io.open(tp, "w", encoding="utf-8").write(TASK_TMPL.format(
        tid=TID, commit=REAL_COMMIT, sha=AGENTS_SHA, section=section))
    return tp


def run(tp):
    r = subprocess.run(["pwsh", "-NoProfile", "-File",
                        os.path.join(WT, "tools", "governance", "check.ps1"),
                        "-TaskPath", tp],
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
    taskdir = tempfile.mkdtemp(prefix="gov-manifest-cases-")
    results = []
    try:
        for c in cases:
            tp = write_case(c["manifest"], c["section"], taskdir)
            summary, fails = run(tp)
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
        shutil.rmtree(taskdir, ignore_errors=True)
        if os.path.exists(VDIR):
            shutil.rmtree(VDIR, ignore_errors=True)
        repo_task = os.path.join(WT, "doc", "tasks", TID + ".md")
        leaked = os.path.exists(repo_task)
        print("\ncleaned: tempdir=%s manifest=%s doc/tasks untouched=%s"
              % (not os.path.exists(taskdir), not os.path.exists(VDIR), not leaked))
        if leaked:
            os.remove(repo_task)
            print("  (removed a leaked fixture from doc/tasks/)")

    print("%d/%d cases behaved as expected" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
