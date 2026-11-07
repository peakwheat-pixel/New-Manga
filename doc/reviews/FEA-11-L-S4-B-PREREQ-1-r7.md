---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r7 最终文档/记录一致性复审（C-16 字节保持 a7f57ebd…）
reviewer: fresh subagent（r7；独立上下文；未参与本 UNFREEZE 起草、r1–r6 复核或任何相关实现；只读）
session: 3fd301c2-68b7-480e-b0df-9dff4483db95
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立文档/记录一致性复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r6 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r7 最终文档/记录一致性复审

> **结论先行：`changes_requested`，P0=0 / P1=0 / P2=1 / P3=2。**
>
> **r6 的 P2 已关闭**：`carrier §6`（`carrier:59-65`）已补 r5、r6 两轮 `changes_requested`（含 P0/P1/P2/P3 计数）与处置摘要，末行已写 **r7 pending**；`doc/reviews` 副本与 `verification/**/carrier.md` 同字节；`EV:3` 已写「r1→…→r6 changes_requested → r7 pending」。
>
> **新 P2（本轮决定 verdict）**：`FROZEN §1B:38` 与 `FROZEN §9:110` 仍停在「…→ r5 changes_requested → 处置 → **r6 pending**」，**没有 r6 changes_requested、没有 r7 pending**。FROZEN 是条件 7 的冻结记录，carrier/EV 已推进到 r7 而 FROZEN 没有，同一冻结包内三份记录互相矛盾。这是文本/记录问题，**不要求改 C-16 字节**。
>
> **r6 的 R3-09 已关闭**：`carrier:41`（§3 安全与兼容）已写「**契约就绪 ≠ 实现/产品可用**」正文句；`carrier:20` 保留「单根探测异常 → false」。**R3-04 仍部分 OPEN**：`carrier §2.E`（`carrier:33-36`）仍未登记 `FROZEN §1B` v1.4 历史行改写（删除 r1 计数/session/head、改为摘要；原信息见 §8）；`carrier:60` 的「保留并加注（不改写其历史值）」较 r5 已改善，但仍未明确「已改写为摘要」。
>
> **C-16 字节/安全不回归**：sha256=`a7f57ebdbd67…`（38912 B，LF 253 行，0 CRLF）= FROZEN pin = blob 内容 sha；`git hash-object`=`67c741d3…`；两列/零写/幂等/单调/错误闭集/红线均未回退；C-15/C-17/C-06/C-07/M2-C1 零字节；`verify_pins` **18/18**；日志重跑逐字节复现；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字相等；EV 7 项 sha 全匹配。
>
> **C-16 §10 ⑦ 的「independent byte-level 复核 approved」仍未满足；当前冻结包不能按 r7 approved 提交/推送。**

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪载体、r1–r6、证据目录 8 文件；**本报告写入后新增 r7 报告 1 个未跟踪项**，其余不变 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff；C-15/C-17/C-06/C-07/M2-C1 亦零 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`；重跑输出按 CRLF 与 `logs/pins.log` **逐字节一致**（408 B，sha `07c2b60c…`） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B，sha `d1e251bc…`） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判文档/记录与契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF（与 r6 同字节） |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `829378973687dad75727e3bc558a90adee477fd550e6d2171d693ff5e61934d0` | 10133 B，LF 113 行（与 r6 同字节，**本轮未改**） |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行（与 r6 同字节） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `4dd5389f1459ac1f4036bbf35c8827997443a1158d36d2ba27914271be4b88e7` | 8938 B，CRLF 72 行（r6 为 `f1f9a32e…`，本轮已改） |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `4dd5389f1459ac1f4036bbf35c8827997443a1158d36d2ba27914271be4b88e7` | 8938 B；与 `doc/reviews` 载体同字节 |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `cf3266a0d3e2224e90fc3e83b47b7fd48a27a98ea0a12d69a4926bebb967c570` | 10578 B，CRLF 102 行（与 r6 同字节） |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `92e29a94d40d695c08c411ee8dfa501bbf78f76f0d982b0658caca335ed5391a` | 8703 B，CRLF 98 行（与 r6 同字节） |
| `verification/.../EV.md` | `2e8e72a8c2747f51d44a3268b51894724ef8e5ffa9d06b16d0cb3901c691be71` | 1042 B，CRLF 13 行（r6 为 `bedcb892…`，本轮已改） |
| `verification/.../changed-lines.diff` | `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | 15436 B（CRLF 81 行；与 r6 同字节） |
| `verification/.../other-17-pins.txt` | `fee1af10007dde7c9523087d7bb804d1838ef4659d791fc76fc44e9d103c1f54` | 2747 B（与 r6 同字节） |
| `verification/.../pre-post.sha256` | `57c1c2d918207cd64f36d501908648dc54fbd54a6ba6421ed9957f564373ba61` | 178 B（与 r6 同字节） |
| `verification/.../logs/pins.log` | `07c2b60cab2953f31ff614c48a6f818744cacd2cf7b02ab15bcf1b194d929a95` | 408 B |
| `verification/.../logs/check.log`、`check-taskpath.log` | `d1e251bcef74ee9f91d57c031ca40d76b1aebd2633bc65f90ecb386d5a36737d` | 各 421 B |

