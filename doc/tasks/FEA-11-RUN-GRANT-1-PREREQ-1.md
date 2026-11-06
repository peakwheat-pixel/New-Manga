---
id: FEA-11-RUN-GRANT-1-PREREQ-1
title: C-06 v1.2 + C-16 v1.3 UNFREEZE（Run-scoped source-read 授权建立命令）
kind: contract
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`（fresh subagent `f26b8cec-2935-4f55-859d-e02e50e142a6`，verdict **READY-WITH-UNFREEZE**，推荐 U-A）；第二独立意见 `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1-delta.md`（Codex fresh subagent `c3c100ae…`，结论一致，非权威存档）；DSH 2026-11-06 裁决 U-A（见「DSH 裁决」）：新增 host-control 授权建立命令；**只改 C-06/C-16 两份契约（2/18 pins）**；M2-C1 不改（文档滞后登记 follow-up）；CORE+HOST 合并在 `FEA-11-RUN-GRANT-1` 另卡实施
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level 复核；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r1.md` 与载体）
depends_on:
  - FEA-11-RENDITION-1
base_commit: 91d224b88ce00e1f3498d4805870d7d2a0d7c4de
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-1-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md
  - doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-1-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-*.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C06.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-RUN-GRANT-1-PREREQ-1/**
out_of_scope:
  - 生产代码/测试（src/**、tests/**、apps/**）——CORE+HOST 合并在 `FEA-11-RUN-GRANT-1`；本卡不得实现
  - M2-C1 字节（§5.7 HostControl 枚举滞后已登记 follow-up；沿用 C-16/C-17 自承载先例）
  - 其余 16 份冻结契约字节；C-08/C-07/C-15/C-17；ADJ-001
  - Run wire 请求/响应字节、`CORE_PROTOCOL_MINOR`、新错误码、schema/迁移/依赖
  - UI/通知/扫描/删除/GC/备份；真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-RUN-GRANT-1-PREREQ-1：C-06 v1.2 + C-16 v1.3 UNFREEZE

> **状态：`ready`（契约前置卡；仅 DSH 起草 + 独立 byte-level 复核 + 重冻；不实现代码）。**
> 来源：`FEA-11-RUN-GRANT-1` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`（**READY-WITH-UNFREEZE**）§4.3 U-A；第二意见 `…-scope-r1-delta.md` 结论一致。
> **本卡只交付契约字节与冻结证据**：不构成实现授权，不构成「referenced Run 产品可用」。

## 来源与证据

1. **权威缺口**：Core 的 source-read 授权面是进程内 `SourceReadGrantRegistry._bindings`（`src/infrastructure/resource_channel/source_read_refs.py:411-440`），写入口只有 import（`src/application/importing/referenced/runtime.py:567-569`）与 sync apply（`src/application/sources/service.py:287,295-323`）；Run 命令面不带 grant（`src/bootstrap/core_service.py:5867-5923`），host-control 闭集无授权建立命令（`:355-364`），scan 铸而不绑（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1371-1386`）。除 import/sync 后 ≤300s 窗口外，生产 referenced Run 必在 provider 读图与 commit guard 处 typed 失败（`src/bootstrap/core_assembly.py:1773`、`src/infrastructure/sqlite/pipeline.py:897-899`）。
2. **scope review 推荐 U-A**：新增一个 host-control 授权建立命令；不改 Run wire、不改 schema/依赖、不加错误码；UNFREEZE 面 = C-06 v1.2 + C-16 v1.3（2/18 pins）。**否决**：identity/facts 回退（重开 `FEA-09-impl-r1` R1-I002，folder 失配，违反 C-17 §7.2/§7.3）；把 grant 塞 Run `overrides`（污染 Run 快照/fingerprint/idempotency）。
3. **冻结契约现状**：C-06 pin `8faa8cd139f2…`（v1.1）、C-16 pin `0b9511a55ea1…`（v1.1）；`verify_pins.ps1` 18/18 PASS（本卡起草前实测）。

## DSH 裁决（2026-11-06，U-A）

| # | 裁决 | 内容 |
|---|---|---|
| D-1 | **契约路径** | 采纳 **U-A**：新增 host-control 命令 **`AuthorizeSourceReadForRun`**（name 由本卡冻结）；不采纳 identity/facts 回退；不把 grant 塞 `overrides`。 |
| D-2 | **UNFREEZE 面** | 只改 `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`（v1.2）与 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.3）；**恰好 2 项 pin 重签，其余 16 项逐字节不变**。 |
| D-3 | **M2-C1** | **不改字节**（§5.7 HostControl 枚举滞后既有先例：C-16/C-17 自行承载）；登记 follow-up（文档一致性，非协议变更）。 |
| D-4 | **能力门** | C-16 §0 新增 additive 能力 **`source.read.run/1`**；Host 缺失 → `CORE_CAPABILITY_MISSING`，不铸 grant、不 dispatch（不得用未知命令探测）。 |
| D-5 | **命令语义** | Core 用**与 Run 相同的 scope 展开器**解析目标页；对每个 healthy binding 按**签名 grant 的 source/version/entry(locator|ordinal|entry_key) 与 facts** 校验当前 binding/entry（无路径回退）；命中则写入与 `bind_imported_entry` 同构的进程内映射；**零 DB 写**、不建 plan/apply、不发布资源；幂等。任一 referenced 目标页不可授权 → **整体 typed 失败且零绑定写入**（fail-closed）。 |
| D-6 | **不改项** | Run wire 请求/响应字节、`CORE_PROTOCOL_MINOR=3`、错误码闭集、schema/迁移/依赖、`IHostController`/C-07、grant 四维 scope 形状、TTL ≤300s、撤销/失联语义。 |
| D-7 | **300s 生命周期** | 契约侧保持「单 grant ≤300s、过期即失效」不变；长 Run 刷新策略**不在本卡**，由 `FEA-11-RUN-GRANT-1` 以 limitation/后续卡处置（L-G1）。 |
| D-8 | **冻结纪律** | 本卡独立 byte-level 复核 approved 并重冻后，`FEA-11-RUN-GRANT-1` 方可释放；实现卡不得顺手改契约字节。 |

## In（本卡变更点，冻结）

### I-1 载体

- `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md`（新载体）：触发/授权链/背景/逐项修订/兼容/回退/复核要求/结果记录（pre/post sha256、16 项不变断言）。

### I-2 C-06 v1.2（`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`）

- 头部状态行 → `FROZEN v1.2（2026-11-06 UNFREEZE 重冻；v1.0 2026-11-01 / v1.1 2026-11-03）` + 载体/冻结记录链接。
- §2.2 新增**一句（授权建立语义，第三生产者）**：source-read grant→page binding 的授权可由 Core 的 host-control 授权建立命令（C-16 §2.4）在 Run dispatch 前建立；该建立不延长 300s、不改变撤销/失联语义；不得以路径回退；同一 binding 允许多份 grant，选择规则沿用既有 `find_bound_for_source`（live、最高 generation/`grant_id`）；建立失败必须 typed 且零业务写。
- §2.3 命令表新增一行：`AuthorizeSourceReadForRun`（Host→Core host-control；语义：按 Run scope 建立 grant→binding 授权；结果：`{bound_pages, refused}`）。
- §5 变更记录追加 v1.2 行。

### I-3 C-16 v1.3（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`）

- 头部状态行 → `FROZEN v1.3（2026-11-06 UNFREEZE 重冻；v1.0 2026-11-03 / v1.1 2026-11-04）` + 载体/冻结记录链接。
- §0 能力列表 mention：新增 additive `source.read.run/1`（缺失 → `CORE_CAPABILITY_MISSING`；按操作检查，不靠发送后看结果）。
- 新增 **§2.4 `AuthorizeSourceReadForRun`（Host→Core，host-control envelope）**：
  - **请求（closed shape）**：`{"grant_ids":["<source-read grant id>"...1..N], "command":"<PipelineCommand>", "scope":{...PipelineScope...}}`；未知键/缺键/类型错误/空 `grant_ids`（>64 上限）→ `INVALID_REQUEST`。
  - **响应**：`{"bound_pages":<int>, "refused":[{"page_id":"<id>","code":"<C-16 §6 code>"}...]}`；成功时 `refused` 为空数组。
  - **校验顺序（冻结）**：host-only（普通面 → `HOST_ONLY_REQUIRED`）→ session/credential（`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）→ 请求形状（`INVALID_REQUEST`）→ 每个 `grant_id` 必须为当前 host session 已注册的 source-read grant，且 live/未撤销/未过期（缺失/不匹配 → `SOURCE_ACCESS_DENIED`；过期 → `SOURCE_GRANT_EXPIRED`；撤销 → `SOURCE_GRANT_REVOKED`）→ 用与 Run 相同的 scope 展开器解析目标页（未知 command/scope → `INVALID_REQUEST`）。
  - **per-page 授权匹配（冻结）**：目标页无 binding（managed）→ 跳过；binding 非 healthy 或 publication gate 非 open → refused（`SOURCE_ACCESS_DENIED`）；存在 live grant 其签名 scope 满足 `scope.source_id == binding.source_id`、`scope.version == binding.accepted_source_version`、且某 entry 满足 `entry_key == binding.entry_id` 或 `locator == source_entries.locator` 或 `ordinal == source_entries.ordinal`（`source_entries` 与 `source_locations` 逐项核对，无路径回退）→ 记录待绑定；否则 refused（`SOURCE_ACCESS_DENIED`）。
  - **原子性（冻结）**：任何 refused 非空 → **零绑定写入**，返回 `{bound_pages:0, refused:[...]}`；否则写入进程内 grant→binding 映射（与 `bind_imported_entry` 同构：`grant_id → {source_id, version_id, entry_ids}`）并返回 `{bound_pages:N, refused:[]}`。**零 DB 写、零业务行、零资源发布、不建 plan/apply/journal。**
  - **幂等**：同一请求重复执行结果一致（集合语义；重复调用返回同一 `bound_pages`）；不得延长 grant TTL，不得撤销/复活 grant。
  - **能力**：`source.read.run/1`；缺失时不得以未知命令探测。
  - **错误码**：复用 C-16 §6 闭集，不新增；`details` 只允许计数/ID（`{bound_pages}`, `{refused_pages}`），无路径/entry 名/签名材料。
  - **脱敏**：本命令不携带路径；WireLog 仍按 §7 按 `scope`/`entries`/`path` 规则脱敏（若实现复用 register 结构）。
- §10 变更记录追加 v1.3 行。

### I-4 冻结记录与矩阵

- `doc/plan/FEA-CONTRACT-FROZEN-C06.md`：sha256 更新为 v1.2 最终字节；新增 v1.2 UNFREEZE 重冻记录（载体/复核/复核字节 vs 冻结字节/历史 pin 保留）。
- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：同上 v1.3。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C06/C16 行更新为 `FROZEN v1.2`/`FROZEN v1.3`（2026-11-06）。
- `tools/governance/verify_pins.ps1` 不修改（自动读冻结记录）；重跑应 18/18，且 C06/C16 = 预登记新值、其余 16 项不变。

### I-5 证据

- `verification/FEA-11-RUN-GRANT-1-PREREQ-1/**`：`pre-post.sha256`（两份契约改前/改后 sha）、`changed-lines.diff`（只含登记段落）、`pins.log`、`check.log`、`other-16-pins.txt`（逐项断言不变）、`carrier.md` 摘要与复核结论。

## Out（明确不做）

- 生产代码/测试：`src/**`、`tests/**`、`apps/**`（CORE+HOST 合并在 `FEA-11-RUN-GRANT-1`）。
- M2-C1/C-07/C-08/C-15/C-17/ADJ-001 与其余 16 份冻结契约字节。
- Run wire 形状/`CORE_PROTOCOL_MINOR`/新错误码；schema/迁移/依赖。
- UI/通知/扫描/删除/GC/备份；真实用户数据/AppData/外部卷/回收站；push。

## Acceptance Criteria（v3）

- [ ] **AC-P1 契约字节最小且可复核**：C-06 v1.2 与 C-16 v1.3 只包含本卡 I-2/I-3 登记的增量（新增小节/句子/能力/命令表行）；**既有 grant 形状、四维 scope、TTL≤300s、撤销/失联语义、错误闭集、§7 脱敏规则零改动**；其余 16 份冻结契约逐字节不变（`git diff --stat` + `other-16-pins.txt`）。证据：`changed-lines.diff`、`pre-post.sha256`、`git diff --name-only`。
- [ ] **AC-P2 独立 byte-level 复核 approved**：由未参与起草的独立上下文 fresh subagent 对**最终工作树字节**复核（改前/改后 diff、pin 预登记值、16 项不变、无新错误码/无 wire 变更）；结论 `approved`（P0=0/P1=0），P2/P3 处置记录；session 记入载体与 `doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r1.md`。<<证据：review 文件 + 载体 §复核结果>>
- [ ] **AC-P3 重冻与 pins**：两份冻结记录更新（新 sha256、v1.2/v1.3 变更记录、历史 pin 保留）；矩阵更新；`verify_pins.ps1` **18/18 PASS**（C06/C16 为新值、其余 16 项原值）；`check.ps1` PASS（既有 3 warnings 不新增）；`check.ps1 -TaskPath` PASS。证据：`pins.log`、`check.log`。
- [ ] **AC-P4 载体与不夸大**：载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` 含触发/授权/变更点/兼容/回退/复核要求/结果；卡面/Handoff 明写「契约就绪 ≠ 实现/产品可用」「长 Run/加密/重启 limitation 未解决」；未改 Run wire/schema/依赖。证据：载体 + Handoff + `scope-validation.log`。
- [ ] **AC-P5 证据与资源**：`verification/FEA-11-RUN-GRANT-1-PREREQ-1/**` 完整（每文件 sha256 + commit）；Resource Manifest 路径真实；无删除/移动仓内文件（0 文件 0 字节，`NOT_APPLICABLE`）；STATUS/PLAN/LEDGER 指针由 Lead 更新。

## 独立复核要求（byte-level）

- Reviewer：未参与本 UNFREEZE 起草/前轮复核的 fresh subagent；只读；记录 session；只读被审字节（工作树）。
- 复核对象：C-06 v1.2、C-16 v1.3、两份冻结记录、矩阵、载体、证据；核对 ①登记段落是否精确落地 ②其余 16 pins 不变 ③无 Run wire/错误码/schema/依赖变化 ④pin 预登记值可由 `Get-FileHash` 复算 ⑤载体与卡面不夸大。
- 通过标准：`approved`（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 提交并重跑 pins；未通过则返修后窄面复审，**不得**先提交后补审。

## 兼容与影响

- 旧 Core（无 `source.read.run/1`）→ Host 以 ping 判定缺失 → 不铸/不绑定、按现状 dispatch（referenced Run 仍 typed 失败）；不因全局 minor=3 推断支持。
- 新 Core × 旧 Host：既有 import/sync/scan 授权不受影响；新命令无害。
- 无 schema/migration/依赖；Run wire 零变化；M2-C1 零变化（登记滞后）。

## 已知 limitation / follow-up（预登记）

- **L-P1**：M2-C1 §5.7 HostControl 命令枚举未同步（既有滞后，D-2）；follow-up：文档一致性卡（不阻塞本卡）。
- **L-P2**：本卡不解决 300s 生命周期（L-G1）、加密 referenced Run（L-G2）、Core 重启不可续跑（L-G9）；由 `FEA-11-RUN-GRANT-1` limitation/后续卡处置。
- **L-P3**：契约就绪不构成实现授权；`FEA-11-RUN-GRANT-1` 释放前不得写码。

## 测试与门禁

| 场景 | 命令 | 预期 |
|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18/18 PASS，C06/C16 新值 |
| check | `pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath`） | PASS（3 warnings 不新增） |
| 契约 diff | `git diff --name-only <base>..HEAD`；`git diff --stat -- doc/plan` | 只含本卡 allowed_paths |
| 16 项不变 | 逐契约 `Get-FileHash` vs 冻结记录 | 16/16 原值 |
| byte 复核 | fresh subagent 只读 | approved（P0/P1=0） |
