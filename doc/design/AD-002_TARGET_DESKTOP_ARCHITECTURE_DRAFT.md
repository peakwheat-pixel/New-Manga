# AD-002 — 目标桌面架构（草案 v0.1，待用户书面裁决后冻结）

Status: DRAFT — 本文件是裁决输入，不是实现授权。取代 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的 React+Tauri 前端目标；AD-001 转为历史。
Owner: DSH（Lead/Architect）· Decision authority: User · Date: 2026-10-26
依据：`verification/DISPLAY-PERF-DECISION-1/{baseline,visual,routes,ui-stack,nonadmin}/**`

---

## 1. 决策

**Windows + C#/.NET 9 + Avalonia 11（XAML/Skia/D3D11）+ 既有 Python Core + SQLite + Managed Copy。**

| 边界 | 责任与约束 |
|---|---|
| Avalonia（C#） | 四页 UI、交互、主题中心、阅读器/工作台画布的全部渲染。不直接访问 SQLite；通过 Host 服务层访问领域能力。 |
| C# Host 服务层 | 进程生命周期（spawn/监控 Python sidecar）、IPC 编解码、主题包加载、缩略图/tile 缓存。**取代原 Tauri/Rust host。** |
| Python Core（保留） | 业务/领域/持久化权威（47,065 行既有资产）。OCR/翻译/修复/排版/导出、SQLite 写入。 |
| 传输 | **stdio JSON-lines，复用已冻结契约**（Core protocol 2.3、资源控制面 wire v1）。非 ASCII 必须 `\uXXXX` 转义（cp936 历史坑）。 |
| SQLite | 保持 Python Core 独占写。 |
| Managed Copy | 保持既有实现与验收。 |

**明确移除**：React/TypeScript、Tauri、Rust host（9 文件/16,926 行）、WebView2、`m2res` 自定义 scheme、CORS、`Cache-Control: no-store`、每请求整文件 SHA-256。
**明确保留**：57 个命令契约语义、grant 三件套（identity/size/digest 校验语义）、`CREATE_NO_WINDOW`、资源大小上限、插件沙箱边界（改成 Host 侧实现）。

## 2. 为什么是这个组合（证据）

| 结论 | 证据 |
|---|---|
| 前端必须非 Web | 用户裁决；WebView2 嵌入宿主有 open 回归（#5752 透明、#5642 大图模糊、#5426 4K canvas 掉帧） |
| Avalonia 主选 | 运行时换肤一等机制（`ControlTheme`/`ThemeDictionaries`/`DynamicResource`/`ThemeVariantScope`）；单文件自包含+裁剪**实测 34.24MB**；HarfBuzz+Skia；Win11 Mica / Win10 AcrylicBlur |
| 不选 WinUI3 | 官方不能单文件；`Application.RequestedTheme` 运行期受限，直接打击"主题中心" |
| 不选 QML/Flutter/Compose | QML 运行期换肤被官方否决 + PySide6 LGPL/同进程；Flutter/Compose Windows IME open issue |
| Python Core 不重写 | 与 Saber-Translator 后端同构（Python+Torch+ONNX+SQLite）；重写无收益，且 47k 行是既有资产 |
| 排版必须留 Core | 任何 UI 栈的 CJK 竖排能力都不足（Avalonia 竖排 PR #22184 未合并；其余未核实）→ Core 渲染成图，UI 只做 1:1 像素显示 |

## 3. 书架 1:1 复刻 Saber（用户指定参考）

参考物：用户本机安装 `E:\software\Saber-Translator`（PyInstaller onedir / Python 3.11 / Vue3 工作区）+ 官方截图（`verification/DISPLAY-PERF-DECISION-1/ui-stack/saber-ref/`）。

**实测视觉令牌（从其工作区 CSS 提取）**

| 令牌 | 值 |
|---|---|
| 顶栏渐变 | `linear-gradient(135deg, #667eea, #764ba2)` |
| 主色 | `#6366f1`（主按钮）/ `#667eea` / `#4f46e5`（hover/active） |
| 页面底 | `#f5f5f5` / `#f8fafc` |
| 卡片 | `#ffffff`，圆角 8–12px，阴影 `0 2px 8px rgba(0,0,0,0.05)` |
| 边框 | `#e0e0e0` / `#e2e8f0` |
| 状态色 | 绿 `#22c55e`、红 `#ef4444`、蓝 `#3498db` |
| 字体 | 系统 UI 字体；正文 14px 级；标题 20–24px |

**书架页结构（按截图 1:1）**：顶栏（Logo+产品名 / 局域网地址条 / 使用教程 / GitHub / 头像）→ 标题行「我的书架」+ 右侧三个动作（`+ 新建书籍`、`管理标签`、`快速翻译`）→ 搜索条（占满宽 + 右侧搜索按钮）→ 标签筛选行（`标签筛选:` + 计数 chip）→ 书籍网格（封面竖版 3:4、书名、`N 章节`、标签 chips）→ 右下角悬浮圆球（桌宠/快捷入口，可选）。

**必须复刻的流程**（下一步做交互规格提取）：
1. **新建书籍**：封面可选 + 书名 + 标签 → 创建后进入详情。
2. **书籍详情页**：封面、元信息、章节列表（新建/排序/统计）、进入工作区。
3. **导入流程**：图片/文件夹/PDF/ZIP/CBZ → 选择书籍/章节 → 进度 → 落库。
4. **快速翻译**：独立工作区，重置语义明确。

