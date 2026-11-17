---
id: MAPMINT-ERROR-FIDELITY-1
title: MapMintFailure 兜底保真 —— 内部诊断保留内层异常类型（公共错误码不变）
kind: fix
governance_version: 3
status: proposed
disposition: "FEA11-ENTRY-MISSING-1 无法定论的根因：MapMintFailure 的 `_ =>` 兜底丢弃内层异常类型，导致失败原因不可辨"
approval: DSH 2026-11-17（按 Codex 裁定 Q2 冻结最小范围；不扩公共错误码/wire/Schema）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - FEA11-ENTRY-MISSING-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/MAPMINT-ERROR-FIDELITY-1
allowed_paths:
  - doc/tasks/MAPMINT-ERROR-FIDELITY-1.md
  - doc/reviews/MAPMINT-ERROR-FIDELITY-1-*.md
  - doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md
  - doc/tasks/FEA11-ENTRY-MISSING-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/MAPMINT-ERROR-FIDELITY-1/**
---

# MAPMINT-ERROR-FIDELITY-1：MapMintFailure 兜底保真

## 来源与目标

`FEA11-ENTRY-MISSING-1` 的结论是「剩余失败无法定论」：`MapMintFailure` 的 `_ =>` 兜底把内层异常类型丢弃，
导致 `SOURCE_ENTRY_MISSING` 无法进一步区分（`FileNotFound` / `Unauthorized` / 其他）。

现卡 `allowed_paths` 不含产品源码，**不能**在诊断卡里改代码；Codex 裁定 Q2 = 选 A：本卡保持 `blocked`，另立本卡承接最小实现。

来源裁定：`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` Q2：
> 修复 `MapMintFailure` 的兜底路径，使内部诊断结果保留内层异常类型；**公共错误码、API/Schema 和 wire 行为不变**。

**一个可观察交付结果**：内部诊断结果能区分内层异常类型，且**公共错误码与 wire 字节完全不变**。

## Acceptance Criteria

- [ ] **AC1 现状取证**：定位 `MapMintFailure` 与其 `_ =>` 兜底分支（给出行号），用现有测试复现「无法区分内层异常类型」。
- [ ] **AC2 内层类型保真**：兜底路径把内层异常类型（至少 `FileNotFoundException`、`UnauthorizedAccessException`、其他）写入**内部诊断元数据**；不改变 `SOURCE_ENTRY_MISSING` 等公共错误码。
- [ ] **AC3 公共契约零变更**：`git diff` 证明 wire/Schema/公共错误码表未改；若必须改，**停止**并交 DSH 冻结契约范围。
- [ ] **AC4 回归断言**：为三类内层异常各加一条映射断言；断言不得把原始绝对路径或敏感消息写入外部错误。
- [ ] **AC5 判别力**：把保真逻辑回退（临时）→ 新测试**变红**；还原后通过，证明断言有判别力。
- [ ] **AC6 证据与边界**：跑相关测试套件并记录 pass/fail/skip；不宣称 `FEA11-ENTRY-MISSING-1` 的归因结论已改变。

## 允许修改范围

- 本卡、`doc/reviews/MAPMINT-ERROR-FIDELITY-1-*.md`、`verification/MAPMINT-ERROR-FIDELITY-1/**`。
- 实现时**仅**允许改错误映射所在的源文件与其测试（执行前由 DSH 在卡面写明精确文件路径）。

## 禁止范围

- 不得改公共错误码、wire 协议、Schema、依赖。
- 不得把内层异常信息（路径/消息）泄漏到外部错误或日志之外的持久化产物。
- 不得删除或弱化既有断言。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 读源码 + 复现不可辨 | 无夹具 | NOT_RUN | 无 |
| AC2/AC4 | 定向单测（三类内层异常） | 同上 | NOT_RUN | 无 |
| AC5 | 回退保真逻辑 → 变红 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **依赖**：`FEA11-ENTRY-MISSING-1`（保持 `blocked`，提供无法定论的现场）。
- **风险 R1**：若内层异常类型要进入公共映射，则属共享契约变更 ⇒ 立即停止并交 DSH 冻结范围。
- **风险 R2**：诊断元数据若被写入可持久化产物，需确认不含用户路径（隐私边界）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
