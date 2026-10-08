---
task_id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
reviewer: DeepSeek Harness（非作者 Reviewer）
author: Antigravity（Owner）；Integrator=Codex
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
reviewed_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
evidence_commit: 2c79645939635beef4a391f4bd9071ffeacd300b
supersedes: doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-aa099f2a-dsh.md（DSH r1；该文件未入库，本报告 §1 复述其 R-001..R-007）
decision: APPROVED
---

# Review（r2）：M2-PACKAGED-AC1-ICU-ISOLATION-FIX

**审阅范围**：唯一仓库 `G:/CODEX/New Manga` 的 linked worktree
`G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity`；
分支 `agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX`；
产品实现提交 `4499217d7b2249da16d5dbf27a3219a43876aac7`；交付证据/文档提交 `2c79645939635beef4a391f4bd9071ffeacd300b`；
Task base `5a72db9e3c5778ce4700b7d404250853e474c5de`；Owner start_head `df824182e813fc6d9045872da51d263f28db87f0`。

**审阅边界（不冒充现场执行）**：

- 本次为**只读静态审查**。我**未执行**任何构建、NSIS 打包、安装、Gate runner、pefile 扫描或 `git` 命令；下文所有 PASS/FAIL 判断均来自**提交内 artefact**（代码、日志、JSON）的只读核对，**不声称已重跑测试**。
- 本会话 shell 不可用（`pwsh` 沙箱初始化失败 `SetNamedSecurityInfoW (Win32 5)`，提权需审批且无审批通道），故 `git diff --name-only`、`git status`、SHA256 复算均**不可执行**，一律记 `NOT_RUN`/`UNKNOWN`（§4 V-3、V-14）。
- 提交链由 reflog 固定（`G:/CODEX/New Manga/.git/logs/refs/heads/agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX:1-9`）：
  `5a72db9e`（base）→ `3d6d8743` → `df824182` → `aa099f2a`（r1 实现）→ `46f50a09`（r1 文档）→ `b66c383d`/`59c0f316`（amend 序列）→ **`4499217d`（r2 实现）** → **`2c796459`（r2 文档/证据）**；`4499217d` 之后无生产代码提交。

## 1. r1 findings（R-001 ~ R-007）关闭核对

> r1 原始报告（`doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-aa099f2a-dsh.md`，reviewed_head=`aa099f2a`）**未入库**（worktree 与主仓 `doc/reviews` 内均无该文件，见 R2-006）；本节按该报告的原文要点逐条核对，并给出本次 r2 判定。

