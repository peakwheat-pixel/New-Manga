# 07 UI/UX 与真实运行观察

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**本轮 UI 构建/运行版本：** 2509db99057a8a57423b3cf3cf4490c558994b37
**阶段结论：** PARTIAL（AUDIT-09）。

## 实际观察

- 真实 Windows 会话打开 Legacy MainWindow 与 Current V2 shell；使用隔离空态/合成数据。Legacy 四页导航、设置空态、Reader fallback 与沉浸模式 H / Esc 键有实际观察。
- Fluent Host 在 115.344 秒观察期内保持 starting，相关控件 disabled；不记作可用。
- V2 Reader Retry 提示要求先选作品/章节，但可见 Library 仍显示合成 book/chapter 选择。此观察登记为 AUDIT-09-CAND-001，未判定严重级别或根因。

## NOT_RUN

未导入生成页面；文件选择器默认目录指向 Task workspace 之外，审计在选择文件前取消。没有运行真实页图阅读、翻页、双页对照、区域编辑/撤销、OCR/翻译、SFX 确认、glossary、Revision、导出、批处理取消/恢复、屏幕阅读器/高对比度、DPI/多显示器、长任务或错误恢复。没有改凭据或设置。

## 证据

- 逐步记录：reports/AUDIT-09-UI-UX-2026-11-13.md
- 截图与 runner log / JSON：audit/V1-FULL-AUDIT/screenshots/audit09-*.jpg、logs/audit09-ui-*.log、evidence/audit09-ui-*.json
- 静态 V2 surfaces：reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md

单一 shell 的空态和快捷键观察不等同完整 GUI 可用性或 accessibility PASS。
