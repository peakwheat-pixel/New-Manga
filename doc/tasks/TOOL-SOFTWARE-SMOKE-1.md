---
id: TOOL-SOFTWARE-SMOKE-1
title: 分层软件检查工具（替代手工 GUI 冒烟）
kind: implementation
governance_version: 3
status: in_review
language: zh-CN
suggested_owner: dsh
owner: dsh（本会话 Lead）
reviewer: reviewer-tool-smoke（独立 Reviewer，非实现者）
depends_on: [PLUGIN-RUNTIME-PACKAGED-PYTHON-1]
base_commit: 6e3ce06f96bb48bc7a8de0a114c8391a9bc82014
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: c680434eab1ff6abcc4bc204e844ecba0c41979a
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TOOL-SOFTWARE-SMOKE-1
allowed_paths:
  - tools/smoke/**
  - tests/tools/**
  - verification/TOOL-SOFTWARE-SMOKE-1/**
  - doc/tasks/TOOL-SOFTWARE-SMOKE-1.md
  - doc/handoffs/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
authorization: 用户 2026-10-23 要求制作「插件/软件检查工具」替代手工 GUI 冒烟；本会话选定方案 D。
---

# TOOL-SOFTWARE-SMOKE-1：分层软件检查工具（替代手工 GUI 冒烟）

## 来源与目标

**来源。** 用户 2026-10-23 要求用可重复、无人值守、可断言、低 token 的检查工具替代手工 GUI 冒烟。
前置证据：`verification/GUI-SANDBOX-SMOKE-1/smoke-notes.md` 记录的四个痛点（启动慢、鼠标/截图 token 消耗、
GUI 内 Hook 需要检测权重、结论无法自动断言）；`GUI-PLUGIN-SANDBOX-SMOKE-1` 因此 paused。
用户在本会话明确要求「先仔细看项目代码」，并选定**方案 D：分层检查工具**（Core 沙箱 + 真实 Core wire +
前端 tsc/Vitest + 真实 bundle），因为其后续仍会修改 UI/UX，需要不依赖 GUI 的稳定契约层。

**目标。** 新增一个只读的检查工具（不修改生产代码与共享契约），一条命令完成四层检查，输出机器可读 JSON
与简体中文摘要，退出码可判定；覆盖插件面、沙箱面、wire 面、前端面、打包面；默认无 GUI、无鼠标、截图关闭；
可重复执行且不残留临时插件/进程。

**实现。** 新增 `tools/smoke/**`（入口 `python -m tools.smoke.plugins`）与 `tests/tools/**`；复用既有生产装配
`assemble_production_core`、`PluginService`、`AppContainerSandbox`、`bootstrap.core_service` stdio 协议、
真实 `core-sidecar` bundle 与前端现有 `tsc`/Vitest 工具链。`src/**`、`apps/**` 生产代码未改。

**本机实测（2026-10-23，修复后 canonical 证据）。** Core 层 11 项 15.5s；Wire 层 6 项 0.5s；前端层 2 项 7.5s
（tsc 2.8s、Vitest 4.6s / 435 tests）；打包层 5 项 0.5s；单次全量 24.0s；`--repack` 层 7.3s（check 6.8s）。

## Acceptance Criteria

- [x] **AC1 一键入口与报告**：`python -m tools.smoke.plugins` 一条命令执行全部默认层；支持 `--only` / `--skip` / `--list-checks` / `--json PATH` / `--keep-artifacts` / `--repack`；输出 JSON（schema、每层/每检查项状态、稳定错误码、耗时）与中文摘要；退出码 0=全部 PASS（显式 skip 允许），1=存在 FAIL/BLOCKED，2=工具自身错误。 <<MET>>
- [x] **AC2 Core 沙箱层**：真实 AppContainer + 独立临时数据根上断言插件加载/拒绝（`PLUGIN_PERMISSIONS_UNSUPPORTED`）、启用/禁用、权限徽标数据、审计事件、根外读被拒、无权限插件网络栈被拒、`network` 权限插件被放行、超时返回 `PLUGIN_HOOK_TIMEOUT`、超时后子进程树被 Job Object 清理、fail-closed（`PLUGIN_HOOK_UNAVAILABLE`）。 <<MET>>
- [x] **AC3 Wire 层**：启动真实 `python -m bootstrap.core_service` 子进程，按 Tauri/前端实际消费的 JSON-lines 信封调用 `core.ping`、`plugins.list`、`plugins.set_enabled`、`plugins.set_plugin_enabled`、`plugins.audit_list`，断言默认关闭、状态往返、拒绝/未知/畸形请求的 typed 错误码、审计字段与 `core.shutdown` 正常退出；该层不依赖 DOM/视觉，供后续 UI/UX 改动守住后端契约。 <<MET>>
- [x] **AC4 前端层**：对 `apps/desktop/frontend` 执行 `tsc --noEmit` 与全量 Vitest（435 tests），断言全部通过；UI/UX 改动后仍由现有测试与类型检查兜底，无需启动 GUI 或占用鼠标。npm/node_modules 缺失时记 BLOCKED（不得写成 PASS），可用 `--skip frontend` 显式跳过。 <<MET>>
- [x] **AC5 打包层**：断言真实 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe` 存在、可在最小 PATH 下启动并导入 Hook 所需标准库、`_hook_interpreter()` 在模拟 frozen 布局下解析到该解释器，并在真实 AppContainer 中执行一个 Hook；`--repack` 复用 `packaging/m2ac5/verify_bundled_python.ps1` 做复制+启动+Hook 复验。 <<MET>>
- [ ] **AC6 幂等、无残留与回归**：连续两次全量运行 PASS 且不修改仓库跟踪文件；临时目录默认清理、无残留临时插件/进程；定向工具测试 PASS；全量 `python -m pytest tests -q` 无本 Task 引入的新失败（既有 3 例环境/历史失败在 `baseline-check.log` 如实记录，不冒充 PASS）；`check.ps1` PASS；独立 Reviewer（非实现者）复审通过。 <<PARTIAL: 等待独立 Reviewer 复审>>
- [x] **AC7 边界如实**：未修改 `src/**`、`apps/**` 生产代码与冻结 IPC 契约；未引入新依赖；不点击/拖拽 GUI、默认不截图、不做安装包冒烟、不验证检测模型推理；文档明确标注非目标；`GUI-PLUGIN-SANDBOX-SMOKE-1` 的恢复/关闭依据由 Lead 在 closeout 时决定，本 Task 不自动改变其状态。 <<MET>>

## 允许修改范围

- 新增 `tools/smoke/**`（检查工具本体；入口 `python -m tools.smoke.plugins`）。
- 新增 `tests/tools/**`（工具自身的定向测试；不替代验收性全量运行）。
- 新增 `verification/TOOL-SOFTWARE-SMOKE-1/**`（本 Task 证据）。
- 本 Task 文件、`doc/handoffs/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`
  （仅 Lead 集成登记与指针维护）。

## 禁止范围

- 不修改 `src/**`、`apps/**`（含前端、Tauri/Rust、IPC 契约、Schema、依赖清单）。
- 不修改其它 Task、Review、历史证据；不删除任何既有文件；不清理/GC/prune worktree。
- 不做 GUI 交互自动化（点击/拖拽/窗口控制）、不做安装包端到端、不验证模型推理质量。
- 不触碰用户真实数据根；运行数据只落在独立临时目录与 workspace/证据目录。
- 不执行 `git push/merge/reset/stash`；不调用 `agy`/`antigravity-dispatch`。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC5 验收 | `python -m tools.smoke.plugins --json verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json` | Windows；Python 3.14.6；node_modules；真实 bundle | PASS（4 层 / 24 项：23 PASS + 1 SKIP 为未传 `--repack`；exit 0；24.0s） | `smoke-report.json`、`run-1.log` |
| AC6 幂等 | `python -m tools.smoke.plugins` 连续两次 | 同上 | PASS / PASS（24.0s / 23.6s；临时目录无残留） | `run-1.log`、`run-2.log` |
| AC5 `--repack` | `python -m tools.smoke.plugins --only packaged --repack --json verification/TOOL-SOFTWARE-SMOKE-1/repack-report.json` | 同上 | PASS（5/5；7.4s；`verify_bundled_python.ps1` OK；`temp_plugin_dirs_cleaned=1`） | `repack-report.json`、`repack-run.log` |
| AC6 定向 | `python -m pytest tests/tools -q` | Python 3.14.6 | PASS：15 passed | `pytest-tools.log` |
| AC6 回归 | `python -m pytest tests -q -rs` | Python 3.14.6 | 2687 passed, 9 skipped, 3 failed（既有环境：transformers 4.48.3 缺 `RTDetrV2ForObjectDetection` ×2；历史 PySide6 viewmodel 测试超时 ×1；9 skip：docTR ×2、openssl unavailable ×6、registry-readiness 既有 guard ×1；`src/**`、`apps/**` 与本 Task 前既有 tests 未改动） | `pytest-full.log`、`baseline-check.log` |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 | PASS（最终运行见 Handoff） | Handoff、`governance-check.log` |

## 依赖、风险与阻塞

- **硬依赖**：`PLUGIN-RUNTIME-SANDBOX-2`、`PLUGIN-RUNTIME-CAPABILITY-1`、`PLUGIN-RUNTIME-PACKAGED-PYTHON-1`
  均已完成（approved），提供真实 AppContainer、network capability 与 bundle 解释器。
- **R1 环境耦合**：真实 AppContainer 要求 Windows 非受限账户（本机实测可用）；bundle 不存在或前端
  `node_modules` 缺失时对应层记 BLOCKED 而非 PASS，可用 `--skip` 显式跳过。
- **R2 网络波动**：`network` 放行只断言「非 PermissionError」，不做外网可用性断言。
- **R3 前端测试漂移**：未来改 UI/UX 会更新前端测试，工具只运行当前仓库测试；测试文件缺失即 BLOCKED/FAIL。
- **R4 AppContainer profile 残留**：profile 为 OS 级容器身份，工具不删除；临时插件目录与进程在退出时清理。
- **R5 全量 pytest 基线失败**：`transformers` 当前安装版本（4.48.3）缺少 `RTDetrV2ForObjectDetection`；
  历史 PySide6 viewmodel 测试超时。9 个 skip 原因为 docTR ×2、openssl unavailable ×6、registry-readiness 既有
  guard ×1（`pytest-full.log` 的 `-rs` 输出）。`baseline-check.log` 以 `git diff --stat 6e3ce06f9..HEAD -- src/apps/tests`
  与逐例复现证明与本 Task 无关；本 Task 不修环境、不把它们记为 PASS。
- **非阻塞**：`GUI-PLUGIN-SANDBOX-SMOKE-1` 保持 paused；本 Task 产出可作为 Lead 决定恢复/关闭的依据。

## 交付与运行记录

- Handoff：[TOOL-SOFTWARE-SMOKE-1-c680434ea.md](../handoffs/TOOL-SOFTWARE-SMOKE-1-c680434ea.md)（review 前 draft）。
- Review：`review-r1.md`（旧 head `963ff5e6f`，approved + 6 项 P2）与 `review-r2.md`（新 head `c680434ea`，待独立复审）。
- 实施提交：`c680434eab1ff6abcc4bc204e844ecba0c41979a`（工具 + 定向测试 + P2 修复）；证据提交：
  `7b2abfa00`（修复后 canonical 证据）；Task 登记：`ff94baf74`。
- 实际测试：2026-10-23，见上表与 `verification/TOOL-SOFTWARE-SMOKE-1/`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-SMOKE-REPORT | AC2/AC3/AC4/AC5/AC7 | `verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json` | 7b2abfa00 | 19a2ab9255b4a5c1560f1f193228ab126d42fe6a3f87ca79889d4ff01e160477 | CANONICAL |
| EV-RUN1 | AC1/AC6 | `verification/TOOL-SOFTWARE-SMOKE-1/run-1.log` | 7b2abfa00 | 79f4ec188890cd729f56666a2621c46b8bee61630deefc9e5b084c5790bf7d19 | CANONICAL |
| EV-RUN2 | AC6 | `verification/TOOL-SOFTWARE-SMOKE-1/run-2.log` | 7b2abfa00 | 4b3bdd0e6c3f58a71985fb6ce8b1e3b4c04cbcf00fadfd06aea40ea82b21d626 | CANONICAL |
| EV-REPACK-REPORT | AC5 | `verification/TOOL-SOFTWARE-SMOKE-1/repack-report.json` | 7b2abfa00 | 5d0deb8a8606c0f438781f5f87fbde6926e2de2f224c34358c2ca5d2df784ac5 | CANONICAL |
| EV-REPACK-RUN | AC5 | `verification/TOOL-SOFTWARE-SMOKE-1/repack-run.log` | 7b2abfa00 | 800822de4183be94e0c35c11020d79abce9662f161f43e6e47f1844c5f01feda | CANONICAL |
| EV-PYTEST-TOOLS | AC6 | `verification/TOOL-SOFTWARE-SMOKE-1/pytest-tools.log` | 7b2abfa00 | cba3576bb24f9013755b5d9d1cc667bd1b57c854ddb8e7ff91bd8cc4403e8f1b | CANONICAL |
| EV-PYTEST-FULL | AC6 | `verification/TOOL-SOFTWARE-SMOKE-1/pytest-full.log` | 7b2abfa00 | 0097a835c04c9711b237a088e3717ea7feed4e60c7f7400232f645c52df8f6f7 | CANONICAL |
| EV-BASELINE | AC6/AC7 | `verification/TOOL-SOFTWARE-SMOKE-1/baseline-check.log` | 7b2abfa00 | 7ca4398d05d5e863713d1690ca82333d850b876cfd18325bf3d1687cdf2e7a57 | CANONICAL |
| EV-REVIEW-R1 | AC6（历史：旧 head） | `verification/TOOL-SOFTWARE-SMOKE-1/review-r1.md` | 7b2abfa00 | d11918f03f41a80b93439ac2bb856a5f7c087775e270014374102b04f46a5381 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | NOT_APPLICABLE | — | — | 使用主 worktree，无新 worktree |
| temp | `%TEMP%/nm-software-smoke-*`、`%TEMP%/nm-bundled-hook-*` | DELETE_SAFE | — | — | 全量运行目录在 finally 清理；repack 脚本自建目录由工具在前后快照后删除（canonical 清理 1 个）；评审前遗留 3 个 `nm-bundled-hook-*` 已删除，2026-10-23 复查计数 0 |
| agent-output | — | NOT_APPLICABLE | — | — | 未产生 agent-output 资源；证据只入 `verification/TOOL-SOFTWARE-SMOKE-1/` |

## Closeout Record

- Closeout date / Codex：待独立 Review 与集成后填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；预计 0（仅临时目录已清理）。
- 未关闭项及保留原因：AC6 待独立 Review；全量 pytest 既有 3 例环境失败保留并记录，不在本 Task 修复。
- 当前指针清理：STATUS / Plan / Task 导航 / TASK_LEDGER 待 closeout 更新。