## 1. A–D 逐项判定

### A. 载体 §6 链与 FROZEN/EV 一致性 — **FAIL（P2）**

| 位置 | 当前字节 | 判定 |
|---|---|---|
| `carrier:59-62` | r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5）→ 处置；r2 `changes_requested`（P0=0/P1=1/P2=4/P3=6）→ 处置；r3 `changes_requested`（P0=0/P1=1/P2=2/P3=7）→ 已传播修正 | **PASS** |
| `carrier:63-64` | r4 `changes_requested`（P0=0/P1=1/P2=0/P3=6）→ 处置；r5 `changes_requested`（P0=0/P1=1/P2=1/P3=3）→ 处置 | **PASS** |
| `carrier:65` | r6 `changes_requested`（P0=0/P1=0/P2=1/P3=2）——R5-N1 / R3-04 / R3-09 → **本轮修正；r7 pending** | **PASS（载体已到 r7 pending）** |
| `EV:3` | 「review=r1→…→r6 changes_requested → **r7 pending**」 | **PASS（与载体一致）** |
| `FROZEN:38`（§1B v1.5 行） | 「r1→r2→r3→r4→r5 changes_requested → 处置 → **r6 pending**，见 §9」，**无 r6 changes_requested、无 r7 pending** | **FAIL（P2）** |
| `FROZEN:110`（§9 复核栏） | 「… r4 changes_requested → r5 changes_requested → 处置 → **r6 pending**（approved 后于本行追加结论）」 | **FAIL（P2）** |
| `FROZEN:50` 条件 7 | 状态 `⏳`；证据指向载体 §6 + `logs/pins.log`；无 ✅、无预填 approved | **PASS** |
| 无预填 approved | `FROZEN:50` `⏳`；`FROZEN:110`「approved 后于本行追加结论」为条件句；`MATRIX:37` 的 approved 属条件列；`carrier`/`EV` 无 v1.5 approved 结论 | **PASS** |

**理由与后果**：r6 的返修把载体与 EV 推进到了「r6 changes_requested → 处置 → r7 pending」，但 FROZEN 的两处记录仍停在 r5 处置后的「r6 pending」。`FROZEN:50` 条件 7 的证据落点正是载体 §6；同一冻结包内 FROZEN、carrier、EV 对当前复核轮次的记载不一致，属 **P2**。修复只需文本：把 `FROZEN:38` 与 `FROZEN:110` 改为「r1→…→r6 changes_requested → 处置 → **r7 pending**」（保留「approved 后于本行追加结论」的条件句式），**不得**预填 approved；`FROZEN:50` 条件 7 保持 `⏳`。

