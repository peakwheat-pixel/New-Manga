"""Validate this fixed planning snapshot; does not run product tests."""
import csv
import re
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "e4242ecd419eb0eea098d2f63b40f709aa5caeea"
TASK_STATES = {"proposed", "ready", "in_progress", "blocked", "in_review",
               "changes_requested", "approved", "done", "closed_with_limitations"}
STATUS_LABELS = {
    "proposed": "proposed / 未释放",
    "ready": "ready / 可启动",
    "in_progress": "in_progress / 执行中",
    "blocked": "blocked / 阻塞待解除",
    "in_review": "in_review / DSH Review复审中",
    "changes_requested": "changes_requested / DSH Review待修订",
    "approved": "approved / Review通过待Codex集成",
    "done": "done / DSH Review与Codex集成通过",
    "closed_with_limitations": "closed_with_limitations / 按限制收口",
}
assert set(STATUS_LABELS) == TASK_STATES


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


if __name__ == "__main__":
    print(f"Planning snapshot base={BASE}; live HEAD={git('rev-parse', 'HEAD')}")
    rows = list(csv.DictReader((HERE / "task-inventory.csv").open(encoding="utf-8-sig")))
    ids = {r["id"] for r in rows}
    assert len(rows) == len(ids) == 196, "snapshot node count/unique IDs drift"
    expected = dict(DONE_RECORDED=114, LEGACY_VERIFIED_COMPLETE=48,
                    LEGACY_DOC_ONLY=5, LEGACY_PARTIAL=9,
                    LEGACY_ARCHIVED_UNFINISHED=13, CLOSED_WITH_LIMITATIONS=1,
                    LEGACY_SUPERSEDED=6)
    assert dict(Counter(r["effective_state"] for r in rows)) == expected
    for r in rows:
        for dep in re.split(r"[;|]", r["depends_on"]):
            assert not dep.strip() or dep.strip() in ids, (r["id"], dep)
        if r["task_file"]:
            assert (ROOT / r["task_file"]).is_file(), r["task_file"]
    print("PASS: 196 unique nodes, all classifications and dependency references")
    new = [r for r in rows if r["architecture"] != "LEGACY"]
    assert len(new) == 105
    for r in new:
        commit = r["integration_full"]
        assert commit and r["ancestor_of_audit_head"] == "YES", r["id"]
        subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, BASE], check=True)
    print("PASS: 105 new architecture/governance integration records are audit-base ancestors")
    plan = (ROOT / "doc/REBASELINE_PLAN.md").read_text(encoding="utf-8")
    protocol = (ROOT / "doc/09_COLLABORATION.md").read_text(encoding="utf-8")
    state_block = re.search(r"^状态：proposed.*?(?=^Task 的开发状态)", protocol, re.M | re.S)
    assert state_block, "task status definitions missing from collaboration protocol"
    protocol_states = set(re.findall(r"^- ([a-z_]+)：", state_block.group(0), re.M))
    assert protocol_states == TASK_STATES, (protocol_states, TASK_STATES)
    current = plan.split("## 2026-10-08 完成：", 1)[0]
    plan_rows = re.findall(r"^\| (P\d{2}) \| ([^|]+) \|", current, re.M)
    allowed_plan_states = {STATUS_LABELS["proposed"]} | (TASK_STATES - {"proposed"})
    assert all(label.strip() in allowed_plan_states for _, label in plan_rows)
    nodes = [node for node, _ in plan_rows]
    assert len(nodes) == len(set(nodes)) == 21
    assert not set(nodes) & ids, "P roadmap IDs collide with historical snapshot"
    assert nodes == [f"P{i:02}" for i in range(1, 22)], "candidate numbering is not consecutive"
    task = (ROOT / "doc/tasks/P08.md").read_text(encoding="utf-8")
    task_state = re.search(r"^status: ([a-z_]+)$", task, re.M)
    assert task_state and task_state.group(1) in TASK_STATES
    assert f"| P08 | {task_state.group(1)} |" in plan
    assert len(re.findall(r"^\| P\d{2} \| proposed / 未释放 \|", plan, re.M)) == 20
    roadmap = (HERE / "ROADMAP.md").read_text(encoding="utf-8")
    diagram_nodes = re.findall(r'\["(P\d{2})<br/>([^<]+)', roadmap)
    assert {node for node, _ in diagram_nodes} == set(nodes)
    accepted_labels = set(STATUS_LABELS.values())
    assert all(label in accepted_labels for _, label in diagram_nodes)
    p08_label = STATUS_LABELS[task_state.group(1)]
    assert [label for node, label in diagram_nodes if node == "P08"] == [p08_label, p08_label]
    for diagram in re.findall(r"```mermaid\n(.*?)```", roadmap, re.S):
        edges = re.findall(r"^\s*([\w-]+)\s+(?:-->|-\.->|-\. .*?\.->)\s*([\w-]+)", diagram, re.M)
        graph = {}
        for a, b in edges:
            graph.setdefault(a, []).append(b)
        def visit(node, active, done):
            assert node not in active, f"diagram cycle: {node}"
            if node in done:
                return
            for child in graph.get(node, []):
                visit(child, active | {node}, done)
            done.add(node)
        done = set()
        for node in graph:
            visit(node, set(), done)
    print("PASS: 21 unique planned nodes and roadmap graphs have no dependency cycles")
    docs = list(HERE.glob("*.md")) + [ROOT / "doc" / n for n in
            ("REBASELINE_PLAN.md", "STATUS.md", "00_INDEX.md", "12_ROADMAP.md")]
    # Check local links in this delivery and only the new navigation sections.
    for doc in docs:
        source = doc.read_text(encoding="utf-8")
        if doc.parent == ROOT / "doc":
            source = source.split("## 2026-10-08 完成：", 1)[0] if doc.name in ("STATUS.md", "REBASELINE_PLAN.md") else source.split("当前无 Active/released Task。", 1)[0] if doc.name == "00_INDEX.md" else source.split("This file is", 1)[0]
        for target in re.findall(r"\]\(([^)]+)\)", source):
            target = target.strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            assert (doc.parent / target).is_file(), (str(doc), target)
    print("PASS: delivery/navigation local links resolve")
    changed = git("diff", "--name-only", BASE, "--", "src", "apps", "tests", "packaging")
    assert not changed, f"production/code paths changed: {changed}"
    subprocess.run(["git", "-C", str(ROOT), "diff", "--check", "--", "doc/REBASELINE_PLAN.md",
                    "doc/STATUS.md", "doc/00_INDEX.md", "doc/12_ROADMAP.md"], check=True)
    print("PASS: zero production/code delta; governance whitespace check")
    print("Product tests/build/GUI: NOT_RUN (planning-only)")
