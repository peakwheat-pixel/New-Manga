---
task: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE r1 返修后的 r2 窄面 byte-level 复审（source.reattest/1 + ReattestSourceLocation 条件写 + roots_available）
reviewer: fresh subagent（r2；独立上下文；未参与本 UNFREEZE 起草、r1 复核或任何相关实现；只读）
session: c7a9c263-5f4b-4124-b572-b7ca6ab11f18
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 byte-level 契约复审（fresh context / read-only / 非作者 / 非实现者 / 非 r1 复核者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 59ba5189f239b580897e6b6a05146f66348125ef
verdict: changes_requested
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE r1 返修的 r2 窄面 byte-level 复审

> **结论先行：`changes_requested`，P0=0 / P1=1 / P2=4 / P3=6。**
>
> **r1 的 P1-1 已闭合**：§2.5 请求在 C-16 §2.5、§10 变更记录、冻结记录 §9、载体 §2.C、PREREQ I-2 五处一致为**恰 2 键** `{source_id, grant_id}`，形状错 → `INVALID_REQUEST` 明确。**P2 的校验拆分与错误码对齐、P3 的 `version` 定义与 roots 探测异常也已落地。**
>
> **但 P1-2 未闭合，且被"修成了另一种阻断缺陷"**：§2.5 把 `last_verified_at` 定为 `grant.created_at`——该字段**不在冻结的 source-read grant 载荷里**（C-06 v1.2 grant 字段表无 `createdAt`；C-16 §2 grant JSON 无该键；Core `_ENVELOPE_FIELDS` 是闭集且严格拒绝多余键）。`created_at` 只存在于 **Host Registry 条目**（`source_list_roots`/`ListSourceRoots` 的 `created_at`），Core 在只带 `{source_id, grant_id}` 的请求里**取不到它**。照字面实现只能（a）给 grant 加签名新字段 → wire 字段新增 + C-06 字节变更 + 2/18 pins，与 §10 ⑦、矩阵 ②、载体 §1/§3 的"零 wire / C-06 零字节 / 1 pin"直接冲突；或（b）由 Core 自己造时间 → 与同句"不取 `now()`、不做任何时钟推断""均为……签名的稳定值"矛盾。**故 r1 P1-2 判 OPEN，重定为 N1（P1）。**
>
> 另有 4 项 P2：矩阵头部仍写 `C-16 v1.4`（矩阵字节相对 r1 **零改动**）；冻结记录 §2 的 v1.5 行编辑把**第 6 行（v1.4）的证据单元格删掉并接到第 7 行末尾**，造成表格列数损坏且 v1.4 证据错挂到 v1.5 行；载体 §6 仍写 `r1：pending`（未落 r1 `changes_requested` 与处置，也无 r2 pending）；§2.5 ① 把"application 面拒绝"映射为 `INVALID_REQUEST`，与 §2.4 ①、C-17/M2-C1 口径及 Core 实现（`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）冲突。
>
> 后果：C-16 §10 ⑦"独立 byte-level 复核 approved（P0/P1=0）"**再次未满足**；当前字节 `39da9766…` 不是最终冻结字节。FROZEN §9 与载体 §6 的 `pending` 必须保留；按 findings 修订后须**重算 sha256/hash-object、更新 pin、重跑 `verify_pins`/`check`、重生成证据**，再走 r3（或 DSH 裁定的等价独立复核）。
>
> 已实测通过的部分（不改判）：`39da9766…` = FROZEN pin = `git hash-object 6f875960…`；`verify_pins` **18/18**；其余 17 项真实不变；`check.ps1`（默认 + `-TaskPath`）PASS 且日志逐字节可复现；`changed-lines.diff` 与 `git diff HEAD` 归一化后逐字节相等；C-15/C-17/C-06/C-07/M2-C1 与 `src/apps/tests/tools` 零 diff；安全红线未被放宽。

## 0. 只读基线、复核字节与实测

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `59ba5189f239b580897e6b6a05146f66348125ef`（复核开始/结束同值，无并发提交） | `git rev-parse HEAD` |
| 工作树改动集 | 4 个已修改 tracked（C-16 / FROZEN-C16 / 矩阵 / PREREQ 卡）+ 10 个未跟踪（载体、r1 报告、证据目录 8 文件）；**本报告写入后新增 r2 报告 1 个未跟踪项**，其余不变 | `git status --porcelain=v1 -uall` |
| 生产/测试/工具 | **零改动**（`src/**`、`apps/**`、`tests/**`、`tools/**` 均不在 diff） | `git diff --name-only HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0；C16 `39da9766475c`、C15 `f9e376a0ed4c`、C17 `aefa0fa5b17e` | 实测；与 `logs/pins.log` 逐字节一致 |
| `check.ps1`（默认 / `-TaskPath`） | **PASS (3 warnings)**，EXIT=0；两者与 `logs/check.log`、`logs/check-taskpath.log` 逐字节一致（421 bytes） | 实测 |
| 全量 `pytest tests` / `dotnet test` / gated IPC | **NOT_RUN**（契约 PREREQ，无实现字节；全量测试会改写 tracked `verification/FEA-09/**`，本轮不冒写入风险） | 见 §5 |
| `ReattestSourceLocation` 运行时 | **NOT_RUN**（仓库中尚无该命令实现；本复审只判契约字节可执行性） | 见 §5 |
| push | **NOT_RUN**（只读；未 `git add/commit/push`） | 见 §5 |

**复核字节指纹（工作树 SHA-256）与 r1 对比**：

| 文件 | r1 审的字节 | 本次（r2）字节 | 变化 |
|---|---|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `c7649b7d…` | `39da9766475cb2e18f0040c29a4876db89a4cdb16e5632be46a494ed4672083d` | 已改 |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | `c5e290d1…` | `93612cfc687979cca46a4b3ba510027f825dab7b4ae1fb624a214ebcad3367ea` | 已改 |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `4373cc6e…` | `4373cc6ecb42e5dee30fd9ebf309c1dc5b821f106b4019b1215e98caab079b47` | **未改（与 r1 逐字节相同）** |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | `156343b7…` | `3de606fb016111a30fb00bc84f7111a3cf135e625eadeb0ebbd34f2e85102dc6` | 已改（= `verification/**/carrier.md`） |
| `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | `663d0fee…` | `332fbcec24a49249faa4208248cf76a0205ed85203d5157d924338dfef5a8a42` | 已改（numstat 3/3；仅 D-4 与 I-2 两处） |

