---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r5 窄面文档/记录一致性复审（C-16 字节保持 a7f57ebd…）
reviewer: fresh subagent（r5；独立上下文；未参与本 UNFREEZE 起草、r1–r4 复核或任何相关实现；只读）
session: a6de55ee-9246-4779-93b4-b042a268ee1d
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立文档/记录一致性复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r4 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r5 窄面文档/记录一致性复审

> **结论先行：`changes_requested`，P0=0 / P1=1 / P2=1 / P3=3（另有 3 项 r4 P3 接受为“不重开 C-16 字节”）。**
>
> **P1 仍在**：r5 返修已把 `FROZEN:110` 与 `PREREQ:100` 改为“两列 + `last_verified_at` 原值”，但 **`PREREQ:67`（I-2 动作）仍写 `registry_id/authorization_generation/last_verified_at` 三列并“原地更新为新条目”**。I-2 是 L-S4-B 实现卡的直接输入，与 `C-16:105`、`PREREQ:46`（D-1）及 `FROZEN:110` 相反，R3-01 未闭合。**C-16 契约字节本身未改（`a7f57ebd…`），因此这是卡面/记录问题，不是契约字节回归。**
>
> **新增 P2（记录链）**：r4 已返回 `changes_requested` 且本轮正在做 r5，但 **`FROZEN:39`/`:111`、`carrier §6:61`、`EV:3` 仍停在“r4 pending”**，未登记 r4 结论与 r5 pending；`carrier §6` 只记到 r1–r3。这使冻结记录的复核链与仓库事实不一致，且 `carrier:61` 的“本轮已传播修正”仍不准确（I-2/AUTO 卡尚有残留）。
>
> **P3 未处置**：R3-04（§1B v1.4 行“保留于 §8、不改写”与 diff 不符；载体 §2.E 未登记）、R3-08（AUTO 卡 `:58` 三列字面、`:72` `updated:false`、AC 编号 1..7/9/10/8）、R3-09（AC-T5 字面句仍只在载体 §5⑥；`carrier:20` 仍缺“单根探测异常 → false”）。R3-05/06/10 因 **C-16 字节未改**，本轮接受为非阻断 P3，不重开字节。
>
> **证据与 pin 全部通过**：C-16 sha256=`a7f57ebd…`（38912 B，LF 253 行，0 CRLF）= FROZEN pin = pre-post post = blob 内容 sha；`git hash-object`=`67c741d3…`；`verify_pins` 18/18；其余 17 不变；日志重跑逐字节复现；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字相等。**C-16 §10 ⑦ 的“independent byte-level 复核 approved（P0/P1=0）”未满足，当前冻结包不能按 r5 approved 提交/推送。**

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无并发提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪载体、r1–r4、证据目录 8 文件；**本报告写入后新增 r5 报告 1 个未跟踪项**，其余不变 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff；C-15/C-17/C-06/C-07/M2-C1 亦零 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`；重跑输出与 `logs/pins.log` **逐字节一致**（408 B，sha `07c2b60c…`） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B，sha `d1e251bc…`） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判文档/记录与契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `6034d229cb399f8ca08dd557eefccc149c87057a095153d2aa296dc509260a06` | 10304 B，CRLF 114 行（r4 为 `46349ea0…`，本轮已改） |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行（与 r4 同字节） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `fa52cff663167f672f28c31068fb69b5de439f27596c1a5038dea759a965933a` | 7956 B（与 r4 同字节） |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `fa52cff663167f672f28c31068fb69b5de439f27596c1a5038dea759a965933a` | 7956 B；与 `doc/reviews` 载体同字节（与 r4 同字节） |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `c940eadb566de1a75ac8072d15cb8f086b717f51928c52fb5726d38dfb73521f` | 10506 B，CRLF 102 行（r4 为 `9f764f5e…`，本轮已改） |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `e5bba4e3fd9de49fdf1164b8e50e5db9d23a62203a3185b7369d2c9b3178fdad` | 8681 B（与 r4 同字节，**P3 未改**） |
| `verification/.../EV.md` | `7b67bfee8bc2884a5cb8c8f37d5cab9b5d8d3bdf6bd577c0483f6e1328d5fa1e` | 1041 B（与 r4 同字节，**链未改**） |
| `verification/.../changed-lines.diff` | `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | 15436 B（CRLF 81 行） |
| `verification/.../other-17-pins.txt` | `fee1af10007dde7c9523087d7bb804d1838ef4659d791fc76fc44e9d103c1f54` | 2747 B |
| `verification/.../pre-post.sha256` | `57c1c2d918207cd64f36d501908648dc54fbd54a6ba6421ed9957f564373ba61` | 178 B |
| `verification/.../logs/pins.log` | `07c2b60cab2953f31ff614c48a6f818744cacd2cf7b02ab15bcf1b194d929a95` | 408 B |
| `verification/.../logs/check.log`、`check-taskpath.log` | `d1e251bcef74ee9f91d57c031ca40d76b1aebd2633bc65f90ecb386d5a36737d` | 各 421 B |

