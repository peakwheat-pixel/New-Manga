# DISPLAY-PERF-DECISION-1 真机基线报告（AC1 / AC2 / AC3）

- 任务：父任务 `DISPLAY-PERF-DECISION-1` 的子任务 **task-3**（真机基线测量）
- 执行者：teammate `baseline-scout`（DSH Lead 派出）
- 测量时间：2026-10-26 20:16–20:56（Asia/Shanghai）
- 测量机：Windows，显示器 2560×1440，应用窗口 1180×860，系统缩放下窗口 `devicePixelRatio=1`
- **纪律声明**：本任务只写 `verification/DISPLAY-PERF-DECISION-1/baseline/**` 与
  `G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/**`。**未修改任何产品源码/配置/依赖**
  （`git status` 中 `apps/**`、`Cargo.toml`、前端源码零改动；唯一的产品侧写入是
  `cargo tauri build` 重写了 gitignored 的 `target/release/`，见 §2.3）。

---

## 0. 一句话结论

**「Core 和软件不是一起启动」这句用户感知是真实的、但方向要纠正：产品是严格「先 Core、后窗口」串行启动——
本机 Core 就绪中位 513 ms、窗口可见中位 558 ms（窗口只在 Core 就绪后 45 ms 出现），最坏情况代码上可达 30 s；
真正的显示问题是「页面被缩到 39.3% 渲染 + 完全没有缩放/长条滚动能力」，真正的效率问题是
「每个图片请求都重读整文件并算 SHA-256（本机 0.6 MB 页约 3.6–4.7 ms/次，比硬件 SHA 慢约 11–13 倍）」，
而不是「渲染掉了帧」——rAF 实测稳定 59.95 fps。**

---

## 1. 被测件（必须随数字一起引用）

| 件 | 路径 | SHA-256 | 说明 |
|---|---|---|---|
| **基线 release exe**（AC1 数字来自它） | `apps/desktop/src-tauri/target/release/new-manga.exe`（原件已按 Lead 指示另存副本） | `1136BB0A8D582A30C6EF0B16959B86A62DD26D2C6D9CE49E298C9B86C3343226` | 2026-10-26 19:32，12,062,720 B |
| 基线副本（防污染，勿修改） | `…/task-envs/DISPLAY-PERF-DECISION-1/pinned-baseline/`（含 `resources/core-sidecar/`） | 同上；`core_service.exe` = `E0A1EFF8D9EE7558EAE903F83AF3870ADA94AFC2D083F82E2CC0B571F6F14BC0` | `PINNED-BASELINE.json` 记录抓取时间 |
| **CDP 验收构建**（AC2/AC3 数字来自它） | 同一路径 `target/release/new-manga.exe`（构建产物，已覆盖基线件） | 见 `build-acceptance-9361.log` | 见 §2.3 |

### 1.1 关键基础设施事实：冻结 release exe 无法开 WebView2 CDP

- 实测 `msedgewebview2.exe` 命令行（证据 `diag/diag-cdp-02/diag-report.json`）只有 wry 默认注入的
  `--disable-features=msWebOOUI,msPdfOOUI,msSmartScreenProtection`，**没有** `--remote-debugging-port`。
- 原因（微软 WebView2 契约 + 实测一致）：环境里显式设置 `AdditionalBrowserArguments` 后，
  `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` 环境变量被**忽略**；当代 Tauri/wry 总会设置该字段，
  所以 uiux-v2 那套「env 变量注入 CDP」在本产品版本上已失效。
- 结论：**AC1 只能用黑盒（Win32 探针 + 日志时间戳）测**；页内 JS 观测（AC2/AC3）必须用带
  `additionalBrowserArgs` 的构建。

### 1.2 隔离环境（每次启动都断言）

`APPDATA / LOCALAPPDATA / TEMP / TMP / NEWMANGA_DATA_ROOT / M2RC1_DERIVED_ROOT /
M2RC1_MANAGED_ROOT / M2RC2_CATALOG_DB / WEBVIEW2_USER_DATA_FOLDER` 全部指向
`…/task-envs/DISPLAY-PERF-DECISION-1/runs/<label>/` 下独立目录，`M2RC1_PACKAGED=1`，
启动前断言目标目录为空/不存在（`harness/env.mjs:assertLaunchTargetsClean`）。**从未触碰用户真实
`%APPDATA%` 或媒体库。** 环境清单逐次写进证据（`ac1-*/ac1-run.json` 的 `env` 字段）。