**pin / 证据实测**：

| 核对 | 期望 | 实测 | 结果 |
|---|---|---|---|
| C-16 工作树原始字节 sha256 | `39da9766…`（FROZEN:16、FROZEN §9:112、pre-post post） | `39da9766475cb2e18f0040c29a4876db89a4cdb16e5632be46a494ed4672083d`（38435 bytes，LF，0 个 CRLF） | ✅ |
| `git hash-object` | `6f875960…`（FROZEN:17） | `6f87596036287ced9e780b58ffa9aa5b00370f88` | ✅ |
| `git cat-file blob` 内容 sha256（LF 原始字节） | 与 FROZEN:18 一致 | `39da9766…`（38435 bytes） | ✅ |
| HEAD v1.4 blob sha256（pre） | `ad25fb3c…`（pre-post pre、FROZEN §1B:37） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc`（32577 bytes） | ✅ |
| `verify_pins.ps1` | 18/18，C16 新值、其余 17 原值 | `PIN AUDIT: PASS (all 18)`，EXIT=0 | ✅ |
| 独立抽查 4 个未重签 pin（文件实算） | 不变 | C15 `f9e376a0ed4c…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`、C07 `3fdb44e49afe…` 全部 match | ✅ |
| `other-17-pins.txt` | 17 项、`changed=0`、@HEAD | 17 行 + `SUMMARY: 17 contracts, changed=0`，标注 `@ 59ba5189f` = 实测 HEAD | ✅ |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 归一化后逐字节相等 | actual 14878 B / evidence 14959 B（差 81 = 81 行 CRLF）；`\r\n→\n` 后 sha256 同为 `3530d8438fabddd39e4f57f4d6786ee2a9fdb8b5633a87a453fe305c7d28c3be` | ✅ |
| EV 表逐文件 sha | 7 项 | carrier `3de606fb`、changed-lines `9caa57c1`、check/check-taskpath `d1e251bc`、pins `ba941aa9`、other-17 `fee1af10`、pre-post `3490a654` 全部实测匹配 | ✅ |
| 证据目录文件集 | 载体 §7 清单 | 8 个文件，一一对应，无多余 | ✅ |
| `verification/**/carrier.md` vs `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` | 逐字节相同 | 同 sha `3de606fb…`、同 6133 bytes | ✅ |
| 日志可复现 | 重跑输出 = log | pins 408 B / check 421 B / check-taskpath 421 B，三者重跑后**逐字节相等** | ✅ |

**事实校正（不构成缺陷）**：任务书把"矩阵"列为本轮待提交修订的一部分；实测矩阵**自 r1 起零字节改动**（`4373cc6e…` 与 r1 报告 §0 记录完全相同），`git diff HEAD` 仍只有原 v1.5 那一行改动——r1 的 P2-3（头部 v1.4）因此**未被处置**（见 §2）。

## 1. A–G 逐项判定

### A. P1-1 关闭：§2.5 请求恰 2 键 — **PASS**

| 核对 | 证据 | 结果 |
|---|---|---|
| C-16 §2.5 标题与正文 | `C-16:98` "请求（closed shape，**恰 2 键**）"；`C-16:100` JSON 仅 `{"source_id", "grant_id"}` | ✅ |
| 无 `command`/`scope`/路径/`registry_id`/`generation` | `C-16:102` "无 `command`/`scope`（源级操作，不是页选择）"；`C-16:103` ②"无路径/无 registry_id/无 generation" | ✅ |
| 形状错 → `INVALID_REQUEST` | `C-16:102` "缺键/多键/类型错 → `INVALID_REQUEST`"；`C-16:103` ②同 | ✅ |
| §10 变更记录 | `C-16:253` "请求 `{source_id, grant_id}`" | ✅ |
| 冻结记录 §9 | `FROZEN:110` "请求 `{source_id, grant_id}`" | ✅ |
| 载体 | `carrier:23` "closed shape **恰 2 键** `{source_id, grant_id}`；无 command/scope/路径/registry_id/generation 入参；形状错 → `INVALID_REQUEST`" | ✅ |
| PREREQ 卡 | `PREREQ:65` "**恰 2 键** `{"source_id": …, "grant_id": …}`（无 command/scope/路径/registry_id/generation 入参；形状错 → `INVALID_REQUEST`）" | ✅ |

五处文字互不矛盾，`command`/`scope` 已从 §2.5 全段消失（不再出现于请求、校验、动作、响应、错误任何一句）。r1 P1-1 的"AC-LS4B-3 不可判别"已解除（实现卡 `AC-LS4B-3` 的"请求 closed shape"现在有唯一解）。**PASS**。

### B. P1-2 关闭：三列写入值来源与幂等/单调 — **FAIL（N1，P1）**

先说已修对的部分（应记入）：

- `C-16:105` 把三值来源写成"**live grant 载荷中的值**"：`registry_id = grant.registry_id`、`authorization_generation = grant.generation`、`last_verified_at = grant.created_at`，并明写"Core 不取 `now()`、不做任何时钟推断"；`carrier:26` 与 `PREREQ:67` 同口径。
- `C-16:106` 的幂等解释在**给定稳定值**的前提下与单点 SQL 一致：同一 grant 第二次调用时三列全等 → 第三谓词 `(registry_id <> ? OR authorization_generation <> ? OR last_verified_at IS NOT ?)` 为假 → `rowcount=0` → `updated:0` 零写。这正好命中 r1 指出的"若取 `now()` 必然 `rowcount=1`"的冲突，**冲突本身已消除**。
- 单调表述与 SQL 一致：`library.py:2329` 的 `(registry_id <> ? OR authorization_generation <= ?)`（行侧旧值 vs 新值）只允许**同 registry 新代次 ≥ 旧代次**、跨 registry 放行，与 `C-16:106`"同 registry 不倒退，跨 registry 允许 1"逐字对应。

**但 `grant.created_at` 不存在**，故"三列写入值明确取自 live grant 载荷"不成立：

| 独立锚点 | 事实 |
|---|---|
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:39`（C-06 v1.2，FROZEN，pin `99831a20ffd6…`） | grant 字段（v1.1 冻结）＝`{grantId, registryId, generation, expiresAt, scope{…}, budget{…}, entries[…], secretRef?, signingKey, signature}`——**无 `createdAt`/`created_at`**。C-06 里的 `createdAt` 只出现在**Registry 条目**（`:29` 条目字段、`:51` `ListSourceRoots` 响应），不是 grant。 |
| `C-16:43-67` §2 `RegisterSourceReadGrant` JSON（本轮 diff **未改**） | 键集恰为 `grant_id/session_id/operation/scope_class/registry_id/generation/expires_at/budget/scope[/secret_ref]/signing_key/signature`——**无 `created_at`**。 |
| `src/infrastructure/resource_channel/source_read_refs.py:62-66`、`:124-131` | Core 的 `_ENVELOPE_FIELDS` 是**闭集**，`register()` 要求 `_ENVELOPE_FIELDS <= set(payload) <= _ENVELOPE_FIELDS | {"secret_ref"}`；`_SourceReadGrant`（`:69-84`）也只落 `grant_id/session_id/registry_id/generation/expires_at/…`。**加 `created_at` 会被判 `SOURCE_ACCESS_DENIED`（payload malformed）。** |
| `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:470-499` | Host 铸造 payload 的键集与上表一致，签名 = payload 减去 `signing_key`/`signature`（`:494-498`）——`created_at` 不存在，故"写入并签名"没有对象。 |

