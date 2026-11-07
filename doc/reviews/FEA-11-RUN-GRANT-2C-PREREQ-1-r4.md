---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE r4 delta 收口（记录/证据/载体一致性；2 pins）
reviewer: DSH fresh subagent（独立上下文；session a3fd5d05…；未参与本 UNFREEZE 起草/r1/r2/r3；只读）
session: a3fd5d05-f61a-4f6d-b34b-aa48b039c149
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_delta_r4
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立 delta 复核 r4（收口）

## 结论先行

- **verdict：`changes_requested`**（P0=0 / P1=0 / **P2=1** / P3=1）。
- **无 byte 级回归**：契约字节自 r3 未变（C-06 `75f8e2b4…`、C-16 `b8f46fb1…`），`verify_pins` **18/18**，其余 16 契约零字节，三锚未软化。
- **R3-001 CLOSED**：载体 §6 `:55` 已记 `0fb2bdaf…`→`75f8e2b4…` 迁移与 C-16 `b8f46fb1…` 不变；两副本同字节（`9d8469d8…`）。
- **R3-002 CLOSED**：矩阵 `:24/:37` 与 FROZEN-C16 `:51` 已改 pending/⏳，无完成式预填。
- **R3-003 PARTIAL**：§1B 两行已补，但 FROZEN-C06 §2 仍无 v1.3 条件行 → R4-002（P3）。
- **唯一阻断 R4-001（P2）**：载体 §6 仍以「**r3 pending**」收尾，未追加 r3 `changes_requested`／处置 3／r4 pending；FROZEN-C06 `:92`、FROZEN-C16 `:125` 同写 r3 pending，而 FROZEN-C16 `:51/:53` 与矩阵写「r4 pending（**r1/r2** 处置后）」跳过 r3 → 与 `EV.md:3` 的「r1→r3 changes_requested→处置→r4 pending」矛盾（与 R2-001 同类）。

## 0. 复核快照