---

## 2. AC1 启动时间线与 Core/UI 启动耦合

### 2.1 方法（无 CDP 的黑盒时间线）

| 观测点 | 手段 | 证据文件 |
|---|---|---|
| process start | `Process.StartTime`（OS 权威值，不是启动器时钟） | `ac1-*/native-probe.jsonl` |
| Core sidecar spawn | `core_service.exe` 首次出现且 `ParentProcessId == new-manga pid` | 同上 |
| Core ready | Core 侧继承 stderr 上 `[core.derived_gc]`（`core_service.py:4599-4642`：GC 在 `serve_forever()`/`core.ping` **之前**） | `ac1-*/ac1-run.json:timeline.coreDerivedGcLog` |
| setup() 到达 | 自身 stderr `[m2rc2-allowlist] production:…`（`main.rs:1849`，`tauri::Builder` 构造期） | `ac1-*/ac1-run.json:timeline.coreReadyPingLog` |
| window visible | `GetProcess.MainWindowHandle != 0` + `GetWindowThreadProcessId` 归属校验 | `ac1-*/native-probe.jsonl` |
| WebView2 首进程 | `msedgewebview2.exe` 中启动时间 ≥ 本次 t0 的进程 | 同上 |

探针在 app 启动**之前**就已就绪（`waitForJsonlKind(probe_ready)`），因此 3–5 ms 轮询分辨率在 t0 即生效
（早期一版未同步，最早两个事件被首轮轮询"归并"，已作废，见 `ac1/_pilot/`）。

### 2.2 实测（3 次独立冷启动，单位 ms，起点 = exe 进程创建）

| 阶段 | 中位 | 最小 | 最大 | 3 次原始值 |
|---|---|---|---|---|
| Core sidecar spawn | **40** | 35 | 44 | 35 / 40 / 44 |
| Core ready（`[core.derived_gc]`） | **513** | 489 | 517 | 489 / 513 / 517 |
| setup() 到达（allowlist） | **554** | 531 | 554 | 531 / 554 / 554 |
| **窗口可见** | **558** | 540 | 582 | 540 / 558 / 582 |
| 首次 `[m2rc1-title]` 心跳（setup 线程 +2 s 后） | 2944 | 2943 | 2992 | 2943 / 2944 / 2992 |

原始数据：`ac1/ac1-summary.json` + `ac1/ac1-summary.md`；每轮 `ac1-run.json`、`native-probe.jsonl`、
`app.stderr.ts.log`（每一行带 epoch ms）。

### 2.3 结论：Core 与 UI 到底怎么启动的？

1. **不是「Core 和 UI 各自起、抢跑」，而是硬串行。** `main.rs:1649-1706` 在 `tauri::Builder`（`main.rs:1734`）
   **之前**同步 `spawn_with_startup_ping(..., 30 s)`，并且 `channel = StdioCoreChannel::spawn_packaged(...)`
   （`main.rs:1691-1706`）用 `.expect()` 硬失败。窗口在 Builder 之后才由配置创建，所以
   **窗口可见必然晚于 Core ready**——实测差值 27–69 ms（中位 45 ms），与代码一致。
2. **卡点在「Core 冷启动 + startup ping」这一段**：本机 513 ms（Core spawn 40 ms → ping 返回 ≈ 473 ms）。
   这段期间**没有任何窗口**（用户感知为"点了图标没反应"），随后窗口一次性出现。
3. **最坏等待 30 s**：ping 超时是 `Duration::from_secs(30)`（`main.rs:1667`）。超时后不重试阻塞，
   而是交给 `ResilientLibraryChannel` 的 supervisor 后台重试（`main.rs:1674-1687`），此时 UI 已出现但
   Core 侧功能不可用（diagnostic run 里真实观测到 3/3 失败 + `[supervisor] Restarting core_service`）。
