# M2-PACKAGED-AC1-ICU-ISOLATION-FIX 验收与验证报告

- 任务：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX`（安装态 Qt 与 ICU78 依赖闭包隔离修复）
- Owner: Antigravity
- 非作者 Reviewer: DeepSeek Harness
- Integrator: Codex
- Base Commit: `5a72db9e3c5778ce4700b7d404250853e474c5de`
- 分支：`agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
- 工作区：`G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`
- Git Common Dir: `G:/CODEX/New Manga/.git`

---

## 1. 调查与闭包分析（AC-1）

### 1.1 五大入口 ICU78 消费者排查矩阵

在修复实施前，对当前打包架构的 5 大入口及构建环境内全部二进制进行了系统性 PE 导入表与代码扫描：

| 入口程序 | 脚本 / 模块 | 实际二进制依赖 | 是否为实际 ICU78 消费者 | 证据与判定依据 |
|---|---|---|---|---|
| `host_bridge.exe` | `-m infrastructure.resource_channel.host_bridge` | 仅 Python 标准库 + in-repo 模块 | **否** | PE 导入表无任何 ICU 依赖；纯 Python 标准库，零 C 扩展。判定：`PROVEN_NOT_CONSUMER`。 |
| `core_service.exe` | `-m bootstrap.core_service` | SQLite, torch, torchvision, transformers, python-doctr, onnxruntime | **否** | 扫描全部 ML 依赖的 `.pyd`/`.dll`（包括 `torchvision/*.pyd`, `onnxruntime*.pyd`, `DirectML.dll`），均无任何 `icu*` 导入。判定：`PROVEN_NOT_CONSUMER`。 |
| `acceptance_bridge.exe` | `-m bootstrap.acceptance_bridge` | PySide6 (`QGuiApplication`), Qt6Core, Qt6Gui | **否** | `Qt6Core.dll` 导入表声明依赖无版本后缀的 `icuuc.dll`（Windows 10/11 系统内置组件，含 542 个无后缀符号）；**并非** ICU78 消费者。旧产物因包内混入第三方 ICU78 导致同名遮蔽。判定：`PROVEN_NOT_CONSUMER`。 |
| `catalog_loader.exe` | `-m infrastructure.resource_channel.catalog_loader` | Python 标准库 + sqlite3 | **否** | 纯标准库 + sqlite3，零外部 C 扩展。判定：`PROVEN_NOT_CONSUMER`。 |
| `sfx_detect_probe.exe` | `-m bootstrap.sfx_detect_probe` | onnxruntime-directml, doctr 传递 ML 栈 | **否** | 扫描其全部二进制扩展，零 ICU 引用。判定：`PROVEN_NOT_CONSUMER`。 |

**调查结论**：当前 5 大入口产物中，**没有任何组件是实际的 ICU78 消费者**。

详细的机器可读闭包排查矩阵在以下两个互补证据文件中完整保留并明确引用：
- [`icu-closure-matrix.json`](icu-closure-matrix.json)：根因确证、符号级 PE 导入/导出分析、系统 ICU 与外部 ICU 对照表及 412 个 bundle PE 二进制扫描统计；
- [`closure-matrix.json`](closure-matrix.json)：5 入口产物指纹、PE 闭包消费者裁决、三道隔离防线与加载解析机制定义。

### 1.2 外来 `icuuc.dll` 根因定位

通过对宿主机全局环境与构建环境的比对扫描证实：
1. 构建环境 `G:\CODEX\New Manga.task-envs\m2ac5-build\Lib\site-packages` 中完全没有包含 `icuuc.dll`。
2. 宿主机环境 `$env:PATH` 中包含了外部原生依赖缓存：
   `C:\Users\49745\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin`。
3. 该目录下存在 Poppler 附带的 `icuuc.dll`（SHA256: `39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf`），其版本为 ICU 78，导出符号全部带有 `_78` 后缀（如 `ucnv_open_78`），缺少 `Qt6Core.dll` 所需的无后缀符号。
4. PyInstaller 的 `bindepend` 在分析 `Qt6Core.dll` 的导入表时，因外部 Poppler 路径排在 `C:\Windows\System32` 之前（或被当成第三方依赖路径），误将该外来 ICU78 及其子依赖 `icudt78.dll` 收集并打包进了 `core-sidecar/_internal/` 顶层目录。
5. 安装态运行时，Windows 加载器优先在 `_internal/` 下搜索，导致 `Qt6Core.dll` 优先加载了该不兼容的 ICU78，产生 `WinError 127`（`ERROR_PROC_NOT_FOUND`），进而使 `import PySide6.QtGui` 失败。

