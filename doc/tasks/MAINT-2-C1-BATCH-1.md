---
id: MAINT-2-C1-BATCH-1
title: C1 批次：8 项 limitation 补实现（READ-2 控件 / FONT 负例与压测 / LIB 投影与边界 / AI-1 清理 / PIN-BASIS suite）
kind: implementation
governance_version: 3
status: closed_with_limitations
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
integration_commit: a19ebdead
delivery_head: b122fb926
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1（C1-1 / L-R2-1）READ-2 可见控件**：书签面板、整书进度、reset 确认三处的**可见控件**接线（VM 与测试已覆盖，缺视图层）；判别测试断言控件存在且绑定到既有命令。 <<MET>>
- [x] **AC2（C1-2 / L-F1-2）FONT wire 负例**：补 wire 级 `FONT_DELETE_FAILED` 负例测试（storage 侧已覆盖，wire 侧缺）。 <<MET>>
- [x] **AC3（C1-3 / L-F1-3）FONT 大文件/并发**：补大文件与并发导入的边界测试（占用文件保留 `KEEP`，不在此列）。 <<MET>>
- [x] **AC4（C1-4 / L-L1-1）LIB `kind` 投影**：`ChapterSummary` 增 `kind` 投影并由 wire 透出；判别测试断言字段存在且与存储一致。 <<MET>>
- [x] **AC5（C1-5 / L-L1-2）LIB `custom_rank` 读回闭环**：`custom_rank` 从 write-only 变为可读回；判别测试覆盖写入→读回一致（排序 UI 属 C3-3，不在本卡）。 <<MET>>
- [x] **AC6（C1-6 / L-L1-4）LIB 64 位边界**：补 R3-001 的 64 位边界校验与断言。 <<MET>>
- [x] **AC7（C1-7 / L-AI1-6）AI-1 清理**：删除死方法 `reassign_references`、修正 `test_issue_markers` 旧注释。 <<MET>>
- [ ] **AC8（C1-8 / L-PB1-3）PIN-BASIS 专项 suite**：复跑专项 suite 并保留原始输出为证。 <<PARTIAL: 复跑留证完成、基线不可比已裁决；不得写 MET>>
- [x] **AC9 回归与门禁**：受影响全量测试 0 failed；`check.ps1` / `verify_pins` / `generate_api_inventory --check` 三项不降级；无 `src` 外的契约字节改动。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/AC4-AC5-CONTRACT-BLOCKER.md | ac69bb955 | 8b7c4cb78a75b805b3fad26f66d0983bfacfd56d1b6633cddf4fc6f2662d5676 | canonical |
| EV-2 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/README.md | 2d985956a | 0514c4689810f85aca7f36f83dfd57823cd9b5d369e6f391f490805c761fb54d | canonical |
| EV-3 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/logs/gates-2026-11-14-final.log | b122fb926 | d61c6f7b4f19e014b12d780e600720bc017f6cb4dccbf763eee26fff5b3a01f0 | canonical |
| EV-4 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/logs/pin-basis-governance-suite.log | ac69bb955 | 430f81a1f04beb5047a988c267b32ab6f2da1a5b32320ec7db77a5584cbd644b | canonical |
| EV-5 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/logs/pytest-full-after-ac45.log | b122fb926 | 19aa95733dbed0494c4c220af362fec0c9e85726dfbc5c739c3c9bdb2545ee24 | canonical |
| EV-6 | DoD SS3 | verification/MAINT-2-C1-BATCH-1/logs/pytest-full.log | ac69bb955 | f7c16cf7ccd35039e1661ba42f6deec8b35440075f0d5ead05f5c308acaeefa6 | canonical |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |
| evidence（仓库） | `verification/MAINT-2-C1-BATCH-1/**` | NOT_APPLICABLE | 仓库内 | `verification/MAINT-2-C1-BATCH-1/EV`（见 Canonical Evidence） | 测试/门禁原始输出已保留 |
## Closeout Record