4. 本机冷启动整体是可用的（≈0.56 s 出窗口），所以**用户"不是一起启动"的抱怨更可能来自 Core 崩溃/重启
   窗口期的 UI 空转**，以及下一节的显示问题，而不是 0.5 s 的固定串行等待。

### 2.4 AC1 未测项（如实标注）

| 项 | 状态 | 原因 |
|---|---|---|
| 首帧/首内容像素级时刻（paint） | **NOT_RUN（精确值）** | 冻结 exe 无 CDP，只能靠外部像素探针；`paint-probe.ps1` 的 C# 采样器因 `Add-Type` 缺 `System.Drawing.Primitives` 引用编译失败（`logs/paint-probe.stderr.log`），3 次正式运行 `paintFrames=0`。 |
| （参考）首内容时刻的**早期试跑**证据 | PROXY / 非正式 | 早期慢速 `GetPixel` 版探针（约 1.1 s/帧）在 `ac1/_pilot/ac1-02` 记录：+891 ms 为纯白空窗（meanL=255, edge=0），+2458 ms 已是深色带文字内容（meanL=38.8, edge=5.17）→ **空窗口期 ≥1.5 s**。仅作方向性参考，正式表不引用。 |
| 书架数据到达 | **NOT_RUN** | 需要页内 DOM 观测；AC1 走黑盒。CDP 构建上可用（见 AC3 的会话），但 AC1 数字按 Lead 要求锚定基线件，两者不可混用。 |

---

## 3. AC2 图片通道成本分解（真实页，实测）

### 3.1 方法（同路径重放 + 关键隔离技巧）

被测件为 §1 的 CDP 验收构建（与基线件**仅 browser args 不同**），真实导入 30 张
`test_assets/comic_golden_suite/日漫_JA/**` 的 jpg（经产品自带原生选择器 `library_import_file` 真正导入，
报告页显示「已导入 1 + 29」、Core `list_chapter_pages` 返回 30 页）。

在页内用**与产品相同的命令与协议**逐段计时（`harness/measure.mjs:AC2_JS`）：

```
resolve_page_resource → issue_resource_url → fetch(url?chunk=0) → new Blob → <img>.decode()
```

**Hash 隔离技巧（本报告的关键方法）**：`resource_protocol.rs:541-587` 中，
`chunk_offset` 先被校验（越界 → `REF_MALFORMED 400`），**之后**才进 `verify_and_serve()`
（整文件顺序读 + SHA-256，`resource_protocol.rs:509-527`）。因此
`fetch(url?chunk=1)`（单 chunk 文件的越界请求，实测恒为 HTTP 400）**只付 Core resolve 的钱、不付哈希的钱**，
于是：`全文件 SHA-256 + serve ≈ chunkMs − rejectedChunkMs`。

### 3.2 单页分解（3 张不同大小的真实页 × 4 次，中位）

| 阶段 | page_001 (657 KB) | page_016 (598 KB) | page_030 (602 KB) | 占端到端(page_001) |
|---|---|---|---|---|
| ① Core resolve（`resolve_page_resource`） | 3.40 | 3.15 | 3.20 | 14.9 % |
| ② 授权签发（`issue_resource_url`） | 3.20 | 2.90 | 3.00 | 14.0 % |
| ③ 协议取块 `fetch(?chunk=0)`（= Core resolve + **整文件 SHA-256** + 读出） | 6.00 | 4.85 | 4.75 | 26.3 % |
| ③a 其中**整文件 SHA-256 估计**（③ − 越界控制） | **4.65** | 3.80 | 3.55 | 20.4 % |
| ③b 越界控制 `fetch(?chunk=1)`（仅 resolve，HTTP 400） | 1.25 | 1.10 | 1.15 | — |
| ④ Blob 组装 + `createObjectURL` | 0.50 | 0.45 | 0.35 | 2.2 % |
| ⑤ 解码首帧（`img.decode()`） | **9.75** | 9.25 | 9.70 | 42.7 % |
| **端到端（①→⑤）** | **≈22.9** | ≈20.6 | ≈21.0 | 100 % |
| 不含解码（①→④） | 12.90 | 11.40 | 11.05 | — |
| 独立参照：同一份字节的 **WebCrypto SHA-256** | **0.35** | 0.35 | 0.30 | — |
| 字节斜率（3 点回归） | 21.8 ms/MB | — | — | 隐含全文件扫描 ≈45.9 MB/s |

