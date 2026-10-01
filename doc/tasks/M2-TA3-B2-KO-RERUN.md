---
id: M2-TA3-B2-KO-RERUN
title: "TA3-B2 ko qualification 重跑（用户裁决③：TILING+ALLOC 解锁后关闭 F1/F2）"
kind: qualification
status: done  # DSH r1 approved（有条件）→ 纯文档返修 R1-R11 全 closed @0ba046b8（50 万红线出处落盘/乘数上界化/--determinism-track 控件落地）→ 集成；§7 七项裁决移交用户

approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2, M2-DETECT-WEBTOON-TILING, M2-IMPORT-ALLOC-LIMIT, M2-TASKS-PRIMARY-SFX-GATE]
base_commit: f99a6c55
branch: agent/zcode/M2-TA3-B2-KO-RERUN
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-B2-KO-RERUN-zcode
---

# M2-TA3-B2-KO-RERUN：ko 侧 qualification 重跑

## 背景（用户裁决③）

TA3-B2 首跑 ko 9 case fail-closed 于 F1（ogkalu webtoon 0 候选）与 F2（Qt 256MB 导入上限）。两缺口已修复集成：TILING（5 页 tiling GATE PASS）+ALLOC（K07/K09/K10 导入 PASS）。**本 Task 必须在 M2-TASKS-PRIMARY-SFX-GATE 集成后启动**（pipeline plan 语义定稿后跑，避免重跑产物语义中途变更）。

## 交付（AC）

1. **AC1 重跑执行**：`experiments/M2-TA3-B/run_qualification.py` 重跑 ko 10 case（K01-K11、K19；含 K03/K06 吗——**不**，沿 case-selection 20 case 原名单的 ko 10）；ja 侧不重跑（无变化）。断点续跑语义沿用；region 策略默认无截断。
2. **AC2 结果登记**：逐 case 结果对照首跑（F1 六 case 现状/K07-K10 导入现状/K11 对照）；**诚实登记**：K19 无字页仍 fail-closed INVALID_INPUT（F4 口径未修，登记）；任何新缺陷 typed 归因。
3. **AC3 评测更新**：ko G1 CER 重算（新 OCR 结果对齐 SVG GT——TILING 后 region 几何变化，对齐脚本沿用 measure_cer.py）；SFX translation 统计（K11 的 SFX region 现经 policy=skip 应 SKIP——新增：`sfx.policy=translate` 的对照跑可选择性做一个 case 验证端到端 SFX 翻译可达性，预算内）；对白可读性工作表 ko 侧增量预填（DeepSeek 自评，预算控制）。
4. **AC4 报告**：`verification/M2-TA3-B/phase2/ko-rerun/`（summaries+评测）+ `ko-rerun-report.md`（vs 首跑对照表：F1/F2 关闭确认、CER 对比、Gate 逐项现状）；全链 Gate 现状如实（ja PASS 维持+ko 新现状）。
5. **AC5 成本与纪律**：DeepSeek key 沿用 env 注入零明文；**翻译预算控制**——ko region 总量可能数百（K01 检测解锁后 180 region），预估请求数/先行一个 case 试算后再全量；重试走生产语义；fail-closed typed；src/tests/契约零改动（发现缺陷登记）。

## 允许修改面

`verification/M2-TA3-B/phase2/**`（ko-rerun 产物+报告）、`experiments/M2-TA3-B/**`（如 run_qualification.py 需 ko-rerun 参数微调——逻辑零变更）、`verification/M2-TA3-B/quality-report.md`（追加 ko-rerun 节）、Task/Handoff。

## 禁改面

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、首跑产物（qual-*.json 首跑版本/quality-thresholds.md）、`doc/STATUS.md`、key 明文任何形态。

## 纪律

- 依赖序：**等 M2-TASKS-PRIMARY-SFX-GATE 集成 main 后启动**（编排会话负责时序，本 Task Owner 启动前自查 main HEAD 含该 Task）。
- directional 口径延续；阈值实测 vs 提案对照沿 quality-thresholds 双轨口径（确定性=相似度 Gate for remote）。
- 环境：融合 venv 方案 A 先例（phase2/env-manifest.txt）；TILING 语义下 detect 延迟预算 awareness（K01 ~20s/页 detect+全链）。

## 执行记录（ZCode，2026-10-02，status=in_review）

