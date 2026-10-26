# DISPLAY-PERF-DECISION-1 / AC6：A 现栈深化 · B 混合原生 GPU 层 · C 换 UI 栈

范围：四个显示面（① 外壳材质/动效 ② 阅读器漫画画面 ③ 翻译成品页排版 ④ 工作台画布）+ Core 启动割裂。
证据基线：父任务卡 F1–F9（`doc/tasks/DISPLAY-PERF-DECISION-1.md`）+ 本目录 AC5 实验（`TYPESETTING_COMPARISON.md`、`metrics.json`）+ 下列外部一手资料。
**「明确不可解决项」是本文件最重要部分**：任何路线都不得承诺「换完就全部解决」。

## 1. 现状事实（决定路线收益的分母）

| # | 事实 | 依据 |
|---|---|---|
| F1 | 窗口创建前同步等 Core ping（≤30s），再 spawn sidecar，最后 `tauri::Builder` | `apps/desktop/src-tauri/src/main.rs:1649-1706,1734` |
| F2 | 每图片 chunk 请求都重新授权 + 打开文件 + **顺序读全文件算 SHA-256**，`no-store` | `apps/desktop/src-tauri/src/resource_protocol.rs:509-527` |
| F3 | 前端逐 chunk fetch 拼 Blob，每页重挂载重签，不复用 | `resourceChannel/client.ts:81-101`、`workbench/pageImage.ts:24-26` |
| F4 | 阅读器图片最宽 480/960，无缩放/平移/分块/预取；DOM `<img>` 由 CSS 缩放 | `src/pages/Reader.tsx:431`、`reader/WebtoonReaderView.tsx:91`、`reader/ReaderPageImage.tsx:235-247` |
| F5 | release `opt-level=1` + `codegen-units=256` + `incremental=true`（F2 的哈希跑在此构建下） | `apps/desktop/src-tauri/Cargo.toml:25-29` |
| F6 | Mica/亚克力为 CSS 仿制，窗口不透明、无 DWM backdrop | `src/design/base.css:113-118`、`tokens.css:80-83`、`tauri.conf.json:11-24` |
| F7 | 成品页 Pillow 逐字符 `draw.text`，无 shaping/竖排禁则/字号拟合 | `pillow_rendering.py:99-172,214-238` + AC5 实测 |
| F9 | 长条滚动 avg 17.53ms / p95 33.3ms（掉 30fps 档） | `verification/P20-AC4-FPS-1/ac3-real-desktop/fps-webtoon-summary.json` |
| 规模 | React：105 个 `.tsx` / 28,602 行，52 个 `.ts` / 8,734 行；Rust：9 文件 / 16,926 行 / 57 个 `#[tauri::command]` / 前端 184 处 `invoke(`；Python Core：217 文件 / 47,065 行；四页：Reader 827、Settings 362、Shelf 1019、Workbench 1452 行；60 个前端测试文件 | 本目录实测（`git status` 干净，HEAD `c0251b9e7`） |

## 2. 三路线矩阵

