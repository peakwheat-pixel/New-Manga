"""P09-MANAGED-READ-ROOT-TRUST-1 / AC5：复制 P09-AC3-DELETE-HARDEN-1 的 9 个探针。

AC5 要求前序 Task 的 9 个探针**不回归**。原始探针硬编码主仓库路径
（``G:\\CODEX\\New Manga``）与它自己的 agent-output scratch 目录；直接运行会
(a) 测到主仓库的代码而不是本 worktree，(b) 写到本 worktree 之外。

本脚本只在**副本**上做两类替换，探针逻辑一行不改：

1. ``G:\\CODEX\\New Manga``（源码根）→ 本 worktree 根；
2. ``G:\\CODEX\\New Manga.workspace\\agent-output\\coordinator\\<name>``
   （仓外 scratch）→ ``verification/P09-MANAGED-READ-ROOT-TRUST-1/_scratch/<name>``。

``n002-race-probe.py`` 用 ``__file__.parents[2] / "src"`` 定位源码，副本放在
``ac5-delete-probes/`` 下深度不同，因此额外把它替换成显式 worktree 路径。

输出：``ac5-delete-probes/<probe>`` 副本 + ``ac5-delete-probes/PATH-ADAPTATION.diff``
（与原件 unified diff，供 Review 核对"只改了路径"）。
"""

from __future__ import annotations

import difflib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO / "verification" / "P09-AC3-DELETE-HARDEN-1"
DEST_DIR = REPO / "verification" / "P09-MANAGED-READ-ROOT-TRUST-1" / "ac5-delete-probes"
SCRATCH = (
    REPO
    / "verification"
    / "P09-MANAGED-READ-ROOT-TRUST-1"
    / "_scratch"
)

PROBES = (
    "n002-race-probe.py",
    "n002-race-probe2.py",
    "n004-ancestor-probe.py",
    "n004-production-order-probe.py",
    "r5-p1-managed-remove-probe.py",
    "r5-p1-cleanup-book-files-probe.py",
    "r5b-p1-remove-managed-race-probe.py",
    "r5b-p1-collect-orphans-race-probe.py",
    "r6-p1a-publish-cleanup-race-probe.py",
)

WORKTREE = str(REPO)
MAIN_REPO = r"G:\CODEX\New Manga"
MAIN_SCRATCH = MAIN_REPO + r".workspace\agent-output\coordinator"
WT_PLACEHOLDER = "@@P09_WORKTREE@@"
SCRATCH_PLACEHOLDER = "@@P09_SCRATCH@@"


def adapt(text: str, probe: str) -> str:
    # Two-phase replacement: the destination paths themselves contain the
    # source-root prefix, so inserted paths go through placeholders to avoid
    # re-replacing them (first version of this script nested the prefix twice).
    text = text.replace(MAIN_SCRATCH, SCRATCH_PLACEHOLDER)
    text = text.replace(MAIN_SCRATCH.replace("\\", "/"), SCRATCH_PLACEHOLDER)
    if probe == "n002-race-probe.py":
        # This probe locates src via __file__.parents[2]; the copied file sits
        # one level deeper, so pin the worktree explicitly (same target).
        text = text.replace(
            'SRC = Path(__file__).resolve().parents[2] / "src"',
            f'SRC = Path(r"{WT_PLACEHOLDER}") / "src"',
        )
    text = text.replace(MAIN_REPO, WT_PLACEHOLDER)
    text = text.replace(MAIN_REPO.replace("\\", "/"), WT_PLACEHOLDER)
    text = text.replace(WT_PLACEHOLDER, WORKTREE)
    text = text.replace(SCRATCH_PLACEHOLDER, str(SCRATCH))
    return text


def main() -> int:
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    diffs = []
    for probe in PROBES:
        original = (SOURCE_DIR / probe).read_text(encoding="utf-8")
        adapted = adapt(original, probe)
        (DEST_DIR / probe).write_text(adapted, encoding="utf-8", newline="\n")
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            adapted.splitlines(keepends=True),
            fromfile=f"verification/P09-AC3-DELETE-HARDEN-1/{probe}",
            tofile=f"verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-delete-probes/{probe}",
        )
        diffs.extend(diff)
    (DEST_DIR / "PATH-ADAPTATION.diff").write_text("".join(diffs), encoding="utf-8")
    print(f"adapted {len(PROBES)} probes -> {DEST_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
