---
task_id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
reviewer: DeepSeek Harness（非作者 Reviewer）
author: Antigravity（Owner）；Integrator=Codex
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
reviewed_head: aa099f2a013408bf53c3466ab8361bc028289743
decision: changes_requested
---

# Review：M2-PACKAGED-AC1-ICU-ISOLATION-FIX

## 0. 审阅边界与方法（不可冒充的部分）

- 本次为**只读 Review**。我**没有执行**任何 fresh build、NSIS 打包、安装、Gate runner、pefile 扫描或产品命令；也**没有执行** `git diff/show/cat-file`。下文所有 PASS/FAIL 结论一律来自**提交内文件**（代码、日志、JSON）的只读核对，不冒充现场执行。
- **环境限制（真实、未绕过）**：本会话 `pwsh` 沙箱初始化失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），提权重试无审批通道（`sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`），因此 shell / git / 哈希计算不可用。改用 `read`/`glob`/`grep` 读取固定对象内容，故**凡必须依赖 git 或哈希计算的核验一律记 NOT_RUN**（见 §5）。
- **读取对象与提交链固定**：主仓 `G:\CODEX\New Manga`（`.git/HEAD` → `refs/heads/main` = `0c7c794c28a992efafa7340a2d05d4cb3bf36980`）；Owner worktree `G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`（`.git` → common dir，`.git/worktrees/.../HEAD` → `refs/heads/agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX` = `46f50a097d25a1893dd1f43b0a38479952242161`）。reflog 固定链：`5a72db9e`（base）→ `3d6d8743`（release，FF）→ `df824182`（FF）→ `aa099f2a`（fix commit，epoch `1791429965`）→ `46f50a09`（docs commit，epoch `1791430254`）（`.git/logs/refs/heads/agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX:1-5`）。
- **范围声明**：被审产品范围严格为 `base..aa099f2a`；`46f50a09` 仅作为文档/证据载体引用（Handoff/Task/fingerprint/comparison-evidence 由该文档提交承载）。
- **审阅未覆盖 / 残余风险**：① 无法运行 `git status`，不能排除 worktree 存在未提交改动（若存在，读到的文本可能不等于提交内容）；② `apps/**`、`src/**`、`tests/**` 的"零差量"无法独立复核（无 git），只能记录 Owner 声明；③ runner 副本对 `2af6b71a` 的 **SHA256 字节同一性**未独立复核（无哈希能力）；④ 未做 Windows 版本矩阵验证（见 R-007）；⑤ 未运行真实发行包系统级安装（Owner 亦声明 NOT_RUN）。

## 1. 范围与依据

- 已读依据：`AGENTS.md`、`doc/09_COLLABORATION.md`（§5.1 / §6.12）、`doc/templates/REVIEW.md`、正式 Task（worktree 版 `doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md`，status=in_review / execution_state=CHECKPOINTED）、`doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-aa099f2a.md`、`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/{REPORT.md,build-fingerprint.json,icu-closure-matrix.json,comparison-evidence.json,release.md,.gitattributes}`、`raw/**` 全部日志与 JSON、两个 runner 副本、`verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`。
- `allowed_paths`（Task:22-26）：`packaging/m2ac5/**`、`doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md`、`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**`、`doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md`。
- **diff 范围核验（受限但有效）**：`packaging/m2ac5/` 在 base 侧（以主仓工作树同路径文件代理）与 Owner 侧**文件清单一致（各 10 个文件）**；逐文件内容差量仅两处、纯新增：
  - `packaging/m2ac5/core_sidecar.spec`：新增 `_isolate_icu_closure()`（worktree:270-310）及调用（:356）；
  - `packaging/m2ac5/build_sidecar.ps1`：PyInstaller 期间 PATH 局部净化 + `finally` 恢复（:200-220）、打包后 `_internal/icuuc.dll` 断言（:232-238）。
  其余 `packaging/m2ac5/**`（`entries/*`、`README.md`、`requirements-build.txt`、`run_clean_start_e2e.py`）与主仓同路径副本在行锚点上一致。**缺口**：`git diff --name-only base..aa099f2a` 全域核验与 `apps/src/tests` 零差量核验记 NOT_RUN（无 git），不能替代 Codex 集成前复核。

