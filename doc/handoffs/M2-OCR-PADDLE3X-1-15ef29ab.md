---
task_id: M2-OCR-PADDLE3X-1
author: ZCode
recipient: Codex（集成）+ DeepSeek Harness（review，非作者）
base_commit: 69137837
delivery_head: 15ef29ab
status: delivered
---

# Handoff：M2-OCR-PADDLE3X-1（生产 ocr_local.py PaddleOCR 3.x 适配修复）

## 交付结果

分支 `agent/zcode/M2-OCR-PADDLE3X-1`（worktree `G:/CODEX/New Manga.worktrees/M2-OCR-PADDLE3X-1-zcode`），base `69137837`，3 个 commit：

| commit | 内容 |
|---|---|
| `1885619b` | AC1：双 region bytes 路径机制判定探针 + 证据（verdict=**ALWAYS_EMPTY**，stale-reuse 排除） |
| `15ef29ab` | AC2+AC3+AC4：`src/infrastructure/providers/ocr_local.py` 生产修复 + `tests/providers/test_ocr_local.py` 17 测试（先红后绿）+ 隔离 venv 真实引擎端到端证据 |
| （本 commit） | AC5：Task frontmatter 回填 + 本 handoff |

变更路径（全部在允许面内）：`src/infrastructure/providers/ocr_local.py`（单文件）、`tests/providers/test_ocr_local.py`（新增）、`experiments/M2-OCR-PADDLE3X-1/`（4 个探针脚本）、`verification/M2-OCR-PADDLE3X-1/`（诊断 + e2e 证据）、`doc/tasks/M2-OCR-PADDLE3X-1.md`、本 handoff。

AC 逐条对照见 [Task 文件 AC 状态表](../tasks/M2-OCR-PADDLE3X-1.md)，全部 done。

核心行为变化（消费方视角）：Settings 选 PaddleOCR 的 Korean 路由在 paddleocr 3.x 环境下从"静默空 OCR"变为"真实文本输出"；输入不可解码→`INVALID_INPUT`，paddle 缺失→`PROVIDER_DEPENDENCY_MISSING`，形状不可识别→`PROVIDER_INVALID_OUTPUT`，语义零放宽，`provider_id`/`provider_type`/错误码零变化。2.x 环境行为不变（legacy 形状解析保留、`enable_mkldnn` 参数 2.x 亦接受）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 双 region bytes 判定 | `PYTHONPATH=src "$PY" experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py --image <K11> --out verification/M2-OCR-PADDLE3X-1/diagnosis.json`（EXIT=0） | 隔离 venv `G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr`（paddleocr 3.7.0/paddle 3.3.1 CPU）；诊断探针含生产默认构造引擎 | PASS：两 region bytes 调用均空 list，引擎日志明确忽略 bytes；`verdict=ALWAYS_EMPTY`，`wrong_text_risk=false` | [diagnosis.md](../../verification/M2-OCR-PADDLE3X-1/diagnosis.md) / [diagnosis.json](../../verification/M2-OCR-PADDLE3X-1/diagnosis.json) |
| AC2/AC3 红态（缺陷复现） | `PYTHONPATH=src <主 venv python> -m pytest tests/providers/test_ocr_local.py -q` | 主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（无 paddle），修复前 src | PASS（红）：`10 failed, 7 passed`——3.x 解析抛 `ProviderInvalidOutput`、engine 收到 bytes、默认构造无 `enable_mkldnn` | 红态输出记录于本表上下文（未入仓库，逐项断言见测试文件注释） |
| AC2/AC3 绿态 + 回归 | 同上 + `PYTHONPATH=src <主 venv python> -m pytest tests/providers tests/core tests/m2_acceptance -q` | 主 venv，修复后 `15ef29ab` | PASS：ocr_local 17/17；全量 **507 passed + 1 skipped, 0 failed**（基线 490+1 + 新增 17，零回退） | pytest stdout |
| AC4 真实引擎端到端 | `PYTHONPATH=src "$PY" experiments/M2-OCR-PADDLE3X-1/paddle_fixed_e2e_probe.py --image <K11> --out verification/M2-OCR-PADDLE3X-1/paddle-fixed-e2e.json`（EXIT=0） | 隔离 venv，`15ef29ab`，零注入生产路径 | PASS：页面级 28 行、全部 polygon 非空、mean conf 0.4086；crop 观测如实记录（见限制） | [e2e-real-engine.md](../../verification/M2-OCR-PADDLE3X-1/e2e-real-engine.md) / [paddle-fixed-e2e.json](../../verification/M2-OCR-PADDLE3X-1/paddle-fixed-e2e.json) |
| AC4 crop 等价性矩阵 | `PYTHONPATH=src "$PY" experiments/M2-OCR-PADDLE3X-1/crop_matrix_probe.py` / `crop_preset_compare_probe.py` | 同上 | PASS：adapter bytes 路径与引擎直调 ndarray 结果 6/6 一致；全预处理 vs 精简预处理在有效 crop 上同为「당근아?」 | 输出见 [e2e-real-engine.md §2](../../verification/M2-OCR-PADDLE3X-1/e2e-real-engine.md) |
| AC5 docstring/登记 | 阅读 `src/infrastructure/providers/ocr_local.py` 模块 docstring | `15ef29ab` | PASS：观测 vs 机制、mkldnn 原因、版本口径齐备 | 源文件 |

