# DSH r2 Reviewer 自有静态核对证据（M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD）

- task_id: `M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
- reviewer: DeepSeek Harness（非作者）
- review_base: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
- reviewed_head: `8b867e0208246e2e478a2906a2198c60c7d88aa6`
- code_delivery_head: `e167e72351d6f725653d1f16b210a54f435e621f`
- review worktree: `G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2`
- 本文件只记录**本人（DSH r2）实际做过的只读核对**；未执行的命令一律标注 NOT_RUN。

## 0. 执行环境（口径声明）

本会话 `pwsh` 在**沙箱准备阶段**即失败，命令体从未运行，逐次返回同一错误：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2)
```

- 默认模式、`workdir=C:\Windows\Temp`、无 workdir 三种调用：同一错误；
- `sandbox_permissions: danger-full-access` 一次性重试：`requires approval, but no approval channel is available`；
- 独立子代理（delegated subagent）复测 4 条 git 命令 + 2 条对照探测：同一错误，结论同为「shell 不可用」。

因此本会话**没有任何 `git` / `python` / `pytest` 命令由本人执行**。下面所有结论来自 `read` / `glob` / `grep` 的文件级核对，以及 `.git` 元数据文件（refs、worktree reflog）的直接读取。

## 1. 固定锚点核对（文件级实测）

| 项 | 实测值 | 方式 |
|---|---|---|
| worktree HEAD 指向 | `ref: refs/heads/review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 读 `.git/worktrees/…-dsh-r2/HEAD` |
| 该 ref 值 | `8b867e0208246e2e478a2906a2198c60c7d88aa6` = reviewed_head | 读 `.git/refs/heads/review/deepseek/…-r2` |
| worktree reflog | `0000… → 8b867e02`、`8b867e02 → 8b867e02  reset: moving to HEAD` | 读 `.git/worktrees/…-dsh-r2/logs/HEAD` |
| common dir | `G:/CODEX/New Manga/.git`（worktree `.git` 文件：`gitdir: G:/CODEX/New Manga/.git/worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2`） | 读 worktree `.git` 文件 |
| Owner 分支 | `refs/heads/agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` = `8b867e02`（与 reviewed_head 同一 commit） | 读 refs |
| main | `dc2b1bd3d3275bc3f8be88c87f604a8a10896d62` | 读 `.git/refs/heads/main` |
| `git status --porcelain` | **NOT_RUN**（无 shell）。替代观察见 §1.1 | — |

### 1.1 Owner 分支拓扑（reflog 直接证据，非猜测）

读 `.git/worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity/logs/HEAD`：

```text
d12ebc7a (start)
 → 1c49fe38  commit: fix(packaging): require explicit output-dir for M2 runners to protect historical raw evidence
 → 76e32b38  commit: docs(packaging): record M2 runner explicit output-dir guard verification and handoff
 → 0ea16b83  commit (amend): docs(packaging): record M2 runner explicit output-dir guard verification and handoff   ← DSH r1 reviewed_head
 → e167e723  commit: fix(packaging): update isolated output-dir example and hermetic parser tests (…)               ← code_delivery_head
 → 3801aa96  commit: docs(packaging): record M2 runner output guard r1 revision verification and handoff
 → 8b867e02  commit: docs: clarify runner guard r1 evidence disposition                                            ← reviewed_head
