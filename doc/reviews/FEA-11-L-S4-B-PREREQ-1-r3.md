---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r3 窄面 byte-level 复审（source.reattest/1 + ReattestSourceLocation 条件写 + roots_available）
reviewer: fresh subagent（r3；独立上下文；未参与本 UNFREEZE 起草、r1/r2 复核或任何相关实现；只读）
session: 1685387b-d1d1-46c1-afb2-c90d2f31da31
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 byte-level 契约复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1/r2 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r3 窄面 byte-level 复审

> **结论先行：`changes_requested`，P0=0 / P1=1 / P2=2 / P3=7。**
>
> **C-16 §2.5「动作」条款已按 r2 P1 修正**：只更新 `registry_id/authorization_generation`，`last_verified_at` 保持当前行原值（不刷新审计时间、不取 `now()`）；`updated:0` 与单点 SQL 谓词一致；grant 载荷未加字段。**矩阵头、FROZEN §2 表列数/证据归属、载体 §6 的 r1/r2 记录、§2.5 ① 的 host-only/session 映射均已修好**（r2 P2 全部关闭）。
>
> **但 r2 P1 的修复没有传播到冻结包其余字节**：载体 §2.C（与证据 `carrier.md` 同字节）仍写“三值取自 live grant 载荷”并列出 **`grant.created_at`**；PREREQ I-2 仍写“三列更新为新条目”；C-16 §2.5「用途」与 §10 变更记录、FROZEN §9 仍写“三列”。`grant.created_at` 不在 C-06 v1.2 grant 字段表、C-16 §2 grant JSON、Core `_ENVELOPE_FIELDS` 或 Host 铸造 payload 中——这正是 r2 P1 指出的“无值可取”。C-16:97「用途」与 C-16:105「动作」在同一冻结文件内直接冲突，PREREQ:67 又为实现卡的直接输入。故 **r2 P1 在包级仍 OPEN（R3-01，P1）**。
>
> 另有两项 P2：FROZEN §1B/§9 的复核状态仍写“r2 复核 pending / pending（r1）”，与载体 §6 的“r2 changes_requested → r3 pending”矛盾（R3-02）；C-16 §6 v1.5 补充仍把“权限面”归 `INVALID_REQUEST`，与 §2.5 ① 的既有 host-only/session 守卫码冲突（R3-03）。
>
> 后果：C-16 §10 ⑦ 的“独立 byte-level 复核 approved（P0/P1=0）”**未满足**；r3 快照字节 `d93ab82a…` 不是最终冻结字节。复核期间工作树已被 r3 处置推进到 `a7f57ebd…`（§0.1），该推进版仍有残留，**不能直接 approved**。FROZEN §9、§2 第 7 行、载体 §6 的 `pending`/`⏳` 必须保留；按 findings 修订后须重算 sha256/hash-object、更新 pin、重跑 `verify_pins` 与 `check.ps1`、重生成证据，再做 r4 独立复核。**不得**在 r4 前提交或推送本 UNFREEZE。

> **复核后推进提示**：本报告成文后工作树被 r3 处置推进到 C-16 `a7f57ebd…`（见 §0.1）；正文的 bytes/verdict 针对 `d93ab82a…` 快照，§0.1 记录推进版已修项与残留项。

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无并发提交） | `git rev-parse HEAD` |
| 复核快照改动集（r3 开始时） | 5 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / AUTO-RECOVERY 卡 / PREREQ 卡）+ 11 个未跟踪项（载体、r1、r2、证据目录 8 文件）；**本报告写入后新增 r3 报告 1 个未跟踪项**；复核期间工作树又被 r3 处置推进，见 §0.1 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `d93ab82ab0bb`、C15 `f9e376a0ed4c`、C17 `aefa0fa5b17e` | 实测；与 `logs/pins.log` 逐字节一致 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` 逐字节一致（各 331 bytes） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §6 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判契约字节可执行性） | 见 §6 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §6 |

**复核字节指纹（r3 开始时的被审快照，SHA-256）**：

| 文件 | sha256 | 对比 r2 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `d93ab82ab0bba988f1458b2f42f789903ee4a4ba1dbde7ad9610d67fc0b533c6`（38678 bytes，LF，0 CRLF） | 已改（r2 为 `39da9766…`） |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `8fd0401289c2d1ee0688516e22d767aa1bff42e56a737fc6ca32946a79813bfc` | 已改 |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 已改（r2 为 `4373cc6e…`，本轮头部/行已修） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `290efff3d2ca346c68da7e6a4e6d94f071c79324433916a7e1114075873d39b6` | 已改（r2 为 `3de606fb…`） |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `3a1da56bf8b24960a3fb65f18ea0dec5083ae1cc6d89ce8a3261a0912ce1c311` | 已改（r2 为 `332fbcec…`） |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `e5bba4e3fd9de49fdf1164b8e50e5db9d23a62203a3185b7369d2c9b3178fdad` | 已改（r2 为 `983d1ab5…`） |

**pin / 证据实测**：

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 被审快照原始字节 sha256（r3 开始时） | `d93ab82a…`（当时的 FROZEN:16、FROZEN §9:112、pre-post post） | `d93ab82ab0bba988f1458b2f42f789903ee4a4ba1dbde7ad9610d67fc0b533c6`（38678 bytes，LF，0 CRLF） | ✅ |
| `git hash-object`（被审快照） | `00a7e474…`（当时的 FROZEN:17） | `00a7e4741c395e0e218b3a037e0b9dd9dd7408b1` | ✅ |
| HEAD v1.4 blob sha256（pre） | `ad25fb3c…`（pre-post pre、FROZEN §1B:37） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc`（32577 bytes） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0 | ✅ |
| 独立抽查 4 个未重签 pin（文件实算） | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 全部 match | ✅ |
| `other-17-pins.txt` | 17 项、`changed=0`、@HEAD | 17 行 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | actual 15121 B / evidence 15202 B（差 81 = 81 行 CRLF）；`\r\n→\n` 后 sha256 同为 `f415a8c546087edc3e624bdf94ed714e9be171af86f791a97dfcc3519dad2556` | ✅ |
| EV 表逐文件 sha | 7 项 | carrier `290efff3`、changed-lines `200c7253`、check/check-taskpath `d1e251bc`、pins `c584cbf3`、other-17 `fee1af10`、pre-post `d9a4e0b5` 全部实测匹配 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `290efff3…`、同 7400 bytes | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 331 B / check-taskpath 331 B，三者重跑后**逐字节相等** | ✅ |

