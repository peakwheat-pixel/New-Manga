---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE 独立 byte-level 复核 r1（source.reattest/1 + ReattestSourceLocation 条件写 + roots_available）
reviewer: fresh subagent（独立上下文；未参与本 UNFREEZE 起草或前轮复核；只读被审字节）
session: 0b40f4af-0458-4631-b1f7-25856e12784c
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 byte-level 契约复核（fresh context / read-only / 非作者 / 非实现者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE 独立 byte-level 复核 r1

> **结论先行：`changes_requested`，P0=0 / P1=2 / P2=4 / P3=5。**
>
> C-16 v1.5 的**增量范围、pin 可复算性、证据真实性、其余 17 契约零字节**均成立（A/C/D/E/H PASS）；
> `roots_available` 是合法的 additive 只读投影；`ReattestSourceLocation` 的启动方向（显式重授权之后的条件单行事实记录、不自动重授权/不重建 identity/撤销后不放行）与红线表述正确。
>
> 但 §2.5 存在 **2 处阻断级（P1）缺陷**：
> 1. **请求形状在冻结字节内部自相矛盾**：§2.5 示例为 4 键（含未定义、未使用的 `command`/`scope`），而 §10 变更记录与冻结记录 §9 写 2 键 `{source_id, grant_id}`；权威 scope review 推荐的也是 2 键。实现者无法判定 closed shape，AC-LS4B-3 不可判别。
> 2. **三列写入值来源未定义，且"幂等"断言与单点 SQL 谓词冲突**：`registry_id/authorization_generation` 未写明取自 live grant；`last_verified_at` 取值未定义；若取 `now()`，同条目重复调用必然 `rowcount=1`（时间戳不同），与"同条目重复调用 → `updated:0` 且零写（幂等）"及 AC-LS4B-4 直接冲突。
>
> 另有 4 项 P2（⑤/⑥ 是 Host 侧前置却并入 Core"校验顺序"、路径条件在 Core 侧不可判定；形状错误码缺失且 PREREQ D-4 码表不一致；矩阵头部仍写 C-16 v1.4；冻结记录 §2 缺 v1.5 条件行）与 5 项 P3。
>
> 后果：C-16 §10 ⑦"独立 byte-level 复核 approved（P0/P1=0）"**未满足**；v1.5 当前字节不能视为最终冻结字节。保留 FROZEN §9、载体 §6 的 `pending`；按 findings 修订后须重算 sha256/blob id、更新 pin、重跑 `verify_pins` 与 `check`，再由 DSH 追加载体 §6 结论。

## 0. 只读基线、复核字节与实测命令

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef` | `git rev-parse HEAD`（复核开始/结束同值） |
| 工作树 | 3 个已修改 tracked + 2 个未跟踪路径（载体、证据目录）；**HEAD 前后无并发提交** | `git status --porcelain=v1 -uall` |
| 被审 diff 集 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C16.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（22/5、17/8、1/1），加未跟踪 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`、`verification/FEA-11-L-S4-B-PREREQ-1/**` | `git diff --numstat HEAD`、`git status` |
| `verify_pins.ps1` | **PASS (all 18)**；C16 `c7649b7da8de`、C15 `f9e376a0ed4c`、C17 `aefa0fa5b17e` | 实测，EXIT=0 |
| `check.ps1`（默认） | **PASS (3 warnings)**，EXIT=0；与 `logs/check.log` 逐字节一致 | 实测 |
| `check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | **PASS (3 warnings)**，EXIT=0；与 `logs/check-taskpath.log` 逐字节一致 | 实测 |
| 生产代码/测试 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff） | `git diff --name-only HEAD` |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（本卡为契约 PREREQ，无实现字节；且全量测试历史上会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时行为 | **NOT_RUN**（仓库中尚无该命令实现；本复核只判定契约字节可执行性） | 见 §5 |

**复核字节指纹（工作树，SHA-256）**：

| 文件 | sha256 |
|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `c7649b7da8de30f3e5dae2b5ccdef5c0cbcfd0d9112abee9ab839fc30fac7f07` |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `c5e290d122e05cffa81c324eaa4a12bb57ebe95dff37d5f20c8f7a05f69db58b` |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `4373cc6ecb42e5dee30fd9ebf309c1dc5b821f106b4019b1215e98caab079b47` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `156343b73b2ff6c8559949c8d068eae614e4a98a7ed8b411fc6efe08ceb138a8` |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `663d0fee560f84cc89c5a0c15d3f9d70eb5ea764f917a9dcd455900c37f18779` |
| `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | `983d1ab5a4e80d4358107d769268e935efc827f341d4c67cfd4fad8650147c9f` |
| `doc/reviews/C16-V15-BATCH-scope-r1.md` | `53804b3ce5a8be39246eb41af6696c41c301483877d1fb6d83e09fc4e5d1e834` |

