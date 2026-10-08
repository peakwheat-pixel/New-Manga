# M2-PACKAGED-AC1-ICU-ISOLATION-FIX 验证报告（DSH r1/r2 修订版）

- **任务 ID**: `M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
- **Owner**: `Antigravity`
- **非作者 Reviewer**: `DeepSeek Harness`
- **Integrator**: `Codex`
- **Base Commit**: `5a72db9e3c5778ce4700b7d404250853e474c5de`
- **固定实现代码 Head (code_head)**: `4499217d7b2249da16d5dbf27a3219a43876aac7`
- **Owner 交付证据 Commit**: `2c79645939635beef4a391f4bd9071ffeacd300b`

---

## 1. DSH r1 审查意见关闭对照（R-001 ~ R-007）与边界准则闭环

| ID | 级别 | 核心问题 | 修订措施与关闭证据 | 状态 |
|---|---|---|---|---|
| **R-001** | **P1** | 交付 installer 与验收 installer 存在两份哈希，且旧 packaged 日志中断不可审计 | 在固定代码 HEAD `4499217d` 上重新 fresh 构建出唯一交付安装包（`f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`），随后由固定 runner 在其上完整重跑 26 项 Packaged Gate；`raw/packaged/cleanstart-gate.json` 与 `build-fingerprint.json` 哈希逐字节一致，入库带 EXIT 0 的完整日志。 | **CLOSED** |
| **R-002** | **P1** | 构建与验收发生在修复尚未提交前，`source_head` 绑定不成立 | 所有生产代码修订先行提交为 `4499217d`；随后 Sidecar 构建、NSIS 构建、Dev Gate、Packaged Gate 均在该固定 commit 上执行。全部日志首部实测输出 `GIT_HEAD: 4499217d7b2249da16d5dbf27a3219a43876aac7`，与 `build-fingerprint.json` 的 `source_head` 完全一致。 | **CLOSED** |
| **R-003** | **P2** | AC-1 缺少可复核 PE 扫描脚本与原始输出，矩阵未列动态加载边界，断链引用 | 新增 [`scan_pe_closure.py`](scan_pe_closure.py) 可复核扫描脚本；全量扫描 bundle 内 313 个 PE 二进制，生成原始输出 [`raw/pe-scan-raw.json`](raw/pe-scan-raw.json)；矩阵 [`icu-closure-matrix.json`](icu-closure-matrix.json) 与 [`closure-matrix.json`](closure-matrix.json) 均入库。各入口传递闭包与动态加载边界严谨标注为 `UNKNOWN`，全包结论限定为 313 个 PE 文件的直接静态导入事实。 | **CLOSED** |
| **R-004** | **P2** | 来源隔离与边界匹配过度泛化，全包无差别移除 ICU 违背最小处置原则 | 修改 `core_sidecar.spec` 中的 `_isolate_icu_closure`：使用边界安全路径检查 `_is_within_dir`；唯一已证实外部污染源严格限定为 external poppler 工具链 `Library\bin\icuuc.dll` 并核验 SHA256（`39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf`）；移除宽泛的 `dependencies\native` / `codex-runtimes` 匹配，未知外部 ICU 一律 fail-closed；保留 venv 与 repo 内部 ICU；`build_sidecar.ps1` 定向净化 poppler PATH。 | **CLOSED** |
| **R-005** | **P3** | spec 内 post-filter 断言判别力不足，PowerShell 断言覆盖与策略表述偏差 | 在 `core_sidecar.spec` 中重构可判别守卫断言（核查已证实污染源未泄漏，并在 COLLECT 前对 aggregated `all_binaries` 实施二次校验）；在 `build_sidecar.ps1` 中明确其全量 ICU 布局门禁为针对 System32 遮蔽风险的 fail-closed 策略约束，而非武断宣称未来永不需要 versioned ICU。 | **CLOSED** |
| **R-006** | **P3** | 报告耗时、PID、版本、哈希口径不一致，CS-E2 描述与 runner 不符 | 全部指标统一从现场日志重新生成：PyInstaller 版本固定为 `6.22.3`；PIDs 实测为 `[61404, 11828] -> [30296, 38904]`；CS-E2 判据修正为“验证安装包文件存在并记录实测 SHA256（无期望值比较判据）”。 | **CLOSED** |
| **R-007** | **P3** | 运行时依赖 System32 ICU 未记录 Windows 支持基线与受支持验证 | 显式记录目标桌面架构支持基线为 Windows 10 version 1809+ / Windows 11，其中 `C:\Windows\System32\icuuc.dll` 为标准 inbox 操作系统组件，Qt6Core 依此正常解析运行。 | **CLOSED** |

---

## 2. 闭包扫描与 ICU 消费者调查（AC-1）

- **扫描脚本**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/scan_pe_closure.py`](scan_pe_closure.py)
- **原始数据**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/pe-scan-raw.json`](raw/pe-scan-raw.json)
- **闭包矩阵**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/icu-closure-matrix.json`](icu-closure-matrix.json) 与 [`closure-matrix.json`](closure-matrix.json)
- **扫描结果与边界定义**:
  - 扫描了 bundle 内全部 **313 个 PE 二进制**（`.exe`, `.dll`, `.pyd`），解析异常数为 **0**（`parse_errors: 0`，全量解析干净）。
  - **静态导入事实**: 全包 313 个 PE 中，版本化 ICU78（`icu*78.dll`）静态导入数为 **0**；仅 `_internal/PySide6/Qt6Core.dll` 静态导入无后缀 `icuuc.dll`（由 Windows 系统库提供）。
  - **五大入口分析**:
    - `host_bridge.exe`, `core_service.exe`, `acceptance_bridge.exe`, `catalog_loader.exe`, `sfx_detect_probe.exe` 的直接静态与延迟导入表中均**无直接 ICU 依赖**（`direct_import_verdict: NO_DIRECT_ICU_IMPORTS`）。
    - 传递闭包结论（`transitive_closure_verdict`）：因静态扫描入口 PE 无法展开其子进程与动态加载的传递闭包，各入口传递消费者结论严谨标注为 **`UNKNOWN`**（其中 `acceptance_bridge.exe` 所在 bundle 包含 `Qt6Core.dll`，要求系统无后缀 `icuuc.dll`）。
    - 运行时动态边界（`dynamic_load_boundary`）：运行时反射、`ctypes.WinDLL`、`LoadLibrary` 等未在静态扫描中显式暴露，严谨标注为 **`UNKNOWN`**。不得让 `UNKNOWN` 与绝对的“无消费者”产生语义冲突。

