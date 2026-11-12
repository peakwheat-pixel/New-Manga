# AUDIT-04 OCR 与文本区域检测

日期：2026-11-13
阶段结果：PARTIAL（静态链路与合成 adapter/Core 回归完成；真实模型、标注准确率与桌面 GUI 未验证）
产品基线：10e4ee013835605800d3830fb960ae8d3aa04167
定向测试生成 HEAD：c20e819009a810ae3828aef7eb8644eb9a3eae80

## 结论摘要

当前 Python Core 有独立的文本检测与 OCR Provider。默认检测链路选择 Manga RT-DETR-v2 ONNX；可选 docTR 与 torch 路径由配置选取，模型文件在本地缺失或校验失败时按 typed error fail closed。OCR 默认注册日文 Manga OCR ONNX recognition-only provider，另注册韩文 PaddleOCR provider；Vision OCR 是显式配置的远端 fallback。模型路径、hash 校验、ORT execution-provider policy、页面/切片坐标和 typed error 传播具备合成单测。

本轮运行 providers 组 175 passed / EXIT 0，Core detect 组 40 passed / EXIT 0；未发生 skip。日文与韩文测试使用 fake engine、伪造 tokens 或 Paddle 输出，不构成识别准确率测试。未加载真实模型权重、未调用网络/Vision API、未创建人工 GT。真实字形、竖排阅读顺序、艺术字、小字漏检/误检、真实 CPU 推理、设备释放、长时中断恢复和 Avalonia GUI 像素坐标均未得到实测结论。因此专项为 PARTIAL，不声明 OCR 或检测质量达标。

## 实际链路

- 检测组装：`src/bootstrap/core_assembly.py` 默认 `NEWMANGA_DETECTOR_BACKEND=manga`，选择 Manga ONNX 权重；`manga-onnx` 指向同一路径，`torch` 与 `doctr` 为显式替代项。环境覆盖、data-root、frozen bundle 的权重查找顺序与缺失诊断由 assembly helper 管理。
- OCR Provider 注册：`src/infrastructure/providers/runtime.py` 默认 `NEWMANGA_OCR_BACKEND=onnx`，注册 Japanese `MangaOcrOnnxProvider`；`NEWMANGA_OCR_BACKEND=torch` 是显式可选路径。`PaddleKoreanOcrProvider` 单独注册为韩文 OCR，Vision provider 依赖配置与 network gate。
- Core 服务：`core_service.handle_detect` 解码受限 PNG/JPEG 输入后调用与 pipeline 共用的 detector instance，输出 provider candidate 和 coordinate space；Provider 输出不创建业务 Region ID。Run handlers 负责 provider 绑定、执行、typed error 与文本写入。
- Avalonia 静态入口：V2 Studio 的 `StudioBatchViewModel` 将重 OCR操作映射为 `reocr_single` / `reocr_selected` / `reocr_all`，经 `HostController.StartRunAsync` 与 `library_start_run` IPC 提交。此次只核对了静态接线；未启动 Avalonia 会话或确认屏幕缩放后的选区/区域坐标。

## 验证矩阵

