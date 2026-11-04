---
id: FEA-11
title: Source 变化 / 重定位 / 同步（scan/diff/plan + 页匹配/lineage + relink/repoint/resync + durable operation）
kind: implementation
governance_version: 3
status: changes_requested
approval: **scope-r1 处置完成；PREREQ-1 done；scope-r2 approved（ZCode 全新上下文，P0=0/P1=0/P2=4 已处置）；DSH 冻结 scope + Appointment 2026-11-04（Owner=ZCode；实际 AC 数=10，AC11-1…10）**
suggested_owner: codex
owner: zcode（Appointment 2026-11-04；待认领）
reviewer: 独立上下文子 agent（fresh subagent，reviewer_kind=subagent；r1/r2/r3 三轮均未参与实现）；报告 doc/reviews/FEA-11-r1.md、FEA-11-r2.md、FEA-11-r3.md
depends_on:
  - FEA-09
  - FEA-10
  - FEA-11-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/SourceSyncJournalTests.cs
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-11-r2.md
  - doc/reviews/FEA-11-r3.md
  - doc/tasks/FEA-11-HOST-AUTH-1.md
  - doc/tasks/FEA-11-LINEAGE-1.md
  - doc/tasks/FEA-11-MATCH-1.md
  - verification/FEA-11/**
  - doc/tasks/FEA-11.md
  - doc/reviews/FEA-11-*.md
  - doc/handoffs/FEA-11-*.md
  - verification/FEA-11/**
  - src/application/sources/__init__.py
  - src/application/sources/model.py
  - src/application/sources/ports.py
  - src/application/sources/scanner.py
  - src/application/sources/matcher.py
  - src/application/sources/planner.py
  - src/application/sources/service.py
  - src/application/sources/runtime.py
  - src/application/sources/errors.py
  - src/infrastructure/sqlite/source_sync.py
  - src/infrastructure/sqlite/schema.py
  - src/infrastructure/sqlite/library.py
  - src/infrastructure/resource_channel/source_read_refs.py
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs
  - tests/fea11/conftest.py
  - tests/fea11/test_source_scan.py
  - tests/fea11/test_source_sync.py
  - tests/fea11/test_source_relink.py
  - tests/fea11/test_source_operation.py
  - tests/fea11/test_source_lineage.py
  - tests/fea11/test_source_resolve.py
  - tests/fea11/test_v8_migration.py
  - tests/core/test_core_assembly.py
  - tests/storage/test_schema_migration.py
  - tests/storage/test_upgrade_schema_data.py
out_of_scope:
  - FEA-12 删除/回收站/GC；FEA-13 备份/迁移/数据根；FEA-14 子项；FEA-15 发布
  - 冻结契约字节（C-01b/C-05/C-08/C-13/C-14/C-15/C-16/**C-17**/FEA-01/**M2-C1 rev 2.12**）与历史 closeout/证据
  - 共享组合根（App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln）
  - App View/ViewModel 与冻结 IHostController/RunContracts；未冻结的新 UI
  - 真实用户数据/AppData/外部卷/回收站；push；新依赖
---
# FEA-11：Source 变化 / 重定位 / 同步

状态：**proposed**；S11-001…011 已由 DSH 处置（见 `doc/reviews/FEA-11-scope-r1.md` + 本卡「scope-r1 处置」）；待 `FEA-11-PREREQ-1` done 与独立 scope-r2 approved 后 Appointment/ready。**不释放实施。**

## 目标

按 [FEA-00 提案](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §8.1–§8.4、§12.1（S3）、§15.5/A10，以及 C-14（SC-S01–S03/S07/S11）、C-15 §3.2/§4.2/§5–6、C-16 §4：实现 Source scan → diff → plan → 用户预览/确认 → 事务发布新 binding；区分 relink/repoint/resync；页映射与 tombstone/lineage；durable operation 与 Host/Core 双确认。全部先预览、歧义默认待确认、stale plan 零写、其他项目不被误改、源字节保留、同步后生产读图走新 binding。

## 依赖与前置

- FEA-09 done：referenced source 基础、`source_versions/source_entries/page_bindings`、SourceReadGrantRegistry/lease/scanner/reader/resolve、Host Sources。
- FEA-10 done：Prepare/Accept 两阶段、digest、candidate-only、durable receipt 原则（**不作为源操作真值**）。
- **硬前置 `FEA-11-PREREQ-1`**：冻结 v8+ DDL、plan/operation 状态机、命令/错误/能力/兼容、CAS 与跨存储发布边界、lineage 存储、resolve 版本选择；未 done 前本卡不得 ready/实施。
- 冻结契约：**C-17 v1.0（Source 同步契约，本卡最直接上游）**、C-14、C-15 v1.1、C-16 v1.1、C-05 v1.2、C-13（SC-D07/08）、M2-C1 rev 2.12（NO_INCREMENT）；不修改其字节。

## Acceptance Criteria

> 本卡实际 **10 条** AC（AC11-1…10）；历史提交信息中「12 AC」为笔误，以本表为准（scope-r2 P2-1 澄清）。

- [ ] **AC11-1（变化检测与阻断）**：启动/访问前检查、操作前强验证、定时扫描、目录 watcher 生产者/消费者四路各有调用证据；丢 hint/overflow 后可全量重枚举检测；相同 mtime/size 但字节变可发现；mtime/size 未变不作内容未变证明；强验证=稳定 lease+digest，不被缓存替代；Dirty 阻断依赖旧绑定的新写入而不是直接换 binding。定时扫描若本卡不做，须由 PREREQ/DSH 裁定并登记承接 Task，不得静默缺失。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: 定时扫描/watcher 生产承接 FEA-11-SCAN-1；本卡三路+消费者>>
- [x] **AC11-2（scan/diff/plan）**：目录/容器 diff 分类（未变/新增/缺失/变化/歧义）数量=明细；plan 绑定 book/页集合/旧新 SourceVersion/binding generation/用户决定/digest；预览与 apply 使用同一不可变 plan；plan 的合法预先持久化与 stale Apply 拒绝基线分别记录。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<MET>>
- [ ] **AC11-3（页匹配，按 C-15 §3.2 冻结规则）**：同源同容器 digest 直接保续 与 容器变化后的跨版本匹配是两条路径；跨版本逐项验证 pixel profile 的 algorithm/decoder/version/params/尺寸/方向可比性与一对一唯一匹配；重复名/重复像素 occurrence 整组 needs_confirmation，不按 ordinal/locator 自动搬运人工成果；PDF 插页/ZIP 重排/目录重复内容不合并 occurrence；旧证据缺失/profile 不可比且不能按冻结参数重算时降为待确认/不可验证，禁止从新图伪造旧证据；以 FEA-09 真实导入旧库 fixture 验证。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: 生产 scan 不写 pixel profile（unique_pixel 仅在有既有 profile 时生效），pixel 提取/旧库 fixture/独立 match 测试承接 FEA-11-MATCH-1 (R-012)>>
- [ ] **AC11-4（CAS/原子性/零写）**：明确三类代次（SourceVersion/binding_version/Host authorization generation + 人工 revision/Lock/draft 基线）的比较对象与事务内重读位置；单 plan/多项目原子单元与批次最后一项冲突时整批回滚唯一口径；并发 apply 仅一个成功、源/绑定/范围/决定/授权各自漂移、授权撤销/失联、第三区域 BaseRevisionId 冲突、DB 失败均有断言；stale Apply 零业务写（比较 pages/bindings/source rows/regions/text/current/revisions/保护/进度/operation receipt，不偷偷发布部分新代次）；拒绝审计落盘若需要须 DSH 明确与 A10 零写边界。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: r2：并发 apply/DB 失败/第三区域 BaseRevision 冲突证据缺失；多项目/末项回滚/撤销已补>>
- [ ] **AC11-5（同步应用/守恒/lineage）**：未变且唯一对应页保留 PageId/用户顺序/人工版本/进度/保护；新增页新 PageId 且顺序由 plan 明示；缺失页 tombstone 可找回（问题/人工修改保留，不连带删除）；变化页新 binding generation、旧区域/旧 revision 的 lineage 映射可恢复且隔离（新图编辑/渲染/导出/Run 目标读取不套旧坐标）；手动迁移新 RegionCandidate/revision、BaseRevisionId 与 Lock 检查，第三项失败整批回滚；Prepare 后同步→旧 Accept/结果 apply 被阻止（结果留 candidate）、旧 edit token 不写新 binding；不自动改写已接受 Run 快照。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: lineage native 写入与读隔离承接 FEA-11-LINEAGE-1 (R-009)>>
- [ ] **AC11-6（relink/repoint/resync）**：三操作分列 preview、命令/确认文案、身份/版本断言；relink（同一物理文件改名/移动）保留 EntryId/PageId/人工版本/区域/进度；repoint（改指向另一文件）改 EntryId、内容已变须走 resync 确认；resync（容器替换/重排/增删页）走页匹配与确认；仅当前/全部引用由用户选择且只更新预览中确认的集合，确认前引用集合变化须重新预览；其他项目 accepted binding/人工/进度不误改（诊断字段变化单列允许）；跨卷重新验证；同 bytes 不同物理文件不自动合并权限/identity；容器成员重排不改变已绑定页用户顺序（SC-S11）。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: r2：其他项目不误改/跨卷/成员重排/共享源只读场景证据不足>>
- [ ] **AC11-7（缺失/无备份与诊断出口）**：原文件不在且无备份时保留元数据/人工修改并诚实显示缺失；管理诊断读取 missing/needs_confirmation/tombstone 走既有 V/R 可见性区分（C-05 P8），不为"显示缺失"暗改可见性契约、不扩 V(p,t)；reader 返回 typed 失败；不以新源或 derived 文件冒充旧源证据。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: 管理诊断查询接线未在本卡实现>>
- [ ] **AC11-8（durable operation 与双确认）**：C-15 的 Host durable authorization 保持在前（不得反序两阶段提交）；operationId 与请求 digest/目标集合绑定；每步 durable receipt、ACK/重放/恢复核对顺序冻结；相同 key+相同请求返回原结果、相同 key+不同 plan/范围拒绝、响应丢失重试不新增 binding；若需 Core 提交后 Host ACK，ACK 前读门控须持久化并在重启后维持（不能内存标志）；分别在 Host 持久化前后、Core 事务前后、ACK 前后杀进程，用真实新进程读取 journal/registry/DB 验证恢复；授权撤销、磁盘满、旧 registry snapshot、grant 过期/失联均有结果断言且不重放破坏性 OS 操作。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: Host 自签完整 HostAuthorization 承接 FEA-11-HOST-AUTH-1 (P0-1)；ACK/Recovery 6 字段接线已修>>
- [ ] **AC11-9（生产链路/读图/回归）**：真实生产装配 Host→Core→DB→resolve→资源字节；先 resolve 旧绑定并读取字节→同步新绑定→生产 resolve/issue 读取新内容且旧资源键/已发布摘要不可变（资源版本选择由 PREREQ 冻结，不覆盖同键旧图）；验收至 Host/API（真实 IPC），不含用户可达 UI（UI 后续独立切片承接，不得宣称用户流程完成）；源原始 hash/mtime/文件数前后守恒、应用不写源；managed 五读路径/既有命令回归；缺能力/撤销/预算/密码错误 fail-closed；pytest/.NET 全量不减少且 skip 原因逐项记录。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: r2：IPC 为 Core 直连（未走 HostRuntime/dispatcher）；旧键/旧摘要不可变与 pre-sync 旧 binding 证据缺失>>
- [ ] **AC11-10（范围/冻结/证据/资源）**：逐项 evidence pin 与范围 diff；v1–v7 迁移字节、冻结契约、FEA-08/09/10 closeout/证据不变；新迁移失败可回滚、旧端拒写新 schema；独立 Review + DSH 集成；Handoff+EV+Resource Manifest；证据/隔离根固定在 `G:/CODEX/New Manga.workspace/FEA-11/` 子目录，重复运行不复写 FEA-09/10 tracked 证据。<<PARTIAL: 待 scope-r2 冻结逐项断言>> <<PARTIAL: 独立上下文 Review 待 Appointment>>

> 状态标记将在 scope-r2 approved 后按冻结断言细化；本卡禁止把未执行项标 MET。

## scope-r1 处置（DSH，2026-11-04）

- 全部接受 `doc/reviews/FEA-11-scope-r1.md` 的 S11-001…011（P0=0/P1=8/P2=3）：
  - S11-001：建立 **FEA-11-PREREQ-1** 硬前置（v8+ DDL/状态机/命令/错误/能力/兼容；v8 为候选版本，不预占）。
  - S11-002：AC11-6 分列 relink/repoint/resync，补 C-14 SC-S01–S03/S11 矩阵。
  - S11-003：AC11-3 改按 C-15 §3.2 冻结的跨版本证据规则与旧证据缺失降级。
  - S11-004：AC11-4/5 补 CAS 比较对象、事务单元、整批回滚、并发/漂移/授权撤销断言与零写口径。
  - S11-005：AC11-5 补 lineage 存储与读写隔离、在途 Run/draft/candidate 交错。
  - S11-006：AC11-8 补 Host durable 授权在先、durable receipt/ACK/读门控与逐崩溃点新进程恢复。
  - S11-007：新增 AC11-9 同步后生产 resolve 读新图、旧资源不可变。
  - S11-008：allowed_paths 改为逐文件清单（采纳报告候选）；AC11-7 明确管理诊断出口与 V/R 区分；AC11-9 验收至 Host/API、UI 后续承接。
  - S11-009：AC11-1 冻结四路；延期须 DSH 裁定并登记承接。
  - S11-010：逐 AC 断言+证据出口+资源计划（见下）；隔离根固定。
  - S11-011：PLAN DAG 错位已修正（FEA-C11-PREREQ-1 行拆回 + FEA-11/FEA-11-PREREQ-1 独立行）。

## 证据与资源计划

- Canonical Evidence：`verification/FEA-11/AC-MATRIX.md`（逐 AC 断言/命令/EXIT）、日志 `verification/FEA-11/logs/**`、IPC 输出目录、迁移负测；EV 行在实施后回填。Resource Manifest：fixtures/DB/Host registry/TRX/bin-obj 全部固定到 `G:/CODEX/New Manga.workspace/FEA-11/` 并登记 PRESERVE_REFERENCED；不清理、不复写 FEA-09/10 tracked 证据。
- 证据出口：EV-AC11-1…10（每 AC 独立 pin）；行为断言优先于数量；passed/failed/skipped 与原因分别记录。

## 待 DSH 裁决（scope-r2 后状态）

1. ~~PREREQ 契约 ID 与 pins 扩展~~ → **已闭合**：C-17 v1.0 FROZEN、pins 18/18（`1c519aec` 前完成）。
2. **定时扫描/目录 watcher 生产者归属** → **DSH 裁决（2026-11-04）**：本卡首版实现三路（启动/访问前检查、操作前强验证、watcher 消费者消费 hint 并全量重枚举），**定时扫描生产者与后台调度登记承接 Task `FEA-11-SCAN-1`（后续小卡，不在本卡写域/AC 强制）**；AC11-1 相应口径：缺定时/生产者须登记承接，不得静默缺失。
3. ~~relink/repoint/resync 的 wire/命令面与文案~~ → **已闭合**：C-17 v1.0 §5.1/§5.3 冻结命令面与确认语义。
4. 若后续纳入 UI：由独立切片（精确 View/VM/端口与可达性 AC），不在本卡。

## 验证矩阵

| AC | 断言（最少） | 测试/命令 | 证据 |
|---|---|---|---|
| AC11-1 | 四路调用证据；丢 hint 全量重枚举；同 mtime/size 字节变可发现；Dirty 阻新写；lease/digest 强验证 | `tests/fea11/test_source_scan.py`（TEMP/TMP=`workspace/FEA-11/fixtures/<case>/`） | EV-AC11-1 + 日志 |
| AC11-2 | 数量=明细；plan 绑定与 digest；预览/apply 同一 plan；stale 拒绝基线 | `test_source_scan.py`（plan 生命周期） | EV-AC11-2 |
| AC11-3 | 直接保续 vs 跨版本；profile 可比/唯一；重复组待确认；旧证据缺失降级；FEA-09 旧库 fixture | `test_source_scan.py`（diff 分类/匹配路径；旧库 fixture 待补） | EV-AC11-3 |
| AC11-4 | 三类代次 CAS；并发/漂移/撤销；整批回滚；零业务写精确比较 | `test_source_sync.py` | EV-AC11-4 |
| AC11-5 | 守恒/顺序/保护/进度；tombstone；lineage 隔离；迁移 revision；Run/draft 交错 | `test_source_lineage.py` + `test_source_sync.py` | EV-AC11-5 |
| AC11-6 | 三操作身份/确认；当前/全部范围；其他项目不误改；SC-S11 顺序 | `test_source_relink.py` | EV-AC11-6 |
| AC11-7 | 诊断入口 missing/tombstone；V/R 区分；typed 失败；不伪造旧证据 | `test_source_resolve.py` | EV-AC11-7 |
| AC11-8 | 同 key/异请求；逐崩溃点 receipt/ACK/读门控；新进程恢复 | `test_source_operation.py` + `support/restart_core.py` | EV-AC11-8 |
| AC11-9 | 真实 IPC 至 Host/API；源字节/mtime/文件数守恒；managed 回归；fail-closed | `Fea11SourceIpcTests.cs` + 全量 | EV-AC11-9 |
| AC11-10 | 迁移 v1–v7 守恒/旧端拒写；冻结字节零 diff；EV/资源核销；独立 Review | `test_v8_migration.py`、check/pins/diff | EV-AC11-10 |

## 实施证据与 AC 状态（DSH，2026-11-05）

实施由 DSH 接手完成（ZCode 中断、Codex 额度受限、ZCode CLI 损坏）。证据基线（`verification/FEA-11/logs/`）：
`pytest tests` 全量 **3042 passed / 0 failed / 10 skipped**；`pytest tests/fea11` 31 passed；全量 `.NET` **1355 passed / 0 failed / 75 skipped**；`NEWMANGA_FEA11_IPC=1` Host.Tests **3/3**（真实 Python Core）；`check.ps1` PASS；`verify_pins.ps1` **18/18**。

| AC | 状态 | 证据 / 缺口 |
|---|---|---|
| AC11-1 | PARTIAL | `test_source_scan.py`：访问前强验证/同 mtime-size 字节变可发现/过期 grant typed；**定时扫描生产与 watcher 消费者**承接 `FEA-11-SCAN-1`（DSH 裁决 2026-11-04） |
| AC11-2 | MET | `test_source_scan.py`：diff 数量=明细、scope all 冻结引用集合、plan 预览/确认/失效 |
| AC11-3 | PARTIAL | `test_source_scan.py`：直接保续、unique_pixel/added/missing 分类；无独立 match 测试文件与 FEA-09 旧库 fixture（缺口如实登记） |
| AC11-4 | PARTIAL | `test_source_sync.py`：stale 零写逐表快照、replay 冲突拒绝、事务发布 |
| AC11-5 | PARTIAL | `test_source_lineage.py` + `test_source_sync.py`：tombstone/lineage captured_v7·legacy_unverified 冻结/relink 保序 |
| AC11-6 | PARTIAL | `test_source_relink.py`：relink 保续、内容变拒绝、repoint 需 resync 确认、成功发布 |
| AC11-7 | PARTIAL | missing 观察/tombstone 保留在 scan/sync 路径；管理诊断查询接线未在本卡实现（缺口登记，UI 承接） |
| AC11-8 | PARTIAL | `test_source_operation.py` + C1 `SourceOperationTests`：durable 恢复/伪造摘要拒绝/ACK 门控/Host journal 状态机 |
| AC11-9 | PARTIAL | `Fea11SourceIpcTests`（`NEWMANGA_FEA11_IPC=1`）3/3：fail-closed、Host 发 grant + ScanSourceSync、**scan→plan→preview→confirm→ResyncSource→ACK→resolve v2 键**；`test_source_resolve.py` v2 键/同键不同 bytes 拒绝 |
| AC11-10 | PARTIAL | `test_v8_migration.py` 全起点迁移/旧数据守恒/旧端拒写；check/pins 18/18；冻结契约与 FEA-08/09/10 证据零 diff；**独立上下文 Review 待 Appointment** |

实现中修复的真实缺口：source-sync 命令边界持久化（plan/operation durable）、同步操作 grant→binding 绑定（`bind_imported_entry`）、scanner 页级 diff 投影（未绑定 unchanged 不破坏 decisions 1:1）、物理身份统一（`normalize_identity`）。

## Canonical Evidence

commit 暂为 pending（"不 commit/push" 约束；DSH 集成提交后回填）。sha256 为当前工作树 pin。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-AC11-MATRIX | AC11-1…10（逐 AC 状态与证据索引） | verification/FEA-11/AC-MATRIX.md | pending | b9de1dbf3002e821e6d3b6239a958524acf99018451ddc130dc03bfcdc39d9fd | CANONICAL |
| EV-AC11-C6-FINAL | AC11-1…10（终版门禁：pytest 3042 / IPC 3/3 / check / pins） | verification/FEA-11/logs/dsh-C6-final.log | pending | 11f1ddca340fd7f5e7623b4bcde46fc1a4f26776e3a7bd8c451c6882e0325ac9 | CANONICAL |
| EV-AC11-C6-GATES | AC11-1…10（早期门禁基线） | verification/FEA-11/logs/dsh-C6-gates.log | pending | efc283ec3f1acb54c899de33c97647126b9193e421b97de6e424db3bd783f30a | SOURCE_PIN |
| EV-AC11-PHASEB-MAIN | AC11-2/4/5/6/8（主套件回归） | verification/FEA-11/logs/dsh-phaseB-main.log | pending | 9046e7caa61c49724f7b3ddbd67edde787dd27791ecb7d1c27e61d2a572e7256 | SOURCE_PIN |
| EV-AC11-PHASEB-PROVIDERS | AC11-10（providers 回归） | verification/FEA-11/logs/dsh-phaseB-providers.log | pending | 63f3e76f9022247e78f5233d4553b987dacf1fceb5a0da00c19e73851070a4fb | SOURCE_PIN |

## Review r1 处置（DSH，2026-11-05）

Reviewer：fresh subagent（parent session-20e77fbf），只读 HEAD `5aadb3cd`；报告 `doc/reviews/FEA-11-r1.md`；**decision=changes_requested（P0=2 / P1=11 / P2=12）**。DSH 处置：**不批准**，进入有限返修。

- **P0（必修，阻断）**：R-001 Host durable authorization 空壳（生成完整 HostAuthorization 并注入 ApplyRequest、走 Registry 持久化授权、op id 绑定）；R-002 Host ACK/recovery 接线错误（6 字段 CompletionRequest、CommitReceipt canonical digest、失败不先落 acknowledged、补 capability handler、修 AC 证据矛盾）。
- **P1（必修，批准条件）**：R-003 新增页 grant→binding；R-004 fail_operation SQL / recover 状态机；R-005 无页 missing 的页级投影；R-006 relink 物理身份；R-007 scope=all 全源引用；R-008 COMMIT 前重验 grant/撤销；R-009 lineage native 写入与读路径；R-010 IPC 全链改 new_zip（新 binding/门控/新字节/旧键不可变）；R-011 AC11-4 补多项目/并发/末项/撤销/DB 失败/第三区域；R-012 AC11-3 pixel profile 写入与独立 match 测试/旧库 fixture；R-013 范围越界逐项窄批登记（见下）。
- **P2（登记/defer）**：文档矛盾、证据处跳过数解释、FEA-09 证据恢复步骤显式化、App.Tests flaky 登记等 12 项。
- **AC 状态修正**（按 Reviewer 判定）：AC11-3/4/5/6/8/9 由 MET 改 **PARTIAL/BLOCKED**（实现缺失或证据不足），AC11-2 可接受（保留），AC11-1/7/10 维持 PARTIAL（done 前须补）。
- **范围窄批登记**（R-013，DSH 作为 Integrator 逐项批准，因实施期间暴露的既有缺陷/集成必要）：`HostCommandDispatcher.cs`、`HostCommandModel.cs`、`src/application/importing/referenced/identity.py`、`src/application/importing/referenced/scanner.py`、`src/infrastructure/resource_channel/handle_resolver.py`、`import_source_refs.py`、`source_strict_read.py`、`tests/fea09/*`（12 个：identity/flaky/v2 键/迁移断言同步）、`tests/fea11/support/*`（2 个 ipc 脚本）、`tests/core/test_p09_fu2_import_pages.py`、`apps/.../SourceSyncJournalTests.cs`、`tests/fea09/test_referenced_resolve.py`；治理指针（STATUS/PLAN/TASK_LEDGER 的 FEA-11 行）与 `doc/tasks/FEA-11-SCAN-1.md`。allowed_paths 中不存在的条目（`test_source_match.py`、`test_source_plan.py`、`support/restart_core.py`）从验证矩阵移除（已在实施证据节更正）。
- 返修完成后：复跑全量门禁 → 请求新上下文复审（新 reviewed_head）→ DSH 集成 closeout。

### Review r1 返修进展（2026-11-05，DSH）

已修复（提交 `80b01229`/`33080869`/`ed0685e0`/`6b1ea62e`）：
- R-003 新增页 grant→binding（receipt.bindings）；R-004 fail_operation SQL + failed→recovered；R-005 无页 missing 页级投影；
- P0-2 Host ACK/Recovery 接线（6 字段 CompletionRequest、Core 成功后才落 acknowledged、真实 CommitReceipt digest、RecoverAsync 调 Core）；
- R-006 relink 物理身份（copy 拒绝，真实 rename 测试）；R-007 全源引用集合（reference_set_digest 覆盖全源共享）；R-008 COMMIT 前 live authorization 重验；
- R-010 真实 IPC 全链改 new_zip（changed→pending gate 拒绝→ACK→新 binding 新字节→源守恒，3/3 passed）。

**DSH 裁决承接**（不满足 done 的部分如实 PARTIAL）：
- P0-1（Host 自签完整 HostAuthorization 的 canonical 摘要与编排）→ 承接 **FEA-11-HOST-AUTH-1**（proposed）。
- R-009（lineage native 写入与读路径隔离）→ 承接 **FEA-11-LINEAGE-1**（proposed）。
- 承接依据：两者均需 Host 摘要规范/写域外路径（regions/render/export/Run），超出本卡冻结范围；DSH 作为 Lead/Architect 裁决登记，Review 复审时判定是否接受。

待办：R-011/R-012（AC11-4/3 证据补强）、P2 文档一致性、复跑全量门禁、新上下文复审。

## Closeout Record

- 实施完成（DSH 接手；Phase A/B/C1/C2/C3/C4/C5），Task → `in_review`（2026-11-05）。
- 待独立上下文 Review（不得自审）→ findings 处置 → DSH 集成验证 → closeout/EV/Resource Manifest。
- 已知缺口如实登记：AC11-1（定时扫描/watcher 生产承接 FEA-11-SCAN-1）、AC11-3（旧库 fixture/独立 match 测试）、AC11-7（管理诊断查询接线）、App.Tests 偶发 flaky。

## scope-r2 处置与 Appointment（DSH，2026-11-04）

- Review：`doc/reviews/FEA-11-scope-r2.md`（ZCode 全新上下文，baseline `1c519aec`）**approved P0=0/P1=0/P2=4**；全部接受。
- P2-1：实际 AC 数 = **10 条**（AC11-1…10；提交信息「12 AC」为笔误，本卡已澄清）。
- P2-2：out_of_scope/依赖节补列 **C-17 v1.0**、**M2-C1 rev 2.12（NO_INCREMENT）**。
- P2-3：PLAN 文末叙述行刷新（PREREQ done；FEA-11 ready）。
- P2-4：待裁决清单闭合/裁决——定时扫描与 watcher 生产者登记承接 Task **FEA-11-SCAN-1**（本卡实现三路 + watcher 消费者）；命令面已由 C-17 冻结。
- Appointment：`doc/reviews/FEA-11-appointment.md`（Owner=ZCode 立即启动，Codex 额度耗尽至 2026-11-05 00:51；Reviewer=独立上下文，不得自审）。