**事实校正（不构成缺陷）**：任务书称 PREREQ 卡也在"待提交 UNFREEZE 改动"中；实测该卡已于 `6613cca5b` 新增、`59ba5189f` 修改并处于 HEAD 最终字节（`git status` 干净），**不在工作树 diff 中**。本复核按工作树最终字节审计，卡的最终字节未变。

## 1. A–H 逐项判定

### A. diff 最小性 — **PASS**

- 工作树 diff 仅含 C-16 / FROZEN-C16 / 矩阵三个 tracked 文件，未跟踪项仅载体与证据目录；无 `src/**`、`apps/**`、`tests/**`、`tools/**`、`C-15/C-17/C-06/C-07/M2-C1` 或其载体/冻结记录混入。
- C-16 实际改动逐行对应载体 §2：
  - 头部状态行/日期行（载体 §2.A）→ `C-16:3-4`；
  - §0 能力 `source.reattest/1`（§2.A）→ `C-16:23`；
  - §1 响应 additive `roots_available[]` + 说明 bullet（§2.B）→ `C-16:31,35`；
  - §2.5 全块（§2.C）→ `C-16:95-106`；
  - §6 v1.5 补充句（§2.D）→ `C-16:210`；
  - §10 冻结条件 ⑦ + 变更记录 v1.5 行（§2.D）→ `C-16:242,251`。
- 唯一附加差异是文件尾部空行归一（diff `-` 空行被 v1.5 行替换），非语义改动。
- 未登记缺口不在 C-16，而在冻结记录：`FROZEN:38` 的 v1.4 行被改写、载体 §2.E 未登记该编辑（见 F/P3-1）。
- 结论：C-16 增量最小、无越界文件。**PASS**（载体/卡与证据的完整性另见 G/H）。

### B. 安全语义审查（重点） — **FAIL**（逐条见 §2）

