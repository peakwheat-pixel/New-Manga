---
id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
title: 安装态 Qt 与 ICU78 依赖闭包隔离修复
kind: bugfix
status: done
approval: user_authorized_release_20261008
suggested_owner: Antigravity
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-PACKAGED-AC1-DLL-DIAG, M2-DERIVED-GC-2]
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
branch: agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX
worktree: G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity
start_head: df824182e813fc6d9045872da51d263f28db87f0
allocated_head: 5a72db9e3c5778ce4700b7d404250853e474c5de
implementation_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
evidence_head: 2c79645939635beef4a391f4bd9071ffeacd300b
reviewed_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
review_report: doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md
gate_evidence: verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md
review_decision: approved
handoff_doc: doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md
execution_state: CHECKPOINTED
integration_commit: 65ba30144048a0b8daae22205c01f8049b44b8a7
allowed_paths:
  - packaging/m2ac5/**
  - doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md
  - verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**
  - doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md
---

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX：安装态 ICU 隔离修复

## 来源与目标

用户于2026-10-08单独释放；本轮针对 DSH r1 Review (R-001..R-007) 及用户指出的事实边界完成修订闭环。
[诊断报告](../../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)固定被审head=229c6c371d34234b65bbdd67fff73f341c60930f，
[Codex r3](../reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md) approved，诊断集成4431754845fc25795058534f21656705ef701cd6。
证据仅适用于固定产物/本机：包内icuuc.dll导出ICU78后缀符号，缺Qt6Core普通导入所需20个无后缀符号，
同名遮蔽系统ICU；native加载127、System32加载对照、同hash bridge自有副本改名对照支持因果。
目标：新架构Windows/Tauri安装态Qt启动正常，同时保持实际ICU78消费者可用（若存在）。

## Acceptance Criteria

- [x] AC-1：列出实际5入口产物的ICU78消费者、普通导入/导出、同名解析和加载闭包矩阵；每项证据或UNKNOWN，未知不得靠全局移除解决。（达成：scan_pe_closure.py 全量扫描 313 个 PE 二进制，直接静态/延迟导入表证明 5 入口无直接 ICU 依赖；入口传递闭包与动态/delay-load 边界如实标为 UNKNOWN；全包结论限定为 313 个 PE 文件中 0 个 versioned ICU78 静态消费者，仅 Qt6Core 依赖未后缀 icuuc.dll，见 icu-closure-matrix.json）
- [x] AC-2：仅打包范围内最小修复；新鲜产物在隔离/purged PATH下Qt6Core/Qt6Gui、acceptance_bridge真实加载成功，ICU78实际消费者仍正常；留原失败与修复后对照。（达成：修改仅 packaging/m2ac5/**，acceptance_bridge 在隔离环境下 0.47s EXIT 0，消除了基线 EXIT 1 / 0.8s ImportError 故障，见 acceptance-bridge-purged-path.log 与 comparison-evidence.json）
- [x] AC-3：fresh Sidecar五入口和NSIS构建成功，实际source_head、命令/解释器、产物hash/大小、EXIT/耗时绑定。不能用skip-existing替代fresh构建。（达成：fresh Sidecar 347.60s EXIT 0；fresh NSIS 326.82s EXIT 0；产物指纹绑定见 build-fingerprint.json）
- [x] AC-4：冻结dev完整10项Gate及13项probe通过；15 production commands、7 probe commands严格核对，不降低阈值。（达成：run_e2e.py 完整 10/10 Gate PASS，13/13 probe 场景 PASS，EXIT 0 / 19.37s，见 dev-gate-execution.log）
- [x] AC-5：新安装副本完整26项packaged Gate全PASS；CS-L1响应minor1.6、请求minor3兼容；两轮AC1完成、重启新PID、summary/reader恢复、PNG digest一致。旧FAIL不回填。（达成：run_clean_start_e2e.py 完整 26/26 场景全 PASS，EXIT 0 / 131.13s，被测 installer SHA256 与 fingerprint 严格一致，见 cleanstart-gate.json 与 packaged-gate-execution.log）
- [x] AC-6：用户源文件、人工修改、Lock、current/pinned Revision、Managed Copy及恢复能力保护；只写自有隔离fixture/输出，运行后无自身sidecar残留。（达成：CS-Z1/Z2/Z4 零写入或篡改断言全 PASS；CS-Z3 断言 4 个 sidecar 残留计数为 0，`python.exe: 6` 仅记录、不作零残留断言）
- [x] AC-7：固定实现head、逐项结果及Handoff齐全；DSH r2 APPROVED，Codex 集成及集成验证完成，见 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/integration-validation.log`。

## DSH Review r2：APPROVED

- Reviewed code head：`4499217d7b2249da16d5dbf27a3219a43876aac7`；Owner evidence commit：`2c79645939635beef4a391f4bd9071ffeacd300b`。
- Review：[M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md](../reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md)。结论 APPROVED（有界；0 P0/P1），DSH 未重跑构建或 Gate。
- R2-001 CLOSED：Codex 以 `git diff --name-only 5a72db9e..4499217d` 实测并归档完整范围核验，见 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review/r2-codex-scope-validation.log`。
- R2-002 ACCEPTED WITH LIMITATION：fresh 构建未发现 ICU 候选，spec 分类/守卫分支只有静态审查证据；未知来源仍 fail-closed，最终递归 bundle 门禁通过。为避免改动已验证生产实现而重跑全套 Gate，本轮不改生产策略。
- R2-003 ACCEPTED WITH LIMITATION：313 个 PE 的实际计数正确，五入口 SHA256 与构建 fingerprint 一致；raw scanner 未自带 HEAD/时间戳且摘要计数硬编码，仅作为本次一次性扫描证据使用。
- R2-004 CLOSED：报告已精确区分 542 个系统 ICU 导出总数与 Qt6Core 所需 20 个 `ucnv_*` 符号。
- R2-005 CLOSED：Task/Handoff 已限定 CS-Z3 断言为 4 个 sidecar 进程归零；`python.exe: 6` 是观测记录。
- R2-006 CLOSED：r1 原始报告位于 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md`；r2 报告已入库，并固定 Owner evidence commit。
## 允许修改范围

Owner仅上述allowed_paths。生产修改仅packaging/m2ac5/**，不更改已冻结验收口径；本次不借机合并runner debt。
允许读取src/apps/tests相关调用链，使用既有工具/依赖；构建可生成自己worktree内Git ignored产物、隔离模型缓存、安装fixture和lab，不修改跟踪的apps文件。
验证runner复用固定head=2af6b71aa06979b822e543b221aaf3a2d5f01abe的
packaging/m2ac5/run_clean_start_e2e.py、verification/M2-RC2/run_e2e.py：
精确字节副本放本Task verification根（相同深度），记录来源/SHA256、实测REPO定位；新--output-dir仅本Task/自有lab。
Codex可维护Plan/STATUS/索引和释放记录；DSH可写doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md及自己的审查证据。

## 禁止范围

禁止跟踪的src/**、apps/**、tests/**、其它verification历史证据、Schema/共享IPC/ACL、依赖清单/版本变更；禁止Legacy修复。
禁止改系统PATH/环境、System32、既有安装目录/用户数据、全局删除ICU；不部署、不推送、不合并main/master，不reset/clean/stash他人工作区。
共享启动代码或依赖升级若不可避免，暂停越界部分、在Task记录blocked原因，交Codex/用户重新冻结；不得先改再补授权。
只使用现成关联/构建机制，不新增通用registry或插件抽象。

## 测试要求

| 场景 | executed 命令或步骤 | 环境/判据 | 结果 |
|---|---|---|---|
| Sidecar 构建 | `pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force` | PyInstaller 6.22.3 / Python 3.12.3；fresh五入口，HEAD=4499217d | PASS (347.60s, EXIT 0, log: sidecar-build.log) |
| NSIS 构建 | `npx.cmd --yes @tauri-apps/cli@2 build` (CWD=apps/desktop) | Node v24.15.0 / Cargo 1.98.1；新 installer 绑定，HEAD=4499217d | PASS (326.82s, EXIT 0, 552.68 MiB, log: nsis-build.log) |
| 隔离加载 | `acceptance_bridge.exe` 启动测试 (purged PATH, M2AC1_TEST_MODE=1, stdin=EOF) | Windows System32 icuuc.dll 正常解析，0 遮蔽 | PASS (0.47s, EXIT 0, log: acceptance-bridge-purged-path.log) |
| Dev Gate | `run_e2e.py --exe .../m2rc1-desktop.exe --skip-build --output-dir .../raw/dev` | 完整 10 项 Gate + 13 项 probe 场景，T1.1.1-impl-py312 环境 | PASS (19.37s, EXIT 0, 10/10 Gate + 13/13 Probe 全 PASS) |
| Packaged Gate | `run_clean_start_e2e.py --installer .../setup.exe --output-dir .../raw/packaged` | 完整 26 场景，purged PATH 隔离环境，被测 installer hash 一致 | PASS (131.13s, EXIT 0, 26/26 场景全 PASS) |
| 范围核验 | `git diff --name-only 5a72db9e..4499217d`；`git diff --check 5a72db9e..4499217d` | 固定实现提交差量枚举；src/apps/tests/deps/Schema 零路径 | PASS；证据见 `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review/r2-codex-scope-validation.log` |

日志全量落库 verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**。

## 依赖、风险与阻塞

硬依赖均已集成且为base祖先：诊断done@4431754845fc25795058534f21656705ef701cd6；
GC-2 done@cea610ed3f3349f1d76361d151815445e991f7d7。
M2-RUNNER-SNAPSHOT-DEBT是关联blocked Task，仅用于本Task验证runner复用，不借机合并或关闭。
本次构建 source_head 与产物 hash 严格绑定见 build-fingerprint.json。
无本Task blocker。

## 交付与运行记录

- Handoff：见 [M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md](../handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d.md)。
- Review：DSH r1 R-001..R-007 已修复；DSH r2 对实现 head `4499217d` 作出 APPROVED（0 P0/P1）。R2-001 已由 Codex 范围日志关闭；R2-002/R2-003 作为非阻断证据局限记录并接受；R2-004/R2-005 文档措辞已修正；R2-006 由入库的 r1/r2 报告及固定 evidence head 收口。
- 实际产品测试：Dev Gate 10/10 + 13/13 PASS；Packaged Gate 26/26 PASS。
- 2026-10-08 Antigravity 完成来源限定闭包隔离修复、可判别守卫断言、fresh 双构建与全量 Gate 验收。
- start_head: df824182e813fc6d9045872da51d263f28db87f0
- implementation_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
- evidence_head: 2c79645939635beef4a391f4bd9071ffeacd300b
- reviewed_head: 4499217d7b2249da16d5dbf27a3219a43876aac7
- review_report: doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md
- status: done / ExecutionState: CHECKPOINTED；integration_commit=`65ba30144048a0b8daae22205c01f8049b44b8a7`。集成代码与 reviewed source head `4499217d` 在 `src/apps/tests/packaging` 零差量；未在 merge 后重跑产品 Gate，沿用 Owner 绑定于 `4499217d` 的 fresh 证据。R2-002/R2-003 为已接受的证据局限。
