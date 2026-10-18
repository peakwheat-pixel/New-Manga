# P20-AC4-FPS-1 真实桌面测量步骤说明（Coordinator 执行）

Owner（ZCode）只交付钩子、单元测试与本脚本；**真实桌面的窗口级测量由 Coordinator 在交互式桌面执行**（本机 CDP 端口被阻断，Owner 无 headless 窗口操作通道——P20 既有探测记录）。

## 交付物与开关口径（Owner 冻结）

- 钩子本体：`apps/desktop/frontend/src/perf/fpsRecorder.ts`（默认关闭；关闭态不注册 rAF、不分配采样数组、不注册任何监听）
- 导出面板：`apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx`（仅采样开启时挂载；默认页面 DOM 完全不含它）
- 接线：`apps/desktop/frontend/src/main.tsx`（默认路径只做一次开关求值）
- 单元测试：`src/perf/fpsRecorder.test.ts`、`src/perf/FpsRecorderPanel.test.tsx`

**开启方式（三通道任一显式开启，默认全关）：**

| 通道 | 形式 | 适用场景 |
|---|---|---|
| 构建期开关 | `VITE_M2_FPS_SAMPLING=1 npm run build` | 测量构建（主通道；嵌入 exe） |
| 查询参数 | `?m2_fps=1` | dev server / 浏览器直跑 |
| localStorage | `m2rc1_fps_sampling=1` | 运行期经 devtools 设置后 reload |

## 排除与报告口径（FPS-R1-05 修订）

- 排除仍只有两类且逐样本留痕（CSV 保留全部行，`excluded=1` + `exclude_reason`）：
  - `raf_gap_ge_1000ms_while_hidden`：帧间隔 ≥ 1000 ms **且采样确认该区间与页面隐藏（visibilitychange hidden）区间相交**才排除；
  - `non_positive_delta`：同时间戳防御。
- **页面可见时的前台主线程停顿（≥1 s 尖峰）不再被排除**，直接参与 kept 统计（avg/max/p95）；无可见性跟踪能力时同样保守保留。
- 汇总恒报双口径：kept 的 `avg/min/max/p95`（nearest-rank p95）**加** `allMaxMs`（全样本最大间隔，含被排除行）与 `excludedMaxMs`（被排除样本最大间隔）；窗口标题摘要含 `allmax=`。任何被观测到的停顿都无法隐身于 PASS 之后。
- 达标判定（用户 2026-10-18 裁决，不可改）：`avg ≤ 50 ms`；p95/max 如实记录，超限不阻断也不得消解。

## 导出行为（FPS-R1-04 修订）

- `FPS: Export CSV / Export JSON` 走 **`window.showSaveFilePicker()` 显式 Save As**：目标位置由调用方在对话框中选择；**取消即不写任何位置**（无默认下载目录回退；旧的 Blob+anchor.download 静默下载路径已删除）。
- 无 save-picker API 的环境按提示改用 `Show CSV/JSON`（textarea + UIA/复制通道）；代码全程不接触绝对路径。
- UIA `ValuePattern` 抓取失败时该轮即失败（runner 非零退出），人工经面板显式保存对话框补齐后重跑。

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
   脚本自动完成：`%TEMP%` 隔离根 → **四路径 fail-closed 钉死**（见下）→ 真实 AppData 基线快照 → 启动 exe → 校验 FPS 面板已挂载（未挂载即 `SAMPLING_NOT_ENABLED` fail-fast）→ 每轮 `Reset & Start` → 滚动注入（mouse wheel / PageDown）→ `Stop` → 读窗口标题摘要 → `Show CSV/JSON` + UIA ValuePattern 抓全文落盘 → **独立复算** avg/p95/max/all_max/excluded_max（nearest-rank，与前端同法）→ `finally` 统一收尾（只清本轮进程树 + AppData 终末快照比对）。
4. **人工步骤（脚本会暂停提示）**：在隔离根内经书架导入对话框导入单页样例与 Webtoon 长图样例，并把阅读器打开到目标页/模式。
5. **判读**：
   - 达标口径（用户 2026-10-18 裁决）：`avg ≤ 50 ms` PASS；
   - `p95`、`max`、`all_max`、`excluded_max` **如实记录**，超限不阻断、不得以任何方式消解（冷路径优化另立 Task，由 Coordinator 决定是否立项）；
   - 撕裂：`NOT_VERIFIED_BY_RULING`（只记 limitation，不做客观验证，不得写 PASS）。
6. **收尾**：测完恢复默认前端（在 `apps/desktop/frontend` 下不带 `VITE_M2_FPS_SAMPLING` 重新 `npm run build`，或按集成方惯例处理 dist）。

## 隔离与进程安全（FPS-R1-01/02 修订）

