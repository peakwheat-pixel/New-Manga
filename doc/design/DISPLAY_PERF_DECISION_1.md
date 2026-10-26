# DISPLAY-PERF-DECISION-1 — 显示效果与运行效率：证据基线 + 三路线裁决建议

> **SUPERSEDED（2026-10-26）**：本文的"A 现栈深化（Tauri）为主线"建议已被用户 2026-10-26 裁决取代——当前目标架构为 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（C#/.NET + Avalonia + 既有 Python Core，GPL-3.0 开源）。本文保留为**证据与成本基线**（测量数据、差距清单、三路线成本对比仍然有效），其路线推荐不再作为当前决策依据。

Status: SUPERSEDED_BY_AD_002（原为 DRAFT_FOR_USER_ADJUDICATION）
Owner: DSH（Lead/Architect）· Reviewer: 待指派（ZCode/Antigravity/Codex，DSH 不审自己的产出）
Evidence: `verification/DISPLAY-PERF-DECISION-1/**`、本 Task 卡 AC 行

---

## 0. 一句话结论

**四个"显示效果"诉求 + 启动割裂，实测下来没有一项是"必须换 UI 栈才能解决"的；唯一严格意义上的引擎上限只有「WinUI 真 Acrylic 的光学质感」（设计稿已明确选择仿制）。** 其余全部是实现欠账，只是欠账的**规模很大**（≈35–60 人日才能补齐），用户的"技术栈不行"体感来自欠账长期未还，而不是栈选错了。
换 UI 栈（WinUI3/Avalonia/Compose/Flutter）不会自动解决任何一个已实测痛点：图片通道成本在 Rust/Python 侧、启动顺序在 Rust 侧、排版在 Python 侧、阅读器渲染是前端欠账；且调查显示替代栈的 CJK 竖排能力并不更强（Avalonia 竖排仍在未合并 PR）。
**建议：A 现栈深化为主线（35–60 人日，分三批），排版单列一条子线；B 混合原生 GPU 层作为"阅读器像素级缩放/超大长条不达标时"的条件性升级（60–110 人日）；C 换栈不推荐（180–320 人日且不解决上述三项）。**

---

## 1. 被测件与口径（数字必须连同它引用）