原始：`ac2/ac2-stages.json`（每页 4 次完整原始值；`resolveMs/issueMs/chunkMs/rejectedChunkMs/
hostHashMsEstimate/blobMs/decodeMs/webCryptoShaMs/pipelineNoDecodeMs` 全量 min/median/max/p95）。

### 3.3 结论

1. **真正的「底层效率」热点是每请求整文件 SHA-256**：0.6 MB 页 ≈ 3.6–4.7 ms，
   占端到端 20 %、占「不含解码」管线 33–36 %。这是 `resource_protocol.rs:509-527` 的设计
   （F-02 修复的代价：每次请求都重算摘要以拒绝等长重写）。**每翻一页就多读一遍整文件**。
2. **同一份字节，WebCrypto 只用 0.30–0.35 ms，Host 侧 3.55–4.65 ms → 慢 11–13 倍。**
   WebCrypto 走 CPU 硬件 SHA-NI；Host 侧 `sha2` crate 在 `Cargo.toml:25-29` 的
   **`opt-level = 1`** 下无法有效内联/向量化。这就是「opt-level 对照」在产品内的**实测代理证据**：
   同一台机器、同一份字节、同一种算法，只差实现路径就 11–13 倍。
   （标注：这是**产品内代理对照**，不是同一份 Rust 代码在 opt-level 1/3 两次构建的对照；
   独立最小工程对照见 §3.4，状态 NOT_RUN。）
3. 解码首帧 9.25–9.75 ms 是最大单项（42.7 %），但这是 WebView2/Chromium 的解码成本，
   与 `opt-level` 无关；要优化只能改通道（如原始 `<img src=协议URL>` 直连、或预解码/预取）。
4. 每页固定 IPC 开销不小：resolve 3.2 ms + issue 3.0 ms ≈ 6.2 ms/页，**与页大小无关**，
   翻页时纯协议往返就吃掉约 27 % 端到端。

### 3.4 AC2 未测项

| 项 | 状态 | 原因 |
|---|---|---|
| 同一 Rust 代码 `opt-level=1` vs `3` 的 A/B 构建对照 | **NOT_RUN** | 需完整重建两套 release（`--config` 只能改配置，改 opt-level 必须动 `Cargo.toml`，本任务禁止）。已用 §3.3 的产品内代理（Host SHA vs WebCrypto SHA）替代，并明确标注为代理。最小 `sha2` 工程对照因 21:05 收口时限未启动。 |
| chunk >1 的分块路径 | NOT_RUN | 测试页均 < 16 MiB，恒为单 chunk；分块只在超大图/PDF 上出现。 |
| 冷缓存 vs 热缓存（文件系统页缓存） | NOT_RUN | 4 次连测均为热缓存；首次冷读成本未单独隔离。 |

---

## 4. AC3 阅读器基线（DPR2、渲染宽度、缩放、FPS、翻页）

### 4.1 实际渲染宽度与「显示效果」

真实页 `page_001.jpg` 源分辨率 **1200×1660**，在 1180×860 窗口、阅读区 **1180×812** 内的实测：

| 项 | DPR=1（真实窗口） | DPR=2（CDP 仿真 1180×860@2x） |
|---|---|---|
| `devicePixelRatio` | 1 | 2 |
| 阅读区（CSS px） | 1180 × 812 | 1180 × 812 |
| 页图 CSS 渲染尺寸 | **471.31 × 651.97** | 471.31 × 651.97（不变） |
| 相对源图线性缩放（CSS） | **0.3928（39.3 %）** | 0.3928 |
| 相对源图线性缩放（物理像素） | 0.3928 | **0.7855（78.6 %）** |
| 页图可用横向空间利用率 | 471.31 / 1180 = **39.9 %** | 39.9 % |
| 布局 | 右 → 左（RTL），1/30 页 | 同 |

