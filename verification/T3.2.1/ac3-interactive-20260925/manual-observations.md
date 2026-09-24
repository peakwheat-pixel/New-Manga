# AC3 手动交互尝试：导入受阻与 UI 观察

日期：2026-09-25（Asia/Shanghai）

执行方式：用户在全新 Windows Sandbox 中手动操作固定 Build 3；正常启动 GUI，未传入 `--smoke-test`。

结论：**AC3=`BLOCKED`，仍是发布阻断项。** 程序可启动并退出，但主流程在图片导入入口受阻，未完成导入、阅读与导出闭环。

## 固定对象与原始证据

- 源树：`agent/antigravity/T3.2.1-repair-12`，HEAD `8738c41d7215920935e6fa067d3740e69280cdc6`；构建日志绑定到该 HEAD。
- Build 3：Sandbox 中的 `NewManga.exe` SHA-256 为
  `95f9ba68086087c9999804fd0cd2bd4e5f772de350c74a22f2eaf3e329772c10`。
- Sandbox `manual-baseline.log` 原样报告 `OS=Windows 10 Enterprise`、`OS_BUILD=26100`；
  这与先前记录的 Windows 11 标签不一致，本报告不根据 build number 推断版本。
- 启动记录：[`manual-baseline.log`](manual-baseline.log)、[`manual-run-01.process.log`](manual-run-01.process.log)。GUI 正常启动（无参数），进程 `EXIT_CODE=0`。
- 原始 stderr：[`manual-run-01.stderr.log`](manual-run-01.stderr.log)。其中有 31 次
  `BookshelfView.qml:23: TypeError: Cannot read property 'currentChapterId' of undefined`。
- 构建来源：[`build3-fixed-cwd.raw.log`](build3-fixed-cwd.raw.log)、
  [`build-fixed-cwd-binding.log`](build-fixed-cwd-binding.log) 与
  [`build3-fixed-cwd-artifact-manifest.sha256`](build3-fixed-cwd-artifact-manifest.sha256)。
- 6 张由用户提供的原始屏幕截图已复制到 [`screenshots/`](screenshots/)；文件名按操作顺序编号，SHA-256 如下：

| 文件 | SHA-256 |
|---|---|
| `01-empty-shelf.png` | `7db9fce001394d69d68a18baab0a2d710fd60b9724b79a1d13b3f8f127b4694e` |
| `02-create-book-dialog.png` | `664f2a8f023ff26259abc0ccab07bf3ed14dd3c65f6e529f8c48b21b6f0c1626` |
| `03-book-created.png` | `75d4c8780f70c4c9037aa068b04ad54ad755144bdf6276f535135dc1fa20f52d` |
| `04-chapter-created.png` | `2ca79bcf5ececc04d1a592a2b3312453068503b3cb77acb83b024d884523f4b9` |
| `05-workbench-no-pages.png` | `d1835a44119f132688ba7f2023a0ec6657097723f635a8a149cc74f3e665feb9` |
| `06-reader-no-chapter.png` | `9659b54b907821493d69e3d349c5ee555b6b9205eab5b545d339909bf8ec5997` |

对照命令：

```powershell
git diff --exit-code 188d72a9d144b8cab16f77757abc46318ac8e5e6 8738c41d7215920935e6fa067d3740e69280cdc6 -- src packaging tests
```

结果：exit 0。测试包来源与 Codex 候选在产品代码、打包文件及打包测试路径上相同；此对照不等于 AC3 通过。

## 观察与判定

1. **图片导入无法继续（已观察，AC3 阻断）**：空书架截图中“导入”按钮可见；用户后续建立了作品与空章节，但 Workbench 仍显示无 Page。构建包 stderr 记录上述 `currentChapterId` TypeError。对应源代码在
   [`BookshelfView.qml`](../../../src/ui/qml/bookshelf/BookshelfView.qml) 第 23 行通过
   `detailArea.chapters` 读取章节 ID；`chapters` 是 `BookDetailPanel.qml` 内部 ID，并未作为外部属性暴露。现有证据支持这是导入回调的 QML 组件作用域接线错误，导致文件选择器无法可靠打开。该代码诊断尚待独立实现与复审。
2. **按钮文字/底色难辨（观察到，未量化）**：截图中多个按钮的浅色文字与浅色按钮底色区分度很低，禁用状态尤其难辨。本次未测量像素对比度，也未据此判断符合任何无障碍阈值；须在后续 UI 修复中检查全局 enabled/disabled/focus 状态。
3. **导出未完成有效测试**：Reader 截图明确显示“尚未选择阅读章节”；`ReaderView.qml` 将“导出”按钮绑定为 `enabled: active`，而 `active` 要求已有阅读章节。因此截图中的按钮为禁用态，点击无响应与当前状态一致。由于没有导入页面、也没有在 Reader 选择有效章节，本次**没有验证导出对话框或导出文件是否正常**。

## AC3 状态

将前一检查点的 `NOT_RUN` 更新为 **`BLOCKED`**：固定包已启动并进入真实 UI 操作，但图片导入链路阻断主流程。不得记为 `PASS`。完成修复、独立 Review 与同一固定包口径下的完整重新测试前，AC3 继续阻断 T3.2.1 Release Gate；所有相关分支仍禁止合并至 `master`。
