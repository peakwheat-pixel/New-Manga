---
id: REALUSE-DATA-SAFETY-9
title: SAFETY-8 Review P2 收尾——判别性断言与证据措辞
kind: quality
governance_version: 3
status: done
approval: follow_up_of_REALUSE-DATA-SAFETY-8_review_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: safety9-reviewer
depends_on:
  - REALUSE-DATA-SAFETY-8
base_commit: 5b888cd70
branch: task/REALUSE-DATA-SAFETY-9
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-9
integration_commit: 9aa6758b6
delivery_head: dcce29a13
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REALUSE-DATA-SAFETY-9
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-9.md
  - doc/tasks/REALUSE-DATA-SAFETY-8.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-9-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-9-*.md
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-9/**
  - verification/REALUSE-DATA-SAFETY-7/**
  - verification/REALUSE-DATA-SAFETY-8/**
---

# REALUSE-DATA-SAFETY-9：SAFETY-8 Review 的 2 条 P2

## 来源

[REALUSE-DATA-SAFETY-8 独立 Review](../reviews/REALUSE-DATA-SAFETY-8-review.md)（`approved`，P0/P1=0，P2×3；R-001 已闭环）保留的 2 条 P2。

## 逐条说明

1. **R-002（AC3 用例不判别修复）**：`ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread` 在 pre-F-005 生产文件下同样通过（close 窗口内 `_isSaving` 仍为 true，旧实现也会早退），只证明"没有回退到更差状态"，不能证明 F-005 门禁生效。Reviewer 在仓外验证了可判别断言：close 窗口内 `PageIndex` 应保持 3（旧代码会变成 5）。
2. **R-003（证据文档提前写入未发生的审查结论）**：`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md:72` 在交付提交中写「SAFETY-8 独立 Review 已按此方式复核并全部一致」——当时该 Review 尚未发生。

## 验收标准

- [x] **AC1 R-002 判别性断言**：在 close 窗口内断言 `PageIndex` 保持 3（`GoToAsync` 被 `_isClosing` 忽略）；用 pre-F-005 生产文件做负向对照，证明该断言在旧代码上失败（EXIT=1）；在 `ac3-closing-gate.md` 明确标注该用例角色（判别性 vs 回归栅栏）。 <<MET>>
- [x] **AC2 R-003 措辞修正**：`ac2-eol-pin.md` 改为只记录已发生的 Review 结论并引用两份已入库报告。 <<MET>>

## 禁止范围

- 不改生产代码（本 Task 只改测试与证据文档）；不改冻结契约；不动用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 交付版 | filtered 判别用例 | net9.0 | **1/1 通过**，EXIT=0 | `ac1-discriminating.md` |
| AC1 负向 | pre-F-005 生产文件（`_isClosing` 0 次）+ 判别用例 | net9.0 | **1 失败 / 0 通过，EXIT=1** | `ac1-discriminating.md` |
| AC1 回归 | 构建 + filtered 7/7 + 全量 | net9.0 | **0 警告 / 0 错误**；filtered **7/7**；全量 **396/0/7（403）**，EXIT=0 | `ac1-fix-tests.txt` |
| AC2 | 文本核对 | 只读 | 两处引用均指向已入库 Review 报告 | `ac2-wording.md` |

## Canonical Evidence

证据 pin 采用 **blob（LF）基准**（`git cat-file blob` → SHA-256）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs` | `dcce29a13` | `dc22432bce2312bc645bdca4f36eb2d31bb20fbc638ce7c5bed579036a4b1394` | CANONICAL |
| E-AC1-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md` | `dcce29a13` | `1b395b9c24de6611bd6f13f92a3d5f0ab10582baf920bb68f6fae4474f8e7a7c` | CANONICAL |
| E-AC1-LOG | AC1 | `verification/REALUSE-DATA-SAFETY-9/ac1-fix-tests.txt` | `dcce29a13` | `83ecb65f92cc2d95e0947b44c72b29972f57bdfef6afea26a5f3655b622193ef` | CANONICAL |
| E-AC2-DOC | AC2 | `verification/REALUSE-DATA-SAFETY-9/ac2-wording.md` | `dcce29a13` | `ce0f7c3a1f8d324f0b8b2b4f96c41299337ac455186bc419600639400ed697ee` | CANONICAL |
| E-AC2-PIN-DOC | AC2 | `verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` | `dcce29a13` | `266f50fe30091d9a6531d881bfb048e20dd9f4cf325dd06530956685e9d25173` | CANONICAL |
| E-AC1-GATE-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md` | `dcce29a13` | `1518a0efceea6cdc48f45c8bbdead5b81d287a152a8a93cdd4343d353eeed64e` | CANONICAL |
| E-EVIDENCE-INDEX | AC1/AC2 | `verification/REALUSE-DATA-SAFETY-9/README.md` | `dcce29a13` | `f9b8ffced0522695ba8726b22ce23d67ec6d67671956fbd8e9635ef49535583f` | CANONICAL |
| E-RESOURCE-MANIFEST | Resource | `verification/REALUSE-DATA-SAFETY-9/resource-manifest.json` | `407d3b1d8` | `3f2573d8db04f61e4584775678d06b77d9fedaa74de04b8ebca35792d8a0d92e` | CANONICAL |

## Resource Manifest

资源收口记录：`verification/REALUSE-DATA-SAFETY-9/resource-manifest.json`（schema_version 1）。

- worktree：PRESERVE_REFERENCED（分支 `task/REALUSE-DATA-SAFETY-9`）
- 负向对照临时日志 `tmp/safety9-negctl.txt`：DELETE_SAFE，已删除
- 用户数据：本 Task 零写操作

## 独立 Review

- 报告：[REALUSE-DATA-SAFETY-9-review.md](../reviews/REALUSE-DATA-SAFETY-9-review.md)
- Reviewer：`safety9-reviewer`（Agent Teams 共享任务 `task-7`，fresh context；未参与实现与证据撰写）
- 被审 head：`40d286e85`；base `5b888cd70`；交付实现 `dcce29a13`
- 结论：**approved**（P0=0 / P1=0 / P2=1 open，不阻断集成）；AC1/AC2 均判 **MET**
- 独立复核：仓外副本换 pre-F-005 生产文件后判别用例 **FAIL（Expected 3 / Actual 5，`:328`）/ EXIT=1**，交付版 PASS/EXIT=0；两次换码构建均 `--no-incremental` 排除增量伪结果
- 复跑：build 0 警告/0 错误；filtered 7/7；全量 396/0/7（403）；`check.ps1` PASS (3 warnings)；卡内 8 条 pin 8/8 MATCH

## Known P2（open，登记为后续项）

| ID | 级别 | 内容 | 建议处置 |
|---|---|---|---|
| R-101 | P2 | `verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md:34-47` 负向对照为精简转录：未写明执行位置（"覆盖工作树"易误读为仓内原地覆盖）、无命令/cwd/host 头、无断言失败明细（Expected 3 / Actual 5 与 `:328`） | 补全转录（执行位置、命令、cwd、失败明细）；实质结论已由 Review 独立复现 |

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：`main@9aa6758b6`（merge `task/REALUSE-DATA-SAFETY-9`，含 `a8a38b595` Review 报告提交）
- 集成验证：`check.ps1` PASS (3 warnings)；`dotnet build` 0 警告 0 错误；`dotnet test` 396 通过 / 0 失败 / 7 跳过（403）
- AC 判定：AC1 `MET`、AC2 `MET`
- 已知 P2：R-101（证据转录完整度），不阻断集成，登记为后续项
- 资源：worktree 保留（PRESERVE_REFERENCED）；负向对照临时日志已删除；用户数据零写操作
