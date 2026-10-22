---
task_id: WORKSPACE-CONSOLIDATION-1
reviewer: Codex
author: dsh
base_commit: "3947d63447457fe3ef8d3587942e632724ab3d72"
reviewed_head: "8d24d4eafe798dd48045404843ca312f2aedc261"
decision: changes_requested
review_mode: read_only
---

## 结论

固定 HEAD 与指定分支一致。返修提交的差异仅有新增和修改，没有删除、重命名或 `tools/**` 改动；提交涉及的文件位于 Task 声明的范围内。

主要未解决项是：P03 隔离恢复演练记录使用了 `C:/Users/49745/AppData/Local/Temp/...` 下的临时 bare repository。该路径不在 Task 的允许路径内，也不符合项目将新临时产物放入 `G:\CODEX\New Manga.workspace\` 的规则。P03 bundle 对两个独有提交的保全证据成立，但这不能消除该范围偏离；其临时仓库的当前状态也未独立核实。基于此项，我不能给出批准结论。

Task 仍为 `in_review`；本审查没有更改状态，也不批准关闭。

## Findings

| ID | 级别 | 证据 | 最小处置建议 |
|---|---|---|---|
| F-01 | P2 | [P03 记录](<G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/p03-preservation-r208.md>)记载演练在系统 Temp 下创建 bare repository；Task 允许路径列于 [Task](<G:/CODEX/New Manga/doc/tasks/WORKSPACE-CONSOLIDATION-1.md>)，工作区临时产物规则见 [WORKSPACE_GOVERNANCE.md](<G:/CODEX/New Manga/doc/WORKSPACE_GOVERNANCE.md>)。该演练未在本轮重放，临时仓库现状未核实。 | 由 Codex 对该范围偏离及临时仓库状态作出记录和裁决。不要将删除或移动该路径视为已获授权。 |
| F-02 | P3 | 固定提交快照中 Task 一直显示 `in_review`；协作协议要求 changes requested 后回到 `in_progress` 再重新进入 `in_review`。Git 快照不能证明提交间是否发生过未提交的状态转换。 | 将状态转换历史列为未证实项，由 Codex 确认；本审查不改 Task 状态。 |
| F-03 | P3 | [findings-disposition-r208.md](<G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/findings-disposition-r208.md>)中“状态只有三种”与主表的 `FIXED/MAPPED/CORRECTED/...` 标签并存，读者可能无法区分主表状态和执行证据状态。另，ledger 的 `LOST_ORIGINAL: 0` 是报告级 availability 汇总，不是给 source 分配 `LOST` disposition，也未发现修改共享 Schema。 | 澄清“三种状态”仅指执行证据行；保持报告级汇总与 source disposition 的区别。 |
| F-04 | P3 | `git diff --check 3947..8d` 退出码为 2，在 [P03 记录](<G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/p03-preservation-r208.md>)的两行 bundle verify 输出发现尾随空格。 | 如这些空格用于忠实保留原始输出，采用可见标记或其他不会被 diff 检查判为尾随空格的表示。 |

## R208-01..08 核对

| 项 | 独立复核结论 |
|---|---|
| R208-01 | P03 tag 指向 `0a25ceb4577158d9dff184776ff4599e74e25c57`；tag 与 bundle 均覆盖独有提交 `112495c70ff8a9c50fe00f4cd2eaa861d9a11b69`、`0a25ceb4577158d9dff184776ff4599e74e25c57`。prerequisite `e3319990216699357c8b5a37c494010505535bb6` 存在且为 HEAD 祖先。bundle verify 成功，但输出要求该 prerequisite，因此已如实标为增量、非自包含。P03 保全足以证明这两个 Git 提交被保存；隔离恢复演练只核对了记录，没有在本轮重放，也没有核实系统 Temp 路径现状。 |
| R208-02/03 | [incident ledger JSON](<G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json>)包含 18 个 protected sources、15 个 removed roots；逐条所需字段齐全，15 条删除回执与原清理回执路径及字节数相符。六个 worktree 的记录仅支持“原路径与 HEAD 部分重建”，不支持原样复原。X6 capture 的现存副本与记录哈希匹配；三个 selftest payload 可在内存中精确重建字节，与记录哈希匹配；未证实内容另行标记。没有 source 被赋予 `LOST` disposition，也未修改 Schema。 |
| R208-04/06 | `tools/**` 未修改。范围偏离有登记；报告没有把 Review 当作写授权，且 Task 的 `allowed_paths` 未因 Review 扩大。P03 系统 Temp 写入是 F-01 所述的范围偏离。 |
| R208-05 | [REBASELINE_PLAN.md](<G:/CODEX/New Manga/doc/REBASELINE_PLAN.md>)、[STATUS.md](<G:/CODEX/New Manga/doc/STATUS.md>)、Task 与 [WORKTREE_SAFETY_INVENTORY.md](<G:/CODEX/New Manga/doc/WORKTREE_SAFETY_INVENTORY.md>)的更正与可核对证据相符。历史 Review、原清册和历史 pin 未被改写；Stage 8 是追加记录。AC1/2/3/6/7/9 均为 `PARTIAL`，没有虚标 `MET`。 |
| R208-07/08 | 关键数值复算一致，详见下表。`49.48 GiB` 是删除回执的逻辑字节总量，不代表物理净释放。task-env 总量和检测环境分别核算，没有混为一谈。 |

[findings-disposition-r208.md](<G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/findings-disposition-r208.md>)对 R208 各项均有回应。其主表状态为：01 `FIXED`（待审）、02 `MAPPED`（open）、03 `CORRECTED`、04 `NOT_FIXED`、05 `CORRECTED`、06 `ACKNOWLEDGED`、07 `PARTIAL`、08 `CORRECTED`。执行证据行使用 `executed`、`NOT_RUN`、`UNVERIFIED` 等状态，没有把缺失证据标为已执行。R208-01 的“FIXED”可支持提交保全这项狭义结论，不能据此视为整个 Task 已通过。

## 逐 AC 裁定

| AC | 裁定 | 依据 |
|---|---|---|
| AC1 | `PARTIAL` | 当前有 132 个 worktree；证据不足以证明全部历史资源完整。 |
| AC2 | `PARTIAL` | 台账和删除回执补齐了映射，但未知内容仍保持未证实。 |
| AC3 | `PARTIAL` | 六个 worktree 仅部分重建，不能称为原样恢复。 |
| AC4 | `MET`（有条件据实表述） | 分支 payload 证据成立；结论限于现存分支与记录覆盖范围。 |
| AC5 | `MET`（保留报告/回执限制） | 记录与回执可核对；不等于证明所有字节均可恢复。 |
| AC6 | `PARTIAL` | 仍有未证实资源与范围偏离待裁决。 |
| AC7 | `PARTIAL` | 修正后的 kept 口径与证据吻合，但不能提升为全部资源完整。 |
| AC8 | `MET`（限于 mainline 证据） | 当前证据支持其所述 mainline 状态，不外推到其他 refs 或文件。 |
| AC9 | `PARTIAL` | 清理与恢复差额仍未完全关闭。 |

## 本轮运行证据

### 提交与路径

- `git rev-parse HEAD`：退出码 `0`；结果为 `8d24d4eafe798dd48045404843ca312f2aedc261`。
- `git branch --show-current`：退出码 `0`；结果为 `antigravity/P09-AC3-DELETE-HARDEN-1`。
- `git diff --name-status 3947d63447457fe3ef8d3587942e632724ab3d72..8d24d4eafe798dd48045404843ca312f2aedc261`：退出码 `0`；4 个 `M`、9 个 `A`，无 `D/R`。
- `git diff -- tools/ 3947d63447457fe3ef8d3587942e632724ab3d72 8d24d4eafe798dd48045404843ca312f2aedc261`：无差异。
- `git diff --check 3947d63447457fe3ef8d3587942e632724ab3d72..8d24d4eafe798dd48045404843ca312f2aedc261`：退出码 `2`；报告 `p03-preservation-r208.md:80` 和 `:98` 两处尾随空格。
- 提交链依次为 `198a9e4`、`759e99c`、`ea5c6fd`、`8d24d4e`；最终 Task 的 `delivery_head` 指向 `ea5c6fd`，Handoff pin 与该指针的修正关系一致。

### P03 bundle 与 refs

- `git show-ref --verify refs/tags/archive/P03-review-prep-112495c7`：退出码 `0`，tag 指向 `0a25ceb...`。
- `git cat-file -t`：两个独有提交及 prerequisite 均为 `commit`。
- `git merge-base --is-ancestor e331999... HEAD`：退出码 `0`。
- `git rev-list --reverse e331999... ..refs/tags/archive/P03-review-prep-112495c7`：恰为 `112495c70...`、`0a25ceb45...`。
- `git bundle verify "G:/CODEX/New Manga.workspace/archive/bundles/P03-review-prep-112495c7.bundle"`：退出码 `0`；Git 输出包含 prerequisite `e331999...`，并确认 bundle 可用。bundle 为 4,391 bytes，SHA-256 为 `4c2aef444ab3974401dfe038c7cf26f289cb8dd370bfe6062dfb5d2d70fddbee`。
- 对当前 77 个 bundle 逐一执行 verify，均退出码 `0`。这验证了 Git bundle/ref 内容，不证明被删除的工作区文件完整。

### 资源数字与字节核对

- 当前 `git worktree list --porcelain`：132 个 worktree。
- 当前本地分支：93 个，其中相对当前 mainline HEAD 有 19 个未合并。
- 以固定 base 复算 archive manifest：76 项合计 1,223 个提交、去重 320 个；当前 77 个 archive refs 合计 1,225 个、去重 322 个，增量正是 `0a25ceb45` 与 `112495c70`。
- 删除回执合计 `53,129,852,873` bytes，即 `49.481031 GiB` 逻辑字节；不能据此声称物理磁盘净释放相同字节数。
- `G:/CODEX/New Manga.workspace/worktrees/` 下记录的 7 个移除路径中，4 个现存、3 个不存在。
- task-envs 递归核算：`3,880,296,828` bytes（约 3.61 GiB）；`M2-PROD-DETECT-ENV-1` 为 `138,129,041` bytes（131.73 MiB），二者边界清楚。
- X6 capture：`stdout.md` 32,426 bytes，SHA-256 `0109aed4fd474546eac28d1b1bfa88510285f1f367c0f157007f93e1886a3602`；`stderr.md` 0 bytes，SHA-256 为标准空文件哈希。
- 内存重建 selftest 字节并计算 SHA-256：`collision.bin` 5 bytes、`exclusive.bin` 1 byte、`partial-run.json` 93 bytes，三项均匹配 ledger。未写入重建文件。

### 治理检查

执行了用户指定命令：

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md
```

退出码 `0`，stderr 为空。原始输出：

```text
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\WORKSPACE-CONSOLIDATION-1.md
WARN: 存在 38 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3190 bytes / 25 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6251 bytes / 55 lines
Governance check: PASS (3 warnings)
```

前序记录的 4 条 warning 中，包含 R208 Review 文件未登记的 evidence-directory warning。当前 Task 已登记 `EV-R208-REVIEW`，证据 pin 哈希复算一致；本轮检查不再出现该 warning，所以由 4 条降至 3 条，剩余三条如原始输出所列。治理 `PASS` 只说明检查器规则通过，不代表资源完整或 Task 获批。

本轮未修改或创建文件，未运行 Git 写命令、测试、删除/移动、分支清理、历史改写、force、push、GC 或 prune。返修提交及当前 refs 未显示这些操作，但 Git 快照不能证明所有带外命令都未发生；我不把快照视作完整操作审计。

**建议下一步：**由 Codex 对 F-01 的系统 Temp 写入作范围裁决并记录，再由 Reviewer 复核；在此之前 Task 保持 `in_review`，不关闭。