| 项 | 实测值 |
|---|---|
| 仓库 / 分支 / HEAD | `G:\CODEX\New Manga` / `main` / `c1e19ed82dc89a0e42af5e27d9803434794586f1`（工作树：6 modified + 5 untracked 路径，含本报告后为 6） |
| 被审对象 | 工作树最终字节 + 载体/冻结记录/矩阵/EV/日志；HEAD 仅用于 pre 对照 |
| 实际执行 | `Get-FileHash`、字节级副本比较、`git hash-object/cat-file/diff/status`、`verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、EV 逐文件 hash、`changed-lines.diff` 归一化比对、16 项 pin 复核 |

## A. R3-001 关闭 — **PASS**

| 子项 | 结果 | 证据 |
|---|---|---|
| 载体 §6 记 C-06 `0fb2bdaf…`→`75f8e2b4…`、C-16 不变 | PASS | 载体 `:55`「C-06 经 R2-004/R2-005 处置后字节由 `0fb2bdaf…`→`75f8e2b4…`，C-16 保持 `b8f46fb1…` 不变」 |
| 两副本字节一致 | PASS | 均 6940 B，sha256 均 `9d8469d8cae7c9a672d4d6c5fa8db05d1ccb2ed17fcd9259b864d60098ef24b0` |
| 与 FROZEN-C06/FROZEN-C16/pre-post/pins.log 的 pin 无矛盾 | PASS | FROZEN-C06 `:16/:93`、FROZEN-C16 `:16/:126`、`pre-post.sha256:1-6`、`pins.log` C06/C16 行首 12 位全一致 |
| 说明 | — | 本节只核 pin 陈述；同一行 `:55` 的**轮次标签**失真见 R4-001 |

## B. R3-002/003 处置 — **FAIL（部分）**

| 子项 | 结果 | 证据 |
|---|---|---|
| 矩阵 C-06/C-16 条件列 pending（无预填 approved） | PASS | 矩阵 `:24`「v1.3 独立 byte-level 复核 pending（…待 r4 收口）」、`:37`「v1.6 … pending」 |
| FROZEN-C16 `:51` 条件 8 用 ⏳、无完成式 | PASS | 状态列 `⏳`；文本「r4 pending」 |
| FROZEN-C06 §1B 有 v1.3 复核字节行 | PASS | `:40` = `75f8e2b4…` |
| FROZEN-C06 §2 有 v1.3 条件行/⏳ | **FAIL** | `:42-51` 仅 6 条条件（`:44-51`）；第 6 条 `:51` = **v1.2 ✅**；无 v1.3 条、无 ⏳ → R4-002 |
| FROZEN-C16 §1B 有 v1.6 行 | PASS | `:53` = `b8f46fb1…` |
| FROZEN-C16 §1B/§2/§10 自洽 | **FAIL** | §10 `:125`「r3 pending」 vs §2 `:51`/§1B `:53`「r4 pending / 待 r4 收口」→ R4-001 |
| FROZEN-C06 §1B/§7 自洽 | **FAIL** | §1B `:40`「待 r4 收口」 vs §7 `:92`「r3 pending」→ R4-001 |

## C. 契约字节 / pin（不回归）— **PASS**

| 检查 | 结果 | 证据（实测） |
|---|---|---|
| C-06 sha256 / blob | PASS | `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84` / `b537e76dad1e4075eb6ffd213e6c01954a256011` |
| C-16 sha256 / blob | PASS | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` / `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` |
| `verify_pins.ps1` | PASS | 重跑输出与 `logs/pins.log` 逐字节一致；`PIN AUDIT: PASS (all 18)` |
| 其余 16 契约零字节 | PASS | `git diff --name-only HEAD` 仅 6 个 doc 文件；`other-16-pins.txt` `SUMMARY: 16 contracts, changed=0` |
| 改动面最小（无新命令/能力/错误码/wire/TTL/schema/依赖） | PASS | C-06 仅 4 hunk（头部/§2.2/§5/§6）、C-16 仅 4 hunk（头部/§2.4/§10/记录）；`PROTOCOL_MINOR=3`、C-16 §0 能力、§2 wire、错误闭集零 diff |
| 三锚与安全语义不软化 | PASS | C-06 `:37` dispatch 前、`:40` ≤300 秒/不得长期通行证、`:43` 追加句（不延长 `expires_at`/不扩 scope/不撤销后重建/不改选/整请求 typed 拒绝零映射写入）；C-16 `:19`、`:78`（不延长任何 TTL/不改 scope/不绕过撤销）、`:91` 保持 |

## D. 证据 — **PASS**

| 对象 | 结果 | 实测 |
|---|---|---|
| EV 逐文件 sha 7/7 | PASS | carrier `9d8469d8…`、changed-lines `9bacc8a0…`、check/check-taskpath `634e0723…`、pins `11bfd413…`、other-16 `431acd2a…`、pre-post `56d4670d…`，全部与 EV 记录同值 |
| pre / post | PASS | pre C-06 `99831a20…`、C-16 `a7f57ebd…`（HEAD blob `9bbd93a01…`/`67c741d3b…` 复算同值）；post `75f8e2b4…`/`b8f46fb1…` |
| changed-lines 与真实 diff | PASS | 归一化后 `equal_norm=True`（存档 CRLF/工作区 LF 差异，内容等同；仅 2 个 diff 头、8 hunk） |
| pins/check 日志可复现 | PASS | `pins.log`、`check.log`、`check-taskpath.log` 重跑逐字节一致；check = `PASS (3 warnings)` |
| 载体副本同 sha | PASS | 见 A 节 |
| 证据卫生 | ACCEPTED P3 | `pre-post.sha256:2-3/5-6` post 值仍折行；`logs/*` 仍无命令/日期/`reviewed_head` 头 → R3-004（任务明确可接受） |

## E. 冻结包 / 不夸大 — **FAIL（记录链）**