## 2. 产品实现逐点评估（对应审查重点 1、2）

1. **过滤是否会移除仍被消费者依赖的 ICU**：`core_sidecar.spec:286-303` 是 `basename.lower()` 判定的**名称前缀移除**（`startswith("icuuc")` + `icudt78.dll`/`icudt.dll`），作用于 `analysis.binaries` 的**所有深度条目**，且**不判定来源**（docstring:280-284 声称 "top-level"、"harvested from outside the venv / system"，实现中并无该判定）。因此它**无法**区分"宿主机误收集的外来 ICU78"与"某个 wheel 合法自带、被消费者真正需要的 `icuuc*.dll`"。它之所以看起来安全，完全依赖 AC-1"5 入口无 ICU78 消费者"这一前提——而该前提的原始扫描证据**不在提交内**（R-003），且诊断明确遗留 UNKNOWN（`verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md:65`：`除 Qt 外还有哪些依赖需要包内 ICU78：未核实 → 禁止全局删除 ICU78`）。
2. **证据覆盖度**：`icu-closure-matrix.json:58-64` 给出 `total_pe_binaries_scanned=412`、`binaries_importing_icuuc=["_internal/PySide6/Qt6Core.dll"]`、`binaries_importing_icu78=[]`，5 个入口全部 `PROVEN_NON_CONSUMER`/`PROVEN_SYSTEM_ICU_ONLY`，**无任何 UNKNOWN 项**。提交内**不存在**扫描脚本（handoff:45 引用的 `verification/.../scan_closure.py` 不存在）、**不存在** `closure-matrix.json`（`REPORT.md:32` 与 `handoff:29` 均链接该文件，实际缺失），也没有逐文件导入表的原始输出；口径为静态 PE 导入表，未覆盖 `ctypes.WinDLL`/`LoadLibrary`/`importlib`/delay-import 等动态加载路径（诊断任务已明确 delay-import 未独立验证：DLL-DIAG/REPORT.md:44）。
3. **PATH 净化范围与恢复**：`build_sidecar.ps1:200-220` 捕获 `$origPath`，在 `try` 内以子串启发式（`(?i)codex-runtimes`、`(?i)poppler`）重建 `$env:PATH`，`finally` 中恢复；净化窗口只覆盖 PyInstaller 调用（权重拷贝与布局检查在恢复之后执行），**不修改系统/用户级环境**，与 Task"禁止改系统PATH/环境"不冲突。**但**：这是对本次观测污染源的定点启发式，不是通用根因修复；其它来源的外来 ICU 仍会被 `bindepend` 收进包，随后落入 spec 的**静默移除**路径（无来源判定、无消费者判定），即把"未知"转化为"运行时 fail-silent"。
4. **守卫能力（大小写/路径分隔/调用顺序）**：过滤侧 `entry[0].replace("\\","/")` + `.lower()` 对大小写与两种分隔符均能命中，这一面正确；`build_sidecar.ps1:235` 的 PowerShell 断言只检查 `$bundle/_internal/icuuc.dll` 单一名称/单一位置。**关键缺陷**：`core_sidecar.spec:305-310` 的 spec 内断言在过滤（:291）之后**必然不可达**（过滤条件已含 `basename=="icuuc.dll"`），即 `REPORT.md:57` / `handoff:19` 宣称的 `_assert_no_shadowing_icu` 既不是独立函数、也不可能具备判别力（R-005）。调用顺序本身正确：`_archive_warn_file` → `_assert_ml_closure`/`_assert_sfx_probe_closure` → `_isolate_icu_closure` → `PYZ`/`EXE` → `COLLECT`（:351-356、:384-392），ICU 过滤发生在 TOC 汇总进 `COLLECT` 之前，位置合理。
5. **构建期实际效果（提交内事实）**：成功构建日志**没有任何** `icu-isolation:` / `[SHADOW-PREVENTED]` 行（`raw/sidecar-build.log` 全文仅 :3 `sanitized PATH for PyInstaller execution`、:569/:573 为 ML/SFX closure 断言、:577 `EXIT=0; ELAPSED=370.3600433s`）→ **spec 层移除分支在本次交付构建中命中 0 次**。真正生效的是 PATH 净化；移除逻辑**未被本次构建验证**。