| 项 | 值 |
|---|---|
| 仓库 HEAD | `c0251b9e7`（工作树干净） |
| 基线 exe | `new-manga.exe` SHA-256 `1136BB0A8D582A30C6EF0B16959B86A62DD26D2C6D9CE49E298C9B86C3343226`（2026-10-26 19:32，packaged 模式：`M2RC1_PACKAGED=1` + 自带 `resources/core-sidecar/`） |
| 测量环境 | 隔离 task-env（`APPDATA`/`LOCALAPPDATA`/`TEMP`/数据根/catalog/WebView2 UDD 全部重定向），未触碰用户真实数据 |
| 可复跑 | `verification/DISPLAY-PERF-DECISION-1/baseline/REPORT.md` §5 证据索引 + `harness/` |
| 重要基础设施事实 | 冻结 release exe **无法开 WebView2 CDP**（wry 覆盖 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`）；AC2/AC3 使用一次仓外配置的 acceptance 构建（差异仅 browser args，溯源见 `BUILD-PROVENANCE.json`） |

---

## 2. 实测基线

### 2.1 AC1 启动时间线（3 次冷启动，中位）

| 阶段 | 中位 ms | 说明 |
|---|---:|---|
| 进程创建 → Core sidecar spawn | 40 | |
| → Core ready（`[core.derived_gc]` 完成） | **513** | PyInstaller sidecar 装配 + startup ping |
| → `setup()` 到达 | 554 | |
| → **窗口可见** | **558** | 窗口在 Core 就绪后 45 ms 才出现 |

**结论（回答用户"Core 和软件不是一起启动"）**：Core 与 UI **是**一起启动的，但顺序是**严格串行、Core 先行**：`main.rs:1649-1706` 在创建窗口前同步等待 Core 的 startup ping，超时上限 **30 s**；超时后 UI 才出现且 Core 空转、由 supervisor 重试。本机代价约 0.56 s，但机器慢/杀软扫描/Core 装配变慢时，用户看到的是**双击后长时间没有任何窗口**。这不是"少了启动 Core"，而是**启动顺序把 UI 当成了 Core 的附属品**。

### 2.2 AC2 图片通道单页分解（真实页 657 KB，端到端 22.9 ms）

| 阶段 | ms | 占比 |
|---|---:|---:|
| Core resolve（授权解析，IPC 往返） | 3.40 | 14.9% |
| issue（签发资源 URL） | 3.20 | 14.0% |
| 协议取块（含**整文件 SHA-256** 4.65） | 6.00 | 26.3% |
| Blob 组装 | 0.50 | 2.2% |
| 解码 + 首帧 | 9.75 | 42.7% |

- 哈希隔离法：`?chunk=1` 越界请求恒 400 且发生在校验**之后**，据此把「整文件哈希」从「取块」里分离出来。
- 同字节 WebCrypto SHA-256 仅 **0.35 ms** → Host 侧慢 **11–13×**，与 `opt-level = 1` 的 release profile 一致（代理证据）。
- **规模效应**：657 KB 页 22.9 ms 尚可接受；但长条页/大图是 MB~数十 MB 级，哈希与取块按字节线性放大（50 MB 页仅哈希一项按当前速率约 350 ms 量级），**长条漫画场景会直接崩掉"翻页手感"**。而长条布局当前根本没接线（见 2.3）。

### 2.3 AC3 阅读器基线（DPR2）

| 项 | 实测 |
|---|---|
| 源图 | 1200 × 1660 |
| 实际渲染 | **471 × 652**（线性缩放 **0.3928**） |
| 阅读区 | 1180 × 812 → **横向利用率仅 39.9%** |
| 缩放能力 | **0 个控件、无手势、无快捷键** |
| 可滚动容器 | **0 个**（分页模式无平移） |
| 长条（webtoon_vertical） | **未接线**：`READER_LAYOUT_WEBTOON_NOT_WIRED`，产品直接提示"不会用分页方式假装可读" |
| 翻页 | 取图 19.25 ms / 解码 27.20 ms / 上屏 **49.60 ms**（n=10） |
| 帧率 | 翻页流/滚动尝试/空闲均 **59.95 fps**（p95 59.52） |

**结论**：阅读器的"显示效果"问题是**画面只有原尺寸 39% 大小、且没有任何缩放/长条能力**，不是帧率问题。现有代码位置：`ReaderPage.tsx` 的 `maxWidth: 480`、`WebtoonReaderView.tsx` 的 `maxWidth: 960`、`PagedReaderView` 的 `maxHeight: calc(100vh - 80px)`。

### 2.4 AC4 视觉差距（43 条编号，见 `visual/GAP_REPORT.md`）

| 类别 | 条数 |
|---|---:|
| 实现欠账 | **27** |
| 栈限制（严格：真 Acrylic 光学质感、OS 窗口圆角） | 2 |
| 栈限制·有原生替代（窗口 Mica、多窗口） | 2 |
| 设计源冲突（基线 vs Figma，需裁决） | 5 |
| 待验证 / 不判 / 已合规样本 | 2 / 1 / 4 |

关键 P0：

- **SH-01 窗口层没接原生 Mica**：亚克力配方（37 色令牌、blur 40/24 + saturate 140%、feTurbulence 噪声、≤2 层预算、3 条降级链）与 Figma 逐项一致，但窗口不透明、底下是纯色 → 全站浮层的模糊"没有东西可透"。Tauri 2 自带 `windowEffects`/`setEffects`（Windows 走 DWM，**不需要 Windows App SDK**），**修它约 0.5–1 人日**。
- **SH-03 双标题栏**：应用内自绘 titlebar 的窗口按钮是 `aria-hidden` 装饰 span，且没有 `decorations:false` → 系统标题栏与自绘条共存。
- **SH-04 四页是卸载式切换**：`UiRoot` 条件渲染，切页=卸载+重挂，无 keep-alive（违反基线 §1.2 冻结语义）、无转场；全仓只有 1 个 `@keyframes`。
- **设置页把内部词上屏**：`section · provider` / `settings_get` / `StartRun.overrides` / `profile_id` 等。
- **工作台**：检查器直书"当前 IPC 未返回 OCR 文本与置信度"；PageList 折叠成 24px 竖条（基线 240 / Figma 72 / 现状 24，三基准互斥）。

### 2.5 成品页排版（AC5，对照实验见 `routes/TYPESETTING_COMPARISON.md`）

现状实现是 Pillow 逐字符 `draw.text()`，实测四项硬缺陷：

1. **无 OpenType shaping**：`PIL.features.check("raqm")=False` 且调用不传 `features/language`；kerning 实测 0 差异（`AV`=35.97 vs `A+V`=36.00）、连字 0 差异（`fi`=16.0 vs `f+i`=16.0）。
2. **日文用中文字形排版**：默认字族 `Source Han Sans K Bold` 本机未安装，回退链最终落到 **Microsoft YaHei**（`available=False`），且 Pillow `ImageFont` **不做逐字形 fallback** → 日中字形差异字与日文专用字可能缺字/错形。
3. **竖排几何错了**：`cell = ascent+descent = 35px = 1.35em`（应 1em），列距 `26px = 1.0em`（应 ≈1.5em）→ 字距松散、列间拥挤；`_vertical` 还直接丢弃空格/换行，无法用换行控制分栏。
4. **无竖排禁则、无 `vert` 竖排字形、无 tate-chu-yoko**：`usable_h // cell` 硬切列，列首列尾禁则靠运气；字号拟合只看列宽，永不因高度不足失败。

