# M2-PACKAGED-AC1-DLL-DIAG 诊断报告（DSH / Owner）—— r2：本地隔离执行证据整合版

- Task: `M2-PACKAGED-AC1-DLL-DIAG`（research/只读诊断）；Owner=DeepSeek Harness；非作者 Reviewer/Integrator=Codex。
- branch `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`；原 base `9063c317937b86bed1f6ff3e2f2c5d224dc10553`；source_head `cfb5d2ee`；installer SHA 原 pin `1cecca95…ccb8`。
- 本轮固定证据 HEAD = `a84980c394ac9c5380c87e097e081065818aa265`（clean）；执行侧证据分布于 Codex 提交：icu-control/symbol-full-exports `13804524`、loader-probe `36765f4b`、loader-system-icu-control `5cd31dda`。
- **执行者 = Codex**（本机隔离执行，自有 lab/fixture）；**DSH 沙箱 shell 仍 NOT_RUN**（Win32 5），本轮 DSH 只做只读核对与报告更新，不重跑、不改产品。
- 保留：原 runner 日志与 r1 版本的 raw/NOT_RUN 记录**原文未改动**；本版为 r1 内容 + 本地实测证据的更新版（r1 历史结论见 §9）。

## 1. 执行环境与命令（执行者 Codex）

| 项 | 值 |
|---|---|
| shell/host | Codex 本机 Windows 隔离执行；外层 wrapper EXIT0（`raw/static-c9e26f6f45.log`、`raw/copy-5be2e006d8.log`） |
| 子进程 env（对照） | `PATH=C:\WINDOWS/System32;C:\WINDOWS`、`PATHEXT` 显式、`M2AC1_TEST_MODE=1`、`QT_QPA_PLATFORM=offscreen`、`APPDATA/LOCALAPPDATA/TEMP/TMP/NEWMANGA_DATA_ROOT` 全部指向自有 lab |
| stdin | `DEVNULL`（EOF） |
| 原 case | 同 hash 桥副本 `acceptance_bridge.exe` **EXIT1 / 0.8s**，QtGui 导入错误复现 |
| 反事实 case | 自有新副本仅把包内 `icuuc.dll` **改名保留字节**（`icuuc.dll.diagnostic-preserved`），同 env → 桥初始化 **EXIT0 / 0.42s** |

**纪律**：外层 wrapper EXIT0 **不等于** bridge PASS；bridge 实测 EXIT1 才是被测事实。反事实对照只在自有 lab 副本上做，**不是**安装态 Gate，也**不是**完整 26 项 PASS。

## 2. 根因结论（PROVEN，范围限定）

**包内 `_internal/icuuc.dll` 遮蔽 System32 的同名 ICU，且其导出仅带 `_78` 版本后缀，缺少 `Qt6Core.dll` 所要求的 20 个无后缀 ICU 符号；Qt6Core 因此加载失败（native WinError 127），进而 `import PySide6.QtGui` 抛 ImportError。**

限定范围：**本固定 installer 产物 + 本机**。不等于 Gate 修复，不推广到其它构建/环境。

## 3. 证据链（每项标注执行者与判定）

