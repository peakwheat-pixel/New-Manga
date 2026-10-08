# M2-PACKAGED-AC1-ICU-ISOLATION-FIX 验证与执行报告

- **任务 ID**：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
- **任务性质**：bugfix（安装态 Qt 与 ICU78 依赖闭包隔离修复）
- **Owner**：Antigravity
- **非作者 Reviewer**：DeepSeek Harness
- **Integrator**：Codex
- **基线 commit**：`5a72db9e3c5778ce4700b7d404250853e474c5de`
- **起始 HEAD**：`df824182e813fc6d9045872da51d263f28db87f0`
- **分支**：`agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
- **工作区**：`G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`
- **Git Common Dir**：`G:/CODEX/New Manga/.git`

---

## 1. 背景与根因确认（AC-1 达成）

### 1.1 诊断事实与真实根因
在前期诊断任务 `M2-PACKAGED-AC1-DLL-DIAG` 中，证实了安装态 `acceptance_bridge.exe` 启动时报 `ImportError: cannot import name 'QtGui' from 'PySide6'` 的根因：
`Qt6Core.dll` 的 PE 导入表声明依赖 `icuuc.dll`，要求 20 个无版本后缀的 `ucnv_*` 符号（由 Windows 10/11 系统自带的 `C:\Windows\System32\icuuc.dll` 提供）。
然而，在打包过程中，PyInstaller 的依赖分析器（`bindepend`）沿着宿主机 `PATH` 搜索 `icuuc.dll`，由于构建宿主机的 `PATH` 中包含外部运行时依赖目录（`C:\Users\49745\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin`），PyInstaller 错误地从该目录抓取了第三方的 ICU78 `icuuc.dll`（SHA256: `39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf`）及其配套的 `icudt78.dll`，并将其放置在打包产物的 `_internal/` 根目录下。

在安装态运行时，Windows 加载器依据默认搜索顺序，优先在应用程序目录（`_internal/`）命中该 `icuuc.dll`，从而**遮蔽**了 `System32` 中的系统 ICU。而该外部 ICU78 的导出符号全部带有 `_78` 版本后缀（如 `ucnv_open_78`），缺少 `Qt6Core.dll` 所需的无后缀符号，引发 Windows 加载器 `WinError 127`（`ERROR_PROC_NOT_FOUND`），导致 Qt 导入失败。

### 1.2 5 入口产物 ICU 消费者全面核验（闭包矩阵）
本任务对 5 个入口产物及其所有依赖模块进行了全面的 PE 导入表与源码审查，逐项证实如下：

| 入口名称 | 对应模块 | 二进制依赖范围 | 是否为实际 ICU78 消费者 | 判定证据与结论 |
|---|---|---|---|---|
| `host_bridge.exe` | `infrastructure.resource_channel.host_bridge` | 仅 Python 标准库与仓内模块 | **否** | 0 外部 C 扩展；PE 导入扫描 0 icu 引用。结论：PROVEN_NON_CONSUMER |
| `core_service.exe` | `bootstrap.core_service` | Python 标准库 + SQLite + PyTorch/torchvision/transformers/onnxruntime/doctr ML 栈 | **否** | 扫描所有 ML 二进制扩展（400+ 个 .pyd/.dll），无任何模块导入 icu*.dll。结论：PROVEN_NON_CONSUMER |
| `acceptance_bridge.exe` | `bootstrap.acceptance_bridge` | Python 标准库 + PySide6 (`Qt6Core.dll`, `Qt6Gui.dll`) | **否 (仅依赖系统 ICU)** | `Qt6Core.dll` 导入 20 个无后缀符号，由 `System32\icuuc.dll` 提供；不消费 ICU78。结论：PROVEN_SYSTEM_ICU_ONLY |
| `catalog_loader.exe` | `infrastructure.resource_channel.catalog_loader` | 仅 Python 标准库与 SQLite 仓内持久化接口 | **否** | 0 外部 C 扩展；PE 导入扫描 0 icu 引用。结论：PROVEN_NON_CONSUMER |
| `sfx_detect_probe.exe` | `bootstrap.sfx_detect_probe` | Python 标准库 + onnxruntime-directml + 传递性 torch/doctr ML 闭包 | **否** | 扫描 `onnxruntime_pybind11_state.pyd` 与 `DirectML.dll`，均无 icu 引用。结论：PROVEN_NON_CONSUMER |

**核心结论**：整个应用程序及其 5 个 entry 中，**没有任何组件是实际的 ICU78 消费者**。原包内出现的 `icuuc.dll` 100% 属于构建宿主机 PATH 污染导致的误收集。

结构化矩阵数据见 [icu-closure-matrix.json](icu-closure-matrix.json)。

---

## 2. 最小打包闭包隔离修复（AC-2 达成）

修改严格限制在 `packaging/m2ac5/**` 范围内，未触碰任何 `src/**`、`apps/**`、`tests/**` 或依赖清单。

### 2.1 修复实施细节
1. **`packaging/m2ac5/core_sidecar.spec`**：
   - 增加闭包隔离函数 `_isolate_icu_closure(analysis, exe_name)`：
     在各个 entry 的 `Analysis` 完成后，检查其 `a.binaries` 列表，主动剔除因 PATH 污染误收集的外来 `icuuc.dll`、`icudt*.dll`，防止其落入 `_internal` 顶层目录造成同名遮蔽。
   - 增加闭包断言：在过滤后严格断言 `a.binaries` 中绝不存在顶层 `icuuc.dll`，一旦出现破坏性遮蔽直接 fail the build。
2. **`packaging/m2ac5/build_sidecar.ps1`**：
   - 在执行 PyInstaller 构建的子进程生命周期内，实施局部环境变量 `$env:PATH` 净化（排除含有第三方原生库的 `codex-runtimes`、`poppler` 等目录，保留标准 Windows 系统目录和构建 Python 虚拟环境工具路径），并在 finally 块中复原，从源头上阻断 `bindepend` 误检索。
   - 构建末尾增加产物安全断言：核验生成的 `target/core-sidecar/core-sidecar/_internal/icuuc.dll` 必须不存在。

### 2.2 修复前后加载因果对照
- **修复前（诊断基线）**：
  在隔离环境（`PATH=C:\Windows\System32;C:\Windows`，`M2AC1_TEST_MODE=1`，stdin DEVNULL）下运行 `acceptance_bridge.exe`：
  - 结果：**EXIT 1 / 0.8s**
  - 错误：`ImportError: cannot import name 'QtGui' from 'PySide6'`（底层为 Qt6Core 报 WinError 127）。
- **修复后（新鲜构建产物）**：
  在完全相同的隔离环境下运行本次构建生成的 `acceptance_bridge.exe`：
  - 结果：**EXIT 0 / 1.01s**
  - 状态：Qt6Core 顺利绑定系统 `System32\icuuc.dll`，QtGui 成功导入，bridge 干净初始化并正常退出。

---

## 3. 构建产物与指纹绑定（AC-3 达成）

本次实施执行了完整的 fresh 构建，未使用任何 `-skip-existing` 绕过。

### 3.1 构建命令与耗时
1. **Sidecar 构建**：
   - 命令：`pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force`
   - 解释器：PowerShell 7.5.4 / Python 3.12.9 (`m2ac5-build`)
   - 耗时：368.6 秒
   - 退出码：`EXIT 0`
   - 日志：[sidecar-build.log](raw/sidecar-build.log)
2. **NSIS 构建**：
   - 命令：`npx.cmd --yes @tauri-apps/cli@2 build`（工作目录 `apps/desktop`）
   - 耗时：340.0 秒
   - 退出码：`EXIT 0`
   - 日志：[nsis-build.log](raw/nsis-build.log)

### 3.2 产物指纹与哈希绑定
详见 [build-fingerprint.json](build-fingerprint.json)。

- **NSIS Installer**：
  - 路径：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
  - 大小：578,944,542 字节 (552.12 MiB)
  - SHA256：`a17a9708d5c18d79b0e009f9bf1da8c0de8701ddd7a06af8356a08dd7766ceb2`
- **5 个 Sidecar 入口**（位于 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`）：
  - `host_bridge.exe`：1,826,431 字节，SHA256: `717c9369d75530aee268f984bea444d0063c07c5a9e94af08ff187a06e4a1bc8`
  - `core_service.exe`：68,542,970 字节，SHA256: `31309052dfa025b5687c0b2b0924c3e96e0715bd7753636ec6eb550a333b5431`
  - `acceptance_bridge.exe`：68,530,186 字节，SHA256: `9cea43db8e9f96f51338dd1a1481c647efbdfa79972077ceb3ddf9ee74f1ecfa`
  - `catalog_loader.exe`：1,824,326 字节，SHA256: `99b6dd76e04c29ac961c5cf852c87bb18d6015d59b587f15072ffab9a66bc166`
  - `sfx_detect_probe.exe`：67,902,901 字节，SHA256: `9f7896d4552f173783bdfc2a8fe631a06753312e7f7ebf4bdcf74ea9e8345d1e`

---

## 4. Dev Gate 验收结果（AC-4 达成）

复用固定 head `2af6b71aa06979b822e543b221aaf3a2d5f01abe` 的 `verification/M2-RC2/run_e2e.py`，执行参数：
`--exe apps/desktop/src-tauri/target/release/m2rc1-desktop.exe --skip-build --output-dir raw/dev`。

- 退出码：`EXIT 0`
- 耗时：26.8 秒
- 日志：[dev-gate-execution.log](raw/dev-gate-execution.log)
- 详细产物：[e2e-gate.json](raw/dev/e2e-gate.json)、[e2e-probe-results.json](raw/dev/e2e-probe-results.json)

### 4.1 Gate 项与 Probe 项统计
- **10 项 Gate**：**10 PASS / 0 FAIL**
  1. `environment`: PASS
  2. `lab`: PASS
  3. `catalog-seeding`: PASS
  4. `sidecar-import-isolation`: PASS
  5. `runtime-build`: PASS
  6. `probe-phase`: PASS
  7. `probe-allowlist-announcement`: PASS
  8. `sidecar-module-dump-probe`: PASS
  9. `interactive-production-surface`: PASS
  10. `sidecar-module-dump-interactive`: PASS
- **13 项 Probe 场景**：**13 PASS / 0 FAIL**（`E-00` 至 `E-08`，`P-01` 至 `P-04` 全部通过）
- **命令面一致性**：15 条生产命令与 7 条 probe 命令核对严格一致。

---

## 5. Packaged Gate 验收结果（AC-5 与 AC-6 达成）

复用固定 head `2af6b71aa06979b822e543b221aaf3a2d5f01abe` 的 `packaging/m2ac5/run_clean_start_e2e.py`，执行参数：
`--installer <本次 fresh installer> --output-dir raw/packaged`。

- 退出码：`EXIT 0`
- 耗时：131.7 秒
- 日志：[packaged-gate-execution.log](raw/packaged-gate-execution.log)
- 详细结果：[cleanstart-gate.json](raw/packaged/cleanstart-gate.json)

### 5.1 场景逐项执行清单（完整 26 项场景全 PASS）

| 阶段 | 场景 ID | 预期行为与实测结果 | 结论 |
|---|---|---|---|
| Phase 0 | `CS-E1-python-purged-from-path` | 净化 PATH 断言：子进程环境无 python 解析 | **PASS** |
| Phase 0 | `CS-E2-installer-present` | Installer 存在且 SHA256 匹配本次构建值 | **PASS** |
| Phase 0 | `CS-E3-install-path-no-spaces` | 临时安装目录路径无空格校验 | **PASS** |
| Phase 1 | `CS-I1-silent-install` | NSIS 静默安装到隔离 temp 目录成功 | **PASS** |
| Phase 1 | `CS-I2-catalog-seeded-packaged-loader` | 使用安装包内的 `catalog_loader.exe` 注入 5 行数据 | **PASS** |
| Phase 1.5 | `CS-L1-packaged-core-ping` | `core_service.exe` 响应 protocol minor 1.6 / status ready | **PASS** |
| Phase 1.5 | `CS-L2-packaged-ListBooks-structure` | `ListBooks` 结构校验合法 | **PASS** |
| Phase 1.5 | `CS-L3-packaged-core-shutdown` | `core.shutdown` 返回 stopped 并正常退出 | **PASS** |
| Phase 2 | `CS-P1-probe-results-written` | PROBE 模式结果 JSON 成功写出 | **PASS** |
| Phase 2 | `CS-P2-probe-scenarios-all-pass` | 13 项 probe 场景全部在安装态下通过 | **PASS** |
| Phase 2 | `CS-P3-sidecar-roundtrip-digest` | 资源通道图片字节往返 digest 完全一致 | **PASS** |
| Phase 3 | `CS-A0-ac1-catalog-prebind` | AC1 模式 catalog 前置绑定 | **PASS** |
| Phase 3 | `CS-A1-run1-completed` | AC1 第一轮运行顺利完成（此前在此处报 QtGui 错误，现修复） | **PASS** |
| Phase 3 | `CS-A1-run2-completed` | AC1 第二轮运行顺利完成 | **PASS** |
| Phase 3 | `CS-A2-restart-new-pids` | 重启验证：第二轮获得全新的独立子进程 PID | **PASS** |
| Phase 3 | `CS-A3-saved-summary-complete` | Summary 状态为 completed，页面数 2 | **PASS** |
| Phase 3 | `CS-A4-restored-reader-matches-saved` | Reader 恢复内容与保存内容 digest 逐位一致 | **PASS** |
| Phase 3 | `CS-A5-export-png-digest-matches` | 导出 PNG 校验一致 (sha: 4afc67386c25) | **PASS** |
| Phase 4 | `CS-R1-production-process-alive` | PRODUCTION 模式窗口进程正常存活 | **PASS** |
| Phase 4 | `CS-R2-userdata-layout-created` | 隔离 APPDATA 结构（catalog/data/derived/managed）创建 | **PASS** |
| Phase 4 | `CS-R3-production-surface-announced` | 生产命令白名单宣告正常 | **PASS** |
| Phase 4 | `CS-R4-no-spawn-failures-in-log` | 运行日志中 0 次 spawn 失败 | **PASS** |
| Phase 5 (AC4/6) | `CS-Z1-install-dir-zero-write` | 安装目录写入防逃逸：前后对比 0 文件变更 | **PASS** |
| Phase 5 (AC4/6) | `CS-Z4-host-real-appdata-untouched` | 宿主机真实 APPDATA 零写入、零篡改防逃逸验证通过 | **PASS** |
| Phase 5 (AC4/6) | `CS-Z2-user-source-files-byte-identical` | 用户源素材文件 100% 逐位一致 | **PASS** |
| Phase 5 (AC4/6) | `CS-Z3-no-surviving-sidecar-processes` | 运行后进程清理检查：0 残留 sidecar 孤儿进程 | **PASS** |

**最终裁决**：`GATE: PASS`（26/26 全部通过）。

---

## 6. 测试状态与异常分类说明

为严格遵守测试诚信与可复核性规范，测试记录分列如下：

| 执行阶段 | 类别 | 状态 | 详细说明 |
|---|---|---|---|
| Sidecar 构建 | 自动化脚本 | **PASS** | `build_sidecar.ps1 -Force` 正常完成，耗时 368.6s，EXIT 0 |
| NSIS 构建 (初次) | 人为中止 | **ABORTED** | 首次执行过程中响应 Codex 停机检查指令中止，记为 ABORTED，不计为产品失败 |
| NSIS 构建 (重试) | 系统锁异常 | **ABORTED** | 因初次中止残留的 `makensis` 进程锁定临时文件触发 `os error 32`；清理残留进程后未再次复现，记为 ABORTED |
| NSIS 构建 (Fresh) | 完整构建 | **PASS** | 成功生成 552.12 MiB 安装包，耗时 340.0s，EXIT 0 |
| 隔离加载对照 | 自动化探针 | **PASS** | `acceptance_bridge.exe` 在 purged PATH 隔离环境下顺利启动退出，EXIT 0 |
| Dev Gate | 自动化测试套件 | **PASS** | 10 Gate + 13 Probe 全绿通过，耗时 26.8s，EXIT 0 |
| Packaged Gate | 端到端集成测试 | **PASS** | 26 项场景 100% 全绿通过，耗时 131.7s，EXIT 0 |

---

## 7. 变更范围与代码安全核查

交付前执行了严格的 Git 变更审查：
- `git diff HEAD -- apps`：**输出为空（0 差异）**，未对 `apps/` 造成任何内容改动。
- `git diff --name-only df824182e813fc6d9045872da51d263f28db87f0 HEAD`：所有修改完全严格限制在允许路径内：
  - `packaging/m2ac5/build_sidecar.ps1`
  - `packaging/m2ac5/core_sidecar.spec`
  - `doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md`
  - `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**`
- `git diff --check`：无任何空白或格式违规。