| 维度 | A 现栈深化（Tauri2+WebView2+React 保留） | B 混合原生 GPU 层（外壳/四页保留，画布原生化） | C 换 UI 栈（WinUI3/Avalonia/Compose/Flutter） |
|---|---|---|---|
| ① 材质/动效 | **可解决**：真 Mica/Acrylic 是配置+平台 API 级工作。Tauri 2 配置 `windowEffects.effects` 已内置 `mica/micaDark/micaLight/tabbed/acrylic/blur`（[schema](https://schema.tauri.app/config/2)）；或 `window-vibrancy` 直接调 DWM（[crate](https://docs.rs/crate/window-vibrancy/latest)）；DWM `DWMWA_SYSTEMBACKDROP_TYPE`/`DWMSBT_MAINWINDOW` 需 **Win11 22621+**（[Learn](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwm_systembackdrop_type)）。风险：透明窗口 + WebView2 在 Runtime 154 上出现「alpha=0 仍画不透明主题底色」的回归（[#5752](https://github.com/MicrosoftEdge/WebView2Feedback/issues/5752)，open，2026-10-08） | **可解决**（同 A，不因画布原生化而变好） | 理论更顺（WinUI3 原生 `MicaBackdrop`），但需重写外壳与主题系统 |
| ② 阅读器画面 | **部分可解决**：DOM `<img>` 的大图由 Chromium cc 分块光栅（GPU 瓦片 ≈ 视口宽×1/4 视口高，见 [How cc Works](https://raw.githubusercontent.com/chromium/chromium/main/docs/how_cc_works.md)），单 canvas 上限 `kMaxCanvasArea=32768*8192≈2.68 亿 CSS px`、`kMaxSkiaDim=65535`（[Chromium 源码](https://raw.githubusercontent.com/chromium/chromium/main/third_party/blink/renderer/core/html/canvas/canvas_rendering_context_host.cc)）；WebGL2 纹理受 D3D11/驱动上限（常见 16384）。**但** 嵌入宿主有已报告回归：canvas ≥3840 宽 FPS 160→55（[#5426](https://github.com/MicrosoftEdge/WebView2Feedback/issues/5426)，open）；缩放后交换同尺寸大图出现「永久模糊瓦片」，Edge 标签页正常、嵌入 WebView2 复现，该生产 Tauri 应用最终**把文档像素移到 transparent WebView 下的原生 DirectComposition 面**（[#5642](https://github.com/MicrosoftEdge/WebView2Feedback/issues/5642)，open） | **最彻底**：wgpu/D3D11 自有交换链，分块贴图 + 无级缩放 + 预取全可控；约束需自管：`wgpu` 默认 `max_texture_dimension_2d=8192`、`max_buffer_size=256MiB`（[wgpu-types](https://docs.rs/wgpu-types/latest/wgpu_types/struct.Limits.html)）→ 必须分块；子 HWND/覆盖层与 WebView2 的 **airspace/输入/DPI 合成** 全部自写（wry 无原生支持，见 [wry#677](https://github.com/tauri-apps/wry/issues/677)） | 视栈而定：Skia/Impeller/Win2D 能给出可控 GPU 面；但四页 UI 也要重写 |
| ③ 成品页排版 | **可解决但必须换排版实现**：Pillow 竖排四欠账（shaping/字体回退/竖排几何/禁则）都是实现级；可自带 Raqm 的 Pillow+自写算法，或换 Skia+HarfBuzz | 同 A（排版在 Core/Python 侧，与画布路线无关） | **不一定更好**：调查到的替代栈对 CJK 竖排支持薄弱或进行中（Avalonia 竖排 advance 仍在 PR：[#22184](https://github.com/AvaloniaUI/Avalonia/pull/22184)）；WinUI3 XAML/Compose/Flutter 的竖排写作能力**未核实**，不能假设有 |
| ④ 工作台画布 | **可解决**：同②的 canvas 方案（大图查看/框选/缩放平移本质是同一套贴图+变换） | **最彻底**（同②） | 视栈而定 |
| Core 启动割裂 | **可解决**：并行化（先建窗再等 Core、sidecar 预热、首屏骨架）——纯工程，与栈无关 | 同 A | 同 A（换栈不会自动解决，反而重写 IPC 更慢） |
| 工作量（人日，含测试/回归） | **35–60**：材质/动效 8–12；阅读器 canvas+缩放+预取 12–20；图片通道（去全量哈希/复用/缓存）8–12；排版引擎 12–20；启动并行 5–8（四页 UI 不重写） | **60–110**：A 的②④替换为原生面 25–45；输入/DPI/合成/窗口层 15–30；回退与降级路径 8–15；其余同 A | **180–320**：四页 + 105 组件 + 57 IPC 重写 120–200（前端 28.6k 行 TSX 为底）；Core/IPC 适配 30–60；排版与画布从零 30–60 |
| 风险/依赖 | 中：WebView2 Evergreen 回归直接落在用户机（#5752/#5642/#5426 均 open）；透明+Mica 组合需逐 Windows 版本验证 | 高：airspace/输入/DPI 合成是自研硬骨头；打包/签名增加原生依赖；但**可把渲染问题与 WebView2 版本解耦** | 最高：范围=重写整个 UI 层；栈级竖排/文本能力未证实；打包/签名/更新链全部重建 |
| 可测量验收门槛（建议） | 冷启动→首屏 p50 ≤1200ms、p95 ≤2000ms；Core ready 不阻塞首帧；4000×60000 长条滚动 p95 ≤16.7ms；DPR2/400% 缩放边缘测试卡无重采样模糊；竖排禁则违例 0 且竖排字形正确；同屏 backdrop 层 ≤2；Mica 在 Win11 22621+ 真机可见、Win10 降级为不透明 | A 的全部门槛 + 原生面与 WebView chrome 的叠放/输入命中/DPI 切换无错位；单帧 GPU 提交 ≤X ms（真机标定） | 四页功能/契约 parity（57 命令 184 调用点全绿）+ A 的显示门槛 + 竖排/字体能力须先做 spike 证明可行 |
| **明确不可解决项** | 1) WebView2 嵌入宿主的合成/重光栅缺陷（#5642 类）只能规避/回退，不能根治；2) 浏览器 Evergreen 更新带来的回归无法锁死（除非固定 WebView2 版本，代价是安全更新缺失）；3) 同屏大量 `backdrop-filter`/亚克力层仍受 GPU 合成成本限制；4) 若要做「像素级无重采样」的 400% 放大，DOM `<img>` 路线的重光栅时机不完全可控 | 1) 不能解决**成品页排版**（仍在 Python/Core）；2) 不能解决 Core 启动割裂；3) 自研原生面要自己承担字体/无障碍/输入法/高 DPI 的全部边界；4) 与 WebView chrome 共存时的合成层级（airspace）始终存在，只是被管理而非消失 | 1) 换栈**不会**自动带来竖排商业级排版（多数栈没有）；2) 不会解决 Core 启动割裂；3) 已投入的 47k 行 Python Core + 57 命令契约是对齐成本，不是收益；4) 一次重写引入的回归风险无法用「栈更好」抵消 |

## 3. 推荐倾向

**A 为主线、B 为条件性升级、C 暂不推荐。**

理由：用户抱怨的「效果做不到」中，AC5 已证明成品页排版主要是 Pillow 实现欠账；F4/F9 的阅读器问题里，缩放/分块/预取未实现（实现欠账）与 WebView2 嵌入合成回归（宿主限制）同时存在。A 的 35–60 人日能覆盖材质、图片通道、启动并行、排版四项；剩余风险集中在「阅读器像素级缩放/超大长条」——这正是 #5642 生产案例最终走向 B 的信号。C 的 180–320 人日没有对应的能力收益证据，且在竖排排版上可能**倒退**。

**B 的触发条件（建议写进裁决）**：A 完成阅读器 canvas/分块后，若真机 DPR2 400% 缩放仍出现不可控的重采样/掉帧（以 AC3 门槛判定），或 #5642 类问题在用户机复现，则启动 B，范围限定在阅读器+工作台画布，外壳四页不动。

**跨路线共同项（无论 A/B 都要做，优先于换栈）**：
1. 图片通道去全量 SHA-256、chunk 复用、预取、`no-store` 治理（F2/F3）；
2. 启动并行化与 Core 生命周期（F1）；
3. Rust release 构建档位（F5，`opt-level` 对照属 AC2）；
4. 字体策略：默认日文字体（Yu Gothic/Noto Sans JP）+ 逐字形 fallback + 竖排字形。

## 4. 需要用户裁决的决策点

1. **成本/时间上限**：A 的 35–60 人日 vs B 的 60–110 人日，是否接受「先 A、按触发条件再 B」的两阶段？
2. **是否接受局部原生化（B）**：阅读器/工作台改为原生 GPU 面，牺牲一部分 Web 技术一致性（事件、无障碍、样式统一）换取像素级渲染控制。
3. **显示能力优先级**：如果「成品页排版质量」优先于「阅读器极限缩放」，则 A 的排版子项可立即开工，不需要等 B。
4. **WebView2 版本策略**：是否接受固定 Runtime 版本以规避 Evergreen 回归（换安全更新滞后）。
5. **Windows 版本门槛**：Mica 需 Win11 22621+；Win10 用户是否接受降级为不透明/纯色。
6. **是否授权先做 3–5 人日的 B-spike**（一个原生面 + 输入/DPI 验证），再决定 B 是否进入排期。

## 5. 外部资料与核实状态

| 事实 | 状态 | 来源 |
|---|---|---|
| Tauri 2 `windowEffects` 支持 mica/micaDark/micaLight/tabbed/acrylic/blur | 已文档化 | https://schema.tauri.app/config/2 |
| `window-vibrancy` 提供 `apply_mica`（Win11）；Tauri 需 `transparent:true` + `html,body{background:transparent}`；blur/acrylic 在 Win11 22621+ 拖动/缩放性能差 | 已文档化 | https://docs.rs/crate/window-vibrancy/latest |
| DWM `DWMSBT_MAINWINDOW`=Mica、`DWMSBT_TRANSIENTWINDOW`=Acrylic；最低 Win11 22621 | 已文档化 | https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwm_systembackdrop_type |
| WebView2 Runtime 154 透明背景回归（Tauri/wry 宿主复现） | 已报告 open（未在本机复现） | https://github.com/MicrosoftEdge/WebView2Feedback/issues/5752 |
| 嵌入 WebView2 大图缩放后永久模糊瓦片；生产 Tauri 应用迁到原生 DirectComposition 面 | 已报告 open（单案例，未本机复现） | https://github.com/MicrosoftEdge/WebView2Feedback/issues/5642 |
| 嵌入 WebView2 canvas ≥3840 宽 FPS 160→55（Runtime 142；Edge 标签页不复现） | 已报告 open（单案例） | https://github.com/MicrosoftEdge/WebView2Feedback/issues/5426 |
| Chromium canvas 上限 `kMaxCanvasArea=32768*8192`、`kMaxSkiaDim=65535` | 已文档化（源码） | https://raw.githubusercontent.com/chromium/chromium/main/third_party/blink/renderer/core/html/canvas/canvas_rendering_context_host.cc |
| Chromium cc 瓦片光栅、Directly composited images | 已文档化（设计文档） | https://raw.githubusercontent.com/chromium/chromium/main/docs/how_cc_works.md |
| wgpu `max_texture_dimension_2d` 默认 8192、`max_buffer_size` 默认 256MiB | 已文档化 | https://docs.rs/wgpu-types/latest/wgpu_types/struct.Limits.html |
| wry 无「WebView 嵌入 wgpu/原生面」一等支持（feature request，已关闭） | 已文档化（issue 状态） | https://github.com/tauri-apps/wry/issues/677 |
| Avalonia 竖排 advance（VVAR/vmtx）仍在未合并 PR | 已文档化（PR 状态，2026-09） | https://github.com/AvaloniaUI/Avalonia/pull/22184 |
| WinUI3 XAML / Compose Desktop / Flutter 的 CJK 竖排写作能力 | **未核实**（本次未取得一手资料，不得当结论） | — |
| WebView2 visual hosting/composition controller 的 airspace 细节 | **未核实**（Learn 页面 404，未取得一手文档） | — |
| `pypdfium2`/商业排版引擎作为 Core 排版替代的成本 | **未核实** | — |

## 6. 不确定项与 AC5 缺口

1. AC5 的 Chromium 侧 DOM 量化 BLOCKED（本机 Edge launcher 交接问题）、有效并排对照图未取得，标点/禁则/描边探针 NOT_RUN —— 详见 `TYPESETTING_COMPARISON.md` §1/§7。
2. 部分显示面数字依赖 AC1–AC4 的真机测量（本任务未跑）：冷启动/首屏、Core ready 时间线、DPR2 渲染宽度、FPS。
3. B 的 airspace/输入/DPI 可行性只到「有生产先例+需自研」级别，未做 spike。
4. 成本区间为工程判断（依据本文件 §1 代码规模与改动面），未做逐项 WBS 估时。
