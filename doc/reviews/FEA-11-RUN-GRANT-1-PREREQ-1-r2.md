---
task: FEA-11-RUN-GRANT-1-PREREQ-1
title: FEA-11-RUN-GRANT-1-PREREQ-1 delta 窄面复审（C-06 v1.2 + C-16 v1.3 UNFREEZE r2）
reviewer: fresh subagent（独立上下文；未参与起草/修复；只读）
session: 587ff25a-50a2-4f92-a9f7-77ec70858ea3（$DSH_SESSION_ID 实测；以 Lead 记录为准）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: b17d7282193afa6583c6c7a7bfc6456d04313af5
verdict: changes_requested
---

# C-06 v1.2 + C-16 v1.3 UNFREEZE · delta 窄面复审 r2

> **结论先行：`changes_requested`。P0=0 / P1=0 / P2=2 / P3=9。**
>
> - **r1 的 P1 与全部 P2 已关闭**，契约字节本身未发现语义/不变量/证据问题：pins 18/18、其余 16 项逐字节不变（本轮实算全部 16 项）、Run wire/`PROTOCOL_MINOR=3`/schema/依赖/M2-C1 零 diff、`pre-post.sha256`/`changed-lines.diff`/两 check 日志均可复算（见 §F）。
> - **两项 P2 均在冻结记录/载体登记面，不涉及契约条款语义**：
>   1. **N-01**：两份冻结记录与载体把「未变态」写成 **17 pins**（`FROZEN-C06:80`、`FROZEN-C16:85`「其他 17 pins」、`FROZEN-C16:46`「其余 17 项不变」、载体 `:36`「其余 17 pins 断言」）。本批 **2/18 重签**（C-06、C-16），未变应为 **16**；`other-16-pins.txt`、载体 `:45`、卡 D-2/AC-P1/AC-P3 均写 16。这是冻结记录层面可证伪的断言。
>   2. **N-02**：C-06 §5 冻结条件 4 的 v1.2 追加句（`FEA-C06_SOURCE_AUTH_DRAFT.md:87`）**未登记**在载体 §2.A / 卡 I-2；而 C-06:96 与 `FROZEN-C06:76` 仍称「仅新增条目」，与实际 diff（修改既有冻结条件文本）不符 ⇒ AC-P1「只包含本卡 I-2/I-3 登记的增量」字面不成立。
> - **两项都是文档级修复**：若保留 §5 追加句并补登记，**不触碰契约字节、无需重算 pin**（C06 仍 `6214ef77…`、C16 仍 `7c355ccb…`，pins 仍 18/18）；只需复跑 `check.ps1`（默认 + `-TaskPath`）并窄面确认修改后的登记文本。若选择回退该句或修正 C-06 变更记录措辞，则须重算 C-06 pin 并再确认。
> - **不构成**：本报告不批准提交，不构成实现授权，也不构成「referenced Run 产品可用」。
>
> **时点说明（2026-11-06 23:39 补记）**：本报告撰写期间（约 23:33–23:38），DSH 于 **23:36–23:37** 按 N-01/N-02 处置并**重签 C-06**（`6214ef77…` → `99831a20…`）；载体 §6 已将本报告记为 r2，并标 **r3 pending（最终字节）**。本报告的数值时点、最终字节与结论适用范围见文末「复核后工作树变更（scope note）」；**本报告不构成对 `99831a20` 最终字节的批准**。

---

## 0. 复核对象、方法与实测环境

- `reviewed_head`：`b17d7282193afa6583c6c7a7bfc6456d04313af5`（`git rev-parse HEAD` 实测；短 hash `b17d72821`），branch `main`。
- 被审字节＝**工作树最终字节**（HEAD 之后仍有未提交 UNFREEZE 改动；`git status --porcelain -uall` 实测 15 项［不含本报告；本报告写入后为 16 项］：6 个 `M` = C-06/C-16/两份冻结记录/矩阵/卡 + 9 个 `??` = 载体、r1 报告、`verification/FEA-11-RUN-GRANT-1-PREREQ-1/**` 7 文件）。未暂存（`git diff --cached` 为空）。
- 只读事实以工作树最终字节为准；载体/卡面自述仅作索引。对 delta 新增/修改的关键主张回源核对代码：`read_gate`（`src/bootstrap/core_assembly.py:1244-1261,1750,1766`）、`_assert_source_sync_gate`（`src/bootstrap/core_service.py:5072-5103`，resolve 面在 `:4458` 调用）、`COMMAND_CATALOG`（`src/domain/tasks/models.py:87`）、`_parse_run_scope`（`core_service.py:5724-5753`）、`StartRun`/`PrepareRun` payload（`:5867-5923`）、grant facts（`src/infrastructure/resource_channel/source_read_refs.py:411-440,610-745`）、`source_locations` 字段（C-15 `:77-96`）。
- 唯一写入：本报告。未 `git add`/`commit`/`push`，未删除/移动文件，未改任何被审字节、证据、卡、冻结记录或矩阵。为读取 HEAD 原始字节，只在系统 `%TEMP%` 写了只读副本（`git cat-file blob` 重定向），未落仓库。
- **NOT_RUN**：pytest、.NET build/test、API inventory、真实 IPC、blocked 的 `git cat-file`（工作树 blob 尚未入 object DB，见 §F 备注）。理由：本卡 `out_of_scope` 禁生产代码，实测 `src/**`、`apps/**`、`tools/**` 相对 HEAD 零 diff，字节级复审不需要这些门禁；未跑即标 NOT_RUN，不以静态判断代替。