## 1. A–E 逐项判定

### A. R3-01 关闭：两列方案的全包传播 — **FAIL（P1；r5 又修好 2 处，I-2 仍未修）**

| # | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| 1 | `C-16:97`（§2.5 用途） | “`registry_id/authorization_generation` **两列**（`last_verified_at` 保持原值、不刷新审计时间）条件单行更新” | **PASS** |
| 2 | `C-16:105`（§2.5 动作） | 只把两列更新为 `grant.registry_id`/`grant.generation`；`last_verified_at` “UPDATE 前读取原值并原样回写”；“不取 `now()`”；复用 A 卡唯一 SQL | **PASS** |
| 3 | `C-16:253`（§10 变更记录） | “只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值” | **PASS** |
| 4 | `FROZEN:110`（§9 修订内容） | “只写 registry/generation 两列、`last_verified_at` 保持原值；…复用 A 卡唯一 SQL”——**“只写三列”已删除**（r5 修正） | **PASS** |
| 5 | `carrier:11`（载体 §1 目标） | “只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值” | **PASS** |
| 6 | `carrier:26`（载体 §2.C 动作） | 两值取自 `grant.registry_id`/`grant.generation`；`last_verified_at` 原值；不取 `now()`；无 `grant.created_at` | **PASS** |
| 7 | `carrier:40`（载体 §3 安全） | “只写 `registry_id/authorization_generation` 两列（`last_verified_at` 不变）” | **PASS** |
| 8 | `PREREQ:46`（D-1） | “只写 `source_locations` 的 registry_id/authorization_generation（`last_verified_at` 保持原值）” | **PASS** |
| 9 | `PREREQ:47`（D-2） | 形状/前置义务，不含三列表述 | **PASS** |
| 10 | `PREREQ:49`（D-4） | 零字节清单已含 C-06；错误码为既有闭集 | **PASS** |
| 11 | `PREREQ:67`（I-2 动作） | “仅把 Core `source_locations` 当前行的 `registry_id/authorization_generation/last_verified_at` 原地更新为新条目…”——**仍三列 + “新条目”** | **FAIL（P1）** |
| 12 | `PREREQ:100`（ZCode 裁决记录） | 已改为“只写 registry/generation 两列（last_verified_at 原值）”（r5 修正） | **PASS** |

补充核对（不在 r3 的 8 处口径内）：

| 位置 | 当前字节 | 判定 |
|---|---|---|
| `AUTO:58`（L-S4-B 卡 Core 动作） | 仍写“条件写 `registry_id/authorization_generation/last_verified_at`（…`last_verified_at` 保持原值）” | **FAIL（P3，属 R3-08）** |
| `C-16:31` 的 `created_at` | `source_list_roots` 条目的既有 Registry 字段，**不是** `grant.created_at` | 不计缺陷 |

