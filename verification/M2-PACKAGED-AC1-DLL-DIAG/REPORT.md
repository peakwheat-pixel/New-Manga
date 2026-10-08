# M2-PACKAGED-AC1-DLL-DIAG 诊断报告（DSH / Owner）

- Task: `M2-PACKAGED-AC1-DLL-DIAG`（kind=research，只读诊断，不修复）
- Owner: DeepSeek Harness；非作者 Reviewer / Integrator: Codex
- branch: `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`
- base: `9063c317937b86bed1f6ff3e2f2c5d224dc10553`
- 指令记载 start_head: `24e0ec6e5c6d64a35daad006565919818616b317`（expectation，本次未能用 git 实测，见 AC1）
- 冻结输入：source_head `cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2`；runner 证据 head `15cd788f10e83f6a1a215e71538bfa175b435785`
- installer（只读，未改动）：`G:\CODEX\New Manga.worktrees\RUNNER-SNAPSHOT-DEBT-codex\apps\desktop\src-tauri\target\release\bundle\nsis\m2rc1-desktop_0.1.0_x64-setup.exe`
  SHA256 `1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8`，589904619 bytes
- 时间：2026-10-08（本会话）；所有命令级证据见 `raw/exec-20261008-dsh-notrun.log`

## 0. 执行限制（阻塞根因，先行声明）

