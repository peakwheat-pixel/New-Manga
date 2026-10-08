---
task_id: M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD
reviewer: DeepSeek Harness
author: Antigravity
integrator: Codex
review_base: d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10
reviewed_head: 8b867e0208246e2e478a2906a2198c60c7d88aa6
code_delivery_head: e167e72351d6f725653d1f16b210a54f435e621f
decision: approved
---

# Review r2：M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD（r1 修订复审）

## 0. 本轮执行环境（口径声明，必读）

本会话 `pwsh` 在**沙箱准备阶段**即失败，命令体从未执行，逐次返回：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2)
```

默认模式、`workdir=C:\Windows\Temp`、无 workdir 三种调用结果相同；`danger-full-access` 一次性重试被拒（`requires approval, but no approval channel is available`）；独立子代理复测 4 条 git 命令 + 2 条对照探测亦为同一错误（属环境/权限层故障，与 `workdir` 无关）。该故障与 DSH r1 报告 §0 记录的完全一致。

**因此本轮没有任何 `git` / `python` / `pytest` 命令由本人执行**，全部记 `NOT_RUN`（清单见 §5）。Owner（Antigravity）与 Codex 已运行的测试、日志、diff 记录在本报告中一律标注为 **Owner 侧记录**，仅用于交叉比对，不写成本人亲验的 PASS。

Reviewer 自有静态核对证据：[`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/review-dsh-r2/dsh-r2-static-checks.md`](../../verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/review-dsh-r2/dsh-r2-static-checks.md)。

### 0.1 固定锚点实测（前置校验）

| 项 | 实测值 | 确认方式 |
|---|---|---|
| branch | `refs/heads/review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 读 `.git/worktrees/…-dsh-r2/HEAD` |
| HEAD | `8b867e0208246e2e478a2906a2198c60c7d88aa6` = **reviewed_head** ✔ | 读 `.git/refs/heads/review/deepseek/…-r2` + worktree reflog |
| common-dir | `G:/CODEX/New Manga/.git` ✔ | worktree `.git` 文件 |
| Owner 分支 | `agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` = `8b867e02`（与 reviewed_head 同一 commit）✔ | 读 refs |
| `git status --porcelain` | **NOT_RUN**（无 shell）。替代观察：worktree 内仅有 **DSH 派发器为本会话写入**的 `verification/…/review-dsh-r2-cli-output.md`、`review-dsh-r2-cli-stderr.log`（内容为本会话自身 reasoning/stderr），非 Owner 内容；两历史 raw 目录文件集合 25+36=61 与 tracked 计数吻合 | glob/read |

`review_base`/`reviewed_head`/`code_delivery_head` 三者与派发指令**逐一匹配**，故不触发「不匹配或 dirty → 停止」的阻塞分支；但「worktree 整体干净」本会话无法证明（见上表末行）。

## 1. 范围与依据

### 1.1 Owner 分支拓扑（reflog 直接证据）

读 `.git/worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/logs/HEAD`：

```text
d12ebc7a → 1c49fe38 (fix: require explicit output-dir)            ← r1 code delivery
         → 76e32b38 → 0ea16b83 (amend)(docs: … verification and handoff)  ← DSH r1 reviewed_head
         → e167e723 (fix: update isolated output-dir example and hermetic parser tests)  ← code_delivery_head
         → 3801aa96 (docs(packaging): record … r1 revision verification and handoff)
         → 8b867e02 (docs: clarify runner guard r1 evidence disposition)                  ← reviewed_head
```

结论：`reviewed_head` = Owner 分支 HEAD；`code_delivery_head e167e723` 是其祖先（相隔 2 个纯文档 commit）；`e167e723` 的父提交正是 DSH r1 审查的 `0ea16b83`。这解释了 Owner 日志中 `git diff …d12ebc7a...e167e723` 的 14 文件集合（含 r1 周期的 Handoff/Task/证据）。

### 1.2 审查覆盖

