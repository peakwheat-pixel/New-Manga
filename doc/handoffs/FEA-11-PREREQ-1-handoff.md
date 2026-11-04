# FEA-11-PREREQ-1 Handoff（Codex 起草 → DSH 收尾，2026-11-04）

## 交付结果

- Task 卡：`doc/tasks/FEA-11-PREREQ-1.md`（scope approved r1；Owner=Codex；本交付为**契约提案 + 隔离验证证据**，非生产实现）。
- 契约提案：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（9 章：权威/版本边界、身份与摘要、规范 SQL 完整增量、状态与持久归属、命令版本/能力/兼容、closed-shape 命令/DTO、CAS/事务/失败原子性、lineage/在途任务/资源选择、错误闭集、冻结可执行清单）。
- 冻结记录草案：`doc/plan/FEA-CONTRACT-FROZEN-C17.md`（DRAFT；最终 commit/三指纹/pin 由 DSH 回填）。
- 冻结矩阵：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 追加 C-17 草案登记行（DSH）。
- 证据：`verification/FEA-11-PREREQ-1/`（validate_contract.py / validate_examples.py / validate_wire.py / wire-schema.json / run_checks.py / baseline.json / candidate-fingerprints.json / 4 个 validation 日志 + DSH 复跑日志 3 个）。

## 验证证据（DSH 复跑，真实输出）

| 场景 | 命令 | 结果 |
|---|---|---|
| 契约 SQL/状态/CAS/迁移负例 | `C:/Python314/python.exe -B verification/FEA-11-PREREQ-1/validate_contract.py` | EXIT=0；**32 passed**（FK/CHECK/唯一性负例、整批最后一项失败回滚、真实 v7 runner 拒写、DDL 中途失败回滚） |
| 规范示例模型 | `validate_examples.py` | EXIT=0；ACK 前门控持久、ACK 原子开门、CAS 零写、lineage 同内容/变化隔离、resolve 旧键/新键不可变、证据降级、canonical 摘要 |
| 命令/DTO 形状 | `validate_wire.py`（schema 由 DSH 重新生成） | EXIT=0；**34 DTO / 15 命令（14 Core + 1 Host-local）/ 28 错误 / 639 形状负例**；既有 Source 错误 category/retryable 与只读生产表一致 |
| 综合检查 | `run_checks.py` | EXIT=0（sql/wire/examples/scope 四段日志均 EXIT=0） |

隔离环境：`G:/CODEX/New Manga.workspace/FEA-11-PREREQ-1/` 与 `:memory:` SQLite；未写系统 AppData/TEMP（TEMP/TMP 重定向到 workspace）。

## 关键契约决定（详见 C-17）

- 采用「两张业务表（source_sync_plans / source_operations）+ 两张发布/lineage 表（source_binding_publications / source_revision_lineage）」，单 plan 的所有选中项目在**一个 Core 业务事务**内提交；整批最后一项失败全部回滚、0 成功页。
- Host durable 授权在先；Core 提交后新 binding 同事务插入 pending 读门；Host durable ACK 后 Core 原子开全部门；stale Apply 连 plan/operation 元数据也零写（显式失效/失败走独立命令）。
- 命令面 15 条（scan/plan/preview/confirm/invalidate/apply/relink/repoint/resync/operation 查询/cancel/ack/recovery/failure/capabilities），写操作走 host-control；能力探测 additive；文档 rev 与 per-command wire minor 分离、默认 minor 不变。
- CAS 三类代次（SourceVersion/binding_version/Host authorization generation）+ 人工 revision/Lock/draft/Run 基线分离；读兼容仍为 generation ≤ 当前（apply 才等值）。
- resolve 新资源键 `page-rendition-v2-<digest>`（含 binding/version/entry/decoder profile），旧键/旧摘要不可变。
- C-15 §3.2 跨版本证据映射（direct/unique_pixel/duplicate_group/missing_old/incomparable）与旧证据缺失降级。

## NOT_RUN（归 FEA-11 实施）

真实 v7→v8 迁移与旧导入库守恒、真实 Host/Core 新进程崩溃矩阵、真实 grant/lease/即时撤销/DPAPI、在途 Run/draft/candidate 生产装配、resolve→issue→新旧实际字节、managed 五读路径与全量回归、真实 IPC。本前置的隔离模型不替代这些证据。

## 冻结/Review 状态

- 契约最终字节 **独立 Review 待派**（DSH 将派全新上下文；Codex 额度耗尽至 2026-11-05 00:51，本轮切 ZCode）。
- pins 17→18 由 **DSH 单点**在 Review approved 后追加；冻结记录三指纹由 DSH 回填。
- M2-C1：默认**无增量**（命令面由 C-17 承载）；若 Review 认为需要增量，须 DSH 明确授权具体章节/命令/错误/版本策略后才写。
- 未 commit/push（DSH 集成提交）。
