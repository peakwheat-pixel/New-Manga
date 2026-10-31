---
id: REALUSE-DATA-SAFETY-6
title: 自查收尾——进度刷新、旧库迁移策略、derived 双份、安装脚本隔离
kind: quality
governance_version: 3
status: in_review
approval: user_authorized_2026-10-30_self_audit_remaining_items
suggested_owner: dsh
owner: dsh-lead
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-5
base_commit: 841cbdc4b
branch: task/REALUSE-DATA-SAFETY-6
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-6
integration_commit: null
delivery_head: fb5065013
canonical_evidence_status: complete
resource_closeout_status: pending
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

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-6 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-6 | doc/handoffs/REALUSE-DATA-SAFETY-6-handoff.md | 本 Task 交付在分支 `task/REALUSE-DATA-SAFETY-6`；Review 与集成完成前保留，不 merge main、不 push |
| user data root | C:/Users/49745/AppData/Roaming/com.newmanga.desktop | PRESERVE_USER_DATA | 原地（未移动） | 见 `ac2-derived-realdata.json`（managed 169 文件 / derived 169 文件 / catalog 169 行） | 只读访问：目录枚举 + 只读 SQLite（在仓外副本上）+ 读取样本算 sha256；**未写入、未删除、未迁移** |
| temp db copy | G:/CODEX/New Manga.workspace/tmp/REALUSE-DATA-SAFETY-6/dbcopy | DELETE_SAFE | — | 含 library.db / catalog.sqlite / legacy data/library.db 的只读副本 | 仓外临时物，含用户数据副本，未纳入 git；核对完成即可删除，不需要归档 |
| prior worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | PRESERVE_REFERENCED | 同路径 | doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md | 前批 worktree 全部保留，本 Task 未触碰 |

## 治理检查

- 命令：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md`
- 结果：**FAIL（2 errors, 2 warnings）—— 全部为既有债务，与本 Task 改动无关**；详见 handoff 与下面的原文。
- 2 条错误原文：`失效的本地引用：doc\AD-003_REFERENCED_SOURCE_ARCHITECTURE.md → design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md`、`… → design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`。这两个文件只存在于 **main 工作区的未提交文件**中（`git ls-tree 841cbdc4b doc/design/FLUENT*` 为空），因此任何干净 worktree 上都会红；修复面在 `doc/AD-003_*.md` / `doc/design/`，均不在本 Task `allowed_paths`，故不擅自修。
- 2 条警告：7 个非终态 Task 的既有提示、`doc/REBASELINE_PLAN.md` 已达预算 80%（既有债务）。
- **不声称 PASS**；本 Task 自身引入的检查项（Task 卡语法、AC 标记、证据 pin、READY 节点一致性）在最终一轮运行中没有新增错误。

## Closeout Record

- Closeout date / DSH：待独立 Review 与集成后填写。
