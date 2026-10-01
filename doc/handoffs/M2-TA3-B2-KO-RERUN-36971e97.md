# Handoff：M2-TA3-B2-KO-RERUN — ko qualification 重跑（试算+最小对照集交付，7 case 预算停跑待裁决）

- owner：ZCode · 交付头：`36971e97` · 分支 `agent/zcode/M2-TA3-B2-KO-RERUN`（base `87f61d8b`=PRIMARY-SFX-GATE close，任务书 base `f99a6c55` 之上经 release commit `1c3ac590` 释放）· worktree `G:/CODEX/New Manga.worktrees/M2-TA3-B2-KO-RERUN-zcode`
- Task：[M2-TA3-B2-KO-RERUN](../tasks/M2-TA3-B2-KO-RERUN.md)（status=in_review）· 重跑报告：[ko-rerun-report.md](../../verification/M2-TA3-B/ko-rerun-report.md) · 首跑报告增补节：[quality-report.md §10](../../verification/M2-TA3-B/quality-report.md)
- commit 拓扑：`87f61d8b`(base) → `36971e97`(implement：runner 微调+3 实验脚本+ko-rerun 产物+报告) → 本 handoff commit（Task 回填+handoff）

## 交付结果

**交付形态**：AC1 试算先行（K02）→ 试算实测触发任务纪律的 50 万 est token 预算红线 → 按纪律停止全量、完成零成本/低成本的最小对照集（K19/K11）→ 逐 case 对照、评测更新、确定性复跑、报告与预算登记全部落盘。**7 个 case（K01/K04/K05/K07/K08/K09/K10）未跑，等用户裁决范围（§下一任务建议）**。

| AC | 状态 | 一句话 |
|---|---|---|
| AC1 重跑 | 部分交付（纪律停跑） | K02 试算全链完成（93 region、export OK）；K19+K11 最小对照集完成；7 case 停跑：外推 63.2 万–209 万 est token > 50 万红线（仅 TILING 已确认五页就 63.2 万） |
| AC2 对照 | 已交付（对照范围=已跑 case） | K02=F1 解锁实证（0→93 region）；K11 行为一致（2 空 OCR region typed 同型；run1 状态差异=PRIMARY 语义定稿预期）；K19 F4 维持；K01/K04/K05/K08/K07/K09/K10 待裁决后补 |
| AC3 评测 | 已交付 | ko G1 CER n=6/median 0.0556/PASS，6 行与首跑逐位一致（OCR 跨 run 确定性再证实）；SFX 主 pass n=1 SKIP；`sfx.policy=translate` 配置语义验证成功、端到端不可达=素材缺口；可读性 ko 增量预填 n=15（ai_mean 4.31，自评预填） |
| AC4 报告 | 已交付 | ko-rerun-report.md（vs 首跑对照/Gate 逐项现状/裁决清单）+ quality-report.md §10 索引节；确定性=K11 相似度 Gate **FAIL**（1/13 合法重译误报 min 0.4615，median=1.0——CALIB 局限 8 形态首次自然实测） |
| AC5 成本纪律 | 已交付（红线登记） | 实际 ≈347 成功请求 ≈20.4 万 est token（估算口径计量 proxy）；budget-register.json 登记外推/停跑/恢复/成本；key 零明文（dump_json scrub） |