**判定修正（相对初查）**：这**不是**"Pillow 做不到"的栈上限——Pillow 带 Raqm 构建 + 自写竖排算法 + 字体回退是可以补的；但"竖排日文 + 禁则 + 均等分栏 + 逐字形回退"这一组合，Chromium/WebView2 已有成熟实现。所以它是**实现欠账**，只是补齐成本高（12–20 人日），或在显示层改走 WebView2 竖排（成本低但需接受"显示/导出双路径"与一次 spike 验证）。

---

## 3. 三路线对比

> 成本单位：人日（1 人 × 1 天），区间含验证与回归；依据=页面数(4)/组件数(≈120 个前端文件)/契约面(已冻结 IPC，换栈需重接)。

| 维度 | **A 现栈深化**（Tauri2+WebView2+React 保留） | **B 混合原生层**（外壳保留，画布走原生 GPU 表面） | **C 换 UI 栈**（WinUI3/Avalonia/Compose/Flutter） |
|---|---|---|---|
| 解决 2.4 的 27 条欠账 | ✅ 全部可解 | ✅ 全部可解（同 A） | ✅ 可用新控件体系重写，但需重做一遍 |
| 窗口真 Mica | ✅ `windowEffects` + `transparent`（0.5–1d） | ✅ 同 A | ✅ 原生天然，但**换栈成本远超收益** |
| 阅读器 39% 画面 / 无缩放 / 长条未接线 | ✅ Canvas2D/WebGL2 分块 + 缩放 + 预取（5–8d） | ✅ 最彻底（原生贴图流水线，+10–20d） | ✅ 可做，但等于重写阅读器 |
| 图片通道成本（哈希/解码/往返） | ✅ Rust profile + 校验策略 + 预取/缓存（2–4d） | ⚠️ 部分（渲染层变了，通道还在 Rust/Python） | ❌ **不变**（与 UI 栈无关） |
| Core 启动串行（最坏 30s 白屏） | ✅ 窗口先行 + Core 异步 + 状态面（1–2d） | ✅ 同 A | ❌ **不变**（Rust 侧） |
| 排版引擎（Pillow 天花板） | ⚠️ 需单独替换：显示层 WebView2 竖排（DirectWrite）或 Core 换 Skia+HarfBuzz（8–15d） | ⚠️ 同 A | ❌ **不变**（Python 侧） |
| 动效系统（11 项清单） | ✅ CSS/View Transitions（2–3d，需验证 WebView2 版本支持） | ⚠️ 原生层动效与 WebView 层割裂 | ✅ |
| **估算总成本** | **35–60 人日** | **60–110 人日** | **180–320 人日**（4 页 + 105 个 TSX/28.6k 行 + 57 命令/184 处 invoke 重接，且上表 3 项 ❌ 不解决） |
| 主要风险 | WebView2 Evergreen 回归不可控：#5752（透明背景 alpha 回归）、#5642（嵌入宿主大图缩放后永久模糊瓦片，该生产 Tauri 应用最终迁到原生 DirectComposition 面）、#5426（嵌入 WebView2 canvas ≥3840 宽 FPS 160→55），均 open | 子窗口/覆盖层与 WebView2 的 airspace/输入/DPI 合成全部自研（wry 无原生支持，`wry#677`）；打包复杂度上升 | 推倒 AD-001 目标架构；368 个 Task 的资产与验收证据失效；竖排能力不保证更好（Avalonia 竖排 PR 未合并，WinUI3/Compose/Flutter 竖排未核实） |
| 不可解决项 | ① 真 WinUI Acrylic 的光学质感（设计已选仿制）② WebView2 嵌入宿主的合成/重光栅缺陷（#5642 类）只能规避不能根治 ③ Evergreen 更新无法锁死 ④ OS 窗口圆角需 DWM 调用（可做，1–2d） | 同 A + 与 WebView chrome 共存的 airspace 层级只是被管理而非消失 | 无一项已实测痛点被结构性解决 |

