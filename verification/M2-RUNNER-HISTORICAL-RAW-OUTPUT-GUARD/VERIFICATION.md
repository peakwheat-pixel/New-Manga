# 验证证据记录：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD

## 1. 任务背景与目标

本任务旨在关闭 DeepSeek Harness r4 审查发现项 `R-001`（见 `doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md` §Findings）：
两个 M2 验收 runner（`verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py`）此前的 `--output-dir` 参数为可选，默认指向历史已跟踪目录（`verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/`）。若操作者未显式传参运行 runner，将意外覆盖历史 raw 证据。

本任务实施内容：
1. 在两个 runner 的现有 `argparse` 中将 `--output-dir` 设为必选参数（`required=True`），省略时立即以 usage error / exit code 2 失败退出，且失败发生在任何目录创建、lab 建立或 Gate 动作之前。
2. 更新两个 runner 的模块文档及 `packaging/m2ac5/README.md`，示例显式指定的隔离输出目录，移除默认输出至历史 raw 目录的陈述。
3. 新增回归测试 `tests/packaging/test_runner_output_dir_required.py`，覆盖两个 runner 的“省略参数拒绝”和“显式参数解析”，测试在参数解析完成后立即拦截，不启动构建、安装或产品 Gate。
4. 验证历史已跟踪的 61 个 raw 文件集合及内容完全未被修改（byte-identical）。

---

## 2. 验证环境

- **主机环境**：Windows 11 (HOME-MY)
- **Shell**：PowerShell 7.5.0-preview.3 / pwsh
- **Python 运行时**：
  - 系统 Python：`C:\Python314\python.exe` (Python 3.14.6)
  - 任务环境 Python：`G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` (Python 3.12.3)
- **代码基线与分支**：
  - Base commit: `e9b66455356c56e0fe6720d658b46bdbdbeb53b5`
  - Start commit: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
  - Code delivery HEAD: `1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661`
  - 分支：`agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
  - 工作树：`G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
  - Common Git dir: `G:/CODEX/New Manga/.git`

---

## 3. 测试与验证执行记录

| 验证项 / 场景 | 执行命令 | 环境 / 解释器 | 退出码 | 结果概要 | 证据日志 |
|---|---|---|---|---|---|
| **AC1/AC2/AC4 参数回归测试 (Python 3.14)** | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.14.6 | 0 | **9 passed** (0.53s)；涵盖两个 runner 的 CLI 缺省调用子进程 exit 2 报错、解析器 SystemExit(2)、显式路径解析、main 拦截、raw 目录未触碰 | [`pytest-regression.log`](pytest-regression.log) |
| **AC1/AC2/AC4 参数回归测试 (Python 3.12)** | `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.12.3 | 0 | **9 passed** (0.58s) | [`pytest-regression-py312.log`](pytest-regression-py312.log) |
| **AC4 历史 raw 文件完整性对比** | 检查 `verification/M2-RC2/raw` (25文件) 与 `verification/M2-AC5/raw` (36文件) 共 61 个文件的 git blob 哈希及 working tree 状态 | Python / Git CLI | 0 | **PASS (byte-identical)**；全部 61 个已跟踪文件与 HEAD 逐位一致，0 修改，0 未跟踪 | [`raw-integrity.log`](raw-integrity.log) |
| **快照护栏回归** | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Python 3.14.6 | 0 | **16 actual-predicate cases PASS**；两个 runner 的语法与静态期望对齐完全正常 | [`check-snapshots.log`](check-snapshots.log) |
| **AC5 范围检查 (git diff --name-only)** | `git diff --name-only d12ebc7a..1c49fe38` | Git CLI | 0 | 变更仅限 4 个允许路径文件：`packaging/m2ac5/README.md`、`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_runner_output_dir_required.py`、`verification/M2-RC2/run_e2e.py` | [`git-diff-name-only.log`](git-diff-name-only.log) |
| **AC5 代码增减统计 (git diff --stat)** | `git diff --stat d12ebc7a..1c49fe38` | Git CLI | 0 | `4 files changed, 199 insertions(+), 16 deletions(-)` | [`git-diff-stat.log`](git-diff-stat.log) |
| **AC5 空白与格式检查 (git diff --check)** | `git diff --check d12ebc7a..1c49fe38` | Git CLI | 0 | **PASS**；零空白错误，零警告 | [`git-diff-check.log`](git-diff-check.log) |

---

## 4. 未执行项目说明（NOT_RUN）

- **完整 Dev Gate / Packaged Gate / NSIS 安装 / Sidecar 构建**：按 Task 明确规定 **NOT_RUN**。本 Task 属于 CLI 参数保护回归（parser-only 边界防护），禁止运行或触发完整产品构建与 Gate。参数测试已通过在 `parse_args` 后拦截执行，确保不进入 runner 主体。本报告不将 parser 回归测试表述为产品 Gate PASS。