变更路径：`experiments/M2-TA3-B/run_qualification.py`（新增 opt-in `--sfx-policy`（生产 settings 键 `sfx.policy` + AC6 同序 re-assemble）与 `--meter-translation`（透传计量 proxy）；默认行为零变更）+ 新增 `ko_rerun_similarity.py`（相似度 Gate，复刻 CALIB 方法）/`ko_rerun_k11_driver.py`（API 故障弹性驱动）/`ko_rerun_readability_increment.py`（ko 增量预填）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 试算 K02 | `run_qualification.py --case K02 --out-dir …/ko-rerun/summaries --pixel-root …/ko-rerun-pixels --meter-translation` | 融合 venv（env-manifest.txt 先例）@ `36971e97`；DeepSeek remote | 93 region / Run1 completed 1848.5s / Run2 completed_with_failures（46 region API 故障 typed）/ export OK 5,069,825B / 计量 140 请求 84.9k est token | `phase2/ko-rerun/summaries/qual-K02.json` |
| AC1 K19 | 同上 `--case K19` | 同上 | detect EMPTY→run2 SKIPPED(data)、run1 COMPLETED_WITH_FAILURES(INVALID_INPUT)=F4 预期维持 | `summaries/qual-K19.json` |
| AC2/AC3 K11 主 pass | `ko_rerun_k11_driver.py` step1（API 恢复自动执行） | 同上 | 13 region/11 翻译/2 空 OCR region term_extract INVALID_INPUT 同型复现/export OK | `summaries/qual-K11.json` |
| AC3 sfx 对照 | driver step2（`--sfx-policy translate --suffix .sfx-translate`，独立 out-dir/pixel-root） | 同上 | region.sfx_policy skip→translate（生产 settings 键生效）；sfx region OCR 空→端到端不可达（素材缺口） | `summaries-sfx/qual-K11.sfx-translate.json` |
| AC4 相似度 | driver step3（`--rerun-check K11`）+ step4（`ko_rerun_similarity.py --case K11`） | 同上 | 13 对对齐校验全过（reading_order 集合+bbox 逐字段+全覆盖）；12/13 逐位一致、1 对合法重译 0.4615→Gate FAIL；export sha 不一致（附报） | `determinism/K11-similarity.json`、`summaries/qual-K11.rerun.json` |
| AC3 CER | `measure_cer.py --summaries-dir …/ko-rerun/summaries --ocr-dir …/ko-rerun/ocr` | stdlib 脚本 | ko G1 n=6 median 0.0556 P90 0.3333 gate PASS；6/6 行与首跑逐位一致；排除 7 行同口径 | `ko-rerun/ocr/cer-{regions.csv,summary.json}` |
| AC3 预填 | `ko_rerun_readability_increment.py` | DeepSeek 自评 3 请求 | n=15（K02 12+K11 3）ai_mean 4.31 range 2.0–5.0 | `ko-rerun/translate/dialogue-readability-ko-increment.csv` |
| NOT_RUN | K01/K04/K05/K07/K08/K09/K10 全链 | — | **预算红线停跑**（外推 63.2 万–209 万 est token>50 万，任务纪律要求停+登记等裁决）；K07/K09/K10 兼为 F2/ALLOC 页级确认的唯一途径 | `phase2/ko-rerun/budget-register.json` |
| key 纪律 | 全程 env 注入 + `dump_json` scrub 落盘 | — | 零明文（产物 grep 复核无 key；与首跑 R13 同机制） | 所有 JSON 落盘 |

## 接收方式

- 分支 `agent/zcode/M2-TA3-B2-KO-RERUN`，worktree `G:/CODEX/New Manga.worktrees/M2-TA3-B2-KO-RERUN-zcode`，delivery `36971e97`。
- 复现命令与长 run 纪律（ZCode 后台 Bash ~58 分钟强杀→detached 进程+落盘轮询）见 [ko-rerun-report.md §8](../../verification/M2-TA3-B/ko-rerun-report.md)。
- Reviewer 检查建议：①对照表与两代 summary 的数字一致性；②K11 相似度 Gate FAIL 的归因（合法重译误报 vs 真漂移——逐对数据在 K11-similarity.json）；③预算外推模型（requests≈2×region、607 est token/请求）与红线判定；④runner 微调的默认行为零变更（`--sfx-policy` 默认空、`--meter-translation` 默认 off）。

## 下一任务建议（必填）

