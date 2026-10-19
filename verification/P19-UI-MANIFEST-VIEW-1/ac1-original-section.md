# AC1 — P19-UI-FIX-1 的 Resource Manifest 节：改前 / 改后

## 改前（原文，逐字保留）

```markdown
见 [`resource-manifest.json`](../../verification/P19-UI-FIX-1/resource-manifest.json)。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖；`build_sidecar.ps1 -Force` 清理的外部 PyInstaller 缓存已在资源清单与 Handoff 风险中明确登记。
```

## 改后

```markdown
外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖；`build_sidecar.ps1 -Force` 清理的外部 PyInstaller 缓存已在资源清单与 Handoff 风险中明确登记。
```

## 源 JSON 指纹（改前，且全程未变）

```
b0772d93ab8ed9182497a43e0761f0d4ccc5560768f806ba86eb8048905c4dc2
```

## 保留了什么

路径改为反引号包裹的仓库相对路径（`verification/P19-UI-FIX-1/resource-manifest.json`），
去掉了 Markdown 链接形式（检查器只匹配反引号内无空格的 `*.json`，链接形式会被匹配成裸文件名）。
**原散文中的处置事实逐字保留**：worktree / 构建产物 / 隔离数据 / 源数据均保留、删除 0 项、
6 个旧成功运行日志仅在证据目录内改名以防覆盖。
