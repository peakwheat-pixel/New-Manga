---
task_id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
author: Antigravity
recipient: DeepSeek Harness
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
start_head: df824182e813fc6d9045872da51d263f28db87f0
delivery_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
status: ready_for_review
---

# Handoff：M2-PACKAGED-AC1-ICU-ISOLATION-FIX（DSH r1/r2 修订交付）

## 交付结果

### 1. 目标与实现范围
本任务针对 Windows / React + Tauri 新架构安装态 Qt 被包内不兼容外部 `icuuc.dll` 同名遮蔽导致 `acceptance_bridge.exe` 启动崩溃（原 EXIT 1 / `ImportError: DLL load failed while importing QtGui`）的问题，按非作者 Reviewer (DeepSeek Harness) r1 审查意见（R-001 ~ R-007）及边界准则实施了全面的严格修订与重新构建验收。

- **生产代码范围**：严格受限于 `packaging/m2ac5/**`
  - [`packaging/m2ac5/core_sidecar.spec`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/packaging/m2ac5/core_sidecar.spec)：实现边界安全的路径比较（`_is_within_dir`）；唯一已证实污染源严格限定为 external poppler 工具链 `Library\bin\icuuc.dll` 并核验 SHA256（`39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf`）；移除宽泛的 `dependencies\native` / `codex-runtimes` 匹配，未知外部 ICU 一律 fail-closed；保留 venv 与 repo 内部 ICU；建立可判别 post-isolation 守卫断言及 COLLECT 汇总独立断言。
  - [`packaging/m2ac5/build_sidecar.ps1`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/packaging/m2ac5/build_sidecar.ps1)：定向净化 PATH 中已证实的 poppler 工具链条目并在 `finally` 恢复；明确全量 ICU 布局门禁为针对 System32 遮蔽风险的显式 fail-closed 安全门禁，而非武断宣称未来永不需要 versioned ICU。
- **只读受保护范围**：`src/**`、`apps/**`、`tests/**`、依赖清单/版本、Schema/共享IPC/ACL 保持严格 0 改动；实测 `git diff HEAD -- apps` 为 0。
- **固定实现代码提交**：[`4499217d7b2249da16d5dbf27a3219a43876aac7`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity) (`fix(packaging): restrict ICU isolation to verified poppler contaminant and tighten fail-closed boundary (M2-PACKAGED-AC1-ICU-ISOLATION-FIX)`)。所有新鲜构建和测试均严格在该固定 HEAD 上执行（R-001, R-002）。
- **本文档提交**：独立文档与证据提交，引用实现 commit `4499217d`。

### 2. DSH r1 审查意见关闭汇总

| Finding ID | 级别 | 解决措施与关闭事实 |
|---|---|---|
| **R-001** | **P1** | 重新在固定 HEAD fresh 构建出唯一安装包（SHA256: `f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`），并在该安装包上完整执行 26 项 Packaged Gate；`cleanstart-gate.json` 与 `build-fingerprint.json` 哈希逐位一致，完整日志入库。 |
| **R-002** | **P1** | 生产代码修订先行提交为 `4499217d`；随后 Sidecar、NSIS、Dev Gate、Packaged Gate 均在该固定 commit 上执行。所有日志实测输出 `GIT_HEAD: 4499217d7b2249da16d5dbf27a3219a43876aac7`，与指纹完全对齐。 |
| **R-003** | **P2** | 新增 `scan_pe_closure.py` 扫描脚本，入库 313 个 PE 二进制的原始扫描输出 `raw/pe-scan-raw.json`；补充入库 `closure-matrix.json` 与 `icu-closure-matrix.json`，明确区分直接静态无导入 (`NO_DIRECT_ICU_IMPORTS`) 与传递闭包/动态加载/延迟导入边界 (`UNKNOWN`)，全包结论限定为 313 个 PE 二进制的静态导入事实。 |
| **R-004** | **P2** | `core_sidecar.spec` 使用边界安全路径检查，唯一已证实污染源限定为 poppler 并校验 SHA256，未知外部来源 fail-closed，保留内部 ICU；`build_sidecar.ps1` 避免宽泛 PATH 正则，定向针对 poppler 并在 `finally` 恢复。 |
| **R-005** | **P3** | 重构具有真实判别力的守卫断言（核查已证实污染源未泄漏，并在 COLLECT 前独立核验）；`build_sidecar.ps1` 明确 fail-closed 门禁策略定位。 |
| **R-006** | **P3** | 所有耗时、PID、版本、哈希统一从现场日志生成：PyInstaller `6.22.3`、PIDs `[61404, 11828] -> [30296, 38904]`；CS-E2 描述修正为“验证安装包文件存在并记录实测 SHA256（无期望值比较判据）”。 |
| **R-007** | **P3** | 明确记录 Windows 10 1809+ / Windows 11 支持基线，其中 `C:\Windows\System32\icuuc.dll` 为标准 inbox 组件，Qt6Core 依此正常加载运行。 |

