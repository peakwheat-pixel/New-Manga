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
- **契约字节/pins 零回归**：C-06 `75f8e2b4…` / blob `b537e76d…`；C-16 `b8f46fb1…` / blob `f8f31f55…`；`verify_pins` **18/18**；其余 16 契约 `changed=0`；三锚未软化。
- **r5 findings**：R5-001 **CLOSED**、R5-002 **CLOSED**；承继 R4-001/R4-002 **CLOSED**、R3-004 **ACCEPTED**。
- **唯一待办（非阻断）**：DSH 在落 r6 approved 的同一次 append-only 提交中把矩阵两格改为 `r1–r5`（并修载体 `:60` 表述）后，方可提交/推送；不改契约字节。

## A. R5-001 关闭 — PASS

- ✅ FROZEN-C06 §2 `:52` 有 v1.3 第 7 条（「r6 pending（r1–r5 处置后）」），状态列 `⏳`，无 ✅。
- ✅ FROZEN-C06 §1B `:40` 与 FROZEN-C16 §1B `:53` 均为「r1–r5 处置后待 **r6** 收口」。
- ✅ 全文无「待 r4/r5 收口」现行残留；仅载体 `:59` 为 r5 报告的历史引文。

## B. 记录链 — FAIL（1 项 P3，非阻断）

- ✅ 载体 §6 `:52-60`（r1/处置 1/r2/r3/处置 3/r4/处置 4/r5/处置 5 → r6 pending）、FROZEN-C06 §7 `:93`、FROZEN-C16 §10 `:125`、EV `:3` 一致记录 `r1→r5 changes_requested → 处置 → r6 pending`。
- ✅ 载体两副本同字节（各 7730 B、sha256 `303165ab…`，`-ceq` True）；记录层无预填 approved（§2 ⏳、§7/§10/§1B/矩阵/EV pending）。
- ❌ 矩阵 `:24`/`:37` 仍「pending（**r1–r4** 处置后待 **r6** 收口）」——只改轮次未改范围，漏 r5；与本表其余五处不一致 → R6-001（P3，非阻断）。

## C. 契约字节 / pin 不回归 — PASS

- ✅ C-06 sha256 `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84` / blob `b537e76dad1e4075eb6ffd213e6c01954a256011`；C-16 `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` / blob `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211`。
- ✅ `verify_pins` 现场重跑 `PIN AUDIT: PASS (all 18)`（C06 `75f8e2b4eb80`、C16 `b8f46fb1feec`），与 `logs/pins.log` 逐字节相等；`other-16-pins.txt` 16/16 `UNCHANGED`、`changed=0`。
- ✅ `git diff --name-only HEAD` 仅 6 个 doc 文件；契约 diff 各 4 hunk，无新命令/能力/错误码/wire/TTL/schema/依赖。
- ✅ 三锚未软化：C-06 `:37` dispatch 前、`:40` ≤300 秒/不得长期通行证、`:43` 不延长 `expires_at`/不扩 scope/不撤销后重建/不改选/整请求 typed 拒绝零映射写入；C-16 `:78` 不延长任何 TTL/不改 scope/不绕过撤销。

## D. 证据 — PASS

- ✅ EV 逐文件 sha 7/7 实测同值：carrier `303165ab…`、changed-lines `9bacc8a0…`、check/check-taskpath `634e0723…`、pins `11bfd413…`、other-16 `431acd2a…`、pre-post `56d4670d…`。
- ✅ `carrier.md` 与载体同 sha/同字节；pre C-06 `99831a20…`、C-16 `a7f57ebd…`（HEAD blob `9bbd93a01…`/`67c741d3b…` 原始字节复算），post `75f8e2b4…`/`b8f46fb1…`。
- ✅ changed-lines 归一化与 `git diff HEAD -- C-06 C-16` 逐字节相等（10261 chars）；pins/check 日志重跑逐字节相等（408 B/427 B，同 sha，check = `PASS (3 warnings)`）。
- ⚠️ 承继卫生：pre-post post 值折行、logs 无命令/日期头（R3-004 ACCEPTED，不新计）。

## E. 不夸大 — PASS

- ✅ L-G1 只降级不关闭：载体 `:37` 独立句 + 6 项子限制（单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；卡 D-7。
- ✅ 契约就绪 ≠ 实现/产品可用：载体 `:37`；FROZEN-C06 `:63`、FROZEN-C16 `:59`/`:63` 不构成实现授权；卡 `:40` 只起草 + 复核 + 重冻；未宣称 Run wire/TTL/撤销/错误闭集/能力或产品 AC 达成。

## Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R6-001 | **P3** | 矩阵 `:24`/`:37`；载体 `:60` | 两处条件列仍「r1–r4 处置后待 r6 收口」，漏 r5，与 FROZEN-C06 `:40`/`:52`、FROZEN-C16 `:53`/`:51`、载体 §6、EV `:3` 的 r1–r5 不一致；r5 观察已要求「r6 前需修正」；载体「矩阵…统一」因此不实 | append-only 改「r1–r5 处置后待 r6 收口」（approved 后按同格式改 approved）；不动契约字节/pins |

## r5 findings 状态

- R5-001（P2）**CLOSED**：§2 第 7 条已补（⏳）；两处 §1B 均「待 r6 收口」；无旧轮次残留（仅 r5 历史引文）。
- R5-002（P3）**CLOSED**：§2 v1.3 行存在；载体对 §2/§1B 的「已补」陈述成立；「矩阵统一」不实另立 R6-001。
- 承继：R4-001/R4-002 **CLOSED**；R3-004 **ACCEPTED**（折行/日志元数据未改，非阻断）。

## 其他观察（不计 finding）

- 载体 §6 仍缺「处置 2」（编号 1/3/4/5 跳号，r5 已观察）；`处置 4` 声称补 §2 行实际由处置 5 完成；两条 §1B 行仍为无表头孤立行（措辞已对）——建议下次 append-only/排版修正。
- 契约字节内承继「approved」（C-06 `:89`⑥、C-16 `:244`⑧，在 2 pins 内，改之即破坏 pins）；C-16 `:240` 仍指 v1.1 载体（pin 内历史文本）——均只登记、不新计。

## Verdict

**`approved`**（P0=0 / P1=0 / P2=0 / P3=1，非阻断）。A/C/D/E 实测通过；B 仅矩阵两格记录文本未同步（R6-001），不影响 2 pins、18/18、冻结状态与 pending 语义。

- DSH 后续（本报告不执行）：①载体 §6 append-only 追加 r6 approved（session/reviewed_head/P0=P1=0）；②FROZEN-C06 §2 第 7 行、FROZEN-C16 §2 第 8 行 → ✅，§7/§10/§1B 同步；③矩阵两格改 `r1–r5` 并修载体 `:60` 表述；④重算 carrier/EV sha、重跑 pins/check 日志；⑤完成后方可提交/推送。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r6.md`；未改被审字节/证据/卡/冻结记录/矩阵/载体；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`；临时文件仅写入 `%TEMP%`。
- 所有 sha/blob/pin 为本机实测（工作树最终字节 + HEAD 原始 blob 复核）；pins/check 为现场重跑并逐字节比对；外部 session ID 不能从仓库字节核验。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock（实现未释放）；r1–r5 报告内的历史测量未重跑（仅核对其结论与当前字节一致性）。
