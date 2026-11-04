---
id: FEA-11
title: Source 变化 / 重定位 / 同步（scan/diff/plan + 页匹配/lineage + relink/repoint/resync + durable operation）
kind: implementation
governance_version: 3
status: proposed
approval: scope-r1（Codex，changes_requested P0=0/P1=8/P2=3）已由 DSH 逐项处置；待 `FEA-11-PREREQ-1` done + 独立 scope-r2 approved 后 Appointment/ready
suggested_owner: codex
owner: null
reviewer: null
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
  - tests/fea11/test_source_match.py
  - tests/fea11/test_source_plan.py
  - tests/fea11/test_source_sync.py
  - tests/fea11/test_source_relink.py
  - tests/fea11/test_source_operation.py
  - tests/fea11/test_source_lineage.py
  - tests/fea11/test_source_resolve.py
  - tests/fea11/test_v8_migration.py
  - tests/fea11/support/restart_core.py
  - tests/core/test_core_assembly.py
  - tests/storage/test_schema_migration.py
  - tests/storage/test_upgrade_schema_data.py
out_of_scope:
  - FEA-12 删除/回收站/GC；FEA-13 备份/迁移/数据根；FEA-14 子项；FEA-15 发布
  - 冻结契约字节（C-01b/C-05/C-08/C-13/C-14/C-15/C-16/FEA-01）与历史 closeout/证据
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
- 冻结契约：C-14、C-15 v1.1、C-16、C-05 v1.2、C-13（SC-D07/08）；不修改其字节。

## Acceptance Criteria

- **AC11-1（变化检测与阻断）**：启动/访问前检查、操作前强验证、定时扫描、目录 watcher 生产者/消费者四路各有调用证据；丢 hint/overflow 后可全量重枚举检测；相同 mtime/size 但字节变可发现；mtime/size 未变不作内容未变证明；强验证=稳定 lease+digest，不被缓存替代；Dirty 阻断依赖旧绑定的新写入而不是直接换 binding。定时扫描若本卡不做，须由 PREREQ/DSH 裁定并登记承接 Task，不得静默缺失。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-2（scan/diff/plan）**：目录/容器 diff 分类（未变/新增/缺失/变化/歧义）数量=明细；plan 绑定 book/页集合/旧新 SourceVersion/binding generation/用户决定/digest；预览与 apply 使用同一不可变 plan；plan 的合法预先持久化与 stale Apply 拒绝基线分别记录。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-3（页匹配，按 C-15 §3.2 冻结规则）**：同源同容器 digest 直接保续 与 容器变化后的跨版本匹配是两条路径；跨版本逐项验证 pixel profile 的 algorithm/decoder/version/params/尺寸/方向可比性与一对一唯一匹配；重复名/重复像素 occurrence 整组 needs_confirmation，不按 ordinal/locator 自动搬运人工成果；PDF 插页/ZIP 重排/目录重复内容不合并 occurrence；旧证据缺失/profile 不可比且不能按冻结参数重算时降为待确认/不可验证，禁止从新图伪造旧证据；以 FEA-09 真实导入旧库 fixture 验证。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-4（CAS/原子性/零写）**：明确三类代次（SourceVersion/binding_version/Host authorization generation + 人工 revision/Lock/draft 基线）的比较对象与事务内重读位置；单 plan/多项目原子单元与批次最后一项冲突时整批回滚唯一口径；并发 apply 仅一个成功、源/绑定/范围/决定/授权各自漂移、授权撤销/失联、第三区域 BaseRevisionId 冲突、DB 失败均有断言；stale Apply 零业务写（比较 pages/bindings/source rows/regions/text/current/revisions/保护/进度/operation receipt，不偷偷发布部分新代次）；拒绝审计落盘若需要须 DSH 明确与 A10 零写边界。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-5（同步应用/守恒/lineage）**：未变且唯一对应页保留 PageId/用户顺序/人工版本/进度/保护；新增页新 PageId 且顺序由 plan 明示；缺失页 tombstone 可找回（问题/人工修改保留，不连带删除）；变化页新 binding generation、旧区域/旧 revision 的 lineage 映射可恢复且隔离（新图编辑/渲染/导出/Run 目标读取不套旧坐标）；手动迁移新 RegionCandidate/revision、BaseRevisionId 与 Lock 检查，第三项失败整批回滚；Prepare 后同步→旧 Accept/结果 apply 被阻止（结果留 candidate）、旧 edit token 不写新 binding；不自动改写已接受 Run 快照。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-6（relink/repoint/resync）**：三操作分列 preview、命令/确认文案、身份/版本断言；relink（同一物理文件改名/移动）保留 EntryId/PageId/人工版本/区域/进度；repoint（改指向另一文件）改 EntryId、内容已变须走 resync 确认；resync（容器替换/重排/增删页）走页匹配与确认；仅当前/全部引用由用户选择且只更新预览中确认的集合，确认前引用集合变化须重新预览；其他项目 accepted binding/人工/进度不误改（诊断字段变化单列允许）；跨卷重新验证；同 bytes 不同物理文件不自动合并权限/identity；容器成员重排不改变已绑定页用户顺序（SC-S11）。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-7（缺失/无备份与诊断出口）**：原文件不在且无备份时保留元数据/人工修改并诚实显示缺失；管理诊断读取 missing/needs_confirmation/tombstone 走既有 V/R 可见性区分（C-05 P8），不为"显示缺失"暗改可见性契约、不扩 V(p,t)；reader 返回 typed 失败；不以新源或 derived 文件冒充旧源证据。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-8（durable operation 与双确认）**：C-15 的 Host durable authorization 保持在前（不得反序两阶段提交）；operationId 与请求 digest/目标集合绑定；每步 durable receipt、ACK/重放/恢复核对顺序冻结；相同 key+相同请求返回原结果、相同 key+不同 plan/范围拒绝、响应丢失重试不新增 binding；若需 Core 提交后 Host ACK，ACK 前读门控须持久化并在重启后维持（不能内存标志）；分别在 Host 持久化前后、Core 事务前后、ACK 前后杀进程，用真实新进程读取 journal/registry/DB 验证恢复；授权撤销、磁盘满、旧 registry snapshot、grant 过期/失联均有结果断言且不重放破坏性 OS 操作。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-9（生产链路/读图/回归）**：真实生产装配 Host→Core→DB→resolve→资源字节；先 resolve 旧绑定并读取字节→同步新绑定→生产 resolve/issue 读取新内容且旧资源键/已发布摘要不可变（资源版本选择由 PREREQ 冻结，不覆盖同键旧图）；验收至 Host/API（真实 IPC），不含用户可达 UI（UI 后续独立切片承接，不得宣称用户流程完成）；源原始 hash/mtime/文件数前后守恒、应用不写源；managed 五读路径/既有命令回归；缺能力/撤销/预算/密码错误 fail-closed；pytest/.NET 全量不减少且 skip 原因逐项记录。<<PARTIAL: 待 scope-r2 冻结逐项断言>>
- **AC11-10（范围/冻结/证据/资源）**：逐项 evidence pin 与范围 diff；v1–v7 迁移字节、冻结契约、FEA-08/09/10 closeout/证据不变；新迁移失败可回滚、旧端拒写新 schema；独立 Review + DSH 集成；Handoff+EV+Resource Manifest；证据/隔离根固定在 `G:/CODEX/New Manga.workspace/FEA-11/` 子目录，重复运行不复写 FEA-09/10 tracked 证据。<<PARTIAL: 待 scope-r2 冻结逐项断言>>

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

