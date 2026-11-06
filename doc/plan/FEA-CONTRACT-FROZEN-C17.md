# C-17 Source 同步契约 · 冻结记录

**状态：FROZEN v1.1（v1.0 冻结 2026-11-04；v1.1 UNFREEZE 重冻 2026-11-06）。** 本冻结不构成 FEA-11 生产实施授权；实施须另经 FEA-11 scope-r2 + DSH Appointment 释放。v1.1 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md`；触发：用户 2026-11-06「Codex 决定下一任务」→ Codex 裁决 SCAN-2 → scope review READY-WITH-UNFREEZE → DSH 裁决 B1。
契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`。起草 Owner：Codex；冻结人：**DSH（2026-11-04）**；上下文独立 Review：**ZCode 全新上下文**（r1 reviewed_head `69d7c31ee`；轻量复核 head `c7940fa7`）。
依据：`doc/tasks/FEA-11-PREREQ-1.md`、Appointment、scope-r1 approved（只批准范围）、`doc/reviews/FEA-11-PREREQ-1-r1.md`（approved P0/P1=0）、`doc/reviews/FEA-11-PREREQ-1-r1-light.md`（轻量复核 approved P0/P1/P2=0）。

## 1. 冻结字节（由 DSH 在最终集成流程回填）

| 项 | 值 |
|---|---|
| 最终 ID / 冻结版本 / 时间 | **C-17 v1.1 / 2026-11-06（DSH UNFREEZE 重冻；v1.0 于 2026-11-04）** |
| 最终语义 commit（v1.0） | `e94c4b8d8f8c0baae857d3335d7aa6f2533a84c6`（v1.0 冻结提交） |
| 实际 reviewed_head | r1 `69d7c31ee60318c6f8a042c60c3f749a0ffda6a6`（ZCode 契约 Review r1）；轻量复核 `c7940fa7179e2b1d029fa58fb09e9a8dea13f5eb` |
| Reviewer 身份/来源/报告 | **ZCode 全新上下文**（r1 session `sess_ec2aaf7b-c0cd-4c1c-8696-436c55733bf3`；轻量 session `sess_39a3cee4-31a4-4f5c-a4b0-fcf3a328d1f6`；未参与起草/返修）；报告 `doc/reviews/FEA-11-PREREQ-1-r1.md`、`doc/reviews/FEA-11-PREREQ-1-r1-light.md`；结论 approved（r1 P0/P1=0、P2=6 已处置；轻量 P0/P1/P2=0） |
| sha256（v1.1 最终工作树 pin） | `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59` |
| git blob ID（v1.1） | `f767e158a43652ea092066081e53fa0810e395fb` |
| blob 内容 SHA-256（v1.1，LF Git blob） | `83c05ae9f575600ba93ea325b86214bd1d3207fa6f276c2bdbef5c976dccb9e8` |

历史（v1.0，仅追溯）：工作树 pin `86b89ff8…`；blob ID `9c6394bf…`；blob SHA-256 `b6766e1a…`；提交 `e94c4b8`。
| 迁移版本与登记名 | **v8 / v8__source_sync（DSH 冻结；已核对 schema.py/migrator.py 未占用 v8；v1–v7 SQL/checksum 不变）** |
| per-command / 默认 minor / 文档 rev | 新面 2.3 / 默认 3 不变 / C-17 v1.1；M2-C1 rev 2.14 现状 **无增量（NO_INCREMENT）** |

候选三指纹与命令保存在 `verification/FEA-11-PREREQ-1/candidate-fingerprints.json`。它记录工作树原始SHA-256、Git过滤后候选blob ID与候选blob字节摘要；**不是已提交blob读取证据，也不是最终pin**。本记录不填可被verify_pins误认的候选sha256。冻结后才由DSH填写上表最终pin并单点追加map `C17=FEA-C17_SOURCE_SYNC_DRAFT.md`。

## 1A. pin 口径

`verify_pins.ps1` 使用最终工作树原始字节SHA-256；Git blob需从最终commit实际读取再算SHA-256。CRLF/LF可导致两者不同，分别记录，不把hash-object的ID当作sha256。Owner未修改pins脚本，当前17/17只验证旧对象。候选计算使用hash-object（无-w），没有写Git object/index。

## 1B. 复核字节与冻结字节

