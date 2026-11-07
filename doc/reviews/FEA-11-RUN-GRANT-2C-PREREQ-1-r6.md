---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE r6 最终收口（r5 delta；2 pins）
reviewer: DSH fresh subagent（独立上下文；session 308751b9…；未参与本 UNFREEZE 起草/r1–r5；只读）
session: 308751b9-d621-43b1-8a0c-58f6c9d256fe
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_delta_r6
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: approved
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立最终收口复审 r6（delta）

## 结论先行

- **verdict：`approved`**（P0=0 / P1=0 / P2=0 / **P3=1**，非阻断记录文本）。
- **A PASS、C PASS、D PASS、E PASS；B FAIL（仅 1 项 P3）**：R5-001 已实质关闭（§2 第 7 条 ⏳、两处 §1B 均「待 r6 收口」、无旧轮次残留），但矩阵 `:24`/`:37` 条件列仍写「r1–r4 处置后待 r6 收口」（漏 r5），载体 `:60`「矩阵…统一」因此不实。
- **契约字节/pins 零回归**：C-06 `75f8e2b4…` / blob `b537e76d…`；C-16 `b8f46fb1…` / blob `f8f31f55…`；`verify_pins` **18/18**；其余 16 契约 `changed=0`；三锚未软化；A/C/D/E 无阻断。
- **r5 findings**：R5-001 **CLOSED**、R5-002 **CLOSED**；承继 R4-001/R4-002 **CLOSED**、R3-004 **ACCEPTED**。
- **唯一待办（非阻断）**：DSH 在落 r6 approved 的同一次 append-only 提交中把矩阵两格改为 `r1–r5`（并修载体 `:60` 的「统一」表述）后，方可提交/推送；不改契约字节。

## A. R5-001 关闭 — PASS

| 子项 | 结果 | 证据 |
|---|---|---|
| FROZEN-C06 §2 有 v1.3 第 7 条（⏳） | PASS | `:52`「v1.3：mid-run 重复建立语义经独立 byte-level 复核 **r6 pending**（r1–r5 处置后）」；状态列 `⏳`，无 ✅ |
| FROZEN-C06 §1B v1.3 行措辞 | PASS | `:40`「…= v1.3 冻结字节；**r1–r5 处置后待 r6 收口**」 |
| FROZEN-C16 §1B v1.6 行措辞 | PASS | `:53`「…= v1.6 冻结字节；**r1–r5 处置后待 r6 收口**」 |
| 无「待 r4/r5 收口」残留 | PASS | 全文检索：仅载体 `:59` 为 r5 报告的历史引文；无现行记录残留 |

## B. 记录链 — FAIL（1 项 P3，非阻断）

| 位置 | 结果 | 证据 |
|---|---|---|
| 载体 §6 | PASS | `:52-60`：r1 → 处置 1 → r2 → r3 → 处置 3 → r4 → 处置 4 → r5 → 处置 5（本轮）；`:60`「r6 pending」 |
| FROZEN-C06 §7 | PASS | `:93`「r1→r2→r3→r4→r5 changes_requested → 处置 → **r6 pending**」 |
| FROZEN-C16 §10 | PASS | `:125` 同链；`:51` 条件 8 `⏳` |
| 矩阵 C-06/C-16 条件列 | **FAIL（P3）** | `:24`/`:37`「pending（**r1–r4** 处置后待 **r6** 收口）」——只改轮次未改范围，漏 r5；与本表其余五处 r1–r5 不一致 |
| EV.md | PASS | `:3`「r1→r5 changes_requested→处置→r6 pending」 |
| 载体两副本同字节 | PASS | 均 7730 B、sha256 `303165ab…`；`-ceq` True |
| 无预填 approved（记录层） | PASS | 载体/EV/矩阵/FROZEN §2/§7/§10/§1B 均 pending/⏳；契约字节内承继文本见观察 |

## C. 契约字节 / pin 不回归 — PASS