**包级结论**：

- **字面“三列”**：`FROZEN`/`PREREQ` 已 0 命中；但 **字段枚举**在 `PREREQ:67` 仍为三项（`AUTO:58` 亦同）。因此“全包一致”**不成立**。
- **`grant.created_at`**：规范条款（C-16 §2.5 用途/动作/§10、FROZEN §9、载体 §1/§2.C/§3、PREREQ I-2/D-2/D-4）**0 命中**；仅 `carrier:58/60` 的 r1/r2 历史复核记录各提到一次（共 2 处），不是写入值来源。**不计为写入值缺陷。**
- **C-16 内部自洽**：C-16 全文无“三列”，无 `grant.created_at`；§2.5 用途/动作/§10 三处均为两列 + 原值；`C-16:105` 对单点 SQL 谓词的描述与只读锚点一致（SET 子句物理上仍列出 `last_verified_at = ?`，由“原值回写”解释为语义两列，**不构成自相矛盾**）。**PASS。**
- **`PREREQ:67` 的严重性**：它是 L-S4-B 实现卡的直接输入，照此实现会把 `last_verified_at` 写成“新条目”的时间（无值可取）或与冻结动作相反；与同卡 `:46`、`C-16:105`、`FROZEN:110` 直接矛盾。**P1。**

### B. r4 P3 处置 / 接受 — **3 OPEN、3 ACCEPTED；§1B 结构无损坏但仍有措辞不实**