**非阻断观察（不计 finding）**：`carrier:63-65` 的 r4/r5/r6 三行使用反斜杠转义（`\doc/reviews/...\`、`\changes_requested\`）而非反引号，与 r1–r3 行的 Markdown 格式不一致；在 CommonMark 下反斜杠只转义 ASCII 标点，`\d`/`\c` 会以字面反斜杠渲染。这是格式问题，不影响事实，单独记 R7-N2（P3）。

### B. r6 P3 复核（§2.E / AC-T5 / carrier:20） — **部分 FAIL（P3）**

| r6 子项 | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| R3-04 §2.E 登记 §1B v1.4 改写 | `carrier:33-36` | 「pin → v1.5 最终字节 sha256；v1.5 重冻记录；历史 pin 保留」；**未登记 §1B v1.4 行改写/加注** | **FAIL（P3，仍 OPEN）** |
| R3-04 `carrier:60` 措辞 | `carrier:60` | 「§1B v1.4 历史行保留并加注（不改写其历史值）」；`FROZEN:37` 实际已由长行（含 r1 计数/session/head）改写为「r1 changes_requested → 处置 → r2 approved，见 §8」，sha 历史值未改 | **部分改善；仍不精确** |
| R3-09 AC-T5 字面句 | `carrier:41`（§3 安全与兼容） | 「**契约就绪 ≠ 实现/产品可用**：本载体只解除 C-16 v1.5 语义阻塞；L-S4-B 实现与 B2 投影均未交付。」 | **PASS** |
| R3-09 `carrier:20` 单根探测异常 | `carrier:20` | 「缺失/不可读/身份不符/**单根探测异常 → false**；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`」 | **PASS（保留）** |
| §5⑥ 复核核对项 | `carrier:54` | 「⑥载体/卡不夸大（契约就绪 ≠ 实现/产品可用）」仍保留；与 §3 正文句并存，不冲突 | **PASS** |

**理由**：r6 对 R3-04 的要求是「载体 §2.E 登记 §1B v1.4 行改写；修正 `carrier:59` 的『§1B v1.4 行保留不改写』」。当前 `carrier:60` 已从「保留不改写」改为「保留并加注（不改写其历史值）」，方向正确；但 §2.E 仍是修订登记处，当前只登记 pin/重冻/历史 pin，没有写「§1B v1.4 行由原长行改为摘要（删除 r1 计数/session/head），原信息见 §8」。`FROZEN:37` 的实际改写与 §2.E 的沉默形成记录缺口，按 r5/r6 口径继续记 **OPEN（P3 非阻断）**。

### C. C-16 字节 / 安全（不回归） — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（FROZEN:16、FROZEN:18、FROZEN §9:111、pre-post post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF 253 行，0 CRLF） | ✅ |
| C-16 blob 内容 sha256 | `a7f57ebd…`（FROZEN:18） | `git cat-file blob 67c741d3…` 输出 38912 B，sha256 `a7f57ebd…`；与工作树字节相同 | ✅ |
| `git hash-object` | `67c741d3…`（FROZEN:17） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| 两列/零写 | C-16:97/105 两列；103 末句「任一不满足 → typed 拒绝、零写」；107「拒绝/无匹配零写」 | 实测原文一致 | ✅ |
| 幂等/单调 | C-16:106 `updated:0` 且零写；同 registry 代次不倒退、跨 registry 允许 1 | 实测原文一致 | ✅ |
| 错误闭集 | C-16:212 只列既有码；§6 表本体零行改动 | `git diff` 仅新增 v1.5 补充句，无新码 | ✅ |
| 红线 | C-16:108 六条：不自动重新授权/不自动重建 identity/撤销后不放行/不扩授权面/folder 排除/reset limitation | 实测原文一致 | ✅ |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | 5 个文件 `git status` 干净；C15/C17/C06/C07 实算 sha 与 pin 一致；M2-C1 零 diff | 实测 | ✅ |
| 「三列」/`grant.created_at` 规范条款 0 命中 | C-16/FROZEN/MATRIX/PREREQ/AUTO/EV 均 0 | 实测 0/0；carrier 仅 `:59`/`:61`/`:62` 的 r1/r2/r3 **历史复核记录**保留原字样（2/2 命中），规范文本 0 | ✅ |

