---
task_id: UIUX-V2-RUNTIME-REALCORE-2
author: Codex
recipient: DeepSeek Harness
base_commit: 2166c4dfb4f98d85139aff6d6822bdfd5660337b
delivery_head: 本文件所在的唯一交付提交；精确 SHA 见本次最终回复
status: partial
---

# Handoff：UIUX-V2-RUNTIME-REALCORE-2

## 交付结果

实现与证据在同一个本地提交中交付（未 push）。当前 Task 未达到全绿 Gate：G4、G5 达成，G1 未达成，G2、G3 部分达成。完整结果见 [验收 README](../../verification/UIUX-V2-RUNTIME-REALCORE-2/README.md)。没有改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 或 Task 卡；STATUS 仍记录该 Task 为 `ready`/Owner 待派，需由 DSH 处置当前状态。

改动文件：

- `apps/desktop/frontend/e2e/uiux-v2/lib/app.mjs`
- `apps/desktop/frontend/e2e/uiux-v2/lib/env.mjs`
- `apps/desktop/frontend/e2e/uiux-v2/run.mjs`
- `apps/desktop/frontend/src/pages/Shelf.test.tsx`
- `apps/desktop/src-tauri/src/core_bridge.rs`
- `apps/desktop/src-tauri/src/ac1_bridge.rs`
- `verification/UIUX-V2-RUNTIME-REALCORE-2/**`
- `doc/handoffs/UIUX-V2-RUNTIME-REALCORE-2-handoff.md`

代码提交前工作区相对基线 `2166c4d` 仅含以上任务改动；最终 SHA 由最终回复给出，未推送。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| TypeScript | `node node_modules/typescript/bin/tsc --noEmit` | Task-local `process-env/typescript-final` | PASS，exit 0，输出为空 | `verification/UIUX-V2-RUNTIME-REALCORE-2/test-typescript.log`、`.result.json` |
| Frontend tests / G5 | `npx vitest run` | Task-local `process-env/vitest-final` | PASS，60 files / 567 tests | `test-vitest.log`、`.result.json` |
| G4 | `cargo test --release non_ascii_payload_returns_visible_error_code` | Task-local `process-env/cargo-g4-final` | PASS，2 passed | `test-cargo-g4-focused.log`、`.result.json` |
| Rust 全量 | `cargo test --release` | Task-local `process-env/cargo-test-final` | FAIL，exit 101：146 passed、23 failed、1 ignored；含互不兼容的 source-backed / packaged 测试环境前置条件 | `test-cargo-release.log`、`.result.json` |
| E2E S1–S10 | `node e2e/uiux-v2/run.mjs`，Acceptance EXE / CDP 9345 | `run-i29`；SHA `E58CFE59DFEACA840AFDFB1E58AC4A5AC3E283BCC91A97F2DFA75BBC63D142EA` | FAIL，exit 1；S1–S7 pass，S8/S9/S10 含未达成项 | `verification/UIUX-V2-RUNTIME-REALCORE-2/run-i29/report.json`；stdout 在 workspace `process-logs/e2e-final-29.log` |
| Frontend build | `npm run build` | Task-local `process-env/frontend-build-2` | PASS，exit 0 | `build-frontend-final.log`、`.result.json` |
| Release build | `cargo tauri build --no-bundle` | Task-local `process-env/release-build-final` | PASS，exit 0；SHA `B47689C5F547432F2DED8A8A5F34837E4F237BB370EC734E3BC991CFBA13905B` | `build-tauri-release-final.log`、`.result.json` |
| Acceptance build | `cargo tauri build --no-bundle --config tauri.acceptance.conf.json` | Task-local `process-env/acceptance-build-final` | PASS，exit 0；SHA `E58CFE59DFEACA840AFDFB1E58AC4A5AC3E283BCC91A97F2DFA75BBC63D142EA` | `build-tauri-acceptance-final.log`、`.result.json` |

G1 的 native picker 未提交所选文件，故没有实际页图导入、Core/UI 页数对照或错误码断言。G2 的 `run-i29` 仅 Settings 与 Shelf 显示 `CORE_UNAVAILABLE`；Core 以新 PID `50360` 重启并经 `core_ping` 回到 `ready`，Shelf 点击重试后从真实 Core 拉回 1 部作品；Workbench/Reader 错误态未通过。G3 在 900×700、DPR 2 下检测到 `scrollWidth=1024`、`clientWidth=900`；其余相关布局检查通过。失败报告均保留，过程日志/截图和 Task 数据留在 workspace。