**事实校正（不构成缺陷）**：r2 报告记录的 check 日志为 421 bytes 是上一轮字节；r3 快照实测为 331 bytes，EV 与 `logs/check.log` 均与 331 bytes 逐字节一致；复核后推进版又回到 421 bytes（见 §0.1）。这是字节演进，不是证据错误。

### 0.1 复核后工作树推进（post-review update，2026-11-07 13:00 左右）

本报告主体是 r3 开始时的被审快照（C-16 `d93ab82a…`；FROZEN pin 同值）。复核期间，工作树被 r3 处置推进到：

| 项 | 推进后实测 |
|---|---|
| C-16 | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 bytes） |
| `git hash-object` | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` |
| FROZEN-C16 | `46349ea067cc1f6af5c1e5b5e1534ee9312db258d206f1a70d891030ba053bf0`（pin/hash-object 已改 `a7f57ebd` / `67c741d3`） |
| 载体 | `fa52cff663167f672f28c31068fb69b5de439f27596c1a5038dea759a965933a`（= `carrier.md`） |
| PREREQ 卡 | `9f764f5e1253729a83e8ef0e637b3640ec27dbebb59e7e5f341f836610ddbfaa` |
| AUTO 卡 | `e5bba4e3fd9de49fdf1164b8e50e5db9d23a62203a3185b7369d2c9b3178fdad`（未改） |
| 证据 | pins.log `07c2b60c…`、changed-lines `9ff9a852…`、pre-post `57c1c2d9…`、carrier `fa52cff6…`、EV `7b67bfee…`；`verify_pins` 仍 PASS 18/18（C16 `a7f57ebd`），check 日志 421 bytes 重跑一致；changed-lines 归一化后与当前 `git diff HEAD -- C-16` 相等（15436 B，归一化 sha `74b94191…`）。 |

推进版已修：`C-16:97/253` 两列、`carrier:11/26/40` 两列、`carrier:60/61` 记 r2/r3、`C-16:212` 改为“closed-shape 错误 `INVALID_REQUEST`、host-only/session 沿用既有码”、`FROZEN:39/111` 改为 r1→r2→r3→r4 pending、`PREREQ:49` 补 C-06、证据重生成。

**推进版仍残留（r4 应复核；不改变本报告对 `d93ab82a…` 快照的 r3 判定）**：

- `PREREQ:67`（I-2 动作）仍写 `registry_id/authorization_generation/last_verified_at` 三列“更新为新条目”；`PREREQ:100` 仍写“只写三列”；
- `FROZEN:110` 同一行仍有“只写三列”（与前半句“只写 registry/generation 两列”并存）；
- `C-16:17` 版本面仍未提 v1.5/§2.5；
- `carrier:20` 仍未同步“单根探测异常 → false”；
- `FROZEN:37-38` / `carrier:33-36`（§2.E）的 §1B v1.4 历史行/登记仍未处理；
- AUTO 卡 `:58`/`:72` 仍写三列/`updated:false`、AC 编号未重排；
- `C-16:103` ④键映射、`:106` `updated` 并发前提仍缺。

这些残留与 r3 快照中的 R3-01/R3-04/R3-05/R3-06/R3-08/R3-09/R3-10 同类；**推进版不应直接 approved**。r4 应以 `a7f57ebd…` 及其重生成证据为准。

## 1. A–F 逐项判定

### A. r2 P1 关闭：`last_verified_at` 与写入值 — **FAIL（包级；C-16 §2.5「动作」子项 PASS）**

**已修对的部分（应记入）**：

- `C-16:105` 的「动作」现已写成：仅把 `registry_id/authorization_generation` 原地更新为 `grant.registry_id` / `grant.generation`；**`last_verified_at` 保持当前行原值**（UPDATE 前读取原值并原样回写；不刷新审计时间、不取 `now()`、不做时钟推断）。`carrier:26` 的旧文本虽仍在，但 C-16 合同正文的「动作」已可按字面实现。
- `C-16:106` 的幂等解释与单点 SQL 一致：同一 grant 第二次调用时 `registry/generation` 相等，且传入的 `last_verified_at` 等于行内原值 → 第三谓词 `(registry_id <> ? OR authorization_generation <> ? OR last_verified_at IS NOT ?)` 为假 → `rowcount=0` → `updated:0`、零写。SQL 的 SET 恰为三列、WHERE 含 `is_current=1`、不 INSERT（`library.py:2324-2338`）。
- `registry_id/generation` 都在 `RegisterSourceReadGrant` 的签名载荷内（`C-16:43-67`），未给 grant 加字段；`C-16:105` 明写“均已在……签名载荷内，不新增 wire 字段”。

**未闭合的部分（R3-01，P1）**：同一冻结包仍有至少 8 处把该命令写成“三列/新条目”，其中两处直接指向不存在的值：

| 位置 | 现有字节 | 问题 |
|---|---|---|
| `C-16:97`（§2.5「用途（冻结）」） | “把……`registry_id/authorization_generation/last_verified_at` **条件单行**更新为新授权条目” | 与同节 `C-16:105`「动作」直接冲突；`last_verified_at` 的“新条目值”没有来源 |
| `C-16:253`（§10 变更记录） | “只写 `source_locations` 三列” | 与动作条款冲突 |
| `FROZEN:110`（§9 修订内容） | “只写三列、复用 A 卡唯一 SQL” | 与动作条款冲突 |
| `carrier:11`（§1 目标） | “只写 `source_locations` 三列” | 与动作条款冲突 |
| `carrier:26`（§2.C 动作） | “仅原地更新 `registry_id/authorization_generation/last_verified_at`，三值取自 live grant 载荷（`grant.registry_id`/`grant.generation`/**`grant.created_at`**；不取 `now()`）” | **`grant.created_at` 不在冻结 grant 载荷**；这是 r2 P1 的原文缺陷，未修 |
| `carrier:40`（§3 安全） | “只写三列” | 与动作条款冲突 |
| `PREREQ:67`（I-2 动作） | “仅把……`registry_id/authorization_generation/last_verified_at` 原地更新为新条目” | 这是 L-S4-B 实现卡的直接输入；仍要求三列/新值 |
| `PREREQ:100`（ZCode 裁决记录） | “只写三列” | 与动作条款冲突 |

`grant.created_at` 不存在的四重锚点（本回复核）：

- `C-06:39`（C-06 v1.2，FROZEN，pin `99831a20ffd6…`）的 grant 字段表为 `{grantId, registryId, generation, expiresAt, scope{…}, budget{…}, entries[…], secretRef?, signingKey, signature}`，**无 `createdAt`/`created_at`**；`createdAt` 只出现在 Registry 条目（`C-06:29,51`）。
- `C-16:43-67` §2 `RegisterSourceReadGrant` JSON 的键集恰为 `grant_id/session_id/operation/scope_class/registry_id/generation/expires_at/budget/scope[/secret_ref]/signing_key/signature`，**无 `created_at`**。
- `src/infrastructure/resource_channel/source_read_refs.py:62-66` 的 `_ENVELOPE_FIELDS` 是闭集，`register()` 要求 `_ENVELOPE_FIELDS <= set(payload) <= _ENVELOPE_FIELDS | {"secret_ref"}`；`:69-84` 的 `_SourceReadGrant` 也不落 `created_at`。加该键会被 `SOURCE_ACCESS_DENIED`（payload malformed）。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:470-499` 铸造 payload 的键集与上表一致；签名 = payload 减 `signing_key`/`signature`（`:494-498`），`created_at` 没有铸造对象。