- **AC1 部分执行（纪律停跑）**：K02 试算全链完成（93 region=TILING qualification 同值、Run1 completed、export OK；Run2 46 region 携带 DeepSeek API 故障窗口 ~115 分钟的 typed PROVIDER_TIMEOUT，environment）+ K19（F4 预期 fail-closed 维持）+ K11 最小对照集（主 pass/sfx 对照/确定性复跑）。**K01/K04/K05/K07/K08/K09/K10 共 7 case 停跑**：试算实测每请求恰 1 target region（请求数≈2×region 数、≈607 est token/请求）→ 全量外推 63 万–209 万 est token > 50 万红线，按 AC5 纪律停止登记等裁决（`verification/M2-TA3-B/phase2/ko-rerun/budget-register.json`）。F2/ALLOC 的页级解锁确认（K07/K09/K10）因此仍无实测。
- **AC2**：逐 case 对照表见 [ko-rerun-report.md §2](../../verification/M2-TA3-B/ko-rerun-report.md)；K02=F1 解锁实证；K11 行为对照一致（2 空 OCR region typed 同型；run1 状态 completed→completed_with_failures=PRIMARY 语义定稿的预期差异，N3 登记）；K19 F4 维持。
- **AC3**：ko G1 CER 重算 n=6/median 0.0556/gate PASS，**6 行与首跑逐位一致**（OCR 层跨 run 确定性再证实）；SFX 主 pass n=1 SKIP 同首跑；`sfx.policy=translate` 对照=配置语义验证成功（生产 settings 键→region.sfx_policy skip→translate→gate 放行），但 K11 唯一 sfx region OCR 空、端到端不可达（素材缺口 N6）；可读性工作表 ko 增量预填 n=15（ai_mean 4.31，自评预填待用户终审）。
- **AC4**：K11 相似度 Gate（remote 轨）**FAIL——12/13 对逐位一致（median=1.0）、1 对语义等价合法重译 min=0.4615<0.70 触发 min 腿**；归因=CALIB 局限 8 的"词面口径保守误报"形态首次自然实测，Gate 口径是否修订移交用户裁决（ko-rerun-report §4/§7.3）。export sha 为 mock 轨口径仅附报。
- **AC5**：实际消耗 ≈347 次成功请求 ≈20.4 万 est token（估算口径计量 proxy；红线由外推触发非实际消耗）；key 零明文（dump_json scrub 沿用）；src/tests/contracts/packaging/apps/首跑产物/thresholds/STATUS 零改动。
- 产物：`verification/M2-TA3-B/ko-rerun-report.md` + `verification/M2-TA3-B/phase2/ko-rerun/**`（summaries ×5、summaries-sfx、determinism、ocr、translate、budget-register.json）+ `experiments/M2-TA3-B/{run_qualification.py 微调, ko_rerun_similarity.py, ko_rerun_k11_driver.py, ko_rerun_readability_increment.py}`。Handoff：`doc/handoffs/M2-TA3-B2-KO-RERUN-<head>.md`。

## 执行记录续：DSH r1 返修（ZCode，2026-10-02，status 维持 in_review）

> 上节 AC1/AC4/AC5 行保留 r1 被审头（`36971e97`/`0001d68c`）时的原文作证据；下列口径更正以本返修后的报告为准。

- **Review 结论**：DSH r1 = **approved（有条件）**——0×P0/P1；3×P2（R1 红线出处/R2 成本乘数/R3 判轨控件）+ R4-R11 精度修补；DSH 独立复算全部数字成立、停跑方向保守成立。报告：`G:/CODEX/New Manga.task-envs/M2-TA3-B2-KO-RERUN/dsh-review-r1.md`。
- **返修形态**：纯文档修订 + R3/R10 runner 微调（均在允许面内），原 head `0001d68c` 之上追加；禁改面（src/tests/contracts/packaging/apps/首跑产物/thresholds/STATUS）零 diff；**停跑决策与全部 Gate 判定不变**。
- **R1（口径更正）**：「50 万 est token 红线」非任务书原文（AC5 只写"预估请求数/先行一个 case 试算"），登记为**编排会话停跑指令数值、无任务书/用户裁决原文背书**；仓库现行纪律=phase2-plan.md:192「数万 token 量级，超预期即停并登记」。停跑依据按现行口径重述（外推 63 万–209 万对两种口径均远超线，决策不变）；「50 万是否追认为新口径」列报告 §7.5 裁决项（若认可需落文，集成方执行）。
- **R2（口径更正）**：「请求数≈2×region 数」改**上界假设**（K02 实测 140/93=1.51×、K11 19/13=1.46×）+ 敏感性行（1.51× → 已知 region ≈47.6 万）+ K11 Run1 仅 8 次调用（13 region/11 有文本）登记为 open 异常（报告 §6 N4 修订）；63.2 万归属更正（=521 region 含 K11，仅五 webtoon 页 508→61.7 万）。
- **R3（推荐项执行：控件落地）**：thresholds §5 尾注要求的 `--determinism-track remote|mock` 显式记录 + 声明与 provider 绑定不一致 fail-closed 落地——`run_qualification.py` 装配前校验（矛盾声明 FATAL exit 2，干跑已验证不触 key/weights）+ report/summary 落 `determinism_track`；`ko_rerun_similarity.py` 计分前按两份 summary 的 provider 绑定判轨（unknown/双轨不一致/声明矛盾均 fail-closed）+ JSON 落 `determinism_track` 字段；K11-similarity.json 带判轨字段重新落盘，**全部数值逐位不变**。
- **R4-R11**：R4 归因链改 BACKFILL→PRIMARY（+`service.py:1054`/`projection.py:336` 终态路径与 run1 步表指纹）；R5 补 K11 未触发 tiling（1.383<4.0）限定；R6 计量口径改"成功 `translate()` 调用数"+retry 盲点（"347 次成功请求"相应标估计：metered 197/119k + 未计量 attempt-1 ~140）；R7 §7 逐项补成本/覆盖/Gate 后果并把 F1 关闭口径、F2 页级必要性拆独立决策点（§7.3/§7.4）；R8 N7 证据标注仓库外仅登记 + 新增 N8（qual-report.json 为覆盖型输出、非 run 级 roll-up）；R9 时间戳 UTC 更正+「12/13 逐位一致」改 raw 口径 11/13+1 对仅空白差+sfx gate 放行改语义推断；R10 metered fork 补回 provider-id 漂移守卫；R11 §4 补语义等价判定依据（Owner 单标注者自评、无独立第二审，列 §7 附件）。
- 逐条落点明细：handoff「r1 返修记录」节（`doc/handoffs/M2-TA3-B2-KO-RERUN-36971e97.md`）。DSH NOT_VERIFIED 运行时项（git 拓扑/首跑产物哈希/key 全库扫描/离线复算/三套件集成门）留集成方执行。