| 子项 | 判定 | 摘要 |
|---|---|---|
| ① 请求 closed shape：无路径/无 registry_id/无 generation | **PASS** | `C-16:100` 仅 `source_id/grant_id/command/scope`；不含 path、registry_id、generation。但 `command`/`scope` 未定义且与 §10/冻结记录冲突（P1-1）。 |
| ② 校验顺序明确 | **PASS（附注）** | `C-16:102` 顺序字面齐全（host-only→shape→grant live/未过期/未撤销+`scope.source_id`→location 四键==grant facts→Host 唯一 live/恰 1 根/normalize 相等/`CreatedAt>RevokedAt`/非 folder→每轮至多一次）。但 ⑤/⑥ 是 Host 侧前置，却并入"Core 命令校验顺序"，未标执行方；"与 Core location 一致"在 Core 侧不可判定（P2-1）。 |
| ③ 拒绝/无匹配零写；只写三列；不新增行/不改 source_id/digest/is_current/binding | **PASS** | `C-16:102-103,105-106` 明写"任一不满足 → typed 拒绝、零写"；动作仅三列、不新增行、不改其它列；与 `library.py:2324-2339` 单点 SQL 的 SET/WHERE 面一致（`is_current=1` 过滤，不写 `is_current`）。 |
| ④ 幂等 / 单调 | **FAIL** | 单调条件与 SQL 一致（`library.py:2329-2330`）；但"同条目重复调用 → `updated:0` 且零写（幂等）"（`C-16:104`）在 `last_verified_at = now()` 时不可实现——SQL 第三谓词 `last_verified_at IS NOT ?` 为真即更新（`library.py:2330-2331`）。P1-2。 |
| ⑤ 错误复用既有闭集、零新增；成功响应 closed shape | **PASS（附注）** | `C-16:105,210` 只列既有码；成功响应 `{source_id, updated, version}` 为 closed shape。但形状错误码未指定（`INVALID_REQUEST` 缺位），且 `version` 未定义（P2-2、P3-3）。 |
| ⑥ folder 排除、`source_reset_registry` 后 limitation | **PASS** | `C-16:106` 明写 folder 排除（L-S4-2）与 reset 后无旧条目可桥接（需重导入）；与 `schema.py:629-646`（无 path 列）、`SourceAccessRegistry.Reset`（`SourceAccessRegistry.cs:112-120`）事实一致。 |
| ⑦ 是否可扩大为通用修授权入口 / 悄悄放宽 | **FAIL（部分）** | 未发现"自动重新授权/自动重建 identity/撤销后放行"的明面放宽：③ 要求 live 且未撤销 grant，④ 四键身份，⑥ 红线，错误路径零写。但 ⑤/⑥ 的"唯一 live、恰一根、路径 normalize、时间序、每轮一次"全部是 Host 侧条件，Core 命令边界无法自证；若实现者把 ⑤ 当 Core 校验，只能跳过或伪造，**"同路径"守卫实际落点不明**（P2-1）。 |

### C. `roots_available` — **PASS**

- additive：与 `roots[]` 同序同长、`[bool]`、旧读者忽略；不改变既有字段形状/命令集（`C-16:31,35`）。
- 只读：仅投影"该根当前可用性"，明确"不代表授权或恢复动作"；不新增命令/能力/错误码。
- fail-closed：文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`、不返回部分数组（`C-16:35`）；与 C-15 `:312` 的文件级/根级拆分一致。
- 无路径/identity 泄露：值为 bool，无 path、无 volume/file、无 registry 内身份。
- 实现延后明示：`C-16:35`、载体 `:20`、实现卡 `:82` 三处均写明"无消费者前不接线/B2 另卡"。
- 附注：未写"单根 probe 异常 → false"与"至多每根一次 probe"（P3-4），但这两点属实现卡 AC-B2-6 范畴，不影响字段冻结。

### D. 不变量零改动 — **PASS**

- `git diff HEAD` 无 C-15/C-17/C-06/C-07/M2-C1 及其载体/冻结记录；无 `src/apps/tests/tools` 改动；HEAD 未变。
- `verify_pins` 18/18：C16 仅本字节新值，其余 17 与其冻结记录 pin 逐项一致（`other-17-pins.txt` 17 行 + `SUMMARY changed=0`）。
- 新增 diff 行中出现的错误码仅 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`，全部在 `C-16:189-207` 既有表内；无新码。
- 无 wire minor：§0 版本面表未改（仍 `PROTOCOL_MINOR=3`）；新增行无 `PROTOCOL_MINOR` 字样。
- 无 schema/依赖：无 DDL/迁移/依赖文件改动；`C-16:103` 明确复用 A 卡唯一 SQL、不新增第二份。
- 能力门禁明确：`C-16:23` 明写 Host 在 B1 后探测，缺失/探测异常 → 不发送、不铸 grant、target 仍 typed skip；`C-16:20` 的旧 Host 不发送新命令口径保留。
- 附注：新 host-control 命令未登记到 M2-C1 command catalog，与 v1.3 `AuthorizeSourceReadForRun` 先例一致（该先例亦未改 M2-C1），本卡明示 M2-C1 零字节；不视为缺陷，但属已知 inventory 滞后。