## 待 DSH 裁决（剩余）

1. PREREQ 契约 ID（建议新 C-17「Source 同步契约」）与 pins 扩展方式。
2. 定时扫描/目录 watcher 生产者归属：本卡或登记承接 Task。
3. relink/repoint/resync 的 wire/命令面与命令文案由 PREREQ 冻结后回填。
4. 若后续纳入 UI：由 ZCode 独立切片（精确 View/VM/端口与可达性 AC）。

## 验证矩阵

| AC | 断言（最少） | 测试/命令 | 证据 |
|---|---|---|---|
| AC11-1 | 四路调用证据；丢 hint 全量重枚举；同 mtime/size 字节变可发现；Dirty 阻新写；lease/digest 强验证 | `tests/fea11/test_source_scan.py`（TEMP/TMP=`workspace/FEA-11/fixtures/<case>/`） | EV-AC11-1 + 日志 |
| AC11-2 | 数量=明细；plan 绑定与 digest；预览/apply 同一 plan；stale 拒绝基线 | `test_source_plan.py` | EV-AC11-2 |
| AC11-3 | 直接保续 vs 跨版本；profile 可比/唯一；重复组待确认；旧证据缺失降级；FEA-09 旧库 fixture | `test_source_match.py` + 旧库 fixture | EV-AC11-3 |
| AC11-4 | 三类代次 CAS；并发/漂移/撤销；整批回滚；零业务写精确比较 | `test_source_sync.py` | EV-AC11-4 |
| AC11-5 | 守恒/顺序/保护/进度；tombstone；lineage 隔离；迁移 revision；Run/draft 交错 | `test_source_lineage.py` + `test_source_sync.py` | EV-AC11-5 |
| AC11-6 | 三操作身份/确认；当前/全部范围；其他项目不误改；SC-S11 顺序 | `test_source_relink.py` | EV-AC11-6 |
| AC11-7 | 诊断入口 missing/tombstone；V/R 区分；typed 失败；不伪造旧证据 | `test_source_resolve.py` | EV-AC11-7 |
| AC11-8 | 同 key/异请求；逐崩溃点 receipt/ACK/读门控；新进程恢复 | `test_source_operation.py` + `support/restart_core.py` | EV-AC11-8 |
| AC11-9 | 真实 IPC 至 Host/API；源字节/mtime/文件数守恒；managed 回归；fail-closed | `Fea11SourceIpcTests.cs` + 全量 | EV-AC11-9 |
| AC11-10 | 迁移 v1–v7 守恒/旧端拒写；冻结字节零 diff；EV/资源核销；独立 Review | `test_v8_migration.py`、check/pins/diff | EV-AC11-10 |

## Closeout Record

- 未开始（proposed；scope-r1 已处置；待 FEA-11-PREREQ-1 done + scope-r2 approved + DSH Appointment）。
