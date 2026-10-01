# M2-TA3-B 阶段二执行计划（正式 run）

- Task：[M2-TA3-B](../../doc/tasks/M2-TA3-B.md) 阶段一 AC4 · 日期 2026-10-01
- 前置阅读：[quality-thresholds.md](quality-thresholds.md)（口径与提案阈值）、[ocr-smoke-results.md](ocr-smoke-results.md)（环境事实与三个发现）、[case-selection.json](../../experiments/M2-TA3-B/case-selection.json)（20 case manifest）
- 状态：**BLOCKED_ON_USER**——启动条件=翻译 endpoint 二选一（§3），二选一后本计划即启，无需再释放。

## 1. 目标与交付物

对 20 case（`experiments/M2-TA3-B/case-selection.json`）跑生产全链真实产物，并按 quality-thresholds.md 的口径产出：

| 交付物 | 位置（规划） | 对应 Gate |
|---|---|---|
| 全链 run 明细 + summaries | `verification/M2-TA3-B/phase2/summaries/` | 全链 pipeline_failures=0 |
| OCR 明细 + GT 工作表 + CER 报告 | `verification/M2-TA3-B/phase2/ocr/` | OCR CER 四档阈值（§2.3） |
| 翻译评分工作表（SFX+对白） | `verification/M2-TA3-B/phase2/translate/` | SFX non-fail ≥70%、对白中位数 ≥3.5 且 ≥3 占比 ≥80% |
| inpaint 定性抽检表 | `verification/M2-TA3-B/phase2/inpaint/` | 无数值 Gate，100% 登记 |
| export 哈希复算 + 3 case 复跑 | `verification/M2-TA3-B/phase2/export/` | 哈希一致、确定性复跑一致 |
| 质量报告（含阈值实测 vs 提案对照） | `verification/M2-TA3-B/quality-report.md` | 全部 |

## 2. runner 扩展设计（基于 TA3-A `run_smoke.py`）

### 2.1 形态

新增 `experiments/M2-TA3-B/run_qualification.py`（**不改动** `experiments/M2-TA3-A/run_smoke.py`，后者保持只读基座），复用其经过验证的骨架：production assembly（`assemble_core_services`，Qt offscreen、真实 docTR detect）→ Run1 PAGE_SELECTION/TRANSLATE_ALL → region 级 Run2 RETRANSLATE_REGION_FULL → 单图 export → 三向归因 fail-closed summary。差异：

| 扩展点 | 设计 |
|---|---|
| case 输入 | 读 `case-selection.json`（不再硬编码 CASES dict）；`--case` 过滤参数保留 |
| provider binding | `ocr`：ja case→`manga-ocr`、ko case→`paddleocr-korean`（生产 registry 既有 descriptor，`runtime.py`）；`translate`：按用户选择绑 `openai-compatible-translation` 或 `sakura-local`（§3）；inpaint/render/export 保持生产默认 |
| OCR 明细导出 | 每 case 新增 `ocr_details` 段：每 region 的 `region_id/region_type/bbox/text/elapsed_ms` + **region crop PNG 落盘**（`phase2/ocr/crops/`，gitignored）——这是 CER 测量与人工抽检的共同底料 |
| translate 明细导出 | 每 region `source_text/translated_text/region_type` 落 JSON（评分工作表的输入） |
| 确定性复跑 | `--rerun-check BJ02,K01,K11`：同环境第二次 run，export sha256 逐位比对 |

### 2.2 OCR provider 适配（阶段二必须处理的两项冒烟发现）

1. **PaddleOCR bytes 静默忽略**（[ocr-smoke-results.md](ocr-smoke-results.md) 发现 3）：生产 `PaddleKoreanOcrProvider` 直传 `image_bytes` 在 paddleocr 3.x 下得到**空结果且不报错**。绕行方案（`src/` 零改动）：runner 组装时给 `PaddleKoreanOcrProvider` 注入 `engine_factory`——工厂返回一个 wrapper 对象（暴露 `.ocr(raw_bytes)`：内部 `np.frombuffer`+`cv2.imdecode` 成 ndarray 后转调真 engine，`enable_mkldnn=False`）。adapter 的请求/响应映射契约不变。
2. **oneDNN/PIR 缺陷**（发现 1）：`PaddleOCR(..., enable_mkldnn=False, ...)` 固定写进 wrapper。
3. **webtoon 长图**（发现 2）：生产链天然在 region crop 级喂 OCR，无 `SHRT_MAX` 风险；禁止整图直喂 PaddleOCR（冒烟教训写死在 runner 注释）。

