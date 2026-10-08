---
task_id: M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
author: Antigravity
recipient: DeepSeek Harness
base_commit: e9b66455356c56e0fe6720d658b46bdbdbeb53b5
start_head: d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10
delivery_head: 1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661
status: in_review
---

# Handoff：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD（关闭 DSH r4 R-001）

## 交付结果

### 1. 目标与实现范围

本任务闭合 DeepSeek Harness r4 独立审查中指出的非阻断遗留问题 `R-001`（见 [`doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md) §Findings）：
`verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py` 两处 runner 的 `--output-dir` 参数此前为可选且默认指向已跟踪的历史 raw 证据目录（`verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/`），后续缺省调用可能意外覆盖历史证据。

实现内容严格限定于本任务 `allowed_paths`：
1. [`packaging/m2ac5/run_clean_start_e2e.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/packaging/m2ac5/run_clean_start_e2e.py)：
   - 提取 `build_parser()` 函数，将 `--output-dir` 设为 `required=True`（移除了旧的默认值 `RAW`）；
   - 更新模块级文档的用法说明，明确 `--output-dir <path>` 为必传参数，移除“默认输出至 `verification/M2-AC5/raw/`”的表述；
   - 更新 `main(argv: list[str] | None = None)`，支持传入参数列表并在 `parse_args` 阶段完成校验。缺省参数时由 argparse 立即输出 usage 错误并以 exit code 2 失败退出，发生在任何 lab/输出目录创建或 Gate 工作之前。
2. [`verification/M2-RC2/run_e2e.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/verification/M2-RC2/run_e2e.py)：
   - 提取 `build_parser()` 函数，将 `--output-dir` 设为 `required=True`（移除了旧的默认值 `RAW`）；
   - 更新模块级文档的用法说明，明确 `--output-dir PATH` 为必传参数，移除“默认输出至 `verification/M2-RC2/raw/`”的表述；
   - 更新 `main(argv: list[str] | None = None)`，同样在任何 lab/输出目录创建之前完成校验并 fail-closed。
3. [`packaging/m2ac5/README.md`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/packaging/m2ac5/README.md)：
   - 更新第 4 节验收 runner 示例命令，增加 `--output-dir "verification/M2-AC5/raw/run-isolated"`；
   - 说明 `--output-dir` 为必选参数，不再声称默认落入历史 raw 目录，明确省略参数将以 usage error / exit 2 报错退出以保护历史 raw 证据。
4. [`tests/packaging/test_runner_output_dir_required.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/tests/packaging/test_runner_output_dir_required.py)：
   - 新增最小回归测试文件（9 个测试用例，全绿通过）；
   - 覆盖两个 runner 的子进程缺省调用报错（exit 2，stderr 包含 usage/required）；
   - 覆盖进程内解析器缺少参数时的 `SystemExit(2)` 拒绝；
   - 覆盖传入显式 `--output-dir` 时的参数正常解析（含附加参数组合）；
   - 覆盖在 `parse_args` 成功后立即拦截执行，验证 `RAW` 输出路径正确赋值且绝不进入 runner 主体或触发构建、安装、Gate 动作；
   - 覆盖历史 tracked raw 证据目录完整性断言。

### 2. 代码提交与差量