结论：**同一页在 1180 px 宽的窗口里只占 471 px 宽、只用掉 39.9 % 的横向空间，
相当于把 1200×1660 的原图压到 39 % 渲染。**（`<img>` 规则 `max-width:100%; max-height:100%;
object-fit:contain`，`pages/reader-settings.css:18-25`，被高度约束压到 39 %。）
在 DPR=2 屏幕上同一像素密度问题仍存在（78.6 % 物理缩放，但 CSS 布局仍是 471 px），
**用户看到的是「画面小、留白大、细节丢」**，与「显示效果不行」的主诉吻合。

### 4.2 缩放能力：**不存在**（0 个缩放控件、无手势、无快捷键）

- DOM 全量扫描 `button/[role=button]/input/select` → 匹配 `zoom|缩放|放大|缩小|fit|适应|宽度|scale`
  的控件：**0 个**（`ac3-measurements.json:steps[0].value.zoomControls = []`，DPR1/DPR2 都是 0）。
- 可滚动容器扫描：**0 个**（`scrollables = []`）；`document` 本身也不可滚（`scrollHeight == clientHeight == 860`）；
  页图父容器 `overflowY = visible`、`scrollHeight == clientHeight == 812`。
- 源码佐证：`pages/Reader.tsx` 的运行时阅读器只有 `reader-prev / reader-next / reader-chapter-select /
  reader-open-settings`，**没有任何缩放/适应模式控件**；`reader/WebtoonReaderView.tsx`（有 scroll 语义）
  **没有被 `UiRoot` 挂载**（`ui/UiRoot.tsx:9-12` 只 import `pages/Reader`）。
- **纵向条漫（长条滚动）在本版本根本没有接线**：`pages/Reader.tsx:673-681` 对
  `layout === "webtoon_vertical"` 直接渲染 `PageBlocked`，错误码
  **`READER_LAYOUT_WEBTOON_NOT_WIRED`**（「纵向条漫布局尚未接线」）。
  且产品 IPC 无法创建 webtoon 章节：`create_chapter` 只接受 `book_id/title/chapter_number`
  （`main.rs:580-596`、`core_service.py:1329-1334`），`chapter_type` 永远取 `book.default_chapter_type`（=PAGED）。

### 4.3 翻页首帧耗时（10 次，DPR=2）

用真实按钮元素触发产品自己的 handler（`reader-prev` 在 RTL 下即「下一页」），页内记录：
点击 → 新 `src` 出现（React 提交）→ `img.decode()` 完成 → 双 rAF（已上屏）。

| 阶段 | 中位 | min | max |
|---|---|---|---|
| 点击 → 新图 `src` 出现（含 fetch/Blob 管线，见 AC2） | **19.25** | — | — |
| 点击 → 首帧解码完成（`img.decode()`） | **27.20** | — | — |
| 点击 → 双 rAF 后确认上屏（painted） | **49.60** | — | — |

10 次全部成功（`n=10`，无 blocked）；原始每次的 `marks/deltas/after` 在
`ac3/ac3-measurements.json:steps[2]`。

### 4.4 内置 rAF 帧时间采样（≥10 s，原始 CSV 已导出）

按 Lead 要求**用 CDP `Runtime.evaluate` 注入独立 rAF 采样器**（不用内置 FPS 面板：其开关依赖
`?m2_fps=1` / `localStorage`，页面 URL 固定、无 query，`Page.reload` 会断 IPC），采样期间不 reload。

| 场景 | 时长 | 样本 | avg fps | p95 fps | 说明 |
|---|---|---|---|---|---|
| 连续翻页流（自动翻页 201 次） | 1.19 s | 71 | **59.95** | 59.52 | 采样窗被 `n>200` 早停，非 10 s |
| 「滚动」尝试（wheel + scrollBy 循环 5 s） | 5.0 s | 300 | **59.95** | 59.52 | 页面**根本不可滚**，见 4.2；这是空转帧率 |
| 空闲 | 3.0 s | 179 | **59.95** | 59.52 | 基线 |

原始 CSV：`ac3/fps-page-turns.csv`、`ac3/fps-scroll-attempt.csv`、`ac3/fps-idle.csv`；
汇总/limit 同 `ac3/ac3-measurements.json`。