| # | 证据 | 内容 | 判定 |
|---|---|---|---|
| E1 | `raw/loader-probe.log`（Codex，HEAD 36765f4b） | 同 hash `Qt6Core.dll`/`Qt6Gui.dll`/`pyside6.abi3.dll`/`QtCore.pyd`/`QtGui.pyd` → `loaded:false, WinError 127`（找不到指定的程序，**符号**级，非 126 模块级）；`shiboken6.abi3.dll`、包内 `icuuc.dll` 可加载 | PROVEN |
| E2 | `raw/loader-system-icu-control.log`（Codex，HEAD 5cd31dda） | 独立进程预加载 `System32/icuuc.dll` 后，**同 hash** Qt6Core/Qt6Gui 可加载，native `GetProcAddress` 命中 2 个样本符号 | PROVEN（环境对照） |
| E3 | `raw/symbol-probe-full-exports.json`（Codex，HEAD 13804524，`max_symbol_exports=100000`） | Qt6Core → `icuuc.dll` `imported:20`、`missing_symbols` = 20 个**无后缀** `ucnv_*`/`UCNV_*`；包内 icuuc `exported_names:3027` | PROVEN |
| E4 | `raw/binary-version-origin.json`（Codex） | `icuuc.dll` SHA `39aec884…` 在 lab 与 installed **同一 hash**，导出仅 `ucnv_open_78` 等 6 个 `_78` 名；Qt6Core/Qt6Gui SHA 在 lab/installed/build_env **三方一致**，FileVersion 6.11.2.0 | PROVEN（未被改动、三树一致） |
| E5 | `raw/icu-control-result.json` + `icu-control-original.log` / `icu-control-owned_icu_renamed.log`（Codex） | 同 hash EXE 断言（对齐 build-fingerprint `acceptance_bridge.exe` SHA）、同 env：原 case EXIT1+QtGui 错误；仅改名包内 icuuc（保留字节）→ EXIT0 | PROVEN（因果对照） |
| E6 | `run_icu_control.py` 逻辑（DSH 只读核对） | 断言副本位于自有 `lab/`、校验源 icuuc 与 EXE hash、env 全 pin 到 lab、stdin EOF、只 rename 不删字节 | 逻辑成立 |

差异说明：E1 的 WinError **127** 是本次 native 复现读到的错误码；**原 runner 日志仍无 GetLastError 记录**，故"原 Gate 运行时的 Win32 码"依旧 **UNKNOWN**，不得回填为 127。

## 4. DSH 对 Codex 支持 probe 的独立核对与局限

- `run_icu_control.py`：逻辑成立（断言、hash 门、env 隔离、EOF、字节保留式改名）。**局限**：反事实是"移除包内 icuuc"而非"提供可用 ICU78"；只 2 个 case、单次运行；`timeout=20s`；env 未含 `ComSpec`/`SystemDrive`（与 `run_local_probe.py` 的 env 不完全一致）；对照对象是 lab 副本，**未在 installed 树上做同名对照**。
- `loader_probe.py`：`ctypes.WinDLL` + 显式 `dll_dirs`（`_internal`、`_internal/PySide6`、`_internal/shiboken6`），`GetProcAddress` 由 `kernel32` 取得。**局限**：宿主是 `T1.1.1-impl-py312` 的 `python.exe`，**不是**冻结 PyInstaller 进程；"预加载 System32 ICU"是人为构造的对照环境，非原 purged PATH Gate。
- `symbol_probe.py`：`pefile` 静态导入表符号匹配（`max_symbol_exports=100000`），JSON 自带 "no loader search/forwarder claim"。**局限**：不解析 API-set/forwarder 语义，不做真实加载；**delay-import 扫描未独立验证**，故本轮根因**只用普通 imports + native 加载 + 同桥因果链**，不引用延迟导入零项结论（我上一轮自建 `probe/pe_import_probe.py` 的 delay 解析同样未经独立验证，一并排除）。
- 结论：Codex 支持 probe 的**数据**与**逻辑**经只读核对自洽，且相互独立（静态符号、native 加载、进程级因果）。但它们是**诊断支持证据**，不能当 Gate PASS，也不能替代安装态全量验收。

## 5. 证据勘误（ERRATUM）

- `raw/symbol-probe.json` 中"QtGui→QtCore 缺 64 个符号"是 **pefile 默认 8192 导出项上限造成的伪差**；`max_symbol_exports=100000` 并断言完整名称数后该 64 项**全部消失**，native `GetProcAddress` 也确认两个样本符号存在。**不得**作为根因或缺陷证据。
- 初次 wrapper 路径预检失败（EXIT1，未启动子进程）与初次 static 子环境缺 `PATHEXT` 导致 step6 失败：**原记录保留**，补齐子进程识别环境后另行重跑并独立记录；不作为结果。
- 上一轮 r1 遗留的"Win32 126 高置信"表述已作废（原日志无 GetLastError），改记具体错误码 **UNKNOWN**；本轮新增的 127 属**独立 native 复现**，仅支撑机制，不回填原 Gate。

