---
task_id: P06
title: GC 分发迁移安全补证
reviewer: dsh（非作者；Owner=antigravity，role_exclusion 机器排除 owner，未参与 implementation/repair）
owner: antigravity
base_commit: b8f39d667ba5f23ba03a5bea4e61c5b930dbcd1a
declared_delivery_head: 2f2da8224fac4509129922069559738b639b47d8
reviewed_head: 4ed493a3f766ec126ab549b0d29f6d3886f9fdf6
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION
isolated_run_root: G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION
base_worktree: G:/CODEX/New Manga（用户 dirty 未被触碰）
date: 2026-10-15
mode: 只读审查 + 独立 Git/SHA-256/产物复核 + 原始进程证据重读；未修改被审分支或主仓任何文件
object_binding: VERIFIED
architecture_axis: PASS
verification_axis: PASS（机制验证；真实装机迁移验收按边界声明不属本 Task）
decision: approved_with_conditions
---

# P06 GC 分发迁移安全补证 — 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/P06-gc-distribution-migration-evidence`，`b8f39d66..4ed493a3`（Owner=**antigravity**，
  由 router 选出：score 122 与 codex 平票；归档 Plan 建议的 zcode 在 runtime 为 `UNKNOWN`、score 84 排末位）。
- Reviewer 实际执行 Git、SHA-256、隔离根产物与原始证据复核；**未采信 Owner 自述**。