**结论**：A 覆盖全部可解项且成本最低；B 的唯一优势是"极端大图/120Hz 场景的渲染上限"，属于 A 达标失败后的**局部**升级路径，不应整栈迁移；C 不解决任何已实测瓶颈，却让既有架构资产全部重写。

---

## 4. 推荐路线：A + 排版子线，分四批

> 成本口径以 `routes/ROUTES.md` 为准（依据代码规模：TSX 105 文件/28.6k 行、Rust 16.9k 行/57 命令/184 处 invoke、Python Core 217 文件/47k 行、四页 3.7k 行）。下表为分批切分，合计对齐 A 的 **35–60 人日**。

### 批次 P0「一眼见效」（8–12 人日，低风险、可回滚、先拿观感）

| # | 改动 | 消掉 | 估时 |
|---|---|---|---:|
| 1 | 窗口 Mica：`transparent:true` + `windowEffects`(Mica) + 页面底改半透明 + 内容区 Solid 分层；失败降级 `#202020`；Win11 22621+ / Win10 降级 | SH-01、SH-02、RD-04 | 1–2 |
| 2 | 窗口 chrome：`decorations:false` + `data-tauri-drag-region` + 真 min/max/close + 双击最大化 | SH-03（双标题栏） | 1 |
| 3 | 四页 keep-alive + 150–250 ms cross-fade（含 `prefers-reduced-motion` 归零） | SH-04、SH-05（部分） | 1–2 |
| 4 | 设置页去技术化（内部词/协议词清零，无 wire 分区改灰置占位） | ST-01/02/05 | 0.5–1 |
| 5 | 书架视觉对齐（等分栅格、封面去掉竖排书名、"页数未知"→"—"、状态条改藏书语义） | SB-01/02/03/06 | 1–1.5 |
| 6 | 动效清单 11 项补齐（浮层 250 ms decelerate、批量条 200 ms、进度 ≤200 ms、共享元素 300 ms；View Transitions 需先验版本） | SH-05、WB-07、SB-09 | 2–3 |

### 批次 P1「阅读器与通道」（20–32 人日，决定"能不能舒服地看漫画"）

| # | 改动 | 消掉 | 估时 |
|---|---|---|---:|
| 7 | 阅读器渲染层：Canvas2D/WebGL2 分块贴图、fit 模式（适应宽/高/原始）、无级缩放+平移、DPR 感知、相邻页预取；长条（webtoon_vertical）接线 + 虚拟化 | 2.3 全部；RD-02/03/04/05；`READER_LAYOUT_WEBTOON_NOT_WIRED` | 12–20 |
| 8 | 图片通道：Cargo release profile 修正（opt-level 3 + LTO）；哈希预算策略（每 issue 一次校验 + 块级校验，或文件身份短 TTL 验证缓存，需契约评审）；chunk 复用 + 预取 + `no-store` 治理 | 2.2 的哈希/往返开销 | 8–12 |
| 9 | 工作台画布真缩放（>100%、平移、1:1、像素锐利）+ 检查器 kv 化 + PageList 形态落地 | WB-01/03/04/05/07 | （并入 7 的渲染层） |

### 批次 P2「启动与字体」（6–10 人日）

