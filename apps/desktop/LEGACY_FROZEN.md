# LEGACY FROZEN — 旧壳（Tauri + React + WebView2）

Status: **FROZEN / HISTORICAL**（2026-10-27，AD-002 S5-C）

本目录是 AD-001 时代的桌面壳（Rust host + React UI + WebView2）。自 AD-002 起，产品前端为
`apps/desktop-avalonia/`（C#/.NET 9 + Avalonia 11），本目录**不再构建、不再发布、不再修复**。

## 为什么不整体移动

治理规则要求「仍被当前 Gate、Task、Review、evidence/source pin 引用的文件留在原路径」。
历史 Task 卡（UIUX-V2-*、SETTINGS-OPEN-*、PLUGIN-*、DISPLAY-PERF-* 等）与证据 pin 大量引用
`apps/desktop/**` 路径；整体移动到 `archive/` 会使这些引用失效。因此采取**原位冻结**：
文件保留、从构建/发布链路移除、文档指针改指新壳。彻底归档需单独授权 + 完整引用迁移清单。

## 新壳入口

- `apps/desktop-avalonia/`（四页 + 主题中心 + TileChannel + 打包脚本）
- 契约：`apps/desktop-avalonia/docs/TILE-CHANNEL-CONTRACT-V1.md`
- 发布件：`apps/desktop-avalonia/scripts/package.ps1`（22.9MB zip）
