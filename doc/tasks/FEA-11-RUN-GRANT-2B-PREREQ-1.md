---
id: FEA-11-RUN-GRANT-2B-PREREQ-1
title: C-16 v1.4 UNFREEZE（容器多成员 entry 授权接受面语义）
kind: contract
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-RUN-GRANT-2` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（**READY-WITH-UNFREEZE**：2B 仅需 C-16 v1.4，1 pin）；Codex 裁决输入（`196dede9…`）同意容器多 entry 需 C-16 修订；DSH 裁决：只改 C-16（1/18 pins），C-17/C-06 零字节；先契约后实现
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r1.md` 与载体）
depends_on:
  - FEA-11-RUN-GRANT-1-PREREQ-1
base_commit: 9ec4826d6
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-2B-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md
  - doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2B-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**
out_of_scope:
  - 生产代码/测试（src/**、tests/**、apps/**）——2B 实现卡（`FEA-11-RUN-GRANT-2`）另起
  - C-06/C-17/C-15/C-07/C-08/M2-C1/ADJ-001 等其余 17 份冻结契约字节（C-16 除外）
  - Run wire/`CORE_PROTOCOL_MINOR`/新错误码/schema/迁移/依赖；UI/扫描策略；真实用户数据；push
---

# FEA-11-RUN-GRANT-2B-PREREQ-1：C-16 v1.4 UNFREEZE（容器多成员 entry）

> **状态：`ready`（契约前置；只起草 + 独立 byte-level 复核 + 重冻；不实现）。**
> 来源：2B 缺口——Core 注册/匹配硬性要求容器 grant **恰好 1 个 entry**（`source_read_refs.py:986-990`、`:598-610`），Host 对 zip/cbz/pdf 只铸容器单 entry → 多成员容器仅首成员可授权；须扩展 C-16 授权接受面语义（1 pin）。

## DSH 裁决（2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| T-1 | **UNFREEZE 面** | **只改 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.4）**；C-17/C-06 及其他 16 份契约零字节；18 pins 中**恰好 1 项**（C16）重签。 |
| T-2 | **语义扩展（最小）** | 容器源（zip/cbz/pdf）的 `RegisterSourceReadGrant` 的 `scope.entries[]` 允许 **1..N**：每项 `path` = 容器绝对路径、`locator`/`ordinal` = 成员身份、`facts` = **容器**物理身份（四键同一）；Core 注册时逐项校验（locator 安全、ordinal ≥0 且唯一、facts 与容器身份一致、path 在同一容器）；匹配时按既有 `entry_key OR locator OR ordinal` + facts 逐项匹配；**任一不匹配 → 整体 typed 零绑定写入**；不得路径回退；不得放宽 `max_entries`/64 grant 上限（超限 typed）。 |
| T-3 | **不改项** | grant 四维 scope 形状、TTL ≤300s、撤销/失联、错误闭集（无新码）、§7 脱敏、Run wire/§2.4 命令、`source.read.run/1` 能力、folder 语义（已支持逐成员）零改动；`<DataRoot>`/路径规则不变。 |
| T-4 | **禁止** | 不得借机放宽 facts/identity/撤销校验；不得新增命令/字段（除 entries 数量与容器项约束的明文澄清）；不得改 pins 数。 |
| T-5 | **顺序** | 先独立 byte-level 复核 approved + 重冻（pins 18/18），后释放 2B 实现卡；实现卡不得顺手改契约。 |

## In（本卡变更点，冻结）

### I-1 载体

- `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md`：触发/授权/缺口/逐项修订/兼容/回退/复核要求/结果。

### I-2 C-16 v1.4（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`）

- 头部状态行 → `FROZEN v1.4（2026-11-07 重冻；v1.0 2026-11-03 / v1.1 2026-11-04 / v1.3 2026-11-06）` + 载体/冻结记录链接；日期行补 v1.4。
- §2（`RegisterSourceReadGrant`）增加 **容器多成员 entry 明文**：
  - 容器源（`rendition.decoder ∈ {zip, cbz, pdf}`）`scope.entries[]` **允许 1..N**；每项 `path` 必须为同一容器绝对路径；`locator`/`ordinal` 为容器内成员身份（成员身份以 Core 权威扫描结果为准，Host 不得自行推断）；每项 `facts` 必须等于**容器**物理身份（四键一致）。
  - 注册校验：逐项 `locator` 安全（不得 `.`/`..`/绝对）、`ordinal ≥0` 且唯一、`path` 一致、`facts` 与容器身份一致、`len(entries) ≤ budget.max_entries`；不满足 → `SOURCE_ACCESS_DENIED`（或既有 §6 对应码），**整 grant 拒绝**（不截断）。
  - 读取/匹配语义：既有 `entry_key == entry_id OR locator == source_entries.locator OR ordinal == source_entries.ordinal` **不变**；facts 仍与容器身份比对；**无路径回退**；`find_bound_for_source`/`commit_guard` 不变。
  - `source.read.run/1` §2.4 语义不变（其 per-page 匹配已按上述 OR 规则与 facts；本 v1.4 只澄清容器 entries 可为 N 项）。
- §10 冻结条件追加 v1.4 条目；变更记录追加 v1.4 行。

### I-3 冻结记录与矩阵

- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：pin → v1.4 最终字节 sha256；新增 v1.4 UNFREEZE 重冻记录（历史 pin 保留）。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-16 行 → `FROZEN v1.4`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18，其中 C16 = 新值、其余 17 项不变。

### I-4 证据

- `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**`：pre/post sha、changed-lines.diff、other-17-pins（C-16 以外全部不变）、pins/check 日志、carrier。

## Out

- 生产实现（2B 实现卡）；C-06/C-17 及其余契约；Run wire/minor/错误码；schema/依赖；UI/扫描策略；push。

## Acceptance Criteria（v3）

- [ ] **AC-T1 契约增量最小且可复核**：C-16 v1.4 只含 I-2 登记增量（容器 entries 1..N 语义 + 校验矩阵 + §10 记录）；既有 grant scope 形状/TTL/撤销/失联/§6 闭集/§7 脱敏/§2.4 命令/Run wire 零改动；C-06/C-17 在内的其余 17 契约逐字节不变。
- [ ] **AC-T2 独立 byte-level 复核 approved**：fresh subagent 对最终字节复核（diff 逐行、无新错误码、无 wire/minor 变更、17 项不变、pin 可复算）；P0/P1=0；session/reviewed_head 入载体。
- [ ] **AC-T3 重冻与 pins**：FROZEN-C16 更新（新 sha、v1.4 记录、历史 pin 保留）；矩阵更新；`verify_pins` **18/18**（C16 新值、其余 17 项原值）；`check.ps1`（默认 + `-TaskPath`）PASS。
- [ ] **AC-T4 载体与不夸大**：载体含触发/授权/变更点/兼容/回退/复核要求/结果；明写「契约就绪 ≠ 实现/产品可用」；未改 Run wire/schema/依赖。

## 独立复核要求（byte-level）

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终工作树字节；记录 session/reviewed_head。
- 核对：①I-2 各项精确落地；②C-06/C-17 在内的其余 17 契约零字节；③无新错误码/无 wire/minor/schema/依赖变化；④pin 可复算、18/18；⑤载体/卡不夸大。
- 通过标准：approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 提交并重跑 pins；未通过 → 返修后窄面复审。

## 已知 limitation / follow-up

- L-P1′：M2-C1 §5.7 HostControl 枚举滞后（既有，随 L-P1 保留）。
- L-P2′：2B 实现仍需 2A 的版本通道（依赖顺序）；长 Run/加密/重启不因本契约解决。
- L-P3′：契约就绪不构成实现授权。

