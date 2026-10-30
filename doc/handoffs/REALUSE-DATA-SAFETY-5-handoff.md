# REALUSE-DATA-SAFETY-5 Handoff

- Task：[REALUSE-DATA-SAFETY-5](../tasks/REALUSE-DATA-SAFETY-5.md)
- 基线：\main a5c08bfb0\；交付 HEAD：\$head\；分支：\	ask/REALUSE-DATA-SAFETY-5- Worktree：\G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5\（保留）

## 核对结论（本批第一步，不是写代码）

B3 剩余 7 条 + B4 的编号。逐条核对后：

| 条目 | 判定 | 处理 |
|---|---|---|
| MA-14 | 仍成立 | 已修：\--page\/\--variant\ 加白名单（原本任意值静默忽略） |
| MA-15 | 部分成立 | 已修：sidecar 缺失消息补候选位置与修复步骤 |
| MA-16 | 仍成立 | 已修：README 0.1.0 → 0.1.1，删掉「9 套主题」与设备状态承诺 |
| MA-17 | 部分成立 | 已修：\HOST_READ_ONLY\/\HOST_NOT_READY\ 补可执行说明 |
| MA-18 | 仍成立 | 已修：Host 首次备份改用 \.sqlite-backup\，不再被 Core 的 \.nmbak\ 抑制 |
| MA-09 | 仍成立 | 未修：进度保存在，阅读器保存后/导入后的界面刷新未接 |
| MA-11 | 仍成立 | 未修：迁移代码在，真实根没跑；旧壳仍能写另一份库（策略需用户裁决） |
| MA-19 | 仍成立 | 未修：\derived/\ 仍是全尺寸副本（涉及资源通道设计） |
| MA-20 | 仍成立 | 脚本实际在 apps/desktop-avalonia/scripts/install.ps1，其 $DataRoot 默认真实 %APPDATA%；未修（部署侧决策） |

**MA-21 / MA-22 存在**（P4 卫生项）：MA-22 已修（grants 证据目录按最近 200 个修剪）；MA-21 记录为暂不修（wire 日志重复属可观测性优化，风险高于收益）。上一版 handoff 曾错误声称它们不存在，已更正。

## 证据

- \dotnet build -warnaserror\：0W/0E
- \dotnet test\：876 passed / 0 failed（App 389、Host 51）
- 新增用例：CLI 校验 13 个、Batch 只读/未就绪 2 个、首次备份命名 1 个
