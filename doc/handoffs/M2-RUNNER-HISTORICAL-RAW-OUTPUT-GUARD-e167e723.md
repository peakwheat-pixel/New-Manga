---
task_id: M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
author: Antigravity
recipient: DeepSeek Harness
base_commit: e9b66455356c56e0fe6720d658b46bdbdbeb53b5
start_head: d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10
delivery_head: e167e72351d6f725653d1f16b210a54f435e621f
status: in_review
---

# Handoff：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD（r1 修订交付）

## 交付结果

### 1. 目标与实现范围

本任务闭合 DeepSeek Harness r4 独立审查中指出的非阻断遗留问题 `R-001`（见 [`doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md) §Findings）：
`verification/M2-RC2/run_e2e.py` 与 `packaging/m2ac5/run_clean_start_e2e.py` 两处 runner 的 `--output-dir` 参数此前为可选且默认指向已跟踪的历史 raw 证据目录（`verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/`），后续缺省调用可能意外覆盖历史证据。

在收到 DeepSeek Harness r1 审查报告（`doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38-dsh-r1.md`，`decision=changes_requested`）后，本次 r1 修订完成必修项 R-01 至 R-04，并按需处理可选项；R-06 的模块加载复杂度明确 deferred，R-07 由 Codex 更新治理元数据：

1. **[`packaging/m2ac5/README.md`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/packaging/m2ac5/README.md) (R-01)**：
   - 将第 4 节验收 runner 示例命令从原先处于历史 raw 树内的路径修改为两根历史 raw 目录之外的独立临时路径：`--output-dir "$env:TEMP/m2ac5-cleanstart-artifacts"`；
   - 强化必选参数说明，明确指出省略参数将导致 usage error / exit 2，且输出路径必须指定在历史 raw 树之外。
2. **[`tests/packaging/test_runner_output_dir_required.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/tests/packaging/test_runner_output_dir_required.py) (R-04, R-05, R-06)**：
   - **R-04**：移除了测试内部对外部 git 仓库状态的断言（删除了 `test_tracked_raw_evidence_directories_unmodified` 及无用的 `RC2_RAW`/`AC5_RAW` 常量），使单元测试保持纯粹聚焦于 parser 行为的 hermetic 测试；
   - **R-05**：将 AC5 main 拦截点从 `tempfile.mkdtemp` 提前至 `Path.mkdir`，实现零目录创建副作用拦截；
   - **R-06**：将子进程参数缺失报错断言简化为 `assert "required" in err`，消除冗余分支；整体加载 runner/conftest 的复杂度按可选建议 deferred，不在本 Task 扩大改动；
   - 测试用例调整为 8 项，全部快速通过（Python 3.14: 0.51s, Python 3.12: 0.55s）。
3. **[`packaging/m2ac5/run_clean_start_e2e.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/packaging/m2ac5/run_clean_start_e2e.py)** 与 **[`verification/M2-RC2/run_e2e.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/verification/M2-RC2/run_e2e.py)**：
   - 维持既有实现，`build_parser()` 将 `--output-dir` 设为 `required=True`，无默认值；
   - `main()` 在任何目录创建或 runner 动作前完成 `parse_args` 校验。
