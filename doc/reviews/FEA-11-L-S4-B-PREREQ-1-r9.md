---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r9 独立复核（仅 C-16 冻结字节实质/安全）
reviewer: fresh subagent（r9；独立上下文；未参与本 UNFREEZE 起草、r1–r8 复核或任何相关实现；只读）
session: b0a2e9f0-2e0b-4a42-b780-3d7871f46e2c
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 byte-level 契约复核（fresh context / read-only / 非作者 / 非实现者 / 非 r1–r8 复核者；仅判 C-16 冻结字节）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: approved
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r9 独立复核（仅判冻结字节）

> **结论先行：`approved`（仅就 C-16 v1.5 冻结字节）。P0=0 / P1=0 / P2=0 / P3=3（均为非阻断；三项均为既有已接受的字节层文字项，未回退）。**
>
> C-16 sha256=`a7f57ebdbd67…`（38912 B、LF 253 行、0 CRLF）= FROZEN pin = blob 内容 sha256；`git hash-object`=`67c741d3…`；pre=`ad25fb3c…`（HEAD v1.4 blob，32577 B）→ post=`a7f57ebd…`；`verify_pins` **18/18**；C-15/C-17/C-06/C-07/M2-C1 及其余 16 契约**零字节**；无 wire minor/schema/依赖；§2.5 的两键 closed shape、Core 校验顺序、Host 义务分离、两列条件写 + `last_verified_at` 原值、零写、幂等/单调、错误闭集与红线均未放宽。
>
> **范围声明（决定本报告效力的第一句）**：本报告**只判** `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` 的 C-16 v1.5 冻结字节，以及其与 FROZEN pin / 冻结矩阵 / 载体 §1–§4 的**语义一致性**。**不判**载体 §6 的 r1–r8 逐轮记录、EV 文案、FROZEN §9 记录链等 DSH 治理记录文本；这些记录文本中的既有 P2/P3 不作为本报告 verdict 的依据，也不因本报告 approved 而被追认通过。若记录链仍有未闭合项，由 DSH 按治理流程处理，**不改写 C-16 字节**。