### 0.1 本轮实测命令与结果（摘要）

| 命令 | 实测结果 |
|---|---|
| `git diff --name-only HEAD -- doc/plan/` | 恰好 5 个：C-06、C-16、`FEA-CONTRACT-FROZEN-C06`、`...-C16`、`FEA-CONTRACT_FREEZE_MATRIX.md` |
| `git diff --name-only HEAD -- doc/contracts src apps tools tests` | **空（NONE）** |
| `Get-FileHash -Algorithm SHA256` C-06 / C-16 | `6214ef77f57d8fe4a234a87336173145e308923f204a65d900470a764ecd3821` / `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5` |
| `git hash-object` C-06 / C-16 | `8a21af823fa4552279da26483ee311d9ea007389` / `a5143d5e162f60ffbd902d7dc60792b162c6a378`（= 两份冻结记录 `:17`） |
| HEAD 原始字节 sha256（`git cat-file blob HEAD:` 重定向后实算） | C-06 `8faa8cd1…b2003`、C-16 `0b9511a5…e5905` = `pre-post.sha256` 的 pre 值 = v1.1 历史 pin |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；C06 `6214ef77f57d`、C16 `7c355ccb8f82`；与 `logs/pins.log` 逐行相同 |
| `check.ps1` / `check.ps1 -TaskPath` | 均 `Governance check: PASS (3 warnings)`，与 `logs/check.log`、`logs/check-taskpath.log` 逐行相同 |
| `changed-lines.diff` vs `git diff HEAD -- C06 C16` | 归一化后**逐字节相同**；两侧 sha256 均 `0f6edb25f4bd58cb36734feb9d39cdbbf67573a74c78f80ba3519f8db9a2708b` |
| 其余 16 项实算（全部） | 与 `other-16-pins.txt`/`pins.log` 全部一致（如 C01b `3c9f5af7d74f`、C07 `3fdb44e49afe`、C15 `d8c0a3bcfc21`、C17 `aefa0fa5b17e`、FEA01 `0370c18932b1`） |

---

## A. P1 关闭：能力缺失口径 —— **PASS**

四处口径已统一为「缺失 → 不铸/不绑、按现状 dispatch」，且**不再**把 `CORE_CAPABILITY_MISSING` 写成 Run 的阻断：

| 位置 | 字节 |
|---|---|
| 卡 D-4（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:59`） | 「Host 缺失 → **不铸 grant、不绑定、按现状 dispatch**（不阻断既有 managed Run；不得用未知命令探测；referenced Run 仍按现状 typed 失败）」 |
| 卡 §兼容与影响（`:128`） | 旧 Core → ping 判定缺失 → 不铸/不绑定、按现状 dispatch（referenced Run 仍 typed 失败）；不因全局 minor=3 推断支持 |
| 卡 I-3（`:81`、`:89`） | 「缺失 → 不铸/不绑定、按现状 dispatch；按操作检查，不靠发送后看结果」/「缺失时不得以未知命令探测；Host 缺失 → 不铸/不绑定、按现状 dispatch」 |
| C-16 §0（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:22`） | 「缺失 → **不铸造、不绑定**，按现状 dispatch（旧 Core 行为不变；referenced Run 仍 typed 失败）。能力缺失不得靠“发送后看结果”判断」 |
| 载体 §3（`doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md:42`） | 同文（旧 Core → 不铸/不绑定、按现状 dispatch；既有 managed Run 零变化） |

- 无残留冲突：C-16 中仍使用 `CORE_CAPABILITY_MISSING` 的只有 §0 `source.read/1`/`source.resolve-secret/1` 两条**既有**能力门（`:20-21`）与 §7 泛化条款（`:205`），均不针对 `source.read.run/1`，也不要求拒绝 Run。
- **备注（不计 finding）**：§7 第 8 条「能力缺失/探测异常不得放行 source 操作（按操作 `CORE_CAPABILITY_MISSING`）」与 v1.3 §0 新行并置时略易误读；新行并未「放行 source 操作」（它只是不建立授权，referenced 读仍 typed 失败），故不构成冲突，但下轮可在 §7-8 或 §0 加一句交叉引用。

