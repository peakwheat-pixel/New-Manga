---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r8 最终收口复审（C-16 字节保持 a7f57ebd…，记录链统一到 r8 pending）
reviewer: fresh subagent（r8；独立上下文；未参与本 UNFREEZE 起草、r1–r7 复核或任何相关实现；只读）
session: 72ec35e7-898c-42c9-8ae8-f1dee1d6cfa6
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立最终收口复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r7 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: approved
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r8 最终收口复审

> **结论先行：`approved`，P0=0 / P1=0 / P2=0 / P3=0**（另有 6 条非阻断观察，见 §3）。
>
> **A（记录链）PASS**：`FROZEN §1B:38`、`FROZEN §9:110`、`carrier §6:73-74`、`EV:3` 四处均已写入统一记录链 **`r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending`**；无 `r6 pending`/`r7 pending` 残留（唯一 `r6 pending` 命中是 `carrier:72` 对 r7 finding 的历史引述）；四文档未转义反斜杠 **0 命中**；`FROZEN:50` 条件 7 仍 `⏳`；无预填 v1.5 approved。
>
> **B（r7 P3 复核）PASS**：`carrier §2.E:37` 已登记 §1B v1.4 行改写（历史 pin `ad25fb3c…` 未改、原明细见 §8、v1.5 行追加）；`§3:42` 与 `§5:55⑥` 保留「契约就绪 ≠ 实现/产品可用」；`§2.B:20` 保留「单根探测异常 → false」；`§6:60-74` 全部改回反引号。
>
> **C（C-16 字节/安全）PASS**：sha256 = `a7f57ebdbd67…`（38912 B，LF 253 行，0 CRLF）= FROZEN pin = blob 内容 sha；`git hash-object` = `67c741d3…`；pre = `ad25fb3c…`（HEAD v1.4 blob，32577 B）；两列/零写/幂等/单调/错误闭集/红线均未回退；C-15/C-17/C-06/C-07/M2-C1 零字节。
>
> **D（证据）PASS**：EV 7/7 逐文件 sha 匹配；`carrier.md` 与 `doc/reviews` 载体同字节；`pins.log`（408 B）与 `check.log`/`check-taskpath.log`（各 421 B）重跑按 CRLF **逐字节复现**；`pre-post`、`changed-lines.diff` 与 C-16 一致；`verify_pins` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）**PASS (3 warnings)**。
>
> **r7 findings：R7-N1 CLOSED、R3-04 CLOSED、R7-N2 CLOSED、R3-09 CLOSED（未回归）；R3-05/R3-06/R3-10 ACCEPTED（未回归）；无 OPEN。**
>
> **C-16 §10 ⑦ 的「独立 byte-level 复核 approved（P0/P1=0）」已满足**；本 UNFREEZE 可进入「载体 §6 append-only 落 approved → 冻结记录条件 7 更新 → 提交/推送」流程。
>
> **必须披露的快照事实**：审查窗口内 `verification/…/EV.md` 于 `13:50:32.737` 被外部写入一次（998 B / sha `4254551c…` / review 字段为空 → 1074 B / sha `da3ad2a8…` / 写入完整链）。本报告以**该写入后的最终字节**为准，并在写入后重新实测全部 A–D 项；截至 `13:59:48` 无二次漂移。

