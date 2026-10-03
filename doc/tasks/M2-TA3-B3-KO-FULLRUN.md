---
id: M2-TA3-B3-KO-FULLRUN
title: "ko 全量补跑（用户裁决④⑦⑧：7 case 全量+K02 干净重跑；F1/F2 关闭确认；相似度 known-limitation 落地）"
kind: qualification
status: done
approval: user_ruling_2026-10-02_seven_items
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2-KO-RERUN]
base_commit: 73252798
delivery_head: bb4b16bc（owner 分支 tip；integration merge=0f872d1b）
branch: agent/zcode/M2-TA3-B3-KO-FULLRUN
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-B3-KO-FULLRUN-zcode
---

# M2-TA3-B3-KO-FULLRUN：ko 全量补跑与缺口关闭

## 背景（用户裁决 2026-10-02：§7 项1=全量、项2=K02 干净重跑、项3/4/6/7 被项1 吸收或按推荐）

KO-RERUN 事件驱动停跑后，用户裁决：**7 case 全量补跑**（选项①，上界 ≈107 万–209 万 est token——**用户显式批准的预算背书**，构成对 phase2-plan.md:192「数万量级」口径的案例级豁免记录，R1/§7.5 由此关闭）+ **K02 干净重跑**（项2，+186 请求 ≈113k）。全量覆盖 F1 系四页（K01/K04/K05/K08）页级全链实测（项3 F1 关闭=组合证据就此闭环）+ F2 系三页（K07/K09/K10，项4 页级必要性被吸收）。相似度 Gate 口径（§7.6）按编排推荐落地：**短期③登记 known-limitation**（合法重译保守 FAIL 方向安全、按 directional 接受，K11 对 0.4615 入已知形态清单）+ 中期②语义度量登记候选（需新校准集，另行释放）。

## 交付（AC）

1. **AC1 全量补跑**：ko 8 case = K01/K04/K05/K08/K07/K09/K10 全量 + K02 干净重跑（首跑 K02 保留对照）；`run_qualification.py` 断点续跑、`--determinism-track remote`（新控件）、region 无截断；逐 case typed 失败如实登记（K19 不在名单——F4 维持；K11 沿用 KO-RERUN 结果不重跑）。
2. **AC2 对照与关闭确认**：逐 case vs KO-RERUN/首跑对照表；**F1 关闭确认**（detect 5/5+全链 8/8 组合证据落报告）+ **F2 关闭确认**（K07/K09/K10 页级全链实测）；全链 Gate 新状态如实（ja PASS+ko 现状；K19 F4 维持登记）。
3. **AC3 评测更新**：ko G1 CER（新增可测页——K01 等 tiling 页的 SVG GT 对齐可行性沿 measure_cer 逻辑，无法自动对齐的如实 NOT_AUTOMATED）；相似度 Gate：至少 1 个新增 webtoon 页（K02 干净版）跑 K11 同款对照（remote 轨），known-limitation 形态清单追加；SFX/可读性增量沿 KO-RERUN 口径（预算内）。
4. **AC4 known-limitation 落地**：`quality-thresholds.md` §5 相似度双轨条目追加 known-limitation 注（合法重译保守 FAIL=方向安全，K11 0.4615 形态实测，语义度量=候选待校准集）；ko-rerun-report §7.6/§7.5 用户裁决记录回填。
5. **AC5 纪律**：key env 注入零明文；**预算上界 220 万 est token（用户批准 209 万+K02 113k 余量）——超上界即停登记**；请求数/用量逐 case 计量（--meter-translation）；DeepSeek 故障窗韧性依赖 typed fail-closed；src/tests/契约/packaging/apps/首跑与 KO-RERUN 产物零改动。

## 允许修改面

`verification/M2-TA3-B/phase2/ko-fullrun/**`、`verification/M2-TA3-B/ko-fullrun-report.md`（或 phase2 下）、`verification/M2-TA3-B/quality-report.md`（追加节）、`verification/M2-TA3-B/quality-thresholds.md`（AC4 known-limitation 注）、`experiments/M2-TA3-B/**`（微调）、Task/Handoff。

## 禁改面

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、首跑与 KO-RERUN 产物、`doc/STATUS.md`、key 明文。

## 纪律

- 长跑：逐 case 落盘断点续跑；失败 typed 后继续；预计总时长数小时（K01 detect ~20s+全链 region 数百）。
- directional 延续；阈值实测 vs 提案对照沿双轨口径。

## 交付记录（Owner 回填，2026-10-03）

**全部 AC 交付，逐项判定见 [ko-fullrun-report.md §10](../../verification/M2-TA3-B/ko-fullrun-report.md)**：

- **AC1 PASS**：9 pass 全落盘（8 case 主 pass + K02 rerun + similarity）；K02 干净双 pass 全绿（首例 ko webtoon pipeline_failures=0 样本）。
- **AC2 PASS**：F1 关闭（detect 5/5 与 TILING qualification 逐 case 同值 ×全链 8/8 export OK 组合）；F2 关闭（K07 362MB/K09 277MB/K10 278MB 页级全链 export OK）；Gate 新状态 §7 如实（K02/K02.rerun/K05 三 pass 全绿；其余 case 含预期内 F3 同型 typed 登记；**K01 run1=FAILED steps 全绿待归因缺陷新登记**）。
- **AC3 PASS（CER 部分 NOT_AUTOMATED 如实登记）**：K01–K10 无 SVG GT 物→NOT_AUTOMATED（AC3 预留口径）；K02 干净版相似度 93 对全非空（median=1.0 达标/min=0.0→FAIL，合法重译形态大样本再证实）。
- **AC4 PASS**：thresholds §5 known-limitation 注（2026-10-03）；ko-rerun-report §7 逐项裁决记录回填。
- **AC5 PASS**：实测 **950,954 est tokens = 上界 43.2%**（未触熔断，stop=null）；请求 1,568≈1.41×region 数；key 零明文；diff 面仅允许修改面（driver 硬化两 commit 属 `experiments/M2-TA3-B/**` 微调授权）。

**执行环境事件（Reviewer 必读）**：run 跨越两次已处置事故——①invalid-env 无效轮（唤醒续接 shell 丢失 OCR venv `PYTHONPATH`→6 case OCR 全 `PROVIDER_DEPENDENCY_MISSING` 静默无效；已归档 `summaries/invalid-env-2026-10-02-ocr-dep-missing/` + ledger 污染条目清除 + driver 硬化 `runner_env()`/`ocr_stack_ok()`，commit `cd76cac0`）；②双 driver 并行（原初 driver 未死+重启同秒双副本撞车；进程审计后收敛原初 driver A 独跑，commit `7aee808d`）。**最终有效数据全部来自原初 driver A**；有效轮判别基线（引擎初始化日志+OCR 速度+run1.steps 无依赖失败）见报告 §1.1。

**新增运行时特性登记**：逐 region 全链耗时 ∝ 页高（~1ms/px 行，R²≈0.99）——BACKFILL fan-out 后 region 渲染作用于整页画布（webtoon 页 277–362MB），region 局部贴图化=优化候选（报告 §6，非本 Task 范围）。

**新登记缺陷（非阻塞）**：K01 run1 pipeline=FAILED 而 step 表全绿（归因未定，planner 聚合层嫌疑）；K10 单 region translate typed 失败保空（fail-closed 正确）。