| r1 ID | r1 级别 | r1 问题摘要 | r2 修订与证据（文件:行） | r2 判定 |
|---|---|---|---|---|
| R-001 | P1 | 交付 installer 与 26 项验收 installer 是两份 hash（交付 `f76b91d6…`，验收 `a17a9708…`），交付物无任何完整 Gate artefact | fresh NSIS 产出的唯一 installer 在**构建日志自身**内记录了产物指纹：`raw/nsis-build.log:87-92`（`END_TIME 13:02:32`、`EXIT: 0`、`ELAPSED_SECONDS 326.8241483`、`INSTALLER_SIZE 579525817`、`INSTALLER_SHA256 f2a4e2e7…`）；随后 packaged gate **在该 installer 之后**启动：`raw/packaged-gate-execution.log:4-7`（`TESTED_INSTALLER_SHA256 f2a4e2e7…`、`START_TIME 13:04:04`），`raw/packaged/cleanstart-gate.json:4` 同为 `f2a4e2e7…`，`build-fingerprint.json:5-8` 亦同；`raw/packaged-e2e.log` 为完整镜像（58 行，含 `GATE: PASS`/`EXIT: 0`/`ELAPSED_SECONDS: 131.1276487`） | **CLOSED** |
| R-002 | P1 | 构建/验收发生在修复未提交的工作树（日志 `HEAD=df824182`），`source_head` 绑定不成立 | 四份现场日志均在首部实测输出 `GIT_HEAD: 4499217d…`：`raw/sidecar-build.log:2`、`raw/nsis-build.log:2`、`raw/dev-gate-execution.log:2`、`raw/packaged-gate-execution.log:2`；辅证 `raw/acceptance-bridge-purged-path.log:2`；`build-fingerprint.json:3` 的 `source_head` 与之逐字一致；reflog 证明 `4499217d`（epoch `1791434926`，约 12:48:46）**早于**首次构建 `START_TIME 12:50:06`（`sidecar-build.log:3`） | **CLOSED**（残留：工作树 clean 无法在本只读环境独立复核，见 §4 V-14） |
| R-003 | P2 | AC-1 缺脚本/原始输出、矩阵无 UNKNOWN 边界、断链引用 `closure-matrix.json` | 入库 `scan_pe_closure.py`（238 行，pefile `fast_load` + IMPORT/DELAY_IMPORT 解析、逐文件 SHA256）；原始输出 `raw/pe-scan-raw.json`（`total_pe_scanned 313`、`parse_error_count 0`、`icu78_static_consumers_in_bundle []`、`binaries_with_icu_imports` 仅 `_internal/PySide6/Qt6Core.dll`）；`closure-matrix.json` 已补入库（98 行）；矩阵对五个入口逐项标 `transitive_closure_verdict: UNKNOWN`、`dynamic_load_boundary: UNKNOWN`（`icu-closure-matrix.json:22-83`） | **CLOSED**（残留 P3 见 R2-003） |
| R-004 | P2 | 名称前缀式、来源无关的整包 ICU 移除，违背"未知不得靠全局移除解决/禁止全局删除 ICU" | `core_sidecar.spec:285-303` 将污染源限定为"源路径含 poppler **且** SHA256 == `39aec884…`"；`:330-361` 按 `sys.prefix`/`REPO_ROOT` 边界保留 venv/repo 内部 ICU，未知外部 ICU 走 `unclassified` → `raise SystemExit`（fail-closed，`:377-382`）；`build_sidecar.ps1:202-222` 仅净化匹配 `dependencies/native/poppler` 或 `poppler/**/bin` 的 PATH 条目（日志实测恰 1 条：`sidecar-build.log:5-6`） | **CLOSED** |
| R-005 | P3 | spec 内断言判别力不足（死代码）、PowerShell 断言覆盖与策略表述偏差 | `core_sidecar.spec:386-409` 两条守卫：①确认污染源未泄漏（对保留集合仍可判别，:388-393）；②Qt6Core 存在时禁止出现遮蔽名 `icuuc.dll`（:395-409）；`:483-490` 在 COLLECT 前对聚合 `all_binaries` 二次校验；`build_sidecar.ps1:246-259` 改为**递归**扫描 bundle 全布局的 `icuuc*.dll`/`icudt*.dll` 并显式 fail-closed（日志 `sidecar-build.log:578` 实测 0 命中） | **CLOSED**（残留：分类/守卫分支本次构建零命中，仅静态审查证据，见 R2-002） |
| R-006 | P3 | 报告耗时/PID/版本/哈希口径与入库日志不一致；CS-E2 描述与 runner 语义不符；`packaged-e2e.log` 仅有 2 行 | 口径已与日志一致：Sidecar `347.60`=`sidecar-build.log:584`；NSIS `326.82`=`nsis-build.log:89`；Dev `19.37`=`dev-gate-execution.log:71`；Packaged `131.13`=`packaged-gate-execution.log:58`；PIDs `[61404,11828]→[30296,38904]`=`packaged-gate-execution.log:36`；PyInstaller 统一 `6.22.3`；`REPORT.md:120` 已将 CS-E2 改写为"记录实测 SHA256，无期望值比较判据"，与 `run_clean_start_e2e.py:751-755` 语义一致；`raw/packaged-e2e.log` 现为完整镜像 | **CLOSED** |
| R-007 | P3 | 运行期依赖 System32 ICU 未记录 Windows 支持基线 | `REPORT.md:154-158` 显式声明基线 Windows 10 1809+ / Windows 11 并说明 `System32\icuuc.dll` 为 inbox 组件；`comparison-evidence.json:25` 同步记录 | **CLOSED**（残留：基线为**声明**，未在 1809 上做安装态验证，见 §5 剩余风险） |

