---
id: FEA-11-PREREQ-1
title: Source 同步契约前置（v8+ DDL / plan-operation 状态机 / scan-plan-apply-relink-repoint-resync 命令面 / CAS 与 lineage / resolve 版本选择）
kind: implementation
governance_version: 3
status: proposed
approval: 待独立 scope review（Codex 全新上下文）；approved 后由 DSH 冻结并 Appointment；不预占 v8 版本
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-09
  - FEA-10
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-PREREQ-1.md
  - doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C17.md
  - doc/plan/FEA-CONTRACT-INDEX.md
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
2. 如经 DSH 授权：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 窄增量（rev 2.13?）与错误/能力登记；
3. `tools/governance/verify_pins.ps1` 加入新契约 pin（由 DSH 单点更新；冻结后 pins 17→18）；
4. 独立 Review 报告（全新上下文）与冻结记录；
5. Handoff + EV + Resource Manifest（证据在 `verification/FEA-11-PREREQ-1/`）。

## Acceptance Criteria

- **AC-P1（DDL/迁移冻结）**：两表 DDL/索引/FK/约束/迁移版本冻结决议可执行（含版本号、回滚、旧端拒写）；与 C-15 "不创建两表" 的预留声明一致；v1–v7 字节不变。<<PARTIAL: 待 scope 冻结与契约评审>>
- **AC-P2（状态机）**：plan/operation 状态机与 Host/Core 存储归属冻结，含 ACK 前读门控持久化与逐崩溃点恢复顺序。<<PARTIAL: 待 scope 冻结>>
- **AC-P3（命令面）**：scan/plan/apply/relink/repoint/resync/operation 查询命令的 closed shape、字段、错误、能力探测与兼容策略冻结；不暗用导入 API。<<PARTIAL: 待 scope 冻结>>
- **AC-P4（CAS/原子性）**：三类代次与人工基线比较对象、事务重读位置、原子单元与整批回滚口径冻结可断言。<<PARTIAL: 待 scope 冻结>>
- **AC-P5（lineage）**：lineage 存储与读写隔离冻结，覆盖在途 Run/draft/candidate 交错规则。<<PARTIAL: 待 scope 冻结>>
- **AC-P6（resolve 版本选择）**：同步后资源版本选择方案冻结，旧资源键不可变。<<PARTIAL: 待 scope 冻结>>
- **AC-P7（证据/冻结）**：契约独立 Review approved；冻结记录 + pins 更新（17→18）可验证；check/PASS；不改既有 17 契约字节与 FEA-08/09/10 证据。<<PARTIAL: 待 scope 冻结>>
- **AC-P8（范围）**：不实现 FEA-11 生产代码、不越界 FEA-12/13/14、不新增依赖、不碰真实用户数据/AppData。<<PARTIAL: 待 scope 冻结>>

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

## 依赖与边界

- 依赖 FEA-09/FEA-10 done（已满足）。
- 禁止：修改既有 17 个冻结契约字节（M2-C1 窄增量须 DSH 明确授权并记录）；实现 FEA-11 生产代码；新增依赖；push。
- 与本 Task 的关系：本 Task done 是 FEA-11 `ready` 的硬前置；FEA-11 的 scope-r2 在本 Task approved 后派发。

## Closeout Record

- 未开始（proposed；待独立 scope review）。
