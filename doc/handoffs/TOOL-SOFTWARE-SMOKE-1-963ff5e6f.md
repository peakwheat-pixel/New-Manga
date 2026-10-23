---
task_id: TOOL-SOFTWARE-SMOKE-1
author: dsh（Lead / 实现者）
recipient: Codex / 独立 Reviewer
base_commit: 6e3ce06f96bb48bc7a8de0a114c8391a9bc82014
delivery_head: 963ff5e6f77f153de2a58153940c96c7569ef22c
status: draft
---

# Handoff：TOOL-SOFTWARE-SMOKE-1

## 交付结果

新增只读分层软件检查工具，替代手工 GUI 冒烟的四项痛点（启动慢、鼠标/截图 token、GUI 内 Hook 依赖检测
权重、结论不可断言）。不修改任何生产代码、共享契约或依赖。

**提交列表（`main`，未 push）：**

| commit | 内容 |
|---|---|
| `ff94baf74` | Task 范围冻结 + Plan/STATUS/LEDGER 登记 |
| `963ff5e6f` | 工具本体 `tools/smoke/**` + 定向测试 `tests/tools/**`（delivery head） |
| `2052b4619` | 判别力证据（两次全量运行、`--repack`、定向/全量 pytest、基线对比） |

**新增入口：**

```powershell
# 从仓库根目录执行
python -m tools.smoke.plugins --json verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json
python -m tools.smoke.plugins --only core,wire
python -m tools.smoke.plugins --skip frontend
python -m tools.smoke.plugins --list-checks
python -m tools.smoke.plugins --only packaged --repack   # 可选：复用 verify_bundled_python.ps1
```

退出码：`0`=PASS（显式 skip 允许）；`1`=FAIL/BLOCKED；`2`=用法或工具内部错误。默认无 GUI、无鼠标、无截图；
临时目录在 `finally` 清理，`--keep-artifacts` 可保留。JSON 报告字段：`schema`、`layers[].checks[]`
（`id/status/code/message/duration_ms/detail`）、`summary`、`environment`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 入口/报告 | `python -m tools.smoke.plugins --list-checks`；`--json PATH`；`--only/--skip` | Windows；Python 3.14.6；`963ff5e6f` | PASS：0/1/2 退出码与 JSON/中文摘要均验证 | `run-1.log`、`smoke-report.json` |
| AC2 Core 沙箱 | 全量运行中的 `core` 层（11 项） | 真实 AppContainer；临时数据根 | PASS：15.0s；加载/拒绝、状态、审计、FS/NET 拒绝、NET 放行、超时、tree-kill、fail-closed | `smoke-report.json` |
| AC3 Wire | 全量运行中的 `wire` 层（6 项） | 真实 `python -m bootstrap.core_service` 子进程 | PASS：0.5s；`core.ping`/`plugins.*`/typed errors/`core.shutdown` | `smoke-report.json` |
| AC4 前端 | 全量运行中的 `frontend` 层 | 真实 `node_modules` | PASS：7.4s；`tsc --noEmit` + 435 Vitest tests | `smoke-report.json` |
| AC5 打包 | `packaged` 层 + `--only packaged --repack` | 真实 `core-sidecar` bundle | PASS：0.5s / 10.4s；bundle 解释器存在、最小 PATH 启动、frozen 解析、AppContainer Hook、`verify_bundled_python.ps1` OK | `repack-report.json`、`repack-run.log` |
| AC6 幂等 | 连续两次全量运行 | 同上 | PASS / PASS（23.3s / 23.5s）；运行后无临时目录；`git status --porcelain --untracked-files=no` 为空 | `run-1.log`、`run-2.log` |
| AC6 定向 | `python -m pytest tests/tools -q` | Python 3.14.6 | PASS：9 passed | `pytest-tools.log` |
| AC6 回归 | `python -m pytest tests -q` | Python 3.14.6 | **2681 passed, 9 skipped, 3 failed**：`transformers` 安装版本缺 `RTDetrV2ForObjectDetection` ×2；历史 PySide6 viewmodel 测试超时 ×1。`git diff --stat 6e3ce06f9..HEAD -- src/tests` 证明 `src/**` 与既有 tests 未改，仅新增 `tests/tools/`；逐例复现见证据 | `pytest-full.log`、`baseline-check.log` |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根，`in_review` 状态 | PASS（最终 closeout 前再次运行） | 本 Handoff / Review |
| AC6 独立 Review | 非实现者复审 `base_commit..delivery_head` + 文档 | `reviewer-tool-smoke` | 待执行 | `review-r1.md`（待提交） |