## 0. 只读基线与复核字节

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（审查开始/结束同值，无新提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪（载体、r1–r8、证据目录 8 文件）；**本报告写入后**新增 r8 报告 1 项 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`git diff --name-only HEAD -- src apps tests tools` 为空；`verification/FEA-09/**` 未被改写） | 实测 |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`；重跑输出按 CRLF 与 `logs/pins.log` **逐字节一致**（408 B） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，只读轮次不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（`src/**`、`apps/**` 无 `ReattestSourceLocation`/`source.reattest` 实现；本轮只判文档/记录与冻结字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256，最终快照）**：

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

**快照与并发注记（不计 finding）**：复核窗口（13:48:28 起）内工作树于 `13:48:15–18`（FROZEN `7494fbb3…`、载体 `833b3276…`、日志重写）与 `13:50:32`（EV 首版 998 B → 最终 `da3ad2a8…`）发生两次外部写入，此后至 `13:59:48` 稳定；本报告以 `13:50:32` 最终字节为准，并在最终快照后重测 A–D。输入报告 `r6.md`（mtime `13:41:13`）与 `r7.md`（mtime `13:37:59`）也晚于其正文所述复核时点（r7 正文自述 13:31 快照），提示输入报告亦被外部更新；本报告只以被审 UNFREEZE 的最终字节为事实，不依赖输入报告的历史版本。

## 1. A–D 逐项判定

### A. 记录链一致性（原 P2） — **PASS**

| 位置 | 当前字节（摘要） | 判定 |
|---|---|---|
| `FROZEN:38`（§1B v1.5 行） | 「`a7f57ebd…`（= v1.5 冻结字节；**r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending**，见 §9）」 | **PASS** |
| `FROZEN:110`（§9 复核栏） | 「r1（P0=0/P1=2/P2=4/P3=5）→ r2（P0=0/P1=1/P2=4/P3=6）→ r3（P0=0/P1=1/P2=2/P3=7）→ r4 changes_requested → r5 changes_requested → r6 changes_requested → **r7 changes_requested** → 处置 → **r8 pending**（approved 后于本行追加结论）」 | **PASS** |
| `carrier:60-74`（§6） | r1 → 处置 1 → r2 → 处置 2 → r3 → 处置 3 → r4 → 处置 4 → r5 → 处置 5 → r6 → 处置 6 → **r7** → **处置 7（本轮）**；`carrier:73` 明写统一链，`carrier:74`「**r8 待复核**：`pending`（只读最终字节；C-16 字节保持 `a7f57ebd…` 不变）」 | **PASS** |
| `EV:3` | 「任务：C-16 v1.5 UNFREEZE；Owner=DSH；review=**r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending**。」 | **PASS** |
| 无过期轮次 | `r6 pending`：`FROZEN`=0、`EV`=0、`carrier`=1（仅 `:72` 历史引述「链停在 r6 pending」）；`r7 pending`：四处均 0 | **PASS** |
| 转义格式 | 四文档 `\` 命中 **0**；`carrier §6` 路径/verdict 统一反引号 | **PASS** |
| 条件 7 | `FROZEN:50` 状态 `⏳`；证据 = 载体 §6 + `verification/…/logs/pins.log`；无 ✅ | **PASS** |
| 无预填 approved | 全部 `approved` 命中均为历史结论（`FROZEN:6/37/44/48/49/66/73/86/98`）或条件句式（`FROZEN:50` 条件文本、`FROZEN:110`「approved 后于本行追加结论」、`carrier:56` 通过标准、`MATRIX:36/37` 条件列）；无 v1.5 approved 结论 | **PASS** |

**说明**：四处链的**轮次序列与 verdict 完全一致**；差异只在计数粒度（`§9` 给 r1–r3 计数、`§1B`/`EV` 用省略式、`carrier §6` 七轮全给计数），不构成链断裂（见 §3 观察 1）。

### B. r7 P3 复核（§2.E / §3 / §5 / §6 格式） — **PASS**

| 子项 | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| §2.E 登记 §1B v1.4 行改写 | `carrier:37` | 「**§1B v1.4 行登记**：FROZEN §1B 的 v1.4 行历史值保留并加注「历史行，见 §8」；原明细（r1 计数/session/head）见 §8，未改动历史 pin 值；v1.5 行追加。」 | **PASS**（引号措辞见观察 2） |
| 历史值保留 | `FROZEN:37` vs `FROZEN:98/112` | v1.4 行仍为 `ad25fb3c89bb…`；原明细（P1×2/P2×4/P3×9、session `e032ed9a-…`、reviewed_head `a0bafc89e`）见 `FROZEN:98`；v1.5 行追加于 `:38` | **PASS** |
| 「契约就绪 ≠ 实现/产品可用」 | `carrier:42`（§3） | 「**契约就绪 ≠ 实现/产品可用**：本载体只解除 C-16 v1.5 语义阻塞；L-S4-B 实现与 B2 投影均未交付。」 | **PASS** |
| 同上（§5⑥ 核对项） | `carrier:55` | ⑥载体/卡不夸大（契约就绪 ≠ 实现/产品可用） | **PASS** |
| 单根探测异常 | `carrier:20`（§2.B） | 「缺失/不可读/身份不符/**单根探测异常 → false**；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`」；与 `C-16:35` 一致 | **PASS** |
| §6 格式 | `carrier:60-74` | 无反斜杠转义；r1–r7 行为 `- **rN**（`…-rN.md`）：`changes_requested`（计数）——…` | **PASS** |

### C. C-16 字节 / 安全（不回归） — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（`FROZEN:16/18/38/111`、`pre-post` post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF 253 行，0 CRLF） | ✅ |
| C-16 blob 内容 sha256 | `a7f57ebd…`（`FROZEN:18`） | `git cat-file blob 67c741d3…` 输出 38912 B，sha256 `a7f57ebd…`；与工作树字节相同 | ✅ |
| `git hash-object` | `67c741d3…`（`FROZEN:17`） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| HEAD（v1.4）blob 内容 sha256（pre） | `ad25fb3c…`（`pre-post` pre、`FROZEN:37`） | HEAD blob `b9be0acf…`，32577 B，sha256 `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` | ✅ |
| 两列 | `C-16:97`/`105` 只写 `registry_id/authorization_generation`，`last_verified_at` 保持原值 | 原文一致（含「不刷新审计时间、不取 `now()`」） | ✅ |
| 零写 | `C-16:103` 末句「任一不满足 → typed 拒绝、**零写**」；`C-16:107`「拒绝/无匹配零写」 | 原文一致 | ✅ |
| 幂等/单调 | `C-16:106` 同 grant 重复 `updated:0` 且零写；同 registry 代次不倒退、跨 registry 允许 1 | 原文一致 | ✅ |
| 错误闭集 | `C-16:212` 只复用 §6 既有码；§6 表本体（`:189-208`）零行改动 | `git diff -U0` 仅新增 v1.5 补充两行（`@@ -194,0 +212,2 @@`） | ✅ |
| 红线 | `C-16:108`：不自动重新授权/不重建 identity/撤销后不放行/不扩授权面/folder 排除/`reset_registry` limitation | 原文一致 | ✅ |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | 5 个文件干净；C15/C17/C06/C07 实算 sha 与 pin 一致；M2-C1 零 diff | C15 `f9e376a0…`、C17 `aefa0fa5…`、C06 `99831a20…`、C07 `3fdb44e4…`；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 232145 B / `701093b5…` 无 diff | ✅ |
| 「三列」/`grant.created_at` 规范条款 0 命中 | C-16/FROZEN/MATRIX/PREREQ/AUTO/EV 均 0 | 规范文本 0；`carrier` 仅 §6 的 r1/r2/处置3/r4/r5（三列 4 行）与 r1/r2/处置3（`grant.created_at` 3 行）**历史复核记录**保留原字样 | ✅ |
| 无新错误码 / wire minor / schema / 依赖 | §2.5 与 §6 补充句只引用既有码；§0/§1 additive | 实测一致 | ✅ |

**接受的非阻断 P3（C-16 字节未改，不重开）**：R3-05（`C-16:103` ④四键未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 映射及「SQL 只匹配三身份键」）、R3-06（`C-16:106` 幂等句未加「无其他写入者介入」前提）、R3-10（`C-16:1` 标题仍「草案 v7，处置契约复核 r6」、`C-16:17` 版本面未提 v1.5/§2.5、A 卡/L-S4-A 指称混用）。这些是 r5 起接受的非阻断项；本轮 C-16 仍为 `a7f57ebd…`，不构成回归。

**结论**：C-16 条款层未发现安全放宽或新授权入口；本轮变更全部落在文档/记录面。C-16 §10 ⑦ 要求的「独立 byte-level 复核 approved（P0/P1=0）」由本报告满足；条件文本本身不改。

### D. 证据 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| EV 表逐文件 sha | 7 项 | carrier `833b3276…`、changed-lines `9ff9a852…`、check/check-taskpath `d1e251bc…`、pins `07c2b60c…`、other-17 `fee1af10…`、pre-post `57c1c2d9…` **全部实算匹配** | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `833b3276…`、同 9271 B，逐字节比较相等 | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B；按 CRLF 拼接后**逐字节相等**（EXIT 均为 0；check 3 warnings） | ✅ |
| `pre-post.sha256` | pre=`ad25fb3c…` / post=`a7f57ebd…` | 178 B；`git cat-file blob HEAD:C-16` 32577 B / `ad25fb3c…`；工作树 38912 B / `a7f57ebd…` | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 证据 15436 B（CRLF 81 行）；原生 diff 15355 B（LF）；`\r\n→\n` 后**逐字节相等**（15355 B，sha `74b94191a2f6…`） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；`logs/pins.log` 逐字节复现 | ✅ |
| 其余 17 不变 | 17 项 `UNCHANGED`、`changed=0`、@HEAD | `other-17-pins.txt` 17 条 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| 改动边界 | 仅 5 个文档 + 载体/报告/证据 | `git diff --name-only HEAD` = C-16/FROZEN/矩阵/AUTO/PREREQ；`src/apps/tests/tools` 零 diff；`verification/FEA-09/**` 干净 | ✅ |

**证据注记（不影响 PASS）**：`logs/*.log` 为 CRLF 存档；按 CRLF 拼接重跑输出逐字节相等（LF 拼接会少 19/6 字节）。`changed-lines.diff` 原始为 CRLF 15436 B；归一化（LF）15355 B、sha `74b94191…`，与原生 diff 逐字节一致。

## 2. r7 findings 逐条处置

| r7 ID | 级别 | r8 状态 | 依据（本报告） |
|---|---|---|---|
| **R7-N1** FROZEN §1B/§9 链停在 r6 pending | P2 | **CLOSED** | `FROZEN:38` 与 `FROZEN:110` 已到「r1→…→r7 changes_requested → 处置 → r8 pending」；`carrier:73-74`、`EV:3` 一致；`FROZEN:50` 条件 7 仍 `⏳`，未预填 approved |
| **R3-04** §2.E 未登记 §1B v1.4 行改写 | P3 | **CLOSED** | `carrier:37` 已登记「历史值保留 + 原明细（r1 计数/session/head）见 §8 + 历史 pin 未改 + v1.5 行追加」；旧「不改写」措辞已移除（`carrier:67` 改述为「加注为历史摘要」） |
| **R7-N2** carrier §6 反斜杠转义 | P3 | **CLOSED** | `carrier:60-74` 全文无反斜杠；r1–r7 行统一反引号格式 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **CLOSED（未回归）** | `carrier:42` 保留正文句；`carrier:20` 保留「单根探测异常 → false」；`carrier:55` ⑤⑥ 核对项保留 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **ACCEPTED（未回归）** | C-16 字节保持 `a7f57ebd…`；`C-16:103` ④仍仅列四键，无映射/SQL 三键说明 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **ACCEPTED（未回归）** | C-16 字节未改；`C-16:106` 幂等句仍无「无并发写入者」前提 |
| **R3-10** §0 版本面 / A 卡指称 | P3 | **ACCEPTED（未回归）** | `C-16:1`/`C-16:17` 未提 v1.5；`C-16:253` 仍用「A 卡」。C-16 字节未改，接受为非阻断 |
| R5-N1（r6 主 finding，链停 r4） | P2 | **CLOSED（未回归）** | `carrier:60-74` 已含 r1–r7 全链 + 处置 1–7 + r8 pending；`EV:3` 一致 |
| R3-02/R3-03/R3-07（r4 已 CLOSED） | P2/P3 | **CLOSED（未回归）** | `C-16:212` §6 映射、`C-16:35` roots 每根/锁外/单根异常、FROZEN/载体状态链均未回退；本轮无新反证 |

**统计**：r7 正文 3 条（P2×1 + P3×2）**全部 CLOSED**；R3-09/R5-N1 CLOSED（未回归）；R3-05/06/10 继续 ACCEPTED；**无 OPEN**。折算 **P0=0 / P1=0 / P2=0 / P3=0**（非阻断观察见 §3）。

## 3. 非阻断观察（不计 finding）

1. **`FROZEN:110` 的计数粒度**：r1–r3 有 P0/P1/P2/P3 计数，r4–r7 只写 verdict；`carrier §6` 七轮全有计数。链内容一致，仅格式不对称，建议后续顺带补齐，不阻断。
2. **`carrier:37` 的引号措辞**：FROZEN §1B 的 v1.4 行实际文本为「（= v1.4 冻结字节；r1 changes_requested → 处置 → r2 approved，见 §8）」，是摘要改写；`carrier:37` 用「加注「历史行，见 §8」」概括而非逐字引用。登记实质（历史 pin 未改、原明细见 §8）已具备；若求字面精确，可改为「加注为历史摘要并指向 §8」。
3. **`carrier:71`（处置 6）的历史表述**：「§2.E 登记；…转义格式修正」实际由「处置 7」完成（r7 报告先指出未完成）。属历史摘要措辞不精确，不改变链与最终字节。
4. **`carrier:41-42` 无空行**：§3 的加粗正文句紧接列表项（懒续行），部分渲染器会并入同一 bullet；字面句仍在 §3，语义不受影响。
5. **矩阵状态 ≠ 结论**：`MATRIX:37` 已标 `FROZEN v1.5` 且条件列写「①v1.5 独立 byte-level 复核 approved（载体…）」，而 `FROZEN:50` 条件 7 仍 `⏳`。**不得**把矩阵状态/条件文字当作已批准事实引用。
6. **行尾 pin 可复算性（仓库既有状况，非本轮引入）**：`core.autocrlf=true` 且 `doc/plan/*.md` 无 `eol=lf` 属性；本树 C-16/FROZEN 为 LF（`git ls-files --eol` = `w/lf`），pin 与 **Git blob 内容**一致（任意 clone 可用 `git cat-file` 复算），但 fresh checkout 会把 `doc/plan` 文本转 CRLF，届时 `verify_pins` 的「工作树字节」口径会失配。r1–r7 同口径；`.gitattributes` 不在本卡 `allowed_paths`，本轮仅记录、不处置。

## 4. 复核结论与处置建议

- **verdict：`approved`**（P0=0 / P1=0 / P2=0 / P3=0；非阻断观察见 §3；R3-05/06/10 继续接受为非阻断）。
- **A–D 全 PASS**：统一记录链已落到 FROZEN §1B/§9、carrier §6、EV 四处；条件 7 仍 `⏳` 且无预填 approved；C-16 字节 `a7f57ebd…` 与安全语义未回退；证据 7/7 + 18/18 + 日志逐字节可复现。
- **C-16 §10 ⑦ 已可满足**：本报告即独立 byte-level 复核（P0=0/P1=0）。条件 7 的 ✅ 与 §9 / carrier §6 的 approved 结论由 DSH 在**本报告落盘后**追加，不得回填到本报告之前的时间点。
- **DSH 收口步骤（建议顺序，本报告不执行）**：
  1. `FROZEN:50` 条件 7 → `✅`（证据指向本报告 + 载体 §6 + `logs/pins.log`）；`FROZEN:110` 追加「**r8 approved**（P0=0/P1=0/P2=0/P3=0；session `72ec35e7…`；reviewed_head `59ba5189f`）」。
  2. `carrier §6` **append-only** 追加 r8 approved 行（只增不改），并同步 `verification/…/carrier.md` 副本。
  3. `EV:3` 链推进到「… → r8 approved」；因 carrier 变更，重算 EV 的 carrier sha，并重跑 `check.ps1`（默认 + `-TaskPath`）重写 `logs/check*.log`；`pins.log`/`other-17`/`pre-post`/`changed-lines` 不变，C-16 pin 不受影响。
  4. 不再修改 C-16/矩阵/AUTO/PREREQ 卡（避免无谓重算）；§3 观察项留作后续文档整洁项。
  5. 提交 UNFREEZE（5 个 tracked 文档 + 载体 + r1–r8 + 证据目录）并由 DSH push。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `72ec35e7-898c-42c9-8ae8-f1dee1d6cfa6`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r7 复核或任何相关实现；只读被审字节与背景只读材料（C-16、载体、冻结记录、矩阵、PREREQ/AUTO 卡、证据、只读源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/AUTO 卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r8.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **快照事实**：复核窗口内 `verification/…/EV.md` 于 `13:50:32.737` 被外部写入一次（998 B → 1074 B；sha `4254551c…` → `da3ad2a8…`），与「本轮不再修改工作树」的前提不符。本报告不据此推定任何一方意图，只记录实测；全部 A–D 项在写入后重测，结论以最终字节为准。另：复核窗口内同路径已存在一份并发 r8 报告（不同 session，`13:49:45` 创建、`13:57:09` 最后写入，verdict 与本报告一致为 approved）；本报告按本任务指令写入该路径，内容为本人独立复核结果。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--unified=0/--unified=2 HEAD`、`git hash-object`、`git cat-file blob/size`、`git ls-files --eol`、`git config --get core.autocrlf`、`Get-FileHash -Algorithm SHA256`、.NET `SHA256` 字节哈希、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell/.NET UTF-8 字节/行尾/哈希/正则计数、重跑日志与 blob 的逐字节比较。
- **代码只读锚点**：本轮为文档/记录一致性复审，未重新深入审计实现；C 项的安全语义判定基于 C-16 冻结字节、P0/P1 条款与 r4/r5 已记录的实现锚点（`library.py` 单点 SQL、`schema.py` 的 `source_locations`、C-17/M2-C1 既有码），并以「无代码 diff + pins 18/18」佐证；`ReattestSourceLocation`/`source.reattest` 在 `src/**`、`apps/**` 实测 0 命中。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1–r7 报告仅作为被审输入与对照，不作为事实来源。
