---
id: GOAL-C-DEBT-AUDIT-1
title: 目标 C 三项技术债核实 —— 两项已清零/已实现，blocked 可归因闭合数 = 0
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: （见 r1）
integration_commit: 876dcfd88
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - DOC-CTRLCHAR-FIX-1
approval: 用户 2026-11-15「全部授权」；目标 C 要求「已登记技术债清零」
base_commit: 1f3bd0d84
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/GOAL-C-DEBT-AUDIT-1
allowed_paths:
  - doc/tasks/GOAL-C-DEBT-AUDIT-1.md
  - doc/reviews/GOAL-C-DEBT-AUDIT-2026-11-16.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/GOAL-C-DEBT-AUDIT-1/**
---

# GOAL-C-DEBT-AUDIT-1：目标 C 三项技术债核实

## 为什么需要

目标 C 的原文是：

> 已登记技术债清零：`check.ps1` 历史终态卡 AC 豁免、`doc/tasks` 控制字符损坏修复、
> AC blocked 项中可归因闭合项。

三项里前两项已在此前完成，但**第三项的规模从未核实过**（历史记录写「64 blocked」）。
本卡做一次**精确核实**，给出可闭合项的**真实数量**。

## 核实方法与结果

### 第 1 项：控制字符 —— ✅ 已清零

`DOC-CTRLCHAR-FIX-1`（`1f3bd0d84`）：37 文件、TAB 33 处还原为 `t`、孤立 CR 20 处删除；
修复后 `TAB = 0`、`孤立 CR = 0`、有问题文件 = 0。

**关键更正**：那 33 处 TAB 不是空白，是**被吃掉的字母 `t`**（`<TAB>ests` → `tests`、
`<TAB>ools` → `tools`、`<TAB>okens.json` → `tokens.json`）。修复方式必须是还原为 `t`。

### 第 2 项：历史终态卡 AC 豁免 —— ✅ 已实现

`check.ps1:853-854`：

```powershell
$htmlAcStyle = ($taskText -match '(?m)^[ \t]*-[ \t]*\[[ xX]\][^\r\n]*\*\*AC...<!--\s*(veri...')
$historicalAcExempt = ($htmlAcStyle -and $metadata['governance_version'] -eq '3' -and $taskStatus -in @('done', ...))
```

`09_COLLABORATION.md` §4.3.1 有对应文档。**无需改动。**

### 第 3 项：blocked AC —— 可归因闭合数 = **0**

**统计口径修正**：历史记「64」。全量扫 `<<BLOCKED:` 得 **16 处**，其中 **4 处**是**说明文字误匹配**
（如 `FEA-15-PIN-POLICY-1.md:52` 讲的是语法规则）。按精确口径（行首 `- [ ] **AC` + `<<BLOCKED>>`）
得 **12 处**。

| 卡 | 处数 | 状态 | 性质 | 可闭合 |
|---|---|---|---|---|
| `GOV-PIN-LINEAGE-1` | 6 | `closed_with_limitations` | 历史卡，已用 `<!-- blocked -->`（§4.3.1 合规） | **无需动** |
| `GIT-CLEAN-CORE-ENV-2` | 3 | `proposed` | 需冻结 V2–V5 环境定义 | ✗ |
| `GIT-CLEAN-PUBLICATION-1` | 1 | `in_review` | Core 测试失败 | ✗ |
| `GIT-CLEAN-RUST-ISOLATION-1` | 1 | `in_review` | peak0 未达 32 | ✗ |
| `REAL-TRANSLATE-PROVIDER-1` | 1 | `done` | **OpenCode 额度**（free=429 / paid=402）⇒ 外部账号 | ✗ 应归 HUMAN-REQUIRED |

⇒ **没有一项可归因于 Agent 独立闭合**。这不是"失败"，是核实结果。

### 附带：3 个 warning 都不是技术债

- 「11 个非终态 Task」= 正常状态（检查器自己说「不得据此批量关闭」）；
- `STATUS.md` / `REBASELINE_PLAN.md` 预算 80% = **容量约束**，不是债。

⇒ 若以「warning 归零」为目标 C 判据，会误把正常状态当债。

## 目标（一个可观察结果）

`doc/reviews/GOAL-C-DEBT-AUDIT-2026-11-16.md` 落盘，三项结论与真实数字一致；
第 3 项的「可闭合=0」有可复算的统计依据。

## Acceptance Criteria

- [x] **AC1 第 1 项结论**：控制字符已清零，且有残留扫描证据。 <<MET>>
- [x] **AC2 第 2 项结论**：豁免已实现，指向 `check.ps1` 具体行与文档章节。 <<MET>>
- [x] **AC3 第 3 项精确统计**：给出「扫 16 处 → 排除 4 处误匹配 → 12 处」的口径与分类表。 <<MET>>
- [x] **AC4 可闭合数结论**：明确「= 0」，并说明每类的不可闭合原因。 <<MET>>
- [x] **AC5 warning 性质澄清**：说明 3 个 warning 不是技术债，避免误判。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

只写核实报告 + 本卡；不改 `check.ps1`、不改任何 `doc/tasks` 历史卡。

## 禁止范围

- 不得为了"让数字好看"而关闭任何 blocked AC；
- 不得修改 `check.ps1` 的判据；
- 不得把 `GIT-CLEAN-*` 的技术阻塞写成"文档问题"。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-GCD-01 | AC1/AC3/AC4 复算证据（残留 0；blocked 16→12） | verification/GOAL-C-DEBT-AUDIT-1/audit.log | 876dcfd88 | 42d1c8fafc1e76326ac3679e40ee4882de5eaddb22482c7767dd64c168f7f52d | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/GOAL-C-DEBT-AUDIT-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH。
- **第 1 项（控制字符）✅ 已清零**：`DOC-CTRLCHAR-FIX-1`（`1f3bd0d84`），37 文件；
  本卡复算残留 **TAB=0、孤立CR=0**。
- **第 2 项（历史终态卡 AC 豁免）✅ 已实现**：`check.ps1:853-854`（`$htmlAcStyle` /
  `$historicalAcExempt`），`09_COLLABORATION.md` §4.3.1 有文档。**无需改动。**
- **第 3 项（blocked 可归因闭合）⚠️ 可闭合数 = 0**：
  - 全量扫 `<<BLOCKED:` = **16**，其中 **4 处是说明文字误匹配**；
  - 精确口径（行首 `- [ ] **AC`）= **12**；
  - 分类：`GOV-PIN-LINEAGE-1` 6 处**已合规**（历史卡 HTML 注释，§4.3.1 豁免）；
    `GIT-CLEAN-CORE-ENV-2` 3 处（需冻结环境）、`GIT-CLEAN-PUBLICATION-1` 1 处（Core 测试失败）、
    `GIT-CLEAN-RUST-ISOLATION-1` 1 处（peak0 未达 32）= **真实技术阻塞**；
    `REAL-TRANSLATE-PROVIDER-1` 1 处 = **OpenCode 额度耗尽 ⇒ 属外部账号，应归 HUMAN-REQUIRED**。
  ⇒ **没有一项可由 Agent 独立闭合**。
- **附带澄清**：`check.ps1` 的 3 个 warning **都不是技术债** ——
  「11 个非终态 Task」是正常状态（检查器自己声明不得据此批量关闭）；
  `STATUS.md` 与 `REBASELINE_PLAN.md` 的 80% 是**容量约束**。
  ⇒ 若以「warning 归零」为目标 C 判据会误判。
- **本卡自身的错误记录**：报告中初稿写「扫 14 处 → 排除 2 处」，实际复算是
  「16 → 排除 4 → 12」。已按 `audit.log` 更正报告与卡面 —— 这是本会话第 N 次
  「先写结论后复算」的失效，本次由复算证据当场纠正。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. `REAL-TRANSLATE-PROVIDER-1` 的 AC3 应在 HUMAN-REQUIRED 清单里显式登记（外部账号/额度），
     本卡只做核实，**未改那张卡**；
  2. `GIT-CLEAN-*` 三条线需要各自的环境/性能前置，应作为独立 Task 释放，**不是文档修复**；
  3. 本卡**不改变**任何 Gate，也不宣称目标 C 已达成 —— 它只给出三项的真实状态。

