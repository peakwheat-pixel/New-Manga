---
id: LICENSE-VARIANT-DECLARATION-1
title: base 变体声明 GPL-3.0-or-later 却内置 632 MB 权重 —— 需用户选向（AGPL 声明 / 移除权重）
kind: fix
governance_version: 3
status: blocked
disposition: "ZCode 裁定（doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md）：现声明非法；Q2 定为 P0 发布阻塞。合法出口只有 ①保守声明 AGPL-3.0 ②移除权重回归 base。方向取舍属用户产品裁决，DSH 不自裁"
approval: DSH 2026-11-17（由 ZCode 裁定触发；方向待用户决定）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - INSTALLER-MATRIX-1
  - INSTALLER-METADATA-CONSISTENCY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/LICENSE-VARIANT-DECLARATION-1
allowed_paths:
  - doc/tasks/LICENSE-VARIANT-DECLARATION-1.md
  - doc/reviews/LICENSE-VARIANT-DECLARATION-1-*.md
  - doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/LICENSE-VARIANT-DECLARATION-1/**
---

# LICENSE-VARIANT-DECLARATION-1：许可证声明与随包权重不相容（阻塞：等用户选向）

## 已定的裁决（ZCode，2026-11-17，全文见 `doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`）

- **不得**声明 `GPL-3.0-or-later`：判定规则 R1–R4 顺序执行，本案落在 **R4**（随包权重三项台账均为「待核实」）。
- 合法出口只有两个：
  - **方向 A**：保守声明 **AGPL-3.0**（可立即执行），并同步 `NOTICE.md` 变体表 / `LICENSE_AUDIT.md` / `THIRD_PARTY_LICENSES.md §3` / `installer.nsi` 许可页文案；variant 与 stage 命名对齐；由 `package.ps1` **干净重建**，禁止手工补 `VERSION.json`。
  - **方向 B**：**移除权重**回归真 base，维持 `GPL-3.0-or-later`，`NOTICE` 小改即可。
- 随包 `NOTICE.md` / `LICENSE_AUDIT.md` 与实物矛盾 = **P0 发布阻塞**（对接收方的虚假合规披露）。
- 权重上游许可的**法律属性证据不足**，ZCode 与 DSH 都不认定。

## 为什么 blocked（而不是 ready）

方向 A 与方向 B 是**产品取舍**（是否随包分发 632 MB 权重），ZCode 裁定明确「方向取舍属用户产品裁决」。
DSH 按「需要人工裁决交 Codex/ZCode」的授权只能拿到**规则**，不能替用户选向 ⇒ 本卡等用户一句话。

## 用户只需回答一句

> **保留权重随包（走 A：声明 AGPL-3.0）** 还是 **移除权重（走 B：维持 GPL-3.0-or-later）**？

## Acceptance Criteria（选向后按分支执行）

- [ ] **AC1 选向登记**：把用户的选择（A 或 B）与本裁定书链接写进卡面。
- [ ] **AC2 声明一致（A）**：`NOTICE.md` 变体表、`LICENSE_AUDIT.md`、`THIRD_PARTY_LICENSES.md §3`、`installer.nsi` 许可页四处**同时**改为与实物一致；或
      **AC2'（B）**：从 base stage 移除 `app/core-sidecar/models/` 并用 `package.ps1` 干净重建，`NOTICE` 只做小改。
- [ ] **AC3 生成器自证**：改后由 `package.ps1` **干净重建**（禁手工补字段），`verify-package-manifest.ps1` **EXIT=0**。
- [ ] **AC4 判别力**：旧 stage（声明 GPL + 632 MB 权重）在新护栏下仍被拒；新 stage 通过；两者证据并列。
- [ ] **AC5 不越界**：不改护栏检查集合；不宣称条件 4 通过；不覆盖旧 stage 字节。

## 允许修改范围

- 本卡、`doc/reviews/LICENSE-VARIANT-DECLARATION-1-*.md`、`verification/LICENSE-VARIANT-DECLARATION-1/**`。
- 选 A 时：`NOTICE.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md`、`THIRD_PARTY_LICENSES.md`、`packaging/nsis/installer.nsi`（仅许可页文案）。
- 选 B 时：`packaging/**` 的权重取舍与 `NOTICE.md` 相应行。

## 禁止范围

- 不得放宽 `tools/ci/verify-package-manifest.ps1` 的检查。
- 不得用「加一句免责声明」替代许可声明与实物一致。
- 不得在本卡内认定上游许可的法律属性（证据不足）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 记录用户选向 | 用户决定 | NOT_RUN | 无 |
| AC3 | `package.ps1` 干净重建 + 护栏 | clean worktree、sidecar 需先重建 | NOT_RUN | 无 |
| AC4 | 旧/新 stage 各跑护栏 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `INSTALLER-MATRIX-1`（stage 来源）、`INSTALLER-METADATA-CONSISTENCY-1`（护栏）。
- **阻塞**：等用户选向（A/B）。
- **风险 R1**：方向 A 需要四份合规文件同时改，任何一处漏改仍是虚假披露。
- **风险 R2**：`package.ps1` 干净重建需要 sidecar 的 `build-manifest.json`（如缺失需 `build_sidecar.ps1 -Force`，重活）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