### 0.1 实际执行的复核

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only b8f39d66..HEAD` | 13 文件，**全部落在 `doc/**` 与 `verification/P06/**`** |
| **AC5 零产品改动** | 过滤 `^(src\|apps\|packaging\|tests)/` | **空 —— 未修改任何产品实现或既有测试** |
| worktree 洁净 | `git status --porcelain` | **空（clean）** |
| 主仓零改动 | `git status --porcelain --untracked-files=no` | **19 项，与开工前完全一致** |
| **旧 runtime 真实性** | 隔离根 `old-runtime/worktree` 的 `git rev-parse HEAD` | **`ad75fadc2944983b4322f353176ba70cf0b0b7ae`**（与 GC-2 base 一致，确为协议引入前版本） |
| **构建产物真实性** | 对 5 个 exe 独立 `Get-FileHash` | **5/5 与报告一致**（`core_service.exe`=`ec8a03bd…`、`catalog_loader.exe`=`e88ce24b…`、`acceptance_bridge.exe`=`3419b179…`、`host_bridge.exe`=`c8549c36…`、`sfx_detect_probe.exe`=`433b17e3…`） |
| 构建/运行 exit | `old-sidecar-build.exit` / `runner_p06.exit` | **均为 0**；build log 结尾 `build_sidecar: OK (HEAD=ad75fadc…, pyinstaller=6.22.3)` |
| **AC2 进程证据** | 重读 `ac2-quiet-window-evidence.json` | 含真实 PID（holder 4568 / core 42952 / core 45944）、时间戳、stderr、判别结论 |
| **AC3 不变量** | 重读 `ac3-legacy-catalogs-evidence.json` | 两个 case 均 **`sha256_before == sha256_after`**（`1e30df7d…` / `32eb3b7e…`），`sha_invariant=true`；core exit=1；含真实 traceback |
| AC6 边界声明 | `REPORT.md` §5 | 明确写出「内核租约互斥与 Fail-Closed **机制验证**」**不等于**「真实多终端线上装机灰度迁移验收」 |
| 证据表 | 11 行 Canonical Evidence | `commit`/`sha256` 齐全，`class` 仅 `CANONICAL`/`SOURCE_PIN`（合法） |

## 1. AC 逐项结论

| AC | 判定 | 依据 |
|---|---|---|
| AC1 受控旧版本 runtime | **接受** | 旧 commit `ad75fadc` 真实取出；`build_sidecar.ps1` 真实构建成功（exit 0，PyInstaller 6.22.3）；5 个 exe 与权重打包完成；产物 hash 独立复算一致 |
| AC2 全退出迁移验收 | **接受** | (i) 持共享租约进程存活时，新版独占被 **Windows Sharing Violation** 非阻塞拒绝，stderr 明确 `namespace busy`，且**未删除任何 orphan/dead row**；(ii) `kill` 后 OS 释放内核租约，新版独占成功并完成首次扫描（`orphan_files_removed=1 dead_rows_removed=1`） |
| AC3 旧 catalog 策略 | **接受** | 两种情形（有行未绑定 / 旧 schema 缺 lifecycle 表）均 **fail-closed 拒绝启动（exit 1）**，且 **catalog SHA-256 前后完全不变** → 零静默迁移；显式 `initialize_namespace` 亦明确拒绝（`unknown history is never claimed`） |
| AC4 出货阻断清单 | **接受** | `RELEASE_BLOCKING_CHECKLIST.md` 落盘，可被 P20 引用 |
| AC5 不重做 GC2 | **接受** | 变更路径过滤后产品源码/测试**零改动** |
| AC6 边界与固定 head | **接受（Review 由本文件闭合）** | 边界声明明确；集成由 Coordinator 执行 |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P2（流程/schema）** | Task frontmatter 使用了**项目非法枚举**：`status: completed`（合法值为 `done` 等）、`resource_closeout_status: completed`（须为 `complete`）；`owner: Antigravity` 大写；`reviewer: null` 未反映已路由的 dsh。按 `tools/governance/check.ps1`，该 Task 作为当前 Task 时必然 FAIL | closeout 由 Coordinator 统一修正为 `done` / `complete` / `antigravity` / `dsh`，并通过 `check.ps1 -TaskPath doc/tasks/P06.md` 复验 |
| **F2** | **P2（流程，重复）** | 申报 `delivery_head=2f2da822`，分支实际 `HEAD=4ed493a3`。这是**第三次**出现同类不一致（P11、P10、P06）→ BL-7 需升级为模板级约束 | Reviewer 绑定实际 HEAD `4ed493a3`；closeout 冻结实际值 |
| **F3** | P3（证据纯度） | AC3 `case1a`（"unbound **no lock**"）的 stderr 首行却是 `[core.derived_gc] skipped: namespace busy (a managed peer holds a shared lease)`，与"无锁文件"场景语义不符 —— 说明该场景运行时仍受**前一进程遗留租约**影响，场景隔离不纯 | 结论不受影响：拒绝启动由 `FileNotFoundError`（锁文件缺失）与 **catalog SHA-256 不变**共同支撑。建议后续 runner 增加显式进程清理与场景洁净断言（BACKLOG） |
| F4 | P3（可读性/误读风险） | AC2 phase1 的 core **exit code = 0**（安全跳过而非失败退出），报告已标 `EXCLUSIVE_REFUSED_NON_BLOCKING_FAIL_SAFE`，但存在被误读为"未防护"的风险 | 建议在 `RELEASE_BLOCKING_CHECKLIST.md` 中显式注明：该场景 exit=0 是**预期安全行为**，判据是"零删除 + 明确跳过日志"，不是退出码 |
| F5 | P4 | `verification/P06/` 共 11 个文件全部已登记进 Canonical Evidence（无未登记文件），但本 Review 报告新增后将变成 12 个 | closeout 时必须把本 Review 登记为 CANONICAL，否则 `check.ps1` 的 evidence_dir 检查会报未登记文件 |

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `4ed493a3f766ec126ab549b0d29f6d3886f9fdf6`，并修正 F1 的全部 schema 字段；closeout 追加本 Review 的证据行（F5）。
- **C2**：P20 释放时必须引用本 Task 的 `RELEASE_BLOCKING_CHECKLIST.md`，并落实「安装前强制 kill 全部存量进程」的外部管控（AC2 机制成立的前提是旧进程全退出）。
- **C3**：F3/F4 转 BACKLOG，在 P20 或后续 runner 迭代中处理，不阻塞本 Task。
- 证据内容本身无需返修。

## 4. 能力边界

- 本 Review 覆盖**机制验证**的正确性与范围合规；**不代表**真实多终端装机灰度迁移验收（该边界由 Owner 明确声明，Reviewer 予以确认）。
- 所有 Git / SHA-256 / 产物 / 进程证据结论均由 Reviewer 在 live 环境实际复核；未重跑构建与 runner（其原始 exit 与日志已核验）。
- Reviewer 未修改被审分支、主仓、隔离根或任何证据文件；未 push。