后果（不是措辞问题，是可执行性/门禁问题）：

1. **不可实现**：Core 只收到 `{source_id, grant_id}`，无法从 grant 取出 `created_at` → 三列中的 `last_verified_at` 无值可取；实现者只能臆造。
2. **照字面补齐会破门禁**：给 grant 加签名 `created_at` = 新的 wire 字段 → C-06 v1.2 的 grant 字段表字节变更（C-06 UNFREEZE）+ Core/Host 两侧改动 → 至少 **2/18 pins**，与 `C-16:244`（§10 ⑦"C-15/C-17/C-06/C-07/M2-C1 与其余 17 pins 零改动，无新错误码/无 wire minor"）、`MATRIX:37`②、`carrier:11`（"C-15/C-17/C-06/C-07/M2-C1 零字节；1/18 pins"）冲突。
3. **由 Core 造时间则自相矛盾**：同句已写"不取 `now()`、不做任何时钟推断"。注意现有 A 卡两个生产者恰恰用 Core `now`（`src/application/sources/service.py:979-987`、`src/application/importing/referenced/runtime.py:651-659/689-699`），所以"同列混写不同来源"本身也需要一句话交代。

→ **r1 P1-2 判 OPEN（重定 N1，P1）**。它的修法必须在"加签名字段（2 pins）/改幂等语义（可能需动 A 卡 SQL 或 `updated` 定义）/放弃 `last_verified_at` 更新"三者中择一并如实记账；当前文本三者都没选。

### C. P2 关闭 — **FAIL（矩阵头未改；另有 N2/N4）**