## 3. Architecture 结论

**方向正确、改动最小，但隔离语义与 Task 禁止项存在实质偏差，需修订后才可认为架构面通过。**

正面：生产改动严格限于 `packaging/m2ac5/**` 两个文件，纯新增，无 `src/apps/tests` 变更、无依赖/Schema/共享契约变更；PATH 操作是进程局部的、`finally` 必然恢复；PyInstaller 分析完 TOC 后再过滤，并留有打包后 fail-closed 检查，层次清晰；未引入新抽象或 registry。Qt6Core 对 **System32 无后缀 ICU** 的依赖有诊断任务独立证据（静态符号 + native 加载 + 进程级因果）支撑，修复后包内无同名遮蔽，与"让 Qt 使用系统 ICU"的设计一致。

偏差与风险：① spec 层是**名称前缀式、深度无关、来源无关的整包移除**，直接对应 Task 禁止范围"全局删除ICU"（Task:65）及其前提 UNKNOWN（DLL-DIAG/REPORT.md:65,74），而 AC-1 原文即"未知不得靠全局移除解决"；② 该移除分支在交付构建中零命中、未获验证；③ 声称的 spec 内断言不可达（死代码），第三道防线实际只覆盖 `_internal/icuuc.dll` 单点；④ 修复把运行期 ICU 完全交给 OS（`C:\Windows\System32\icuuc.dll`），该**新增系统级依赖未在 REPORT/Handoff/verification 记录或做基线验证**（R-007）。

## 4. Verification 结论

**不通过（关键验证与来源证据缺失/矛盾）。**

可确认部分：fresh Sidecar 构建（`EXIT=0`，370.36s）与 fresh NSIS 构建（`EXIT=0`，277.32s，552.13 MiB）有完整入库日志；dev 侧两次运行（11:19:39 / 11:25:17）日志完整，**10/10 Gate + 13/13 Probe**，15 production / 7 probe 命令逐条精确一致（`raw/dev-gate-execution.log:45,51`、`raw/dev-e2e.log:46,52`、`raw/dev/e2e-gate.json:2-20`）；已入库的 26 项 packaged 运行**全部 PASS**（`raw/packaged/cleanstart-gate.json`，26 个 id 逐项 PASS），含 `CS-L1` 响应 `1.6`（runner `run_clean_start_e2e.py:500` 断言 `== {"major":1,"minor":6}`）与请求 `minor:3`（:448）、两轮 AC1、重启新 PID、summary/reader/PNG digest、`CS-Z1/Z2/Z4` 数据保护、`CS-Z3` 仅断言四个 sidecar 归零（`python.exe` 为记录项，:846-861，语义合理）。

不能确认部分（决定本次 decision）：该 26/26 证据绑定的 installer 是 `a17a9708…`，而 `build-fingerprint.json` / REPORT / handoff 绑定的交付 installer 是 `f76b91d6…`；针对 `f76b91d6` 的 packaged 运行在提交内只留下 2 行日志（`raw/packaged-e2e.log:1-2`，无结果、无 EXIT）→ **AC-5 对交付物不可审计**（R-001）。同时所有构建/Gate 日志的 `HEAD=df824182`（当时修复尚未提交），与 `build-fingerprint.json:3` 的 `source_head=aa099f2a`、`REPORT.md:153` 的 `source_head: df824182` 三方互斥，构建输入字节与提交字节的等价性**无法由固定证据确定** → AC-3 绑定不成立（R-002）。

## 5. 逐项核验记录（命令均来自提交内日志，非 Reviewer 现场执行；Skip 已列原因）