## 6. 矩阵更新摘要（详见 `dll-closure-matrix.json`）

- C11（真正失败模块）UNKNOWN → **PROVEN：包内 icuuc 的 ICU 符号缺失**（E1–E5）。
- C14（符号级错配）部分 UNKNOWN → **PROVEN 根因**：无后缀 `ucnv_*` 需求 vs 仅 `_78` 导出。
- C13（搜索路径）UNKNOWN → **PROVEN 相关性**：包目录（`_internal`）先于 System32 命中同名 `icuuc.dll`，形成遮蔽。
- C8（`icuin*` 未见）/C9（`d3dcompiler_47`）/C10（`opengl32sw`）：维持"未在枚举树观察到 / 影响 UNKNOWN"，**未参与**本根因。
- C12（安装态完整性）：Qt6Gui/Qt6Core/icuuc 在 lab 与 installed **hash 一致**（E4）→ 这几个关键文件落盘完整；installed 树的 bridge 级对照未做 → 仍**部分 UNKNOWN**。

## 7. UNKNOWN / 未覆盖（不得越界）

1. 原 Gate 运行时的 Win32 错误码（原日志无 GetLastError）。
2. installed 树上未做改名对照；未在真正的 purged-PATH 安装态复跑。
3. 除 Qt 外**还有哪些依赖需要包内 ICU78**：未核实 → **禁止全局删除 ICU78**。
4. 完整 26 项 clean-start Gate、Tauri 打包验收：**未跑**。
5. DSH 自身无法验证 git/HEAD/clean/installer hash（shell NOT_RUN）——上述由 Codex 实测并记录，DSH 只做只读核对。

## 8. 最小拟议修复范围（未实施、未释放）

- 下一 Task 建议：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX`（**未创建/未释放**；须由用户/Codex 冻结）。
- 建议 Owner：Antigravity 或 ZCode；非作者 Reviewer：DSH。
- 建议 allowed_paths：`packaging/m2ac5/**` + 该 Task 自己的 `verification/**`；**先冻结再动手**。
- 方向（只给范围不给实现）：让包内 ICU 不再遮蔽系统 ICU，或确保包内 ICU 提供 Qt 所需的无后缀符号；**必须保护其它仍需要 ICU78 的依赖**（第 7.3 条）并保持原 purged-PATH 语义。
- 若必须改依赖版本/共享契约 → **先交用户裁决**；本 Task 不启动任何修复。
- 完成后 Gate：fresh Sidecar + NSIS → 固定 installer SHA → 全新 clean-start **完整 26 项** → 非作者 Review → Codex 集成验证。

## 9. AC 状态（执行者标注）与历史保留

- AC1 输入固定：installer 与 5 个 exe hash 由 **Codex 实测匹配**（`local-evidence.md:4`）→ 达成（executor=Codex）；DSH 侧 git/hash 复测 NOT_RUN。
- AC2 有界复现：自有 lab 同 hash 副本 **bridge EXIT1 / 0.8s** + QtGui 错误复现 → 达成（executor=Codex，E5/E1）。
- AC3 矩阵：候选逐项 PROVEN/REJECTED/UNKNOWN 已按本轮证据更新，含勘误 → 达成。
- AC4 环境差量与最小范围：原 full build/weights 差量 + 本轮 env/stdin 对照 + 最小修复范围 → 达成。
- AC5：待 **Codex 非作者 Review + 文档集成**；本轮 DSH **不自审、不 done**。
- 历史：r1 版本的 REPORT 结论（含其被修正的 126 表述）与全部原 raw 日志保留在仓库历史/`raw/` 中；本版取代 r1 作为可审查报告。