| # | 改动 | 消掉 | 估时 |
|---|---|---|---:|
| 10 | 启动重排：窗口先行（≤300 ms 可见）+ Core 异步 + 顶部状态面（连接中/就绪/重试）；sidecar 预热 | 2.1 的串行代价 | 5–8 |
| 11 | 字体策略：默认日文字体（Yu Gothic / Noto Sans JP）+ 逐字形 fallback + 竖排字形 | 2.5 缺陷 2 | 1–2 |

### 批次 P3「排版引擎」（12–20 人日，需先裁决显示/导出路径）

- 方案 1（先做 3–5 人日 spike）：**显示层** WebView2 竖排 HTML（`writing-mode: vertical-rl` + `line-break: strict` + `text-combine-upright`），**导出层**保持确定性渲染器 → 必须接受"屏幕所见与导出像素不完全一致"，用基准集约束。
- 方案 2：Core 内换 Skia+HarfBuzz（`skia-python`），显示与导出同源，Python 依赖与打包体积上升。
- 方案 3：Pillow 补齐 shaping（带 Raqm 构建）+ 竖排算法 + 禁则 + 字重回退（**成本最高、收益最低**，仅保底）。
- **AC5 的 WebView2 对照样本当前无效**（HTML flex 容器塌缩），方案 1 必须先用 spike 证明。

**合计：A = 35–60 人日。若 P0+P2 先做（14–22 人日），"像正经应用 + 启动不白屏"即可达成；P1 决定阅读体验；P3 决定成品页专业度。**

---

## 5. 可测量验收门槛（建议作为后续实现 Task 的硬门槛）

| # | 门槛 | 当前实测 |
|---|---|---|
| G1 | 冷启动到窗口可见 ≤ 300 ms（Core 不再阻塞开窗） | 558 ms（串行） |
| G2 | 阅读器默认 fit 下横向利用率 ≥ 90%，且可切 1:1/适应宽/适应高 | 39.9% |
| G3 | 4000×60000 长条页滚动 p95 帧 ≤ 20 ms，无 >100 ms 卡顿 | 长条未接线（BLOCKED） |
| G4 | DPR2 下 400% 缩放像素级锐利（无插值模糊），平移 ≥ 55 fps | 无缩放能力 |
| G5 | 单页冷加载 ≤ 60 ms（50 MB 长条页 ≤ 400 ms），哈希占比 ≤ 10% | 22.9 ms@657KB，哈希 26.3% |
| G6 | 同屏 `backdrop-filter` ≤ 2 层且 Mica 生效时窗后壁纸可见 | Mica 未接；亚克力底下无内容 |
| G7 | 内部术语上屏 = 0（`Core`、`IPC`、`section`、`provider_id` 等黑名单 grep） | 多处（见 GAP_REPORT） |
| G8 | 竖排排版禁则违例 = 0，基线偏差 ≤ 1 px（对照参考渲染器） | Pillow 无禁则 |
| G9 | 四页切换保留状态、转场 150–250 ms、`prefers-reduced-motion` 下归零 | 卸载式切换、无转场 |

---

## 6. 需要用户裁决的决策点

| # | 决策点 | 选项 | DSH 建议 |
|---|---|---|---|
| D1 | 一级导航形态（**设计源冲突**：基线左侧 Rail 64 vs Figma titlebar 横向 tab；现状是第三种） | ① 按 Figma 横向 tab ② 按基线 Rail ③ 保持现状 | ①（Figma 是用户最新确认稿） |
| D2 | 阅读器是否沉浸式（隐藏 titlebar；基线 vs Figma 冲突） | ① 沉浸式 ② 保留 chrome | ①，并保留浮动退出 |
| D3 | 工作台 PageList 形态（基线 240 / Figma 72 filmstrip / 现状 24 折叠） | ① Figma 72 胶片条 ② 基线 240 可调 | ① 更贴近 Figma，且窄窗友好 |
| D4 | 是否授权窗口层原生化（`transparent` + Mica + 无边框 chrome） | ① 授权 ② 不授权 | ①（0.5–1 人日，是"像正经应用"的关键一步） |
| D5 | 排版显示/导出是否接受双路径 | ① 接受（显示 WebView2、导出确定性引擎） ② 要求同源（Core 换 Skia） | ① 先验证，② 作为备选 |
| D6 | 是否授权按 P0→P1→P2 顺序开工（先 P0 拿观感，再 P1 拿阅读体验） | ① 全部 ② 只 P0 试点 ③ 先 P1 | ① |
| D7 | 预算/时间上限（用于我拆 Task 与选 Owner） | 由用户给 | 建议先给 P0+P1 的预算（约 28–44 人日） |
| D8 | WebView2 版本策略（A 路线最大的不确定性来源：Evergreen 回归无法锁死） | ① 跟随 Evergreen ② 固定 Runtime 版本（牺牲安全更新） | ① 跟随 + 用降级路径兜住；不固定版本 |
| D9 | Windows 版本门槛（真 Mica 需 Win11 22621+） | ① Win10 降级为不透明/纯色 ② 不支持 Win10 | ① |
| D10 | 是否先授权 3–5 人日 spike：① WebView2 竖排排版 spike（决定 P3 方案 1/2）② 阅读器 canvas 在真机 DPR2 的 400% 缩放/长条 spike（决定要不要启动 B） | ① 都做 ② 只做① ③ 只做② ④ 都不做 | ①（两个 spike 直接决定后续两条大分支，避免盲投） |

