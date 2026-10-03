# M2-TA3-B3-KO-FULLRUN 非作者静态 Review 报告（DSH r1，2026-10-03）

verdict: approved_with_conditions

条件：集成收口前由 owner 在允许修改面内完成 F1、F2 两项文档/证据修正（均为小修，无需重跑、无代码返工）。AC1–AC5 的实质判定全部经受住独立复算，无 P0/P1/P2 缺陷。

## R-A..R-G 逐项结论

| 项 | 结论 | 关键证据 |
|---|---|---|
| **R-A** AC 判定复核 | **PASS，无夸大无漏项** | AC1：9 pass 全落盘（summaries/qual-K*.json 9 份 + ledger 9 条 + determinism/K02-similarity.json）；断点续跑逻辑在案（ko_fullrun_driver.py:275-278）；max_regions: null/truncated: false 在案（qual-K02.rerun.json run2）；K11/K19 不在 driver 队列（ko_fullrun_driver.py:112 MAIN_ORDER）✓。AC1「新控件」表述核对：--determinism-track 在 base 73252798 的 run_qualification.py 已存在（grep 14 处命中），本 Task 仅使用——引用 KO-RERUN 遗产而非自称新增，无夸大 ✓。AC2/AC3/AC4/AC5 见 R-D/R-E/R-B/R-F |
| **R-B** invalid-env 处置 | **PASS，附 F1（P3）note 丢失、F2（P3）聚合数字** | 归档目录 8 文件在案（6 qual-*.json + qual-report.json + rerun-compare.json）；6/6 份 run1 含 ocr/failed/PROVIDER_DEPENDENCY_MISSING 且 run2 per_region OCR steps 全部（879/879）同错误码（逐份扫描证实，含 K01×180、K10×147）；ledger 9 条 entries 加总人工复算 = 950,954 ✓、requests 加总 = 1,568 ✓、stop: null ✓；driver runner_env()（ko_fullrun_driver.py:64-71）与 ocr_stack_ok()（:74-84，probe 失败→main() :252-253 return 2 fail-fast）逻辑正确；三处 subprocess 全部用 runner_env()：ocr probe :78、run_phase :238、similarity :355 ✓；K05.log 原文证实 paddle 从 M2-TA3-B-ocr\Lib\site-packages 加载 + Creating model 双模型初始化日志在案 ✓ |
| **R-C** 双 driver 叙事 vs 7aee808d | **PASS，附 F4/F5（P4）两处 message 瑕疵** | driver-result.json：driver_started_utc=2026-10-02T00:10:53Z、status=DONE、finished_utc=2026-10-03T07:34:35Z（与报告 §1.2 逐字一致）、无 RESUME_SKIPPED 条目（佐证 driver A 从 K04 一路独跑到 K02.rerun）✓；driver-restart2.log 完整转录副本冲突：05:56:09Z 硬化重启→K07 exit=4294967295（1281.4s 被杀）→K09 exit=4294967295（137.4s 被杀），与 7aee808d message 的双副本处置吻合 ✓；driver-result.invalid-env-leg.json 改名归档在案 ✓ |
| **R-D** F1/F2 关闭证据链 | **PASS** | TILING 先例 qualification-results.json pages 实测：K01=180/K02=93/K04=113/K05=62/K08=60，conf 0.5，页尺寸与报告 §2 逐格吻合，5/5 逐 case 同值成立 ✓；K19 页 expected_zero_candidates: true + f4_note 在案 ✓。F2：K07/K09/K10 import OK、RGB32 换算 362,357,640/277,324,800/277,862,640 ≈ 362/277/278MB ✓；export 像素 9/9 文件存在 ✓。JSON 抽查（K02/K05/K07 + 全 9 pass 复算）：与报告 §2 全部行值逐格一致 ✓ |
| **R-E** 相似度与口径回填 | **PASS** | K02-similarity.json stats 独立复算：n=93、51 identical、42 variant、min=0.0、median=1.0、p10=0.5433——与报告 §5 逐字一致；worst pair 实证一致 ✓；determinism_track.declared=inferred=remote ✓。thresholds.md diff 单 hunk 纯追加 §5 known-limitation 注（自述不改变阈值数值）✓；ko-rerun-report §7 回填为 9 行纯新增 blockquote，三方口径一致、阈值零改动 ✓ |
| **R-F** 禁改面与 key | **PASS，附 F7（P4）diff 面备注** | git diff --name-only 73252798..3a046657 全 27 文件：无 src/**、tests/**、doc/contracts/**、packaging/**、apps/** ✓；无 phase2/summaries/（首跑）、无 phase2/ko-rerun/** ✓；experiments/ 下仅 ko_fullrun_driver.py（属「experiments/M2-TA3-B/** 微调」授权，见 F9）；key 零明文 ✓ |
| **R-G** K01/K10 登记如实性 | **PASS，登记如实、未夸大** | K01 run1 step 表逐类计数全 completed（translate/mask_refine/inpaint/ocr/segment/color/term_extract 各 125 + render 124 + detect 1）、零 failed，而 run1.status=failed——报告「step 表全绿却 FAILED，归因未定」与 JSON 完全一致 ✓。K10：空翻译 7 个中 6 个 source_text 为空（F3 同型），有源文本而翻译保空恰 1 个（translate step = failed/PROVIDER_INVALID_OUTPUT/malformed_json，fail-closed）——报告 §4.2 措辞精确 ✓ |

## Findings

- **F1 [P3]** invalidated_entries_note 不在最终交付树：budget-ledger.json（0ca8c740 版）无该字段；note 在 cd76cac0 与 7aee808d 版在案。机制：driver 长驻进程只在启动时 ledger_load() 一次，每次 ledger_append 全量重写文件，driver A 内存态覆盖了人工磁盘编辑。建议：owner 小 commit 回填 note（内容从 git show cd76cac0 取回）或修订报告措辞。
- **F2 [P3]** 主报告聚合数字与自身逐行表格/底层 JSON 不一致（逐 case 行值全部正确）：§2:57 合计行 detect 1,248（实际 1,114，差 134）、OCR 非空 1,070/1,112=96.2%（实际 1,074/1,114=96.4%）、翻译非空 1,069（实际 1,073）；§4.2:94「42 个空 OCR region」（实际 40：K01 1+K04 4+K07 21+K08 4+K09 4+K10 6）；§1.1:25 无效轮「0/958」（实际 0/879）；§8:120 分母 1,115（实际 1,114，853 vs 854，影响可忽略）。不影响 43.2% 预算、Gate 结构、F1/F2 结论。
- **F3 [P4]** 报告 §1.1:26「归档副本的 run1.steps 首条 = ocr/failed/...」对 K01/K10 不严格成立（首条为 detect/completed，OCR 失败 step 在后）。建议措辞改「run1.steps 中 OCR step 均为 failed/PROVIDER_DEPENDENCY_MISSING」。
- **F4 [P4]** 7aee808d commit message「12:17-12:29Z」为 local 时间误标 Z（UTC 应为 04:22-04:29；报告 §1.1「UTC 04:17–04:29」正确）。
- **F5 [P4]** 7aee808d 版 ledger 实存 4 条，第 4 条为副本写入的假 K09 条目（est=0、exit=4294967295）；该 commit message 只提删假 K07。该条目随后被 driver A 内存态重写自然清除，最终 9 条干净。
- **F6 [P4]** cd76cac0 commit message「227/286 OCR non-empty」分母 286 与三 summary 口径不符（region 合计 235、非空 227——分子正确）。正文无 286 引用，仅 message 瑕疵。
- **F7 [P4]** diff 面含 doc/tasks/M2-SFX-E2E-MATERIAL.md——来自 batch release commit 24a89d7d（两 Task 并行波次的纯 Task 定义新增），非 KO-FULLRUN 擅扩范围，集成者知悉即可。
- **F8 [P4]** qual-report.json/rerun-compare.json/逐 case summary 顶层 task 字段为 runner 常量 "M2-TA3-B2"（budget-ledger 的 task 字段正确）。runner 属既有实现，建议未来参数化，非阻塞。
- **F9 [P4]** ko_fullrun_driver.py 在 cd76cac0 为首次入库（+363 行全新增）——「driver 硬化」实为「原初 driver A 以未提交工作树形态运行，硬化版本首次提交」，阅读 commit 图谱时易误解，备注即可。
- **正面核实（非 finding）**：K02.rerun ledger exit=1 与 §2「completed/completed 全绿」并存不矛盾（进程退出码 vs pipeline run 终态两口径）；§6 s/region 抽查（K07=128.8、K04=29.4、K10=106.2）与 §5 定价参考均证实。

## NOT_VERIFIED（集成方运行时项）

1. OCR 纯速度「~16s/region」——无逐 stage 拆分计时；间接证据方向支持，数值未复算。
2. runner 进程退出码判定树（K02.rerun 全绿而 exit 1 的内部成因）——runner 非 本 Task 改动面。
3. ALLOC 2047MiB 口径下 277–362MB 页 Qt import OK 的运行时内存行为。
4. 「production retry 不落计量」口径（沿用 KO-RERUN r1 R6）。
5. export 像素 sha256 与 summary 逐一比对（9/9 存在性已证，哈希未复算）。
6. pytest 三套件基线（预期 611+1skipped 0 failed 不变）——集成方标准门禁。
7. 双 driver 冲突期是否产生实际 DeepSeek 双倍费用——仓库证据无法审计账单面。
8. K09 run1 86s/region 异常窗根因（登记为观测，未归因）。

## 推荐下一步

owner 按 F1/F2 做两处小修（note 回填 ledger + §2/§1.1/§4.2/§8 聚合数字按 JSON 复算值修正，顺带 F3 措辞）后，走标准门禁（三套件 pytest）完成 merge 与 STATUS/PLAN 收口。
