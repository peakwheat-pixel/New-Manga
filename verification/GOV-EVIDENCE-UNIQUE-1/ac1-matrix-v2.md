# AC1 — 61 项逐项记录（v2，按 r18 口径）

**Task**: GOV-EVIDENCE-UNIQUE-1 · **冻结 head**: `3c9ee0877` · **性质**: 只读

> v2 相对 v1 的差别：新增 **`在证据组中的作用`** 与 **`贡献给`** 两列。
> 这两列来自 AC2 的覆盖核验结果——只有做过 AC 级覆盖分析，才知道每份文件在
> 哪个 AC 的证据组里扮演什么角色。


## 汇总

| 项 | 值 |
|---|---:|
| 总项数 | 61 |
| 存在 | 54 |
| **不存在** | **7** |


## 角色的分布

| 作用 | 数量 |
|---|---:|
| **ABSENT** —— 文件不存在，无法承担任何作用 | 7 |
| 前端测试 | 6 |
| 脚本 | 5 |
| stderr | 5 |
| 独立 Review 记录 | 4 |
| 配置，非证据 | 3 |
| UIA 采集 | 3 |
| Core 测试日志 | 2 |
| 断言失败记录 | 2 |
| Rust 测试日志 | 2 |
| 前端构建日志 | 2 |
| 源数据快照 | 2 |
| 失败记录 | 1 |
| Rust packaged 测试日志 | 1 |
| Rust source 测试日志 | 1 |
| GUI 实测日志 | 1 |
| 环境记录 | 1 |
| 隔离准备日志 | 1 |
| 源数据保护日志 | 1 |
| 构建失败记录 | 1 |
| 前端测试日志 | 1 |
| 制品核验 | 1 |
| 命令 | 1 |
| 环境 | 1 |
| 退出码 | 1 |
| 日志 | 1 |
| Core 测试输出 | 1 |
| 请示文件，非证据 | 1 |
| 依赖安装日志 | 1 |
| cargo 构建日志 | 1 |


## 逐项矩阵

