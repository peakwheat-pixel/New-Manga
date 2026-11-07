---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE 独立 byte-level 复核 r2（mid-run 重复建立；2 pins）
reviewer: DSH fresh subagent（独立上下文；未参与本 UNFREEZE 起草/r1 复核；只读被审字节）
session: 1e70991e-b727-4c73-bc71-3a4a5e030c60
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_byte_level
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立 byte-level 复核 r2

## 结论先行

- **verdict：`changes_requested`**（P0=0 / P1=0 / **P2=1** / P3=5）。
- **安全语义再次实测成立**：C-06 §2.2 `:43` 与 C-16 §2.4 `:78` 追加句覆盖全部要求子句；`dispatch 前/≤300s/不得长期通行证` 三锚原文未改；契约 diff 无新命令/能力/错误码/wire/TTL/schema/依赖；C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约零字节。
- **r1 的 4 项 P2 实质闭合**：FROZEN-C16 §2 行 7/8 已恢复 4 列与正确证据；`other-16-pins.txt` 已存在且 `changed=0`；卡 I-2/AC-T1 已登记「§5 ⑥ + §6 变更记录」；AC-T2 已改为语义等价。
- **唯一阻断项（P2）**：载体 §6 `:52` 仍写 `r1：pending`，未落 r1 `changes_requested`、处置与 r2 状态；与 `EV.md:3`、r1 报告矛盾（同类缺陷在 V15 轮 r2 被判 P2）。
- **实测 pin 全部正确且可复算**：C-06 `sha256=0fb2bdaf…`、blob `c5b0861b…`；C-16 `sha256=b8f46fb1…`、blob `f8f31f55…`；`verify_pins` **18/18 PASS**；`check.ps1` 两种模式均 PASS（3 warnings）。

## 0. 复核快照与方法

