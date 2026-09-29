---
task_id: M2-TA1
author: Codex
recipient: Codex Integrator
base_commit: 40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be
delivery_head: 00df8f1dd4d480d4e4432c833981481f2c01dd3e
status: ready_for_integration
---

# Handoff：M2-TA1

## 交付结果

在 `test_assets/comic_golden_suite/` 增加 55-case JA/KO 统一 JSON catalog、分类 taxonomy、标准库 `download/verify/list/missing` CLI、本地原图 ignore 边界与使用说明；在 `tests/m2_test_assets/` 增加 10 个定向测试。Task/Plan/Status/Index 和审计、来源及运行证据一并更新。提交 `00df8f1d`，base=`40ce1f91`。没有修改生产 Schema/Pipeline/Provider/UI/依赖。KO 10 个 smoke case、80 个文件已在作者 Task worktree 本地取得；Manga109、Pepper&Carrot、其他外部数据没有下载。

| AC | 结果 |
|---|---|
| AC1–AC3 | PASS：55 唯一 case、统一 schema、JA10+KO10 L0；四命令可枚举/报告缺失和 gated 状态。 |
| AC4、AC6 | PASS：标准库、安全显式下载/导入、路径/CRC/PNG 校验、数字 Manga109 页名↔XML 索引、无覆盖写入、原图 Git 忽略。 |
| AC5 | PASS（状态如实）：L1 当前 55，目标 100–150，标 `PARTIAL`；L2 不进日常运行；素材状态见 README 和 `verification/M2-TA1/asset-sources.md`。 |
| AC7 | PASS：定向 10 passed；新架构 acceptance 的同一组基线失败已在 Task 与 base 对照；证据逐项归档。 |
| AC8 | Review 已 approved；集成和集成后检查由接收 Integrator 完成后，Task 才可置 `done`。 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/2/4/6 | `python -m pytest tests/m2_test_assets -q` | Windows PowerShell 7.6.6；`C:\Python314\python.exe` 3.14.6；HEAD `00df8f1d` | PASS：10 passed，EXIT=0 | `verification/M2-TA1/pytest-m2-test-assets.log` |
| KO L0 数据 | `assets.py verify --language ko --level smoke`；再执行同级 `download` 重复检查 | Task worktree；HEAD `00df8f1d` | PASS：READY=10；downloaded=0、existing=80，EXIT=0 | `ko-smoke-verify.log`、`ko-smoke-repeat-download.log` |
| JA gated | `assets.py download --language ja --level smoke` | Task worktree；无 gated ZIP/token | PASS：10×`BLOCKED_BY_ASSET_ACCESS`，下载 0，EXIT=0 |
| acceptance 回归对照 | `python -m pytest tests/m2_acceptance -q --tb=no` | Task HEAD `00df8f1d` 与 main base `40ce1f91`；同一 PowerShell/Python | BASELINE_FAILURE：两边均 8 failed / 24 passed / 3 skipped，测试名一致；非 Task 回归 | `pytest-m2-acceptance-*.log` |
| Legacy 测试尝试 | `python -m pytest tests/core -q --tb=no` | Python 3.14.6，无 PySide6 | BLOCKED_BY_ENV：4 collection errors；不作为新架构 Gate | `pytest-core-environment.log` |
| 来源与 URL | 对 manifest URL 发送 HTTP HEAD | Python stdlib `urllib`；2026-09-29 | 6 个来源 200；AIHub 403（只记录环境响应）；没有通过 HEAD 获取素材 | `asset-url-head-check.log` |
| Git/格式 | `git check-ignore --no-index -v`、`git diff --check`、`git ls-tree` | 固定提交 `00df8f1d` | PASS：KO/JA media path 被忽略；提交只包含元数据、脚本、规则和测试；原图为 0 | `git-ignore-probe.log`、`git-diff-check.log` |

真实 Manga109 gated ZIP 导入、Pepper&Carrot 下载、应用级 OCR/Detection/Translation/Inpainting/Typesetting/Webtoon slice-and-stitch Pipeline 均为 `NOT_RUN`。自动工具并不声称这些能力已经接线或测过。

## 接收方式

