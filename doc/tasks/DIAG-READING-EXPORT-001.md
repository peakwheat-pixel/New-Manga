---
id: DIAG-READING-EXPORT-001
title: Reading/export completion signal and connection-lifetime flaky diagnosis
kind: diagnostic
status: done
approval: approved_by_user_2026-09-27
execution_approval: approved_by_user_2026-09-27_explicit_task_release
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: []
base_commit: 83de13dfe0521125715c2e26da75b96a63103938
branch: agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis
worktree: C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga
integration_commit: e0a0e784498fc339a4d666dd931cc67cfb65bbdb
---

# DIAG-READING-EXPORT-001 — reading_export 间歇失败诊断

## 来源与目标

[M2-I1 R3 非作者 Review](../reviews/M2-I1-09ad43a-deepseek.md) P3-004 在隔离的 `master@0275290` 全仓首次运行观测到 `tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history` 失败：`exportFinished` 未触发，同时 teardown 有后台 `settleReadingTime` 对已关闭 SQLite 连接写入。第二次基线全仓、交付树两次全仓及两树各三次单文件运行均通过。I1 修改范围不含该测试、reader/export ViewModel 或连接实现，故不归因 I1。

这并非首次出现的症状：[T1.1.1 独立 Review](../../verification/T1.1.1/review-2f116a2.md) 已对同一测试记录既有 export/Qt 信号竞态并建议独立修复窗口；[TASK-034](TASK-034.md) 诊断涉及另一导出测试和终态信号观察。本 Task 只诊断现象、触发条件及证据；不授权修复，也不将历史失败归因到 M2。

## 固定恢复点与角色

- Repository: `G:/CODEX/New Manga`，common Git directory: `G:/CODEX/New Manga/.git`。
- Fixed base/head: `main@83de13dfe0521125715c2e26da75b96a63103938`。
- Owner: DeepSeek Harness；非作者 Reviewer: Codex；Integrator: Codex。
- Owner branch/worktree: `agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis` / `C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`。该 worktree 在释放时为固定 base 上的干净分支。
- Dependencies: `[]`。这是单独的 Legacy reliability 只读诊断，不是 M2 successor，不依赖或重开 M2-RC2。

## Acceptance Criteria

- [x] 记录固定 base、OS/shell、绝对 Python 路径与版本、pytest、PySide6/Qt、SQLite、`openssl`、`QT_QPA_PLATFORM`；测试期间保持同一环境。若找不到项目支持且可导入 PySide6 的 Python 环境，先记录证据并将 Task 标 `blocked`，不得把缺依赖的 pytest skip 记为通过。（[environment.txt](../../verification/DIAG-READING-EXPORT-001/environment.txt)；15 次运行同一 `TASK-012-py312` 解释器；环境 Gate=PASS）
- [x] 按下方固定矩阵运行至多 15 次；每次保存原始 stdout/stderr、精确命令和 `EXIT`。不得因为首次失败而删日志、只报告重跑结果或增加未批准的循环。（15/15 完成、全 EXIT=0、逐次转录 `run-01..15.log`；未扩次数）
- [x] 对比全仓、单文件、单测试及双文件正/反收集顺序；根据源码与运行记录分析 `exportFinished` 投递、测试等待、reader heartbeat/`settleReadingTime` 和 SQLite 连接生命周期，提出可证伪的根因假设及最多两个只读/隔离探针。（矩阵五场景 + 报告 §4 + 恰好 2 个隔离探针，均无 monkeypatch/编辑产品或测试文件）
- [x] 如果矩阵复现失败，保留首次失败的完整日志和可复现上下文；如果未复现，报告准确次数与 `NOT_REPRODUCED`，不声称已修复。测试失败、skip、环境差异和阻塞均逐项披露。（0 失败 → `NOT_REPRODUCED`；run-01 的 11 个环境 skip 逐条披露，未计为通过）
- [x] 提交诊断报告、证据、Handoff；给出风险边界及是否建议另立修复 Task。修复 Task 需由 Codex 另行冻结并释放。（[报告](../../doc/research/DIAG-READING-EXPORT-001.md)、[Handoff](../../doc/handoffs/DIAG-READING-EXPORT-001-8b36e98e.md)；建议 FIX-A/FIX-B，已另行登记为 `proposed`）
- [x] Codex 以非作者身份完成范围/证据 Review 并集成；Review 或集成 Gate 未过时 Task 不得标为 `done`。（[Review](../reviews/DIAG-READING-EXPORT-001-77c661b0.md) `approved` @ `77c661b0`；integration_commit=`e0a0e784498fc339a4d666dd931cc67cfb65bbdb`）

