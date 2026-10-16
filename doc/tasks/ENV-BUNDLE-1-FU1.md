---
id: ENV-BUNDLE-1-FU1
title: packaged 驱动验收：让真实 frozen sidecar 驱动协议 2.3 端到端证据（闭环 ENV-BUNDLE-1 AC4 严格口径）
kind: infra
governance_version: 2
status: in_review
approval: coordinator_release_20261016_followup_of_env_bundle_1_closeout
suggested_owner: Codex
owner: codex
reviewer: null
depends_on: [ENV-BUNDLE-1]
base_commit: 3bf2604dc9e8ef6be47bd80897e4df05cae077b3
branch: codex/ENV-BUNDLE-1-FU1-packaged-acceptance
worktree: G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1
integration_commit: null
delivery_head: pending implementation commit
canonical_evidence_status: pending_final_hash_and_head
resource_closeout_status: recorded
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

- [x] **AC1 前置与来源固定**：明确并记录本 Task 使用的 frozen bundle 与 `frontend/dist` 的
      **来源、字节数、SHA-256、协议版本**。允许两条路径，Owner 需在 Handoff 说明选择理由：
      (a) 复用 `G:/CODEX/New Manga.task-envs/m2ac5-build` 与 `packaging/m2ac5/build_sidecar.ps1 -Force`
      在本 worktree 重建（推荐，可复现）；或
      (b) 从 `ENV-BUNDLE-1` worktree 以**零拷贝 junction/复制**引入并记录其 SHA-256 与来源 commit。
      **不得**使用主仓 10-14 的旧 bundle 作为被测对象。
- [x] **AC2 packaged 驱动验收（核心）**：让**同一组 sidecar 场景**在
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
- [x] **AC4 主仓产物对齐**：用项目既定入口把 main 仓的 gitignored
      `apps/desktop/src-tauri/target/core-sidecar/**` 与 `apps/desktop/frontend/dist/**`
      刷新到与协议 2.3 一致（**仅 gitignored 产物，不产生 Git 变更**），并给出前后
      `core_service.exe` 的字节数/SHA-256/协议版本对比。若判定不应动 main 仓产物 → 如实说明并 `NOT_RUN`。
- [x] **AC5 不越界**：**不修改**产品语义代码（`src/**`、`apps/**` 的业务实现）、契约、Schema、
      依赖清单；测试代码改动**仅限** AC2 所必需的新增测试/测试支持文件，且必须在 Handoff 逐文件列明并说明必要性。
      不得放宽既有断言、不得跳过用例、不得 mock 掉 frozen bundle。
- [x] **AC6 主仓保护**：不触碰用户既有 **19 项 dirty/untracked**；给出改动前后
      `git status --porcelain --untracked-files=no` 与 HEAD 对比自证（注意 `core.autocrlf=true`
      会产生 CRLF 纯行尾噪音，须用 `git diff` 复核真实内容为空）。
