---
id: M2-TA3-A
title: "应用级 E2E Smoke（用户裁决 2026-09-30）：5 个真实 case（日漫+韩漫）detect→OCR→translate→inpaint→render/export 全链，不做质量 qualification"
kind: acceptance
status: ready
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: [M2-TA2B]
base_commit: PENDING_SET_AT_CLAIM
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

- [ ] AC1（case 选取）：恰好 5 个 case（≥2 日漫 BJ + ≥2 韩漫 KO + 1 P&C 任一语言），在 Task 内登记选取清单与理由（特性覆盖）。
- [ ] AC2（全链执行）：每 case 走通 `detect → OCR → translate → cleanup/inpaint → render/export` 五段，全部真实执行（Provider 可用 deterministic/local 实现——翻译质量不在本阶段验收，但产物真实存在且可打开），失败段 fail-closed 如实记录（不得静默跳过）。
- [ ] AC3（真实产物）：每 case 留存产物清单（检测区域数、OCR 文本、译文、inpaint 图、导出文件路径+SHA256），产物在 gitignored 目录、路径与哈希入 verification。
- [ ] AC4（证据）：每 case 一份 smoke 结果（PASS/FAIL per stage + 耗时 + 产物清单）入 `verification/M2-TA3-A/`；失败 case 逐段归因（环境/数据/缺陷三分类）。
- [ ] AC5（范围与回归）：既有测试套件不回归（pytest tests/m2_test_assets + m2_acceptance 相关子集 EXIT=0）；diff 仅允许路径；`git diff --check` EXIT=0。

## 允许修改范围

- `verification/M2-TA3-A/**`、本 Task、Handoff
- `test_assets/comic_golden_suite/manifests/cases.json`（仅 pipeline_status 回填：NOT_RUN → 各 stage 实际结果）
- 如需薄封装脚本：`experiments/M2-TA3-A/**`（调用生产入口，不改生产代码）

## 禁止范围

- 生产代码 `src/**`、`apps/**`、共享契约（发现缺陷→记录+走缺陷 Task 流程，本 Task 不修）
- 真实外部 API 凭据使用（翻译/OCR 用生产可用的 deterministic/local Provider；真实 Provider 质量验收属 TA3-B/后续）
- 素材像素入 Git

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 全链 | 5 case × 五段执行（生产入口/deterministic provider） | TA2B 素材 + GPU/CPU venv | NOT_RUN | 待入 verification |
| AC5 回归 | pytest tests/m2_test_assets + 相关 m2_acceptance 子集 | — | NOT_RUN | 待入 verification |

## 依赖、风险与阻塞

- **硬依赖：M2-TA2B done**（日漫 case 来源）。
- 风险 1：生产 E2E 入口面向 app 流程（import→pipeline→export），素材 case 接入需薄适配脚本——放 experiments/，不改生产。
- 风险 2：inpaint/OCR 的 deterministic 实现能力边界——如实记录每段实际 Provider 与输出形态。
- 风险 3：长条 webtoon 需按 approved_regions 切片进管线——用既有 digest per-chunk 机制。
- 阻塞：M2-TA2B 未 done 前不得开工（依赖门）。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无。