**另需用户确认一件事**：你观察到"Core 和软件不是一起启动"的具体现象是什么？——①双击后长时间没有窗口；②任务栏出现两个窗口/进程；③界面出来了但提示 Core 未连接、要等或手动重启；④其他。实测显示当前 packaged 构建是"Core 先起、窗口后出"（0.56 s），与①的症状一致；若你看到②③，可能是安装版构建/环境与仓库构建不同，需要用你的安装包复测一次。

---

## 7. 风险与不可解决项

- **不可解决（本栈内）**：CSS 合成永远达不到 WinUI Acrylic 的真光学质感（设计已选择仿制）；WebView2 嵌入宿主的合成/重光栅缺陷（`#5642` 类）只能规避不能根治；Evergreen 更新带来的回归无法锁死（除非固定 Runtime，代价是安全更新滞后）。
- **WebView2 已知 open 回归（A 路线的主要风险）**：`#5752` 透明背景 alpha 回归；`#5642` 嵌入宿主大图缩放后永久模糊瓦片（该生产 Tauri 应用最终迁到原生 DirectComposition 面）；`#5426` 嵌入 WebView2 canvas ≥3840 宽 FPS 160→55。均未在本机复现，但都是 open 状态。
- **B 的触发条件（建议写进裁决）**：A 完成阅读器 canvas/分块后，若真机 DPR2 400% 缩放仍出现不可控重采样/掉帧（按 §5 G3/G4 判定），或 `#5642` 类问题在用户机复现，则启动 B，范围**限定在阅读器+工作台画布**，外壳四页不动。
- **需要验证**：WebView2 版本对 `document.startViewTransition` 的支持（决定共享元素动效实现）；WebView2 竖排 HTML 的实际排版质量（AC5 对照样本当前无效，必须 spike）。
- **不能承诺**：4K/120 Hz 下超长图的无级缩放极致顺滑 —— 若 A 路线 G3/G4 不达标，再启用 B 的"原生 GPU 画布"局部升级。
- **跨路线共同项（无论 A/B 都要先做，不因换栈消失）**：① 图片通道去全量 SHA-256 / chunk 复用 / 预取 / `no-store` 治理；② 启动并行化与 Core 生命周期；③ Rust release 构建档位（`opt-level`）；④ 字体策略（默认日文字体 + 逐字形 fallback + 竖排字形）。

---

## 8. 证据索引

| AC | 证据 |
|---|---|
| AC1/AC2/AC3 | `verification/DISPLAY-PERF-DECISION-1/baseline/REPORT.md`（+ `harness/`、`ac1/`、`ac2/`、`ac3/`，43 文件） |
| AC4 | `verification/DISPLAY-PERF-DECISION-1/visual/GAP_REPORT.md`（43 条编号 + `figma-ref/`） |
| AC5/AC6 | `verification/DISPLAY-PERF-DECISION-1/routes/TYPESETTING_COMPARISON.md`、`routes/ROUTES.md` |
| 代码事实 | 本文各节行号引用（`main.rs:1649-1706`、`resource_protocol.rs:509-527`、`resourceChannel/client.ts:81-101`、`Cargo.toml:25-29`、`pillow_rendering.py:99-238`、`base.css:113-118`、`tauri.conf.json:11-24`） |