| # | path | 存在 | content_kind | 在证据组中的作用 | 贡献给 |
|---:|---|---|---|---|---|
| 1 | `verification/EXPORT-REVEAL-1/post-merge-packaged-capture-error.log` | 是 | RESULT_LOG | 失败记录（test failed） | EXPORT-REVEAL-1 AC6（反证） |
| 2 | `verification/EXPORT-REVEAL-1/pytest-core.log` | 是 | RESULT_LOG | Core 测试日志 | EXPORT-REVEAL-1 AC6 |
| 3 | `verification/EXPORT-REVEAL-1/rust-packaged.log` | 是 | RESULT_LOG | Rust packaged 测试日志 | EXPORT-REVEAL-1 AC6 |
| 4 | `verification/EXPORT-REVEAL-1/rust-source.log` | 是 | RESULT_LOG | Rust source 测试日志 | EXPORT-REVEAL-1 AC6 |
| 5 | `verification/FEAT-CREATE-3/dsh-review-r1.md` | 是 | EVIDENCE_NARRATIVE | 独立 Review 记录（判断，非证据） | 对应 Task 的 Review Gate |
| 6 | `verification/FEAT-CREATE-4/dsh-review-r1.md` | 是 | EVIDENCE_NARRATIVE | 独立 Review 记录（判断，非证据） | 对应 Task 的 Review Gate |
| 7 | `verification/FEAT-CREATE-4/gui-uia-command-r5.log` | 是 | RESULT_LOG | GUI 实测日志 | FEAT-CREATE-4 AC1 |
| 8 | `verification/FEAT-CREATE-4/isolation-namespace-rebind.log` | 是 | RESULT_LOG | 环境记录 | FEAT-CREATE-4 AC6 |
| 9 | `verification/FEAT-CREATE-4/isolation-prepare.log` | 是 | RESULT_LOG | 隔离准备日志 | FEAT-CREATE-4 AC6 |
| 10 | `verification/FEAT-CREATE-4/prepare-isolated-data.ps1` | 是 | SCRIPT | 脚本（产生隔离日志） | FEAT-CREATE-4 AC6 |
| 11 | `verification/FEAT-CREATE-4/rebind-isolated-namespace.py` | 是 | SCRIPT | 脚本（命名空间重绑） | FEAT-CREATE-4 AC6 |
| 12 | `verification/FEAT-CREATE-4/run-create-uia.ps1` | 是 | SCRIPT | 脚本（产生 UIA 日志） | FEAT-CREATE-4 AC1 |
| 13 | `verification/FEAT-CREATE-4/source-preservation-check.log` | 是 | RESULT_LOG | 源数据保护日志 | FEAT-CREATE-4 AC6 |
| 14 | `verification/FEAT-IMPORT-MULTI-1/appdata-preservation.log` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 15 | `verification/FEAT-IMPORT-MULTI-1/checkpoint.md` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 16 | `verification/FEAT-IMPORT-MULTI-1/dsh-review-r1.md` | 是 | EVIDENCE_NARRATIVE | 独立 Review 记录（判断，非证据） | 对应 Task 的 Review Gate |
| 17 | `verification/FEAT-IMPORT-MULTI-1/fixture-generation.log` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 18 | `verification/FEAT-IMPORT-MULTI-1/gui-runner-console.log` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 19 | `verification/FEAT-IMPORT-MULTI-1/isolation-prepare.log` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 20 | `verification/FEAT-IMPORT-MULTI-1/main-worktree-status.log` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 21 | `verification/FEAT-IMPORT-MULTI-1/make-fixtures-r1.py` | **否** | ABSENT | **ABSENT** —— 文件不存在，无法承担任何作用 | 无（BLOCKED_ABSENT） |
| 22 | `verification/HOST-TTL-BOUNDARY-1/ac3-rust-ttl-boundary-build-attempt-1.log` | 是 | RESULT_LOG | 构建失败记录（EXIT_CODE=101） | HOST-TTL-BOUNDARY-1 AC3（未通过） |
| 23 | `verification/HOST-TTL-BOUNDARY-1/ac4-export-frozen-rust-attempt1-4662239.log` | 是 | RESULT_LOG | 断言失败记录 | HOST-TTL-BOUNDARY-1 AC4（未通过） |
| 24 | `verification/HOST-TTL-BOUNDARY-1/ac4-frozen-host-importpages.log` | 是 | RESULT_LOG | 断言失败记录 | HOST-TTL-BOUNDARY-1 AC4（未通过） |
| 25 | `verification/HOST-TTL-BOUNDARY-1/ac6-rust-tests.log` | 是 | RESULT_LOG | Rust 测试日志（84 pass） | HOST-TTL-BOUNDARY-1 AC6 |
| 26 | `verification/P14/frontend-build.log` | 是 | UNKNOWN | 前端构建日志 | P14 AC5 |
| 27 | `verification/P14/frontend-tests.log` | 是 | RESULT_LOG | 前端测试日志 | P14 AC5 |
| 28 | `verification/P15/cargo-test-unfiltered-first-run.log` | 是 | RESULT_LOG | Rust 测试日志（与 AC5 前端要求不匹配） | P15 AC5（不匹配） |
| 29 | `verification/P15-CORE-1C/canonical-hash-verification.txt` | 是 | RESULT_LOG | 制品核验 | P15-CORE-1C AC6 |
| 30 | `verification/P15-CORE-1C/pytest-core-focused.command.txt` | 是 | RESULT_LOG | 命令 | P15-CORE-1C AC6 |
| 31 | `verification/P15-CORE-1C/pytest-core-focused.environment.txt` | 是 | UNKNOWN | 环境 | P15-CORE-1C AC6 |
| 32 | `verification/P15-CORE-1C/pytest-core-focused.exit-code.txt` | 是 | UNKNOWN | 退出码 | P15-CORE-1C AC6 |
| 33 | `verification/P15-CORE-1C/pytest-core-focused.log` | 是 | RESULT_LOG | 日志 | P15-CORE-1C AC6 |
| 34 | `verification/P15-HOST-1/.gitattributes` | 是 | CONFIG | 配置，非证据 | 无 |
| 35 | `verification/P15-HOST-1/core-pytest-full-suite-extra.txt` | 是 | RESULT_LOG | Core 测试输出（含 37 FAILURES） | P15-HOST-1 AC5（未通过） |
| 36 | `verification/P15-HOST-1/resource-manifest.json` | 是 | CONFIG | 配置，非证据 | 无 |
| 37 | `verification/P15-HOST-2/ac1-coordinator-blocker.md` | 是 | EVIDENCE_NARRATIVE | 请示文件，非证据 | 无 |
| 38 | `verification/P15-HOST-2/core-pytest-final.log` | 是 | RESULT_LOG | Core 测试日志 | P15-HOST-2 AC5 |
| 39 | `verification/P15-HOST-2/frontend-deps-setup.log` | 是 | RESULT_LOG | 依赖安装日志 | P15-HOST-2 前置条件 |
| 40 | `verification/P15-HOST-2/frontend-vitest-alias-attempt.log` | 是 | RESULT_LOG | 前端测试（别名修复尝试，pass=2 fail=31） | P15-HOST-2 AC5（早尝试） |
| 41 | `verification/P15-HOST-2/frontend-vitest-final.log` | 是 | RESULT_LOG | 前端测试（最终） | P15-HOST-2 AC5 |
| 42 | `verification/P15-HOST-2/frontend-vitest-isolated.log` | 是 | RESULT_LOG | 前端测试（中尝试） | P15-HOST-2 AC5 |
| 43 | `verification/P15-HOST-2/host-only-rescan.ps1` | 是 | SCRIPT | 脚本 | 无 |
| 44 | `verification/P15-HOST-2/modified-files-sha256.py` | 是 | SCRIPT | 脚本 | 无 |
| 45 | `verification/P19-BOOT-1/.gitignore` | 是 | CONFIG | 配置，非证据 | 无 |
| 46 | `verification/P19-UI-FIX-1/04-settings-before-final-code-refinement.uia.txt` | 是 | UNKNOWN | UIA 采集（早） | P19-UI-FIX-1 AC1 |
| 47 | `verification/P19-UI-FIX-1/04-settings-uia-pass-2.txt` | 是 | UNKNOWN | UIA 采集（中） | P19-UI-FIX-1 AC1 |
| 48 | `verification/P19-UI-FIX-1/04-settings-uia-pass-exit-code-blank.txt` | 是 | UNKNOWN | UIA 采集（最终） | P19-UI-FIX-1 AC1 |
| 49 | `verification/P19-UI-FIX-1/app-err-before-final-code-refinement.log` | 是 | RESULT_LOG | stderr（早） | P19-UI-FIX-1 AC4 |
| 50 | `verification/P19-UI-FIX-1/app-err-namespace-mismatch.log` | 是 | RESULT_LOG | stderr（命名空间失败） | P19-UI-FIX-1 AC4（反证） |
| 51 | `verification/P19-UI-FIX-1/app-err-ui-a-pass-exit-code-blank-2.log` | 是 | RESULT_LOG | stderr（后） | P19-UI-FIX-1 AC4 |
| 52 | `verification/P19-UI-FIX-1/app-err-ui-load-failure.log` | 是 | RESULT_LOG | stderr（UI 加载失败） | P19-UI-FIX-1 AC4（反证） |
| 53 | `verification/P19-UI-FIX-1/app-err-uia-pass-exit-code-blank.log` | 是 | RESULT_LOG | stderr（最终） | P19-UI-FIX-1 AC4 |
| 54 | `verification/P19-UI-FIX-2/appdata-source-after.json` | 是 | CONFIG | 源数据快照（后） | P19-UI-FIX-2 隔离 |
| 55 | `verification/P19-UI-FIX-2/appdata-source-before.json` | 是 | CONFIG | 源数据快照（前） | P19-UI-FIX-2 隔离 |
| 56 | `verification/P19-UI-FIX-2/bookshelf-import-targeted-test-final-r2.log` | 是 | RESULT_LOG | 前端测试（最终 R2） | P19-UI-FIX-2 AC3 |
| 57 | `verification/P19-UI-FIX-2/bookshelf-import-targeted-test-final.log` | 是 | RESULT_LOG | 前端测试（最终 R1） | P19-UI-FIX-2 AC3 |
| 58 | `verification/P19-UI-FIX-2/bookshelf-import-targeted-test.log` | 是 | RESULT_LOG | 前端测试（首跑，1 failed） | P19-UI-FIX-2 AC3 |
| 59 | `verification/P19-UI-FIX-2/cargo-build-before.log` | 是 | RESULT_LOG | cargo 构建日志（带 EXIT_CODE=0） | P19-UI-FIX-2 AC4 |
| 60 | `verification/P19-UI-FIX-2/dsh-review-r1.md` | 是 | EVIDENCE_NARRATIVE | 独立 Review 记录（判断，非证据） | 对应 Task 的 Review Gate |
| 61 | `verification/P19-UI-FIX-2/frontend-npm-build-before.log` | 是 | RESULT_LOG | 前端构建日志（带 EXIT_CODE=0） | P19-UI-FIX-2 AC4 |

