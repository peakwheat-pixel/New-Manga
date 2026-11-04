# FEA-11-PREREQ-1 Appointment（DSH，2026-11-04）

状态：**scope approved（r1 Codex，P0=0/P1=0/P2=4）→ DSH 冻结 scope / Appointment 完成；Task 置 `ready`；不释放 FEA-11 生产实施；不 push**
Task：`doc/tasks/FEA-11-PREREQ-1.md`（scope: v8+ DDL / 状态机 / 命令面 / 错误与能力 / CAS 与跨存储 / lineage / resolve 版本选择 / 冻结可执行清单）
依据：`doc/reviews/FEA-11-PREREQ-1-scope-r1.md`（approved）；`doc/reviews/FEA-11-scope-r1.md`（S11-001…007）；C-14、C-15 v1.1、C-16 v1.1、C-05 v1.2、C-13、M2-C1 rev 2.12；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`；`tools/governance/verify_pins.ps1`。

## 1. 角色

| 角色 | Agent | 说明 |
|---|---|---|
| Owner（契约起草） | **Codex** 新实现会话 | 只写 FEA-11-PREREQ-1 卡 allowed_paths；不得自审 |
| Reviewer（契约最终字节） | DSH 派发的**全新上下文**（Codex/ZCode；未参与起草） | 只读 reviewed_head；报告归档 |
| Integrator / 冻结 | DSH | 冻结范围、pins 17→18 单点更新、M2-C1 窄授权裁定、集成、closeout |

## 2. 冻结范围

- v8+（版本号由 DSH 在冻结记录确认，不预占）两表 `source_sync_plans`/`source_operations` 与 lineage 必要持久表达的 DDL/索引/FK/约束/迁移登记/回滚；
- plan/operation 状态机与 Host/Core 存储归属（C-15 Host durable authorization 在先）；
- scan/plan/apply/relink/repoint/resync/operation 查询命令的 closed shape、错误/能力/兼容（additive minor 或 bump 由契约裁决）；
- 三类代次 CAS 与人工基线、事务重读、原子单元与整批回滚；
- lineage 存储与读写隔离、在途 Run/draft/candidate 规则；
- resolve 资源版本选择（旧资源键/已发布摘要不可变）；
- C-15 §3.2 跨版本证据降级口径的映射；
- 冻结可执行清单（隔离 SQL 验证、状态转移表、命令/DTO 表、lineage/resolve 对照样例）。

## 3. 硬边界

- 不修改既有 17 个冻结契约字节；M2-C1 窄增量仅在 DSH 书面授权具体章节/命令/错误/版本策略后允许，否则记录"无增量"决定。
- `tools/governance/verify_pins.ps1` 的 17→18 追加由 **DSH 单点**执行；Owner 提供候选条目/指纹。
- 不实现 FEA-11 生产代码/迁移/测试（归 FEA-11）；不新增依赖；不碰真实用户数据/AppData/外部卷/回收站；不 push。
- 不修改共享组合根、FEA-08/09/10 closeout/证据。

## 4. 交付与门禁

- 交付：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（C-17 提案，ID 待 DSH 确认）、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 登记行、条件性的 M2-C1 窄增量、`verification/FEA-11-PREREQ-1/**` 隔离验证证据（SQL 负例/回滚/旧端拒写）、Handoff、EV；若需新 ID 由 DSH 确认。
- 门禁：`check.ps1` PASS；`verify_pins.ps1` 17/17（新增 C-17 pin 由 DSH 在冻结时追加为 18/18）；隔离 SQL 验证命令/EXIT/DataRoot 记录；范围 diff 0 域外。
- 完成定义：起草交付 → 全新上下文 Review approved → DSH 冻结记录 + pins 18 + 集成提交 → Task `done` → 固定 C-17/pin 基线。

## 5. 后续

- PREREQ done 后，DSH 派发 **FEA-11 scope-r2**（全新上下文）审修订后的 FEA-11 实现卡；scope-r2 approved + DSH ready/Appointment 后才允许 FEA-11 实施。