**结论**：C-16 §2.5「动作」子项 PASS；但冻结包层面 r2 P1 **OPEN**。这不是措辞小疵：`C-16:97` 与 `C-16:105` 在同一冻结文件内对“更新哪些列”给出相反答案，且载体 §2.C/证据 `carrier.md` 与 PREREQ I-2 仍要求 `last_verified_at` 取一个新值。实现者按载体/PREREQ 实现会再次得到“值无来源”的阻断。**R3-01（P1）**。

**修法建议**：把上述 8 处统一为“只改 `registry_id/authorization_generation`；`last_verified_at` 保持原值”；从载体 §2.C 删除 `grant.created_at`，并在载体 §6 明写 §2.C 以最终冻结字节为准；若载体 §2.C 要保留为“历史提议”，须显式标注“已被 §6 处置取代”，不能让读者把它当作最终修订。`C-16:97`/`:253`、`FROZEN:110`、`PREREQ:67/100` 同步改。

### B. r2 P2 关闭：矩阵 / FROZEN §2 / 载体 §6 / §2.5 ① — **PASS（4/4）**

| 子项 | 判定 | 证据 |
|---|---|---|
| 矩阵头 C-16 v1.5 | **PASS** | `MATRIX:3` 已写 “C-05 v1.2/C-15 v1.5/**C-16 v1.5**……v1.5 增 `source.reattest/1` + §2.5 条件写 + `roots_available`”；`MATRIX:37` 的 C-16 行亦为 v1.5，含 “re-attest 条件写/roots 可用性投影”，并指向载体 V15。 |
| FROZEN §2 列数正确、v1.4/v1.5 证据归属正确 | **PASS** | 实测 §2 表头 4 列、7 行数据均 4 格（`FROZEN:43-51`）。第 6 行（v1.4）证据为 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md` §6 + `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/logs/pins.log`；第 7 行（v1.5）证据为 V15 载体 §6 + `verification/FEA-11-L-S4-B-PREREQ-1/logs/pins.log`；状态 `⏳`。第 6/7 行不再错挂。 |
| 载体 §6 记录 r1/r2 changes_requested + 处置 + r3 pending | **PASS** | `carrier:58` 记 r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5）；`:59` 记处置（2 键、两列、Core/Host 拆分、错误码、矩阵/FROZEN §2 修复等）；`:60` 记 r2 `changes_requested`（P0=0/P1=1/P2=4/P3=6）并写 “**r3 窄面复核 pending**”。 |
| §2.5 ① host-only/session 映射改为沿用既有守卫错误码 | **PASS** | `C-16:103` ①已改为 “host-only session；application 面拒绝，**沿用既有 host-only/session 守卫错误码**，不新增码”，不再写 `INVALID_REQUEST`；与 `C-16:89`（§2.4 ①：`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）、`C-17:192,359` 及 `core_service.py:6259,1441-1453` 口径一致。`C-16:107` 亦写 “host-only/session 守卫沿用既有码”。 |

**残余**：`C-16:212`（§6 v1.5 补充）仍写 “形状/权限面 `INVALID_REQUEST`”，与 ①的既有守卫码存在映射歧义 → **R3-03（P2）**；不影响 B 的上述四项判定（§2.5 ① 本项 PASS）。

### C. r1 findings 状态

| r1 ID | 级别 | 状态 | 依据 |
|---|---|---|---|
| **P1-1** 请求 4 键 vs 2 键 | P1 | **CLOSED** | `C-16:98-102` 明写“恰 2 键” `{source_id, grant_id}`，无 `command`/`scope`/路径/`registry_id`/`generation`；`C-16:253`、`FROZEN:110`、`carrier:23`、`PREREQ:65` 五处一致；形状错 → `INVALID_REQUEST`。 |
| **P1-2** 三列值来源 + 幂等冲突 | P1 | **CLOSED（C-16 §2.5 动作）／OPEN（包级，R3-01）** | `C-16:105-106` 已改为两列 + 原值；但 `C-16:97/253`、`FROZEN:110`、`carrier:11/26/40`、`PREREQ:67/100` 仍写三列，`carrier:26` 仍有 `grant.created_at` → 见 A。 |
| **P2-1** Host 条件并入 Core 校验 | P2 | **CLOSED** | `C-16:103` 只列 Core 边界四项；`C-16:104` 独立成“Host 侧前置义务（本命令不校验、不依赖）”，含唯一 live、恰 1 根、路径 normalize、`live.CreatedAt > old.RevokedAt`、非 folder、每轮一次，并说明 Core `source_locations` 无 path 列（`schema.py:629-648` 实测无 path）。 |
| **P2-2** 形状错误码 + D-4 码表不一致 | P2 | **CLOSED** | `C-16:102` 形状错 `INVALID_REQUEST`；`C-16:107` / `C-16:212` / `PREREQ:49` 六码一致（`INVALID_REQUEST`/`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`）；`PREREQ:49` 已删 `SOURCE_BUDGET_EXCEEDED`、补 `SOURCE_GRANT_EXPIRED`/`SOURCE_REGISTRY_BUSY`。注：D-4 的“零字节清单”仍漏 C-06，属另一 P3（R3-09）。 |
| **P2-3** 矩阵头 v1.4 | P2 | **CLOSED** | `MATRIX:3` 已改 v1.5；矩阵字节 `b23ffa86…` 相对 r2 `4373cc6e…` 已变。 |
| **P2-4** FROZEN §2 缺 v1.5 行 | P2 | **CLOSED** | `FROZEN:51` 第 7 行 v1.5、状态 `⏳`、证据正确；第 6 行 v1.4 证据已恢复；两行均 4 格。 |
| **P3-1** FROZEN §1B v1.4 行改写未登记 | P3 | **OPEN（R3-04）** | `FROZEN:37` 相对 HEAD 被改写（删 r1 计数/session/head）；`:38` 又加同名“v1.4 复核字节”指针行，称“原 v1.4 行保留于 §8，不改写”，但 §8 是 v1.4 UNFREEZE 记录、且 §1B 原行确已改；载体 §2.E（`:33-36`）未登记；`carrier:59` 还声称“§1B v1.4 行保留不改写”。 |
| **P3-2** 键映射 / `size_bytes` 不在 SQL 谓词 | P3 | **OPEN（R3-05）** | `C-16:103` ④仍只给四键列名，未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size`，也未写“SQL 只匹配三身份键、`size_bytes` 由 handler 先比对”（`library.py:2327-2328` 的 WHERE 无 `size_bytes`）。 |
| **P3-3** response `version` 未定义 | P3 | **CLOSED** | `C-16:106` 定义 “`version` 为 Core 当前 source version id，只读诊断用，不参与授权/不落库”，并给 closed shape `{source_id, updated, version}`。 |
| **P3-4** roots probe 异常未写 | P3 | **CLOSED（字段级；残 N8/R3-07）** | `C-16:35` 已写“缺失/不可读/身份不符/**单根探测异常**为 `false`（探测异常不得抛出、不得使整命令失败）”；仍缺“每根至多一次/锁外探测”，见 R3-07。 |
| **P3-5** 卡面小疵 | P3 | **OPEN（部分，R3-08/R3-09）** | AUTO 卡 AC 编号仍 1..7、9、10、8；`AC-LS4B-4` 仍写 `updated:false`（合同为 `updated: 0|1`）；`PREREQ:49` D-4 仍漏 C-06；AC-T5 要求的“契约就绪 ≠ 实现/产品可用”字面句仍只出现在载体 §5 的核对项（`carrier:53` ⑥）。 |

### D. 安全语义复核（不回归） — **PASS（C-16 合同语义层）**

| 子项 | 判定 | 证据 |
|---|---|---|
| 请求 2 键；无路径 / 无 `registry_id` / 无 `generation` | **PASS** | `C-16:100` 仅 `{"source_id","grant_id"}`；`C-16:102` 明写无 command/scope/路径/registry_id/generation。 |
| 拒绝 / 无匹配零写 | **PASS** | `C-16:103` 末句“任一不满足 → typed 拒绝、**零写**”；`C-16:107` “拒绝/无匹配零写”。 |
| 只写两列（`last_verified_at` 不变） | **PASS（合同动作）** | `C-16:105` 只更新 `registry_id/authorization_generation`，`last_verified_at` 原值回写；复用 `library.py:2324-2339` 单点 SQL（SET 三列但第三列传原值；无第二份 SQL，`commit_source_location_auth_refresh:2341-2353` 为独立写单元）。包内文档残留见 R3-01。 |
| 不改行数 / `source_id` / digest / `is_current` / binding | **PASS** | `C-16:105` 明写；SQL `UPDATE … WHERE … is_current = 1`，不写 `is_current`，不 INSERT；`page_bindings` 不在 SQL 内。 |
| 错误码闭集无新增 | **PASS** | `C-16:189-208` 表本体零行改动；`C-16:212` 只列既有六码；host-only/session 码为 M2-C1/C-17 既有码。§6 的“权限面”措辞歧义见 R3-03。 |
| C-15 / C-17 / C-06 / C-07 / M2-C1 零字节 | **PASS** | `git diff --stat HEAD` 对五个文件为空；`git status -uall` 无这些文件；`verify_pins` 18/18，C15/C17/C06/C07 实算匹配；M2-C1 无 diff。 |
| 红线：不自动重新授权 / 不重建 identity / 撤销后不放行 / 不扩面 / folder 排除 / reset limitation | **PASS** | `C-16:108` 六条齐备；`C-16:97` 明写“不是恢复动作、不是授权决定”；`C-16:103` ③要求 grant live/未撤销；④四键身份阻止同路径换文件；`C-16:104` Host 侧 folder 排除；`C-16:108` reset 后无旧条目可桥接。 |

**结论**：C-16 条款层未发现安全放宽或新授权入口；R3-01 是“包内文档仍要求不存在的值/相反的列集合”，属可执行性与冻结包一致性问题，不是新的安全放行。

### E. pin / 证据 — **PASS**

见 §0 两张实测表（r3 快照）与 §0.1（推进版）：r3 快照 C-16 实际 sha256 = `d93ab82a…` = 当时的 FROZEN pin = `git hash-object 00a7e474…` = blob 内容 sha256；`verify_pins` 18/18；其余 17 项以 `other-17-pins.txt`（@HEAD、`changed=0`）与 C15/C17/C06/C07 独立实算双重佐证；pre/post 分别为 `ad25fb3c…`/`d93ab82a…`；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字节相等（归一化 sha `f415a8c5…`）；EV 7 个文件 sha 与实测逐项匹配；`carrier.md` 与载体同 sha `290efff3…`；三份日志重跑后逐字节复现。**无伪造/无陈旧证据**。推进版 `a7f57ebd…` 的 pin/证据见 §0.1，初步抽查 pins/carrier/changed-lines/check 一致；完整逐项复核归 r4。

### F. 冻结包一致性 / 不夸大 — **FAIL（R3-01 / R3-02 / R3-04）**

| 子项 | 判定 | 证据 |
|---|---|---|
| 版本主链 | **PASS** | `C-16:3` v1.5、`FROZEN:15` v1.5、`MATRIX:3/37` v1.5、证据 pre/post 一致。 |
| 历史 pin 保留 | **PASS** | `FROZEN:35-37`（v1.1/v1.3/v1.4）、`FROZEN:113`（v1.4/v1.3/v1.1/v1.0）；v1.4 pre 实测 `ad25fb3c…`；v1.3/v1.1/v1.0 历史值按记录保留（未在工作树重算）。 |
| §1A 三口径 | **PASS** | `FROZEN:22-25` 未改；三口径在本字节上实测一致。 |
| §1B 自洽 | **FAIL（R3-02/R3-04）** | `FROZEN:39` 仍写“r2 复核 **pending**”（r2 已 `changes_requested`）；`:37-38` 的 v1.4 历史行/指针行语义不精确（见 C/P3-1）。 |
| §2 条件 7 | **PASS** | `FROZEN:51` 第 7 行 v1.5、`⏳`，证据指向载体 §6 与本轮 `pins.log`；无预填 `approved`。 |
| §9 自洽 | **FAIL（R3-01/R3-02）** | `FROZEN:110` 仍写“只写三列”（与 C-16:105 冲突）；`:111` 仍写“`pending`（r1；approved 后…）”，与 `carrier:60` 的 r2→r3 pending 不一致。 |
| 载体 §6 = r2 处置 + r3 pending | **PASS** | `carrier:58-60`；r1/r2 计数、处置、r3 pending 齐备。但 `carrier:59` 的“§1B v1.4 行保留不改写”不实（R3-04）。 |
| 无预填 approved | **PASS** | v1.5 相关状态为 `⏳`/`pending`/“r3 pending”（`FROZEN:51,111`、`carrier:60`、`EV:3`）；`MATRIX:37` 的“①v1.5 … approved”属冻结条件列，与 v1.4 行同构，不是本次结论。 |
| 不夸大（契约 ≠ 实现/产品） | **PASS（弱）** | `carrier:3`“须经独立复核 + DSH 重新冻结后方可视为最终字节”；`C-16:240`“不构成实现授权；不证明 AC 达成”；`FROZEN:57` 同口径；`C-16:35`/`carrier:20`/AUTO 卡 `:82` 三处“实现延后”。AC-T5 字面句仍缺（R3-09）。 |

## 2. r2 findings 逐条处置

| r2 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **N1** `grant.created_at` 不在 grant 载荷 | P1 | **OPEN（C-16 §2.5 动作已修；包内 8 处未修，R3-01）** | §1-A：`C-16:105` 已改两列+原值；但 `C-16:97/253`、`FROZEN:110`、`carrier:11/26/40`、`PREREQ:67/100` 仍写三列；`carrier:26` 仍列 `grant.created_at`，四重锚点证明该字段不存在。 |
| **N2** FROZEN §2 表损坏 / 证据错挂 | P2 | **CLOSED** | §1-B：§2 表头 4 列、7 行均 4 格；第 6 行 v1.4 证据、第 7 行 v1.5 证据归属正确。 |
| **N3** 载体 §6 未记 r1 / FROZEN §9 pending | P2 | **PARTIAL → OPEN（R3-02）** | 载体 §6 已记 r1/r2 + 处置 + r3 pending（PASS）；但 `FROZEN:39` 仍“r2 pending”、`:111` 仍“pending（r1）”，与载体 §6 矛盾。 |
| **N4** §2.5 ① host-only 映射 `INVALID_REQUEST` | P2 | **PARTIAL → OPEN（R3-03）** | §2.5 ①/错误段已改为沿用既有守卫码（PASS）；但 `C-16:212` 仍写“形状/权限面 `INVALID_REQUEST`”，与 §2.5 ①/§2.4 ①/§2.5 ③④ 的映射不一致。 |
| **N5** FROZEN §1B v1.4 行改写未登记 | P3 | **OPEN（R3-04）** | `FROZEN:37` 相对 HEAD 被改写；`:38` 同名指针行；载体 §2.E 未登记；`carrier:59` 称“保留不改写”不实。 |
| **N6** 四键键映射 / SQL `size_bytes` | P3 | **OPEN（R3-05）** | `C-16:103` ④仍缺键映射与“SQL 只匹配三键、`size_bytes` 由 handler 比对”。 |
| **N7** `updated:0` 三来源/并发 | P3 | **OPEN（部分，R3-06）** | `C-16:106` 已定义 `updated` 0/1 与幂等，但未写“无其他写入者介入”前提，也未明确代次回退/无匹配的返回；SQL 第三谓词在并发刷新下可使 `rowcount=1`。 |
| **N8** roots_available 每根/锁外 | P3 | **OPEN（R3-07）** | `C-16:35` 只有异常→false，仍缺“每次调用每根至多一次、锁外探测”；B2 卡不存在。 |
| **N9** 卡面小疵 | P3 | **OPEN（部分，R3-08/R3-09）** | `AC-LS4B-4` 已改两列（PASS），但仍 `updated:false`；AC 编号仍 1..7、9、10、8；D-4 仍漏 C-06；AC-T5 字面句仍只在 `carrier:53` 核对项。 |
| **N10** §0 版本面未提 v1.5 | P3 | **OPEN（R3-10）** | `C-16:17` 仍只写 “source-access-wire/1.3（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…）”，未提 v1.5/§2.5；A 卡指称仍混用（`C-16:105` 用全名、`PREREQ:46/67` 用 A 卡/L-S4-A）。 |

**统计**：r2 正文 N1–N10 共 10 条 = P1×1 + P2×3 + P3×6（r2 报告的 P2=4 另含 r1 P2-3「矩阵头」，本轮已在 C 表判 CLOSED）。**CLOSED 1**（N2）；**PARTIAL 3**（N3、N4、N7）；**OPEN 6**（N1、N5、N6、N8、N9、N10）。其中 N1 与 N3 直接决定 verdict。

## 3. 新 findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R3-01** | **P1** | `C-16:97,253`；`FROZEN:110`；`carrier:11,26,40`；`PREREQ:67,100`（`carrier.md` 同字节） | r2 P1 的修复只在 `C-16:105`「动作」落地；包内 8 处仍写“三列/新条目”，`carrier:26` 仍列 **`grant.created_at`**（C-06 v1.2 grant 字段表、C-16 §2 JSON、`_ENVELOPE_FIELDS`、Host 铸造 payload 均无该键）。C-16:97「用途」与 C-16:105「动作」同文件内直接冲突；PREREQ I-2 是实现卡直接输入。照包内文本实现仍会得到“`last_verified_at` 无值可取”。 | 统一改为“只改 `registry_id/authorization_generation`；`last_verified_at` 保持原值”；删除载体 §2.C 的 `grant.created_at`；在载体 §6 明写 §2.C 以最终冻结字节为准（或标注历史提议已被 §6 取代）；同步 C-16:97/253、FROZEN:110、PREREQ:67/100。 |
| **R3-02** | **P2** | `FROZEN:39,111` vs `carrier:60`、`EV:3` | FROZEN §1B 的 v1.5 行写“r2 复核 **pending**”，§9 写“`pending`（r1…）”；r2 已完成 `changes_requested`，载体 §6/EV 已写 r2 `changes_requested` → r3 pending。冻结记录对同一轮复核给出两个状态。 | 按 append-only 更新：`FROZEN:39` 改“r1 changes_requested（P0=0/P1=2/P2=4/P3=5）→ 处置 → r2 changes_requested（P0=0/P1=1/P2=4/P3=6）→ 处置 → r3 pending”；`FROZEN:111` 同步；`⏳` 保留。 |
| **R3-03** | **P2** | `C-16:212`；对照 `C-16:89,103,107`、`C-17:192,359`、`core_service.py:6259,1441-1453` | §6 v1.5 补充仍写“形状/权限面 `INVALID_REQUEST`”。“权限面”若指 host-only/session，则应为 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`（§2.4 ①、C-17/M2-C1 既有口径）；若指 grant 授权面，则应为 `SOURCE_ACCESS_DENIED`。同段又与 `C-16:107`“复用 §6 既有闭集”并用，而 §6 表（`:189-208`）不含 HOST_* 码，措辞不准确。 | `C-16:212` 拆清：形状错 `INVALID_REQUEST`；host-only/session 沿用既有 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`；grant 状态/身份/registry 各自列既有码。`C-16:107` 的“§6 既有闭集”改为“既有错误码（§6 + M2-C1 host-control 码）”。 |
| **R3-04** | P3 | `FROZEN:37-38`；`carrier:33-36`（§2.E）与 `:59`（§6） | §1B 的 v1.4 行相对 HEAD 被改写（删 r1 计数/session/head），又加一行同名“v1.4 复核字节（行保留历史；v1.5 行追加）”；“原 v1.4 行保留于 §8，不改写”不精确（§8 是 v1.4 UNFREEZE 记录，§1B 原行确已改写）。载体 §2.E 未登记该编辑；`carrier:59` 还称“§1B v1.4 行保留不改写”，与 diff 不符。 | 二选一：恢复 `FROZEN:37` 原 v1.4 行文本并删 `:38` 重复指针行；或把 `:38` 改成精确表述“v1.4 原始行信息见 §8；本行仅登记 v1.5 追加”，并删“不改写”字样；在载体 §2.E/§6 登记实际编辑。 |
| **R3-05** | P3 | `C-16:103` ④、`:105`；`C-16:60`；`library.py:2327-2328` | 四键物理身份与 grant facts 的键映射未写：`content_digest↔facts.sha256`、`size_bytes↔facts.size`、`volume_serial`/`file_id` 同名；单点 SQL 的 WHERE 只匹配 `content_digest/volume_serial/file_id`，不含 `size_bytes`，故 `size_bytes` 必须由 handler 在调用前显式比对。实现者可能误以为 SQL 覆盖四键。 | 在 §2.5 ④ 或动作段补一行键映射 + “SQL 只匹配三身份键；`size_bytes` 由 handler 先比对”。 |
| **R3-06** | P3 | `C-16:106`；`library.py:2330-2331` | `updated` 写“当且仅当 registry/generation 实际变化为 1”，但 SQL 的第三谓词在“handler 读取原值后、UPDATE 前”有别的写入者刷新 `last_verified_at` 时可为真 → `rowcount=1`（且会把该列写回旧值）；“同 grant 重复调用 → `updated:0`”也未限定“无其他写入者介入”。同 registry 代次回退、无匹配行的返回（`updated:0` 还是 typed）仍未明确。 | 给幂等句加“无并发写入者介入”前提；明确代次回退为 `updated:0` 还是 typed；明确无匹配（行不存在/`is_current=0`）走 `SOURCE_ACCESS_DENIED` 零写。 |
| **R3-07** | P3 | `C-16:35` | `roots_available` 已写单根探测异常→false、不得抛出；仍缺“每次调用每根至多探一次、锁外探测”（scope review AC-B2-6 的实现约束）。B2 实现卡尚不存在，当前是“要求无归属”。 | 在 §1 补该两句，或待 B2 卡建立时登记为 AC；不能只留在 scope review。 |
| **R3-08** | P3 | `AUTO:58,69-78`（尤其 `:72`） | ①AC 编号仍 1..7、9、10、8；②`AC-LS4B-4` 仍写“重复调用 `updated:false`”，与合同 `updated: 0|1`（`C-16:106`、`PREREQ:69`）类型不一致；③`AUTO:58` 仍写“条件写 `registry_id/authorization_generation/last_verified_at`（…；`last_verified_at` 保持原值）”，字面仍是三列。 | 重排 AC 编号；把 `updated:false` 改 `updated:0`；把 `AUTO:58` 改为“只改 `registry_id/authorization_generation`（`last_verified_at` 保持原值）”。 |
| **R3-09** | P3 | `PREREQ:49`；`carrier:53`；`carrier:20` | ①D-4 的零字节清单仍写 `C-15/C-17/C-07/M2-C1`，**漏 C-06**（out_of_scope/AC-T1 明列；I-2 仅在 grant 校验语境提到 C-06）；②AC-T5 要求的“契约就绪 ≠ 实现/产品可用”字面句仍只出现在载体 §5 的核对项（`carrier:53` ⑥），未作为结论句出现在载体正文；③载体 §2.B（`carrier:20`）仍只写“缺失/不可读/身份不符 → false”，未同步 C-16:35 的“单根探测异常 → false、不得抛出”。 | D-4 补 C-06；载体 §1 或 §3 补“契约就绪 ≠ 实现/产品可用”结论句；载体 §2.B 同步单根探测异常口径。 |
| **R3-10** | P3 | `C-16:17`；`PREREQ:46,67` | §0 版本面行仍写“本契约 **source-access-wire/1.3**（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…）”，未提 v1.5/§2.5；读者无法从版本面判断新命令归入哪个 wire 面（虽然“不 bump”是既定裁决）。另“A 卡”指称混用：`C-16:105` 用全名 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`，`PREREQ:46` 用“A 卡”，`PREREQ:67` 用“L-S4-A”。 | 版本面行补“v1.5 additive §2.5（不 bump）”；统一 A 卡指称（首次出现给别名）。 |

**计数**：P1×1（R3-01）、P2×2（R3-02、R3-03）、P3×7（R3-04…R3-10）。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=1 / P2=2 / P3=7；针对 r3 快照 `d93ab82a…`）。
- C-16 §10 ⑦ 的“独立 byte-level 复核 approved（P0/P1=0）”**未满足**；r3 快照 `d93ab82a…` **不是可长期保留的最终冻结字节**。复核后工作树已推进到 `a7f57ebd…`（§0.1）：推进版修复了 R3-01/R3-02/R3-03 的主体，但仍残留 `PREREQ:67/100`、`FROZEN:110` 等（§0.1），**不能直接 approved**。FROZEN §2 第 7 行 `⏳`、§9 `pending`、载体 §6 “r4 pending” 必须保留；**不得**在 r4 前提交或推送。
- 建议处置顺序：
  1. **先修 R3-01（唯一 P1）**：把 `C-16:97/253`、`FROZEN:110`、`carrier:11/26/40`、`PREREQ:67/100` 统一为“只改两列；`last_verified_at` 保持原值”；删除载体 §2.C 的 `grant.created_at`；若保留 §2.C 为历史提议，必须在 §6 明示“以最终冻结字节为准/已被处置取代”。同步 `AUTO:58` 的“条件写三列”措辞。
  2. 修 P2：`FROZEN:39/111` 的复核状态改为 r1→r2→r3 链；`C-16:212` 的“权限面 `INVALID_REQUEST`”拆清为既有守卫码/业务码。
  3. 修 P3（R3-04…R3-10）：FROZEN §1B 指针行、键映射/SQL `size_bytes`、`updated` 前提/代次回退、roots 每根一次、AUTO 卡编号/`updated:false`、D-4 补 C-06、AC-T5 字面句、载体 §2.B、§0 版本面。
  4. 重算 C-16 sha256 与 `git hash-object`，更新 FROZEN §1/§1B/§2/§9 与矩阵；若只改文档而 C-16 字节不动，仍须确认 pin 未变；若按 R3-01 改 C-16:97/253，C-16 字节必变 → 更新 pin、重跑 `verify_pins`（仍应 18/18：C16 新值、其余 17 不变）、`check.ps1`（默认 + `-TaskPath`），重生成 `changed-lines.diff`/pre-post/日志/EV。
  5. 再做 r4 独立 byte-level 复核；通过后由 DSH 在载体 §6 append-only 落结论并提交。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施；**不建议**在 r4 前提交或推送 UNFREEZE。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `1685387b-d1d1-46c1-afb2-c90d2f31da31`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1/r2 复核或任何相关实现；只读被审字节与背景只读材料（C-06/C-15/C-17/C-16、scope review、实现卡、源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/实现卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r3.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only HEAD`、`git diff --stat/numstat HEAD`、`git diff HEAD -- <各文件>`、`git hash-object`、`git cat-file blob HEAD:<C-16>`、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、Python 3（UTF-8 表格列数/hash/日志重跑比对）。
- **代码只读锚点**：`src/infrastructure/sqlite/library.py:2293-2353`、`src/infrastructure/sqlite/schema.py:629-648`、`src/infrastructure/resource_channel/source_read_refs.py:62-84,124-131`、`src/bootstrap/core_service.py:1441-1453,6253-6261`、`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:470-499`、`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:39`。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明；R3-01 的判定基于**冻结字节 + 只读实现锚点**，不依赖运行结果。
- **事实优先级**：报告主体断言取自 `59ba5189f` 工作树的 r3 被审快照（C-16 `d93ab82a…`）、只读源码与工具输出；§0.1 记录复核后推进的 `a7f57ebd…` 及其残余。不采用聊天记录或旧快照作为事实来源。r1/r2 报告仅作为被审输入与对照，不作为事实来源。
