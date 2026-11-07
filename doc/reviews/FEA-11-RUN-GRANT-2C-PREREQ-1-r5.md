---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE r5 最终收口（记录/证据 delta；2 pins）
reviewer: DSH fresh subagent（独立上下文；session 8059c00b…；未参与本 UNFREEZE 起草/r1–r4；只读）
session: 8059c00b-b1e5-4468-a16c-6c06c32381f8
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_delta_r5
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立最终收口复审 r5（delta）

## 结论先行

- **verdict：`changes_requested`**（P0=0 / P1=0 / **P2=1** / **P3=1**）。
- **A PASS、C PASS、D PASS、E PASS；B FAIL**：主记录链（载体 §6、FROZEN-C06 §7、FROZEN-C16 §10、矩阵、EV）已统一为 `r1→r2→r3→r4 changes_requested → 处置 → r5 pending`，两副本同字节，无 approved 预填；但 **FROZEN-C06 §2 仍无 v1.3 条件行**（载体 `:58` 称已补），且 **两处 §1B 仍写「待 r4 收口」**。
- **契约字节/pins 无回归**：C-06 `75f8e2b4…` / blob `b537e76da…`；C-16 `b8f46fb1…` / blob `f8f31f55…`；`verify_pins` **18/18**；其余 16 契约 `changed=0`；三锚未软化；**R4-001 主链 CLOSED**（§1B 残留另立 R5-001，P2），**R4-002 OPEN**（R5-002，P3）。

## A. R4-001 关闭 — PASS

| 子项 | 结果 | 证据 |
|---|---|---|
| 载体 §6 统一链 | PASS | `:52-58`：r1 → 处置 1 → r2 → r3 → 处置 3 → r4 → 处置 4；`:58` 明写 `r1→r2→r3→r4 changes_requested → 处置 → r5 pending` |
| FROZEN-C06 §7 | PASS | `:92`「r1 changes_requested → r2 → r3 → r4 changes_requested → 处置 → **r5 pending**」 |
| FROZEN-C16 §10 | PASS | `:125`「r1→r2→r3→r4 changes_requested → 处置 → **r5 pending**」 |
| 矩阵 C-06/C-16 条件列 / EV | PASS | 矩阵 `:24`、`:37`「pending（r1–r4 处置后待 r5 收口）」；EV `:3`「r1→r4 changes_requested→处置→r5 pending」 |
| 载体两副本同字节 | PASS | 均 7475 B、sha256 `19e0cb01a1cdd6c855b1780ac7f8beaaaec44b48a2703fa6d959898cdb029ccb`；内容 `-ceq` True |
| 无 approved 预填（记录层） | PASS | 载体/EV/矩阵/FROZEN §7/§10 均 pending；FROZEN-C16 §2 条件 8 状态 `⏳` |

## B. R4-002 关闭 — FAIL

| 子项 | 结果 | 证据 |
|---|---|---|
| FROZEN-C06 §2 有 v1.3 第 6 条（⏳） | **FAIL** | `:44-51` 仅 6 行；第 6 行 `:51` 仍为 **v1.2 ✅**；无 v1.3 条件行、无 ⏳；载体 `:58`「FROZEN-C06 §2 补 v1.3 行」与字节不符 |
| FROZEN-C06 §1B/§7 自洽 | **FAIL** | §1B `:40` 仍「r1/r2 处置后待 **r4** 收口」，与 §7 `:92`「r5 pending」矛盾；该行还是无表头的孤立表行 |
| FROZEN-C16 §1B/§10 自洽 | **FAIL** | `:53` 仍「r1/r2 处置后待 **r4** 收口」，与 §10 `:125`「r5 pending」及 §2 `:51`「r5 pending」矛盾；该行位于 §2 表后，未并入 §1B 表 |

## C. 契约字节 / pin 不回归 — PASS