## 允许修改范围

- `doc/tasks/DIAG-READING-EXPORT-001.md`（仅 Task 状态与实际交付记录）。
- `doc/research/DIAG-READING-EXPORT-001.md`。
- `verification/DIAG-READING-EXPORT-001/**`。
- `doc/handoffs/DIAG-READING-EXPORT-001-*.md`（自己的 Handoff）。
- 只读检查 `tests/reading_export/**`、`src/ui/viewmodels/{reader,export}/**`、相关 SQLite/服务代码与历史证据。

## 禁止范围

不修改任何生产代码、测试文件/断言/等待预算、Schema、Domain Contract、依赖文件、M2-I1/I2 产品文件或 T3.2.1 Gate；不改写历史 Review、Handoff、提交或既有证据。不得添加 skip、通过增加等待或重试掩盖首次失败。诊断中发现的修复、接口或范围扩展须另由 Codex 登记并释放。

## 固定验证矩阵

所有命令从仓库根目录、同一个已冻结 Python 环境运行；命令中的 `python` 必须解析到环境清单所记的绝对解释器。每一行的每次运行单独保存原始输出、命令、开始时间、环境编号和 exit code。最多 15 次：

| Run IDs | 场景 | 每次命令 | 次数 |
|---|---|---|---:|
| `01` | 全仓基线 | `python -m pytest -q -p no:cacheprovider -rs tests` | 1 |
| `02`–`04` | reading_export 单文件 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export/test_viewmodels.py` | 3，连续独立运行 |
| `05`–`09` | 目标测试隔离 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history` | 5，连续独立运行 |
| `10`–`12` | reader → export 收集顺序 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export/test_reading.py tests/reading_export/test_viewmodels.py` | 3 |
| `13`–`15` | export → reader 收集顺序 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export/test_viewmodels.py tests/reading_export/test_reading.py` | 3 |

如需矩阵以外的动态探针，最多两个；须隔离保存在 `verification/DIAG-READING-EXPORT-001/`，不得编辑或 monkeypatch 产品/测试文件，不得引入新依赖。若要再扩大运行次数或探针范围，停止并交 Codex 另作范围决定。

## 交付物与 Gate

- `doc/research/DIAG-READING-EXPORT-001.md`：方法、环境、逐项结果、证据链接、假设/反证、风险、结论与修复建议。
- `verification/DIAG-READING-EXPORT-001/environment.txt`：冻结环境及导入检查结果。
- `verification/DIAG-READING-EXPORT-001/matrix.tsv`：15 个 Run ID 的命令、顺序、结果、exit 和日志路径；未运行项写 `NOT_RUN`/`BLOCKED`。
- `verification/DIAG-READING-EXPORT-001/run-*.log`：逐次原始转录，包含 stdout、stderr 与 `EXIT=<code>`。
- 新 Handoff：固定 Owner head、文件清单、所有运行结果、阻塞和剩余风险。
- Gate：15 次矩阵完成并留证，或在环境前置条件失败时以证据标为 `blocked`；诊断结论与原始日志可交叉核对；无越权文件差异；Codex 非作者 Review approved；Codex 集成核验通过。不得把 `NOT_RUN`/`BLOCKED` 表述为 PASS。

## 启动与认领

本 Task 已由用户于 2026-09-27 明确授权并由 Codex 按协作协议 §5.1 释放为 `ready`。Owner 先记录工作区恢复检查与环境启动 Gate；开始实际诊断前，仅从本 Task 注册/释放 commit 将这一个 Task 文件复制到上述 Owner worktree，改为 `in_progress` 并提交 claim。不得把治理释放 commit 合入 Owner 分支，也不得在 claim commit 前运行验证矩阵。若环境 Gate 失败，提交环境证据并置 `blocked`，等待 Codex 决定；不改产品代码、不自行解阻。

本 Task 不属于 M2 首波授权、不重开 M2-RC2，也不改变 T3.2.1 Full Gate。历史来源证据：[M2-I1 Review](../../doc/reviews/M2-I1-09ad43a-deepseek.md)、[M2-I1 integration](../../verification/M2-I1/integration-cff1e0a/record.md)。

## 交付记录（Owner=DeepSeek Harness）