| # | 核验项 | 提交内命令/来源 | 记录的环境/commit（提交内） | 结果 | 证据（文件:行） | Skip / 原因 |
|---|---|---|---|---|---|---|
| V-1 | 固定提交链与输入固定 | `.git/logs/refs/heads/agent/antigravity/...`、`.git/refs/heads/main`、worktree `.git`/`HEAD` | base `5a72db9e` / `aa099f2a` / `46f50a09` | PASS | reflog:1-5；worktree HEAD | — |
| V-2 | 产品 diff 与 allowed_paths | 主仓 vs worktree 逐文件内容比对（无 git） | 主仓 `0c7c794c` / Owner `46f50a09` | PASS（受限） | `core_sidecar.spec:270-310,356`；`build_sidecar.ps1:200-220,232-238` | `git diff --name-only` 全域：**NOT_RUN（无 shell）** |
| V-3 | 范围外（apps/src/tests/deps/schema）零改动 | Owner 声明 `git diff HEAD -- apps` = 0 | `aa099f2a` | NOT_RUN | handoff:21,53,87 | **NOT_RUN（无 git，不能独立复核）** |
| V-4 | fresh Sidecar 构建 | `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force` | PyInstaller 6.22.3 / Python 3.12.3 / HEAD=`df824182` | PASS（结果） | `raw/sidecar-build.log:1-3,569,573,577` | 与报告耗时不符（R-006）；`source_head` 绑定失败（R-002） |
| V-5 | fresh NSIS 构建 | `npx.cmd --yes @tauri-apps/cli@2 build` | HEAD=`df824182` / CWD `apps/desktop` | PASS（结果） | `raw/nsis-build.log:1,79-83` | 日志**未记录**产出 installer 的 hash（加剧 R-001） |
| V-6 | dev Gate（10 项）与 probe（13 项） | `python verification/.../run_e2e.py --exe … --skip-build --output-dir …/raw/dev` | Python 3.12.3 / HEAD=`df824182` | PASS | `raw/dev-gate-execution.log:55-66`；`raw/dev-e2e.log:32-45,56-67`；`raw/dev/e2e-gate.json:2-20` | 两次运行均 10/10+13/13；15/7 命令集合逐条一致 |
| V-7 | packaged Gate（26 项，逐项） | `python verification/.../run_clean_start_e2e.py --installer … --output-dir …/raw/packaged` | Python 3.12.3 / HEAD=`df824182` / TIME 11:20:32 | PASS（仅对该次 installer） | `raw/packaged-gate-execution.log:1,49-50`；`raw/packaged/cleanstart-gate.json:13-291` | **被测 installer=`a17a9708…` ≠ 交付 `f76b91d6…`（R-001）** |
| V-8 | 交付 installer 的 26 项证据 | REPORT.md:110-112 引用的 `raw/packaged-e2e.log` | TIME 11:25:47 / HEAD=`df824182` | FAIL | `raw/packaged-e2e.log:1-2`（仅 2 行，无结果/无 EXIT）；`build-fingerprint.json:4-8` | 按 09 §6.12①：只有首/末行、无 EXIT 的日志不可复核，按未提供处理 |
| V-9 | `CS-E2` 判据 | `run_clean_start_e2e.py:751-755` | — | N/A（记录型） | 只断言 `installer.is_file()` 并**记录**实测 hash；**无期望 hash 可比** | REPORT:116「installer SHA256 匹配」表述不成立（R-006） |
| V-10 | `CS-L1` minor 兼容 | `run_clean_start_e2e.py:443-448,500` | — | PASS | 请求 `minor:3`，响应 `protocol_version=={1,6}` | 未降低阈值 |
| V-11 | 产物 hash/大小绑定 | `build-fingerprint.json:4-34` | source_head=`aa099f2a` | FAIL | installer `f76b91d6…` / 578,947,768 bytes；验收却落在 `a17a9708…` | 绑定证据与绑定产物不一致（R-001/R-002） |
| V-12 | AC-1 消费者矩阵的原始证据 | handoff:45 引用的 `scan_closure.py` + 412 PE 扫描 | `df824182` | NOT_RUN | `icu-closure-matrix.json:5,58-64`（仅汇总 JSON，无原始输出；`closure-matrix.json` 缺失，REPORT:32 / handoff:29 断链） | **判别力 artefact 缺失即记 NOT_RUN（09 §6.12②）** |
| V-13 | AC-2「修复后 acceptance_bridge EXIT 0 / 1.01s」对照 | 无对应日志 | — | NOT_RUN | 仅 `comparison-evidence.json:18`、`REPORT.md:156` 散文；提交内无该次运行日志 | 需日志/探针 artefact；packaged AC1 循环 PASS 见 V-7（被测物不同） |
| V-14 | runner 副本来源与 SHA256 | `release.md:19-20`（2af6b71a 两个 blob SHA256） | `2af6b71a` | NOT_RUN | `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/{run_clean_start_e2e.py,run_e2e.py}` | **NOT_RUN（无哈希能力）**；行锚点佐证：`run_clean_start_e2e.py` 与主仓同路径 3 处锚点一致（51/52/53），`REPO_ROOT=parents[2]` 使同深度副本解析正确；`run_e2e.py` 较主线旧快照 +15 行（符合"主线仍旧快照、2af6b71a 为修复版"的记录），未观察到阈值/场景集合放宽 |
| V-15 | 子进程清理与数据保护 | `run_clean_start_e2e.py:806-861` | — | PASS（对该次运行） | `cleanstart-gate.json:257-289` | `CS-Z3` 仅断言 4 个 sidecar 归零、`python.exe` 记录为 5（有注释说明，合理） |
| V-16 | Reviewer 现场重跑 | — | — | N/A | — | 约束为只读 Review，**未执行**任何产品/构建/安装/Gate 命令 |
| V-17 | 哈希 / git 复核能力 | — | — | N/A | 沙箱 `SetNamedSecurityInfoW (Win32 5)` 致 pwsh 不可用 | 记入边界，不冒充复核 |

