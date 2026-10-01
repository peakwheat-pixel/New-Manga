# M2-OCR-PADDLE3X-1 AC1：双 region bytes 路径机制判定（2026-10-01）

## 结论（R10 结案）

**判定：ALWAYS_EMPTY（恒空）——stale-reuse（错位复用）被排除。**

paddleocr 3.x 对 bytes 输入在**输入类型校验层直接忽略**（引擎日志原话：`Not supported input data type! Only numpy.ndarray and str are supported! So has been ignored: b'\x89PNG...'`），不进入推理执行器，**无异常返回空 list**。历史调用从未产出过任何文本，因此不存在"静默错误文本"风险面；风险性质是**静默空 OCR**（可用性缺陷，非正确性缺陷）。

## 探针设计

脚本：[diagnose_bytes_path.py](../../experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py)（入仓）；机器可读结果：[diagnosis.json](diagnosis.json)。

1. `engine_ref`：`PaddleOCR(lang="korean", use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False, enable_mkldnn=False)`——全页 ndarray 推理定位文本框，裁出**两个文本不同**的 region（A：「당근아?」box (62,8,161,50)；B：「당근아!」box (544,17,620,52)），各自 crop 后 ndarray 推理取得真值（GT_A=["당근아?"]、GT_B=["당근아!"]）。`enable_mkldnn=False` 仅为 ndarray 推理可行（paddlepaddle 3.3.1 Windows CPU PIR/oneDNN 缺陷）；bytes 路径的忽略发生在输入校验层、先于任何执行器调用，与该开关无关。
2. `engine_prod`：`PaddleOCR(lang="korean")`——与生产 `PaddleKoreanOcrProvider` 默认构造**逐字一致**（无 mkldnn 参数）。
3. bytes 路径连续两次：`engine_prod.ocr(A_png_bytes)` → `engine_prod.ocr(B_png_bytes)`，提取 rec_texts。

## 结果

| 步骤 | region | bytes | 返回类型 | 返回长度 | 提取文本 | GT（ndarray 真值） |
|---|---|---|---|---|---|---|
| 1 | A「당근아?」 | 5582 B PNG | list | **0**（空） | [] | ["당근아?"] |
| 2 | B「당근아!」 | 3884 B PNG（与步骤 1 不同输入） | list | **0**（空） | [] | ["당근아!"] |

- 两次输出均为空 list → 不满足 stale-reuse 的判定条件（第二次输出≠空且≠自己的输入）；`t2_matches_gt_a=null`。
- 判定矩阵命中 `ALWAYS_EMPTY`；`wrong_text_risk=false`。

## 环境

- 隔离 venv `G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/`（paddleocr 3.7.0 / paddlepaddle 3.3.1 CPU / numpy 2.3.5 / opencv 5.0.0），权重已在 `~/.paddlex` 缓存，零入库。
- 素材：`G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg`（与 M2-TA3-B 冒烟同页，sha256 `4bd9b181…`）。
- 探针 EXIT=0（判定成功落盘即为交付；verdict 字段记录机制结论）。

## 复现

```bash
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
  experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py \
  --image "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg" \
  --out verification/M2-OCR-PADDLE3X-1/diagnosis.json
# 期望输出：probe_verdict=ALWAYS_EMPTY
```

## 对修复的含义

- 输入侧把 bytes 解码为 ndarray 即可让 3.x 引擎真正推理（观测→机制已闭合，`np.frombuffer` 内存解码无需 CJK 路径往返）。
- 无需任何"防错位复用"的防御层；fail-closed 语义保持：解码失败 → typed `ProviderInputError`。
- 附带观测：3.x 的 `engine.ocr()` 打 DeprecationWarning（"Please use predict instead"），但仍是可用的兼容别名；生产 adapter 保留 `ocr(ndarray)` 调用以兼容 2.x（2.x 无 `predict`）。