### 2.3 OCR CER 测量挂点（独立脚本，不进 runner）

新增 `experiments/M2-TA3-B/measure_cer.py`：

1. 输入：`ocr_details` JSON + GT 工作表 + crop 目录；
2. GT 生成（quality-thresholds §2.2 三分）：
   - G1：`extract_svg_gt.py` 从 lang-pack ZIP 提取 SVG 文本（`lang/<lang>/E\d\dP\d\d.svg`），按 region bbox 对齐（SVG 元素坐标→bbox 内文本收集）；
   - G2：`ocr-gt-ai-draft.csv` 由 AI 视觉直读 crop 预填 → **用户逐条审核** → `ocr-gt.csv`（C1 工作表纪律：`[AI]`/`[人工修订]` 前缀、user_rationale 列、draft 整体存档）；
3. 计算：region 级 CER（§0 归一化 + Levenshtein，标准库实现）；输出 per-region CSV + 语言级汇总 JSON（中位数/P90/CER=0 占比）；
4. 人工抽检（n=30）工作表同目录生成，`ai_draft` 预填列 + 用户终审列分离。

### 2.4 venv 融合（阶段二环境前提，登记为执行前检查项）

冒烟 venv `M2-TA3-B-ocr` 只有 OCR 栈；生产链需要 PySide6/docTR/sqlite 全栈（在 `T1.1.1-impl-py312` 主 venv）。二选一：

- **方案 A（推荐）**：在 `M2-TA3-B-ocr` venv 内补装生产 `requirements.txt` + PySide6 → 单 venv 全栈，隔离性最好；
- **方案 B**：主 venv 增装 `manga-ocr`+`paddleocr`+`paddlepaddle`——最快但污染主 venv（契约原文"隔离实验 venv"精神下不建议）。

执行前检查：`python -c "import manga_ocr, paddleocr, PySide6, doctr"` 在选定 venv 内全部成功。

## 3. 翻译 endpoint 操作手册（用户二选一）

### 选项 (a)：用户提供 OpenAI-compatible endpoint

需用户提供三项：`base_url`（如 `https://api.example.com/v1`）、`model` 名、API key。

配置注入（`runtime.py` settings 契约，runner 内执行、零硬编码）：

```python
# run_qualification.py 内（示意）：
core.settings.update({
    "providers": {"profiles": {
        "openai-compatible-translation": {
            "base_url": os.environ["TA3B_TRANSLATE_BASE_URL"],
            "model": os.environ["TA3B_TRANSLATE_MODEL"],
            "enabled": True,
        }
    }}
})
core.pipeline_defaults.save_provider_binding("translate", "openai-compatible-translation")
```

**凭证纪律**：API key 只经环境变量 `TA3B_TRANSLATE_API_KEY` 传入 runner 进程；**不入仓、不入日志、不入 summary JSON**（summary 只记 provider_id+base_url host+model 名）。用户也可直接给本地明文文件路径（`credential_ref` 机制），由用户自行管理。

前置自检：runner 启动时对 endpoint 发 1 次最小 completion 探针（1 region、短文本），失败即 fail-closed 退出，不进入正式 run。

### 选项 (b)：本地 Sakura 部署（需用户授权 GB 级下载）

生产 provider 已内建：`sakura-local`（`SAKURA_DEFAULT_BASE_URL = http://127.0.0.1:8080/v1`、模型名默认 `sakura`），探针 `sakura_probe.py` 已在位（`/v1/models` readiness + `/health` liveness，typed reason codes）。

部署步骤（用户授权后 agent 可代执行，磁盘与耗时预估在每步标注）：

