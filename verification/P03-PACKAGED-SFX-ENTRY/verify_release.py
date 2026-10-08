"""Validate the live P03 release metadata and its assigned linked worktree."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = (ROOT / "doc/tasks/P03.md").read_text(encoding="utf-8")
PLAN = (ROOT / "doc/REBASELINE_PLAN.md").read_text(encoding="utf-8")
STATUS = (ROOT / "doc/STATUS.md").read_text(encoding="utf-8")
ROADMAP = (ROOT / "verification/PROJECT-ROADMAP-20261008/ROADMAP.md").read_text(encoding="utf-8")

LABELS = {
    "proposed": "proposed / 未释放",
    "ready": "ready / 可启动",
    "in_progress": "in_progress / 执行中",
    "blocked": "blocked / 阻塞待解除",
    "in_review": "in_review / DSH Review复审中",
    "changes_requested": "changes_requested / DSH Review待修订",
    "approved": "approved / Review通过待Codex集成",
    "done": "done / DSH Review与Codex集成通过",
}


def field(name: str) -> str:
    match = re.search(rf"^{re.escape(name)}: (.+)$", TASK, re.MULTILINE)
    assert match, f"P03 frontmatter missing {name}"
    return match.group(1).strip()


state = field("status")
assert state in LABELS, state
expected_label = LABELS[state]
assert re.search(rf"^\| P03 \| {re.escape(expected_label)} \|", PLAN, re.MULTILINE)
assert ROADMAP.count(f"P03<br/>{expected_label}") == 2
assert f"P03={state}" in STATUS.splitlines()[2]
assert "唯一Active/released Task" in STATUS.split("## 历史检查点", 1)[0]

deps = re.search(r"^depends_on: \[(.*)\]$", TASK, re.MULTILINE)
assert deps, "P03 dependency list missing"
for dependency in (item.strip() for item in deps.group(1).split(",")):
    dep_task = (ROOT / f"doc/tasks/{dependency}.md").read_text(encoding="utf-8")
    dep_state = re.search(r"^status: ([a-z_]+)$", dep_task, re.MULTILINE)
    integration = re.search(
        r"^(?:integration_commit|integration): .*\b[0-9a-f]{8,40}\b",
        dep_task,
        re.MULTILINE,
    )
    assert dep_state and dep_state.group(1) == "done", (dependency, dep_state)
    assert integration, (dependency, "missing integration commit")

branch = field("branch")
worktree = field("worktree").replace("/", "\\").casefold()
worktrees = subprocess.check_output(
    ["git", "-C", str(ROOT), "worktree", "list", "--porcelain"], text=True
)
blocks = [block for block in worktrees.split("\n\n") if block]
match = next((block for block in blocks if f"worktree {worktree}" in block.replace("/", "\\").casefold()), None)
assert match, f"assigned worktree is not registered: {worktree}"
assert f"branch refs/heads/{branch}" in match, match

base = field("base_commit")
owner_head = re.search(r"^HEAD (.+)$", match, re.MULTILINE)
assert owner_head, match
subprocess.run(
    ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", base, owner_head.group(1)],
    check=True,
)

print(
    f"PASS: P03 state={state}; dependencies done; roadmap links agree; "
    f"worktree={worktree}; owner_head={owner_head.group(1)}"
)
