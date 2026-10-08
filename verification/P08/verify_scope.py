"""Check P08 document coverage and scope; never run product tests."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "ab2f813c0ce311a6712002cafd852b9e7a258380"

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
    for doc in list(HERE.glob("*.md")) + [ROOT / "doc/tasks/P08.md"]:
        content = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>").split("#", 1)[0]
            if target and "://" not in target:
                assert (doc.parent / target).is_file(), (doc, target)
    print("PASS: P08 local links resolve")
    task = (ROOT / "doc/tasks/P08.md").read_text(encoding="utf-8")
    state = re.search(r"^status: (changes_requested|in_review)$", task, re.M)
    assert state and "integration_commit: null" in task and "reviewer: DeepSeek Harness" in task
    assert "reviewed_head: 490f9bd9637de0812a3ef3d9bbfa754868d5c15f" in task
    assert "approval: user_scope_confirmed_review_pending" in task
    scope = (HERE / "SCOPE_DRAFT.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^\| D[1-7] \|", scope, re.M)) == 7
    for row in rows:
        if "[P0]" in row or "[P1]" in row:
            assert "INCLUDED" in row and "DEFERRED" not in row, row
    assert sum("DEFERRED" in row for row in rows) == 6
    for fmt in ("MOBI", "CBZ", "PDF", "TEXT"):
        assert f"P08-FMT-{fmt}" in scope
    print("PASS: all seven decisions recorded; all P0/P1 included, six P2 extensions deferred; extra formats mapped")
    plan = (ROOT / "doc/REBASELINE_PLAN.md").read_text(encoding="utf-8")
    assert f"| P08 | {state.group(1)} |" in plan
    assert len(re.findall(r"^\| P\d{2} \| proposed / 未释放 \|", plan, re.M)) == 20
    print(f"PASS: P08 {state.group(1)}, 20 successors/candidates unreleased; no fabricated approval")
    paths = ["src", "apps", "tests", "packaging", "doc/contracts", "doc/reviews",
             "verification/PROJECT-ROADMAP-20261008/task-inventory.csv"]
    assert not subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE, "--", *paths]).strip()
    for name in ("REBASELINE_PLAN.md", "STATUS.md"):
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{BASE}:doc/{name}"]).decode("utf-8").replace("\r\n", "\n")
        new = (ROOT / "doc" / name).read_text(encoding="utf-8")
        marker = "## 2026-10-08 完成："
        assert old.split(marker, 1)[1] == new.split(marker, 1)[1], name
    print("PASS: zero production/contracts/Review/inventory changes; historical Plan/Status preserved")
    print("Product tests/build/GUI/model calls: NOT_RUN (document preparation only)")
