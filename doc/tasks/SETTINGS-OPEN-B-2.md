---
id: SETTINGS-OPEN-B-2
title: 设置分区开放批次 B-2：缓存/Revision 清理操作面
kind: implementation
governance_version: 2
status: in_progress
approval: user_ruling_20261022_open_all_settings_partitions
suggested_owner: dsh
owner: dsh
reviewer: tbd_independent
depends_on: [SETTINGS-OPEN-B-1]
base_commit: 7d19164f838607e68e2b6970bbbd57bee7bd5777
branch: main
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-OPEN-B-2
allowed_paths:
  - doc/design/SETTINGS_SECTION_SCHEMAS.md
  - doc/tasks/SETTINGS-OPEN-B-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/handoffs/SETTINGS-OPEN-B-2-*.md
  - verification/SETTINGS-OPEN-B-2/**
  - apps/desktop/frontend/src/settings/**
  - apps/desktop/src-tauri/src/**
  - apps/desktop/src-tauri/capabilities/**
  - apps/desktop/src-tauri/build.rs
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - src/application/maintenance/**
  - tests/core/**
  - tests/application/**
---

# SETTINGS-OPEN-B-2：缓存/Revision 清理操作面

## 来源与目标

用户 2026-10-22 裁决开放全部设置分区。批次 A（四节）与 B-1（模型/GPU、任务/并发）已完成。本 Task 实现设计 §4.3：**缓存/Revision** 分区的真实操作面——预览可清理缓存、执行清理、重试挂起项；不开放自动清理天数/Revision 保留策略（无调度/存储消费点，禁止假控件）。

交付结果：设置页"缓存/Revision"分类可打开，展示可清理文件数与字节数，可执行清理并显示结果（成功/失败/跳过），可重试挂起项；不触碰用户源文件与 current/pinned revision。

## Acceptance Criteria

- [ ] **AC1 Core 操作面**：新增**应用层命令**（与 `settings.get` 同型，走 StdioLibraryChannel application envelope；**不**加入 `_HOST_CONTROL_COMMANDS` 冻结集合）`cleanup.preview` / `cleanup.run` / `cleanup.retry_pending`（payload `{}`），返回 `CleanupPreview` / `CleanupOutcome` 的 JSON 投影；`CleanupService` 由 assembly 用 `WebtoonTileCacheSweeper` + `ManagedFileStorage` 删除器 + 既有 trash manifest 构造并注入 CoreService；Core 边界校验 payload 形状（非 object → INVALID_REQUEST）；注入缺失时 `CORE_UNAVAILABLE`（unavailable，retryable=true）。
- [ ] **AC2 Tauri 命令面**：新增 production-only 命令 `cleanup_preview` / `cleanup_run` / `cleanup_retry_pending`（Core 转发、typed 错误映射沿用 `CORE_UNAVAILABLE`/`INVALID_REQUEST`），并在 `command_allowlist` 常量、`*_PRODUCTION_ONLY_COMMANDS`、`generate_handler!` 三处清单、capabilities 声明、build.rs manifest（如涉及）同一 commit 同步；probe/ac1 模式保持冻结形状。
- [ ] **AC3 前端面板**：`cache_revision` 分类 open；面板显示"可清理 N 个文件 / X MB"（预览）、"清理"与"重试挂起项"按钮、结果反馈（成功/失败/跳过计数与失败明细）、只读说明（Revision 保留策略/自动清理未开放）；加载失败/禁用态（无 Core）有明确提示；不显示假控件。
- [ ] **AC4 测试**：Core 单测（三命令 + 空预览/有缓存/失败后 pending/重试成功；安全前缀拒绝与既有 cleanup 测试不弱化）；Rust 单测（命令面同步断言/allowlist）；前端面板测试（预览/清理/重试/失败投影）；`cargo test` 与前端 `npm test`、`tsc` 全绿或明确记录环境性 NOT_RUN。
- [ ] **AC5 证据**：固定 commit、evidence_dir 原始日志、独立 Review（非实现者）、GUI 烟测（打开缓存分类、预览、清理、重启后 pending 状态一致）或明确 NOT_RUN。

## 允许修改范围

上列 allowed_paths。不改 `settings_update_section` 的 wire 形状与既有白名单语义；不改 Schema/migration；不加依赖；不动 Provider/Network/凭据/SFX 面。

## 禁止范围

- 不开放自动清理天数/Revision 保留策略（无消费点）。
- 不新增缓存删除路径（必须复用 `CleanupService` 的安全前缀与 `ControlledFileRemover`）。
- 不删用户源文件、不 push/merge/rebase。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `python -m pytest tests/core -k cleanup -q` | 本地 Python | NOT_RUN | 待填 |
| AC2 | `cargo test`（apps/desktop/src-tauri） | Rust 工具链 | NOT_RUN | 待填 |
| AC3/AC4 | `npm --prefix apps/desktop/frontend test` | node_modules | NOT_RUN | 待填 |
| 烟测 | dev preview：缓存分类预览/清理/重启复查 | 构建可用 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 依赖 SETTINGS-OPEN-B-1（in_review）：分类矩阵与 client union 模式。
- 风险一：Tauri 三处清单 + capabilities 漏同步 → R2-04 纪律测试必须覆盖。
- 风险二：Rust 编译环境/时间；若 cargo test 不可执行，标 NOT_RUN 并保留独立 Review。
- 风险三：清理空库时 preview 为 0；UI 必须显示"无可清理文件"而非崩溃。

## 交付与运行记录

- 2026-10-22：dsh 释放并组织（wire writer + UI writer），独立 Review 另行指派。
- Handoff / Review / 实际测试：待填。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pending | pending | pending | pending | pending | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference check |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | NOT_APPLICABLE | — | — | 本 Task 不产生持久资源（清理操作只作用于可重建缓存） |

## Closeout Record

- Closeout：待关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：缓存清理为产品功能，不是资源处置；本 Task 不执行清理。
- 当前指针清理：STATUS/REBASELINE/LEDGER 已登记本 Task。
