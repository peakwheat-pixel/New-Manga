---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE 独立 byte-level 复核 r3（byte-level 收口；2 pins）
reviewer: DSH fresh subagent（独立上下文；未参与本 UNFREEZE 起草/r1/r2 复核；只读被审字节）
session: 37cfe645-fe79-4579-a116-55a76e3dce7f
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_byte_level
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立 byte-level 复核 r3（收口）

## 结论先行

- **verdict：`changes_requested`**（P0=0 / P1=0 / **P2=1** / P3=3）。
- **安全实质、最终 pin 与证据均成立**：C-06 §2.2 `:43`、C-16 §2.4 `:78` 追加句覆盖全部要求子句；三锚原文未改；契约 diff 无新命令/能力/错误码/wire/TTL/schema/依赖；C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约零字节。
- **实测 pin**：C-06 `sha256=75f8e2b4…`、blob `b537e76da…`；C-16 `sha256=b8f46fb1…`、blob `f8f31f55…`；`verify_pins` **18/18 PASS**；`other-16 changed=0`；pre/post 与 `changed-lines.diff` 可复算一致。
- **唯一阻断（P2）**：载体 §6 `:55` 的「处置 2」仍称 C-06/C-16 字节保持 `0fb2bdaf…`/`b8f46fb1…` 不变；最终 C-06 实为 `75f8e2b4…`（R2-004/005 采纳后字节已变），直接矛盾于 FROZEN-C06 `:16/:91`、`pre-post.sha256:3`、`pins.log` 及载体自己的 `:26`，且未登记 `0fb2bdaf…→75f8e2b4…` 的 pin 迁移 → **R3-001**。
- r1 的阻断项已实质闭合；r2 除 R2-001 外均已关闭或按 P3 接受。

## 0. 复核快照