```

结论：`d12ebc7a` 是 `1c49fe38` 的父提交；`e167e723` 是 `8b867e02` 的祖先（相隔 2 个 commit）；DSH r1 审查的 head `0ea16b83` 恰好是 r2 修订的父提交。

### 1.2 dirty 状态的替代观察（不能替代 `git status`）

- 本 worktree 内存在两个**非 Owner 内容**的未跟踪文件：`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/review-dsh-r2-cli-output.md`（0 行）与 `review-dsh-r2-cli-stderr.log`（142 行）。其内容为**本会话（DSH 派发器）自身的 reasoning/stderr 流**，非 Owner 提交内容、亦非 Product 代码。
- 两个历史 raw 目录的文件集合（`glob`，含 hidden/ignored）与 tracked 计数吻合：`verification/M2-RC2/raw` = 25、`verification/M2-AC5/raw` = 36，合计 **61**；`raw-snapshot-before.json` 内 `"sha256"` 命中数亦为 **61**。
- **`git status --porcelain` 未执行**，故「worktree 整体是否干净」在本轮为 NOT_RUN；本报告不得声称本人验证过仓库干净。

## 2. 代码语义核对（静态）

| # | 核对点 | 结果 | 证据 |
|---|---|---|---|
| S-1 | 每个 runner 只有一个 argparse parser | PASS | `grep "ArgumentParser("`：`run_e2e.py:497`、`run_clean_start_e2e.py:735` 各 1 处 |
| S-2 | `--output-dir` 均 `required=True`、无 `default=RAW` 残留 | PASS | `run_e2e.py:501`、`run_clean_start_e2e.py:737`；两文件 `add_argument` 全集中无 `default=RAW` |
| S-3 | `parse_args` 先于任何输出目录副作用 | PASS | RC2 `main`：`:508 parse_args` → `:509 RAW=args.output_dir.resolve()` → `:510 mkdtemp` → `:511 RAW.mkdir`；AC5 `main`：`:744 parse_args` → `:745 RAW=resolve` → `:747 RAW.mkdir` → `:748 mkdtemp` |
| S-4 | 显式路径继续作为唯一输出根 | PASS | 两文件 `RAW` 在 `main` 内被唯一赋值一次；`grep "^RAW"` 仅模块级默认定义（`run_e2e.py:49`、`run_clean_start_e2e.py:53`），导出处无写盘 |
| S-5 | 无第二个 `--output-dir` / 第二个 parser | PASS | 同上 grep 全命中集 |

### 2.1 「变更仅限 parser/docstring」的行号锚点法（对 base proxy）

base proxy = 仓库内冻结副本 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/{run_e2e.py,run_clean_start_e2e.py}`（非 `d12ebc7a` 的 git 取回，属 proxy，与 r1 §1.1 同法）。

| 锚点 | ICU proxy | reviewed_head | 偏移 |
|---|---|---|---|
| `run_e2e.py` `SIDECAR_ALLOWED_PROJECT_MODULES = {` | 59 | 58 | −1 |
| `run_e2e.py` `def log(` | 80 | 79 | −1 |
| `run_e2e.py` `def check_sidecar_dump` | 485 | 484 | −1 |
| `run_e2e.py` `if __name__` | 650 | 654 | +4 |
| `run_e2e.py` 总行数 | 651 | 655 | +4 |
| `run_clean_start_e2e.py` `class Gate` | 98 | 98 | 0 |
| `run_clean_start_e2e.py` `def log(` | 119 | 119 | 0 |
| `run_clean_start_e2e.py` `def purged_environment` | 130 | 130 | 0 |
| `run_clean_start_e2e.py` `if __name__` | 883 | 888 | +5 |
| `run_clean_start_e2e.py` 总行数 | 884 | 889 | +5 |

- 两个文件在 parser/main 区之前**偏移恒定**（RC2 −1、AC5 0），在 parser/main 区之后偏移恒为 +4 / +5 ⇒ 净插入量全部落在 `def build_parser()/def main()` 区域；
- 两个文件的**总行数差 = 净差**（+4 = 11−7；+5 = 12−7），与 Handoff §3 声明的 per-file numstat（`run_e2e.py` 11+/7−、`run_clean_start_e2e.py` 12+/7−）**逐一相等**；
- 变更区绝无 Gate 场景/阈值结构：`S-1..S-5` 显示参数集与顺序不变，仅 `default=RAW → required=True` + `build_parser()` 抽取 + `main(argv)` 注入。

### 2.2 4 个代码文件的 r1→r2 差量自算

| 文件 | r1 worktree (`0ea16b83`) | r2 worktree (`8b867e02`) | 自算结论 |
|---|---|---|---|
| `verification/M2-RC2/run_e2e.py` | 655 行；`:496-515` 文本 | 655 行；`:496-515` 文本**逐行相同** | r1→r2 零改动 ✓ |
| `packaging/m2ac5/run_clean_start_e2e.py` | 889 行；`:734-750` 文本 | 889 行；`:734-750` 文本**逐行相同** | r1→r2 零改动 ✓ |
| `tests/packaging/test_runner_output_dir_required.py` | 173 行（含 `test_tracked_raw_evidence_directories_unmodified`、`git status` subprocess、`:73` 冗余 `or`） | 153 行（无 git 依赖、无冗余 `or`、AC5 拦截点改 `Path.mkdir`） | 153 = 173 − 24 + 4，与 Handoff 声明的 4+/24− **精确相符** ✓ |
| `packaging/m2ac5/README.md` | 基线+3 行（bar 5） | bar 5 = 3+2 | 与 Handoff 声明的 3+/3− 自洽 ✓ |

## 3. 证据文件核对（静态）