## 接收方式

- 仓库：`G:\CODEX\New Manga`
- Branch：`main`
- Base：`2166c4dfb4f98d85139aff6d6822bdfd5660337b`
- Delivery head：本文所在单提交；其精确 SHA 在 Codex 最终交付回复中。
- 复现命令、环境变量、EXE SHA 和全部限制见 `verification/UIUX-V2-RUNTIME-REALCORE-2/README.md`。
- 隔离数据根示例：`G:\CODEX\New Manga.workspace\task-envs\UIUX-V2-RUNTIME-REALCORE-2\run-i29\data-root\library.db`。不得触碰 `C:\Users\49745\AppData\Local\New Manga`。

## 下一任务建议（必填）

- Task ID / 标题：`UIUX-V2-RUNTIME-REALCORE-2` 独立 Review 与部分 Gate 处置（现有 Task，不创建占位 Task）。
- 推荐 Agent / Reviewer：DeepSeek Harness（DSH）。
- 推荐原因与前置依赖：DSH 未参与实现；交付存在 G1/G2/G3 缺口及 Rust 全量测试失败，需要独立核验后决定后续 Task 与状态变更。
- Recovery point：仓库 `G:\CODEX\New Manga`，branch `main`，base `2166c4dfb4f98d85139aff6d6822bdfd5660337b`，head 为本文所在单提交（SHA 见最终回复）。
- 允许修改路径：Review 期间只读本提交、Task 卡、README/Handoff 和列明的原始证据；若需修复，先由 DSH 创建并释放新的 Task，再按新卡指定路径。
- 禁止范围与新增授权条件：不得访问真实用户库；不得改产品视觉、交互或 IPC 形状；不得改 `tauri.conf.json`；不得在未释放新 Task 前继续实现或更新本 Task 的状态指针。
- 交付物：DSH 独立 Review，逐项裁定 G1–G5、四条验收命令、E2E 隔离、两个 EXE SHA 与 full Rust test 前置条件；必要时提出下一 Task。
- 验证命令、环境与完成 Gate：Review `verification/UIUX-V2-RUNTIME-REALCORE-2/README.md`、`run-i29/report.json` 和 workspace `process-logs/e2e-final-29.log`；复跑需使用 README 所列 Task-local 环境。只有缺口全部关闭、全量命令满足 Gate 且集成验证通过后，才能建议 Task `done`。
- 可直接转发给 Agent 的指令：

  > DSH，请在 `G:\CODEX\New Manga` 的 `main` 分支独立 Review `UIUX-V2-RUNTIME-REALCORE-2` 的交付提交（SHA 见本 Handoff 所在提交及 Codex 最终回复，base 为 `2166c4dfb4f98d85139aff6d6822bdfd5660337b`）。先只读检查 `verification/UIUX-V2-RUNTIME-REALCORE-2/README.md`、`run-i29/report.json`、workspace `process-logs/e2e-final-29.log`、`test-cargo-release.log` 与代码 diff；按 G1–G5、隔离边界、Rust 全量测试与两版 EXE SHA 给出独立结论。不要访问真实用户库，不要修改产品视觉/交互/IPC/`tauri.conf.json`，不要 push。若需实现修复，请先另建并释放 Task、明确 Owner/Reviewer/base/worktree/allowed paths 后再安排。

## 风险与遗留

- G1 目前阻塞在 Windows 原生文件选择器的脚本提交；不能声称真实页图导入通过。
- G2 supervisor 自动恢复后能读回书架数据，但 Workbench/Reader 的错误码状态未观察到。
- G3 900px 宽视口仍横向溢出 124px；本 Task 不允许修改产品布局。
- `cargo test --release` exit 101 的原始日志已保留；G4 两条定向测试通过，但不能替代全量 Rust 测试。
- 本次没有 push。task 状态、DAG 与集成由 DSH 按 Review 结果处置。

## 返修轮 r2 追加交付（2026-10-26）