- 两 runner 的 parser/`main` 语义与 base 差量（静态）；
- `packaging/m2ac5/README.md` 示例与说明；新增回归测试全文；
- `verify_raw_integrity.py`、`raw-integrity.log`、`raw-snapshot-before.json` 与其余 6 份日志；
- Task / 新旧 Handoff / `VERIFICATION.md` / `doc/STATUS.md`（分支版与主线版）的相互对照；
- 依赖 Task 的冻结 oracle `verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` 兼容性；
- 是否存在**仍在调用**两 runner 的活脚本（避免 required 参数打断别处流程）。

### 1.3 未审到 / 无法审的部分

- 一切需 `git`/`pytest`/runner 执行的结论（§5 全为 NOT_RUN）；
- `d12ebc7a` 的**完整**文件集合与 base 全文件等值：仍用 base proxy（`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/{run_e2e.py,run_clean_start_e2e.py}`）+ 行号锚点法（§3.2），非 git 证明；
- r1 引用的 `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/release.md` 与 `ANTIGRAVITY_INSTRUCTION.md`：在主线 checkout、Owner worktree、r1/r2 worktree 中**均已不存在**，且未被任何 Owner 日志列出（属未入库的本地派发文件）。故本轮 AC3 判据改用冻结 Task 文本（Task:30）而非该治理文件。

## 2. r1 findings 逐项复核

