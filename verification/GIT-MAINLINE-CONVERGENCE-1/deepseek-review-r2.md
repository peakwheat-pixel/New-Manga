---
task_id: GIT-MAINLINE-CONVERGENCE-1
reviewer: DeepSeek Harness
author: Codex
base_commit: 83a8a15c259c82267c0a1001123f3cf4ede8a246
reviewed_head: c9a1bdd3061300c9c1c633eb8f2279903918e5a2
decision: approved
---

# Review R2：GIT-MAINLINE-CONVERGENCE-1（限定增量复审）

## 结论先行

- 固定 `HEAD=c9a1bdd3061300c9c1c633eb8f2279903918e5a2`，与 `reviewed_head` 一致；复审前后 HEAD 未变，`git diff --check base..head` **EXIT=0**。
- 增量共 2 个提交、15 个文件，全部为治理/证据变更，无产品代码、无 merge、无删除。
- R1 的 R-001…R-006 **六项均已修复**。
- 新发现 1 项 P2（N-001）：Task 正文与滚动 checkpoint 仍引用旧交付/证据 head `a91e659c3`，与当前 `delivery_head=c615d52b4` 不一致。
- 无 P0/P1；**批准仍仅限非破坏性盘点/保全/治理元数据切片**。不批准 Task done、删除、GC/prune；AC4/AC5 继续 `BLOCKED`，AC2/AC3 继续 `PARTIAL`。

## R1 Findings 处置

| Finding | 状态 | 实际核验 |
|---|---|---|
| R-001 main tip | **fixed** | `branches.md` 的 main 行已改为分析时 `56272e40b`；表头同时说明分析时 `56272`、R1 时 `83a8`，未强行改成当前 HEAD。当前 HEAD `c9a1` 另由状态文件记录。 |
| R-002 R1 checker 日志 | **fixed** | 已新增 `verification-log-r1-head83.txt`：`SOURCE_HEAD=83a8...`、`PASS (3 warnings)`、EXIT=0；原始 stderr 的 `InvalidOperation ... ConstrainedLanguage` 与说明均保留。另存在 c9 的只读验证日志，内容同为 3 warnings、EXIT=0。 |
| R-003 STATUS 对账 | **fixed** | `doc/STATUS.md:16` 改为“325 文件 / 312 终态 / 13 非终态”，旧 `322/309/ready 2` 已删除。按 frontmatter 复算：325 个 Task 文件（不含 README）、312 终态、13 非终态，与台账一致。 |
| R-004 备份时间边界 | **fixed** | Task Resource Manifest 已改为“截至 main=56272e40b 的快照：214 common refs 全等、135 记录时 HEAD 可读；不含后续治理提交；仅 Git 历史”；并保留未提交/ignored/应用会话不覆盖的限制。 |
| R-005 Plan Legacy Mapping | **fixed** | `doc/REBASELINE_PLAN.md:17` 已删除“Legacy Mapping”；`git grep "Legacy Mapping"` 无匹配。现存 `Legacy` 仅为“无 Legacy 实施/诊断/修复释放”，不是未依据的继承声明。 |
| R-006 README P22 指针 | **fixed** | `doc/tasks/README.md:10` 已将 `P22-REBASE-1` 标为 `done / integrated，非下一实施切片`；当前 READY 明确为“无”。 |

## 新 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| N-001 | P2 | `doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md:130`；`verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md:5` | Task frontmatter 已写 `delivery_head: c615d52b4...`，但正文仍写“交付 head a91e659c3...”，checkpoint 仍写“盘点证据 a91e659c3”。复审/恢复读者可能据此回到旧证据 head，错过 c615 的 19 项重签；不影响本轮安全结论和 pin 本身。checkpoint 仍是滚动文件，不应 pin。 | `git grep a91e659c3` 命中上述两处；`delivery_head` 为 c615d52b4。 | 将正文改为“R1 交付 a91e；R2 证据 c615”，checkpoint 更新为 c615 或明确“R1 历史证据”；不将 checkpoint 登记为不可变证据，保留其未登记 warning。 | open |

## 原始字节与数据补证

### 19 项 EV/SRC raw-byte 核验

严格使用 `subprocess.run(['git','show',commit+':'+path], capture_output=True).stdout` 的 **bytes** 与 `Path(path).read_bytes()` 比较，未使用 `text=True`，未经过 PowerShell 文本管道：

- pin 行数：**19/19**
- pin 统一 commit：`c615d52b4f2f382979e4061b38c01fc7a38120c3`
- 磁盘字节 == commit blob 字节：**19/19**
- 磁盘 SHA-256 == commit blob SHA-256 == Task pin：**19/19**
- 不一致：**0**

覆盖 EV-AUTH、EV-BASE、EV-INV、EV-BRANCH、EV-WT、EV-ARCHIVE、EV-RESTORE、EV-REPORT、EV-CHECK，以及 SRC-ATTR、SRC-BRANCHES、SRC-WORKTREES、SRC-LOG-ATTEMPT1、EV-OTHERREFS、EV-DELTA、EV-REWORK、SRC-R1、SRC-DISPATCH、SRC-EARLY-CHECK。

