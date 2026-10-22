---
task_id: GIT-MAINLINE-CONVERGENCE-1
reviewer: zcode
author: dsh
base_commit: fdca2057eec058996f936fc16138cc87e8cdc0bc
reviewed_head: 6997733bf959fdd4b087993c80624cafc2e7c93f
decision: approved
---

# Review：GIT-MAINLINE-CONVERGENCE-1（r3 独立审查，zcode）

审查日 2026-10-22；只读审查，未修改除本文件外的任何文件；未执行 `--apply`/`worktree remove`/`branch -D`/prune/GC 等任何删除或清理命令。Reviewer 未参与本 Task 任何实现。

## 范围与依据

- 审查对象：`6997733bf`（= 活树 HEAD，实测确认）。提交链：交付证据提交 `92425ef1a`（仅新增 convergence-verification-log.txt）→ `6997733bf`（转 in_review，改 Task/Handoff/STATUS/PLAN/LEDGER 5 文件）。`git show --stat` 逐一核实，两提交全部落在 Task `allowed_paths` 内，零触碰 `tools/governance/**`。
- 背景：Task 历经 R1（`83a8a15c`）/R2（`c9a1bdd30`，DeepSeek 仅批准非破坏性盘点切片）→ blocked → 用户四次明示授权（D-1/D-3「授权全部」、A+B+C、删除旧主线）→ dsh epoch 10 执行最终收敛 → 本次 r3 为执行阶段的独立审查。
- 区间归属甄别（`fdca2057e..6997733bf` 内触碰 `tools/governance/` 的 7 个提交）：全部归属其他独立治理 Task（historical-evidence-interpretation / broad-root-preservation / non-declaration-json-exceptions / path-header-compat / residual-runtime-identity-impl），无一属于本 Task。
- 声明审计「0 errors」来源核实：由独立 Task `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` 实现（`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/` 有 audit-baseline 7 errors → audit-resolved 0 errors 的前后 raw 证据；Antigravity 独立批准后 done，REBASELINE_PLAN L10 有登记）。本 Task 未绕过任何保护解析失败。
- 审查环境披露：审查前半程主会话 Bash 不可用，git 实测、bundle/manifest/leftover 哈希复核经只读 Explore 子代理执行；全部为只读命令（唯一派生产物为子代理自身报告）。

## Architecture / 合规结论

破坏性收敛的执行架构总体扎实，核心纪律全部保持：

1. **执行顺序正确**：先修正执行链（delta §10「先退工作树再删分支」，纠正了「83 条可独立删」的错误预判）→ 备份（bundle + 空仓恢复验证）→ 分批执行 → 逐批复验。分支账目完全闭合：`104→84→64→55→4→2→1`（d1 -20 → §12 -20 → phaseA-delete -9 → d3f -51 → 收尾 -2 → §17 旧主线 -1），20 条归档 = 9 条未检出 + 11 条检出后删，51 = 11 已归档检出 + 40 已合并检出，全部对上。
2. **强制手段受控**：`branch -D` 仅用于 20 条已建 `refs/archive/*` 的分支（phaseA-delete 逐条带 archive_ref 与 tip 对应，d3f `branches_refused=0`）；其余删除全部 `branch -d`（含旧主线，§17 实录「was 26c0f2aab」）。`worktree remove --force` 仅用于 3 个经逐文件哈希证明与 main 逐字节相同的冗余副本（delta §15 明列 3 个路径，redundancy-analysis 台账支撑）；BUILD_ONLY 批次 2 个被 git 拒绝的工作树如实保留（§12.2），未强删。
3. **保护边界完整**：五广域根与 r212 禁令未动（声明审计 0 errors / 1946 protected roots、EXIT 0——保护根只增不减 1936→1946）；未执行 prune/GC/push/reset/stash；用户未提交内容原样保留（实测 `git status --porcelain` 1246 行全为 `??`、非 `??` 为 0、stash 0）。
4. **恢复三路径全部实证可用**（见 Verification 表）。