| 子项 | 判定 | 证据 |
|---|---|---|
| Core 校验顺序 vs Host 前置义务**清楚分离** | **PASS** | `C-16:103` 只列 ①②③④（envelope / closed shape / grant live+`scope.source_id` / location 四键 == grant facts），`C-16:104` 独立成段并明写"**Host 侧前置义务（本命令不校验、不依赖；由 L-S4-B 实现卡 AC 保证）**"，逐项含唯一 live 非撤销条目、恰 1 根、路径 normalize、`live.CreatedAt > old.RevokedAt`、kind 非 folder、每轮至多一次；并给出不可在 Core 判定的理由"Core `source_locations` 无 path 列（`schema.py:629-646`）"（实测该表确无 path 列）。载体 `:24-25`、PREREQ `:66` 同构。实现卡 `AC-LS4B-2`/`AC-LS4B-9` 确实承载这些 Host 义务（引用有效，非空指）。 |
| 错误码 §2.5/§6/PREREQ D-4 **三者一致（含 `INVALID_REQUEST`）** | **PASS（三处一致）** | `C-16:107` 六码 = `INVALID_REQUEST`/`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY`；`C-16:212`（§6 v1.5 补充）同六码且含"形状/权限面 `INVALID_REQUEST`"；`PREREQ:49`（D-4）同六码（已删 `SOURCE_BUDGET_EXCEEDED`、补 `SOURCE_GRANT_EXPIRED`/`SOURCE_REGISTRY_BUSY`）。§6 表本体零行改动、零新码。**但** §2.5 ① 的"application 面 → `INVALID_REQUEST`"与同文件 §2.4 ①、C-17/M2-C1 口径和 Core 实现冲突 → **新 N4（P2）**。 |
| 矩阵头 v1.5 | **FAIL** | `MATRIX:3` 仍写"C-05 v1.2/C-15 v1.5/**C-16 v1.4** 于 … UNFREEZE 重冻"，且同段只描述到 v1.4；与 `MATRIX:37` 的 `FROZEN v1.5` 冲突。矩阵文件 sha `4373cc6e…` 与 r1 审的字节**完全相同** → 本轮未处置 r1 P2-3。 |
| FROZEN §2 有 v1.5 条件行且 **⏳ 未预填 approved** | **PASS（有一处结构损坏）** | `FROZEN:51` 新增第 7 行，状态 `⏳`，证据指向载体 §6 与 `verification/FEA-11-L-S4-B-PREREQ-1/logs/pins.log`——没有 ✅、没有 approved。**但**同一编辑把第 6 行（v1.4）的"证据"单元格删除、把其文本接到第 7 行末尾：第 6 行只剩 3 个数据格（缺证据），第 7 行有 5 个数据格（多出 v1.4 的"载体 `CONTRACT-UNFREEZE-2026-11-07-C16.md` §6；`verification/FEA-11-RUN-GRANT-2B-PREREQ-1/logs/pins.log`"）→ **新 N2（P2）**。 |

→ **C 判 FAIL**（矩阵头），其中"校验拆分"与"三处错误码一致"两项实质通过。

### D. P3 处置 — **PARTIAL（2 项 PASS、1 项替代、1 项未清）**

| r1 P3 | 处置 | 判定 |
|---|---|---|
| P3-1 FROZEN §1B v1.4 行改写未登记 | 采用"记录内联登记"替代载体 §2.E：`FROZEN:38` 新增行声明"原 v1.4 行见 §8；v1.5 追加 v1.5 行"。信息仍可从 `FROZEN:99`（含 v1.4 r1 计数、r2 session `e032ed9a-…`、reviewed_head `a0bafc89e`）恢复 | **CLOSED（替代方式）**，但措辞不实（见 N5） |
| P3-3 response `version` 未定义 | `C-16:106` 定义"`version` 为 Core 当前 source version id，只读诊断用，不参与授权/不落库"，closed shape `{source_id, updated, version}` | **CLOSED** |
| P3-4 roots probe 异常未写 | `C-16:35` 已写"缺失/不可读/身份不符/**单根探测异常**为 `false`（**探测异常不得抛出、不得使整命令失败**）"；文件级损坏仍整命令失败、不返回部分数组 | **CLOSED（字段级）**；"每根至多一次/锁外探测"仍未写且仓库无 B2 卡可承接 → N8（P3） |
| P3-5 卡面小疵 | 实现卡 AC 编号仍 1..7、9、10、8；PREREQ D-4 仍漏 C-06（`PREREQ:49` 只写 C-15/C-17/C-07/M2-C1）；AC-T5 要求的"契约就绪 ≠ 实现/产品可用"字面句仍只出现在载体 §5 的**核对项**（`carrier:53` ⑥），未作为结论句出现 | **OPEN**（详见 N9） |

→ **D 判 PARTIAL**（非阻断，但未清）。

### E. 安全语义复核（不回归） — **PASS**

| 子项 | 判定 | 证据 |
|---|---|---|
| 请求无路径 / 无 `registry_id` / 无 `generation` | **PASS** | `C-16:100,102`；请求恰 2 键；registry/generation 只从签名 grant 取 |
| 拒绝 / 无匹配**零写** | **PASS** | `C-16:103` 末句"任一不满足 → typed 拒绝、**零写**"；`C-16:107`"拒绝/无匹配零写" |
| 只写三列 | **PASS** | `C-16:105` 三列；复用 `library.py:2324-2339` 单点 SQL（SET 恰这三列，`commit_source_location_auth_refresh:2341-2353` 提供独立写单元，无第二份 SQL） |
| 不改行数 / `source_id` / digest / `is_current` / binding | **PASS** | `C-16:105` 明写；SQL `UPDATE … WHERE … is_current = 1`，不写 `is_current`，不 INSERT；`page_bindings` 不在 SQL 内 |
| 错误码闭集无新增 | **PASS** | §6 表本体零行改动；新增的只是 `C-16:212` 的"补充"段；六个码全在既有表内（`INVALID_REQUEST` 亦为 §1 既有码） |
| C-15 / C-17 / C-06 / C-07 / M2-C1 零字节 | **PASS** | `git diff --name-only HEAD` 无这些文件；`verify_pins` 18/18；M2-C1 无未跟踪/未暂存改动（`git status -uall` 仅 4 tracked + 评审/证据） |
| 红线：不自动重新授权 / 不重建 identity / 撤销后不放行 / 不扩面 / folder 排除 / reset 后 limitation | **PASS** | `C-16:108` 六条齐备；`C-16:97`"不是恢复动作、不是授权决定"；grant 必须 live 且未撤销（`C-16:103`③）；四键身份（④）阻止同路径换文件；`C-16:104` Host 侧 folder 排除（L-S4-2 在 scope review 有定义）；`C-16:108` reset 后无旧条目可桥接 |

