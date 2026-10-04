---
id: M2-SFX-ANNOTATE-R2
title: "SFX 标注轮 R2（T1b-R2 扩标轮）：素材补齐（BJ+10 页/KO+5 页）+BJ 低置信扩审+回放补审+三集扩集重导出——闭合 A′ 输入条件缺口"
kind: feature
status: in_review
owner_claim: 2026-10-04 by zcode subagent @9b9916af（AC1 素材链）+ @cb055135（AC2-AC5 三集扩集重导出；docs 收尾轮报告/Handoff/本回填随 docs 提交）
approval: user_ruling_2026-10-04_选项a_补齐再训
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
integration_commit: 84f952b3（merge into main，2026-10-04；分支顶 1157e17d=DSH r1 返修，d7b2e7d2=Owner 交付）
depends_on: [M2-SFX-ANNOTATE-R1, M2-SFX-DATA-INFRA, M2-SFX-FINETUNE-PREFLIGHT]
base_commit: 99eab8b6
branch: agent/zcode/M2-SFX-ANNOTATE-R2
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode
review_events: []
created: 2026-10-04
---

# Task: M2-SFX-ANNOTATE-R2 — SFX 标注轮 R2（扩标轮）

## 背景与目标

T1b（M2-SFX-ANNOTATE-R1，done @merge `6bfa1cde`）交付了 ai-consensus GT 三集（train 342/val 3/test 1+合成 324），但 DSH r1 C1 与 stage2-report.md §8.1 对照表确认 **A′ 采纳输入条件未满足**：BJ 域正集=0（主攻毛笔竖排零真实正样本）、BJ 在册 15/25 页、KO 在册 10/15 页、challenge（BJ13/14/15）空集、回放 5 页未产正例。

用户裁决（2026-10-04）：**选项 (a) 补齐再训**——先补素材+扩审闭合缺口，BJ 正集入册后再释放 T2 训练。

## 交付物（阶段化）

- **AC1 素材补齐**：
  - **KO +5 页**：从 cases.json 既有登记 K11-K25（peppercarrot.com 韩文版，CC-BY-4.0，E04P02 等）下载 5 页页图到素材根（选取标准：与 K01-K10 的 webtoon 形态互补性优先，SFX 密集页优先；peppercarrot sources 页可直下）。cases.json 条目已存在（K11-K25），无需新增登记，只需文件落位（对齐 `resolve_asset_roots()` 语义：`<素材根>/<local_path>/<source_id>.png`）。
  - **BJ +10 页**：从 densho810.com/free/（官方免费页，用户授权合作语境+许可降权备案）下载 10 张新页，**新增 cases.json 登记**（BJ16-BJ25：source=https://densho810.com/free/、source_category=01_black_jack_official、source_type=official_free_manga_page、language=ja、local_path=日漫_JA/01_black_jack_official/volXX/pages、source_id=volXX_pYYYY，沿 BJ01-15 字段先例）。**选取标准**：候选页先落盘，跑 chiqui7 生产序列（DOMAIN-EXT 口径）看 SFX 检出密度，取 top-10 SFX 密集页正式入池（毛笔竖排形态优先），其余候选留扩标池。许可备案沿 densho810 报告义务语境（报告窗口 2026-11-02）。
  - 下载失败 fallback：若 densho810 直链不可得，登记已试 URL 形态与失败模式后**停等交编排**（不得用非授权镜像源凑数）。
- **AC2 BJ 低置信扩审**：R1 遗留 conf 0.2-0.5 层 BJ 域候选（user-residual.json 分层 124 个中 BJ 部分；以 residual 分层实际数为准）走 R1 同款双 AI 交叉审核（codex+agy 独立→共识+分歧仲裁），`human_review=false` 保真。**重点**：毛笔竖排形态在 chiqui7 下置信度偏低是已证主根因，本层是 BJ 正集的主要潜在来源之一。
- **AC3 回放 5 页补审**：R1 §8.1 C4 偏差闭合——回放页（BJ06+J38/J41/J43/J51）单元（user-residual.json 内 6 单元）本轮补审入判定，使回放页按合同目的产出训练正例。
- **AC4 新 BJ 页预标注+扩审**：BJ16-BJ25 十页跑 R1 同款三源合并预标注（chiqui7 九档 raw+ogkalu+参照框，工具 stage1_preannotate.py 复用）→ 工作表 → 双 AI 交叉审核 → 判定。
- **AC5 三集扩集重导出**：全部新判定并入后重跑 stage2_finalize.py split/yolo/summary（组隔离 seed 冻结沿 R1 口径；names 硬约束双通道校验）→ 验证：**BJ 域正集 ≥1 页真实样本入册**（训练+challenge 至少 challenge 补齐 BJ13/14/15 有正样本可评——BJ13 判定可翻案重裁）、KO 在册 ≥15 页、BJ 在册 ≥25 页、stage2-report.md §8.1 对照表数字回填更新。

