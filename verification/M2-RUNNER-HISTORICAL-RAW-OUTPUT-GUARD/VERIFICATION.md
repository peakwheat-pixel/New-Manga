# 验证证据记录：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD（r1 修订）

## 1. 任务背景与目标

本任务旨在关闭 DeepSeek Harness r4 审查发现项 `R-001`（见 `doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md` §Findings）：
两个 M2 验收 runner（`verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py`）此前的 `--output-dir` 参数为可选，默认指向历史已跟踪目录（`verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/`）。若操作者未显式传参运行 runner，将意外覆盖历史 raw 证据。

在收到 DeepSeek Harness r1 审查报告（`doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38-dsh-r1.md`，`decision=changes_requested`）后，本次 r1 修订处理闭合项如下：
1. **R-01 (P1)**：修正 `packaging/m2ac5/README.md` 第 4 节示例，将 `--output-dir` 指向历史 raw 树之外的独立临时路径（`"$env:TEMP/m2ac5-cleanstart-artifacts"`），并强化必选参数说明。
2. **R-02 (P2)**：保留旧 Handoff `1c49fe38` 只读；新建 `e167e723` Handoff，严格按 `git diff --stat` 和 `git diff --numstat` 填写文件增减统计，记录 R-01..R-07 disposition。
3. **R-03 (P2)**：入库可复现脚本 `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py`，支持运行前后快照比对，验证 61 个历史文件的 SHA-256 及 git blob hash，日志记录规范，明确非 Gate PASS。
4. **R-04 (P2)**：从 `tests/packaging/test_runner_output_dir_required.py` 移除外部 VCS 状态断言（移除 `test_tracked_raw_evidence_directories_unmodified`），保持测试纯粹与 hermetic。
5. **R-05 (P3)**：在 `test_ac5_main_interception_after_parse_args` 中将 monkeypatch 拦截点提前至 `Path.mkdir`，实现零目录创建副作用拦截。
6. **R-06 (P3)**：简化子进程缺失参数的断言为 `assert "required" in err`；整体加载 runner/conftest 的复杂度仍 deferred，属于可选建议，不扩大本 Task。
7. **R-07 (P3)**：Owner 遵守治理边界；Codex 已通过主线治理提交 `8ad092d2` 更新 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 和导航元数据。

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
  - Code delivery HEAD: `e167e72351d6f725653d1f16b210a54f435e621f` (`e167e723`)
  - 分支：`agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
  - 工作树：`G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
  - Common Git dir: `G:/CODEX/New Manga/.git`

---

## 3. 测试与验证执行记录

| 验证项 / 场景 | 执行命令 | 环境 / 解释器 | 退出码 | 结果概要 | 证据日志 |
|---|---|---|---|---|---|
| **AC1/AC2/AC4 参数回归测试 (Python 3.14)** | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.14.6 @ `e167e723` | 0 | **8 passed** (0.51s)；涵盖两个 runner 的 CLI 缺省调用子进程 exit 2 报错、解析器 SystemExit(2)、显式路径解析、main 提前拦截（无目录创建副作用） | [`pytest-regression.log`](pytest-regression.log) |
| **AC1/AC2/AC4 参数回归测试 (Python 3.12)** | `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.12.3 @ `e167e723` | 0 | **8 passed** (0.55s) | [`pytest-regression-py312.log`](pytest-regression-py312.log) |
| **AC4 历史 raw 完整性前后比对 (R-03)** | `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py --compare-after ...` | Python 3.14.6 @ `e167e723` | 0 | **PASS (byte-identical)**；全部 61 个已跟踪文件与运行前快照逐位一致；两个历史 raw 路径的 Git status clean，无修改或 untracked 文件 | [`raw-integrity.log`](raw-integrity.log) |
| **快照护栏回归** | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Python 3.14.6 @ `e167e723` | 0 | **16 actual-predicate cases PASS**；两个 runner 的语法与静态期望对齐完全正常 | [`check-snapshots.log`](check-snapshots.log) |
| **AC5 范围检查 (git diff --name-only)** | `git diff --name-only d12ebc7a..e167e723` | Git CLI @ `e167e723` | 0 | 变更仅限 4 个 allowed_paths 代码文件：`packaging/m2ac5/README.md`、`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_runner_output_dir_required.py`、`verification/M2-RC2/run_e2e.py` | [`git-diff-name-only.log`](git-diff-name-only.log) |
| **AC5 代码增减统计 (git diff --stat)** | `git diff --stat d12ebc7a..e167e723` | Git CLI @ `e167e723` | 0 | 纯代码 4 文件：`179 insertions(+), 16 deletions(-)` | [`git-diff-stat.log`](git-diff-stat.log) |
| **AC5 空白与格式检查 (git diff --check)** | `git diff --check d12ebc7a..e167e723` | Git CLI @ `e167e723` | 0 | **PASS**；零空白错误，零警告 | [`git-diff-check.log`](git-diff-check.log) |

---

## 4. 未执行项目说明（NOT_RUN）

- **派发状态说明**：本轮 `agy` 进程 EXIT=0，但输出 JSON 的 `status` 字段为 `ERROR`。Codex 不以该字段作为成功依据，已在实际 Owner worktree 独立核验提交、测试、raw 快照和 Git 范围；DSH r2 仍是必需 Gate。

- **完整 Dev Gate / Packaged Gate / NSIS 安装 / Sidecar 构建**：按 Task 明确规定 **NOT_RUN**。本 Task 属于 CLI 参数保护回归（parser-only 边界防护），禁止运行或触发完整产品构建与 Gate。参数测试已通过在 `parse_args` 后拦截执行，确保不进入 runner 主体。本报告不将 parser 回归测试表述为产品 Gate PASS。
