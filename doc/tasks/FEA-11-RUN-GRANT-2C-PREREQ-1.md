---
id: FEA-11-RUN-GRANT-2C-PREREQ-1
title: 2C 长 Run 续期契约前置（C-06 v1.3 + C-16 v1.6：mid-run 重复建立语义；2 pins）
kind: contract
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/2C-LONG-RUN-RENEWAL-scope-r1.md`（fresh subagent `857903ae-…`，**READY-WITH-UNFREEZE**：严格读 C-06 v1.2→v1.3 + C-16 v1.5→v1.6 **2 pins**；0-pin 解释不成立）；Codex 不可用 → ZCode 故障转移裁决（`cbdf231a-…`：**APPROVE 2 pins 路径**，D-1…D-10 见卡）；DSH 裁决 D-1…D-10（见下）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；未参与起草）：r1 changes_requested（P2×4）→ 处置 → r2 changes_requested（P2×1）→ 处置 → r3 changes_requested（P2×1）→ 处置 → r4 changes_requested（P2×1）→ 处置 → r5 changes_requested（P2×1）→ 处置 → **r6 `approved`（P0=0/P1=0/P2=0/P3=1 非阻断；session `308751b9-…`；reviewed_head `c1e19ed82`）**；报告 `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r1…r6.md`；载体 §6
depends_on:
  - FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
base_commit: null
branch: null
worktree: null
integration_commit: 7317837d5
delivery_head: 7317837d5
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-RUN-GRANT-2C-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2C-PREREQ-1.md
  - doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-*-C06-C16-RUN-RENEWAL.md
  - doc/handoffs/FEA-11-RUN-GRANT-2C-PREREQ-1-*.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C06.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-RUN-GRANT-2C-PREREQ-1/**
out_of_scope:
  - 生产代码/测试（src/**、apps/**、tests/**）—— 实现卡 `FEA-11-RUN-GRANT-2C` 另起
  - C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约字节；Run wire/TTL/撤销/错误闭集/能力
  - App/UI；自动重新授权；schema/依赖；真实用户数据；push
---

# FEA-11-RUN-GRANT-2C-PREREQ-1：2C 长 Run 续期契约前置（2 pins）

> **状态：`ready`（契约前置；只起草 + 独立 byte-level 复核 + 重冻；不实现）。**
> 来源：`2C-LONG-RUN-RENEWAL-scope-r1`（READY-WITH-UNFREEZE）+ ZCode 裁决（APPROVE 2 pins）；实现卡 `FEA-11-RUN-GRANT-2C` 依赖本卡。

## DSH 裁决（D-1…D-10，2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| D-1 | **2 pins** | C-06 v1.2→v1.3 + C-16 v1.5→v1.6；其余 16/18 pins 逐字节不变。0-pin 解释**不成立**（未覆盖新 grant_ids/新请求；「同一 binding 多份 grant」是读端选择规则，不是建立时机授权）。 |
| D-2 | **改动面（只追加、不改既有句）** | C-06 §2.2 `:43` 追加 mid-run 重复建立语义（Run 非终态期间，对同一冻结 `{command, scope}` 重复建立；每次新铸新 grant（各自 ≤300s、顺序重验 facts）；不得延长既有 grant、不扩 scope、不撤销后重建、不改选 command/scope）；C-16 §2.4 `:78` 用途句追加（可在 Run 非终态期间重复调用；每次只绑定当次 live grants；不延长 TTL、不改 scope、不绕过撤销；任一页不可授权仍整请求 typed 拒绝、零映射写入）。 |
| D-3 | **拆卡** | PREREQ-1（本卡，契约 2 pins）+ 实现卡 `FEA-11-RUN-GRANT-2C`（Host-only）；卡 id 采 `FEA-11-RUN-GRANT-2C`，旧别名 `FEA-11-2C-LONG-RUN-RENEWAL-1` 仅登记、**不得并存**。 |
| D-4 | **方案 (a)** | Host 非终态期间对同一冻结 `{command, scope}` 周期重铸 grant + 重发 `AuthorizeSourceReadForRun`；零 Core、零 Run wire；每轮重走 `Registry.Authorize`+facts 重算。延 TTL / Core sliding / Core→Host 协议均否决。 |
| D-4b | **folder 成本** | 接受「逐成员 sha256 重算 + 单轮超限 typed skip」，**拒绝**复用旧 digest/仅比 volume+file id（= weaker identity，违反 R-2）；skip 计数入 EV；不得并行绕 `_gate`；登记 L-G8 放大。 |
| D-5 | **接线点** | dispatcher post-dispatch 钩子（`HostCommandDispatcher.cs`，Host 内部零 wire）；**不**触 App；不得 (i)/(ii) 同改。 |
| D-6 | **不加 TTL 测试 seam** | 时间维用 in-process fake clock（先例 `tests/fea11/test_source_run_grant.py:698-716`）；gated IPC 只证「同 scope 二次 mint+bind+可读」；不缩短生产 TTL。 |
| D-7 | **L-G1 只降级不关闭** | 「无续期」→「有续期 + 子限制」（单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；STATUS/Handoff/EV 措辞按此。 |
| D-8 | **红线** | 10 条：不延单 grant 的 `expires_at`/不放宽 identity/不绕过撤销/不扩 scope 或加新 source/失败不放行/不自动重新授权/不新增 Run 码 wire 能力/不阻塞请求线程/不作新授权入口/不宣称任意长 Run 可用；`interval + 单轮 mint 时长 < 300s` 作为可判别预算条款。 |
| D-9 | **基线/证据** | clean head 重测；pytest 3360/10、.NET 1660/0/95（既有 flaky 隔离）；`verification/FEA-09` 写卫生如实记录。 |
| D-10 | **命名** | 实现卡 `FEA-11-RUN-GRANT-2C`；PREREQ `FEA-11-RUN-GRANT-2C-PREREQ-1`。 |

## In（本卡变更点，冻结）

### I-1 载体
`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL.md`（触发/授权/缺口/逐项修订/安全分析/兼容/回退/复核要求/结果）。

### I-2 C-06 v1.3（`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`）
- 头部状态 → `FROZEN v1.3（2026-11-07 重冻；v1.0/v1.1/v1.2 历史）`；日期行补 v1.3；载体链接。
- §2.2 `:43` 追加 mid-run 重复建立语义（D-2 原文；只追加，不改既有句）。
- §2.3/§3/§4 零改动（`AuthorizeSourceReadForRun` 行保持）；§5 追加条件 ⑥ + §6 变更记录 v1.3 行。

### I-3 C-16 v1.6（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`）
- 头部状态 → `FROZEN v1.6`；日期行补 v1.6；载体链接。
- §2.4 用途句追加 D-2 原文；wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动。
- §10 冻结条件追加 ⑧ v1.6 行；变更记录追加 v1.6 行。