## B. P2-1/P2-2/P2-5 关闭 —— **PASS**

**P2-1（失败形态统一）PASS**：
- C-06 §2.3（`:56`）：「任一目标页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`**、零绑定写入、Host 不得 dispatch（C-16 v1.3 §2.4）」。
- C-16 §2.4（`:85`、`:88`）：「**不使用「成功响应 + refused 列表」形态**」/「整体 typed `SOURCE_ACCESS_DENIED`（`details={"refused_pages": n}`）且零映射写入（不返回部分成功、`bound_pages` 不适用）」。
- 卡 I-3（`:84`、`:87`）与载体 `:31` 同文。C-06 未重复写 `details` 键，但显式交叉引用 C-16 §2.4，属可接受的分工（见 P3-2 的类型注记）。

**P2-2（facts 核验）PASS**：
- C-16 §2.4（`:87`）新增：「并核验该 entry 的 **facts**（`volume_serial`/`file_id`/`size`/`sha256`）与 `source_locations` 当前物理身份一致（`source_entries`/`source_locations` 逐项核对，**无路径回退**）」。
- C-06 §2.2（`:43`）、卡 D-5（`:60`）/I-3（`:86`）、载体 `:23/:31` 同域。字段在代码中存在：`_facts` 严格要求四键（`source_read_refs.py:723-726`），`source_locations` 有 `content_digest/volume_serial/file_id/size_bytes`（C-15 `:77-93`）。
- 残留精度问题见 **P3-6**（folder 成员的 facts 应落 `source_entries`，而 `source_locations` 只有目录级身份；容器源单 entry 即容器 facts）。不改变「无路径回退」这一关键不变量。

**P2-5（gate 谓词）PASS**：
- C-16 §2.4（`:87`）：「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；无 publication 行按既有 open 处理」；`:90` 明写「publication gate 的两读面既有差异（L-R11，`core_assembly.read_gate` vs resolve 面 `_assert_source_sync_gate`）不属于本命令语义，本命令不引入第三套 gate 判定」；卡 I-3（`:86`）同文。
- 回源核对成立：`read_gate` docstring 自述「the single definition shared by the Run commit guard, the provider image source and the Run target catalog — no third gate predicate exists in the assembly」，且「A binding without a publication row is `open` exactly as the pre-existing commit guard treated it」（`core_assembly.py:1244-1261`）；同一函数在 `:1750`（Run target catalog）与 `:1766`（`run_source_guard`）接线。resolve 面确为另一谓词 `_assert_source_sync_gate`（`core_service.py:5072-5103`，`:4458` 调用），被新文本显式排除。

## C. P2-3/P2-4 关闭与未登记缺口 —— **FAIL（P2×2；另 P3 残留）**

**P2-3（不再预填 approved）PASS**：
- `FROZEN-C06:77`：r1 `changes_requested` → DSH 处置 → **delta 窄面复核 pending**；`FROZEN-C16:46`：条件 5 状态 `⏳`，同写 pending；`FROZEN-C16:82` 同；载体 §6 `:63`：**pending**。
- 工作树文档中不存在针对 v1.2/v1.3 的「approved / P0=0/P1=0」既成事实断言（C-06 `:3`、C-16 `:3` 的两处 approved 均限定为 v1.1 历史，并指向冻结记录）。
- 残留歧义：`FROZEN-C06:44` 的「冻结条件逐条核验」表 row 1 仍为 ✅，证据是 v1.0/v1.1 的 r1→r3，表内无 v1.2 行 ⇒ 可能被读成 v1.2 条件 1 已满足（**P3-4**）。

**P2-4（limitation 登记）PASS**：
- 载体 §4（`:49`）已登记 L-G1（300s）、L-G9（Core 重启）、L-G2（加密 referenced Run）、L-R11（L-G10，两读面 gate 不一致）；卡 L-P2（`:135`）登记 L-G1/L-G2/L-G9/L-G10。
- 未发现「契约就绪 = 实现/产品可用」的改写（见 §G）。

**未登记缺口（本项判 FAIL 的原因）**：
- **N-01（P2）**：冻结记录/载体「17 pins」计数错误（见下）。
- **N-02（P2）**：C-06 §5 条件 4 的 v1.2 追加句未在载体 §2.A / 卡 I-2 登记（见下）。
- R1-P3-2/R1-P3-3/R1-P3-8 三条 r1 P3 残留仍未登记（对应新表 P3-1/P3-2/P3-3）。

## D. P3 处置 —— **PASS（清单项已落地）＋ 残留 P3 未登记（非阻断）**

| 要求 | 实测 | 判定 |
|---|---|---|
| 卡 §5→§6 | 卡 I-2 `:76`「§6 变更记录追加 v1.2 行」 | 已修复（R1-P3-1 CLOSED） |
| 响应形态 | 卡 I-3 `:84/:87`、C-06 `:56`、C-16 `:85/:88`：整体 typed 失败、零绑定写入、不返回部分成功 | 已修复（R1-P2-1 / 卡 I-3 响应形态） |
| `command` 取值域限定 | C-16 `:83`「`COMMAND_CATALOG` 中可由 scope 展开的 Run 起始命令；与对应 Run 命令同一取值域与同一 scope 展开器；未知/越域 → `INVALID_REQUEST`」；卡 `:83` 同 | 已限定（R1-P3-7 CLOSED；残留措辞 P3-5） |
| 冻结记录头部时间 | `FROZEN-C06:4`「2026-11-01（v1.0）/ 2026-11-03（v1.1）/ 2026-11-06（v1.2）」；`FROZEN-C16:4` 增 v1.3 | 已修复（R1-P3-5 时间部分） |
| 状态行历史复核标注 | C-06 `:3`「v1.1 复核 r7 approved 见冻结记录」；C-16 `:3`「v1.1 UNFREEZE r15 approved + 已提交字节独立复核 approved 见冻结记录」 | 已修复（R1-P3-6 CLOSED） |
| 证据 `carrier.md` | 存在（`verification/FEA-11-RUN-GRANT-1-PREREQ-1/carrier.md`，9732 B）；与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` **sha256 相同**（`7645C5DA…96B`） | 存在（R1-P3-4 CLOSED；副本卫生 P3-7） |
| 证据 `check-taskpath.log` | 存在（426 B）；与 `check.ps1 -TaskPath` 复跑逐行相同（与 `check.log` 也逐字节相同，因默认检查解析到同一 Task） | 存在 |
| 其余 P3 登记/修复 | P3-1（§2.4 嵌套，即 R1-P3-2）、P3-2（错误码措辞，即 R1-P3-3）、P3-3（C-06:58 仍 v1.1，即 R1-P3-8 残留）**均未修复也未登记**；P3-9 去重未做（R1-P3-5 残留） | **未完成（非阻断；已登记为 P3-1/P3-2/P3-3/P3-9）** |

