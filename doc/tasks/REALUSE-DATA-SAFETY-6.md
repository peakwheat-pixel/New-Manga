---
id: REALUSE-DATA-SAFETY-6
title: 自查收尾——进度刷新、旧库迁移策略、derived 双份、安装脚本隔离
kind: quality
governance_version: 3
status: done
approval: user_authorized_2026-10-30_self_audit_remaining_items
suggested_owner: dsh
owner: dsh-lead
reviewer: safety6-reviewer
depends_on:
  - REALUSE-DATA-SAFETY-5
base_commit: 841cbdc4b
branch: task/REALUSE-DATA-SAFETY-6
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-6
integration_commit: 011b19bbf
delivery_head: fb5065013
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REALUSE-DATA-SAFETY-6
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-6.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-6-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-6-*.md
  - apps/desktop-avalonia/src/**
  - apps/desktop-avalonia/tests/**
  - src/**
  - scripts/**
  - verification/REALUSE-DATA-SAFETY-6/**
---

# REALUSE-DATA-SAFETY-6：自查收尾的 4 条

## 来源

REALUSE-DATA-SAFETY-5 的核对结论：9 条里修了 6 条，剩下 4 条明确记录为「仍成立、未修」。本 Task 承接它们。

## 逐条说明（依据见 DEFECTS.md 复核记录）

1. **MA-09 阅读进度刷新**：`HostController.SaveReadingProgressAsync` 存在，但阅读器保存后与导入后的界面刷新未接。用户保存进度后回到书架/阅读器看到的仍是旧值。
2. **MA-11 旧库迁移**：`src/infrastructure/sqlite/upgrade_legacy_layout.py` 已实现，但真实数据根没有跑过（无 `upgrade-legacy.log`），旧壳仍可写另一份 `data/library.db`。**这条涉及用户数据与旧壳共存策略，需要用户裁决后才能动**。
3. **MA-19 `derived/` 全尺寸副本**：managed 原图与 derived 各一份，磁盘 2×，无自动清理。改动涉及资源通道设计，不能贸然删。
4. **MA-20 安装脚本隔离**：`apps/desktop-avalonia/scripts/install.ps1` 的 `$DataRoot` 默认就是真实 `%APPDATA%`，验证/安装流程可在未隔离情况下触碰真实数据。

## 验收标准

- [x] **AC1 MA-09 进度刷新**：保存进度后书架与阅读器显示一致的当前进度；导入后进度信息不陈旧。有测试证明刷新确实发生（不是只看代码）。 <<MET>>
- [x] **AC2 MA-19 derived 冗余**：给出 derived 是否必需的结论（读资源通道代码 + 真实数据印证），能安全去掉冗余副本或明确记录为什么必须保留。 <<MET>>
- [x] **AC3 MA-11 / MA-20 需要裁决的部分**：这两条都涉及用户数据或部署流程，**先写清楚可选方案与各自影响，交用户/DSH 裁决**，不擅自实施。 <<MET>>

## 实施摘要（2026-11-01，delivery_head `fb5065013`）

### AC1（MA-09）：已接线的刷新路径

根因：进度保存早已存在，缺的是"保存结果回到书架"。详情见 [AC1 证据](../../verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md)。

- `ReaderOverlayViewModel`：新增 `ReaderProgressSavedEvent` + 可选回调 `progressSaved`；**仅当 Core 真正提交（`IsSaved`）** 才回调；`CloseAsync` 以 `isClosing: true` 触发一次权威重读；`LastSaveResult` 保留类型化结果供测试/证据使用。
- `LibraryViewModel`：注入回调；同章节镜像 `DetailProgressText`（与投影路径共用 `FormatSavedProgress`）；`IsClosing` 时 `LoadProgressAsync()` 重读 Core 投影；`ReloadAfterImportAsync()` 末尾补 `LoadProgressAsync()`；新增 `ProgressRefreshes` 计数用于证明刷新真的发生。
- 深链保护：阅读浮层打开的是别的章节时，不改写书架当前章节的进度行。
- 性能取舍：翻页保存用本地镜像（不额外读投影，避免每翻一页对整章每页做 resolve+sha256）；关闭浮层/导入各做一次权威投影重读。

### AC2（MA-19）：结论为"现阶段必需，不改代码"

见 [AC2 结论文档](../../verification/REALUSE-DATA-SAFETY-6/ac2-derived-conclusion.md) 与 [真实数据只读盘点](../../verification/REALUSE-DATA-SAFETY-6/ac2-derived-realdata.json)。

- 代码面：`handle_resolve_page_resource` 按确定性键 `page-original-{page_id}` 把 managed 原件逐字节发布进 derived 根（`core_service.py:3189-3252`、`render_preview.py:115-156`）；Host 按作用域根供字节（`HostRuntime.cs:511-569`）；`preview_namespace` 把 catalog 身份绑定在 **derived 根**身份上（`catalog_store.py:198`、`core_service.py:5757/5798`）；现网 catalog 169 行全部 `derived-read-only`、0 行 `managed-read-only`。
- 数据面（只读）：managed 169 文件 100,434,899 B，derived/pages 169 文件同字节；169/169 成对同尺寸；样本页 sha256 完全一致；derived 无 `previews/`，仅 315 B 命名空间锁。
- 约束面：AD-003 §3.2 明文"未实现新源读取前，不得以消除双份为由删除现有 `derived/` 或 managed 文件"。
- 同时更正 MA-19 记录的两处口径：derived 已有启动期 GC（孤儿文件 + 死行，`render_preview.py:158`）；删副本会按同键自动重建，省不了空间。

### AC3（MA-11 / MA-20）：只出方案，未实施

见 [AC3 方案](../../verification/REALUSE-DATA-SAFETY-6/ac3-options.md)。

- MA-11：真实数据根上迁移是**幂等空操作**（当前根 `library.db` 1 书/1 章/169 页/1 进度且更新，旧 `data/library.db` 1 书/0 章/0 页/0 进度；`data/backups`、`data/managed/temp` 为空 → 无可合并内容 → 无 `upgrade-legacy.log`）。真风险是旧壳仍可写旧根。方案 A0（保持）/A1（只读封存）/A2（显式迁移，仅灾备）/A3（以旧库为准，**不建议**）/A4（阻断旧壳写入 + 提示）。
- MA-20：`install.ps1:4` 默认真实 `%APPDATA%`；不加 `-SkipBackup` 会在真实 `backups/` 写整根 zip（`install.ps1:20`）；`install-verify.ps1:15` 的 `data_root_untouched=$true` 是**硬编码断言而非测量**。方案 M-1（默认隔离 + 实测断言，推荐）/M-2（保持真实根 + 二次确认）/M-3（仅文档化，不推荐）/M-4（验证流程强制隔离）。
- 本 Task 未运行迁移、未改部署脚本、未执行安装/卸载/备份/恢复，未移动/删除/改名任何真实数据。

## 禁止范围

- 不删除任何用户数据；不擅自执行迁移；不改冻结契约；不 push 远端。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 新增用例 | `dotnet test --filter "FullyQualifiedName~LibraryProgressRefreshTests"` | net9.0 / Avalonia headless | **PASS 5/5**（同动作刷新、关闭后 Host 重读、真实导入坞刷新、拒绝不伪造、深链不串章） | `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt` |
| AC1 回归 | `dotnet test tests/NewManga.App.Tests` | net9.0 | **PASS 394 通过 / 0 失败 / 7 跳过（共 401）** | 同上（日志第 2 段） |
| AC1 负向对照 | 临时移除构造函数回调接线后重跑 | 同上 | **3/5 失败**（`CommittedSave_*`、`ClosingReader_*`、`Import_*`），另 2 例按设计仍通过 → 证明测试真的覆盖"刷新已接线" | 同上（日志第 3 段） |
| AC1 构建 | `dotnet build NewManga.sln` | net9.0 | **PASS 0 警告 / 0 错误** | 本地实测；实现文件见 Canonical Evidence |
| AC2 代码核对 | 读资源通道代码（resolve/publish/catalog/namespace/Host 读路径） | 只读 | **结论：derived 现阶段必需**，不改代码 | `ac2-derived-conclusion.md` §2 |
| AC2 真实数据印证 | 只读枚举 + 只读 SQLite（仓外副本）+ 样本 sha256 | 只读，无写入 | **managed 169/100,434,899 B ≡ derived/pages 169/100,434,899 B**；样本 sha256 双向一致；catalog 169 行全 `derived-read-only` | `ac2-derived-realdata.json` |
| AC3 方案 | 写方案与影响，不实施 | — | **已出方案**：MA-11 五选、MA-20 四选，附影响与建议；**未实施** | `ac3-options.md` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md` | worktree | 见「治理检查」一节（既有债务，如实记录） | 本节 + handoff |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-READER-VM | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs` | `fb5065013` | `603ed15e600aefaf91fa04984fb4844e2daa32b459e88dca616ab586151fe865` | CANONICAL |
| E-AC1-LIBRARY-VM | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs` | `fb5065013` | `2b6f2525f1724cecaf0e0a5de6cf18560ceb28ef6d71784cdb7ba8c2c53066f6` | CANONICAL |
| E-AC1-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs` | `fb5065013` | `135de02c1856c5989269a70f8544925d03c4a7e3127642b0b75e88f3cff260a2` | CANONICAL |
| E-AC1-TEST-FAKE | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs` | `fb5065013` | `6c63c2c5fc933eea8fab51ba792246d6131e997ce31bccb248eb32d2affe4a11` | CANONICAL |
| E-AC1-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md` | `fb5065013` | `e913e2dd01d8e8f8af6cc54b7d1126eb5993b64d0b0976f0bf2f0d44669866e8` | CANONICAL |
| E-AC1-LOG | AC1 | `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt` | `fb5065013` | `2eab80965115b0d2feb5ca9fb9a4903682311e63b78a3ac1be9e1a517cc0a63c` | CANONICAL |
| E-AC2-DOC | AC2 | `verification/REALUSE-DATA-SAFETY-6/ac2-derived-conclusion.md` | `fb5065013` | `1edb35f14a3676cecaad7c8d2b78ed75af2ca3ae43b43c20967bb85e73c77c47` | CANONICAL |
| E-AC2-DATA | AC2 | `verification/REALUSE-DATA-SAFETY-6/ac2-derived-realdata.json` | `fb5065013` | `22f9793f071de4173aed7bad4017d54edf8261692a14242694a4a17bd2da0ddc` | CANONICAL |
| E-AC3-DOC | AC3 | `verification/REALUSE-DATA-SAFETY-6/ac3-options.md` | `fb5065013` | `9c27d477301e090e79cb48a3fafa892b86ddfce80e41723826cd2acfef5c950b` | CANONICAL |
| E-EVIDENCE-INDEX | AC1/AC2/AC3 | `verification/REALUSE-DATA-SAFETY-6/README.md` | `fb5065013` | `d199f4843dea5c3c6b25ee293f1b54b93ce58bdb82fa9960c4eb6676041ca3ff` | CANONICAL |
| E-GOV-CHECK | Gate（治理检查） | `verification/REALUSE-DATA-SAFETY-6/governance-check.txt` | `b94dc3d86` | `bc97d7a78e4db6e84899c415bc82a27e45b8874c16b31e71baf571c69e7b592e` | CANONICAL |
| E-RESOURCE-MANIFEST | Resource | `verification/REALUSE-DATA-SAFETY-6/resource-manifest.json` | `82e86e97b` | `133943d78481e43c0bb4d4766cf7691ca00fe7358506c249c50130b629befd99` | CANONICAL |

## Resource Manifest

资源收口记录：`verification/REALUSE-DATA-SAFETY-6/resource-manifest.json`（schema_version 1）。

- worktree：PRESERVE_REFERENCED（分支 `task/REALUSE-DATA-SAFETY-6`，未删除、未 prune）
- 用户数据根：PRESERVE_USER_DATA（全程只读，未写入 / 未删除 / 未迁移）
- 仓外临时副本：`tmp/REALUSE-DATA-SAFETY-6` 与 `tmp/safety6-review` 均为 DELETE_SAFE，已于 2026-11-01 核对绝对路径后删除（closeout_counts.deleted=2）

## 治理检查

- 命令：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md`
- **交付时（worktree 基于 `841cbdc4b`）：FAIL（2 errors, 2 warnings）—— 全部为既有债务，与本 Task 改动无关**。
  - 2 条错误原因：`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` 引用 `design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md` 与 `design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`，这两个文件当时只在 main 工作区未提交，任何干净 worktree 上都会红。修复面在 `doc/AD-003_*.md` / `doc/design/`，不在本 Task `allowed_paths`，未擅自修。
- **集成后（main 已入库两个 FLUENT 文档，提交 `6cab0b083`；本 Task 分支 `merge main` 后重跑）：PASS (2 warnings)** —— 2 条 warning 为既有提示（7 个非终态 Task、`REBASELINE_PLAN` 预算 80%）。集成环境 `main@011b19bbf` 实测 `PASS (2 warnings)`。
- 结论：交付时的 FAIL 已由 main 侧引用修复消除，**未伪造当时的 PASS**。

## 独立 Review

- 报告：[REALUSE-DATA-SAFETY-6-review.md](../reviews/REALUSE-DATA-SAFETY-6-review.md)
- Reviewer：`safety6-reviewer`（Agent Teams 共享任务 `task-3`，fresh context；未参与实现与返修）
- 被审 head：`0feff7a4c`（merge main 后）；实现内容 `fb5065013`
- 结论：**approved**（P0=0 / P1=0 / P2=3 open，不阻断集成）；AC1/AC2/AC3 均判 **MET**
- 复跑：build 0 警告 0 错误；新增用例 5/5；全量 394 通过 / 0 失败 / 7 跳过（401）；`check.ps1 -TaskPath` PASS (2 warnings)；负向对照独立复现 3 failed / 2 passed
- 独立性：2026-10-31 用户裁决口径（上下文独立）；Review 报告字节由 reviewer 写入，DSH 未改写

## Known P2（open，随集成保留，登记为后续项）

| ID | 级别 | 内容 | 建议处置 |
|---|---|---|---|
| R-001 | P2 | 关闭阅读浮层与在途保存并发时，镜像回调在 `ReaderOverlayViewModel.cs:377-379` 解引用已置 null 的 `_book`，抛出未捕获 NRE，且关闭时权威重读被跳过（reviewer 在仓外副本用 gate 门控用例真实复现，EXIT 1） | 下一轮小修：`await` 前局部固化 book/chapter/page 值；`CloseAsync` 在 `_isSaving` 时仍保证一次权威重读。属实现引入的并发缺陷，不涉及数据丢失（Core 已提交的保存不受影响） |
| R-002 | P2 | 证据 pin 哈希基准受 CRLF/LF 影响（worktree 一致 10/11、blob 一致 6/11；`E-GOV-CHECK` pin 与当前字节不符） | 加 `.gitattributes` 规则（`verification/** text eol=lf`）后重算 pin |
| R-003 | P2 | AC1 测试日志缺 EXIT 码与完整命令，负向对照为散文摘要（Q-009 口径） | 后续任务补全日志格式 |

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：`main@011b19bbf`（merge `task/REALUSE-DATA-SAFETY-6`，含 `36b666830` Review 报告提交）
- 集成验证：`check.ps1` PASS (2 warnings)；`dotnet build NewManga.sln` 0 警告 0 错误；`dotnet test NewManga.App.Tests` 见测试表
- AC 判定：AC1 `MET`、AC2 `MET`、AC3 `MET`（方案已出，裁决待用户）
- 未完成/待裁决：MA-11（A1/A4 等）、MA-20（M-1/M-4）需用户裁决后另立实施 Task；AC2 真正去重属资源通道契约演进（`G-CONTRACT` OPEN）
- 资源：worktree 保留（`PRESERVE_REFERENCED`）；仓外临时副本 `G:/CODEX/New Manga.workspace/tmp/REALUSE-DATA-SAFETY-6/` 与 reviewer 的 `tmp/safety6-review/` 可删，但按纪律不擅自清理（待用户/DSH 资源处置裁决）
- 已知 P2：R-001 / R-002 / R-003 见上表