| 原始检查项 | 结果 | 证据和边界 |
|---|---|---|
| 检测模型选择 | PARTIAL（静态+合成） | `test_detector_assembly.py`、`test_detector_weights_lookup.py` 与 ONNX Provider 单测覆盖选路、查找和缺失权重；没有真实模型装载。 |
| 日文 OCR | PARTIAL（fake engine） | `test_ocr_manga_onnx.py` 验证 request 限制、预处理/解码循环、special-token 过滤和返回 `こんにちは`；字符由 fake engine/decoder 提供。 |
| 韩文 OCR | PARTIAL（fake Paddle） | `test_ocr_local.py` 验证 PaddleOCR 3.x/2.x payload、Hangul 文本/分数/多边形解析与图像 ndarray 输入；没有真实 Paddle inference。 |
| 区域坐标与缩放回映 | PASS（合成几何） | `test_detection_manga_onnx.py` 检查 640 输入的 page-size 坐标回映；`test_detection_doctr.py` 检查 page-bound clipping；`test_detection_manga.py` 检查 tiled Webtoon box 加 tile origin、裁切与 page-global 输出。 |
| 横排/竖排 | PARTIAL（契约） | OCR request 校验 direction 且 result 保留 direction；未测模型实际阅读顺序、竖排日文列序或横排混排准确性。 |
| 小字体与艺术字 | NOT_RUN | 未运行真实权重，也没有人工标注对照样本。 |
| 重叠区域 | PARTIAL（合成规则） | tiled detector 有跨切片重复框 NMS 单测；不证明模型对真实重叠文字/气泡的区分。 |
| 漏检/误检 | NOT_RUN（质量） | 合成 logits/box 测试覆盖阈值与类别筛选；没有真实模型输出和人工 GT，不能计算 precision/recall 或错误数。 |
| CPU 推理 | PARTIAL（执行策略） | `test_onnx_sessions.py` 检查显式 CPU、auto→CPU fallback 及 EP 静默降级 fail-closed；ORT session 由 fake runtime 提供，不是 CPU 模型推理。 |
| 模型初始化与释放 | PARTIAL | Provider 懒加载并缓存 engine/session，测试覆盖 engine 初始化前的 missing/hash failure；此批没有真实权重初始化、session teardown 或长时内存观察。 |
| 模型缺失处理 | PASS（合成） | Detector/OCR 适配器 missing weights 测试返回 `PROVIDER_NOT_CONFIGURED`；hash mismatch fail-closed；不触发下载。 |
| 推理中断与恢复 | PARTIAL（typed-path） | Core detect 测试覆盖输入错误和 Provider typed errors 的响应；没有真实 ONNX/Paddle native exception、进程中断后模型重载或 GUI 恢复演练。 |

## 命令与结果

`audit_runner.py audit04-ocr-detection` 在 HEAD `c20e819009a810ae3828aef7eb8644eb9a3eae80` 分两组执行，避免不同测试目录同名 `conftest.py` 冲突：

- Providers：175 passed，0 skipped，EXIT 0。包含 docTR/Manga/ONNX detector 单测、日/韩 OCR adapter、Detect handler、权重选择和 `test_onnx_sessions.py`；排除 `test_detection_doctr_real.py`、`test_detection_manga_real.py`。
- Core detect：40 passed，0 skipped，EXIT 0。覆盖 `core.detect` 输入上限、解码/尺寸错误、候选透传、Provider 错误分类与无 detector fail-closed。
- 两组日志/JSON 分别记录 Python 3.14 interpreter、argv、cwd、generated HEAD、UTC、elapsed 与 EXIT。pytest cache、basetemp 和 Core data root 均位于 `New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/`。
- 最终静态范围捕获 `audit04-static-20261112T203819Z`：generated HEAD=`c20e819009a810ae3828aef7eb8644eb9a3eae80`；`src/apps/tests` 基线 diff EXIT 0；`git diff --check` EXIT 0；采集时 21 条工作树路径全部位于 Task allowed paths，out-of-scope=0。base→HEAD 的 305 条历史变更中有 14 条继承自 FEA-11 HOST-AUTH-4，不作为本 Task 工作树编辑。

## 限制与后续

- `tests/providers/test_detection_doctr_real.py` 与 `test_detection_manga_real.py` 未运行，避免依赖或访问真实模型资产；OCR 没有本轮可用的日/韩人工 GT 集。
- 没有启动安装包、真实 GUI、真实模型、真实素材或远端 Vision API。此前 Avalonia .NET TestHost 的 8/8 runner `BLOCKED-TESTHOST-ACCESS`、TRX 0 tests 是既有环境限制；本轮未重试。
- 现有测试支持 adapter/API 行为与坐标算子，不支持真实识别率、模型资源回收或屏幕缩放交互结论。发现严重度由 ZCode 独立裁决；本轮不新建 issue ID、不覆盖既有严重度，也不修改产品源代码。
- AUDIT-04 保持 PARTIAL，不影响全 Task AC2/AC3/AC4 的 PARTIAL、Release Gate BLOCKED 或 Task `in_progress`。下一项依 DAG 推进 AUDIT-07。
