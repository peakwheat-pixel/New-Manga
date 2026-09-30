# 独立静态 Review — M2-DOCTR-QUAL-C4（非作者，DSH）

## Verdict
**approved_with_conditions** — 测量与口径核验全部通过（Gate 三项数值与结果 JSON 逐项一致、与 QUAL-RUN 基线引用一致、冻结口径无越界、脚本确为 import 复用且基座逻辑未变），但 §7 的"无剩余收益空间/不值得投入"表述强于 §5 自设前提（R1），且粒度成分、抽检方案、版本/许可证据、复现证据四处披露不足，须在结论被引用为路线裁决依据前闭合。

关于本次审查方式的限制（不影响结论，但须登记）：沙箱完全禁止执行命令（`SetNamedSecurityInfoW failed (Win32 5)`），web 检索端点亦 401 失效，故为**纯静态审查**；权重 sha256 无法重算、`git diff` 无法复跑。我以本地 HF 缓存元数据、主仓库集成副本对照、以及 per_region 逐条回读作为替代证据（见 R12、AC5）。

## Findings

**R1（P1）结论语气强于自身前提：§7.1 "没有剩余收益空间" 与 §5.2 待抽检限定冲突**
文件/位置：`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md` §7.1（L102）、§5.2（L74）；`doc/handoffs/M2-DOCTR-QUAL-C4-19d1772e.md` L13、Known limitations #2（L71）。
问题：§5.2 明确"PASS 可能部分来自框风格与伪 GT 标注风格对齐""解读为真实达标前需人工抽检"；§7.1 却无条件断言"C4 fine-tune 主线不值得投入""没有剩余收益空间"。若 §5.2 的同源性风险成立，则"无剩余空间"恰恰是必须由抽检才能证成的命题，当前是结论超出前提。
建议：把 §7.1 改为条件式（"在冻结口径内无剩余收益空间；真实目标下的剩余空间待 §7.2 抽检结论后确认"），或在 §7 开头显式声明"§7.1–7.3 均以 §5.2 抽检通过为前提"。

**R2（P2）§7.2 抽检建议未具体到可执行**
文件/位置：报告 §7.2（L103）、§5.1（L73）；Handoff L71/L80；对照 `qualification-report.md` §7 C1（L110）。
问题："8 个未匹配 region + FP 抽样（~30 框）"缺少：①FP 抽样框（108 个 block_coverage FP 中怎么选、跨哪些 region、随机种子/分层规则）；②抽样单位定义（block 还是 raw box）；③遗漏对本结论最关键的层——**mean coverage 贴合样本**（coverage 略高于 0.5 的匹配，用于区分"真匹配"与"边界对齐"）与 **n_gt=0 但产生 FP 的 95 个 region**（纯盲区候选）。而 QUAL-RUN §7 C1 反而写了"全部 severe region + ~35 random GT-bearing regions"的分层写法。
建议：写成可交接的审计协议——分层定义、每层配额、随机种子、分类枚举（真实文字漏检 / 伪 GT 噪声 / 盲区 FP / 粒度不达标）、输出字段（region、框、判定、依据）。

**R3（P2）"同一 merge+评分路径 ⇒ detector 单变量对照"缺关键量化：本候选的生产合并非"复用"而是近乎空转**
文件/位置：报告 §2 L44、§4 L67–69；JSON `results-formal-manga_rt_detr_v2-cuda-seg05.json` L66–119（`raw_strict.n_det=1021`、`block_strict.n_det=990`、`block_coverage.n_det=990`、`n_gt=917`）及 per_region 例证（K04 r1：`n_gt=11 / n_det_raw=11`；K04 r18：`13 / 12`；L2184–2197、L2352–2365）。
问题：合并只把 1021 个原始框缩到 990 个（−3.0%），说明该模型的原始输出**已是块级**、与伪 GT 粒度基本 1:1；而 fast_base 是词级框（QUAL-RUN §2：3067 FP、3505 检测块）。代码路径确实同一，但**实际处理不等价**：候选绕过了对 docTR 最具破坏性的 word→block 合并环节。因此 +48.4 pp 不是 merge 中性的"检测质量"增量。
建议：在 §4 补 1021/990/917 三个数字与"本候选合并近乎空转"一句，并在 §7 明示该 PASS 的含义是"现成模型在**生产块级消费口径**下达标"，而非"检测质量高 48 pp"。

**R4（P3）§2 算术与"唯一"表述不准**
文件/位置：报告 §2（L42）。
问题："0.92 需要相对 fast_base（0.4776）+48.4 pp 的提升"错误——0.4776→0.92 只需 **+44.2 pp**（`qualification-report.md` §1 L23 正是 44.2），+48.4 pp 是本候选实达增量（0.9618−0.4776）。同句"唯一一个越过 0.92 Gate 的候选"亦偏宽（C2/C5 从未运行）。
建议：改为"0.92 需较 fast_base +44.2 pp；本候选实达 +48.4 pp"，"唯一"限定为"已实测候选中唯一"。