| 项 | 值 |
|---|---|
| 独立复核字节 SHA-256 / blob ID / blob SHA-256 | r1 `69d7c31ee`：blob `84fbd2b1c2e777f1a5c1c0638f6ac99e82c86de3` / SHA-256 `cb7c574987d9694f094a65c7aea4e286ab2a0df2347d05ea11433b369452e00b`；轻量 `c7940fa7`：blob `1e5887ea2c20cefd686b473f0b9fca852b49126a` / SHA-256 `aba6b77ebb8a02a5ce41aa45f5e6f504a8e5e9c0ada71093bfddf7c2a7949183` |
| 最终冻结字节三指纹（v1.1） | 工作树 `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59` / blob ID `f767e158a43652ea092066081e53fa0810e395fb` / blob SHA-256 `83c05ae9f575600ba93ea325b86214bd1d3207fa6f276c2bdbef5c976dccb9e8` |
| v1.0 三指纹（历史） | 工作树 `86b89ff8…` / blob ID `9c6394bf…` / blob SHA-256 `b6766e1a…` |
| v1.1 独立复核（2026-11-06） | fresh subagent session `1326c586-5b5b-4e7a-bc80-653ed57f3e3a`；报告 `workspace/FEA-11/review-c17-v11/C17-v1.1-review.md`（仓内副本 `doc/reviews/FEA-11-SCAN-2-PREREQ-1-c17-review.md`）；结论 **APPROVE**（P0/P1/P2=0；P3×6 非阻断） |
| 差异清单 | 已核对：r1→轻量仅 6 处说明性文字（§2.1/§3.1/§5.1/§5.3/§7.1/§8），SQL/DTO/错误表/状态机零变化；wire-schema SHA-256 `9fed28fa…` 未变；无状态行/冻结链接外的字节差异 |
| 条款/SQL/DTO相等的复核 | **相等**（ZCode 轻量复核确认；validate_wire 文档实时编译 == 冻结 schema） |

最后一次编辑后重新计算，禁止提前计算pin后再修改状态行。本记录已由 DSH 冻结（FROZEN v1.1）；FEA-11 生产实施仍须 scope-r2 + DSH Appointment。

## 1C. v1.1 UNFREEZE 记录（2026-11-06）

- 触发/授权：用户 2026-11-06「让 Codex 判断下一部任务，由 DSH 执行」→ Codex `NEXT-TASK=FEA-11-SCAN-2`（先 scope review、优先 B1）→ scope review `doc/reviews/FEA-11-SCAN-2-scope-r1.md` **READY-WITH-UNFREEZE** → DSH 裁决 B1 采纳/S-1②/S-2/S-4。
- 修订内容：仅新增只读命令 `source_list_scan_targets` + `ScanTarget/ScanTargets` DTO + `source.sync.enumerate/1`（只进 `core.ping.capabilities`；Capabilities DTO 仍恰好 7 项）+ §5.3 守卫与 §8 零新增错误码注记 + §9 P3/P7/P8 适用声明；header/§0 版本与既有 DRAFT v0.1 漂移一并修正。
- 复核：r1 独立 fresh subagent byte-level 复核（报告与 session 待补；**APPROVE 前本记录 sha 行不构成最终 pin 声明，以 §1 行为准并由 DSH 在复核后确认**）。
- pins：`verify_pins.ps1` 仍 **18 pins**（C17 重算），其余 17 契约与 ADJ-001 字节零 diff。
- 回退：若复核否决/用户要求回退，恢复 v1.0 字节（sha `86b89ff8…`）与冻结记录/matrix；SCAN-2 实现卡不释放。

## 2. 条件核验

| 条件 | 当前状态 | 证据/下一责任 |
|---|---|---|
| DDL/状态/命令/CAS/lineage/resolve提案及AC索引 | DRAFT_DELIVERED | 契约§1–9；Owner隔离脚本/日志 |
| 隔离SQL、DTO、模型验证 | EXECUTED，限证据声明范围 | verification专属目录；DSH复跑 |
| 最终语义固定commit与上下文独立Review approved | **DONE**（v1.0：r1+轻量 approved；v1.1：UNFREEZE 独立 byte-level 复核 APPROVE，报告/session 见 §1B） |
| 最终ID/schema号/wire策略确认 | **DONE**（v1.1：C-17 v1.1 / v8 / 新面 2.3 / M2-C1 无增量；新增枚举命令走 app 面） |
| 最终指纹/pins18/18/冻结后check | **DONE**（本记录/verify_pins 18/18/check 见集成提交日志） |
| 当前旧17pins、治理与写域门禁 | 见最终日志 | 不能替代上述条件 |
| M2-C1 | NO_INCREMENT | 新命令/错误闭集由C-17承载，不改M2-C1字节 |

## 3. DSH 接收/冻结顺序

1. 核对main/HEAD与dirty清单，接收未提交文件；保留Owner工作树快照与候选指纹。
2. 确认C-17/schema/wire策略，固定语义commit（Owner未获commit权），给全新上下文Reviewer固定reviewed_head；Review不得参与实现/返修。
3. Reviewer逐条核对§9清单并复跑隔离命令，报告身份/来源、Architecture/Verification、未跑项及P0/P1；DSH处置findings，有返修就新head复核。
4. approved后，仅做明确记录的冻结元数据编辑；复核差异、实际读取新旧blob字节，最后编辑后算三指纹；最终pin写本记录（v1.1 已为 18/18 口径，v1.0 时代“仅追加第18项”为历史描述）。
5. 18/18 + check + 范围/资源/集成验证后，由DSH更新Task/STATUS/PLAN并done。之后才释放FEA-11 scope-r2，不能从本草案直接启动生产实施。
