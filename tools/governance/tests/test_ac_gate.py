# -*- coding: utf-8 -*-
"""AC4 for GOV-AC-GATE-1: fixture test for the v3 AC gate.

Fixtures live in the system temp dir, never in doc/tasks/.
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

REPO = r"G:\CODEX\New Manga"
CHECK = os.path.join(REPO, "tools", "governance", "check.ps1")
EVID_REL = "verification/GOV-AC-GATE-1/fixture-evidence.md"

BASE_FM = """---
id: {tid}
title: fixture
kind: governance
governance_version: 3
status: {status}
approval: fixture
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: 071fb2158
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-AC-GATE-1
allowed_paths:
  - verification/GOV-AC-GATE-1/
---

# fixture {tid}

## Acceptance Criteria

{acs}

## 允许修改范围

无。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E1 | AC1 | `{evid}` | `071fb2158` | `{sha}` | `CANONICAL` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/{tid}.md` | fixture |

## Closeout Record

- fixture
"""

CASES = [
    ("F1_all_met",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [x] **AC2 乙**：文本。 <<MET>>",
     "PASS", "in_review"),
    ("F2_unticked_no_marker",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [ ] **AC2 乙**：文本没有标记",
     "FAIL", "in_review"),
    ("F3_blocked_with_reason",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [ ] **AC2 乙**：文本。 <<BLOCKED: 无头环境无法弹窗>>",
     "PASS", "in_review"),
    ("F4_checked_but_blocked",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [x] **AC2 乙**：文本。 <<BLOCKED: 无头环境>>",
     "FAIL", "in_review"),
    ("F5_met_with_reason",
     "- [x] **AC1 甲**：文本。 <<MET: 因为跑过了>>\n- [x] **AC2 乙**：文本。 <<MET>>",
     "FAIL", "in_review"),
    ("F6_blocked_without_reason",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [ ] **AC2 乙**：文本。 <<BLOCKED>>",
     "FAIL", "in_review"),
    ("F7_not_applicable_with_reason",
     "- [x] **AC1 甲**：文本。 <<MET>>\n- [x] **AC2 乙**：文本。 <<NOT_APPLICABLE: 本 Task 无数据面>>",
     "PASS", "in_review"),
    ("F8_in_progress_no_gate",
     "- [ ] **AC1 甲**：文本没有标记",
     "PASS", "in_progress"),
    ("F9_done_unticked_met",
     "- [ ] **AC1 甲**：文本。 <<MET>>",
     "FAIL", "done"),
]


def sha_of(rel):
    return hashlib.sha256(io.open(os.path.join(REPO, rel.replace("/", os.sep)), "rb").read()).hexdigest()


def main():
    ev = os.path.join(REPO, EVID_REL.replace("/", os.sep))
    if not os.path.exists(ev):
        os.makedirs(os.path.dirname(ev), exist_ok=True)
        io.open(ev, "w", encoding="utf-8", newline="\n").write(
            "# GOV-AC-GATE-1 fixture evidence\n\n由 AC4 夹具测试引用的占位证据文件。\n")
    sha = sha_of(EVID_REL)

    tmp = tempfile.mkdtemp(prefix="acgate-")
    before = set(os.listdir(os.path.join(REPO, "doc", "tasks")))
    results = []
    try:
        for name, acs, expected, status in CASES:
            tid = "FIXTURE-" + name.upper().replace("_", "-")
            p = os.path.join(tmp, tid + ".md")
            io.open(p, "w", encoding="utf-8", newline="\n").write(
                BASE_FM.format(tid=tid, status=status, acs=acs, evid=EVID_REL, sha=sha))
            r = subprocess.run(["pwsh", "-NoProfile", "-File", CHECK, "-TaskPath", p],
                               capture_output=True, text=True, encoding="utf-8", cwd=REPO)
            out = (r.stdout or "") + (r.stderr or "")
            all_errs = [l.strip() for l in out.split("\n") if "FAIL:" in l]
            # Only judge errors produced by the AC gate (SS4.3). Fixtures necessarily
            # trip unrelated rules - DAG registration, evidence commits - because they
            # are not real repo tasks. Isolating the gate's own output is what makes
            # this a unit test of the gate rather than an integration test of everything.
            gate_errs = [e for e in all_errs
                         if ("AC " in e) or ("AC 标记" in e) or ("AC 状态" in e)
                         or ("AC1" in e) or ("AC2" in e) or ("未找到任何 AC" in e)]
            got = "FAIL" if gate_errs else "PASS"
            errs = gate_errs or all_errs
            results.append((name, expected, got, errs))
    finally:
        after = set(os.listdir(os.path.join(REPO, "doc", "tasks")))
        shutil.rmtree(tmp, ignore_errors=True)
        assert before == after, "doc/tasks was touched by the fixture run"

    ok = 0
    print("%-32s %-7s %-7s %s" % ("case", "expect", "got", "result"))
    print("-" * 78)
    for name, exp, got, errs in results:
        good = exp == got
        ok += good
        print("%-32s %-7s %-7s %s" % (name, exp, got, "OK" if good else "*** MISMATCH ***"))
        for e in errs[:2]:
            print("      %s" % e[:110])
    print("-" * 78)
    print("%d/%d cases behaved as specified" % (ok, len(results)))
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
