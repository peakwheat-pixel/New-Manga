# Studio I2c DEVIATIONS（登记，不在本卡自行重构）

| 项 | 状态 | 说明 |
|---|---|---|
| `StudioStopConfirmModal` 与壳层 `ConfirmModal` 同构重复 | 登记待 INT-1 | 壳层可视 Modal 在 `AppShellV2` 内部，跨区域不可直接复用；语义一致（默认取消/影响面/Esc/聚焦），INT-1 统一壳层模态时删除本实现 |
| `StudioStates.NoDataGlyph = "–"` | 登记 | 与 DS `Skipped=–` 同形但语义为“无投影数据”；DS 若提供 noData 符号则替换 |
| 图标集 | 部分上收 | 状态符号已全部来自 `StatusCatalog/NmStatusSymbols`；`Nm.Icon.*` 图形图标（HUD/页签）仍为字母/汉字占位，待 DS 图标集消费（INT-1/后续卡） |
| 保留的 Studio 样式类 `studio-state-*` | 合规 | 由 `StatusCatalog.ClassName` 派生，颜色 token 来自 `Nm.Color.Status.*`，未自造色值 |
| `StudioMetrics` 回退值（1600/1280/1024/11） | 合规 | 仅 design-time 无资源时回退；运行时读取 `Nm.Size.Breakpoint.*` / `Nm.FontSize.Xs` 资源键 |
