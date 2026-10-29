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

## 2026-10-29 更新（LEGACY-SHELL-ARCHIVE-1）

- **构建路径已解耦**：sidecar 构建输出从 `apps/desktop/src-tauri/target/` 迁到 `apps/desktop-avalonia/build/sidecar/`
  （`packaging/m2ac5/build_sidecar.ps1`、`package.ps1`、README、公开 CI workflow 已同步）。本目录不再参与任何构建/发布链路。
- **可移动部分已归档**：`src/ui`（PySide6/QML）、`tests/ui_shell` 与依赖它们的旧壳测试/打包文件已移入
  `archive/history/legacy-shell/`（0 条 evidence pin，已核实）。
- **本目录保持原位冻结**：42 条历史 done Task 的 Canonical Evidence pin 直接引用 `apps/desktop/src-tauri/src/**`
  与 `apps/desktop/frontend/src/**`；按治理「仍被 evidence pin 引用的文件留在原路径」不得移动。彻底移动需
  先做历史 pin 迁移方案（不在本卡范围）。