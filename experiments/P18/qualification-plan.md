# P18 JA/KO 质量资格方案

**范围**：只对 P18 指定的 JA/KO 质量资格与真实 Core 切片负责；不改产品实现、Schema、测试或依赖。  
**执行基线**：用户指定 worktree `codex/P18-ja-ko-quality` @ `5a18b865ec34534c64bc719db37549f4f4ead27f`。Task 元数据初值写着 `7f09bca4a8cebe7e7dd91a81e375c84256a488d6`，与本次授权坐标不一致，按用户的固定 base 执行并在 Task 记录差异。  
**产品质量门槛**：未冻结。检测、OCR、翻译、无字页与复杂背景修复的产品发布判定保持 `BLOCKED_WAITING_EXTERNAL_DECISION`；下列实验阈值只保留其原有实验适用范围。

## 1. AC1：既有证据与五类口径缺口

治理文件路径核对：本 worktree 不存在 `doc/WORKSPACE_GOVERNANCE.md`；使用项目快照 `verification/PROJECT-ROADMAP-RELEASE/inputs/doc/WORKSPACE_GOVERNANCE.md` 中的 registry 规则，并将该快照 SHA-256 固定在 `verification/P18/source-pins.json`。实际素材 registry 的路径和 SHA-256 见 `verification/P18/material-registry.json`。此处记录路径差异，不修改全局治理文件。

P08 `SCOPE_DRAFT.md` 第 65 行冻结规则原文：`数值质量门槛尚未冻结：检测/OCR 真值、翻译相似度评测方式、无字页 F4 与复杂背景修复标准从既有报告逐项列出缺失，再在 P18 资格方案独立审查。不得编造统一“90%通过率”；BJ13 0.90 是当前检测阈值，不能当整个产品质量分数。`

| 类别 | 既有报告与已有口径 | 尚缺证据 / 不可外推处 |
|---|---|---|
| 检测 | `verification/M2-DOCTR-QUAL/qualification/qualification-report.md` 对 10 个 KO Cleaned Webtoon case、机器 `text_seg` pseudo-GT 使用 block coverage；user-ruling 的实验 gate 为 Recall ≥0.92、mean coverage ≥0.60、severe page-miss ≤0.05。Formal Recall=0.4776，整体实验 gate FAIL。`verification/M2-KO-TILE-CALIB/calib-report.md` 与 `verification/M2-DETECT-WEBTOON-TILING/qualification-report.md` 有切片/拼接与耗时观察。 | docTR GT 不是人工真值，SFX/背景字漏标；KO tiling 报告明确无逐框 GT。无覆盖 JA 竖排、振假名、手写/SFX 与无字页的代表性人工 GT。0.92 等是该冻结评测集的 detector gate，不能直接当产品通用门槛。BJ13 0.90 仍只是检测阈值，不能成为产品总分。 |
| OCR 真值 | `verification/M2-TA3-B/quality-thresholds.md` 记载 ja J46/J47 只有 partial SVG credits/结束卡 GT；ko K11/K19 SVG 有文本但无 bbox 对齐。`quality-report.md` 记录 ja G1 无可自动计分样本；ko G1 仅 n=6 幸存对齐，median CER 0.0556，且排除项含 CER=1.0 的真实错误，统计偏低。 | 缺少覆盖 JA 对白/竖排与 KO Webtoon 手写气泡的完整、独立人工核验框与逐 region 转录真值。ja CER ≤0.10/0.15、ko ≤0.20/0.25 是用户可撤销的初版提案；KO 实验数不能升格为发布门槛。 |
| 翻译相似度/质量 | `verification/M2-QUAL-DETERM-CALIB/calibration.md` 用字符级 `1-Levenshtein/max_len` 校准重跑稳定性，只有 K11 与 BJ02 两个 case；建议 median ≥0.95 且 min ≥0.70。`verification/M2-TA3-B/quality-report.md` 的对白可读性为忠实/流畅/语境三维人工量表，n=26，用户终审尚未完成；SFX 自动翻译 n=0。 | 相似度仅测同输入重跑的词面稳定性，不判断语义正确性。缺少足量、独立双语盲评的 JA/KO 标准译文与裁决程序；现有 0.95/0.70、3.5/80% 都不得作为 P18 产品 gate。 |
| 无字页 F4 | `verification/M2-TA3-B/quality-report.md` 的 K19（无字页）无候选；生产 detect 结果是 `failed/INVALID_INPUT`。F4 明确记录文档期望的“无 region 数据豁免”与 production terminal 状态不一致，待 Codex/用户裁定。 | 没有按语言/画风锁定的无字页样本及人工“确实无文字”真值，也没有可批准的 false-positive 定义/数值限值。ARCH-DOC 报告中的虚警 ≤2% 缺少 P08/D08 冻结来源，不能直接采用。 |
| 复杂背景修复 | `verification/M2-TA3-B/phase2/inpaint/inpaint-spot-check-note.json`、`quality-report.md` 与 `quality-thresholds.md §4` 明确 SimpleFill 只查执行正确及产物可渲染，复杂背景去字质量不在范围内、无数值 gate。D08 `AC-INPAINT-003/004` 要求记录 provider/model/router provenance，并按策略路由彩色 Webtoon。 | 缺少复杂背景/网点/渐变分层的 paired ground truth、盲评标签与 collateral-damage/残影标准；AC-INPAINT-004 是路由要求，不是画质阈值。ARCH-DOC 中 OCR 95/92、FPR 2% 等无对应 D08 冻结出处，不在 P18 擅自引用为 gate。 |

