# ADJ-2026-11-04：下一 Task 优先级裁决（Codex 独立裁决 + DSH 处置）

## 裁决者与来源

- Codex 全新上下文（用户指定独立优先级裁决者），只读；未修改仓库、commit、push。
- 证据：`G:\CODEX\New Manga.workspace\FEA-09\next-task-adjudication-codex.md`（原字节；DSH 归档）。
- 裁决输入：`REBASELINE_PLAN` 当前 DAG、`STATUS`、`TASK_LEDGER`、候选 Task 卡、提案 §12.1/§15.5/§15.6、协作协议与 2026-10-31 Review 独立性规则。

## Codex 裁决（原文要点）

- **唯一首选：FEA-10「快照/候选/提交安全」先建卡并 scope review，通过后释放实施**；本次不安排并行清洁项，不授权直接编码、集成或 push。
- 排序：FEA-10 → FEA-11 → FEA-12（需先解 `G-DELETE-IMPL`）→ FEA-13 → FEA-14 子项 → FEA-15；其余仅作处置优先级（PUBLICATION-DIAG 历史收口、D07 状态对账、GOV-11 裁决对账、CORE-ENV-2 前提澄清、Rust 历史归档裁决、V1 审计恢复条件）。
- 不建议现在释放：Rust 设计（不恢复 Legacy 诊断）、PUBLICATION-DIAG（approved 只覆盖 `fed1a9…`，AC3 PARTIAL/父任务 in_review）、CORE-ENV-2（缺定义/环境）、GOV-11/D07/V1 审计（需对账或用户裁决）。
- 建议：Owner=Codex 新实现会话；scope reviewer 与 implementation reviewer 均为 DSH 派发的全新独立上下文；先卡、范围矩阵、契约缺口与 scope review，不写生产代码。
- 不确定/NOT_RUN：未运行测试/构建/治理/pins；Rust base 重验被 Git ownership 阻断；报告指出 Plan/GOV-11/D07 指针待对账，工作区有未跟踪图文件。

## DSH 接受与修正

1. **接受首选与排序**：FEA-10 作为下一主线；不并行释放其他实施 Task。
2. **补一项 Codex 未覆盖的硬前置**：C-08 冻结记录 §3 规定「M2-C1 块②协议注册（PrepareRun/AcceptRun + 3 错误码 + host `allowedRunErrorCodes` + 负向对照）」是 **Run 实现释放前置**，当前 M2-C1 仍为 rev 2.11、未见该块 → 必须先释放 `FEA-10-PREREQ-1`，通过后 FEA-10 才可 ready。已建卡（proposed，待 scope review）。
3. **建卡**：`doc/tasks/FEA-10-PREREQ-1.md` 与 `doc/tasks/FEA-10.md` 均为 proposed；首轮只交卡/范围矩阵/契约缺口 + 独立 scope review，不写生产代码、不 push。
4. **指针修复（当前轮）**：PLAN 更新 FEA-09-UI-1 done、加入 FEA-10 前置与实现节点；STATUS 指针改为 FEA-10-PREREQ-1（proposed，待 scope review）。FEA-D07 AC8 与 GOV-11 旧待裁决文字登记为后续对账项，不在本轮重开历史工作。
5. **Appointment 顺位**：PREREQ-1 scope approved 后由 DSH 指派 Owner（建议 Codex 全新会话；协议/错误码小面）；FEA-10 实施 Owner 建议 Codex，reviewer 另行全新上下文。

## 后续动作（DSH）

- PREREQ-1：scope review（全新 Codex）→ 处置 findings → 冻结 ready + Appointment（Owner 建议 Codex；只改 M2-C1 块② + host 投影白名单与测试）。
- FEA-10：待 PREREQ-1 done 后释放（Owner Codex；L2 高风险；真实 IPC + 隔离故障注入）。
- 不 push；C-05/C-15/C-16 冻结字节、FEA-08/FEA-09 closeout 文件不动；共享组合根仍仅 DSH 单点提交。

## Scope Review r1 处置（DSH，2026-11-04）

- Reviewer：Codex 全新上下文（未参与建卡/实现）；报告 `doc/reviews/FEA-10-scope-r1.md`（reviewed_head `ae1d2392`）。
- 结论：changes_requested；P0=0 / P1=3（写域缺口、SC-R09 验收、提交安全 AC 覆盖）/ P2=5。
- DSH 处置：**全部接受**。
  - 写域补 `src/bootstrap/core_service.py`/`core_assembly.py`、`CoreServiceClient.cs`、Python `tests/**` 精确文件；其余目录收窄；
  - AC 增 SC-R09 durable receipt（丢 ACK/重启找回/异 fingerprint/request_id 非键）；
  - 提交安全 AC 逐项覆盖 lease/binding/manual/final/draft token/Run receipt，明确多 Region 编辑 apply 与 Pipeline seam 事务单位；
  - PreparedRun 增 Prepare 零 DB 写/零执行、`RUN_PREVIEW_EXPIRED`、payload digest 一致；
  - PREREQ-1 增「未注册码不作 UI 分支依据」与 rev 2.12 vs wire minor 边界；
  - 增验证矩阵与既有实现复用清单。
- **拆分裁定（P2-4）**：C-08 冻结记录 §3 原「与 C-04b 共用 Task」是冻结期安排；C-04b 已冻结且删除线不属于 FEA-10 范围，DSH 裁定硬前置独立为 `FEA-10-PREREQ-1`，仅做协议注册/投影，不碰删除线；该替代安排登记于本 ADJ，不修改 C-08 冻结字节。
- 下一轮：两卡修订后交**全新上下文 Codex** scope review r2；仍不写生产代码、不 push。

## Scope Review r2 处置（DSH，2026-11-04）

- Reviewer：Codex 全新上下文（未参与建卡/实现）；报告 `doc/reviews/FEA-10-scope-r2.md`（reviewed_head `1ac21de7`）；结论 changes_requested P0=0/P1=3/P2=3。
- DSH 处置：**全部接受**。
  - P1-1：FEA-10 改**文件级写域矩阵**（bootstrap/CoreClient/Host/App/Services/ApplicationCore/Python tests 逐文件）；PREREQ 也收窄到文件级；
  - P1-2：AC7 增「关闭/重启 Core、重开同一 DB 后同键找回原 Run」；
  - P1-3：AC5 增 10 项逐条故障注入矩阵 + 两类事务单位定义（多 Region 编辑 apply vs Pipeline step seam）；
  - P2-1：明确 `preparedDigest` 按冻结四元组算法校验，另比较 `payloadDigestPreview == payloadDigestSend`，不要求两种不同摘要相等；
  - P2-3：PREREQ 明确登记 C-08 §3 已批准 wire 2.12，文档 rev 与 `PROTOCOL_MINOR` 分离，客户端 registry/Core dispatch 归属分开；
  - P2-5：验证矩阵补精确文件/命令/solution/DataRoot/门径/证据出口。
- 下一轮：两卡修订后交**全新上下文 Codex** scope review r3；仍不写生产代码、不 push。
