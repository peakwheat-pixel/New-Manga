---
id: FEA-11-PREREQ-1
title: Source 同步契约前置（v8+ DDL / plan-operation 状态机 / scan-plan-apply-relink-repoint-resync 命令面 / CAS 与 lineage / resolve 版本选择）
kind: implementation
governance_version: 3
status: in_review
approval: **scope approved（r1 Codex，P0=0/P1=0/P2=4，S11P-001…004 已处置）+ DSH 冻结/Appointment 2026-11-04**；Owner=Codex 契约起草待认领；不预占 v8 版本
suggested_owner: codex
owner: codex（Appointment 2026-11-04；待认领）
reviewer: 契约最终字节 Review 待 Appointment（全新上下文；不得由起草者自审）
depends_on:
  - FEA-09
  - FEA-10
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: d23cf812ea430777ad3a30eeb5a6e38e46b4a836
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-PREREQ-1.md
  - doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C17.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/reviews/FEA-11-PREREQ-1-*.md
  - doc/handoffs/FEA-11-PREREQ-1-*.md
  - verification/FEA-11-PREREQ-1/**
  - tools/governance/verify_pins.ps1
out_of_scope:
  - FEA-11 生产实现（scan/diff/plan/apply/relink 代码与测试；另卡）
  - FEA-12/13/14 范围；既有 17 个冻结契约字节（除 M2-C1 经 DSH 授权的窄增量）
  - 共享组合根；真实用户数据/AppData/外部卷/回收站；push；新依赖
---
# FEA-11-PREREQ-1：Source 同步契约前置

状态：**proposed**；由 `doc/reviews/FEA-11-scope-r1.md` S11-001 要求建立；approved 并 done 前 FEA-11 不得 ready/实施。

## 目标

为 FEA-11 冻结实现所必需的契约面，使真实 IPC/Host-Core 链路与数据安全可验收：

1. **Schema（v8+ 候选，版本号由 DSH 冻结）**：`source_sync_plans` / `source_operations` 的表名、字段、索引、外键、约束、迁移版本与回滚策略；旧端（v7）拒写新 schema 的行为；v1–v7 字节守恒。
2. **状态机与存储归属**：plan 生命周期（draft/previewed/confirmed/applied/stale）、operation 生命周期（started/host-authorized/core-committed/acknowledged/failed/recovered）；哪些状态由 Core 持久化、哪些由 Host registry 持有；C-15 的 Host durable authorization 在先不可反转。
3. **命令面（closed shape）**：scan/plan/apply/relink/repoint/resync 与 operation 查询命令的请求/响应字段、取消/重试语义；是否扩展现有 Source 命令或新增；protocol minor 增量（沿用 additive minor 先例或 bump，由契约裁决）；旧面兼容。
4. **错误与能力**：错误 category/retryable/可诊断字段；capability 探测（扫/plan/apply/relink/repoint/resync 各自能力与不可用原因）；不泄露路径/密码/签名材料。
5. **CAS 与跨存储发布边界**：三类代次比较对象（SourceVersion/binding_version/Host authorization generation）与人工 revision/Lock/draft 基线；Core 事务内重读位置；单 plan/多项目原子单元与整批回滚口径；跨 Host/Core 无分布式事务时的安全依赖。
6. **lineage 存储**：旧 region/revision→binding lineage 与迁移来源的可恢复映射（旁表或既有快照扩展由 DSH 定）；未迁移旧区域的诊断/历史入口；新图编辑/渲染/导出/Run 目标读取的隔离规则。
7. **resolve 版本选择**：`page-rendition-{page_id}` 等资源键的版本选择方案，保证同步后生产 resolve/issue/读取新内容而旧资源键/已发布摘要不可变；不覆盖同键旧图。
8. **兼容与回退**：v8+ 迁移失败回滚、旧端拒写、备份/恢复（FEA-13）不因此获得范围；跨版本证据（pixel profile）可比性规则与旧证据缺失降级口径（引用 C-15 §3.2）。

## 交付物

1. 新契约提案 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（ID 建议 C-17，由 DSH 确认）与冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C17.md`；
2. 如经 DSH 授权：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 窄增量（rev 2.13?，须 DSH 明确章节/命令/错误/版本策略后才写；若不加增量须记录"无增量"决定）与错误/能力登记；
3. `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 追加 C-17 登记行（保留历史行，DSH 单点）；
3. `tools/governance/verify_pins.ps1` 加入新契约 pin（由 DSH 单点更新；冻结后 pins 17→18）；
4. 独立 Review 报告（全新上下文）与冻结记录；
5. Handoff + EV + Resource Manifest（证据在 `verification/FEA-11-PREREQ-1/`）。

## Acceptance Criteria

- [ ] **AC-P1（DDL/迁移冻结）**：两表 DDL/索引/FK/约束/迁移版本冻结决议可执行（含版本号、回滚、旧端拒写）；与 C-15 "不创建两表" 的预留声明一致；v1–v7 字节不变。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P2（状态机）**：plan/operation 状态机与 Host/Core 存储归属冻结，含 ACK 前读门控持久化与逐崩溃点恢复顺序。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P3（命令面）**：scan/plan/apply/relink/repoint/resync/operation 查询命令的 closed shape、字段、错误、能力探测与兼容策略冻结；不暗用导入 API。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P4（CAS/原子性）**：三类代次与人工基线比较对象、事务重读位置、原子单元与整批回滚口径冻结可断言。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P5（lineage）**：lineage 存储与读写隔离冻结，覆盖在途 Run/draft/candidate 交错规则。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P6（resolve 版本选择）**：同步后资源版本选择方案冻结，旧资源键不可变。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P7（证据/冻结）**：契约独立 Review approved；冻结记录 + pins 更新（17→18）可验证；check/PASS；不改既有 17 契约字节与 FEA-08/09/10 证据。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>
- [ ] **AC-P8（范围）**：不实现 FEA-11 生产代码、不越界 FEA-12/13/14、不新增依赖、不碰真实用户数据/AppData。<<PARTIAL: 契约提案与隔离验证已交付；待独立 Review 与 DSH 冻结>>

## 验证矩阵

| AC | 断言/命令 | 证据 |
|---|---|---|
| AC-P1 | DDL/迁移评审记录 + `tests/storage` 迁移链评审（实施后由 FEA-11 验证） | 冻结记录 + EV |
| AC-P2 | 状态机文档版本化；崩溃点顺序评审 | 冻结记录 |
| AC-P3 | 命令 closed shape/错误/能力表；M2-C1 增量（如授权） | 契约 + pins |
| AC-P4 | CAS/原子单元表；回滚口径唯一 | 契约 |
| AC-P5 | lineage 存储映射表；隔离规则表 | 契约 |
| AC-P6 | 资源键/版本选择方案；不可变旧键规则 | 契约 |
| AC-P7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1`（17→18 PASS）、`check.ps1` PASS、`git diff` 冻结字节零 diff | EV + pins 日志 |
| AC-P8 | 范围 diff；无依赖/用户数据变更 | Handoff + scope 日志 |

## 冻结可执行清单（S11P-004；AC-P1…P6/P8 的验收索引）

> 隔离验证脚本/输出放 `verification/FEA-11-PREREQ-1/` 与 `G:/CODEX/New Manga.workspace/FEA-11-PREREQ-1/`（Owner 记录 Resource Manifest）。真实升级链/全量回归/真实杀进程/IPC 字节归 FEA-11。

1. **P1（DDL/迁移）**：规范 SQL 全文（两表 + lineage 必要列/表）与版本/迁移登记规则（v8 不预占；逐 migration 事务；不动 v1–v7 SQL/checksum）；在隔离合成 v7 库执行拟议增量，记录 FK/唯一性/CHECK 负例、失败后 schema 与迁移元数据回滚判据、旧写者拒写判据；lineage 若需额外持久表/列须一并列入，不得写"未来再定"。
2. **P2/P4（状态/原子/CAS）**：持久状态转移表（前态、事件、守卫、写入方、持久确认点、后态）；Host durable 授权前后、Core 提交前后、ACK 前后各恢复/重放预期；三类代次（SourceVersion/binding_version/Host authorization generation）与人工 revision/Lock/draft 基线失配反例；整批最后一项失败的唯一结果。
3. **P3（命令/错误/能力/兼容）**：每条命令/DTO 的 required/nullability/type/枚举/范围与未知字段行为；错误 code/category/retryable；能力缺失与旧新 Host×Core 四象限；文档 rev、per-command wire minor、全局默认 minor 分开记录（不预设必须 bump）。
4. **P5/P6（lineage/resolve）**：旧→新 lineage 读写隔离反例；旧 edit token/Run/draft/candidate 的预期；旧键读取旧摘要、新绑定 resolve/issue 选择新资源的对照样例；C-15 §3.2 的 profile 可比/重复组待确认/旧证据缺失且不能按冻结参数重算的降级规则挂到 AC 与矩阵。
5. **P7/P8**：pins 17→18 由 DSH 单点追加；冻结记录写明最终语义 commit、实际 reviewed_head、工作树 SHA-256/blob ID、复核字节与最终冻结字节差异（只允许状态元数据差异）；最后编辑后复算；不改旧 17 契约字节与 FEA-08/09/10 证据。

## 依赖与边界

- 依赖 FEA-09/FEA-10 done（已满足）。
- 禁止：修改既有 17 个冻结契约字节（M2-C1 窄增量须 DSH 明确授权并记录）；实现 FEA-11 生产代码；新增依赖；push。
- 与本 Task 的关系：本 Task scope approved 后由 DSH 冻结工作范围并 Appointment(Owner=Codex 契约起草)；本 Task 契约最终字节独立 Review approved、DSH 冻结集成并 **done** 后，固定 C-17/pin 基线，再派发 FEA-11 scope-r2；scope-r2 approved 且 DSH 完成 ready/Appointment 登记后才允许 FEA-11 实施。

## Closeout Record

- 未开始（proposed；待独立 scope review）。

## Scope review 处置（DSH，2026-11-04）

- Review：`doc/reviews/FEA-11-PREREQ-1-scope-r1.md`（Codex 全新上下文，reviewed_head `d1341945`）**approved P0=0/P1=0/P2=4**；全部接受。
- S11P-001：AC-P1…P8 改为 lifecycle v3 勾选框 `- [ ]`；S11P-002：交付物改为登记现有 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（不造新 INDEX）；S11P-003：scope-r2 触发点统一为 PREREQ **done** 后；S11P-004：新增"冻结可执行清单"作为 AC-P1…P8 验收索引。
- Appointment：`doc/reviews/FEA-11-PREREQ-1-appointment.md`；Owner=Codex 契约起草（新实现会话）；最终契约 Review 由另一全新上下文执行。

## 实施与交付记录（Codex 起草 / DSH 收尾，2026-11-04）

- 交付：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（9 章；含规范 SQL/状态机/15 命令/DTO/错误/CAS/lineage/resolve/冻结可执行清单）、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`（DRAFT）、冻结矩阵 C-17 候选行、`doc/handoffs/FEA-11-PREREQ-1-handoff.md`、`verification/FEA-11-PREREQ-1/**`。
- 验证（DSH 复跑）：`validate_contract.py` 32 passed；`validate_examples.py` 全部通过；`validate_wire.py` 34 DTO/15 命令/28 错误/639 形状负例（schema 由 DSH 在表最终编辑后重新生成）；`run_checks.py` EXIT=0。日志见 `verification/FEA-11-PREREQ-1/logs/`。
- 未提交/未 push（DSH 集成提交）；pins 仍 17/17（C-17 pin 由 DSH 在 Review approved 后追加为 18）。
- 未完成：契约最终字节独立 Review（DSH 派发中，Codex 额度耗尽至 2026-11-05 00:51 → 切 ZCode）；DSH 冻结记录/三指纹/pin 18；M2-C1 无增量决定待 Review 确认。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-PREREQ1-C17 | AC-P1…P6/P8（契约提案） | doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md | pending | cb7c574987d9694f094a65c7aea4e286ab2a0df2347d05ea11433b369452e00b | CANONICAL |
| EV-PREREQ1-WIRE | AC-P3（命令/DTO 形状） | verification/FEA-11-PREREQ-1/wire-schema.json | pending | 9fed28fa1e8b6579934edba889b9aed87be1b3542a9ec77320c3f44f8b32de1e | CANONICAL |
| EV-PREREQ1-LOGS | AC-P1…P4（隔离验证） | verification/FEA-11-PREREQ-1/sql-validation.log | pending | 63113979cbc589c3af5a60ff9e235bcb799ca7fb3ceb9c7c57b73ba1689d297c | SOURCE_PIN |
| EV-PREREQ1-EXAMPLES | AC-P2/P4/P5/P6（规范模型） | verification/FEA-11-PREREQ-1/examples.log | pending | cecabea533a2e7c2a31a4e220fce2f629c2cd9e316cd307b032ae1c83052203c | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| evidence | G:/CODEX/New Manga/verification/FEA-11-PREREQ-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/FEA-11-PREREQ-1 | verification/FEA-11-PREREQ-1/baseline.json | 原始脚本/日志/基线保留 |
| isolated temp | G:/CODEX/New Manga.workspace/FEA-11-PREREQ-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/FEA-11-PREREQ-1 | verification/FEA-11-PREREQ-1/baseline.json | 隔离 SQLite/TEMP/TMP；不清理 |
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | verification/FEA-11-PREREQ-1/baseline.json | 主树；无新 worktree |