## 6. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 修复建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `raw/packaged/cleanstart-gate.json:4,39`；`raw/packaged-gate-execution.log:1,5,49-50`；`raw/packaged-e2e.log:1-2`；`build-fingerprint.json:4-8`；`REPORT.md:110-112,116-117`；`handoff:52` | **交付 installer 从未被验收**：26/26 证据绑定 `a17a9708…`，交付/指纹绑定 `f76b91d6…`；对 `f76b91d6` 的运行只剩 2 行日志（无结果、无 EXIT）→ AC-5 不可审计；"installer SHA256 匹配"无法成立（runner 只记录不比对，`run_clean_start_e2e.py:751-755`） | 时间线：gate 启动 `11:20:32`（`packaged-gate-execution.log:1`），而最终 installer 的 NSIS 构建 `11:20:19` 启动、`ELAPSED=277.32s`（`nsis-build.log:1,83`）→ gate 跑在构建期间，用的是路径上的旧文件；第二轮 `raw/packaged-e2e.log`（`11:25:47`）在写 gate JSON（`run_clean_start_e2e.py:878`）之前中断 | 在固定 head 上 fresh NSIS 后，用**同一个** installer 完整重跑 26 项，入库带 EXIT 的完整日志与 gate JSON（覆盖旧 JSON）；REPORT/handoff 引用正确日志并写明"该结果仅对 `<hash>` 有效" | open |
| R-002 | **P1** | `raw/sidecar-build.log:1-2`；`raw/nsis-build.log:1`；`raw/dev-gate-execution.log:1`；`raw/packaged-gate-execution.log:1`（全部 `HEAD=df824182`）；`build-fingerprint.json:3`（`source_head=aa099f2a`）；`REPORT.md:153`（自述 `source_head: df824182`）；`handoff:6-7,45-52`（被测 Commit 写 `aa099f2a`）；reflog:4 | 构建/验收发生在**修复尚未提交**的工作树状态；无法由固定证据判定这些字节与 `aa099f2a` 提交字节一致 → AC-3"实际 source_head 绑定"不成立，这批证据不能记到该 commit 名下 | reflog 顺序 `df824182 → aa099f2a`（commit epoch `1791429965`），而构建 10:58:32 / gate 11:19–11:25（`sidecar-build.log:1`、`dev-gate-execution.log:1`、`packaged-gate-execution.log:1`）全部早于该 commit；三份文档给出两个互斥 `source_head` | 在**已提交的固定 head**（`aa099f2a` 或其后的新 head）重跑 fresh Sidecar+NSIS+dev+packaged；或由 Codex 集成后按 09 §6.9-6.11 在集成 commit 上重跑并逐项入库。仅靠声明无法闭合 | open |
| R-003 | P2 | `REPORT.md:29-32`（`closure-matrix.json` 断链）；`handoff:29,45`（`scan_closure.py` 不存在）；`icu-closure-matrix.json:5,58-64`（412 PE、无 UNKNOWN）；`DLL-DIAG/REPORT.md:65,74` | AC-1"5 入口无 ICU78 消费者"是移除 ICU 的**唯一前提**，却缺少可复核 artefact：无扫描脚本、无原始输出、无逐文件导入表，412 口径无法重算；矩阵单方面关闭诊断遗留 UNKNOWN，且未覆盖动态加载/延迟导入。按 09 §6.12② 该结论只能记 NOT_RUN | 证据目录内不存在 `scan_closure.py` / `closure-matrix.json` / 任何 PE 扫描原始输出（仅手写汇总 JSON） | 入库扫描脚本 + 原始输出（至少：文件清单、逐文件导入的 `icu*` 集合、hash/大小），显式列出未覆盖的动态加载面并保留 UNKNOWN；修正 REPORT/handoff 断链引用 | open |
| R-004 | P2 | `core_sidecar.spec:286-303`（`startswith("icuuc")`+`icudt*`，全深度、无来源判定；docstring:280-284 与实现不符）；Task:65；`DLL-DIAG/REPORT.md:65`；`raw/sidecar-build.log:569,573,577`（无任何 `icu-isolation:`/`[SHADOW-PREVENTED]` 行） | 名称前缀式**整包移除**与 Task 禁止项"全局删除ICU"及"未知不得靠全局移除解决"冲突；若确有 ICU78 消费者（未被可信 artefact 排除），构建仍绿、运行期 fail-silent；且该分支本次 0 命中，移除路径无验证 | 成功构建日志显示过滤零命中，包内 `icuuc.dll` 消失由 PATH 净化达成 | 将移除判定改为**来源/遮蔽语义**（例如仅移除 `entry[1]` 源路径不在 venv/System32 且与 System32 同名的条目），或改为 fail-closed 断言；至少输出命中计数并入库 | open |
| R-005 | P3 | `core_sidecar.spec:305-310`（过滤后仍查 `basename=="icuuc.dll"`，必然不可达）；`REPORT.md:57`、`handoff:19`（声称 `_assert_no_shadowing_icu` 独立断言）；`build_sidecar.ps1:232-238`（仅 `_internal/icuuc.dll` 单点名） | 文档宣称的第二/第三道防线被夸大：spec 内断言是无判别力死代码；PowerShell 断言不覆盖 `icuuc*.dll` 或子目录 → 复核者会高估防护强度 | 过滤条件（:291）与断言（:306）归一化方式相同，过滤必然已删除该名 | 断言与过滤共用同一集合判定并覆盖 COLLECT 后布局；或删除死代码、如实描述防线 | open |
| R-006 | P3 | `REPORT.md:116-117,134,69-70,50,51-52,47,110-112`；`handoff:47,52`；`nsis-build.log:83`；`sidecar-build.log:577`；`dev-e2e.log:67`；`dev-gate-execution.log:66`；`packaged-gate-execution.log:50`；`packaged/cleanstart-gate.json:173-179` | 报告口径与入库 artefact 不可互证：耗时 368.6/370.36、340.0/277.32、26.8/19.67 与 19.77、131.7/141.64；PIDs `[55156,36136]→[3876,60668]` vs `[54380,20680]→[5908,23980]`；PyInstaller 6.16.0 vs 6.22.3；把 2 行日志当 26/26 证据；引用不存在的 `closure-matrix.json` | 左列各文件行（同一指标两处不同值） | 全部数字以入库日志为准重写；`CS-E2` 描述改为"记录实测 SHA256（无期望值）"；补回或删除断链引用 | open |
| R-007 | P3 | `core_sidecar.spec:271-285`（依赖 System32 `icuuc.dll`）；`REPORT.md:52,157`；Task:41 | 修复后 Qt6Core 的运行期 ICU 完全由 OS 提供（`C:\Windows\System32\icuuc.dll`，Win10 1809/1903+ 级别），这是**新增系统级依赖**，但 REPORT/Handoff/verification 未记录最低 OS 依赖、未做基线覆盖验证；缺失时故障模式由 127 变为模块级加载失败 | 诊断/修复证据全部来自单机 Windows 11 `10.0.26300`（`sidecar-build.log:6`） | 在 REPORT/Handoff 记录该 OS 依赖与受支持基线，并在声明的基线环境补充一次安装态验证（或显式声明支持范围） | open |

