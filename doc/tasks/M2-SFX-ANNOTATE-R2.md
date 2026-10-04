---
id: M2-SFX-ANNOTATE-R2
title: "SFX 标注轮 R2（T1b-R2 扩标轮）：素材补齐（BJ+10 页/KO+5 页）+BJ 低置信扩审+回放补审+三集扩集重导出——闭合 A′ 输入条件缺口"
kind: feature
status: ready
owner_claim: —
approval: user_ruling_2026-10-04_选项a_补齐再训
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
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

- [ ] AC1 素材补齐（KO 5 页落位+BJ 10 页下载入池登记+对账脚本全绿+fallback 纪律）
- [ ] AC2 BJ conf 0.2-0.5 扩审（双 AI 交叉审核，全量判定无残留）
- [ ] AC3 回放 5 页补审（R1 C4 偏差闭合）
- [ ] AC4 BJ 新页三源预标注+双 AI 扩审
- [ ] AC5 三集扩集重导出+BJ 正集/challenge 验证+§8.1 对照表回填
- [ ] AC6 零 src；数据本体外部树 gitignored；Git 只进 manifest 摘要与 cases.json 新增登记

## 允许修改范围

`experiments/M2-SFX-ANNOTATE-R2/**`（新建，可复用 R1 工具代码以复制/包装方式）、`verification/M2-SFX-ANNOTATE-R2/**`、本 Task/Handoff、`training_data/sfx-v1/**`（gitignored）、`test_assets/comic_golden_suite/manifests/cases.json`（**仅限新增 BJ16-BJ25 条目**）、素材根 test_assets 文件树（页图落盘，gitignored 语义核对后落位）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、cases.json 既有 100 条目（只增不改不删）、R1 交付的三集 manifest 与 final/ 既有产物（重导出写同目录沿 R1 gitignore 语义，不覆盖 Git 内摘要的历史版本）。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①densho810 下载形态未知（URL 规律/反爬）→AC1 已定义 fallback 停等纪律；②BJ13 唯一判定=delete 是 ai-consensus 结论，challenge 补齐依赖翻案或新页正集——AC5 允许如实登记空集+交编排；③peppercarrot 韩文版页与 K01-10 webtoon 形态差异大（欧漫布局），若与 KO 域训练目标（webtoon）错配，在报告登记形态差异供 T2 裁决参考。
- 裁量点（Owner 可自裁，登记即可）：BJ 候选页 chiqui7 密度并列时的选取；KO 5 页的具体选页。

## 交付与运行记录

-（待 Owner 回填）
