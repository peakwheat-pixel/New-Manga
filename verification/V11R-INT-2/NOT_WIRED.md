# V11R-INT-2 边界与未覆盖项

| # | 项 | 现状 | 说明 |
|---|---|---|---|
| 1 | Theme Studio 7 分区内容 | 仍由 V11R-C-2/INT-1 提供；本任务只修启动外观优先级与 Theme Studio 服务异步覆盖问题 | 表面占位/注册 seam 不变 |
| 2 | Studio Batch 的共享 Run poller | 仍属 INT-1 轮询统一范围 | 本任务未改 Batch |
| 3 | CLI 空格形式 `--key value` | 仍会被解析成 `"true"`；由 core-bridge 修复 | 本任务证据使用 `--key=value` 正确形式 |
| 4 | L4 实机启动矩阵全量复跑 | 本任务提供 v2 真实 sidecar 启动 + dark/light 真实窗口证据；7 组合矩阵由 Lead/INT-1 在合并后复跑 | 本任务不修改 L4 证据目录 |
| 5 | 安装包/发布产物启动 | 发布流程归 Lead | 本任务以 Debug 构建 + 真实 sidecar 取证 |
| 6 | 真实窗口截图 1600×1000 | 本机桌面宽度 1567，窗口被 Windows 钳制为 1567×1009 | headless 证据仍 1600×1000；环境限制已记录 |
| 7 | B-1 历史证据（StatusBand 截图） | B-1 证据是历史交付快照，未回改；本任务 INT-2 证据反映始终可见的状态栏 | 以本目录为准 |

## 已知非阻塞

- Host self-check 为 `Degraded`（core_protocol 2.3 < required_minor 3），但 `mode=ReadWrite`、无 `ReadOnlyReason`；Host 就绪判定为真实 Ready。
- 启动耗时约 1–3s（sidecar 冷启动），期间状态栏显示“Host 启动中…”，不阻塞窗口。