| 检查 | 结果 | 实测 |
|---|---|---|
| C-06 sha256 / blob | PASS | `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84` / `b537e76dad1e4075eb6ffd213e6c01954a256011` |
| C-16 sha256 / blob | PASS | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` / `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` |
| `verify_pins.ps1` | PASS | 重跑 `PIN AUDIT: PASS (all 18)`；C06 `75f8e2b4eb80`、C16 `b8f46fb1feec` |
| 其余 16 契约零字节 | PASS | `other-16-pins.txt` 16/16 `UNCHANGED`、`changed=0`；`git diff --name-only HEAD` 仅 6 个 doc 文件 |
| 三锚 / 改动面 | PASS | C-06 `:37` dispatch 前、`:40` ≤300 秒/不得长期通行证、`:43` 不延长 `expires_at`/不扩 scope/不撤销后重建/不改选/整请求 typed 拒绝零映射写入；C-16 `:19`、`:78` 不延长任何 TTL/不改 scope/不绕过撤销；C-06 4 hunk、C-16 4 hunk，无新命令/能力/错误码/wire/TTL/schema/依赖 |

## D. 证据 — PASS

| 对象 | 结果 | 实测 |
|---|---|---|
| EV 逐文件 sha 7/7 / carrier 副本 | PASS | carrier `19e0cb01…`（同 sha、同 7475 B）、changed-lines `9bacc8a0…`、check/check-taskpath `634e0723…`、pins `11bfd413…`、other-16 `431acd2a…`、pre-post `56d4670d…` 全部同值 |
| pre / post | PASS | pre C-06 `99831a20…`、C-16 `a7f57ebd…`（HEAD blob `9bbd93a01…`/`67c741d3b…` 复算同值）；post `75f8e2b4…`/`b8f46fb1…` |
| changed-lines 与真实 diff | PASS | 归一化 `equal_norm=True`；均 10337 chars；numstat C-06 6/4、C-16 5/4 |
| pins/check 日志可复现 | PASS | `pins.log` 408 B、sha `11bfd413…`；`check*.log` 各 427 B、sha `634e0723…`；按 CRLF 重跑逐字节相等；check = `PASS (3 warnings)` |
| 证据卫生（承继） | ACCEPTED P3 | `pre-post.sha256:2/4` post 值折行；`logs/*` 无命令/日期头（R3-004 已接受，不新计） |

## E. 不夸大 — PASS

| 检查 | 结果 | 证据 |
|---|---|---|
| L-G1 只降级不关闭 | PASS | 载体 `:37` 独立句 + 6 项子限制（单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；卡 D-7 |
| 契约就绪 ≠ 实现/产品可用 | PASS | 载体 `:37`；卡 `:40`「只起草 + 复核 + 重冻；不实现」；FROZEN-C06 §4、FROZEN-C16 §3/§4 不构成实现授权；未宣称 Run wire/TTL/撤销/错误闭集/能力变更或产品 AC 达成 |

## Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R5-001 | **P2** | FROZEN-C06 `:40`；FROZEN-C16 `:53` | R4-001 的 §1B 残留：两行仍写「r1/r2 处置后待 r4 收口」，与 §7/§10 的 r5 pending 矛盾；且均为无表头孤立行 | append-only 改为「r1–r4 处置后待 r5 收口」，并入合法表格；不动契约字节 |
| R5-002 | P3 | FROZEN-C06 `:44-51`；载体 `:58` | R4-002 未关闭：§2 仍无 v1.3 条件行/⏳；载体却称已补 | 补 v1.3 行（⏳，证据引用载体 §6）；修正载体 `:58` 措辞；不动契约字节 |

## r4 findings 状态

| ID | 级别 | 状态 | 说明 |
|---|---|---|---|
| R4-001 | P2 | **CLOSED（五项主链）** | 载体 §6、FROZEN-C06 §7、FROZEN-C16 §10、矩阵、EV 已一致；其 §1B 残留转 R5-001 |
| R4-002 | P3 | **OPEN** | FROZEN-C06 §2 仍无 v1.3 行；§1B 孤立行未并表；载体处置 4 的「已补」陈述不实 |
| R3-004 | P3 | **ACCEPTED** | 折行/日志元数据未改；任务明确可接受为非阻断 |

## 其他观察（不计 finding）

- 载体 §6 仍缺「处置 2」（仅 1/3/4/5，编号跳号），建议补回；另 18:54:12–14 外部更新（处置 5、r6 pending）不在本 r5 快照（18:45:54–56）内，矩阵 `:24/:37` 仍写 r1–r4 未同步 r5，r6 前需修正。
- 承继：C-06 `:89` ⑥、C-16 `:244` ⑧ 的冻结字节已写「approved」；属 2 pins，自 r1 存在，改之即破坏 pins；本轮仍只登记、不计 finding。

## Verdict

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / P3=1）。

- A/C/D/E 全部实测通过；B 因两处记录文本失败：R5-001（§1B 轮次残留，P2）与 R5-002（§2 条件行缺失，P3）。
- 修正只动 FROZEN-C06/FROZEN-C16/载体（+EV carrier hash），**不动 C-06/C-16 字节**；修正后 C-06 `75f8e2b4…`、C-16 `b8f46fb1…`、18/18 均不变，可做 r6 delta 收口。
- 在 R5-001/R5-002 落盘前**不得**预填 approved，也不得提交/推送本 UNFREEZE。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r5.md`；未改被审字节、证据、卡、冻结记录、矩阵、载体；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`。所有 sha/blob/pin 为本机实测（工作树最终字节 + HEAD 原始 blob 复核）；日志为现场按 CRLF 重跑比对，非引用记录；临时文件仅写入 `%TEMP%`。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock 测试（实现未释放）；外部会话 ID 不可从仓库字节核验；r1–r4 报告内的历史测量未重跑（仅核对其结论与当前字节的一致性）。