质量相关 D08 行为 AC（`AC-OCR-001..004`、`AC-TRANS-001..004`、`AC-INPAINT-001..004`、`AC-SFX-001..003`）用于定义行为和溯源，不自动生成数值质量门槛。未提出统一通过率，也未合并各指标为总分。

## 2. AC2：语言分开的样本、真值、指标与记录方案

| 维度 | JA | KO | 真值与方法 / 阈值来源边界 |
|---|---|---|---|
| 初始真实链切片 | 仅以 registry 对象 `sha256:9bbd38763fde3a45e0dc3af61647ee8097f1345653dce99c32759a58c6c499e1`（BJ02 已翻译 PNG）作运行链 smoke fixture；不是源页质量样本。 | 仅以 registry 对象 `sha256:c451815727ec24b64bfd7656fd7fe574879de4d9dc1d79013456f89cee22b7a2`（K11 已翻译 PNG）作运行链 smoke fixture；不是 Webtoon 质量样本。 | 许可为 private local verification only；派生图含既有叠字，不作检测/OCR/翻译精度分数或真值。不得重新获取 Manga109。 |
| 资格候选样本集 | 已有报告候选 J46/J47（P&C credits/结束卡）与 BJ family dialogue；分别保留 credits 和对白/竖排层，不混成单一比例。 | 已有报告候选 K11/K19（P&C 印刷体）及 K01–K10（Webtoon 长图）；印刷体与 Webtoon 分层，不互相代替。 | 开跑前只能从 workspace registry 固定对象 ID、source hash 与许可状态。无注册源图/无相应 GT 的 case 排除并记 `NOT_RUN`，不得重新下载补齐。现存 registry 对本次实际使用的 BJ02/K11 仅确认“派生测试素材、源权利继承、私有本地验证”；不扩大其许可。 |
| 检测 | 同一份 JA source page 的人工 polygon GT；报告 page/region recall、coverage 与误检样本。 | 分别使用 Webtoon 与 P&C 印刷体人工 polygon GT；Webtoon 报告 tile seam 合并前后关联，不以 tiling 候选数代替召回。 | 复用 M2-DOCTR detector 指标作为可比指标；0.92/0.60/0.05 只作为 M2-DOCTR-QUAL 的历史实验 gate。新的 JA/KO 产品门槛未冻结，需用户决定。 |
| OCR | 日文字符归一规则固定后算每 region CER，并保留 bbox、脚本方向、GT 来源等级与被排除行。 | 韩文同口径算 CER，分别报告 SVG 人工 bbox 对齐子集和 Webtoon 人工誊录子集。 | 真值来自原生文字层时记录文本与 bbox 是否对齐；AI draft 只作预填，必须人工核对后才作为 GT。0.10/0.15/0.20/0.25 仅为 M2-TA3-B 初提阈值，JA/KO 发布门槛待裁决。 |
| 翻译 | 按 `reading_order` 对齐源句、译句；保存双语盲评（忠实、流畅、语境）逐项分与仲裁记录；另报重跑稳定性。 | 同法独立建 KO 层，标注长图跨气泡上下文及 SFX 策略；SFX n=0 时只登记，不判通过。 | `0.95/0.70` 仅为 n=2 字符相似稳定性校准建议，不等同语义质量；三维人工评分建议只作为 worksheet，产品阈值须用户裁决。 |
| 无字页 | 独立抽取已许可 JA 插画/无字页并由两人确认无文本；保留原图 hash。 | 独立抽取已许可 KO Webtoon/P&C 无字页并双人确认无文本。 | 每页报告 FP region 数、是否误触发 OCR/后续阶段、原始 artifact hash。错误率分母为确认无字页数；F4 production 状态语义及可接受 FPR 未冻结，不先判产品 PASS。 |
| 修复 | 对气泡白底、网点、渐变/线稿背景分别留原图、mask 与输出，盲评残影/误伤。 | 同分层并加彩色 Webtoon 背景与 tile seam；记录 router/provider/model/理由。 | 先测可复核的逐图观测和成对人工判读，不设通用图像相似度指标或阈值；是否达到发布可接受档由用户决定。 |