- **收口（2026-11-14，DSH）**：AC1–AC7/AC9 `MET`；**AC8 `PARTIAL`**（r1 复核与 DSH 裁决口径：复跑留证完成、validation clone 为唯一可比基线、两套原始输出保留；**不得写 MET**）。r1 独立复核 `approved`（P0=0/P1=0/P2=5），P2-1/2/5 已修、P2-3 已修（`a19ebdead`，测试缺口已披露）、P2-4 登记 limitation。
- **limitation 清单**：① P2-3 降级路径无 runtime 注入 seam，无单元级判别测试；② AC8 基线不可比；③ AC1 的 UI 打磨项（`fluent-reader-title` 定位、书签面板布局、顶栏长文案）；④ AC4/AC5 依赖 M2-C1 rev 2.16（M2-C1 无 pin 体系）。
- 删除/迁移/归档：0。

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

## r1 复核处置（2026-11-14）

r1：**`approved`**，P0=0 / P1=0 / P2=5 / P3=2（报告 [`MAINT-2-C1-BATCH-1-r1.md`](../reviews/MAINT-2-C1-BATCH-1-r1.md)；被审 head `b122fb926`）。独立复跑：pytest 3544/0、App.Tests 914/0、Host 321/0、CoreClient 180/0、四门禁 EXIT=0。

| P2 | 处置 |
|---|---|
| P2-1 `M2-C1:30` 状态行仍 2.15、history 缺 2.16 | **已修**（状态行改 2.16；history 增 2.16 条目） |
| P2-2 未写「每个存活章节必须返回 `kind`」 | **已修**（写入 2.16 条目） |
| P2-5 README:49 旧 commit 描述 | **已修**（限定为「AC8 复跑时点」） |
| P2-3 `ChapterSummary.Parse` 抛 `FormatException` 未被 `ListChaptersAsync` 捕获，违约行可能绕过「降级为空列表」 | **必须修**（真实降级语义缺口，不得登记为 limitation）；下一轮派 |
| P2-4 AC1 的 `fluent-reader-title` 定位脆弱 / 书签面板无 `MaxHeight`·`ScrollViewer` / 底栏 2s 自动隐藏会带走面板 / 顶栏长文案可能溢出 | **登记 limitation**，属 UI 打磨，另开卡 |

**载体 §7 复核记录**：本卡即 r1 复核的引用源，`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md` §6/§7 以本表为准（DSH 补记）。

### DoD §3 判定：**条件达成**

7 项 `<<MET>>` + **AC8 `<<PARTIAL>>`**（DSH 2026-11-14 裁决口径：复跑留证完成、validation clone 为唯一可比基线、两套原始输出保留）+ **P2-3 待修**。

**不得写成 8/8 MET 或 AC8 通过。** P2-3 落地后本卡方可 `done`。

## P2-3 修复（2026-11-14）

- **改动**：`apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` 的 `ListChaptersAsync` catch 过滤新增 `FormatException`，与 `ChapterSummary.Parse` 的严格化对齐；违约行现在**降级为空列表**而不是逃逸到 UI。
- **为何必须修**：r1 指出 `Parse` 收紧后抛 `FormatException`，而 catch 只认 `CoreOperationException/SidecarException/BridgeException/OperationCanceledException/IOException` —— 一条契约违约行会让整个 `ListChaptersAsync` 抛出，绕过 `:919-922` 与 `:946-950` 的「降级为空/空列表」不变量。
- **判别测试的诚实缺口**：`HostController` 只能经 `HostOptions` 构造，**无 runtime 注入 seam**，无法在单元层构造违约 payload 触发该 catch。因此本项只有：
  ① `ChapterSummary.Parse` 的严格性测试（`Parse_MissingFrozenKey_Throws`，既存）；
  ② 1 行 catch 过滤的代码审查；
  ③ 全量 App.Tests 回归（build 0 error、0 failed）。
  **不写成"已带判别测试"。** 建议后续在 gated 集成用例补真实验证，属已披露缺口。
- 该缺口与本卡 AC1/AC2 的 gated 缺口同类，一并记入 limitation。