| r4 项 | 核对 | 状态 | 证据 |
|---|---|---|---|
| **R3-04** | §1B v1.4 行是否保留且无重复/损坏 | **结构 PASS；准确性 OPEN（P3）** | `FROZEN:37` 的 v1.4 pin 行仍存在且只出现一次；§1B 表 2 列、无重复 pin、无表格损坏。但 `FROZEN:38` 仍写“原 v1.4 行保留于 §8，不改写”；`git diff HEAD` 显示 `:37` 已被改写（删去 r1 计数/session/head）。`carrier §2.E` 仍未登记该编辑。 |
| — | 载体 §2.E | **OPEN（P3）** | `carrier:34-35` 仍只写“pin → v1.5…；v1.5 重冻记录；历史 pin 保留”，未登记 §1B v1.4 行的改写。 |
| — | C-16:17 v1.5 标注 | **ACCEPTED（P3；不重开字节）** | `C-16:17` 仍只写 `source-access-wire/1.3` + v1.3/v1.4，不提 v1.5/§2.5。C-16 字节本轮保持 `a7f57ebd…`，按 r4 口径接受为非阻断 P3。 |
| **R3-09** | `carrier:20` 单根探测异常 | **OPEN（P3）** | `carrier:20` 仍为“缺失/不可读/身份不符 → false；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`”，未同步 `C-16:35` 的“单根探测异常为 false（探测异常不得抛出、不得使整命令失败）”。载体文字可改，未改。 |
| **R3-08** | AUTO 卡三列残留 | **OPEN（P3，3/3 未改）** | `AUTO:58` 仍列三字段；`AUTO:72` 仍写“重复调用 `updated:false`”（合同为 `updated: 0|1`）；`AUTO:69-78` 的 AC 编号仍为 1..7、9、10、8。 |
| **R3-05** | C-16:103 ④ 四键键映射 | **ACCEPTED（P3；不重开字节）** | `C-16:103` ④已列四键 `content_digest/volume_serial/file_id/size_bytes`，但仍未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 的映射，也未写“单点 SQL 的 WHERE 只匹配三身份键，`size_bytes` 由 handler 在调用前比对”。C-16 字节未改，接受 P3。 |
| **R3-06** | C-16:106 并发前提/无匹配 | **ACCEPTED（P3；不重开字节）** | `C-16:106` 仍写“同 grant 重复调用 → `updated:0` 且零写（幂等）”，未加“无其他写入者介入”前提；无匹配/代次回退的返回未逐项写死。C-16 字节未改，接受 P3。 |
| **R3-10** | §0 版本面 / A 卡指称 | **ACCEPTED（P3；不重开字节）** | `C-16:17` 未提 v1.5/§2.5；`C-16:105` 用全名、`PREREQ:46` 用“A 卡”、`PREREQ:67` 用“L-S4-A”，指称仍混用。C-16 字节未改，接受 P3。 |

**非阻断观察（沿用 r4，不计 finding）**：`C-16:107` 的“复用 §6 既有闭集——host-only/session 守卫沿用既有码”字面上仍可被读成“§6 表包含 `HOST_*` 码”（实际 §6 表不含）；`:212` 已拆清。建议改为“既有错误码（§6 + M2-C1 host-control 码）”。

### C. 冻结包一致性 — **FAIL（P2 记录链 + P3 措辞）；无预填 approved；不夸大基本成立**

| 子项 | 判定 | 证据 |
|---|---|---|
| 版本主链 | **PASS** | `C-16:3/4` v1.5、`FROZEN:4/15` v1.5、`MATRIX:3/37` v1.5、证据 pre/post 一致。 |
| 历史 pin 保留 | **PASS** | `FROZEN:35-37`（v1.1/v1.3/v1.4）、`FROZEN:113`（v1.4/v1.3/v1.1/v1.0）；v1.4 pre 实测 `ad25fb3c…`（32577 B，HEAD blob `b9be0acf…`）；v1.3/v1.1/v1.0 历史值按记录保留（未在工作树重算）。 |
| §1A 三口径 | **PASS** | `FROZEN:22-25` 未改；三口径在本字节上实测一致（见 D）。 |
| §1B v1.4 行 | **准确性 FAIL（R3-04，P3）** | `FROZEN:37` 的 v1.4 复核行为 `ad25fb3c…`、r1→r2 approved，正确；但 `:38` 的“原 v1.4 行保留于 §8，不改写”与 `git diff` 不符（`:37` 已改写），载体 §2.E 未登记。 |
| §1B v1.5 行 / 复核链 | **FAIL（R5-N1，P2）** | `FROZEN:39` 仍写“r1→r2→r3 changes_requested → 处置 → **r4 pending**”；r4 报告已存在并返回 `changes_requested`，本轮为 r5。 |
| §2 条件 7 | **PASS** | `FROZEN:51` 第 7 行为 v1.5、状态 `⏳`；证据指向载体 §6 与本轮 `pins.log`；无 ✅、无预填 approved。 |
| §9 修订内容 | **PASS（列口径）** | `FROZEN:110` 已是“两列 + `last_verified_at` 原值”；“三列”0 命中。 |
| §9 复核栏 | **FAIL（R5-N1，P2）** | `FROZEN:111` 仍为“…→ 处置 → **r4 pending**（approved 后于本行追加结论）”；未记 r4 `changes_requested` 与 r5 pending。 |
| 矩阵行 | **PASS（附流程注记）** | `MATRIX:37` C-16 为 `FROZEN v1.5`，条件列含“①v1.5 独立 byte-level 复核 approved”。这与 v1.4/v1.5 的矩阵写法同构：状态列不是结论、条件列才是 Gate；`FROZEN:51` 仍 `⏳`，**不得**把矩阵状态当作已批准事实。 |
| 载体 §6 | **FAIL（R5-N1，P2）** | `carrier:56-61` 只记 r1、处置、r2、r3，最后一行仍“本轮已传播修正；**r4 pending**”；未记 r4 `changes_requested`、未写 r5 pending。且因 `PREREQ:67`/`AUTO:58` 仍有残留，“本轮已传播修正”不准确。 |
| 无预填 approved | **PASS** | v1.5 相关状态为 `⏳`/`pending`/“r4 pending”（`FROZEN:51,111`、`carrier:61`、`EV:3`）；`MATRIX:37` 的“approved”属条件列，不是结论；`FROZEN:111` 的“approved 后于本行追加结论”是条件句。 |
| 不夸大（契约 ≠ 实现/产品） | **PASS（弱）** | `carrier:3`“须经独立复核 + DSH 重新冻结后方可视为最终字节”；`C-16:240`“不构成实现授权；不证明 AC 达成”；`FROZEN:57` 同口径。AC-T5 字面句仍只出现在载体 §5⑥（R3-09，P3）。 |

**流程注记（不计 finding）**：`MATRIX:3/37` 已把 C-16 标为 `FROZEN v1.5`，而 `FROZEN:51` 条件 7 仍 `⏳`；这与 r3/r4 对 v1.4 行的处理口径一致（条件列不是结论），但在 r5 通过前不应把矩阵状态当作已批准事实。

### D. pin / 证据 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（FROZEN:16、FROZEN:18、FROZEN §9:112、pre-post post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF 253 行，0 CRLF） | ✅ |
| C-16 blob 内容 sha256 | `a7f57ebd…`（FROZEN:18） | `git cat-file blob 67c741d3…` 输出 38912 B，sha256 `a7f57ebd…`；与工作树字节逐字节相同 | ✅ |
| `git hash-object` | `67c741d3…`（FROZEN:17） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| HEAD v1.4 blob sha256（pre） | `ad25fb3c…`（pre-post pre、FROZEN §1B:37） | HEAD blob `b9be0acf…`，内容 32577 B，sha256 `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；重跑原始输出与 `logs/pins.log` 逐字节相等（408 B） | ✅ |
| 其余 17 不变 | 17 项 `UNCHANGED`、`changed=0`、@HEAD | `other-17-pins.txt` 17 行 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD；`verify_pins` 全部 OK | ✅ |
| 独立抽查未重签 pin | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 全部 match | ✅ |
| `pre-post.sha256` | pre=`ad25fb3c…` / post=`a7f57ebd…` | 178 B；两值实测匹配 | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 证据原始 15436 B（CRLF 81 行，sha `9ff9a852…`）；原生 diff 15355 B（LF）；`\r\n→\n` 后**逐字节相等**（归一化 15355 B，sha `74b94191a2f643ae00bbde198c4889f3aeeac9a9f81302b8cbc73a29e0979cae`） | ✅ |
| EV 表逐文件 sha | 7 项 | carrier `fa52cff6`、changed-lines `9ff9a852`、check/check-taskpath `d1e251bc`、pins `07c2b60c`、other-17 `fee1af10`、pre-post `57c1c2d9` 全部实测匹配 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `fa52cff6…`、同 7956 B | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B；三者与 log **逐字节相等**（EXIT 均为 0；check 3 warnings） | ✅ |
| 改动边界 | 仅 5 个文档 + 证据 | `git diff --name-only HEAD` 只有 C-16/FROZEN/矩阵/AUTO/PREREQ；`src/apps/tests/tools` 零 diff；`verification/FEA-09/**` 未被改写 | ✅ |

