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
    assert "status: blocked" in task and "integration_commit: null" in task and "reviewer: null" in task
    assert "P09正式Book/Chapter写链" not in task
    plan = (ROOT / "doc/REBASELINE_PLAN.md").read_text(encoding="utf-8")
    assert "| P08 | blocked |" in plan
    assert len(re.findall(r"^\| P\d{2} \| proposed / 未释放 \|", plan, re.M)) == 20
    print("PASS: P08 blocked, 20 successors/candidates unreleased; no fabricated approval")
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