- **Code Delivery HEAD**：[`1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity) (`1c49fe38`)
  - 提交信息：`fix(packaging): require explicit output-dir for M2 runners to protect historical raw evidence`
- **代码差量**：`git diff --stat d12ebc7a..1c49fe38`
  - 4 个文件变更：+199 / −16
  - `packaging/m2ac5/README.md` (+5 / -2)
  - `packaging/m2ac5/run_clean_start_e2e.py` (+19 / -8)
  - `tests/packaging/test_runner_output_dir_required.py` (+173)
  - `verification/M2-RC2/run_e2e.py` (+18 / -6)
- **禁止范围核对**：`src/**`、`apps/**`、其它 `tests/**`、Schema、依赖 0 差量；历史 raw 证据 0 差量。

### 3. Acceptance Criteria 对照

| AC 项 | 目标要求 | 达成事实与状态 |
|---|---|---|
| **AC1** | 两个 runner 的 CLI 都要求显式 `--output-dir`；省略时以 argparse usage error / exit 2 失败，且失败发生在任何文件系统副作用及 Gate 启动之前 | **PASS**：两 runner 均配置 `parser.add_argument("--output-dir", type=Path, required=True)`；测试证实 subprocess 与 parse_args 均在副作用前 exit 2 失败。 |
| **AC2** | 传入显式 `--output-dir <isolated-path>` 时 argparse 接受参数，并继续将该路径作为本次运行输出根；不改变 Gate 场景、阈值、产物结构或其他 runner 行为 | **PASS**：解析器正常接收 `output_dir` 并在 `main()` 中赋给全局 `RAW`；Gate 场景、阈值、产物逻辑零修改。 |
| **AC3** | 更新 `packaging/m2ac5/README.md` 当前验收命令，示范新建/隔离输出目录；用法说明不再声称 runner 会默认落入历史 raw 目录。历史 Handoff / verification 原始记录不改写 | **PASS**：README 第 4 节已更新示例为 `--output-dir "verification/M2-AC5/raw/run-isolated"` 并附防护说明；历史文档原样保留。 |
| **AC4** | 新增回归测试覆盖两个 runner 的“省略参数拒绝”和“显式参数解析”；测试在调用 runner 主体前停止，避免触发构建、安装或产品 Gate。确认 `verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/` 的 tracked 文件集合及内容未被测试改变 | **PASS**：新增 `tests/packaging/test_runner_output_dir_required.py` 9 项测试全绿；61 个历史 tracked raw 文件经 SHA256 与 git blob 比对证实 byte-identical。 |
| **AC5** | 实现差量严格限于本 Task allowed_paths；交付固定 commit、测试日志及 Handoff；非作者 DSH 独立审查通过后由 Codex 集成并完成集成验证 | **IN_REVIEW**：代码已固定于 `1c49fe38`，测试日志与 Handoff 齐全，等待非作者 DeepSeek Harness 独立审查。 |

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 Commit | 结果 | 日志/产物路径 |
|---|---|---|---|---|
| **AC1/AC2/AC4 回归测试** | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.14.6 @ `1c49fe38` | **PASS** (9 passed in 0.53s) | [`pytest-regression.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/pytest-regression.log) |
| **AC1/AC2/AC4 venv 回归测试** | `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.12.3 @ `1c49fe38` | **PASS** (9 passed in 0.58s) | [`pytest-regression-py312.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/pytest-regression-py312.log) |
| **AC4 历史 raw 完整性核查** | 比对 `verification/M2-RC2/raw` (25文件) 与 `verification/M2-AC5/raw` (36文件) 全部 61 个文件的 git blob 哈希及 working tree 状态 | Python / Git CLI @ `1c49fe38` | **PASS** (61 files byte-identical to HEAD) | [`raw-integrity.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/raw-integrity.log) |
| **快照护栏回归** | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Python 3.14.6 @ `1c49fe38` | **PASS** (16 actual-predicate cases PASS, EXIT=0) | [`check-snapshots.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/check-snapshots.log) |
| **AC5 范围核对** | `git diff --name-only d12ebc7a..1c49fe38` | Git CLI @ `1c49fe38` | **PASS** (仅 4 个 allowed_paths 文件) | [`git-diff-name-only.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-name-only.log) |
| **AC5 空白与格式检查** | `git diff --check d12ebc7a..1c49fe38` | Git CLI @ `1c49fe38` | **PASS** (EXIT=0，零空白错误) | [`git-diff-check.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-check.log) |
| **AC5 代码增减统计** | `git diff --stat d12ebc7a..1c49fe38` | Git CLI @ `1c49fe38` | **PASS** (+199 / -16) | [`git-diff-stat.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-stat.log) |

### 未运行项目说明（NOT_RUN）
- 完整 Dev Gate、Packaged Gate、Sidecar 构建、NSIS 安装：**NOT_RUN**。本任务只负责 CLI 参数保护与隔离输出路径解析（parser-only 边界防护），按任务规定不启动完整产品 Gate。测试通过在 `parse_args` 成功后拦截，确保不触发 runner 主体。

---

## 接收方式

1. **工作树与分支**：
   - 分支：`agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
   - 工作树：`G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
   - Git Common Dir：`G:/CODEX/New Manga/.git`
2. **审查对象**：
   - Review Base: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`（或 task base `e9b66455356c56e0fe6720d658b46bdbdbeb53b5`）
   - Code Delivery HEAD: `1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661` (`1c49fe38`)
3. **独立审查复核重点**：
   - 检查 `verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py` 中 `build_parser()` 的 `--output-dir` 是否为 `required=True` 且无默认值；
   - 检查 `main()` 是否在进行任何文件系统写入（`mkdir` / `tempfile.mkdtemp`）前先调用 `parse_args`；
   - 检查 `packaging/m2ac5/README.md` 的示例命令与说明是否已移除默认 raw 输出陈述；
   - 运行 `python -m pytest -q tests/packaging/test_runner_output_dir_required.py` 验证回归测试结果；
   - 确认 `src/**`、`apps/**`、其它 `tests/**` 零差量，历史 raw 文件未被修改。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` 独立代码审查
- **推荐 Agent / Reviewer**：DeepSeek Harness（非作者 Reviewer）
- **推荐原因与前置依赖**：Antigravity 已完成代码实现、回归测试、Task 更新与证据入库，代码提交为 `1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661`。按协作协议须由非作者 Reviewer 进行独立审核。
- **Recovery point**：
  - 仓库路径：`G:/CODEX/New Manga`
  - 分支：`agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
  - 工作树：`G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
  - Base commit: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
  - Reviewed Head: `1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661`
- **允许修改路径**：
  - `doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38-dsh-r1.md`
  - Reviewer 自有 verification 证据路径
- **禁止范围与新增授权条件**：不得修改生产代码或测试代码；不合并主线。
- **交付物**：DSH 独立审查报告与 decision（`approved` / `changes_requested`）。
- **验证命令、环境与完成 Gate**：
  - `git diff --check d12ebc7a..1c49fe38` (EXIT 0)
  - `git diff --name-only d12ebc7a..1c49fe38` (仅 4 个允许文件)
  - `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` (9 passed)
- **可直接转发给 Agent 的指令**：
  ```text
  请作为非作者 Reviewer (DeepSeek Harness) 对 Task M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD 进行独立代码审查。
  - 工作树：G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity
  - 分支：agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
  - Review Base：d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10
  - Reviewed Head：1c49fe38dd0fc67b9c8abc39bfd6b57386ac0661
  - Handoff：doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38.md
  - 范围：核查两个 runner 的 --output-dir 必选参数约束、README 说明及回归测试，确认 src/apps/tests/raw 零超界差量。
  - 产出：doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38-dsh-r1.md
  ```

---

## 风险与遗留

1. **显式传入历史路径无法被参数解析阻断**：
   本任务将 `--output-dir` 改为必选，消除了操作者无意缺省调用时破坏历史 raw 证据的风险。若调用者在命令行显式传入 `--output-dir verification/M2-RC2/raw`，参数解析器仍会接受。此取舍已在 Task §依赖、风险与阻塞中明确冻结：“required 参数不能阻止操作者显式选中历史路径，因此本 Task 仅消除危险的隐式默认，不新增路径策略或清理行为”。
2. **产品 Gate 状态不变**：
   本回归测试仅针对 CLI 参数校验与隔离解析逻辑（parser-only），不构成完整产品 Gate PASS 的替代证据。