**R5（P3）AC1"注明来源 URL/版本/获取日期"缺"版本"：未登记 HF revision**
文件/位置：报告 §1（L22–30）、JSON `candidate`（L6–22）。
问题：只登记了文件 sha256 与日期，未记 revision。本地缓存已持有 `16e8a622f91fabc6b5b65c96d32d1183f8843546`（`.cache/huggingface/trees/16e8a622….json`），应直接写入。另：同一 revision 还含 `detector.onnx`(168,481,531 B)、`detector_int8.onnx`、`detector-v4-s_int8.onnx`（tree L16–35），选型理由未说明为何取 transformers 检查点、对应哪个模型版本（v4 ONNX 是否为更新版本）。
建议：补 revision commit，并加一句 ONNX 变体存在性说明与不采用理由。

**R6（P3）许可证据未入库，AC1 的硬纪律当前不可复核**
文件/位置：Handoff §选型表（L33–34）、报告 §1（L17–20）、权重 tree（仅 config/preprocessor/README 396 B + safetensors + onnx，**无 LICENSE**）。
问题：Adopt（Apache-2.0）与 Reject（GPL-3.0）均为 2026-09-30 的 API/模型卡查询结论，仓库与权重快照内均无许可工件；pinned revision 的文件清单本身不含许可文件。
建议：把 HF 模型卡/API 元数据与 GitHub `license.spdx_id` 响应快照（或哈希+抓取时间）存入 `verification/M2-DOCTR-QUAL/qualification/`。

**R7（P3）复现核验证据仅在 gitignored 外部路径，正式运行无 raw 日志**
文件/位置：报告 §8（L133）、Handoff AC4 行（L62）；对照 `qualification-report.md` §3 artifacts 表（提交了 `raw/*.log`）。
问题："24/24 entries 0 diff" 与三次 EXIT=0 只能凭 Handoff 自述；`results-repro-check24.json` 不入库。可佐证的部分：JSON 的 `elapsed_seconds` 38.89/23.51/22.69 与报告 38.9/23.5/22.7 一致。
建议：补一个小的 committed 证据文件（命令、两个 JSON 的 sha256、逐字段 diff 计数与范围），并保留三次正式运行的 stdout/EXIT 日志。

**R8（P3）JSON 内 `reproduce_command` 在声明的 Windows 平台不可原样执行**
文件/位置：三个 results JSON 的 `reproduce_command`（formal L64）。
问题：使用 POSIX 前缀 `PYTHONPATH=src "…python.exe"`，在 PowerShell/cmd 下不成立（QUAL-RUN 用 `$env:PYTHONPATH = "src"`）；且未含 CWD 与 `--limit` 变体写法。AC4 要求"复现命令入报告"，当前是配方而非可执行命令。
建议：改为 `$env:PYTHONPATH="src"; & "…python.exe" …`，或双写。

**R9（P3）新增脚本文档与实物/依据不一致**
文件/位置：`experiments/M2-DOCTR-QUAL/eval_detection_manga.py` L46–56（Usage 的 `--out` 为 `results-c4-manga-rt-detr-cuda-seg05.json`，与正式产物 `results-formal-manga_rt_detr_v2-cuda-seg05.json` 不同名）、L156–160（`--conf-threshold` help 称 "0.5 = formal, aligned with the docTR detection default"）。
问题：生产调用 `src/infrastructure/providers/detection_doctr.py` L226–233 未传任何 box/bin 阈值，"docTR detection default = 0.5" 在仓库内无依据（docTR 预测器默认并非 0.5）。
建议：改为真实理由——"0.5 为保守取值（越低召回越高，故对 PASS 是保守方向），0.3 作敏感性附报"。

**R10（P4）两处参数处理小瑕**
文件/位置：`eval_detection_manga.py` L225（`supp_iou_thr = 0.3` 硬编码，未读 `thresholds.json.fp_attribution_iou_threshold`，值一致故风险低）；L203（`if args.limit:` 真值判断，`--limit 0` 会静默变全量）。
建议：前者从 `THRESHOLDS` 读取，后者改 `is not None`。

**R11（P4）`arch`/参数量声明无 pinned 产物依据**
文件/位置：`eval_detection_manga.py` L85–86、JSON L8/L23、报告 §1 L19。
问题：`config.json` 仅能证明 `RTDetrV2ForObjectDetection`、`model_type=rt_detr_v2`、backbone `rt_detr_resnet`（L5–23、L87）与 3 类 `id2label`（L66–78）；`r50vd` 与"42.9M params"来自模型卡，非快照元数据（tree 无参数量字段）。
建议：标注来源，或改为"backbone: rt_detr_resnet（模型卡称 r50vd）"。

