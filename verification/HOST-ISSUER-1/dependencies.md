# 依赖变更

新增 direct dependency：`tauri-plugin-dialog = "2"`；`Cargo.lock` 锁定 `tauri-plugin-dialog 2.8.3`。理由：本 Task 需要 Windows OS 原生文件选择、文件夹选择和保存目标对话框，现有 Tauri host 未提供这些接口；Rust 侧官方 dialog plugin 是最小可用入口。

锁文件新增/更新的相关官方 Tauri 传递依赖包括 `tauri-plugin 2.7.2`、`tauri-plugin-fs 2.7.1` 与 `rfd 0.16.0`。没有新增 JavaScript API 或 capability permission；前端不能直接调用 dialog/fs plugin。Host 只使用 Rust `DialogExt`，选择结果路径留在 Rust 内部。

安全影响：native picker 把用户选择限制在单个文件、单个文件夹或单个保存目标；文件/目录 scope 与后续签名 grant 一致。没有给 WebView 授予任意文件系统访问权，也未放宽现有 Tauri command permission。版本与传递依赖以 `apps/desktop/src-tauri/Cargo.lock` 为准。
