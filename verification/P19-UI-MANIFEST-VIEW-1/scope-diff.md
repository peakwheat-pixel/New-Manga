# AC5 — 改动面

本 Task 只改一个文件的正文一句话：

```diff
--- a/doc/tasks/P19-UI-FIX-1.md
+++ b/doc/tasks/P19-UI-FIX-1.md
@@ -(Resource Manifest 节)
-见 `[esource-manifest.json](../../verification/P19-UI-FIX-1/resource-manifest.json)`。worktree、构建产物、...
+外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、...
```

## 未触及

- `verification/P19-UI-FIX-1/resource-manifest.json`（源 JSON）
- `verification/P19-UI-FIX-1/` 下任何证据文件
- `tools/governance/`
- 任何 pin、Canonical Evidence 表、资源

## 为什么只有一句

原节剩余全部文字逐字保留：保留声明、删除 0 项、6 个日志改名、
`build_sidecar.ps1 -Force` 清理的 PyInstaller 缓存登记。节字节 353 → 332。