| 证据 | 核对结果 |
|---|---|
| `raw-integrity.log` | 有 `HOST/SHELL/PYTHON/VER/HEAD`（`:1`）、`COMMAND`（`:2`）、`EXIT=0`（`:9`）；`HEAD=e167e723…`；命令为 `verify_raw_integrity.py --compare-after …/raw-snapshot-before.json`；`:4` 61 files、`:5` 61 byte-identical、`:6` `Historical raw paths clean: True` |
| `verify_raw_integrity.py` | 已入库；`RAW_DIRS` 仅两个历史 raw 路径；tracked 集来自 `git ls-files -s`，逐文件 `sha256(read_bytes)` 与 `git hash-object` 对 index blob；前后快照做 keys 集合 + sha256 比对；`git status --porcelain=v1 -- <两个路径>` 限定作用域 |
| `raw-snapshot-before.json` | 已入库；`"sha256"` 计数 = **61**（与 log 的 61 独立吻合） |
| `pytest-regression.log` | 头 + `COMMAND` + `collected 8 items` + 8 项逐条 PASSED + `8 passed in 0.51s` + `EXIT=0`；rootdir=antigravity worktree |
| `pytest-regression-py312.log` | 同上，Python 3.12.3，`8 passed in 0.55s`，`EXIT=0` |
| `check-snapshots.log` | 头 + `COMMAND` + 16 个 actual-predicate case（含 8 条预期 FAIL 的负例）+ `PASS: 16 actual-predicate cases` + `EXIT=0` |
| `git-diff-stat.log` | `BASE/HEAD/COMMAND` + 14 files changed, 485 insertions(+), 28 deletions(-) + `EXIT=0`；4 个代码文件 bar = 5/19/153/18（合计 195 = 179+16，与 Handoff 的纯代码 179+/16− **精确自洽**） |
| `git-diff-name-only.log` | 同 14 个路径 + `EXIT=0`；含 r1 Handoff、Task、8 个 verification 文件 |
| `git-diff-check.log` | `BASE/HEAD/COMMAND` + 空输出 + `EXIT=0` |
| `VERIFICATION.md` | 7 项执行记录与上表一致；`:52-54` 如实标注 agy `status=ERROR`、完整 Dev/Packaged Gate NOT_RUN |
| 依赖 Task oracle `verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | 108 行；只按名 AST 抽取 `ALLOWLIST_RE/PRODUCTION_EXPECTED/PROBE_EXPECTED/check_announcement`、`Gate/run_library_probe`，断言 protocol minor 与公告/探针谓词；**不依赖 `--output-dir` 默认值**；r1/r2 worktree 副本锚点与行号一致（未改） |
| 历史 raw 未变（静态） | r1/r2 worktree 的 `verification/M2-AC5/raw` 文件名集合一致（36 个）；`M2-RC2/raw` 25 个；合计 61 = tracked 计数 |

## 4. 本人**未执行**的命令（NOT_RUN 清单）

| # | 命令/步骤 | 状态 |
|---|---|---|
| N-1 | `git rev-parse --abbrev-ref HEAD / HEAD / --git-common-dir` | NOT_RUN（改用 `.git` 文件直读，见 §1） |
| N-2 | `git status --porcelain` | NOT_RUN |
| N-3 | `git diff --name-only\|--check\|--stat --numstat d12ebc7a..8b867e02`（及 e167e723 口径） | NOT_RUN（仅交叉核对 Owner 日志） |
| N-4 | `python -m pytest -v tests/packaging/test_runner_output_dir_required.py`（3.14 / 3.12） | NOT_RUN |
| N-5 | `python verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/verify_raw_integrity.py`（含 61 文件 SHA256/blob 复算） | NOT_RUN |
| N-6 | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | NOT_RUN |
| N-7 | 任一 runner 的缺省调用（真实 exit 2 观测） | NOT_RUN |
| N-8 | 完整 Dev/Packaged Gate、Sidecar、NSIS | NOT_RUN（Task 明确排除，Review 授权亦禁止） |

## 5. 结论

静态意义上：AC1/AC2 的 CLI 语义、AC3 的 README 示例隔离性、AC4 的 hermetic 测试与可复现完整性脚本、以及依赖 Task 的冻结 oracle 兼容性均成立；r1 的 R-01..R-05、R-07 已在 reviewed_head 上关闭，R-06 为**明确披露**的部分闭合 + deferred。本会话无 shell，全部运行级证据为 **NOT_RUN**，须由 Codex 集成 Gate 承接（见报告 §6）。
