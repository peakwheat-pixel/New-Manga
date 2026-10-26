# MANUAL_VERIFY（实机人工核验清单）

> 状态：**NOT_RUN by agent**（最新版：2026-10-27，FINAL-VALIDATION-1 终验后发布件）。
> 以下 5 项需用户在真实 Windows 11 桌面会话执行，Agent 不得代填数字。
> 被测包：`NewManga-0.1.0-win-x64.zip`（base，97.75MB，Core sidecar 186.3MiB 内含、模型分离）或
> `NewManga-0.1.0-win-x64-models.zip`（含基础模型，690.94MB，开箱即可检测/OCR）。

| # | 项目 | 通过标准 | 用户记录 |
|---|---|---|---|
| 1 | Mica 取色 | Win11 设置/标题栏为 Mica 材质；Win10 为非透明回退 | 待填：OS build / 材质 / 截图 |
| 2 | DPR2 400% 像素 | 200% 缩放下 webtoon 400% 无插值模糊，边缘锐利 | 待填：截图 / DPI |
| 3 | 进程工作集峰值 | 阅读 4000×60000 webtoon 时 ≤1.5GB | 待填：任务管理器峰值 MB |
| 4 | 微软拼音 IME | 在书架搜索框连续输入 20 个汉字，无丢字/乱码 | 待填：输入内容 / 截图 |
| 5 | 沉浸阅读 Esc | 打开阅读器无边框全屏，Esc 立即退出并回到书架 | 待填：通过/失败 |

## 安装前置（终验已自动验证项）
- 解压 → `install.ps1 -PackageDir <解压目录>`；安装后 `app/core-sidecar/core_service.exe` 与 `host_bridge.exe` 必须存在
  （终验 install-smoke：sidecar_bundled=true，1954 文件/186.3MiB）。
- base 包不含模型：首次检测会以 typed `PROVIDER_NOT_CONFIGURED` 报错——把模型放到
  `%APPDATA%\com.newmanga.desktop\models\{detector,ocr}` 或改用 `-models` 包；属预期（模型分发策略见包内 `VERSION.json`）。
- 卸载：`uninstall.ps1 -InstallDir <安装目录>`；退出后不得残留 `NewManga.App` / `core_service` / `host_bridge` 进程。

## 采集方法
- 工作集：任务管理器 → 详细信息 → NewManga.App（+ core_service.exe）→ 内存峰值（MB）。
- Mica/像素：Win+Shift+S 截图附在 Review。
- IME：微软拼音输入法，逐字核对 20 字文本。
- Esc：阅读器内按 Esc，确认窗口关闭、无残留进程。
- 检测/OCR 实机抽查（如用 -models 包）：导入 1 页漫画 → 运行 → 确认区域生成与译文渲染；OCR 文本非空。