**证据注记（不影响 PASS）**：r4 报告把“归一化 sha”写成 `9ff9a852…`；实测 `9ff9a852…` 是**原始 CRLF 证据文件**的 sha，归一化（LF）后是 `74b94191…`（r3 §0.1 亦记 `74b94191…`）。证据文件本身与原生 diff 文本一致，**无伪造/无陈旧**；此处仅是 r4 报告的标注笔误，不是本包缺陷。

### E. 安全语义（不回归） — **PASS**

| 子项 | 判定 | 证据 |
|---|---|---|
| 请求恰 2 键；无路径/`registry_id`/`generation` | **PASS** | `C-16:98-102` 仅 `{"source_id","grant_id"}`；`C-16:103` ②明写无路径/无 registry_id/无 generation。 |
| 拒绝/无匹配零写 | **PASS** | `C-16:103` 末句“任一不满足 → typed 拒绝、**零写**”；`C-16:107`“拒绝/无匹配零写”。 |
| 只写两列；`last_verified_at` 不变 | **PASS（合同动作）** | `C-16:105` 只改 `registry_id/authorization_generation`，`last_verified_at` 原值回写；复用 `library.py` 单点 SQL（SET 含第三列但写原值；无第二份 SQL）。 |
| 不改行数/`source_id`/digest/`is_current`/binding | **PASS** | `C-16:105` 明写；不 INSERT、不写 `is_current`、`page_bindings` 不在 SQL 内。 |
| 错误码闭集无新增 | **PASS** | C-16 `git diff` 仅新增 v1.5 条款；§6 表本体零行改动；`C-16:212` 只列既有码；host-only/session 为 M2-C1/C-17 既有码。 |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | **PASS** | `git diff --name-only HEAD` 仅 5 个文档；这些文件 `git status` 均为空；`verify_pins` 18/18，C15/C17/C06/C07 实算匹配；`M2-C1_TYPED_IPC_CONTRACT.md` 未改。 |
| 红线：不自动重新授权/不重建 identity/撤销后不放行/不扩面/folder 排除/reset limitation | **PASS** | `C-16:108` 六条齐备；`C-16:97` 明写“不是恢复动作、不是授权决定”；`C-16:103` ③要求 grant live/未撤销；`C-16:104` Host 侧 folder 排除；`C-16:108` reset 后无旧条目可桥接。 |
| Host/Core 义务分离 | **PASS** | `C-16:103` 只列 Core 边界四项；`C-16:104` 独立成“Host 侧前置义务（本命令不校验、不依赖）”，含唯一 live、恰 1 根、路径 normalize、`live.CreatedAt > old.RevokedAt`、非 folder、每轮一次；Core `source_locations` 无 path 列（`schema.py` 实测）。 |
| 无新 wire minor/schema/依赖 | **PASS** | C-16 diff 无 `PROTOCOL_MINOR`/schema/依赖行；`C-16:244` ⑦；`PREREQ:49` 错误码复用既有闭集。 |
| C-07 / `HostCommandRegistry.All` 不变 | **PASS** | 无代码 diff；C-07 pin `3fdb44e49afe…` 未变；C-16:36 明写 FEA-09 不新增 `IHostController`。 |

