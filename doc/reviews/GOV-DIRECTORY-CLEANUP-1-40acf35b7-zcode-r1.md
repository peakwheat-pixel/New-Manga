---
task_id: GOV-DIRECTORY-CLEANUP-1
reviewer: zcode
author: dsh
base_commit: 9ae8aab0a05a447b6330a86efd12a8b2d0ff9a31
reviewed_head: 40acf35b77b528c8b9aa0ad4608ba42074ba61a0
decision: approved
---

# Review：GOV-DIRECTORY-CLEANUP-1（r1 独立审查，zcode）

审查日 2026-10-22；只读审查，未修改除本文件外的任何文件；未执行任何删除/移动/清理命令。Reviewer 未参与本次清理执行。

## 范围与依据

- 审查对象 `40acf35b7`（= 活树 HEAD，实测确认）。提交链：`9ae8aab0a`（base，即 Task 声称的 delivery head）→ `04e222224`（证据提交，新增 6 份证据共 4,278 行）→ `40acf35b7`（转 in_review，仅 5 个 doc 导航文件）。`git diff 9ae8aab0a..40acf35b7 -- tools/ apps/ src/ tests/` 为空——零产品代码与解析器改动。
- 授权：用户 2026-10-22「负责本项目的目录清理，自动完成调查、分类、计划、执行和验收，减少人工参与」，五根盘点范围明确。
- 审查环境披露：主会话 Bash 间歇不可用，git/文件系统/归档实测部分经只读 Explore 子代理执行；tar 仅用 `-t`（列表）与 `-xOf`（提取到 stdout，未落盘解包）。
- 审查重点（依指令）：两项真实删除（合计 1,109.6 MiB / 67,573 文件）的合规性、判定真实性、归档完整性、分类诚实性、保留边界、禁止项、一致性。

## 合规结论

两项删除均满足「已备份 + 可恢复 + 已授权 + 依据充分」，且全程体现保守纪律：

1. **A 项（`G:/CODEX/P02-scratch-build-source`，401.3 MiB / 7,656 文件）**：依据链完整——唯一 ref `refs/heads/main`（tip `ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`）与 detached HEAD（`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`）**均经本 Review 从归档 tar 内只读提取 OID 后在主仓库 `cat-file -e` 独立复核为 REACHABLE**；工作树 tracked 干净、0 untracked（inventory 记录在案）；`.git` 170.9 MiB 为重复对象、`.tmp.driveupload` 为上传临时。删除前先归档 327.1 MiB（tar 清单 7,656 与源文件数相等），删除后实测目录不存在。Git 历史双保险（主仓库对象库 + tar 内完整 `.git`）。
2. **B 项（`G:/CODEX/New Manga.worktrees/*` 40 个目录，708.3 MiB / 59,917 文件）**：判定「无 `.git` ⇒ 不被 Git 管理」成立——tar 清单实测无任何 `.git` 元数据条目（仅 1 个 `M2-I1-r1-review-archive/.gitignore` 文件）；inventory 按 40 目录逐项登记。**删除动作不可能为无差别通配符递归删除**：根下 15.1 MiB 的既有 zip（`M2-I1-r1-review-archive.zip`）实测幸存且同时被复制入归档，若执行了 `Remove-Item ...worktrees/*` 式盲删该 zip 必然消失。删除后实测根下仅剩该 zip（B_root_children=1）。
3. **执行纪律**：先归档 → 清单比对（archive-stage 的 `files_before == files_listed_in_tar`，tar/list exit 0）→ SHA-256 固定 → 删除 → 复验；执行期 `attrib -R` 仅对将删对象清除只读属性，如实披露；`git clean -fdx`/强制 worktree 删除/`reset --hard`/GC/prune/历史改写均未发生（git 终态 heads=1、refs/archive=21、worktree 仅主 checkout、tracked 干净）。
4. **分类极度保守**：cleanup-plan 173 项（executed 2 + pending 171）中无 DELETE_SAFE、无 MIGRATE——除两个整根 ARCHIVE 项外全部 PRESERVE_REFERENCED（50）或 PRESERVE_UNKNOWN（121）；`task-envs`（47 环境 24.6 GiB）、`workspace/builds|temp|tasks|scratch`（约 12.3 GiB）均因「未取得不含唯一产物的证据」保留待逐项核对。无「按名字或 Task 已完成推定可删」的实例。
5. **保留边界实测未动**：`task-envs` 47 目录在（+1 个登记外的 json 文件）；workspace 分类目录齐全；主仓库 1,235 个 untracked 根全为 `??`、非 `??` 0 行，与 inventory 登记一致。

