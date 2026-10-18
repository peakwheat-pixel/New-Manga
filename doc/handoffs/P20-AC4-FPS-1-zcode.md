---
task_id: P20-AC4-FPS-1
author: ZCode
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 011293151
status: delivered_for_review
---

# Handoff：P20-AC4-FPS-1（AC4 帧率与帧时间测量钩子）

## 交付结果

实现 commit `011293151`（main，仅 8 个明确路径；本文档随其后的文档 commit 一并入库）。

| 交付物 | 路径 | 说明 |
|---|---|---|
| 采样钩子本体 | `apps/desktop/frontend/src/perf/fpsRecorder.ts` | 默认关闭的 rAF 帧间隔记录器；CSV/JSON/标题摘要导出；kept/excluded 双口径 |
| 导出面板 | `apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx` | 仅采样开启时挂载；下载/剪贴板/textarea 三导出通道；运行中不做定时刷新（避免污染帧时间） |
| 接线 | `apps/desktop/frontend/src/main.tsx` | 默认路径只做一次开关求值，无 rAF/无数组/无面板 |
| 单元测试 | `src/perf/fpsRecorder.test.ts`（15 用例）、`src/perf/FpsRecorderPanel.test.tsx`（7 用例） | AC1 零开销证明 + 采样/排除审计/汇总数学/导出通道 |
| 测量脚本 | `verification/P20-AC4-FPS-1/run-ac4-fps.ps1` | Coordinator 真实桌面执行；%TEMP% 隔离根；独立复算 avg/p95/max；收尾全退进程 |
| 步骤说明 | `verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md` | 构建链、开关口径、人工步骤、判读口径、产物布局、已知限制 |
| 测试证据 | `verification/P20-AC4-FPS-1/npm-test-20261018.log` | 32 files / 319 tests passed，exit 0 |

**开启方式（Owner 冻结，三通道任一显式开启，默认全关）**：
1. 构建期：`VITE_M2_FPS_SAMPLING=1 npm run build`（测量构建主通道；Tauri v2 编译期嵌入 dist，需重编译 debug exe 才生效）
2. 查询参数：`?m2_fps=1`
3. localStorage：`m2rc1_fps_sampling=1`

### AC 对照

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认关闭零开销 | **PASS**（Owner 可执行部分） | 单测证明：模块 import + 开关求值后 rAF spy 0 次调用、`getActiveFpsRecorder()===null`（无实例即无采样数组）；App 默认渲染不含面板；rAF 注册点仅 `start()` 与帧回调内部，无常驻回调 |
| AC2 结构化产物 | **PASS**（单元级） | CSV（`seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason`）/ JSON（meta+summary+samples）；落盘仅经保存对话框由调用方选 OutDir 或 UIA 抓取写 OutDir；代码无任何路径写入逻辑，不触碰 `%APPDATA%\com.newmanga.m2rc1.desktop`，无默认落盘 |
| AC3 真实桌面测量 | **NOT_RUN（Owner 范围外）** | 窗口级测量属 Coordinator（dsh, epoch 8）；脚本与说明已交付；样例导入为脚本暂停提示的人工步骤 |
| AC4 p95 如实记录 | **PASS**（机制层） | 排除仅两类且逐样本留痕（`raf_gap_ge_1000ms` / `non_positive_delta`），尖峰样本一律保留在 CSV；汇总恒含 p95/max；阈值 50ms 为常量不可配置 |
| AC5 撕裂只记 limitation | **NOT_VERIFIED_BY_RULING** | 脚本 metadata 与 GUIDE 显式声明；未做任何客观验证、未写 PASS |
| AC6 不回归 | **PASS** | `npm test` 32 files / 319 tests passed（基线 30 files / 294 tests 全数保留 + 新增 22）；`npx tsc --noEmit` exit 0；AC4 既有延迟结论（avg=36.0ms、20/20 有效）未触碰未覆盖，直接复用 `verification/P20/ac4-20261018-0720/**` |
| AC7 不回归 P20 其他 AC | **PASS** | 变更面仅 `frontend/src/perf/**` + `main.tsx` 接线；未触碰 IPC/契约/Schema/ACL/依赖/`src-tauri/**`；AC2/AC3/AC5/AC6/AC7 相关实现零改动 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2/AC4 机制 | `npm test`（frontend，独占、无管道） | Windows 11，commit `011293151` | PASS（319/319，exit 0） | `verification/P20-AC4-FPS-1/npm-test-20261018.log` |
| 类型检查 | `npx tsc --noEmit` | 同上 | PASS（exit 0） | 本 Handoff 记录（无独立日志） |
| AC3 单页滚动 | 待 Coordinator 执行 `run-ac4-fps.ps1 -Mode single` | 真实交互桌面 | NOT_RUN | `verification/P20-AC4-FPS-1/run-*/`（待产出） |
| AC3 Webtoon 滚动 | 待 Coordinator 执行 `-Mode webtoon` | 同上 | NOT_RUN | 同上 |
| AC5 撕裂 | 不执行（用户裁决） | — | NOT_VERIFIED_BY_RULING | 脚本 `fps-metadata.txt` 固定写入声明 |