### E. pin 可复算 — **PASS**

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `c7649b7d…`（pre-post post / FROZEN:16 / matrix） | `c7649b7da8de30f3e5dae2b5ccdef5c0cbcfd0d9112abee9ab839fc30fac7f07` | ✅ |
| `git hash-object` | `008fb484…`（FROZEN:17） | `008fb484fe105aba046aa1f065482624902d5871` | ✅ |
| HEAD v1.4 blob sha256（pre） | `ad25fb3c…`（pre-post pre） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` | ✅ |
| `verify_pins.ps1` | 18/18、C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0 | ✅ |
| 抽查其余 4 pins（实际文件 vs 冻结记录） | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 均 match=True | ✅ |
| `other-17-pins.txt` 真实性 | 17 项、changed=0、@HEAD | 17 行 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |

### F. 冻结记录 / 矩阵一致性 — **FAIL**

- 版本主链一致：C-16 头部 v1.5（`C-16:3`）、FROZEN §1 v1.5（`FROZEN:15-18`）、矩阵行 v1.5（`MATRIX:37`）、证据 pre/post 一致。
- **FAIL-1（P2-3）**：矩阵头部状态行仍写 `C-16 v1.4`（`MATRIX:3`），与 `MATRIX:37` 的 v1.5 行冲突；同一次 UNFREEZE 内未同步。
- **FAIL-2（P2-4）**：FROZEN §2"冻结条件逐条核验"只有 v1.0/v1.1/v1.3/v1.4 行（`FROZEN:44-49`），无 v1.5 行；v1.5 条件只在 §9 `pending`（`FROZEN:109`）出现，条件核验面不完整（v1.3/v1.4 均有独立行，先例不一致）。
- **FAIL-3（P1-1 的跨文档面）**：`FROZEN:108` 把 §2.5 请求写成 `{source_id, grant_id}`（2 键），与 `C-16:100` 的 4 键冲突。
- 历史 pin 保留：v1.4 `ad25fb3c…`、v1.3 `7c355ccb…`、v1.1 `0b9511a5…`、v1.0 `6e7f8d3d…` 均在 §1B/§9 保留（`FROZEN:35-38,111`）→ PASS。
- §1A 三口径声明保留且未改（`FROZEN:22-25`）→ PASS。
- 无"复核前预填 approved"：载体 §6、FROZEN §9、EV 均写 `pending`（`carrier:57`、`FROZEN:109`、`EV:4`）→ PASS。
- 附注：`FROZEN:38` 的 v1.4 行被改写（删除 r1 计数与 session/head），载体 §2.E 未登记；信息仍完整保留在 `FROZEN:97`（P3-1）。

### G. 载体 / 卡不夸大 — **PASS（附 P3）**

- 未把契约就绪写成实现/产品可用：载体开篇"须经独立复核 + DSH 重新冻结后方可视为最终字节"（`carrier:3`）；C-16 §9"不构成实现授权；不证明 AC 达成"（`C-16:238`）；FROZEN §3"不构成实现授权、运行时协议已实现、产品 AC 已达成"（`FROZEN:55`）。
- 保留"B1 显式动作之后才算零交互"：实现卡 `:49`（"用户完成 B1 的显式『重新授权』动作之后…不是撤销后自动恢复"）、PREREQ D-7（`:52`）。
- 保留"无自动恢复/自动重新授权"：载体 §3（`:39`）、C-16 §2.5 红线（`:106`）、实现卡 limitation（`:85`）。
- 保留"C-15 解释条件性"：载体 §3"若后续 Review 不背书则升 2 pins"（`carrier:41`）、PREREQ ZCode 记录（`:101`）。
- 保留"B2 实现延后"：载体 §2.B（`:20`）、C-16:35、实现卡 limitation（`:82`）。
- 明写 1 pin 与 C-15/C-17 零字节：载体 §1/§2.E（`:11,33-35`）、C-16 §10 ⑦（`:242`）、矩阵条件 ②（`:37`）。
- 附注（P3-5）：PREREQ AC-T5 要求"明写『契约就绪 ≠ 实现/产品可用』"（`PREREQ:90`），但载体正文未出现该字面句（仅 `carrier:52` 把它列为核对项）；属可补的文案项，不影响结论。

### H. 证据真实性 — **PASS**

- `pre-post.sha256`：pre = HEAD v1.4 `ad25fb3c…`（实测 `git cat-file blob HEAD:…` 的字节 sha256），post = 工作树 `c7649b7d…`（实测）→ 一致。
- `changed-lines.diff` 与 `git diff HEAD -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`：按 `\r\n→\n` 归一后**逐字节相等**（actual 13809 bytes / evidence 13888 bytes，差 79 = 79 行的 CRLF）；证据文件 sha256 = `3aa79181…`，与 EV 表一致。
- 日志可复现：重跑 `verify_pins.ps1` 输出与 `logs/pins.log` 逐字节一致；重跑 `check.ps1`（默认与 `-TaskPath`）分别与 `logs/check.log`、`logs/check-taskpath.log` 逐字节一致（两者本就同文本，因为默认模式也打印当前 Task 行——已实测确认，非复制粘贴伪造的必然证据，但内容真实）。
- EV 表 7 个文件 hash 全部实测匹配（carrier `156343b7…`、changed-lines `3aa7918…`、check/check-taskpath `d1e251bc…`、pins `7e260a4d…`、other-17 `fee1af10…`、pre-post `d5480635…`）。
- `verification/.../carrier.md` 与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` 逐字节相同（同 sha `156343b7…`）。
- 证据目录文件集（8 个）与载体 §7 清单完全对应，无多余文件。
- 附注：日志不含命令行/时间戳，因此"何时、用何命令产生"只能由本次重跑复现佐证；复现结果一致，判 PASS。

