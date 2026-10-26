# 排版渲染对照实验：Pillow 现状 vs Edge/WebView2（Chromium `writing-mode: vertical-rl`）

任务：DISPLAY-PERF-DECISION-1 / AC5。全部产物在 `verification/DISPLAY-PERF-DECISION-1/routes/`。
实验脚本：`typesetting_sample.py`（可复跑）；原始数值：`metrics.json`。

## 1. 运行状态（如实）

| 项 | 状态 | 证据 |
|---|---|---|
| 现状样张（真实产品路径：`PillowTextLayoutEngine` + `PillowFontCatalog` + `PillowImageCompositor` + `resolve_font_size`） | **DONE** | `sample_current_pillow.png`（真实页 `test_assets/comic_golden_suite/日漫_JA/oc material/17/050.jpg` + 白泡清版 + 竖排日文） |
| 共享基底「清版图」（气泡内部白填充，模拟 CLEAN artifact） | **DONE** | `page_clean_plate.png`；方法见 `metrics.json.base` 与 `_probe_bubble.py` |
| 替代样张截图（Edge headless） | **PARTIAL** | `sample_webview2_vertical_rl.png` 已截到 1350×1920 真页图，但**该 HTML 的 flex 竖排容器把文字压成顶部细条**：截图只证明「同一页 + Chromium 能渲染页面」，**不能作为有效排版对照样本**（这是本实验 HTML 写法缺陷，不是 Chromium 能力结论） |
| Chromium 侧 DOM 量化（逐字符 rect / 列结构 / 禁则 / 字号拟合 overflow / `CSS.supports`） | **BLOCKED** | 本机 `msedge.exe` 是 launcher，`--dump-dom` 在子进程交接时输出丢失（0 字节，stderr 空）；尝试 `subprocess`、`Start-Process -Wait`、`Start-Process` 轮询、`cmd /c > file` 均失败；截图路径在「不重定向 launcher stdio」时可成功 → 判定为本机 Edge 启动器限制，非能力缺失 |
| 调优样张（显式分栏 + justify + 日文字体） | **NOT_RUN** | 同一 Edge 阻塞 |
| 标点/禁则/描边三个探针 | **NOT_RUN**（脚本已实现，未跑通） | `typesetting_sample.py` 中已定义，未产出 PNG |

**结论口径**：本文只把「现状 Pillow 实测」当作硬证据；Chromium 侧只能给能力性判断，凡未实测处标「待验证」。

## 2. 字体与 shaping 实测（硬证据，来自 `metrics.json.font_current`）

- 生产默认字族 `D03 §11.6 = "Source Han Sans K Bold"`（`src/application/rendering/style.py:28`），本机**未安装**；`PillowFontCatalog` 回退链 `Source Han Sans K Bold → Source Han Sans Bold → Source Han Sans SC Bold → Microsoft YaHei → SimSun → Arial`（`pillow_rendering.py:25-32`）最终落到 **Microsoft YaHei（中文字体）**，`available=False`。
  - 后果：日文正文用中文字形排版（如 直/骨/海 等日中字形不同的字），且**没有逐字形 fallback**（Pillow `ImageFont` 不做字体回退），日文专用字（込/峠/畑 等）可能缺字。
  - 定性：这是**配置/实现欠账**，不是「换 UI 栈才有的能力」——Pillow 也能加载 `Yu Gothic/Noto Sans JP`，只是默认链里没有日文字体。
- shaping：`Pillow 12.3.0`，`PIL.features.check("raqm") = False`（本机 Python），且代码调用 `draw.text` 时不传 `features`/`language`（`pillow_rendering.py:230-238`）。实测：
  - kerning：`getlength("AV")=35.97` vs `getlength("A")+getlength("V")=36.00` → 差异 0.03px（舍入），**无 kerning**；
  - 连字：`getlength("fi")=16.0` vs `getlength("f")+getlength("i")=16.0` → **无 ligature**；
  - 竖排标点/竖排字形（`vert` 特性）、`tate-chu-yoko`：代码逐字符 `draw.text`，`TextDirection.VERTICAL` 仅改变坐标计算（`pillow_rendering.py:160-172`），**没有任何竖排字形替换**。
- Chromium/WebView2 侧：`writing-mode: vertical-rl` + DirectWrite/HarfBuzz 是文档化能力（Chromium 支持 vertical writing、`text-combine-upright`、`line-break: strict`）；具体 CSS 支持矩阵本次未实测 → **待验证**。WebView2 与 Edge 同 Chromium 引擎，差异仅在宿主（见 ROUTES.md 的 WebView2 宿主风险项）。