**无 P0。** P1（R-001、R-002）未解决 → 依 `doc/09_COLLABORATION.md:171` 与 `doc/templates/REVIEW.md`，本 head **不可 approved**。

## 7. Task AC 与 Handoff 状态对照

| AC | Owner 记录 | 本 Review 判定（基于提交内证据） |
|---|---|---|
| AC-1 | [x] 达成（REPORT:14-32、`icu-closure-matrix.json`） | **BLOCKED / NOT_RUN**：汇总 JSON 存在，但无扫描 artefact、无 UNKNOWN 保留、引用断链（R-003） |
| AC-2 | [x] 达成（EXIT 0 / 1.01s） | **部分 PASS**：改动仅在 `packaging/m2ac5/**`；隔离加载的实质由 packaged AC1 循环佐证，但 1.01s 对照无 artefact（V-13），且佐证运行绑定到非交付 installer |
| AC-3 | [x] 达成（368.6s / 340.0s，指纹绑定） | **FAIL**：`source_head` 绑定不成立、日志耗时与报告不符（R-002/R-006） |
| AC-4 | [x] 达成（10/10 Gate、13/13 probe、26.8s） | **PASS（内容）/ 绑定受限**：入库存根完整、15/7 命令精确一致；HEAD=`df824182`（R-002） |
| AC-5 | [x] 达成（26/26、minor1.6/请求3、双轮/PID/digest） | **BLOCKED**：交付 installer 无完整 26 项证据（R-001） |
| AC-6 | [x] 达成（Z1/Z2/Z3/Z4） | **PASS（对该次运行）**：断言逻辑与 JSON 一致（V-15） |
| AC-7 | [ ]（待 DSH Review + Codex 集成） | **NOT_RUN**：本 Review 不批准；DSH 未自审、未审核 Codex 工作、未批准任何越范围改动 |