## 2. 安全语义逐条判定（展开）

### ① 请求 closed shape
`C-16:100`：`{"source_id", "grant_id", "command", "scope"}`。**无 path、无 registry_id、无 generation** → 满足 B① 的字面要求。
但 `command`（`<PipelineCommand>`）与 `scope`（Run 的 book/chapter/page/region/page_selection 展开器）**在 §2.5 的校验、动作、响应中完全没有使用**，也没有任何语义说明；这是从 §2.4 复制过来的形状（`C-16:82`）。权威 scope review 推荐的 b3 形状只有 `{source_id, grant_id}`（`C16-V15-BATCH-scope-r1.md:127`）。→ **P1-1**。

### ② 校验顺序
`C-16:102` 的 ①→⑥ 顺序明确，覆盖 host-only、shape、grant live/未过期/未撤销 + `scope.source_id`、location 四键 vs grant facts、Host 唯一 live/恰一根/normalize/`CreatedAt>RevokedAt`/非 folder、每轮至多一次。**顺序本身 PASS**。
问题在于执行方：这是一条 **Host→Core** 命令，Core 没有 Host Registry（§0"Host 是唯一授予方并完成 scope→授权根解析"，`C-16:19`），因此 ⑤/⑥ 不可能由 Core 校验；`source_locations` 也没有 path 列（`schema.py:629-646`：`location_id/source_id/registry_id/authorization_generation/content_digest/volume_serial/file_id/size_bytes/mtime_hint/observed_at/last_verified_at/is_current/created_at`），"其根路径 normalize 后与 Core location 一致"在 Core 侧**不可判定**。scope review 的原意是 Host 侧比较"旧条目根 vs live 条目根"（`C16-V15-BATCH-scope-r1.md:138`）。→ **P2-1**。

### ③ 零写与三列
`C-16:102` 末句"任一不满足 → typed 拒绝、零写"；`C-16:103` 动作只有三列 SET；`C-16:106` 红线。与单点 SQL（`library.py:2324-2339`）一致：SET 三列、WHERE `source_id/content_digest/volume_serial/file_id/is_current=1`，不写 `is_current`，不插行。**PASS**。
注意：SQL 的 WHERE 不含 `size_bytes`，而 ④ 要求四键（含 `size_bytes`）相等；因 `content_digest` 为内容 sha256、`size` 由内容决定，实际风险极低，但 handler 必须在 SQL 之外显式比对 `size_bytes`（P3-2）。