- Task ID / 标题：**M2-TA3-B2-KO-RERUN 范围裁决后补跑**（无需新建 Task 文档——裁决落在用户对 §7 清单的选择，补跑在本 Task 分支继续，Reviewer=DSH 不变）
- 推荐 Agent / Reviewer：ZCode（补跑执行）/ DeepSeek Harness（非作者 Review）
- 推荐原因与前置依赖：AC1 全量 7 case 与 F2/ALLOC 页级确认被预算红线阻断；需用户先裁决 §7.1–§7.2（范围与 K02 是否干净重跑）
- Recovery point：本仓库、branch `agent/zcode/M2-TA3-B2-KO-RERUN`、base `87f61d8b`、delivery `36971e97`；worktree 已存在
- 允许修改路径：`verification/M2-TA3-B/phase2/ko-rerun/**`、`verification/M2-TA3-B/ko-rerun-report.md`（增量节）、`experiments/M2-TA3-B/**`（微调）
- 禁止范围与新增授权条件：src/tests/contracts/packaging/apps/首跑产物/thresholds/STATUS 零改动；翻译预算超 50 万 est token 的任何执行必须先获用户明示批准
- 交付物：补跑 case 的 summaries + 对照表增量 + 相似度 Gate（ko webtoon 家族若跑 K02）+ 报告增补
- 验证命令、环境与完成 Gate：同 ko-rerun-report.md §8；完成 Gate=补跑范围内逐 case 四件产物齐 + pipeline_failures 构成如实登记 + 预算登记更新
- 可直接转发给 Agent 的指令：**待用户对 ko-rerun-report.md §7（1: 7 case 范围与预算；2: K02 干净重跑 +113k est token；3: 相似度 Gate 合法重译口径；4: SFX 端到端素材路线）作出裁决后，由 ZCode 按 §8 命令在原 worktree/分支补跑并增量登记。裁决前无需执行。**

## 风险与遗留

- **预算红线是本 Task 的核心遗留**：ko webtoon 全链成本结构（每请求 1 target region、请求数≈2×region 数）使全量 qualification 的翻译成本与 region 总量线性相关；任何全量 rerun 前应先裁决范围/抽样策略（`--max-regions` 逃生阀会改变 Gate 分母口径，R7 披露义务随之触发）。
- K02 当前 summary 携带 API 故障伤害（Run2 46 region environment 失败；Run1/export 层完整、93/93 final 有译文）——F1 解锁结论不受影响，但"完整 pipeline_failures=0 的 ko webtoon 样本"尚不存在。
- K11 相似度 Gate FAIL 为保守方向误报（合法重译）；若维持现阈值，该形态会系统性出现在语义敏感的短译文上（ Gate 口径裁决点 §7.3）。
- F4（无字页 step=failed vs 文档豁免口径）维持未修（禁改面）；K19 每次重跑都会 typed fail-closed 计入 pipeline_failures。
- 环境事件存档：DeepSeek API 故障 ~115 分钟（budget-register.json api_outage_window）；ZCode 后台 Bash 58 分钟强杀（N7，长 run 必须 detached）。
- Git 外 scratch 残留：`%TEMP%/m2-ta3b2-K02-*` 两个目录（一次被强杀的尝试+首跑 K09/K10 遗留），无敏感内容，可手工清理。

## 实验附录

- 数据：ko 10 case 沿 `experiments/M2-TA3-B/case-selection.json`（sha256 逐 case 校验 OK）；SVG GT=首跑 `svg-gt-K11/K19.json` 只读副本。
- 模型/权重：ogkalu 三文件快照（`NEWMANGA_DETECTOR_WEIGHTS` 默认）+ chiqui7 yolo11s-seg onnx + manga-ocr + paddleocr-korean 3.x dual-side wrapper（`enable_mkldnn=False`）；TILING env 未设=冻结默认（4.0/1024/128/0.5）。
- Provider/Runtime：DeepSeek `deepseek-chat`（target zh，temperature=0）；Qt offscreen；单 venv 融合方案 A（`phase2/env-manifest.txt`）。
- 计量口径：experiments 层透传 proxy + `ports/translation/protocol.py::estimate_tokens`（CJK-aware）；**估算非 endpoint usage**（生产 client 不暴露）。
- 运行次数：K02 全链×2（一次被宿主强杀 + 一次完成）、K19×1、K11×3（主/sfx/rerun）+ 自评 3 请求 + 探针 ~7 次。
- 失败样例：K02 Run2 46 region（45×PROVIDER_TIMEOUT+1×INVALID_OUTPUT）；K11 2 region（空 OCR term_extract INVALID_INPUT=F3 同型）。
- Secret：无（key 仅 env，零明文入库）。

