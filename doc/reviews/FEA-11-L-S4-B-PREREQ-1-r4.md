---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r4 窄面 byte-level 复审（source.reattest/1 + ReattestSourceLocation 条件写 + roots_available）
reviewer: fresh subagent（r4；独立上下文；未参与本 UNFREEZE 起草、r1/r2/r3 复核或任何相关实现；只读）
session: 94407c8e-f283-48b2-8dc5-91579bc48e3a
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 byte-level 契约复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1/r2/r3 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r4 窄面 byte-level 复审

> **结论先行：`changes_requested`，P0=0 / P1=1 / P2=0 / P3=6。**
>
> **r3 的 P2 已关闭**：FROZEN §1B/§9 的复核链已补成 `r1 changes_requested → r2 changes_requested → r3 changes_requested → 处置 → r4 pending`（R3-02）；C-16 §6 v1.5 补充已把 closed-shape 归 `INVALID_REQUEST`、host-only/session 归既有守卫码（R3-03）。
>
> **R3-01 仍未闭合（P1）**：冻结包 8 处中 5 处已改为“两列 + `last_verified_at` 原值”，但 **FROZEN §9:110 同时保留“只写 registry/generation 两列”和“只写三列、复用 A 卡唯一 SQL”**；**PREREQ I-2:67 仍写 `registry_id/authorization_generation/last_verified_at` 三列并“原地更新为新条目”**；**PREREQ ZCode 记录:100 仍写“只写三列”**。PREREQ I-2 是 L-S4-B 实现卡的直接输入，照此实现仍会得到“`last_verified_at` 无值可取/列集合与冻结动作相反”的阻断。
>
> `grant.created_at` 在规范条款（C-16 §2.5 用途/动作/§10、FROZEN §9、载体 §1/§2.C/§3、PREREQ I-2/D-2/D-4）中 **0 命中**；载体 §6 的 4 处出现是 r1/r2 历史复核记录，不是写入值来源。C-16 自身未发现“三列”或 `grant.created_at` 的自相矛盾。
>
> 因此 C-16 §10 ⑦ 的“独立 byte-level 复核 approved（P0/P1=0）”**未满足**；当前冻结包不能按 r4 approved 提交/推送。FROZEN §2 第 7 行 `⏳`、§9 `r4 pending`、载体 §6 `r4 pending` 必须保留；修复后走 r5（或 DSH 裁定的等价独立复审）。

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无并发提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 未跟踪载体、r1/r2/r3、证据目录 8 文件；**本报告写入后新增 r4 报告 1 个未跟踪项**，其余不变 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff；C-15/C-17/C-06/C-07/M2-C1 亦零 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `a7f57ebdbd67`、C15 `f9e376a0ed4c`、C17 `aefa0fa5b17e` | 实测；与 `logs/pins.log` **逐字节一致**（408 B） |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节一致**（各 421 B） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `46349ea067cc1f6af5c1e5b5e1534ee9312db258d206f1a70d891030ba053bf0` | 10205 B，LF |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行（与 r3 同字节） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `fa52cff663167f672f28c31068fb69b5de439f27596c1a5038dea759a965933a` | 7956 B，CRLF 68 行 |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `fa52cff663167f672f28c31068fb69b5de439f27596c1a5038dea759a965933a` | 7956 B；与 `doc/reviews` 载体同字节 |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `9f764f5e1253729a83e8ef0e637b3640ec27dbebb59e7e5f341f836610ddbfaa` | 10456 B |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `e5bba4e3fd9de49fdf1164b8e50e5db9d23a62203a3185b7369d2c9b3178fdad` | 8681 B（与 r3 同字节，**P3 未改**） |
| `verification/.../EV.md` | `7b67bfee8bc2884a5cb8c8f37d5cab9b5d8d3bdf6bd577c0483f6e1328d5fa1e` | 1041 B |
| `verification/.../changed-lines.diff` | `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | 15436 B（CRLF） |
| `verification/.../other-17-pins.txt` | `fee1af10007dde7c9523087d7bb804d1838ef4659d791fc76fc44e9d103c1f54` | 2747 B |
| `verification/.../pre-post.sha256` | `57c1c2d918207cd64f36d501908648dc54fbd54a6ba6421ed9957f564373ba61` | 178 B |
| `verification/.../logs/pins.log` | `07c2b60cab2953f31ff614c48a6f818744cacd2cf7b02ab15bcf1b194d929a95` | 408 B |
| `verification/.../logs/check.log`、`check-taskpath.log` | `d1e251bcef74ee9f91d57c031ca40d76b1aebd2633bc65f90ecb386d5a36737d` | 各 421 B |

**pin / 证据实测**：

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `a7f57ebd…`（FROZEN:16、FROZEN:18、FROZEN §9:112、pre-post post） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，LF，0 CRLF） | ✅ |
| `git hash-object` | `67c741d3…`（FROZEN:17） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| HEAD v1.4 blob sha256（pre） | `ad25fb3c…`（pre-post pre、FROZEN §1B:37） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc`（32577 B） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0；重跑原始输出与 `logs/pins.log` 逐字节相等 | ✅ |
| 独立抽查 4 个未重签 pin（文件实算） | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 全部 match | ✅ |
| `other-17-pins.txt` | 17 项、`changed=0`、@HEAD | 17 行 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | 原生 diff 15355 B（LF）/ 证据 15436 B（CRLF 81 行）；`\r\n→\n` 后逐字节相等，归一化 sha256 `9ff9a852dccbe37c0c96947d4b66b23bd1cb87b1d51c0a73244801dc71ec317c` | ✅ |
| EV 表逐文件 sha | 7 项 | carrier `fa52cff6`、changed-lines `9ff9a852`、check/check-taskpath `d1e251bc`、pins `07c2b60c`、other-17 `fee1af10`、pre-post `57c1c2d9` 全部实测匹配 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `fa52cff6…`、同 7956 B | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B，三者用 `cmd` 重定向后与 log **逐字节相等** | ✅ |