- [x] **AC7 固定交付**：固定 commit、写 Handoff（[模板](../templates/HANDOFF.md)）、登记 Canonical Evidence（含真实 sha256）、
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
| AC1 | 固定 bundle 来源并计算 SHA-256/协议版本 | 既有 build venv；完整构建，无 `-SkipWeights` | PASS | [构建与产物清单](../../verification/ENV-BUNDLE-1-FU1/ac1-bundle-and-frontend-manifest.md)、[sidecar build log](../../verification/ENV-BUNDLE-1-FU1/ac1-build-sidecar.log)、[frozen smoke](../../verification/ENV-BUNDLE-1-FU1/ac1-core-service-smoke.log) |
| AC2 | frozen bundle 驱动的六场景协议往返；路径、SHA、环境、日志及逐项结果 | 2.3 frozen bundle；`M2RC1_PACKAGED=1`，source env unset | PASS：6/6 | [逐项结果](../../verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-test-results.md)、[原始 Cargo log](../../verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests.log)，exit `0` |
| AC3 | frozen Core 上由 host 侧 issuer 发起的 HostControl 往返 | 2.3 frozen bundle + `StdioLibraryChannel` | BLOCKED：`RegisterImportSource` 返回 `REF_EXPIRED`；未触及产品代码 | [阻塞分析](../../verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md)、[原始探测 log](../../verification/ENV-BUNDLE-1-FU1/ac2-ac3-combined-attempt.log)，combined exit `101` |
| AC4 | 刷新 main 仓 gitignored sidecar 与 frontend/dist 并比较 | 本 worktree 经既定 sidecar/frontend 构建入口生成，再镜像到已确认 ignored 的主仓目标 | PASS：Core 2.3 | [前后对比](../../verification/ENV-BUNDLE-1-FU1/main-artifacts-after.md)、[复制记录](../../verification/ENV-BUNDLE-1-FU1/ac4-copy-sidecar-to-main.log)、[主仓 smoke](../../verification/ENV-BUNDLE-1-FU1/ac4-main-core-smoke-after.log) |
| AC5 | 确认仅新增 AC2 测试路径；生成物噪音恢复；无产品/契约/依赖变更 | Task worktree | PASS | [生成物副作用记录](../../verification/ENV-BUNDLE-1-FU1/ac5-generated-side-effects.md)、Handoff 逐文件说明 |
| AC6 | 主仓 HEAD + `git status --porcelain --untracked-files=no` 前后对比，复核原 19 项 diff | 主仓 `G:/CODEX/New Manga` | PASS：19 项原始 dirty 指纹未变 | [主仓状态对比](../../verification/ENV-BUNDLE-1-FU1/main-status-comparison.md)及 before/after snapshots |
| AC7 | 固定 commit、Handoff、Canonical Evidence、未跑项标记；不 push/merge | Task branch | PASS：Handoff 与 evidence 在交付 commit 中 | 本 Task 的 Canonical Evidence 表；Handoff 路径待最终固定 |

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
- 2026-10-16 Codex 认领：branch=`codex/ENV-BUNDLE-1-FU1-packaged-acceptance`，worktree=`G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`，base=`3bf2604dc9e8ef6be47bd80897e4df05cae077b3`；起始 worktree clean，git common directory=`G:/CODEX/New Manga/.git`。构建前置可行性探测通过：G: 可用空间约 1.50 TB；既有 `m2ac5-build` Python 3.12.3 / PyInstaller 6.22.3，`pip check` 无损坏依赖；Node v24.15.0 / npm 12.0.1 可用；`package-lock.json` 存在；npm registry 查询成功；当前 worktree 的 sidecar、frontend/dist、node_modules 均缺失。详见 `verification/ENV-BUNDLE-1-FU1/preflight.md`。
- 2026-10-16 Codex 构建：复用隔离 venv 执行 `build_sidecar.ps1 -Force`（exit `0`，未跳过 weights），`npm ci --no-audit --no-fund` 与 `npm run build` 均 exit `0`；`package-lock.json` SHA-256 前后不变。产物固定见 AC1 manifest。Cargo 之前完成构建，遵守 `build.rs` 的 fail-closed 前置。
- 2026-10-16 AC2：仅新增独立 `packaged_sidecar_tests` 驱动路径，过滤运行规定六项，`6 passed; 0 failed; 0 ignored; 77 filtered out`，exit `0`。每次启动均断言 `M2RC1_PACKAGED=1`、`M2RC1_SRC_ROOT` 和 `M2RC1_PYTHON` unset，并记录 frozen exe 路径、大小、SHA 与参数。两次开发尝试分别保留原始失败日志；最终通过日志单独归档。
- 2026-10-16 AC3：用真实 frozen Core 进行一次 HostControl 探测；`OpenHostSession` 成功，`RegisterImportSource` 返回 `REF_EXPIRED`，因此标记 `BLOCKED`。过期边界分析及证据见 `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md`；未修改产品实现，需另立授权修复任务后再测。
- 2026-10-16 AC4：将当前 worktree 已构建的 sidecar bundle 与 frontend dist 镜像到主仓对应 gitignored 路径；对主仓新 Core 做了隔离协议 smoke，ping 2.3 ready、shutdown stopped、exit `0`。主仓 Core 从 68,604,146 bytes / SHA-256 `61f128d6878baad1c72fa24f7cda75675b31354ea47b43828861e7d8b2ca91f0` / protocol `1.6` 更新为 68,717,156 bytes / SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` / protocol `2.3`。具体目录统计见 `main-artifacts-after.md`。
- 2026-10-16 AC6：主仓原 19 项 dirty 的 status SHA-256=`a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a`、`git diff --binary` 250,300 bytes / SHA-256=`fde78be03b5e5be8a01d10050703c2b2e587756b8d77a39be6bce05d1e7bfe35` 前后相同。主仓 HEAD 在运行期间被并发 UI-DESIGN-1 文档提交推进；该变化不在本 Task 写入路径中。最终快照在提交前重取并归档。
- 代码范围：唯一 tracked 代码改动是 `main.rs` 中 `#[cfg(test)]` 测试模块声明；新增 `packaged_sidecar_tests.rs` 包含 AC2 独立 packaged 路径的六项用例。没有改动产品语义实现、契约、Schema 或依赖。Cargo 产生的 27 个行尾噪音文件已逐项恢复，`git diff` 内容为空；详见副作用记录。
- Handoff：待写入固定实现 commit 后续文档提交，交独立 Review；本 Task 尚未被接受。
- Review：待独立 Reviewer（推荐 DeepSeek Harness）；Owner 不自审。
- 未运行：既有 source-backed 全套 77 tests 未运行（本次只过滤执行新增六项）；NSIS installer / GUI 安装验收未运行；AC3 处于 `BLOCKED`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| ENV-BUNDLE-1-FU1-AC1-BUILD | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-build-sidecar.log` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-ARTIFACTS | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-bundle-and-frontend-manifest.md` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-SMOKE | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-core-service-smoke.log` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-RAW | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests.log` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-RESULTS | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-test-results.md` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC3 | AC3 | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4 | AC4 | `verification/ENV-BUNDLE-1-FU1/main-artifacts-after.md` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-SMOKE | AC4 | `verification/ENV-BUNDLE-1-FU1/ac4-main-core-smoke-after.log` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6 | AC6 | `verification/ENV-BUNDLE-1-FU1/main-status-comparison.md` | 待固定 | 待计算 | CANONICAL |
| ENV-BUNDLE-1-FU1-RESOURCE | AC7 | `verification/ENV-BUNDLE-1-FU1/resource-manifest.json` | 待固定 | 待计算 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1 | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | Task branch/worktree retained for independent review |
| frozen-bundle | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/src-tauri/target/core-sidecar | PRESERVE_REFERENCED | Same worktree ignored bundle | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | 2.3 bundle; exe SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`; not staged |
| main-frozen-bundle | G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar | PRESERVE_REFERENCED | Same main ignored bundle | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | AC4 refreshed; ignored artifacts retained for P19/P20 |
| frontend-dist | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/frontend/dist | PRESERVE_REFERENCED | Same worktree ignored dist | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | Production build output; not staged |
| main-frontend-dist | G:/CODEX/New Manga/apps/desktop/frontend/dist | PRESERVE_REFERENCED | Same main ignored dist | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | AC4 refreshed; ignored artifacts retained |
| build-venv | G:/CODEX/New Manga.task-envs/m2ac5-build | PRESERVE_REFERENCED | Same existing venv | verification/ENV-BUNDLE-1-FU1/resource-manifest.json | Reused without rebuild; preserved |

## Closeout Record

- Handoff date / Codex：2026-10-16；Task 已提交并交独立 Review，本次不代替 Coordinator 关闭 Task。
- canonical_evidence_status：`recorded`；表内哈希及实现 commit 在交付文档提交后固定。
- resource_closeout_status：`recorded_preserve_referenced`；manifest 列明保留的 worktree、ignored bundle/dist 与既有 venv。
- 删除、迁移、归档数量/字节数：删除 `0`；大型产物仅在 ignored 目标间刷新，不入库。
- 未关闭项及保留原因：AC3 `BLOCKED`（HostControl grant 返回 `REF_EXPIRED`）；独立 Review 尚未完成；source-backed 全套和 GUI/installer 未运行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 由 Coordinator 在 Review 后同步；本 Task 未触碰。
