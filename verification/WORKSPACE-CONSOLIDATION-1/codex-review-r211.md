---
task_id: WORKSPACE-CONSOLIDATION-1
reviewer: Codex
author: dsh
base_commit: abba2b0c580bbf6c2190ed10d129c263bf39cf20
reviewed_head: abba2b0c580bbf6c2190ed10d129c263bf39cf20
decision: changes_requested
review_mode: read_only
---

# 结论

**暂不批准关闭。** R211 对限时恢复搜索及残余风险的记录总体诚实，用户对 `closed_with_limitations` 的接受也足以作为残余风险裁决。但当前 Resource Manifest 漏列仍存在的 P03 系统 Temp scratch；因此 `resource_closeout_status: complete` 尚无充分依据。

本轮没有修改 Task 状态，也没有授权 Owner 关闭 Task。

## Findings

| ID | 级别 | 证据 | 最小处置建议 |
|---|---|---|---|
| R211-01 | High | [closure-package-r211.md](</G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/closure-package-r211.md>) 的 L8 记录 P03 Temp bare repo 仍存在，但 Task 当前 Resource Manifest 未列出该目录。治理脚本只校验已列出的行，不会发现漏列资源。 | 在 Resource Manifest 加入该 scratch，记录其现存路径、保留 disposition 和证据；继续原位保留，不删除或移动。之后再评估 `resource_closeout_status: complete`。 |
| R211-02 | Medium | [TASK_LEDGER.md](</G:/CODEX/New Manga/doc/TASK_LEDGER.md>) 的总数 `322 task files / 39 non-terminal` 与当前摘要相符；但其 tracked/untracked 子计数与此前对 Git 树及工作区的核验不一致。 | 关闭前用项目规定的生成器重建 Ledger，核对关闭后的总数与子计数；预计非终态总数会随本 Task 关闭而变化。 |
| R211-03 | Low | [WORKSPACE-CLEANUP-TOOL-HARDENING-1.md](</G:/CODEX/New Manga/doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md>) 的 `allowed_paths` 限于五个 tools 脚本、evidence_dir 和自身；状态为 `proposed`、`approval: pending_user_release`，未释放。该文件不在父 Task 原 `allowed_paths` 内。 | 保持 proposed、不实施。Codex 应另行冻结范围并按 Plan/Status 流程登记释放；父 Task 关闭不能代替该步骤。 |
| R211-04 | Low | [recovery-search-r211.md](</G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/recovery-search-r211.md>) 描述了搜索范围与结果，但没有附原始枚举、回收站 `$I` 解析和 USN 输出，独立重放能力有限。 | 将其保留为已披露的证据限制；不得把 `NOT_FOUND` 推断成永久不可恢复。 |

## Standards

- R211 的 Resource Manifest 行在机械格式上均符合要求：6 列、disposition 合法；已列出的保留类目的 destination 存在，integrity 指向现存 manifest 或匹配的 SHA-256。P03 bundle 的 SHA-256 与 pin 匹配。
- **机械校验通过不等于资源清册完整。** P03 Temp scratch 未列入清册，故不能据现有行批准资源关闭完整。
- R208 原表留在历史附录；未发现新增 `LOST` disposition 或 Schema 修改。
- 新 proposed Task 的自身范围准确，且保持未释放；但需由 Codex 另行冻结、登记。

## Spec

### 1. 恢复搜索、限制与用户裁决

恢复搜索明确限定在 5 个卷的目录名枚举、回收站、VSS 和 USN；记录 G: 无卷影，T1–T7 有 USN 删除记录，T8 为 `NOT_COVERED`。报告说明了未覆盖的内容恢复、MFT/LogFile、文件雕刻、权限跳过等边界，也没有把未找到表述为永久不可恢复。

L1–L8 覆盖了 18 个 source / 15 个 removed roots、ignored 内容缺口、49.48 GiB 仅为逻辑字节、bundle 增量属性、tools 根因、AC `PARTIAL` 状态和 F-01 临时目录。L3 对六个 worktree 使用“原路径与 HEAD 部分重建”的口径，没有声称原样复原。L4 没有把逻辑字节量说成物理净释放。

