## Verdict
**approved_with_conditions** — r1 的 1×P1 + 2×P2 已实质闭合（R1/R3 closed、R2 框架达成），三个正式 results JSON 冻结未动、口径无回潮、许可与 revision 证据经本地 HF 元数据原件独立交叉印证；但**交付 hash 未登记**（实际 HEAD `76fc593f`，文档仍写 `19d1772e`，N1）与**§7.2 抽检所需框级数据依赖未声明**（N2）须在集成 / C1 释放前由集成方闭合。

复核方式（限制同 r1）：沙箱仍禁执行命令（`SetNamedSecurityInfoW failed (Win32 5)`），纯静态。本轮额外取得的**独立证据**：① `G:/CODEX/New Manga/.git/refs/heads/agent/zcode/M2-DOCTR-QUAL-C4` = `76fc593f37e8a5b0243796741c5dc580de72428f` 与 worktree `logs/HEAD` 全链；② 本地 HF 缓存 tree 元数据（revision 名、4 个 lfs_sha256、size）；③ `license-evidence-*.json` 三个原件；④ 主仓库集成副本；⑤ per_region 间接推导（`n_det_block: 0` 全量计数）。行为等价性已由我**静态论证**（r2 脚本相对 r1 仅 4 处非评分改动），不依赖作者的外部复查证据。

## 逐条核对表

| R | 判定 | 依据 |
|---|---|---|
| R1（P1） | **closed** | 报告 §7 L105 新增口径声明"§7.1-7.3 全部以 §7.2 抽检协议通过为前提；抽检未完成前本节结论只在该口径内有效"；§7.1 标题改"（条件式结论）"、正文 L109 写"在冻结口径内无剩余收益空间 / 真实目标下的剩余空间待 §7.2 抽检结论后确认"；Handoff L13/L75 与 Task L63/L76 同步限定。 |
| R2（P2） | **partial** | §7.2（L111-126）已给出 6 层（A1/A2/B1/B2/C/D）分母-配额-判定问题、4 类分类枚举、7 项输出字段、种子移交 C1 声明，框架达成；但见 N2（框级数据依赖仅对 C 层声明）、N3（D 层分母 95 vs 配额单位"零检测"实为 72）。 |
| R3（P2） | **closed** | 报告 §4 第 4 条（L73）：`1021→990（−3.0%）vs GT 917`、K04 r1 11→11 / K04 r18 13→12、docTR 3505 检测块对照、"合并近乎空转""绕过 word→block 环节""+48.4 pp 非 merge 中性的检测质量增量"；§2 L45、§7 L105、Handoff L13/L54 同步。脚本 docstring 未同步 → N4。 |
| R4（P3） | **closed** | L45："0.92 需较 fast_base（0.4776）**+44.2 pp**，本候选实达 **+48.4 pp**"；"**已实测候选里**第一个、也是唯一……（C2/C5 从未运行）"。 |
| R5（P3） | **closed** | revision `16e8a622f91fabc6b5b65c96d32d1183f8843546` 登记于报告 L26、Handoff L39、license-evidence L21/L55；该值与我独立读取的本地 HF 缓存 `trees/16e8a622….json` 文件名逐字符一致；ONNX 三变体不采用理由见报告 L32 / license-evidence §1.5。 |
| R6（P3） | **closed** | `license-evidence.md` 入库。HF API 摘录与原件 `license-evidence-hf-api.json` 逐字段一致（`sha`/`tags` 含 `license:apache-2.0`/`cardData.license`/`F32=42,861,209`/siblings 8 项）；`?blobs=true` 摘录的 4 个 `lfs_sha256` 与本地 HF tree 元数据**逐字符一致**；GitHub 原件 `key=gpl-3.0`/`spdx_id=GPL-3.0`/`pushed_at=2023-08-13`/`default_branch=master`/`archived=false`/`stargazers_count=379` 与摘录及"379 stars"口径一致。（快照 sha256 本身无法离线重算，但内容交叉印证的强度高于自证。） |
| R7（P3） | **partial** | 报告 L134 + Handoff L85 已登记为遗留、随 C1 Task 闭合，处置可接受；但未在本 Task 补 committed 证据，且理由"本 Task 范围（AC1-AC5 允许路径清单）未含该证据文件"**不成立**——AC5 允许路径含 `verification/M2-DOCTR-QUAL/qualification/**`，r2 本身就在该目录新增了 `license-evidence.md`。 |
| R8（P3） | **closed** | 报告 §8 L153-163 新增等价 PowerShell 命令（`$env:PYTHONPATH="src"; & …`），L165 声明 JSON 内 POSIX 字段不重写（与"正式产物冻结"自洽）。 |
| R9（P3） | **closed** | docstring L53 `--out` 已改为正式产物名 `results-formal-manga_rt_detr_v2-cuda-seg05.json`；L156-162 conf help 改为"0.5 是 PASS 方向的保守取值 / 0.3 为敏感性变体"，删除了无依据的 "docTR detection default" 说法。 |
| R10（P4） | **closed** | L205 `if args.limit is not None`；L227 `supp_iou_thr = THRESHOLDS["fp_attribution_iou_threshold"]`（值 0.3 不变，且 seg05 下 `attribution_available=False`，该分支不执行）。 |
| R11（P4） | **closed** | 报告 L19 + license-evidence §1.4 明确"**r50vd 与 42.9M params 为模型卡口径**"并以 HF API `safetensors.parameters.F32=42,861,209` 佐证；pinned `config.json` 仅证 `RTDetrV2ForObjectDetection`/`rt_detr_v2`/backbone `rt_detr_resnet`（与 r1 一致）。脚本 docstring 未标注 → N4。 |
| R12（P4） | **closed** | 报告 §6 L97-100 拆为"真未检出 6 个（`n_det_raw=0`）：K06 r36/r38/r48/r94、K07 r79、K09 r14"与"有检出但 coverage 不达标 2 个：K07 r109（1 框）、K08 r3（3 框）"，与 r1 逐条回读结果逐字吻合。 |

