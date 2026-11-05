---
task_id: FEA-12-PREREQ-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现/返修；本子会话 adb50e70-11a7-401d-9d49-a3f02fd4ac5b，父会话 session-8db9dae5-49df-4d09-ac62-696f0805a95c）
reviewer_kind: subagent
base_commit: 035468a81
reviewed_head: 3e37c595b
decision: approved
---

# Review：FEA-12-PREREQ-1（r2 复审；M2-C1 rev 2.13 删除/回收站 wire 注册）

**审查者身份与来源**：DSH 派发的独立上下文 fresh subagent（本会话 id `adb50e70-11a7-401d-9d49-a3f02fd4ac5b`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）。**未参与本卡任何实现、返修、Handoff 或证据生成**；r1 Reviewer（`68898595-4d2b-46a7-8a72-0d4b6ba05db8`）亦未被复用。审查为**只读**：未 commit、push、stash、reset 或修改仓库文件；仅向仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq-r2\` 写日志、临时副本与本报告；未触碰真实用户数据/AppData/外部卷/真实回收站。

**审查对象**：r1 被审 head `5a7c7e028` → r2 修复 commit `26775dfef` + Handoff 提交 `3e37c595b`（r2 交付 head；`reviewed_head`）。`base_commit` 沿用卡内 `035468a81`。审查执行时（15:46–15:52）仓库 HEAD 为 `3e37c595b`；审查期间其他任务又提交了 `90a8c8218`/`280bb7bd0`/`144683876`，报告落盘时 HEAD 为 `f11bff37e`——`git diff --name-only 3e37c595b..HEAD -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md doc/tasks/FEA-12-PREREQ-1.md doc/handoffs/FEA-12-PREREQ-1-035468a81.md verification/FEA-12-PREREQ-1` 始终为空，**不影响本报告结论**。审查期间工作树出现其他任务的未提交/未跟踪写入（FEA-12-DSIM-1 `verification/FEA-12-DSIM-1/`、`doc/tasks/FEA-12-DSIM-1.md` 等），非本 Reviewer 所为，我未触碰；报告落盘时工作树 clean。

## 结论

**decision: approved（P0=0；P1=0；P2=0；P3=4，均为证据标注/措辞小项，不阻塞 done）**。

r1 唯一 P1（R-001）已实质修复：`M2-C1 §5.11.3` 表新增 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 行（`unavailable` / `retryable=true`），表 code 集合 ⊇ 两个 `ErrorView.code` 集合在**独立解析**与**独立复跑审计脚本**下均成立；旧 head 文档副本判别性 FAIL 被独立复现。r2 只做最小返修（文档 1 行新增 + 1 行措辞 + 审计断言 + 测试注释 + 证据整理），`src/**` 零改动、既有断言零改动、冻结契约/18 pins 零改动。AC1 恢复 **MET**；AC2–AC5 可延用 r1 结论并以本报告独立复跑补强。

| 级别 | 数量 | 摘要 |
|---|---|---|
| P0 | 0 | — |
| P1 | 0 | R-001 已核销 |
| P2 | 0 | R-002 已按 DSH 裁决登记 defer CORE（本卡未改白名单） |
| P3 | 4 | R-004 残留一句措辞（R2-01）；EV-01 审计日志 provenance（R2-02）；审计脚本 `DeliveryCommits` 未覆盖 r2 修复 commit（R2-03）；`gates.log` G1 未记录 r2 pins head 而 Handoff 写 `(r1/r2)`（R2-04）。均不改变事实成立性 |

## R-001 核销（P1 → 已修）

- **修复事实**：`git diff 5a7c7e028..3e37c595b -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 仅 2 个 hunk、`2 insertions / 1 deletion`：①`§5.11.1a` 原有的 r1 新增行改写（R-004，该行不在 base，故不增加「既有行变更」）；②`§5.11.3` 表新增一行。新增行位于 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:848`：
  `| 删除影响清单计算失败（DB 错/临时故障；§5.11.1a/§5.13） | BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE / unavailable / retryable=true | 清单未生成即失败，零副作用（内容行/保护状态/DB/文件均不变）；可显式重试；不得降级软删除，不得伪报为空清单。 |`
  与 `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:86`（`unavailable` / `true` / 清单计算失败、零副作用）及 `:104`（零副作用）一致；语义与 C-04b §2.3/§2.4 无冲突。
- **表 ⊇ 两个 ErrorView 集合（独立验证，不依赖交付脚本）**：我用 Python 独立解析 head 文档：`§5.11.3` 表 code=16、单条视图 code=11、批量视图 code=12，`missing_from_table=[]`；对 `5a7c7e028` 文档副本解析：表 code=15，`missing=[BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE]`（`r2-independent-parse.log`）。对应正文：表行 `:848`、单条视图 `:875`、批量视图 `:885`、批量 `items[].error_code` 白名单句 `:852`、§5.13 预览错误表 `:966`。
- **判别性审计**：`verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1:92-191` 新增「表 ⊇ 两视图 + 5 个 rev 2.13 码」断言，并纳入 `:194-202` 的 PASS 条件。独立复跑：
  - worktree（HEAD `3e37c595b`）：`ADDITIVE_AUDIT=PASS`，EXIT 0，`missing_from_s531_table=0`、`rev213_codes_missing_from_error_tables=0`（`r2-audit-worktree.log`；worktree_head=`3e37c595b`）。
  - 旧 head 文档副本（`git show 5a7c7e028:<path>` 写入仓外，内容 hash `0dcfcfe8…` 与 r1 文档一致）：`ADDITIVE_AUDIT=FAIL`，EXIT 1，`missing=BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（`r2-audit-oldhead.log`）。判别力成立。
- **additive 形态**：`git diff --numstat 035468a81..3e37c595b -- <M2-C1>` = `166 / 2`；`-U0` removed 行仅 2 条——文档状态行 rev 2.12→2.13、§11 `Permanent-delete user policy` 行（ADJ §D2 授权）；无其他既有行改动。文档 rev 2.13（`:24`）、`src/bootstrap/core_service.py:302 PROTOCOL_MINOR=3` 未变；既有 delete per-command minor 仍 10（`HostCommandRegistry.cs:308/:340`）。**R-001 核销。**

## P3 核销（R-003/R-004/R-005/R-006）与 R-002 登记

| Finding | 结论 | 证据 |
|---|---|---|
| R-003 `check-final.log` 自指 / 4 vs 3 warnings | **已修**：`logs/check-final.log` 从 evidence_dir 移出；副本 `G:\CODEX\New Manga.workspace\agent-output\fea12-prereq-impl\FEA-12-PREREQ-1\check-final-r1.log`（1212 bytes，sha256 `7772…`，manifest 已列）；原始 sidecar stderr/wire 日志同样移出并保留副本。**独立核对 13/13 个被移文件与删除前 git blob 内容 LF 归一后逐一相同**（manifest 25/25 bytes+sha256 亦匹配）；判别力 JSON（EV-08/09/10）留在仓内。当前交付文档无引用断裂；仅 r1 历史 Review（`doc/reviews/FEA-12-PREREQ-1-r1.md:55`）引用 r1 head 的 `logs/check-final.log`，属历史记录（副本已在 workspace/manifest 登记）。独立复跑 `check.ps1` = **PASS（3 warnings：非终态 Task 15 / STATUS 80% / REBASELINE_PLAN 80%；无 evidence_dir 告警）**，EXIT 0（`r2-check.log`）。 |
| R-004 §5.11.1a「拒收」措辞 | **基本已修，残留一句不准确（R2-01）**：`:809` 已明确「Host 既有 delete 路径保持 legacy 透传（只取已知键、不新增未知键拒绝）」；但末尾「未知键由 Core 的 closed-shape 校验拒绝」与 Host 实际行为不符——Host 单删只重建已知键（`HostCommandDispatcher.cs:458-473`，`:471` 只转 `inventory_digest`、`inventory_digests` 不转发），未知键不转发，Core 不会收到因而不会拒绝。 |
| R-005 B1/B2 注释过度声明 | **已修**：`CommandWiringB1Tests.cs`/`CommandWiringB2Tests.cs` 的 r2 diff **仅为 `//` 注释**，无断言/集合/测试名改动；注释已改为「reconstructed pre-registration allow-list = NEW projector minus the 5 codes」，并注明真实基线 delete 族无白名单。135/0/15 复跑与 r1 一致。 |
| R-006 基线日志 `existing=l` | **已修（脚本）/已注明（日志）**：`tools/baseline-negative-control.ps1:79` 已为 `existing=single`；已提交的 `logs/baseline-negative-control-base-035468a81.log:22` 保持原字节 `existing=l`；Handoff`:131` 注明 cosmetic、无判别含义。 |
| R-002 `CORE_CAPABILITY_MISSING` 未进白名单 | **按裁决登记，不修白名单**：`doc/tasks/FEA-12-PREREQ-1.md:128` 与 `doc/handoffs/FEA-12-PREREQ-1-035468a81.md:125` 明确 CORE 二选一（(a) additive 加入 `AllowedDeleteTrashErrorCodes` + 投影测试；(b) probe 错误在 `HostRuntime` 层抛出 + 判别性测试）。`src/**` 在卡提交零改动；白名单仍 20 码（15 既有 + 5 新，无 `CORE_CAPABILITY_MISSING`）。注意：`FEA-12-CORE.md` 正文尚未写入该二选一（属 DSH 释放 CORE 时的卡编辑责任；本卡 allowed_paths 不含该文件，不构成本卡返修项）。 |

## 独立复跑（只读；日志在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq-r2\`）

| 场景 | 命令 / 环境 | 结果 | 日志 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18，EXIT 0** | `r2-pins.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-PREREQ-1.md` | **PASS（3 warnings），EXIT 0** | `r2-check.log` |
| 命令治理过滤测试 | `dotnet test .../NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Command"` | **135 passed / 0 failed / 15 skipped，EXIT 0** | `r2-dotnet-command.log` |
| sidecar 冻结 Core 负向 3/3 | 同 csproj，filter `Fea12NewCommands\|B1Commands_ExecuteAgainstFrozenCore\|B2Commands_ExecuteAgainstFrozenCore`；`NEWMANGA_CORECLIENT_SIDECAR_DIR=…\HOST-CORECLIENT-1\sidecar-copy`；`NEWMANGA_EVIDENCE_DIR` 指仓外 | **3/3 passed，EXIT 0**；独立生成的 `fea12-old-core-negative-control.json` 与 EV-08 sha256 **byte-identical**（`ab817eac…`）；ns-b1/b2 JSON 仅随机 ID/端口不同（非判别字段） | `r2-dotnet-sidecar.log`、`sidecar-evidence/` |
| 审计（修复后） | `pwsh -NoProfile -File verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1` | **PASS，EXIT 0**，`missing_from_s531_table=0` | `r2-audit-worktree.log` |
| 审计（旧 head 文档） | 同上 `-DocFile <git show 5a7c7e028 文档副本>` | **FAIL，EXIT 1**，`missing=BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` | `r2-audit-oldhead.log` |
| Canonical Evidence | 逐条对照 Task EV-01…EV-20 的 sha256 | **20/20 OK**（EV-01 `3e0b…`、EV-02 `e5c2…`、EV-15 `5152…`、EV-18 `a00c…`、EV-19/20 工具均匹配） | 本报告复核 |
| agent-output manifest | manifest 25 个副本逐文件 bytes+sha256 | **25/25 OK**（含 `check-final-r1.log`、stderr/wire 副本） | 本报告复核 |

**未重跑项（引用，不冒充实测）**：全量 .NET 与全量 pytest 未由本 Reviewer 重跑（本卡无 Python 产品改动；全量 .NET 会重写 `verification/FEA-09`（既有测试副作用）且耗时较长）。引用 r1 实测：全量 .NET **首跑 1 failed（flaky：`FluentResidual2VisualEvidenceTests` 与 `WireLogSourceRedactionTests` 跨程序集证据写竞争）→ 复跑 1403 passed / 0 failed / 79 skipped**；pytest **3073 passed / 10 skipped**。**flaky 不作为稳定 PASS**：首跑失败已单列，归于既有测试债务（两测试均非本卡改动）。我运行 sidecar 后 `verification/FEA-09/logs/wire-redacted.ndjson` 被既有测试重写，已执行 `git checkout -- verification/FEA-09` 恢复（当前 clean）；未提交任何恢复动作。

## 范围 / 冻结核对

- **r2 本卡 delta 仅限 allowed_paths**：`26775dfef` 24 files（B1/B2 测试、M2-C1、Task、`verification/FEA-12-PREREQ-1/**`）+ `3e37c595b` 1 file（Handoff）。与 r1 的两个交付 commit 合并去重后 **44 files，越界 0**（B1/B2 在卡 allowed_paths，证据目录在 `verification/FEA-12-PREREQ-1/**`）。
- **r1→r2 范围的「越界观感」**：`git diff --name-status 5a7c7e028..3e37c595b` 含 10 个 commit（FEA-11-LINEAGE-1 r2/r3、FEA-12-DSIM-1、Lead 窄批 `2fd395548`、r1 Review 落盘 `1780c1f89` 等）；`src/**`、`doc/STATUS.md`、`REBASELINE_PLAN`、`TASK_LEDGER` 等差异全部归其他任务/Lead 文档 commit，**不是本卡 delta**（`git log --graph` 已核；r1 Review 已同样说明）。
- **产品代码零改动**：`08b359251`、`5a7c7e028`、`26775dfef`、`3e37c595b` 四个本卡 commit 的 `src/**` 文件数均为 **0**；`git diff 5a7c7e028..3e37c595b -- apps/desktop-avalonia/src/NewManga.CoreClient/` 为空。r2 测试 diff 仅 B1/B2 注释。
- **冻结契约 / pins**：`git diff 035468a81..3e37c595b -- doc/plan/FEA-C*.md` **零 diff**；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` **零 diff**；`verify_pins.ps1` **18/18 PASS**。`PROTOCOL_MINOR=3` 未改（已核 `src/bootstrap/core_service.py:302`；该文件在 base..HEAD 的改动全部来自 FEA-11-LINEAGE-1 的 r2/r3 commit，非本卡）。既有 delete 命令 per-command minor 仍 10（`HostCommandRegistry.cs:308/:340`）。
- **证据整理不是「删除证据」**：移出 evidence_dir 的 `check-final.log` 与 sidecar stderr/wire 原始日志在 workspace agent-output 有副本（manifest 25/25 哈希匹配；13/13 与删除前 git blob 内容 LF 归一后逐一相同）；判别力 JSON（EV-08/09/10）保留；`REGISTRATION-COMPARISON.md` 等当前交付文档未引用被移除的 wire/stderr 路径；`check.ps1` 不再出现 evidence_dir 未登记告警。**无放宽断言、无删测试**。

## AC1 回归判定（修复后可 MET？）

**AC1 = MET**。9 项登记点复核：

1. §3.2 目标 wire bullet — `:132`；
2. §5 catalog 5 行 — `:163-167`（preview 11 / trash 13）；
3. §5.11.1a digest 字段 + 两级校验 — `:785-800`；
4. §5.11.3 表 **两行** + 两个 ErrorView + 批量 items 白名单 — `:847-852`、`:875`、`:885`；
5. §5.13 preview + `DeletePreviewItem` PD-01 三项 — `:913-970`（`:966` 预览错误表含 PROTECTION 码）；
6. §5.14 回收站 4 命令 + 3 `TRASH_*` 码 — `:974-1023`；
7. §11 对账行 FROZEN — `:1440`；
8. §12 释放边界 — `:1470`；
9. Revision history 2.13 — `:28`；文档状态 `:24`。

另外：3 个 capability 名在 §5.13/§5.14 与 Host 常量中齐备；`DeletePreviewItem` 未加 C-14 pending-operation 字段（全文无 `pendingOperation/pending operation` 命中）；`PROTOCOL_MINOR=3`、既有 delete minor 10 未变。r1 的 AC1 PARTIAL 仅因 R-001，现修复，故可恢复 MET。

**AC2–AC5**：AC2（Host 投影/命令治理测试）可延用 r1 且 r2 未动产品代码（135/0/15 本次复跑）；AC3（基线 negative control + 冻结 Core 3/3 + EV-08 byte-identical）成立（r2 仅改测试注释，结论不变）；AC4 以本次 pins/check/命令治理/负向 + r1 全量实测（首跑 flaky 已分列）成立；AC5（Task/Handoff/证据/EV 20/20）成立。

## Findings（均为 P3，不阻塞）

| ID | 级别 | 位置 | 问题 | 最小返修点 |
|---|---|---|---|---|
| R2-01（R-004 残留） | P3 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:809`（Task `:100` 同样表述） | 末句「未知键由 Core 的 closed-shape 校验拒绝」与 Host 实际行为不符：Host 单/批量 delete 只写已知键（`HostCommandDispatcher.cs:458-473`），未知键不转发，Core 不会拒绝。主句「Host legacy 透传、不新增未知键拒绝」已正确。 | 改为「Host legacy 路径只取已知键、未知键被丢弃；Core closed-shape 只对实际到达 Core 的键生效」；或补 Host 单删 `inventory_digests` 行为测试。可与 closeout 同批。 |
| R2-02 | P3 | `verification/FEA-12-PREREQ-1/logs/rev213-diff-audit.log:4`（Handoff `:42`/Task `:119`） | 该 PASS 日志的 `worktree_head=94a12e93f`（R-001 修复尚未提交时的脏工作树），而 Handoff 标为「r2 修复后 head `26775dfef`」。PASS 内容本身可复现（本 Reviewer 在 `3e37c595b` 复跑 PASS），但该日志不能自证对应 commit。 | 在 r2 head 复跑审计并更新 EV-01/handoff；或把 Handoff 标注为「提交前工作树实跑，r2 head 由复审复跑」。 |
| R2-03 | P3 | `verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1:17` | `DeliveryCommits` 仅 `08b359251,5a7c7e028`，未含 r2 修复 commit `26775dfef`（Handoff 声明的 `delivery_head`）；因此 `delivery_src_changed_count=0` / `delivery_pinned_contract_count=0` 的 guard 不覆盖修复 commit。独立 `git show` 已证 `26775dfef`/`3e37c595b` 的 src/pinned 均为 0。 | 把 `'26775dfef'`（必要时加 `'3e37c595b'`）加入 `DeliveryCommits` 并重跑；或注明 guard 只覆盖 r1 交付 commit。 |
| R2-04 | P3 | `verification/FEA-12-PREREQ-1/logs/gates.log:15`（Handoff `:46`） | G1 只记录 `R1 HEAD: c2b40c9f3`，但 Handoff 写 pins「PASS 18/18（EXIT 0；r1/r2）」，缺少 r2 运行记录。本次独立复跑 18/18 PASS（事实成立），属证据标注不一致。 | 补记 r2 pins 的 head/EXIT；或 Handoff 改为「r1 实测 + r2 复审复跑（本 Review 记录）」。 |

## done vs changes 意见

**approved**，可进入 DSH 集成验证与 closeout。R-001 已实质修复，AC1 恢复 MET，无 P0/P1/P2；R2-01…R2-04 是措辞/证据标注小项，不要求 r3。建议 closeout 时顺手处理：

1. R2-01 一句措辞（`§5.11.1a` 末句）与 Task `:100` 同步修正；
2. R2-02/R2-03/R2-04 的证据 provenance（在最终 head 复跑审计、把 `26775dfef` 纳入 `DeliveryCommits`、补 r2 pins 记录）；
3. DSH 在 `FEA-12-CORE` 卡写入 R-002 二选一（加入白名单或 HostRuntime 层抛出）并在 CORE release note/判别性测试落实；
4. closeout 时按 Task 的 Resource Manifest 处置 baseline worktree/temp/agent-output（**保留** baseline worktree 直到集成完成）。

全量 .NET 的既有 flaky 债务仍应在后续门禁中保留「首跑+复跑」记录，不得写成稳定 PASS。

## 自审声明

- 我是 DSH 派发的独立上下文 fresh subagent（会话 `adb50e70-11a7-401d-9d49-a3f02fd4ac5b`），**未参与** FEA-12-PREREQ-1 的实现、r2 返修、Handoff 或证据生成；r1 Reviewer 未被复用。
- 审查只读：未 commit/push/stash/reset/checkout 他人改动；未修改仓库文件。唯一对仓库写操作是按审查指令恢复**我自己测试**重写的 `verification/FEA-09`（`git checkout -- verification/FEA-09`，恢复后该路径 clean），已在本报告记录。
- 日志与临时旧文档副本全部写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq-r2\`；未触碰真实数据/AppData/外部卷/真实回收站。
- 事实以 Git、文件内容、独立命令与测试结果为准；交付日志仅作引用（EV/日志），独立复跑结果单列；未把 flaky 写成稳定 PASS，未把未跑项写成实测。
