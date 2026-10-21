---
task_id: GIT-MAINLINE-CONVERGENCE-1
reviewer: DeepSeek Harness
author: Codex
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
reviewed_head: 83a8a15c259c82267c0a1001123f3cf4ede8a246
decision: approved
---

# Review：GIT-MAINLINE-CONVERGENCE-1（非破坏性盘点/保全/治理元数据切片）

## 审查结论先行

- 已确认 `HEAD = 83a8a15c259c82267c0a1001123f3cf4ede8a246`，与 `reviewed_head` 一致；审查前后 HEAD、97 heads、214 refs、135 worktrees 均未变化。
- 本 Review **只批准固定 head 上的非破坏性盘点/保全/治理元数据切片**。
- **不批准删除、不批准 GC/prune、不批准 Task done，也不把本 Review 当作完整 AC4/AC5 的通过。** AC4、AC5 继续 `BLOCKED`，AC2、AC3 继续 `PARTIAL`，Task 保持 `in_review`。
- 未发现 P0/P1；发现 6 项 P2，均为清单/证据/导航的准确性问题，不改变“当前没有可执行删除”的安全结论。
- 产品代码未变化；产品测试 `NOT_RUN` 有正当性。未运行 `consolidate.py`，避免产生写入或清理副作用。

## 范围与依据

固定范围为 `fdca2057e..83a8a15c`，共 3 个提交、21 个文件、全部为治理文档/证据/归档快照：

- `A`：Plan 基线快照、Task、`verification/GIT-MAINLINE-CONVERGENCE-1/**`
- `M`：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、`doc/WORKTREE_SAFETY_INVENTORY.md`、`doc/tasks/README.md`
- 无产品代码、共享接口、Schema、依赖或测试变更；无 merge commit。