| 检查 | 结果 | 证据 |
|---|---|---|
| 记录链 r1→r2→r3 `changes_requested`→处置→r4 pending | **FAIL** | 载体 `:52-55` 止于「r3 pending」；FROZEN-C06 `:92`、FROZEN-C16 `:125` 同；无处置 3、无 r4 pending；与 `EV.md:3` 矛盾 → R4-001 |
| 无预填 approved（记录层） | PASS | 载体/EV/矩阵/FROZEN §7/§10 均 pending；FROZEN-C16 条件 8 `⏳` |
| L-G1 只降级不关闭 | PASS | 载体 `:37` 独立句 + 6 项子限制；卡 D-7 |
| 契约就绪 ≠ 实现/产品可用 | PASS | 载体 `:37`；卡 `:40`「只起草 + 复核 + 重冻；不实现」；FROZEN-C06 `:62`/FROZEN-C16 `:59`、`:63` 不构成实现授权 |
| 承继观察（不计 finding） | — | C-06 `:89` ⑥ 与 C-16 `:244` ⑧ 条款文本已写「approved」；属 2 pins 冻结字节（自 r1 起存在，r1–r3 未按预填计），改之即破坏 2 pins，本轮仅登记 |

## Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R4-001 | **P2** | 载体 `:55`；FROZEN-C06 `:40/:92`；FROZEN-C16 `:51/:53/:125`；矩阵 `:24/:37` | 记录链未随 r3 收口：载体仍「r3 pending」且无处置 3；FROZEN-C06 §7、FROZEN-C16 §10 同；FROZEN-C16 条件 8 写「r4 pending（r1/r2 处置后）」、§1B 与矩阵 `:24/:37` 写「待 r4 收口」，均跳过 r3 `changes_requested`（P2=1/P3=3）→ 与 `EV.md:3` 矛盾（同类 R2-001） | append-only：载体 §6 增「r3 changes_requested（P0=0/P1=0/P2=1/P3=3；session `37cfe645…`；reviewed_head `c1e19ed82`）→ 处置 3 → r4 pending」；FROZEN-C06 §7、FROZEN-C16 §10 同步，条件 8/§1B/矩阵补 r3 段；不动契约字节 → 2 pins/18/18 不变，仅重算载体/EV hash 并重跑 pins/check |
| R4-002 | P3 | FROZEN-C06 `:42-51`、`:40` | §2 无 v1.3 条件行/⏳（第 6 条仍 v1.2 ✅）；§1B 新增行为孤立表行（无表头分隔），R3-003 未全处置 | 补 v1.3 条件行（⏳，引用载体 §6）；§1B 行并入合法表格；不改契约字节 |

## r3 Findings 状态

| ID | 级别 | 状态 | 说明 |
|---|---|---|---|
| R3-001 | P2 | **CLOSED** | 载体 `:55` 已记 C-06 迁移与 C-16 不变，两副本同 sha，pin 无矛盾 |
| R3-002 | P3 | **CLOSED** | 矩阵 `:24/:37`、FROZEN-C16 `:51` 改为 pending/⏳ |
| R3-003 | P3 | **PARTIAL / OPEN** | §1B 已补；FROZEN-C06 §2 条件行仍缺 → R4-002 |
| R3-004 | P3 | **ACCEPTED** | 折行/日志元数据未改；任务明确可接受为非阻断 |

## Verdict

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / P3=1）。

- 契约字节、2 pins、18/18、16 项不变、pre/post、changed-lines、EV 7/7、安全语义全部实测成立，无 byte 级回归；R3-001/R3-002 已关闭，R3-004 接受。
- 唯一阻断为 **R4-001**：r3 的 `changes_requested` 与处置未进入载体/冻结记录链，且各记录对「当前轮次」自相矛盾（r3 pending vs r4 pending）。修正只动记录文本（载体两副本 + FROZEN-C06/C16 + 矩阵 + EV hash），**不动 C-06/C-16 字节**；修正后 C-06 `75f8e2b4…`、C-16 `b8f46fb1…`、18/18 均不变。
- 不预填 approved；FROZEN §7/§10 在 r5（或同轮确认）通过后按 append-only 落 approved 并补 R4-002。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r4.md`；未改被审字节、证据、卡、冻结记录、矩阵、载体；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`。
- 所有 sha/blob/pin 为本机实测（工作树最终字节 + HEAD 原始 blob 复核）；日志为现场重跑比对，非引用记录。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock 测试（实现未释放）；外部会话 ID（`857903ae-…`、`cbdf231a-…`、`37cfe645-…`）不可从仓库字节核验；r1–r3 报告内的历史测量未重跑（仅核对其结论与当前字节的一致性）。