## E. 新字节最小性 —— **FAIL（N-02）**

**文件面 PASS**：`git diff --name-only HEAD -- doc/plan/` 恰为预期 5 文件；另有卡 `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md`（allowed_paths 内）与未跟踪载体/证据；`doc/contracts`/`src`/`apps`/`tools`/`tests` 0 文件。

**C-06 diff（5 hunk）**：`@@ -1,7 +1,7 @@`（状态行/日期行）、`@@ -40,6 +40,7 @@`（§2.2 新行）、`@@ -52,6 +53,7 @@`（§2.3 新行）、`@@ -82,7 +84,7 @@`（**§5 条件 4**）、`@@ -91,3 +93,4 @@`（§6 变更记录）。其中 `-82,7 +84,7` **不在**载体 §2.A / 卡 I-2 的登记清单内 ⇒ **N-02**。且 `C-06:96` 与 `FROZEN-C06:76` 均写「仅新增条目」，与「修改既有冻结条件文本」不符。

**C-16 diff（4 hunk）**：`@@ -1,7 +1,7 @@`、`@@ -14,11 +14,12 @@`（§0 wire 1.2 + `source.read.run/1`）、`@@ -69,6 +70,25 @@`（新 §2.4）、`@@ -201,10 +221,11 @@`（§10 条件 ⑤ + 变更记录）。每一 hunk 都能对应载体 §2.B.1–§2.B.4，**无未登记段落**。

**不变量零改动（逐项，PASS）**：