## 2. r2 实现 diff 精读（4499217d 相对 r1 head）

**改动范围核验（行锚点算术 + 逐行读取）**：`packaging/m2ac5/` 目录文件清单与 base 侧一致（10 个文件，无新增/删除）；r2 相对 r1 的生产差量**仅两处**：
- `core_sidecar.spec`：392 → 500 行（+108）。其中 `_isolate_icu_closure` 由名称移除重写为来源分类（占据原 `270` 位置起，`271-409`，+99），`EXCLUDED` 顺移 `313→412`、`exes` 顺移 `328→427`，`COLLECT` `384→492`（+108）；即尾部仅新增 `483-490` 的聚合二次校验（含空行 +9）。其余行号完全对齐，未发现其它改动。
- `build_sidecar.ps1`：244 → 265 行（+21）。`197-234` 为定向 PATH 净化块（含 `finally` 恢复），`246-259` 为递归 bundle fail-closed 门禁；其余锚点（`[CmdletBinding()] 28`、`$ErrorActionPreference 61`、`Copy-MangaWeights 72`、`Copy-SfxWeights 124`、`$existingBundle 172`、`$gitHead 187`、`Write-Host HEAD 195`）与 r1 完全一致。

**重点 1（spec 来源分类与守卫）——核查通过**：
- 边界安全路径比较：`_is_within_dir`（`:271-277`）使用 `root + os.sep` 前缀比较，避免 `…\venv-evil` 之类前缀碰撞；`src_norm` 经 `os.path.normcase(os.path.abspath(...))`（`:337`，Windows 下统一小写与 `/`→`\`）。
- 污染源限定：`KNOWN_CONTAMINANT_SHA256`（`:280-282`）与 `_is_confirmed_contaminant`（`:285-303`）要求**源路径含 poppler 且文件 SHA256 命中**，非普通文件一律 `False`（不得绕过）；不存在宽泛的 `dependencies\native`/`codex-runtimes` 匹配。
- 分类与处置（`:333-384`）：`icuuc*`/`icudt*`/`icuin*` 候选 → venv/repo 内**保留**；已确认污染物**隔离**；其余**fail-closed**（`SystemExit` 并打印路径清单），不会静默删除未知 ICU。
- 判别力守卫（`:386-409`）：①保留集合中若仍含已确认污染物则失败（对"venv 内恰含同 hash 污染物"这一窄情形具备真实判别力，不再是死代码）；②Qt6Core 在场时禁止遮蔽名 `icuuc.dll`；`:483-490` 在 COLLECT 前对聚合闭包二次校验。
- PATH 与 COLLECT 的关系：PATH 净化仅覆盖 PyInstaller 子进程且 `finally` 恢复（`build_sidecar.ps1:200-234`），故 spec 的移除分支本次**零命中**（见 R2-002），其正确性由静态审查确认。

**重点 2（build_sidecar.ps1 精准净化与门禁）——核查通过**：正则 `(?i)[\\/]dependencies[\\/]native[\\/]poppler|(?i)[\\/]poppler[\\/].*bin`（`:208`）在本次实测命中且仅命中 1 条（`sidecar-build.log:5-6`），不误伤其它 PATH 条目；`finally { $env:PATH = $origPath }`（`:232-234`）保证异常路径也恢复；门禁为 `Get-ChildItem -Recurse` 全 bundle 扫描（`:252-258`），策略注释明确其是"防 System32 遮蔽的 fail-closed 约束"而非"未来永不需要 versioned ICU"的断言（`:250-251`），与 r1 R-005 的表述要求一致。

## 3. Findings（r2 新增）

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-001 | P2 | `doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md:75`；`doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md:63` | Task/Handoff 把"范围核验（`git status --short --branch; git diff HEAD -- apps; git diff --check`）"记为 **PASS**，但本次交付的 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**` 内**没有任何该检查的入库日志**（仅 `release.md`/`release-validation.log` 为释放期 Codex 记录），违反 `doc/09_COLLABORATION.md:176`①"运行日志必须带 EXIT 与 shell/venv 头并逐次入库"与③"NOT_RUN 不得记为通过"。影响：`src/**`、`apps/**`、`tests/**`、依赖/Schema 零改动这一结论在固定证据内**不可复核**（Reviewer 无 shell 亦无法代验） | `verification/**` 内无 `git diff --name-only`/`git status` 输出（全文检索仅命中 wrapper 的 `git rev-parse` 与释放期文档）；生产内容差量经 Reviewer 逐文件比对仅 `packaging/m2ac5/{core_sidecar.spec,build_sidecar.ps1}` 两文件 | 交付前补入库范围核验日志（同样的 `*_logged.ps1` 包装即可，含 `EXIT` 与 `git rev-parse HEAD`），或把该行如实改为 `NOT_RUN` 并说明由 Codex 集成 Gate 覆盖；Codex 集成时按 §6.9 复核路径范围 | open |
| R2-002 | P3 | `packaging/m2ac5/core_sidecar.spec:363-382`；`verification/.../raw/sidecar-build.log`（无 `icu-isolation:` 行），`:5-6,578` | ICU 分类/隔离/守卫分支在交付构建中**零命中**（无 `icuuc*` 候选），且函数在无命中时**不打印任何摘要**，日志无法自证"该检查已执行且通过"（目前只能由 `build_sidecar.ps1:578` 的 bundle 门禁间接旁证）。影响：无法用日志回答"若出现候选会怎样"，防御分支仅有静态审查证据 | `grep "icu-isolation|SHADOW-PREVENTED|ICU-PRESERVED"` 在 `sidecar-build.log` 零匹配；同日志仅有 PATH 净化与 bundle 门禁两行 | 在 `_isolate_icu_closure` 末尾无条件打印候选/保留/隔离/未分类计数（例如 `icu-isolation: candidates=0 preserved=0 isolated=0 unclassified=0`），使"已执行"可被日志证明 | open |
| R2-003 | P3 | `verification/.../raw/pe-scan-raw.json:1-5`；`scan_pe_closure.py:200-203` | ①原始扫描输出**不自带** `source_head`/时间戳/解释器，与其所绑定的提交只有间接绑定（五个入口 exe 的 SHA256 与 `build-fingerprint.json` 一致，构成强旁证）；②`bundle_wide_summary` 字符串**硬编码 "313"**，与实际一致，但后续 bundle 变化时会静默失真 | `pe-scan-raw.json:5,7` `total_pe_scanned`/`scanned_pe_count`=313；`:85-119` 仅 Qt6Core 一条 ICU 消费者；矩阵 `icu-closure-matrix.json:26,38,50,62,74` 的 hash 与 `build-fingerprint.json:14,19,24,29,34` 逐一相同 | 在 raw 输出中加入 `source_head`、`generated_at`、解释器路径；把 summary 改为由实际计数插值生成 | open |
| R2-004 | P3 | `REPORT.md:157`；`icu-closure-matrix.json:19` | "导出 542 个无后缀 C 接口符号（`ucnv_*`）"把 System32 `icuuc.dll` 的**导出总数 542**表述为 `ucnv_*` 符号数；应为"542 个无后缀导出，其中含 Qt6Core 所需的 20 个 `ucnv_*`"。影响：仅表述精度，不改变结论 | `pe-scan-raw.json:18-39` 列出 Qt6Core 需要的 20 个无后缀符号（含 `ucnv_open` 等）；542 为诊断期测得的导出总数 | 修正措辞为"542 个无后缀导出（含 Qt6Core 需要的 20 个 `ucnv_*`）" | open |
| R2-005 | P3 | `doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md:46`；`doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md:47` | Handoff/Task 用"零孤儿进程断言全 PASS"概括 AC-6，未按实际字段限定：`CS-Z3` 只断言 4 个 sidecar 归零，`python.exe` 为**记录项**且实测为 6（`raw/packaged/cleanstart-gate.json:288`）。影响：外读者可能误读为"宿主无任何幸存进程" | `run_clean_start_e2e.py:846-861`（断言 4 个 sidecar == 0，`python.exe` 仅记录并附注释）；`REPORT.md:150` 表述准确 | Handoff/Task 与 `REPORT.md:150` 对齐："4 个 sidecar 残留为 0；`python.exe` 计数为记录项（本次 6）" | open |
| R2-006 | P3 | `doc/reviews/`（无 `M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md`）；`REPORT.md:13`；`doc/tasks/...:90` | r1 Review 原文未入库：r1 findings 只能通过 Owner 的转述表（`REPORT.md:15-23`、Handoff §2）复核，`findings_disposition` 链在仓库内不完整；另 `REPORT.md:9` 与 Handoff:23 的"交付证据 Commit"只写"本次修订提交"，未给出 `2c796459…`，证据 commit 未在文档内固定。影响：可追溯性/治理项，非产品缺陷 | worktree 与主仓 `doc/reviews` 均无该 Task 的 r1 报告（basename 匹配 `*ICU*` 无结果）；Task:57 本已授权 DSH 写 `doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md` | 把 r1 报告与本 r2 报告一并入库，并在 REPORT/Handoff 写明 `evidence_commit=2c796459…` | open |