**结论**：C-16 条款层未发现安全放宽或新授权入口；R3-01 是“冻结包内文档仍要求不存在的值/相反的列集合”，属可执行性与包一致性问题，不是新的安全放行。

## 2. r4 findings 逐条处置

| r4 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **R3-01** 两列方案未传播 | P1 | **OPEN（r5 修好 FROZEN:110/PREREQ:100；I-2:67 未修）** | `C-16:97/105/253`、`FROZEN:110`、`carrier:11/26/40`、`PREREQ:46/100` 已为两列；`PREREQ:67` 仍三列/“新条目”；`AUTO:58` 仍三字段（P3）。`grant.created_at` 规范条款 0 命中。 |
| **R3-02** FROZEN §1B/§9 与载体不一致 | P2 | **CLOSED** | `FROZEN:39/111`、`carrier:61`、`EV:3` 在 r4 时同为“r4 pending”，互不矛盾；r4 的 P2 关闭。**注意**：r4 返回后这条链未推进，另计 R5-N1。 |
| **R3-03** §6“权限面”归 `INVALID_REQUEST` | P2 | **CLOSED** | `C-16:212` 已拆为 closed-shape `INVALID_REQUEST` + host-only/session 既有码；与 `C-16:103①`、§2.4①、C-17、`core_service.py` 既有码一致。 |
| **R3-04** §1B v1.4 行改写未登记 | P3 | **OPEN** | `FROZEN:38` 仍称“原 v1.4 行保留于 §8，不改写”，但 diff 显示 `:37` 已改写；载体 §2.E 未登记。 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **ACCEPTED（P3；不重开字节）** | C-16 字节本轮保持 `a7f57ebd…`；`C-16:103` ④仍仅列四键，无映射/SQL 三键说明。按 r4 口径接受为非阻断 P3。 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **ACCEPTED（P3；不重开字节）** | C-16 字节未改；`C-16:106` 幂等句仍无“无并发写入者”前提。接受为非阻断 P3。 |
| **R3-07** roots 每根/锁外 | P3 | **CLOSED** | `C-16:35` 仍写“每根至多一次、不跨调用缓存、探测在快照后锁外进行；单根探测异常为 false”。（载体 §2.B 未同步，属 R3-09。） |
| **R3-08** 卡面小疵 | P3 | **OPEN（3/3 未改）** | `AUTO:69-78` AC 顺序仍 1..7、9、10、8；`AUTO:72` 仍 `updated:false`；`AUTO:58` 仍三字段字面。 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **OPEN（1/3 已修）** | D-4 已补 C-06；AC-T5 字面句仍只在 `carrier:53` ⑥ 核对项；`carrier:20` 仍缺“单根探测异常 → false”。 |
| **R3-10** §0 版本面/A 卡指称 | P3 | **ACCEPTED（P3；不重开字节）** | C-16:17 仍未提 v1.5/§2.5；`C-16:105`/`PREREQ:46`/`PREREQ:67` 的“全名/A 卡/L-S4-A”仍混用。C-16 字节未改，接受为非阻断 P3。 |