| 不变量 | 证据 | 结论 |
|---|---|---|
| grant 四维 scope 形状 | C-06:39 grant 字段行、C-16:51-60 scope 示例均无 hunk | 零改动 |
| TTL ≤300s | C-06:40 无 hunk；C-16 §2.4:75/:88 明写「不延长」；registry 的 `now+300` 校验在 `src` 零 diff | 零改动 |
| 撤销语义 | C-06:42、C-16:23、C-16:204 无 hunk；§2.4:75 明写「不改变」 | 零改动 |
| 失联语义 | 同上（C-06:42、C-16:204） | 零改动 |
| C-16 §6 错误闭集无新增码 | C-16:169-194 无 hunk；§2.4 只引用 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED` 与 M2-C1 §5.7 envelope 码 | 无新增码 |
| §7 脱敏规则 | C-16:196-205 无 hunk；§2.4:89「脱敏沿用 §7」 | 零改动 |
| §3.1 fresh-grant/密码通道 | C-16:102-128 无 hunk | 零改动 |
| `RegisterSourceReadGrant` 语义 | C-16:37-71 主体无 hunk（新 §2.4 插在 `:72` 之后） | 零改动 |
| `RevokeSourceReadGrant` 语义 | C-06:55、C-16:23/:204 无 hunk | 零改动 |
| Run wire 请求/响应 | `src` 零 diff；`StartRun`/`PrepareRun` 在 `core_service.py:5867-5923`；无 Run wire 文档改动 | 零改动 |
| `CORE_PROTOCOL_MINOR` | `PROTOCOL_MINOR = 3`（`src/bootstrap/core_service.py:320`），`src` 零 diff | 零改动 |
| schema/迁移/依赖 | `src` 零 diff；依赖文件不在 diff | 零改动 |
| M2-C1 | `doc/contracts` 零 diff | 未改 |

**结论**：E 的失败**仅限 N-02（一行的登记缺口）**；文件面、hunk 面与全部不变量均通过。

## F. pin 与证据 —— **PASS（附 N-01 计数注记）**

- **pin 复算**：C-06 工作树 sha256 `6214ef77…3821` = `FROZEN-C06:16/:18` 的 pin；C-16 `7c355ccb…19e5` = `FROZEN-C16:16/:18` 的 pin。两值 `git hash-object` = `8a21af82…`/`a5143d5e…`，分别等于冻结记录 `:17` 的 blob id。
- **改前值**：`git cat-file blob HEAD:` 原始字节实算 = `8faa8cd1…`/`0b9511a5…`，等于 `pre-post.sha256` 的 pre 行，也等于两份冻结记录的 v1.1 历史 pin。
- **`verify_pins.ps1`**：实测 `PIN AUDIT: PASS (all 18)`，C06 `6214ef77f57d`、C16 `7c355ccb8f82`，与 `logs/pins.log` 19 行逐行一致。
- **其余 16 项**：`other-16-pins.txt` 16 项全部 `prev=actual`、`SUMMARY: 16 contracts, changed=0`；本轮**实算全部 16 项**均相等（抽查值见 §0.1）。
- **`changed-lines.diff`**：与 `git diff HEAD -- C06 C16` **逐字节相同**（sha256 同为 `0f6edb25…708b`），不是手写摘要。
- **日志**：`logs/pins.log`、`logs/check.log`、`logs/check-taskpath.log` 与复跑逐行相同；`check.log` 与 `check-taskpath.log` 亦逐字节相同（默认 `check.ps1` 实测解析到同一 Task，输出同文，属预期）。
- **`carrier.md`**：存在且与 doc 载体 sha256 相同（见 §D）。
- **N-01 注记**：冻结记录/载体的「其他 17 pins」与上述实测（未变 **16**）矛盾，属证据文本错误，不影响 pin 值本身（详见新 findings）。
- **方法备注**：工作树 blob（`8a21af82…`/`a5143d5e…`）尚未入 object DB（未 `git add`，本报告也不得 add），故 `git cat-file` 对它们报 `bad file`；「blob 内容 sha256（LF 原始字节）」通过两条等价事实核验：① `git hash-object` 复现记录中的 blob id；② 两文件实测 **0 个 CRLF**（纯 LF），故 blob 内容 sha256 = 工作树 sha256 = 记录 pin。

## G. 不夸大 —— **PASS**

- 卡 `:44`：「本卡只交付契约字节与冻结证据：不构成实现授权，不构成「referenced Run 产品可用」」；L-P3 `:136`：「契约就绪不构成实现授权；`FEA-11-RUN-GRANT-1` 释放前不得写码」。
- 载体 §1 `:10`：「生产 referenced 页 Run 仍不可端到端（L-R1）」；§3 `:42-44` 与 §4 `:49` 保留兼容/风险/limitation；矩阵第 16 行 `:37`「Run 接线归 FEA-11-RUN-GRANT-1」。
- 未发现把「契约就绪」写成「实现/产品可用」或把 pending 复核写成已通过的断言（N-01 是 pin 计数错误，不是产品能力夸大）。

---

## r1 findings 逐条处置判定

| r1 ID | 严重度 | 判定 | 依据 |
|---|---|---|---|
| R1-P1-1 | P1 | **CLOSED** | 卡 D-4 `:59`、I-3 `:81/:89`、§兼容 `:128`、C-16 §0 `:22`、载体 §3 `:42` 五处同文「不铸/不绑、按现状 dispatch」，不再写 Run 的 `CORE_CAPABILITY_MISSING` |
| R1-P2-1 | P2 | **CLOSED** | C-06 `:56` 与 C-16 `:85/:88` 统一为整体 typed `SOURCE_ACCESS_DENIED`、零绑定写入、不返回部分成功；卡 `:84/:87`、载体 `:31` 同 |
| R1-P2-2 | P2 | **CLOSED** | C-16 `:87` 已补 facts 四键与 `source_locations` 物理身份核验、`source_entries/source_locations` 逐项、无路径回退；C-06 `:43` 同步 |
| R1-P2-3 | P2 | **CLOSED** | 冻结记录与 C-16 §2 row 5 均改为 pending/⏳（`FROZEN-C06:77`、`FROZEN-C16:46/:82`、载体 `:63`）；无 v1.2/v1.3 approved 断言（row 1 歧义见 P3-4） |
| R1-P2-4 | P2 | **CLOSED** | 载体 §4 `:49` 登记 L-G1/L-G9/L-G2/L-R11(L-G10)；卡 L-P2 `:135` 登记 L-G1/L-G2/L-G9/L-G10 |
| R1-P2-5 | P2 | **CLOSED** | C-16 `:87/:90` 明确复用 Run 目标/commit guard 同一谓词、无 publication 行按 open、L-R11 不属本命令、不引入第三套；与 `read_gate` docstring/接线一致 |
| R1-P3-1 | P3 | **CLOSED** | 卡 I-2 `:76` 改为 §6 |
| R1-P3-2 | P3 | **OPEN** | `FEA-C16:73` 的 §2.4 仍嵌在 §2 `RegisterSourceReadGrant`（`:37`）之下，§2 无 2.1–2.3；未登记（见 P3-1） |
| R1-P3-3 | P3 | **OPEN** | C-16 `:89` 仍写「复用 §6 闭集」，而 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`/`INVALID_REQUEST` 属 M2-C1 §5.7 envelope 码、不在 §6 表；无新增码（见 P3-2） |
| R1-P3-4 | P3 | **CLOSED** | `carrier.md` 与 `check-taskpath.log` 均已存在；副本卫生问题转为 P3-7 |
| R1-P3-5 | P3 | **CLOSED（时间）/ 残留去重** | `FROZEN-C06:4`、`FROZEN-C16:4` 已补 v1.2/v1.3 时间；`FROZEN-C06:32` 与 `:37` 的 v1.1 pin 仍重复（P3-9） |
| R1-P3-6 | P3 | **CLOSED** | C-06 `:3`、C-16 `:3` 已恢复上一版复核标注并指向冻结记录 |
| R1-P3-7 | P3 | **CLOSED（附措辞残留）** | C-16 `:83` 已限定 `COMMAND_CATALOG` + scope 展开器 + Run 起始语义；`COMMAND_CATALOG` 取值面已回源（`models.py:87`）（措辞问题见 P3-5） |
| R1-P3-8 | P3 | **OPEN** | C-06 `:58` 仍写「本组命令 v1.1」；§5 条件 4 已补 v1.2 说明但未登记（即 N-02） |