**如实解读**：所有场景都稳定在 ≈60 fps（59.95），**没有掉帧证据**。但这**不能**用来反驳
「运行效率不行」，因为：
- 产品**没有长条滚动阅读模式**（4.2），所以「长条滚动 FPS」这一项在本版本**不存在**，
  上面的滚动采样只是「对不可滚容器发 wheel 事件」的空转，**不是**卷轴性能；
- 翻页流实际耗时全在 AC2 的管线（≈23 ms/页）与 AC3 的 ≈50 ms 首帧上，是**吞吐/延迟问题，不是帧率问题**。

### 4.5 AC3 未测项

| 项 | 状态 | 原因 |
|---|---|---|
| 长条滚动（纵向条漫）FPS | **BLOCKED（产品未接线）** | `READER_LAYOUT_WEBTOON_NOT_WIRED`（`pages/Reader.tsx:673-681`）；且 IPC 无 `chapter_type` 入口。非测量失败，是产品能力缺失。 |
| 真实 4K/DPR2 物理屏上的渲染 | NOT_RUN | 本机 DPR=1，DPR2 用 `Emulation.setDeviceMetricsOverride` 仿真，物理屏采样未做。 |
| 缩放交互（若有） | NOT_RUN（能力不存在） | 无控件可测（4.2）。 |
| 截图（原生窗口 / DPR2） | 已产出 | `session/main/shots/ac3-reader-native-window.png`、`ac3-reader-dpr2.png`。 |

---

## 5. 证据索引（全部可复核）

### 5.1 仓库内（本任务写范围）

```
verification/DISPLAY-PERF-DECISION-1/baseline/
├─ REPORT.md                      ← 本文件
├─ harness/                       ← 自建自包含测量工装（node 24 + pwsh 7）
│  ├─ env.mjs                     ← 隔离 env 构造 + 空目录断言 + CDP 端口基准
│  ├─ cdp.mjs                     ← 零依赖 CDP 客户端
│  ├─ launch.mjs                  ← 启动/日志打点/探针/清理
│  ├─ native-probe.ps1            ← Win32 探针（进程/窗口/Core/WebView2）
│  ├─ paint-probe.ps1             ← 首帧像素探针（NOT_RUN，见 2.4）
│  ├─ native-dialog.ps1           ← 原生选择器兜底驱动（未用于最终路径）
│  ├─ import-pages.ps1            ← 真实页导入（WM_SETTEXT + IDOK）
│  ├─ session.mjs / ctl.mjs       ← CDP 交互会话 + 控制 CLI
│  ├─ measure.mjs                 ← AC2/AC3 测量驱动
│  └─ run-ac1.mjs / diag-cdp.mjs  ← AC1 批量运行 / CDP 可用性诊断
├─ ac1/
│  ├─ ac1-summary.json / .md      ← AC1 中位/极值/逐次值
│  ├─ ac1-02/ ac1-03/ ac1-04/     ← 3 次正式冷启动（ac1-run.json + native-probe.jsonl + app.stderr.ts.log）
│  └─ _pilot/                     ← 2 次作废试跑（早期探针未同步/慢速采样，报告中不引用其数值）
├─ ac2/ac2-stages.json            ← AC2 逐页逐段原始值（3 页 × 4 次）
├─ ac3/
│  ├─ ac3-measurements.json       ← 渲染宽度/缩放扫描/翻页/采样汇总
│  ├─ fps-page-turns.csv / fps-scroll-attempt.csv / fps-idle.csv  ← 原始 rAF 采样
└─ session/
   ├─ main-ac3run/                ← AC3 运行的会话快照（session-start/teardown + shots/*.png）
   └─ main/                       ← AC2 运行的会话快照
```

### 5.2 仓外 task-env

