---
id: M2-TA2C
title: No-HF JA/KO Asset Migration
kind: asset_infrastructure
status: done
approval: user_authorized_2026-09-29
suggested_owner: Codex Desktop
owner: Codex Desktop
reviewer: DeepSeek Harness
depends_on: [M2-TA1, M2-TA2A]
base_commit: d4d3977907bc64177ef85c61da4c95901f135fc6
branch: agent/codex/M2-TA2C-no-hf-assets
worktree: C:/Users/49745/.codex/worktrees/no-hf-comic-assets/New Manga
integration_commit: a4cd513d0f7ca6a50e1ae018629b3042612be3bb
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
- [x] 原图、ZIP、mask、cache 均不进入 Git；定向资产测试和 Git 检查已留证；独立非作者 Review 与 Codex 集成后复验已执行（r2 `approved` @`8cb3a135`、集成复验全绿 @`a4cd513d`）。生产代码与依赖零改动。

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

返修实现 HEAD=`66dc361dac18b02fe3e4b773e9d0091ce6e37f60`；[r2 Handoff](../handoffs/M2-TA2C-66dc361d.md)、[r2 运行结果](../../verification/M2-TA2C/run-results-r2.md)。作者复验 25 passed、JA/KO L0 20 READY、KO 新 3 READY；m2_acceptance 仍同组 `BASELINE_FAILURE`。

## Review r2 与集成（2026-09-29，ZCode 代行 Codex 集成）

首轮 r2 会话 `INVALID_REQUEST 422` 无 final，判无效；重派的独立会话（r2b，session=`ca1ae6af-3e74-421c-a4ab-1ec58ec54927`）对 reviewed_head=`8cb3a135c58d7a7a7b3d07fc5bba75c17aa6deb7` 给出 [`approved`](../reviews/M2-TA2C-8cb3a135-dsh-r2.md)：0×P0/P1/P2，r1 P2-1/P2-2 判定关闭，P3-1 关闭、P3-3/4/5/6/7 保留、新增 P3-8（r1 会话转录入库含本机路径与掩码 key，集成时移出树并立规）、P3-9（`66dc361d` 对已提交 raw log 的 whitespace-only 规范化，集成记录登记）、P3-10（断言覆盖缺口，候选留 planning），均不阻塞。报告原字节 SHA256=`d8fede0c9106fd9942babdd749d12c9e278cdd88badc805e91a4c95b32f473f4`。

集成 merge=`a4cd513d0f7ca6a50e1ae018629b3042612be3bb`（parents `406f2c76`+`2e784327`，无冲突，31 文件）。集成方复验（[integration record](../../verification/M2-TA2C/integration-a4cd513d/integration.md)）：pytest assets **25 passed EXIT=0**（非沙箱复现）、CLI 六命令全 EXIT=0（READY 20/23/8/37、download 幂等 downloaded=0）、KO 新 4 文件非覆盖复制且三重 SHA-256 一致（合计 16,292,579 bytes）、`git check-ignore` 4/4 命中、`test_assets/**` tracked 媒体 0、`git diff --check d4d39779..a4cd513d` EXIT=0、m2_acceptance 8 failed/24 passed/3 skipped 失败集合与 `BASELINE_FAILURE` 基线逐条一致。范围证明：`d4d39779..2e784327` 全部 32 路径均在允许清单内，`src/`/`apps/`/`contracts/`/`packaging/`/`requirements*` 零命中。