## 验收判据

AC1：素材文件落位+cases.json 新条目 schema 与 BJ01-15 同构+`resolve_asset_roots()` 全量对账 BJ≥25/KO≥15 可解析；下载来源与许可备案登记。
AC2+AC3+AC4：判定全量覆盖本次范围单元（共识∪仲裁=范围全量，残留=0）；`human_review=false`；判定链留痕（codex/agy/arbiter batch 文件+consensus/divergence）。
AC5：五 manifest 指纹一致+names 双通道 PASS+BJ 正集 ≥1 页+challenge 非空（或 BJ13 判定仍=delete 时如实登记并交编排裁决）+报告对照表更新。

## 标注量承诺（本轮闭合目标）

BJ 域在册 ≥25 页（15 既有+10 新增）、KO 域在册 ≥15 页（10 既有+5 新增）；域内回放 5 页产正例（或如实登记判定=delete）。

## Acceptance Criteria

- [x] AC1 素材补齐（KO 5 页落位+BJ 10 页下载入池登记+对账脚本全绿+fallback 纪律）——KO 15 候选直下 15/15（peppercarrot CC-BY-4.0）→ top-5 落位（K13/K18/K15/K24/K19=ep04×3+ep20×2，PIL/sha 5/5）；BJ 零新增网络下载（TA2B 卷 vol01/03/05 复用，PDF sha256 3/3 MATCH，JASRAC 卷 2/7/11 未触碰；fetch_bj.py render 固定 4 页采样不可指定页→自写 material_bj_render.py pypdfium2 DPI150 渲染 54 候选页避开 BJ01-15 已用 source_id）→ chiqui7 整页 letterbox 扫描 top-10 → cases.json BJ16-BJ25（字段 BJ13 同构+pipeline_status 如实全 NOT_RUN+page_sha256 逐页）；验证：cases.json 110 条合法、既有 100 条 byte-identical（diff +750/−0）、fetch_bj verify BJ16-25 10/10 VERIFY_OK、resolve_asset_roots BJ 25/25（R2 worktree 不在 DEFAULT_ASSET_ROOTS，以 SFX_DATA_ASSET_ROOTS/extra 指根验证）+KO 在册 15/15；未入池 44 BJ+10 KO 候选留扩标池
- [x] AC2 BJ conf 0.2-0.5 扩审（双 AI 交叉审核，全量判定无残留）——**空集如实登记**：R1 残留 BJ 域 11 单元=ref_no_conf 7+conf_lt_0.2 4，conf∈[0.2,0.5) 为 0，无判定输入（units.json counts.bj_lowconf=0；该 11 单元仍走 R1 user-residual 用户通道）
- [x] AC3 回放 5 页补审（R1 C4 偏差闭合）——回放 6 单元（BJ06+J38/J41/J43/J51）双审全 delete，按判定如实排除出框列表+provenance.stage2r2 留痕（R1 stage2 链保留；R1 worktree 只读未动 git status 干净）；回放页经补审确认无可保留 SFX 正例（判定即证据）
- [x] AC4 BJ 新页三源预标注+双 AI 扩审——29 候选（worksheet-bj-new）→ conf≥0.2 13 单元：codex 19 单元=confirm 11/correct 0/delete 8、agy 19=confirm 12/correct 0/delete 7、共识 18/分歧 1（R2-BJ17-B02）经 arbiter 裁 delete、uncovered=0/留用户 0；终判 confirm 11（BJ16/17/18/23/24→5 页 complete 正集）/delete 8（BJ25 唯一框→零框负证据 pseudo；BJ19-22 全候选 conf<0.2 保持 pseudo）；human_review=false 保真
- [x] AC5 三集扩集重导出+BJ 正集/challenge 验证+§8.1 对照表回填——五 manifest 指纹一致 564498e1…ccfa；train 345/571（324 合成 pinned+21 真实）/val 4/53/test 2/5/challenge **仍空集（本轮判定范围不含 BJ13/14/15、BJ13 delete 未翻案、AC2 层空集无翻案输入——按 AC5 验收判据允许分支如实登记+交编排裁决，lock.challenge_note+challenge.json note 双登记）**；组隔离 14 组 0 违例、合成 0 入 test；YOLO names 双通道 PASS（脚本读回+pyyaml 6.0.3 独立解析）、labels cls 恒 2（629 行）/坐标∈[0,1]/stem 0 失配、T1a schema 794 样本 0 错误；**BJ 正集=5 页 11 框（pre-bj16×3/pre-bj17×2/pre-bj18×3/pre-bj23×2/pre-bj24×1，densho810/vol01(1)+vol03(2)+vol05(2)）全部入 train——A′ 主攻毛笔竖排形态首批真实正样本；§8.1 对照表五行逐项回填于 verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md §7**
- [x] AC6 零 src；数据本体外部树 gitignored；Git 只进 manifest 摘要与 cases.json 新增登记——git status 复核仅 experiments/verification 新文件与 gitignored 树（遗留：build_r2_units.py/stage1_preannotate_bj_new.py 两个 AC4 工具脚本 untracked，登记于报告 §8 与 Handoff 风险节，建议集成轮补录）

