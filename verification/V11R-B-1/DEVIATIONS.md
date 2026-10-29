# V11R-B-1 偏差记录（DEVIATIONS）

只记录与冻结规格/契约的**有意偏差**及理由；不影响 AC 的项也列出，便于 L3 审查裁决。

| ID | 规格/契约 | 实际实现 | 理由 | 影响 |
|---|---|---|---|---|
| D-1 | SCREEN_SPECS §2：主体 `PageGrid` 封面网格（≥1600 四列、1280 三列），右栏驻留详情面板 | 主体=作品封面网格（1600 四列 / 1280 三列 / 1024 三列），右栏=驻留详情（元信息/章节账本/页数/进度/操作）；**页**以真实文件名清单 + 多选呈现，不用缩略图网格 | Host 未提供封面与页缩略图读取命令；页缩略图需资源通道（`ReadPageImageAsync` 可用但整章预取成本高，且 Library 规格把「页」列在驻留面板） | 视觉上主页无封面图（首字占位）；列的响应式断点符合规格 |
| D-2 | SCREEN_SPECS §1：Row2 StatusBand「有 Run 时才显形」 | Run 未接入前，StatusBand 仅在真实活动（导入进行中）或 Host 未就绪时出现；通知走内容区就地 `AlertBanner` | 避免底部常驻空条；Run 进度属 B-4 | B-4 接入后恢复 Run 摘要（结构已预留） |
| D-3 | 契约 §3.2：`StatusGlyph/StatusBadge/Kbd/EmptyState/AlertBanner` 由 DS 提供 | DS M0 尚未交付这些自定义控件；暂用 `Views/V2/Shell/Controls/` 本地实现（命名/职责贴近契约） | 依赖未合入时的既定降级策略（任务卡允许先本地实现） | DS 交付后替换为 `nmc:*`；样式只保留在 `V2LocalStyles.axaml` |
| D-4 | 契约 §6.3：`Tab` = Studio 模式切换 | 只在工位空间拦截 `Tab`；Library/Console 保留系统焦点遍历 | 全局吞掉 Tab 会破坏键盘无障碍（WCAG 2.1.2）；模式切换仍满足契约位 | 工位空间内 Tab 生效；其它空间不误伤 |
| D-5 | DESIGN_SYSTEM §8：焦点环 2px accent | DS M0 已覆盖 Button/TextBox；**TextBox 仍有 Fluent 的 system accent 外发光**（Fluent FocusAdorner 未被 DS 覆盖） | DS M0 范围问题，不在本任务修改 DS | 功能无影响；待 DS 后续统一（已上报 Lead） |
| D-6 | 契约 §6.3 命令面板 `↑↓` 选择、`Enter` 执行 | 键盘由 shell 单一隧道处理（不依赖列表控件焦点）；列表保留鼠标双击执行 | 保证无论焦点在搜索框/列表，行为一致 | 无 |
| D-7 | SCREEN_SPECS §2：搜索支持「中文/拼音首字母」 | 中文子串 + 本地常用字拼音首字母表（约 400 字）；未覆盖字符退化为原字匹配 | 不引入第三方拼音库（许可证评审未做，B-1 不扩依赖） | 生僻字首字母搜不到；已知限制 |
| D-8 | FUSION_SPEC §2.3：状态七态 + 未开始/锁定 | 本地 `NmStatus`（九态）+ 契约 §2.3 符号；`queued` 用契约符号 `◦`，而 `tokens.json` 写 `·` | 契约 §2.3 是 UI 接口权威；两者不一致已记录待 Lead/DS 统一（DS `Nm.State.Symbol.*` 已存在，后续直接采用） | 状态符号视觉差异 1 字符；不影响语义 |
| D-9 | 上下文保留：切换空间/模式不重建 VM、不丢滚动/筛选 | 已实现（K/V 实例保持 + `ShellState` 每空间视图状态）；测试断言 VM 引用相等与 scroll/search/selection 保持 | — | 无 |
| D-10 | 阅读浮层：Webtoon 纵向 + 双模态进度 | 双模态（页码+百分比）显示真实；webtoon 保存按页 id，滚动像素 offset 传 null（UI 百分比为近似） | `SaveReadingProgressAsync` 的 scrollOffsetY 语义待 Core 契约明确 | 断点续读回到该页起始位置，不回到精确滚动像素 |
| D-11 | V11R-A-1 未合入时「新建章节」应显示能力待接入 | 合并 main 后 `CreateChapterAsync` 已存在 → 已切换为**真实实现**（含失败 typed 码、空标题本地拒绝、成功后刷新章节账本）；无章节时 ImportDock 入口真实可用 | 依赖已合入 | 关闭审计 F011；证据见测试 `ImportDock_WithoutChapter_*` |
