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
delivery_head: cffa9666fbbe5f2adfe213de37a8beb20a994a38
canonical_evidence_status: registered_blob_level
resource_closeout_status: accounted_with_preserved_residuals
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
| AC2 | frozen bundle 驱动的六场景协议往返；路径、SHA、环境、日志及逐项结果 | 2.3 frozen bundle；`M2RC1_PACKAGED=1`，source env unset | PASS：I1返修后 `6/6`；测试 `139.55 s`、命令总耗时 `174.24 s`，exit `0` | [I1返修与逐项结果、Reviewer复现记录](../../verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md)、[返修后原始 Cargo log](../../verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests-i1-repair.log) |
| AC3 | frozen Core 上由 host 侧 issuer 发起的 HostControl 往返 | 2.3 frozen bundle + `StdioLibraryChannel` | BLOCKED：`RegisterImportSource` 返回 `REF_EXPIRED`；未触及产品代码 | [阻塞分析](../../verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md)、[原始探测 log](../../verification/ENV-BUNDLE-1-FU1/ac2-ac3-combined-attempt.log)，combined exit `101` |
| AC4 | 刷新 main 仓 gitignored sidecar 与 frontend/dist 并比较 | 本 worktree 经既定 sidecar/frontend 构建入口生成，再镜像到已确认 ignored 的主仓目标 | PASS：Core 2.3 | [前后对比](../../verification/ENV-BUNDLE-1-FU1/main-artifacts-after.md)、[复制记录](../../verification/ENV-BUNDLE-1-FU1/ac4-copy-sidecar-to-main.log)、[主仓 smoke](../../verification/ENV-BUNDLE-1-FU1/ac4-main-core-smoke-after.log) |
| AC5 | 确认仅新增 AC2 测试路径；生成物噪音恢复；无产品/契约/依赖变更 | Task worktree | PASS | [生成物副作用记录](../../verification/ENV-BUNDLE-1-FU1/ac5-generated-side-effects.md)、Handoff 逐文件说明 |
| AC6 | 主仓 HEAD + `git status --porcelain --untracked-files=no` 前后对比，复核原 19 项 diff | 主仓 `G:/CODEX/New Manga` | PASS：19 项原始 dirty 指纹未变 | [主仓状态对比](../../verification/ENV-BUNDLE-1-FU1/main-status-comparison.md)及 before/after snapshots |
| AC7 | 固定 commit、Handoff、Canonical Evidence、未跑项标记；不 push/merge | Task branch | PASS：实现返修 commit 与本次 Handoff 分开固定；待独立 Review，未 push/merge | 本 Task 的 Canonical Evidence 表；[I1返修 Handoff](../handoffs/ENV-BUNDLE-1-FU1-cffa9666f.md) |

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
- 2026-10-16 I1 有界返修：独立 Reviewer=dsh 指出 AC2 六项测试的 `PackagedLab::start_library()` 将真实 frozen Core startup ping deadline 固定为 30 秒，负载下发生假阴性。仅在 `packaged_sidecar_tests.rs` 将 deadline 改为正整数环境变量 `M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS`，默认 `120` 秒；启动 ping 仍必须成功，六项场景断言不变。新默认值全量复跑 `6 passed; 0 failed; 0 ignored; 77 filtered out`，Cargo 测试耗时 `139.55 s`、命令总耗时 `174.24 s`、exit `0`。原始日志和三份 Reviewer 原始复现日志（含外部来源路径、逐字节副本及 SHA-256）、复现条件和逐项结果见 [I1返修记录](../../verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md)。生产 Host 启动同样传入 30 秒，详见返修记录的 `main.rs:840,848` 调查；只报告，未改产品代码，待 Coordinator 另立 Task。AC3 `REF_EXPIRED` 继续为 `BLOCKED`。本 Task 等待 Reviewer 对返修提交独立复跑，不表示已接受。
- 代码范围：唯一 tracked 代码改动是 `main.rs` 中 `#[cfg(test)]` 测试模块声明；新增 `packaged_sidecar_tests.rs` 包含 AC2 独立 packaged 路径的六项用例。没有改动产品语义实现、契约、Schema 或依赖。Cargo 产生的 27 个行尾噪音文件已逐项恢复，`git diff` 内容为空；详见副作用记录。
- Handoff：[ENV-BUNDLE-1-FU1-cffa9666f.md](../handoffs/ENV-BUNDLE-1-FU1-cffa9666f.md)，引用 I1 实现 head `cffa9666fbbe5f2adfe213de37a8beb20a994a38`；前次交付记录保留于 [ENV-BUNDLE-1-FU1-998200d48.md](../handoffs/ENV-BUNDLE-1-FU1-998200d48.md)。本 Task 尚未被接受，等待独立 Review 复跑。
- Review：待 Coordinator 释放独立 Review，推荐 DeepSeek Harness；Owner 不自审。
- 未运行：既有 source-backed 全套 77 tests 未运行（本次只过滤执行新增六项）；NSIS installer / GUI 安装验收未运行；AC3 处于 `BLOCKED`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| ENV-BUNDLE-1-FU1-PREFLIGHT | AC1 | `verification/ENV-BUNDLE-1-FU1/preflight.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `6e02a7f50aaf31046cf188a54ae89aeceb0c915a3d1973d9e9c6becc304282fd` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-BUILD | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-build-sidecar.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `f2468474be2a3a47cf7a6bd262d51e2956ed1c63e807cda41c1001f28aeedd96` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-NPM-CI | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-npm-ci.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `52a079e5a738cf4780769c8d77089c791c00bf7940979ed12a0c0422681ce0ac` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-FRONTEND | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-frontend-build.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `c5cc5211dfbb9d73bf333aa3daa93ba1b0a3326c847fd9d79ac46096e387c2df` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-ARTIFACTS | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-bundle-and-frontend-manifest.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `e0c9ac95e361ef1cc06f495461bc37e1de05b15feea308bda9ebea3761fb24dc` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC1-SMOKE | AC1 | `verification/ENV-BUNDLE-1-FU1/ac1-core-service-smoke.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `3c97b0c0e116bc4e235b3daf87ddfc10faa5f140a4db565ba455f1c8093fdb05` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-COMBINED | AC2/AC3 | `verification/ENV-BUNDLE-1-FU1/ac2-ac3-combined-attempt.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `5dc4072a7da656ee48b66dc88011b734f7c72ccdbee51fc70c4ae4fdc25e39c8` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-COMPILE-ATTEMPT | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-tests-attempt-1-compile-failure.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `6210d9cbb17f5bd62e4b49fb93772fc61c9b530978cc24671c8116eac15f67d8` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-RAW | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `5eb49f5f0d3613d642f39313392570621181c315a06807137cc7bc535e647a86` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC2-RESULTS | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-test-results.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `9fecee263ca3560eaab4174a554c5acadefb74359b94bc53f5e3b76356501c23` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-AC2-RAW | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests-i1-repair.log` | `cffa9666fbbe5f2adfe213de37a8beb20a994a38` | `500c6ff537c793d112943251671d89d14761578aec25f7315c90bd34fe5ca821` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-REVIEWER-FULL | AC2 | `verification/ENV-BUNDLE-1-FU1/reviewer-rerun-packaged.log` | `cffa9666fbbe5f2adfe213de37a8beb20a994a38` | `0ae5ab593cc859dd2203b1c8773f0bd899161aa3f4a24844cba74d7037d0a004` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-REVIEWER-ISOLATED-1 | AC2 | `verification/ENV-BUNDLE-1-FU1/reviewer-rerun-isolated.log` | `cffa9666fbbe5f2adfe213de37a8beb20a994a38` | `4c1b9e469efd445863bd6be1888ec9bdc2688f5830cee708ceab6ec0539c347f` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-REVIEWER-ISOLATED-2 | AC2 | `verification/ENV-BUNDLE-1-FU1/reviewer-rerun-isolated-2.log` | `cffa9666fbbe5f2adfe213de37a8beb20a994a38` | `188097a7583267cab7061be719a90c10fc71bbc882e43d2e5a8aadefdc0b1141` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-RECORD | AC2 | `verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md` | `dca85f71ffa92f4f2dbd3cb212d7000ad87bc0b0` | `31147f840e2a55e2342c0d0e2b6ff0dbaa36862a7316acd181ef795e4f5c379a` | CANONICAL |
| ENV-BUNDLE-1-FU1-I1-HANDOFF | AC2/AC7 | `doc/handoffs/ENV-BUNDLE-1-FU1-cffa9666f.md` | `dca85f71ffa92f4f2dbd3cb212d7000ad87bc0b0` | `8f65745ffc7c297d3dfb65145fe886359ee97096269f080b587788f7c79e72db` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC3 | AC3 | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `89a10430acbaab7f0d82d42307c1b988978d8c4c66b9cf1e4c0fa4c62138a158` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-COPY-SIDECAR | AC4 | `verification/ENV-BUNDLE-1-FU1/ac4-copy-sidecar-to-main.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `2759eb47c6b8438f50421bc13e81cacd20f57e2a7fa0ad7f4e1e302e608f3dce` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-COPY-FRONTEND | AC4 | `verification/ENV-BUNDLE-1-FU1/ac4-copy-frontend-to-main.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `ec8bdd321e2600f31cf3e5b652b59553d3af6acdd8e3d9bf04e7d55d2ac65f57` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-SMOKE | AC4 | `verification/ENV-BUNDLE-1-FU1/ac4-main-core-smoke-after.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `1ec00efebcc249235135bdceb9ebdde8a7bdd2b82a617038b7aba0fa079240cc` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-AFTER | AC4 | `verification/ENV-BUNDLE-1-FU1/main-artifacts-after.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `b3f45be2f9fc7af05f3579cb68cf8cf365e9cbc1ab687bfcbf1b92b8967c8420` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC4-BEFORE | AC4 | `verification/ENV-BUNDLE-1-FU1/main-artifacts-before.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `04c8f25e2aa54761d181ef17dca08f0415c0104b84c998ef3f6aa2850823130e` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC5 | AC5 | `verification/ENV-BUNDLE-1-FU1/ac5-generated-side-effects.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `fee724c5e2aace61625c9541a9adddd9b569e0743324d2560e4cc6f6a82a8bbb` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-BEFORE-HEAD | AC6 | `verification/ENV-BUNDLE-1-FU1/main-head-before.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `e54ddf4b34a7ab9ac63ae498a34c1d26af00e3fceed536806876aba61951b641` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-AFTER-HEAD | AC6 | `verification/ENV-BUNDLE-1-FU1/main-head-after.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `de0b5bf57e8e6c84cdde9350fe87c25bcd3a87af106c5dafb0caab0862970850` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-BEFORE-STATUS | AC6 | `verification/ENV-BUNDLE-1-FU1/main-status-before.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-AFTER-STATUS | AC6 | `verification/ENV-BUNDLE-1-FU1/main-status-after.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-BEFORE-DIFF | AC6 | `verification/ENV-BUNDLE-1-FU1/main-diff-fingerprint-before.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `702c9eef86cd90e0c9cfd1f81a9389abc97adaf294193bfc736f9f30a0675ba5` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-AFTER-DIFF | AC6 | `verification/ENV-BUNDLE-1-FU1/main-diff-fingerprint-after.txt` | `998200d48e10899e2916a73143578c69bceb30cf` | `1a2a4b9b7e2d31cee65e24f38da7a4c95067baa6ec484f1cd8df6fbf2d5f572b` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-COMPARISON | AC6 | `verification/ENV-BUNDLE-1-FU1/main-status-comparison.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `a8330fd416ca8fc3ad89e86915da9aa3f08a90d3d38e3aca1d9ff088e5ece640` | CANONICAL |
| ENV-BUNDLE-1-FU1-AC6-OLD-CORE | AC6 | `verification/ENV-BUNDLE-1-FU1/main-old-core-ping-before.log` | `998200d48e10899e2916a73143578c69bceb30cf` | `23bb9dde73e3c8600295c0bd9e05f4c037f36451b524660a9c2a3a58ad3082f5` | CANONICAL |
| ENV-BUNDLE-1-FU1-RESOURCE | AC7 | `verification/ENV-BUNDLE-1-FU1/resource-manifest.json` | `998200d48e10899e2916a73143578c69bceb30cf` | `60729b5bc76ba32691b0f89cadfcd736f4e3b103e536f68d75f767a86cba3fc3` | CANONICAL |

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
- canonical_evidence_status：`registered_blob_level`；表内 SHA-256 对应固定实现 commit 中的 blob bytes。
- resource_closeout_status：`accounted_with_preserved_residuals`；manifest 列明保留的 worktree、ignored bundle/dist 与既有 venv。
- 删除、迁移、归档数量/字节数：删除 `0`；大型产物仅在 ignored 目标间刷新，不入库。
- 未关闭项及保留原因：AC3 `BLOCKED`（HostControl grant 返回 `REF_EXPIRED`）；独立 Review 尚未完成；source-backed 全套和 GUI/installer 未运行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 由 Coordinator 在 Review 后同步；本 Task 未触碰。