### 3. Acceptance Criteria 逐项对照

| AC 项 | 目标要求 | 达成事实与状态 |
|---|---|---|
| **AC-1** | 5 入口产物的 ICU78 消费者、PE 导入/导出、同名解析和加载闭包矩阵全面扫描，逐项记录证据或 UNKNOWN | **PASS**：全量扫描 313 个 PE 二进制，证实 5 个入口均无直接 ICU 静态/延迟导入；入口传递闭包与动态加载边界严谨标注为 UNKNOWN；全包结论限定为 313 个 PE 中 0 个 versioned ICU78 消费者，仅 Qt6Core 依赖未后缀 icuuc.dll。见 [`icu-closure-matrix.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/icu-closure-matrix.json) 与 [`closure-matrix.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/closure-matrix.json)。 |
| **AC-2** | 最小打包范围内修复；purged PATH 下 `acceptance_bridge.exe` 真实加载成功；保留原失败与修复后对照 | **PASS**：隔离环境（`PATH=C:\Windows\System32;C:\Windows`，`M2AC1_TEST_MODE=1`，`stdin=EOF`）下 `acceptance_bridge.exe` 0.47s 完成初始化随 EOF 退出，EXIT 0，消除基线 WinError 127 故障。见 [`acceptance-bridge-purged-path.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/acceptance-bridge-purged-path.log)。 |
| **AC-3** | fresh Sidecar 5 入口与 fresh NSIS 构建成功，绑定 source_head、命令、hash、大小、EXIT 与耗时 | **PASS**：fresh Sidecar 347.60s EXIT 0；fresh NSIS 326.82s EXIT 0（552.68 MiB）。指纹绑定见 [`build-fingerprint.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/build-fingerprint.json)。 |
| **AC-4** | 冻结 Dev Gate 完整 10 项 Gate 及 13 项 probe 通过；15 production / 7 probe commands 严格核对 | **PASS**：`run_e2e.py` 完整 10/10 Gate PASS，13/13 Probe 场景 PASS（耗时 19.37s，EXIT 0）。见 [`dev-gate-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev-gate-execution.log)。 |
| **AC-5** | 新安装副本完整 26 项 Packaged Gate 全 PASS；CS-L1 响应 minor 1.6、两轮 AC1、重启新 PID、数据与 PNG digest 一致 | **PASS**：`run_clean_start_e2e.py` 完整 26/26 场景全 PASS（耗时 131.13s，EXIT 0），被测安装包 SHA256 与 fingerprint 严格一致。见 [`cleanstart-gate.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged/cleanstart-gate.json)。 |
| **AC-6** | 用户源文件、人工修改、Lock、current/pinned Revision、Managed Copy 及恢复能力保护；零残留 | **PASS**：CS-Z1~Z4 零写入/零篡改/零孤儿进程断言全 PASS；真实 APPDATA 零触碰。 |
| **AC-7** | 固定实现 head、逐项结果及 Handoff 齐全；经外部非作者 DSH 审核 approved 及 Codex 集成后方可 done | **PENDING (NOT_RUN)**：实现提交固定为 `4499217d`，文档交接中；等待 DSH r2 独立 Review 与 Codex 集成。 |

---

## 验证证据

### 1. 验证命令执行与统计

| AC/场景 | 实际命令/步骤 | 解释器/环境 | 被测 Commit | 结果与耗时 | 日志/产物路径 |
|---|---|---|---|---|---|
| **AC-1 闭包扫描** | `python verification/.../scan_pe_closure.py` | Python 3.12 (m2ac5-build venv) | `4499217d` | **PASS** (10.0s) | [`pe-scan-raw.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/pe-scan-raw.json) |
| **AC-2 隔离加载** | `.\acceptance_bridge.exe` (purged PATH, M2AC1_TEST_MODE=1, EOF) | Subprocess (purged PATH) | `4499217d` | **PASS** (0.47s, EXIT 0) | [`acceptance-bridge-purged-path.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/acceptance-bridge-purged-path.log) |
| **AC-3 Sidecar 构建** | `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force` | PowerShell 7 / PyInstaller 6.22.3 | `4499217d` | **PASS** (347.60s, EXIT 0) | [`sidecar-build.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/sidecar-build.log) |
| **AC-3 NSIS 构建** | `npx.cmd --yes @tauri-apps/cli@2 build` (CWD=apps/desktop) | Node.js v24.15.0 / Cargo 1.98.1 | `4499217d` | **PASS** (326.82s, EXIT 0) | [`nsis-build.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/nsis-build.log) |
| **AC-4 Dev Gate** | `python run_e2e.py --exe .../m2rc1-desktop.exe --skip-build --output-dir raw/dev` | Python 3.12 (T1.1.1-impl-py312) | `4499217d` | **PASS** (19.37s, EXIT 0) 10/10 Gate + 13/13 Probe | [`dev-gate-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev-gate-execution.log) |
| **AC-5 Packaged Gate** | `python run_clean_start_e2e.py --installer .../m2rc1-desktop_0.1.0_x64-setup.exe --output-dir raw/packaged` | Python 3.12 (T1.1.1-impl-py312) | `4499217d` | **PASS** (131.13s, EXIT 0) 26/26 场景全 PASS | [`packaged-gate-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged-gate-execution.log) |
| **AC-6 零污染验证** | `git diff HEAD -- apps; git status --short` | Git CLI | `4499217d` | **PASS** (apps 0 内容差异，宿主机 0 污染) | 工作区实测检验通过 |

