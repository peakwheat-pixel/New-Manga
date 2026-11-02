# R2R2 finding 处置表（实施者记录，不代替独立 Review）

所有“已修复”均指代码/自动化断言已交付；PNG 逐图签署由 DSH 重新 Appointment 独立上下文 Reviewer。未签署=NOT_RUN；AC-1/AC-3 不写 MET。Task 保持 in_progress。只修改用户本轮 allowed_paths，不使用 Task 较宽的历史授权修改域外 Controls、Themes、Task/STATUS/PLAN/checkpoint。

| Finding | 本轮处置 | 证据 / 仍待事项 |
|---|---|---|
| R2R2-001 P1 | 已修复主题捕获 | Residual2Evidence 从 App.axaml 重新加载真实资源清单；DesignSystemThemeManager.Initialize + 传入 shell；AppearanceCoordinator 存 workspace 临时根；light/dark Canvas token 和非文本背景 patch 像素断言；组件也做双主题。 |
| R2R2-002 P1 | 粒子可见性已修复；渐变独审待签 | 粒子前景 IsHitTestVisible=false；Reader Grid 限定视口；隔离粒子层比较同帧像素，25px≤差异<阅读区1%，非整页淡入；生产 clock 首/中/尾采样；full/reduce 帧均真实。shelf 只选既有 Bg.Canvas/Bg.Overlay 令牌提高差值；原像素裁切，fresh shell phase0 / intermediate-2000ms / reduce静态；生产clock另采精确半周期。可辨度仍由独审签署，不以微小像素差强行签署。 |
| R2R2-003 P1 | 已修复 | Slider:not(:disabled) /template/ Thumb 使用 StyleTrigger 优先级覆盖模板值；normal/hover/disabled 都断言实际 Thumb/模板 Border/轨道；FluentMotionScope排除模板RepeatButton的外层按钮tween；截图重生。 |
| R2R2-004 P1 | 已修复 | fluent-icon class + NmIcon.Settings；checked class；default/checked 像素差异断言。 |
| R2R2-005 P1 | 核心空白/缺图已修复；范围仍 PARTIAL | Reader host 两页 ReaderPageData + LoadAsync(book-1,chapter-key)，单页显示；Progress=60/100；Progress/Thumb显式基类ControlTheme、横向缩略页项、模板内容/像素非空断言；三章列表足够视口；补全 IN-2A 各状态、AlertBanner九值、Error/Skeleton/StreamingThumb、Dialog/Drawer开合、CommandPalette真实结果/空。Top/Nav/Status真实默认/较窄布局截图已有；StatusBand错误/运行专用通道不存在，NavRail独立折叠/真实200%DPI未跑，明确 NOT_RUN，不用默认帧冒充。未经 DSH 重冻结不改 IN 分类。 |
| R2R2-006 P1 | 已修复文档 | expected-tokens 每状态明确键/属性/file:line；旧矩阵EFFECTIVE交叉锚点；D-11四态↔九值表；D-14例外。 |
| R2R2-007 P2 | 已修复 | coverage新增9派生类；ChapterList/StreamingThumb/ReaderPage/Progress/SettingsGroup/SettingsField/TabStrip解析后属性断言。 |
| R2R2-008 P2 | 已修复 | inventory由单一捕获测试一次写出；head=捕获时git rev-parse HEAD；真实frame/theme/frontend/尺寸/命令/SHA；行数=PNG数；签署NOT_RUN。 |
| R2R2-009 P2 | 已修复最终日志 | impl-r2-rework-verification.log 保存最终命令/EXIT/逐程序集/57条实际skip原因/差值；旧三份日志保留原字节，历史统计不冒充当前。 |
| R2R2-010 P2 | 已修复 | ResourceChanged仅附着时订阅、detach解除；detach后换主题不刷新、reattach刷新回归；重复checked样式删除。映射澄清：旧R2-011=泄漏，旧R2-007=状态通道，二者不混号。 |
| R2R2-011 P2 | 已修复接线/采样 | WindowBase.HandleDeactivated触发真实Window事件；Activate恢复；Hide/Show暂停恢复；失焦后改动效策略不重启循环、暂停粒子detach清理缓存层；粒子停帧后保留剩余时间；生产clock采样；布局定位仅SizeChanged，帧内无Canvas.SetLeft/Top。 |
| R2R2-012 P2 | 已修复 | SearchField内部TextBox按Tab聚焦，断言外部nm-focus-ring可见、Accent.Base与Border.Focus；内边框保持Line.Default/Hairline；修正旧无通道注释/测试名。 |
| R2R2-013 P2 | Handoff已修正；域外指针待DSH | 本轮准确计数/主题/限制/提交锚点见Handoff；Task delivery_head不在用户本轮allowed_paths，由DSH接收后更新。 |
| R2R2-014 P2 | 已修复 | 默认捕获前后真实git status对verification相同；旧FEA-06全文件SHA字典前后相同；opt-in精确输出路径+git status仅本卡visuals断言。 |
| R2R2-015 P2 | NOT_RUN（域外治理） | DSH在集成/终态判定前更新STATUS下一步、PLAN旧下一节点、Task delivery_head；本会话未改这些文件。 |
| R2R2-016 P2 | 活跃路径已修复；旧死代码清理NOT_RUN | HasMotion注释限定有限navigation/feedback，新增decorative-only显式断言；新粒子执行器消费归一化progress，无duration常量反向依赖/每帧Canvas写入；旧Controls/FluentUi.cs未调用粒子工厂仍保留using与旧函数，超本轮写域不清理。完成测试原先默认Navigation|Feedback未再缩减，decorative有独立测试覆盖。 |
| R2R2-017 P2 | 新证据标识已修正；域外历史声明待DSH | 新decor全部builtin.fluent、与页面相同带数据Host和真实资源栈；inventory含frontend。checkpoint §142/143的过度声明未获本轮写域授权，明确由本表/Handoff纠偏，DSH追加当前说明，不改历史原字节。 |
| R2R2-018 P2 | 保持独立后续卡，不写达成 | D-14已有裁决A和ready后续卡；本卡不改StatusCatalog、保留NotStarted特判；OUT/BLOCKED保持原分类。 |

未完成项的Owner/时点：DSH接收本Handoff时处置R2R2-005清单缺口、002暗色渐变感知阈值及015/017治理指针；R2R2-016域外死代码清理须另行授权；所有PNG待fresh独立Reviewer逐图签署。原生DPI/a11y仍B-5/D-1 NOT_RUN，不伪造结果。