## 0. 基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始与报告写入前同值；无新提交） | `git rev-parse HEAD` |
| 工作树改动集 | 5 个已修改 tracked：C-16 / FROZEN-C16 / 冻结矩阵 / PREREQ 卡 / AUTO-RECOVERY 卡；未跟踪：载体、r1–r8、证据目录 8 文件；本次复核唯一写入为本报告 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**：`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 `git diff HEAD`；C-15/C-17/C-06/C-07/M2-C1 亦无 diff | `git diff --name-only HEAD`、`git status` |
| `verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT=0；C16 `a7f57ebdbd67`；重跑输出与 `logs/pins.log` **逐字节相等**（408 B，sha `07c2b60c…`） | 实测 |
| `check.ps1`（默认 / `-TaskPath`） | PASS（3 warnings），EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` **逐字节相等**（各 421 B，sha `d1e251bc…`） | 实测 |
| 全量 `pytest` / `dotnet test` / gated IPC | **NOT_RUN**（本卡为契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §8 |
| `ReattestSourceLocation` / `source.reattest` 运行时 | **NOT_RUN**（`src/**`、`apps/**` 尚无实现；本报告只判契约字节与只读锚点） | 见 §8 |
| push / `git add` / `git commit` | **NOT_RUN**（只读；未执行） | 见 §8 |

**被审字节指纹（工作树 SHA-256；`Get-FileHash` 与 .NET 原始字节复核一致）**：

| 文件 | sha256 | 字节 / 行尾 |
|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | 38912 B，LF 253 行，0 CRLF |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md`（当前记录，非 C-16 pin 本身） | `7494fbb352a6306ddf8de33b0b774dff9c01a060402668865eb5eb9b748194fb` | 10193 B，LF 113 行 |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `b23ffa86cd20595297fab44a7d9ffe779af5ff0bcafd2ab4d53c89464121fb76` | 8743 B，CRLF 91 行 |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `833b3276c8c0da32cb4b094eae1d5d1b65b6444a2d112d4628e948337e927aa5` | 9271 B，CRLF 81 行 |
| `verification/FEA-11-L-S4-B-PREREQ-1/carrier.md` | `833b3276c8c0da32cb4b094eae1d5d1b65b6444a2d112d4628e948337e927aa5`（与上同字节） | 9271 B |
| `verification/FEA-11-L-S4-B-PREREQ-1/EV.md` | `da3ad2a8ef2cf74bb953de28e432440ae97c144821fda58278e7c62e08129b9a` | 1074 B，CRLF 14 行 |

**C-16 三口径**：

| 口径 | 值 |
|---|---|
| 工作树原始字节 SHA-256（`verify_pins` 口径） | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` |
| `git hash-object`（blob id） | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` |
| `git cat-file blob 67c741d3…` 原始字节 SHA-256 | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d`（38912 B，与工作树逐字节相同） |
| HEAD（v1.4）blob id / 内容 SHA-256 / 大小 | `b9be0acfa232154510d8453133ef8803b6b8fbbe` / `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` / 32577 B |

## 1. A — C-16 v1.5 字节完整性：**PASS**

| # | 核对项 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| A1 | 工作树 sha256 | `a7f57ebd…` | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` | ✅ |
| A2 | `git hash-object` | `67c741d3…` | `67c741d3b99fcf85c9b6dfd790a80a48a3c8d2b8` | ✅ |
| A3 | FROZEN pin 一致 | `FEA-CONTRACT-FROZEN-C16.md` §1 三口径、§1A、§1B v1.5 行同值 | §1 工作树/blob 内容 = `a7f57ebd…`；§1 blob id = `67c741d3…`；§1B v1.5 复核字节 = `a7f57ebd…`（= 冻结字节） | ✅ |
| A4 | pre-image（v1.4） | `ad25fb3c…` | HEAD blob `b9be0acf…`，`git cat-file blob` 原始 32577 B，sha `ad25fb3c…`；`pre-post.sha256:1` 同值 | ✅ |
| A5 | post-image（v1.5） | `a7f57ebd…` | 工作树与 blob 内容均 `a7f57ebd…`；`pre-post.sha256:2` 同值 | ✅ |
| A6 | v1.4→v1.5 diff 范围 | 仅 carrier §2.A–§2.D 所述：头部/§0 能力、§1 `roots_available`、§2.5、§6/§10 补充 | `git diff HEAD -- C-16` 共 6 个 hunk：①状态行+日期行（v1.5，历史 v1.0/v1.1/v1.3/v1.4 保留）；②§0 `source.reattest/1` 能力行；③§1 响应表 + `roots_available` additive 说明；④§2.5 全节插入；⑤§6 v1.5 补充句；⑥§10 冻结条件 ⑦ + 变更记录 v1.5 行（同 hunk 去掉文件末空行）。**无其它实质改动** | ✅ |
| A7 | 旧版本历史 | v1.0/v1.1/v1.3/v1.4 历史保留 | 状态行、日期行、§10 变更记录、FROZEN 历史 pin 均保留；v1.4 内容只被增量取代，未被删改 | ✅ |

**A 结论**：C-16 v1.5 的字节指纹、FROZEN pin、pre/post 与 diff 范围全部一致；未发现「复核后改字节」或「pin 早于最后一笔编辑」的迹象。

## 2. B — 安全语义（实质）：**PASS（无放宽）**

| # | 安全要求 | C-16 v1.5 字节 | 判定 |
|---|---|---|---|
| B1 | 请求恰 2 键，无路径 / `registry_id` / `generation` 入参 | §2.5:98–102：`{"source_id": "<Core source id>", "grant_id": "<source-read grant id>"}`；明写「无 `command`/`scope`」「无路径/无 `registry_id`/无 `generation`」「缺键/多键/类型错 → `INVALID_REQUEST`」 | ✅ |
| B2 | Core 校验顺序：host-only → shape → grant live（含 expiry/revoked）→ `scope.source_id` → 四键 identity → 条件 UPDATE | §2.5:103：①host-control envelope（host-only session；application 面拒绝，沿用既有守卫码、不新增码）②closed shape（恰 2 键）③`grant_id` live、未过期、未撤销 → `SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`，且 `grant.scope.source_id == source_id` → `SOURCE_ACCESS_DENIED` ④当前 `source_locations` 行四键 identity 与 grant facts 逐项相等 → `SOURCE_ACCESS_DENIED`；任一不满足 → typed 拒绝、零写 | ✅ |
| B3 | Host 前置义务与 Core 校验分离 | §2.5:104 独立「Host 侧前置义务（本命令不校验、不依赖；由 L-S4-B 实现卡 AC 保证）」：**唯一 live 非撤销条目**、**恰 1 根**、根路径 normalize 后与 Core location 指向**同一物理文件**、`live.CreatedAt > old.RevokedAt`、**kind 非 folder**、**每个 grant/每轮 refresh 至多一次**；任一不满足 → Host 不发送。并明写 Core `source_locations` 无 path 列（`schema.py:629-646`），路径 normalize 只能在 Host 侧判定 | ✅ |
| B4 | 只写两列 + `last_verified_at` 原值 + 不取 now | §2.5:105：仅原地更新 `registry_id/authorization_generation`（值取 `grant.registry_id`/`grant.generation`，均在签名载荷内，不新增 wire 字段）；`last_verified_at` 保持当前行原值（UPDATE 前读取、原样回写）；不刷新审计时间、不取 `now()`、不做时钟推断；不新增 location 行、不改 `source_id/content_digest/is_current/binding`、不改其它列 | ✅ |
| B5 | 复用同一单点 SQL，幂等/单调 | §2.5:105：复用 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 同一单点 SQL（不得新增第二份）；其 `(registry_id <> ? OR authorization_generation <= ?)` 与相等分支谓词保证仅当 registry/generation 实际变化时更新，同值重复调用 `rowcount=0`。§2.5:106：`updated` 当且仅当实际变化为 1；同 grant 重复调用 → `updated:0` 且零写；generation 单调（同 registry 不倒退，跨 registry 允许 1） | ✅（并发前提见 P3-2，非阻断） |
| B6 | 拒绝 / 无匹配零写 | §2.5:103 末句「任一不满足 → typed 拒绝、**零写**」；§2.5:107「拒绝/无匹配零写」；§2.5:108 红线「撤销后不放行」 | ✅ |
| B7 | 错误码闭集，零新增 | §2.5:107 明确复用 §6 既有码：host-only/session 沿用既有码、形状错 `INVALID_REQUEST`、grant 状态 `SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`、身份/条目 `SOURCE_ACCESS_DENIED`、registry `SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`；§6 v1.5 补充句（:212）同口径；§6 表本体零行改动（diff 仅新增补充句） | ✅ |
| B8 | `INVALID_REQUEST` 仅 closed-shape；host-only/session 用既有码 | §2.5 仅在第②步 closed shape 使用 `INVALID_REQUEST`；第①步明写沿用既有 host-only/session 守卫码、不新增码 | ✅ |
| B9 | 不自动重新授权 / 不重建 identity / 撤销后不放行 / 不扩授权面 / folder 排除 / reset limitation | §2.5:108 六条红线逐项在文；§2.5:97 明写「本命令不是恢复动作、不是授权决定」，只传播用户已完成显式操作的事实；§2.5:104「kind 非 folder」；§2.5:108「`source_reset_registry` 后无旧条目可桥接（需重导入）」 | ✅ |
| B10 | 能力门禁明确（旧 Core 不发送） | §0:23：`source.reattest/1`；Host 在 B1 显式重授权成功后探测；缺失/探测异常 → 不发送、行为与现状一致（target 仍 typed skip；不建文件、不铸 grant）；能力缺失不得靠「发送后看结果」判断 | ✅ |
| B11 | 不新增 wire 字段 / 不放宽既有 grant scope | §2.5:105 明写 `registry_id`/`generation` 已在 `RegisterSourceReadGrant` 签名载荷内（C-16 §2:49–50；C-06:39 字段表同构），不新增 wire 字段；请求只有 `source_id`/`grant_id`；不修改 §2 四维 scope、≤300s TTL、撤销/失联语义 | ✅ |

**B 结论**：C-16 v1.5 的条件写命令是一个**受签名 grant 约束的、单行、两列、可重入的安全传播命令**：它不能产生新授权、不能重建 identity、不能跨 source/身份误写、不能绕过撤销；所有失败路径 typed 且零写。未发现安全放宽或新授权入口。

## 3. C — 不变量零改动：**PASS**

| # | 不变量 | 实测 | 结果 |
|---|---|---|---|
| C1 | C-15/C-17/C-06/C-07/M2-C1 零字节 | `git diff --name-only HEAD` 无这 5 个文件；C15/C17/C06/C07 实算 sha 与 pin 一致；M2-C1 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f` 与 `FEA-CONTRACT-FROZEN-C04b.md` 记录一致、无 diff | ✅ |
| C2 | 其余 17 契约零字节 | `other-17-pins.txt` 17 条 `UNCHANGED`、`changed=0`、@`59ba5189f`；`verify_pins` 18/18 实测；17 个契约文件均无 `git diff` | ✅ |
| C3 | 无 wire minor / schema / 依赖 | C-16 §0 协议面仍 `new-manga.core` 2.3（`PROTOCOL_MAJOR=2/PROTOCOL_MINOR=3`），明写不 bump；`src/**`、`apps/**`、`tests/**`、`tools/**` 零 diff；无 DDL/迁移/依赖文件变化 | ✅ |
| C4 | `source.reattest/1` 能力门禁明确 | §0:23 明写按操作探测、缺失/异常不发送、旧 Core 行为不变；与 v1.1/v1.3 能力追加的既有模式一致；不新增错误码 | ✅ |
| C5 | C-15 零字节的语义判断（D-6） | 见下方说明；本报告独立背书：不需要 C-15 字节变更 | ✅ |
| C6 | C-17 零字节 | §2.5 不触碰 Host 枚举 exact-match / fail-closed 原文；实现顺序「先 reattest 后枚举」由 L-S4-B AC 承载，不是 C-17 字节变更 | ✅ |

**C5 说明（独立判断，不是复核记录转述）**：C-15:204/233 的规范点是「重授权/重新注册**原地更新**该行、不新建重复 location」，其三列列举描述的是既有 refresh 写路径（import/apply 单独写路径）；C-16 §2.5 复用**同一单点 SQL**，原地写**同一行**，仅把 `registry_id/authorization_generation` 变为 live grant 的新值，`last_verified_at` 以原值回写（净变化 0），不新建 location、不改 identity 键。C-15:314 的「显式用户操作」= B1 点击；reattest 只传播该操作的事实，不是第二个授权/恢复动作。故 C-15 字节无需变更。**边界**：若后续治理口径要求该传播路径也刷新审计时间，应另开 C-15/C-16 UNFREEZE，不得在本轮静默改字节；本报告不把该解释冒充为 C-15 的既有明文。

## 4. D — pin / 证据：**PASS**

| # | 证据项 | 实测 | 结果 |
|---|---|---|---|
| D1 | `verify_pins` | `PIN AUDIT: PASS (all 18)`，EXIT=0；C16 新值 `a7f57ebdbd67`；其余 17 原值；重跑输出与 `logs/pins.log` 逐字节相等（408 B，sha `07c2b60c…`） | ✅ |
| D2 | 其余 17 不变 | `other-17-pins.txt`：17 条 `UNCHANGED`、`SUMMARY: 17 contracts, changed=0`、标注 @`59ba5189f`；C15/C17/C06/C07 实算匹配；M2-C1 无 diff | ✅ |
| D3 | `pre-post.sha256` | 178 B；pre=`ad25fb3c…`（HEAD blob 原始 32577 B 实测）、post=`a7f57ebd…`（工作树 38912 B 实测） | ✅ |
| D4 | `changed-lines.diff` vs `git diff HEAD -- C-16` | 证据文件 15436 B（CRLF 81 行，sha `9ff9a852…`）；同命令重定向输出逐字节相等；原生 LF diff 15355 B、sha `74b94191…`；CRLF→LF 归一化后与原生 diff 逐字节相等 | ✅ |
| D5 | EV 逐文件 sha | 7 项全部实测匹配：carrier `833b3276…`、changed-lines `9ff9a852…`、check-taskpath `d1e251bc…`、check `d1e251bc…`、pins `07c2b60c…`、other-17 `fee1af10…`、pre-post `57c1c2d9…` | ✅ |
| D6 | `check` 日志可复现 | 默认与 `-TaskPath` 均 PASS（3 warnings），EXIT=0；重跑输出与两个日志逐字节相等（各 421 B，sha `d1e251bc…`） | ✅ |
| D7 | 证据边界 | 工作树无 `git add`/`commit`/`push`；本报告写入前 HEAD 未变；`verification/FEA-09/**` 未被改写 | ✅ |

**D 结论**：pin 可复算、其余 17 项不变、pre/post 与 diff/EV/日志全部可复现；证据目录没有陈旧或伪造迹象。**注**：`check` 日志是治理门禁证据，不是 C-16 字节语义的一部分；其 PASS 只用于佐证包内状态。

## 5. E — 载体 §1–§4 与字节一致：**PASS**

| 载体位置 | 载体描述（摘要） | C-16 字节对应 | 判定 |
|---|---|---|---|
| §1 背景与目标 | ①能力 `source.reattest/1`；②条件写 `ReattestSourceLocation`（两列、`last_verified_at` 原值、复用 A 卡唯一 SQL）；③`roots_available` 只读投影（实现延后）；C-15/C-17/C-06/C-07/M2-C1 零字节、1/18 pins | §0:23；§2.5:95–108；§1:31/35；§10:244/253 | ✅ |
| §2.A 头部与 §0 | 状态行 → FROZEN v1.5（历史保留）；日期行补 v1.5；§0 追加能力，缺失/异常不发送、行为与现状一致 | 状态行/日期行/§0:23 逐项在文 | ✅ |
| §2.B §1 `roots_available` | 响应 additive `[bool]`；同序同长；缺失/不可读/身份不符/单根探测异常 → false；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`；旧读者忽略；实现延后 | §1:31 响应表 + §1:35 additive 说明逐项在文 | ✅ |
| §2.C §2.5 | 请求恰 2 键；Core 顺序 host-only → shape → grant live/expiry/revoked + `scope.source_id` → 四键 identity → 条件 UPDATE；Host 义务分离（唯一 live、恰 1 根、路径 normalize、`CreatedAt > RevokedAt`、非 folder、每轮一次；Core 无 path 列）；动作两列 + 原值 + 不取 now + 复用 A 卡唯一 SQL；响应 `{source_id, updated, version}`；幂等/单调；错误复用 §6 零新增 | §2.5:97–108 与上表 B1–B9 逐项一致；响应字段与 `updated:0|1` 在 :106；错误段在 :107；§6 补充在 :212 | ✅ |
| §2.D §6/§10 | §6 增 v1.5 补充句（复用既有码，不新增）；§10 追加条件 ⑦ 与变更记录 v1.5 行 | §6:212；§10:244；§10:253 | ✅ |
| §2.E 冻结记录/矩阵 | pin → v1.5 最终字节；重冻记录；矩阵 C-16 行 → FROZEN v1.5；verify_pins 不改；18/18 | FROZEN §1/§1A/§1B 与矩阵行均为 `a7f57ebd…`/v1.5；§2.E 的记录文本细节不属本报告判定（见范围声明） | ✅（pin/矩阵值） |
| §3 安全与兼容 | 请求由签名 grant 证明同一 source + 同一物理身份；Core 不识路径；只写两列（`last_verified_at` 不变）；拒绝零写；不自动重授权/不重建 identity/撤销后不放行；folder 排除；旧 Host/Core 兼容；无 wire minor/schema/依赖；「契约就绪 ≠ 实现/产品可用」 | §2.5:97–108、§0:23、§1:35、§10:244；§9「不构成实现授权；不证明 AC 达成」 | ✅ |
| §4 风险与回退 | 1/18 pin 须独立复核；reattest 不得扩大为通用修授权入口；实现需先 reattest 后枚举；回退恢复 v1.4 `ad25fb3c…` 与冻结记录/矩阵 | pin 与 pre-image 实测 `ad25fb3c…`；§2.5 红线/宿主义务与「冷启动/下一次 refresh 枚举重新命中」在 :97 | ✅ |

**E 结论**：载体 §1–§4 的**契约层描述**与 C-16 v1.5 字节逐项一致；载体 §3 的 C-15 零字节解释已在本报告 §3 C5 独立背书；载体 §2.E/§6 的记录登记文本不作为本轮通过依据。

## 6. 非阻断 P3 与观察（不改变 approved）

以下三项均**不是本轮新发现**，而是既有复核已接受、在 `a7f57ebd…` 字节中仍然存在的非阻断文字/实现前提项；本轮独立确认其未回退、未放宽安全：

| ID | 位置 | 内容 | 影响 | 处置 |
|---|---|---|---|---|
| P3-1（R3-05） | C-16:103 ④、:60 | 四键 identity 用 `content_digest/size_bytes`，grant facts 用 `sha256/size`；未逐字写键映射，也未写「单点 SQL 只匹配 `content_digest/volume_serial/file_id` 三键，`size_bytes` 由 handler 在调用前比对」 | 实现者可能误以为 SQL 覆盖四键；正确映射后行为不变；错误映射只会 fail-closed，不会放宽授权 | 建议在实现卡/测试写死映射；不要求改 C-16 字节 |
| P3-2（R3-06） | C-16:106 | 幂等句「同 grant 重复调用 → `updated:0` 且零写」未加「无其他写入者介入」前提；共享 SQL 的第三谓词 `last_verified_at IS NOT ?` 在「读原值后、UPDATE 前」被并发 refresh 时可为真（`rowcount=1`，并把旧时间戳写回） | 并发审计时间回退，非授权放宽；单连接/串行写单元下不出现 | 实现应用单写单元/串行化；不要求改 C-16 字节 |
| P3-3（R3-10） | C-16:17 | §0 版本面行仍写 `source-access-wire/1.3`（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…），未提 v1.5/§2.5；读者无法从版本面直接看出新命令归入 `source-access-wire/1.3`（不 bump） | 导航/可读性；无 wire 字段/命令集/版本语义变化 | 建议后续 UNFREEZE 顺手补一句；不要求本轮改字节 |

**其他非阻断观察（不计 finding）**：

1. **未注册/跨 session 的 `grant_id` 错误码**：§2.5:103 ③ 只逐字给 expired/revoked 与 `scope.source_id` 的码；「grant 缺失/会话不符」未逐字写码。可由 §2.4:89 先例与 §2.5:107「身份/条目 `SOURCE_ACCESS_DENIED`」推出，不会新增码。建议实现卡测试覆盖缺失/跨 session 两种拒绝。
2. **§0:23 的「不建文件」**：reattest 本身不创建 secret 文件，该短语可读作对能力缺失路径的防御性说明；不构成语义矛盾，也不影响安全。

## 7. Verdict

- **verdict：`approved`（仅 C-16 v1.5 冻结字节）。**
- **P0=0 / P1=0 / P2=0 / P3=3（非阻断）**；P3 均为既有已接受的字节层文字/实现前提项，本轮独立确认未回退，不构成 blocks。
- **C-16 §10 ⑦ 的「独立 byte-level 复核 approved（P0/P1=0）」在字节层已满足**；记录链/EV 的最终登记与提交由 DSH 按治理流程完成，**不属本报告判定范围**。
- **不要求任何 C-16 字节修改**；若 DSH 决定同批修 P3 文字，应走新的 UNFREEZE，不得在本轮静默改 `a7f57ebd…`。

## 8. 真实性声明

- **只判范围**：本报告**仅判 C-16 v1.5 冻结字节**（`a7f57ebd…`）及其与 FROZEN pin、冻结矩阵、载体 §1–§4 的语义一致性。**本报告不判**载体 §6 的 r1–r8 逐轮记录、EV 文案、FROZEN §9 记录链、PREREQ/AUTO 卡面记录等 DSH 治理记录文本；这些文本的 P2/P3 不作为本报告 verdict 的依据，也不因 `approved` 被追认。
- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `b0a2e9f0-2e0b-4a42-b780-3d7871f46e2c`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1–r8 复核或任何相关实现；只读被审字节与背景材料（C-16、FROZEN、矩阵、载体、C-06/C-15/C-17、只读源码锚点）。
- **只读与写入边界**：未执行 `git add`/`git commit`/`git push`；未修改 C-16/FROZEN/矩阵/载体/卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r9.md`。字节比对临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only/--stat/HEAD`、`git hash-object`、`git rev-parse HEAD:<path>`、`git cat-file blob`、`Get-FileHash -Algorithm SHA256`、.NET 原始字节/LF/CRLF 计数、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、PowerShell 重定向重跑日志与证据文件逐字节比较、`cmd` 原始管道 diff 与 CRLF/LF 归一化比较。
- **事实优先级**：全部断言取自 `59ba5189f` 的 HEAD 与工作树最终字节、只读源码和工具输出；不以聊天记录、旧快照或 r1–r8 的结论替代实测。r1–r8 仅作为被审输入/对照，不作为事实来源。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明。
- **稳定性**：C-16 `a7f57ebd…` 在本轮多次测量（写入报告前）保持不变；HEAD 未变；若本报告写入后 C-16 字节被任何一方修改，本报告的 pin/结论自动失效，须重审。