**统计**：r4 正文 10 条（P1×1 + P2×2 + P3×7）；本轮 **CLOSED 3**（R3-02、R3-03、R3-07）、**ACCEPTED 3**（R3-05、R3-06、R3-10）、**OPEN 4**（R3-01、R3-04、R3-08、R3-09）。其中 R3-01 决定 verdict。

## 3. 新 findings

### R5-N1（P2）：r4 返回后复核链未推进到 r5 pending

| 位置 | 当前字节 | 应有 |
|---|---|---|
| `FROZEN:39`（§1B v1.5 行） | “r1→r2→r3 changes_requested → 处置 → **r4 pending**” | 记 r4 `changes_requested`（P0=0/P1=1/P2=0/P3=6）→ 处置 → **r5 pending** |
| `FROZEN:111`（§9 复核栏） | “…→ 处置 → **r4 pending**（approved 后于本行追加结论）” | 同上；r5 通过后再追加 approved 结论 |
| `carrier:61`（§6 末行） | “r3 …→ 本轮已传播修正；**r4 pending**” | 追加 r4 `changes_requested` + 处置要点 + **r5 pending**；并修正“本轮已传播修正”表述 |
| `EV:3` | “review=r1→r2→r3 changes_requested → **r4 pending**” | 记 r1–r4 changes_requested → r5 pending |

**理由**：r4 报告已于 2026-11-07 产出（`doc/reviews/FEA-11-L-S4-B-PREREQ-1-r4.md`，verdict=`changes_requested`，P0=0/P1=1/P2=0/P3=6），本轮 r5 正在复审；记录仍写“r4 pending”与仓库事实不符。r3 的 §0.1 也采用同一约定：上一轮返回后把链推进到“rN changes_requested → 处置 → rN+1 pending”。**这不影响 C-16 字节，纯记录修正**；但它是冻结记录（条件 7 证据指向载体 §6）的一部分，属 P2。