**回潮与污染核验（三项均通过）**：① 口径无越界回潮——L105 口径声明 / §7.1 条件式 / Handoff L13 / Task L76 一致，未见"生产集成可用""用户体验达标"类断言；② 三个正式 results JSON 未被改写——formal `generated_at=07:00:41`、`elapsed 38.89`、总行数 7309 与 r1 相同，padoffset `07:01:41`、conf03 `07:02:16` 均早于 r2 等价重跑 `07:24:42`；③ 与 r1 正面核验无冲突——权重指纹（`037930a8…`）、8-region 清单、口径合规记录在 r2 中被保留并写入报告 §1/§6/§7。另：`dsh-review-r1.md` 经比对确为我 r1 报告原文（Handoff L83 声称属实），`dsh-review-r2.md` 为空（本轮输出位，不存在预设结论）；`git log` 链由 worktree `logs/HEAD` 独立确认：`2e9f564d → ae66fbbd → 19d1772e → a19d2254 → 76fc593f`。

## 新增问题

**N1（P2）交付 hash 未登记，frontmatter 指向返修前状态**
实际 HEAD = `76fc593f37e8a5b0243796741c5dc580de72428f`（refs + worktree `logs/HEAD` 双证），但 `doc/tasks/M2-DOCTR-QUAL-C4.md` L7 与 L75、`Handoff` frontmatter L6 仍为 `delivery_head: 19d1772e…`；Handoff commit chain（L17-22）**未给出任何 hash**，且编号（第 3 条"r2 返修"、第 4 条"本 commit 回填"）与真实 4-commit 链（`ae66fbbd`/`19d1772e`/`a19d2254`/`76fc593f`）不吻合——真正的 handoff 回填 commit `a19d2254` 被漏掉。风险：集成方按 frontmatter 检出将拿到**未返修**状态（缺 `license-evidence.md`、报告为 r1 版），AC5 范围核对也会漏项。
建议：Task/Handoff frontmatter 更新为 `76fc593f…`，并在 commit chain 中逐条登记 hash。