---

## 3. 隔离加载因果对照（AC-2）

- **测试脚本**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/test_acceptance_bridge.ps1`](test_acceptance_bridge.ps1)
- **执行日志**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/acceptance-bridge-purged-path.log`](raw/acceptance-bridge-purged-path.log)
- **环境条件**:
  - `PATH = C:\Windows\System32;C:\Windows`（严格净化，无宿主外部工具链或 Python）
  - `M2AC1_TEST_MODE = 1`
  - `QT_QPA_PLATFORM = offscreen`
  - `stdin = EOF`（子进程立即读取 EOF 并正常退出循环）
- **实测结果**:
  - **EXIT Code**: `0`
  - **耗时**: `0.47s`
  - **因果对照**: 基线包含同名外来 `icuuc.dll` 时启动在 0.8s 报 `ImportError: cannot import name QtGui from PySide6`（底层 WinError 127，符号缺失）；隔离修复后包内无遮蔽文件，Qt6Core 加载系统 `C:\Windows\System32\icuuc.dll`，0.47s 完成初始化并随 stdin EOF 退出，EXIT 0。

---

## 4. Fresh 双构建与产物绑定（AC-3）

### 4.1 Sidecar Fresh 构建
- **命令**: `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force`
- **执行日志**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/sidecar-build.log`](raw/sidecar-build.log)
- **Git HEAD**: `4499217d7b2249da16d5dbf27a3219a43876aac7`
- **PyInstaller 版本**: `6.22.3`
- **耗时**: `347.60s`
- **EXIT Code**: `0`
- **构建防线输出**:
  - `build_sidecar: sanitized 1 confirmed alien toolchain entries from PATH for PyInstaller execution: [PATH-SANITIZED] C:\Users\49745\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin`
  - `build_sidecar: verified 0 shadowing ICU binaries across bundle layout under .../target/core-sidecar/core-sidecar (fail-closed guard satisfied)`

### 4.2 NSIS Fresh 构建
- **命令**: `npx.cmd --yes @tauri-apps/cli@2 build`（工作目录: `apps/desktop`）
- **执行日志**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/nsis-build.log`](raw/nsis-build.log)
- **Git HEAD**: `4499217d7b2249da16d5dbf27a3219a43876aac7`
- **Node 版本**: `v24.15.0`
- **耗时**: `326.82s`
- **EXIT Code**: `0`