所有变更路径均在 Task `allowed_paths` 内，未发现越界修改。审查依据为 Task AC、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/09_COLLABORATION.md` §4/§6、`doc/templates/REVIEW.md`，以及 Task 引用的证据文件。

**未覆盖范围**：产品行为/测试、135 个 worktree 的未提交与 ignored 文件内容、逐路径进程占用、历史 Task 全文、删除安全性本身、GC/prune 历史与远端状态。上述不是本切片的批准对象。

## Standards / Spec（可选视角）

- **Standards：executed（轻量）**。治理变更符合 §4 的 evidence pin、AC v3 标记和 Review 生命周期；未修改 checker 语义；未用聊天或分支名替代 Task 状态。
- **Spec：executed**。AC1 有交接/授权记录；AC2/AC3 如实标记 `PARTIAL`；AC4/AC5 如实 `BLOCKED`；AC6 仍 `PARTIAL`。未发现把完整目标写成已完成，也未发现删除或合并的 scope creep。

## Architecture

- **分层/契约/依赖**：本切片不触碰 React/Tauri/Python/SQLite 调用链，不改变共享契约、依赖方向或持久化边界。治理文档变更不影响产品架构。
- **保全与保护**：未提交、untracked、ignored、应用会话和 reflog-only/unreachable 内容均未纳入 Git bundle；报告和 `backup-restoration.json` 已明确该限制。当前清理/GC/prune 禁令、旧主线显式保留、所有既有保护均未解除。
- **完整性**：基线 Plan 快照与 `fdca2057e:doc/REBASELINE_PLAN.md` 逐字节一致（blob `224d64230a1419319ad20cc7c9682b579735777f`，6,945 B / 60 行，SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`），未发现授权丢失或历史节点被重新激活。
- **状态与指针**：Task、STATUS、Plan 均指向 `GIT-MAINLINE-CONVERGENCE-1 / in_review`；未声称 Task done，未把 Review 通过解释为删除授权。
- **结论**：Architecture 面对本切片为 **可接受**；存在 P2 文档准确性问题，需在后续治理提交修正，不影响非破坏性结论。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `verification/GIT-MAINLINE-CONVERGENCE-1/branches.md:3,92`；`branch-analysis.json` 的 `mainline_head` 与 `main.tip` | 表头称“分析时 main 56272e40b”，但 main 行 tip 写成基线 `fdca2057e`。97 heads 清单的 main 行因此不准确；当前 main 已到 `83a8a15c`。不影响 19 未合并/78 已合并的判定，也不使 main 成为删除候选。 | `git rev-parse main` = `83a8a15c...`；JSON `mainline_head=56272e40b...`，`branches[main].tip=fdca2057e...`。 | 将 main 行改为“分析时 `56272e40b`”，另注当前 `83a8a15c`；如改文件需重算 `SRC-BRANCHES` pin。 | open |
| R-002 | P2 | `verification/GIT-MAINLINE-CONVERGENCE-1/verification-log.txt:2-9`；`doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md:48`；`report.md:51` | 日志绑定 `SOURCE_HEAD=56272e40b`、记录“PASS (2 warnings)”；AC6/报告也写“2 warnings”。但在 reviewed head `83a8a15c` 实测为 **PASS (3 warnings)**，新增 warning 为 `evidence_dir 含未登记过程文件 ... checkpoint.md`。检查器仍 exit 0，非失败；但最终治理证据未绑定 reviewed head，且漏记了本应预期的 mutable-checkpoint warning。 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md`：EXIT=0，3 warnings。 | 在 `83a8a15c` 重跑并保存带 EXIT 和环境头的日志；AC6/report 改为 3 warnings，并明确 checkpoint 为滚动文件、不作不可变证据。 | open |
| R-003 | P2 | `doc/STATUS.md:16-17`；`doc/TASK_LEDGER.md:9-16,22-28` | STATUS 仍写“322 个文件、terminal 309、非终态 13（ready 2 / in_review 2）”，并称“2026-10-21 实算，可复算”。实际按 Task frontmatter 复算为 325 个 Task 文件（不含 `README.md`）、terminal 312、非终态 13（`in_review` 4、`ready` 0、`blocked` 7、`in_progress` 2）。台账自身一致，STATUS 已过期。 | 文件计数 326（含 README）→ 325；状态统计 `done 254 / closed 34 / cancelled 18 / superseded 6 / blocked 7 / in_review 4 / in_progress 2`。 | 用 `task_ledger.py` 口径重算 STATUS 对账段，或删除过期计数；不要保留“实算可复算”的错误陈述。 | open |
| R-004 | P2 | `doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md:104`；`report.md:31-33`；`backup-restoration.json` | 全 refs 备份的“214 refs 全等、135 HEAD 可读”是 **记录时（main=56272e40b）** 的事实，但 Manifest 行未写时间边界。reviewed head 下恢复仓仍有 214 个 ref 名称，`refs/heads/main` 却为 `56272e40b`，当前 main `83a8a15c` 不在备份内；当前 127 个唯一 worktree HEAD 中 126 个可读，唯一缺失正是 `83a8a15c`。 | 恢复仓 `for-each-ref` 214；与记录时 214 refs 精确相等；与当前比较仅 main OID 不同。 | 在 Manifest/报告写明“截至 `56272e40b` 的快照”，列出当前 main 差异；未来任何删除窗口前应在最终 head 重新建全量 Git 备份。不得称其为最终工作区完整备份。 | open |
| R-005 | P2 | `doc/REBASELINE_PLAN.md:17`；快照 `archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md` | 当前 Plan 声称从快照继承“其余节点状态、依赖、Legacy Mapping 与限制”，但快照全文没有任何 `Legacy` 字样，无法支持“Legacy Mapping”已被继承的表述。节点/依赖/限制本身已由逐字节快照保全，未发现授权丢失或历史激活。 | 快照 `grep Legacy` 无匹配；快照 hash/字节已验证一致。 | 改为准确列出快照实际包含的内容，或另引真实的 Legacy Mapping 来源；不要把未出现的章节写成已继承。 | open |
| R-006 | P2 | `doc/tasks/README.md:6` | 仍写“下一实施切片：P22-REBASE-1，独立审查后释放”。但 `P22-REBASE-1` 已 `done` 且 `integration_status: integrated`，当前 Plan 的 READY 为“无”。这是过期导航，可能误导下一个 Agent 重新释放已完成切片。 | `doc/tasks/P22-REBASE-1.md` frontmatter：`status: done`、`integration_status: integrated`；Plan 第 13 行“READY 节点：无”。 | 将该行标为历史或删除；如需下一任务，以 Plan/STATUS 当前指针为准。 | open |

**P0/P1：无。** 以上 P2 均不改变以下事实：本轮没有可执行的删除候选，77 个声明错误仍 fail-closed，旧禁令仍有效。

## 验证

环境：Windows；外层 DSH PowerShell 为 ConstrainedLanguage，子进程 `pwsh -NoProfile` 正常；`pwsh 7.6.6`、`Python 3.14.6`、`git 2.52.0.windows.1`。所有 Git 读操作使用 `--no-optional-locks`；未 push、未联网、未安装、未派发子任务、未写仓库文件。

| 场景 | 命令或步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 固定 | `git rev-parse HEAD` | `83a8a15c` | PASS；审查前后一致 | 本报告 |
| diff/提交 | `git diff --stat --name-status fdca..83a8`；`git log` | base..head | PASS；3 commits，21 files，0 merge，无产品代码 | 终端输出 |
| 范围冻结 | 对照 Task `allowed_paths` 与变更路径 | `83a8a15c` | PASS；21/21 在允许范围 | 解析结果 |
| refs/stash | `git for-each-ref`；`git stash list` | 当前 | PASS；214 = 97 heads + 3 remotes + 77 tags + 37 codex；stash 0 | 终端输出 |
| 分支合并判定 | 对 97 个 tip 逐一 `merge-base --is-ancestor` | 分析时 main `56272e40b` | PASS；77 已合并 + main，19 未合并；未把未合并误算为已合并 | 终端输出 |
| worktree 清册 | `git worktree list --porcelain`；对比 `worktrees.md` | 当前/分析时 | PASS；135 条，路径全集一致；39 Detached，96 分支检出 | 终端输出/JSON |
| dirty/ignored/保护 | `worktree-analysis.json` 汇总复算 | 记录时 | PASS；82 个含 dirty/untracked（35 tracked + 62 untracked 重叠）；60 个 worktree 含 ignored 根（主工作树单树 121 根，非根总量）；125 个 worktree 有保护命中（主工作树 1,134 条） | JSON `summary` |
| ignored 强度 | 检查 `ignored_file_hashes` | 记录时 | PASS；值为 `NOT_MEASURED: grouped roots only...`，未逐文件 hash，不能据此删除 | JSON |
| 19 个增量 bundle | 逐个 SHA-256、`git bundle verify`、tag tip 比对 | 当前 | PASS 19/19；hash/verify/tag 全匹配，总 4,728,495 B | `archive-verification-resolved.json` |
| 全 refs bundle | `Get-FileHash`；`git bundle verify` | 当前 | PASS；238,847,964 B；SHA-256 `8128955e...0f1a9`；bundle 含 349 refs（含 worktree HEAD 伪 ref） | 终端输出 |
| 空仓恢复 refs | `for-each-ref` 对比记录时 214 refs；`fsck --full --no-reflogs` | 恢复仓 | PASS（记录时）；214/214 名称+OID 精确相等；fsck EXIT=0，2 dangling，无错误；当前仅 main 的 `83a8a15c` 不在备份内 | `backup-restoration.json`/终端 |
| 135 HEAD 可读 | 按记录时 127 个唯一 HEAD 批量 `cat-file --batch-check` | 恢复仓 | PASS（记录时）；127/127 可读，对应 135 个 worktree；当前新增 `83a8a15c` 不在备份内 | 终端输出 |
| Plan 快照 | `git hash-object`、`sha256`、行数 | `fdca2057e` | PASS；blob `224d6423...`；6,945 B/60 行；SHA-256 `1d2c...`；与基线 blob 逐字节一致 | 终端输出 |
| Canonical Evidence | 13 个 EV/SRC pin 的 path、commit、SHA-256、blob | `a91e659c` | PASS 13/13；工作区字节与 pin 一致，commit 中 blob 一致 | 解析结果 |
| Resource Manifest | 核对 bundle、restore、agent-output 三个根 | 当前 | PASS；实际根均存在，无漏项；但见 R-004 时间边界 | 目录枚举 |
| 表面候选 | `git -C ... status --porcelain`、`ls-files -o/-i`、`rev-list --count` | `WORKSPACE-CLEANUP-TOOL-HARDENING-1` | PASS；status/untracked/ignored/modified 均 0，unique=0；仍不判 `DELETE_SAFE`，77 错误/占用未知阻塞 | 终端输出/JSON |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md` | `83a8a15c` | **PASS (3 warnings), EXIT=0**；warning 为 13 非终态、STATUS 80%、未登记 `checkpoint.md` | 终端输出 |
| whitespace | `git diff --check fdca..83a8` | base..head | PASS，EXIT=0 | 终端输出 |
| `consolidate.py` preflight | 未重跑（避免写入） | — | NOT_RUN；记录值 77 声明错误/236 warnings/0 Git inspection errors 已由 JSON 复核；不作为删除清单 | `preflight-inventory.json` |
| 产品测试 | 无产品代码变更 | — | NOT_RUN（N/A） | diff 证据 |
| 删除/merge/GC/prune | 只读观察 refs/提交 | — | 未执行；无 merge commit，refs/worktree 数量未变；GC/prune 无法由快照反证 | 终端输出 |