## 4. 逐项核验结果

> 所有"提交内命令"均取自 artefact 首部；**本次 Review 未重跑任何一项**。`结果` 列只反映"提交内证据是否支持其结论"。

| # | 核验项 | 提交内命令/来源 | 记录的环境/commit | 结果 | 证据（文件:行） | Skip / UNKNOWN 说明 |
|---|---|---|---|---|---|---|
| V-1 | 提交链与固定输入 | reflog、worktree `.git` | base/`4499217d`/`2c796459` | PASS | reflog:1-9；分支 ref = `2c796459` | — |
| V-2 | 生产改动仅 `packaging/m2ac5/**` 且仅 2 文件 | 主仓工作树 vs worktree 逐文件内容比对（无 git） | 主仓 `0c7c794c` / worktree `2c796459` | PASS（受限） | `core_sidecar.spec:271-409,483-490`；`build_sidecar.ps1:197-234,246-259`；目录仍为 10 个文件 | `git diff --name-only base..4499217d`：**NOT_RUN（无 shell）** |
| V-3 | `src/**`、`apps/**`、`tests/**`、依赖/Schema 零改动 | Task:75/Handoff:63 声明 `git diff HEAD -- apps`=0 | `4499217d` | **UNKNOWN / NOT_RUN** | 无入库日志（R2-001） | 无 git，Reviewer 亦无法代验；不得据此记 PASS |
| V-4 | fresh Sidecar 构建 | `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force`（`build_sidecar_logged.ps1:13`） | PyInstaller `6.22.3` / Python 3.12.3 / `GIT_HEAD 4499217d` | PASS | `sidecar-build.log:1-6,578,581,583-584`（`EXIT: 0`，`ELAPSED 347.6011288`） | 与 REPORT/Task 的 347.60s 一致 |
| V-5 | fresh NSIS 构建并自记录产物指纹 | `npx.cmd --yes @tauri-apps/cli@2 build`（`build_nsis_logged.ps1`） | Node `v24.15.0` / `GIT_HEAD 4499217d` | PASS | `nsis-build.log:1-5,83-92`（552.68 MiB、`EXIT 0`、`326.8241483`、`INSTALLER_SHA256 f2a4e2e7…`） | 构建日志自带产物 hash，闭合 r1 的"构建日志不记录产物"缺口 |
| V-6 | 隔离加载（AC-2 对照） | `Start-Process acceptance_bridge.exe`（purged PATH、`M2AC1_TEST_MODE=1`、`stdin=EOF`） | `GIT_HEAD 4499217d` | PASS | `raw/acceptance-bridge-purged-path.log:1-6`（`EXIT 0`，`0.4672841`） | 与 Handoff/REPORT 的 0.47s 一致；stderr 为空 |
| V-7 | Dev Gate 10 项 + 13 probe + 15/7 命令集合 | `run_e2e.py --exe … --skip-build --output-dir …/raw/dev`（`run_dev_gate_logged.ps1`） | `T1.1.1-impl-py312` Python 3.12.3 / `GIT_HEAD 4499217d` | PASS | `dev-gate-execution.log:2,34-48,54,58-68,70-71`；`raw/dev/e2e-gate.json:2-20`；`raw/dev-e2e.log:2,54,68-71` | 10 Gate 全 PASS、13 probe（E-00..E-09、D-01..D-03）全 PASS、production allowlist 15 项与 probe allowlist 7 项精确匹配；`ELAPSED 19.3714139` 与文档 19.37s 一致 |
| V-8 | Packaged Gate 26 项 | `run_clean_start_e2e.py --installer … --output-dir …/raw/packaged`（`run_packaged_gate_logged.ps1`） | `T1.1.1-impl-py312` / `GIT_HEAD 4499217d` / `START_TIME 13:04:04` | PASS | `packaged-gate-execution.log:2,4-7,11,23,36,55,57-58`；`raw/packaged/cleanstart-gate.json:4,12,15-289`（26 个 id 全 `PASS`）；`raw/packaged-e2e.log` 完整镜像 | 26/26 与结论一致；`ELAPSED 131.1276487` 与文档 131.13s 一致 |
| V-9 | 交付 installer 与验收 installer 精确一致 | 包装脚本先算哈希 + runner 运行期再算一次 | 两次一致 | PASS | `nsis-build.log:92`、`packaged-gate-execution.log:6,11`、`cleanstart-gate.json:4,39`、`build-fingerprint.json:8` 全部 `f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`；`nsis-build.log:87`（13:02:32）< `packaged-gate-execution.log:7`（13:04:04） | 双次独立测量 + 时序，r1 R-001 根因消除 |
| V-10 | Sidecar/NSIS/Fingerprint/Matrix 的 source_head | `GIT_HEAD`/`source_head` 字段 | `4499217d` | PASS | `sidecar-build.log:2`、`nsis-build.log:2`、`dev-gate-execution.log:2`、`packaged-gate-execution.log:2`、`build-fingerprint.json:3`、`icu-closure-matrix.json:5`、`closure-matrix.json:5`、`comparison-evidence.json:15` | `raw/pe-scan-raw.json` 本身无该字段（R2-003），经入口 hash 间接绑定 |
| V-11 | AC-1 闭包扫描（313 PE） | `python verification/.../scan_pe_closure.py` | 报告称 m2ac5-build venv | PASS（有界） | `raw/pe-scan-raw.json:5,7-11,45,85-119,2508,2512-2578`；`icu-closure-matrix.json:10,22-90` | 313/0 解析异常；唯一 ICU 静态消费者为 `_internal/PySide6/Qt6Core.dll`（`icuuc.dll`，20 个无后缀符号，`has_suffixed_symbols=false`）；`pyside6.abi3.dll:2508` `icu_imports {}`；全包 0 个 ICU78 静态消费者 |
| V-12 | 动态/传递边界如实标 UNKNOWN | 矩阵字段 | `4499217d` | PASS | `icu-closure-matrix.json:31-32,43-44,55-56,67-68,79-80`；`pe-scan-raw.json:46,53-54,60-61,67-68,74-75,81-82` | 表述未过度：结论限定为 313 个 PE 的直接静态/延迟导入事实 |
| V-13 | AC-6 零触碰/零残留字段准确性 | runner + gate JSON | `4499217d` | PASS（含表述修正项） | `cleanstart-gate.json:18,54,61,85,111,188,216,253,260,268-269,277,284-288`；`run_clean_start_e2e.py:806-861` | 断言 4 个 sidecar=0（`python.exe: 6` 为记录项）；`CS-Z1 changed_entries []`、`CS-Z4 files 4/changed_entries []`、`CS-Z2 files 4`；Handoff 措辞见 R2-005 |
| V-14 | 工作树 clean 与 runner 副本字节同一性（对 `2af6b71a`） | — | — | **NOT_RUN / UNKNOWN** | runner 副本行锚点与 r1 一致（`run_clean_start_e2e.py:51,53,740,753-754,867`；`run_e2e.py:48,497,646`），未观察到改写；日志首部含 `GIT_HEAD`/`TESTED_INSTALLER_*` | 无 shell → 不能算 SHA256、不能跑 `git status`；`release.md:19-20` 记录的 `2af6b71a` blob SHA256 未独立复核；由 Codex 在集成前以 `git status` 复核 |
| V-15 | reviewer 现场重跑 | — | — | N/A | — | 只读 Review，**未执行**任何产品/构建/安装/Gate/扫描命令 |
| V-16 | 文档/状态一致性 | Task frontmatter、Handoff、REPORT | `4499217d`/`2c796459` | PASS（含 R2-006） | Task:5,15,17,19,20,90,94-95；Handoff:6-8,22-23；REPORT:8-9 | `status: ready_for_review`/`CHECKPOINTED`/`implementation_head 4499217d` 与 handoff `delivery_head 4499217d` 相符；证据提交号未固定（R2-006） |

