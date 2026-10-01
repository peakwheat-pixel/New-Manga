# M2-TA3-B AC2：OCR 安装+冒烟证据（阶段一，2026-10-01）

- 环境：隔离 venv `G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/`（python 3.12.3，`py -3.12 -m venv`，参照 task-envs 既有模式；`include-system-site-packages=false`）
- 安装通道：pip 经代理 `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:7890`
- 冒烟脚本：`experiments/M2-TA3-B/ocr_smoke.py`（入仓）；结果 JSON：[ocr-smoke-manga-ocr.json](ocr-smoke-manga-ocr.json) / [ocr-smoke-paddleocr.json](ocr-smoke-paddleocr.json)
- 纪律：权重只落在 venv/HF/paddlex 缓存（Git 外），**零入库**；本冒烟不产生任何质量数字（质量口径见 [quality-thresholds.md](quality-thresholds.md)，实测属阶段二）

## 1. 安装结果（全部 EXIT=0，总耗时 166s）

| 包 | 版本 | 说明 |
|---|---|---|
| manga-ocr | 0.1.16 | 携带 torch 2.14.1（CPU）、transformers 5.18.0、Pillow 12.3.0 |
| paddlepaddle | 3.3.1 | **CPU 版**（官方默认 wheel 即 CPU） |
| paddleocr | 3.7.0 | 携带 paddlex 3.7.2、opencv-contrib-python 4.10.0、modelscope 1.40.1 |

版本交互注记：paddleocr 安装把 numpy 从 2.5.3 降到 2.3.5（pip resolver 行为）；manga-ocr 冒烟在此组合下照常通过。

## 2. 模型权重（首次运行自动下载，均在 Git 外缓存）

| 模型 | 缓存位置 | 体积 | 下载方式 |
|---|---|---|---|
| manga-ocr-base（kha-white） | `~/.cache/huggingface/hub/models--kha-white--manga-ocr-base` | **424 MB** | HF 经代理 |
| korean_PP-OCRv5_mobile_rec + PP-OCRv5_server_det | `~/.paddlex/official_models/` | 合计 **171 MB**（paddlex 缓存整体） | paddleocr 首次运行经代理 |

## 3. 冒烟结果（各 1 页真实 OCR）

| 引擎 | 素材页 | 结果 | 关键数字 |
|---|---|---|---|
| manga-ocr | BJ02（`vol01_p0053.png`，sha256 `c1ce0620…`，TA2B suite） | **OK，EXIT=0** | weights_load 10.5s；首推理 0.22s；输出 `"．．．"`（整页输入非生产用法——生产 adapter 只喂 region crop，见 `ocr_local.py` `needs_detection=False`；冒烟只验证安装/下载/推理链路） |
| PaddleOCR | K11（`kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg`，sha256 `4bd9b181…`，main suite） | **OK，EXIT=0** | weights_load 5.5s；首推理 20.0s（CPU）；28 文本行，mean confidence 0.6871，样例「당근아? / 이렇게까지는 / 할 필요없을줄 …」 |

## 4. 冒烟过程发现（如实登记，三项）

1. **[已修，environment] paddlepaddle 3.3.1 Windows CPU oneDNN/PIR 缺陷**：默认 MKLDNN 路径推理即抛 `NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`（`onednn_instruction.cc`）。标准解法 `PaddleOCR(..., enable_mkldnn=False)` 后通过。阶段二 runner 必须携带该参数。
2. **[data 形态限制，如实登记] webtoon 长条漫整图超 OpenCV 上限**：K01 base.png 为 690x62133 长条图，PaddleOCR 3.x 预处理后触发 `cv::remap` 断言（`dst.rows < SHRT_MAX`）。生产链路不受影响（`PaddleKoreanOcrProvider` 收的是 detect 后的 region crop，尺寸有限）；阶段二测量脚本的 lesson：**webtoon case 的 OCR 测量必须在 region crop 级做，不能整图喂**。
3. **[适配器兼容性风险，登记为修复候选] 生产 adapter 的 bytes 直传在 PaddleOCR 3.x 下返回空结果且无异常**。**观测**（R10：仅陈述实测）：`engine.ocr(raw_bytes)` 无异常返回，seam probe 提取文本为空（`EMPTY_RESULT`）；3.x 侧日志记 "Not supported input data type ... ignored"。**机制为假设，未验证**：r1 版"静默复用上一次输入"的表述与本次观测（成功 ndarray 推理之后 bytes 调用仍返回空）不相容，已撤回——是"恒空"还是"错位复用"由修复 Task 用连续 2 个不同 region 走 bytes 路径判定（错位复用=静默错误文本，严重度更高）。这是静默退化而非 fail-closed。本 Task 禁改 `src/**`，不修复；阶段二测量脚本绕行（`np.fromfile`+`cv2.imdecode` → ndarray 直传 + 输出形状适配，见 phase2-plan §2.2）。**建议后续立小 Task**（验收条件三件：输入契约 fail-closed/ndarray 化、输出形状 3.x→legacy 适配、双 region bytes 行为判定）。

## 5. 复现

```bash
PY="G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe"
export HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890
"$PY" "G:/CODEX/New Manga.worktrees/M2-TA3-B-zcode/experiments/M2-TA3-B/ocr_smoke.py" \
  --engine manga-ocr \
  --image "G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol01/pages/vol01_p0053.png" \
  --out verification/M2-TA3-B/ocr-smoke-manga-ocr.json
"$PY" "G:/CODEX/New Manga.worktrees/M2-TA3-B-zcode/experiments/M2-TA3-B/ocr_smoke.py" \
  --engine paddleocr \
  --image "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg" \
  --out verification/M2-TA3-B/ocr-smoke-paddleocr.json
# 两命令 EXIT=0（结果 JSON 内 "status":"OK"）
```
