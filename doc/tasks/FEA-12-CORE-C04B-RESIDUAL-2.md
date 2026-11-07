---
id: FEA-12-CORE-C04B-RESIDUAL-2
title: C-04b v1.2 UNFREEZE（R-1 谓词/R-2 措辞/R-3 术语/R-4 节名/R-5 来源/R-8 单条 manifest）+ M2-C1 rev 2.15 同步
kind: contract
governance_version: 3
status: ready
approval: 用户 AUTORUN 指令（2026-11-08，全部授权/自主裁决/不询问用户）；权威 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（session `0fc94b7f…`；verdict recommended；§3.3 给出 UNFREEZE 确切行/句与 pin 口径：**C-04b 1/18 pin + M2-C1 记录型 rev（0/18 机械 pin）**）；**DSH 裁决（2026-11-08，裁决人=DSH）**：按 AUTORUN §2 判据 (b) 立项清偿契约债务；C-04b 升 v1.2、M2-C1 升 rev 2.15（仅措辞/谓词同步，规则不变）；R-1 的**代码**修复归 `FEA-12-CORE-C04B-RESIDUAL-3`；P3-03/P3-04 类「改字节即变 pin」项不在本卡
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本卡起草；session 见 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md`）
depends_on:
  - FEA-12-CORE
  - FEA-12-CORE-C04B-RESIDUAL-1
base_commit: d91d9b6cc
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE-C04B-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md
  - doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-*.md
  - doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-12-CORE-C04B-RESIDUAL-2/**
out_of_scope:
  - C-04b/M2-C1 以外的契约字节（C-17/C-06/C-15/C-16/C-07 等零 diff）
  - 删除协议语义/错误码/wire minor/能力/schema/迁移/依赖变更（本卡只同步措辞与谓词文字）
  - R-1 的代码实现（`src/infrastructure/sqlite/library.py`）——归 RESIDUAL-3
  - `src/**`、`apps/**`、`tests/**`
  - ADJ-001/C-01b/Gate 语义；STATUS/PLAN/LEDGER（Lead 维护）
---

# FEA-12-CORE-C04B-RESIDUAL-2：C-04b v1.2 + M2-C1 rev 2.15（契约债务清偿）

> **状态：`ready`（DSH 起草并实施；1/18 pin + M2-C1 记录型 rev）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` §2（8 项逐项事实）与 §3.3（UNFREEZE 确切行/句、
> pin 精确口径、复核与提交隔离要求）；上游登记 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A `R-1…R-8`。

## 目标

把 C-04b 的 6 项**契约正文**债务就地清偿（措辞/谓词文字，不改任何规则行为）：
**R-1** artifact 成员谓词补 `media_artifacts.book_id = 本书`；**R-2** §2.0「单一字段」措辞纠偏；
**R-3** 删除无定义术语 `separate/detached` + 写死 representative 排序；**R-4** §1 表 M2-C1 行号改节名；
**R-5** 首确认「预览 `book_ids`」改「请求 `book_ids`」+ 单条 digest 来源写清；**R-8** 单条 manifest 批次字段取值写死。
同步 M2-C1 至 **rev 2.15**（`:18` banner 批量限定、`:30` history 记录、`:814/:815/:819` 来源与措辞、
`:953/:954` DTO 注释、**`:972` §5.13 PD-01 段**）。**R-1 的代码实现不在本卡**（RESIDUAL-3）。

## Acceptance Criteria

- [x] **AC-1 C-04b v1.2 六处落地**：状态行 v1.2 + §0 增 v1.2 摘要 + §6 变更记录；`:18`/`:53` 补 artifact 谓词、删 `separate/detached`、写死 representative 排序；`:21`/`:71` 单条 manifest 取值；`:28-32` 行号改节名；`:44` 措辞纠偏；`:64` 请求 `book_ids`；`:69` 单条来源 `inventoryDigests[bookId]`。**不改**任何校验规则/错误码/字段名/语义。 <<MET>>
- [x] **AC-2 M2-C1 rev 2.15**：`:18` banner retry 描述限定「批量」；`:30` Revision history 追加 2.15（说明仅同步 C-04b v1.2 措辞与谓词，规则同 2.14）；`:814` 补单条取 `inventoryDigests[bookId]`；`:815` 「预览 `book_ids`」→「请求 `book_ids`」；`:953` 删 `separate/detached`；**`:972` §5.13 PD-01 段补 artifact 谓词**；`:954` 补 artifact 谓词。**不新增**命令/字段/错误码，不改 §5.11 家族语义。 <<MET>>
- [x] **AC-3 独立 byte-level 复核**：fresh subagent（未参与起草）对 C-04b v1.2 + M2-C1 rev 2.15 做逐行复核并 `approved`（P0/P1=0）；报告入库 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md`。 <<MET>>
- [x] **AC-4 pin 账**：`verify_pins.ps1` **18/18 PASS**（C-04b 重签为新 sha、其余 **17 项 UNCHANGED** 实测）；M2-C1 **不在 18 pin 映射**（0/18 机械 pin），其新 sha256 手工登记进冻结记录 §1B/§4C 与载体；`check.ps1`（默认 + `-TaskPath`）PASS。 <<MET>>
- [x] **AC-5 零漂移**：C-17/C-06/C-15/C-16/C-07 等其余契约 blob 零 diff；`src/**`、`apps/**`、`tests/**`、`schema.py`、依赖零 diff；无新错误码/命令/能力/`PROTOCOL_MINOR`。 <<MET>>
- [x] **AC-6 证据与不夸大**：EV（改前/改后字节、diff、pin 复算、门禁实跑）、Resource Manifest、Closeout Record 完整；**不得**写「8 项 residual 全部关闭 / R-1 已修复」（R-1 的代码归 RESIDUAL-3，本卡只改契约文字）。 <<MET>>

## 依赖与下一步

- 依赖：`FEA-12-CORE`（residual 来源）、`FEA-12-CORE-C04B-RESIDUAL-1`（docs 收口，`698ac9524`）。
- 完成后：释放 `FEA-12-CORE-C04B-RESIDUAL-3`（R-1 artifact 成员谓词**代码**修复；需与 v1.2 谓词一致；0/18 机械 pin）。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1..AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-2/EV.md | PENDING-COMMIT | 77646bb471934ee4796d95e986b5786c1e4b904e70b77a7e370d4bd3732b6f44 | CANONICAL |
| EV-02 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/check-taskpath.log | PENDING-COMMIT | 40fdc9d90b869bf6f5ebaef23aec0dfa6bf12f72bcc91663352840d3fd2df0ca | CANONICAL |
| EV-03 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/check.log | PENDING-COMMIT | 40fdc9d90b869bf6f5ebaef23aec0dfa6bf12f72bcc91663352840d3fd2df0ca | CANONICAL |
| EV-04 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/code-drift.log | PENDING-COMMIT | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL |
| EV-05 | AC-1/AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/diffstat.log | PENDING-COMMIT | 40389e9ce40431596ae9e4255e53e6e7d269e02cc1ac8a72310acb952cd4b932 | CANONICAL |
| EV-06 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/other-contracts-drift.log | PENDING-COMMIT | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL |
| EV-07 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/pins.log | PENDING-COMMIT | aedf5a6b579c255e4b1544ccc1479aaf8517d6cdd711f9e7a12018f08e6f118d | CANONICAL |
| EV-08 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/scope-changed.log | PENDING-COMMIT | 3e8141d6f581ed746c915e97865c4742ac22ef35b094144ed2e4ceed792d3d9b | CANONICAL |
| EV-09 | AC-1 | verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/sha-check.log | PENDING-COMMIT | 5a704162e2d2fe7383f9c5ead1e6385e352acfa504ea5e2abff144366e6b01ac | CANONICAL |
| EV-10 | AC-1/AC-2 | verification/FEA-12-CORE-C04B-RESIDUAL-2/unfreeze.diff | PENDING-COMMIT | 6b6bb9ca133c37a48323213355c442ce63e7dd9dda7a499c74de022530c4e0bc | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改 C-04b/M2-C1 契约字节 + 冻结记录/矩阵/载体/卡/证据；仓外复核/探针目录保留（无独有数据）；无残留进程 |

## Closeout Record（2026-11-08；Lead）

- **状态**：`done`；`integration_commit`/`delivery_head` = **`4b304c0c`**（UNFREEZE 提交：C-04b v1.2 + M2-C1 rev 2.15 + 冻结记录 + 矩阵 + 载体 + 卡 + 证据）。
- **AC 判定**：AC-1…AC-6 **全 MET**。
- **Review 链**：r1 `changes_requested`（P0=0/P1=2/P2=1/P3=4）→ 返修 → r2 `changes_requested`（P0=0/P1=1/P2=2/P3=2；artifact fallback 应取 pointer 首项，reviewer 探针复现）→ 再返修 → **r3 `approved`（P0=0/P1=0/P2=3/P3=4；session `98692074-…`）**；r3 三案探针确认 representative 与实现逐要素等价。
- **门禁**：pins **18/18**（其余 17 blob 与 HEAD 全同）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；numstat C-04b **26/15**、M2-C1 **20/16**（全为文字）；`PROTOCOL_MINOR=3` 与 wire minor 不变；`src/**`/`apps/**`/`tests/**` 零 diff；`git diff --check` 干净。
- **残余 P2/P3（非阻断）**：P2-1/P2-2/P2-3 已在本 closeout 前清理（记录 representative 表述、载体过宽句、EV numstat）；P3-1（M2-C1 `:140` 仍写「文档 rev 2.14」）**保留不改**（属历史段落；改契约字节需新一轮独立复核，收益低于成本）；P3-2/P3-3/P3-4 已处理。
- **limitation 保留**：**R-1 代码未改**（`library.py:1178-1190` 仍 page/chapter join）→ 契约与实现当前不一致、**L-3 仍有效**，归 `FEA-12-CORE-C04B-RESIDUAL-3`；**不得**写「8 项 residual 全部关闭 / R-1 已修复」。
- **指针清理**：Lead 更新 STATUS/PLAN/LEDGER 并释放 `FEA-12-CORE-C04B-RESIDUAL-3`。
- **push**：随本轮 Lead 统一 push（记录见 handoff §24）。
