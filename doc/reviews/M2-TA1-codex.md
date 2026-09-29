---
task_id: M2-TA1
reviewer: Codex independent Reviewer subagent (`/root/m2_ta1_review`)
author: Codex
base_commit: 40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be
reviewed_head: 00df8f1dd4d480d4e4432c833981481f2c01dd3e
decision: approved
---

# Review：M2-TA1

## 范围与依据

独立 Reviewer 阅读固定 diff `40ce1f91..00df8f1d` 的 27 个提交路径、`M2-TA1` AC、允许/禁止路径、素材工具调用流与相关验证日志。reviewer 没有修改文件或执行网络下载。后续唯一差异是对证据日志的固定 HEAD 标头与 README 的素材状态用语归档；资产工具、manifest、测试未修改。

## Architecture

**PASS。** 变更限于测试目录、定向测试、Task/治理导航和 verification。未修改生产代码、Schema、Provider、Pipeline、UI 或依赖。55 个 `case_id` 唯一；20 个 L0 case 可枚举。KO/JA 原始素材被各自 `.gitignore` 排除，固定提交不含任何漫画原图。工具仅使用标准库；Manga109 只允许对用户提供的官方 ZIP 选择性导入，不安装依赖、不传 token 参数、不用 `extractall`。

## Verification

| 场景 | 命令 / 证据 | 结果 |
|---|---|---|
| 定向测试 | `python -m pytest tests/m2_test_assets -q`，HEAD `00df8f1d` | PASS：10 passed，EXIT=0 |
| KO Smoke | `assets.py verify --language ko --level smoke` | PASS：READY=10，EXIT=0 |
| JA gated 状态 | `assets.py download --language ja --level smoke` | PASS：10 个 case 均报告 `BLOCKED_BY_ASSET_ACCESS`，无网络下载，EXIT=0 |
| 新架构 acceptance 对照 | Task 与 base `main` 的 `tests/m2_acceptance` | BASELINE_FAILURE：两边相同 8 failed / 24 passed / 3 skipped，失败测试名相同 |
| Legacy 集合 | `python -m pytest tests/core -q --tb=no` | BLOCKED_BY_ENV：缺少 PySide6，4 collection errors；不属于新架构验收 |
| Git 边界 | 固定提交 `git ls-tree`、`git check-ignore` 与 `git diff --check` | PASS：没有原图在提交内；KO/JA 图片路径匹配 ignore；diff check EXIT=0 |
| 真实数据与产品 Pipeline | Manga109 gated ZIP 导入、OCR/translation/render smoke | NOT_RUN：无获批归档；此 Task 未接入正式 Pipeline |

详细日志在 `verification/M2-TA1/`。固定提交内日志后来补正过 HEAD 标头，当前最新 10 项测试日志记载 `Tested HEAD=00df8f1d`。

## Findings 与处置

此前 Review 发现 KO 截断/损坏下载可能落盘、部分资产误报 `READY`、缺少 Manga109 显式导入通路，以及按作品名前缀筛图会排除真实归档 `000.jpg` / `003.jpg`。这些已在固定提交中修复：下载长度/PNG CRC 校验并清理临时文件；严格 marker 与完整文件验证；用户提供官方 ZIP 的路径/CRC 安全导入；数字页名与 XML `page@index` 双向匹配。非法索引的本地校验转成明确失败而非 traceback。**未解决 P0/P1：0。**

## 结论

`00df8f1dd4d480d4e4432c833981481f2c01dd3e` 的固定实现获 **approved，可交 Codex 集成**。KO 本地 smoke 图片仍禁止进入 Git；真实 Manga109 导入和应用 Pipeline 质量仍为 `NOT_RUN`。