4. **可复现历史 raw 完整性脚本与快照比对 (R-03)**：
   - 入库 [`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py)；
   - 在 pytest 运行前后记录快照并自动比对 61 个历史文件的 SHA-256 及 git blob hash，确认 byte-identical，记录符合纪律的日志并明确标注非 Gate 声明。
5. **新建 Handoff 与统计精确性 (R-02)**：
   - 旧 Handoff `doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38.md` 原样只读保留；
   - 新建本次 delivery HEAD 对应的 Handoff，文件增减统计严格以 `git diff --stat` 和 `git diff --numstat` 为准。
6. **治理与元数据规则 (R-07)**：
   - Owner 未修改全局治理文档；Codex 已在主线治理提交 `8ad092d2` 更新 Plan、STATUS、Task 索引和 Task 状态。

---

### 2. DSH r1 审查意见处置汇总（Review Disposition）

| 审查项 | 级别 | 处置状态 | 处置说明与证据 |
|---|---|---|---|
| **R-01** | P1 | **RESOLVED** | `packaging/m2ac5/README.md` 第 4 节示例更新为 `--output-dir "$env:TEMP/m2ac5-cleanstart-artifacts"`，位于历史 raw 树之外，保留必选说明。 |
| **R-02** | P2 | **RESOLVED** | 保留旧 Handoff `1c49fe38` 不变；新建 `e167e723` Handoff，文件增减统计严格以 `git diff --stat` 与 `git diff --numstat` 实际输出填报。 |
| **R-03** | P2 | **RESOLVED** | 编写入库可复现脚本 `verify_raw_integrity.py`，完成运行前后 61 个文件的 SHA256 与 git blob 快照对比，日志记录规范，明确非 Gate PASS。 |
| **R-04** | P2 | **RESOLVED** | 从 `tests/packaging/test_runner_output_dir_required.py` 移除对 git subprocess / status 的全局 VCS 状态断言，测试保持 hermetic。 |
| **R-05** | P3 | **RESOLVED** | 在 `test_ac5_main_interception_after_parse_args` 中将拦截点提前至 `Path.mkdir`，实现零目录创建拦截。 |
| **R-06** | P3 | **PARTIALLY_RESOLVED / PARTIALLY_DEFERRED** | 冗余断言分支已删除；整体加载 runner/conftest 的复杂度按可选建议 deferred，未声称完全关闭。 |
| **R-07** | P3 | **RESOLVED_BY_CODEX** | Owner 遵守边界；Codex 已在主线治理提交 `8ad092d2` 同步 Plan、STATUS、Task 索引和 Task 状态。 |

---

### 3. 代码提交与精确差量

- **Code Delivery HEAD**：[`e167e72351d6f725653d1f16b210a54f435e621f`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity) (`e167e723`)
  - 提交信息：`fix(packaging): update isolated output-dir example and hermetic parser tests (M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD)`
- **基线 Commit**：[`d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`](file:///G:/CODEX/New%20Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity) (`d12ebc7a`)
- **纯代码文件统计（相比基线 d12ebc7a）**：
  - `packaging/m2ac5/README.md`: 3 insertions(+), 2 deletions(-)
  - `packaging/m2ac5/run_clean_start_e2e.py`: 12 insertions(+), 7 deletions(-)
  - `tests/packaging/test_runner_output_dir_required.py`: 153 insertions(+), 0 deletions(-)
  - `verification/M2-RC2/run_e2e.py`: 11 insertions(+), 7 deletions(-)
  - **纯代码合计**：4 个文件，179 insertions(+), 16 deletions(-)（`git diff --numstat` 严格对齐）
- **r1 代码修订差量（相比 1c49fe38）**：
  - `git diff --stat 1c49fe38..e167e723`：
    - `packaging/m2ac5/README.md`: 3 insertions(+), 3 deletions(-)
    - `tests/packaging/test_runner_output_dir_required.py`: 4 insertions(+), 24 deletions(-)
    - 2 个文件，7 insertions(+), 27 deletions(-)
- **禁止范围核对**：`src/**`、`apps/**`、其它 `tests/**`、Schema、依赖 0 差量；历史 raw 证据 0 差量。

---

### 4. Acceptance Criteria 对照

| AC 项 | 目标要求 | 达成事实与状态 |
|---|---|---|
| **AC1** | 两个 runner 的 CLI 都要求显式 `--output-dir`；省略时以 argparse usage error / exit 2 失败，且失败发生在任何文件系统副作用及 Gate 启动之前 | **PASS**：两 runner 均配置 `parser.add_argument("--output-dir", type=Path, required=True)`；测试证实 subprocess 与 parse_args 均在副作用前 exit 2 失败。 |
| **AC2** | 传入显式 `--output-dir <isolated-path>` 时 argparse 接受参数，并继续将该路径作为本次运行输出根；不改变 Gate 场景、阈值、产物结构或其他 runner 行为 | **PASS**：解析器正常接收 `output_dir` 并在 `main()` 中赋给全局 `RAW`；Gate 场景、阈值、产物逻辑零修改。 |
| **AC3** | 更新 `packaging/m2ac5/README.md` 当前验收命令，示范新建/隔离输出目录；用法说明不再声称 runner 会默认落入历史 raw 目录。历史 Handoff / verification 原始记录不改写 | **PASS**：README 第 4 节已更新示例为 `--output-dir "$env:TEMP/m2ac5-cleanstart-artifacts"`，明确指定在历史 raw 树之外，并附防护说明；历史文档原样保留。 |
| **AC4** | 新增回归测试覆盖两个 runner 的“省略参数拒绝”和“显式参数解析”；测试在调用 runner 主体前停止，避免触发构建、安装或产品 Gate。确认 `verification/M2-RC2/raw/` 与 `verification/M2-AC5/raw/` 的 tracked 文件集合及内容未被测试改变 | **PASS**：新增 `tests/packaging/test_runner_output_dir_required.py` 8 项测试全绿，测试为 hermetic；61 个历史 tracked raw 文件经入库脚本 `verify_raw_integrity.py` 证实前后快照完全一致，byte-identical；raw 两目录无 tracked 修改或 untracked 文件。 |
| **AC5** | 实现差量严格限于本 Task allowed_paths；交付固定 commit、测试日志及 Handoff；非作者 DSH 独立审查通过后由 Codex 集成并完成集成验证 | **IN_REVIEW**：代码已固定于 `e167e723`，测试日志、前后快照比对与 Handoff 齐全，等待非作者 DeepSeek Harness 独立复审。 |

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 Commit | 结果 | 日志/产物路径 |
|---|---|---|---|---|
| **AC1/AC2/AC4 回归测试** | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.14.6 @ `e167e723` | **PASS** (8 passed in 0.51s) | [`pytest-regression.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/pytest-regression.log) |
| **AC1/AC2/AC4 venv 回归测试** | `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest -v tests/packaging/test_runner_output_dir_required.py` | Python 3.12.3 @ `e167e723` | **PASS** (8 passed in 0.55s) | [`pytest-regression-py312.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/pytest-regression-py312.log) |
| **AC4 历史 raw 完整性前后比对 (R-03)** | `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py --compare-after ...` | Python 3.14.6 @ `e167e723` | **PASS** (61/61 files byte-identical before and after; Git status clean for the two historical raw paths) | [`raw-integrity.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/raw-integrity.log) |
| **快照护栏回归** | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Python 3.14.6 @ `e167e723` | **PASS** (16 actual-predicate cases PASS, EXIT=0) | [`check-snapshots.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/check-snapshots.log) |
| **AC5 范围核对** | `git diff --name-only d12ebc7a..e167e723` | Git CLI @ `e167e723` | **PASS** (仅 4 个 allowed_paths 代码文件 + 既有证据/任务文件) | [`git-diff-name-only.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-name-only.log) |
| **AC5 空白与格式检查** | `git diff --check d12ebc7a..e167e723` | Git CLI @ `e167e723` | **PASS** (EXIT=0，零空白错误) | [`git-diff-check.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-check.log) |
| **AC5 代码增减统计** | `git diff --stat d12ebc7a..e167e723` | Git CLI @ `e167e723` | **PASS** (纯代码 4 文件 +179 / -16) | [`git-diff-stat.log`](../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/git-diff-stat.log) |

**派发状态说明**：本轮 `agy` 进程 EXIT=0，但输出 JSON 的 `status` 字段为 `ERROR`。Codex 不把该字段当作成功依据；上述提交、测试、raw 快照和 Git 范围已在实际 Owner worktree 独立核验。DSH r2 仍是必需 Gate。

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
   - Code Delivery HEAD: `e167e72351d6f725653d1f16b210a54f435e621f` (`e167e723`)
3. **独立审查复核重点**：
   - 检查 `packaging/m2ac5/README.md` 的示例命令是否已指向 `$env:TEMP` 且位于历史 raw 树两根之外；
   - 检查 `tests/packaging/test_runner_output_dir_required.py` 是否已移除 git status/subprocess 的外部断言，且 `test_ac5_main_interception_after_parse_args` 是否在 `Path.mkdir` 前拦截；
   - 运行 `python -m pytest -q tests/packaging/test_runner_output_dir_required.py` 验证 8 项测试全绿；
   - 运行 `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py` 确认 61 个历史 raw 文件完整性与干净状态。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` r2 独立代码审查
- **推荐 Agent / Reviewer**：DeepSeek Harness（非作者 Reviewer）
- **推荐原因与前置依赖**：Antigravity 已完成 r1 修订代码实现、hermetic 回归测试、README 路径修正、raw 完整性复现脚本入库与证据记录，代码提交为 `e167e72351d6f725653d1f16b210a54f435e621f`。按协作协议由非作者 Reviewer 进行 r2 独立审核。
- **Recovery point**：
  - 仓库路径：`G:/CODEX/New Manga`
  - 分支：`agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
  - 工作树：`G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
  - Base commit: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
  - Code Delivery Head: `e167e72351d6f725653d1f16b210a54f435e621f`；DSH r2 应审查 Codex 派发时实测并固定的 Owner branch HEAD（包含本 Handoff 与验证证据提交）。
- **允许修改路径**：
  - `doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-e167e723-dsh-r2.md`
  - Reviewer 自有 verification 证据路径
- **禁止范围与新增授权条件**：不得修改生产代码或测试代码；不合并主线。
- **交付物**：DSH 独立审查报告与 decision（`approved` / `changes_requested`）。
- **验证命令、环境与完成 Gate**：
  - `git diff --check d12ebc7a..e167e723` (EXIT 0)
  - `git diff --name-only d12ebc7a..e167e723` (零超界)
  - `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` (8 passed)
  - `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py` (PASS, 61 files byte-identical)
- **可直接转发给 Agent 的指令**：
  ```text
  请作为非作者 Reviewer (DeepSeek Harness) 对 Task M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD 的 r1 修订进行 r2 独立代码审查。
  - 工作树：G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity
  - 分支：agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
  - Review Base：d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10
  - Code Delivery Head：e167e72351d6f725653d1f16b210a54f435e621f；Reviewed Head 以 Codex 派发时实测固定值为准，覆盖最新 Task/Handoff/evidence。
  - Handoff：doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-e167e723.md
  - 范围：逐项核查 R-01..R-07 的修复与 disposition，确认 R-06 的剩余模块加载复杂度已明确 deferred；检查 README 示例路径、hermetic 测试、raw-integrity 前后快照与 Path.mkdir 拦截点。
  - 产出：doc/reviews/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-e167e723-dsh-r2.md
  ```

---

## 风险与遗留

1. **显式传入历史路径无法被参数解析阻断**：
   本任务将 `--output-dir` 改为必选，消除了操作者无意缺省调用时破坏历史 raw 证据的风险。若调用者在命令行显式传入 `--output-dir verification/M2-RC2/raw`，参数解析器仍会接受。此取舍已在 Task §依赖、风险与阻塞中明确冻结：“required 参数不能阻止操作者显式选中历史路径，因此本 Task 仅消除危险的隐式默认，不新增路径策略或清理行为”。
2. **产品 Gate 状态不变**：
   本回归测试仅针对 CLI 参数校验与隔离解析逻辑（parser-only），不构成完整产品 Gate PASS 的替代证据。
