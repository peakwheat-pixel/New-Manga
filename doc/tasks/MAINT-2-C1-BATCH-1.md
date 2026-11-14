---
id: MAINT-2-C1-BATCH-1
title: C1 批次：8 项 limitation 补实现（READ-2 控件 / FONT 负例与压测 / LIB 投影与边界 / AI-1 清理 / PIN-BASIS suite）
kind: implementation
governance_version: 3
status: in_progress
disposition: "DoD §3 收口批（2026-11-14 DSH 释放）；依据 MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14 §3-C1-1..C1-8"
approval: DSH 2026-11-14 释放（DoD §3 未达成的唯一缺口）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 1e272c5f6
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/MAINT-2-C1-BATCH-1
allowed_paths:
  - doc/tasks/MAINT-2-C1-BATCH-1.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md
  - doc/reviews/MAINT-2-C1-BATCH-1-*.md
  - verification/MAINT-2-C1-BATCH-1/**
  - src/domain/**
  - src/infrastructure/sqlite/**
  - src/bootstrap/**
  - src/application/**
  - tests/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/tests/**
out_of_scope:
  - 冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）；除 4A/4B 已授权的 C-07 外不得改动
  - schema/DDL 变更、依赖变更、Release Gate、远端写操作
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# MAINT-2-C1-BATCH-1：8 项 C1 limitation 补实现

## 来源

[limitation 处置矩阵](../reviews/MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14.md) 的 §3 列出 C1 的 8 项 `IMPL`；DSH 终裁明确「8 项落地前 DoD §3 未达成」。本卡即其落地载体。

## Acceptance Criteria

- [ ] **AC1（C1-1 / L-R2-1）READ-2 可见控件**：书签面板、整书进度、reset 确认三处的**可见控件**接线（VM 与测试已覆盖，缺视图层）；判别测试断言控件存在且绑定到既有命令。
- [ ] **AC2（C1-2 / L-F1-2）FONT wire 负例**：补 wire 级 `FONT_DELETE_FAILED` 负例测试（storage 侧已覆盖，wire 侧缺）。
- [ ] **AC3（C1-3 / L-F1-3）FONT 大文件/并发**：补大文件与并发导入的边界测试（占用文件保留 `KEEP`，不在此列）。
- [ ] **AC4（C1-4 / L-L1-1）LIB `kind` 投影**：`ChapterSummary` 增 `kind` 投影并由 wire 透出；判别测试断言字段存在且与存储一致。
- [ ] **AC5（C1-5 / L-L1-2）LIB `custom_rank` 读回闭环**：`custom_rank` 从 write-only 变为可读回；判别测试覆盖写入→读回一致（排序 UI 属 C3-3，不在本卡）。
- [ ] **AC6（C1-6 / L-L1-4）LIB 64 位边界**：补 R3-001 的 64 位边界校验与断言。
- [ ] **AC7（C1-7 / L-AI1-6）AI-1 清理**：删除死方法 `reassign_references`、修正 `test_issue_markers` 旧注释。
- [ ] **AC8（C1-8 / L-PB1-1）PIN-BASIS 专项 suite**：复跑专项 suite 并保留原始输出为证。
- [ ] **AC9 回归与门禁**：受影响全量测试 0 failed；`check.ps1` / `verify_pins` / `generate_api_inventory --check` 三项不降级；无 `src` 外的契约字节改动。

## 允许修改范围

见 front matter `allowed_paths`。允许分多个 commit 按子项落地（建议按栈分批：Python/Core 一批、Avalonia 一批），每批自身测试全绿。

## 禁止范围

冻结契约字节、schema/DDL、依赖、Release Gate、远端写、`doc/STATUS.md` / `REBASELINE_PLAN` / `TASK_LEDGER`。

## 测试要求

每项至少 1 条判别测试；Python 用 `C:\Python314\python.exe -m pytest`，C# 用 `dotnet test`。全量回归：pytest 与 `NewManga.App.Tests` 不得出现新增 failed。

## 风险

- AC4/AC5 触 `ChapterSummary`/wire 透出：若需改冻结契约（C-02/C-03 等），**先回卡报 DSH**，不得擅自 UNFREEZE。
- AC1 触 Avalonia 视图：可能引发现有 UI 测试的结构断言失效，需同步更新而非删除断言。
- 本卡范围较大，允许分批交付；每批必须自身可验收。

## 证据计划

`verification/MAINT-2-C1-BATCH-1/README.md` + `logs/`（测试与门禁原始输出）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |

## Closeout Record

- 未关闭（当前 `in_progress`）。

## DSH 裁决（2026-11-14）

### AC4 / AC5：**批准方案 A（契约 additive 修订）**

- **授权**：写 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md` 载体，把 `kind`（`paged|webtoon`）与 `custom_rank`（`integer|null`）登记为 `list_chapters` 的**可选字段**（additive widening，**协议 minor 不 bump**）。
- **依据**：`M2-C1:194` 的 `ListRegions` 1.5 additive widening 先例（加可选 `geometry`/`page_size`，minor 不变）。
- **约束**：只加可选字段，不改既有四字段、不改键集语义、不动其它冻结字节；载体 §6 复核记录必须留 `pending`（作者不得自写 approved）。
- **与矩阵一致性**：两项在 limitation 矩阵中为 `IMPL`，本裁决维持该处置，不改为 OUT。
- **实现顺序**：载体 → Core 加键 → 客户端 DTO/解析 → AC4/AC5 判别测试（3 个 commit）。

### AC8：**接受「以 validation clone 为可比基线」**

- 理由：governance suite 断言的是**仓库字节**（EOL/autocrlf 语义），主工作树与 validation clone 的检出字节本就不同，两者数字不可直接比；该漂移与 C-07 pin 的 `GOV-EOL-PIN` 既有债同源。
- **要求**：① 证据 README 写明「**复跑留证，不等于复跑通过**」；② 两套原始输出（validation clone 的 3F/61P 与主工作树的 12F/56P）都保留；③ 不得把 AC8 写成 `MET`，只能写「留证完成 + 基线不可比已说明」；④ 若要真正清零，另开 EOL 口径卡。
- **本卡 AC8 判定**：`PARTIAL`（留证完成、基线漂移已披露且经 DSH 裁决）；不阻断 DoD §3 的其余 7 项。

### AC1：**批准执行**（Avalonia 视图层，等 Python 批收尾后做）

- 若引发现有 UI 结构断言失效，必须同步更新断言并说明，不得删除。