补充（不构成缺陷的观察）：

- Core 不检查 `kind == folder`。因为 folder grant 没有单一 `container_facts`（`source_read_refs.py:984-1021` 走 `folder_entries`），§2.5 ④ 的"四键 == grant facts"对 folder 无对象，自然 fail-closed；但契约只把 folder 排除写在 Host 义务与红线里。若想加一层纵深，Core 侧显式拒绝 `sources.source_kind == 'folder'` 成本极低（P3 级建议，未计入 findings）。
- reattest 效果依赖 `(registry_id, generation)` 被枚举精确命中；`source_locations.last_verified_at` 的唯一读点是该单点 SQL 的差异谓词（`grep last_verified_at`：写点 `service.py:986`、`runtime.py:658,697`，SQL SET/谓词 `library.py:2326,2331-2336`，其余命中 `schema.py:100`、`artifacts.py:227`、`pipeline.py:1179` 属其他表），故 N1 属"不可实现"，**不是**新的放宽或安全回归。

### F. pin / 证据 — **PASS**

见 §0 两张实测表：C-16 实际 sha256 = `39da9766…` = FROZEN pin = `git hash-object 6f875960…` = blob 内容 sha256；`verify_pins` 18/18；其余 17 项以 `other-17-pins.txt`（@HEAD、changed=0）与独立抽查 4 个文件实算双重佐证；pre/post 分别为 `ad25fb3c…`/`39da9766…`；`changed-lines.diff` 归一化后与 `git diff HEAD -- C-16` 逐字节相等（sha `3530d843…`）；8 个证据文件 sha 与 EV 表逐项匹配；`carrier.md` 与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md` 同字节；三份日志重跑后逐字节复现。**无伪造/无陈旧证据**。

### G. 冻结包一致性 / 不夸大 — **FAIL**

| 子项 | 判定 | 证据 |
|---|---|---|
| 版本主链 | **PASS** | `C-16:3` v1.5、`FROZEN:4/15` v1.5、`MATRIX:37` v1.5、证据 pre/post 一致 |
| 历史 pin 保留 | **PASS** | `FROZEN:35-37`（v1.1/v1.3/v1.4）、`FROZEN:113`（v1.4/v1.3/v1.1/v1.0）、§1B `:37-39` |
| §1A 三口径 | **PASS** | `FROZEN:22-25` 未改；三口径在本字节上实测一致 |
| §1B 自洽 | **FAIL（轻度）** | `FROZEN:37` 的 v1.4 行被**再次**改写（删 r1 计数/session/head），`:38` 又加一行同名"v1.4 复核字节"却指向 §8；"行保留历史"与"原 v1.4 行见 §8"均不精确（§8 是 v1.4 UNFREEZE 记录，不是 §1B 原行）→ N5（P3） |
| §2 自洽 | **FAIL** | 第 6/7 行单元格数损坏（4 列表头 vs 3/5 个数据格），v1.4 证据错挂 v1.5 行 → N2（P2） |
| §9 自洽 | **FAIL（轻度）** | `FROZEN:111` "独立复核｜载体 §6：`pending`（r1；approved 后于本行追加结论）"——但 §1B `:39` 已写 r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5），同一文件对 r1 结论自相矛盾（陈旧） → N3（P2，与载体 §6 同一根因） |
| 载体 §6 = r1 处置 + r2 pending | **FAIL** | `carrier:56-59` 仍为"- **r1：pending**。- 处置/结论：复核后由 DSH 追加（append-only）"；既未落 r1 `changes_requested` 计数，也未写"处置"与"r2 pending" → N3（P2） |
| 无预填 approved | **PASS** | v1.5 相关的 `⏳`/`pending` 齐备（`FROZEN:51,111`、`carrier:58`、`EV:4`）；`MATRIX:37` 的"①v1.5 … approved"属**冻结条件**列（与 C-15 行同构），不是结论 |
| 不夸大（契约 ≠ 实现/产品） | **PASS（弱）** | `carrier:3`"须经独立复核 + DSH 重新冻结后方可视为最终字节"；`C-16:238`"不构成实现授权；不证明 AC 达成"；`FROZEN:57`"不构成：实现授权、运行时协议已实现、产品 AC 已达成"；`C-16:35`/`carrier:20`/实现卡 `:82` 三处"实现延后"。**但** AC-T5 要求的字面句仍未以结论形式出现在载体 → N9（P3） |

→ **G 判 FAIL**（N2/N3 是硬缺口；N5/N9 属“一致性/文案”非阻断项）。

## 2. r1 findings 逐条处置

| r1 ID | 级别 | 状态 | 依据（本报告） |
|---|---|---|---|
| **P1-1** §2.5 请求 4 键 vs 2 键 | P1 | **CLOSED** | §1-A：五处一致为恰 2 键；`command`/`scope` 已删；形状错 → `INVALID_REQUEST` |
| **P1-2** 三列值来源未定义 + 幂等冲突 | P1 | **OPEN（重定 N1）** | §1-B：幂等/单调推理已修对，但 `last_verified_at = grant.created_at` 指向不存在的 grant 字段（C-06:39 / C-16:43-67 / `_ENVELOPE_FIELDS` / Host payload 四重证据） |
| **P2-1** Host 条件并入 Core 校验 / 路径不可判定 | P2 | **CLOSED** | §1-C：`C-16:103`/`:104` 两段分离，明写"本命令不校验、不依赖"与"无 path 列" |
| **P2-2** 形状错误码缺失 + D-4 码表不一致 | P2 | **CLOSED** | §1-C：`C-16:102,212` 与 `PREREQ:49` 六码一致 |
| **P2-3** 矩阵头 v1.4 | P2 | **OPEN** | §1-C/§0：`MATRIX:3` 仍 v1.4；矩阵字节 `4373cc6e…` 与 r1 审的完全相同（本轮未改） |
| **P2-4** FROZEN §2 缺 v1.5 行 | P2 | **CLOSED（引入新缺陷 N2）** | §1-C：`FROZEN:51` v1.5 行已加且 `⏳`；但第 6/7 行单元格损坏、证据错挂 |
| **P3-1** FROZEN §1B v1.4 行改写未登记 | P3 | **CLOSED（替代方式，措辞见 N5）** | §1-D：`FROZEN:38` 内联登记；信息可从 §8 恢复 |
| **P3-2** 键映射 / `size_bytes` 不在 SQL 谓词 | P3 | **OPEN** | §1-D、N6：`C-16:103`④ 仍只给列名，未写 `content_digest↔facts.sha256`、`size_bytes↔facts.size`，也未写"SQL 只匹配三身份键、`size_bytes` 由 handler 先比对" |
| **P3-3** response `version` 未定义 | P3 | **CLOSED** | §1-D：`C-16:106` 定义为 Core 当前 source version id、只读诊断 |
| **P3-4** roots probe 异常未写 | P3 | **CLOSED（字段级；残 N8）** | §1-D：`C-16:35` 已写异常→false、不得抛出/不得使整命令失败 |
| **P3-5** 卡面小疵 | P3 | **OPEN（部分）** | §1-D、N9：AC 编号未重排；D-4 仍漏 C-06；AC-T5 字面句仍缺 |

**统计**：r1 共 11 条 = P1×2 + P2×4 + P3×5。**CLOSED 7**（P1-1、P2-1、P2-2、P2-4、P3-1、P3-3、P3-4；其中 P2-4 与 P3-1 属"闭合但引入新缺陷/采用替代方式"，分别见 N2、N5）；**OPEN 4**（P1-2→N1、P2-3、P3-2、P3-5）；**ACCEPTED 0**（未发现可接受的残余风险——N1 与 N4 均落在"实现者无法判定"级别，不宜以风险接受处理）。其中 **P1-2（N1）与 P2-3 直接决定 verdict**。

## 3. 新 findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **N1** | **P1** | `C-16:105`；`C-06:39`；`C-16:43-67`；`source_read_refs.py:62-66,124-131`；`SourceReadCoordinator.cs:470-499` | `last_verified_at = grant.created_at` 的 `created_at` **不在**冻结 grant 载荷（C-06 v1.2 字段表无该键；C-16 §2 JSON 无该键；Core envelope 是闭集且严格拒绝多余键；Host 铸造 payload 无该键）。`created_at` 只存在于 Host Registry 条目（`C-06:29,51`；`C-16:31` `source_list_roots`）。Core 在 2 键请求里取不到该值；照字面补齐需给 grant 加签名新字段 → wire 新增 + C-06 字节变更 + ≥2 pins，与 §10 ⑦/矩阵 ②/载体"1 pin、零 wire、C-06 零字节"冲突；由 Core 造时间则违背同句"不取 `now()`/不做时钟推断"与"签名的稳定值" | 二选一并如实记账：**（a）**给 grant 载荷加签名 `created_at`（C-06 §2.2 字段表 + C-16 §2 JSON + §2.5 同步，pins 改 2/18，并补 C-06 安全/兼容说明）；**（b）**保留 1 pin，改用"Core 可得且稳定"的值并重写幂等条款——但这意味着不能再用单点 SQL 的 `last_verified_at IS NOT ?` 做幂等判据（需先读后比或改 `updated` 语义），必须显式写出取舍。**不得**保留当前"不存在的字段 + 声称已签名"的组合 |
| **N2** | P2 | `FROZEN:50-51`（§2 表） | v1.5 行的插入把第 6 行（v1.4）的"证据"格删除，其文本被接到第 7 行末尾：表头 4 列，第 6 行只有 3 个数据格（无证据），第 7 行有 5 个数据格，末尾挂着 v1.4 的"载体 `CONTRACT-UNFREEZE-2026-11-07-C16.md` §6；`verification/FEA-11-RUN-GRANT-2B-PREREQ-1/logs/pins.log`"→ 表格结构损坏且 **v1.4 证据错挂 v1.5 行** | 恢复第 6 行证据格；删除第 7 行末尾多出的 v1.4 证据格；核对两行均为 4 格 |
| **N3** | P2 | `carrier:56-59`；`FROZEN:111` | 载体 §6 仍写"r1：pending"，未记 r1 `changes_requested`（P0=0/P1=2/P2=4/P3=5）与处置，也未写 r2 pending；FROZEN §9 同一栏亦写 `pending`（r1…），与 `FROZEN:39` 已记的 r1 changes_requested 自相矛盾 | 按 append-only 在载体 §6 追加：r1 `changes_requested`（计数）+ 处置要点 + "r2 `changes_requested`（P0=0/P1=1/P2=4/P3=6）→ r3 待复核"；FROZEN §9 的复核栏同步为"r1 changes_requested → 处置 → r2 changes_requested → pending" |
| **N4** | P2 | `C-16:103`①、`C-16:107`；对照 `C-16:89`①、`C-17:192,359`、`core_service.py:6257-6261,1441-1453` | §2.5 ① 写"host-only session；application 面拒绝，`INVALID_REQUEST`"，且 §2.5 错误段把"权限面"归 `INVALID_REQUEST`。但同文件 §2.4 ① 对**同类** host-control 命令写 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`；C-17 §5（`:192`、码表 `:359`）将其定为既有口径；Core 实现在命令分发入口（handler 之前）就以 `HOST_ONLY_REQUIRED` 拒绝 application 面、以 `HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH` 拒绝会话问题——§2.5 的字面值**不可达且与冻结口径冲突**，实现者/AC 无法判定 | ① 改为与 §2.4 同口径（`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`），§2.5 错误段区分"envelope 码"与"本命令业务码"；若确要收敛到 `INVALID_REQUEST`，须说明为何与 §2.4/M2-C1 不同并同步 C-17 口径（不建议） |
| **N5** | P3 | `FROZEN:37-38`；`carrier:33-36`（§2.E） | §1B 的 v1.4 行**再次**被改写（丢 r1 计数与 session/head，仅留"见 §8"）；新增行标签重复（两行都叫"v1.4 复核字节"），值为"原 v1.4 行见 §8；v1.5 追加 v1.5 行"，其中"行保留历史"不实（行被改写、未保留），"RFC 改写登记"术语未定义；"原 v1.4 行见 §8"不精确（§8 是 v1.4 UNFREEZE 记录，非 §1B 原行）；载体 §2.E 仍未登记该编辑 | 载体 §2.E 明写"§1B v1.4 行改写为指针行，原信息保留于 §8"；§1B 该行措辞改为可核验表述（如"v1.4 复核字节（历史行，信息见 §8）"），删去未定义缩写；或恢复原行文本并接受与 §8 重复 |
| **N6** | P3 | `C-16:103`④、`:105` | 四键身份与 grant facts 的**键映射**未写（`content_digest↔facts.sha256`、`size_bytes↔facts.size`、`volume_serial`/`file_id` 同名）；也未写"单点 SQL 只匹配 `content_digest/volume_serial/file_id` 三键，`size_bytes` 必须由 handler 在调用前比对"（`library.py:2324-2338`）。实现者可能误以为 SQL 覆盖四键 | 在 §2.5 ④ 或 §2 动作段补一行键映射 + "SQL 只匹配三身份键、`size_bytes` 由 handler 先比对"（r1 P3-2 的原始建议） |
| **N7** | P3 | `C-16:106` | `updated:0` 的**三种来源**未区分：①同 grant 幂等（已写）；②同 registry 代次回退（SQL 第二谓词使其 0，但契约只说"不倒退"，未说响应是 0 还是 typed）；③无匹配（行不存在/`is_current=0`，SQL 返回 0，但 §2.5 ④ 又要求"事实必须相等，否则 typed 拒绝"——两者可同时成立，语义未定）。另：若期间有 A 卡 `now()` 刷新介入（`service.py:986`、`runtime.py:658,697`），同 grant 复调会重新 `updated:1`，故"同 grant 重复调用 → `updated:0`"需限定"无其他写入者介入" | 明确 `updated` 的语义边界（仅表示本次三列是否变化）与"无匹配/代次回退"的返回（typed `SOURCE_ACCESS_DENIED` 还是 `updated:0`），并给幂等句加前提 |
| **N8** | P3 | `C-16:35` | roots_available 已写"单根探测异常 → false、不得抛出"；仍缺"每次调用每根至多探一次、锁外探测"（scope review 的实现约束；实现卡 `FEA-11-L-S4-B-AUTO-RECOVERY-1.md:82` 明写 B2 实现延后、另卡，而该 B2 卡尚不存在，`doc/tasks` 下 L-S4 仅有 PREREQ / AUTO-RECOVERY / LOCATION-AUTH-REFRESH 三张） | 要么在 §1 补该两句（字段冻结与实现约束可同段），要么在后续 B2 卡建立时登记为 AC；当前状态是"要求无归属" |
| **N9** | P3 | `FEA-11-L-S4-B-AUTO-RECOVERY-1.md:69-78`；`PREREQ:49,90`；`carrier:53` | ①实现卡 AC 编号仍 1..7、9、10、8（未重排，且该卡不在本卡 `allowed_paths`，本轮无法修）；②`AC-LS4B-4` 写"重复调用 `updated:false`"，与契约 `updated: 0|1`（`C-16:106`、`PREREQ:69`）类型不一致；③PREREQ `D-4` 零字节清单仍漏 **C-06**（`I-2`/`AC-T1`/`out_of_scope` 均含），而 N1 恰好落在 C-06 的 grant 字段表上；④AC-T5 要求的"契约就绪 ≠ 实现/产品可用"仍未以结论句形式出现在载体正文（仅 `carrier:53` 的核对项） | ③④ 本轮可修（D-4 补 C-06；载体 §1 或 §3 补该字面句）；①② 需在 L-S4-B 实现卡另行修订（建议随该卡下一次改动一并重排编号并把 `updated:false` 改为 `updated:0`） |
| **N10** | P3 | `C-16:17`；`PREREQ:46,67` | §0 版本面行仍写"本契约 **source-access-wire/1.3**（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…）"，未提 v1.5/§2.5——读者无法从版本面判断新命令归入哪个 wire 面（虽然"不 bump"是既定裁决）；另"同一单点 SQL"的指称混用三种写法（`C-16:105` = `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`；`PREREQ:46` = "A 卡"；`PREREQ:67` = "L-S4-A"） | 版本面行补"v1.5 additive §2.5（不 bump）"；统一 A 卡指称（建议统一为 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`，首次出现处给"A 卡"别名） |

**计数**：P1×1（N1）、P2×4（N2、N3、N4 + r1 P2-3）、P3×6（N5…N10）。

## 4. 复核结论与处置建议

- **verdict：`changes_requested`**（P0=0 / P1=1 / P2=4 / P3=6）。
- C-16 §10 ⑦ 的"独立 byte-level 复核 approved（P0/P1=0）"**未满足**；C-16 当前字节 `39da9766…` **不是可长期保留的最终冻结字节**。FROZEN §9、载体 §6 的 `pending` 必须保持；矩阵行"①v1.5 独立 byte-level 复核 approved"在 r2 下仍为未满足条件。
- 建议处置顺序：
  1. **先裁 N1**（唯一 P1）：选"加签名 `created_at`（pins 记 2/18）"或"改幂等语义（保留 1 pin）"；两条路的字节后果不同，需 DSH 先裁决再改字节，避免又改出"字段不存在"。
  2. 修 P2：矩阵头 v1.4→v1.5；FROZEN §2 行 6/7 单元格复原；载体 §6 追加 r1 结论 + r2 结论；§2.5 ① 的 envelope 码与 §2.4 对齐。
  3. 修 P3（N5…N10；其中 D-4 补 C-06 与 AC-T5 字面句在本卡范围内可立即做，实现卡两项另记）。
  4. 重算 C-16 sha256 与 `git hash-object`，更新 FROZEN §1/§1B/§2/§9 与矩阵，重跑 `verify_pins`（18/18 或 2 pins 方案下的对应值）与 `check.ps1`（默认 + `-TaskPath`），重生成 `changed-lines.diff`/pre-post/日志/EV。
  5. 因 P1 变更会再次改动冻结字节，须再做一轮独立 byte-level 复核（r3）；通过后由 DSH 在载体 §6 append-only 落结论并提交。
- 本报告**不修改**任何被审字节、证据、卡或冻结记录；findings 中的建议不代表已实施；**不建议**在 r3 前提交或推送 UNFREEZE。

## 5. 真实性声明

- **身份与独立性**：本报告由 fresh subagent 在独立上下文中产出（session `c7a9c263-5f4b-4124-b572-b7ca6ab11f18`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；未参与本 UNFREEZE 的起草、r1 复核或任何相关实现；只读被审字节与背景只读材料（C-06/C-15/C-17/C-16、scope review、实现卡、源码锚点）。
- **只读**：未使用 `git add/commit/push`；未修改 C-16/FROZEN/矩阵/载体/PREREQ 卡/实现卡/证据/源码；唯一写入为 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r2.md`。字节比对用的临时脚本只写入本机 `%TEMP%`，未进入仓库。
- **实测命令**：`git rev-parse HEAD`、`git status --porcelain=v1 -uall`、`git diff --name-only HEAD`、`git diff --numstat HEAD`、`git diff HEAD -- <各文件>`、`git hash-object`、`git cat-file blob`、`Get-FileHash -Algorithm SHA256`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1`（默认与 `-TaskPath`）、Python 3（字节级/hash/表格列数比对、日志重跑对比）。
- **代码只读锚点**：`src/infrastructure/sqlite/library.py:2293-2353`、`src/infrastructure/sqlite/schema.py:629-648`、`src/infrastructure/resource_channel/source_read_refs.py:62-84,124-131,199-213,984-1021`、`src/bootstrap/core_service.py:1441-1453,4906-4914,6253-6261`、`src/application/sources/service.py:979-987`、`src/application/importing/referenced/runtime.py:651-659,689-699`、`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:470-499`。
- **NOT_RUN**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` gated IPC、`ReattestSourceLocation` 运行时（仓库尚无实现）、真实用户数据/AppData/回收站、push。本报告的 PASS 不对这些未跑项作任何声明；N1 的判定基于**冻结字节 + 只读实现锚点**，不依赖运行结果。
- **事实优先级**：全部断言取自 `59ba5189f` 的工作树最终字节、只读源码与工具输出；不采用聊天记录或旧快照作为事实来源。r1 报告仅作为被审输入与对照，不作为事实来源。