## 允许修改范围

`experiments/M2-SFX-ANNOTATE-R2/**`（新建，可复用 R1 工具代码以复制/包装方式）、`verification/M2-SFX-ANNOTATE-R2/**`、本 Task/Handoff、`training_data/sfx-v1/**`（gitignored）、`test_assets/comic_golden_suite/manifests/cases.json`（**仅限新增 BJ16-BJ25 条目**）、素材根 test_assets 文件树（页图落盘，gitignored 语义核对后落位）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、cases.json 既有 100 条目（只增不改不删）、R1 交付的三集 manifest 与 final/ 既有产物（重导出写同目录沿 R1 gitignore 语义，不覆盖 Git 内摘要的历史版本）。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①densho810 下载形态未知（URL 规律/反爬）→AC1 已定义 fallback 停等纪律；②BJ13 唯一判定=delete 是 ai-consensus 结论，challenge 补齐依赖翻案或新页正集——AC5 允许如实登记空集+交编排；③peppercarrot 韩文版页与 K01-10 webtoon 形态差异大（欧漫布局），若与 KO 域训练目标（webtoon）错配，在报告登记形态差异供 T2 裁决参考。
- 裁量点（Owner 可自裁，登记即可）：BJ 候选页 chiqui7 密度并列时的选取；KO 5 页的具体选页。

## 交付与运行记录

