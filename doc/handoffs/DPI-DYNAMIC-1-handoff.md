# Handoff — DPI-DYNAMIC-1

- 代码：`Program.cs` 显式 PerMonitorV2；`MainWindow.axaml.cs` RenderScaling 变化重排 + 日志。
- 诊断：`%APPDATA%\com.newmanga.desktop\logs\window-material.log` 会写 `scaling a -> b`。
- 回归：test.ps1 102/102、vitest 60/567、pytest 3F/2739P/9S。
- 未完成：真机拖动验证（4K 屏未连接，环境阻塞）；接回 4K@200% 后按卡片步骤复验。
- 集成：a6241b6c8。