**N2（P2）§7.2 的框级数据依赖只对 C 层声明，B/A 层同样依赖**
正式 results JSON 的 `per_region` 仅含计数（`case_id`/`region_index`/`n_gt`/`n_det_raw`/`n_bubble_dropped`/`n_det_block`/`tp_*`/`fn_*`），**不含任何框坐标或置信度**。因此 A2（4 框 vs GT 错位）、B1/B2（"按 conf 十分位分层比例配额"）、输出字段要求（`框坐标 xyxy` + 图像证据）在现有证据下**无法执行**；报告仅在 C 行注明"现有 results JSON 未存 per-pair coverage，需 eval 侧补 matched-pair 导出开关"，未对 A2/B1/B2 作同等声明。此外 C 层分母（coverage∈[0.5,0.7) 的对数）未知、未给"不足 20 对则全查"的 fallback，而 meanCov=0.9965 使该区间样本量存在不足风险；预览图当前仅 K01 前 12 张（默认 `--previews 12`），B/A/C/D 层的图像证据也需按目标 region 重生成。
建议：C1 Task 契约显式写入"在 `eval_detection_manga.py` 新增 FP 框级导出（xyxy+conf+层别）与 matched-pair 导出开关，**不改动已集成文件**"，并补 C 层分母与 fallback、按目标 region 生成图像证据。

**N3（P3）§7.2 D 层分母与抽取对象不一致**
D 行分母列写"95 个 `n_gt=0` region（其中 23 个产生 FP 已入 B2）"，配额却是"随机抽 10 个**零检测** region"，未定义"零检测"（`n_det_raw=0` 还是 `n_det_block=0`）。本次独立推导确认：全 JSON `"n_det_block": 0` 共 **78** 条 = 无 GT 零检测 **72** + 有 GT 零检测 **6**（K06 r36/r38/r48/r94、K07 r79、K09 r14），故 D 层实际分母为 **72**，而 B2 的 23 个 region（95−72）由此得到独立佐证、与报告一致。
建议：D 行分母改写 72，并定义"零检测 = `n_det_block=0`"。

**N4（P3）脚本 docstring 未同步 r2 结论**
`eval_detection_manga.py` L28-32 仍写 "the comparison is apples-to-apples up to the detector swap"，与报告 §4 第 4 条"代码路径同一但**实际处理不等价**、合并近乎空转"直接冲突；L13-14 仍无条件写 "r50vd backbone, 42.9M params"（R11 已要求标注模型卡口径）。Handoff L54 承诺"决策细节与理由在 docstring 与报告 §4 双处登记"，此处双处已不一致。
建议：docstring 补"代码路径单变量、合并负载不等价"限定与模型卡口径标注。

**N5（P3）Handoff Changed paths 清单漏项**
Handoff L24 的 `git diff --name-only` 清单只列 `eval_detection_manga.py`、三个 results JSON、报告、Task、Handoff，**漏列 r2 新增的 `verification/M2-DOCTR-QUAL/qualification/license-evidence.md`**（该文件在同段 L21、L45 被声明为 R6 交付物）。集成方按此清单核对范围会对不上。
建议：补入 license-evidence.md。

**N6（P4）Task 契约原文与实际架构冲突未更正**
Task L38 仍描述候选 2 为"ogkalu/comic-text-and-bubble-detector（HuggingFace；**YOLO** 气泡/文本检测）"，与 pinned `config.json` 证实的 RT-DETR-v2 矛盾（Handoff L34 已写对，但未点明契约原文有误）。
建议：在 Task 内加一行更正说明，避免后续引用契约原文者误判架构。

**N7（P4）B 层框数拆分未能独立重算**
`B1=78 框/49 region`、`B2=30 框` 依赖跨行算术，静态手段无法求和；本次已确认 `78 = 108 − 30` 与总 FP `108` 自洽、且 B2 的 23 个 region 分母已独立验证（见 N3），但 49 region 与 30 框本身仍属未复核。
建议：C1 冻结时随协议输出分层清单（region + 框计数 + conf），使后续复核可逐项对齐。