用户在本轮直接确认接受此前推荐，因此 closure package §2 对 `closed_with_limitations`、接受残余风险、先行限时搜索和工具修复另开 Task 的记录，足以满足用户裁决要求。**F-01 的事件记录和“原位保留、不删除、不移动”的裁定可以接受为限制项；但仍须把现存目录列入 Resource Manifest，才能支持资源完整收口。**

### 2. Resource Manifest 与终态字段

按 `tools/governance/check.ps1` 的规则手工核对，现有清册行本身没有会触发机械 FAIL 的列数、disposition、destination 或 integrity 问题。遗漏的 P03 Temp scratch 不会由这些逐行检查发现；它造成的是清册完整性不足。

`integration_commit: null` 与 `closed_with_limitations` 相容；`canonical_evidence_status: complete` 可在证据 pin 有效时成立。但在补齐临时资源记录前，**不应批准** `resource_closeout_status: complete`，也不应批准整个关闭字段组合。终态转换还必须先更新 STATUS 的活动 Task 指针，否则治理检查会因 STATUS 仍指向终态 Task 而失败。

### 3. 不变量、差异和收口数字

此前对固定提交差异的只读核验记录为：`3947d6344..HEAD` 只有 A/M、无 D/R；`tools/**` 无改动。提交内容未显示删除、移动、分支清理或历史改写。记录中也没有 GC、prune、push 或恢复搜索写操作的证据；这表示提交和所审证据未显示这些行为，不构成对仓外操作的系统审计证明。

审查材料中列出的 `132 worktrees`、`93 branches / 19 unmerged`、`77 archive refs` 以及 49.48 GiB 逻辑字节口径与前序清点一致；不得将其解释为物理净释放。TASK_LEDGER 的总数 `322 / 39` 相符，但子计数需要在收口前刷新。

### 4. Proposed Task

新 Task 的 `allowed_paths` 确实只列五个工具脚本、其 evidence_dir 和 Task 自身；保持 `proposed`、`pending_user_release`、未分配 owner、无实现分支是合适的。另开 Task 的方向已获用户接受，但该文件不在父 Task 原有 `allowed_paths` 中；应由 Codex 单独冻结和登记后再释放，不应把当前草案视为实施授权。

### 5. 逐 AC 裁定

| AC | 裁定 |
|---|---|
| AC1 | `PARTIAL`，维持 |
| AC2 | `PARTIAL`，维持 |
| AC3 | `PARTIAL`，维持 |
| AC4 | `MET`，维持 |
| AC5 | `MET`，维持 |
| AC6 | `PARTIAL`，维持 |
| AC7 | `PARTIAL`，维持 |
| AC8 | `MET`，维持 |
| AC9 | `PARTIAL`，维持 |

## 本轮运行证据

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` | 此固定 head 的前序核验记录为 exit 0，结果 `abba2b0c580bbf6c2190ed10d129c263bf39cf20`。 |
| `git diff --name-status 3947d6344..HEAD` | 前序核验记录为 exit 0，仅 A/M，无 D/R。 |
| `git diff -- tools/ 4072411eba420684cf0ba694c29cfcbdab9b0fc8..HEAD` | 前序核验记录为 exit 0，无差异。 |
| `git diff --check 3947d6344..HEAD` | 本轮未能执行；本轮命令启动器在进程创建前报 `helper_unknown_error: setup refresh had errors`，无进程 exit。 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | 前序核验记录为 exit 0、`PASS (3 warnings)`。本轮重跑同样在进程启动前失败，未获得新的原始输出或进程 exit；因此不把前序结果冒称为本轮新跑结果。 |
| Resource Manifest 手工规则核对 | 已列行机械规则均通过；发现 P03 Temp scratch 漏列，故语义上的资源清册完整性未通过。 |

本轮裁决**不授权** Task 状态转换或关闭操作。建议 Owner 先补齐 P03 Temp scratch 的资源记录并刷新 TASK_LEDGER，再提交新的关闭请求；本裁决不授权删除、移动、GC、prune 或历史改写。