- **认领**：`064ff980`（仅取入释放版 Task 文件 + `status: in_progress`；未把治理释放 commit `ceab572b` 合入 Owner 分支；claim 前未运行验证矩阵）。
- **环境 Gate：PASS** —— 冻结解释器 `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`（Python 3.12.3 / PySide6 6.11.2 / Qt 6.11.2 / pytest 9.1.1 / sqlite3 3.45.1；与 `requirements*.txt` pin 一致）。清单与导入检查：[environment.txt](../../verification/DIAG-READING-EXPORT-001/environment.txt)。主 `python`（3.14.6）无 PySide6，未使用。
- **固定矩阵：15/15 次完成，全部 exit 0，目标测试 0 次失败 → `NOT_REPRODUCED`**。全仓 `1310 passed, 11 skipped`；单文件 15 passed ×3；目标测试 1 passed ×5；双文件正/反序 30 passed ×6。命令、顺序、结果、exit、日志、起止时间：[matrix.tsv](../../verification/DIAG-READING-EXPORT-001/matrix.tsv)；逐次原始转录：`verification/DIAG-READING-EXPORT-001/run-01..15.log`（含 `EXIT=`）。**11 个 skip 逐条为环境缺依赖**（6 OpenSSL、2 docTR、1 numpy、2 torch），不计为通过。
- **机制结论（报告 §4）**：症状 A（`exportFinished` 未投递）＝终态信号排队投递 vs 等待谓词轮询 `running` 的竞态 —— 探针 1 隔离 0/400、忙碌主线程 **26/200** 命中历史诊断形态；症状 B（后台 `settleReadingTime` 写已关闭 SQLite）＝未停止的读者心跳（`openChapter` 启动、仅 `closeReader` 停止）—— 探针 2 **确定性复现**，栈帧与历史 stderr 逐帧相同且失败后心跳仍 active。两者均与 M2-I1/I2 交付无关，与 [T1.1.1 Review R2-I02](../../verification/T1.1.1/review-2f116a2.md) 既有记录一致。
- **交付物**：本 Task 文件、[doc/research/DIAG-READING-EXPORT-001.md](../../doc/research/DIAG-READING-EXPORT-001.md)、Handoff `doc/handoffs/DIAG-READING-EXPORT-001-<head>.md`、`verification/DIAG-READING-EXPORT-001/**`（environment.txt、matrix.tsv、run-01..15.log、2 个隔离探针脚本与日志）。
- **越权核对**：相对 base 的唯一差异是新目录 `verification/DIAG-READING-EXPORT-001/` 与本文档/报告/Handoff；**未修改任何生产代码、测试文件/断言/等待预算、Schema、依赖或历史证据**；未加 skip、未加重试、未以等待掩盖失败。
- 不授权修复：建议另立 FIX-A（等待/投递语义）与 FIX-B（读者心跳生命周期），由 Codex 冻结范围后释放。状态保持 `in_progress`，等 Codex 非作者 Review 与集成；本 Task 在 Review/集成 Gate 通过前不得标 `done`。

## 集成记录（Integrator=Codex 代行，2026-09-28）

- **非作者 Review**：[DIAG-READING-EXPORT-001-77c661b0](../reviews/DIAG-READING-EXPORT-001-77c661b0.md) `decision=approved`，绑定 `base=83de13df` → `reviewed_head=77c661b0`；0×P0/P1，1×P2（R-001：报告 §4.1 把"全仓事件负载"写成确定放大条件、与 §5 U3 未决矛盾——集成层修正措辞，保留 U3）、1×P3（R-002：探针 r1/r2 中间日志被覆盖，accepted）。U1–U3 维持未决，U4（两症状独立）采信。
- **集成 merge**：`e0a0e784498fc339a4d666dd931cc67cfb65bbdb`（parents `c90b8b27`（Review）+ `77c661b0`（Owner tip）；Owner 提交历史未改写）。唯一冲突 `doc/tasks/DIAG-READING-EXPORT-001.md` 按用户指示以 Owner 已交付版为底。
- **集成核验**：24 路径全授权、禁改路径零改动、`git diff --check` exit 0；`_finish` 顺序 `0275290` vs base 逐字节相同；矩阵 15 条记录与 run-01..15.log 逐条一致。详见 [integration-e0a0e784](../../verification/DIAG-READING-EXPORT-001/integration-e0a0e784/integration.md)。
- **结论口径**：`NOT_REPRODUCED` 维持，不写"已解决"；该 flaky 的修复归属 [DIAG-READING-EXPORT-001-FIX-A](DIAG-READING-EXPORT-001-FIX-A.md) 与 [DIAG-READING-EXPORT-001-FIX-B](DIAG-READING-EXPORT-001-FIX-B.md)（均 `proposed / NOT_RELEASED`，未启动实现）。