| 项 | 实测值 |
|---|---|
| 仓库 / 分支 / HEAD | `G:\CODEX\New Manga` / `main` / `c1e19ed82dc89a0e42af5e27d9803434794586f1` |
| 工作树 | 6 modified（C-06/C-16/FROZEN×2/矩阵/卡）+ 4 untracked 路径（载体、r1/r2、证据目录；不含本报告，写入后为 5） |
| 事实来源 | 工作树**最终字节**；HEAD 仅用于 pre 对比；未改被审字节/证据/卡/冻结记录 |
| 实际执行 | `Get-FileHash`、`git hash-object/cat-file/diff/status`、`verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、EV 逐文件 hash、`changed-lines.diff` 归一化比对、16 项 pin 复核 |

## A. r2 P2 关闭 — **FAIL（P2）**

| 子项 | 结果 | 证据 |
|---|---|---|
| 载体 §6 记 r1 `changes_requested`（P0=0/P1=0/P2=4/P3=8）与处置 1 | PASS | 载体 `:52` |
| 载体 §6 记 r2 `changes_requested`（P0=0/P1=0/P2=1/P3=5）与处置 2 | PASS | 载体 `:54` |
| 载体 §6 记 r3 pending | PASS | 载体 `:55` |
| 与 FROZEN-C06 §7 / FROZEN-C16 §10 / EV 的链一致 | PASS | FROZEN-C06 `:90`「r1（P2×4）→ 处置 → r2（P2×1）→ 处置 → **r3 pending**」；FROZEN-C16 `:123` 同链；EV `:3` |
| 载体 §6 的 pin 陈述与最终字节一致 | **FAIL** | 载体 `:55` 称 C-06/C-16 保持 `0fb2bdaf…`/`b8f46fb1…` 不变；实测 C-06 `75f8e2b4…`（FROZEN-C06 `:16/:91`、`pre-post.sha256:3`、`pins.log`、载体 `:26` 已写 `75f8e2b4…`）；C-16 确为 `b8f46fb1…`；未记 `0fb2bdaf…→75f8e2b4…` 迁移 → R3-001 |
| 矩阵 C-06 行 v1.3 独立复核（载体 RUN-RENEWAL）、依赖 C-16 v1.6、无旧 r3/wire v1.2 残留 | PASS | 矩阵 `:24`：①v1.3 独立 byte-level 复核（载体 `CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL`）②C-01b ✅ ③Gate 不阻塞 ④C-16 v1.6 同批 ⑤18/18；依赖列 `C-01b/C-16 v1.6`；矩阵 `:37` C-16 行同步 v1.6 |
| 矩阵条件 ① 的 approved 措辞 | P3 观察 | 矩阵 `:24/:37` 与 FROZEN-C16 `:51` 以完成式写「approved」，而 r3 仍 pending；状态列/FROZEN §7/§10 均为 pending → R3-002（非状态级预填） |

## B. r2 P3 处置 — **PASS**

| 子项 | 结果 | 证据 |
|---|---|---|
| FROZEN-C16 行 7 恢复「（C16 新值、其余 **17** 项不变）」 | PASS | FROZEN-C16 `:50` |
| C-06 §5 有独立第 6 条（⑥） | PASS | C-06 `:89`「6. **v1.3**：…」；`5.` 与 `6.` 已分行 |
| C-06 `:43` 分隔符已修 | PASS | C-06 `:43`「零业务写。**v1.3 追加（mid-run 重复建立）**」 |
| §5 无重复编号 | PASS | C-06 `:84-89` 连续 1–6，无重复 `⑥`/`6.` |
| 证据折行 / 日志元数据 | ACCEPTED P3 | `pre-post.sha256:2-3/5-6` post 值仍折行；`logs/*` 仍无命令/日期/`reviewed_head` → R3-004（任务明确可接受为 P3） |
| FROZEN-C06 §7 历史 pin 实值完整 | PASS | FROZEN-C06 `:92` 三个 64-hex 实值，无「…」 |

## C. 契约安全语义（最终字节）— **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| C-06 追加句覆盖「每次新铸新 grant、各自 ≤300s、顺序重验 facts；不延长既有 `expires_at`、不扩 scope、不撤销后重建、不改选 command/scope；任一页不可授权整请求 typed 拒绝零映射写入」 | PASS | C-06 `:43` 末段逐项命中 |
| C-16 追加句覆盖「每次只绑定当次 live grants；不延长任何 TTL、不改 scope、不绕过撤销；任一页不可授权整请求 typed 拒绝零映射写入」 | PASS | C-16 `:78` 末段逐项命中；`:90-91` 既有 per-page facts/原子性未改 |
| 三锚未软化 | PASS | C-06 `:37`「dispatch 前」、`:40`「≤300 秒」「**不得**作为长期通行证复用」、`:43`「各自 ≤300s」；C-16 `:19`「dispatch 前」、`:78`「≤300s TTL」「不延长任何 TTL」、`:91`「不延长 TTL」均保持 |
| 无新命令/能力/错误码/wire/TTL/schema/依赖 | PASS | C-06 仅 4 hunk（头部/§2.2/§5/§6）；C-16 仅 4 hunk（头部/§2.4/§10/记录）；C-16 §0 能力、§2 wire、§6 错误闭集、`PROTOCOL_MINOR=3` 零 diff；C-06 grant 形状/§3 零 diff |
| C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约零字节 | PASS | `git diff --name-only HEAD` 仅 6 个 plan/task 文件；`doc/contracts` 无变更；`other-16-pins.txt` 16/16 `changed=0` |

**安全结论**：续期 = 新 grant + 新一次建立；不延 TTL、不扩 scope、不绕撤销、失败闭集不放松；未发现「长期通行证/自动恢复入口/自动重新授权」语义。

## D. pin/证据（最终字节）— **PASS**

| 对象 | 记录/期望 | 实测 | 判定 |
|---|---|---|---|
| C-06 sha256 | `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84` | 同值（工作树 + blob 内容） | ✅ |
| C-06 `git hash-object` | `b537e76dad1e4075eb6ffd213e6c01954a256011` | 同值 | ✅ |
| C-16 sha256 | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` | 同值 | ✅ |
| C-16 `git hash-object` | `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` | 同值 | ✅ |
| pre（HEAD 原始 blob） | C-06 `99831a20…`；C-16 `a7f57ebd…` | HEAD blob `9bbd93a01…` / `67c741d3b…` 原始字节复算同值 | ✅ |
| `verify_pins.ps1` | 18/18 | 重跑 `PIN AUDIT: PASS (all 18)`；C06 `75f8e2b4eb80`、C16 `b8f46fb1feec` | ✅ |
| 其余 16 契约 | changed=0 | `SUMMARY: 16 contracts, changed=0`；`git diff` 无这 16 份 | ✅ |
| `changed-lines.diff` | = `git diff HEAD -- C-06 C-16` | `equal_norm=True`，10337 chars；numstat C-06 6/4、C-16 5/4 | ✅ |
| EV 逐文件 sha | 7/7 | carrier `a2d81b7b…`、changed-lines `9bacc8a0…`、check/check-taskpath `634e0723…`、pins `11bfd413…`、other-16 `431acd2a…`、pre-post `56d4670d…` 全部同值 | ✅ |
| pins/check 日志可复现 | 输出逐行一致 | `pins.log` = 重跑输出；`check*.log` = `Governance check: PASS (3 warnings)`（默认 + `-TaskPath`） | ✅ |

## E. 冻结包/不夸大 — **PASS（含 P3 观察）**

| 检查 | 结果 | 证据 |
|---|---|---|
| 记录链 r1→r2→r3 pending | PASS | FROZEN-C06 `:90`、FROZEN-C16 `:123`、载体 `:52-55`、EV `:3`；r3 行均为 pending |
| 无状态/verdict 级预填 approved | PASS | FROZEN §7/§10、载体 §6、EV 均 pending；FROZEN-C16 条件 8 状态列 `⏳`；矩阵条件列为判据陈述（措辞见 R3-002） |
| L-G1 只降级不关闭 | PASS | 载体 `:37` 独立句 + 6 项子限制（单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）；卡 D-7 同 |
| 契约就绪 ≠ 实现/产品可用 | PASS | 载体 `:37` 独立句；卡 `:40`「只起草 + 独立 byte-level 复核 + 重冻；不实现」；FROZEN-C06 `:60`/FROZEN-C16 `:57`「不构成实现授权」 |
| v1.3/v1.6 复核字节行/条件行补齐 | P3 观察 | FROZEN-C06 §1B/§2 无 v1.3 复核字节/条件行；FROZEN-C16 §1B 无 v1.6 行（R1-008 遗留；pending 期可接受）→ R3-003 |

## Findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| R3-001 | **P2** | 载体 `:55` | 处置 2 称「C-06/C-16 字节保持 `0fb2bdaf…`/`b8f46fb1…` 不变」；最终 C-06 为 `75f8e2b4…`（R2-004/005 采纳后字节已变），未登记 `0fb2bdaf…→75f8e2b4…` 迁移；与 FROZEN-C06 `:16/:91`、`pre-post:3`、`pins.log`、载体 `:26` 矛盾 | 载体 `:55` vs `:26`；FROZEN-C06 `:16/:91`；实算 | 按 append-only 把 `:55` 改为「C-06 `0fb2bdaf…→75f8e2b4…`（R2-004/005 采纳）；C-16 `b8f46fb1…` 不变」；不改契约字节则 2 pins/18/18 不变，仅需重算载体/EV hash 并重跑 pins/check |
| R3-002 | P3 | 矩阵 `:24/:37`；FROZEN-C16 `:51` | 条件列以完成式写「v1.3/v1.6 … approved」，与 r3 pending 并存，易读作已批准 | 矩阵条件 ①；FROZEN-C16 条件 8 状态 `⏳` | 建议改「须经独立 byte-level 复核 approved」或在 r3 通过后再定稿；非阻断 |
| R3-003 | P3 | FROZEN-C06 §1B/§2；FROZEN-C16 §1B | 缺 v1.3/v1.6 的复核字节行 / §2 条件行（R1-008 遗留） | FROZEN-C06 `:22-49`；FROZEN-C16 `:27-38` | pending 期可接受；approved 时补 v1.3/v1.6 行（不改条款字节） |
| R3-004 | P3 | `pre-post.sha256:2-3/5-6`；`logs/*` | post 值折行；日志无命令/日期/`reviewed_head` 头（R2-006 遗留） | 文件字节 | 一行一 hash；日志补元数据；非阻断 |

## r2 Findings 状态

| ID | 级别 | 状态 | 说明 |
|---|---|---|---|
| R2-001 | P2 | **PARTIAL / OPEN** | 链与计数已补；但 `:55` pin 陈述错误 → R3-001 |
| R2-002 | P3 | **CLOSED** | 矩阵 C-06/C-16 行版本、依赖、旧 r3/wire v1.2 引用已修；残留措辞 R3-002 |
| R2-003 | P3 | **CLOSED** | FROZEN-C16 `:50` 已恢复「（C16 新值、其余 **17** 项不变）」 |
| R2-004 | P3 | **CLOSED** | C-06 `:89` 已有独立第 6 条 |
| R2-005 | P3 | **CLOSED** | C-06 `:43` 已加「。」分隔；字节随之变化，pin 已更新为 `75f8e2b4…`（载体陈述见 R3-001） |
| R2-006 | P3 | **ACCEPTED** | 折行/日志元数据未改；任务明确可接受为 P3 |

## Verdict

**`changes_requested`**（P0=0 / P1=0 / P2=1 / P3=3）。

- 安全语义、三锚、2 pins、18/18、16 项不变、pre/post、changed-lines、EV 7/7 全部实测成立；r1 四项 P2 实质闭合，r2 的 R2-002…006 已关闭或接受。
- **唯一阻断**为 R3-001：载体 §6 `:55` 的最终 pin 陈述错误且漏记 R2-004/005 导致的 C-06 字节迁移。修正只动载体两副本 `doc/reviews/…RUN-RENEWAL.md` 与 `verification/…/carrier.md`（及 EV 中 carrier hash），**不需要改 C-06/C-16 字节**；修正后 C-06 `75f8e2b4…`、C-16 `b8f46fb1…`、18/18 均不变，可只做 r4/delta 复核。
- 若在 r4 前再次改契约字节，则必须重算 2 pins 并重跑本报告 D 节全部证据；不得沿用本次 pin。
- 不预填 approved；FROZEN §7/§10 在 r4 通过后按 append-only 落 approved。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r3.md`；未改被审字节、证据、卡、冻结记录、矩阵、载体；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`。
- 所有 sha/blob/pin 均为本机实测（工作树最终字节 + HEAD 原始 blob 复算），非引用记录；报告写入后仅新增本文件为 untracked。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock 测试（实现面未释放）；外部会话 ID（`cbdf231a-…`、`857903ae-…` 等）无法从仓库字节核验。