---

## 2. 最小打包闭包隔离修复方案（AC-2）

本修复严格限定在 `packaging/m2ac5/**` 范围内，不修改任何 `src/**`、`apps/**`、`tests/**`，不更改依赖版本与 Schema：

1. **构建环境 PATH 隔离（第一道防线，`packaging/m2ac5/build_sidecar.ps1`）**：
   在执行 PyInstaller 期间，脚本局部净化 `$env:PATH`，排除 `codex-runtimes`、`poppler` 等包含外来第三方原生动态库的路径，保留系统目录与构建工具链。在 `finally` 块中立即恢复宿主原始 PATH。
   这使得 PyInstaller 在分析 `Qt6Core.dll` 时，直接查找到 `C:\Windows\System32\icuuc.dll`，并正确识别其为 Windows 操作系统内置库而不予收集。

2. **二进制闭包隔离与断言（第二道防线，`packaging/m2ac5/core_sidecar.spec`）**：
   在 Spec 的每个 entry 分析后，增加 `_isolate_icu_closure(a, name)`：
   - 过滤从外部误收集的顶层 `icuuc.dll` 及 `icudt*.dll`。
   - 增加断言 `_assert_no_shadowing_icu`：强制确保打包产生的二进制 TOC 中绝不存在任何会遮蔽系统 ICU 的同名 `icuuc.dll`。

3. **构建产物防遮蔽断言（第三道防线，`packaging/m2ac5/build_sidecar.ps1`）**：
   在打包完成后，显式断言检查 `$bundle/_internal/icuuc.dll` 必须不存在，一旦发现立即 fail-closed 退出。

---

## 3. 构建指纹与产物绑定（AC-3）

- **构建命令**: `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force`（全新五入口构建，无 skip-existing）
- **Tauri NSIS 命令**: `npx.cmd --yes @tauri-apps/cli@2 build`（全新 NSIS 安装包）
- **构建环境**: Windows, PowerShell 7, Node v24.15.0, Rustc 1.98.1, Python 3.12.3 (m2ac5-build venv)
- **Sidecar 构建日志**: `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/sidecar-build.log`（EXIT 0）
- **NSIS 构建日志**: `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/nsis-build.log`（EXIT 0）

### 产物指纹

| 产物文件 | 路径 | 大小 (bytes) | SHA256 |
|---|---|---|---|
| **Installer** | `apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe` | 578,947,768 (552.13 MiB) | `f76b91d6f78518787a8bb16f721581430dc8ec7c1498cf5a4e09d29f6225ce1f` |
| `host_bridge.exe` | `target/core-sidecar/core-sidecar/host_bridge.exe` | 1,826,431 | `717c9369d75530aee268f984bea444d0063c07c5a9e94af08ff187a06e4a1bc8` |
| `core_service.exe` | `target/core-sidecar/core-sidecar/core_service.exe` | 68,542,970 | `31309052dfa025b5687c0b2b0924c3e96e0715bd7753636ec6eb550a333b5431` |
| `acceptance_bridge.exe` | `target/core-sidecar/core-sidecar/acceptance_bridge.exe` | 68,530,186 | `9cea43db8e9f96f51338dd1a1481c647efbdfa79972077ceb3ddf9ee74f1ecfa` |
| `catalog_loader.exe` | `target/core-sidecar/core-sidecar/catalog_loader.exe` | 1,824,326 | `99b6dd76e04c29ac961c5cf852c87bb18d6015d59b587f15072ffab9a66bc166` |
| `sfx_detect_probe.exe` | `target/core-sidecar/core-sidecar/sfx_detect_probe.exe` | 67,902,901 | `9f7896d4552f173783bdfc2a8fe631a06753312e7f7ebf4bdcf74ea9e8345d1e` |

---

## 4. Dev Runner 验证（AC-4）

- **测试命令**: `python verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/run_e2e.py --exe apps/desktop/src-tauri/target/release/m2rc1-desktop.exe --skip-build --output-dir verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev`
- **执行日志**: `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev-e2e.log`
- **结果**: **10 项 Gate 全部 PASS，13 项 Probe 全部 PASS，EXIT 0**

