---
id: REALUSE-DATA-SAFETY-3
title: 修复真实使用自查 B2 核心链路——Console 分区接线、Run 列表、重复读取、错误码本地化
kind: fix
governance_version: 3
status: in_review
approval: user_authorized_2026-10-30_self_audit_repair
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless
depends_on:
  - REALUSE-DATA-SAFETY-2
base_commit: 15efbcfb0
branch: task/REALUSE-DATA-SAFETY-3
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3
integration_commit: null
delivery_head: 569e4fa56
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-3
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-3.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-3-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-3-*.md
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/**
  - src/**
  - verification/REALUSE-DATA-SAFETY-3/**
---

# REALUSE-DATA-SAFETY-3：B2 核心链路可达（审计 DEFECTS.md 的 B2 剩余项）

## 为什么先做这一批

真实使用自查（`G:\CODEX\New Manga.workspace\tmp\self-audit\DEFECTS.md`）把缺陷分成四批。B1（数据安全）与 REALUSE-DATA-SAFETY-2（MA-02/04/05 诚实性）已完成，但审计认定的 B2「核心链路可达」目标——**让用户能把「导入 → 检测 → 翻译 → 导出」跑通**——仍未达成：控制台缺入口、任务队列要求手抄 `run_id`、错误码直接暴露 Core 枚举。

## 范围

- **MA-06**：Console 9 个分区里仍有 3 个「待接入」（设备与模型、缓存与版本清理、插件与 Hooks；备份与恢复已在 REALUSE-DATA-SAFETY-1 接线）。其中「模型/Provider 配置」是 MA-02 指引的实际落点，必须有 UI 入口。
- **MA-07**：「任务与队列」分区要求用户手工输入 `run_id`，冻结契约无 List Run。需要在不改冻结契约的前提下给出可用路径（例如本会话已知 Run 的本地索引 + 明确说明外部 Run 需 run_id），或经 DSH 裁决扩展契约。
- **MA-08**：启动期 `ListBooks`×3、`list_chapters`×2 的重复全量读取（Host 就绪刷新 + Library 刷新 + `LoadReaderBookAsync` 内部重复读），大数据根上放大 3 倍。
- **MA-10**：运行终态 `completed_with_failures` 与步骤错误码直接以 Core 枚举值出现在界面，未本地化。

## 验收标准

- [ ] **AC1 Console 分区接线**：无可用 Provider/模型时，控制台提供明确入口与状态（不再是「待接入」占位）；缓存与版本清理、插件与 Hooks 要么真实接线，要么保留占位但**明确说明未接入原因**，不得静默。 <<PARTIAL: 待实现>>
- [ ] **AC2 Stop 手工输入 run_id**：普通用户无需手抄 run_id 即可看到本会话/近期的 Run；外部 Run 的 run_id 路径仍在且有说明。若需契约扩展，先记录裁决再实施。 <<PARTIAL: 已实现且未改冻结契约（RunStatusMonitor 记忆本会话真实 run id + Console 列表点击加载 + Studio 创建后回填索引），5 个测试通过，待独立审查>>
- [ ] **AC3 消除启动期重复读取**：同一数据根下一次启动内 `ListBooks` 与 `list_chapters` 各只发生一次（或明确缓存命中），wire 帧计数可证明。 <<PARTIAL: 已实现（Library 首屏复用启动快照、阅读器复用快照书架、章节列表按 book 会话内缓存并由 CreateChapter 失效），3 个调用计数测试；Reader 侧复用由代码路径断言，未单独接线真实 wire 计数，待独立审查评估证据强度>>
- [ ] **AC4 错误码本地化**：`completed_with_failures` 与常见步骤错误码在 UI 显示为中文说明，同时保留 typed code（诊断用）。 <<PARTIAL: 已实现（RunStateText/RunStateStatus 覆盖 projection.py 全部终态；新增 StepErrorText 说明真实 upper-snake 步骤码并始终保留标识符），19 个用例通过，待独立审查>>

## 允许修改范围

见 frontmatter `allowed_paths`。**冻结契约 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的命令语义不得擅自更改**；MA-07 若确需新命令，先在本 Task 记录契约变更提案并交 DSH 裁决。

## 禁止范围

- 不修改用户数据根内容；不以假数据填充列表；不引入新依赖。
- 不 push 远端。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 分区接线 | `dotnet test --filter Console` + headless 截图 | net9.0 | NOT_RUN | 待补 |
| AC2 Run 列表 | `dotnet test --filter "RunIndexTests"` + `--filter TasksSection_ListsRunsThisSessionSaw` | net9.0 / `8b5530608` | PASS 5/5（索引 4 + Console 集成 1） | `RunIndexTests.cs`、`V2ConsoleUiTests.cs` |
| AC3 重复读取 | `dotnet test --filter StartupReadDedupTests` | net9.0 / `569e4fa56` | PASS 3/3（`RefreshCalls` 断言：首屏 0 次、显式刷新 1 次、冷快照 1 次） | `StartupReadDedupTests.cs` |
| AC4 错误码 | `dotnet test --filter CoreStateTextTests` | net9.0 / `569e4fa56` | PASS 19/19（终态文案 + 状态映射 + 步骤码说明与保留） | `CoreStateTextTests.cs` |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2 | doc/handoffs/REALUSE-DATA-SAFETY-2-handoff.md | 前两批 worktree 保留；本 Task 尚未开 worktree |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