未运行项理由：真实桌面窗口级测量明确划归 Coordinator（本机 CDP 端口被阻断、headless Agent 无法可靠操作 WebView2 窗口；任务书与 Task 风险二均如此规定）。

## 接收方式

- 分支/仓库：`main` @ `G:\CODEX\New Manga`（未新建 worktree）。
- 复现：`cd apps/desktop/frontend && npm test`（应 319 passed）；`npx tsc --noEmit`（应 exit 0）。
- Coordinator 测量入口：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -BuildFrontend -Mode both`（exe 重编译 `-BuildExe` 需先与 P20-CLOSE-BOUND-HARDEN-1 协调 src-tauri/target 占用）。
- 无依赖变化；无共享契约变化；默认构建行为与性能特征不变（钩子代码虽入 bundle，但关闭态零注册零分配——单测为证）。

## 下一任务建议（必填）

- Task ID / 标题：无新 Task；先由 Codex 对本交付做独立 Review，再由 Coordinator（dsh, epoch 8）执行 AC3 真实桌面测量。
- 推荐 Agent / Reviewer：Reviewer = Codex（本 Task 既定）；测量执行 = dsh（Coordinator）。
- 推荐原因与前置依赖：实现已冻结 head `011293151`；测量依赖 `-BuildExe`，须避开 P20-CLOSE-BOUND-HARDEN-1 对 `src-tauri/target` 的并行使用。
- Recovery point：仓库 `G:\CODEX\New Manga`，branch `main`，base `a04e4ea78`，delivery `011293151`；未创建新 worktree（复用主 worktree）。
- 允许修改路径：Review 返修限 `apps/desktop/frontend/src/perf/**`、`main.tsx`、`verification/P20-AC4-FPS-1/**`、本 Task 与本 Handoff。
- 禁止范围与新增授权条件：维持 Task 冻结范围（不碰 IPC/契约/`src-tauri/**`/用户 20 个 dirty 文件；不得默认开启钩子；不得改 `avg ≤ 50 ms` 口径）。
- 交付物：见上表。
- 验证命令、环境与完成 Gate：`npm test` 全绿 + Codex Review approved + Coordinator 产出 `run-*/fps-*-samples.csv` 与汇总（avg 判定、p95 如实）。
- 可直接转发给 Agent 的指令：见 Task `doc/tasks/P20-AC4-FPS-1.md` 与 `MEASUREMENT-GUIDE.md`（测量执行段）。

## 风险与遗留

- **治理检查（`tools/governance/check.ps1`）结果**：`FAIL (1 errors, 2 warnings)`。唯一 error 为 `READY DAG 只允许 status: ready；P20-AC4-FPS-1 当前为 in_review`——Task 已按协议转入 in_review，但 `doc/REBASELINE_PLAN.md` 的 READY 节点行（第 35 行）仍登记本 Task，需由 Codex 做指针同步；该文件属用户 20 个具名 dirty 文件，Owner 无权修改。两条 warning（STATUS/PLAN 预算 80%）为既有状态，与本交付无关。
- **AC3 未执行**：真实桌面测量依赖 Coordinator 重建 exe（Tauri 编译期嵌入 dist）；若 `-BuildExe` 与 HARDEN-1 冲突，等其集成后重跑即可，钩子交付不受影响。
- **vitest 环境事实**：vitest node 环境自带 `URL.createObjectURL` polyfill，测试对其做无条件覆盖+恢复（记录于测试注释），避免环境差异导致的假失败。
- **UIA 抓取大文本** 为 best-effort：失败时 trace 如实记 FAILED，人工经保存对话框/剪贴板补齐（GUIDE 已注明）。
- 回退方法：revert `011293151` 即完全移除钩子（无共享面变更，回退无级联）。
- p95 预期仍超 50ms（既有记录 77.5ms）：按用户裁决不阻断达标，如实登记；冷路径优化是否立项由 Coordinator 决定。