## 新 findings

| ID | 严重度 | 事实（path:line） | 最小修复 |
|---|---|---|---|
| **N-01** | **P2** | 「未变态」被写成 17：`FROZEN-C06:80`、`FROZEN-C16:85`「其他 17 pins \| 逐字节不变」、`FROZEN-C16:46`「其余 17 项不变」、载体 `:36`「其余 17 pins 断言」。本批 **2/18** 重签（C-06/C-16），未变应为 **16**；`other-16-pins.txt`（changed=0、16 项）、载体 `:45`、卡 D-2 `:57`/AC-P1 `:114`/AC-P3 `:116`/复核要求 `:123`/门禁 `:145` 均写 16 ⇒ 四处冻结记录/载体文本与实测及自证断言矛盾 | 四处改为「其余 **16** 项逐字节不变（C-06/C-16 同批共改）」；doc-only，不改契约字节、不需重算 pin |
| **N-02** | **P2** | C-06 `:87` §5 条件 4 由「（v1.1 minor 增量）」改为「（v1.1 minor 增量；v1.2 为 additive host-control 命令，不改 Run wire/`PROTOCOL_MINOR`）」，但载体 §2.A（`:22-25`，仅 4 项）与卡 I-2（`:73-76`，仅 4 项）均未登记；`C-06:96` 与 `FROZEN-C06:76` 仍称「仅新增条目」⇒ AC-P1「只包含 I-2/I-3 登记的增量」字面不成立 | 载体 §2.A 与卡 I-2 各补一条（「§5 冻结条件 4 追加 v1.2 版本说明」），冻结记录「修订内容」补记；若要求 C-06 变更记录措辞也精确，则改 `C-06:96` 并重算 C-06 pin（否则可登记为 P3 待下轮） |
| **P3-1** | P3 | §2.4 仍位于 §2 `RegisterSourceReadGrant` 之下（C-16 `:37`、`:73`），结构上像 register 的子节 | 下轮 UNFREEZE 重排为独立命令节（本次不改字节） |
| **P3-2** | P3 | C-16 `:89`「错误码：复用 §6 闭集」不含 §2.4 自身使用的 M2-C1 §5.7 envelope 码（`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`/`INVALID_REQUEST`）；**确无新增码** | 措辞改为「复用 §6 闭集 + M2-C1 §5.7 envelope 既有码，不新增」 |
| **P3-3** | P3 | C-06 `:58` 仍写「本组命令 v1.1」，与 C-16 §0 `:17` 的 `source-access-wire/1.2` 及 C-06 `:87` §5 条件 4 的 v1.2 说明不一致；r1 P3-8 残留未登记 | 下轮 UNFREEZE 将该句改为「本组命令 v1.1；v1.2 additive」（本次不改冻结条款字节） |
| **P3-4** | P3 | `FROZEN-C06:44` 冻结条件核验表 row 1 ✅ 的证据是 v1.0/v1.1 的 r1→r3，表内无 v1.2 行；易被误读为 v1.2 条件 1 已通过 | 在 row 1 或表头注明「v1.2 见 §6 pending」 |
| **P3-5** | P3 | C-16 `:83` 把 `COMMAND_CATALOG`（pipeline 命令值，`models.py:87`）与「Run 起始命令」混写；卡 `:83` 写 `<可由 scope 展开的 Run 起始命令>`，C-16 示例写 `<PipelineCommand>`，两者措辞不一致 | 明写 `command` = `COMMAND_CATALOG` 值、与本 Run `StartRun` payload 同域；卡/契约统一 |
| **P3-6** | P3 | §2.4 facts 与表映射对 **folder 源**不精确：`source_locations` 只有容器/目录级 `content_digest/volume_serial/file_id/size_bytes`（C-15 `:77-93`），folder 的 `entries[].facts` 是逐成员文件的 facts（`source_read_refs.py:678-720` 以 `folder_entries` 保存）；字面按 `source_locations` 核对 size/sha256 可能误拒合法 folder | 明确「容器源：单 entry facts ↔ `source_locations`；folder：`volume_serial/file_id` ↔ `source_locations`，`size/sha256` ↔ `source_entries`」 |
| **P3-7** | P3 | 证据 `carrier.md` 是 doc 载体的**逐字节副本**（非摘要），其 `../plan/...` 链接在 `verification/` 下不可解析；DSH 追加 delta 结论后副本会与 doc 载体分歧；卡 I-5 `:103` 称「摘要与复核结论」 | 改为指针/摘要并标快照时间，或追加结论时同步副本（含相对链接修正） |
| **P3-8** | P3 | 卡 `reviewer`（`:10`）与 AC-P2（`:115`）仍只指向 r1；冻结记录写「session/reviewed_head 在载体与 r1.md」，而载体 §6 尚无 delta 的 session/reviewed_head | DSH 在 approved 后把 r2 session `587ff25a…`/`reviewed_head` 追加到载体 §6（含 `carrier.md`）并更新卡/冻结记录指针 |
| **P3-9** | P3 | `FROZEN-C06:32` 与 `:37` 的 v1.1 pin 重复（r1 P3-5 去重未做，无害冗余） | 下轮记录维护去重 |

