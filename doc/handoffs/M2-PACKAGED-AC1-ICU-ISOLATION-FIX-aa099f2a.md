---
task_id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
author: Antigravity
recipient: DeepSeek Harness
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
start_head: df824182e813fc6d9045872da51d263f28db87f0
delivery_head: aa099f2a013408bf53c3466ab8361bc028289743
status: ready_for_review
---

# Handoff：M2-PACKAGED-AC1-ICU-ISOLATION-FIX

## 交付结果

### 1. 目标与实现范围
本任务针对 Windows / React + Tauri 新架构安装态 Qt 被包内不兼容外部 `icuuc.dll` 同名遮蔽导致 `acceptance_bridge.exe` 启动崩溃（原 EXIT 1 / `ImportError: DLL load failed while importing QtGui`）的问题进行根因定位与最小打包闭包隔离修复，同时核实并保护实际 ICU78 消费者的可用性。

- **生产代码范围**：严格限制在 `packaging/m2ac5/**`
  - [`packaging/m2ac5/core_sidecar.spec`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/packaging/m2ac5/core_sidecar.spec)：新增 `_isolate_icu_closure` 依赖过滤，剥离误入的第三方 ICU78 二进制；新增 `_assert_no_shadowing_icu` 守卫断言。
  - [`packaging/m2ac5/build_sidecar.ps1`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/packaging/m2ac5/build_sidecar.ps1)：在构建脚本中对 PyInstaller 子进程 `$env:PATH` 进行局部净化，消除构建期来自宿主机 PATH 的第三方 ICU78 污染源；并在生成末尾增加无同名遮蔽断言。
- **只读受保护范围**：`src/**`、`apps/**`、`tests/**`、依赖清单/版本、Schema/共享IPC/ACL 保持严格 0 改动；实测 `git diff HEAD -- apps` 为 0（无真实内容变更）。
- **固定实现提交**：[`aa099f2a013408bf53c3466ab8361bc028289743`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity) (`fix(packaging): isolate Qt from shadowing ICU78 in sidecar bundle (M2-PACKAGED-AC1-ICU-ISOLATION-FIX)`)。
- **本文档提交**：独立文档提交，引用实现 commit `aa099f2a`。

### 2. Acceptance Criteria 逐项对照