## r1 返修记录（DSH r1 = approved 有条件：0×P0/P1 + 3×P2 + R4-R11 精度；纯文档修订 + R3/R10 runner 微调，原 head `0001d68c` 之上）

DSH r1 报告：`G:/CODEX/New Manga.task-envs/M2-TA3-B2-KO-RERUN/dsh-review-r1.md`（DSH 独立复算全部数字成立、停跑方向保守成立）。返修=在原分支追加分诊 commit，禁改面（src/tests/contracts/packaging/apps/首跑产物/thresholds/STATUS）零 diff；**停跑决策与全部 Gate 判定不变**。逐条落点：

| ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R1 | P2 | 红线口径出处落盘：「50 万 est token」登记为**编排会话停跑指令数值、无任务书/用户裁决原文背书**（任务书 AC5 只写"预估请求数/先行一个 case 试算"）；仓库现行纪律=phase2-plan.md:192「数万 token 量级，超预期即停并登记」。停跑依据按现行口径重述（外推 63 万–209 万对两种口径均远超线，决策不变）；「50 万是否追认为新口径」列为 §7 裁决项 | ko-rerun-report.md §1.2（红线口径出处段）/§0 AC1/§6 N2/§7.5；budget-register.json `stop_line_provenance`+`extrapolation.verdict`+`stop_ruling.reason`；quality-report.md §10 |
| R2 | P2 | 「请求数≈2×region 数」改**上界假设**（K02 实测 140/93=1.51×、K11 实测 19/13=1.46×）；补敏感性一行（1.51× → 已知 region ≈47.6 万 < 50 万——「仅已知页即超线」表态不稳健，含 K07-10 时任何乘数仍超线、停跑不变）；K11 Run1 仅 8 次调用（13 region/11 有文本，三 pass 一致）登记为 **open 异常**（duplicate-text 不能完全解释） | ko-rerun-report.md §1.2 模型行+敏感性/§6 N4/§8；budget-register.json `note_requests`+`formula`+`k11_run1_anomaly`；quality-report.md §10 |
| R3 | P2 | **控件落地（推荐项执行）**：`run_qualification.py` 新增 `--determinism-track remote|mock`（装配前 fail-closed 校验：声明与 provider 绑定推断不一致 → exit 2）+ report/summary 落 `determinism_track` 字段；`ko_rerun_similarity.py` 计分前按两份 summary 的 provider 绑定判轨（unknown/双轨不一致/声明矛盾均 fail-closed）+ JSON 落 `determinism_track` 字段。干跑验证：`--determinism-track mock` → FATAL exit 2（不触 key/weights）；`remote` 通过；K11-similarity.json 已带判轨字段重新落盘（**全部数值逐位不变**） | experiments/M2-TA3-B/run_qualification.py（`infer_determinism_track`+CLI+main 校验+run_case 传参）；ko_rerun_similarity.py（判轨校验+payload 字段）；phase2/ko-rerun/determinism/K11-similarity.json；ko-rerun-report.md §4/§8 |
| R4 | P3 | N3 归因改 **BACKFILL→PRIMARY 两步定稿链**（BACKFILL R1 账目统一 → PRIMARY primary 纳入+页级决策链退役），补判别指纹（首跑 run1 步表页级 9 步 → 重跑 region 级 ~66 步）与终态计算路径 `service.py:1054`/`projection.py:336` | ko-rerun-report.md §2 注/§6 N3 |
| R5 | P3 | §3.1 补限定：K11 1200×1660（h/w=1.383）**未触发 tiling 阈值 4.0**、与首跑同路径，逐位一致属同路径复现预期；tiling 路径 OCR 稳定性本 run 未覆盖（K02 无 GT）；§5 表同步 | ko-rerun-report.md §3.1/§5 |
| R6 | P3 | 计量口径全文改「成功 `translate()` 调用数」（HTTP 数 ≥ 该值）；补 retry 盲点（production retry 在 provider 之外、默认 max_attempts=2，失败尝试与重发 input 未落计量，attempt_count 未落盘）；"无重试风暴"量级证据按调用数口径改述（≈92 次尝试/~115 分钟，方向保守） | ko-rerun-report.md §0 AC5/§1.1/§1.3；budget-register.json `note_requests`/`metered_requests_total` |
| R7 | P3 | §7 裁决清单逐项补**成本/覆盖/Gate 后果**（①107–209 万 ②随 N 线性 ③44–146 万 ④0；K02 +113k；F1 四页全链若必须 ≈50.4 万 @2×/37.8 万 @1.5×），并把 **F1 关闭口径**（detect 5/5+全链 1/5 是否足够）与 **F2 页级必要性**拆为独立决策点（§7.3/§7.4），新增**红线口径追认**裁决项（§7.5）与 Gate 三候选的后果（§7.6） | ko-rerun-report.md §7 |
| R8 | P3 | N7 证据标注**仓库外仅登记**（ko-rerun-logs/K02-rerun-attempt*.log 与 K11-driver-result.json 在 task-envs，仓库内不可复核）；`qual-report.json` 覆盖行为登记为新 **N8**（现内容=最后一次调用 K11 rerun-check pass，非 run 级 roll-up）+ §8 补产物索引 | ko-rerun-report.md §6 N7/N8/§8 |
| R9 | P4 | 精度修补五处：63.2 万归属（=521 region 含 K11；五页 508→61.7 万）；「≈347 次请求 ≈20.4 万」标**估计**（含未计量 attempt-1 ~140 次；metered=197/119k）；时间戳 UTC 更正（首版误标 +0800、`20:40Z+0800` 类非法标签修正）；「12/13 逐位一致」改 raw 口径 **11/13+1 对仅空白差**（ro10 raw=0.9474/normalized=1.0，JSON 已附 raw、正文补注）；sfx「gate 放行」改**语义推断**（无该 region translate step 实证） | ko-rerun-report.md §0/§1.2/§1.3/§3.2/§4；budget-register.json `generated_at_utc`/`probe_*`/`timestamp_note`/`minimal_set_still_executed.K11`/`known_only_note` |
| R10 | P4 | metered fork 补回 production provider-id 漂移守卫（`PROVIDER_OPENAI_TRANSLATION != PROVIDER_ID` → RuntimeError，与 translate_probe.reregister_env_resolver 同一断言）；不做 probe 帮助函数签名重构（避免扩大行为面） | experiments/M2-TA3-B/run_qualification.py `reregister_env_resolver_metered` |
| R11 | P3 | §4 补语义等价判定依据：Owner 对源文逐句对照两版译文（均完整传达"本以为没必要做到这种程度"，差异仅语气/自谦显隐），判定人=Owner 单标注者 directional 自评、**无独立第二审**，两版原文见 K11-similarity.json reading_order=5 对，列 §7 裁决附件供用户复核 | ko-rerun-report.md §4/§7.6 |

DSH NOT_VERIFIED 运行时项（1-9：git 拓扑/首跑产物哈希/key 全库扫描/离线复算/三套件集成门等）留集成方执行；R3 干跑（矛盾声明 exit 2）与 K11-similarity.json 离线再生成（数值逐位不变）已在本返修完成并记录于上表。