> 统计：**P0=0 / P1=0 / P2=2（N-01/N-02）/ P3=9**。其中 **P3-1…P3-3 为 r1 残留仍 OPEN**（R1-P3-2 §2.4 嵌套、R1-P3-3 错误码措辞、R1-P3-8 的 C-06:58 仍写 v1.1）；**P3-4…P3-9 为本轮新增**（P3-4 C-06 条件核验表无 v1.2 行；P3-5 `command` 措辞；P3-6 folder facts 映射；P3-7 `carrier.md` 副本；P3-8 r2 session/指针回填；P3-9 v1.1 pin 重复）。N-01/N-02 与全部 P3 均为非契约语义问题，其中 N-01/N-02 是提交前必须处理的登记/证据准确性缺陷。

## 最终判定

- **verdict：`changes_requested`**（P0=0、P1=0、P2=2、P3=9）。
- **已闭环**：r1 的唯一 P1 与全部 P2 关闭；C-06 v1.2 / C-16 v1.3 的语义面、不变量、pin 与证据均通过（18/18、16/16 未变、Run wire/`PROTOCOL_MINOR`/schema/依赖/M2-C1 零 diff、`pre-post.sha256`/`changed-lines.diff`/日志可复算、无夸大）。
- **必须修（提交前）**：
  1. **N-01**：`FROZEN-C06:80`、`FROZEN-C16:85`、`FROZEN-C16:46`、载体 `:36` 的「17」改为「16」，并注明 C-06/C-16 同批共改（doc-only；不影响 pin）。
  2. **N-02**：在载体 §2.A、卡 I-2（及冻结记录「修订内容」）登记 C-06 §5 条件 4 的 v1.2 追加句；若同时修正 `C-06:96`「仅新增条目」措辞，则须重算 C-06 pin 并重跑 `verify_pins`。
- **修复后收口路径**：若选择「保留 §5 句 + 补登记」（推荐）：C-06/C-16 契约字节不变 ⇒ sha 仍 `6214ef77…`/`7c355ccb…`、pins 仍 18/18；只需复跑 `check.ps1`（默认 + `-TaskPath`）并窄面确认登记文本与载体/卡 diff，无需重跑完整字节复核。若改契约字节，则重算 C-06 pin、重跑 pins，再做一次窄面确认。
- **不构成**：本报告不批准提交，不构成实现授权、产品可用结论或 push 授权。