**接受的非阻断 P3（C-16 字节未改，不重开）**：R3-05（`C-16:103` 四键未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 映射及「SQL 只匹配三身份键」）、R3-06（`C-16:106` 幂等句未加「无其他写入者介入」前提）、R3-10（`C-16:17` 未提 v1.5/§2.5；A 卡/L-S4-A 指称混用）。这些是 r5 已接受的非阻断项；本轮 C-16 仍为 `a7f57ebd…`，不构成回归。

**结论**：C-16 条款层未发现安全放宽或新授权入口；本轮所有变更均在文档/记录面，不是契约字节变更。C-16 §10 ⑦ 仍未满足，原因仅是记录链 P2（以及 P3 文字项），不是 C-16 字节本身。

### D. 证据 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| EV 表逐文件 sha | 7 项 | carrier `4dd5389f…`、changed-lines `9ff9a852…`、check/check-taskpath `d1e251bc…`、pins `07c2b60c…`、other-17 `fee1af10…`、pre-post `57c1c2d9…` 全部实测匹配 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `4dd5389f…`、同 8938 B | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B；三者按 CRLF 与 log **逐字节相等**（EXIT 均为 0；check 3 warnings） | ✅ |
| `pre-post.sha256` | pre=`ad25fb3c…` / post=`a7f57ebd…` | 178 B；HEAD blob 实测 32577 B，sha `ad25fb3c89bb…`；工作树 38912 B，sha `a7f57ebd…` | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 证据原始 15436 B（CRLF 81 行，sha `9ff9a852…`）；原生 diff 15355 B（LF）；`\r\n→\n` 后**逐字节相等**（归一化 15355 B，sha `74b94191a2f643ae00bbde198c4889f3aeeac9a9f81302b8cbc73a29e0979cae`） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；重跑原始输出与 `logs/pins.log` 逐字节相等 | ✅ |
| 其余 17 不变 | 17 项 `UNCHANGED`、`changed=0`、@HEAD | `other-17-pins.txt` 17 条 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| 改动边界 | 仅 5 个文档 + 证据 | `git diff --name-only HEAD` 只有 C-16/FROZEN/矩阵/AUTO/PREREQ；`src/apps/tests/tools` 零 diff；`verification/FEA-09/**` 未被改写 | ✅ |

**证据注记（不影响 PASS）**：`logs/pins.log`、`logs/check*.log` 为 CRLF 存档；用 LF 拼接重跑输出会少 19/6 字节，按 CRLF 拼接则逐字节相等。这与 r6 的「逐字节一致」口径一致，不是伪造或陈旧。`changed-lines.diff` 原始文件为 CRLF 15436 B；归一化（LF）后为 15355 B，sha `74b94191…`，与原生 diff 逐字节一致。

## 2. r6 findings 逐条处置