## 结论与复审

**decision: approved（仅限非破坏性盘点/保全/治理元数据切片）。**

理由：固定 head 的治理变更范围受控，未触碰产品代码或受保护内容；97/135/214/19/0 等关键计数、19/19 bundle、全 refs 备份与空仓恢复、Plan 快照、13/13 evidence pins 均可独立复核；Task 未声称完成，AC4/AC5 仍 `BLOCKED`，没有删除或合并授权。治理检查在 reviewed head 实测 PASS（3 warnings, EXIT=0），`git diff --check` 为 EXIT=0。

**批准边界**：不批准删除、GC/prune、强删 worktree、Task done；不批准把 77 错误或“表面唯一候选”解释为 `DELETE_SAFE`；不解除旧主线/既有保护。若 Codex 在未来新增删除窗口，必须另冻范围，逐项解决保护声明错误，完成 source/HEAD/hash/backup 与用户授权，再独立复审。

**剩余风险**：R-001 至 R-006 需要在新的治理元数据提交中修正；R-002 的最终 checker 日志必须绑定新 head；R-004 的全量 Git 备份不覆盖 `83a8a15c` 之后的内容，不能作为最终工作区完整备份。当前 ignored 内容、未提交内容、应用会话和进程占用仍未证明可删除，必须原位保留。

**推荐下一步**：由 Codex 在 `main` 上做仅治理元数据的修订提交，修正 R-001～R-006，重跑 checker 并保存带 EXIT/环境头的 3-warning 日志，更新受影响的 pin；Task 继续保持 `in_review`，AC4/AC5 继续保持 `BLOCKED`，不释放清理/GC/prune，不派发删除任务。若只需要接受当前切片，则把上述 P2 作为已记录的后续修订项，固定 head 不变；任何新 head 出现后本批准自动失效并需复审。