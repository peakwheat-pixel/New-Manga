---
task_id: WORKSPACE-CONSOLIDATION-1
reviewer: Codex
author: dsh
base_commit: 2e0a30644ad434f94a7ca4cd5836ab490f43b5da
reviewed_head: 2e0a30644ad434f94a7ca4cd5836ab490f43b5da
decision: approved_with_conditions
review_mode: read_only
---

# 结论

**R211-01..04 可按下述状态处置；批准以 `closed_with_limitations` 收口，但须完成关闭提交前的计数刷新和治理验证。** 没有发现新的资源清册遗漏或阻止限制性关闭的问题。R211-03/04 是被明确接受并披露的限制，不代表原始范围偏离或日志缺口已经消失。

我未修改 Task 状态。当前 Task 仍为 `in_review`；以下授权供 Owner 在关闭提交中执行，并受本报告的条件约束。

## Findings

| ID | 级别 | 裁定与证据 |
|---|---|---|
| R211-01 | High | **FIXED。** [Task Resource Manifest](</G:/CODEX/New Manga/doc/tasks/WORKSPACE-CONSOLIDATION-1.md:284>) 已加入 `p03-temp-scratch`。只读复算为 20 files / 26,469 B，`objects/` 为 0 files；source/destination 同址、`PRESERVE_UNKNOWN`，integrity 指向的 [rework-r209-response.md](</G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/rework-r209-response.md>) 存在。 |
| R211-02 | Medium | **FIXED（关闭提交仍须重生成）。** 当前 [TASK_LEDGER.md](</G:/CODEX/New Manga/doc/TASK_LEDGER.md:7>) 的 322 / 296 tracked / 26 untracked / 39 non-terminal / 28 tracked non-terminal 与文件及 Git index 复算相符。Task 关闭后预计为 322 / 38，tracked non-terminal 为 27。 |
| R211-03 | Low | **ACKNOWLEDGED。** 新 Task 仍是 `proposed` / `pending_user_release`，没有 owner、base、branch 或 worktree；关闭父 Task 不等于释放实施。原父 Task 的 `allowed_paths` 未包含新 Task 草案，偏离已记录。 |
| R211-04 | Low | **ACKNOWLEDGED 为证据限制。** [closure-package-r211.md §8](</G:/CODEX/New Manga/verification/WORKSPACE-CONSOLIDATION-1/closure-package-r211.md:92>) 保留了原始枚举日志未逐条持久化的说明，并记录已有 spot-check 输出；没有把 `NOT_FOUND` 改写为永久不可恢复。 |

## 逐项裁决

### a. Finding 处置与资源清册

当前 Resource Manifest 有 **11 行资源**。逐行核对为 6 列、disposition 合法、destination 存在、非 SHA integrity 指向存在的 manifest 文件；没有发现会触发清册逐行校验 FAIL 的行。P03 bundle SHA-256 实测匹配 `4c2aef444ab3974401dfe038c7cf26f289cb8dd370bfe6062dfb5d2d70fddbee`。

对照 closure package、Handoff、recovery 和 P03 证据，未发现另一个未入清册、仍存在的 Task 资源根。恢复搜索中的其余目标均作为缺失或部分重建资源留在事故台账和限制项中；X6 副本及可重建字节也没有被当成原始文件仍存在。

恢复搜索仍然是有边界的搜索：T1–T7 有 USN 删除记录，T8 标为 `NOT_COVERED`，G: 无卷影副本。报告没有由未找到推导永久不可恢复。F-01 目录继续原位保留；本裁决不授权清理。

### b. 终态字段

以下组合可以用于限制性关闭：

- `status: closed_with_limitations`
- `integration_commit: null`
- `canonical_evidence_status: complete`
- `resource_closeout_status: complete`

这里的 `complete` 表示资源及证据的收口记录完整，**不表示资源完整恢复**。L1–L8 和新增 `p03-temp-scratch` 覆盖已披露限制；AC1/2/3/6/7/9 继续保持 `PARTIAL`，不得改为 `MET` 或勾选，也不得将 Task 标成 `done`。