## 1. A–G 逐项判定

### A. R3-01 关闭：两列方案的全包传播 — **FAIL（P1；5 处已修、1 处半修、2 处未修）**

| # | 位置 | 当前字节 | 判定 |
|---|---|---|---|
| 1 | `C-16:97`（§2.5 用途） | “`registry_id/authorization_generation` **两列**（`last_verified_at` 保持原值、不刷新审计时间）条件单行更新” | **PASS** |
| 2 | `C-16:105`（§2.5 动作） | 只把两列更新为 `grant.registry_id`/`grant.generation`；`last_verified_at` “UPDATE 前读取原值并原样回写”；“不取 `now()`、不做时钟推断”；复用 A 卡唯一 SQL | **PASS** |
| 3 | `C-16:253`（§10 变更记录） | “只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值” | **PASS** |
| 4 | `FROZEN:110`（§9 修订内容） | 前半句“只写 registry/generation 两列、`last_verified_at` 保持原值”，**后半句仍写“只写三列、复用 A 卡唯一 SQL”** | **FAIL（半修）** |
| 5 | `carrier:11`（载体 §1 目标） | “只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值” | **PASS** |
| 6 | `carrier:26`（载体 §2.C 动作） | 两值取自 `grant.registry_id`/`grant.generation`；`last_verified_at` 原值；不取 `now()`；**`grant.created_at` 已删除** | **PASS** |
| 7 | `carrier:40`（载体 §3 安全） | “只写 `registry_id/authorization_generation` 两列（`last_verified_at` 不变）” | **PASS** |
| 8 | `PREREQ:46`（D-1） | “只写 `source_locations` 的 registry_id/authorization_generation（`last_verified_at` 保持原值）” | **PASS** |
| 9 | `PREREQ:47`（D-2） | 写形状/前置义务，不含三列表述 | **PASS** |
| 10 | `PREREQ:49`（D-4） | 零字节清单已含 C-06；错误码为既有闭集 | **PASS** |
| 11 | `PREREQ:67`（I-2 动作） | “`registry_id/authorization_generation/last_verified_at` 原地更新为新条目” | **FAIL** |
| 12 | `PREREQ:100`（ZCode 裁决记录） | 仍写“只写三列” | **FAIL** |