### I-4 冻结记录与矩阵
- `FEA-CONTRACT-FROZEN-C06.md` / `FEA-CONTRACT-FROZEN-C16.md`：pin → v1.3 / v1.6 最终字节 sha256；历史 pin 保留；§1B/§9 记录。
- `FEA-CONTRACT_FREEZE_MATRIX.md`：C-06 → v1.3、C-16 → v1.6（2026-11-07）。
- `verify_pins.ps1` 不改；18/18（C06/C16 新值、其余 16 不变）。

### I-5 证据
`verification/FEA-11-RUN-GRANT-2C-PREREQ-1/**`：pre/post sha（C-06/C-16）、changed-lines.diff、other-16-pins、pins/check 日志、carrier。

## Out

- 生产实现（`FEA-11-RUN-GRANT-2C`）；C-05/C-15/C-17/C-07/M2-C1；Run wire/TTL/撤销/错误闭集/能力；App/UI；自动重新授权；schema/依赖；真实用户数据；push。

## Acceptance Criteria（v3）

- [x] **AC-T1 契约增量最小**：C-06 v1.3 只含 I-2（§2.2 一句 + §5 条件 ⑥ + §6 变更记录 + 头部）；C-16 v1.6 只含 I-3（§2.4 一句 + 头部 + §10 条件/记录）；C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约逐字节不变；无新命令/能力/错误码/wire 字段/TTL 变更/schema/依赖。 <<MET>>
- [x] **AC-T2 安全语义明确**：两句逐句语义等价（且更严）含「不延长任何 TTL/不扩 scope/不绕过撤销/不改选 command/scope/每次新铸新 grant 并顺序重验 facts/任一页不可授权整请求 typed 拒绝零映射写入」；不构成「放宽授权/长期通行证/恢复入口」。 <<MET>>
- [x] **AC-T3 独立 byte-level 复核 approved**：fresh subagent 复核最终字节（diff 逐行、安全语义无放宽、16 项不变、pin 可复算）；P0/P1=0；session/reviewed_head 入载体。 <<MET>>
- [x] **AC-T4 重冻与 pins**：FROZEN-C06/C16 更新；矩阵更新；`verify_pins` **18/18**（C06/C16 新值、其余 16 原值）；`check.ps1`（默认 + `-TaskPath`）PASS。 <<MET>>
- [x] **AC-T5 载体与不夸大**：载体含触发/授权/变更点/安全/兼容/回退/复核要求/结果；明写「契约就绪 ≠ 实现/产品可用」「L-G1 只降级不关闭」；未改 Run wire/TTL/撤销/错误闭集/能力。 <<MET>>

## 独立复核要求（byte-level）

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：I-2/I-3 逐项落地；C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约零字节；无新命令/能力/错误码/wire 字段/TTL 变更；pin 可复算 18/18；载体/卡不夸大（L-G1 只降级不关闭）。
- 通过标准 approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## ZCode 裁决记录