- 分支：`agent/codex/M2-TA1-comic-test-asset-foundation`
- Worktree：`C:\Users\49745\.codex\worktrees\comic-test-assets\New Manga`
- 合并前固定 HEAD：`00df8f1dd4d480d4e4432c833981481f2c01dd3e`
- 基线：`40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be`
- Review：`doc/reviews/M2-TA1-codex.md`，decision=`approved`。
- 当前主工作区原有改动清单：`verification/M2-TA1/main-worktree-preexisting-status.txt`。集成应保留它们；`test_assets/comic_golden_suite/` 在集成前不存在。
- 本机 KO 原图位于 Task worktree 的 ignored 路径。合并后只复制到主仓库同一套 `test_assets/comic_golden_suite/韩漫_KO/` 目录，不覆盖文件；随后在主仓库复跑定向测试、KO verify、重复下载检查、`git check-ignore` 与 `git ls-files`。

## 下一任务建议（必填）

- Task ID / 标题：提议 `M2-TA2` — L1 Core Regression 100–150 固定 case 证据化扩充。
- 推荐 Agent / Reviewer：Owner=ZCode；Reviewer=DeepSeek Harness（非作者）；Integrator=Codex。Owner 与 Reviewer 不同。
- 推荐原因与前置依赖：M2-TA1 已统一 schema/taxonomy 和 case CLI；当前仅 55 个 definitions，低于 L1 100–150 目标。用户要求不虚构、遵守许可；扩充前需逐案给出真实来源/标签/许可与可用状态。
- Recovery point：集成后仓库 `main@<M2-TA1 integration commit>`；worktree 待 Codex 创建；以 `doc/STATUS.md` 的最新 live state 为准。
- 允许修改路径：`test_assets/comic_golden_suite/manifests/cases.json`、套件 README、对应 Task/Handoff/Review 与 `verification/M2-TA2/**`；若不增加案例而只形成证据化候选清单，说明理由并保持现有 55 case。
- 禁止范围与新增授权条件：不提交漫画原图，不自动下载大数据集、不绕过 gated、不改生产 schema/pipeline/Provider/UI/依赖；仅登记并说明状态的 case 可先完成，获取受限素材必须走来源官方授权。
- 交付物：100–150 个经证据支持的 case 定义（若来源/许可不足则报告准确的 `PARTIAL` 数量）；覆盖 JA/KO 难例 taxonomy；每个 case 记录许可、可再分发性、GT 状态与所需来源；不得把空占位计入有效样本。
- 验证命令、环境与完成 Gate：`python -m pytest tests/m2_test_assets -q`、manifest 唯一 ID/taxonomy/路径校验、`git check-ignore`；固定清单 URL HEAD 检查；独立 Review approved；Codex 集成后复验；每条日志含 EXIT 和 shell/Python 环境。
- 可直接转发给 Agent 的指令：

```text
你负责 New Manga 的提议任务 M2-TA2：把 test_assets/comic_golden_suite 的 L1 Core Regression 清单从当前 55 个 case 扩充并证据化到 100–150 个固定困难 case。先核对当前 main HEAD、STATUS、REBASELINE_PLAN、M2-TA1 Task/Handoff/Review 和现有 manifest，再等待该 Task 在 Plan/STATUS 被明确 release 后开始实现。只改 manifest、资产 README、M2-TA2 文档与 verification。统一复用现有 JA/KO schema 和 16 项 difficulty taxonomy；真实来源、case 标识、许可/可再分发性、ground truth、预期 pipeline、URL 状态必须可追溯；不要虚构 case、把 annotation license 当成图像授权，或把目录占位计为有效素材。禁止提交任何 Manga109/Webtoon 原图，不自动下载大型数据集、不绕过 gated、不改生产 Schema/Pipeline/Provider/UI/依赖。可用素材状态准确记录 READY/PARTIAL/MISSING/BLOCKED_BY_ASSET_ACCESS/NOT_RUN。Owner=ZCode；Reviewer=DeepSeek Harness（非作者）；Integrator=Codex。完成时提供固定 base/head、实际命令/EXIT/shell/venv 日志、Handoff，并等待独立 Review；不要自行合并。
```

## 风险与遗留

- 真实 gated archive 无本机凭据/审批：`BLOCKED_BY_ASSET_ACCESS`，真实 Manga109 importer 只由 synthetic ZIP 验证。
- L0 是 case manifest + 素材验证；应用级 smoke pipeline 尚未接线，执行 `NOT_RUN`。
- L1 55/100–150，状态 `PARTIAL`；此 Handoff 只推荐后续任务，不表示 M2-TA2 已由本次释放。
- main 原有 dirty/untracked 用户文件未改动；素材原图不在提交内。