Handoff 记录 `ready_for_review`、Task `in_review` + `CHECKPOINTED`，与"待非作者 Review"一致；**但 Handoff §2 与 Task 的 AC 表述把上述 P1 问题写成 PASS，属 09 §6.12③"不得把 NOT_RUN/BLOCKED 写成通过"的口径问题**，需随 R-001/R-002/R-006 一并修订。

## 8. 结论与复审

- **该 head 暂不可交 Codex 集成（decision=changes_requested）**，理由是 R-001/R-002 两个 P1：**关键验证（交付 installer 的 26 项）与来源绑定（source_head 与提交）在提交内不成立**。
- 代码方向本身无 P0/P1 级架构缺陷：范围最小、纯新增、PATH 为进程局部且在 `finally` 恢复、TOC 过滤位置正确。若 Codex 按 09 §6.9-6.11 走"先集成、再在集成 commit 上 fresh 构建 + 完整 26 项重跑"的路径，**R-002 可由集成后重跑闭合；R-001 必须在同一轮用交付 installer 的完整日志闭合**；R-003/R-004/R-005 应在同一轮补齐（扫描 artefact、来源判定的过滤/断言）。推荐执行者：**Owner=Antigravity**（在其 worktree 固定新 head 重跑并补 artefact），或 **Integrator=Codex** 在集成后统一重跑并入库；二者均须由 DSH 对新 head 复审（复审仅追加新 head 与 findings disposition，不抹除本记录）。
- **复审前仍存在的风险**：① 交付 installer 与已验证 installer 的差异性质未知（可能仅时间戳，也可能含实质差异）；② ICU78 消费者问题在可复核 artefact 层面仍为 UNKNOWN，而当前实现以"整包名称移除"承担该风险；③ 无 Windows 基线矩阵验证，System32 ICU 依赖未固化；④ 无法运行 git，worktree 是否存在未提交改动未排除，集成前请 Codex 以 `git status` 与 `git diff --name-only 5a72db9e..<head>` 复核范围与 clean 状态。
- 本 Review 仅输出报告，未修改任何仓库文件；报告落位与后续派发由 Codex 负责。
