---
id: ENV-BUNDLE-1-FU1
title: packaged 驱动验收：让真实 frozen sidecar 驱动协议 2.3 端到端证据（闭环 ENV-BUNDLE-1 AC4 严格口径）
kind: infra
governance_version: 2
status: ready
approval: coordinator_release_20261016_followup_of_env_bundle_1_closeout
suggested_owner: Codex
owner: codex
reviewer: null
depends_on: [ENV-BUNDLE-1]
base_commit: null
branch: codex/ENV-BUNDLE-1-FU1-packaged-acceptance
worktree: G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/ENV-BUNDLE-1-FU1
---

# ENV-BUNDLE-1-FU1：packaged 驱动验收（闭环 AC4 严格口径）

## 来源与目标

- **来源**：[ENV-BUNDLE-1](ENV-BUNDLE-1.md) 以 `closed_with_limitations` 收口（Review `8250b420`、集成 `7b9cbbe6`、closeout `814d3fb4`），
  其 Closeout 明确留下**必须另立 Task 的前置项**："a separately authorised task must make those six tests
  drive the frozen bundle via `M2RC1_PACKAGED` before any packaged six-test acceptance claim."
- **已确认的事实（本 Task 的起点，2026-10-16 Coordinator 实测）**：
  - 主仓 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe` 仍是 **2026-10-14 15:09** 的旧版（协议 < 2.3）。
  - **重建后的 2.3 frozen bundle 只存在于 `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1`**
    （`…/target/core-sidecar/core-sidecar/core_service.exe`，2026-10-16 16:13，68,717,156 bytes）；
    它是 **gitignored 产物，未随集成进入 main**。
  - 主仓 `apps/desktop/frontend/dist` 亦为 2026-10-07 旧版。
- **问题实质**：ENV-BUNDLE-1 的 cargo 六项用例是通过 `M2RC1_PYTHON` 以 **Python source module** 启动 Core
  （`M2RC1_SRC_ROOT` 默认指向仓库 `src`），因此 `76 passed` **不能**作为打包产物验收。
  代码事实：`apps/desktop/src-tauri/src/{main.rs,library_bridge.rs}` 的集成测试以
  `M2RC1_PYTHON` + `M2RC1_SRC_ROOT` 启动 `-m infrastructure...`；frozen bundle 仅在
  `resolve_packaged_sidecar_dir()`（`M2RC1_PACKAGED=1` 或裸启动安装布局）路径上被解析。
- **目标**：产出一份**由真实 frozen bundle 驱动**的协议 2.3 端到端验收证据，
  使"打包端到端可用"从 `NOT_RUN` 变成一个**可复核的真实结论**；
  并让主仓的 gitignored 构建产物与协议 2.3 对齐，供后续 P19/P20 使用。

## Acceptance Criteria

- [ ] **AC1 前置与来源固定**：明确并记录本 Task 使用的 frozen bundle 与 `frontend/dist` 的
      **来源、字节数、SHA-256、协议版本**。允许两条路径，Owner 需在 Handoff 说明选择理由：
      (a) 复用 `G:/CODEX/New Manga.task-envs/m2ac5-build` 与 `packaging/m2ac5/build_sidecar.ps1 -Force`
      在本 worktree 重建（推荐，可复现）；或
      (b) 从 `ENV-BUNDLE-1` worktree 以**零拷贝 junction/复制**引入并记录其 SHA-256 与来源 commit。
      **不得**使用主仓 10-14 的旧 bundle 作为被测对象。
- [ ] **AC2 packaged 驱动验收（核心）**：让**同一组 sidecar 场景**在
      **frozen bundle 驱动**下真实执行，并归档原始日志、退出码与**逐项结果**：
      至少覆盖 `real_core_sidecar_round_trip`、`real_library_sidecar_round_trip_and_eof`、
      `real_core_sidecar_rc4_commands_round_trip_typed_errors`、
      `real_core_sidecar_retype_pair_empty_page_and_typed_rejection`、
      `real_core_sidecar_settings_round_trip_and_typed_rejection`、
      `real_core_sidecar_answers_startup_ping_on_fresh_catalog`
      所覆盖的协议语义（catalog → issue → resolve → typed error → shutdown）。
      **推荐实现**：新增**独立的 packaged 驱动测试路径**，不改动既有六个 source-backed 测试的语义
      （它们按 `main.rs` 注释是"dev-mode frozen env contract"，改动会破坏其原有用途）。
      **必须证明驱动的是 frozen 产物**：给出被测 exe 的绝对路径 + SHA-256 + 进程证据或启动日志，
      并显式说明 `M2RC1_PACKAGED`/`M2RC1_SRC_ROOT`/`M2RC1_PYTHON` 的实际取值。
- [ ] **AC3 packaged HostControl E2E**：在 frozen Core 上验证 HostControl（host 侧 `host_issuer.rs` →
      Core 侧 handler）真实往返；或如实 `BLOCKED`/`NOT_RUN` 并给出根因与原始证据。**不得**伪造。
- [ ] **AC4 主仓产物对齐**：用项目既定入口把 main 仓的 gitignored
      `apps/desktop/src-tauri/target/core-sidecar/**` 与 `apps/desktop/frontend/dist/**`
      刷新到与协议 2.3 一致（**仅 gitignored 产物，不产生 Git 变更**），并给出前后
      `core_service.exe` 的字节数/SHA-256/协议版本对比。若判定不应动 main 仓产物 → 如实说明并 `NOT_RUN`。
- [ ] **AC5 不越界**：**不修改**产品语义代码（`src/**`、`apps/**` 的业务实现）、契约、Schema、
      依赖清单；测试代码改动**仅限** AC2 所必需的新增测试/测试支持文件，且必须在 Handoff 逐文件列明并说明必要性。
      不得放宽既有断言、不得跳过用例、不得 mock 掉 frozen bundle。
- [ ] **AC6 主仓保护**：不触碰用户既有 **19 项 dirty/untracked**；给出改动前后
      `git status --porcelain --untracked-files=no` 与 HEAD 对比自证（注意 `core.autocrlf=true`
      会产生 CRLF 纯行尾噪音，须用 `git diff` 复核真实内容为空）。
- [ ] **AC7 固定交付**：固定 commit、写 Handoff（[模板](../templates/HANDOFF.md)）、登记 Canonical Evidence（含真实 sha256）、
      未跑项如实标 `NOT_RUN`/`BLOCKED`；不 `push`、不 `merge`（集成由 Coordinator 执行）。

## 允许修改范围

- **新建（入库）**：本 Task（`doc/tasks/ENV-BUNDLE-1-FU1.md`）、`doc/handoffs/ENV-BUNDLE-1-FU1-*.md`、
  `verification/ENV-BUNDLE-1-FU1/**`；**新增测试文件**（如 `apps/desktop/src-tauri/tests/**` 或
  `apps/desktop/src-tauri/src/**` 内新增的 `#[cfg(test)]` 模块）——必须在 Handoff 逐文件说明理由。
- **新建/重建（gitignored，不入库）**：本 worktree 的 `apps/desktop/src-tauri/target/**`、
  `apps/desktop/frontend/{dist,node_modules}/**`；`G:/CODEX/New Manga.task-envs/m2ac5-build`（复用，不重建）。
- **只读引用**：`packaging/m2ac5/**`、`apps/desktop/src-tauri/{tauri.conf.json,build.rs,src/**}`、
  `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、[ENV-BUNDLE-1](ENV-BUNDLE-1.md)、
  `verification/ENV-BUNDLE-1/**`、`.orchestrator/BL11-ENV-EVIDENCE.md`。
- 写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`。

## 禁止范围

- **不得**为"让测试变绿"而放宽断言、跳过用例、mock frozen bundle、或把 source-backed 结果申报为 packaged 结果。
- **不得修改**产品语义实现、契约（`doc/contracts/**`）、[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、
  依赖清单（`requirements.txt`、`Cargo.toml` 产品依赖、`package.json`）。
- **不得触碰**用户 19 项 dirty/untracked（含 `AGENTS.md`、`doc/00_INDEX.md`、`doc/01`、`doc/03`、`doc/04`、
  `doc/06`、`doc/09`、`doc/11`、`doc/12`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、
  `doc/WORKTREE_SAFETY_INVENTORY.md`、`doc/tasks/P02*`、`doc/templates/**`、
  `verification/PROJECT-ROADMAP-20261008/ROADMAP.md`、`.qoder-credits/report.json`）。
- **不得修改** `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（Coordinator 专有权威指针）。
- 不 `push`、不 `merge`、不 `reset`、不 `stash`、不删除既有 worktree 或既有 `task-envs`。
- 不得把大型二进制产物提交入库（保持 gitignored）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 固定 bundle 来源并计算 SHA-256/协议版本 | build venv 或 ENV-BUNDLE-1 worktree | NOT_RUN | 无 |
| AC2 | packaged 驱动的六场景协议往返（原始日志 + 逐项结果 + 被测 exe 路径/SHA-256） | 2.3 frozen bundle | NOT_RUN | 无 |
| AC3 | frozen Core 上的 HostControl 往返 | 2.3 frozen bundle + host 侧通道 | NOT_RUN | 无 |
| AC4 | 刷新 main 仓 gitignored 产物并前后对比 | `build_sidecar.ps1 -Force` / frontend build | NOT_RUN | 无 |
| AC6 | 主仓 HEAD + `git status --porcelain --untracked-files=no` 前后对比（19 项） | 主仓 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：ENV-BUNDLE-1（`closed_with_limitations`，已提供 2.3 bundle 与 build venv）。
- 风险一：**drive frozen bundle 的实现方式可能与现有测试架构冲突**（既有测试按设计走 dev-mode source 路径）。
  缓解：优先新增独立 packaged 测试路径；若判定必须改动既有测试，先 `BLOCKED` 并交 Coordinator 裁决，**不得**自行扩大范围。
- 风险二：PyInstaller 重建耗时（约 6–7 分钟）且需磁盘空间；AC1 允许零拷贝 junction 复用 ENV-BUNDLE-1 的产物。
- 风险三：CRLF 噪音污染主仓状态 → 必须用 `git diff`（而非 `git status`）判定真实改动。
- 阻塞条件：若 frozen bundle 无法启动、或协议版本与预期不符 → 如实 `BLOCKED` + 原始证据，**不得同策略反复重试**。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：依据 ENV-BUNDLE-1 的 Closeout 明确留下的后续项，
  以及 Coordinator 实测的"2.3 bundle 仅在 ENV-BUNDLE-1 worktree、主仓仍为 10-14 旧版"事实。
  与在飞的 [UI-DESIGN-1](UI-DESIGN-1.md)（owner=zcode）**并行**：agent、branch、worktree、写入路径互不重叠。
- Handoff：尚无。
- Review：尚无（Reviewer 必须独立于 Owner）。
- 实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1 | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |
| frozen-bundle | G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar | PRESERVE_REFERENCED | G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | gitignored 构建产物；AC4 刷新为协议 2.3 对齐；保留 |
| build-venv | G:/CODEX/New Manga.task-envs/m2ac5-build | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/m2ac5-build | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | 复用 ENV-BUNDLE-1 建立的隔离构建环境；不重建 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放时同步。
