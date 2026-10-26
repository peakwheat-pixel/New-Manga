# AD-002 — 目标桌面架构

Status: **ACCEPTED_TARGET_ARCHITECTURE**（用户 2026-10-26 书面裁决 v1.0）。本文件取代 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的 React+Tauri 前端目标；AD-001 转为历史。
Owner: DSH（Lead/Architect）· Decision authority: User · Date: 2026-10-26
依据：`verification/DISPLAY-PERF-DECISION-1/{baseline,visual,routes,ui-stack,ui-spec,nonadmin}/**`

**用户已裁决的三项**：① 前端 = C#/.NET + Avalonia 11；② UI = **全部页面"着重参考" Saber（不做 1:1 复刻）**，书架是参考重点；③ 许可证 = **GPL-3.0 开源**（因此可合法移植 Saber 代码并保留版权声明）。

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

## 5. 许可证（已裁决：L2 开源 GPL-3.0）

**产品主许可 = GPL-3.0。** 由此解锁：

- ✅ 可移植 Saber-Translator（GPL-3.0）的代码/流程/组件，**必须保留原版权声明与许可证文本**，衍生作品同样 GPL-3.0；
- ✅ 可随包分发 OFL/Apache 字体（思源/Noto 等）；
- ⚠️ **Ultralytics YOLO = AGPL-3.0**：GPL-3.0 与 AGPL-3.0 可组合（GPLv3 §13），但组合作品分发时应按 **AGPL-3.0** 提供——**建议直接把产品声明为 AGPL-3.0**（最省事、合规），或改用 Apache/MIT 检测器以保持纯 GPL-3.0；
- ⚠️ 商业/系统字体（`msyh`、`STKAITI`、`STZHONGS` 等）**不得随包分发**，只能依赖用户系统已安装或改用 OFL 字体；
- ❌ 即使开源，也不得删除上游版权声明或附加额外限制。

**合规义务清单（写进发布 Gate）**：仓库根 `LICENSE`（GPL-3.0 或 AGPL-3.0 全文）、`NOTICE`/`THIRD_PARTY_LICENSES.md`（逐项列出移植的 Saber 文件与模型/字体许可）、源码可获得性（发布页提供对应源码 tag）、构建脚本可复现。

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

## 7. 裁决结果（已定）

| # | 决策点 | 结果 |
|---|---|---|
| D-A | 许可证 | **L2 开源 GPL-3.0**（含 Ultralytics 时按 AGPL-3.0 分发，建议产品直接声明 AGPL-3.0） |
| D-B | UI 参考范围 | **全部页面均为"着重参考" Saber，不做 1:1 复刻**：书架重点参考其信息架构/布局范式/交互流程/视觉语言；工作区参考其分区与动作顺序；阅读器/设置沿用既有 Figma v2 结构 + Saber 配色令牌（主题中心统一）。Saber Purple 作为内置默认主题 |
| D-C | 主题中心 | 内置 6 套 + Saber Purple 默认；ThemePack 三档换肤；后续可导入 |
| D-D | 桌宠/悬浮球 | 待定（Saber 有；Avalonia 透明窗口可做，+5–8 人日） |
| D-E | 旧壳处置 | Tauri 版保留并行可运行，S4 完成后删除 |

## 8. 任务拆解（S0–S5，可直接释放）

| 阶段 | Task 建议 ID | 交付 | 估时 | 依赖 |
|---|---|---|---|---|
| S0 | `UI-AVALONIA-SPIKE-1` | 11 项门槛（spike 工程在 workspace，不进产品仓库） | 5 人日 | AD-002 冻结（本文件） |
| S0b | `SABER-UI-SPEC-1` | `ui-spec/SABER_UI_SPEC.md` + `tokens-saber-purple.json` | 2 人日 | —（进行中） |
| S1 | `HOST-CORECLIENT-1` | C# `CoreClient`：spawn/JSON-lines/错误码/`\uXXXX`；`ping`+`list_books`；中文零乱码 | 5–8 人日 | S0 通过 |
| S2 | `HOST-COMMAND-MIGRATION-1` | 57 命令 → 6 个 C# service；契约 parity 测试 | 15–25 人日 | S1 |
| S3 | `UI-SHELL-THEME-1` | 主窗+导航+主题中心+书架 1:1+设置骨架 | 25–40 人日 | S1/S0b |
| S4 | `UI-WORKBENCH-READER-1` | 工作台画布/区域编辑 + 沉浸式阅读器（分块/缩放/长条） | 40–70 人日 | S3 |
| S5 | `LEGACY-SHELL-REMOVAL-1` | 删 Tauri/React/WebView2/m2res/CORS/每请求 SHA-256；全量回归 | 15–25 人日 | S4 |

**合计 200–400 人日**（含回归）；关键路径 S0 → S1 → S3 → S4。