本段追加记录 r1 复核后的修订；上一轮已通过的 G4、G5、S1–S7 保留，未改其断言，也未修改产品源码/CSS/TSX、IPC、`tauri.conf.json`、STATUS、REBASELINE_PLAN 或 TASK_LEDGER。本次交付为本文件所在的新本地提交，未 push；精确 SHA 见提交历史和本次交付回复。

### 逐项结果

- **R1 — 未达成。** `run.mjs` 移除了 PowerShell/UIAutomation 原生 picker 操作，改为导入对话框打开后查询 CDP DOM，并在可用时调用 `DOM.setFileInputFiles`、验证页面 `FileList`。但真实 EXE 的 ImportDialog 没有 `input[type=file]`：`run-i33/report.json` 记录 `rootInputNodeId=0`、`dialogNodeId=230`、`inputNodeId=0`。现有 Tauri command 自行调用原生 picker，IPC 没有本地路径参数。没有文件被交给页面/Core，真实 PNG 导入、Core/UI 页数对照和错误码路径未完成。当前 Task 禁止产品源码和 IPC 修改；需 DSH 另行冻结/释放具备受支持文件输入路径的 Task。
- **R2 — 已达成。** S9 在一次定向 sidecar 故障后，书架、工作台、阅读器、设置四页均显示可见 Core 错误码；supervisor 恢复 `core_ping=ready` 后逐页回到正常内容。报告 S9 为 12 PASS / 0 FAIL，见 `verification/UIUX-V2-RUNTIME-REALCORE-2/run-i33/report.json`。
- **R3 — 按裁定记录。** S10 水平溢出记为 `KNOWN_DEFECT`，检测值 `docWidth=1024`、`clientWidth=900`、`pageWidth=1024`，不让该检查使场景失败；产品布局另立 Task。
- **R4 — 记录完成。** README 新增 23 项 Cargo 全量失败明细、原始错误、当前源代码实际使用的环境变量和分组复跑命令，并给出本卡改动模块的 focused exit 0 证据。`M2RC1_PACKAGED_DIR` 在当前 checkout 无读取点，实际 packaged 测试要求 `M2RC1_PACKAGED=1`。
- **R5 — 已达成。** 每项检查记录 `PASS` / `FAIL` / `KNOWN_DEFECT`、`label` 与 `detail`；每个 scenario 记录 `checkSummary`、`passRate`。`test-e2e-r2.result.json` 校验 `all_checks_have_status=true`、`all_checks_have_label_and_detail=true`。

### 本轮验收

| 命令 | 实际结果 | 证据 |
|---|---|---|
| `node e2e/uiux-v2/run.mjs` | **exit 1**，仅 S8 因当前产品没有 file input 而失败；S1–S7、S9 通过，S10 缺陷状态为 `KNOWN_DEFECT` | `verification/UIUX-V2-RUNTIME-REALCORE-2/test-e2e-r2.log`、`test-e2e-r2.result.json`、`run-i33/report.json` |
| `node node_modules/typescript/bin/tsc --noEmit` | **exit 0** | `test-typescript-r2.log`、`test-typescript-r2.result.json` |
| `npx vitest run` | **exit 0**，60 files / 567 tests | `test-vitest-r2.log`、`test-vitest-r2.result.json` |
| `cargo test --release non_ascii_payload_returns_visible_error_code` | **exit 0**，`core_bridge`、`ac1_bridge` 两项通过 | `test-cargo-request-encoding-r2.log`、`test-cargo-request-encoding-r2.result.json` |

Cargo 全量输出仍以既有 `test-cargo-release.log` 为准：exit 101，146 passed、23 failed、1 ignored；README 逐项列出 6 条 `library_bridge::tests::*`、12 条 packaged 测试和其余 5 条 `tests::*` 的实际报错。定向测试成功不能替代完整 Cargo Gate。TypeScript、Vitest、E2E 原始日志和机器结果均位于 `verification/UIUX-V2-RUNTIME-REALCORE-2/`。

### 建议 DSH 下一步

请 DSH 独立复核本修订提交、README、`run-i33/report.json` 和四条验收日志，并处置 Task 状态。R1 不具备当前允许范围内的实现路径；如要关闭该 Gate，建议先定义并释放独立 Task，冻结如何让前端取得真实文件并交给 Core 的产品/IPC 契约，再安排实现与独立 Review。当前不得据此把本 Task 标为 `done`。