未运行：真实 2.x 引擎回归（环境无 paddleocr 2.x；legacy 形状解析由单测覆盖，行为兼容以单测为证）；OCR 质量数字（本 Task 不声称质量，口径属阶段二测量）。

## 接收方式

- worktree：`G:/CODEX/New Manga.worktrees/M2-OCR-PADDLE3X-1-zcode`，分支 `agent/zcode/M2-OCR-PADDLE3X-1`，tip 即本 commit（delivery_head=`15ef29ab`）。
- 单测复现（无需 paddle）：`cd <worktree> && PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers/test_ocr_local.py -q`
- 全量基线：`PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q`（预期 507 passed + 1 skipped）。
- 真实引擎复现（隔离 venv，模型已缓存 `~/.paddlex`，零入库）：见 [e2e-real-engine.md §1](../../verification/M2-OCR-PADDLE3X-1/e2e-real-engine.md)。
- Reviewer 检查建议：① `git diff 69137837..15ef29ab -- src/` 仅 `ocr_local.py`；② `_parse_paddle_output` 双形状分支 fail-closed 语义；③ 测试伪造结构与 TA3-B 实测 JSON 的一致性。

## 下一任务建议（必填）

- Task ID / 标题：M2-OCR-PADDLE3X-1 的 Review（DeepSeek Harness 非作者审查）→ Codex 集成；无新建 Task。
- 推荐 Agent / Reviewer：DeepSeek Harness（review）；Codex（集成验证 + merge）。
- 推荐原因与前置依赖：任务书指定 reviewer=DSH（非作者）；集成需 DSH 通过后由 Codex 执行。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-OCR-PADDLE3X-1`，base `69137837`，head `15ef29ab`；worktree 已存在（路径见上）。
- 允许修改路径：review 意见记录 `verification/M2-OCR-PADDLE3X-1/`（DSH report）；集成操作按协作协议由 Codex 执行。
- 禁止范围与新增授权条件：review/集成期间不得直接改 `src/infrastructure/providers/ocr_local.py` 语义面；如需引擎构造参数变更（见限制②③），立新 Task 由 Codex 定范围。
- 交付物：DSH review 报告（`verification/M2-OCR-PADDLE3X-1/dsh-review-r1.*`）+ Codex 集成验证记录。
- 验证命令、环境与完成 Gate：上表验证命令全数复现；Gate=协作协议标准（DSH 0xP0/P1/P2 + 集成后基线不回退）。
- 可直接转发给 Agent 的指令：

  > 对分支 `agent/zcode/M2-OCR-PADDLE3X-1`（worktree `G:/CODEX/New Manga.worktrees/M2-OCR-PADDLE3X-1-zcode`，head `15ef29ab`）执行非作者 review：对象 `src/infrastructure/providers/ocr_local.py` 3.x 适配（bytes→ndarray、enable_mkldnn=False、双形状解析、numpy box 物化）与 `tests/providers/test_ocr_local.py`；证据在 `verification/M2-OCR-PADDLE3X-1/`（诊断 verdict=ALWAYS_EMPTY、e2e 页面级 OK）；复现命令见 `doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md` 验证证据表；禁改 src/tests，发现问题按协议出报告。

## 风险与遗留

1. **[TA3-B2 联动，需跟进] runner wrapper 输入约定**：本修复后生产 `recognize` 传给 engine 的是 ndarray。M2-TA3-B2（并行中）phase-2 runner 的 `build_wrapper().ocr(data)` 当前假设收到 bytes（内部 `np.frombuffer`+`imdecode`）。TA3-B2 在自己的 worktree/基线上不受影响；**其分支 merge 本修复后需一行适配**（`data` 已是 ndarray 时跳过 decode）。建议 TA3-B2 owner 在集成期处理，或 Codex 在 merge 顺序上协调（TA3-B2 先出交付、后统一适配）。
2. **[限制，超授权面，待决策] PP-OCRv5 det 对孤立小 crop 常检不出框**：页面级可检出的文本行，裁成孤立 crop 后单独推理常返回零框，且同一 crop 多次运行带不确定性（矩阵实证，`crop_matrix_probe.py`）。生产 OCR 的输入是 detect 步骤产出的 region crop——孤立 crop 再检测的可靠性需要引擎参数调优或 rec-only 模式决策。本 Task 构造参数授权仅 `enable_mkldnn=False`，未处理。登记给 D06 OCR 环节/阶段二质量 Task（`doc/contracts/**` 不在允许面，以此登记替代）。
3. **[质量观测，超授权面] 默认构造全预处理质量低于精简预处理**：默认构造（doc_ori/UVDoc/textline_ori 全开）页面级 mean conf 0.4086、preview 含乱码；TA3-B 冒烟同页精简预处理为 0.6871、文本正常。生产构造是否携带 `use_doc_orientation_classify=False` 等参数属引擎配置决策，需 D06/质量 Task 定（TA3-B wrapper 的精简构造可作起点）。
4. **paddleocr 3.x `ocr()` DeprecationWarning**（"Please use predict instead"）：生产保留 `ocr(ndarray)` 以兼容 2.x（2.x 无 `predict`）；若未来 paddleocr 移除别名需再适配（3.7.0 实测仅 warning）。
5. 测试基线已从 490+1 变为 **507+1**（新增 17 个 ocr_local 测试，0 回退）；主 venv 纪律保持——无 paddle 依赖引入，真实引擎验证全部在隔离 venv 手动执行。
