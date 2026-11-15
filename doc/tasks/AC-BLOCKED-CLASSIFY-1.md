---
id: AC-BLOCKED-CLASSIFY-1
title: 72 条 blocked AC 的可闭性分类 + HUMAN-REQUIRED 清单
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: blocked-classify-r2（独立上下文子 agent，APPROVED_WITH_LIMITATIONS；r1 为 CHANGES_REQUESTED）
integration_commit: 1df6e7272
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - AC-CHECKBOX-AUTHORITY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」与目标 D「HUMAN-REQUIRED 清单」
base_commit: 73da5ab40
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/AC-BLOCKED-CLASSIFY-1
allowed_paths:
  - doc/tasks/AC-BLOCKED-CLASSIFY-1.md
  - doc/reviews/HUMAN-REQUIRED-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/AC-BLOCKED-CLASSIFY-1/**
---

# AC-BLOCKED-CLASSIFY-1：blocked 分类与 HUMAN-REQUIRED 清单

## 来源

`AC-CHECKBOX-AUTHORITY-1` 收口时 40 张卡共 **72 条 `blocked`** AC。目标 C 要求「AC blocked 项中
可归因闭合项」清零，目标 D 要求「剩余仅物理设备/人眼/外部账号类事项逐条登记为 HUMAN-REQUIRED
并附最小操作步骤」。本卡是这两项的前置：**先把 72 条分类清楚，再决定闭/不闭**。

## 目标（一个可观察结果）

72 条 `blocked` 全部归类，每类给出归因依据；其中真正需要人的 5 项整理成
`doc/reviews/HUMAN-REQUIRED-2026-11-15.md`，附最小操作步骤与预估耗时。

## Acceptance Criteria

- [x] **AC1 全量分类**：72 条逐条归入 **7 类**（`ARCHIVE` / `WITHDRAWN` / `HUMAN` / `RERUN` / `DOC` / `IMPL` / `MECHANISM_NA`）之一，总数与 `verify_final.py` 的 `blocked=72` 一致。 <<MET>>
      > 类目演进（r2 复核 P2-01）：初版为 6 类（含 `OTHER`）；逐条判定后发现 `OTHER` 是垃圾筐，
      > 拆为 `WITHDRAWN`（方案撤回/已裁决不实施）与 `MECHANISM_NA`（要求本身不适用），`OTHER` 归零。
- [x] **AC2 可闭性判定**：对每类给出「可否由 Agent 闭合」的判定与依据（不笼统）。可闭合计 **41 条**（`RERUN` 10 + `DOC` 9 + `IMPL` 22）；不可闭 31 条（`ARCHIVE` 13 + `WITHDRAWN` 9 + `HUMAN` 5 + `MECHANISM_NA` 4）。 <<MET>>
- [x] **AC3 HUMAN-REQUIRED 清单**：需人完成的事项逐条给出「为什么必须人做」+「最小操作步骤」+「预估耗时」；且与 `blocked` 明细不重叠、不遗漏。 <<MET>>
      > 数字对账：5 条 `HUMAN` AC（`MICA-FIX-1` AC1/AC3、`FEA-07` AC-N1/N3/N4）→ H-01(2)+H-02(3)；
      > 3 个非 `blocked` 的 `FINAL-HANDOFF` 项 → H-03/H-04/H-05；清单共 5 项。
- [x] **AC4 判定零改动**：本轮**不改任何 AC 注释的 kind**（分类不改判定）；只新增分类文档与清单。（r2 复核实测：`git diff 3d1aca73a 1df6e7272 -- doc/tasks/` 为空，40 卡注释增删 = 0。） <<MET>>
- [x] **AC5 证据与不回归**：分类明细落 `verification/AC-BLOCKED-CLASSIFY-1/`；`check.ps1` PASS、`verify_pins` 18/18、`api_inventory` OK。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**本轮只新增文档，不动 72 条 AC 的注释**。

## 禁止范围

- 不得把 `blocked` 改成 `verified`/`not-applicable`（那是下一张卡的事，需逐条验证证据）；
- 不得修改 `doc/tasks/**` 下除本卡外的任何文件；
- 不得为凑数把「真实实现缺口」归入 HUMAN。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| blocked 计数一致 | `verify_final.py`（`AC_BASE=0b517259e`） | 40 卡 / 260 AC / 72 blocked |
| 分类总数 | 分类脚本 | 72 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-ABC-01 | AC1/AC2 分类明细（72 条逐条判定）（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md | 1df6e7272 | a85454bdcbb4d3d5ec8fef60a12e1f0686e6b3751bf202792475e30f9e3051d6 | CANONICAL | WORKTREE |
| EV-ABC-02 | AC1 判定脚本（72 条显式表）（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | verification/AC-BLOCKED-CLASSIFY-1/classify_v2.py | 1df6e7272 | d2d1f91641e02d7ba0ccfba253d0f90c409f61a66eadfa7fe2b18286a038fa56 | CANONICAL | WORKTREE |
| EV-ABC-03 | AC3 HUMAN-REQUIRED 清单（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | doc/reviews/HUMAN-REQUIRED-2026-11-15.md | 1df6e7272 | b39ba98b98803129fb7e44cacae617250effeee4292d39e68e7f97bc0135b317 | CANONICAL | WORKTREE |
| EV-ABC-04 | AC5 三件套实测日志（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | verification/AC-BLOCKED-CLASSIFY-1/four-pieces.log | 1df6e7272 | ef4a181d447a14ba4da8423e525879cf34cda460f2921b1ef1c163578938d353 | CANONICAL | WORKTREE |
| EV-ABC-05 | AC1-AC5 证据总述（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | verification/AC-BLOCKED-CLASSIFY-1/README.md | 1df6e7272 | 3aa65af87dee38083244cd86d796aff534e81a8869b0ec7a684500f857d8699e | CANONICAL | WORKTREE |
| EV-ABC-06 | AC1 原理由提取脚本（WORKTREE_ENV=Windows 11 / pwsh 7 / Python 3.14） | verification/AC-BLOCKED-CLASSIFY-1/extract_full.py | 1df6e7272 | a192067d7cabf56fcbb1afb3ce5d2eb94e1ea98d19f8d115ed0a38db7668364b | CANONICAL | WORKTREE |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/AC-BLOCKED-CLASSIFY-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 commit `3d1aca73a` + r1 返修 `1df6e7272`。
- **结果**：72 条 `blocked` 全部逐条判定（7 类）：`ARCHIVE` 13 / `WITHDRAWN` 9 / `HUMAN` 5 /
  `RERUN` 10 / `DOC` 9 / `IMPL` 22 / `MECHANISM_NA` 4 = **72**；**可由 Agent 闭合 41 条**。
- **独立复核两轮**：
  - r1 `CHANGES_REQUESTED`（0/2/8/6）—— 抓出「分类是脚本原样输出、未人工复核」及 6 组误分类；
  - r2 **APPROVED_WITH_LIMITATIONS**（0/0/1/7）—— 实测 72 条逐条对应、6 组修正全部成立、
    抽查 33 条依据成立、HUMAN 清单已修好、AC4 边界 = 0 改动。
  - r2 的 P2-01（卡面 AC1 仍写 6 类含 `OTHER`）已在本卡修订（改 7 类 + 类目演进说明）；
    P3-01/P3-02（`P20` AC3/AC4 与 `V11R-C-2` AC6 的标签）已改判 `WITHDRAWN`；
    P3-03（`four-pieces.log` WARN 不全）已重采；P3-04（`V11R-C-3` 的 AC ID 为 `R1`）已修，全表 0 个 `?`。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. 本卡只做**分类**，41 条可闭项的**实际改判**尚未执行（需逐条验证证据定位符），留待后续卡；
  2. `MECHANISM_NA` 4 条（`V11R-C-1` AC1/AC6/AC7、`TASK-056` AC⑥）是否改判 `not-applicable` 待 DSH 裁决；
  3. `TASK-056` AC⑥ 的处置需引历史 commit（`1d41e00c2`/`cc4e976fd` 的 STATUS 曾含该行）或改写理由；
  4. `FEA-07` 的 `EV-AC5-P05` ID 在卡内重复（既有缺陷，本次未改）。
