# AC4 — 新建 worktree 的 6 个假错误：原因与最小绕过

**Task**: GOV-UNTRACKED-BACKLOG-1 · **面向**: 后续任何需要新建 linked worktree 的 Agent

这份文档存在的理由：本会话中三个 Task（`GOV-RESOURCE-MANIFEST-JSON-1`、
`P19-UI-MANIFEST-VIEW-1`、`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`）各撞一次同一堵墙，
每次都要从头推导「为什么新建的 worktree 治理检查全是红的」。

## 现象

在 `G:\CODEX\New Manga` 主 checkout 里 `check.ps1` 是 **PASS**。
用同一 HEAD 新建 linked worktree，立刻变成 **FAIL (6 errors)**：

```
FAIL: 缺少当前治理入口：doc/WORKSPACE_GOVERNANCE.md
FAIL: 失效的本地引用：AGENTS.md → doc/WORKSPACE_GOVERNANCE.md
FAIL: 失效的本地引用：doc\00_INDEX.md → WORKSPACE_GOVERNANCE.md
FAIL: 失效的本地引用：doc\00_INDEX.md → ../archive/history/2026-10-12/README.md
FAIL: 失效的本地引用：doc\00_INDEX.md → ../archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md
FAIL: 失效的本地引用：doc\AD-001_TARGET_DESKTOP_ARCHITECTURE.md → ../archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md
```

## 原因

worktree 只检出 **Git 追踪的文件**。下列文件在主 checkout 是**未入库**的，
因此在新 worktree 中**根本不存在**：

| 文件 | 主 checkout 状态 | 作用 |
|---|---|---|
| `doc/WORKSPACE_GOVERNANCE.md` | **untracked** | 检查器 11 个必需静态文件之一 |
| `archive/history/2026-10-12/README.md` | untracked | 被 `doc/00_INDEX.md` 引用 |
| `archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` | untracked | 被 `doc/00_INDEX.md` 与 `doc/AD-001_*.md` 各引用一次 |

**关键**：这 6 个错误与你的 Task **毫无关系**。它们是积压造成的环境缺陷，
不是你的改动引入的，**不要去修它们**。把 `doc/WORKSPACE_GOVERNANCE.md` 提交入库
会让主 checkout 的决策被一个临时 worktree 的需求绑架。

## 最小绕过：只复制 3 个文件

实测有效，复制后同一 worktree 立即 **PASS (1 warnings)**：

```powershell
$main = "G:\CODEX\New Manga"
$wt   = "<你的 worktree 路径>"
@(
  "doc/WORKSPACE_GOVERNANCE.md",
  "archive/history/2026-10-12/README.md",
  "archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md"
) | ForEach-Object {
  $src = Join-Path $main $_; $dst = Join-Path $wt $_
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  Copy-Item $src $dst -Force
}
```

**重要**：这 3 个文件是**镜像**，不是交付物。

- **不要 `git add`** 它们；
- **不要提交**它们；
- worktree 删除时它们随之消失，无需清理。

本会话早期我曾复制整个 `doc/` 与 `archive/`（33 个文件）来绕过同一问题。
**那是过度的**——只需 3 个。过度镜像会污染 `git status`，反而让人怀疑自己动了不该动的文件。

## 永远不要 stage 的东西

```gitignore-心理模型（非实际 .gitignore）
verification/**        # 1470 个 agent 运行产物，绝大多数无引用价值
.orchestrator/**       # 67 个协调器运行时状态
archive/history/**     # 19 个历史快照（部分被 doc 引用，但不入库）
CON                    # Windows 保留设备名
INTERRUPTED*           # 脚本 bug 产物（把路径写成文件名）
```

实际规则更简单：**`git add` 只加你明确写过的路径**，永远不要 `git add <目录>`。

本会话已因此犯过两次错：
- `git add doc/tasks/` 扫入 26 个无关未追踪文件（Round 18）；
- `git add doc/handoffs/` 扫入他人的 `P09-AC3-DELETE-1-antigravity.md`（Round 32）。

两次都靠 `git reset --mixed HEAD~1` 回退。

## 那 137 个被引用的文件

1591 项中有 **137** 项被已入库的 `doc/**/*.md` 引用（Task、Plan、Review、Handoff）。
它们**不得移动、删除或归档**——引用会断。其余 **1454** 项无引用，
但**无引用不等于可删**：AGENTS.md 要求在确认来源与归属之后才能处置。

本 Task 不做处置。处置是后续 Task 的事。

## 一句话总结

> 新建 worktree 看到 6 个红，先复制那 3 个文件；它们是环境镜像，不是你的交付物，
> 不要 stage，也不要试图修复主 checkout 的积压。
