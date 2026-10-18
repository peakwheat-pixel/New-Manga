# P20-AC4-FPS-1 真实桌面测量步骤说明（Coordinator 执行）

Owner（ZCode）只交付钩子、单元测试与本脚本；**真实桌面的窗口级测量由 Coordinator 在交互式桌面执行**（本机 CDP 端口被阻断，Owner 无 headless 窗口操作通道——P20 既有探测记录）。

## 交付物与开关口径（Owner 冻结）

- 钩子本体：`apps/desktop/frontend/src/perf/fpsRecorder.ts`（默认关闭；关闭态不注册 rAF、不分配采样数组）
- 导出面板：`apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx`（仅采样开启时挂载；默认页面 DOM 完全不含它）
- 接线：`apps/desktop/frontend/src/main.tsx`（默认路径只做一次开关求值）
- 单元测试：`src/perf/fpsRecorder.test.ts`（15 用例）、`src/perf/FpsRecorderPanel.test.tsx`（7 用例）

**开启方式（三通道任一显式开启，默认全关）：**

| 通道 | 形式 | 适用场景 |
|---|---|---|
| 构建期开关 | `VITE_M2_FPS_SAMPLING=1 npm run build` | 测量构建（主通道；嵌入 exe） |
| 查询参数 | `?m2_fps=1` | dev server / 浏览器直跑 |
| localStorage | `m2rc1_fps_sampling=1` | 运行期经 devtools 设置后 reload |

## 测量流程（run-ac4-fps.ps1）

1. **构建测量前端**（脚本开关 `-BuildFrontend`）：
   ```powershell
   pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -BuildFrontend ...
   ```
   脚本会以 `VITE_M2_FPS_SAMPLING=1` 执行 `npm run build` 产出带钩子的 `dist`。
2. **重编译 debug exe**（脚本开关 `-BuildExe`；⚠️ `src-tauri` 属 P20-CLOSE-BOUND-HARDEN-1 范围，执行前先与该 Task 协调，避免并行构建冲突）：Tauri v2 在**编译期**嵌入 `frontendDist`，磁盘上的新 dist 必须重编译 exe 才生效。
3. **执行测量**：
   ```powershell
   pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -Mode both -ScrollSeconds 20 -ScrollMode wheel
   ```
   脚本自动完成：`%TEMP%` 隔离根（绝不写 `%APPDATA%\com.newmanga.m2rc1.desktop`）→ 启动 exe → 校验 FPS 面板已挂载（未挂载即 `SAMPLING_NOT_ENABLED` fail-fast）→ 每轮 `Reset & Start` → 滚动注入（mouse wheel / PageDown）→ `Stop` → 读窗口标题摘要 → `Show CSV/JSON` + UIA ValuePattern 抓全文落盘 → **独立复算** avg/p95/max（nearest-rank，与前端同法）→ 收尾杀 `m2rc1-desktop` / `core_service` / `host_bridge`。
4. **人工步骤（脚本会暂停提示）**：在隔离根内经书架导入对话框导入单页样例与 Webtoon 长图样例，并把阅读器打开到目标页/模式。
5. **判读**：
   - 达标口径（用户 2026-10-18 裁决）：`avg ≤ 50 ms` PASS；
   - `p95`、`max` **如实记录**，超限不阻断、不得以任何方式消解（冷路径优化另立 Task，由 Coordinator 决定是否立项）；
   - 撕裂：`NOT_VERIFIED_BY_RULING`（只记 limitation，不做客观验证，不得写 PASS）。
6. **收尾**：测完恢复默认前端（在 `apps/desktop/frontend` 下不带 `VITE_M2_FPS_SAMPLING` 重新 `npm run build`，或按集成方惯例处理 dist）。

## 产物布局

| 文件 | 内容 |
|---|---|
| `fps-<mode>-samples.csv` | 样本级逐帧数据（`seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason`；**排除样本保留在 CSV 中**，带 `excluded=1` 与理由） |
| `fps-<mode>-summary.json` | 前端汇总（kept 统计 + excluded 计数/理由 + p95 方法 + 阈值判定） |
| `fps-<mode>-title.txt` | Stop 时刻窗口标题一行摘要（UIA 通道） |
| `fps-trace.log` | 执行轨迹 + 独立复算结果 + PASS/FAIL 断言 |
| `fps-metadata.txt` | runner、exe sha256、参数、口径与 limitation 声明 |

## 已知限制（如实登记）

- 排除规则只有两类且逐样本留痕：`raf_gap_ge_1000ms`（页面隐藏/系统休眠期间 rAF 暂停，非渲染掉帧）、`non_positive_delta`（同时间戳防御）。**无任何其他剔除**；kept/excluded 双口径并列报告。
- UIA `ValuePattern` 抓取大段 CSV 文本如失败，用面板 `FPS: Export CSV` 保存对话框（调用方选 OutDir）或 `Copy CSV` 剪贴板通道，脚本 trace 会如实记录 FAILED。
- 面板在采样运行中不做定时自动刷新（避免周期性 re-render 污染帧时间）；计数靠 `FPS: Refresh` 手动刷新。
