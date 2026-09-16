# TASK-016 调研记录：OCR 与检测候选路线

本文件是 **实验性调研记录**（TASK-016 白名单内），不是产品需求、不是 Provider 契约，也不改变 `src/`、`tests/`、Schema 或共享 Protocol。所有候选均来自本仓库既有文档，本文只做**归集与可验证性标注**。

> **重要限制（本环境实测）**：本机 `huggingface.co` **不可达**（TCP 超时），PyPI 可达；实验解释器（Python 3.12.3 任务环境）**未安装**任何 OCR/检测依赖。因此**本文不给出任何版本号或权重哈希**——那需要联网确认或本地权重，均不具备。下表"许可"列同理为**待核实**，不得据本文做合规决策。

## 1. 候选来源（仓库文档）

| 出处 | 内容 |
|---|---|
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:215` | `manga_ocr`——manga_ocr 库，GPU 自动检测 |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:218` | `paddleocr_vl`——VLM(transformers) |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:220` | `ai_vision`——任意 visionOcr 能力 LLM |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:221` | **混合**——manga_ocr ↔ 48px 置信度回退（阈值默认 0.2） |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:222` | `paddleocr_korean`——韩国条漫优先 OCR；长条 Webtoon 建议先切片/分区；复杂艺术字可回退 Vision OCR（标注为**目标规划**） |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:223` | `openai_compatible_vision_ocr`——`base_url` / `api_key` / `model`，图片 URL/Base64（标注为**目标规划**） |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md:255` | 历史材料引用（**本仓库无此文件**）：`default`(DBNet ResNet34，默认)、`ctd`、`yolo`(YSGYolo)、`saber_yolo`(仅二阶段纠错)；辅助 `aux_yolo` 融合(默认关)；大图切片触发条件（缩放比 > 2.5 或长宽比 > 3.0）——原出处 `detector/registry.py:18-33` |
| `doc/02_TECHNICAL_ARCHITECTURE_.md:24` | 文字检测：DBNet / CTD / YOLO 系 Adapter，统一 `DetectionProvider` 接口 |
| `doc/02_TECHNICAL_ARCHITECTURE_.md:26` | OCR：manga-ocr / 48px / RapidOCR / PaddleOCR Korean / OpenAI-compatible Vision OCR，统一 `OCRProvider` 接口 |
| `doc/02_TECHNICAL_ARCHITECTURE_.md:479-482` | OCR 节点：manga-ocr、RapidOCR、PaddleOCR Korean（韩国条漫）、OpenAI-compatible Vision OCR |

**注意**：`doc/01` 的 L255 段落明确写"本仓库无此文件"，即 `detector/registry.py` 与 `constants.py` **不在本仓库**。TASK-016 的 AC 要求"不复制旧仓库未提供代码"——本文因此**只记录路线名与文档出处**，不重建任何未提供的实现。

## 2. 候选与可验证性

"本环境可验证性"指：在当前无网络、无依赖的 Windows 实验解释器下能否完成**真实模型推理**。全部为 **BLOCKED** 的原因是共同的：无依赖 + 权重不可下载。

| 候选 | 类别 | 实现载体（按文档） | 额外条件 | 许可 | 本环境可验证性 |
|---|---|---|---|---|---|
| `manga_ocr` | 日漫 OCR | `manga_ocr` 库，GPU 自动检测 | manga-ocr 权重（HF Hub） | **待核实** | **BLOCKED**（依赖缺失 + `huggingface.co` 不可达） |
| `paddleocr_vl` | VLM OCR | transformers | VLM 权重 | **待核实** | **BLOCKED**（同上，且权重体积大） |
| `ai_vision` | 通用 Vision | 任意 visionOcr 能力 LLM | 已授权 LLM 端点 | 取决于端点 | **BLOCKED**（无 `NEWMANGA_VISION_BASE_URL`/`OPENAI_API_KEY`，且不读取 secret 值） |
| `openai_compatible_vision_ocr` | 通用 Vision 适配层 | OpenAI 兼容图片输入（URL / Base64） | `base_url` + `api_key` + `model` | 取决于端点 | **BLOCKED**（同 `ai_vision`；属目标规划，未实现） |
| `paddleocr_korean` | 韩文 OCR | PaddleOCR 韩文专用识别模型 | PaddleOCR 权重 | **待核实** | **BLOCKED**（依赖缺失 + 权重需下载） |
| `rapidocr_onnxruntime` | 本地 ONNX OCR | RapidOCR + onnxruntime | 随包模型 | **待核实** | **BLOCKED**（依赖缺失；模型通常随包，若可装则本项**最可能**在离线环境跑通） |
| 混合（manga_ocr ↔ 48px） | 回退策略 | 置信度回退，阈值默认 0.2 | 需上述两者 | — | **BLOCKED**（依赖其组成候选） |
| `detector_dbnet` | 检测（默认） | DBNet ResNet34 | detection 权重 | **待核实** | **BLOCKED** |
| `detector_ctd` | 检测 | CTD | detection 权重 | **待核实** | **BLOCKED** |
| YOLO 系（`yolo`/`saber_yolo`/`aux_yolo`） | 检测 | 文档仅列名，`detector/registry.py` 不在本仓库 | 权重 | **待核实** | **BLOCKED**（且无可用实现来源） |

### 许可与版本为何一律"待核实"

- **版本**：需要从 PyPI/HF 读取实际包元数据或权重文件；本环境 HF 不可达，且**不允许**由实验 Task 修改依赖清单去安装，故无法取得可信版本号。给出任何版本号都会是**未经验证的猜测**。
- **许可**：候选涉及多个上游项目与模型权重，许可可能因**模型权重**与**代码**而异（例如代码与权重的授权条款常不一致），并可能包含非商业或 copyleft 条款。本文不做法律判断，**请由 Codex / 用户在有网络的环境核实后再决策**。

## 3. 本环境可直接验证的部分（已验证）

以下不依赖任何模型或网络，已在 `experiments/TASK-016/` 内实现并验证：

| 能力 | 实现 | 结果 |
|---|---|---|
| Tile-local → page-global 坐标映射 | `protocol.tile_polygon_to_global` | ✅ 通过（`test_protocol.py`） |
| 单 Region 结果保留原始 `region_id` | `protocol.map_region_result` | ✅ 通过 |
| 阅读顺序稳定排序（同序按 `region_id` 决胜） | `protocol.order_results` | ✅ 通过 |
| 失败 fallback 只允许已配置路由 | `protocol.fallback_status` | ✅ 通过（空配置集 → `BLOCKED`，不发明路由） |
| 自制样本（横排/竖排/韩文/艺术字/Tile）与 manifest（含参考文本、参考区域、Tile 原点、SHA-256） | `generate_samples.py` | ✅ 生成成功 |
| 环境与依赖探测、逐样本 BLOCKED/NOT_RUN 记录 | `run_experiment.py` | ✅ 见 verification 记录 |

## 4. 结论与建议（供 Codex Review）

1. **候选路线是清晰的**：日漫 OCR 以 `manga_ocr`（+48px 混合回退）为主，韩漫以 `paddleocr_korean` 为主，通用/复杂艺术字走 `openai_compatible_vision_ocr`；检测统一为 DBNet/CTD/YOLO 系 Adapter。
2. **本环境无法提供任何模型质量证据**：无依赖、权重不可下载、无授权端点。按 TASK-016 测试要求，这些项全部标 **BLOCKED**，未以 Mock 冒充。
3. **可立即推进的下一步**是有网络的环境里完成两件事：①确认各候选的**实际版本与许可**（尤其权重条款）；②至少让 `rapidocr_onnxruntime` 跑通（模型随包，最可能离线可用），取得第一组真实延迟与错误率数据。
4. **坐标/顺序/映射/fallback 协议已经是可回归的**，建议在接入真实 Provider 时沿用这套记录字段（`sample_id`、`region_id`、`polygon`、`reading_order`、`coordinate_space`），以尽早暴露坐标系与 RegionID 错配。