- **计数口径**：上表第 2 行（C-16:105）与第 8–10 行（D-1/D-2/D-4）是补充核对，不计入 r3 的 8 处；按 r3 的 8 处计，5 处已修、1 处半修、2 处未修。
- **`grant.created_at` 命中**：规范条款 0 命中；仅载体 §6:58/60 与 `doc/reviews` 载体的对称历史记录各 2 处（共 4 处）提到该字段，作为 r1/r2 缺陷历史，不是值来源。**不计为写入值缺陷。**
- **C-16 内部自洽**：C-16 全文无“只写三列”，无 `grant.created_at`；`§2.5 用途/动作/§10` 三处均为两列 + 原值；`C-16:105` 对单点 SQL 的两个守卫谓词 `(registry_id <> ? OR authorization_generation <= ?)` 与相等分支谓词的描述与 `library.py:2324-2339` 的 WHERE 一致（SET 子句物理上仍列出 `last_verified_at = ?`，由“原值回写”解释为语义两列，**不构成自相矛盾**）。**PASS。**
- **包级结论**：FROZEN §9 与 PREREQ I-2 都在任务 A 明确列出的核对面内；PREREQ I-2 是 L-S4-B 实现卡直接输入。故 **R3-01 仍 OPEN，P1**。

### B. R3-02 关闭：FROZEN §1B/§9 与载体 §6 复核状态 — **PASS**

| 子项 | 判定 | 证据 |
|---|---|---|
| FROZEN §1B v1.5 行 | **PASS** | `FROZEN:39`：“`a7f57ebd…`（= v1.5 冻结字节；r1→r2→r3 changes_requested → 处置 → r4 pending，见 §9）” |
| FROZEN §9 独立复核行 | **PASS** | `FROZEN:111`：r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5）→ r2 `changes_requested`（P0=0/P1=1/P2=4/P3=6）→ r3 `changes_requested`（P0=0/P1=1/P2=2/P3=7）→ 处置 → **r4 pending**（approved 后于本行追加结论） |
| 载体 §6 | **PASS** | `carrier:61` 记 r3 结果与“本轮已传播修正；**r4 pending**”；与 FROZEN 链一致 |
| EV | **PASS** | `EV:3`：“review=r1→r2→r3 changes_requested → r4 pending” |
| 条件 7 / 无预填 approved | **PASS** | `FROZEN:51` 第 7 行状态 `⏳`；无 `✅`/`approved` 结论；`FROZEN:111` 的“approved 后于本行追加结论”是条件句。 |

**残余**：`FROZEN:38` 的“原 v1.4 行保留于 §8，不改写”仍不准确（见 D/R3-04），但不影响“复核状态链”本身；B 项 PASS。

### C. R3-03 关闭：§6 v1.5 补充的 host-only/session 映射 — **PASS**