| AC 项 | 目标要求 | 达成事实与状态 |
|---|---|---|
| **AC-1** | 5 入口产物的 ICU78 消费者、PE 导入/导出、同名解析和加载闭包矩阵全面扫描，逐项记录证据或 UNKNOWN | **PASS**：全量扫描 dist 内 412 个 PE 二进制与构建环境 `site-packages`，证实 5 个入口均不是 ICU78 消费者；`Qt6Core.dll` 仅依赖系统 `C:\Windows\System32\icuuc.dll` 的无后缀符号。见 [`icu-closure-matrix.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/icu-closure-matrix.json)（符号级证据与 412 个 PE 扫描）与 [`closure-matrix.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/closure-matrix.json)（产物闭包指纹与解析机制）。 |
| **AC-2** | 最小打包范围内修复；purged PATH 下 `acceptance_bridge.exe` 真实加载成功；保留原失败与修复后对照 | **PASS**：仅修改 `packaging/m2ac5/**`；隔离环境下 `acceptance_bridge.exe` 启动通过（EXIT 0 / 1.01s，消除了基线 EXIT 1 / 0.8s ImportError 故障）。 |
| **AC-3** | fresh Sidecar 5 入口与 fresh NSIS 构建成功，绑定 source_head、命令、hash、大小、EXIT 与耗时 | **PASS**：fresh Sidecar 368.6s EXIT 0；fresh NSIS 340.0s EXIT 0（552.12 MiB）。指纹绑定见 [`build-fingerprint.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/build-fingerprint.json)。 |
| **AC-4** | 冻结 Dev Gate 完整 10 项 Gate 及 13 项 probe 通过；15 production / 7 probe commands 严格核对 | **PASS**：`run_e2e.py` 完整 10/10 Gate PASS，13/13 Probe 场景 PASS（耗时 26.8s，EXIT 0）。 |
| **AC-5** | 新安装副本完整 26 项 Packaged Gate 全 PASS；CS-L1 响应 minor 1.6、两轮 AC1、重启新 PID、数据与 PNG digest 一致 | **PASS**：`run_clean_start_e2e.py` 完整 26/26 场景全 PASS（耗时 131.7s，EXIT 0）。 |
| **AC-6** | 用户源文件、人工修改、Lock、current/pinned Revision、Managed Copy 及恢复能力保护；零残留 | **PASS**：CS-Z1~Z4 零写入/零篡改/零孤儿进程断言全 PASS；未触碰用户安装或生产数据。 |
| **AC-7** | 固定实现 head、逐项结果及 Handoff 齐全；经外部非作者 DSH 审核 approved 及 Codex 集成后方可 done | **PENDING (NOT_RUN)**：实现提交固定为 `aa099f2a`，文档交接中；等待 DSH 独立 Review 与 Codex 集成。 |

---

## 验证证据

### 1. 验证命令执行与统计

| AC/场景 | 实际命令/步骤 | 解释器/环境 | 被测 Commit | 结果与耗时 | 日志/产物路径 |
|---|---|---|---|---|---|
| **AC-1 闭包审查** | `python verification/.../scan_closure.py` (pefile 分析) | Python 3.12 隔离虚拟环境 | `df824182` | **PASS** (12.4s) | [`icu-closure-matrix.json`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/icu-closure-matrix.json) |
| **AC-2 隔离加载** | `.\acceptance_bridge.exe --help` (purged PATH) | Windows Subprocess (purged PATH) | `aa099f2a` | **PASS** (1.01s, EXIT 0) | [`REPORT.md`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md#L30-L55) |
| **AC-3 Sidecar 构建** | `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force` | PowerShell 7 / PyInstaller 6.16.0 | `aa099f2a` | **PASS** (368.6s, EXIT 0) | [`sidecar-build.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/sidecar-build.log) |
| **NSIS Attempt 1** | `npx.cmd --yes @tauri-apps/cli@2 build` | Node.js / Cargo / Tauri CLI 2 | `aa099f2a` | **ABORTED** (人为停机指令中止) | 响应 Codex 停机检查，非产品故障 |
| **NSIS Attempt 2** | `npx.cmd --yes @tauri-apps/cli@2 build` | Node.js / Cargo / Tauri CLI 2 | `aa099f2a` | **ABORTED** (残留 makensis 进程锁) | 孤儿进程 PID 48016/57972 触发 os error 32，清理后重试 |
| **AC-3 NSIS Fresh 构建** | `npx.cmd --yes @tauri-apps/cli@2 build` | Node.js / Cargo / Tauri CLI 2 | `aa099f2a` | **PASS** (340.0s, EXIT 0) | [`nsis-build.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/nsis-build.log) |
| **AC-4 Dev Gate** | `python run_e2e.py --exe .../m2rc1-desktop.exe --skip-build --output-dir raw/dev` | Python 3.12 (复用固定 head 2af6b71a 副本) | `aa099f2a` | **PASS** (26.8s, EXIT 0) 10/10 Gate + 13/13 Probe | [`dev-gate-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/dev-gate-execution.log) |
| **AC-5 Packaged Gate** | `python run_clean_start_e2e.py --installer .../m2rc1-desktop_0.1.0_x64-setup.exe --output-dir raw/packaged` | Python 3.12 (复用固定 head 2af6b71a 副本) | `aa099f2a` | **PASS** (131.7s, EXIT 0) 26/26 场景全 PASS | [`packaged-gate-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity/verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/packaged-gate-execution.log) |
| **AC-6 零污染验证** | `git diff HEAD -- apps; git status --short` | Git CLI | `aa099f2a` | **PASS** (apps 0 内容差异，宿主机 0 污染) | 工作区实测检验通过 |

### 2. 产物指纹与 Hash 绑定

- **NSIS 安装包**：
  - 路径：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
  - SHA256：`f76b91d6f78518787a8bb16f721581430dc8ec7c1498cf5a4e09d29f6225ce1f`
  - 大小：578,947,768 字节 (552.13 MiB)
- **5 个 Sidecar 入口**（位于 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`）：
  - `host_bridge.exe`: `717c9369d75530aee268f984bea444d0063c07c5a9e94af08ff187a06e4a1bc8` (1,826,431 字节)
  - `core_service.exe`: `31309052dfa025b5687c0b2b0924c3e96e0715bd7753636ec6eb550a333b5431` (68,542,970 字节)
  - `acceptance_bridge.exe`: `9cea43db8e9f96f51338dd1a1481c647efbdfa79972077ceb3ddf9ee74f1ecfa` (68,530,186 字节)
  - `catalog_loader.exe`: `99b6dd76e04c29ac961c5cf852c87bb18d6015d59b587f15072ffab9a66bc166` (1,824,326 字节)
  - `sfx_detect_probe.exe`: `9f7896d4552f173783bdfc2a8fe631a06753312e7f7ebf4bdcf74ea9e8345d1e` (67,902,901 字节)

### 3. 未运行项目与说明
- **真实发行包系统级安装**：未运行（NOT_RUN）。安装态测试在自有隔离临时目录 `cleanstart_lab/inst` 中静默解包执行，严格禁止向宿主机 `C:\Program Files` 或系统注册表执行真实安装，以杜绝环境污染。
- **AC-7 独立 Review 与主线合并**：未运行（PENDING）。按团队协作规范，作者 Agent 禁止审核自己提交的代码，待 DeepSeek Harness 独立审核后由 Codex 执行最终主线集成。

---

## 接收方式

1. **工作树与分支**：
   - 分支：`agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
   - 工作树：`G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`
   - Git Common Dir：`G:/CODEX/New Manga/.git`
2. **前置条件与被测 HEAD**：
   - Base Commit: `5a72db9e3c5778ce4700b7d404250853e474c5de`
   - 实现 Commit: [`aa099f2a013408bf53c3466ab8361bc028289743`](file:///G:/CODEX/New%20Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity)
3. **Reviewer (DeepSeek Harness) 审核重点**：
   - 检查 `packaging/m2ac5/core_sidecar.spec` 中 `_isolate_icu_closure` 过滤逻辑的安全性与边界保护。
   - 检查 `packaging/m2ac5/build_sidecar.ps1` 中的 `$env:PATH` 净化范围是否合理，是否仅影响 PyInstaller 子进程。
   - 核对 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md` 与 `icu-closure-matrix.json` 中 412 个 PE 二进制的导入扫描事实。
   - 确认 `git diff HEAD -- apps` 为 0（确认 apps 目录仅存在 mtime 触碰，实际 blob 内容严格未变）。
   - 核验 Dev Gate (10+13) 与 Packaged Gate (26 场景) 原始日志及退出码。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX` 独立非作者审查 (Review)
- **推荐 Agent / Reviewer**：`DeepSeek Harness`
- **推荐原因与前置依赖**：Antigravity 已完成代码实现、fresh Sidecar/NSIS 构建及 Dev/Packaged 全量 Gate 验收，提交已固定为 `aa099f2a`；根据架构规范，需非作者角色执行独立审查。依赖 `aa099f2a`。
- **Recovery point**：
  - 仓库：`G:/CODEX/New Manga`
  - 分支：`agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`
  - Base Commit：`5a72db9e3c5778ce4700b7d404250853e474c5de`
  - Delivery Head：`aa099f2a013408bf53c3466ab8361bc028289743`
  - Worktree：待 Codex 创建或复用已有只读 worktree。
- **允许修改路径**：
  - `doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md`
  - `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review/**`
- **禁止范围与新增授权条件**：严格只读审查，严禁修改生产代码 `packaging/**`、`src/**`、`apps/**` 或主线文档；若发现事实不符仅记录证据报告 Codex。
- **交付物**：符合 `doc/templates/REVIEW.md` 规范的独立审查报告。
- **验证命令、环境与完成 Gate**：
  - 核查 `git diff 5a72db9e..aa099f2a --stat` 与内容 diff，确认生产变更严格受限于 `packaging/m2ac5/**`。
  - 验证 `git diff HEAD -- apps` 退出码为 0 且无 diff 输出。
  - 抽检 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/raw/` 下日志的真实性。
- **可直接转发给 Agent 的指令**：
  ```text
  请作为非作者 Reviewer (DeepSeek Harness) 审查 Task M2-PACKAGED-AC1-ICU-ISOLATION-FIX。
  工作区基准：分支 agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX，被测提交 aa099f2a013408bf53c3466ab8361bc028289743。
  参考文档：doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md、doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-aa099f2a.md、verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md。
  重点核查：
  1. 生产代码变更是否严格限定在 packaging/m2ac5/**，apps/** 内容是否确为 0 变更；
  2. icu-closure-matrix.json 对 5 入口非 ICU78 消费者的判断依据是否充分；
  3. core_sidecar.spec 与 build_sidecar.ps1 的隔离逻辑是否合理且具备防同名遮蔽断言；
  4. Dev Gate (10+13) 与 Packaged Gate (26) 的执行证据是否完备。
  请按 doc/templates/REVIEW.md 输出审查报告至 doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-aa099f2a-dsh.md。
  ```

---

## 风险与遗留

1. **构建机 PATH 污染源根因**：
   - 本次调查查明，宿主机环境变量 PATH 中存在第三方 Poppler 原生依赖路径（`...\dependencies\native\poppler\Library\bin`），该路径下包含带有 ICU78 后缀的 `icuuc.dll`。PyInstaller 在为 `Qt6Core.dll` 解析依赖时按系统 PATH 寻路，导致该第三方 DLL 被错误抓取入包。
   - 本次在 `build_sidecar.ps1` 中实施了局部环境变量净化，并在 `core_sidecar.spec` 中增加了二进制闭包过滤与断言。长期建议在构建流水线中统一规范构建环境变量隔离机制。
2. **主线 Runner 债务隔离**：
   - 验证过程中精确复用了固定 commit `2af6b71aa06979b822e543b221aaf3a2d5f01abe` 的 runner 代码副本，未借机修改或合并关联任务 `M2-RUNNER-SNAPSHOT-DEBT`，保持依赖与责任边界清晰。
3. **开发态构建触碰状态**：
   - `apps/` 目录经 `git diff HEAD -- apps` 逐 blob 比对严格为 0 内容差量，`git status` 严格清洁，生产只读保护 100% 达成。
