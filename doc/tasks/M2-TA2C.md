---
id: M2-TA2C
title: No-HF JA/KO Asset Migration
kind: asset_infrastructure
status: changes_requested
approval: user_authorized_2026-09-29
suggested_owner: Codex Desktop
owner: Codex Desktop
reviewer: DeepSeek Harness
depends_on: [M2-TA1, M2-TA2A]
base_commit: d4d3977907bc64177ef85c61da4c95901f135fc6
branch: agent/codex/M2-TA2C-no-hf-assets
worktree: C:/Users/49745/.codex/worktrees/no-hf-comic-assets/New Manga
integration_commit: null
---

# M2-TA2C：No-HF JA/KO Asset Migration

## 来源与目标

用户提供 `漫画素材包_无HF方案_日漫韩漫.zip`，要求升级已有 `comic_golden_suite`，不能创建第二套系统。附件只含脚本、目录占位和来源建议，不能视为已取得素材。以 `main@d4d3977907bc64177ef85c61da4c95901f135fc6` 为冻结基线；主工作区其他未提交内容归原作者所有。

## Acceptance Criteria

- [x] 记录附件静态审计、官方来源的实际内容/许可/访问条件；附件脚本不直接执行或机械导入。
- [x] 统一 JA/KO Case schema 与现有 16 项 taxonomy；资产 `READY` 和各 Pipeline `NOT_RUN` 独立表达；已阻塞/仅注释来源不计可运行数。
- [x] 保留现有 KO 10 个完整 Smoke 文件和 JA 10 个公开页面；公开、许可适配、体量可控的新资产才下载，逐文件记录路径、大小、SHA-256、来源、许可和 GT 范围。
- [x] OpenMantra、eBDtheque、Pepper&Carrot JA/KO、Artificial Manga、JMangaBench_Mixed、TextMasks、Public Domain Japan、Manga109 optional、AIHub 均有真实状态；不以代码仓库或空目录冒充视觉资产。
- [x] 现有 CLI `download/list/missing/verify` 保持幂等、离线和失败保护；L0/L1/L2 定义数、READY 数、blocked 数如实报告。
- [ ] 原图、ZIP、mask、cache 均不进入 Git；定向资产测试和 Git 检查已留证；独立非作者 Review 与 Codex 集成后复验待执行。生产代码与依赖零改动。

## 允许修改范围

- `test_assets/comic_golden_suite/**`（唯一测试资产体系，包括 ignored 本地素材）
- `tests/m2_test_assets/**`
- `doc/tasks/M2-TA2C.md`、`doc/handoffs/M2-TA2C-*.md`、`doc/reviews/M2-TA2C-*.md`
- `verification/M2-TA2C/**`
- Codex 串行回填 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/README.md` 的任务导航/状态及 TA2B/TA3 依赖。

## 禁止范围

不得执行附件脚本、无条件克隆非商业/许可不明数据、绕过注册/gated 条件、大规模抓取 Japan Search/NDL，或将漫画原图/大文件提交 Git。不得修改生产 Schema、migration、Pipeline、Provider、UI、Library、依赖或锁文件。不得以 Case 数量代替可运行覆盖；不在此 Task 扩 L1 到 100–150。

## 执行顺序与并行

M2-TA1 与 M2-TA2A 均已 `done`，本 Task 可释放。来源/许可只读审计、既有 KO 完整性复核可与新资产获取并行；共享 manifest、inventory、README 由 Owner 串行写入。M2-TA2B 保持 gated optional，未取得官方归档时不得实施；其来源审计可并行。M2-TA3 在本 Task 完成后按实际可运行覆盖再释放，不以 TA2B 为硬前置。

## 测试计划

`python -m pytest tests/m2_test_assets -q`；`python test_assets/comic_golden_suite/tools/assets.py list|verify|missing|download --level smoke`（按 CLI 实参分别执行）；对首次/重复/离线/部分文件和哈希做定向验证；`git ls-files`、`git check-ignore --no-index -v`、`git diff --check`。`tests/m2_acceptance` 若执行须与固定基线比较失败集合；`tests/core` 的历史 PySide6 环境障碍不在本 Task 修复。所有未运行项记 `NOT_RUN`。

## 交付与 Gate

Owner 已交付初版固定实现 HEAD=`2e9797013dcb73280462a7b34390abcb2be12977`、[Handoff](../handoffs/M2-TA2C-2e979701.md)、[运行证据](../../verification/M2-TA2C/run-results.md)；DeepSeek Harness r1 已独立审查并要求返修，不能视为批准。Codex 仅在返修、复审及关键验证完成后集成并复验，之后才可置 `done`。已在上述 linked worktree 认领，Git common directory=`G:/CODEX/New Manga/.git`。

## Review r1 与返修

[DeepSeek Harness r1](../reviews/M2-TA2C-2c12ba1e-dsh-r1.md) 对 Handoff HEAD=`2c12ba1ec9d302de10a210211dfa46cd490845df` 给出 `changes_requested`：0×P0、0×P1、2×P2、7×P3。P2-1 为 KO Cleaned Webtoon 来源层 `PARTIAL` 与固定 10 Case `READY` 口径冲突；P2-2 为 JA Pepper&Carrot `checksum_inventory=null` 且来源索引路径基准不统一。本次返修已将来源层限定为固定 10 Case 的资产状态并统一仓库根相对 checksum 路径；另澄清 SVG 文本计数口径。P3-2 的 `required_files()` 增传语言参数会使已有无效 profile 的 `status()` 从 `PARTIAL` 变成异常，故保留已有在 `load_manifest` / `download` / `validate_public_case` 的语言校验路径。返修后的固定 HEAD、测试和复审另行登记，不复用 r1 结论。
