---
id: GOV-UNTRACKED-BACKLOG-1
title: 仓库未入库积压（1591 文件）的分类与边界化
kind: governance
governance_version: 2
status: ready
approval: dsh_release_2026-10-20_measured_1591_files
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 6ee8c87b1
branch: GOV-UNTRACKED-BACKLOG-1
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-UNTRACKED-BACKLOG-1
allowed_paths:
  - doc/tasks/GOV-UNTRACKED-BACKLOG-1.md
  - verification/GOV-UNTRACKED-BACKLOG-1/
  - doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md
  - doc/reviews/GOV-UNTRACKED-BACKLOG-1-*.md
---

# GOV-UNTRACKED-BACKLOG-1：仓库未入库积压的分类与边界化

## 来源与目标

主 checkout `G:\CODEX\New Manga` 长期积累~~1233~~ **1591** 个未入库文件。它们已经造成
可复现的实际损害：

**每次新建 linked worktree，治理检查器都会报出 6 个与本 Task 无关的错误**——
因为 worktree 看不到这些未入库文件，而 `tools/governance/check.ps1` 需要
`doc/00_INDEX.md`、`doc/WORKSPACE_GOVERNANCE.md` 等文件存在。本会话中
`GOV-RESOURCE-MANIFEST-JSON-1`、`P19-UI-MANIFEST-VIEW-1`、
`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` 三个 Task 各撞一次，每次都要手工镜像 33 个文件
才能让检查器跑通。

本 Task 的目标**不是清空积压**，而是让它**被记录、被分类、被边界化**，
使后来者不必每次重新踩坑。

## 实测构成（DSH，2026-10-20）

| 目录 | 文件数 | 占比 |
|---|---:|---:|
| `verification/P02` | **1072** | 67% |
| `verification/P22` | 69 | 4% |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 60 | 4% |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 39 | 2% |
| `verification/P04` | 38 | 2% |
| `verification/P02-NEW-TIME-BASELINE` | 33 | 2% |
| **`verification/` 合计** | **1470** | **92%** |
| `.orchestrator/` | 67 | 4% |
| `doc/` | 32 | 2% |
| `archive/` | 19 | 1% |
| 其它 | 3 | <1% |

`git status --porcelain` 只显示 1235 **条目**，因为 Git 把目录折叠成一条；
`git ls-files --others --exclude-standard` 才是真实的 **1591 文件**。先前流传的「1233」
既不是条目数也不是文件数。

## 两个必须单独处理的异常条目

### 1. `CON`（34778 bytes，2026-10-13 创建）

内容是一个 CSV 哈希清单：

```
"Path","Hash"
"G:\CODEX\sfx_review\final_sfx_list.csv","942B48C2..."
"G:\CODEX\sfx_review\gain_sheet_01_clean.png","73AA02FE..."
...（约 300 行，指向 G:\CODEX\sfx_review\ 下的文件）
```

**文件名 `CON` 是 Windows 保留设备名**，是脚本把空变量当作重定向目标的产物。
内容本身是 SFX review 的真实哈希清单，**可能有证据价值，不得因文件名畸形而丢弃**。

### 2. `INTERRUPTED by Codex before final report; no exit marker; partial JSONL preserved; not Review evidence`（72 bytes）

内容只有一行：

```
verification/P02/dsh-appcontainer-contract-r3-review-attempt1.status.txt
```

即某个脚本把一个**路径参数**当成了**输出文件名**。纯 bug 产物，无独立内容。

## Acceptance Criteria

- [ ] **AC1 构成与来源核实**：对 `git ls-files --others --exclude-standard` 的 1591 项按目录、来源 Task、生成方式分类；逐类给出数量与判断依据。不得只依据目录名推断归属。
- [ ] **AC2 两个异常条目的处置**：对 `CON` 与长句名文件分别记录内容指纹、生成来源推断、是否被任何 Task/Review/evidence/pin 引用，并给出**保留 / 归档 / 不得删除**的结论与理由。对 `CON` 必须给出在 Windows 保留设备名下安全读取与保存的方法。
- [ ] **AC3 引用关系核查**：核实 1591 项中哪些被当前 Plan / STATUS / Task / Review / Canonical Evidence pin 引用。**被引用者一律留在原路径**，不得移动或删除。
- [ ] **AC4 边界化文档**：产出一份可由后来者直接使用的说明，至少覆盖：为什么新建 worktree 会看到 6 个无关错误、如何最小化绕过（镜像哪些文件）、哪些文件永远不要 stage。目标是让下次新建 worktree 不再需要重新推导。
- [ ] **AC5 只读保护**：本 Task **不删除、不移动、不归档、不重命名**任何积压文件；不改 `.gitignore`、`.gitattributes` 或 `tools/governance/`。处置动作（若有）只以建议形式记录，由后续 Task 执行。
- [ ] **AC6 交付与 Review**：入库分类矩阵与来源 commit/hash；生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。

## 允许修改范围

- `verification/GOV-UNTRACKED-BACKLOG-1/`：分类矩阵、引用核查、运行输出。
- 本 Task 自身文件、Handoff、Review，以及 Codex 管理的 Plan/STATUS 指针元数据。

## 禁止事项

- 不删除、不移动、不归档、不重命名任何积压文件。
- 不改 `.gitignore` / `.gitattributes` / `tools/governance/`。
- 不 stage 任何积压文件（`git add` 只允许本 Task 自己的路径）。
- 不把「未入库」写成「不存在」或「可删除」。
- 不改其它 Task 的 AC、pin 或 evidence。

## 测试与验证

本 Task 为只读盘点，不运行产品测试。验证方式：
`git ls-files --others --exclude-standard | wc -l` 前后一致（1591）；
`pwsh -NoProfile -File tools/governance/check.ps1` 保持 PASS；
逐条引用核查给出可复跑命令。

## Canonical Evidence

交付时登记：分类矩阵、引用核查表、两个异常条目的指纹与结论、Handoff、Review、checker 输出。
每项记录仓库相对路径、含文件 commit、SHA-256、class。

## Resource Manifest

本 Task 不处置资源，只记录。交付时逐项登记盘点范围内的顶层目录与其保留结论；
`NOT_APPLICABLE` 需有核实依据。

## Closeout Record

- 状态：`proposed`。尚未释放、无交付。
- 释放前置：由 Codex 确认范围冻结、登记真实 branch/worktree 与 base/head。