### Plan 快照与属性

- 快照仍为 **6,945 B / 60 行**，blob 与 `fdca2057e:doc/REBASELINE_PLAN.md` 逐字节相等；SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7` 未变。
- `verification/.../.gitattributes` 为 `* text eol=lf`；新增归档目录 `.gitattributes` 为 `*.md text eol=lf`，仅约束该目录，未改原历史源文件或全局规则。

### 77 声明错误与 other refs

- `declaration-delta.json`：`old 76 → new 77`；added 仅 1 条 `TABLE_SCHEMA_INCOMPLETE`，文件为 `doc/tasks/workspace-declaration-remediation-1.md`；removed 0；`no_semantic_change=true`。未放宽 fail-closed。
- `other-refs-analysis.json`：117 条非 heads refs；117/117 `PRESERVED_UNCHANGED`，`inspection_exit=0`；`branch_unique_count_sum=351`、去重 `224`、全部 refs 去重 `334`、集合外 `110`，与说明一致。

## 验证

环境：Windows；外层 DSH PowerShell 为 ConstrainedLanguage，子进程 `pwsh -NoProfile` 正常；pwsh 7.6.6、Python 3.14.6、git 2.52.0.windows.1。本轮只读，未改文件、租约、refs、worktree，未删除/合并/GC/prune，未联网、未安装、未派发子任务。

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 固定 | `git rev-parse HEAD` | c9a1bdd30 | PASS；前后一致 | 终端输出 |
| 增量与 whitespace | `git diff --stat`、`git diff --name-status`、`git diff --check` | 83a8..c9a1 | PASS；2 commits/15 files；EXIT=0 | 终端输出 |
| 6 项修复 | 定向读取/diff/grep | c9a1bdd30 | PASS 6/6；见上表 | 治理正文 diff |
| 19 pins raw bytes | `git show` bytes + `Path.read_bytes()` | c615d52b4 | PASS 19/19，0 不一致 | 本次脚本 |
| Plan 快照 | 快照 bytes vs fdca blob | fdca2057e | PASS；6,945 B、SHA 未变 | 本次脚本 |
| 治理 checker | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md` | c9a1bdd30 | **PASS (3 warnings)，EXIT=0**；warning 为 13 非终态、STATUS 80%、未登记 `checkpoint.md` | 终端输出 |
| R1 日志 | 读取 `verification-log-r1-head83.txt` | 83a8a15c | PASS；3 warnings、EXIT=0、stderr/ConstrainedLanguage 保留 | 文件内容 |
| c9 验证日志 | 读取 `validation-c9a1bdd30.txt` | c9a1bdd30 | PASS；3 warnings、EXIT=0；`TRACKED_DIRTY_BEFORE=''` | 文件内容 |
| 77 错误增量 | 解析 `declaration-delta.json` | c615d52b4 | PASS；76→77，新增 1，删除 0 | 本次脚本 |
| 117 refs | 解析 `other-refs-analysis.json` | c615d52b4 | PASS；117/117 保留，计数 351/224/334/110 | 本次脚本 |
| R1 bundle/214/135 | 未重新遍历 | R1 证据 | N/A（按要求不复核；未发现需要重开 R1 的问题） | — |
| 产品测试 | 无产品代码变更 | — | NOT_RUN（N/A） | diff 证据 |
| 删除/merge/GC/prune | 只读观察 | — | 未执行；本轮 0 | 终端输出 |

`checkpoint.md` 的“未登记过程文件”warning 为预期项：它是滚动恢复点，不是不可变证据；本轮**不**将其 pin、不消除该 warning。当前只需注意 N-001 的内容陈旧。

## 结论与复审

**decision: approved（仅非破坏性盘点/保全/治理元数据切片，固定 head `c9a1bdd30`）。**

R-001…R-006 已逐项修复；19 项证据以原始字节重新核验通过；Plan 快照字节/hash 未变；治理 checker 在实际 reviewed head 为 PASS（3 warnings, EXIT=0）；`git diff --check` 为 EXIT=0。无 P0/P1。N-001 是 P2 指针陈旧问题，建议在下次治理元数据提交中修正，但不改变本轮“无删除授权、Task 未完成”的安全结论。

**批准边界不变**：不批准删除、GC/prune、强删 worktree、Task done；不把 77 错误、other-refs 的 117 条保留项或表面唯一候选解释为 `DELETE_SAFE`；不解除旧主线/既有保护。完整 Task 的 AC4/AC5 仍 `BLOCKED`。

**生命周期**：本 Review 只确认复审通过；是否将完整 Task 从 `in_review` 转 `blocked`（暂停前阶段 `in_review`，记录外部授权阻塞）由 Codex 决定。这不是关闭或完成；若转移，必须保持 AC4/AC5 的 BLOCKED 原因、全部保护与清理禁令不变。

**推荐下一步**：Codex 修正 N-001（Task §“盘点交付与 Review 范围”和 checkpoint 的旧 `a91e` 引用），保留 checkpoint 为滚动文件并接受其未登记 warning；不需要重跑 R1 的 bundle/214/135 验证。修正后如需新 head，本批准自动失效，应只复审该元数据增量。