| ID | r1 级别 | 复核结论 | 关键证据 |
|---|---|---|---|
| R-01 | P1 | **RESOLVED** | `README.md:145-146` 示例现为 `--output-dir "$env:TEMP/m2ac5-cleanstart-artifacts"`，位于 `verification/M2-RC2/raw`、`verification/M2-AC5/raw` **两根之外**；`:152` 明确「runner 不再提供默认输出路径…输出目录须指定于历史 raw 树之外」。全 README 无 `$env:TEMP=` 重定向，无把输出指回仓库内路径的语句 |
| R-02 | P2 | **RESOLVED（含一处 P3 残余，见 R-09）** | 旧的 per-file 累加不自洽（215≠199）已消除：Handoff 现 write README 3+/2−、`run_clean_start_e2e.py` 12+/7−、test 153+/0−、`run_e2e.py` 11+/7− = **179+/16−**，与 Owner `git-diff-stat.log` 的条形值 5+19+153+18=195=179+16 **精确自洽**；我另以行数独立复算：655−651=4=11−7、889−884=5=12−7、153=173−24+4（§3.2），**三处全部命中**。旧 Handoff 未被修改（见 R-02 证据行下） |
| R-03 | P2 | **RESOLVED** | 脚本已入库 `verify_raw_integrity.py`；`raw-integrity.log` 现带头部（`:1` HOST/SHELL/PYTHON/VER/**HEAD**）、`COMMAND`（`:2`）、`EXIT=0`（`:9`）；`raw-snapshot-before.json` 已入库且 `"sha256"` 计数 = 61，与 log 的 61 独立吻合；比对口径 = tracked 集合（`git ls-files -s`）+ 逐文件 SHA256 + index/worktree blob |
| R-04 | P2 | **RESOLVED** | `tests/packaging/test_runner_output_dir_required.py` 已无 `git`/`subprocess-git`/`RC2_RAW`/`AC5_RAW` 及 `test_tracked_raw_evidence_directories_unmodified`（r1 版在 `:160-173`）；现存 `subprocess` 仅用于运行 runner CLI 本身。VCS 完整性核查移入 Task 的 verification 步骤（`verify_raw_integrity.py`），与 r1 建议一致 |
| R-05 | P3 | **RESOLVED** | `tests/…:137-153` 的 AC5 用例改为 `monkeypatch.setattr(Path, "mkdir", stop_before_work)`；runner `packaging/m2ac5/run_clean_start_e2e.py:744 parse_args → :745 RAW=resolve → :747 RAW.mkdir → :748 mkdtemp`，故拦截发生在**首个建目录调用之前**，实现零目录创建 |
| R-06 | P3 | **部分闭合 + 明确 deferred（判定：可接受，非误报全关）** | 冗余断言已删（r1 `:73` `or "the following arguments are required"` → 现 `:69` `assert "required" in err`）；`load_module_from_path`（`:24-43`）连同 `sys.modules["conftest"]` 注入与整体 `exec_module` 复杂度**仍然保留**。Handoff:53 如实写 `PARTIALLY_RESOLVED / PARTIALLY_DEFERRED`，`:28` 说明「按可选建议 deferred，不在本 Task 扩大改动」；`VERIFICATION.md:14` 同口径。**未发现把该 deferred 谎报为全关的表述**，且该复杂度不构成正确性风险 → 接受 |
| R-07 | P3 | **RESOLVED_BY_CODEX（核实）** | 主线 reflog：`248271a5 → 8ad092d2 "docs: record runner guard review changes requested" → dc2b1bd3 "docs: record runner guard revision ready for review"`（现 `main=dc2b1bd3`）；主线 `doc/STATUS.md:3-5` 已写 `in_review / CHECKPOINTED`、code head `e167e723`、Owner Task/Handoff/evidence head `8b867e02`、DSH r2 worktree 与 R-01..R-07 处置。反证 Owner 未越界：**本 head 的 `doc/STATUS.md:3-5` 仍是旧文**（`ready`/`IDLE`/「本次释放还未派发」），说明 Owner 分支未改治理文件，与 Handoff:40 声明一致 |

**R-02 补充：旧 Handoff 未被修改的证据（静态）**
- `doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-1c49fe38.md` 在 Owner 日志中始终以「新增文件」形态出现（r1 日志 `git-diff-stat.log:4` 138 insertions，无 deletions），r2 的 `git-diff-name-only.log:4` 仍只列该路径一次且未出现在任何删除面；
- 本 head 未出现「旧 Handoff 被改写」的任一痕迹（无 `-` 行归属该文件；其内容与 r1 报告 §4.2 引用的文本一致）。

## 3. 代码语义复核（派发指令逐条）

### 3.1 结论表

| # | 指令核查项 | 结论 | 证据 |
|---|---|---|---|
| C-1 | 两个 runner 都只有一个 argparse parser | **PASS** | `grep ArgumentParser(`：`verification/M2-RC2/run_e2e.py:497`、`packaging/m2ac5/run_clean_start_e2e.py:735` 各 1 处 |
| C-2 | `--output-dir` `required=True` | **PASS** | `run_e2e.py:501`、`run_clean_start_e2e.py:737`；两文件无 `default=RAW` |
| C-3 | 缺省时 `parse_args` 在任何输出目录副作用/Gate 之前失败 | **PASS（静态）** | RC2 `:508 parse_args → :509 RAW=resolve → :510 mkdtemp → :511 RAW.mkdir`；AC5 `:744 → :745 → :747 mkdir → :748 mkdtemp`。argparse 在 `usage error` 后 `SystemExit(2)`；两文件模块级唯一顶层语句为 `sys.path.insert`（`run_e2e.py:53`）与常量定义，无 `mkdir/open/write_text` |
| C-4 | 显式路径继续到同一输出根 | **PASS** | `RAW = args.output_dir.resolve()` 是 `main()` 内对 `RAW` 的唯一赋值；所有写盘点（如 RC2 `:538`、AC5 `:717`）继续相对 `RAW` |
| C-5 | 其他 Gate 行为无差异 | **PASS（静态，proxy 口径）** | r1→r2：两 runner 文本与行数零差异（`655`/`889` 行、`:496-515`/`:734-750` 逐行相同）——即**本轮修订未触 Gate 逻辑**；base→head：行号锚点法显示净插入全部落在 `build_parser()/main()` 区（RC2 区前恒 −1、区后恒 +4；AC5 区前恒 0、区后恒 +5），且净差与 numstat 精确相等（§3.2）。参数集与顺序不变（`--exe/--skip-build/--output-dir`；`--installer/--output-dir`），仅 `default=RAW → required=True` |
| C-6 | 范围内无 src/apps/Schema/依赖改动 | **PASS（受限）** | Owner `git-diff-name-only.log`（14 路径）无 `src/**`、`apps/**`、Schema、依赖文件；`check_snapshots.py`（依赖 Task oracle，108 行）在 r1/r2 worktree 锚点行号一致，未被本 Task 修改；其断言不依赖 `--output-dir` 默认值，故 Oracle 兼容。**完整 `d12ebc7a...8b867e02` 名称集合为 NOT_RUN**（无 git） |
| C-7 | 历史 raw 未被修改 | **PASS（受限）** | 两 raw 目录文件集合 25+36=61 = tracked 计数 = 快照条目数；r1 worktree 与 r2 worktree 的 `M2-AC5/raw` 文件名集合一致（36）。**逐文件字节等值复算为 NOT_RUN** |
| C-8 | 无其他地方以缺省方式调用这两个 runner（免打断） | **PASS（静态）** | 全仓 `.py`/`.ps1` 检索：唯一不带 `--output-dir` 的调用是**历史冻结**脚本 `verification/M2-RC2/integration-88f972fe/verify.ps1:14`（旧任务集成证据，见 §6 残余风险 3）；`check_snapshots.py`/`bind_review.py` 只按路径做 AST/哈希引用，不执行 |

### 3.2 base 差量的行号锚点法（本人自建，proxy）

| 锚点 | ICU proxy | head | 偏移 |
|---|---|---|---|
| `run_e2e.py` `SIDECAR_ALLOWED_PROJECT_MODULES` / `def log` / `def check_sidecar_dump` / `if __name__` / 总行数 | 59 / 80 / 485 / 650 / 651 | 58 / 79 / 484 / 654 / 655 | −1 / −1 / −1 / **+4** / +4 |
| `run_clean_start_e2e.py` `class Gate` / `def log` / `def purged_environment` / `if __name__` / 总行数 | 98 / 119 / 130 / 883 / 884 | 98 / 119 / 130 / 888 / 889 | 0 / 0 / 0 / **+5** / +5 |

净差 +4 与 +5 分别等于 Handoff 声明的 `11+/7−` 与 `12+/7−`（净 +4、+5）；结合 C-1/C-2/C-5 的参数面比对，可判定变更集中在 `build_parser()/main()` 与 docstring，**无 Gate 场景、阈值、产物结构改动**。口径声明：这是对 base proxy 的静态推断，**不是** `git diff` 结论。

## 4. Findings

| ID | 级别 | 文件/行 | 触发条件 | 影响 | 证据 | 修复建议 | disposition |
|---|---|---|---|---|---|---|---|
| R-08 | P3 | `doc/tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md:57` | 读者据 Task 测试表核验 AC4 | Task 自述 `PASS (9/9 passed)`，但同 commit 测试文件只有 **8** 个用例、被引用的 `pytest-regression.log:9-20` 为 `collected 8 items` / `8 passed`；`Handoff:94-95`、`VERIFICATION.md:40-41`、Task:73-74 均为 8 | Task:57 vs `pytest-regression.log:9,20` vs `tests/…py`（7 个 `def test_` 经参数化产生 8 个实例） | 改为 `PASS (8/8 passed)`；顺手把该行命令与实测命令（`-v`）对齐 | **open（非阻断）** |
| R-09 | P3 | `doc/handoffs/…-e167e723.md:70-73`；`doc/tasks/…md:78` | 有人按 Handoff/Task 写明的命令复核 | 标注的 `git diff --stat 1c49fe38..e167e723` **不可能**输出「2 个文件」：由 reflog 可证 `0ea16b83`（r1 文档提交）是 `1c49fe38` 与 `e167e723` 之间的提交，且 r1 Handoff/Task/8 份证据在 `1c49fe38` 时不存在（r1 日志 `git-diff-name-only.log` = 4 个代码文件），故该 diff 必含 ~11 个文件（r1 Handoff +138 等）。2 文件的 7+/27− 实为「本次修订所编辑的两个文件」的差值（等价于 `--diff-filter=M` 或显式 pathspec）。Task:78 同类：`git diff --name-only d12ebc7a..e167e723` 的实输出为 14 条路径，而文中写「4 个 allowed_paths 代码文件」 | 变更规模/范围结论无法**照抄命令**复现（数字本身正确、范围结论亦正确） | `git-diff-name-only.log` / `git-diff-stat.log`（14 files, 485/28）；r1 版 `git-diff-name-only.log`（4 文件）；antigravity reflog | 命令补 `--diff-filter=M`（或写明 pathspec），或改为「本次修订实际编辑 2 个文件：…」 | **open（非阻断）** |
| R-10 | P3 | `raw-integrity.log:7`；`verify_raw_integrity.py:115`、`:107` | 读者/后续脚本解释 RESULT 行与统计数字 | ①`:7`「…61 tracked historical raw files byte-identical…; **zero modifications or untracked files**」的后半句未复述作用域，可被读成「整个 worktree 零 untracked」——而 worktree 整体**并不干净**（本会话即有 DSH 派发器写入的 2 个未跟踪文件）。②`:107` `byte-identical = len(∩) − len(errors)` 把「文件集合不匹配」「git status 脏」等**非 byte 差异**错误地计入被减数，失败运行时会打印误导性（甚至负数）数字 | 证据措辞/统计口径不精确（结论本身正确：`:6` 已单列 `Historical raw paths clean: True`，脚本 `RAW_DIRS` 亦只含两根） | 脚本 `:21` `RAW_DIRS`、`:59-63` 作用域、`:105-115` 输出逻辑 | ① RESULT 行补「(scoped to the two historical raw paths)」；② 把计数器改为只统计 sha256 差异（如 `matched = sum(1 for k in ∩ if before[k]["sha256"] == after[k]["sha256"])`） | **open（非阻断）** |
| R-11 | P3（可选加固） | `packaging/m2ac5/README.md:145-146` | 操作者连续照抄示例两次 | 示例路径 `$env:TEMP/m2ac5-cleanstart-artifacts` 固定不唯一：第二次运行会覆盖上一次的产物，与同段「**全新**隔离输出目录」的措辞略有张力（**历史 raw 安全性不受影响**，AC3 目标已达成） | README:145 vs :146、:152 | 追加 run-id/时间戳后缀，如 `"$env:TEMP/m2ac5-cleanstart-artifacts-$(Get-Date -Format yyyyMMdd-HHmmss)"` | **open（建议项）** |

**说明**：本轮**未发现 P0/P1/P2**。R-08/R-09 属文档精度，R-10/R-11 属证据措辞与可选加固，均不改变代码语义、不削弱安全门、不构成放行阻断。

## 5. 验证

| # | 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|---|
| V-1 | 两 runner `--output-dir` 必选、唯一 parser、无默认残留 | read + grep `ArgumentParser(` / `add_argument(` / `default=` | reviewed_head 工作树 | **PASS（静态）** | §3.1 C-1/C-2 |
| V-2 | `parse_args` 先于任何输出目录副作用 | 全文 `main()` + 模块级语句 grep | 同上 | **PASS（静态）** | §3.1 C-3；`run_e2e.py:53`、`:505-511`；`run_clean_start_e2e.py:741-748` |
| V-3 | base→head 仅 parser/docstring 变更 | ICU proxy 行号锚点法 + 净差与 numstat 对齐 | base proxy vs `8b867e02` | **PASS（静态，proxy）** | §3.2；全文件等值 **NOT_RUN** |
| V-4 | README 示例在两根历史 raw 之外 | read `README.md:142-153`；read `.gitignore` | 同上 | **PASS（静态）** | `$env:TEMP/…`；两 raw 根分别由 `run_e2e.py:49`、`run_clean_start_e2e.py:53` 定义 |
| V-5 | 新测试在 runner 主体前停止、无 VCS 依赖 | read 测试全文（153 行） | 同上 | **PASS（静态）**；R-05 已加固 | 无 `git`；AC5 拦截 `Path.mkdir`；RC2 拦截 `tempfile.mkdtemp` |
| V-6 | 依赖 Task 冻结 oracle 兼容 | read `verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`（108 行） | 同上 | **PASS（静态）** | 只 AST 抽取常量/函数 + `compile()` 语法；不读取 parser 默认值 |
| V-7 | 历史 raw 文件集合未变 | glob 两 raw 目录 + 快照条目计数 | 同上 | **PASS（静态，集合级）**；字节等值 **NOT_RUN** | 25+36=61；`raw-snapshot-before.json` 61 条 |
| V-8 | 8 项回归（pytest，3.14 / 3.12） | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` | `e167e723`（**Owner 侧**） | **NOT_RUN（本人未执行）**；Owner 侧记录 8 passed / EXIT=0 | `pytest-regression.log:9-21`、`pytest-regression-py312.log:8-20` |
| V-9 | 61 文件 SHA256/blob 前后一致 | `python verification/…/verify_raw_integrity.py --compare-after …` | `e167e723`（**Owner 侧**） | **NOT_RUN**；Owner 侧记录 PASS / EXIT=0；脚本与快照已入库可复跑 | `raw-integrity.log:1-9`、`verify_raw_integrity.py`、`raw-snapshot-before.json` |
| V-10 | 快照护栏回归 | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | `e167e723`（**Owner 侧**） | **NOT_RUN**；Owner 侧记录 16 cases PASS / EXIT=0 | `check-snapshots.log:27-28` |
| V-11 | diff 范围 / 空白 / 统计 | `git diff --name-only\|--check\|--stat d12ebc7a...e167e723` | Git CLI（**Owner 侧**） | **NOT_RUN**；Owner 侧记录 14 文件、EXIT=0、485/28（口径见 R-09） | `git-diff-{name-only,check,stat}.log` |
| V-12 | commit 拓扑与锚点 | 读 worktree reflogs + refs + 主线 reflog/STATUS | — | **PASS（文件级）** | §0.1、§1.1、§2 R-07 |
| V-13 | `git status --porcelain`（worktree 干净度） | — | — | **NOT_RUN**（无 shell）；仅可确认两个 raw 目录文件集合为 25+36 | §0.1 末行 |
| V-14 | 完整 Dev/Packaged Gate、Sidecar、NSIS、真实缺省 exit 2 运行观测 | — | — | **NOT_RUN**（Task:49 排除；Review 授权禁止） | Task:49、Handoff:105、`VERIFICATION.md:54` 三处口径一致 |

**Architecture**：`N/A`——不触 `src/**`、`apps/**`、Schema、IPC、依赖；唯一可议处是 `build_parser()` 抽取与模块级 `RAW` 全局形成的测试 seam（R-06，已明确 deferred）。
**Verification**：AC1/AC2/AC3/AC4 的静态证据链闭合；AC5 交付物齐备（固定 commit + 测试日志 + 新 Handoff + 入库复现脚本）；运行级证据全部 **NOT_RUN**，由 Codex 集成 Gate 承接（§6）。
**证据纪律**：9 份证据文件中，8 份带 shell/头/EXIT 或 BASE/HEAD/COMMAND/EXIT；`raw-integrity.log` 已按 r1 要求补齐头部/COMMAND/EXIT（残余措辞见 R-10）。无「NOT_RUN 被写成 PASS」的表述（Task:49/65、Handoff:104-105、`VERIFICATION.md:50-54` 口径一致）。

## 6. 结论

**decision = `approved`。**

理由：

1. r1 的阻断项 **R-01（P1）已真正关闭**：README 当前示例指向 `$env:TEMP` 下的独立路径，明确位于 `verification/M2-RC2/raw`、`verification/M2-AC5/raw` 之外，并保留「必选参数 / 省略即 usage error + exit 2 / 输出目录须在历史 raw 树之外」的说明；原先「文档示范 = 回归门红灯」的互斥已消失（R-04 同时移除了 VCS 状态断言）。
2. R-02..R-05、R-07 均已在 reviewed_head 上关闭，且我用**独立算术**（行数差、stat 条形值和、快照条目数、raw 文件集合计数）交叉验证了 Owner 声明，未发现夸大。
3. R-06 的处置**诚实且可接受**：冗余断言已删，模块加载复杂度明确 deferred，Handoff/VERIFICATION 均未声称全关。
4. 代码语义逐条复核通过（§3）：唯一 parser、`required=True`、`parse_args` 先于一切输出目录副作用、显式路径沿用同一输出根、其他 Gate 行为零差异；依赖 Task 的冻结 oracle 不受影响。
5. 新增发现均为 **P3 文档/措辞/可选加固**（R-08..R-11），不触发「P0/P1 未解决不得批准」。

**放行条件（供 Codex 集成 Gate 执行；本 Task 未运行产品 Gate，不得把下列任一项写成产品 Gate PASS）**：

1. `python -m pytest -v tests/packaging/test_runner_output_dir_required.py` → 期望 `8 passed`、EXIT=0（3.14 与 3.12 各一次，与 Owner 侧一致）；
2. `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py --snapshot-before <tmp.json>` → 再跑回归 → `--compare-after <tmp.json>`，期望 61 文件 byte-identical + 两根 `git status` clean、EXIT=0；
3. `git diff --name-only --stat --check d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10..8b867e0208246e2e478a2906a2198c60c7d88aa6`（**注意用 reviewed_head 并保留 EXIT**），确认零超界、零空白错误；
4. 真实缺省调用观测：`python verification/M2-RC2/run_e2e.py`（无参数）与 `python packaging/m2ac5/run_clean_start_e2e.py`（无参数）→ 期望 exit 2 + `--output-dir` usage error，且**不在任何历史 raw 目录产生文件**（跑前跑后各取一次两 raw 目录状态）；
5. 顺手落字（非阻断）：R-08（Task:57 改 8/8）、R-09（命令补 `--diff-filter=M`/pathspec）、R-10（RESULT 行补作用域、修正 `:107` 计数），R-11 视需要。

**剩余风险（本 head 固有或本会话限制，供 Codex 登记）**：

1. **本会话零命令执行**：AC1「缺省真实 exit 2」、8 项回归、61 文件字节等值均只有 Owner 侧记录；其源码级充分性我已静态确证（V-1/V-2/V-5），但**运行级复现必须由集成 Gate 补齐**。
2. **base 等值为 proxy**：`d12ebc7a` 的完整树未能取回，V-3 依赖 ICU 冻结副本 + 行号锚点；若集成 `git diff` 发现变更区文本与 proxy 不一致，须以 git 为准重新确认 C-5。
3. **历史脚本/callers 的连带影响**：`verification/M2-RC2/integration-88f972fe/verify.ps1:14` 与 `doc/handoffs/M2-RG1-a1100d75.md:48` 记录了**不带 `--output-dir`** 运行 `verification/M2-RC2/run_e2e.py` 的旧命令；本 Task 之后这些冻结记录的命令不再可原样复跑（按设计：危险隐式默认被消除，历史文件禁止改写）。建议在集成记录/索引中登记一句，避免后续 Reviewer 误判为回归。
4. **显式传历史路径仍被接受**：Task:64 已冻结披露，本轮不新增路径策略；R-11 修复后「示范入口」已不再引导进入历史树。
5. **未入库的治理文件**：r1 引用的 `release.md` / `ANTIGRAVITY_INSTRUCTION.md` 在四处均不存在，本轮无法据其复核 AC3 原始口径（改以 Task:30 为判据）。

**集成建议**：可在上述放行条件（尤其第 3、4 条）通过后合并 `8b867e02`；Task/STATUS 的元数据回填归 Codex（R-07 已核实其主线提交 `8ad092d2`、`dc2b1bd3`）。