Task 中 EV-R211-CLOSURE、EV-R211-RECOVERY、EV-R209-RESPONSE 的 SHA-256 均与对应文件匹配；关闭 package 的更新 pin 为 `ee23870b605861d17ddbcf7580b77bd05524fe0395125a8b4414ec9d7180b89f`。

### c. STATUS、Plan、TASK_LEDGER 与治理 FAIL

按 [check.ps1](</G:/CODEX/New Manga/tools/governance/check.ps1:297>) 的规则，`proposed` 是合法状态；第 300 行只禁止 STATUS 指向终态 Task。将 STATUS 指针改到 proposed Task **本身不会触发该项 FAIL**，关闭 Task 的 canonical/resource 检查也可在 STATUS 已改指后通过。

项目协议仍要求 proposed Task 不得实施。因此 STATUS 应明确标注它是“proposed / 未释放的下一候选”，Plan 中保持 proposed、不得放入 READY；Codex 仍须另行冻结范围和释放。关闭 Task 后重生成 Ledger，预期总数为 322 files、38 non-terminal、296 tracked、26 untracked、27 tracked non-terminal。

### d. 提交与数量不变量

`.git/HEAD` 指向分支 `antigravity/P09-AC3-DELETE-HARDEN-1`，该分支 ref 内容为固定 head `2e0a30644ad434f94a7ca4cd5836ab490f43b5da`。

读取 E4 Git 对象并与父提交 `abba2b0c580bbf6c2190ed10d129c263bf39cf20` 比较，E4 只修改了：

- `doc/TASK_LEDGER.md`
- `doc/tasks/WORKSPACE-CONSOLIDATION-1.md`
- `verification/WORKSPACE-CONSOLIDATION-1/closure-package-r211.md`

E4 的 `tools/` tree 与父提交相同。结合 R211 已核验的 `3947d6344..abba2b0c5` 结果，累计差异仍只有 A/M、没有 D/R，`tools/**` 未改。当前文档中的 132 worktree、93 branches / 19 unmerged、77 archive refs 数字仍一致；本轮没有重新扫描运行中的 worktree 或 refs。提交树和关闭证据没有显示新的删除、移动或 GC/prune 操作；这不是对仓外历史操作的审计证明。

## 授权 Owner 执行

授权 Owner 在关闭提交中：

1. 将 Task 设为 `closed_with_limitations`，保持 `integration_commit: null`，并将 canonical/resource closeout 设为 `complete`。
2. 更新 STATUS 指针、Plan 和 TASK_LEDGER；STATUS 将 proposed Task 标注为未释放候选，不能称为正在实施。
3. 状态更新后重生成 TASK_LEDGER；运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md`，保存完整输出与 exit，并在关闭提交前复核差异和 `git diff --check`。

**本授权不包括删除、移动、GC、prune、push 或历史改写。**

## 本轮运行证据

- `exec_command` 启动器仍在进程创建前返回 `helper_unknown_error: setup refresh had errors`。因此本轮没有新的 `git diff`、`git diff --check` 或 PowerShell 治理检查进程，也没有这些命令的 exit code；不把它们描述为本轮 PASS。
- 通过 `node_repl` 与 `node:fs/promises` 只读读取 `.git/HEAD`、分支 ref、Git 对象、Task、证据及治理脚本：固定 head 匹配；E4 父子 tree 差异为上述三项 M；`tools/` tree 相同。
- 文件系统与 Git index 只读复算：Task files 322、non-terminal 39、tracked 296、untracked 26、tracked non-terminal 28；与当前 TASK_LEDGER 一致。
- Resource Manifest 逐行核验：11 行无格式、disposition、destination 或 integrity 路径问题；P03 Temp 为 20 files / 26,469 B，`objects/` 为 0 files；P03 bundle 为 4,391 B 且 SHA-256 匹配。
- 手工核对 `check.ps1` 的状态及终态门槛：新 proposed 指针不会因终态指针规则失败；关闭提交后仍须实际运行检查器并记录结果。

下一步建议：Owner 按授权提交关闭更新并保存治理检查输出；`WORKSPACE-CLEANUP-TOOL-HARDENING-1` 继续保持 proposed，等待 Codex 单独冻结和释放。