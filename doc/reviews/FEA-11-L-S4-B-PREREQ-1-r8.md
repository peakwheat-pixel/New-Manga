---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r8 最终收口复审（C-16 字节保持 a7f57ebd…）
reviewer: fresh subagent（r8；独立上下文；未参与本 UNFREEZE 起草、r1–r7 复核或任何相关实现；只读）
session: fc11c286-8b80-4276-9d57-9b4b226b30d5
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立文档/记录一致性最终收口复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r7 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: approved
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r8 最终收口复审

> **结论先行：`approved`，P0=0 / P1=0 / P2=0 / P3=0（另有非阻断观察，见 §3）。**
>
> **A（记录链）PASS**：`FROZEN §1B:38`、`FROZEN §9:110`、`carrier §6`（`:60-74`）、`EV:3` 已一致记录 `r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending`；`carrier §6` 末行以「**r8 待复核**：`pending`」表达同一 pending；`FROZEN:50` 条件 7 仍为 `⏳`，无预填 approved。
>
> **B（r7 P3 复核）PASS**：`carrier §2.E:37` 已新增「**§1B v1.4 行登记**」：历史值保留、原明细（r1 计数/session/head）见 §8、历史 pin 未改动、v1.5 行追加；`carrier §6` 尾行与链一致；`carrier:20` 保留「缺失/不可读/身份不符/**单根探测异常 → false**；…文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`」；AC-T5 字面句在 `carrier:42`（§3）；`carrier §6`（`:60-74`）的反斜杠转义已全部改回反引号（实测 0 命中）。
>
> **C（C-16 字节/安全）PASS**：sha256=`a7f57ebdbd67…`（38912 B，LF 253 行，0 CRLF）= FROZEN pin = blob 内容 sha=`a7f57ebd…`；`git hash-object`=`67c741d3…`；pre=`ad25fb3c…`（HEAD v1.4 blob，32577 B）/ post=`a7f57ebd…`；两列/零写/幂等/单调/错误闭集/红线均未回退；C-15/C-17/C-06/C-07/M2-C1 零字节；「三列」/`grant.created_at` 规范条款 0 命中（仅载体 §6 的 r1/r2/r3/处置3/r4/r5 历史复核记录保留原字样）。
>
> **D（证据）PASS**：EV 7 项 sha 全部实测匹配（carrier `833b3276…`）；`doc/reviews` 载体与 `verification/**/carrier.md` 同字节；`verify_pins` **18/18**；`check`（默认 / `-TaskPath`）PASS（3 warnings）；pins/check 日志重跑**逐字节复现**；`pre-post.sha256` 与 HEAD/worktree 一致；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字节相等。
>
> **C-16 §10 ⑦ 的「独立 byte-level 复核 approved（P0/P1=0）」已满足；本 UNFREEZE 可按 approved 进入「载体 §6 append-only 落结论 → 冻结记录条件 7 更新 → 提交/推送」流程。**

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无新提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪 17 项（载体、r1–r8、证据目录 8 文件）；r8 报告为本轮新增，其余与 r7 复核时一致 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff；C-15/C-17/C-06/C-07/M2-C1 亦零 diff；`verification/FEA-09/**` 无改动） | `git diff --name-only HEAD`、`git status` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`；重跑输出按 CRLF 与 `logs/pins.log` **逐字节一致**（408 B，sha `07c2b60c…`） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B，sha `d1e251bc…`） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（`src/**`、`apps/**`、`tests/**` 中 `ReattestSourceLocation`/`source.reattest` 实测 0 命中；本复审只判文档/记录与契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256；最终快照 2026-11-07 13:48:15–13:50:32，之后至本报告多次测量稳定）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `7494fbb352a6306ddf8de33b0b774dff9c01a060402668865eb5eb9b748194fb` | 10193 B，LF 113 行，0 CRLF |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行 |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `833b3276c8c0da32cb4b094eae1d5d1b65b6444a2d112d4628e948337e927aa5` | 9271 B，CRLF 81 行 |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `833b3276c8c0da32cb4b094eae1d5d1b65b6444a2d112d4628e948337e927aa5` | 9271 B；与 `doc/reviews` 载体同字节 |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `cf3266a0d3e2224e90fc3e83b47b7fd48a27a98ea0a12d69a4926bebb967c570` | 10578 B，CRLF 102 行 |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `92e29a94d40d695c08c411ee8dfa501bbf78f76f0d982b0658caca335ed5391a` | 8703 B，CRLF 98 行 |
| `verification/.../EV.md` | `da3ad2a8ef2cf74bb953de28e432440ae97c144821fda58278e7c62e08129b9a` | 1074 B，CRLF 14 行 |
| `verification/.../changed-lines.diff` | `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | 15436 B（CRLF 81 行） |
| `verification/.../other-17-pins.txt` | `fee1af10007dde7c9523087d7bb804d1838ef4659d791fc76fc44e9d103c1f54` | 2747 B（CRLF 19 行） |
| `verification/.../pre-post.sha256` | `57c1c2d918207cd64f36d501908648dc54fbd54a6ba6421ed9957f564373ba61` | 178 B（CRLF 2 行） |
| `verification/.../logs/pins.log` | `07c2b60cab2953f31ff614c48a6f818744cacd2cf7b02ab15bcf1b194d929a95` | 408 B（CRLF 19 行） |
| `verification/.../logs/check.log`、`check-taskpath.log` | `d1e251bcef74ee9f91d57c031ca40d76b1aebd2633bc65f90ecb386d5a36737d` | 各 421 B（CRLF 6 行） |

**快照与并发注记（不计 finding）**：复核期间工作树发生两次外部更新：13:48:15–18（FROZEN `7494fbb3…`、carrier `833b3276…`、EV 首版、日志重写）与 13:50:32（EV 最终 `da3ad2a8…`）；本报告以 **13:50:32 最终字节** 为准，并在最终快照后多次复核稳定。输入报告 `r7.md`（13:37:59）与 `r6.md`（13:41:13）亦被外部更新，但均非本任务被审 UNFREEZE 字节。r7 报告正文的实测表基于 13:31 快照（carrier `4dd5389f…`、EV `2e8e72a8…`），未覆盖 13:37/13:48/13:50 的最终载体/EV；本 r8 直接复核最终字节。

## 1. A–D 逐项判定

### A. 记录链一致性（唯一 P2） — **PASS**

| 位置 | 当前字节（摘要） | 判定 |
|---|---|---|
| `FROZEN:38`（§1B v1.5 行） | 「…r1→r2→r3→r4→r5→r6→**r7 changes_requested** → 处置 → **r8 pending**，见 §9」 | **PASS** |
| `FROZEN:110`（§9 复核栏） | 「r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5）→ r2 `changes_requested`（P0=0/P1=1/P2=4/P3=6）→ r3 `changes_requested`（P0=0/P1=1/P2=2/P3=7）→ r4 changes_requested → r5 changes_requested → r6 changes_requested → **r7 changes_requested** → 处置 → **r8 pending**（approved 后于本行追加结论）」 | **PASS** |
| `carrier §6`（`carrier:60-74`） | r1、处置 1、r2、处置 2、r3、处置 3、r4、处置 4、r5、处置 5、r6、处置 6、**r7**、**处置 7（本轮）**；末行「**r8 待复核**：`pending`（只读最终字节；C-16 字节保持 `a7f57ebd…` 不变）」 | **PASS（含 r7；r8 pending 语义一致）** |
| `EV:3` | 「任务：C-16 v1.5 UNFREEZE；Owner=DSH；review=**r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending**。」 | **PASS** |
| `FROZEN:50` 条件 7 | 状态 `⏳`；证据＝载体 §6 + `verification/.../logs/pins.log`；无 ✅ | **PASS（未预填 approved）** |
| 无预填 approved | `FROZEN:50` `⏳`；`FROZEN:110`「approved 后于本行追加结论」为条件句；`carrier §6` 末行 `pending`；`carrier:56` 为「通过标准 approved」；`MATRIX:37` 的 approved 属**冻结条件列**（与 C-15/C-16 v1.4 行同构，不是结论） | **PASS** |

**理由**：r7 的 R7-N1 要求把记录链推进到「r1→…→r7 changes_requested → 处置 → r8 pending」。最终字节中，`FROZEN §1B`、`FROZEN §9`、`carrier §6`、`EV` 四处均已包含 r7 `changes_requested` 与 r8 pending；`FROZEN:38` 的「见 §9」在 §9 有对应项；`FROZEN:50` 条件 7 仍为 `⏳`，无预填 approved。**A 闭合。**

### B. r7 P3 复核（§2.E / §6 尾行 / carrier:20 / AC-T5） — **PASS**

| r7 子项 | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| **R3-04** §2.E 登记 §1B v1.4 行改写 | `carrier:37`（§2.E） | 「**§1B v1.4 行登记**：FROZEN §1B 的 v1.4 行历史值保留并加注「历史行，见 §8」；原明细（r1 计数/session/head）见 §8，未改动历史 pin 值；v1.5 行追加。」 | **PASS**（登记已补；「加注」措辞见观察 2） |
| **R3-04** 旧「不改写」措辞 | 旧 `carrier:60` 内容 | 已被 §6 重写移除；`carrier:67`（处置 4）改为「§1B v1.4 行加注为历史摘要（原明细见 §8）」；`carrier:73`（处置 7）为「§2.E 登记 §1B v1.4 行改写」 | **PASS** |
| **R3-04** §6 尾行与链一致 | `carrier:74` | 「**r8 待复核**：`pending`（只读最终字节；C-16 字节保持 `a7f57ebd…` 不变）。」 | **PASS** |
| **R3-09** AC-T5 字面句 | `carrier:42`（§3 安全与兼容） | 「**契约就绪 ≠ 实现/产品可用**：本载体只解除 C-16 v1.5 语义阻塞；L-S4-B 实现与 B2 投影均未交付。」 | **PASS** |
| **R3-09** `carrier:20` 单根探测异常 | `carrier:20` | 「缺失/不可读/身份不符/**单根探测异常 → false**；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`」 | **PASS（保留）** |
| **R7-N2** 反斜杠转义 | `carrier:60-74` | 路径与 verdict 改用反引号（如 `` `changes_requested` ``、`` `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r1.md` ``）；实测 `\doc/reviews`/`\changes_requested` **0 命中** | **PASS（已修）** |
| §5⑥ 复核核对项 | `carrier:55` | 「⑥载体/卡不夸大（契约就绪 ≠ 实现/产品可用）」仍保留；与 §3 正文句并存，不冲突 | **PASS** |

**理由**：r7 的 R3-04 要求载体 §2.E 登记 §1B v1.4 行改写、原信息见 §8；最终 §2.E 新增了登记段，明确历史值保留、r1 计数/session/head 原明细见 §8、历史 pin 未改、v1.5 行追加。R7-N2 的反斜杠已全部改为反引号；`carrier:20` 与 AC-T5 字面句均保留。**B 闭合。**

### C. C-16 字节 / 安全（不回归） — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（FROZEN:16、FROZEN:18、pre-post post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF 253 行，0 CRLF） | ✅ |
| C-16 blob 内容 sha256 | `a7f57ebd…`（FROZEN:18） | `git cat-file blob 67c741d3…` 输出 38912 B，sha256 `a7f57ebd…`；与工作树字节相同 | ✅ |
| `git hash-object` | `67c741d3…`（FROZEN:17） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| HEAD（v1.4）blob 内容 sha256（pre） | `ad25fb3c…`（pre-post pre、FROZEN §1B:37） | HEAD blob `b9be0acf…`，内容 32577 B，sha256 `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` | ✅ |
| 两列/零写 | C-16:97（用途）、105（动作）、253（变更记录）两列；103 末句「任一不满足 → typed 拒绝、**零写**」；107「拒绝/无匹配零写」 | 实测原文一致 | ✅ |
| 幂等/单调 | C-16:106 `updated:0` 且零写（幂等）；「generation 单调（同 registry 不倒退，跨 registry 允许 1）」 | 实测原文一致 | ✅ |
| 错误闭集 | C-16:212 只列既有码；§6 表本体零行改动；无新码 | `git diff` 仅新增 v1.5 补充句（`@@ -194,0 +212,2 @@`），§6 表未动 | ✅ |
| 红线 | C-16:108 六条：不自动重新授权/不自动重建 identity/撤销后不放行/不扩授权面/folder 排除/reset limitation | 实测原文一致 | ✅ |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | 5 个文件无改动；C15/C17/C06/C07 实算 sha 与 pin 一致；M2-C1 零 diff（232145 B，sha `701093b5…`） | 实测 | ✅ |
| 「三列」/`grant.created_at` 规范条款 0 命中 | C-16/FROZEN/矩阵/PREREQ/AUTO/EV 均 0 | 实测 0/0；carrier 仅 §6 的 r1/r2/r3/处置3/r4/r5 **历史复核记录**保留原字样（三列 4 处、`grant.created_at` 3 处），规范文本 0 | ✅ |
| 无新错误码/wire minor/schema/依赖 | C-16 §2.5 错误行与 §6 补充句只引用既有码；§0/§1 additive；无 schema/依赖 diff | 实测 | ✅ |

**接受的非阻断 P3（C-16 字节未改，不重开）**：R3-05（`C-16:103` ④四键未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 映射及「SQL 只匹配三身份键」）、R3-06（`C-16:106` 幂等句未加「无其他写入者介入」前提）、R3-10（`C-16:17` 未提 v1.5/§2.5；A 卡/L-S4-A 指称混用）。这些是 r5 已接受的非阻断项；本轮 C-16 仍为 `a7f57ebd…`，不构成回归。

**结论**：C-16 条款层未发现安全放宽或新授权入口；本轮所有变更都在文档/记录面，不是契约字节变更。**C-16 §10 ⑦ 的 independent byte-level 复核 approved（P0/P1=0）已满足**；冻结记录中的 `⏳` 状态由 DSH 在落 approved 结论时更新，不构成本复审的字节修改。

### D. 证据 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| EV 表逐文件 sha | 7 项 | carrier `833b3276…`、changed-lines `9ff9a852…`、check/check-taskpath `d1e251bc…`、pins `07c2b60c…`、other-17 `fee1af10…`、pre-post `57c1c2d9…` **全部实测匹配** | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `833b3276…`、同 9271 B | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B；三者按 CRLF 与 log **逐字节相等**（EXIT 均为 0；check 3 warnings） | ✅ |
| `pre-post.sha256` | pre=`ad25fb3c…` / post=`a7f57ebd…` | 178 B；`git cat-file blob HEAD:C-16` 实测 32577 B、sha `ad25fb3c…`；工作树 38912 B、sha `a7f57ebd…` | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 证据原始 15436 B（CRLF 81 行，sha `9ff9a852…`）；原生 diff 15355 B（LF）；`\r\n→\n` 后**逐字节相等**（归一化 15355 B，sha `74b94191a2f643ae00bbde198c4889f3aeeac9a9f81302b8cbc73a29e0979cae`） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；重跑原始输出与 `logs/pins.log` 逐字节相等 | ✅ |
| 其余 17 不变 | 17 项 `UNCHANGED`、`changed=0`、@HEAD | `other-17-pins.txt` 17 条 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD；C15/C17/C06/C07 实算 match | ✅ |
| 改动边界 | 仅 5 个文档 + 证据 | `git diff --name-only HEAD` 只有 C-16/FROZEN/矩阵/AUTO/PREREQ；`src/apps/tests/tools` 零 diff；`verification/FEA-09/**` 未被改写 | ✅ |

**证据注记（不影响 PASS）**：`logs/pins.log`、`logs/check*.log` 为 CRLF 存档；用 CRLF 拼接重跑输出逐字节相等。`changed-lines.diff` 原始文件为 CRLF 15436 B；归一化（LF）后为 15355 B，sha `74b94191…`，与原生 diff 逐字节一致。

## 2. r7 findings 逐条处置

| r7 ID | 级别 | r8 状态 | 依据（本报告） |
|---|---|---|---|
| **R7-N1** FROZEN 记录链停在 r6 pending | P2 | **CLOSED** | `FROZEN:38` 与 `FROZEN:110` 均已含 r7 `changes_requested` → 处置 → **r8 pending**；`carrier §6` 补 r7 行与「处置 7（本轮）」；`EV:3` 为完整链 `r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending`。四处一致。 |
| **R3-04** §2.E 未登记 §1B v1.4 行改写 | P3 | **CLOSED** | `carrier:37` 新增「§1B v1.4 行登记」：历史值保留、原明细（r1 计数/session/head）见 §8、历史 pin 未改、v1.5 行追加；旧「不改写」措辞已被 §6 重写移除。 |
| **R7-N2** `carrier` 反斜杠转义 | P3 | **CLOSED** | `carrier:60-74` 全部使用反引号；`\doc/reviews`/`\changes_requested` 实测 0 命中。 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **CLOSED（未回归）** | `carrier:42`（§3）有「契约就绪 ≠ 实现/产品可用」正文句；`carrier:20` 保留「单根探测异常 → false」；`carrier:55` §5⑥ 核对项保留。 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **ACCEPTED（未回归）** | C-16 字节保持 `a7f57ebd…`；`C-16:103` ④仍仅列四键、无映射/SQL 三键说明。按 r5 口径接受为非阻断。 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **ACCEPTED（未回归）** | C-16 字节未改；`C-16:106` 幂等句仍无「无并发写入者」前提。接受为非阻断。 |
| **R3-10** §0 版本面/A 卡指称 | P3 | **ACCEPTED（未回归）** | `C-16:17` 仍未提 v1.5/§2.5；`C-16:105`/`PREREQ:46`/`PREREQ:67` 的全名/A 卡/L-S4-A 仍混用。C-16 字节未改，接受为非阻断。 |
| R3-02/R3-03/R3-07（r4 已 CLOSED） | P2/P3 | **CLOSED（未回归）** | `C-16:212` 的 §6 映射、`C-16:35` 的 roots 每根/锁外/单根异常、FROZEN/载体状态链的 r4 结论均未回退；本轮无新反证。 |

**统计**：r7 正文 3 条（P2×1 + P3×2）全部 CLOSED；R3-09 CLOSED；R3-05/06/10 继续 ACCEPTED。按本轮口径 **P0=0 / P1=0 / P2=0 / P3=0**（非阻断观察见 §3）。

## 3. 非阻断观察（不计 finding）

1. **`FROZEN:110` 的 r4–r7 计数**：r1–r3 有 P0/P1/P2/P3 计数，r4–r7 只写 verdict；不影响链一致性，建议下次同构补齐。
2. **`carrier:37` 的「加注」措辞**：FROZEN §1B 的 v1.4 行实际文本为「（= v1.4 冻结字节；r1 changes_requested → 处置 → r2 approved，见 §8）」，是摘要改写；`carrier:37` 的「加注「历史行，见 §8」」是概括而非逐字引用。登记实质（历史 pin 未改、原明细见 §8）已具备，不阻断。
3. **`carrier:71`（处置 6）的历史表述**：其「§2.E 登记；…转义格式修正」实际是在 r7 之后的「处置 7」完成；r7 行已把这两项记为 finding、处置 7 已记录修复。属历史摘要措辞不精确，不改变链与最终字节。
4. **`carrier:42` 的排版**：AC-T5 正文句紧接 `carrier:41` 的列表项且无空行，部分渲染器会并入同一列表项；字面句仍在 §3。
5. **矩阵状态 vs 条件**：`MATRIX:37` 已标 `FROZEN v1.5`，条件列含「v1.5 独立 byte-level 复核 approved」；`FROZEN:50` 条件 7 仍 `⏳`。状态列不是结论、条件列才是 Gate；**不得**把矩阵状态/条件文字当作已批准事实。approved 结论落载体 §6 后由 DSH 更新冻结记录。
6. **r7 报告的复核快照**：r7 正文实测表基于 13:31 快照（carrier `4dd5389f…`、EV `2e8e72a8…`），未覆盖 13:48/13:50 的最终载体/EV；本 r8 已直接复核最终字节，r7 的结论在最终字节上已被修复。

## 4. 复核结论与处置建议

- **verdict：`approved`**（P0=0 / P1=0 / P2=0 / P3=0；非阻断观察见 §3）。
- **C-16 字节安全、pin 与证据均通过**：`a7f57ebd…` 未变；`verify_pins` 18/18；日志可复现；`changed-lines` 与原生 diff 一致；未发现安全放宽或新授权入口。
- **r7 findings 全部闭合**：R7-N1、R3-04、R7-N2 CLOSED；R3-09 CLOSED；R3-05/06/10 继续接受为非阻断。
- **DSH 后续（本报告不执行）**：
  1. 在载体 §6 **append-only** 追加 r8 `approved` 结论（含 session `fc11c286-8b80-4276-9d57-9b4b226b30d5`、reviewed_head `59ba5189f`、P0/P1=0）。
  2. 更新冻结记录：`FROZEN:50` 条件 7 → `✅`；`FROZEN:38` / `FROZEN:110` 的 `r8 pending` → approved 结论（按既有格式）。
  3. carrier 变化后**重算 EV 的 carrier sha**，重跑 `verify_pins`（应仍 18/18）与 `check.ps1`（默认 + `-TaskPath`），并重跑日志存档。
  4. 完成上述记录后提交/推送本 UNFREEZE；**不得**在 approved 结论落盘前提交或推送。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `fc11c286-8b80-4276-9d57-9b4b226b30d5`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r7 复核或任何相关实现；只读被审字节与背景只读材料（C-16、载体、冻结记录、矩阵、PREREQ/AUTO 卡、证据、只读源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/AUTO 卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r8.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--unified=0/--unified=2 HEAD`、`git hash-object`、`git cat-file blob/size`、`Get-FileHash -Algorithm SHA256`、.NET `SHA256` 字节哈希、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell/.NET UTF-8 字节/行尾/哈希/正则计数、PowerShell 重定向重跑日志与 blob 的逐字节比较。
- **代码只读锚点**：本轮为文档/记录一致性复审，未深入实现审计；C 项的安全语义判定基于 C-16 冻结字节、P0/P1 条款与 r4/r5 已记录的实现锚点（`library.py` 单点 SQL、`schema.py` 的 `source_locations`、C-17/M2-C1 既有码），并以「无代码 diff + pins 18/18」佐证；`ReattestSourceLocation`/`source.reattest` 在 `src/**`、`apps/**` 实测 0 命中。
- **并发事实**：复核期间工作树于 13:48:15–18、13:50:32 被外部更新（FROZEN/carrier/EV/日志）；本报告以 13:50:32 最终字节为准，最终快照后多次测量稳定。输入报告 `r7.md`（13:37:59）与 `r6.md`（13:41:13）亦被外部更新，均非被审 UNFREEZE 字节。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1–r7 报告仅作为被审输入与对照，不作为事实来源。
