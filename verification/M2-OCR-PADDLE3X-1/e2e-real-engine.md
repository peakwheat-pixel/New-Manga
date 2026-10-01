# M2-OCR-PADDLE3X-1 AC4：真实引擎端到端验证（隔离 venv，2026-10-01）

- 环境：隔离 venv `G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/`（paddleocr 3.7.0 / paddlepaddle 3.3.1 CPU / numpy 2.3.5 / opencv 5.0.0），权重 `~/.paddlex` 缓存，零入库
- 被测：修复后的生产 `PaddleKoreanOcrProvider`（`src/infrastructure/providers/ocr_local.py` @ agent/zcode/M2-OCR-PADDLE3X-1），**零注入**（无 engine_factory，默认构造路径）
- 素材：与 M2-TA3-B 冒烟同页 K11（sha256 `4bd9b181…`）

## 1. 主验收：零注入生产路径端到端（[paddle-fixed-e2e.json](paddle-fixed-e2e.json)，EXIT=0 status=OK）

探针：[paddle_fixed_e2e_probe.py](../../experiments/M2-OCR-PADDLE3X-1/paddle_fixed_e2e_probe.py)

| 项 | 结果 |
|---|---|
| 引擎构造 | `PaddleOCR(lang="korean", enable_mkldnn=False)`（生产默认路径），无 PIR/oneDNN 崩溃 |
| 页面级输入 | 整页 PNG bytes（生产形态：`image_bytes` 经 `np.frombuffer`+`cv2.imdecode`→ndarray） |
| 页面级输出 | **28 行**，`page_level_lines_with_empty_polygon=[]`（全部非空 polygon），mean confidence 0.4086 |
| 复现 | `PYTHONPATH=src "$PY" experiments/M2-OCR-PADDLE3X-1/paddle_fixed_e2e_probe.py --image <K11> --out verification/M2-OCR-PADDLE3X-1/paddle-fixed-e2e.json` |

这证明 AC2+AC3 全链路：bytes 不再被 3.x 静默忽略（修复前 bytes 路径恒空，见 [diagnosis.md](diagnosis.md)）；3.x `rec_*` 输出被解析为 OcrLine 且 numpy box 物化后 polygon 非空（修复前 `_polygon_of` 对 numpy 静默丢弃）。

## 2. crop 级观测与等价性矩阵（[crop_matrix_probe.py](../../experiments/M2-OCR-PADDLE3X-1/crop_matrix_probe.py)、[crop_preset_compare_probe.py](../../experiments/M2-OCR-PADDLE3X-1/crop_preset_compare_probe.py)）

矩阵实验（6 个 crop × {引擎直调 ndarray predict, 生产 adapter 同款 PNG bytes 往返}）：

```
diag_box_A_pad8 (115x58, 页顶'당근아?'): direct=1行['당근아?'] | png=1行['당근아?']  ← 一致且非空
topconf0 '당근아?!' (107x49): direct=0 | png=0   ← 一致（空）
topconf1 '당근아?' (98x50):   direct=0 | png=0
topconf2 '당근아!' (96x39):   direct=0 | png=0
topconf3 '늘' (77x58):        direct=0 | png=0
probe_box_exact (123x65):     direct=1行['232'] | png=1行['232'] ← 一致
```

构造 A/B（同一 crop 115x58）：全预处理 `PaddleOCR(lang='korean', enable_mkldnn=False)` 与精简预处理（关 doc_ori/unwarp/textline_ori）**均识别出「당근아?」**——预处理开关不影响 adapter 契约层。

三条结论：

1. **等价性**：生产 adapter 的 bytes→ndarray 转换与引擎直调逐例一致（6/6），无转换损失、无形状偏差。
2. **[限制，如实登记] PP-OCRv5 det 对孤立小 crop 的检测行为**：页面级能检出的行（整页 28 行）裁成孤立小图后 det 常返回零框；同一 crop 多次运行结果带不确定性（同一 box 一次空、一次「232」）。这是引擎检测/配置口径问题（生产 OCR 收到的 region crop 来自 detect 步骤，孤立 crop 再检测的可靠性需引擎参数或 rec-only 模式决策），**不属于本 Task 授权面**（构造参数授权仅 `enable_mkldnn=False`），登记待集成方/D06 处理。
3. **[质量观测，不声称] 页面级 mean confidence 0.4086、preview 含乱码**（TA3-B 冒烟同页精简预处理为 0.6871、文本正常）：默认构造全预处理管线（doc_ori/UVDoc/textline_ori 全开）在韩漫页上的识别质量显著低于精简预处理。质量数字口径属阶段二测量 Task；引擎默认构造的质量调优超本 Task 授权面，一并登记。

## 3. 主 venv 回归

修复前后 `PYTHONPATH=src` 主 venv `pytest tests/providers tests/core tests/m2_acceptance -q`：

- 修复前（新测试已写）：`10 failed, 7 passed`（红态，红项即缺陷复现）
- 修复后：**`507 passed, 1 skipped, 0 failed`**（基线 490+1 + 新增 17，零回退；主 venv 无 paddle，真实引擎验证不入 pytest）
