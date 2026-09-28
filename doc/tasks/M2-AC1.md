---
id: M2-AC1
title: M2-AC1 end-to-end acceptance on the M2 baseline
kind: implementation
status: in_progress
release_state: M2_END_TO_END_ACCEPTANCE_RELEASED
approval: approved_by_user_2026-09-28
execution_approval: approved_by_user_2026-09-28_explicit_task_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [M2-RC2]
base_commit: 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d
branch: agent/zcode/M2-AC1-end-to-end-acceptance
worktree: G:/CODEX/New Manga.worktrees/M2-AC1-zcode
integration_commit: null
---

# M2-AC1 end-to-end acceptance on the M2 baseline

## 来源与目标

来源是 [REBASELINE_PLAN 的 M2 Acceptance Backlog 首行](../REBASELINE_PLAN.md#m2-acceptance-backlog-planning-rows-and-explicit-releases) 与 [D08 AC-SMOKE](../08_ACCEPTANCE_CRITERIA.md) 的 Mock / Local Pipeline → Save → Reader → Export → Restart 片段。依赖 [M2-RC2](M2-RC2.md) 已于 `88f972fe` 集成。

Owner=ZCode（建议执行角色：`heavy_task_executor`）；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。固定实现基线为 `7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`。目标是在 React + TypeScript / Tauri / Python Core / SQLite 的 M2 桌面路径上，交付并验证一个确定性的 Mock/Local 成功闭环：执行 Pipeline、保存结果、真正退出并重启进程、恢复结果、在 Reader 阅读并导出。

允许为闭环补齐必要的产品代码和专用验收 harness。Mock/Local 必须确定且可重复，不调用网络、真实 docTR、模型权重或用户漫画。测试模式仅在显式测试启动配置下开放，不得扩大生产 WebView/Tauri command surface。

## Acceptance Criteria

- [x] **AC1 — 确定性 Pipeline 成功路径：** 使用仓库内或临时目录中的合成 Book / Chapter / 多页输入，走 M2 Python Core 与桌面宿主的真实调用链，以 Mock/Local provider 成功执行。记录 provider、输入 fixture 清单、预期结果和输出摘要；两个独立运行的摘要一致，状态为成功完成，且未触碰真实模型或网络。
- [x] **AC2 — 结果保存：** 成功结果通过 M2 SQLite 持久化路径保存。重启前核对结果记录与生成页面/文件可由持久化状态重新读取；若确有必要新增 schema/migration，仅限本 AC 所需的非破坏性结果持久化，并提交升级与恢复证据。
- [x] **AC3 — 进程重启恢复：** 先正常结束桌面进程及其 Core 子进程，再以相同的临时数据根目录启动新进程。以不同 PID 或等价的进程级证据证明确实重启；不依赖内存对象、不重新运行 Pipeline 或重建 fixture，即可恢复同一 Chapter 与结果。
- [x] **AC4 — Reader 阅读：** 在恢复后的桌面会话中打开同一结果，显示合成页面并完成至少两页的阅读/翻页；证据需关联到 AC2 保存的结果，不能用进程内 mock 状态替代读取路径。
- [x] **AC5 — 导出验证：** 从恢复后的 Reader 导出当前页的单图 PNG；验证导出文件非空、可解码，且像素摘要与 Reader 展示的同一合成页面一致。此项只覆盖该确定性样例的 PNG 导出，不代表 D08 全部导出格式均已验收。
- [x] **AC6 — 可复现证据与诚实 Gate：** 提供可从仓库根目录运行的 `python verification/M2-AC1/run_e2e.py`，覆盖至少两次独立确定性运行及其真实进程重启，并将命令、环境、PID/恢复结果、摘要、Reader/export 结果和原始日志写入 `verification/M2-AC1/`。Gate 必须对 `FAIL`、缺失结果、`NOT_RUN` 失败关闭；环境不满足时标 `BLOCKED`，不得写成 PASS。Handoff 说明所有未覆盖项及独立 Review 所需固定 head。

## 允许修改范围

- `apps/desktop/frontend/src/**`：仅实现 AC1–AC5 所需的 M2 页面、调用与 Reader/export 展示。
- `apps/desktop/src-tauri/src/**`：仅实现相同闭环所需的宿主/Core 启动与 IPC；测试 command 只能在显式测试启动模式下注册，不得进入生产 command surface。
- `src/application/library/**`、`src/application/tasks/**`、`src/application/translation/**`、`src/application/reading/**`、`src/application/export/**`、`src/bootstrap/**`、`src/domain/**`、`src/ports/**`：仅本 Task 闭环所需的 Python Core 装配、Pipeline、结果恢复和读取/导出逻辑。
- `src/infrastructure/pipeline/**`、`src/infrastructure/providers/**`、`src/infrastructure/sqlite/**`、`src/infrastructure/imaging/**`：仅本 Task 的 Mock/Local provider、SQLite 结果保存/恢复及 Reader/export 输入输出路径。SQLite schema/migration 仅按 AC2 的限缩条件修改。
- `tests/m2_acceptance/**`、`verification/M2-AC1/**`、本 Task 文件、`doc/handoffs/M2-AC1-*.md`。

不得因测试便利修改其他路径；超出此清单先暂停并交 Codex 另行登记范围。

## 禁止范围

- 不实现或验收真实 docTR/模型权重、联网 Provider、Provider 缺失 fail-closed、源哈希/Managed Copy/人工修改/Lock/current 或 pinned Revision 完整性、Reader export lineage、Library page-count/unknown 语义、干净机安装、无系统 Python 启动、打包发布、冷启动性能、Windows 支持矩阵或 GUI console policy；这些 backlog/Release Gate 行仍未登记。
- 不修改 Legacy PySide6/QML、`packaging/**`、共享 M2 Contract、根目录/前端/Rust 依赖或锁文件、打包配置、用户源文件、真实凭据或模型权重。
- 不借用既有 `M2-RC1` 资源协议探针来声称其已覆盖 Pipeline / Reader / Export；M2 安全及打包边界保持既有 `UNVERIFIED` / `NOT_RUN`。

## 测试要求

| 场景 / AC | 计划命令或步骤 | 环境与判定 | 实际结果 | 证据 |
|---|---|---|---|---|
| Core acceptance | `python -m pytest tests/m2_acceptance -q` | Windows；runner 与被测代码均用 TASK-012-py312 venv（Python 3.12.3，日志头记录解释器路径）；合成输入；新建专用测试集 | **PASS**（4 passed, 0 failed, EXIT 0） | [pytest-m2-acceptance.log](../../verification/M2-AC1/pytest-m2-acceptance.log) |
| Tauri host regression（如有 Rust 改动） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | Windows；cargo 1.98.1 | **PASS**（26 passed, 0 failed, EXIT 0） | [cargo-test.log](../../verification/M2-AC1/cargo-test.log) |
| React regression（如有前端改动） | `npm test --prefix apps/desktop/frontend -- --run` | Node v24.15.0 / npm 12.0.1；既有 lockfile | **PASS**（3 files, 19 passed, EXIT 0） | [vitest.log](../../verification/M2-AC1/vitest.log) |
| M2 end-to-end gate | `python verification/M2-AC1/run_e2e.py`（完整构建版，最终证据） | Windows + WebView2；gate runner 与桌面/Core sidecar 均运行于 TASK-012-py312 venv（gate JSON `EVN-runner-python`/`runner_executable` 字段记录，证据↔commit 经 `implementation_commit` 绑定）；同一隔离临时数据根（%TEMP%）；未使用用户数据 | **PASS**（终版 gate GATE PASS **45 场景**，含 `EVN-pyside6` 环境门与 F-001/002/004 新增断言；r1 前 36 场景旧格式存档见 [e2e-evidence](../../verification/M2-AC1/e2e-evidence/raw/e2e-gate.json) 及其 NOTE.md；桌面/Core PID 均跨启动不同） | [e2e-gate-full](../../verification/M2-AC1/e2e-gate-full/raw/e2e-gate.json) |
| 范围与 whitespace | `git diff --name-status 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d..<reviewed-head>`；`git diff --check 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d..<reviewed-head>` | 固定 reviewed head；逐项对照允许/禁止路径 | **PASS**（diff --check exit 0；全路径审计见 Handoff §范围审计） | Handoff / Review / Codex integration record |
| 全仓回归（Owner 加跑） | `python -m pytest -q -p no:cacheprovider -rs` | 同 venv；验证 core_assembly 生产装配零回归 | **非本 Task 引入的 2 failed**：最终重采 `2 failed, 1320 passed, 5 skipped, EXIT 1`——失败集中在 Legacy QML 行点击测试 `tests/ui_shell/test_repair13_import_entry.py`（Task 禁改域 `tests/ui_shell/**`，与本 Task 19 路径零交集）；同一时刻在零 M2-AC1 改动的主 checkout @1347a67c 复现完全相同 2 失败（[base 对照](../../verification/M2-AC1/ui-shell-base-control-20260928.log)）；同工作区当天早些时候曾 **1322 passed / EXIT 0**（历史日志取回：`git show a74ce105:verification/M2-AC1/pytest-full-suite.log`）→ 判为会话级环境回归；失败原样保留未隐藏 | [pytest-full-suite.log](../../verification/M2-AC1/pytest-full-suite.log)（头部 NOTE）、[ui-shell-base-control-20260928.log](../../verification/M2-AC1/ui-shell-base-control-20260928.log) |

只运行实际有改动的语言套件；E2E 与范围 Gate 必须执行。工具或环境不可用时写 `BLOCKED` / `NOT_RUN`，不可从 unit tests 推断端到端 PASS。

## 依赖、风险与阻塞

- 硬依赖：[M2-RC2](M2-RC2.md) `done`；Contract 1.1 固定 blob `fc35913801297ee1876ea395f9c5041a16226f20`，本 Task 不修改 Contract。
- 仅验证 Windows + WebView2 的本地开发运行；本 Task 不覆盖安装包与无系统 Python 环境。
- 若实现 AC 所需的共享 API 或 schema 变化超出上列闭环，停下提交最小变更请求；不得顺带关闭其他 M2 Acceptance Backlog 行。

## 交付与运行记录

- 状态：`ready`；Owner=ZCode（`heavy_task_executor`），Reviewer=DeepSeek Harness（非作者），Integrator=Codex。
- 释放证据：[release-7db0e7b6](../../verification/M2-AC1/release-7db0e7b6.md)。Owner worktree 尚待 Codex 在冻结路径创建；从固定 base 创建后，只从释放 commit 取入本 Task 文件并先提交 `ready` → `in_progress` claim，不将治理提交合入实现历史。
- Handoff、Review、实际运行结果与最终 `integration_commit` 待交付后由各责任人填写；当前所有测试均为 `NOT_RUN`。