**未跑 / 非目标：** GUI 点击/拖拽、截图、NSIS/Tauri 安装包端到端、检测模型推理质量、真实用户数据根。
**全量 pytest 的 3 个失败不是本 Task 引入**：失败位于既有 provider 环境依赖与历史 PySide6 测试；本 Task 未修改
`src/**` 与任何既有测试，证据见 `baseline-check.log`。不将其写成 PASS。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支 `main`；无新 worktree。
- 复现：

```powershell
cd 'G:/CODEX/New Manga'
python -m tools.smoke.plugins --json verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json
python -m pytest tests/tools -q
pwsh -NoProfile -File tools/governance/check.ps1
```

- 前置：Windows 非受限账户（AppContainer）；Python 3.14.6；`apps/desktop/frontend/node_modules` 已安装；
  真实 bundle 存在（`apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe`）。
- 接收者检查点：① 工具未改生产代码/契约（`git diff 6e3ce06f9..HEAD -- src apps` 为空）；② 四层报告 PASS；
  ③ 两次运行幂等；④ 检查器 PASS；⑤ 全量 pytest 仅上述 3 个既有失败。

## 下一任务建议（必填）

- Task ID / 标题：无需新实现 Task；建议 Lead 依据本 Task 结果裁决 `GUI-PLUGIN-SANDBOX-SMOKE-1`（paused）
  是否关闭或缩窄为「可选 CUA 截图附件」，后者需用户新授权。
- 推荐 Agent / Reviewer：Lead（Codex 角色）裁决；如恢复 GUI 附件，推荐 dsh 实现、独立 Reviewer 复审。
- 推荐原因与前置依赖：本工具已覆盖手工冒烟中的插件/沙箱/wire/前端/打包断言；剩余仅视觉证据与安装包，
  不在本 Task 授权内。
- Recovery point：`G:/CODEX/New Manga`，`main`，base `6e3ce06f9`，delivery `963ff5e6f`；无需新 worktree。
- 允许修改路径：无（本 Task 已冻结，不再扩大）。
- 禁止范围与新增授权条件：GUI 点击/截图、安装包冒烟均需新 Task 与用户授权；不得在检查工具中引入
  `agy`/`antigravity-dispatch` 或修改生产契约。
- 交付物：无新增；现工具与证据保留在原路径。
- 验证命令、环境与完成 Gate：`python -m tools.smoke.plugins`、`python -m pytest tests -q`、
  `pwsh -NoProfile -File tools/governance/check.ps1`；环境同「接收方式」。
- 可直接转发给 Agent 的指令：「只读核对 `TOOL-SOFTWARE-SMOKE-1` 的 Task/Handoff/证据与 `main` 提交
  `963ff5e6f`，运行 `python -m tools.smoke.plugins` 与 `check.ps1`；不要修改生产代码或扩大范围，输出独立
  Review（不得自审）。」

## 风险与遗留

- **R1 全量 pytest 基线**：3 例既有失败（transformers 缺类 ×2、PySide6 超时 ×1）保留原状；修复它们需要单独的
  环境/历史测试 Task，不属于本工具授权范围。
- **R2 前端测试漂移**：未来 UI/UX 改造会更新 Vitest 测试；工具运行当前仓库测试，若测试被删/改名，前端层会报
  `FRONTEND-DEPS-MISSING` 或 Vitest 失败，不会静默跳过。
- **R3 AppContainer profile**：OS 级 profile 会被复用，不删除；临时插件目录与子进程已清理。
- **R4 网络依赖**：`network` 放行只断言非 `PermissionError`，不保证外网可用。
- 回退：删除 `tools/smoke/**`、`tests/tools/**`、`verification/TOOL-SOFTWARE-SMOKE-1/**` 与相关文档提交即可；
  不影响生产代码。