每次语言独立运行固定记录：`run_id / task_id / step_run_id / target_id / sample_id / source_sha256 / GT reference+SHA / git HEAD / Python 与依赖版本 / OS / CPU / GPU+driver / provider_id / model+revision+weight SHA / options / device / endpoint_type+provider+redacted URL+protocol / started_at+ended_at / raw stdout+stderr / process exit / typed error / output artifact SHA`。API key、Credential、Authorization header 一律不入日志；若 endpoint 为远程，记录是否上传、目标语言和数据范围，执行前先确认许可边界。当前 blocked 切片不调用远程翻译 endpoint。

## 3. AC3：逐步 terminal 与产物一致性

判别以生产 `PipelineRunStatus`、`PipelineTaskStatus`、`StepRunStatus`、`PlanDecision` 和 SQLite 持久化投影为准（`src/domain/tasks/models.py`、`src/application/tasks/service.py`）。每个 scope/target 绑定 `run_id + task_id + target_id + unit_id + step_type + decision + reason + step_run_id`；记录状态、错误码、时间、`StepRun.output`、`StepResult.outputs/revision_updates`、被提交 revision/artifact ID 与文件 SHA-256。审计者按外部采集顺序记录证据，并同时读取 fresh Run/Task/Step projection 与 SQLite 记录核对；不得假定产品存在未定义的事件序号字段。

| Pipeline step | `COMPLETED` 必须核对的产物/引用 | terminal / 失败条件 |
|---|---|---|
| `detect` | detector 输出 region 集合、关联 page/target、几何与实际提交的 region IDs；每个后继 region Task 应从本次 detector 输出扇出。 | Run/Task/Step 完成但 region 集为空且无显式合法解释、region 集合与持久化 projection 不同、或错误 region 被后继引用，即失败；合法无字页语义仍待产品裁决。 |
| `ocr` | 每个 region 的 OCR 文本 revision 与 region ID、语言/脚本元数据；检查 revision 当前指针与文件/数据库内容一致。 | 缺少某个计划 region 的 OCR 输出、输出指错 region、或 status/revision pointer 不一致，即失败；显式 skip 需有有效 `PlanDecision` 与 reason。 |
| `translate` | 每个源 region 的译文 revision、目标语言和 reading-order 对应；核对锁定/人工修改对象未被覆盖。 | 译文缺失/错配、锁状态被绕过、或未计划 region 被改写，即失败。翻译语义质量需另按人工盲评，不能从 terminal PASS 推出。 |
| `segment` / `mask_refine` / `inpaint` | 实际 mask/provider/model/router provenance；Clean revision 与输入 translation/mask lineage 对应，文件存在且 SHA 与 revision 记录相符。 | Clean 缺失、使用错误输入/路由或 status 指针不一致即失败；“文件能打开”只证明可渲染，不证明去字质量。 |
| `render` | Rendered 输出与正确 Clean/Translation revision、target 和输出格式关联；独立读取产物并核 hash。 | 导出文件存在但引用旧 revision、丢页/错序/错 target 或持久化 output 缺失，均失败。 |
| `export`（命令级结果） | 命令的格式、目标范围、文件路径与 SHA-256。 | export 命令成功只记自身成功；不能填充或覆盖 PipelineRun/Task/Step terminal 证据。 |

