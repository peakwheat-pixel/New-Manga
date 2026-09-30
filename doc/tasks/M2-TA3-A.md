---
id: M2-TA3-A
title: "应用级 E2E Smoke（用户裁决 2026-09-30）：5 个真实 case（日漫+韩漫）detect→OCR→translate→inpaint→render/export 全链，不做质量 qualification"
kind: acceptance
status: in_review
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: [M2-TA2B]
base_commit: bebcfcde6ded3d20871a2ddeeadba6f8629f50d5
branch: agent/zcode/M2-TA3-A-E2E-SMOKE
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-A-E2E-SMOKE-zcode
integration_commit: null
---

# M2-TA3-A：应用级 E2E Smoke（5 case 全链，真实产物）

## 来源与目标（用户裁决 2026-09-30）

- M2-TA3 拆两阶段：**TA3-A = 5 个真实 case 的应用级 E2E Smoke**（同时覆盖日漫+韩漫），验证 `detect → OCR → translate → cleanup/inpaint → render/export` 全链与**真实产物**；本阶段**不做最终质量 qualification**。
- TA3-B（20-case 正式 E2E Quality Qualification）**暂缓**：待检测器与 OCR/翻译 Provider 稳定后另行释放，届时单独定义各阶段质量阈值（登记于 REBASELINE_PLAN，proposed）。
- 素材依赖：至少 2 个日漫 case 来自 M2-TA2B 产出（BJ 官方日文版）；韩漫 case 用既有 KO webtoon/P&C。

## Acceptance Criteria

- [x] AC1（case 选取）：恰好 5 个 case（≥2 日漫 BJ + ≥2 韩漫 KO + 1 P&C 任一语言），在 Task 内登记选取清单与理由（特性覆盖）。
- [x] AC2（全链执行）：每 case 走通 `detect → OCR → translate → cleanup/inpaint → render/export` 五段，全部真实执行（Provider 可用 deterministic/local 实现——翻译质量不在本阶段验收，但产物真实存在且可打开），失败段 fail-closed 如实记录（不得静默跳过）。
- [x] AC3（真实产物）：每 case 留存产物清单（检测区域数、OCR 文本、译文、inpaint 图、导出文件路径+SHA256），产物在 gitignored 目录、路径与哈希入 verification。
- [x] AC4（证据）：每 case 一份 smoke 结果（PASS/FAIL per stage + 耗时 + 产物清单）入 `verification/M2-TA3-A/`；失败 case 逐段归因（环境/数据/缺陷三分类）。
- [x] AC5（范围与回归）：既有测试套件不回归（pytest tests/m2_test_assets + m2_acceptance 相关子集 EXIT=0）；diff 仅允许路径；`git diff --check` EXIT=0。**注：含一处允许路径冲突的最小修正，见 §冲突记录。**

### AC1 case 选取清单（定稿）

| case | 语言/族 | 源 | 选取理由（特性覆盖） |
|---|---|---|---|
| BJ02 | ja / black_jack_official_free | TA2B 套件 vol01 p0053 | 竖排对白 + 复杂背景（日漫典型版式） |
| BJ06 | ja / black_jack_official_free | TA2B 套件 vol03 p0056 | SFX 拟声 + 低对比夜景 + 小字（最难段） |
| K01 | ko / hf_cleaned_webtoon | 主仓库套件 K01_724815_1 | 真实韩漫彩色**长条 webtoon**（690×62133 整页直进，验证长图行为） |
| K02 | ko / hf_cleaned_webtoon | 主仓库套件 K02_651664_112 | 长条 webtoon 第二样本（600×18401） |
| K11 | ko / peppercarrot | 主仓库套件 ep04 E04P02 (kr) | P&C 公开 ground truth 单页（CC BY，svg_text_layer） |

- 初版候选 O01/O08（OpenMantra）素材状态为可选隔离目录、不属生产基线，改用 K01/K02 两个真实 webtoon（更符合「真实 case」要求）。
- BJ 像素仅存在于 TA2B worktree、KO/P&C 像素仅存在于主仓库 checkout（均为 gitignored 素材目录）；`run_smoke.py` 以绝对路径引用，未复制任何像素进 Git。

### AC2 执行方式与 Provider 身份（如实登记）

- 薄封装 `experiments/M2-TA3-A/run_smoke.py`：只调生产 seam，不改生产代码。
  - **Run1**：`create_run(TRANSLATE_ALL, PAGE_SELECTION)` —— 生产 planner 自动前插 `detect`（真 docTR fast_base，pin 权重 sha256=688a8b34…，CPU，严格离线），检测经 `RegionEditingService` 建 Region，整页 9 步链（ocr/color/term_extract/translate/segment/mask_refine/inpaint/render）一段式执行。
  - **Run2**：对每个检测 Region 逐个 `create_run(RETRANSLATE_REGION_FULL, REGION)`（region scope 为单 region 选择语义，即阅读器逐格重翻流；BJ06 57 region 触发 40 region smoke 上限，`truncated` 如实记录）。
  - **Export**：生产 `ExportService.export(SINGLE_IMAGE, mode="translated")`。
