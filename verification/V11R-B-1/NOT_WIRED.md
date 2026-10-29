# V11R-B-1 未接入能力清单（诚实降级，UI 全部标注）

原则（AC1）：未接入真实 API 的能力**不伪造数据、不假装成功**。每条都在 UI 上以标记 + 文案呈现，
且不能通过键盘/点击得到“假成功”。

| # | 能力 | 现状（代码位置） | UI 呈现 | 依赖 |
|---|---|---|---|---|
| 1 | 回收站列表 / 恢复 / 永久删除 | `IHostController` 未暴露 `list_recycle_bin` / restore / purge（命令在注册表但无服务层方法） | `RecycleBinView`：`AlertBanner`「能力待接入」+ 空态；`恢复/永久删除` 均打开真实二次确认 Modal，但确认按钮 disabled 并给出原因，不写任何数据 | core-bridge 追加服务层方法 |
| 2 | 批量删除 / 标记（页/书） | 无对应 Host 命令 | 批量条按钮 → 就地提示「能力待接入（Host 未暴露…）」 | core-bridge |
| 3 | 导出（批量条 & Ctrl+E） | V2 导出预检归 **V11R-B-5**；旧版导出流程未迁移（旧 `Views/ImportExportPanels.cs` 不修改） | 按钮 → 就地提示「能力待接入：V11R-B-5」；Ctrl+E 同样诚实提示，不静默 | V11R-B-5 |
| 4 | 需要我处理（待确认/失败/阻塞/过期）与 `F5`/`Ctrl+Shift+F` | Run 投影 `GetTaskProjection` 属 **V11R-A-2 / V11R-B-4** | `AttentionMenu` 计数显示「—」（不显示 0 以免误读为“无异常”）；点击/F5 → 提示能力待接入 | V11R-A-2 + B-4 |
| 5 | Region 跳转 | 无工位画布/Region 数据（**V11R-B-3**） | Ctrl+P 只列作品/章节/页；底部注明 Region 需工位空间 | V11R-B-3 |
| 6 | 工位空间内容（Page/Batch） | 归属 **ui-studio**（B-3/B-4 已合入 main）；壳侧工作区注册/激活集成属 **V11R-INT-0** | `StudioPendingView` 诚实占位（未注册工作区应有的降级形态）；空间路由、Tab 模式切换、共享 selection 已可验证 | V11R-INT-0（Studio 的 IWorkspaceView 适配） |
| 7 | 控制台空间 9 分区 | **V11R-B-2** 已交付（Owner 同一人，另有独立证据 `verification/V11R-B-2/`）；本 B-1 证据中的控制台截图为当时占位 | 本任务保留 `ConsoleView` 路由与工作区 seam；B-2 证据见其目录 | 无（B-2 已交付） |
| 8 | 主题工作室 7 分区 | **V11R-C-2** | `ThemeStudioPendingView` 占位 + **真实**深浅外观切换（DesignSystemThemeManager） | V11R-C-2 |
| 9 | 封面图片 / 页缩略图 | Host 无封面/缩略图读取命令 | 书卡用标题首字占位（不伪造图片）；页以真实文件名清单呈现。**页缩略图网格：待 Host 缩略图命令（follow-up，Lead 裁决定为 V1 后可延项）** | core-bridge / 资源通道扩展（follow-up） |
| 10 | 未选中章节的页数 | `list_chapters` 不返回页数；逐章 `list_chapter_pages` 代价高 | 未选中章节显示「—」，选中后真实填充 | Core 投影扩展（可选） |
| 11 | 文件夹导入的逐文件明细 | `ImportFolderAsync` 为单次调用，Host 只回聚合计数 | 文件夹行显示聚合结果并注明「Core 不返回逐文件明细」；**文件导入**为逐文件真实状态 | 契约扩展（可选） |
| 12 | Webtoon 断点像素级还原 | `SaveReadingProgressAsync.scrollOffsetY` 当前传 null，按页 id 保存 | 滚动百分比为 UI 近似（用于双模态显示），保存仍为真实 page id + 结果状态 | Core 进度语义确认 |
| 13 | 页图像显示 | `ReadPageImageAsync` 真实读取（`Host` 资源通道） | 无 Core/无图时显示占位框与页码（不伪造图片） | 运行时环境 |
| 14 | `MainWindow` 承载新外壳 | 由 **V11R-INT-1（DSH）** 切换 | 本任务提供可独立承载的 `AppShellV2` + 测试/证据入口；旧 `MainWindow.axaml` 未改 | V11R-INT-1 |
| 15 | 深链接生产入口 | 提供 `ShellDeepLink` 解析 + `NEWMANGA_V2_DEEPLINK` 环境钩子 | 证据/集成可用；正式 CLI/URL 参数由 INT-1 接入 | V11R-INT-1 |
| 16 | Studio / Theme Studio 的工作区注册与激活 | `IWorkspaceView` seam 已就绪；Studio（ui-studio）、Theme Studio（theme-studio）把实现注册进壳、TopBand 主题入口与 Ctrl+, 路由到表面栈、StatusBand Run 数据源，均属 **V11R-INT-0/INT-1** | 未注册时按契约显示「尚未接入」占位，不渲染伪造工作区 | V11R-INT-0（壳集成就绪） |