- **数据根 fail-closed**：启动 exe 前把 `NEWMANGA_DATA_ROOT`、`M2RC1_DERIVED_ROOT`、`M2RC1_MANAGED_ROOT`、`M2RC2_CATALOG_DB` 全部钉到新建 `%TEMP%` 隔离根并读回校验；**任一缺失或指向隔离根之外即拒绝启动（exit 7）**，绝不落入 `%APPDATA%\com.newmanga.m2rc1.desktop` 回退（见 main.rs packaged_user_root 链）。
- **dev 模式**：传 `-DevSrcRoot <repo src dir>` 显式设置并核对 `M2RC1_SRC_ROOT`；不传时要求 exe 旁存在 packaged sidecar（`resources\core-sidecar\host_bridge.exe`），否则拒绝启动（app 自身会 panic）。
- **AppData 实证**：启动前对真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 做逐文件 sha256 清单（`appdata-baseline.txt`），收尾后再拍 `appdata-after.txt` 比对；**任何新增/修改/删除都判 FAIL（exit 6）**。
- **进程所有权**：只记录并清理**本轮启动的** app PID 及其后代（Win32_Process PPID 链，启动后与每轮 capture 前刷新），结束前再按进程名家族白名单复核（防 PID 复用）；已存在的同名进程登记为 `NOT_OURS` 且绝不触碰。清理在 `try/finally` 中统一执行，覆盖正常、失败、人工中止路径；收尾复查全退，残留即 FAIL。
- **退出码**：`0`＝所有请求 phase 完整（CSV+JSON 齐）且全部 `avg ≤ 50 ms` 且 AppData 无变化且本轮进程全退；`2`＝无 exe/无窗口；`3`＝SAMPLING_NOT_ENABLED；`4`＝OutDir 已存在拒绝覆盖；`5`＝构建失败；`6`＝测量/断言/artifact/隔离/进程清理任一失败；`7`＝隔离环境 fail-closed 拒绝。

### Owner 侧已执行的实测（非测量，不替代 AC3）

| 命令 | 结果 | 证据 |
|---|---|---|
| `pwsh -NoProfile -File run-ac4-fps.ps1 -SafetySelfCheck` | PASS（6 项：四路径接受/缺一拒绝/越界拒绝/快照阴性对照/阳性对照/真实 AppData 只读基线），exit 0 | `selfcheck-20261018-173828/`（首次运行 `…173814` 曾 FAIL 并抓出前缀判定缺陷，修复后复测通过——自检机制有效性实证，保留为证据） |
| `pwsh -NoProfile -File run-ac4-fps.ps1 -SmokeTest` | PASS：启动 exe 12 s（窗口正常、11 个后代 PID）→ 只清本轮进程全退 → 真实 AppData 24 文件 sha256 前后 **UNCHANGED** → 写入全部落在隔离根（`catalog/catalog.sqlite`、`library.db`、`derived/.preview-lifecycle.lock`、`managed/temp`），exit 0 | `smoke-20261018-173917/`（`…173840` 为同代码首次冒烟，亦 PASS） |

`-SmokeTest` 不做任何采样/滚动/UIA 交互；真实桌面测量（AC3）仍由 Coordinator 执行。

## 产物布局

| 文件 | 内容 |
|---|---|
| `fps-<mode>-samples.csv` | 样本级逐帧数据（`seq,frame_ts_ms,frame_time_ms,instant_fps,excluded,exclude_reason`；**排除样本保留在 CSV 中**，带 `excluded=1` 与理由） |
| `fps-<mode>-summary.json` | 前端汇总（kept 统计 + allMaxMs/excludedMaxMs + excluded 计数/理由 + p95 方法 + 阈值判定） |
| `fps-<mode>-title.txt` | Stop 时刻窗口标题一行摘要（UIA 通道） |
| `fps-trace.log` | 执行轨迹 + 独立复算结果（含 all_max/excluded_max）+ PASS/FAIL 断言 + 进程所有权记录 |
| `fps-metadata.txt` | runner、exe sha256、参数、隔离根、our_pids、口径与 limitation 声明 |
| `appdata-baseline.txt` / `appdata-after.txt` | 真实 AppData 前后逐文件 sha256 清单（隔离证明） |
| `app-out.log` / `app-err.log` | 本轮 app 的 stdout/stderr |

## 已知限制（如实登记）

- 排除规则两类且逐样本留痕（见上节）；kept/excluded/all-sample 三口径并列报告，尖峰不可隐身。
- 面板在采样运行中不做定时自动刷新（避免周期性 re-render 污染帧时间）；计数靠 `FPS: Refresh` 手动刷新。
- UIA `ValuePattern` 抓取大段 CSV 文本失败时，该轮直接判 FAIL（非零退出）；人工经显式保存对话框补齐后重跑，trace 如实记录。
- `showSaveFilePicker` 依赖 WebView2 的 File System Access API（secure context）；不可用时面板明示并引导 Show/Copy 通道，不落任何默认位置。