| r6 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **R5-N1** 载体 §6 复核链停在 r4 | P2 | **CLOSED** | `carrier:59-65` 已补 r5/r6 `changes_requested`（含计数）+ 处置 + **r7 pending**；`EV:3` 一致；`doc/reviews` 副本同字节。注意：FROZEN 未同步是新 P2（R7-N1），不否定 R5-N1 在载体侧的关闭。 |
| **R3-04** §1B v1.4 行改写未登记 | P3 | **OPEN（部分）** | `FROZEN:37` 已改写为摘要（删除 r1 计数/session/head，加「见 §8」），`carrier:60` 措辞已改为「保留并加注（不改写其历史值）」；但 `carrier §2.E`（`:33-36`）**仍未登记**该改写，且「不改写其历史值」未说明描述文本已改写。 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **CLOSED** | `carrier:41`（§3）已有「契约就绪 ≠ 实现/产品可用」正文句；`carrier:20` 保留「单根探测异常 → false」；`carrier:54` §5⑥ 核对项保留。 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **ACCEPTED（未回归）** | C-16 字节保持 `a7f57ebd…`；`C-16:103` ④仍仅列四键、无映射/SQL 三键说明。按 r5 口径接受为非阻断。 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **ACCEPTED（未回归）** | C-16 字节未改；`C-16:106` 幂等句仍无「无并发写入者」前提。接受为非阻断。 |
| **R3-10** §0 版本面/A 卡指称 | P3 | **ACCEPTED（未回归）** | `C-16:17` 仍未提 v1.5/§2.5；`C-16:105`/`PREREQ:46`/`PREREQ:67` 的全名/A 卡/L-S4-A 仍混用。C-16 字节未改，接受为非阻断。 |
| R3-02/R3-03/R3-07（r4 已 CLOSED） | P2/P3 | **CLOSED（未回归）** | `C-16:212` 的 §6 映射、`C-16:35` 的 roots 每根/锁外/单根异常、FROZEN/载体状态链的 r4 结论均未回退；本轮无新反证。 |

**统计**：r6 正文 3 条（P2×1 + P3×2）；本轮 **CLOSED 2**（R5-N1、R3-09）、**OPEN 1**（R3-04 部分）、**ACCEPTED 3**（R3-05/06/10）。另新增 **R7-N1（P2）** 与 **R7-N2（P3）**。按本轮口径折算 **P0=0 / P1=0 / P2=1 / P3=2**。R7-N1 决定 verdict。

## 3. 新 findings 与处置建议

### R7-N1（P2，新）：FROZEN 记录链停在 r6 pending

| 位置 | 当前字节 | 应有 |
|---|---|---|
| `FROZEN:38`（§1B v1.5 行） | 「r1→r2→r3→r4→r5 changes_requested → 处置 → **r6 pending**，见 §9」 | 「r1→…→r6 changes_requested → 处置 → **r7 pending**，见 §9」 |
| `FROZEN:110`（§9 复核栏） | 「… r4 changes_requested → r5 changes_requested → 处置 → **r6 pending**（approved 后于本行追加结论）」 | 「… r4 changes_requested（P0=0/P1=1/P2=0/P3=6）→ r5 changes_requested（P0=0/P1=1/P2=1/P3=3）→ r6 changes_requested（P0=0/P1=0/P2=1/P3=2）→ 处置 → **r7 pending**（approved 后于本行追加结论）」 |
| `carrier:65` / `EV:3` | 已到「r6 changes_requested → r7 pending」 | 保持；无需再改 |

**理由**：r6 报告产出 `changes_requested` 后，载体与 EV 已按同一轮次规则推进；FROZEN 的 §1B/§9 仍写「r6 pending」，使条件 7 的证据链在冻结记录自身断了一轮。修复只改 FROZEN 文本，**不改 C-16 字节**；不得预填 approved，条件 7 保持 `⏳`。

### R3-04（P3，仍 OPEN 部分）：载体 §2.E 未登记 §1B v1.4 行改写

- `carrier §2.E`（`:33-36`）当前只写「pin → v1.5 最终字节 sha256；v1.5 重冻记录；历史 pin 保留」；应补一句：「`§1B` v1.4 历史行已由原长行（含 r1 计数/session/head）改写为摘要并保留 sha 历史值；原信息见 §8」或等价表述。
- `carrier:60` 的「§1B v1.4 历史行保留并加注（不改写其历史值）」建议改为「§1B v1.4 历史行已改写为摘要并登记（sha 历史值不变，原信息见 §8）」，避免「不改写」与 `FROZEN:37` 实际改写之间的歧义。
- FROZEN 侧的改写本身是准确的；剩余问题只在载体登记。

### R7-N2（P3，新，非阻断）：carrier §6 的 r4/r5/r6 行 Markdown 转义异常

