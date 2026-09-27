# M2-I1 R3 集成记录（2026-09-25）

## 固定点与集成

- 集成前 `master`：`0275290c3cc64e92dc53157b7d35028447d4d54f`；已含 M2-I2 集成。
- 固定 I1 R3 Product Delivery：`09ad43a03c324eb52def326a6b7a49cb3da03efa`；作者 R3 Handoff head：`8dab0abbc667e09054616d4f0b0f5a76b1a04d9e`。
- DeepSeek Harness [非作者 Review](../../../doc/reviews/M2-I1-09ad43a-deepseek.md)：`approved`；Reviewer 非实现者。Review 的原始证据在 [`review-09ad43a/`](../review-09ad43a/)。
- Codex 在隔离 worktree `G:/CODEX/New Manga.worktrees/M2-I1-integration-09ad43a` 从 `0275290` 执行 `git merge --no-ff --no-edit 09ad43a`，产品合并提交：**`cff1e0a8658f57a2e9caf774a9de0961e8f65da3`**。主工作树的既有未提交/未跟踪内容未参与合并。
- `8dab0ab` 中的 R3 Handoff 与 `12-r3-reconcile-verification.log` 作为已审文档取入集成元数据；`09ad43a` 之外无产品代码改写。Review 报告及原始日志由用户提供，集成到版本化证据。

## 集成后验证

| 项 | 命令/环境 | 结果与证据 |
|---|---|---|
| 全仓 | Windows PowerShell；Python `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（3.12.3 + PySide6 6.11.2）；PATH 加 `C:/Program Files/Git/usr/bin` 的 `openssl`；`python -m pytest -q -p no:cacheprovider -rs tests`；在 `cff1e0a` 合并树运行 | **1238 passed, 5 skipped, exit 0**；docTR×2、numpy×1、torch×2 均为环境缺依赖，逐项见 [full-suite.log](full-suite.log)。另有 1 个 `imghdr` deprecation warning。 |
| 架构守卫 | 同一解释器；`python -m pytest -q -p no:cacheprovider -rs tests/core/test_architecture.py` | **16 passed, exit 0**；见 [architecture.log](architecture.log)。 |
| 范围 | `git diff --name-only 0275290 cff1e0a`、`git diff --check 0275290 cff1e0a` | **21 个授权路径，diff check exit 0**；I2 application/UI、Domain/Ports、Schema、T3.2.1 零修改。原始列表见 [scope-and-diff.log](scope-and-diff.log)。 |

全仓结果与 DeepSeek R3 Review 交付树两次 `1238 passed, 5 skipped` 一致；相对 `0275290` 基线稳定运行的 `1229 passed, 5 skipped`，九项差值为 I1 新增 Core 探针八项和 P-01 回归一项。真实人工 GUI 交互 `NOT_RUN`，沿用 R3 Review 的准确边界。集成后验证完成，故 Task 可置 `done`。

## Review P3 disposition

- **P3-001 closed**：`12-r3-reconcile-verification.log:80` 已改为“delta 包含已审 I1 产品代码，未新增产品改写”。
- **P3-002 closed**：`verification/M2-I1/README.md` 登记 R3、DeepSeek Review 与集成证据。
- **P3-003 closed**：`doc/tasks/M2-I1.md` 已统一 `status=done`、`reviewer=DeepSeek Harness`、`reconcile_status=integrated_verified`、`integration_commit=cff1e0a...`。
- **P3-004 tracked separately**：同一 `reading_export` 测试在 `0275290` 隔离基线全仓一次失败、复跑通过，且 T1.1.1 历史 Review 已记录此信号竞态。其连接关闭异常值得诊断；建立 [DIAG-READING-EXPORT-001](../../../doc/tasks/DIAG-READING-EXPORT-001.md) 为 `proposed / NOT_RELEASED` 的独立 Legacy 可靠性 Task。该发现不归因 I1，也不改变 T3.2.1 Full Gate。

M2-C1/M2-S1 仍未释放；M2-UI1 按其独立 Task Gate 推进。