## 复核后工作树变更（scope note，2026-11-06 23:39 实测）

本报告 §0–§F 的数值是 **r2 复核时点（约 23:20–23:33）** 的工作树字节：C-06=`6214ef77…`、C-16=`7c355ccb…`、`changed-lines.diff`=`0f6edb25…`、`pins.log` 的 C06=`6214ef77f57d`。本报告撰写期间，工作树在 **23:36:20–23:37:44** 被 DSH 并发更新（写入已停止：23:38–23:39 连续两次快照哈希一致）。**最终字节的实测**：

| 项 | 最终值（23:38–23:39 实测） |
|---|---|
| C-06 sha256 / blob | `99831a20ffd608257b4f2cf46f63f3836f605b35a4de787c4ab803e5dd6013d4` / `9bbd93a01cb74886f2cddb6aeeafe28455baaaf3`（纯 LF，0 CRLF） |
| C-16 sha256 / blob | `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5` / `a5143d5e162f60ffbd902d7dc60792b162c6a378`（未变） |
| C-06 diff | 仅 4 个 hunk：`@@ -1,7 +1,7 @@`、`@@ -40,6 +40,7 @@`、`@@ -52,6 +53,7 @@`、`@@ -91,3 +93,4 @@`；**§5 条件 4 已回退到 HEAD 文本（无 hunk）**，故「仅新增条目」重新成立 |
| `pre-post.sha256` | post = `99831a20…` / `7c355ccb…`（已同步重生成） |
| `changed-lines.diff` | 与当前 `git diff HEAD -- C06 C16` **逐字节一致**，sha256 均为 `11351eea5aac3264de517b54f78930a228d99aee4602a1814845b05a64878f18` |
| `logs/pins.log` / `verify_pins` | C06 `99831a20ffd6`、C16 `7c355ccb8f82`；复跑 `PIN AUDIT: PASS (all 18)`，与日志逐行一致 |
| `logs/check.log` / `check-taskpath.log` | 已重生成（23:37:43/44）；与复跑 `PASS (3 warnings)` 逐行一致 |
| 冻结记录 | `FROZEN-C06:16` = `99831a20…`；「其他 16 pins」（`:81`）；`FROZEN-C16:85` 亦改「16」、`:46`「其余 16 项不变」；`FROZEN-C06:49` 新增 v1.2 条件行（⏳） |
| 载体 | §2.C `:36` 改「其余 16 pins 断言」；§6 `:63` 记录 r2 处置（回退 §5、17→16、补 FROZEN-C06 §2 v1.2 行、C-06 重算 pin），`:65` **r3 pending**；`carrier.md` 与 doc 载体同哈希 |
| 文件面/不变量 | `git diff --name-only HEAD -- doc/plan/` 仍为 5 文件；`doc/contracts`/`src`/`apps`/`tools`/`tests` 零 diff；C-16 未变，不变量无新增改动 |

**含义**：
- 本报告的 **N-01**（17→16）与 **N-02**（§5 未登记）在最终字节中已被处置：N-01 四处改 16；N-02 以**回退 §5 句**关闭（C-06 因此重签为 `99831a20…`）。本报告的 `changes_requested` 判定只适用于 `6214ef77…` 时点字节。
- **`99831a20…` 最终字节尚待载体 §6 所述 r3 fresh-context 窄面复审**；本报告不构成对其批准。r3 应重点核对：C-06 4 个 hunk 是否仍全部落在载体 §2.A/卡 I-2 登记内、`99831a20/7c355ccb` 与冻结记录/pins/证据是否一致、C-16 §2.4 语义未因回退受影响。
- **转交 r3 的观察（非本报告 finding 编号）**：载体 §6 `:64` 的 P3 引用（「P3-2（§2.4 置于 §2 下）」「P3-3『复用 §6 闭集』」「P3-8（C-06 §2.3 末尾仍引 v1.1）」）与本报告 P3 表编号错位一件（本报告为 P3-1/P3-2/P3-3）；r3 或 DSH 应校正引用，避免处置记录与报告对不上。

## 真实性声明

本报告是本次复审中**唯一**写入的文件（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r2.md`）。复审者未参与 C-06 v1.2 / C-16 v1.3 的起草、r1 复核或本轮处置；未修改被审字节、证据、卡、冻结记录或矩阵；未执行 `git add`/`commit`/`push`；未删除或移动任何文件。所有 sha256、pin、门禁结论均由本轮命令在 `reviewed_head=b17d7282193afa6583c6c7a7bfc6456d04313af5` 的**工作树最终字节**上实测得出，未采信载体/卡面的自述结论。未跑项已在 §0 标 `NOT_RUN`。
