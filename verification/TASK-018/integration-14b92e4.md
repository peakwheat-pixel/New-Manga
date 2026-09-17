# TASK-018 集成验证：`14b92e4`（修订切片）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `8c63f9b19f6daf065847aefce01bda578332cd6b` |
| 被审 head（delivery） | `50633158d98f4382fe17da070454423d992b7496` |
| 元数据 head | `b10f1ba` |
| Review 报告 | [`doc/reviews/TASK-018-5063315.md`](../../doc/reviews/TASK-018-5063315.md)（decision=`approved`，覆盖首轮 R-001～R-007 与修订切片 R-101～R-104） |
| implementation merge / integration commit | `14b92e4`（merge，parents `d49679b` + `b10f1ba`） |
| 修订切片 head | `d7c10d4`（元数据 `3b38d39`），本次集成一并带入 |
| 前次集成基线（仍有效） | `4d189ce`（merge，parents `461e639`+`ef6d1c3`，被审 head `6c33e7f`）→ 见 [integration-4d189ce.md](integration-4d189ce.md) |
| 环境 | Windows `10.0.26200`；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）；PySide6 6.11.2；`PYTHONPATH=experiments/TASK-018`、`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM` |

## 复验结果（master `14b92e4`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m unittest experiments/TASK-018/test_mask_protocol.py` | 0 | **12** | **0** | `OK`（该文件自首轮起未被改动） | 无 |
| 2 | `…python.exe -m unittest experiments/TASK-018/test_route_gating.py` | 0 | **13** | **0** | `OK` | 无（需可导入 `run_experiment` 的解释器，故依赖 PySide6，见 R-101 更正） |
| 3 | `…python.exe <副本>/experiments/TASK-018/run_experiment.py --repeat 3` | 0 | N/A | N/A | `{"MEASURED": 10, "BLOCKED": 20}`；`blocked_stage` 20/20 `not_implemented`；`protected_violations` 10/10 为空；`protected_box_violations` **20 框全 0**；`results/` 仅 10 张 PNG；BLOCKED 记录无 `output_image`/`output_sha256` | 进程执行，N/A |
| 4 | `…python.exe -m pytest -q -p no:cacheprovider`（全仓） | 0 | **530** | **6** | `530 passed, 6 skipped in ~23 s` | 6 项均为 `openssl unavailable`（`tests/network/`） |

命令 3 在 `%TEMP%\task018-int2-144747` 的整目录副本中执行（harness 会把 `results/experiment.json` 写在实验根内，直接在仓库运行会改写交付数据；该限制的处置见 R-003）。仓库内 `results/experiment.json` 在本次集成中**未被覆盖**：其 `routes` 块与全部确定性字段（`mask_sha256`、`output_sha256`、`sample_sha256`、`parameters`、`mask`、`protected_box_violations`、`blocked_stage`、`requirement_probes`）与复跑输出**逐项一致，0 差异**。

**flaky 说明（沿用前次登记）**：在 `8c63f9b` 基线的上一轮集成检查中，全仓套件曾 7 次运行出现 1 次 `1 failed, 529 passed`（未捕获用例名，其后连续 4 次通过）。本次集成复验 1 次为 `530 passed, 6 skipped`，未复现；TASK-018 只涉及 `experiments/`、`doc/`、`verification/`，不在 `pytest.ini` 的 `testpaths = tests` 范围内。该抖动仍作为环境级移交项保留，不记为通过也不归因于本 Task。

## 验收结论

- [x] 独立 Review 由非作者（Codex）执行并绑定固定 base/head；修订切片的 R-101/R-102 已按事实修正、R-103 已修、R-104 以等价防护部分落地，均经 Reviewer 独立核对。
- [x] 五条候选路线可用范围与 `BLOCKED` 结论保持：20 条学习型路线记录 `BLOCKED`，`blocked_stage` 全为 `not_implemented`，无伪造图、数字或 Hash；`default_eligible` 仅两个非模型基线为 `true`。
- [x] 非目标像素保护证据完整：final Mask 外违规 10/10 = 0，且 manifest 的 `protected_boxes` **逐框断言 20/20 = 0**。
- [x] fail-closed 已生效（R-007）：门控为显式 `FILLERS` 映射 + 未登记即拒绝，依赖齐备也不会授权未实现路线（反例见 [revision-d7c10d4.md](revision-d7c10d4.md) §4）。
- [x] 白名单越界 0；未修改生产 `src/`、`tests/`、Schema、依赖清单、`AGENTS.md`、其他或冻结 Task；未扩展到 TASK-019；未 push。
- [ ] 四条学习型路线的质量/耗时/内存/显存仍 `BLOCKED`；Mask 内部结构损伤量化、真实 OOM、真实漫画样例仍 `NOT_RUN`——**不得视为通过**。

## 未关闭项

| ID | 级别 | 内容 | 状态 |
|---|---|---|---|
| R-104（剩余部分） | P3 | `ROUTES[*].implementation` 非 None ⇒ route 必须在 `FILLERS` 注册的一致性断言未实施；误配会在运行中途 `KeyError`（响亮失败、不产生伪数据，但会留下部分产物） | deferred，登记于实验日志 §7.3 与研究报告 §9.2 |
| — | — | 学习型路线质量/性能、Mask 内部结构损伤、真实 OOM、真实漫画样例 | BLOCKED / NOT_RUN，原因未变 |