- **已记录（`cbdf231a-…`，2026-11-07，只读）**：APPROVE 2 pins 路径（C-06 v1.3 + C-16 v1.6）；0-pin 不成立（幂等条款对象是「同请求」；「同一 binding 多份 grant」是读端选择规则）；方案 (a) 成立；红线 10 条充分；D-4b 接受「重算+单轮超限 typed skip」；接线点采 dispatcher post-dispatch；不加 TTL seam；L-G1 只降级不关闭；卡 id 采 `FEA-11-RUN-GRANT-2C`。

## Review 处置（DSH，2026-11-07；append-only）

- 独立 byte-level 复核 r1–r6：逐轮 `changes_requested`（记录/证据/卡一致性 + C-06 两处措辞修正，契约安全语义自 r1 起无放宽）→ 逐项处置 → **r6 `approved`（P0=0/P1=0/P2=0/P3=1 非阻断）**；session `308751b9-…`，reviewed_head `c1e19ed82`。
- 最终字节：C-06 v1.3 sha256 `75f8e2b4…`（blob `b537e76d…`）；C-16 v1.6 sha256 `b8f46fb1…`（blob `f8f31f55…`）；其余 16 契约零字节；无新命令/能力/错误码/wire/TTL/schema/依赖。
- ZCode 裁决（`cbdf231a-…`）：APPROVE 2 pins 路径（0-pin 不成立）；方案 (a) Host 周期重铸；红线 10 条；L-G1 只降级不关闭。
- 不改变 AC-T1…T5 MET 判定。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/carrier.md | 7317837d5 | b10872652f2d92ce43cbe68730d098a8775f1222bc234fde5da033ad6b320c33 | CANONICAL |
| EV-02 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/changed-lines.diff | 7317837d5 | 9bacc8a0fd9b5a87355632f09521ccaba9a6105cb96062cd7c7b187380594664 | CANONICAL |
| EV-03 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/logs/check-taskpath.log | 7317837d5 | 634e072301dfad18a3f6cdaa683846173b9827cc51dd2bc053049f537f93a424 | CANONICAL |
| EV-04 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/logs/check.log | 7317837d5 | 634e072301dfad18a3f6cdaa683846173b9827cc51dd2bc053049f537f93a424 | CANONICAL |
| EV-05 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/logs/pins.log | 7317837d5 | 11bfd4130c47fa0c7da84c8ef05d9474bfd5e2624030b7196d731326b9b3af34 | CANONICAL |
| EV-06 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/other-16-pins.txt | 7317837d5 | 431acd2a381aa353c9c620d0cf5fb35940d9b43dc89bef61d53d3d5966cc441a | CANONICAL |
| EV-07 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/pre-post.sha256 | 7317837d5 | 56d4670d4eddc323cfdcea04632ddf2c3098ddf10a196f6c4a77fdcc3e4ad5a7 | CANONICAL |
| EV-08 | AC-T4 | verification/FEA-11-RUN-GRANT-2C-PREREQ-1/EV.md | 7317837d5 | b3c56b70b2e35a088c610f9b0e969d0c5e0337c4b70b73d9093aed01aab79d7f | CANONICAL |

> 证据树逐文件 sha256 以本表为准；r1–r6 报告不在 evidence_dir，按载体 §6/卡面引用。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改两契约/冻结记录/矩阵/载体/卡/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2C-PREREQ-1/` 保留（无独有产品数据） |

## Closeout Record（2026-11-07）

- **状态**：`done`；delivery/integration = `7317837d5`（C-06 v1.3 + C-16 v1.6 + FROZEN×2 + 矩阵 + 载体 + r1–r6 报告 + 证据 + PREREQ 卡）。
- **AC 判定**：AC-T1…AC-T5 **全 MET**。
- **Review 处置**：r1–r5 changes_requested → 处置 → **r6 approved（P0=0/P1=0/P2=0/P3=1 非阻断）**。
- **门禁数字**：pins **18/18**（C06 `99831a20…`→`75f8e2b4…`；C16 `a7f57ebd…`→`b8f46fb1…`；其余 16 项实测 UNCHANGED）；check（默认+`-TaskPath`）PASS(3 warnings)；C-06 变更 +3 行/1 处（§2.2 追加 + §5 ⑥ + §6 记录）、C-16 +2 行/2 处（§2.4 追加 + §10 ⑧ + 记录）；C-05/C-15/C-17/C-07/M2-C1 零字节；全量 pytest/.NET **NOT_RUN**（契约-only；由实现卡门禁实跑）。
- **limitations / follow-up**：实现卡 `FEA-11-RUN-GRANT-2C` 未交付；L-G1 **只降级不关闭**（子限制：单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；B2/folder/L-S4-1/L-R1 保留。
- **指针清理**：STATUS 当前 Task → `FEA-11-RUN-GRANT-2C`（实现，base=本 closeout 提交）；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