| 观察到的终态 | 一致性条件 | 失败判定 |
|---|---|---|
| `PlanDecision.SKIP_VALID / SKIP_LOCK / SKIP_POLICY` | 计划/Task 中 decision 与 reason 一致；unit 计入 terminal；没有伪造成功 StepRun 或新 artifact。 | 产物变更但仍记 skip；缺 reason；terminal unit 计数不符。 |
| `StepRunStatus.COMPLETED` | 每一成功 step 都有应有的 output；输出引用的 revision 属于正确 target/type，文件存在且 SHA 与持久化值相同；fresh projection 与 DB 一致。 | status completed 但 output/revision/文件缺失或指向错误对象；产物 hash 漂移。 |
| `StepRunStatus.FAILED` / `PipelineTaskStatus.FAILED` | 保存非空 typed `error_code` 与失败 step；失败输出不被标为当前有效 artifact。 | 失败无错误码；DB 与 projection 状态不同；失败产物被冒记为完成。 |
| `PipelineTaskStatus.BLOCKED` / `PipelineRunStatus.BLOCKED` | blocked reason/依赖可复核；未运行后继阶段，不增写 revision。 | blocked 后继仍被执行或任务被假记为成功。 |
| `PipelineTaskStatus.CANCELLED` / `PipelineRunStatus.CANCELLED` | 控制动作与事件/终态一致，未提交步骤不出现当前指针推进。 | stop/cancel 记录与 Run/Task terminal 不一致，或未提交写入被引用。 |
| `PipelineRunStatus.COMPLETED_WITH_FAILURES` | 至少一个 Task failed 且其余 Task/Step 的成功/失败终态、产物分别对账。 | 有失败却只用 export 成功声称整条链通过；或失败列表与 DB 不一致。 |
| `PipelineRunStatus.COMPLETED` | 无 fatal/cancel/blocked/failed task，所有已计划 unit 终止；成功输出与 skip reason 逐项相符。 | 有非终态 unit、失败/blocked task、遗漏输出或状态投影不一致。 |

`export OK` 仅能证明 Export 命令自身输出，不证明 PipelineRun/Task/StepRun 已 terminal，也不证明 artifact pointer 正确；必须逐 target 读取 terminal projection 和 artifact lineage。现有 `StepRunStatus` 没有 `skipped`，skip 由 plan decision 与 Task 状态表达，不能虚构 StepRun。F4 的“检测 0 region”到底应记录 failed 还是 data-exempt success 是既有明确待裁决项；P18 不覆写产品语义，按实际生产状态记录，作为未决 Gate。

## 4. AC4 与 AC5 运行安排

素材只引用 `verification/P18/material-registry.json` 中两个已登记 private-local 派生 PNG；不复制进仓库，不请求网络，不重新获取 Manga109。原始资产 SHA 按 workspace registry 核对。两条切片命令由 `experiments/P18/run_core_slice_probe.py` 通过生产 Core JSONL sidecar 执行，Core data root 各自隔离在 `verification/P18/raw/{ja,ko}/data/`。不使用 `acceptance_bridge`、mock provider 或旧 PySide/QML pipeline。

原始结果、child process exit code 与 request-level typed error 分开记录。即使 sidecar 进程退出码为 0，也不能据此认定阶段成功；必须查看每个响应、Run/Task/Step terminal 与产物。遇到缺模块/模型/endpoint/输入 IPC 时保留失败原文，将后继 stage 记 `BLOCKED`，不回放历史 PASS。

## 5. 结论边界

P18 当前只确定可复核的指标定义、证据字段、现存缺口与 terminal 对账方法；本文件没有设定产品发布阈值。需要发布口径裁决的指标保持 `BLOCKED_WAITING_EXTERNAL_DECISION`。最小真实切片若因 runtime/provider 缺失停在中途，AC5 就是 `BLOCKED`，不能由历史 M2 证据或单独导出结果替代。