- **素材轮（2026-10-04，AC1 @9b9916af）**：KO+5/BJ+10 素材补齐交付。KO：cases.json 既有 K11-K25 15 候选 peppercarrot CC-BY-4.0 直下 15/15 → chiqui7 tile 扫描 top-5 落位 ep04/E04P07+E04P08+E04P01 与 ep20/E20P06+E20P01（=K13/K18/K15/K24/K19，两集互补）。BJ：零新增网络下载——复用 M2-TA2B-OPEN-ASSETS worktree 已下载卷 vol01/03/05 PDF（bj_download_manifest.json sha256 逐卷核对 MATCH；JASRAC 卷 2/7/11 未触碰）；fetch_bj.py render 子命令只支持每卷 4 页固定采样不可指定页，自写 `material_bj_render.py` 以 pypdfium2 同款 DPI150 渲染 54 张均匀候选页（每卷 18 张，避开 BJ01-15 已用 source_id）→ chiqui7 整页 letterbox 扫描（引擎=R1 conf_scan_diag 只读复用生产 detection_sfx 序列，权重 M2-SFX-DETECT/weights/yolo11s-seg.onnx，venv=M2-DOCTR-QUAL-C4-gpu-py312）密度排序 sha256(seed:source_id)=20261004 决胜沿 R1 口径取 top-10（vol01_p0045(7)/vol05_p0167(5)/vol05_p0065(4)/vol05_p0116(3)/vol05_p0052(2)/vol03_p0059(2)/vol01_p0067(2)/vol03_p0047(2)/vol03_p0186(1)/vol05_p0077(1)）→ cases.json 新增登记 BJ16-BJ25（BJ13 字段口径同构，pipeline_status 如实 NOT_RUN，page_sha256 逐页）。验证全绿：cases.json 110 条合法、既有 100 条深度对比 byte-identical（git diff +750/−0）、fetch_bj.py verify BJ16-25 10/10 VERIFY_OK（BJ01-15 missing=预期，像素在 TA2B/E2E 跨根素材树）、resolve_asset_roots() 全量对账 BJ 25/25+KO 在册 15/15（R2 worktree 不在 importers.DEFAULT_ASSET_ROOTS，以 SFX_DATA_ASSET_ROOTS 环境变量/extra 参指根验证）。未入池 44 BJ+10 KO 候选留 training_data/sfx-v1/annotate-r2/ 扩标池；证据 density-scan-material.json+material-selection.json 同落该 gitignored 树。
- **扩审轮（2026-10-04，AC2/AC3/AC4）**：判定范围 19 单元（judgments/units.json：bj_lowconf 0+replay 6+bj_new 13）。**AC2 空集如实登记**（R1 残留 BJ 域 11 单元=ref_no_conf 7+conf_lt_0.2 4，conf∈[0.2,0.5) 为 0）。AC3 回放 6 单元双审全 delete，按判定如实排除出框列表+stage2r2 留痕（R1 底册 72 样本 450 框只读并入：除 5 个回放页外其余 67 条逐字节一致，R1 worktree git status 干净）。AC4 BJ16-25 预标注 29 候选→conf≥0.2 13 单元双 AI 交叉审核：codex 19=confirm 11/correct 0/delete 8、agy 19=confirm 12/correct 0/delete 7、共识 18/分歧 1（R2-BJ17-B02，arbiter 裁 delete）/留用户 0，uncovered=0；human_review=false 保真（GT=ai-consensus 沿 R1 §0 口径）。
- **三集轮（2026-10-04，AC5 @cb055135）**：stage2_finalize_r2.py --step manifest/split/yolo/summary 全跑+独立复验脚本重读盘上产物核对。preannotate/manifest.r2.json 82 样本（R1 底册 72 只读并入+BJ16-25 新页 10；stage2r2 actions {—:67, completed:5, kept_pseudo_replay_page_delete_excluded:5, kept_pseudo_no_judged_units_this_round:4, kept_pseudo_zero_box_negative_evidence:1}）；final 五 manifest：train 345/571（324 合成 pinned train+21 真实，**BJ 正集 5 页 11 框全入 train**）/val 4/53/test 2/5/challenge 空集如实（本轮判定范围不含 BJ13/14/15、BJ13 delete 未翻案、AC2 层空集——按 AC5 验收判据允许分支交编排裁决，lock.challenge_note 双登记）；seed=20261004 冻结沿 R1，五 manifest 指纹一致=564498e1…ccfa；组隔离 14 组 0 违例、合成 0 入 test；YOLO names 双通道 PASS+labels cls 恒 2（629 行）/坐标∈[0,1]/stem 0 失配/challenge 未导出；T1a schema 794 样本 0 错误；R1 real split 漂移 18/3/1→21/4/2（组池 10→13 组同算法同 seed 重切，组不跨集仍 0 违例）登记 r1_baseline_for_diff。
- **文档收尾轮（2026-10-04，docs 提交）**：`verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md`（全部数字从盘上产物复算：素材链/双审统计/三集/YOLO/schema/对账复算命令与输出见其 §2.2；§7=A′ 输入条件复核表对照 R1 §8.1 五行逐项回填——BJ 在册 25/25 页数口径满足+KO 在册 15/15 满足+BJ 正集 5 页 11 框首批满足+challenge 仍空集交裁决+合成 324 满足）+ `doc/handoffs/M2-SFX-ANNOTATE-R2-zcode-20261004.md`（DSH 审查可转发指令）+ 本 Task 回填（status=in_review）。
- 报告：[verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md](../../verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md)；摘要：verification/M2-SFX-ANNOTATE-R2/stage-r2-final-summary.json；Handoff：[doc/handoffs/M2-SFX-ANNOTATE-R2-zcode-20261004.md](../handoffs/M2-SFX-ANNOTATE-R2-zcode-20261004.md)。
- **A′ 输入条件结论（T2 释放判定依据，交编排/用户）**：BJ 正集 0→5 页 11 框（主攻毛笔竖排形态首批真实正样本，量级仍小）；BJ/KO 在册页数双满足（25/25、15/15，判定覆盖口径见报告 §7 如实细分）；challenge 仍空集（未满足，交裁决）；合成 324 满足。是否释放 T2 由编排/用户按对照表裁决。

## Review

- **DSH r1（2026-10-04）=approved_with_conditions（0×P0/P1、5×P2、6×P3、2×P4）**：AC1-AC6 实质全 PASS（AC5=PASS WITH DEVIATION 明许分支）；Q1 AC2 空集属实（三重复算）、Q2 BJ 正集判定方向正确（目视核验 8/11）、Q3 漂移须固定切分。全部条件已由 Owner 返修落实（P2-4 含编排原页对照实证：BJ17 双框合并/BJ18·BJ23 独立实例）+数据链重跑（P3-2 注记更正，指纹不变）；P3-6 两 untracked 脚本随集成补录。status 待集成置 done。
