---
id: GOV-UNTRACKED-BACKLOG-1
title: 仓库未入库积压（1591 文件）的分类与边界化
kind: governance
governance_version: 2
status: in_review
approval: dsh_release_2026-10-20_measured_1591_files
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 6ee8c87b1
branch: GOV-UNTRACKED-BACKLOG-1
worktree: null
integration_commit: null
delivery_head: 60970cf9da4b2852aeaf5b64f0c9e80883189684
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

- [x] **AC1 构成与来源核实**：对 `git ls-files --others --exclude-standard` 的 1591 项按目录、来源 Task、生成方式分类；逐类给出数量与判断依据。不得只依据目录名推断归属。
- [x] **AC2 两个异常条目的处置**：对 `CON` 与长句名文件分别记录内容指纹、生成来源推断、是否被任何 Task/Review/evidence/pin 引用，并给出**保留 / 归档 / 不得删除**的结论与理由。对 `CON` 必须给出在 Windows 保留设备名下安全读取与保存的方法。
- [x] **AC3 引用关系核查**：核实 1591 项中哪些被当前 Plan / STATUS / Task / Review / Canonical Evidence pin 引用。**被引用者一律留在原路径**，不得移动或删除。
- [x] **AC4 边界化文档**：产出一份可由后来者直接使用的说明，至少覆盖：为什么新建 worktree 会看到 6 个无关错误、如何最小化绕过（镜像哪些文件）、哪些文件永远不要 stage。目标是让下次新建 worktree 不再需要重新推导。
- [x] **AC5 只读保护**：本 Task **不删除、不移动、不归档、不重命名**任何积压文件；不改 `.gitignore`、`.gitattributes` 或 `tools/governance/`。处置动作（若有）只以建议形式记录，由后续 Task 执行。
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

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| BACKLOG-AC1 | AC1 | `verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md` | `60970cf9d` | `a86b42336085345e0d27edf5664061aac53d4337caf98e0b23a80ca62d883e6a` | `CANONICAL` |
| BACKLOG-AC1-JSON | AC1 | `verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-inventory.json` | `60970cf9d` | `4ec0cf8b8f4fed0eb9169a00a3eb948c54cd52f6f07c4093bf30e2165efff1db` | `CANONICAL` |
| BACKLOG-AC2 | AC2 | `verification/GOV-UNTRACKED-BACKLOG-1/ac2-anomalous-entries.md` | `60970cf9d` | `9b8a87549371cd17a77812c7e1c80df1de067b2c2074c1ab7050a0fccb1f827b` | `CANONICAL` |
| BACKLOG-AC3 | AC3 | `verification/GOV-UNTRACKED-BACKLOG-1/ac3-references.json` | `60970cf9d` | `e4dd2cb52db29825d6e241cf4b1510f74e348eb30da6c7372a05cf30585df3dc` | `CANONICAL` |
| BACKLOG-AC4 | AC4 | `verification/GOV-UNTRACKED-BACKLOG-1/ac4-worktree-mirror-guide.md` | `60970cf9d` | `9611a6c0be6a9d91d58a060003f1338c51e7ef7aeb7561f23f3d1e36b50b8945` | `CANONICAL` |
| BACKLOG-HANDOFF | AC6 | `doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md` | `60970cf9d` | `bd978b7d2865dde1865260ce147fb4e71a9115a4e54680829701ff5d06eefed6` | `CANONICAL` |

## Resource Manifest

本 Task 不处置资源，只记录。交付时逐项登记盘点范围内的顶层目录与其保留结论；
`NOT_APPLICABLE` 需有核实依据。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| untracked backlog | `verification/`、`.orchestrator/`、`doc/`、`archive/` 下的 1591 个未入库文件 | `PRESERVE_UNKNOWN` | 原路径保留 | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | 本 Task 只读盘点，未删除/移动/归档任何一项；137 项被已入库文档引用，一律留原路径 |
| CON (reserved name) | `CON` | `PRESERVE_REFERENCED` | `CON` | `8241373a2cc3ac428786e92b23a5872952cf7635e8a5153cac660560c4ac8714` | 34778 bytes，SHA-256 8241373A2CC3AC428786E92B23A5872952CF7635E8A5153CAC660560C4AC8714；内容为真实 SFX 哈希清单，不得删除 |
| evidence dir | `verification/GOV-UNTRACKED-BACKLOG-1/` | `PRESERVE_REFERENCED` | `verification/GOV-UNTRACKED-BACKLOG-1/` | `9611a6c0be6a9d91d58a060003f1338c51e7ef7aeb7561f23f3d1e36b50b8945` | 6 份证据，均为本 Task AC 直接产物 |
| agent output | 仓外 agent-output，非本 Task 交付物 | `NOT_APPLICABLE` | — | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | 派发产物不入库 |

## Closeout Record

- 状态：`proposed`。尚未释放、无交付。
- 释放前置：由 Codex 确认范围冻结、登记真实 branch/worktree 与 base/head。