本会话**无法执行任何 shell 命令**。`pwsh -Command` 每次都在启动前置阶段失败：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\PACKAGED-AC1-DLL-DIAG-dsh)
```

一次 `sandbox_permissions=danger-full-access` 升级重试被拒：`sandbox escalation ... requires approval, but no approval channel is available`。

因此本报告中的全部结论来自**只读文件工具**（读取已有日志、spec、脚本、构建产物目录清单）。
凡是需要"实际加载/实际执行/实际重新计算 hash"的项，一律记为 **NOT_RUN**，不填 PASS、不编造根因。
按指令第 43 行："静态扫描/文件存在不等于加载验证"——本报告严格遵守该界限。
已按要求创建可执行 probe（`probe/`），由 Codex 实跑后独立审查。

## 1. AC1 Reality Check

| 项 | 计划 | 实际 | 状态 |
|---|---|---|---|
| `git rev-parse HEAD` / branch / common-dir | 实测 | shell 不可用 | **NOT_RUN** |
| `git status --short --branch` clean | 实测 | shell 不可用 | **NOT_RUN** |
| `git diff --check` | 实测 | shell 不可用 | **NOT_RUN** |
| installer SHA256 复测 | `Get-FileHash` | shell 不可用 | **NOT_RUN** |
| installer 路径/字节/哈希一致性（文档互证） | — | `input-manifest.json` ≡ `build-fingerprint.json` ≡ `release.md`（三者同哈希/同字节/同路径，已只读比对） | 文档级 PROVEN |
| 冻结输入未漂移 | — | 本 Task 目录内 4 个文件与 Task doc 引用一致 | PROVEN |

环境事实（来自既有日志，非本会话实测）：Windows 11 `10.0.26300`；Python `3.12.3`；
PyInstaller `6.22.3`（contrib hooks `2026.7`）；构建 venv `G:/CODEX/New Manga.task-envs/m2ac5-build`；
`PySide6_Essentials==6.11.2`、`shiboken6==6.11.2`（互等，排除二者版本错配）。

## 2. AC2 原失败与有界复现

- 原始失败证据（只读重读，原文）：`raw/packaged/cleanstart-ac1-run1-stdout.log`
  - `exit=1`；`M2AC1_TEST_MODE=1`，purged PATH；`[m2ac1-allowlist] ac1:...` 后：
    `File "bootstrap\acceptance_bridge.py", line 173, in assemble_acceptance_core`
    `ImportError: DLL load failed while importing QtGui: 找不到指定的模块。`（日志中该中文为 mojibake）
  - `line 173` 正是 `src/bootstrap/acceptance_bridge.py:173` 的 `from PySide6.QtGui import QGuiApplication`。
- **PROVEN**：失败点在 `import PySide6.QtGui` 这条语句本身，**早于**第 175 行 `QGuiApplication([...])` 构造。
  故 "Qt platform plugin (qoffscreen/qwindows) 加载失败" 一类根因与本次 traceback 行号不符 → **REJECTED**（就本错误而言）。
- `ImportError: DLL load failed while importing ...` + `找不到指定的模块`(Win32 126, ERROR_MOD_NOT_FOUND)
  语义上指向：被 import 的扩展模块（`_internal/PySide6/QtGui.pyd`）或其依赖链（`Qt6Gui.dll`/`Qt6Core.dll`/`pyside6.abi3.dll`/`shiboken6.abi3.dll`/MSVC runtime/ICU）中有模块在加载时解析不到。
- 本会话复现：**NOT_RUN**（无 shell）。已有 1 次失败运行，`result-summary.json` 记 CS-A1-run1 FAIL、其余 5 项 NOT_RUN。
- **未覆盖的证据缺口（重要）**：证据集中**没有已安装树的 `_internal` 文件清单**。
  `cleanstart-gate.json` CS-I1 只证明安装目录存在 4 个 exe（`resources/core-sidecar/*.exe`）。
  即"NSIS 安装是否把 `_internal/**`（Qt DLL）完整落到安装目录"为 **UNKNOWN**。
  probe 第 2/3 步专门补这个缺口。

## 3. AC3 DLL / closure 矩阵

机器可读版：`dll-closure-matrix.json`；表内证据列均为仓库相对路径的原文行号。

| # | 候选 | 观测（静态实测） | 判定 | 置信度 |
|---|---|---|---|---|
| C1 | `QtGui.pyd` 未被打进包 | 存在 `_internal/PySide6/QtGui.pyd` | **REJECTED**（文件存在） | 高 |
| C2 | `Qt6Gui.dll` 缺失 | 存在 `_internal/PySide6/Qt6Gui.dll` | **REJECTED** | 高 |
| C3 | `Qt6Core.dll` 缺失 | 存在 `_internal/PySide6/Qt6Core.dll` | **REJECTED** | 高 |
| C4 | PySide6 ABI 运行库缺失 | 存在 `_internal/PySide6/pyside6.abi3.dll`、`_internal/shiboken6/shiboken6.abi3.dll` | **REJECTED** | 高 |
| C5 | MSVC/CRT 运行库未随包 | 存在 `_internal/{msvcp140,MSVCP140_1,MSVCP140_ATOMIC_WAIT,VCRUNTIME140,VCRUNTIME140_1,VCRUNTIME140_THREADS,ucrtbase}.dll` + `api-ms-win-crt-*` | **REJECTED** | 高 |
| C6 | Qt 完全未进分析图（=ModuleNotFoundError 类） | 构建日志 239–243 行：acceptance 入口触发 `hook-PySide6` / `hook-shiboken6` / `hook-PySide6.QtCore` / `hook-PySide6.QtGui` | **REJECTED** | 高 |
| C7 | PyInstaller 构建被 weights 失败打断、产物不完整 | `sidecar-build.log:548-552` `COLLECT ... completed successfully` / `Build complete!`；`EXIT=1` 出现在其后 560–569 行（`Get-FileHash` CommandNotFound） | **REJECTED** | 高 |
| C8 | `icuin*.dll`（ICU i18n）未随包 | `_internal/` 顶层清单只有 `icudt78.dll`、`icuuc.dll`，**无任何 `icuin*`** | 缺失 PROVEN；**对 QtGui 加载的影响 UNKNOWN** | 缺失=高，影响=低 |
| C9 | `d3dcompiler_47.dll` 未随包 | 全 bundle `**/d3dcompiler*` = 0 命中 | 缺失 PROVEN；影响 **UNKNOWN**（Win11 System32 可能有同名系统副本，本次无法实测） | 缺失=高，影响=低 |
| C10 | `opengl32sw.dll` 未随包 | `_internal/` 顶层清单未见 | 缺失 PROVEN；影响 **UNKNOWN** | 同上 |
| C11 | 真正解析失败的模块（具体 DLL/导出符号） | 需实际加载或导入表解析，本会话不可执行 | **UNKNOWN** | — |
| C12 | 安装态 `_internal` 是否完整（NSIS 落盘/长路径/文件被丢） | 无安装树清单证据 | **UNKNOWN** | — |
| C13 | DLL 搜索路径/`AddDllDirectory` 差异 | 构建期 `PATH` 搜索目录含 `...\site-packages\PySide6`（`sidecar-build.log:186/324`）；运行期搜索集未实测 | **UNKNOWN** | — |
| C14 | Export/符号错配（ABI 不匹配） | `PySide6_Essentials==6.11.2` 与 `shiboken6==6.11.2` 同 pin，构建期无版本告警 | 二者错配 **REJECTED**；其他符号级错配 **UNKNOWN** | 中 |

结论（措辞严格）：**根因类别**高置信 = "packaged 进程内 `PySide6.QtGui` 依赖链存在 Win32 126 未解析模块"；
**具体是哪一个 DLL/符号，仍为 UNKNOWN**。不从 `QtGui` 模块名倒推 DLL 名。

## 4. AC4 环境差量与最小范围

**PROVEN（原始日志原文）**：同一 `HEAD=cfb5d2ee...` 上有两次调用，环境不同：

| | full build | weights 恢复 |
|---|---|---|
| 命令 | `["powershell","-NoProfile","-File","packaging/m2ac5/build_sidecar.ps1","-Force"]` | `["C:/Program Files/PowerShell/7/pwsh.exe","-NoProfile","-File","packaging/m2ac5/build_sidecar.ps1"]`（**无** `-Force`） |
| 日志 | `raw/sidecar-build.log` | `raw/sidecar-weights-retry.log` |
| 结果 | PyInstaller 6.22.3 成功（COLLECT+5 exe+closure assertion 全绿），随后 `Copy-MangaWeights` 抛 `Get-FileHash is not recognized as the name of a cmdlet...`，`EXIT=1; ELAPSED=417.3s` | `build_sidecar: target exists, skipping (use -Force to rebuild)` + manga/sfx weights sha256 校验通过，`EXIT=0; ELAPSED=0.8s` |

推论（PROVEN）：
1. 被安装的 5 个 exe 全部来自那次 `-Force` 的 PyInstaller 输出；PS7 重试走了 `build_sidecar.ps1:173` 的**增量短路**，只补 weights，**没有重建 exe**。
2. 因此 "weights 步骤 EXIT1 导致 exe 半成品" 不成立（C7 REJECTED）；EXIT1 的**唯一**已证后果是 weights 未随首次构建落盘，由第二次调用补齐。
3. AC4 原有表述（"PowerShell5 PyInstaller 成功、weights 失败，PS7 只恢复 hash/copy"）与日志**完全一致**。
4. `Get-FileHash` 在 `powershell.exe -NoProfile` 会话中不可用：这是 cmdlet 不可见（受限语言模式/模块路径）现象，**PROVEN**；
   "因为 ConstrainedLanguage 模式" 属解释性推断，日志未写 `$ExecutionContext.SessionState.LanguageMode`，记 **UNKNOWN**。

根因置信度：类别高（见 §3）；具体 DLL 低=UNKNOWN。
**最小拟议修复 allowed_paths（不实施，仅供另开 Task 冻结）**：
- 首选仅打包层：`packaging/m2ac5/core_sidecar.spec`（为 acceptance 入口补一段**显式 Qt/PySide6 二进制闭包断言**，与现有 `_assert_ml_closure` / `_assert_sfx_probe_closure` 同形制——目前 Qt 闭包**没有任何** build-time 断言，闭合缩小只能在 release 才暴露，这正是本次失败形态）、`packaging/m2ac5/build_sidecar.ps1`（幂等/可复测的闭包清单输出；修 `Get-FileHash` 调用点使其在 PS5.1/PS7 下都可诊断）、必要时 `packaging/m2ac5/requirements-build.txt`。
- **不建议**先动 `src/**`：无代码级证据支持（C14 未证）。
- 后续 fresh/full Gate 必须：fixed-head 重新 `-Force` 构建 → hash 固定 installer → 全新 clean-start 26 项完整跑 → 非作者 Review → Codex 集成验证。诊断完成**不**解除 runner debt。

## 5. AC5 交付与状态

- 已写：本 `REPORT.md`、`dll-closure-matrix.json`、`raw/exec-20261008-dsh-notrun.log`、`probe/**`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`。
- **未能 git 提交/`git diff --check`**：shell 不可用 → 交付处于**未提交状态**，`delivery_head` = 未固定（期望 `24e0ec6e...`，未实测）。由 Codex 导入证据。
- 产品/历史零差量：本会话只通过 `write`/`edit` 触及 `verification/M2-PACKAGED-AC1-DLL-DIAG/**` 与 `doc/handoffs/**`、`doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`；未触碰 `src/apps/tests/packaging`。**但 `git diff src apps tests packaging` 的机器级证明为 NOT_RUN**，不能自称已证明。
- AC1/AC2 = NOT_RUN（工具限制）；AC3 = 静态完成、含 UNKNOWN；AC4 = PROVEN（日志级）；AC5 = 部分完成、未固定 head。
- **本 Task 未 done、未自审、未批准**；runner debt 继续 blocked。