### 4.3 产物指纹与 Hash 绑定（build-fingerprint.json）

| 产物 | 路径 | 大小 (字节) | SHA256 |
|---|---|---|---|
| **NSIS 安装包** | `apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe` | 579,525,817 (552.68 MiB) | `f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae` |
| `acceptance_bridge.exe` | `target/core-sidecar/core-sidecar/acceptance_bridge.exe` | 68,530,186 | `9e4a0068e153e376c02bf802435e9dbffe7442b014fee7e420197e50e4d7eae8` |
| `catalog_loader.exe` | `target/core-sidecar/core-sidecar/catalog_loader.exe` | 1,824,326 | `f0a59794fb6c6beefa49305506ec0e97b2e31adf4edf78c56a3b0f151c67bf6f` |
| `core_service.exe` | `target/core-sidecar/core-sidecar/core_service.exe` | 68,542,970 | `7a1a78525dae14ac862e2da518fc493c7993b0ffbbe953cebd42b5823d70e10a` |
| `host_bridge.exe` | `target/core-sidecar/core-sidecar/host_bridge.exe` | 1,826,431 | `6ca28abaf9ec0d1ba4e21a237b7d733f5c72b8d0fa4831e3051cf69efea346a2` |
| `sfx_detect_probe.exe` | `target/core-sidecar/core-sidecar/sfx_detect_probe.exe` | 67,902,901 | `f9b31287136e44262c37ce342ee663c0210a6a33090ba67533c3c0b40aaa9456` |

---

## 5. Dev Runner 验证（AC-4）

- **测试命令**: `python verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/run_e2e.py --exe apps/desktop/src-tauri/target/release/m2rc1-desktop.exe --skip-build --output-dir verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev`
- **解释器**: `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe` (`Python 3.12.3`)
- **执行日志**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev-gate-execution.log`](raw/dev-gate-execution.log) 与 [`raw/dev-e2e.log`](raw/dev-e2e.log)
- **耗时**: `19.37s`
- **EXIT Code**: `0`
- **结果**: **10/10 Gate PASS，13/13 Probe PASS**
  - 10 Gate: `environment`, `lab`, `catalog-seeding`, `sidecar-import-isolation`, `runtime-build`, `probe-phase`, `probe-allowlist-announcement`, `sidecar-module-dump-probe`, `interactive-production-surface`, `sidecar-module-dump-interactive` 全部 PASS。
  - 13 Probe: `E-00` 到 `E-09`、`D-01` 到 `D-03` 全部 PASS。
  - 严格核对：15 production commands 与 7 probe commands 逐条严格匹配。

---

## 6. Packaged Clean-Start 验证（AC-5）

- **测试命令**: `python verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/run_clean_start_e2e.py --installer apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe --output-dir verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged`
- **解释器**: `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe` (`Python 3.12.3`)
- **被测 Installer SHA256**: `f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`（与 fingerprint 严格一致）
- **执行日志**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged-gate-execution.log`](raw/packaged-gate-execution.log) 与 [`raw/packaged-e2e.log`](raw/packaged-e2e.log)
- **Gate 数据**: [`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged/cleanstart-gate.json`](raw/packaged/cleanstart-gate.json)
- **耗时**: `131.13s`
- **EXIT Code**: `0`
- **结果**: **GATE: PASS（26/26 项场景全部通过）**