## 逐项验证结论

| 必审项 | 步骤 | 结果 | 证据 |
|---|---|---|---|
| 删除合规性 | 收据/台账核对 + 授权链 | **PASS**：两项均「归档→验证→删除→复验」；授权为用户 2026-10-22 全权清理指令；依据逐项在案（见合规结论 1-2） | execution-receipts、archive-stage、inventory |
| A 项判定真实性 | tar -xOf 提取 `.git/HEAD` 与 `.git/refs/heads/main` → 主仓 `cat-file -e` | **PASS**：tip `ceffb747…` 与 HEAD `7ce3c40c…` 双双 REACHABLE；packed-refs 为空、refs 仅 heads/main ⇒「唯一 ref 可达」成立；tar 另含完整 `.git`（170.9 MiB）作第二恢复路 | 本 Review 实测 |
| B 项判定真实性 | tar 清单构成分析 | **PASS（风险已被合理接受，见特别说明）**：59,917 文件中 34,132（57%）为 `verification/` 证据类，target/node_modules/dist 均为 0，无 .git 元数据；逐目录 40/40 验证在案 | tar -tzf 统计 |
| 归档完整性 | SHA-256 复算 + 条目数复算 | **PASS**：两 tar SHA-256 与字节数**精确匹配**（`be8ea5e9…ed104` / 342,961,510 B；`69ea26de…22dd0` / 373,490,486 B）；非目录条目 7,656 / 59,917 与源文件数逐一相等；`files_before == files_listed` 且 tar 全读成功 ⇒ 打包时点无遗漏，SHA 固定 ⇒ 事后未损坏 | 本 Review 实测 + archive-stage |
| 清单=源数是否充分 | 方法论评估 | **PASS**：tar 由源打包且 exit 0，两独立计数（源文件数 vs tar 清单）相等排除打包遗漏；目录条目（8,465/68,548 原始行）与文件数口径差异已由本 Review 按非目录过滤复核 | 本 Review 复算 |
| 分类诚实性 | cleanup-plan 全量结构 + 抽样 | **PASS（带 F-001）**：173 项无 DELETE_SAFE/MIGRATE；两个 executed 项依据具体（ref 可达/无 .git+归档）；无名字推定 | cleanup-plan.json |
| 保留边界 | 实测 | **PASS**：见合规结论 5 | ls / git status 实测 |
| 禁止项 | git 终态 + zip 幸存反证 + 提交链 | **PASS**：无 clean -fdx/强删 worktree/reset --hard/GC/prune/历史改写；无通配符盲删（zip 幸存为直接反证）；未跟随越界（tar 无异常链接条目） | 本 Review 实测 |
| 一致性 | Task/Handoff/report/inventory/receipts vs 实测 | **PASS（带 F-002）**：P02 不存在、worktrees 仅剩 zip、净释放 426.3 MiB（1,109.6−683.3）数学一致、五根 171 子项（37+47+28+40+19）、untracked 1,235 前后一致 | 各证据交叉 |
| AC1-AC5 MET | 逐条 | **PASS**：AC1（HEAD/租约/worktree 核实在 inventory）；AC2（五根 171 项全登记）；AC3（六类分类、无推定）；AC4（先归档后删、未验证项保留）；AC5（check PASS 3 warnings/audit 0 errors 1983 roots/diff-check 0，NOT_RUN 项如实标注「构建/冒烟未触及」） | inventory/cleanup-plan/report-verification |
| AC6 PARTIAL | — | **PASS（诚实）**：独立 Review（本 r1）与集成复验待完成，如实标注 | Task L51 |

## Findings

