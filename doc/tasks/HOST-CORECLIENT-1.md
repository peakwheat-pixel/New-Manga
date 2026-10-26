---
id: HOST-CORECLIENT-1
title: S1 C# Host/CoreClient——spawn 双 sidecar + JSON-lines + 中文零乱码 + 失败可诊断
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: zcode
depends_on: [DISPLAY-PERF-DECISION-1]
base_commit: a93f20c7b
branch: task/HOST-CORECLIENT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-CORECLIENT-1
allowed_paths:
  - doc/tasks/HOST-CORECLIENT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-CORECLIENT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1/**
---

# HOST-CORECLIENT-1：S1 Host 与 CoreClient

## 来源与目标

依据 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[ADR-0001](../design/ADR-0001_REPO_LAYOUT_AND_COEXISTENCE.md)、[EXECUTION_DIRECTIVE_AD002_V2](../design/EXECUTION_DIRECTIVE_AD002_V2.md) §8；S0 spike 已 **GO**（`verification/DISPLAY-PERF-DECISION-1/spike/SPIKE_REPORT.md`）。

目标：在 `apps/desktop-avalonia/` 建立 C# 工程骨架，实现与既有 Python Core 的 stdio 通信层，跑通 `core.ping` 与 `list_books`，并保证中文零乱码、sidecar 启动失败可诊断（不 panic）。

## Acceptance Criteria

- [ ] **AC1 工程骨架**：`apps/desktop-avalonia/NewManga.sln` + `src/NewManga.App`（Avalonia）+ `src/NewManga.Host` + `src/NewManga.CoreClient` + `src/NewManga.Theme` + `tests/`（xunit + Avalonia.Headless）；`dotnet build -warnaserror` 通过；发布配方按 spike：`PublishSingleFile + SelfContained + PublishTrimmed + IncludeNativeLibrariesForSelfExtract + ReadyToRun + 压缩`。
- [ ] **AC2 双通道**：`CoreClient` 以 `Process` spawn **两个** sidecar —— `host_bridge`（wire v1：issue/resolve/revoke）与 `core_service`（protocol 2.3：`core.ping`/`ListBooks`）；`CREATE_NO_WINDOW`；stdio 单行 JSON；非 ASCII 一律 `\uXXXX` 转义。
- [ ] **AC3 功能与编码**：`core.ping` 返回 ready；`list_books` 返回真实书架；**中文书名往返**（至少 `雾港来信・日本語テスト`）且抓**原始 wire 字节**证明 `\uXXXX`；原始 UTF-8 负例复现 `UNKNOWN`（与 spike 结论一致）。
- [ ] **AC4 失败可诊断（不得 panic）**：sidecar 路径缺失/启动失败/启动超时/令牌完整性异常（子进程 IL 与父不一致）→ 记录 stderr 到文件、返回 typed 错误、UI 可显示；不需要提权即可运行（AC11：非提权测试用无标签副本）。
- [ ] **AC5 共存约束**：按 ADR-0001 实现全局单实例 Mutex `Global\NewManga.Host`；启动检测旧壳 `new-manga.exe` 存在时进入只读/提示（二选一并测试）；S2 parity 前对生产数据只读；首次运行备份。
- [ ] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`dotnet build/test` 绿；旧壳 `vitest` 基线不受影响（60 文件/567 用例）；中文 IPC 证据入库；无控制台窗口泄漏；lifecycle v3 AC 标记与证据 pin 齐全。
- [ ] **AC7 交接**：Handoff（`doc/handoffs/HOST-CORECLIENT-1-handoff.md`）+ 可复跑命令 + 未完成项；record decision 段（协议字段映射、错误码映射、sidecar 发现顺序）。

## 允许修改范围

- `apps/desktop-avalonia/**`（新工程）、本 Task 卡、STATUS/PLAN/LEDGER 指针、`verification/HOST-CORECLIENT-1/**`、workspace task-env/worktree。
- 只读引用：`apps/desktop/src-tauri/src/{core_bridge.rs,library_bridge.rs,main.rs}`、`doc/AD-002*`、`doc/design/ADR-*`、`verification/DISPLAY-PERF-DECISION-1/**`。

## 禁止范围

- **不得修改旧壳** `apps/desktop/**`（S5 才退役）；不得修改 Python Core（`src/**`）、`requirements*.txt`、AD-002/ADR、旧前端。
- 不得 push main；不得 gc/prune；不得动受保护资源。
- 不得引入商业字体；依赖需核许可并登记 `THIRD_PARTY_LICENSES.md`（若新增）。
- 不得把 sidecar 的 OS 绝对路径暴露给 UI 层。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet build -warnaserror` + `dotnet test` | .NET SDK 9/10 | NOT_RUN | 待填 |
| AC2/AC3 | 起真 sidecar：`core.ping`、`list_books`、中文往返 + wire hex | packaged sidecar 副本（无标签目录） | NOT_RUN | 待填 |
| AC4 | 负例：缺失 exe/超时/IL 不一致 | 同上 | NOT_RUN | 待填 |
| AC5 | 单实例 Mutex + 旧壳检测 | 手工 + 自动化 | NOT_RUN | 待填 |
| AC6 | 治理 + 双轨测试 + 无控制台 | 全量 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- `depends_on`：DISPLAY-PERF-DECISION-1（S0 GO 已达成）。
- 风险 1：cp936 编码坑（历史事故）→ AC3 用原始字节验证。
- 风险 2：sidecar 启动路径（packaged 目录 vs 仓库树）→ 用无标签副本 + 隔离 env。
- 风险 3：57/66 命令面差异 → S2 才需 parity，本 Task 只需两个通道跑通。
- 风险 4：单实例 Mutex 与旧壳无协作 → 检测进程并降级只读。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