> 复刻原则：**视觉与交互规格可 1:1；代码不 1:1**（见 §5 许可证）。Avalonia 侧用 ThemePack + 自定义 ControlTheme 实现，令牌集中成一个 JSON，便于主题中心切换。

## 4. 主题中心（Saber 没有的能力，本项目差异化）

**ThemePack 结构**（目录或 `.nmtheme` zip）：

```
manifest.json          # id/name/version/author/preview.png/minAppVersion
tokens.json            # 颜色/圆角/间距/字体/字号/密度/阴影/状态色
controlthemes.xaml     # 每类控件（Button/ListBox/Card/TabView/ScrollBar…）的完整 ControlTheme
materials.json         # Mica / Acrylic / Solid 三档 + 回退
motion.json            # 动效时长/曲线（100–300ms，reduced-motion 归零）
icons/                 # 图标集（可选，覆盖默认）
```

**三档切换粒度**：① 仅配色 ② 完整皮肤（配色+形状+图标+动效）③ 材质档。**运行时热切换**（`ThemeVariantScope` + `DynamicResource`），目标 P95 ≤100ms、无重启、无旧色残留。
**内置**：Fluent Dark、Fluent Light、Saber Purple（1:1 复刻）、高对比无障碍、纸质漫画、霓虹。

## 5. 许可证决策树（**阻塞项，必须用户裁决**）

用户要求「有能用的代码和模型直接拿来使用」+「书架 1:1 复刻」。这与 Saber-Translator 的 **GPL-3.0** 直接冲突：

| 方案 | 能否拿 Saber 代码 | 代价 | 适用 |
|---|---|---|---|
| **L1 闭源/商业化** | ❌ 不可拷代码、不可粘片段；UI 可自己复刻 | 需独立实现全部流程；AGPL 模型（如 Ultralytics YOLO）需商业授权或替换；字体只能用 OFL/Apache 类（思源/Noto），Windows 系统字体与华文商业字体不得随包 | 将来要卖/闭源分发 |
| **L2 开源 GPL-3.0** | ✅ 可移植代码并保留版权声明；AGPL 组件兼容 | 整个产品须 GPL-3.0 开源（含后续修改） | 不打算闭源分发，愿意开源 |
| **L3 混合隔离** | ⚠️ 仅"独立进程/独立仓库 + 明确边界"下的有限借用，法律风险取决于交互方式（IPC 边界判例不统一） | 架构复杂化，仍需法务确认 | 不建议 |

**模型/资产许可证（逐项待核实，先给方向）**：PaddleOCR/RapidOCR ≈ Apache-2.0 ✅；Ultralytics YOLO = **AGPL-3.0**（商用需授权）；manga-ocr / LaMa / litelama 权重需逐个核实；思源黑体 = OFL-1.1 ✅ 可随包；`msyh.ttc`、`STKAITI`、`STZHONGS` 等为系统/商业字体 ❌ 不得随包。
**本仓库当前没有任何 Saber 代码**（仅截图与公开 README 事实）。

## 6. 迁移路线（灰度，非一次性重写）

| 阶段 | 内容 | 出口门槛 |
|---|---|---|
| S0 选型 spike（5 人日） | 11 项门槛（见 `ui-stack/STACK_COMPARISON.md` §6）：单文件 34MB、Mica、3 套主题热切、CoreClient 中文往返、4000×60000 分块渲染、IME、打包 | 任一硬失败 → 换备选 |
| S1 Host 协议 | C# `CoreClient`：spawn sidecar + JSON-lines 往返 + 错误码透传 + `\uXXXX`；跑通 `ping`/`list_books` | 中文书名往返零乱码；无控制台窗口 |
| S2 57 命令 | 按 6 个 domain service 分组迁移（settings 36 / library 14 / region 7 / reader 4 / resource 2 / workbench 1 生产调用） | 契约 parity 测试全绿 |
| S3 三页 | 主题中心 + 书架（1:1 Saber）+ 设置 | 截图对照 + 换肤验收 |
| S4 两页 | 工作台（画布/区域编辑）+ 阅读器（沉浸式、分块缩放、长条） | 阅读器门槛 G2–G4 |
| S5 删除旧面 | 移除 Tauri/React/WebView2/m2res/CORS/no-store/每请求 SHA-256 | 通道成本 ≤10%、全量回归 |

**成本**：200–400 人日（依据 `ui-stack/STACK_COMPARISON.md` §3.6）；S0+S1 约 15–25 人日可先出可运行骨架。

## 7. 待用户裁决

- **D-A 许可证**：L1 闭源 / L2 开源 GPL-3.0 / L3 隔离——**决定 S2 之后能拿多少 Saber 资产，也决定能否 1:1 复刻时直接移植其实现**。
- **D-B UI 参考范围**：仅书架/详情/新建/导入 1:1，还是工作台也尽量贴 Saber（当前工作台 Saber 是 Web 版式，与阅读器沉浸式可能冲突）。
- **D-C 主题中心内置套数与品牌色**：默认 6 套 + Saber Purple 复刻？
- **D-D 桌宠/悬浮球**：是否要（Saber 有，Avalonia 透明窗口可做，+5–8 人日）。
- **D-E 旧壳处置**：Tauri 版保留为并行可运行版本直到 S4 完成，还是尽早删除。
