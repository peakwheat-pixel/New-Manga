---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r6 窄面文档/记录一致性复审（C-16 字节保持 a7f57ebd…）
reviewer: fresh subagent（r6；独立上下文；未参与本 UNFREEZE 起草、r1–r5 复核或任何相关实现；只读）
session: ee3813ec-73ad-4d83-8666-130c9b1231ec
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立文档/记录一致性复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r5 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r6 窄面文档/记录一致性复审

> **结论先行：`changes_requested`，P0=0 / P1=0 / P2=1 / P3=2。**
>
> **r5 P1 已关闭**：`PREREQ:67`（I-2 动作）已改为 `registry_id/authorization_generation` 两列 + `last_verified_at` 保持当前行原值；全包规范条款一致，`三列`/`grant.created_at` 在当前规范文本 0 命中（仅载体 §6 的 r1/r2/r3 历史复核记录保留原字样）。**C-16 契约字节未改（`a7f57ebd…`），R3-01 属卡面/记录修正，不是契约字节回归。**
>
> **r5 P2 未关闭，且复核期间工作树被并发修改**：本报告主快照为 2026-11-07 13:31:52/54，之后 13:37 又发生一次外部修改（见 §0.1）。13:31 快照中，`carrier §6` 与 `EV:3` 已推进到「r1→…→r6 changes_requested → 处置 → **r7 pending**」，但 **`FROZEN:38/110` 仍停在「r1→…→r5 changes_requested → 处置 → r6 pending」**；13:37 快照中，FROZEN 已前进到 r8 pending，但 **carrier §6 无 r7 记录、FROZEN:110 跳过 r7**。两种快照下三份记录都不一致，记录链 P2 始终未闭合；这是记录问题，不是 C-16 字节问题。
>
> **r5 P3 部分关闭**：R3-08（AUTO 卡三处）已全部修好；R3-09 已关闭（`carrier:20` 补「单根探测异常 → false」；AC-T5 字面句已移到 `carrier:41` §3 正文结论）；**R3-04 仍 OPEN**（`carrier §2.E` 仍未登记 §1B v1.4 行改写，`carrier:60` 只写「历史行保留并加注（不改写其历史值）」，`carrier:65` 又声称「本轮修正」）。另有新 P3：`carrier:63-65` 的路径/verdict 被反斜杠转义（`\doc/reviews/…\`、`\changes_requested\`），疑为脚本写入遗留。R3-05/06/10 因 C-16 字节未改，继续按 r5 口径接受为非阻断 P3。
>
> **证据与 pin 全部通过**：C-16 sha256=`a7f57ebd…`（38912 B，LF 253 行，0 CRLF）= FROZEN pin = blob 内容 sha；`git hash-object`=`67c741d3…`；`verify_pins` 18/18；其余 17 不变；日志重跑逐字节复现；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字相等；EV 7 项 sha 全匹配（carrier 新 sha `4dd5389f…`）。**C-16 §10 ⑦ 的「independent byte-level 复核 approved」仍未满足；当前冻结包不能按 r6 approved 提交/推送。**

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无并发提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪载体、r1–r6、证据目录 8 文件；**本报告写入后新增 r6 报告 1 个未跟踪项**，其余不变 | `git status --porcelain=v1 -uall` |
| 并发改动注记 | 复核开始（约 13:22）时 carrier=`f1f9a32e…`（8316 B）、EV=`bedcb892…`（1051 B）；13:31:52/54 二者被外部修改为 carrier=`4dd5389f…`（8938 B）、EV=`2e8e72a8…`（1042 B）；13:37:14/16 又变为 FROZEN=`ac688fba…`（10168 B）、carrier=`7f2c3e50…`（8938 B）、EV=`77cd1160…`（1042 B），并新增 `r7.md`。本报告主表以 **13:31 快照** 为准，§0.1 补记 13:37 状态 | 文件 mtime + SHA-256 |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff；C-15/C-17/C-06/C-07/M2-C1 亦零 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`；重跑输出与 `logs/pins.log` **逐字节一致**（408 B，sha `07c2b60c…`） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B，sha `d1e251bc…`） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判文档/记录与契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256，13:31 最终快照）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF（与 r5 同字节） |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `829378973687dad75727e3bc558a90adee477fd550e6d2171d693ff5e61934d0` | 10133 B，LF 113 行（r5 为 `6034d229…`，本轮已改） |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行（与 r5 同字节） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `4dd5389f1459ac1f4036bbf35c8827997443a1158d36d2ba27914271be4b88e7` | 8938 B，CRLF 72 行（13:31 最终；早先为 `f1f9a32e…`） |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `4dd5389f1459ac1f4036bbf35c8827997443a1158d36d2ba27914271be4b88e7` | 8938 B；与 `doc/reviews` 载体同字节 |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `cf3266a0d3e2224e90fc3e83b47b7fd48a27a98ea0a12d69a4926bebb967c570` | 10578 B，CRLF 102 行（r5 为 `c940eadb…`，本轮已改） |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `92e29a94d40d695c08c411ee8dfa501bbf78f76f0d982b0658caca335ed5391a` | 8703 B，CRLF 98 行（r5 为 `e5bba4e3…`，本轮已改） |
| `verification/.../EV.md` | `2e8e72a8c2747f51d44a3268b51894724ef8e5ffa9d06b16d0cb3901c691be71` | 1042 B（13:31 最终；早先为 `bedcb892…`） |
| `verification/.../changed-lines.diff` | `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | 15436 B（CRLF 81 行；与 r5 同字节） |
| `verification/.../other-17-pins.txt` | `fee1af10007dde7c9523087d7bb804d1838ef4659d791fc76fc44e9d103c1f54` | 2747 B（与 r5 同字节） |
| `verification/.../pre-post.sha256` | `57c1c2d918207cd64f36d501908648dc54fbd54a6ba6421ed9957f564373ba61` | 178 B（与 r5 同字节） |
| `verification/.../logs/pins.log` | `07c2b60cab2953f31ff614c48a6f818744cacd2cf7b02ab15bcf1b194d929a95` | 408 B |
| `verification/.../logs/check.log`、`check-taskpath.log` | `d1e251bcef74ee9f91d57c031ca40d76b1aebd2633bc65f90ecb386d5a36737d` | 各 421 B |

## 0.1 复核后变更（13:37，post-snapshot）

本报告主表为 13:31 快照；完成主表后，工作树于 13:37:14/16/59 又发生一次外部修改。为使「最终字节」可核对，补记如下（这些后续字节不由本 r6 报告作完整复审，但其记录链状态仍需在下一轮处理）：

| 文件 | 13:37 最终 sha256 / 字节 | 关键变化 |
|---|---|---|
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `ac688fbab4276a85f333324afd0e8d75173ba517e983b2cd71eca440223ec19b` / 10168 B | `FROZEN:38` 改为「r1→…→r7 changes_requested → 处置 → **r8 pending**」；但 `FROZEN:110` 仍写「…r6 changes_requested → 处置 → **r8 pending**」，**跳过 r7** |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `7f2c3e50883725e784e0cd572875fdabbecea29152bead080365e53779bfcc72` / 8938 B | §6 仍只有 r1–r6；`carrier:65` 的 r6 行末改为「本轮修正；**r8 pending**」，**无 r7 记录**；§2.E 仍未登记 v1.4 行改写；`:63-65` 反斜杠转义仍在 |
| `verification/FEA-11-L-S4-B-PREREQ-1/EV.md` | `77cd11600ecac639a7107e9adc88cfb7c3b4bef5b3eaf88806c1b10b66f7bb16` / 1042 B | `EV:3` 改为「r1→…→r7 changes_requested → **r8 pending**」，与 FROZEN:38/EV 一致，但与 carrier §6 缺 r7 不一致 |
| `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r7.md` | 23652 B（13:37:59 新增） | r7 报告已产出，verdict=`changes_requested`（P0=0/P1=0/P2=1/P3=2），其正文基于 13:31 快照 |

**13:37 状态的结论**：r6 的 P2 没有被真正关闭，只是把滞后点从「FROZEN 未推进」变成「carrier §6 缺 r7、FROZEN §9 跳过 r7」；r7 报告已存在但 carrier §6 未登记 r7，FROZEN:110 也未登记 r7。**R5-N1 仍 OPEN（P2）**；R3-04（§2.E）与 R6-N1（carrier 转义）在 13:37 字节上仍未修。C-16/PREREQ/AUTO/矩阵自 13:22/13:31 起未变。

## 1. A–E 逐项判定

### A. R3-01 关闭：两列方案的全包传播 — **PASS**

| # | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| 1 | `C-16:97`（§2.5 用途） | 「`registry_id/authorization_generation` **两列**（`last_verified_at` 保持原值、不刷新审计时间）条件单行更新」 | **PASS** |
| 2 | `C-16:105`（§2.5 动作） | 只把两列更新为 `grant.registry_id`/`grant.generation`；`last_verified_at` 「UPDATE 前读取原值并原样回写」；不取 `now()`；复用 A 卡唯一 SQL | **PASS** |
| 3 | `C-16:253`（§10 变更记录） | 「只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值」 | **PASS** |
| 4 | `FROZEN:109`（§9 修订内容） | 「只写 registry/generation 两列、`last_verified_at` 保持原值」 | **PASS** |
| 5 | `carrier:11`（载体 §1 目标） | 「只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值」 | **PASS** |
| 6 | `carrier:26`（载体 §2.C 动作） | 两值取自 `grant.registry_id`/`grant.generation`；`last_verified_at` 原值；不取 `now()`；无 `grant.created_at` | **PASS** |
| 7 | `carrier:40`（载体 §3 安全） | 「只写 `registry_id/authorization_generation` 两列（`last_verified_at` 不变）」 | **PASS** |
| 8 | `PREREQ:46`（D-1） | 「只写 `source_locations` 的 registry_id/authorization_generation（`last_verified_at` 保持原值）」 | **PASS** |
| 9 | `PREREQ:47`（D-2） | 形状/前置义务，不含三列表述 | **PASS** |
| 10 | `PREREQ:49`（D-4） | 错误码为既有闭集；零字节清单已含 C-06 | **PASS** |
| 11 | `PREREQ:67`（I-2 动作） | 「仅把 Core `source_locations` 当前行的 `registry_id/authorization_generation` 原地更新为新条目（取自 grant 载荷；`last_verified_at` 保持当前行原值、不刷新审计时间…）」 | **PASS（r5 P1 关闭）** |
| 12 | `PREREQ:100`（ZCode 裁决记录） | 「只写 registry/generation 两列（last_verified_at 原值）」 | **PASS** |

**字面/字段枚举核对**：

| 文件 | 「三列」 | `grant.created_at` | 判定 |
|---|---|---|---|
| `C-16` | 0 | 0 | PASS |
| `FROZEN` | 0 | 0 | PASS |
| `MATRIX` | 0 | 0 | PASS |
| `PREREQ` | 0 | 0 | PASS |
| `AUTO` | 0 | 0 | PASS |
| `EV` | 0 | 0 | PASS |
| `carrier` | 仅 `:59`/`:61`/`:62` 的 r1/r2/r3 **历史复核记录** | 仅 `:59`/`:61` 的 r1/r2 历史记录 | PASS（规范文本 0 命中） |

> 行号说明：13:31 版 carrier 在 §3 插入 AC-T5 正文句（`:41`），并在 §6 增加 r4/r5/r6 记录，故历史记录行号较 r5 版整体后移；`三列`/`grant.created_at` 仍只出现在 r1/r2/r3 的历史复核描述中（`:59`/`:61`/`:62`），当前规范条款（§1/§2.C/§3/§9/§10）均为两列。

**结论**：r5 的 P1（`PREREQ:67` 三列/`last_verified_at` 无来源）已关闭。全包规范条款均为「两列 + `last_verified_at` 原值」，`grant.created_at` 不在任何写入值规范中；C-16 内部亦自洽（§2.5 用途/动作/§10 三处同口径，SET 子句物理上仍列出 `last_verified_at = ?`，由「原值回写」解释为语义两列，不构成矛盾）。

**非阻断观察（不计 finding）**：`PREREQ:67` 仍用「原地更新为新条目」而非逐字写 `grant.registry_id`/`grant.generation`；但紧随的「取自 grant 载荷」+「`last_verified_at` 保持当前行原值」已消除原缺陷，**不构成三列残留**。若追求与 `C-16:105` 完全同构，可在下轮顺手改成「更新为 live grant 载荷中的 `grant.registry_id`/`grant.generation`」；不影响本轮 R3-01 关闭判定。

### B. R5-N1 关闭：复核链推进 — **FAIL（P2，记录链未闭合）**

| 位置 | 当前字节 | 判定 |
|---|---|---|
| `FROZEN:38`（§1B v1.5 行） | 13:31：「r1→…→r5 changes_requested → 处置 → **r6 pending**」；13:37：「r1→…→r7 changes_requested → 处置 → **r8 pending**」 | **FAIL（两快照均与载体不一致）** |
| `FROZEN:110`（§9 复核栏） | 13:31：「…r4 → r5 changes_requested → 处置 → **r6 pending**」；13:37：「…r6 changes_requested → 处置 → **r8 pending**」（**跳过 r7**） | **FAIL（13:37 缺 r7）** |
| `carrier §6`（`carrier:59-65`） | 13:31：记 r1–r6，`carrier:65` 末句「… → 本轮修正；**r7 pending**」；13:37：仍只有 r1–r6，`carrier:65` 末句改为「… → 本轮修正；**r8 pending**」，**无 r7 行** | **13:31 PASS；13:37 FAIL（缺 r7）** |
| `EV:3` | 13:31：「review=r1→…→r6 changes_requested → **r7 pending**」；13:37：「review=r1→…→r7 changes_requested → **r8 pending**」 | **PASS（但 13:37 与 carrier §6 缺 r7 不一致）** |
| `FROZEN:50` 条件 7 | 状态 `⏳`；证据指向载体 §6 + `pins.log`；无 ✅、无预填 approved | **PASS** |
| 无预填 approved | `FROZEN:50` `⏳`；`FROZEN:110`「approved 后于本行追加结论」为条件句；`MATRIX:37` 的 approved 属条件列；`carrier`/`EV` 无 v1.5 approved 结论 | **PASS** |

**理由与后果**：当前三份记录不一致。13:31 快照：carrier/EV 已把 r6 记为 `changes_requested` 并推进到 r7 pending，但 FROZEN 仍停在 r5→r6 pending。13:37 快照（§0.1）：FROZEN 已前进到 r8 pending，但 carrier §6 没有 r7 记录，FROZEN:110 跳过 r7。**r5 P2 的具体缺陷（carrier 不记 r5/r6）在 13:31 已修，但记录链始终没有三处同轮一致**；13:31 的滞后文件是 FROZEN，13:37 的缺口是 carrier/FROZEN §9 的 r7。`FROZEN:50` 条件 7 的证据落点正是载体 §6，因此这不是纯美观问题：冻结记录/证据链与仓库事实不一致，属 **P2**。修复只需文本：三处统一到同一轮次（当前应至少把 carrier §6 补 r7、FROZEN:110 补 r7，并统一 r8 pending；或回退到 r7 pending），保持条件 7 `⏳`。同步后 `FROZEN` 仍无需改 C-16 字节。

**13:37 复核后变更**：`FROZEN` 改为 `ac688fba…`（10168 B）、carrier 改为 `7f2c3e50…`（8938 B）、EV 改为 `77cd1160…`（1042 B），并新增 `r7.md`（23652 B，13:37:59，verdict=`changes_requested`）。但 `carrier §6` 仍无 r7 行，`FROZEN:110` 仍跳过 r7；**R5-N1 未因这次修改而关闭**，只是把缺口从「FROZEN 未推进」改成「carrier/FROZEN §9 缺 r7」。

**非阻断观察（不计 finding）**：`FROZEN:110` 对 r4/r5/r6 只写 verdict、未写 P0/P1/P2/P3 计数；r1–r3 有计数。若追求同构，可补「r4 changes_requested（P0=0/P1=1/P2=0/P3=6）→ r5 changes_requested（P0=0/P1=1/P2=1/P3=3）→ r6 changes_requested（P0=0/P1=0/P2=1/P3=2）」。不影响 B 的失败原因（失败在 FROZEN 滞后）。

### C. P3 处置 — **R3-08/R3-09 CLOSED；R3-04 OPEN；新增 carrier 格式 P3**

| r5 项 | 子项 | 核对 | 状态 |
|---|---|---|---|
| **R3-04** | `FROZEN:37` v1.4 行措辞 | 现为「= v1.4 冻结字节；r1 changes_requested → 处置 → r2 approved，见 §8」；r5 所指「原 v1.4 行保留于 §8，不改写」已不在 FROZEN 中 | **PASS** |
| — | `carrier §2.E`（`carrier:33-36`） | 仍只写「pin → v1.5…；v1.5 重冻记录；历史 pin 保留」，**未登记 §1B v1.4 行改写**（删除 r1 计数/session/head，改为摘要） | **OPEN（P3）** |
| — | `carrier:60`（r1 处置第⑤点） | 已从「§1B v1.4 行保留不改写」改为「§1B v1.4 历史行保留并加注（不改写其历史值）」；但实际 `FROZEN:37` 的行文本被改写为摘要，不只是「加注」，措辞仍不完整 | **OPEN（P3，弱）** |
| — | `carrier:65`（r6 处置） | 写「R3-04 载体 §2.E 未登记… → 本轮修正」，但 `carrier §2.E` 至今仍未登记，**「本轮修正」与最终字节不符** | **OPEN（P3）** |
| **R3-08** | `AUTO:58` 三列 | 已改为「条件写 `registry_id/authorization_generation` 两列（`last_verified_at` 保持原值、不刷新审计时间）」 | **PASS** |
| — | `AUTO:72` `updated:false` | 已改为「重复调用 `updated:0` 且零写（字节不变）」 | **PASS** |
| — | `AUTO:69-78` AC 编号 | AC-LS4B-1…10 顺序排列；AC-LS4B-8 已移到 9/10 之前 | **PASS** |
| **R3-09** | `carrier:20` 单根探测异常 | 已写「缺失/不可读/身份不符/**单根探测异常 → false**；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`」 | **PASS** |
| — | AC-T5 字面句 | 已新增 `carrier:41` §3 正文结论：「**契约就绪 ≠ 实现/产品可用**：本载体只解除 C-16 v1.5 语义阻塞；L-S4-B 实现与 B2 投影均未交付。」 | **PASS（CLOSED）** |
| **R6-N1** | `carrier:63-65` 转义瑕疵 | r4/r5/r6 三条记录的路径与 verdict 使用 `\doc/reviews/…\`、`\changes_requested\`，应为反引号代码 span；疑为脚本写入遗留 | **OPEN（P3）** |

**补充核对**：

- `AUTO:58`/`:72`/`:69-78` 已无「三列」「updated:false」残留；AC 编号 1..10 连续，与 PREREQ AC-T1…T5、AC-LS4B-9/10 的引用不冲突。
- `carrier:20` 已同步 `C-16:35` 的「单根探测异常 → false」；`C-16:35` 的括注「探测异常不得抛出、不得使整命令失败」未逐字复制到载体，但载体「单根探测异常 → false」+「文件级损坏仍整命令 …」已表达同一 fail-closed 方向，**不单独计 finding**。
- `carrier:41` 的 AC-T5 字面句已落在 §3 正文结论，满足 r5 的「移到 §1/§3」建议；该行未加列表符号，渲染上可能并入上一条 bullet，属轻微排版问题，**不单独计 finding**。
- `carrier:63-65` 的反斜杠转义是本次 13:31 修改新引入的；它不影响事实内容，但会破坏 Markdown 代码 span 渲染，且三行均为复核链关键记录，记为 **P3**。

### D. C-16 字节 / 安全（不回归） — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（FROZEN:16、FROZEN:18、FROZEN §9:111、pre-post post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF 253 行，0 CRLF） | ✅ |
| C-16 blob 内容 sha256 | `a7f57ebd…`（FROZEN:18） | `git cat-file blob 67c741d3…` 输出 38912 B，sha256 `a7f57ebd…`；与工作树字节相同 | ✅ |
| `git hash-object` | `67c741d3…`（FROZEN:17） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| 两列/零写 | C-16:97/105 两列；103 末句「任一不满足 → typed 拒绝、零写」；107「拒绝/无匹配零写」 | 实测原文一致 | ✅ |
| 幂等/单调 | C-16:106 `updated:0` 且零写；同 registry 代次不倒退、跨 registry 允许 1 | 实测原文一致 | ✅ |
| 错误闭集 | C-16:212 只列既有码；§6 表本体零行改动 | `git diff` 仅新增 v1.5 补充句，无新码 | ✅ |
| 红线 | C-16:108 六条：不自动重新授权/不自动重建 identity/撤销后不放行/不扩授权面/folder 排除/reset limitation | 实测原文一致 | ✅ |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | 5 个文件 `git status` 干净；C15/C17/C06/C07 实算 sha 与 pin 一致；M2-C1 未改 | 实测 | ✅ |

**接受的非阻断 P3（C-16 字节未改，不重开）**：R3-05（`C-16:103` 四键未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 映射及「SQL 只匹配三身份键」）、R3-06（`C-16:106` 幂等句未加「无其他写入者介入」前提）、R3-10（`C-16:17` 未提 v1.5/§2.5；A 卡/L-S4-A 指称混用）。这些是 r5 已接受的非阻断项；本轮 C-16 仍为 `a7f57ebd…`，不构成回归。

**结论**：C-16 条款层未发现安全放宽或新授权入口；R3-01 的修复是卡面/记录修正，不是契约字节变更。C-16 §10 ⑦ 仍未满足，原因仅是记录链 P2（以及 P3 文字项），不是 C-16 字节本身。

### E. 证据 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| EV 表逐文件 sha | 7 项 | 13:31 快照：carrier `4dd5389f…`、changed-lines `9ff9a852…`、check/check-taskpath `d1e251bc…`、pins `07c2b60c…`、other-17 `fee1af10…`、pre-post `57c1c2d9…` 全部实测匹配；13:37 快照：carrier 更新为 `7f2c3e50…`，其余 6 项不变，EV 表同步匹配 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `4dd5389f…`、同 8938 B | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B；三者与 log **逐字节相等**（EXIT 均为 0；check 3 warnings） | ✅ |
| `pre-post.sha256` | pre=`ad25fb3c…` / post=`a7f57ebd…` | 178 B；HEAD blob 实测 32577 B，sha `ad25fb3c89bb…`；工作树 38912 B，sha `a7f57ebd…` | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 证据原始 15436 B（CRLF 81 行，sha `9ff9a852…`）；原生 diff 15355 B（LF）；`\r\n→\n` 后**逐字节相等**（归一化 15355 B，sha `74b94191a2f643ae00bbde198c4889f3aeeac9a9f81302b8cbc73a29e0979cae`） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；重跑原始输出与 `logs/pins.log` 逐字节相等 | ✅ |
| 其余 17 不变 | 17 项 `UNCHANGED`、`changed=0`、@HEAD | `other-17-pins.txt` 17 条 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| 独立抽查未重签 pin | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 全部实测 match | ✅ |
| 改动边界 | 仅 5 个文档 + 证据 | `git diff --name-only HEAD` 只有 C-16/FROZEN/矩阵/AUTO/PREREQ；`src/apps/tests/tools` 零 diff；`verification/FEA-09/**` 未被改写 | ✅ |

**证据注记（不影响 PASS）**：`changed-lines.diff` 原始文件为 CRLF 15436 B；归一化（LF）后为 15355 B，sha `74b94191…`。这与原生 diff 逐字节一致；r4/r5 报告已指出「原始文件 sha `9ff9a852…` vs 归一化 sha `74b94191…`」的标注差异，本轮复核再次确认为证据文件本身的 CRLF/LF 差异，不是伪造或陈旧。EV 的 carrier sha 已从 `f1f9a32e…` 更新为 `4dd5389f…`，与 13:31 最终 carrier 一致。

## 2. r5 findings 逐条处置

| r5 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **R3-01** 两列方案未传播 | P1 | **CLOSED** | `PREREQ:67` 已改两列 + `last_verified_at` 原值；C-16:97/105/253、FROZEN:109、carrier:11/26/40、PREREQ:46/47/49/67/100 一致；规范文本「三列」/`grant.created_at` 0 命中。 |
| **R5-N1** 复核链未推进 | P2 | **OPEN** | 13:31：carrier §6 `:59-65`、EV:3 已到 r1–r6 → r7 pending；FROZEN:38/110 仍 r1–r5 → r6 pending。13:37：FROZEN 提到 r8，但 carrier §6 仍无 r7，FROZEN:110 跳过 r7。两快照下三份记录都不一致，条件 7 证据指向 carrier §6。 |
| **R3-04** §1B v1.4 行改写未登记 | P3 | **OPEN** | FROZEN:37 措辞已修（无「保留不改写/原行保留」）；载体 §2.E 仍未登记该编辑；`carrier:60` 只写「保留并加注（不改写其历史值）」，`carrier:65` 却称「本轮修正」。 |
| **R3-08** AUTO 卡小疵 | P3 | **CLOSED** | `AUTO:58` 两列；`AUTO:72` `updated:0`；AC-LS4B-1…10 顺序正确；无「三列」/`updated:false` 残留。 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **CLOSED** | `carrier:20` 已补「单根探测异常 → false」；AC-T5 字面句已移到 `carrier:41` §3 正文结论；D-4 的 C-06 清单已在 r5 前补上。 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **ACCEPTED** | C-16 字节保持 `a7f57ebd…`；`C-16:103` ④仍仅列四键、无映射/SQL 三键说明。按 r5 口径接受为非阻断。 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **ACCEPTED** | C-16 字节未改；`C-16:106` 幂等句仍无「无并发写入者」前提。接受为非阻断。 |
| **R3-10** §0 版本面/A 卡指称 | P3 | **ACCEPTED** | C-16:17 仍未提 v1.5/§2.5；`C-16:105`/`PREREQ:46`/`PREREQ:67` 的「全名/A 卡/L-S4-A」仍混用。C-16 字节未改，接受为非阻断。 |
| R3-02/R3-03/R3-07（r4 已 CLOSED） | P2/P3 | **CLOSED（未回归）** | C-16:212 的 §6 映射、C-16:35 的 roots 每根/锁外/单根异常、FROZEN/载体状态链的 r4 结论均未回退；本轮无新反证。 |

**统计**：r5 正文 5 条（P1×1 + P2×1 + P3×3）；本轮 **CLOSED 3**（R3-01、R3-08、R3-09）、**OPEN 2**（R5-N1、R3-04）、**ACCEPTED 3**（R3-05/06/10），另有新 **R6-N1（P3，carrier 转义）**。按 r5 的 P1/P2/P3 口径折算本轮为 **P0=0 / P1=0 / P2=1 / P3=2**（R3-04 + R6-N1）。R5-N1 决定 verdict。

## 3. 新 findings 与处置建议

本轮没有发现 C-16 字节层的新问题；新 finding 是 r5 记录的未闭合部分与 13:31 载体修改引入的格式问题：

### R5-N1（P2，仍 OPEN）：记录链两快照均未三处一致

| 位置 | 当前字节 | 应有 |
|---|---|---|
| `FROZEN:38/110` | 13:31：仍「r1→…→r5 changes_requested → 处置 → **r6 pending**」；13:37：`:38` 写 r1→…→r7 → r8 pending，但 `:110` 写 r1→…→r6 → **r8 pending**（跳过 r7） | 三处统一到同一轮次；当前至少应把 `FROZEN:110` 补 r7，或回退 `:38` 到 r6/r7 一致状态 |
| `carrier §6`（`:59-65`） | 13:31：已到 r6 changes_requested → r7 pending；13:37：仍只有 r1–r6，r6 行改「r8 pending」，**无 r7** | 补 r7 行；若决定回退，三处统一 |
| `EV:3` | 13:31：r1→…→r6 changes_requested → r7 pending；13:37：r1→…→r7 changes_requested → r8 pending | 与 carrier/FROZEN 统一；carrier 字节变化后重算 EV 的 carrier sha |

**理由**：FROZEN 是冻结记录主体，carrier/EV 是复核证据；三者对同一 review 轮次的状态必须一致。13:31 快照中 FROZEN 落后（r6 pending vs carrier/EV r7 pending）；13:37 快照中 FROZEN 前进到 r8，但 carrier §6 没有 r7、FROZEN:110 跳过 r7。**两快照下 R5-N1 都成立**，只是缺口位置变了：13:31 在 FROZEN，13:37 在 carrier §6/FROZEN §9 的 r7 记录。`FROZEN:50` 条件 7 的证据落点（carrier §6）已经跑到 r8，FROZEN 却缺少 r7 的 §9 记录，读者无法判断哪份是最终状态。这是记录链 P2，不是 C-16 字节问题。

### R3-04（P3，仍 OPEN）：载体 §2.E 未登记 v1.4 行改写；`carrier:65` 的「本轮修正」不实

- `carrier §2.E`（`:33-36`）只登记 pin → v1.5、v1.5 重冻记录、历史 pin 保留；未写「§1B v1.4 行已由原长行改写为摘要（删除 r1 计数/session/head），原始信息见 §8」。
- `carrier:60` 的「§1B v1.4 历史行保留并加注（不改写其历史值）」比 r5 的「保留不改写」准确一些（至少限定为「历史值」），但仍未说明行文本被改写为摘要；`carrier:65` 的「本轮修正」与 §2.E 最终字节不符。
- FROZEN 侧的「原 v1.4 行保留于 §8，不改写」已删除，**FROZEN 措辞本身 PASS**；剩余问题在载体。

### R6-N1（P3，新）：`carrier:63-65` 反斜杠转义

- 13:31 版 carrier 的 r4/r5/r6 三条记录使用 `\doc/reviews/…\`、`\changes_requested\`，而不是反引号代码 span；Markdown 会渲染出多余反斜杠，且三行是复核链关键记录。
- 建议把 `\...\` 改回 `` `...` ``；不改变事实，不影响 C-16 字节或 pin，但应在 r7 前修掉，避免复核链记录继续带格式瑕疵。

### 非阻断观察（不计 finding）

1. **`PREREQ:67` 的「新条目」措辞**：已由「取自 grant 载荷；`last_verified_at` 保持当前行原值」限定，不再产生「三列/新条目时间」歧义；若追求与 `C-16:105` 逐字同构，可改为「更新为 live grant 载荷中的 `grant.registry_id`/`grant.generation`」。
2. **`FROZEN:110` 的 r4/r5/r6 计数**：r1–r3 有 P0/P1/P2/P3 计数，r4/r5/r6 只写 verdict；可补计数以保持同构，不影响 B 的失败点。
3. **`carrier:20` 的括注**：`C-16:35` 的「探测异常不得抛出、不得使整命令失败」未逐字复制到载体；载体「单根探测异常 → false」+「文件级损坏仍整命令 …」已表达同一方向，不单独计 finding。
4. **`carrier:41` 的列表格式**：AC-T5 正文句未加 bullet，紧跟 §3 第一条 bullet；渲染可能并入上一条，建议加空行或独立 bullet，不单独计 finding。
5. **矩阵状态 vs 条件**：`MATRIX:37` 已标 `FROZEN v1.5`，`FROZEN:50` 条件 7 仍 `⏳`；这与 v1.4/v1.5 的矩阵写法同构，状态列不是结论、条件列才是 Gate；**不得**把矩阵状态当作已批准事实。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=0 / P2=1 / P3=2 待修；R3-05/06/10 继续接受为非阻断）。
- **C-16 字节安全、pin 与证据均通过**：`a7f57ebd…` 未变；`verify_pins` 18/18；日志可复现；`changed-lines` 与原生 diff 一致；未发现安全放宽或新授权入口。
- **阻塞修复（文本修正，不需改 C-16 字节）**：
  1. **R5-N1**：三处统一到同一轮次。当前 13:37 字节下，至少给 `carrier §6` 补 r7 行、给 `FROZEN:110` 补 r7，并与 `FROZEN:38`/`EV:3` 的 r8 pending 对齐；或整体回退到 r7 pending。保持条件 7 `⏳`。
  2. **R3-04**：`carrier §2.E` 登记 §1B v1.4 行改写；修正 `carrier:60` 的「保留并加注」与 `carrier:65` 的「本轮修正」表述，使它们与最终字节一致。
- **P3 建议（同批修，避免下轮再开）**：
  - **R6-N1**：修复 `carrier:63-65` 的反斜杠转义，改回反引号代码 span。
- **证据与重冻**：
  - 若只改 FROZEN/carrier（及同步副本/EV），C-16 的 `a7f57ebd` pin、`changed-lines.diff`、pre-post、pins.log、other-17 均可保留；`verify_pins` 仍应 18/18，`check.ps1` 重跑。
  - carrier/EV 改动后须重算 EV 的 carrier sha；其余 6 项证据 sha 不变。
  - 修复后做 **r7** 独立 byte-level/记录复审；通过后由 DSH 在载体 §6 append-only 落 approved 结论并提交。**不得**在修复/复审通过前提交或推送本 UNFREEZE。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `ee3813ec-73ad-4d83-8666-130c9b1231ec`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r5 复核或任何相关实现；只读被审字节与背景只读材料（C-16、载体、冻结记录、矩阵、PREREQ/AUTO 卡、证据、只读源码锚点）。
- **并发改动**：复核期间工作树两次被外部修改：①2026-11-07 13:31:52/54，carrier 从 8316 B/`f1f9a32e…` 变为 8938 B/`4dd5389f…`，EV 从 1051 B/`bedcb892…` 变为 1042 B/`2e8e72a8…`；②13:37:14/16/59，FROZEN 变为 `ac688fba…`（10168 B），carrier 变为 `7f2c3e50…`（8938 B），EV 变为 `77cd1160…`（1042 B），并新增 `r7.md`（23652 B）。本报告主表以 13:31 快照为准，§0.1 补记 13:37 状态；两种快照下 R5-N1 均未闭合（13:31 滞后在 FROZEN，13:37 缺 r7 于 carrier/FROZEN §9），结论仍为 `changes_requested`。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/AUTO 卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r6.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--unified=0 HEAD`、`git hash-object`、`git cat-file blob/size`、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell/.NET UTF-8 字节/行尾/哈希/正则计数、PowerShell 重定向重跑日志与 blob。
- **代码只读锚点**：本轮为文档/记录一致性复审，未重新深入审计实现；D 项的安全语义判定基于 C-16 冻结字节、P0/P1 条款与 r4/r5 已记录的实现锚点（`library.py` 单点 SQL、`schema.py` 的 `source_locations`、C-17/M2-C1 既有码），并以「无代码 diff + pins 18/18」佐证。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1–r5 报告仅作为被审输入与对照，不作为事实来源。