| 项 | 实测值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| HEAD | `c1e19ed82dc89a0e42af5e27d9803434794586f1` |
| 工作树 | 6 modified（C-06/C-16/FROZEN×2/矩阵/卡）+ 3 untracked（载体、r1/r2 报告、证据目录）；本报告为本次唯一写入 |
| 事实来源 | 工作树**最终字节**；历史对比用 `HEAD` |
| 实际执行 | `Get-FileHash`、`git hash-object/cat-file/diff/status`、`verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、EV 逐文件 hash、`other-16-pins` 独立抽查 5 项、`changed-lines.diff` 归一化比对 |

## A. r1 P2 关闭 — **PASS（3/4）；矩阵子项 FAIL**

| 子项 | 结果 | 证据 |
|---|---|---|
| FROZEN-C16 §2 行 7 含 `P0=0/P1=0/P2=0/P3=0` 与证据列 | PASS | `FROZEN-C16:50` 4 列；证据=载体 V15 §6 + `verification/FEA-11-L-S4-B-PREREQ-1/logs/pins.log` |
| 行 8 仅 4 列且证据=RUN-RENEWAL 载体 | PASS | `FROZEN-C16:51` 4 列；证据=`CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL.md` §6 |
| `other-16-pins.txt` 存在且 SUMMARY changed=0 | PASS | 文件 16 行 + `SUMMARY: 16 contracts, changed=0`；独立抽查 C05/C07/C15/C17/FEA01 实算值逐项等于记录 |
| 卡 I-2/AC-T1 含 C-06 §5 ⑥ + §6 变更记录 | PASS（字面） | 卡 `:67`「§5 追加条件 ⑥ + §6 变更记录」；`:88`「§5 条件 ⑥ + §6 变更记录 + 头部」 |
| 矩阵 C-06/C-16 行无 v1.2 r3/v1.5 过时引用 | **FAIL** | C-16 `:37` 已更新为 v1.6；**C-06 `:24` 仍「①独立 byte-level 复核 r3 approved（P0=0/P1=0；载体）…④wire v1.2 additive DSH 批准 ✅」**，r3 属 v1.2，v1.3 当前仅 r1 changes_requested/r2 pending → R2-002 |

## B. r1 P3 关闭 — **PASS（含 1 项措辞 P3）**

| 子项 | 结果 | 证据 |
|---|---|---|
| 载体含「首次建立仍须在 Run dispatch 前；重复建立只对其后读取/提交生效」 | PASS | 载体 `:34` 独立句「首次建立仍须在 Run **dispatch 前**…且只对其后读取/提交生效」 |
| 载体含「契约就绪 ≠ 实现/产品可用」「L-G1 只降级不关闭」 | PASS | 载体 `:37` 两个独立句，并列 L-G1 子限制 |
| AC-T2 已为语义等价 | PASS | 卡 `:89`「逐句语义等价（且更严）」 |
| C-06 §7 历史 pin 完整 sha | PASS | `C-06:92` 三个 64-hex 实值（v1.2/v1.1/v1.0），无「…」 |
| §5 ⑥ 不重复编号 | PASS（字面） | `C-06:88` 为条件 5 内「**v1.3**：…」，无重复 `⑥`/`6.`；但全文件无独立 `⑥` 标记 → R2-004 |

## C. 契约安全语义 — **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| C-06 追加句覆盖全子句 | PASS | `:43`「每次必须**重新铸造新 grant**（各自 ≤300s、按当时 facts 顺序重新核验）；**不得**延长既有 grant 的 `expires_at`、不得扩大 scope、不得在撤销后重建、不得改选 command/scope；任一页不可授权仍**整请求 typed 拒绝、零映射写入**」 |
| C-16 追加句覆盖全子句 | PASS | `:78`「每次只绑定当次 live grants；**不延长任何 TTL**、不改 scope、不绕过撤销；任一页不可授权仍整请求 typed 拒绝、**零映射写入**」 |
| 三锚未软化 | PASS | C-06 `:37/:43/:56`「dispatch 前」、`:40`「≤300 秒」/`:43`「≤300s」、`:40`「**不得**作为长期通行证复用」原文未改；C-16 `:19/:22/:78` 同 |
| 无新命令/能力/错误码/wire/TTL/schema/依赖 | PASS | 两份 diff 仅 4 hunk；C-16 §0 能力、§2 wire、§6 闭集、`PROTOCOL_MINOR=3` 零 diff；C-06 grant 形状/§3 零 diff |
| C-05/C-15/C-17/C-07/M2-C1 及其余 16 契约零字节 | PASS | `git diff --name-only HEAD` 仅 5 个 plan 文件 + 卡；`doc/contracts` 无变更；`other-16-pins` 16/16 不变 |

> 观察（非缺陷）：C-06 `:43` 的「零业务写」与「**v1.3 追加**」之间缺分隔符，渲染为「零业务写v1.3 追加」→ R2-005。

## D. pin/证据 — **PASS**

| 对象 | 期望 | 实测 | 判定 |
|---|---|---|---|
| C-06 sha256 | `0fb2bdaff52bf7836d13cdc88229ee1dd02cd530a9161f7549d123781230fa91` | 同值（工作树 + blob 内容） | ✅ |
| C-06 `git hash-object` | `c5b0861bde610b051d90af0d490a69db45995bda` | 同值 | ✅ |
| C-16 sha256 | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` | 同值 | ✅ |
| C-16 `git hash-object` | `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` | 同值 | ✅ |
| pre（HEAD 原始 blob） | C-06 `99831a20…` / C-16 `a7f57ebd…` | 逐字节复算同值 | ✅ |
| `verify_pins.ps1` | 18/18 | 重跑 `PIN AUDIT: PASS (all 18)`；`C06 0fb2bdaff52b`、`C16 b8f46fb1feec` | ✅ |
| 其余 16 契约 | changed=0 | `SUMMARY changed=0`；独立抽查 C05 `f6e6f3cb…`、C07 `3fdb44e4…`、C15 `f9e376a0…`、C17 `aefa0fa5…`、FEA01 `0370c189…` 与记录一致 | ✅ |
| `changed-lines.diff` | = `git diff HEAD -- C-06 C-16` | `equal_norm=True`，均 10330 chars | ✅ |
| EV 逐文件 sha | 7/7 | carrier/changed-lines/2×check/pins/other-16/pre-post 全部同值；`carrier.md` 与 `doc/reviews/…RUN-RENEWAL.md` 字节相同 | ✅ |
| pins/check 日志可复现 | 输出逐行一致 | `pins.log` = 重跑输出；`check*.log` = `Governance check: PASS (3 warnings)` | ✅ |

## E. 冻结包/不夸大 — **FAIL（记录链）**

| 检查 | 结果 | 证据 |
|---|---|---|
| 记录链 r1 changes_requested → 处置 → r2 pending | **FAIL** | 载体 §6 `:52` 仍 `r1：pending`；未落 r1 计数/处置/r2 状态。仅 `EV.md:3` 记录了正确链（「r1 changes_requested→处置→r2 pending」）。FROZEN-C06 §7 `:90`、FROZEN-C16 §10 `:123` 均引「载体 §6」为证据 → R2-001 |
| 无预填 approved（FROZEN/载体） | PASS（FROZEN）/ FAIL（矩阵） | FROZEN-C06 `:90`、FROZEN-C16 `:123` 均 `pending`；载体无 approved。但矩阵 C-06 `:24` 把 r3 approved 挂在 v1.3 行 → R2-002 |
| L-G1 只降级不关闭 | PASS | 载体 `:37` 明写，并保留 6 项子限制 |

## Findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| R2-001 | **P2** | 载体 `:52` | §6 仍写 `r1：pending`；未记 r1 `changes_requested`（P0=0/P1=0/P2=4/P3=8）与处置，也无 r2 状态；与 `EV:3` 及 r1 报告矛盾，FROZEN 两处又以其为复核证据 | 载体 `:52`；`EV:3`；r1 报告 verdict 行 | 按 append-only 追加：r1 `changes_requested`（计数）+ 处置要点 + r2 `changes_requested`（P0=0/P1=0/P2=1/P3=5）→ 下一轮待复核；FROZEN §7/§10 复核栏同步 |
| R2-002 | P3 | 矩阵 `:24` | C-06 v1.3 行的条件 ① 仍为「r3 approved」、④「wire v1.2 additive」；r3 属 v1.2，等于把旧核准挂到当前版本，r1 R1-007 仅修了 C-16 半边 | 矩阵 `:24` vs `:37`；r1 R1-007 | 条件 ① 改「v1.3 独立 byte-level 复核 pending（载体 §6）」；④ 保留历史或注明 v1.2 阶段 |
| R2-003 | P3 | `FROZEN-C16:50` | 行 7 恢复时删去历史括注「（C16 新值、其余 **17** 项不变）」；与 HEAD 非逐字一致，属历史行静默编辑的残余 | `git diff HEAD` 该行 | 逐字恢复括注 |
| R2-004 | P3 | 载体 `:18`；卡 `:67/:88` | 记录称「§5 条件 ⑥」，但 C-06 §5 只有 5 个编号项，v1.3 条件是第 5 项内的「**v1.3**：」句；AC-T1 的 ⑥ 无字节锚点 | C-06 `:88`（无 `⑥`） | 卡/载体改「§5 条件 5 追加 v1.3 句」；或 approved 时在 §5 显式加 ⑥（会改字节/重算 pin） |
| R2-005 | P3 | C-06 `:43` | 「零业务写」与「**v1.3 追加（mid-run 重复建立）**」之间缺分隔符，渲染粘连 | 该行原始字节 | 加「；」或「。」（改字节须重算 2 pins） |
| R2-006 | P3 | `pre-post.sha256:2-3/5-6`；`logs/*` | post 值仍折行；日志仍无命令/日期/`reviewed_head` 头（r1 R1-010 未处置） | 文件字节 | 一行一 hash；日志补命令、日期、head |

## r1 Findings 状态

| ID | 级别 | 状态 | 说明 |
|---|---|---|---|
| R1-001 | P2 | **CLOSED** | 行 7 恢复严重度+证据；行 8 回 4 列并改挂 RUN-RENEWAL 证据（残余 R2-003） |
| R1-002 | P2 | **CLOSED** | 历史行的严重度/证据已恢复；仅剩 R2-003 括注 |
| R1-003 | P2 | **CLOSED** | `other-16-pins.txt` 存在，16 行 + `changed=0`，5 项独立复算一致 |
| R1-004 | P2 | **CLOSED** | 卡 `:67`/`:88` 已含 §5 ⑥ + §6 记录（残余措辞 R2-004） |
| R1-005 | P3 | **CLOSED** | 载体 `:34` 独立解释句 |
| R1-006 | P3 | **CLOSED** | AC-T2 `:89` 已改语义等价（且更严） |
| R1-007 | P3 | **OPEN** | C-16 行已修；C-06 `:24` 未修 → R2-002 |
| R1-008 | P3 | **PARTIAL / ACCEPTED** | C-06 §7 历史 pin 已写实值；§1B/§2 的 v1.3/v1.6 复核行仍待 approved 后补齐（r1 原意，pending 期可接受） |
| R1-009 | P3 | **CLOSED** | §5 不再有重复「6.」编号；但无独立 ⑥（R2-004） |
| R1-010 | P3 | **OPEN** | pre-post 折行 + 日志元数据 → R2-006 |
| R1-011 | P3 | **CLOSED** | 载体 `:37` 两个独立句 |
| R1-012 | P3 | **ACCEPTED** | 载体 `:32`「mint 内部重走 `Registry.Authorize`+facts（撤销/漂移/根替换自动 typed 停止）」已消解字面张力；额外解释句非必需 |

## Verdict

**`changes_requested`**（P0=0 / P1=0 / P2=1 / P3=5）。

- 安全实质与 2 pins 均成立；C-06 字节自 r1 后有变化（`8cb153d5…`→`0fb2bdaf…`），可见差异集中在 §5 条件文本，已由本报告按最终字节覆盖。
- 阻断仅 R2-001（载体 §6 记录链）；R2-002…006 为非阻断 P3，可与 R2-001 同批修。
- 修复不涉及契约条款字节时，C-06/C-16 两 pin 与 18/18 不变；若采纳 R2-004/005 的契约措辞改动，则须重算 2 pins 并再做 delta 复核。

## 真实性声明与 NOT_RUN

- 本次**唯一写入** `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r2.md`；未改被审字节、证据、卡、冻结记录、矩阵、载体；未 `git add/commit/push`；未改 `src/**`、`apps/**`、`tests/**`。
- 所有 sha/blob/pin 均为本机实测（工作树最终字节 + HEAD 原始 blob 复算），非引用记录。
- **NOT_RUN**：pytest/.NET 全量基线（纯文档变更，`src/**` 零 diff）；`tools/generate_api_inventory.py --check`（未涉 API 面）；gated IPC/fake-clock 测试（实现面未释放）；ZCode/Codex 外部会话 ID 的可核验性（无法从仓库字节核验）。
