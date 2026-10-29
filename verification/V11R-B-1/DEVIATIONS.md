# V11R-B-1 偏差记录（I1 返修后）

| ID | 规格/契约 | 实际实现 | 理由 | 影响 |
|---|---|---|---|---|
| D-1 | SCREEN_SPECS §2 主体 PageGrid 封面网格 | 作品封面网格（≥1600 四列 / 1280–1599 三列 / <1280 四列+覆盖式详情）；页以真实文件名清单+多选呈现（缩略图网格待 Host 缩略图命令，follow-up） | Host 未提供封面/缩略图读取命令 | 视觉无封面图（首字占位）；响应式断点符合 R-18 |
| D-2 | SCREEN_SPECS §1 StatusBand「有 Run 时才显形」 | Run 未接入前，StatusBand 仅在真实活动（导入/Host 未就绪）出现；通知走内容区 AlertBanner | 避免底部常驻空条 | B-4/INT-0 接入 Run 后恢复 Run 摘要 |
| D-3 | 契约 §3.2 DS 自定义控件 | DS M0 未交付 StatusGlyph/StatusBadge/Kbd/AlertBanner/EmptyState；暂用本地实现（命名贴近契约） | 依赖未合入的既定降级 | DS 交付后替换为 `nmc:*` |
| D-4 | 契约 §6.3 Tab = Studio 模式切换 | 键盘漏斗先给当前工作区 `TryHandleKey`（R-17），工作区未消费才由 shell KeyMap 处理 Tab；Library/Console 不吞 Tab | 修复「Studio 的 Tab/Esc 收不到」且不破坏无障碍焦点遍历 | 工位内 Tab 生效；其它空间保持系统焦点遍历 |
| D-5 | DESIGN_SYSTEM §8 焦点环 | DS M0 已覆盖 Button/TextBox；TextBox 仍有 Fluent 系统 accent 外发光 | DS M0 范围问题，已转 design-platform | 功能无影响；待 DS 修复 |
| D-6 | 契约 §6.3 命令面板 ↑↓/Enter | 键盘由 shell 单一隧道处理（不依赖列表焦点）；列表保留鼠标双击执行 | 保证焦点无关的一致行为 | 无 |
| D-7 | 搜索支持中文/拼音首字母 | 中文子串 + 本地常用字拼音首字母表（约 400 字），未覆盖字符退化为原字匹配 | 不引入第三方拼音库 | 生僻字首字母搜不到（已知限制） |
| D-8 | queued 状态符号 | **`·`（中圆点）**：Lead 裁决以冻结 DESIGN_SYSTEM §2.2 为准；此前「◦ 来自契约 §2.3、tokens.json 为 ·」的记录已作废（§2.3 为起草笔误） | Lead 裁决 | 全状态符号与 DS `Nm.State.Symbol.Queued` 一致 |
| D-9 | 上下文保留 | ViewModel 实例保持；`IWorkspaceView.OnDeactivated` 写回滚动/筛选/选择，`OnActivated` 恢复；滚动为真实 `ScrollViewer.Offset` | 契约 §6.1 | 无 |
| D-10 | Webtoon 双模态进度 | 页码/百分比显示真实；保存按页 id，`scrollOffsetY` 传 null | Core 进度语义待确认 | 断点回到页起始，不回到精确像素 |
| D-11 | V11R-A-1 未合入时新建章节显示待接入 | 已合入 → 真实 `CreateChapterAsync`（失败 typed 码、空标题本地拒绝、成功刷新账本）；ImportDock 措辞与类注释已改为「请先新建章节（走 Core CreateChapter）」 | 依赖已合入 | 关闭审计 F011 |
| D-12 | 契约 §6.1 `IWorkspaceView` | 已定义并用 Library/Console 实现；扩展 `bool TryHandleKey(KeyEventArgs, ShellState)`（R-17）；`AppShellViewModel.SwitchSpace/SetStudioMode` 严格先 deactivate 后 activate | 审查 P2.2/P2.3 | 工位/主题工作室接入可复用同一 seam（INT-0） |
| D-13 | AC2「不丢滚动」 | 滚动从「只写 ShellState 的测试同义反复」改为真实 ScrollChanged 写回 + 激活恢复，测试断言真实 Offset 往返 | 审查 P2.3 | 无 |
| D-14 | AC4 裸设计值 | 新增 `ShellLayout` 统一解析 DS 令牌；`Nm.Size.Breakpoint.*` 尚未由 design-platform 合入，暂以 `ShellLayout.BreakpointFull/Compact/Narrow = 1600/1280/1024` 常量承载（文件内注释 + TODO）；其余尺寸（Drawer/TreeWidth/FilmStrip/Space）均读 DS 资源 | 审查 P2.4/P2.5；不阻塞当前门 | DS Breakpoint 合入后切换常量来源（follow-up） |
| D-15 | conformance 扫描范围 | C# 扫描限定本任务 Owner 目录（Shell/V2、ViewModels/V2/{Shell,Library,Console}、Views/V2/{Shell,Library,Console}），排除 Studio/ThemeStudio（各自 Owner 审查）与旧 Views | 审查 P2.4 | Studio/ThemeStudio 由其 Owner 保证 |
| D-16 | 证据生成 | R-19：测试默认只写 `%TEMP%/newmanga-evidence/<TASK>/`；仓库证据必须由显式 `curate.ps1`（`NEWMANGA_EVIDENCE_SYNC=1`）生成；文件名含测试名唯一化；IO 失败重试且不炸测试 | Lead R-19；修复 `IOException` 映射文件争用 | 普通测试不再污染仓库 |
| D-17 | TopBand 高度 36px | 用 `Height` + `MinHeight` 双约束保证真实 36px（DS 按钮最小高度会撑破 MinHeight），内边距改用 `Nm.Padding.IconSm` 令牌 | 审查 P2.8 要求 36px 断言 | 内容在 36px 内垂直居中 |
| D-18 | 主题入口语义 | TopBand 保留两个入口：「主题工作室」（打开 C-2 表面/占位）+「深色/浅色」快速外观切换；tooltip 说明差异 | 审查 P2.10 | 无 |
