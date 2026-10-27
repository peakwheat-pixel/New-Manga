# RUN-OCR-DIAG-1 报告：Run 链 OCR / detect 失败诊断（只诊断，不改 Core）

- Task：`RUN-OCR-DIAG-1`（team task-33，kind=research，base `9f58b4c1d`）
- 诊断对象：models 包冻结 sidecar
  `...\FINAL-VALIDATION-1\out\NewManga-0.1.0-win-x64-models\app\core-sidecar\core_service.exe`
  `sha256 = 2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b`
  （**注意**：与 AC11 无标签副本 `e0a1eff8…f6f14bc0` 不是同一构建，本报告的结论只对 models 包这份成立）
- 数据根：`BOOK-FIXTURE-1/isolated-data` 的**私有副本**（`task-envs/RUN-OCR-DIAG-1/data-root-*`，
  重建 catalog 绑定）；原件与真实 `%APPDATA%` 均未触碰
- 硬规则遵守：只诊断；未改 Python Core 语义、产品源码、协议、Host 契约、旧壳；未 push/gc/prune；未伪造复现

## 0. 结论

| AC | 判定 | 一句话 |
|---|---|---|
| AC1 最小复现 | **MET** | 单页（page 1）与整书 8 页都稳定复现：`detect` completed → `ocr` **`PROVIDER_NOT_CONFIGURED`**（`completed_with_failures`） |
| AC2 OCR 根因 | **MET** | **不是**模型缺失、**不是**EP 配置、**不是**输入不符；是 **Core 侧 step provider binding 未配置**：`pipeline_defaults.provider_bindings_json = '{}'`，`handlers._chain()` 取不到 `ocr` 键 → 抛 `ProviderNotConfigured("no provider binding configured for step 'ocr'")`。加一个 StartRun 覆盖 `overrides.provider_bindings={"ocr":"manga-ocr"}` 后，**同一请求 OCR 步骤直接 completed**（manga-ocr / local-manga-ocr-onnx / cpu / 1 行 / 13 个 region 全部有 text） |
| AC3 detect INVALID_INPUT | **MET** | 页 4–8 的 `INVALID_INPUT` = `detector returned no candidates`（**检测器正常返回 0 候选**，不是解码/尺寸/格式失败）。页 4–8 是**无文字全彩插画页**（E20 封面/跨页图），8 页 `core.detect` 实测候选数 = 13/6/7/**0/0/0/0/0** |
| AC4 建议 | **MET** | 5 条按最小改动排序的建议 + 影响面见 §5；顺带发现**第 2 个阻断点**：`color` 步骤因 `_StubStyleAnalyzer` 缺 `analyze` 必失败 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff 见本报告 |

**两条根因一句话**：
1. **OCR**：缺 **provider binding**（配置缺口，不是模型缺口）。模型包里的 OCR 权重与 provider 的 SHA-256 pin **逐字节一致**。
2. **detect 页 4–8**：检测器对**无文字页**返回 0 候选，而 Core 把"0 候选"映射成 `INVALID_INPUT`（把"无事可做"当成"输入非法"）。

---

## 1. AC1 最小复现

### 1.1 复现步骤（可重跑）

```powershell
$E = "G:\CODEX\New Manga.workspace\task-envs\RUN-OCR-DIAG-1"
# 整书 8 页（等价 RUN-EXPORT-E2E-1 的现场）
python "$E\scripts\run_diag.py" --variant models --command translate_untranslated `
  --scope book --tag models-book --out evidence/diag-models-book.json
# 单页最小复现（page 1）
python "$E\scripts\run_diag.py" --variant models --command translate_untranslated `
  --scope page --page-index 0 --tag page0 --out evidence/diag-page0.json
```

- 请求帧（application 通道 2.3）：`{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"diag-StartRun-00N","command":"StartRun","payload":{"command":"translate_untranslated","scope":{"kind":"book","book_id":"14340ddad0ed472fbe687fe12340c5d8"},"overrides":{},"idempotency_key":"…"}}`
- 环境：`NEWMANGA_DATA_ROOT=<私有副本>`、`M2RC1_DERIVED_ROOT/M2RC2_CATALOG_DB/M2RC1_MANAGED_ROOT` 全部指向该副本；
  **未设置** `NEWMANGA_MANGA_OCR_WEIGHTS` / `NEWMANGA_OCR_DEVICE` / `NEWMANGA_OCR_BACKEND` / `NEWMANGA_DETECTOR_WEIGHTS`（全用内置默认）
- EP：detect 步骤实测 `inference_ep = "DmlExecutionProvider,CPUExecutionProvider"`（models 包 ORT 为 `onnxruntime-directml`，含 `DirectML.dll` 18.5 MB）；OCR 侧 provider 默认 `device="cpu"`
- 模型路径（models 包内）：`app/core-sidecar/models/detector/rtdetr-v2-fixed.onnx`（171,618,071 B）、
  `app/core-sidecar/models/ocr/manga-ocr-onnx/{encoder_model.onnx,decoder_model.onnx,vocab.txt,generation_config.json,...}`

### 1.2 复现结果（8 页整书）

| 页 | 文件 | 终态 | page-level error |
|---|---|---|---|
| 1 | E04P02.jpg | failed | **PROVIDER_NOT_CONFIGURED** |
| 2 | E04P03.jpg | failed | **PROVIDER_NOT_CONFIGURED** |
| 3 | E04P06.jpg | failed | **PROVIDER_NOT_CONFIGURED** |
| 4 | E20P01.jpg | failed | INVALID_INPUT |
| 5 | E20P02.jpg | failed | INVALID_INPUT |
| 6 | E20P03.jpg | failed | INVALID_INPUT |
| 7 | E20P04.jpg | failed | INVALID_INPUT |
| 8 | E20P05.jpg | failed | INVALID_INPUT |

run 终态 `completed_with_failures`，与 RUN-EXPORT-E2E-1 观测一致（`evidence/probe-models-book.json`）。
**关键**：`step_runs.error_detail` 直接给出机制（RUN-EXPORT-E2E-1 当时没抓到这一层）：

| step | status | error_code | error_detail |
|---|---|---|---|
| detect (p1/p2/p3) | completed | — | — （真实 ONNX 检测，`candidate_count` 13/6/7） |
| **ocr (p1/p2/p3)** | **failed** | **PROVIDER_NOT_CONFIGURED** | **`no provider binding configured for step 'ocr' (stage=ocr)`** |
| detect (p4–p8) | **failed** | **INVALID_INPUT** | **`detector returned no candidates for page '<id>' (stage=detect)`** |

---

## 2. AC2 OCR 根因（逐项判定）

### 2.1 判定结论：**(c) Core 侧 step provider binding 未配置** —— 四项候选逐条排查如下

| 候选原因 | 判定 | 可判定证据 |
|---|---|---|
| (a) 模型包缺 OCR 模型/配置 | **排除** | ① 文件全在：`models/ocr/manga-ocr-onnx/{encoder,decoder,config,generation_config,preprocessor,vocab,…}`；② **三个受校验文件的 SHA-256 与 provider 内置 pin 逐字节一致**：encoder `15fa8155…def85f`、decoder `ef776526…61f5e8`、vocab `5cb5c558…a36a3`；③ **stderr 里没有任何 OCR weights 警告**（对比 base sidecar 会打印 `WARNING: detector weights not found …`）；④ 一旦绑定，OCR 立刻成功（见 2.2） |
| (b) EP / provider 配置错误 | **排除** | detect 用 DirectML 跑通（`DmlExecutionProvider` 生效）；OCR 的 `device` 默认 `cpu`，`resolve_execution_provider` 不会失败；失败点在 **binding 解析**（见下），早于任何 EP/权重逻辑 |
| (c) Core 侧 OCR provider 未注册 | **部分成立，但真正缺口是"绑定"而非"注册"** | `runtime.py:583-588` **注册了** `MangaOcrOnnxProvider`（provider_id `manga-ocr`，`capabilities={OCR}`）；错误文案来自 `handlers.py:1068-1074` 的 `_chain()`：`binding = run.provider_binding_snapshot.get(step_type)` → `chain_from_binding(None)` → `None` → `ProviderNotConfigured`。**`pipeline_defaults.provider_bindings_json` 实测为 `'{}'`**，且 `core_assembly`/`pipeline.set_defaults` 对全新安装**不种任何默认绑定**（`pipeline.py:929-947` 只写 `'{}'`） |
| (d) 输入不符合预期 | **排除** | 错误发生在输入处理之前；且绑定后同一页、同一图片 OCR 成功 |

调用链（源码位置）：
`core_service` 步骤执行 → `infrastructure/providers/handlers.py:1068` `_chain(run, "ocr")`
→ `infrastructure/providers/fallback.py:164` `chain_from_binding(binding)`
→ 绑定为 `None` → `handlers.py:1072` `raise ProviderNotConfigured("no provider binding configured for step 'ocr'")`
→ step 失败码 `PROVIDER_NOT_CONFIGURED`。

绑定数据来源：
`core_service.handle_start_run` → `pipeline.accept_start_run(..., overrides=…)`
→ `infrastructure/sqlite/pipeline.py` `freeze()`：`providers = _merge(_load(row["provider_bindings_json"]), overrides.get("provider_bindings", {}))`
→ `application/tasks/service.py:270` `provider_binding_snapshot=frozen.provider_bindings`。
即：**绑定只来自 `pipeline_defaults.provider_bindings_json`（默认 `{}`）或 StartRun 的 `overrides.provider_bindings`**。

### 2.2 因果验证（同一 sidecar、同一数据根、只改一个字段）

| 实验 | StartRun 负载差异 | detect | **ocr** | 后续 |
|---|---|---|---|---|
| 对照 | `overrides: {}` | completed (13/6/7 候选) | **failed `PROVIDER_NOT_CONFIGURED`** | 不到 translate/render |
| 实验 | `overrides: {"provider_bindings": {"ocr": "manga-ocr"}}` | completed | **completed** | `color` failed `PROVIDER_FAILED` |

OCR 成功证据（`evidence/probe-binding-override.json` 的 `step_runs[1].output_json`）：

```json
{"ocr_text":"…日文…","provenance":{"provider_id":"manga-ocr","provider_type":"local-manga-ocr-onnx",
 "model":"manga-ocr-base-onnx","device_host":"cpu","fallback_chain":["manga-ocr"],
 "used_fallback":false,"line_count":1,"attempts":[{"ok":true,"provider_id":"manga-ocr"}]}}
```
region 侧：13 个 region 的 `text_json` **全部非空**（detect 产出的 region 均写入了识别文本）。

**因此 OCR `PROVIDER_NOT_CONFIGURED` 是配置缺口（binding 未配置），与模型包、EP、输入无关。**

---

## 3. AC3 detect `INVALID_INPUT`（页 4–8）

### 3.1 判定：检测器对**无文字页**正常返回 0 候选，Core 把"0 候选"映射为 `INVALID_INPUT`

- 直接证据：`handlers.py:296` `f"detector returned no candidates for page {unit.page_id!r}"`，
  该 step 的 `error_code` 为 `INVALID_INPUT`（不是解码/尺寸错误）。
- 逐页 `core.detect` 实测（验证面使用与 pipeline **同一个 detector 实例**，`evidence/detect-per-page.json`）：

| 页 | 尺寸/格式 | 字节 | **candidates** | detect 耗时 | 运行结果 |
|---|---|---|---|---|---|
| 1 | 1200×1660 JPEG | 657,353 | **13** | 1603 ms（含首载） | OCR 失败（binding） |
| 2 | 1200×1660 JPEG | 605,434 | **6** | 70 ms | 同上 |
| 3 | 1200×726 JPEG | 249,097 | **7** | 48 ms | 同上 |
| 4 | 1200×1660 JPEG | 477,560 | **0** | 66 ms | INVALID_INPUT |
| 5 | 1200×1660 JPEG | 512,573 | **0** | 66 ms | INVALID_INPUT |
| 6 | 1200×1660 JPEG | 587,669 | **0** | 67 ms | INVALID_INPUT |
| 7 | 1200×1660 JPEG | 474,212 | **0** | 65 ms | INVALID_INPUT |
| 8 | 1200×1660 JPEG | 495,759 | **0** | 65 ms | INVALID_INPUT |

- **不是** 尺寸/格式/固定 640 约束问题：8 页全是合法 JPEG、尺寸正常，detect 调用**返回 ok**（无 `INVALID_INPUT` 错误码），
  0 候选是检测器的**正常输出**；RT-DETR 内部统一 resize 到 640×640，与页面长宽比无关（页 3 的 726 高也正常返回 7 个候选）。
- 输入特征（`evidence/page-features.json`，灰度统计）：

| 页 | mean | std | darkFrac(<100) | edge 密度 | 判定 |
|---|---|---|---|---|---|
| 1–3（E04P02/P03/P06） | 132.7 / 152.0 / 148.3 | 77–79 | 0.34–0.48 | 6.9–7.5 | 密集分镜+对话气泡 |
| 4–8（E20P01–P05） | 145.2–199.5 | 52–62 | **0.05–0.26** | **3.6–5.1** | 无文字全彩插画（页 4 目视确认：整幅风景/角色插画，无气泡无文字） |

- **结论**：页 4–8 的 `INVALID_INPUT` 不是"坏输入"，而是 **"空检测"语义被当作硬失败**。
  对无文字页，正确行为应是 `completed`（0 region）或 `skipped`，而不是失败整页。

---

## 4. 顺带发现的第 2 个阻断点（OCR 修好后立刻撞上）

绑定 OCR 后，run 继续走到 `color` 步骤并失败：

```
color | failed | PROVIDER_FAILED | '_StubStyleAnalyzer' object has no attribute 'analyze'
```

- 调用链：`infrastructure/providers/handlers.py:726` `self.deps.source_styles.extract(original_png, box)`
  → `application/translation/color/service.py:30` `self._analyzer.analyze(original_png, box)`
  → 组装时注入的是 `core_service.py:654` 的 `_StubStyleAnalyzer`（**只有 `analyze_pixel_styles`，没有 `analyze`**），
    见 `core_service.py:715` `source_styles=SourceStyleService(_StubStyleAnalyzer())`。
- 现成实现已存在：`infrastructure/rendering/pillow_source_style.py:55 PillowSourceStyleAnalyzer`、
  `pixel_source_style.py:51 PixelSourceStyleAnalyzer`（`acceptance_bridge.py:172` 即用 `PillowSourceStyleAnalyzer`）。
- 影响：**即使 OCR 修好，color/segment/inpaint/render 仍会在 color 处断**，Run 到不了 translate/render。

---

## 5. AC4 建议（按最小改动排序）与影响面

| # | 建议 | 改动性质 | 预计效果 | 影响面 |
|---|---|---|---|---|
| **1** | **调用侧先加 provider binding 覆盖**：Host 在 `StartRun` 的 `overrides.provider_bindings` 里带 `{"ocr":"manga-ocr"}`（或按已配置的 provider profile 动态生成） | **不改 Core**，只改 Host 请求构造 | OCR 立刻可跑（本任务已实证） | RUN-EXPORT-E2E-1 AC3 从 BLOCKED → partial；任何断言"detect+ocr 完成"的 e2e |
| **2** | **给全新安装种默认本地绑定**：`pipeline.set_defaults` / `assemble_production_core` 时写入 `{"ocr":"manga-ocr","detect":"local-manga", …}`，或在 `_chain()` 无绑定时回退到本地默认 provider | Core 语义/契约变更（**需 DSH 裁决 + 契约修订**） | 免去每个调用方都记得带 override；与 P15 `prepare_run_snapshot` 的 provider_profiles 机制对齐 | 所有 Run 入口；需回归 `pipeline_defaults` 迁移与既有测试 |
| **3** | **补齐 `color` 步骤的 analyzer**：把 `_StubStyleAnalyzer` 换成 `PixelSourceStyleAnalyzer`/`PillowSourceStyleAnalyzer`（或补 `analyze` 方法） | Core 组装层 1 处替换 | color/segment/inpaint/render 可继续 | Run 全链；渲染相关测试 |
| **4** | **区分"空检测"与"坏输入"**：`handlers.py:296` 处把"0 候选"改为 `completed(0 region)` 或 `skipped`（或新增 `empty_detection_policy` 设置项） | Core 语义/契约变更（**需裁决**） | 无文字页/封面页不再整页失败 | 所有含无文字页的书；Run 终态统计（completed vs completed_with_failures） |
| **5** | **Export 闭环**：先补 translated 产物 + host-control `RegisterExportTarget` grant（沿用 RUN-EXPORT-E2E-1 AC2 结论） | 依赖 1+2+3 | Export 真跑 | RUN-EXPORT-E2E-1 AC2 |

**预计哪些 Task 会变绿**
- 只做 **#1**：`RUN-EXPORT-E2E-1` AC3 的"OCR typed 失败"消失（detect+ocr 完成），但仍会卡 `color`（#3）→ AC3 从 BLOCKED 变 **PARTIAL**。
- **#1+#3**：Run 能走完 detect→ocr→color，卡在 translate（需要 translation provider binding + 远端配置）→ 可断言"前三步全绿"。
- **#1+#2+#3+#4**：8 页整书 Run 不再有 `PROVIDER_NOT_CONFIGURED`/`INVALID_INPUT` 类失败，终态有望 `completed`（translate 仍需远端 provider）。
- **观测方式**：以上都不需要改产品源码即可用本任务的 `run_diag.py` 复测（`--bindings '{"ocr":"manga-ocr"}'`）。

---

## 6. NOT_RUN / 局限

| 项 | 状态 | 原因 |
|---|---|---|
| translate/inpaint/render 全链验证 | NOT_RUN | translate 需 translation provider（远端 endpoint/凭证），本任务不配置网络与凭证；且 color 已先失败 |
| 不带 binding 的其它 step（translate/segment/…）根因 | NOT_RUN（可推定） | 同一 `_chain()` 机制，任何 step 无 binding 都会 `PROVIDER_NOT_CONFIGURED`；本任务只对 `ocr` 做了因果实证 |
| OCR 识别质量评估（日文准确率） | NOT_RUN | 本任务只诊断"能不能跑"，不做质量评测（另见 INFER-BASELINE-EP-1 的跨运行时一致性） |
| 页 4–8 是否"真无文字"的逐页人工确认 | PARTIAL | 页 4 已目视确认（全彩插画无字）；其余 4 页仅按统计特征（darkFrac/edge）与 0 候选推断，未逐页目视 |
| AC11 无标签副本 vs models 包 sidecar 的差异 | 记录 | 两者 sha256 不同（`e0a1eff8…` vs `2b36bfeb…`）；本报告结论只覆盖 models 包构建，若线上用另一构建需复测 |

---

## 7. 证据索引

| 文件 | 内容 |
|---|---|
| `probe-models-book.json` | 整书 8 页复现：全部请求/响应帧、step_runs、task_projection、DB 快照 |
| `probe-binding-override.json` | 因果实验：注入 `overrides.provider_bindings={"ocr":"manga-ocr"}` 后的完整帧 + OCR 成功输出 |
| `detect-per-page.json` | 8 页 `core.detect` 候选数（13/6/7/0/0/0/0/0）与耗时 |
| `page-features.json` | 8 页图像特征（尺寸/格式/亮度/暗像素比/边缘密度） |
| `core-models-book.log` / `core-binding-override.log` | 两次运行的 Core stdin/stdout/stderr 全量日志 |
| `REPORT.md` | 本文件 |

复跑脚本在 `G:/CODEX/New Manga.workspace/task-envs/RUN-OCR-DIAG-1/scripts/`：
`run_diag.py`（Run 复现/因果实验）、`detect_probe.py`（逐页 detect）、`page_features.py`（输入特征）、`summarize.py`（结果汇总）。