**R12（P4，正面核验记录）权重指纹已获独立佐证；8 个未匹配 region 清单逐条正确**
证据：本地 HF 缓存 `model.safetensors.metadata` 第 2 行 etag = `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d`，与报告 §1 L27、Handoff L40、JSON L21 pin **完全一致**；tree 元数据 size 171,543,900 / 2,320 / 470 与报告声明逐一一致。提示后续复核者：`config.json.metadata`/`preprocessor_config.json.metadata` 第 2 行是 **git blob SHA-1**（非 LFS 文件），不能用它核对 sha256——二者不匹配属正常，不代表漂移。
另：8 个未匹配 region 已逐条回读确认为 `n_gt=1` 且 `tp_block_coverage=0`——K06 r36/r38/r48/r94（`n_det_raw`=0/0/0/0）、K07 r79（0）、K07 r109（**1**）、K08 r3（**3**）、K09 r14（0）。其中 K07 r109 与 K08 r3 并非"未检出"而是 coverage 不达标，§6 L93 仅称"未命中"未区分，抽检分类时须区分这两类。

**R13（P4，口径合规核验记录：无越界）**
核验项：`primary_layer=block_coverage`、生产 pad 6px 为正式、pad 抵消仅附报、Precision 在 JSON 中为 `gate:false` 且带 `reference:0.85`（L135–140）、`all_pass` 仅取三项 Gate（L151）、GT 盲区前提在报告 §2/§5 与 JSON 内多次标注（L42、L52、L139）；报告 L104–105 明示"本 Task 不宣称、不启动该集成""PASS 不构成对生产集成的推荐"；全文未见"生产集成可用"或"真实用户体验达标"类断言。唯一需修的是 R1 的措辞。

## AC 核验表

| AC | 判定 | 依据 |
|---|---|---|
| AC1 选型+受控权重 | **PASS（附条件 R5/R6）** | 一个候选完成全链：Apache-2.0 采用 / GPL-3.0 弃用理由登记（Handoff L33–34、报告 L17–20），权重 SHA-256 pin 且被本地 HF 缓存 etag 独立佐证、大小 171,543,900/2,320/470 全部对上，权重落 gitignored 外部路径不入库；但 revision commit 与许可证据未归档。 |
| AC2 适配评测 | **PASS** | `eval_detection_manga.py` 确属 import 复用（L69–80 复用 `match_greedy`/`blocks_to_rects`/`iou`/`sha256_file`/`THRESHOLDS`，L191–193 复用生产 `cluster_words_into_blocks` 且缺失即 fail-closed），三层评分/summary/verdict 与基座逐段同构；seg05 全量 511/511（JSON L62）。注：合并对本候近乎空转（R3）。 |
| AC3 对照报告 | **PASS（附条件 R1/R2）** | 报告 §2 Gate 逐项判定、§3 与 fast_base 0.4776/db_resnet50 0.6085 对照（均与 `qualification-report.md` 数值一致）、pad 抵消附报、§5 前提、§7 C1/C4 明确建议齐备；全部引用数值与三个 results JSON 逐项相符。 |
| AC4 可复现 | **PASS（附条件 R7/R8）** | 三个 JSON 均带 `manifest_sha256=4f16425a…`（与 QUAL-RUN 同一 manifest/GT）、`weights_sha256`、`reproduce_command`；报告 §8 有命令；CPU 降级路径如实标注未跑。条件：复现核验产物未入库、命令为 POSIX 写法。 |
| AC5 范围纪律 | **PASS（静态核验；git 级 NOT_VERIFIED）** | 新增物均落在 `experiments/M2-DOCTR-QUAL/**`、`verification/.../qualification/**` 与 Task/Handoff；主仓库集成副本 `eval_detection.py`（517 行，L184–201/371–400/494–517 逐行一致）与 `thresholds.json`（20 行逐行一致）同 worktree 版本，生产 `detection_doctr.py` 仍为 `MERGE_PAD_PX = 6.0`；因沙箱禁执行，`git diff --name-only 2e9f564d..HEAD` 未能复跑，故 git 级零改动未获工具级确证。 |

**推荐下一步（基于当前仓库状态）**：由 Codex（Integrator）把 R1/R3 的措辞与量化补丁退回 ZCode 出一个小修订 commit（限 `verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md` 与 Handoff 文案），同时将 R2 抽检协议、R5/R6 版本与许可证据、R7 复现证据合并释放为一个独立的小 Task；在 R2 抽检闭合前，采纳"释放 C1 抽检型审计、不释放 C4 fine-tune 主线、生产集成另行释放"的裁决是安全的。若需要，我可作为非作者 Reviewer 复看修订 commit。