| 检查 | 结果 | 实测 |
|---|---|---|
| C-06 sha256 / blob | PASS | `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84` / `b537e76dad1e4075eb6ffd213e6c01954a256011` |
| C-16 sha256 / blob | PASS | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` / `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` |
| `verify_pins.ps1` | PASS | 现场重跑 `PIN AUDIT: PASS (all 18)`；C06 `75f8e2b4eb80`、C16 `b8f46fb1feec`；与 `logs/pins.log` 逐字节相等 |
| 其余 16 契约零字节 | PASS | `other-16-pins.txt` 16/16 `UNCHANGED`、`changed=0`；`git diff --name-only HEAD` 仅 6 个 doc 文件，`src/apps/tests` 零 diff |
| 三锚 / 改动面 | PASS | C-06 `:37` dispatch 前、`:40` ≤300 秒/不得长期通行证、`:43` 不延长 `expires_at`/不扩 scope/不撤销后重建/不改选/整请求 typed 拒绝零映射写入；C-16 `:78` 不延长任何 TTL/不改 scope/不绕过撤销；C-06 4 hunk（6+/4−）、C-16 4 hunk（5+/4−），无新命令/能力/错误码/wire/TTL/schema/依赖 |

## D. 证据 — PASS

| 对象 | 结果 | 实测 |
|---|---|---|
| EV 逐文件 sha 7/7 | PASS | carrier `303165ab…`、changed-lines `9bacc8a0…`、check/check-taskpath `634e0723…`、pins `11bfd413…`、other-16 `431acd2a…`、pre-post `56d4670d…` 全部同值 |
| carrier.md 与载体一致 | PASS | 同 sha `303165ab…`、同 7730 B；内容 `-ceq` True |
| pre / post | PASS | pre C-06 `99831a20…`、C-16 `a7f57ebd…`（HEAD blob `9bbd93a01…`/`67c741d3b…` 按原始字节复算同值）；post `75f8e2b4…`/`b8f46fb1…` |
| changed-lines 与真实 diff | PASS | 归一化 `norm_equal=True`（10261 chars）；原生 `git diff HEAD -- C-06 C-16` 与证据逐字节相等 |
| pins/check 日志可复现 | PASS | 重跑 `pins.log` 408 B、sha `11bfd413…` 逐字节相等；`check.log`/`check-taskpath.log` 各 427 B、sha `634e0723…` 逐字节相等；check = `PASS (3 warnings)` |
| 证据卫生（承继） | ACCEPTED | `pre-post.sha256` post 值折行；`logs/*` 无命令/日期头（R3-004 已接受，不新计） |

## E. 不夸大 — PASS

| 检查 | 结果 | 证据 |
|---|---|---|
| L-G1 只降级不关闭 | PASS | 载体 `:37` 独立句 + 6 项子限制（单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；卡 D-7 |
| 契约就绪 ≠ 实现/产品可用 | PASS | 载体 `:37`；FROZEN-C06 `:63`、FROZEN-C16 `:59`/`:63` 均「不构成实现授权」；卡 `:40`「只起草 + 复核 + 重冻；不实现」；未宣称 Run wire/TTL/撤销/错误闭集/能力变更或产品 AC 达成 |

## Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R6-001 | **P3** | 矩阵 `:24`/`:37`；载体 `:60` | 两处条件列仍「r1–r4 处置后待 r6 收口」，漏 r5，与 FROZEN-C06 `:40`/`:52`、FROZEN-C16 `:53`/`:51`、载体 §6 `:60`、EV `:3` 的 r1–r5 不一致；r5 已在观察中要求「r6 前需修正」，本轮只改轮次；载体「矩阵…统一」因此不实 | append-only 改「r1–r5 处置后待 r6 收口」（approved 后按同格式改 approved）；不动契约字节/pins |

## r5 findings 状态

| ID | 级别 | 状态 | 说明 |
|---|---|---|---|
| R5-001 | P2 | **CLOSED** | §2 第 7 条已补（⏳）；两处 §1B 均「r1–r5 处置后待 r6 收口」；无旧轮次残留（仅 r5 历史引文） |
| R5-002 | P3 | **CLOSED** | §2 v1.3 行存在；载体对 §2/§1B 的「已补」陈述已成立；但「矩阵统一」仍不实，另立 R6-001 |
| R4-001 | P2 | **CLOSED**（r5 认定） | 主记录链已统一；其 §1B 残留随 R5-001 关闭 |
| R4-002 | P3 | **CLOSED（本轮）** | FROZEN-C06 §2 v1.3 条件行已补 |
| R3-004 | P3 | **ACCEPTED** | 折行/日志元数据未改；任务口径接受为非阻断 |

## 其他观察（不计 finding）

- 载体 §6 仍缺「处置 2」（编号 1/3/4/5 跳号）；r5 已登记为观察，建议 append-only 补回。
- FROZEN-C06 `:40`、FROZEN-C16 `:53` 仍是无表头孤立表行（措辞已对）；建议下次并入合法表格。
- 载体 `:58`（处置 4）称「FROZEN-C06 §2 补 v1.3 行」，实际由处置 5 完成；append-only 保留原句，属历史归因。
- 契约字节内承继「approved」：C-06 `:89` ⑥、C-16 `:244` ⑧（2 pins 内，r1–r5 已登记）；改之即破坏 pins，不新计。
- C-16 `:240` 仍写「C-06 修订按 v1.1 UNFREEZE 载体执行」（v1.3 已另立载体）；pin 内历史文本，不新计。

## Verdict

**`approved`**（P0=0 / P1=0 / P2=0 / P3=1，非阻断）。

- A/C/D/E 实测通过；B 仅矩阵两格记录文本未同步（R6-001，P3），不影响 2 pins、18/18、冻结状态与 pending 语义。
- DSH 后续（本报告不执行）：①载体 §6 append-only 追加 r6 approved（session/reviewed_head/P0=P1=0）；②FROZEN-C06 §2 第 7 行、FROZEN-C16 §2 第 8 行 → ✅，§7/§10 与 §1B 同步；③矩阵两格改 `r1–r5` 并修载体 `:60` 表述；④重算 carrier/EV sha，重跑 pins/check 并更新日志；⑤以上完成后方可提交/推送。
- r5 的 R5-001/R5-002 均 CLOSED；C-06 `75f8e2b4…`、C-16 `b8f46fb1…`、18/18 不变。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r6.md`；未改契约/冻结记录/矩阵/载体/卡/证据；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`；临时文件仅写入 `%TEMP%`。
- 所有 sha/blob/pin 为本机实测（工作树最终字节 + HEAD 原始 blob 复核）；pins/check 为现场重跑并按字节与日志比对，非引用记录；外部 session ID 不能从仓库字节核验。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock 测试（实现未释放）；r1–r5 报告内的历史测量未重跑（仅核对其结论与当前字节一致性）。
