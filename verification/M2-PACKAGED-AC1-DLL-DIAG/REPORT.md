# M2-PACKAGED-AC1-DLL-DIAG 诊断报告（DSH / Owner）—— r1 返修版

- 本版按 Codex 非作者 Review r1（`doc/reviews/M2-PACKAGED-AC1-DLL-DIAG-f0ad317c-codex-r1.md`）修正 R1/R2/R3；
  **R1 轮原始最终回答与其 NOT_RUN 日志原文保留、未改写**（`raw/exec-20261008-dsh-notrun.log` 未变动）。
- r1 draft head（Codex 提交、本次返修起点）：`f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50`
- Task: `M2-PACKAGED-AC1-DLL-DIAG`（kind=research，只读诊断，不修复）
- Owner: DeepSeek Harness；非作者 Reviewer / Integrator: Codex
- branch: `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`
- base: `9063c317937b86bed1f6ff3e2f2c5d224dc10553`
- 指令记载 start_head: `24e0ec6e5c6d64a35daad006565919818616b317`（expectation，未能用 git 实测，见 AC1）
- 冻结输入：source_head `cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2`；runner 证据 head `15cd788f10e83f6a1a215e71538bfa175b435785`
- installer（只读，未改动）：`G:\CODEX\New Manga.worktrees\RUNNER-SNAPSHOT-DEBT-codex\apps\desktop\src-tauri\target\release\bundle\nsis\m2rc1-desktop_0.1.0_x64-setup.exe`
  SHA256 `1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8`，589904619 bytes

## 0. 执行限制（阻塞根因，先行声明）

