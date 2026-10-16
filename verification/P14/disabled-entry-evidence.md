# P14 禁用入口文本证据

依据 `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md` §7；行为断言见 `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx` 中“renders every §7 disabled entrance…”与缩略图测试。测试枚举下表每个 `data-testid`，逐个断言入口存在且按钮 `disabled=true`、原因文本可见且非空、`aria-describedby` 指向该原因；G18 当前 Run 页缩略图另在 Run projection 存在时断言 disabled 与原因文本。该证据证明 DOM 中可发现、不可操作且原因可理解，不是 GUI e2e 截图或真实窗口交互验证。

| §7 缺口 | 可见入口（`data-testid`） | 人类可理解的禁用原因 | 证据/附加断言 |
|---|---|---|---|
| G9 保存人工译文 | `gap-g9-save-manual-translation`（Region Inspector） | `SaveManualTranslation` 写入接口尚未冻结。 | 通用禁用入口 DOM 断言 |
| G10 新建 Region | `gap-g10-create-region`（工具栏） | 等待 `CreateRegion` 能力接入。 | 通用禁用入口 DOM 断言 |
| G10 删除 Region | `gap-g10-delete-region`（工具栏） | 等待 `DeleteRegion` 能力接入。 | 通用禁用入口 DOM 断言 |
| G11 Region 几何编辑 | `gap-g11-region-geometry`（工具栏） | 移动、缩放、合并、拆分与顺序写入 wire 尚未冻结。 | 通用禁用入口 DOM 断言 |
| G12 Lock 设置/解除 | `gap-g12-region-lock`（Region Inspector） | Lock 写入接口尚未冻结；当前锁态只读显示。 | 通用禁用入口 DOM 断言 |
| G13 Revision pin | `gap-g13-revision-pin`（Region Inspector） | Revision pin 写入接口尚未冻结；历史固定状态只读显示。 | 通用禁用入口 DOM 断言 |
| G14 页序拖拽重排 | `gap-g14-page-order`（PageList） | 页序写入 wire 尚未冻结，页面顺序保持 Core 投影结果。 | 通用禁用入口 DOM 断言 |
| G15 Run 发现/队列/中断处置 | `gap-g15-run-discovery`（固定 TaskProgressPanel） | Core 尚无 `ListRuns` 查询；仅能查看本次工作台明确启动的 Run。 | 通用禁用入口 DOM 断言；测试另断言未调用任何 `ListRuns` 命令 |
| G16 Core 可用性 | `gap-g16-core-availability`（工具栏） | Core 可用性查询/事件 wire 尚未冻结；此处不推断运行状态。 | 通用禁用入口 DOM 断言 |
| G18 PageList 缩略图 | `gap-g18-page-thumbnails`（PageList） | 只有原图资源通道，低清缩略图能力尚未接入。 | 通用禁用入口 DOM 断言 |
| G18 当前 Run 页缩略图 | `gap-g18-current-page-thumbnail`（TaskProgressPanel 有 Run projection 时） | 低清预览/缩略图通道尚未接入，不把原图当缩略图加载。 | 单独断言 Run projection 存在时仍 `disabled=true` 且原因文本可见 |
| G26 导入细分进度 | `gap-g26-import-progress`（工具栏） | 当前只返回同步导入结果，细分进度 snapshot 尚未冻结。 | 通用禁用入口 DOM 断言 |

G15 入口保持禁用；已知 `run_id` 的快照/投影能力继续只用于本次工作台启动的 Run，前端不构造列表、不做本地聚合。
