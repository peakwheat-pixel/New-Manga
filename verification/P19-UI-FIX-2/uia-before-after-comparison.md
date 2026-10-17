# P19-UI-FIX-2：顶栏导入入口复验

## 结论

修复前的基线产品在本 worktree 重建后，顶栏 `导入作品` 已能打开同一 WebView 窗口内的 `ImportDialog`。UIA 可见状态说明“未开放：空书架暂不支持创建作品和章节，当前无法导入文件或文件夹。”，并能看到文件和文件夹入口均已禁用。AC1 的行为在基线已满足，因此本 Task 没有改生产组件；提交新增了顶栏、空态及详情侧栏入口的一致性回归测试，并保存固定产品的修复前/后真实 GUI 证据。

R4/R6 记录的是没有新建 `#32770`/系统文件选择器窗口。它准确说明没有系统选择器窗口；但顶栏入口在无可导入目标时走的是 WebView 内的可见原因提示，单独采样顶层窗口不能证明页面无反馈。

## GUI/UIA 对照

| 检查 | 修复前（基线） | 修复后（delivery head） |
|---|---|---|
| 应用 | `target/debug/m2rc1-desktop.exe`，SHA-256 `b9bb6ce419229f96d3de9c22ccd11fb889effc52eef03a54c136b5cacabbd63d` | 同路径重建，SHA-256 `de411ffefba9c494ee36c79c2e3efcadf7a1f189ae848ea62ffddca0217e58de` |
| 窗口（点击前） | `M2-RC1 resource channel runtime`，UIA 顶层窗口数 15 | `M2-RC1 resource channel runtime`，UIA 顶层窗口数 15 |
| 前端 bundle | `index-B2KOm56c.js` | `index-B2KOm56c.js`（同名内容 hash 资源；本 Task 未改生产组件） |
| 顶栏入口 | `导入作品`：`IsEnabled=True`、`IsOffscreen=False` | `导入作品`：`IsEnabled=True`、`IsOffscreen=False` |
| 点击结果 | 同一窗口内出现 `导入页面到章节` 与可见 `role=status` 原因说明 | 同一窗口内出现 `导入页面到章节` 与可见 `role=status` 原因说明 |
| 文件/文件夹入口 | 两按钮均 `IsEnabled=False`、`IsOffscreen=False` | 两按钮均 `IsEnabled=False`、`IsOffscreen=False` |
| 应用退出 | exit 0 | exit 0 |

两次 UIA 转储中的关键元素：

```text
Text|未开放：空书架暂不支持创建作品和章节，当前无法导入文件或文件夹。|IsEnabled=True|IsOffscreen=False
Button|📄 选择图片 / PDF 文件|IsEnabled=False|IsOffscreen=False
Button|📁 选择图片文件夹|IsEnabled=False|IsOffscreen=False
```

修复前记录：[`before-confirm/uia-run.log`](before-confirm/uia-run.log)、[`before-confirm/import-open.uia.txt`](before-confirm/import-open.uia.txt)。修复后记录：[`after/uia-run.log`](after/uia-run.log)、[`after/import-open.uia.txt`](after/import-open.uia.txt)。

## 导入入口清单

| 入口 | 现有行为 | 回归覆盖 |
|---|---|---|
| 书架顶栏 `导入作品` | 调用 `handleOpenImport(null)`；无目标章节时展示原因并禁用两个 picker | [`BookshelfPage.test.tsx`](../../apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx)：顶栏入口可见反馈；一致性测试 |
| 空书架 `导入作品` | 调用同一个 `handleOpenImport(null)`；显示相同空书架原因 | [`BookshelfPage.test.tsx`](../../apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx)：点击并核对相同原因及禁用状态 |
| 详情侧栏 `导入页面` | 调用 `handleOpenImport(null)`；有作品但无章节时显示无目标章节原因 | [`BookshelfPage.test.tsx`](../../apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx)：点击并核对原因及禁用状态 |
| `import-file-btn` / `import-folder-btn` | 无目标章节时禁用；有目标章节时通过现有 `LibraryClient` 打开原生 picker | [`BookshelfPage.test.tsx`](../../apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx) 与既有 `ImportDialog` file/folder IPC 测试 |

代码盘点未发现其它书架导入入口。过滤无结果态只提供清除过滤条件，不提供导入操作。

## 隔离与源数据保护

UIA 应用从隔离副本启动：只复制 `%APPDATA%\com.newmanga.m2rc1.desktop\catalog` 和 `data` 到 `apps/desktop/src-tauri/target/p19-ui-fix-2-isolation-20261017`，新建空 `derived`、`managed`、profile、local、temp 与 WebView 目录。Namespace identity 只在副本上重绑。原始 `catalog`（1 个文件，24,576 bytes）及 `data`（2 个文件，311,297 bytes）前后聚合 SHA-256 未变；详情见 [`appdata-source-preservation-check.json`](appdata-source-preservation-check.json)。

最终 UIA 构建顺序和二进制校验见 [`frontend-npm-build-final.log`](frontend-npm-build-final.log)、[`sidecar-build-final.log`](sidecar-build-final.log)、[`cargo-build-final.log`](cargo-build-final.log) 与 [`sidecar-resource-hash-final.json`](sidecar-resource-hash-final.json)。五个 sidecar executable 的 bundle/resource SHA-256 均一致。