1. **选型与下载**：Sakura 系列翻译模型 GGUF（如 Sakura-13B/14B 翻译特化版；**具体模型与量化档位由用户裁决**，磁盘 8-16GB、下载 20-60 分钟经代理）→ 存放 `G:/CODEX/New Manga.task-envs/M2-TA3-B-sakura/models/`（Git 外）；
2. **推理服务**：llama.cpp `llama-server`（单 exe，Windows 预编译包 ~20MB）加载 GGUF，监听 `127.0.0.1:8080`（`--port 8080 --api-key ''`），显存不足时 `--n-gpu-layers` 分层或纯 CPU（速度代价如实告知用户）；
3. **探针验证**：`GET http://127.0.0.1:8080/v1/models` 期望 reason_code=`ready`（当前状态=`unreachable`，2026-10-01 侦察：127.0.0.1:8080 无服务响应）；
4. **绑定**：runner 内 `save_provider_binding("translate", "sakura-local")`（profile 无凭证，localhost 直连豁免默认网络 profile）。

前置自检：同 (a) 的 1-region 最小 completion 探针。

### 二选一的决策输入（给用户）

| 维度 | (a) remote endpoint | (b) 本地 Sakura |
|---|---|---|
| 用户准备成本 | 提供 base_url/model/key（5 分钟） | 授权下载 8-16GB + 部署（0.5-1 小时） |
| 翻译质量 | 取决于所选模型（通用 LLM 对漫画语域无特化） | 漫画翻译特化模型，语域适配预期更好 |
| 凭证/隐私 | key 交由 runner 环境变量（不落盘） | 无外部凭证，全本地 |
| 可复现性 | endpoint 侧模型更新可能改变结果 | 本地权重固定，确定性最好 |

## 4. 执行清单（二选一解锁后按序执行）

| # | 步骤 | 产出 | 依赖 |
|---|---|---|---|
| 1 | venv 融合（§2.4 方案 A）+ 导入自检 | 执行记录 | - |
| 2 | 翻译 endpoint 接入 + 1-region 探针 | 探针记录（无 key 泄漏） | 用户二选一 |
| 3 | GT 前置：G1 SVG 提取脚本跑通（K11 页人工比对） | `svg-gt-*.json` | - |
| 4 | 20 case 正式 run（`run_qualification.py`，detect→OCR→translate→inpaint→render/export） | summaries + crops + 明细 | 1/2 |
| 5 | 3 case 确定性复跑 | 复跑哈希对照 | 4 |
| 6 | export 哈希独立复算 | 复算记录 | 4 |
| 7 | G2 AI 预判 GT 预填（BJ/webtoon crop）→ 交用户审核 | ai-draft + 正式 `ocr-gt.csv` | 4 |
| 8 | `measure_cer.py`：CER 汇总（G1/G2 分列） | CER 报告 | 7 |
| 9 | OCR 人工抽检 n=30 工作表 → 用户终审 | 抽检工作表 | 8 |
| 10 | SFX 语义核对表 + 对白可读性评分表（AI 预填）→ 用户终审 | 评分工作表 | 4 |
| 11 | inpaint 定性抽检 10 region → 用户判读 | 抽检记录 | 4 |
| 12 | `quality-report.md`（实测 vs 提案阈值对照 + 裁决登记） | 质量报告 | 8-11 |
| 13 | 独立 Review（DSH 非作者）→ Codex 集成 | review/integration | 12 |

预计总量：正式 run 20 case（TA3-A 5 case 单 case wall 2-5 分钟，20 case 估 1-2 小时含 CPU OCR）+ 人工审核两轮（用户侧）。

## 5. 风险与如实登记义务

1. **生产 adapter 的 PaddleOCR 3.x 兼容缺口**：本计划用 engine_factory wrapper 绕行（不动 `src/`）；绕行成功不等于生产缺口闭合——**修复 Task 建议**（`ocr_local.py` 输入契约适配）在质量报告中正式登记，交 Codex 裁决。
2. **CER 对齐风险**：SVG GT（G1）按 bbox 收集可能混入非目标文本；对策=align 后抽样 5 region 人工核对对齐正确性，再全量计算。
3. **目标语言默认 zh**（quality-thresholds §0）：如用户改选，仅影响 §3.2 评分维度中的 fluency/register 锚点描述，工作量不变。
4. **modelscope 下载通道**：paddleocr 模型经 modelscope/aistudio 下载（冒烟已走通）；如网络策略变化，备用=`HF_ENDPOINT` 镜像或手动放置 `~/.paddlex/official_models/`。