## 3. 竖排几何缺陷（硬证据，最重要的「是不是栈不行」判定）

`PillowTextLayoutEngine._vertical`（`pillow_rendering.py:160-172`）的几何：
- 字符纵向步进 `cell = ascent + descent`。本机 YaHei @26px：ascent=28、descent=7 → **cell=35px = 1.35em**；
- 列间距（横向）`pitch = max glyph advance × line_spacing` = **26px = 1.0em**。

即：**本该 1em 等距的字符被拉开到 1.35em，本该 ~1.5em 的列距反而只有 1.0em**——字距松散、列间拥挤。实测同一 232×536 文本框：
- Pillow 分 3 列、每列最多 15 字（`usable_h // 35`），43 字排成 15/15/13，文本块宽 78px、高 525px；
- 换行/空格被**直接丢弃**：`_vertical` 过滤 `character.isspace()`（`pillow_rendering.py:161`），实测追加 `"\n追記"` 后 items 数不增加 → 竖排模式**无法用换行控制分栏**，也不能做均等割り/追い込み；
- 竖排禁则（行頭禁則 `、。」` 等 / 行末禁則 `「『（` 等）：引擎把字符按 `usable_h // cell` 硬切块，**没有任何禁则判断**。本样本未触发违例（列首字符恰好是「だ」「で」），但这是概率结果，不是规则保证；受控探针已写在脚本里但未跑（BLOCKED）。
- 字号拟合：`resolve_font_size` 只做「候选 26px → 是否 fits → 0.5px 级收缩」（`style.py:120-182`）；竖排的 `fits` 只看列宽，**永远不会因高度不足而失败**——分栏数溢出宽度才缩字号，无法按「均等分栏」求最优字号。

## 4. 像素分析（谨慎解读）

同区域 ink 统计（`metrics.json.pixel_analysis`）：

| 指标 | Pillow 现状 | Chromium 截图 | 解读 |
|---|---|---|---|
| ink coverage | 0.066 | 0.020 | **不可直接比较**：Chromium 样本布局塌缩（见 §1），文字少 |
| mid-gray（抗锯齿）比例 | 0.568 | 0.644 | 两者都是灰度抗锯齿；比例受字号/描边/缩放影响，**不作质量分** |
| mean ink darkness | 54.8 | 75.2 | Pillow 黑字更「实」，与 `stroke_width=3` 白描边位置（Pillow 先描边后填充）有关 |

结论：像素统计仅作方向性证据；**不能**据此声称「Chromium 更清晰」。清晰度结论要看 AC3 的真机 DPR2 截图（本任务外的 AC3 证据）。

## 5. 对照结论（一句话版）

排版差距的主因是**当前 Pillow 竖排实现的几何/字形/禁则/字形回退四项欠账**，而不是「Pillow 这个库做不到」：Pillow 可以做真 shaping（需带 Raqm 的构建 + `features`/`language` 参数），竖排几何、禁则、分栏是可实现的排版算法；但在「竖排日文 + 禁则 + 均等分栏 + 逐字形字体回退」这一组合上，**Chromium 已经有了免费且成熟的实现**，Pillow 路线需要自己补齐或换排版引擎（Skia/HarfBuzz 等）。

## 6. 可复跑

```
cd verification/DISPLAY-PERF-DECISION-1/routes
python typesetting_sample.py          # Pillow 侧可完整复跑；Edge 侧在本机 BLOCKED（见 §1）
```
Edge 手动截图（可用，但不含 DOM 量化）：
`msedge.exe --headless --disable-gpu --hide-scrollbars --window-size=1350,1920 --virtual-time-budget=5000 --screenshot=<png> <html>`；注意本机需把输入/输出放在无空格路径下，且不要重定向 launcher 的 stdout/stderr。

## 7. 缺口清单（给裁决用）

1. Chromium 侧逐字符 DOM 量化（列结构/禁则违例/字号拟合/`text-combine-upright`/`CSS.supports`）——BLOCKED，需换一台不被 launcher 限制的机器或用 Playwright/CDP。
2. 有效的并排对照图（当前 WebView2 截图布局塌缩）——需修 HTML 后重截。
3. 标点探针（`。、「」` 竖排字形位置/ink centroid）、受控禁则探针、描边/AA 探针——NOT_RUN。
4. 商业排版引擎（InDesign 级）对照——未纳入本次范围。
