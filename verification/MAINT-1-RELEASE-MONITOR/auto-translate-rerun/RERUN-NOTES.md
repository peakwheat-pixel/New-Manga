# 自动翻译 Core 端到端重跑（尝试记录）

- 时间：2026-11-14
- 目标：用有额度的 DeepSeek key 重跑 `REAL-TRANSLATE-PROVIDER-1` 的 AC3，取得「Core 侧端到端」翻译产出。
- 方法：复用 `run_translate_probe.py`（冻结 Core stdio，`StartRun command=translate_untranslated`，book scope，`overrides.provider_bindings={"ocr":"manga-ocr","translate":"openai-compatible-translation"}`）。

## 装配

| 项 | 值 |
|---|---|
| 隔离根 | `workspace/task-envs/REAL-TRANSLATE-PROVIDER-1/work-root`（旧运行留下的） |
| profile | 已改为 `base_url=https://api.deepseek.com/v1`、`model=deepseek-chat` |
| credential | `credential_ref=NewManga/provider/3819f991…/3218c767…`；用 `cmdkey /generic` 写入 Windows 通用凭据（与 Core 的 `CRED_TYPE_GENERIC` 读取一致） |
| sidecar | `artifacts/release/NewManga-0.1.1-win-x64/core-sidecar`（**不是**该 Task 原来用的 RELEASE-REPACK-2 models sidecar） |

## 结果（真实，未修饰）

`terminal=completed_with_failures`，8 个 target：**3 skipped + 5 failed**，全部失败为 `ocr / INVALID_INPUT`；**translate step 从未出现**（上游无可用 OCR 产出，翻译无事可做）。

证据：`ac3-deepseek-rerun.json`（`task_projection.error_codes` 5 条 `INVALID_INPUT`，`counts={total:8, completed:0, failed:5, skipped:3}`）。

## 为什么这次不算「验证成功」

1. **隔离根已被上次运行污染**：`library.db` 里已有该次运行产生的 26 个 region，不是 0-region 初始态；重跑的 pipeline 行为与首次不可比。
2. **sidecar 不同**：原验证用的是 RELEASE-REPACK-2 models sidecar（`core_service` sha `c5531930…`，含 OCR 模型）；本次只有一个 `0.1.1` 发布包，其 `core-sidecar` 未含该模型集。
3. 报告本身已声明「identity 回退运行另有 5 个 OCR `INVALID_INPUT`（region-less 页的既有行为）」，本次 5 个失败与之同型，**不能归因于 DeepSeek 配置**。

## 结论

- 「零代码重跑换取 Core 端到端」这个设想**在当前工作区状态下不成立**：需要**干净的 BOOK-FIXTURE-1 副本（8 页 / 0 regions）+ 含 OCR 模型的 sidecar**，两者都不是现成的。
- **深/浅两条边界仍成立**：provider 层真实调用已验证（`model-api-verification.log`、`vision-ocr-verification.log`）；Core→provider→落库的端到端**未验证**。
- **不改写事实**：本次没有产出任何翻译，没有把 `INVALID_INPUT` 说成配置问题，也没有把 `completed_with_failures` 说成通过。

## 若要继续，最小前置

1. 重建干净 fixture（可从 `BOOK-FIXTURE-1` 私有副本重新生成，或从 `library.db` 回滚到 0-region 状态）；
2. 取得/重建含 OCR 模型的 sidecar（或改探针为直接跑 `python -m bootstrap.core_service`，用源码而非打包件）。
