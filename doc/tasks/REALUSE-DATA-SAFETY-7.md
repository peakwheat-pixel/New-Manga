---
id: REALUSE-DATA-SAFETY-7
title: SAFETY-6 Review P2 收尾——并发 NRE、证据 pin 规范化、日志格式
kind: quality
governance_version: 3
status: done
approval: follow_up_of_REALUSE-DATA-SAFETY-6_review_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: safety7-reviewer
depends_on:
  - REALUSE-DATA-SAFETY-6
base_commit: 29d06c462
branch: task/REALUSE-DATA-SAFETY-7
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-7
integration_commit: aaed145e9
delivery_head: 306ae09ae
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REALUSE-DATA-SAFETY-7
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-7.md
  - doc/tasks/REALUSE-DATA-SAFETY-6.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-7-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-7-*.md
  - apps/desktop-avalonia/src/**
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-7/**
  - .gitattributes
---

# REALUSE-DATA-SAFETY-7：SAFETY-6 Review 的 3 条 P2

## 来源

[REALUSE-DATA-SAFETY-6 独立 Review](../reviews/REALUSE-DATA-SAFETY-6-review.md)（`approved`，P0/P1=0，P2×3 open）在集成后保留的 3 条 P2。本 Task 承接，不重复 SAFETY-6 的范围。

## 逐条说明

1. **R-001（并发 NRE）**：关闭阅读浮层与在途保存并发时，镜像回调在 `ReaderOverlayViewModel.cs:377-379` 解引用已置 null 的 `_book`，抛未捕获 NRE，且关闭时权威重读被跳过。Reviewer 已在仓外副本用 gate 门控用例真实复现（NRE 堆栈 `:377 ← GoToAsync :308`，EXIT 1）。属实现引入的并发缺陷；Core 已提交的保存不受影响，无数据丢失。
2. **R-002（证据 pin 漂移）**：SAFETY-6 的 11 条 Canonical Evidence pin 以 CRLF 工作树字节为基准，worktree 一致 10/11、blob 一致 6/11；`E-GOV-CHECK` pin 与当前字节不符。
3. **R-003（日志格式）**：`ac1-progress-refresh-test-log.txt` 缺 EXIT 码与完整命令，负向对照为散文摘要（Q-009 口径）。

## 验收标准

- [x] **AC1 R-001 修复**：等待保存前局部固化 book/chapter/page 值，不再解引用可能为 null 的字段；`CloseAsync` 在 `_isSaving` 时仍保证一次权威重读；新增并发用例（关闭 + 在途保存）证明不再 NRE 且刷新发生。 <<MET>>
- [x] **AC2 R-002 规范化**：为 `verification/REALUSE-DATA-SAFETY-6/**` 增加 `.gitattributes` eol=lf 规则并强制 LF 检出；重算 11 条 pin 对照（2 条更新），登记于 `ac2-eol-pin.md`。 <<MET>>
- [x] **AC3 R-003 日志格式**：测试日志含完整命令、EXIT 码与 ISO 时间戳；负向对照给出可复现步骤。 <<MET>>

## 禁止范围

- 不改冻结契约；不动用户数据；不 push 远端；不重写 SAFETY-6 的历史证据字节（只允许在 SAFETY-7 的 evidence 中登记对照）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests`（含新增并发用例） | net9.0 | **PASS 6/6**，EXIT=0 | `ac1-fix-tests.txt` |
| AC1 全量 | `dotnet test tests/NewManga.App.Tests` | net9.0 | **PASS 395 / 0 失败 / 7 跳过（402）**，EXIT=0 | `ac1-fix-tests.txt` |
| AC1 负向 | 移除生产修复、保留测试后重跑并发用例 | net9.0 | **1 失败 / 0 通过，EXIT=1** | `ac1-negative-control.md` |
| AC1 构建 | `dotnet build NewManga.sln -v q --nologo` | net9.0 | **0 警告 / 0 错误**，EXIT=0 | `ac1-fix-tests.txt` |
| AC2 | `.gitattributes` eol=lf + 强制 LF 检出 + `Get-FileHash` 重算 | 只读 | **9 条不变 / 2 条更新**，W/LF 一致 | `ac2-eol-pin.md` |
| AC3 | 日志格式自检 | — | 含 generated_at、命令、EXIT、负向步骤 | `ac3-log-format.md` |

## Canonical Evidence

证据 pin 采用 **blob（LF）基准**，与 AC2 的规范化一致。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-READER-VM | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs` | `306ae09ae` | `22d594d10fcf0f89094ab7510ac63d7fb59532e1038f725854ce48e61d08b073` | CANONICAL |
| E-AC1-TEST-FAKE | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs` | `306ae09ae` | `33106db11704b8f3d9d6d05948a6d018637418207a053671b04cadcc828122be` | CANONICAL |
| E-AC1-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs` | `306ae09ae` | `71785cd438f3b38da53c0f774a224cd153034c86953d900a6b78581b6c2c7d0e` | CANONICAL |
| E-AC1-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-7/ac1-fix.md` | `306ae09ae` | `b31d04e1691872567d7b62628ad0e93d9afa7441fdbd49bde9f8f2c1bff5734b` | CANONICAL |
| E-AC1-NEG | AC1 | `verification/REALUSE-DATA-SAFETY-7/ac1-negative-control.md` | `306ae09ae` | `e3c19b997ac7a21a2e7626acc0686e4f585fe5f77e3da905616e309dc790488b` | CANONICAL |
| E-AC1-LOG | AC1 | `verification/REALUSE-DATA-SAFETY-7/ac1-fix-tests.txt` | `306ae09ae` | `8debe2abc9f81b6cc1b135f9932e303cfd1bdf7e867f245b50c3482887e508a4` | CANONICAL |
| E-AC2-DOC | AC2 | `verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` | `306ae09ae` | `07bf46068ea06b0bc3a05f6b0a03e482758494cd56ed9b586b64275637500da1` | CANONICAL |
| E-AC3-DOC | AC3 | `verification/REALUSE-DATA-SAFETY-7/ac3-log-format.md` | `306ae09ae` | `2263aa38148200f474a9e527a684a6fbfce87eb3de7c0638d910c9a91c849fef` | CANONICAL |
| E-EVIDENCE-INDEX | AC1/AC2/AC3 | `verification/REALUSE-DATA-SAFETY-7/README.md` | `306ae09ae` | `a246badb5564f52bbd1bde2bf1844a1248dc9de748c9d814bac8e6142d4e7bf1` | CANONICAL |
| E-RESOURCE-MANIFEST | Resource | `verification/REALUSE-DATA-SAFETY-7/resource-manifest.json` | `8a343d76f` | `047aed04294f6e9acf6d8c834569bbdd494e23cd774824e35502667f5522807d` | CANONICAL |

## Resource Manifest

资源收口记录：`verification/REALUSE-DATA-SAFETY-7/resource-manifest.json`（schema_version 1）。

- worktree：PRESERVE_REFERENCED（分支 `task/REALUSE-DATA-SAFETY-7`）
- 负向对照临时目录 `tmp/safety7-negctl`：DELETE_SAFE，已删除（`closeout_counts.deleted=1`）
- 用户数据：本 Task 零写操作（不涉及真实数据根）

## 独立 Review

- 报告：[REALUSE-DATA-SAFETY-7-review.md](../reviews/REALUSE-DATA-SAFETY-7-review.md)
- Reviewer：`safety7-reviewer`（Agent Teams 共享任务 `task-4`，fresh context；未参与实现与返修）
- 被审 head：`58596949a`；base `29d06c462`
- 结论：**approved**（P0=0 / P1=0 / P2=5 open，不阻断集成）；AC1/AC2/AC3 均判 **MET**
- 复跑：build 0 警告/0 错误；全量 395/0/7（402）跑 2 次一致；filtered 6/6 跑 6 次全过；`check.ps1` PASS (3 warnings)
- pin 复核：SAFETY-6 12/12、SAFETY-7 10/10 与 `git cat-file blob` 一致；5 条变化 pin 的旧值 == 「blob→CRLF」哈希（纯行尾归一化）
- 负向对照：Reviewer 在仓外副本独立复现 1 failed / EXIT=1（NRE 堆栈 `ReaderOverlayViewModel.cs:377 ← GoToAsync:308`）

## Known P2（open，登记为后续项）

| ID | 级别 | 内容 | 建议处置 |
|---|---|---|---|
| F-001 | P2 | `ac2-eol-pin.md` 与任务卡的 pin 计数与实际不符（实际 12 条 pin / 5 条值变化；文档写 11/2/9；对照表漏 4 条代码 pin） | 修正证据文档计数并补代码 pin 对照（可由 SAFETY-8 或治理小项处理） |
| F-002 | P2 | 负向对照步骤是「提交前工作树」配方，在交付 head 上逐字执行是空操作；无原始输出与 `exit_code=` | 改为 post-delivery 配方（`git checkout <base> -- <path>` → 测试 → `git checkout HEAD -- <path>`）并附输出 |
| F-003 | P2 | filtered 6/6 未进入 canonical 日志；日志命令缺 cwd（仓库根执行会 MSB1009） | 日志记录 cwd/绝对路径并单列 filtered 段 |
| F-004 | P2 | `CloseAsync` 的 `catch (Exception)` 静默吞未知异常 | 限定捕获类型（与 core 类型化集合一致）或记录 Debug/notify |
| F-005 | P2 | 极窄残留竞态：等待窗口内再触发翻页保存时，closing 权威重读仍可能被 `_isSaving` 跳过（不再 NRE） | closing 期间禁用新保存或在 closing 时循环等待 |

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：`main@aaed145e9`（merge `task/REALUSE-DATA-SAFETY-7`，含 `2a0528851` Review 报告提交）
- 集成验证：`check.ps1` PASS (3 warnings)；`dotnet build` 0 警告 0 错误；`dotnet test` 395 通过 / 0 失败 / 7 跳过（402）
- AC 判定：AC1 `MET`、AC2 `MET`、AC3 `MET`
- 已知 P2：F-001 ~ F-005（见上表），不阻断集成，登记为后续项
- 资源：worktree 保留（PRESERVE_REFERENCED）；负向对照临时目录已删除；用户数据零写操作
