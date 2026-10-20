# `P20` AC4 的可测性分析（只读）

**产出**: 2026-10-20 · **性质**: 只读调查 · **目的**: 判断 AC4 的剩余项能否在不改产品代码的前提下测得

## 一、AC4 现在缺什么

`doc/tasks/P20.md` 的 AC4：

> **交互响应与帧率**——按键/点击交互延迟 **≤ 50 ms**；单页/Webtoon 长图滚动
> **稳定 60 FPS**；缩放平移无可见撕裂。
>
> **（实测部分通过，保留未勾选：** 无障碍 `Invoke` → 后置条件可见的**端到端**延迟
> （含 UIA 开销，为上界）：**20/20 样本有效**，**avg = 36.0 ms ≤ 50 ms ✅**；
> 但 **p95 = max = 62.4 ms > 50 ms ⚠️**（非平凡开销主要来自首次切换）。
> **FPS 与「缩放平移无撕裂」未测**：需 WPR/GPUView 或前端 `performance` 埋点，
> 本 Task 无此测量手段，**如实标注 NOT_MEASURED**，不以静态推理代替。）

**三项子要求的状态：**

| 子项 | 状态 |
|---|---|
| 交互延迟 ≤ 50 ms | **avg 36.0 ms 通过；p95 = max = 62.4 ms 超过** |
| 滚动稳定 60 FPS | **NOT_MEASURED** |
| 缩放平移无撕裂 | **NOT_MEASURED** |

## 二、FPS 测量的可行路径（本轮实测）

### 2.1 前端**已经有**帧时间记录器

`apps/desktop/frontend/src/perf/fpsRecorder.ts`（425 行，`P20-AC4-FPS-1` 产出）：

> `// P20-AC4-FPS-1: opt-in requestAnimationFrame frame-time recorder.`

判据写在文件里，且是**用户 2026-10-18 裁决**的：

```ts
/** User-ruled AC4 frame-time criterion (2026-10-18): avg <= 50ms. */
export const FPS_AVG_THRESHOLD_MS = 50;
```

**三种启用开关**（文件头自述）：

1. build flag `VITE_M2_FPS_SAMPLING=1`（measurement build only）
2. query param `?m2_fps=1`
3. localStorage `m2rc1_fps_sampling=1`

### 2.2 但记录器**没有挂载到产品界面**

`FpsRecorderPanel.tsx` 存在，有完整的 `data-testid`（`fps-recorder-panel`、
`fps-panel-stats`、`fps-panel-verdict`）和导出通道。

**但全仓搜索「谁 import 它」的结果是：只在 `FpsRecorderPanel.test.tsx` 里。**
**没有任何产品页面挂载它。**

**Settings 页也搜不到 `m2_fps` / `fps_sampling` / `startFpsRecorder`。**

**所以：工具实现了，但没有入口。**

### 2.3 CDP 路径不可用（本轮实测）

想用 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9333`
给 WebView2 注入调试端口，再从外部用 CDP 驱动滚动 + 读 `requestAnimationFrame`。

**实测结果：`/json/version` 无响应，端口未监听。**

```
launching with WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9333 --remote-allow-origins=*
/json/version: (no response)
CDP endpoint NOT reachable on port 9333
VERDICT: CDP UNAVAILABLE on this build
```

**该 build 的 WebView2 未开放 devtools 端点**（`tauri.conf.json` 的 window 无
`devtools` 设置，生产构建默认关闭）。

### 2.4 其它工具

| 工具 | 可用性 |
|---|---|
| `wpr.exe`（Windows Performance Recorder） | **存在**（`C:\WINDOWS\system32\wpr.exe`）|
| `xperf.exe` / `gpuview.exe` | **不存在** |
| `PresentMon.exe` | **不存在** |

**WPR 可采 ETW trace，但没有 GPUView 时分析 DWM 呈现时序极其繁琐**，
且需要 `wpr -start` 特定 profile 与后续 trace 解析。**这不是一次只读调查能完成的。**

## 三、撕裂测量

撕裂是**帧级呈现问题**，没有任何 OS API 直接报告它。

**可行手段只有**：
- 帧精确录屏 + 逐帧比对（需要高速录制设备或 DWM 层面的帧捕获）；
- 或人眼观察（**这正是「NOT_MEASURED」而非「FAIL」的原因**）。

**在没有改产品代码、没有专用采集设备的前提下，此项无法自动化测量。**

## 四、结论

| 子项 | 能否在不改产品代码的前提下测 | 结论 |
|---|---|---|
| 交互延迟 | **能**（已有 UIA 脚本，已测 20/20）| 已测，p95 超标 |
| **滚动 FPS** | **不能**——记录器无 UI 入口，CDP 不可用 | 需产品改动（暴露入口）或 measurement build |
| **缩放平移撕裂** | **不能**——无 OS API，需帧捕获或人眼 | 需专用设备或人工观察 |

## 五、因此 AC4 的处境

**AC4 不是「治理债」，是产品验收缺口**，且缺口分两类：

1. **p95 = 62.4 ms > 50 ms**：这是**实测超标**，不是没测。
   注释说「非平凡开销主要来自首次切换」——**首帧慢**。
2. **FPS / 撕裂未测**：缺的是**测量手段**，不是实现。

**两者都不是只读调查能解决的**：
- 前者要么优化（产品代码），要么由用户裁决 p95 是否计入（判据裁决）；
- 后者需要把 `FpsRecorderPanel` 暴露到产品界面（产品改动），或接受人工观察。

## 六、建议

1. **p95 的判据问题应由用户或 Codex 裁决**：AC4 写的是「交互延迟 ≤ 50 ms」，
   而实测 avg 36.0 通过、p95 62.4 不通过。**「≤50 ms」指的是哪个统计量，
   AC 没写清。** 这与 `P20-ISOLATION-1` 的 AC4 内存问题**是同一类缺陷**——
   **一条 AC 里混写了未定义优先级的多个判据**。
2. **FPS 要能测，必须给 `FpsRecorderPanel` 一个入口**（Settings 页或隐藏手势），
   那是一个**小的产品 Task**。
3. **撕裂建议明确降级为「人工观察」并写入 limitation**，而不是长期挂着 NOT_MEASURED。

## 七、明确未做

- **未修改任何产品代码。**
- 未修改 `P20` 的 AC4 勾选状态。
- 未修改 `fpsRecorder.ts` / `FpsRecorderPanel.tsx`。
- 未运行 WPR trace（成本与解析复杂度超出本轮范围）。

## 八、产物

本轮探测过程无持久产物（CDP 探测脚本在临时目录）。
**本文件是唯一入库结果。**
