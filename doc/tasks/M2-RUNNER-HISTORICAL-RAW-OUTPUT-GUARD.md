---
id: M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
title: Require explicit isolated output directories for M2 runner commands
kind: implementation
status: ready
approval: user_authorized_release_20261008
suggested_owner: Antigravity
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-RUNNER-SNAPSHOT-DEBT]
base_commit: e9b66455356c56e0fe6720d658b46bdbdbeb53b5
branch: agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
worktree: G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity
integration_commit: null
---

# M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD：阻止默认覆盖历史 raw 证据

## 来源与目标

来源：已完成的 [M2-RUNNER-SNAPSHOT-DEBT](M2-RUNNER-SNAPSHOT-DEBT.md) 的非阻断 deferred finding R-001；证据见 [DSH r4 Review](../reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md) §Findings。

当前 `verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py` 的 `--output-dir` 可省略，默认分别写入历史 tracked 目录 `verification/M2-RC2/raw/`、`verification/M2-AC5/raw/`。目标是缺省调用在任何输出目录创建、runner lab 建立或 Gate 动作之前失败，避免意外覆盖历史证据；调用者须显式提供隔离输出目录。复用现有 `argparse`，不新增通用抽象。

## Acceptance Criteria

- [ ] AC1：两个 runner 的 CLI 都要求显式 `--output-dir`；省略时以 argparse usage error / exit 2 失败，且失败发生在任何文件系统副作用及 Gate 启动之前。
- [ ] AC2：传入显式 `--output-dir <isolated-path>` 时 argparse 接受参数，并继续将该路径作为本次运行输出根；不改变 Gate 场景、阈值、产物结构或其他 runner 行为。
- [ ] AC3：更新 `packaging/m2ac5/README.md` 当前验收命令，示范新建/隔离输出目录；用法说明不再声称 runner 会默认落入历史 raw 目录。历史 Handoff / verification 原始记录不改写。
- [ ] AC4：新增回归测试覆盖两个 runner 的“省略参数拒绝”和“显式参数解析”；测试在调用 runner 主体前停止，避免触发构建、安装或产品 Gate。确认 `verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/` 的 tracked 文件集合及内容未被测试改变。
- [ ] AC5：实现差量严格限于本 Task allowed_paths；交付固定 commit、测试日志及 Handoff；非作者 DSH 独立审查通过后由 Codex 集成并完成集成验证。

## 允许修改范围

- `packaging/m2ac5/run_clean_start_e2e.py`
- `packaging/m2ac5/README.md`
- `verification/M2-RC2/run_e2e.py`
- `tests/packaging/test_runner_output_dir_required.py`（新建的最小回归测试）
- 本 Task 文件 `doc/tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md`
- `doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-<short-head>.md`
- `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/**`
- Codex 独占维护的 Task 导航/状态元数据，仅更新状态、链接和本 Task 导航，不改需求或扩大代码范围。

## 禁止范围

- 禁止改动 `src/**`、`apps/**`、Schema、共享 IPC、依赖、项目产品契约及其它 tests/packaging 文件。
- 禁止改写既有 `verification/**/raw/**`、历史 Review/Handoff/日志；不执行会向历史 raw 目录写入的 runner 命令。
- 不运行 Sidecar/NSIS 构建、安装、完整 Dev/Packaged Gate；本 Task 只验证 CLI 参数保护与隔离输出路径解析。
- 不部署、不推送、不合并主线；不访问或修改用户漫画、安装目录、Qoder 本地报表或其他 Agent 的工作区；不 reset/clean/stash 他人改动。
- 若必须修改共享契约、Schema、依赖或扩大允许路径，暂停该部分并由 Codex重新冻结 Task。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 parser regression | `python -m pytest -q tests/packaging/test_runner_output_dir_required.py` | Windows/Python；测试在 `parse_args` 成功后拦截，不进入 runner 主体 | NOT_RUN | `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/` |
| AC4 历史 raw 不变 | 对两个 tracked raw 目录运行前后文件集合/内容摘要对比 | 与 parser regression 同一 checkout | NOT_RUN | `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/` |
| 范围与空白 | `git diff --name-only <base>...<head>`；`git diff --check <base>...<head>` | 固定 owner base/head | NOT_RUN | Handoff / verification |

## 依赖、风险与阻塞

- 硬依赖：`M2-RUNNER-SNAPSHOT-DEBT` 已 done @ `73588624`。
- R-001 为防误操作的 CLI 边界修复；required 参数不能阻止操作者显式选中历史路径，因此本 Task 仅消除危险的隐式默认，不新增路径策略或清理行为。
- 运行完整产品 Gate 非本 Task 的必要条件；不得将 parser 回归测试表述为产品 Gate PASS。

## 交付与运行记录

- Task release evidence：待 Codex 写入 `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/release.md`。
- Handoff：尚无。
- Review：尚无。
- 实际测试：NOT_RUN；Owner 开始后逐项记录真实命令、shell/解释器、EXIT 和日志路径。
