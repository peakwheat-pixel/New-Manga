---
id: SETTINGS-OPEN-B-2
title: 设置分区开放批次 B-2：缓存/Revision 清理操作面
kind: implementation
governance_version: 2
status: in_review
approval: user_ruling_20261022_open_all_settings_partitions
suggested_owner: dsh
owner: dsh
reviewer: reviewer-settings-a
depends_on: [SETTINGS-OPEN-B-1]
base_commit: 7d19164f838607e68e2b6970bbbd57bee7bd5777
branch: main
worktree: null
integration_commit: 0e2e6233aa54363e49e992ba2353a00c665c3de0
delivery_head: 0e2e6233aa54363e49e992ba2353a00c665c3de0
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
  - apps/desktop/src-tauri/gen/**
  - apps/desktop/src-tauri/permissions/**
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

- [x] **AC1 Core 操作面**：新增**应用层命令**（与 `settings.get` 同型，走 StdioLibraryChannel application envelope；**不**加入 `_HOST_CONTROL_COMMANDS` 冻结集合）`cleanup.preview` / `cleanup.run` / `cleanup.retry_pending`（payload `{}`），返回 `CleanupPreview` / `CleanupOutcome` 的 JSON 投影；`CleanupService` 由 assembly 用 `WebtoonTileCacheSweeper` + `ManagedFileStorage` 删除器 + 既有 trash manifest 构造并注入 CoreService；Core 边界校验 payload 形状（非 object → INVALID_REQUEST）；注入缺失时 `CORE_UNAVAILABLE`（unavailable，retryable=true）。
- [x] **AC2 Tauri 命令面**：新增 production-only 命令 `cleanup_preview` / `cleanup_run` / `cleanup_retry_pending`（Core 转发、typed 错误映射沿用 `CORE_UNAVAILABLE`/`INVALID_REQUEST`），并在 `command_allowlist` 常量、`*_PRODUCTION_ONLY_COMMANDS`、`generate_handler!` 三处清单、capabilities 声明、build.rs manifest（如涉及）同一 commit 同步；probe/ac1 模式保持冻结形状。
- [x] **AC3 前端面板**：`cache_revision` 分类 open；面板显示"可清理 N 个文件 / X MB"（预览）、"清理"与"重试挂起项"按钮、结果反馈（成功/失败/跳过计数与失败明细）、只读说明（Revision 保留策略/自动清理未开放）；加载失败/禁用态（无 Core）有明确提示；不显示假控件。
- [x] **AC4 测试**：Core 单测（三命令 + 空预览/有缓存/失败后 pending/重试成功；安全前缀拒绝与既有 cleanup 测试不弱化）；Rust 单测（命令面同步断言/allowlist）；前端面板测试（预览/清理/重试/失败投影）；`cargo test` 与前端 `npm test`、`tsc` 全绿或明确记录环境性 NOT_RUN。
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
| AC1 | `python -m pytest tests/core -k cleanup -q` | 本地 Python | PASS（`tests/core` 752 passed，含新增 28 项 cleanup wire；cleanup 靶向 40 passed） | wire-report.md / wire-*.log |
| AC2 | `cargo test --locked --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | Rust 1.98.1 | PASS（152 passed / 1 ignored / 12 filtered；默认线程 149+2 个既有 flaky，单跑与串行全绿） | wire-report.md §5.2 / wire-cargo-test-serial.log |
| AC3/AC4 | `npm --prefix apps/desktop/frontend test` | node_modules | PASS（41 files / 406 tests；tsc exit 0） | ui-report.md / ui-test-*.log |
| 烟测 | dev preview：缓存分类预览/清理（隔离数据根预置 3 tile） | 构建可用 | PASS（预览 3 文件/6.0 KB → 清理成功 3/失败 0/跳过 0 → 归零；文件已删除） | gui-smoke.md + screenshots/01..03 |

## 依赖、风险与阻塞

- 依赖 SETTINGS-OPEN-B-1（in_review）：分类矩阵与 client union 模式。
- 风险一：Tauri 三处清单 + capabilities 漏同步 → R2-04 纪律测试必须覆盖。
- 风险二：Rust 编译环境/时间；若 cargo test 不可执行，标 NOT_RUN 并保留独立 Review。
- 风险三：清理空库时 preview 为 0；UI 必须显示"无可清理文件"而非崩溃。

## 交付与运行记录

- 2026-10-22：dsh 释放并登记；wire 由 `wire-settings-b2`、前端由 `ui-settings-b2` 两个独立 writer 并行实现；Lead 独立复核 diff、跑 pytest 与 GUI 烟测。
- 2026-10-22：交付 commit `0e2e623`；独立 Review 由 `reviewer-settings-a`（非实现者）执行，结论落 `verification/SETTINGS-OPEN-B-2/review-b2.md`。
- Lead 独立验证：`pytest tests/core tests/providers --ignore=tests/providers/test_detection_manga_real.py -q` → 1251 passed / 3 skipped；`npm --prefix apps/desktop/frontend test` → 41 files / 406 tests；`tsc --noEmit` exit 0；GUI 烟测 PASS（gui-smoke.md）。
- 任务文本笔误已修：AC1 原写"HostControl 命令"，实际按**应用层命令**实现（与 `settings.get` 同型；不加入冻结的 `_HOST_CONTROL_COMMANDS`），见 wire-report §2。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|EV-B2-GUI-SMOKE|AC1-AC5|verification/SETTINGS-OPEN-B-2/gui-smoke.md|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|a4506241c6baf0dfcbe6ef07f137c0ac619e42a9a873a3f891540838297f62a6|CANONICAL|
|EV-B2-01-CACHE-PREVIEW-3-FILES|AC1-AC5|verification/SETTINGS-OPEN-B-2/screenshots/01-cache-preview-3-files.png|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|b584300db49a6718866f3178f47b86bb932441e203ae64bb57f2ad38a531bc9f|CANONICAL|
|EV-B2-02-CACHE-CLEANED|AC1-AC5|verification/SETTINGS-OPEN-B-2/screenshots/02-cache-cleaned.png|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|89c283acc92b8f654ded2b61840c274176d00e076e7ace2fea8142c8cac3f244|CANONICAL|
|EV-B2-03-CACHE-EMPTY-IDLE|AC1-AC5|verification/SETTINGS-OPEN-B-2/screenshots/03-cache-empty-idle.png|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|dcd09faacc0b4e9f7c1b767d786cafceade57f9502b4f529ec45a448f105f5c8|CANONICAL|
|EV-B2-UI-REPORT|AC1-AC5|verification/SETTINGS-OPEN-B-2/ui-report.md|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|8861fbdaba8b9a109fb9f22d9b53848235e85eb435502b15574aa9bf07c3ad7d|CANONICAL|
|EV-B2-UI-TEST-FRONTEND|AC1-AC5|verification/SETTINGS-OPEN-B-2/ui-test-frontend.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|be1b136943ea09ea7336c5025362b2ec82489be7f1747395d9b6b6dc84776b6d|CANONICAL|
|EV-B2-UI-TEST-TARGETED|AC1-AC5|verification/SETTINGS-OPEN-B-2/ui-test-targeted.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|f35b56932ae3039c4f26fe66c55ea6e2f27a48fed6ebfb375b38e0503bd1acef|CANONICAL|
|EV-B2-UI-TSC|AC1-AC5|verification/SETTINGS-OPEN-B-2/ui-tsc.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|a419d8d72338a478b07d1f043fceaa320b06fde9b824029951635ca130dc3654|CANONICAL|
|EV-B2-WIRE-CARGO-TEST-DEFAULT-THREADS|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-cargo-test-default-threads.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|9494ba0e738afd15a1f9468c49cc8c9d370f3a9f193b18431e0541e9420f69d8|CANONICAL|
|EV-B2-WIRE-CARGO-TEST-ISOLATED-FLAKY-RERUN|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-cargo-test-isolated-flaky-rerun.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|d8225ee3fccdeeca6c12170d826574f2048a010bdb81aca8c8470f200a901a3e|CANONICAL|
|EV-B2-WIRE-CARGO-TEST-SERIAL|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-cargo-test-serial.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|d7416b4eb342f55e5dead29fb00a332bb697be618b88dbb0cbe203eb5d097ba6|CANONICAL|
|EV-B2-WIRE-CLEANUP-TARGETED-PYTEST|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-cleanup-targeted-pytest.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|51940eef75338210b3e4c917427889d9b37eaeb3e53daeda12398834ec300434|CANONICAL|
|EV-B2-WIRE-CORE-PYTEST-FULL|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-core-pytest-full.log|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|42e3b613e53f6c6bde376db5062d58f2917f9d0b118468c63a28dedf03b9b7c1|CANONICAL|
|EV-B2-WIRE-REPORT|AC1-AC5|verification/SETTINGS-OPEN-B-2/wire-report.md|a5bdb307e3a45ce99d0a20e220f1503a9f3004d2|2c942fb75551d2b7faf0f155246c83789d4d6cc5d857d0c31aaecfdcac5bdfe1|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference check |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | NOT_APPLICABLE | — | — | 本 Task 不产生持久资源（清理操作只作用于可重建缓存） |

## Closeout Record

- Closeout：待关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：缓存清理为产品功能，不是资源处置；本 Task 不执行清理。
- 当前指针清理：STATUS/REBASELINE/LEDGER 已登记本 Task。