**连带**：若修 `carrier.md`，必须同步 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`（同字节），并更新 `EV.md` 的 carrier sha；`carrier:61` 的“本轮已传播修正”应改为“已传播 FROZEN:110/PREREQ:100；I-2:67/AUTO:58 仍待修”或等价事实表述。

### 非阻断观察（不计 finding）

1. **`FROZEN:110` 的 Host 义务枚举用“=”但未穷尽**：`C-16:104` 的 Host 义务还包括“路径 normalize”与“每个 grant/每轮 refresh 至多一次”，`§9:110` 只列“唯一 live 条目+`CreatedAt>RevokedAt`+恰一根+非 folder”；Core 侧“live grant+四键身份”亦省略 `grant.scope.source_id == source_id`。建议把“=”改为“包括”或补全，避免读者把摘要当穷尽清单。**不影响两列结论。**
2. **`carrier:61`“本轮已传播修正”仍不准确**：`PREREQ:67`/`AUTO:58` 仍有残留；随 R5-N1 一并改。
3. **r4 报告的归一化 sha 标注笔误**：`9ff9a852…` 是原始 CRLF 文件 sha；归一化 LF 后是 `74b94191…`。证据文件本身无问题。
4. **矩阵状态 vs 条件**：`MATRIX:37` `FROZEN v1.5` 与 `FROZEN:51` `⏳` 并存，沿用 v1.4 的矩阵写法；不当作已批准事实。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=1 / P2=1 / P3=3 待修；另有 3 项 r4 P3 接受为非阻断）。
- C-16 §10 ⑦ 的“independent byte-level 复核 approved（P0/P1=0）”**未满足**；当前冻结包不能按 r5 approved 提交/推送。
- **阻塞修复（必须先做，均为文本修正，不需改 C-16 字节）**：
  1. `PREREQ:67` 改为“仅把 Core `source_locations` 当前行的 `registry_id/authorization_generation` 原地更新为 live grant 载荷中的 `grant.registry_id`/`grant.generation`；`last_verified_at` 保持原值”；删除“三列/新条目”表述。
  2. R5-N1：`carrier §6` append r4 `changes_requested`（P0=0/P1=1/P2=0/P3=6）+ 处置 + **r5 pending**；`FROZEN:39/111`、`EV:3` 同步；修正 `carrier:61` 的“已传播”表述；同步 `carrier.md` 副本与 EV carrier sha。
- **P3 建议（同批修，避免下轮再开）**：
  - R3-04：`FROZEN:38` 改精确表述（“§1B v1.4 行已改写为…；原 v1.4 记录见 §8”），载体 §2.E 登记。
  - R3-08：`AUTO:58` 改两列；`AUTO:72` `updated:false`→`updated:0`；AC 编号重排为 1..10。
  - R3-09：载体 §2.B 补“单根探测异常 → false（不得抛出/不得使整命令失败）”；AC-T5 字面句移到载体正文结论（§1/§3）。
- **证据与重冻**：
  - 若只改 PREREQ/FROZEN/carrier/EV/AUTO（不改 C-16），C-16 的 `a7f57ebd` pin、`changed-lines.diff`、pre-post、pins.log、other-17 均可保留；`verify_pins` 仍应 18/18，`check.ps1` 重跑。
  - `carrier.md`/`EV.md` 改动后须重算 EV 的 carrier sha；若 `check.log` 输出不变可保留（本轮 PREREQ 文本改动未改变 check 输出，已实测）。
  - 修复后做 **r6** 独立 byte-level/记录复审；通过后由 DSH 在载体 §6 append-only 落 approved 结论并提交。**不得**在修复/复审通过前提交或推送本 UNFREEZE。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `a6de55ee-9246-4779-93b4-b042a268ee1d`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r4 复核或任何相关实现；只读被审字节与背景只读材料（C-16、载体、冻结记录、矩阵、PREREQ/AUTO 卡、证据、只读源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/AUTO 卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r5.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--unified=0 HEAD`、`git hash-object`、`git cat-file blob/size`、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell/.NET UTF-8 字节/行尾/哈希/正则计数、`cmd` 重定向重跑日志与 blob。
- **代码只读锚点**：本轮为文档/记录一致性复审，未重新深入审计实现；E 项的安全语义判定基于 C-16 冻结字节、P0/P1 条款与 r4 已记录的实现锚点（`library.py` 单点 SQL、`schema.py` 的 `source_locations`、C-17/M2-C1 既有码），并以“无代码 diff + pins 18/18”佐证。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1–r4 报告仅作为被审输入与对照，不作为事实来源。