### 26 项场景逐项清单
- **Phase 0: Environment & Path Purge**
  - `CS-E1-python-purged-from-path`: **PASS**（purged PATH 下无 python）
  - `CS-E2-installer-present`: **PASS**（验证安装包文件存在并记录实测 SHA256 `f2a4e2e7...`，无期望值比较判据）
  - `CS-E3-install-path-no-spaces`: **PASS**
- **Phase 1: Silent Install & Loader**
  - `CS-I1-silent-install`: **PASS**（安装至隔离临时目录，5610 文件）
  - `CS-I2-catalog-seeded-packaged-loader`: **PASS**（packaged catalog_loader.exe 种子注入成功，5 行）
- **Phase 1.5: Packaged Library Sidecar Probe**
  - `CS-L1-packaged-core-ping`: **PASS**（协议响应 `major: 1, minor: 6`，与请求 `minor: 3` 兼容）
  - `CS-L2-packaged-ListBooks-structure`: **PASS**
  - `CS-L3-packaged-core-shutdown`: **PASS**
- **Phase 2: Probe Mode (Resource Channel)**
  - `CS-P1-probe-results-written`: **PASS**
  - `CS-P2-probe-scenarios-all-pass`: **PASS**（13 场景全绿）
  - `CS-P3-sidecar-roundtrip-digest`: **PASS**（digest 逐位一致）
- **Phase 3: AC1 Acceptance Loop (两轮全闭环)**
  - `CS-A0-ac1-catalog-prebind`: **PASS**
  - `CS-A1-run1-completed`: **PASS**（第一轮完成，退出码 0）
  - `CS-A1-run2-completed`: **PASS**（第二轮完成，退出码 0）
  - `CS-A2-restart-new-pids`: **PASS**（run1 PIDs: [61404, 11828] -> run2 PIDs: [30296, 38904]，完全换新 PID）
  - `CS-A3-saved-summary-complete`: **PASS**（2 页处理，mock-ocr/translate 闭环）
  - `CS-A4-restored-reader-matches-saved`: **PASS**（重启后 reader 成功恢复）
  - `CS-A5-export-png-digest-matches`: **PASS**（PNG 导出哈希匹配）
- **Phase 4: Production Mode**
  - `CS-R1-production-process-alive`: **PASS**
  - `CS-R2-userdata-layout-created`: **PASS**（隔离 APPDATA 正常创建）
  - `CS-R3-production-surface-announced`: **PASS**
  - `CS-R4-no-spawn-failures-in-log`: **PASS**
- **Phase 5: Zero-Touch Assertions (AC-6)**
  - `CS-Z1-install-dir-zero-write`: **PASS**（安装目录只读，运行前后 0 变更）
  - `CS-Z4-host-real-appdata-untouched`: **PASS**（真实宿主 %APPDATA% 零触碰，4 文件完好）
  - `CS-Z2-user-source-files-byte-identical`: **PASS**（用户源文件 4 个字节完全一致）
  - `CS-Z3-no-surviving-sidecar-processes`: **PASS**（全部 4 个 sidecar 进程残留计数为 0）

---

## 7. 系统级依赖与 Windows 支持基线说明（R-007）

- **声明支持基线**: Windows 10 version 1809+（OS Build 17763+）以及 Windows 11。
- **系统依赖**: `C:\Windows\System32\icuuc.dll` 为 Windows 10 1809+ 起内置的官方操作系统组件，共有 542 个无后缀导出，其中包含 Qt6Core 所需的 20 个 `ucnv_*` 符号。
- **运行依赖机制**: 新架构采用 React + TypeScript + Tauri v2。Tauri 依赖宿主 WebView2（在 Windows 10/11 均为系统标配），Sidecar 内 PySide6 (Qt 6.8+) 动态链接到系统 `System32\icuuc.dll`。修复后包内消除了外来同名 ICU78 遮蔽，运行时顺利由操作系统内核供给，符合已声明的 Windows 支持基线承诺。
