# C-17 Source 同步契约 · 冻结记录草案

**状态：DRAFT / 未冻结 / 不构成实现授权。** 日期：2026-11-04。
契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`。起草 Owner：Codex；冻结人：**待 DSH**。
依据：`doc/tasks/FEA-11-PREREQ-1.md`、Appointment、scope-r1 approved（后者只批准范围）。

## 1. 冻结字节（由 DSH 在最终集成流程回填）

| 项 | 值 |
|---|---|
| 最终 ID / 冻结版本 / 时间 | PENDING_DSH（候选 C-17 v1.0） |
| 最终语义 commit | PENDING_DSH；当前未提交 |
| 实际 reviewed_head | PENDING_REVIEW；不可填当前 base 冒充已审语义 head |
| Reviewer 身份/来源/报告 | PENDING_APPOINTMENT（全新上下文，不得由起草会话自审） |
| sha256（最终工作树 pin） | PENDING_DSH_FINAL_BYTES |
| git blob ID（最终语义/冻结 head 分列） | PENDING_DSH |
| blob 内容 SHA-256（原始 Git blob bytes） | PENDING_DSH |
| 迁移版本与登记名 | 8 / v8__source_sync 仅候选；待 DSH 核对未占用后分配 |
| per-command / 默认 minor / 文档 rev | 新面2.3 / 默认3不变 / C-17候选v1.0；M2-C1 rev2.12无增量 |

候选三指纹与命令保存在 `verification/FEA-11-PREREQ-1/candidate-fingerprints.json`。它记录工作树原始SHA-256、Git过滤后候选blob ID与候选blob字节摘要；**不是已提交blob读取证据，也不是最终pin**。本记录不填可被verify_pins误认的候选sha256。冻结后才由DSH填写上表最终pin并单点追加map `C17=FEA-C17_SOURCE_SYNC_DRAFT.md`。

## 1A. pin 口径

`verify_pins.ps1` 使用最终工作树原始字节SHA-256；Git blob需从最终commit实际读取再算SHA-256。CRLF/LF可导致两者不同，分别记录，不把hash-object的ID当作sha256。Owner未修改pins脚本，当前17/17只验证旧对象。候选计算使用hash-object（无-w），没有写Git object/index。

## 1B. 复核字节与冻结字节

| 项 | 值 |
|---|---|
| 独立复核字节 SHA-256 / blob ID / blob SHA-256 | PENDING_REVIEW |
| 最终冻结字节三指纹 | PENDING_DSH |
| 差异清单 | PENDING；仅允许明确记录的状态行/冻结链接元数据差异 |
| 条款/SQL/DTO相等的复核 | PENDING；有任何语义变动必须新head复审 |

最后一次编辑后重新计算，禁止提前计算pin后再修改状态行。本记录不签发approved/frozen/done。

## 2. 条件核验

| 条件 | 当前状态 | 证据/下一责任 |
|---|---|---|
| DDL/状态/命令/CAS/lineage/resolve提案及AC索引 | DRAFT_DELIVERED | 契约§1–9；Owner隔离脚本/日志 |
| 隔离SQL、DTO、模型验证 | EXECUTED，限证据声明范围 | verification专属目录；DSH复跑 |
| 最终语义固定commit与上下文独立Review approved | NOT_RUN | DSH Appointment/处置 |
| 最终ID/schema号/wire策略确认 | PENDING_DSH | 不预占v8，不修改旧面 |
| 最终指纹/pins18/18/冻结后check | NOT_RUN | DSH单点，Owner只交候选 |
| 当前旧17pins、治理与写域门禁 | 见最终日志 | 不能替代上述条件 |
| M2-C1 | NO_INCREMENT | 新命令/错误闭集由C-17承载，不改M2-C1字节 |

## 3. DSH 接收/冻结顺序

1. 核对main/HEAD与dirty清单，接收未提交文件；保留Owner工作树快照与候选指纹。
2. 确认C-17/schema/wire策略，固定语义commit（Owner未获commit权），给全新上下文Reviewer固定reviewed_head；Review不得参与实现/返修。
3. Reviewer逐条核对§9清单并复跑隔离命令，报告身份/来源、Architecture/Verification、未跑项及P0/P1；DSH处置findings，有返修就新head复核。
4. approved后，仅做明确记录的冻结元数据编辑；复核差异、实际读取新旧blob字节，最后编辑后算三指纹；最终pin写本记录，verify_pins仅追加第18项。
5. 18/18 + check + 范围/资源/集成验证后，由DSH更新Task/STATUS/PLAN并done。之后才释放FEA-11 scope-r2，不能从本草案直接启动生产实施。