| 子项 | 判定 | 证据 |
|---|---|---|
| `INVALID_REQUEST` 仅用于 closed-shape | **PASS** | `C-16:212`：“closed-shape 错误 `INVALID_REQUEST`、host-only/session 守卫沿用既有码、身份/条目不符 `SOURCE_ACCESS_DENIED`、grant 状态 `SOURCE_GRANT_REVOKED`/`SOURCE_GRANT_EXPIRED`、registry 状态 `SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`，零写。” |
| host-only/session 归既有守卫码 | **PASS** | `C-16:103` ①“application 面拒绝，沿用既有 host-only/session 守卫错误码，不新增码”；`C-16:107` 同口径 |
| 与 §2.4 ① / C-17 / Core 一致 | **PASS** | `C-16:89`（§2.4 ①）列 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`；`C-17:359-361` 为既有 M2-C1 §5.7 码；`core_service.py:1442/1444/1453/6259` 实测同码 |

**非阻断观察**：`C-16:107` 的“复用 §6 既有闭集——host-only/session 守卫沿用既有码”在字面上仍可被读成“§6 表包含 HOST_* 码”（实际 §6 表不含）。建议改为“既有错误码（§6 + M2-C1 host-control 码）”，但 `:212` 已明确分离，本轮不据此阻断。

### D. P3 处置 — **2 项 CLOSED / 1 项 PARTIAL / 3 项 OPEN**

| r3 P3 | 核对项 | 状态 | 证据 |
|---|---|---|---|
| **R3-04** | §1B 历史行措辞 | **OPEN** | `FROZEN:38` 仍写“原 v1.4 行保留于 §8，不改写”；但 `git diff HEAD` 显示 `FROZEN:37` 已被改写（删 r1 计数/session/head，改成“r1 changes_requested → 处置 → r2 approved，见 §8”）；`§8` 是 v1.4 UNFREEZE 记录，不是原 §1B 行。载体 §2.E 未登记该编辑，`carrier:59` 仍称“§1B v1.4 行保留不改写”。 |
| **R3-05** | `size_bytes` 四键落点 | **PARTIAL/OPEN** | `C-16:103` ④已列四键 `content_digest/volume_serial/file_id/size_bytes`，但未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 的映射，也未写“单点 SQL 的 WHERE 只匹配三身份键，`size_bytes` 由 handler 在调用前比对”。实测 `library.py:2327-2331` 的 WHERE 确无 `size_bytes`；`schema.py` 的 `source_locations` UNIQUE 也仅三键。 |
| **R3-06** | `updated` 前提/并发/无匹配 | **OPEN** | `C-16:106` 仍写“同 grant 重复调用 → `updated:0` 且零写（幂等）”，未加“无其他写入者介入”前提；SQL 第三谓词 `(… OR last_verified_at IS NOT ?)` 在读取原值后、UPDATE 前被并发刷新时可为真 → `rowcount=1` 并把时间戳写回旧值。无匹配/代次回退的返回也未逐项写死（虽可由 §2.5 ④/零写推出）。 |
| **R3-07** | roots 每根一次/不缓存/锁外 | **CLOSED** | `C-16:35` 已写“每根至多探测一次、不跨调用缓存、探测在快照后锁外进行；单根探测异常为 `false`（探测异常不得抛出、不得使整命令失败）”。 |
| **R3-08** | L-S4-B AC 编号/`updated:false`/三列 | **OPEN（3/3）** | `AUTO:69-78` 的 AC 顺序仍为 1..7、9、10、8；`AUTO:72` 仍写“重复调用 `updated:false`”（合同为 `updated: 0|1`）；`AUTO:58` 仍写“条件写 `registry_id/authorization_generation/last_verified_at`（…`last_verified_at` 保持原值）”，字面仍是三列。 |
| **R3-09** | D-4 补 C-06 / AC-T5 字面句 / 载体 §2.B | **PARTIAL（1/3）** | D-4 已补 C-06（`PREREQ:49` 含 `C-15/C-17/C-06/C-07/M2-C1`）；但 AC-T5 的“契约就绪 ≠ 实现/产品可用”仍只出现在载体 §5 的核对项（`carrier:53` ⑥），未作为结论句出现在 §1/§3；`carrier:20`（§2.B）仍只写“缺失/不可读/身份不符 → false”，未同步 C-16:35 的“单根探测异常 → false、不得抛出”。 |

补充：D 项未列但仍在 r3 P3 清单内的 **R3-10**（§0 版本面/A 卡指称）仍 OPEN：`C-16:17` 仍写“`source-access-wire/1.3`（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…）”，未提 v1.5/§2.5；`C-16:105` 用全名、`PREREQ:46` 用“A 卡”、`PREREQ:67` 用“L-S4-A”，指称仍混用。

### E. 安全语义（不回归） — **PASS**

| 子项 | 判定 | 证据 |
|---|---|---|
| 请求恰 2 键；无路径/`registry_id`/`generation` | **PASS** | `C-16:100` 仅 `{"source_id","grant_id"}`；`C-16:102` 明写无 command/scope/路径/registry_id/generation。 |
| 拒绝/无匹配零写 | **PASS** | `C-16:103` 末句“任一不满足 → typed 拒绝、**零写**”；`C-16:107` “拒绝/无匹配零写”。 |
| 只写两列；`last_verified_at` 不变 | **PASS（合同动作）** | `C-16:105` 只改 `registry_id/authorization_generation`，`last_verified_at` 原值回写；复用 `library.py:2324-2339` 单点 SQL（SET 含第三列但写原值；无第二份 SQL，`commit_source_location_auth_refresh:2341-2353` 为独立写单元）。 |
| 不改行数/`source_id`/digest/`is_current`/binding | **PASS** | `C-16:105` 明写；SQL `UPDATE … WHERE … is_current = 1`，不写 `is_current`，不 INSERT；`page_bindings` 不在 SQL 内。 |
| 错误码闭集无新增 | **PASS** | `C-16:189-208` 表本体零行改动；`C-16:212` 只列既有码；host-only/session 为 M2-C1/C-17 既有码。 |
| C-15/C-17/C-06/C-07/M2-C1 零字节 | **PASS** | `git diff --name-only HEAD` 仅 5 个文档；`git status -uall` 无这些文件；`verify_pins` 18/18，C15/C17/C06/C07 实算匹配。 |
| 红线：不自动重新授权/不重建 identity/撤销后不放行/不扩面/folder 排除/reset limitation | **PASS** | `C-16:108` 六条齐备；`C-16:97` 明写“不是恢复动作、不是授权决定”；`C-16:103` ③要求 grant live/未撤销；`C-16:104` Host 侧 folder 排除；`C-16:108` reset 后无旧条目可桥接。 |
| Host/Core 义务分离 | **PASS** | `C-16:103` 只列 Core 边界四项；`C-16:104` 独立成“Host 侧前置义务（本命令不校验、不依赖）”，含唯一 live、恰 1 根、路径 normalize、`live.CreatedAt > old.RevokedAt`、非 folder、每轮一次；Core `source_locations` 无 path 列（`schema.py` 实测）。 |

**结论**：C-16 条款层未发现安全放宽或新授权入口；R3-01 是“冻结包内文档仍要求不存在的值/相反的列集合”，属可执行性与包一致性问题，不是新的安全放行。

### F. pin / 证据 — **PASS**

见 §0 两张实测表：C-16 实际 sha256 = `a7f57ebd…` = FROZEN pin = `git hash-object 67c741d3…` = blob 内容 sha256；`verify_pins` 18/18；其余 17 项以 `other-17-pins.txt`（@HEAD、`changed=0`）与 C15/C17/C06/C07 独立实算双重佐证；pre/post 分别为 `ad25fb3c…`/`a7f57ebd…`；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字节相等（归一化 sha `9ff9a852…`，81 B/81 行 CRLF 差异）；EV 7 个文件 sha 与实测逐项匹配；`carrier.md` 与载体同 sha `fa52cff6…`；三份日志用 `cmd` 重定向后与 log 逐字节相等。**无伪造/无陈旧证据。**

### G. 冻结包一致性 / 不夸大 — **FAIL（R3-01 / R3-04）**

| 子项 | 判定 | 证据 |
|---|---|---|
| 版本主链 | **PASS** | `C-16:3` v1.5、`FROZEN:15` v1.5、`MATRIX:3/37` v1.5、证据 pre/post 一致。 |
| 历史 pin 保留 | **PASS** | `FROZEN:35-37`（v1.1/v1.3/v1.4）、`FROZEN:113`（v1.4/v1.3/v1.1/v1.0）；v1.4 pre 实测 `ad25fb3c…`；v1.3/v1.1/v1.0 历史值按记录保留（未在工作树重算）。 |
| §1A 三口径 | **PASS** | `FROZEN:22-25` 未改；三口径在本字节上实测一致。 |
| §1B 自洽 | **FAIL（R3-04）** | 复核状态链已修（B PASS），但 `FROZEN:38` 的“原 v1.4 行保留于 §8，不改写”与 `git diff` 不符（`:37` 已改写）；载体 §2.E 未登记。 |
| §2 条件 7 | **PASS** | `FROZEN:51` 第 7 行 v1.5、`⏳`，证据指向载体 §6 与本轮 `pins.log`；无预填 `approved`。 |
| §9 自洽 | **FAIL（R3-01）** | `FROZEN:110` 同一单元格内“只写 registry/generation 两列”与“只写三列、复用 A 卡唯一 SQL”并存；`:111` 复核链与载体一致（B PASS）。 |
| 载体 §6 = r3 处置 + r4 pending | **PASS（记录形式）** | `carrier:61` 记录 r3 `changes_requested` 与 r4 pending；但“本轮已传播修正”与实际字节不符（FROZEN/PREREQ 尚有残余），属 R3-01 的直接后果。 |
| 无预填 approved | **PASS** | v1.5 相关状态为 `⏳`/`pending`/“r4 pending”（`FROZEN:51,111`、`carrier:61`、`EV:3`）；`MATRIX:37` 的“①v1.5 … approved”属冻结条件列，与 v1.4 行同构，不是本次结论（沿用 r3 的判定口径）。 |
| 不夸大（契约 ≠ 实现/产品） | **PASS（弱）** | `carrier:3`“须经独立复核 + DSH 重新冻结后方可视为最终字节”；`C-16:240`“不构成实现授权；不证明 AC 达成”；`FROZEN:57` 同口径；`C-16:35`/`carrier:20`/AUTO 卡 `:82` 三处“实现延后”。AC-T5 字面句仍只出现在载体 §5 核对项（R3-09，P3）。 |

**流程注记（不计 finding）**：矩阵 `MATRIX:3/37` 已把 C-16 标为 `FROZEN v1.5`，而 `FROZEN:51` 条件 7 仍 `⏳`；这与 r3 对 v1.4 行的处理口径一致（条件列不是结论），但在 r5 通过前不应把矩阵状态当作已批准事实。最终提交只能在独立复核 approved 后发生。

## 2. r3 findings 逐条处置

| r3 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **R3-01** 两列方案未传播 | P1 | **OPEN（5/8 修、1/8 半修、2/8 未修）** | C-16:97/105/253、carrier:11/26/40 已修；FROZEN:110 仍含“只写三列”；PREREQ:67 仍三列/新条目；PREREQ:100 仍“只写三列”。`grant.created_at` 规范条款 0 命中。 |
| **R3-02** FROZEN §1B/§9 与载体不一致 | P2 | **CLOSED** | FROZEN:39/111 已为 r1→r2→r3→r4 pending；carrier:61/EV:3 同链；条件 7 `⏳`，无预填 approved。 |
| **R3-03** §6“权限面”归 `INVALID_REQUEST` | P2 | **CLOSED** | C-16:212 已拆为 closed-shape `INVALID_REQUEST` + host-only/session 既有码；与 C-16:103①、§2.4①、C-17:359-361、`core_service.py:1442/1444/1453/6259` 一致。 |
| **R3-04** §1B v1.4 行改写未登记 | P3 | **OPEN** | FROZEN:38 仍称“原 v1.4 行保留于 §8，不改写”，但 diff 显示 :37 已改写；载体 §2.E 未登记，carrier:59 仍重复“不改写”。 |
| **R3-05** 四键键映射 / SQL `size_bytes` | P3 | **OPEN（部分）** | C-16:103 列四键，但无 `content_digest↔facts.sha256`、`size_bytes↔facts.size` 映射，也无“SQL 只匹配三键、`size_bytes` 由 handler 先比对”；`library.py:2327-2331` WHERE 无 `size_bytes`。 |
| **R3-06** `updated:0` 并发/无匹配 | P3 | **OPEN** | C-16:106 幂等句仍无“无并发写入者”前提；SQL 第三谓词在并发刷新下可为真；无匹配/代次回退的返回未逐项写死。 |
| **R3-07** roots 每根/锁外 | P3 | **CLOSED** | C-16:35 已写“每根至多一次、不跨调用缓存、探测在快照后锁外进行”。 |
| **R3-08** 卡面小疵 | P3 | **OPEN（3/3）** | AUTO:69-78 AC 顺序仍 1..7、9、10、8；AUTO:72 仍 `updated:false`；AUTO:58 仍三列字面。 |
| **R3-09** D-4/AC-T5/载体 §2.B | P3 | **PARTIAL（1/3）** | D-4 已补 C-06；AC-T5 字面句仍只在 carrier:53 ⑥ 核对项；carrier:20 仍缺“单根探测异常 → false”。 |
| **R3-10** §0 版本面/A 卡指称 | P3 | **OPEN** | C-16:17 仍未提 v1.5/§2.5；C-16:105/PREREQ:46/67 的“FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/A 卡/L-S4-A”仍混用。 |

**统计**：r3 正文 10 条（P1×1 + P2×2 + P3×7）；本轮 **CLOSED 3**（R3-02、R3-03、R3-07）、**PARTIAL 1**（R3-09）、**OPEN 6**（R3-01、R3-04、R3-05、R3-06、R3-08、R3-10）。其中 R3-01 决定 verdict。

## 3. 新 findings

**无新增独立 finding。** 两项非阻断观察，供 DSH 一并处置：

1. **C-16:107 的“§6 既有闭集”措辞**：`§6` 表本身不含 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`；同句后半“host-only/session 沿用既有码”已限定，`:212` 也已拆清。建议改为“既有错误码（§6 + M2-C1 host-control 码）”，不单独计 P3。
2. **载体 §6:61 “本轮已传播修正”**：因 FROZEN:110/PREREQ:67/100 仍有残余，该句目前不准确；它是 R3-01 的记录面后果，不另计 ID。修复 R3-01 后应改为“已传播修正（剩余 … 于本轮修复）”或等价表述。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=1 / P2=0 / P3=6）。
- C-16 §10 ⑦ 的“独立 byte-level 复核 approved（P0/P1=0）”**未满足**；当前冻结包不能按 r4 approved 提交/推送。
- **阻塞修复（必须先做）**：
  1. `FROZEN:110` 删除“只写三列、”，保留“只写 registry/generation 两列、复用 A 卡唯一 SQL”。
  2. `PREREQ:67` 改为“仅把 `registry_id/authorization_generation` 原地更新为 live grant 的值；`last_verified_at` 保持原值”。
  3. `PREREQ:100` 的“只写三列”改为“只写两列”（历史裁决记录同步到最终形状）。
  4. `AUTO:58` 的“条件写 `…/last_verified_at`”改为“条件写 `registry_id/authorization_generation`（`last_verified_at` 保持原值）”（P3，但与实现卡直接相关，建议同批修）。