- Provider 身份：detect = 生产 `DoctrDetectionProvider`（权重 pin sha256=688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace，`NEWMANGA_DETECTOR_WEIGHTS`/`DEVICE=cpu`）；ocr = `m2ac1-mock-ocr`、translate = `m2ac1-mock-translate`（M2-AC1 deterministic mock，AC2 明示允许，`step_run_output_refs` 样本如实记录 MOCK-OCR-SOURCE-TEXT / MOCK-TRANSLATED-TEXT）；inpaint = 生产 `SimpleFillProvider`（route="simple-fill"）；render/export = 生产 Qt 渲染 + ExportService。
- 运行环境：venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（PySide6+torch 2.14.0+cpu+doctr+pytest 全齐）；QT_QPA_PLATFORM=offscreen。
- **重要发现**：M2-AC1 handoff §风险与遗留登记的「region-less 页面 detect→backfill→ocr 链 LOCK_CHANGED planner 缺口」在本轮 5 case **全部未复现**——真 docTR detect 后整页链一段式 completed。该缺口登记可能仅适用于 mock detect 或特定计划时序；留待缺陷 Task 核实，本 Task 不改生产。

### AC2/AC4 结果总表（`SUMMARY cases=5 pipeline_failures=0`，EXIT=0）

| case | Run1 整页链 | detect regions | Run2 region 链 | export | wall_s |
|---|---|---|---|---|---|
| BJ02 | completed (25.9s) | 33 | completed（33 runs） | OK 8,736,076 B | 668.6 |
| BJ06 | completed (21.3s) | 57 | completed（40 runs，cap 40 truncated 如实记录） | OK 8,771,537 B | 820.6 |
| K01 | completed (67.5s) | 15 | completed（15 runs） | OK 20,408,981 B | 1041.6 |
| K02 | completed (18.7s) | 7 | completed（7 runs） | OK 5,984,018 B | 137.3 |
| K11 | completed (5.2s) | 24 | completed（24 runs） | OK 3,036,455 B | 113.0 |

- 归因：5 case 全部无环境/数据/缺陷归因项（`attribution: []`）。
- 导出产物 sha256（与磁盘复算双向一致）：BJ02 `9bbd38763fde3a45e0dc3af61647ee8097f1345653dce99c32759a58c6c499e1`、BJ06 `c5497a499ac80bc86d563e15193bc4f0f447a3ae78b015bbcc36b9d506f7e147`、K01 `02499d71f86f78ae17b1c9f937a455c28fb087c9a29f9352363f10fe1129275f`、K02 `207410cb599acf203e6eb188d94b310d90245c75c8c01a814a2305ec04ce35ee`、K11 `c451815727ec24b64bfd7656fd7fe574879de4d9dc1d79013456f89cee22b7a2`。
- 产物落盘 `verification/M2-TA3-A/artifacts/*.png`（该目录 `.gitignore` 忽略 PNG，像素不入 Git；哈希与尺寸入 summaries）。
- 译文/OCR/inpaint 身份样本：`verification/M2-TA3-A/summaries/artifact-samples.json`（probe_artifacts.py 从各 case scratch db 只读抽取：ocr_text=MOCK-OCR-SOURCE-TEXT、machine_translation=MOCK-TRANSLATED-TEXT、inpaint route=simple-fill、render_status=committed；K01 16×9 步、BJ06 41×9 步全 completed）。

### AC5 回归与回填完整性

- `pytest tests/m2_test_assets tests/m2_acceptance -q` = **82 passed**，EXIT=0（ac3 日志）。
- cases.json pipeline_status 回填：仅 5 case 的 exercised 键 NOT_RUN→PASS（33 行 diff，全部为该映射；schema `load_manifest` 97 case 校验通过；ac4 日志）。未 exercise 的键（bubble_detection/sfx/speaker_attribution/webtoon_slice_reassemble）保持 NOT_RUN。

## 冲突记录（允许路径缺口 → 代行 Codex 最小修正）