```
G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/
├─ pinned-baseline/               ← 基线 exe + core-sidecar 副本 + PINNED-BASELINE.json（SHA-256）
├─ build-config/tauri.acceptance-dp1.conf.json  ← 仓外配置（仅 browser args，端口 9361）
├─ build-acceptance.log / build-acceptance-9361.log ← 两次构建日志（18.9–29 s，增量）
├─ fixtures/pages/page_001..030.jpg  ← 30 张真实页（来自 test_assets/comic_golden_suite/日漫_JA）
├─ runs/ac1-0N/                   ← 每次冷启动的隔离 APPDATA/TEMP/DATA/UDD + logs
├─ runs/session-main/             ← AC2/AC3 会话的隔离环境
├─ diag/diag-cdp-03/diag-report.json ← CDP 可用性证据（acceptance 构建 9361 监听 200）
└─ diag/diag-cdp-02/diag-report.json ← 冻结 release exe 无 CDP 的命令行证据
```

关键命令可完全复现（全部在 `harness/README` 内联注释里）：

```powershell
# AC1（黑盒，基线件）
node verification/DISPLAY-PERF-DECISION-1/baseline/harness/run-ac1.mjs 3
# CDP 验收构建（仓外配置，不改仓库文件）
cd apps/desktop/src-tauri
cargo tauri build --no-bundle --config "G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/build-config/tauri.acceptance-dp1.conf.json"
# AC2/AC3（会话 + 控制面）
node .../harness/session.mjs main 9362 9361      # 另开终端
node .../harness/measure.mjs ac3
node .../harness/measure.mjs ac2
```

---

## 6. NOT_RUN / BLOCKED 清单（汇总）

| # | 项 | 状态 | 原因（可复核） |
|---|---|---|---|
| 1 | AC1 首内容像素级精确时刻 | NOT_RUN | 冻结 exe 无 CDP；像素探针 C# 编译失败（`logs/paint-probe.stderr.log`）；仅早期试跑给 PROXY（空窗 ≥1.5 s） |
| 2 | AC1 书架数据到达时刻 | NOT_RUN | 需页内观测，AC1 锚定基线件（无 CDP） |
| 3 | AC2 `opt-level=1 vs 3` 同码 A/B 构建 | NOT_RUN | 改 opt-level 必须动 `Cargo.toml`（禁止）；已用产品内代理：Host SHA 3.55–4.65 ms vs WebCrypto 0.30–0.35 ms（慢 11–13×）。最小 `sha2` 工程对照未启动（时限） |
| 4 | AC2 分块（>16 MiB）路径 | NOT_RUN | 测试页均 <1 MiB，恒单 chunk |
| 5 | AC2 冷缓存首读 | NOT_RUN | 连测均热缓存 |
| 6 | AC3 长条滚动 FPS | **BLOCKED（产品未接线）** | `READER_LAYOUT_WEBTOON_NOT_WIRED`（`pages/Reader.tsx:673-681`）+ IPC 无法建 webtoon 章节 |
| 7 | AC3 真实物理 DPR2 采样 | NOT_RUN | 本机 DPR=1，仅 CDP 仿真 |
| 8 | 打包/启动场景（NSIS 安装后首启） | NOT_RUN | 本任务只测 `--no-bundle` 构建产物 |

---

## 7. 给下游（DISPLAY-PERF-DECISION-1 裁决）的 4 条可判决事实

1. **显示问题有明确量化指标**：真实页渲染到 39.3 % 缩放、横向利用率 39.9 %、**缩放能力 0**、
   长条滚动 = 未接线（`READER_LAYOUT_WEBTOON_NOT_WIRED`）。这不是审美问题，是几何/能力缺失。
2. **启动耦合是设计选择而非 bug**：Core 先起（本机 513 ms），窗口后开（558 ms），最坏 30 s 超时后
   UI 空转 + supervisor 后台重试。要改的是「窗口先出、Core 异步就绪」的架构顺序，不是加个 splash。
3. **字节效率热点可定位到行**：`resource_protocol.rs:509-527` 每请求整文件 SHA-256，
   0.6 MB 页 3.6–4.7 ms（占端到端 20 %、占管线 33–36 %）；`Cargo.toml:25-29` 的 `opt-level=1`
   让同一算法比硬件 SHA 慢 11–13 倍（产品内代理证据）。
4. **帧率不是问题**：rAF 稳定 59.95 fps；用户「效率不行」的真实来源是**每页 ≈23 ms 管线 +
   ≈50 ms 首帧延迟 + 每页 6.2 ms 固定 IPC**，以及不可滚/不可缩的交互缺失。