本会话**无法执行任何 shell 命令**。`pwsh -Command` 每次都在启动前置阶段失败：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\PACKAGED-AC1-DLL-DIAG-dsh)
```

`sandbox_permissions=danger-full-access` 升级重试被拒：`requires approval, but no approval channel is available`。
按 r1 指示，本轮**不再重复权限尝试**：本轮全部实跑项仍为 **NOT_RUN**。

全部结论来自**只读文件工具**（读取已有日志、spec、脚本、构建产物目录清单）。
需要"实际加载/执行/重新计算 hash/读取 GetLastError"的项一律 **NOT_RUN**，不填 PASS、不编造根因。

## 1. AC1 Reality Check

| 项 | 计划 | 实际 | 状态 |
|---|---|---|---|
| `git rev-parse HEAD` / branch / common-dir | 实测 | shell 不可用 | **NOT_RUN** |
| `git status --short --branch` clean | 实测 | shell 不可用 | **NOT_RUN** |
| `git diff --check` / `git diff <base> HEAD -- src apps tests packaging` | 实测 | shell 不可用 | **NOT_RUN** |
| installer SHA256 复测 | `Get-FileHash` | shell 不可用 | **NOT_RUN** |
| installer 路径/字节/哈希互证 | — | `input-manifest.json` ≡ `build-fingerprint.json` ≡ `release.md`（同哈希/同字节/同路径，只读比对） | 文档级 PROVEN |
| r1 draft head 引用 | — | 采用 Review r1 记录的 `f0ad317c...`（**未用 git 实测**） | 引用级 |

环境事实（来自既有日志，非本会话实测）：Windows 11 `10.0.26300`；Python `3.12.3`；
PyInstaller `6.22.3`（contrib hooks `2026.7`）；构建 venv `G:/CODEX/New Manga.task-envs/m2ac5-build`；
`PySide6_Essentials==6.11.2`、`shiboken6==6.11.2`（互等，排除二者版本错配）。

## 2. AC2 原失败与有界复现

- 原始失败证据（只读重读，原文）：`raw/packaged/cleanstart-ac1-run1-stdout.log`
  - `exit=1`；`M2AC1_TEST_MODE=1`，purged PATH；`[m2ac1-allowlist] ac1:...` 后：
    `File "bootstrap\acceptance_bridge.py", line 173, in assemble_acceptance_core`
    `ImportError: DLL load failed while importing QtGui: 找不到指定的模块。`（日志中该中文为 mojibake）
  - `line 173` 正是 `src/bootstrap/acceptance_bridge.py:173` 的 `from PySide6.QtGui import QGuiApplication`。
- **PROVEN（事实层面）**：失败点在 `import PySide6.QtGui` 这条语句本身，**早于**第 175 行 `QGuiApplication([...])` 构造。
  故 "Qt platform plugin (qoffscreen/qwindows) 加载失败" 一类根因与本次 traceback 行号不符 → **REJECTED**（就本错误而言）。
- **R3 修正**：原日志**只有 CPython 的 `ImportError` 文本，没有任何 `GetLastError()` / Win32 错误码记录**。
  因此 **具体 Win32 错误码 = UNKNOWN**；本报告不再写"Win32 126 / ERROR_MOD_NOT_FOUND"，也不以该编码支撑高置信结论。
  仅可陈述日志原文：导入 `PySide6.QtGui` 时扩展模块加载失败，且失败信息为本地化的"找不到指定的模块"。
  该文本指向"某依赖模块在加载期无法解析"只是**待验证的推断（UNKNOWN/medium）**，不是已测事实。
- 本会话复现：**NOT_RUN**（无 shell）。已有 1 次失败运行，`result-summary.json` 记 CS-A1-run1 FAIL、其余 5 项 NOT_RUN。
- **未覆盖的证据缺口（重要）**：证据集中**没有已安装树的 `_internal` 文件清单**。
  `cleanstart-gate.json` CS-I1 只证明安装目录存在 4 个 exe。故"NSIS 是否把 `_internal/**`（Qt DLL）完整落盘"为 **UNKNOWN**。
  probe 步骤 2/3 分别只做"构建产物树扫描"与"安装树扫描"，两者都**只是文件是否存在于被扫描目录**，
  **都不等于可加载**，也都**不能**由一方缺席推证另一方缺席。

## 3. AC3 DLL / closure 矩阵

机器可读版：`dll-closure-matrix.json`。

> **矩阵作用域声明（R3）**：下表"PRESENT/未列出"全部是**对特定被扫描目录树的一次静态文件枚举结果**，
> 仅证明"在被扫描的那棵树里是否存在该文件名"。它**不证明**安装态是否存在、**不证明** Windows Loader
> 能否解析、**不证明**实际加载成功或失败。枚举工具存在路径数上限，故"未列出"≠"完整证明不存在"。

| # | 候选 | 观测（静态实测，限被扫描树） | 判定 | 置信度 |
|---|---|---|---|---|
| C1 | `QtGui.pyd` 未被打进包 | 构建产物树中有 `_internal/PySide6/QtGui.pyd` | 该树中不存在此问题（≠安装态结论） | 中 |
| C2 | `Qt6Gui.dll` 缺失 | 构建产物树中有 `_internal/PySide6/Qt6Gui.dll` | 同上 | 中 |
| C3 | `Qt6Core.dll` 缺失 | 构建产物树中有 `_internal/PySide6/Qt6Core.dll` | 同上 | 中 |
| C4 | PySide6 ABI 运行库缺失 | 构建产物树中有 `pyside6.abi3.dll`、`shiboken6/shiboken6.abi3.dll` | 同上 | 中 |
| C5 | MSVC/CRT 运行库未随包 | 构建产物树中有 `msvcp140/MSVCP140_1/MSVCP140_ATOMIC_WAIT/VCRUNTIME140/VCRUNTIME140_1/VCRUNTIME140_THREADS/ucrtbase` + `api-ms-win-crt-*` | 同上 | 中 |
| C6 | Qt 完全未进 PyInstaller 分析图 | 构建日志 239–243 行触发 `hook-PySide6` / `hook-shiboken6` / `hook-PySide6.QtCore` / `hook-PySide6.QtGui` | **REJECTED**（构建期事实，日志级） | 高 |
| C7 | 构建被 weights 阶段 EXIT=1 截断、产物不完整 | `sidecar-build.log:548-552` `COLLECT ... completed successfully` / `Build complete!`；`EXIT=1` 在其后 560–569 行（`Get-FileHash` CommandNotFound） | **REJECTED**（日志级） | 高 |
| C8 | `icuin*.dll` 未出现在构建产物树 | 只读到 `icudt78.dll`、`icuuc.dll`，未见 `icuin*` | **该树未见**；对安装态与加载的影响 **UNKNOWN** | 未见=中，影响=低 |
| C9 | `d3dcompiler_47.dll` 未出现在构建产物树 | `**/d3dcompiler*` 0 命中 | 同上（Win11 System32 可能有系统副本，未实测） | 同上 |
| C10 | `opengl32sw.dll` 未出现在构建产物树 | 顶层 DLL 列表中未见 | 同上 | 同上 |
| C11 | 真正解析失败的模块（具体 DLL / 导出符号） | 需实际加载或 GetLastError 观测；不可执行 | **UNKNOWN** | — |
| C12 | 安装态 `_internal` 是否完整 | 无安装树清单证据 | **UNKNOWN** | — |
| C13 | 运行期 DLL 搜索路径差异 | 构建期搜索目录含 `...\site-packages\PySide6`（`sidecar-build.log:186/324`）；运行期未实测 | **UNKNOWN** | — |
| C14 | 符号级错配 | `PySide6_Essentials==6.11.2` 与 `shiboken6==6.11.2` 同 pin | 该二者错配 REJECTED；其他符号级 **UNKNOWN** | 中 |

结论（措辞严格）：**已证事实**仅为"packaged 运行的 `import PySide6.QtGui` 抛出 ImportError（日志原文）"。
"哪个依赖模块未解析、Win32 错误码是多少、是否与安装态落盘有关"全部 **UNKNOWN**；
具体根因不得从 `QtGui` 模块名或从构建树文件枚举倒推。

## 4. AC4 环境差量与最小范围

**PROVEN（原始日志原文）**：同一 `HEAD=cfb5d2ee...` 上有两次调用，环境不同：

| | full build | weights 恢复 |
|---|---|---|
| 命令 | `["powershell","-NoProfile","-File","packaging/m2ac5/build_sidecar.ps1","-Force"]` | `["C:/Program Files/PowerShell/7/pwsh.exe","-NoProfile","-File","packaging/m2ac5/build_sidecar.ps1"]`（**无** `-Force`） |
| 日志 | `raw/sidecar-build.log` | `raw/sidecar-weights-retry.log` |
| 结果 | PyInstaller 6.22.3 成功（COLLECT + 5 exe + closure assertion 全绿），随后 `Copy-MangaWeights` 抛 `Get-FileHash is not recognized as the name of a cmdlet...`，`EXIT=1; ELAPSED=417.3s` | `build_sidecar: target exists, skipping (use -Force to rebuild)` + weights sha256 校验通过，`EXIT=0; ELAPSED=0.8s` |

推论（PROVEN）：被安装的 5 个 exe 全部来自那次 `-Force` 的 PyInstaller 输出；PS7 重试走 `build_sidecar.ps1:173`
增量短路，只补 weights，**未重建 exe**。故 "weights EXIT1 导致 exe 半成品" 不成立（C7 REJECTED）。
`Get-FileHash` 在 `powershell.exe -NoProfile` 会话中不可用属 **PROVEN**；"因 ConstrainedLanguage" 属推断，记 **UNKNOWN**。

**最小拟议修复 allowed_paths（不实施，仅供另开 Task 冻结）**：
- 首选仅打包层：`packaging/m2ac5/core_sidecar.spec`（为 acceptance 入口补**显式 Qt/PySide6 二进制闭包断言**，
  与现有 `_assert_ml_closure` / `_assert_sfx_probe_closure` 同形制——目前 Qt 闭包**没有任何** build-time 断言）、
  `packaging/m2ac5/build_sidecar.ps1`、必要时 `packaging/m2ac5/requirements-build.txt`。
- **不建议**先动 `src/**`：无代码级证据支持。
- 后续 fresh/full Gate 必须：fixed-head 重新 `-Force` 构建 → 固定 installer hash → 全新 clean-start 26 项完整跑
  → 非作者 Review → Codex 集成验证。诊断完成**不**解除 runner debt。

## 5. AC5 交付与状态

- 已写：本 `REPORT.md`、`dll-closure-matrix.json`、`raw/exec-20261008-dsh-notrun.log`（r1 起未改动）、
  `probe/{run_dll_diag_probe.ps1,pe_import_probe.py,README.md}`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`。
- **未能 git 提交/`git diff --check`**：shell 不可用 → 交付处于**未提交状态**，本轮 head 由 Codex 记录。
  r1 draft head = `f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50`（引用，未实测）。
- 产品/历史零差量：本会话只触及 `verification/M2-PACKAGED-AC1-DLL-DIAG/**`、`doc/handoffs/**`、
  `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`；未触碰 `src/apps/tests/packaging`。
  **但机器级 diff 证明为 NOT_RUN**，不能自称已证明。
- AC1/AC2 = NOT_RUN（工具限制）；AC3 = 静态完成、含 UNKNOWN；AC4 = PROVEN（日志级）；AC5 = 部分完成、未提交。
- **本 Task 未 done、未自审、未批准**；`M2-RUNNER-SNAPSHOT-DEBT` 继续 blocked。

## 6. r1 返修记录（本轮）

- **R1（P1）**：`probe/run_dll_diag_probe.ps1` 步骤 1 改为 **fail-closed**——installer 缺失或 SHA256 漂移时
  `Say ... FAIL_CLOSED` 后 `throw`（非零退出），不再打印 BLOCKED/DRIFT 后继续。
- **R2（P1）**：步骤 4/5 重写——默认 **static-read-only**，不启动任何 exe；仅 `-CopyBundle` 时复制，
  且复制使用 **copy-only（`/E`，无 `/MIR`、无 PURGE，源树只读）**，复制 exit≥8 或 lab 内
  `acceptance_bridge.exe`/Qt6Gui.dll/Qt6Core.dll/pyside6.abi3.dll/shiboken6.abi3.dll 缺失或 SHA256 不一致时
  **立即停止、绝不从原 bundle 启动**；只有"复制成功 + lab 内已核验"才允许步骤 5 运行自有 lab 副本。
- **R3（P2）**：本 REPORT、`dll-closure-matrix.json`、Handoff 同步修正——具体 Win32 错误码记 **UNKNOWN**
  （原日志无 GetLastError），删除"126 高置信"表述；明确"某 DLL 未出现在枚举树"**不证明**安装态缺失，
  也**不证明**加载失败，并新增矩阵作用域声明。
- r1 原始最终回答与 NOT_RUN 日志**原文保留**；本轮未改 Plan/STATUS/索引，未新增框架或依赖。