## Verification 结论

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 终态一致性 | `git rev-parse HEAD` / `for-each-ref refs/heads` / `worktree list` / `refs/archive` 计数 | 活树 6997733bf | **PASS**：HEAD=6997733bf；`refs/heads` 仅 main；worktree 仅主 checkout；`refs/archive/*` 恰 21 条（21 条 tip 与 phaseA-tags/§17 台账全量一致）；stash 0 | 子代理实测原始输出 |
| 删除合规性（分支） | 台账逐项核对 + 计数链 | d1/phaseA-delete/d3f | **PASS**：d1 台账 20 条全 `branch -d` exit 0 带 tip；phaseA-delete 9 条 `-D` 全带 archive_ref；账目链闭合至 1（见 Architecture 节） | 本 Review 逐台账比对 |
| 删除合规性（工作树） | 台账逐项核对 | d3/d3b/d3c/d3d/d3e/d3f/d3g + archive-result | **PASS（带 R-002）**：142→116→96→84→81→…→1 各批台账齐全；75 targeted/71 removed/4 refused 与 5 个 leftover 目录（d3f 4 REFUSED + d3g P09-IMPORT-CORE）内容全部归档实证 | d3f-d1f-ledger、leftover-archive、本 Review实测 |
| 恢复可行性 ① refs/archive | 抽样 6 条 `git rev-parse <ref>` + `cat-file -t` | 活树 | **PASS**：6/6 tip 与台账期望完全相等、类型均 commit（P09-AC3-DELETE-HARDEN-1=26c0f2aa、gov-residual-runtime-identity-impl-1=4d5e9710、T3.2.1-repair-13=13ae23f6、GIT-TOPLEVEL=0af89808、M2-RUNNER-r2=daab1996、P14=41c32069）；21 条全量名单与台账一致 | 子代理实测 |
| 恢复可行性 ② 内容归档 | 读 manifest + 逐文件 SHA-256 复算（M2-C1-dsh-review-7de1cd2-r2，8 文件） | worktree-content-20261022 | **PASS**：8/8 文件 size+SHA-256 与 `_manifest.json` 完全一致 | 子代理实测 |
| 恢复可行性 ③ 残留目录归档 | 5 子目录文件数统计 | `_leftover` | **PASS**：1719/2010/1909/647/884 与台账 5/5 一致（覆盖 leftover 台账 rc=9/rc=1 的疑点，逐文件 missing=0 声称成立） | 子代理实测 |
| 恢复可行性 ④ bundle | SHA-256 + 字节数 + `git bundle verify` | all-refs-352410640c.bundle | **PASS**：SHA-256 `35869bc3…cc6cd` 与字节数 239,944,235 精确匹配；verify exit 0（363 refs、complete history） | 子代理实测 |
| 保护边界 | `git status --porcelain` 统计 + 审计计数 | 活树 | **PASS**：1246 行全 `??`、tracked dirty 0、diff --check 0；审计 0 errors/1946 roots 只增不减；r212/五广域根未解除 | 子代理实测 + convergence-log L26 |
| AC1 MET | EV-AUTH/EV-BASE + checkpoint 接管记录 | c615d52b4 | **PASS**：CAS 接管 epoch 9→10、helper selftest 127 passed、基线记录在案 | checkpoint.md L9 |
| AC2 MET | 全量盘点 142/142 + 分类台账 | EV-CONV-INV 等 | **PASS**：worktree-inventory 逐项存在性/HEAD/dirty/untracked/ignored/独有提交/占用；42 与 103 分支分类（A 83/D 19/B 0/C 0）有 branch-analysis 与 delta §2-§4 支撑 | delta §9.1、§1-§2 |
| AC3 MET | 19 条未合并分支逐项 | unmerged-evidence-20261022.json | **PASS**：独有提交/变更文件数/Legacy 命中/当前文档引用逐项在案；19/19 无活动 Task 引用；2 条 patch 全等价如实标注；未盲合并 | delta §3、§9.2 |
| AC4 MET | 备份+恢复+授权+Review | 全链 | **PASS 带时序张力（R-003）**：备份/恢复/用户授权三要件实证满足；「通过独立 Review」在本 Review（r3）完成，见 R-003 | 各台账 + 本文件 |
| AC5 MET | 终态实测 | 活树 | **PASS**：refs/heads 仅 main（103→1）、注册 worktree 仅主 checkout；例外（旧主线）最终经用户追加授权归档删除，无隐藏例外 | 子代理实测 |
| AC6 PARTIAL | — | — | **PASS（诚实）**：独立 Review（本 r3）与集成复验当时未完成，如实标 PARTIAL，未夸大 | Task L53 |
| 0 errors 来源 | IMPL-1 证据目录 + git log | 区间 | **PASS**：7→0 由 GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 实现（Antigravity 独立批准、PLAN L10 登记 done）；本 Task 零触碰解析器 | 子代理第 8/9 项 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | `doc/STATUS.md:9-10`、`doc/REBASELINE_PLAN.md:27` | 权威导航残留陈旧快照，与同文件新状态自相矛盾：STATUS L7-8 记录收敛完成（heads 仅 main、worktree 1），L9 仍写「父任务 GIT-MAINLINE-CONVERGENCE-1 `blocked`」、L10 仍写「当前103本地分支/141工作树；**尚未达到只剩main**」；PLAN L23 已更新为 in_review 但 L27 仍写「当前唯一 active 为 GOV-RESIDUAL-RUNTIME-IDENTITY-1」（该 Task 已 done）。影响：恢复点读者可能按陈旧行误判仓库状态 | 本 Review Read 原文对照 | 集成/done 时删除或刷新 STATUS L9-10 与 PLAN L27 的陈旧行（本 Review 不代改） | open |
| R-002 | P2 | `verification/GIT-MAINLINE-CONVERGENCE-1/d3f-d1f-ledger-20261022.json`（worktrees_after=6）、`d3g-part1-20261022.json`（P09-IMPORT-CORE REFUSED 255） | 收尾段过程台账粒度不足：d3f 记录 4 个工作树 REFUSED（权限/占用）+ d3g 1 个 REFUSED（Directory not empty），`worktrees_after=6` 到终态 1 之间这 5 个的最终注册移除（重试成功？手动清除注册元数据？）无逐项命令台账；delta §16.2 只记「71 移除、4 被拒」。影响：该 5 项的「逐项可追溯」收口打折。**资产安全不受影响**：75 targeted 的内容归档覆盖这 4 个（manifest 实证）、5 个残留目录内容经 leftover 归档且文件数 5/5 实测吻合、终态 worktree=1 实测正确 | d3f/d3g 台账 + 本 Review 终态实测 | 集成时在 Task 交付记录补一段收尾说明：如实写明这 5 个的最终处置方式（及 6→1 的衔接），不改已 pin 台账字节 | open |
| R-003 | P2 | `doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md:51`（AC4） | AC4 含「通过独立 Review」子条件，但执行链时序为「用户授权 → 删除执行 → 事后独立 Review（本 r3）」；`6997733bf` 标 AC4 MET 时该子条件尚未发生。Task 以 AC6 PARTIAL 诚实挂起了 Review 事项（无掩盖），用户明示授权构成最高裁决、本 Review 已事后覆盖全部删除合规性——属 AC 声明时序的透明度问题，非实质安全缺陷 | Task AC4/AC6 对照 + 执行时间线（delta §11-§17 均先于本 Review） | 在 Task 注明「AC4 的『通过独立 Review』由 r3 承担、MET 以 r3 通过为条件」；本 Review approved 后该子条件闭合 | open（随本 Review approved 即闭合） |