### 10 项 Gate 详情
1. `environment`: PASS
2. `lab`: PASS
3. `catalog-seeding`: PASS
4. `sidecar-import-isolation`: PASS
5. `runtime-build`: PASS
6. `probe-phase`: PASS
7. `probe-allowlist-announcement`: PASS
8. `sidecar-module-dump-probe`: PASS
9. `interactive-production-surface`: PASS (15 production commands 严格匹配)
10. `sidecar-module-dump-interactive`: PASS

### 13 项 Probe 详情
`E-00` 到 `E-09`、`D-01` 到 `D-03` 全部 PASS（7 项 probe commands 严格匹配）。

---

## 5. Packaged Clean-Start 验证（AC-5）

- **测试命令**: `python verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/run_clean_start_e2e.py --installer apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe --output-dir verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged`
- **执行日志**: `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged-e2e.log`
- **结果**: **完整 26 项场景全部 PASS，GATE: PASS，EXIT 0**

### 26 项场景逐项清单
- **Phase 0: Environment & Path Purge**
  - `CS-E1-python-purged-from-path`: **PASS**（purged PATH 下无 python）
  - `CS-E2-installer-present`: **PASS**（installer SHA256 匹配）
  - `CS-E3-install-path-no-spaces`: **PASS**
- **Phase 1: Silent Install & Loader**
  - `CS-I1-silent-install`: **PASS**（安装至隔离临时目录，5565 文件）
  - `CS-I2-catalog-seeded-packaged-loader`: **PASS**（packaged catalog_loader.exe 种子注入成功）
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
  - `CS-A1-run1-completed`: **PASS**（第一轮成功，退出码 0）
  - `CS-A1-run2-completed`: **PASS**（第二轮成功，退出码 0）
  - `CS-A2-restart-new-pids`: **PASS**（run1 PIDs: [55156, 36136] -> run2 PIDs: [3876, 60668]，完全换新 PID）
  - `CS-A3-saved-summary-complete`: **PASS**（2 页处理，mock-ocr/translate 闭环）
  - `CS-A4-restored-reader-matches-saved`: **PASS**（重启后 reader 成功恢复）
  - `CS-A5-export-png-digest-matches`: **PASS**（PNG 导出哈希一致）
- **Phase 4: Production Mode**
  - `CS-R1-production-process-alive`: **PASS**
  - `CS-R2-userdata-layout-created`: **PASS**（隔离 APPDATA 正常创建）
  - `CS-R3-production-surface-announced`: **PASS**
  - `CS-R4-no-spawn-failures-in-log`: **PASS**
- **Phase 5: Zero-Touch Assertions (AC-6)**
  - `CS-Z1-install-dir-zero-write`: **PASS**（安装目录只读，运行前后零写入）
  - `CS-Z4-host-real-appdata-untouched`: **PASS**（真实宿主 %APPDATA% 零触碰，完全隔离）
  - `CS-Z2-user-source-files-byte-identical`: **PASS**（用户源文件 4 个字节完全一致）
  - `CS-Z3-no-surviving-sidecar-processes`: **PASS**（全部 4 个 sidecar 进程残留计数为 0）

---

## 6. 修复前后对比矩阵

| 指标 | 修复前（诊断基线，source_head: `cfb5d2ee`） | 修复后（本次提交，source_head: `df824182`） |
|---|---|---|
| **包内 `_internal/icuuc.dll`** | 存在（SHA256: `39aec884...`，Poppler ICU78） | **不存在**（零同名遮蔽） |
| **`acceptance_bridge.exe` 启动** | **FAIL**（EXIT 1 / 0.8s，`ImportError: cannot import name QtGui from PySide6`，WinError 127） | **PASS**（EXIT 0 / 1.01s，加载系统 ICU 顺畅启动） |
| **Qt6Core ICU 加载路径** | 误加载包内 `_internal/icuuc.dll`（缺 20 个无后缀符号） | 加载 `C:\Windows\System32\icuuc.dll`（542 个符号完全匹配） |
| **Dev Runner 结果** | 未完成完整 Gate | **10/10 Gate PASS, 13/13 Probe PASS** |
| **Packaged Runner 结果** | 20 PASS / 1 FAIL (`CS-A1-run1`) / 5 NOT_RUN | **26/26 ALL PASS** |
| **安装包大小** | 589,904,619 bytes | 578,947,768 bytes |
| **Sidecar 进程残留** | 未知/中断 | **0 残留** |
