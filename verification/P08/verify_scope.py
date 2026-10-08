"""Check P08 document coverage and scope; never run product tests."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "ab2f813c0ce311a6712002cafd852b9e7a258380"
TASK_STATES = {"proposed", "ready", "in_progress", "blocked", "in_review",
               "changes_requested", "approved", "done", "closed_with_limitations"}

if __name__ == "__main__":
    source = (ROOT / "doc/08_ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8")
    expected = re.findall(r"^## (AC-[A-Z0-9-]+)\s+", source, re.M)
    coverage = (HERE / "AC_COVERAGE.md").read_text(encoding="utf-8")
    actual = re.findall(r"^\| (AC-[A-Z0-9-]+) \|", coverage, re.M)
    assert actual == expected and len(set(actual)) == len(actual)
    rows = [line for line in coverage.splitlines() if line.startswith("| AC-") or line.startswith("| D08-")]
    gates = re.findall(r"^\| D08-GATE-(\d+) \|", coverage, re.M)
    assert sorted(map(int, gates)) == list(range(68, 80)), gates
    assert "| D08-AC-SMOKE |" in coverage
    assert len(rows) == len(expected) + 1 + 12
    assert all(line.endswith("| NOT_RUN |") for line in rows)
    print(f"PASS: {len(actual)} numbered D08 criteria, AC-SMOKE and all 12 §68–79 gates mapped; results remain NOT_RUN")
    handoffs = list((ROOT / "doc/handoffs").glob("P08-*.md"))
    for doc in list(HERE.glob("*.md")) + [ROOT / "doc/tasks/P08.md"] + handoffs:
        content = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>").split("#", 1)[0]
            # Review evidence may quote an elided target as an example, not a link.
            if target in {"…", "..."}:
                continue
            if target and "://" not in target:
                assert (doc.parent / target).is_file(), (doc, target)
    print("PASS: P08 local links resolve")
    task = (ROOT / "doc/tasks/P08.md").read_text(encoding="utf-8")
    protocol = (ROOT / "doc/09_COLLABORATION.md").read_text(encoding="utf-8")
    state_block = re.search(r"^状态：proposed.*?(?=^Task 的开发状态)", protocol, re.M | re.S)
    assert state_block, "task status definitions missing from collaboration protocol"
    protocol_states = set(re.findall(r"^- ([a-z_]+)：", state_block.group(0), re.M))
    assert protocol_states == TASK_STATES, (protocol_states, TASK_STATES)
    state = re.search(r"^status: ([a-z_]+)$", task, re.M)
    integration = re.search(r"^integration_commit: (null|[0-9a-f]{40})$", task, re.M)
    approval = re.search(r"^approval: ([a-z_]+)$", task, re.M)
    assert state and state.group(1) in TASK_STATES and integration and approval
    assert "reviewer: DeepSeek Harness" in task
    assert state.group(1) != "done" or integration.group(1) != "null"
    reviewed_head = re.search(r"^reviewed_head: ([0-9a-f]{40})$", task, re.M)
    assert reviewed_head, "P08 must record a full reviewed_head"
    expected_approval = ("user_scope_confirmed_review_approved"
                         if state.group(1) in {"approved", "done"}
                         else "user_scope_confirmed_review_pending")
    assert approval.group(1) == expected_approval, (approval.group(1), state.group(1))
    scope = (HERE / "SCOPE_DRAFT.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^\| D[1-7] \|", scope, re.M)) == 7
    for row in rows:
        if "[P0]" in row or "[P1]" in row:
            assert "INCLUDED" in row and "DEFERRED" not in row, row
    assert sum("DEFERRED" in row for row in rows) == 6
    assert "AC-REGION-001..004" in coverage and "AC-DOC-001/002/003" in coverage
    assert "ACG主题" in coverage and "Architecture Documentation Rebaseline Task" in coverage
    assert all("ZCode" in next(row for row in rows if row.startswith(f"| AC-WIN-00{i} |"))
               and "P12/P14/P15/P17" in next(row for row in rows if row.startswith(f"| AC-WIN-00{i} |"))
               for i in range(1, 7))
    for fmt in ("MOBI", "CBZ", "PDF", "TEXT"):
        assert f"P08-FMT-{fmt}" in scope
    print("PASS: all seven decisions recorded; all P0/P1 included, six P2 extensions deferred; extra formats mapped")
    plan = (ROOT / "doc/REBASELINE_PLAN.md").read_text(encoding="utf-8")
    assert f"| P08 | {state.group(1)} |" in plan
    assert len(re.findall(r"^\| P\d{2} \| proposed / 未释放 \|", plan, re.M)) == 20
    print(f"PASS: P08 {state.group(1)}, 20 successors/candidates unreleased; no fabricated approval")
    paths = ["src", "apps", "tests", "packaging", "doc/contracts", "doc/reviews",
             "AGENTS.md", "doc/09_COLLABORATION.md",
             "doc/01_FUNCTIONAL_ARCHITECTURE.md", "doc/02_TECHNICAL_ARCHITECTURE_.md",
             "doc/03_DATA_MODEL.md", "doc/04_USER_FLOW.md", "doc/05_UI_MAPPING.md",
             "doc/06_TRANSLATION_PIPELINE.md", "doc/07_NON_FUNCTIONAL_REQUIREMENTS.md",
             "doc/08_ACCEPTANCE_CRITERIA.md", "doc/13_ACCEPTANCE_TRACEABILITY.md",
             "doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md",
             "verification/PROJECT-ROADMAP-20261008/task-inventory.csv"]
    assert not subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE, "--", *paths]).strip()
    allowed_files = {
        "doc/tasks/P08.md", "doc/REBASELINE_PLAN.md", "doc/STATUS.md", "doc/00_INDEX.md",
        "doc/12_ROADMAP.md", "doc/tasks/README.md",
        "verification/PROJECT-ROADMAP-20261008/REPORT.md",
        "verification/PROJECT-ROADMAP-20261008/ROADMAP.md",
        "verification/PROJECT-ROADMAP-20261008/RESUME.md",
        "verification/PROJECT-ROADMAP-20261008/verify_plan.py",
    }
    handoff_prefix = "doc/handoffs/P08-"

    def allowed(path):
        return (path in allowed_files or path.startswith("verification/P08/")
                or (path.startswith(handoff_prefix) and path.endswith(".md")
                    and "/" not in path[len(handoff_prefix):]))

    assert allowed("verification/P08/review-example.md") and allowed("doc/handoffs/P08-r5.md")
    assert not allowed("doc/10_CURRENT_STATE_AND_GAPS.md")
    assert not allowed("doc/handoffs/P08/nested.md")
    assert not allowed("doc/handoffs/M2-x.md")
    assert not allowed("doc/reviews/x.md")
    # Check the fixed commit range without attributing pre-existing worktree dirt to P08.
    changed = subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only",
                                       "--no-renames", BASE, "HEAD"], text=True).splitlines()
    outside_scope = [path for path in changed if not allowed(path)]
    assert not outside_scope, f"committed P08 diff escapes allowed paths: {outside_scope}"
    print(f"PASS: committed BASE..HEAD diff is within P08 allowed paths ({len(changed)} files)")
    handoffs = sorted(path.relative_to(ROOT).as_posix()
                      for path in (ROOT / "doc/handoffs").glob("P08-*.md"))
    assert handoffs, "P08 Handoff scope must not be empty"
    checked = subprocess.run(["git", "-C", str(ROOT), "diff", "--check", BASE, "--",
                              "verification/P08", "doc/tasks/P08.md", "doc/REBASELINE_PLAN.md",
                              "doc/STATUS.md", "doc/00_INDEX.md", "doc/12_ROADMAP.md",
                              "doc/tasks/README.md", *handoffs,
                              "verification/PROJECT-ROADMAP-20261008"],
                             capture_output=True, text=True)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    print(f"PASS: frozen product docs unchanged; full P08 subtree/task governance diff is whitespace-clean ({len(handoffs)} Handoffs)")
    for name in ("REBASELINE_PLAN.md", "STATUS.md"):
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{BASE}:doc/{name}"]).decode("utf-8").replace("\r\n", "\n")
        new = (ROOT / "doc" / name).read_text(encoding="utf-8")
        marker = "## 2026-10-08 完成："
        assert old.split(marker, 1)[1] == new.split(marker, 1)[1], name
    print("PASS: zero production/contracts/Review/inventory changes; historical Plan/Status preserved")
    print("Product tests/build/GUI/model calls: NOT_RUN (document preparation only)")