### ④ 幂等 / 单调
单调：SQL `(registry_id <> ? OR authorization_generation <= ?)`（`library.py:2329-2330`）→ 同 registry 代次不倒退；跨 registry 不受代次限制（与 §2.5"跨 registry 允许 1"及 A 卡 AC-LS4-5 一致）。**PASS**。
幂等：SQL 第三谓词 `(registry_id <> ? OR authorization_generation <> ? OR last_verified_at IS NOT ?)`（`library.py:2330-2331`）。若 `last_verified_at` 取 `now()`：
- 第 2 次调用时 registry/generation 已相等，但新 `now()` 与行内值不同 → 第三谓词为真 → `rowcount=1` → `updated:1`，**不是零写**；
- 只有传入与行内完全相同的 `last_verified_at` 时才 `rowcount=0`——但那等于不更新该列，与"更新三列"矛盾。
`C-16:104` 未定义 `last_verified_at` 的来源；`C-16:103` 也未定义 `registry_id/authorization_generation` 取自哪里（协议内唯一可用来源是 live grant 的 `registry_id/generation`，见 `C-16:49-50`，但正文没写）。→ **P1-2**。
另：同 registry 代次回退也会走 `rowcount=0`，与"已最新"的 `updated:0` 混同；§2.5 只说 0 是幂等成功，未说回退是 0 还是 typed，建议一并明确。

### ⑤ 错误闭集与成功响应
`C-16:105` 列出的 5 个码全部在 §6 表内；`C-16:210` 明确"不新增码"、给出映射。成功响应 `{source_id, updated, version}` 为 closed shape。**PASS**。
缺口：② 的 closed shape 错误（未知键/缺键/类型错误）未指定码；§2.4 的同位置明确 `INVALID_REQUEST`（`C-16:87`），§2.5 没有；§6 补充句也未列 `INVALID_REQUEST`。→ **P2-2**。`version` 的取值（version_id？最新 version？可能为 null？）未定义 → P3-3。

### ⑥ folder 与 reset limitation
`C-16:106` 明确 folder 源排除（L-S4-2）与 `source_reset_registry` 后无旧条目可桥接（需重导入）。与 `SourceAccessRegistry.Reset`（`SourceAccessRegistry.cs:112-120`）事实一致（reset 创建空 Registry，旧条目不存在）。**PASS**。
执行方：folder 排除同样落在 ⑤（Host 侧）；建议在 Core 侧也显式拒绝 `sources.kind == folder`（Core 可判定），以免完全依赖 Host。归入 P2-1。

### ⑦ 扩面 / 放宽
未发现明面的"自动重新授权/自动重建 identity/撤销后放行"：
- grant 必须 live 且未撤销（③）；撤销 → `SOURCE_GRANT_REVOKED`，零写；
- 四键身份必须与当前 location 行相等（④），同路径换文件/换 inode 被拒；
- 不创建/复活/延长 grant，不写 Host Registry，不新增 source/version/entry，不发布资源（`C-16:103,106`）；
- folder 排除、reset 后不桥接（⑥）。
**但**：同一路径的"唯一 live 条目"与"时间序"是 Host 侧条件；若 Host 实现放宽（多 live、忽略 `CreatedAt>RevokedAt`、把 live 根换成同 inode 的另一路径），Core 命令无法察觉。契约目前只靠 ⑤ 的字符串 + Host AC 兜底，**没有在 Core 边界形成可自证的不变量**。→ **P2-1**（不是"悄悄放宽"，而是"守卫落点未定义"）。