**事实**：Task 允许路径含「cases.json 仅 pipeline_status 回填」，但 `tests/m2_test_assets/test_catalog.py:45` 存在快照断言「**全部 97 case** 的 pipeline_status 必须全 NOT_RUN」（M2-TA2B 时点状态锁）。回填后该断言必然失败（实测 1 failed, 81 passed）。tests/** 不在 Task 允许路径内——这是 Task 释放时允许路径清单的疏漏（AC 要求回填，却未把锁定该状态的断言纳入允许路径）。

**处置**（依据用户 2026-09-28/29/30 对 ZCode 代行 Codex 的全权授权，Lead 裁决留痕）：

- 最小修正：仅放宽 `test_catalog.py:45` 这一条断言——非 TA3-A 94 case 仍强制全 NOT_RUN（fail-closed 不变）；TA3-A 5 case 要求键集合与 expected_pipeline 精确相等、PASS 集合非空且为 expected_pipeline 子集。断言判别力保持（仍锁定其余 94 case 与 5 case 的键集合）。
- 不触碰该文件其他任何断言；不动共享契约。
- 同类漂移登记：`test_assets/comic_golden_suite/README.md:7`「当前所有应用 Pipeline 都是 `NOT_RUN`」一句在回填后失实（README 不在本 Task 允许路径）——交集成方随收口修订或登记候选。

## 允许修改范围（含 §冲突记录 追加）

- `verification/M2-TA3-A/**`、本 Task、Handoff
- `test_assets/comic_golden_suite/manifests/cases.json`（仅 pipeline_status 回填：NOT_RUN → 各 stage 实际结果）
- 薄封装脚本：`experiments/M2-TA3-A/**`（调用生产入口，不改生产代码）
- （§冲突记录追加）`tests/m2_test_assets/test_catalog.py` **仅** `test_manifest_has_unique_cases_and_exact_taxonomy` 内的 pipeline_status 全 NOT_RUN 断言同步

## 禁止范围

- 生产代码 `src/**`、`apps/**`、共享契约（发现缺陷→记录+走缺陷 Task 流程，本 Task 不修）
- 真实外部 API 凭据使用（翻译/OCR 用生产可用的 deterministic/local Provider；真实 Provider 质量验收属 TA3-B/后续）
- 素材像素入 Git

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 全链 | `run_smoke.py` 5 case（生产 seam/deterministic provider） | TA2B+主仓库素材 + T1.1.1-impl-py312 venv | PASS：5 case 全链 COMPLETED、export OK | raw/ac1-smoke-all-cases.log（EXIT=0） |
| AC2 产物身份 | `probe_artifacts.py`（只读 scratch db 抽样） | run_smoke 已执行 | PASS：5 case OCR/译文/inpaint/render 样本齐 | raw/ac2-artifact-samples-probe.log + summaries/artifact-samples.json |
| AC5 回归 | `pytest tests/m2_test_assets tests/m2_acceptance -q` | — | PASS：82 passed | raw/ac3-pytest-regression.log（EXIT=0） |
| AC5 回填完整性 | diff 字段类统计 + `load_manifest` schema 校验 | — | PASS：33 行全为 5 case pipeline_status PASS 回填、97 case schema OK | raw/ac4-manifest-backfill-integrity.log |
| AC5 范围纪律 | git status/diff --name-status/check-ignore/diff --check | — | PASS：禁改路径零命中、PNG ignored | raw/ac5-scope-proof.log |

## 依赖、风险与阻塞

- 依赖 M2-TA2B done（已闭环 @fae0d8f6/收口 bebcfcde）。
- 风险 1（薄适配）：已按预期落 experiments/，未改生产。
- 风险 2（deterministic Provider 边界）：ocr/translate 为 M2-AC1 mock，身份与样本全部如实登记（见 AC2）。
- 风险 3（长条 webtoon）：**实测未做切片、整页直进成功**（K01 690×62133 全链 completed；docTR CPU 检测单页 1-2s 级，未复现预期中的 OOM/超时）。`webtoon_slice_reassemble` 保持 NOT_RUN。
- 阻塞：无。

## 遗留（不阻断，登记候选）

- L-1：M2-AC1 handoff 登记的 LOCK_CHANGED planner 缺口未复现——需缺陷 Task 以 mock detect 复现核实（或修正该登记的条件描述）。
- L-2：`README.md:7`「所有应用 Pipeline 都是 NOT_RUN」失实一句待集成方修订（README 不在本 Task 允许路径）。
- L-3：region scope 单 region 语义 + TRANSLATE_ALL 拒绝 region scope（`TARGET_NOT_FOUND: page command requires page scope`）为生产 fail-closed 行为，非缺陷；阅读器批量逐格重翻的用户体验优化属产品层后续。
- L-4：BJ06 57 region 触发 smoke cap 40（truncated 如实记录）；cap 为本 Task smoke 裁剪，非生产限制。
- L-5：QT_QPA_PLATFORM=offscreen 下 Qt 无字体目录告警（PySide6 不再自带 fonts）；render 仍 completed，文字排版质量属 TA3-B 范围。

## 交付与运行记录

- 交付 head：`dc2b9aca`（分支 `agent/zcode/M2-TA3-A-E2E-SMOKE`，claim 1328a766，base=bebcfcde）。amend 轨迹：首commit `b94ebe87`→`319a3036`（仅 raw 日志头对齐交付 head 重生成）→`dc2b9aca`（Task 补披露行）。代码/数据内容自 `b94ebe87` 起零变化。
- Handoff：`doc/handoffs/M2-TA3-A-1328a76.md`。Review：待派发（DSH 非作者静态）。
- 实际测试：见 §测试要求 与 `verification/M2-TA3-A/`（summaries 7 份 JSON + raw 5 份日志 + artifacts 5 份 PNG[gitignored]）。