### 2. 产物指纹与 Hash 绑定

- **NSIS 安装包**：
  - 路径：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
  - SHA256：`f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`
  - 大小：579,525,817 字节 (552.68 MiB)
- **5 个 Sidecar 入口**（位于 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`）：
  - `acceptance_bridge.exe`: `9e4a0068e153e376c02bf802435e9dbffe7442b014fee7e420197e50e4d7eae8` (68,530,186 字节)
  - `catalog_loader.exe`: `f0a59794fb6c6beefa49305506ec0e97b2e31adf4edf78c56a3b0f151c67bf6f` (1,824,326 字节)
  - `core_service.exe`: `7a1a78525dae14ac862e2da518fc493c7993b0ffbbe953cebd42b5823d70e10a` (68,542,970 字节)
  - `host_bridge.exe`: `6ca28abaf9ec0d1ba4e21a237b7d733f5c72b8d0fa4831e3051cf69efea346a2` (1,826,431 字节)
  - `sfx_detect_probe.exe`: `f9b31287136e44262c37ce342ee663c0210a6a33090ba67533c3c0b40aaa9456` (67,902,901 字节)

### 3. 未运行项目与说明
- **真实发行包系统级安装**：未运行（NOT_RUN）。安装态测试在自有隔离临时目录 `cleanstart_lab/install` 中静默解包执行，严格禁止向宿主机 `C:\Program Files` 或系统注册表执行真实安装，以杜绝环境污染。
- **AC-7 独立 Review 与主线合并**：未运行（PENDING）。按团队协作规范，作者 Agent 禁止审核自己提交的代码，待 DeepSeek Harness r2 独立审核后由 Codex 执行最终主线集成。

---

## 接收方式

1. **工作树与分支**：
   - 分支：`agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
   - 工作树：`G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`
   - Git Common Dir：`G:/CODEX/New Manga/.git`
2. **前置条件与被测 HEAD**：
   - Base Commit: `5a72db9e3c5778ce4700b7d404250853e474c5de`
   - 实现 Commit: [`4499217d7b2249da16d5dbf27a3219a43876aac7`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity)
3. **Reviewer (DeepSeek Harness) 复审重点**：
   - 核查 `packaging/m2ac5/core_sidecar.spec` 中 `_isolate_icu_closure` 来源限定与分类逻辑（venv/repo 边界安全保留、poppler 哈希核验隔离、未分类 fail-closed）及独立断言有效性；
   - 核查 `packaging/m2ac5/build_sidecar.ps1` 中的 PATH 定向净化与递归目录 fail-closed 门禁；
   - 核验 `raw/pe-scan-raw.json`、`icu-closure-matrix.json`、`closure-matrix.json` 中 313 个 PE 文件的扫描数据与动态/传递边界 UNKNOWN 标识；
   - 核查 `build-fingerprint.json`、`raw/nsis-build.log`、`cleanstart-gate.json` 中交付安装包 SHA256 (`f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`) 的一致性与完整 26 项输出；
   - 确认 `git diff HEAD -- apps` 严格为 0。

---

## 下一步建议

本任务代码修复与全部证据链已闭环，保持 `ready_for_review` 与 `CHECKPOINTED` 状态。请 Codex 调度非作者 Reviewer (DeepSeek Harness) 执行 r2 独立审查：

```bash
# 指令转发给 DeepSeek Harness
Agent: DeepSeek Harness
Action: Review
Task: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
Branch: agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX
Target Commit: 4499217d7b2249da16d5dbf27a3219a43876aac7
Handoff: doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md
Report: verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md
```