## 3. Findings 表

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P1-1** | P1 | `C-16:100` vs `C-16:251`、`FROZEN:108`；载体 `:23`、PREREQ `:65`；scope review `:127` | §2.5 请求示例为 4 键（含未定义、未使用的 `command`/`scope`），§10 变更记录与冻结记录 §9 为 2 键，权威 scope review 推荐 2 键；`command`/`scope` 无语义、无校验、无用途；形状错误行为未写 | 二选一：①删除 `command`/`scope`，恢复 b3 的 2 键，并同步 C-16 §10、FROZEN §9、载体 §2.C、PREREQ I-2；②若确有用途，定义必填性/语义/与 grant 的关系并加入校验。同时写明"未知键/缺键/类型错误 → `INVALID_REQUEST`" |
| **P1-2** | P1 | `C-16:103-104`；SQL `library.py:2324-2339` | 三列写入值来源未定义：`registry_id/authorization_generation` 未写"取自 live grant 的 `registry_id/generation`"；`last_verified_at` 取值未定义。若取 `now()`，同条目重复调用必然 `updated:1`，与"重复调用 → `updated:0` 且零写（幂等）"及 AC-LS4B-4 冲突；若取旧值，又不算"更新该列" | 明确：`registry_id ← grant.registry_id`、`authorization_generation ← grant.generation`、`last_verified_at ← <固定可复算值或 now() 的明确定义>`；据此改写幂等条款（"仅当三列均不变才 0"或"允许刷新审计时间、`updated` 表示 auth 列是否变化"），并让 AC-LS4B-4 可判别。另明确同 registry 代次回退是 `updated:0` 还是 typed |
| **P2-1** | P2 | `C-16:102` ⑤/⑥；`schema.py:629-646` 无 path 列 | ⑤/⑥ 是 Host 侧前置，却并入 Core 命令"校验顺序"且未标执行方；"live 根 normalize 与 Core location 一致"在 Core 侧不可判定（location 无 path）；folder/唯一 live/时间序/每轮一次同理。若按字面实现，只能跳过或伪造，削弱"同路径"守卫 | 拆成"Host 发送前置（唯一 live、恰 1 根、live 根与旧已撤销条目根 normalize 相等、`CreatedAt>RevokedAt`、非 folder、每轮至多一次）"与"Core 校验（①②③④，可选加 folder/kind）"两段；路径比较明确由 Host 执行、比较对象是旧条目根；Core 只按 grant 字段与 location 四键写 |
| **P2-2** | P2 | `C-16:102,105,210`；PREREQ `:49` | §2.5 形状错误未指定码（§2.4 为 `INVALID_REQUEST`）；§6 补充句未列 `INVALID_REQUEST`；PREREQ D-4 的码表含不相关的 `SOURCE_BUDGET_EXCEEDED`、缺 `SOURCE_GRANT_EXPIRED`/`SOURCE_REGISTRY_BUSY`，与 §2.5/§6 不一致 | 写明形状错误 → `INVALID_REQUEST`；PREREQ D-4 与 §2.5/§6 对齐（删 BUDGET_EXCEEDED，补 EXPIRED/BUSY） |
| **P2-3** | P2 | `MATRIX:3` vs `MATRIX:37` | 矩阵头部状态行仍写"C-16 v1.4"，与同文件 C-16 行 v1.5 冲突 | 改为 C-16 v1.5（本次 UNFREEZE 一并修） |
| **P2-4** | P2 | `FROZEN:44-49`、`FROZEN:109` | 冻结记录 §2 条件表缺 v1.5 行（v1.3/v1.4 均有独立行），v1.5 条件只在 §9 `pending`；条件核验面不完整 | 在 §2 增 v1.5 行（状态 `pending（r1）`，复核 approved 后回填），保持与 v1.3/v1.4 同构 |
| **P3-1** | P3 | `FROZEN:38`；载体 `:33` | §1B 的 v1.4 行被改写（删除 r1 计数与 session/head），载体 §2.E 未登记该编辑；信息仍在 `FROZEN:97` | 在载体 §2.E 登记该行编辑，或恢复原 v1.4 行文本（与 §8 去重可保留） |
| **P3-2** | P3 | `C-16:102` ④；`library.py:2327-2328` | ④ 用 `content_digest/size_bytes`，grant facts 用 `sha256/size`（`C-16:60`），映射未写明；`size_bytes` 不在单点 SQL 谓词中，需 handler 显式比对 | 写明键映射；注明"SQL 只匹配三身份键，`size_bytes` 由 handler 在调用前比对" |
| **P3-3** | P3 | `C-16:104` | 响应 `version: "<current source version>"` 未定义（version_id？最新 version？是否可为 null？）；`updated` 与 `version` 的组合语义未述 | 定义为当前 `source_versions.version_id`（或明确字段），并说明 `updated:0` 时仍返回当前 version |
| **P3-4** | P3 | `C-16:35` | `roots_available` 只写"缺失/不可读/身份不符 → false"，未写 probe 异常 → false、每根至多一次 probe（scope review AC-B2-6 要求） | 在 §1 补一句"单根探测异常按 `false` 处理、每次调用每根至多探一次、锁外探测" |
| **P3-5** | P3 | 实现卡 `:69-78`；PREREQ `:49,90` | 实现卡 AC 编号顺序为 1..7、9、10、8；PREREQ D-4 零字节清单漏 C-06（I-2/AC-T1 均含）；AC-T5 要求的"契约就绪 ≠ 实现/产品可用"未在载体正文明写 | 调整 AC 编号顺序；D-4 补 C-06；载体 §1 或 §3 补该字面句 |

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=2 / P2=4 / P3=5）。
- C-16 §10 ⑦ 的冻结条件"独立 byte-level 复核 approved（P0/P1=0）"**未满足**；C-16 当前字节（`c7649b7d…`）**不是可长期保留的最终冻结字节**。FROZEN §9、载体 §6 的 `pending` 必须保持；矩阵行的"①v1.5 独立 byte-level 复核 approved"在 r1 下为未满足条件——这属于"先冻结字节、后复核"的既有流程，但 r2 通过前不得把 v1.5 当作已验收。
- 建议处置顺序：
  1. 修 **P1-1、P1-2**（以及同一轮可低成本完成的 P2-1/P2-2/P2-3/P2-4、P3 文案项）；
  2. 重算 C-16 sha256 与 `git hash-object`，更新 FROZEN §1/§1B/§2/§9 与矩阵（含头部 v1.4→v1.5）；
  3. 重跑 `verify_pins.ps1`（18/18）与 `check.ps1`（默认 + `-TaskPath`），重生成 `changed-lines.diff`/pre-post/日志/EV；
  4. r2 独立复核 approved 后，再由 DSH 在载体 §6 追加结论（append-only）。
