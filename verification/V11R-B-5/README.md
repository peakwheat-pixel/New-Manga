# V11R-B-5 · 导出预检 + 导出历史/进度/取消 + 术语与约束

Owner: ui-studio · 基于 I2c 之后的 main；B-5 WIP 从 stash 选择性恢复（只取 B-5 文件，保留 I1/I2 修复）

## 实现
- 导出预检：真实 `GetTranslatedPageIdsAsync` + 当前 Run 投影计数（失败/阻塞）；范围（本章/选中 N 页，共享 `StudioSelection`）；格式 ZIP/PDF（PDF image_only / searchable_dual_layer）。
- stale 策略（已核实）：Core 接受 abort|continue_existing，但 `IHostController.StartExportAsync` 未暴露 stale_policy（Host 固定默认 abort）→ 仅 abort 可选，continue_existing 显示「未支持」并禁用。
- 未确认/过期计数：无预读命令（review 面属 F0-2；stale 由 Core 在 StartExport 内计算并返回 EXPORT_STALE 明细）→ 显示「—」并说明。
- 执行/进度/取消/历史：`StartExportAsync` → `GetExportSnapshotAsync`（可注入轮询 700ms）→ `CancelExportAsync`（终态停止、无残留）→ `GetExportHistoryAsync`；「打开导出目录」用 `RevealExportFolderAsync`；只显示文件名/SHA 前缀。
- 术语与约束（已核实）：无 glossary/DNT/constraint 命令 → 三页均 NOT_WIRED（AlertBanner+原因+禁用搜索/编辑，零伪造行）。
- 入口：Studio 头部「导出」「术语」→ `StudioToolsOverlay` 三页签。

## 证据
JSON：preflight / stale-policy / export-job / readonly / history / terms；截图：export-preflight / export-cancelled / export-history-terms / terms-not-wired（测试写 %TEMP%，curate 落仓）。

## NOT_RUN / 限制
- 术语/约束无真实命令（NOT_WIRED 呈现，不伪造）。
- continue_existing 未支持（Host 契约未暴露参数）。
- 过期/未确认不可预读（显示 —）。