`carrier:63-65` 使用 `\doc/reviews/...\`、`\changes_requested\` 的字面反斜杠，而 r1–r3 行使用反引号。CommonMark 只把反斜杠视为 ASCII 标点的转义，`\d`/`\c` 会渲染为带反斜杠的字面文本，导致 §6 记录可读性下降。建议改为反引号（`` `changes_requested` ``、`` `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r4.md` ``）。不影响事实与字节。

### 非阻断观察（不计 finding）

1. **`FROZEN:110` 的 r4/r5 计数**：r1–r3 有 P0/P1/P2/P3 计数，r4/r5 只写 verdict；R7-N1 的修复可顺手补齐 r4/r5/r6 计数，保持同构。
2. **`carrier:65` 的「本轮修正」**：对 R3-09 已成立，对 R3-04 只完成措辞改善、§2.E 未登记；在 R3-04 修复后该句才完全准确。
3. **矩阵状态 vs 条件**：`MATRIX:37` 已标 `FROZEN v1.5`，`FROZEN:50` 条件 7 仍 `⏳`；状态列不是结论、条件列才是 Gate；**不得**把矩阵状态当作已批准事实。
4. **`carrier:41` 的排版**：该正文句紧接 `carrier:40` 的列表项且无空行，部分渲染器会把它并入同一列表项；字面句仍位于 §3，可作为 P3 格式项在本轮一并整理。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=0 / P2=1 / P3=2 待修；R3-05/06/10 继续接受为非阻断）。
- **C-16 字节安全、pin 与证据均通过**：`a7f57ebd…` 未变；`verify_pins` 18/18；日志可复现；`changed-lines` 与原生 diff 一致；未发现安全放宽或新授权入口。
- **阻塞修复（文本修正，不需改 C-16 字节）**：
  1. **R7-N1**：把 `FROZEN:38`、`FROZEN:110` 推进到「r1→…→r6 changes_requested → 处置 → r7 pending」（建议补 r4/r5/r6 计数）；保持 `FROZEN:50` 条件 7 `⏳`，不得预填 approved。
- **P3 建议（同批修，避免下轮再开）**：
  1. **R3-04**：`carrier §2.E` 登记 §1B v1.4 行改写；把 `carrier:60` 的「不改写」改为「已改写为摘要并登记（sha 历史值不变）」。
  2. **R7-N2**：把 `carrier:63-65` 的反斜杠转义改为反引号；可顺手把 `carrier:41` 独立成段。
- **证据与重冻**：
  - 若只改 FROZEN + carrier（及同步副本/EV），C-16 的 `a7f57ebd` pin、`changed-lines.diff`、pre-post、pins.log、other-17 均可保留；`verify_pins` 仍应 18/18，`check.ps1` 重跑。
  - carrier 改动后须重算 EV 的 carrier sha；其余 6 项证据 sha 不变。
  - 修复后做 **r8** 独立 byte-level/记录复审；通过后由 DSH 在载体 §6 append-only 落 approved 结论并提交。**不得**在修复/复审通过前提交或推送本 UNFREEZE。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `3fd301c2-68b7-480e-b0df-9dff4483db95`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r6 复核或任何相关实现；只读被审字节与背景只读材料（C-16、载体、冻结记录、矩阵、PREREQ/AUTO 卡、证据、只读源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/AUTO 卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r7.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--unified=0 HEAD`、`git hash-object`、`git cat-file blob/size`、.NET `SHA256` 字节哈希、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell/.NET UTF-8 字节/行尾/哈希/正则计数、PowerShell 重定向重跑日志与 blob 的逐字节比较。
- **代码只读锚点**：本轮为文档/记录一致性复审，未重新深入审计实现；C 项的安全语义判定基于 C-16 冻结字节、P0/P1 条款与 r4/r5 已记录的实现锚点（`library.py` 单点 SQL、`schema.py` 的 `source_locations`、C-17/M2-C1 既有码），并以「无代码 diff + pins 18/18」佐证。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1–r6 报告仅作为被审输入与对照，不作为事实来源。