| ID | 级别 | 位置 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-001 | P2 | `verification/GOV-DIRECTORY-CLEANUP-1/cleanup-plan.json`（pending 项） | 计划文件的子项状态在整根执行后未回写：pending 171 项中含 40 条 `New Manga.worktrees/<name>` 子项与 19 条 P02 子项，均标 `PRESERVE_UNKNOWN`（理由「按保守原则保留」），但其实际已被两条根级 `executed=true` 的 ARCHIVE 项整根归档删除。影响：`totals.pending=171` 会被误读为「171 项仍待处置」，后续轮次若按 pending 清单逐项核对会与文件系统现实矛盾 | cleanup-plan 抽样（子代理第 9 项）：40+19 子项 pending 与根级 executed 并存 | 集成时在 Task 交付记录注明「pending 中 59 个 worktrees/P02 子项已随根级 ARCHIVE 执行覆盖，不再单独待办」，或在下一轮盘点重新生成 plan；不修改已 pin 证据字节 | open |
| F-002 | P2 | `doc/tasks/GOV-DIRECTORY-CLEANUP-1.md:78`、`doc/handoffs/GOV-DIRECTORY-CLEANUP-1.md:6,13` | 固定 head 漂移：Task 与 Handoff 写「交付 head / 待审查固定 `9ae8aab0a`」且 frontmatter `delivery_head=9ae8aab0a`（= base），但证据实际 pin 在 `04e222224`、本 Review 固定 `40acf35b7`。影响：复审者按文档找恢复点会拿到无证据的 base 提交 | Task/Handoff 原文 vs git log（9ae8aab0a→04e222224→40acf35b7） | 集成时更新 Task 的 `delivery_head`/`reviewed_head` 为实际链（证据 `04e222224`、审查 `40acf35b7`）或在交付记录追加一行说明 | open |

备注（不构成 finding）：

1. `execution-receipts.json` 未固化 P02 仓库的 ref tip OID；`inventory.json` 已记录 head OID（`7ce3c40c`）与 `in_main_history: {refs: 1, all_in_main: true, missing: []}` 结论。tip OID 本 Review 已从 tar 提取并验证可达（`ceffb747`），可复核性由「inventory + tar」共同保证，不构成证据缺口；建议未来此类收据直接内联 OID。
2. tar 原始清单含目录条目（8,465 / 68,548 行），`report.md` 所称「tar 清单 N 项」为非目录文件口径，与 `files_before` 口径一致，无矛盾。
3. `M2-I1-r1-review-archive.zip` 被同时保留原件并复制入归档（双份，无害）；task-envs 的 `ls` 计数 48 = 47 目录 + 1 个 `plan_base_cases.json` 文件，inventory 按 47 目录登记，一致。
4. 两个 tar 的恢复前提是归档目录长期保留——Resource Manifest 已将 `archive/directory-cleanup-20261022` 登记为 `PRESERVE_REFERENCED`，与本 Review 结论互为条件。

## 特别说明：「无 .git 目录的可删判定」是否需要人工层面再审

**不构成阻塞，无需人工逐目录复审。** 理由：(a) 逻辑成立——无 `.git` 即无 Git 管理关系，tar 清单实证 40 目录全无 `.git` 元数据；(b) 真正的删除依据不是「内容无价值」（59,917 文件中 57% 是 verification 证据，保守假定可能含不被任何 Git 保护的内容），而是「全量归档 + 清单与源数逐一相等 + SHA-256 固定 + 归档目录 PRESERVE_REFERENCED」的恢复兜底——风险被可恢复性合理吸收，而非被判定消解；(c) 逐目录人工审 59,917 文件不可行，且 40/40 的 `.git` 检查已逐项执行并登记。**前提条件**：`archive/directory-cleanup-20261022/`（683.3 MiB）及其 SHA 记录必须与 `workspace/archive` 同等级保护，任何对它的处置（删除/移动/再压缩）须专项授权——本 Review 将此列为 approved 的附带约束。

## 结论与复审

**decision: approved（限 reviewed_head `40acf35b7`）。**

两项删除的授权、依据、备份与可恢复性全部独立实证成立（含从归档反向提取 OID 复核 Git 可达性、SHA-256 与条目数精确复算、zip 幸存反证无通配符盲删）；分类保守诚实、保留边界与禁止项全部实测通过；AC1–AC5 的 MET 有证据支撑、AC6 PARTIAL 诚实。两项 P2（计划子项状态陈旧、固定 head 漂移）均为文档层瑕疵，不涉及资产安全，随集成处置即可。

集成要求（dsh 执行后才可 done）：
1. F-001：在 Task 交付记录注明 pending 中 59 个子项已被根级执行覆盖；
2. F-002：更新或注明实际 delivery/reviewed head 链（04e222224 / 40acf35b7）；
3. 集成复验：重跑 `check.ps1`、声明审计、`git diff --check` 记录真实 EXIT，与 report-verification 口径对照；填写 Closeout Record、`resource_closeout_status` 转 complete、同步三份导航；
4. 重申附带约束：`archive/directory-cleanup-20261022/` 两 tar 为 B 项（59,917 文件无 Git 保护内容）唯一恢复层，长期 PRESERVE，处置须专项授权；`task-envs` 与 `workspace` 派生物的后续清理须按 Task §5 另行逐项裁决，本 approved 不构成对它们的任何删除授权。