- **P3 建议**：`FROZEN:38` 改精确表述并登记载体 §2.E/§6；`C-16:103` 补四键映射与“SQL 三键 + handler 比对 `size_bytes`”；`C-16:106` 补并发前提/无匹配返回；AUTO 卡重排 AC 编号、`updated:false`→`updated:0`；载体 §2.B 同步单根探测异常；`C-16:17` 补 v1.5；AC-T5 字面句放到载体正文结论。
- **证据与重冻**：
  - 若只改 FROZEN/PREREQ/AUTO/载体（不改 C-16），C-16 的 `a7f57ebd` pin、`changed-lines.diff`、pre-post、pins/check 日志、other-17 均可保留；载体/EV 改动后须重算 EV 中 carrier 的 sha；`verify_pins` 仍应 18/18，`check.ps1` 重跑。
  - 若按 R3-05/R3-10 改 C-16 字节，则 C-16 sha256/hash-object 必变 → 更新 FROZEN §1/§1B/§2/§9 与矩阵；重生成 `changed-lines.diff`、pre-post、EV、日志；`verify_pins` 仍应 18/18（C16 新值、其余 17 不变）。
  - 修复后做 **r5** 独立 byte-level 复核；通过后由 DSH 在载体 §6 append-only 落结论并提交。**不得**在修复/复审通过前提交或推送本 UNFREEZE。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `94407c8e-f283-48b2-8dc5-91579bc48e3a`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1/r2/r3 复核或任何相关实现；只读被审字节与背景只读材料（C-06/C-15/C-17/C-16、载体、冻结记录、实现卡、只读源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/实现卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r4.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/--numstat HEAD`、`git diff HEAD -- <各文件>`、`git hash-object`、`git cat-file blob`、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、Python 3（UTF-8 字节/行尾/哈希/计数）、`cmd` 重定向重跑日志。
- **代码只读锚点**：`src/infrastructure/sqlite/library.py:2293-2353`、`src/infrastructure/sqlite/schema.py`（`source_locations` 列与 UNIQUE）、`src/infrastructure/resource_channel/source_read_refs.py:62-84`、`src/bootstrap/core_service.py:1441-1453,6253-6261`、`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:466-499`、`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:29,39`。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明；R3-01 的判定基于**冻结字节 + 只读实现锚点**，不依赖运行结果。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1/r2/r3 报告仅作为被审输入与对照，不作为事实来源。