备注（不构成 finding，供集成时知悉）：

1. 「103→1 / 删除 102 条」口径未说明执行期间新建 1 条实施分支（`codex/gov-residual-runtime-identity-impl-1`，IMPL-1 的开发分支，后归档删除）；台账实际链为 104→1，数字自洽（102 = 接管时 103 − main 1，新建分支的建与删相抵）。delta §1（142 worktree）与 §16.4（141）的 1 个差异同源（实施 worktree）。
2. untracked 根计数：convergence-log 时点 1247、Task Closeout 1246、本 Review 实测 1246——±1 属时点自然漂移；「原样保留」结论不受影响（全 `??`、tracked 0）。
3. leftover 台账 `rc=9/rc=1` 标 COPIED：robocopy 语义下 rc≥8 含失败位，单看返回码有疑；但逐文件比对 missing=0 + 本 Review 5/5 文件数实测一致，内容完整性已独立闭环。

## 结论与复审

**decision: approved（限 reviewed_head `6997733bf`）。**

理由：六个必审项全部独立实证通过——102 条分支、140 个工作树、5 个残留目录的删除全部满足「已备份 + 已归档 + 已授权 + 恢复可行」（备份 bundle 哈希与字节精确匹配且 verify 通过、归档内容逐文件哈希抽样一致、refs/archive 21 条全量对上并抽样可 peel）；AC2–AC5 的 MET 有台账与实测支撑、AC6 PARTIAL 诚实；强制手段（`--force`×3 仅冗余副本、`-D`×20 仅已归档分支）均在授权与已归档范围内；五广域根、r212、用户未提交内容（1246 untracked 全 `??`）实证未动；声明审计 0 errors 系独立 Task 成果、本 Task 零触碰解析器。三项 P2（导航陈旧行、收尾台账粒度、AC4 时序）均不构成 P0/P1 或关键验证缺失，随本 Review approved，R-003 即闭合。

集成要求（dsh 执行后才可 done）：
1. 处置 R-001：刷新 STATUS L9-10、PLAN L27 陈旧行；
2. 处置 R-002：在 Task 交付记录追加收尾 5 工作树（d3f 4 REFUSED + P09-IMPORT-CORE）的最终移除说明；
3. 集成复验：重跑 `pwsh -NoProfile -File tools/governance/check.ps1`、`git diff --check`、声明审计并记录真实 EXIT，与 convergence-verification-log 终态口径对照；
4. 重申：本 approved 不解除 r212 禁令与五广域根保护、不授权任何进一步清理（含 `.git/worktrees` 孤儿元数据、`restore-all-refs` temp 探针仓、11 个 `p19*` 系统 Temp 目录的处置均需另行授权）；Resource Manifest 中 PRESERVE 项维持原位。