- 不需要修改 C-15/C-17/C-06/C-07/M2-C1：本复核未发现需要其字节变更的语义问题；P1-1/P1-2 均可在 C-16 内部（及 FROZEN/矩阵/载体/卡）闭合，**仍为 1/18 pins**。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `0b40f4af-0458-4631-b1f7-25856e12784c`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、前轮复核或任何相关实现；只读被审字节与背景只读材料。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/实现卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r1.md`。字节比对用的临时文件只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --numstat HEAD`、`git diff HEAD -- <C-16>`、`git hash-object`、`git cat-file blob HEAD:<C-16>`（经 `cmd /c` 重定向取原始字节）、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、Python 3.14 字节级 diff/哈希比对。
- **代码只读锚点**：`src/application/sources/scanner.py:96-177`、`src/infrastructure/sqlite/library.py:2293-2353`、`src/infrastructure/sqlite/schema.py:629-646`、`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1505-1512/1561-1610/2162-2169`、`SourceAccessRegistry.cs:34-52/100-110`、`src/application/importing/referenced/runtime.py:658-698`、`src/application/sources/service.py:954-987`。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。上表与 §1 的 PASS 不对这些未跑项作任何声明。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节与只读代码/工具输出；本报告不采用聊天记录或旧快照作为事实来源。