## 判读要点

### 1. 七项不存在，角色为空

`FEAT-IMPORT-MULTI-1` 的 7 份文件不存在，无法承担任何证据作用。
它们的 `role_in_group` 记为 `ABSENT`，不是「未知」——**缺失是确定事实，不是不确定**。

### 2. 「配置」与「脚本」不是证据

`.gitignore`、`.gitattributes`、`resource-manifest.json` 是配置；
`.ps1`、`.py` 是脚本。它们**能产生证据，本身不是证据**。

这一点在 v2 里通过 `在证据组中的作用` 列显式表达：
脚本记为「脚本（产生 X 日志）」，配置记为「配置，非证据」。

### 3. 「失败记录」也是证据——但是反证

`HOST-TTL-BOUNDARY-1` 的三份失败日志、`EXPORT-REVEAL-1` 的
`post-merge-packaged-capture-error.log`、`P19-UI-FIX-1` 的两份 `app-err-*-failure`，
都记为「失败记录」并注明「（反证）」或「（未通过）」。

**把它们记成「无作用」是错的**——它们恰恰证明某次运行失败了。
本 Task 只记录它们在组中的真实作用，不对「失败是否已被修复」下结论
（那需要后续运行的日志，而候选集里没有）。

### 4. 多次尝试的时序可辨识

`P19-UI-FIX-1` 的三份 UIA 采集、`P15-HOST-2` 的四份 vitest 日志、
`P19-UI-FIX-2` 的三份 import 测试日志——都在作用列标注了
（早 / 中 / 最终 / R2），使「哪次是最终依据」可追溯。

这直接落实 r18 第一条口径。

### 5. 与 AC2 的对应关系

本文只记录**每份文件在组里的作用**，不下覆盖结论。
覆盖结论在 `ac2-coverage-batch{1,2,3}*.md`。
两者的关系是：**AC2 判「这个 AC 的组够不够」，AC1 判「这份文件在组里干什么」。**

## 局限

- 作用分类是我根据 AC2 的覆盖分析**人工指派**的，不是从文件内容自动推断。
  61 项里 54 项已指派，7 项因缺失无法指派。
- 若某份文件实际上服务于我没识别出的 AC，本表会漏记。
  **这是人工指派的固有风险**，已在 AC4 的 limitation 中声明。

