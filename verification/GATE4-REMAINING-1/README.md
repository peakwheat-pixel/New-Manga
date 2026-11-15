# GATE4-REMAINING-1：条件 4 三项残留的处置

基线 `40c63b6ec`。**先分类，不一律标 blocked**。

## 1. `reader` 页 —— **已实测取证，结论 NEEDS_INTERACTION**（不是猜的）

### 1.1 先把 `AppOptions` 的全部参数读出来（我曾因不知道 `--exit-after` 白卡两轮）

`AppOptions.cs` 共 364 行，全部 `--xxx` 参数：`--data-root`、`--log-dir`、`--sidecar-dir`、
`--mutex-name`、`--theme-home`、`--frontend`、`--theme`、`--theme-id`、`--shell`、`--variant`、
`--page`、`--exit-after`、`--width`、`--height`、`--presentation-host`、`--legacy-shell-check`、
`--demo-write`。

**没有任何"注入按键"或"启动即打开阅读器窗口"的参数。**

`AllowedStartupPages` = `bookshelf / library / reader / workbench / studio / settings / console`
—— **`reader` 确实是允许值**。

### 1.2 实测（`--page=reader` + `--exit-after=15000`，无交互，退出码 0）

**截图证据**：`page-reader-startup.png`（1416×939，窗口标题 "New Manga"）。

**界面上显示的是「资料柜」页面**，不是阅读器：

- 标签栏：`资料柜 1 | 工位 2 | 控制台 3`
- 标题：`资料柜 0/0 作品`
- 中央：`书架还是空的` / `新建作品，选择章节后导入页面；所有读写都经 Core`
- 右侧：`选择一本作品`

### 1.3 为什么这是决定性的

`startup.log` 里**确实出现了** `[Binding] ... CurrentPage.Image` ——
那是 **`ReaderOverlay` 的绑定**，说明 **overlay 控件被构建了**；
但**截图证明它不可见**（被 Library 空间覆盖）。

⇒ **`--page=reader` 只切空间（`SpaceId.Library`），不打开沉浸式阅读器。**
要看到阅读器必须**按 F11**，而 F11 需要**真实交互**（`GATE4-READER-PAGE-1` 已证：
非交互进程 `SetForegroundWindow` 失败、`keybd_event` 到不了 shell）。

**⇒ 结论：`NEEDS_INTERACTION`，且这是实测结论而非推断。**

## 2. sidecar 缺 `yolo11s-seg.onnx` —— **BLOCKED（需用户提供）**

- **缺什么**：`apps/desktop-avalonia/build/sidecar/**/yolo11s-seg.onnx`（分割模型权重）。
- **谁能提供**：**用户**（这是训练产物，不是能从代码生成的东西）。
- **现状**：安装包 stage 里 `models_bundled: false` 曾被误写，实际 bundles 3 个 ONNX 共 **632,552,582 B**；
  但 `yolo11s-seg.onnx` **不在其中**。
- **提供后怎么验证**：把它放进 sidecar 模型目录，跑 `resolve_page_resource` 的检测路径，
  断言返回真实 mask 而非降级结果；并在安装矩阵里复核 `models_bundled` 明细。

## 3. installer unsigned —— **BLOCKED（需用户提供证书）**

- **缺什么**：代码签名证书（OV/EV，含私钥）+ 时间戳服务访问。
- **谁能提供**：**用户**。
- **提供后怎么验证**：`signtool sign /fd sha256 /tr <ts> installer.exe` 后
  `Get-AuthenticodeSignature` 应为 `Valid`；安装时 SmartScreen 不再拦。
- **替代口径（若用户接受）**：明确记录"内测包不签名"，并在 Gate 条件 4 里标注为**已知限制**。

## 4. 三项汇总

| 项 | 状态 | 缺什么 | 谁能提供 |
|---|---|---|---|
| `reader` 页 | **NEEDS_INTERACTION**（已实测） | 真实按键（F11） | 只能人工操作 |
| `yolo11s-seg.onnx` | **BLOCKED** | 模型权重文件 | **用户** |
| installer 签名 | **BLOCKED** | 代码签名证书 | **用户** |