## 5. 结论

- **Architecture：PASS（无 P0/P1）**。改动仍严格落在 `packaging/m2ac5/**` 两文件，最小且可逆；隔离语义已从"名称前缀整包移除"改为**来源限定 + SHA256 证认 + 未知 fail-closed + 内部保留**，并补上可判别的守卫与 COLLECT 前二次校验；PATH 净化定向、`finally` 恢复；最终布局由递归 fail-closed 门禁与 26 项安装态 Gate 双重覆盖。
- **Verification：PASS（有界）**。r1 的两个 P1 已闭合（构建日志自带产物 hash、四份日志首部实测 `GIT_HEAD`、构建完成早于 packaged gate 启动）；Dev 10+13、Packaged 26/26、installer SHA256 全链一致；耗时/PID/版本口径与入库日志逐一对齐。**未解决项：1 个 P2（R2-001）+ 5 个 P3（R2-002..R2-006）**，均不构成产品缺陷或关键验证缺失。
- **决定：APPROVED（有界批准）** —— 0 P0/P1，可交 Codex 集成；集成时须：① 按 §6.9 复核 head/路径范围并**实测 `git status --short --branch`、`git diff --name-only 5a72db9e..4499217d`** 关闭 R2-001；② 在集成 commit 上按 §6.11 记录集成验证（本次 artefact 仅对 `4499217d` 有效）；③ 收口 R2-001~R2-006（随集成修订即可；若引入代码/契约变化按 §6.10 触发复审）。
- **剩余风险**：① `src/apps/tests`/`verification/M2-AC5` fixture 零改动仍**未知**（R2-001）；② ICU 分类/守卫分支本次**零命中**（R2-002），未来首次命中将表现为**构建失败**（fail-closed，需人工判定，属有意策略）；③ Windows 10 1809+ 基线为**声明**，证据仅来自 Windows 11 `10.0.26300`；④ runner 副本对 `2af6b71a` 的字节同一性未独立复核（V-14）；⑤ raw 扫描未自记录 head/时间戳（R2-003）。
