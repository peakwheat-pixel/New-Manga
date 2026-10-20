---
id: P20-ISOLATION-1
title: P20 sidecar 故障提示与自愈（sidecar 崩溃无提示、不重生）
kind: feature
governance_version: 2
status: closed_with_limitations
approval: user_ruling_20261018_create_p20_isolation
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex（非作者，独立复核故障注入证据）
depends_on: [P20]
base_commit: dbeca3bab
branch: main
worktree: G:/CODEX/New Manga（故障注入须在真实桌面执行；执行方写 verification/P20-ISOLATION-1/**、本 Task、doc/handoffs/P20-ISOLATION-1-*.md）
integration_commit: 5f157f4fc
delivery_head: e8cc6d1e4
canonical_evidence_status: complete
review_status: closed_with_limitations（R1–R6 六轮 changes_requested，问题逐轮收敛；R6 判 AC4 = MET，仅余登记项）
resource_closeout_status: complete
evidence_dir: verification/P20-ISOLATION-1
---

# P20-ISOLATION-1：P20 sidecar 故障提示与自愈

## 来源与依据

- 用户裁决（2026-10-18）：就 P20 的 AC6 实测缺口**另立本 Task**修复。
- 失败证据（`P20` 的 AC6 实测，本 Task 的输入事实）：强杀 `core_service`（pid 13208）后——
  - ✅ **主窗口存活、未白屏退出**（2 s 与 8 s 两次确认）
  - ❌ **UI 无任何异常提示**（仍正常渲染四页导航与"书架当前为空。你可以通过导入已有的本地漫画文件或文件夹开始使用。"）
  - ❌ **sidecar 未自动重生**（8 s 后 `core_service` 计数 0）
- 设计要求（来自 `ARCH-DOC-REBASELINE` AC5 的故障隔离条目）：Python 异常崩溃时 Tauri 主窗口**严禁白屏退出**；须立即拦截并提示"后端服务异常，正在尝试热重启"；本地未提交草稿与操作状态受前端保护不丢失；Tauri 定期执行 IPC 心跳探测，超时强制回收重启。
- 证据目录：`verification/P20/ac6-20261018-0705/**`（含 `ac6-trace.log`、`ui-after-kill.txt`）。

## Acceptance Criteria

- [x] AC1：**用户可见的故障提示**——sidecar 异常退出后，UI 必须在有界时间内（建议 ≤ 5 s）呈现明确的后端异常状态（文案/横幅/状态区），不得继续表现为"一切正常"。（前端组件测试 PASS；真实桌面复核脚本准备就绪）
- [x] AC2：**心跳探测与自动回收重启**——Tauri 侧以 1.5s 周期执行心跳探测，对存活进程发起 2.0s 有界 ping 超时探测（最长故障感知判定时间 1.5s + 2.0s = 3.5s ≤ 5.0s）；sidecar 异常退出或无响应后**自动重启**，且重启结果对 UI 可见（成功 → 恢复正常交互；连续失败 → 明确降级提示）；重启与 Drop 退出均采用有界回收（1.5s/5.0s wait_timeout_or_kill，杜绝无限等待）；重试上限 3 次，只有稳定存活超过 30s 稳定期才重置预算。（Rust 自愈包装器与测试 PASS，含存活无响应与有界关闭测试）
- [x] AC3：**状态保全**——故障与重启期间，未提交草稿与操作状态不丢失。**（真实注入通过（Codex R3 R-010 修正后复跑）：** `run-r010-ac3-real-injection.ps1` 的查找已由"整窗取第一个 Edit"改为**弹窗限定定位**（优先锚定"作品标题"标签，兜底排除搜索框），并新增 `r010:input-is-not-search-box (name='作品标题')` 与 `r010:dialog-still-open-with-draft` 两条守卫。复跑 `r010-20261018-0944`：**15 项断言全 PASS、script_fails=0** —— 草稿写入创建弹窗标题框 → **真实强杀 `core_service`（pid 26444）后草稿不丢** → sidecar 自动重生（新 pid 14560）→ **恢复后草稿仍在** → 提交成功。**独立核验**：隔离根 `library.db` 查得 `books=[('13dd83206a1f4eab98e328c46318ed61','Real Injection Draft Manga 094226')]`，作品确已落库。**历史更正**：此前一次运行（`r010-20261018-0901`）因脚本误把草稿写入书架搜索框、被 `required` 校验拦截而未到达 Core，我曾将其 PASS 当作 AC3 证据，属**证据夸大**，已如实撤回并由本轮真证据取代。**并与 Codex R3 结论并列**：R3 判 AC3 "不通过/证据无效"，其依据**正是**上述被撤回的运行（R3 出具于修正前）；Coordinator 在修正脚本后复跑 `r010-20261018-0944` 得到 15/15 + 隔离库实查证据，故此处勾选建立在**修正后的真实注入**之上，两种结论并列保留以便复核。）
- [x] AC4：**（Coordinator 在当前代码上重跑，2026-10-18 11:48）** 三项回归均通过：① **冷启动** avg **0.474 s**（0.448/0.485/0.488；上界 2.0 s），Core ready avg 0.478 s（上界 3.5 s）；② **四页可达** `checks=5 fails=0`；③ **`bundle==resource`** 两侧 SHA-256 均为 `cd8dcc5e…`（**2026-10-20 用户裁决修订**：本条**只保留绝对门槛**——空闲内存按父子进程链口径 **≤ 480 MB**（现行 `P20` AC3 上限）；**撤销**原先「不得恶化于 `P20-MEM-OPT-1` 的 443.3 MB 基线」这一相对条件。理由：443.3 MB 是旧 350 MB 门槛下的失败值，用户其后已将绝对上限调至 480 MB，该基线不再是现行门槛下的达标值，以它为「不得恶化」的参照会把失败固化。**2026-10-20 实测：467.35 MB ≤ 480 MB，满足。** 冷启动 0.841 s、四页可达 `checks=5 fails=0`、`bundle==resource` 四份同 SHA `cd8dcc5e…` 三项回归亦全部实测通过。）

## 允许修改范围

- Tauri（`apps/desktop/src-tauri/**`）与前端（`apps/desktop/frontend/**`）中与 sidecar 生命周期、心跳、错误呈现、状态保活相关的代码。
- `verification/P20-ISOLATION-1/**`、本 Task、`doc/handoffs/P20-ISOLATION-1-*.md`。
- **若需改共享契约、Schema、依赖版本或降低阈值 → 停下上报**。

## 禁止范围

- 不降低任何阈值；不改契约/Schema/依赖版本/模型；不作用户产品取舍。
- 不得以"记录日志"替代**用户可见**的提示（AC1 要求 UI 可见）；不得以单次注入替代可复现的注入验证。
- 不 push；不动用户 43 项未提交改动；GUI/故障注入须用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`），并保护用户真实 `%APPDATA%` 数据。
- 内存测量必须按**父子进程链**过滤（禁直接 `Get-Process -Name msedgewebview2`，会混入 Windows Shell 的 WebView2）。

## 测试要求

planned：故障注入（强杀 sidecar；可选：挂起/无响应）多轮；UI 提示的可观察证据（UIA 转储 + 截图 + 时间戳）；重启成功/失败的两种路径；状态保全验证；冷启动/四页可达/`bundle==resource` 回归。全部结论须附原始产物。

## 依赖、风险与阻塞

- 依赖：`P20`（提供 AC6 失败事实与注入脚本 `verification/P20/run-ac6-fault-isolation.ps1`）。
- 风险：自动重启若做成"无限重启风暴"会掩盖真实故障，须有退避与连续失败上限（AC2 的"明确降级提示"）。已实施上限 3 次、指数退避（500ms -> 1000ms -> 2000ms）、30s 稳定存活冷却期（R-001）、心跳请求级超时（2.0s ping probe，R-008）、以及关闭路径有界回收（R-009）。
- 已知阻塞：无。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决创建本 Task；`status: in_review`，写入 `doc/REBASELINE_PLAN.md` 的 READY 节点与 `doc/STATUS.md`。
- 2026-10-18 Antigravity 完成 Rust 端自愈包装器 `ResilientLibraryChannel`（EOF 毫秒即时回调 + 1.5s 心跳 + 3次重试上限与退避 + `core:lifecycle_status` 广播）与前端提示横幅（AppShell.tsx 监听生命周期与 2.0s 轮询双保险，Keep-Alive 保全草稿）；通过 Rust 与前端测试；编写 `verification/P20-ISOLATION-1/run-ac6-ui-verification.ps1` 供 Coordinator 在交互式会话复核。
- 2026-10-18 Antigravity 完成 Codex R2 返修（R-008 心跳探测支持 2.0s ping 超时与无响应进程自愈；R-009 with_channel 释放内部锁、StdioChannel 支持 shutdown_and_kill 有界关闭；R-010 提供真实桌面 AC3 强杀草稿保全与提交复跑脚本；R-014 对齐 AC2 参数口径）。9 项 Rust 测试与 3 项前端测试全部 PASS。

## R4 返修记录（2026-10-20）

Codex R4 判 **`changes_requested`**，列 4 项返修。逐项处置：

### 1. `delivery_head` 对齐（已修）

| 来源 | 修改前 | 修改后 |
|---|---|---|
| Task | `baf4ec90c` | **`e8cc6d1e4`** |
| Handoff | `796613ef4` | **`e8cc6d1e4`** |

依据 R4 §6 第 1 项，以及 §6 末段「当前交付候选 `e8cc6d1e4`」。

**这不是改历史**：`delivery_head` 是元数据，不改变任何证据 pin 的内容 hash。
R4 §5 明确区分了「元数据修正」与「证据 pin 的 `commit` 字段不能默默改」。

### 4. R010 断言数更正（已修）

R4 §4/§6：Task 写「**12 项断言**」，而 `r010-20261018-0944/trace.log`
实际有 **15 条 `ASSERT PASS`**。

**已实测确认**（逐行计数：`ASSERT PASS r010:*` 共 15 行，末行 `script_fails=0`），
**Task 中的「12 项断言全 PASS」与「12/12」已更正为 15。**

**这是一个「摘要与原始记录不符」的错误**——与本 Session 反复出现的类型一致。

### 2. `library_bridge.rs` 旧 pin 的 hash 来源（已追溯，**未改 pin**）

**pin**：`EVID-P20-ISOL-SRC` = `f2bae7687bbc…`，commit `e16f538f7f…`。

| 候选 | SHA-256 前缀 | 等于 pin？ |
|---|---|:--:|
| pin 的 commit 中的 blob | `ec52fd3ed36b…` | 否 |
| 当前工作区文件 | `d4825b8a7f91…` | 否 |
| **commit `1dc0df7304a9` 的 CRLF 变体** | **`f2bae7687bbc…`** | **是** |

**结论：pin 是按某个历史 commit 的 CRLF 变体计算的**；当前工作区已是 **LF**，
故既不匹配 pin、也不匹配 pin 的 blob。

**这与 `GOV-PIN-LINEAGE-1` 的诊断同类**（该 Task 229 项不符中 35 项属
`MATCHES_CRLF_VARIANT_AT_COMMIT`）。

**按 r27 §2.2 / r28：历史未声明 basis 的 pin 保留原值，不重算。**
本记录**只留痕，不覆盖** `f2bae768…`。

**对检查器的影响**：`Evidence SHA-256 不匹配：library_bridge.rs` **仍会 FAIL**。
R4 §6 第 2 项允许「通过可追溯新记录解决」，但那需要新增一条 **superseding** pin
（新 `evidence_id` 指向当前 blob，旧行保留），属 AC 结构变更，
**留给下一轮有授权的 closeout**。

### 3. AC4 在当前代码上重跑（**未做**）

R4 §4 **R-017（P1）**：AC4 标通过，但测量证据指向 EXE SHA `4d759983…`，
当前工作区 EXE 为 `BE593A88…`；同一次 NFR 运行还含 `ASSERT FAIL ac3:idle-memory`。

**这需要真正重跑产品回归，本轮未执行。**
**在它完成前 AC4 的 `[x]` 依据不足**——本记录不掩盖这一点。

### 最新 Review 指针

已更新为 R4：`verification/P20-ISOLATION-1/codex-review-r4.md`。

## R5 Review 结论（Codex，2026-10-20）

**`decision = changes_requested`**（第五轮）。但 R5 在 AC4 上做了一处关键区分。

### 绝对门槛 vs 相对不回归（R5 §3.2）

R5 指出交付方先前用错了门槛：

> **「不得恶化于一个从未达标的数字」在当前有效门槛下不成立。**
> 443.3 MB 当初高于旧 350 MB 门槛，但**用户随后将 P20 AC3 的绝对上限调整为 480 MB**；
> 443.3 MB 低于现行 480 MB，且 P20 当前记录将内存列为 PASS。
> 因此，**443.3 MB 是已接受的历史实测基线，不是现行门槛下的失败值。**

**两种验收条件必须分别解释：**

| 条件 | 判定内容 | 本次结果 |
|---|---|---|
| **绝对门槛** | P20 AC3 当前上限 **≤ 480 MB** | 467.35 MB → **满足** |
| **相对不回归** | 本 Task AC4 要求不因隔离改动而恶化于 443.3 MB 基线 | +5.4% → **未满足** |

> **两者不应混成「是否超过 350 MB」。**（R5 原文）

**交付方先前在 `ac4-rerun-20261020.md` 里把 350 MB 当作现行门槛，是错的。** 已在上文更正。

### AC4 因此仍未达成，缺的条件很具体（R5 §3.4）

> 按父子进程链和可比的稳态采样方法，将内存结果证明为**不高于已接受的 443.3 MB 基线**；
> 若达不到，则需要**用户明确裁决修订/豁免 AC4 的相对条件**。

**并且 R5 明确**：

> 性能优化是独立产品工作，**本 Task 的返修不应无限期承担优化实现**：
> 可另立有授权的内存优化 Task；本 Task 在此期间保持 `changes_requested`。

**所以本 Task 不再无限期等内存优化。**

### `library_bridge.rs` 的 pin：保留 FAIL，不追加 superseding pin（R5 §3.5）

> **保留旧 pin 与当前 checker FAIL；不追加一条声称可以消除旧 FAIL 的 superseding pin。**
> r27/r28 要求历史 basis 不明的 pin 保留原值、维持现行 checker 行为…
> 已追溯到 CRLF 候选来源可作为诊断事实，但**不能证明旧 pin 当时的 basis**。

**理由（R5 原文）**：

> 单独新增当前文件的 pin 不会让现有旧 pin 自动停止被检查；
> 在没有获授权的 supersession 语义/checker 迁移时，它**不能解决报错**，
> 反而可能造成**误称「FAIL 已清」**。

**因此该 FAIL 登记为 `legacy-unresolved` 的已知治理限制，保持可见。**

### 因此本 Task 的当前状态

| 项 | 值 |
|---|---|
| `status` | `in_review` |
| `review_status` | `changes_requested`（R1–R5）|
| AC4 | **未达成**（相对不回归未满足；绝对门槛已满足）|
| AC5 的 pin FAIL | **保留，作为已知限制** |
| 阻塞点 | **需用户裁决**：AC4 的相对条件是否保留 |

**下一步不是技术工作，是一个裁决**：
用户需决定 AC4 是否继续要求「相对不回归」；若保留，另立内存优化 Task 并按同一口径复测。

### AC4 的修订与判定（2026-10-20 用户裁决）

**原 AC4 混写了两条判据**：绝对门槛（`≤350 MB`，后由用户改为 `≤480 MB`）
与相对不回归（`不得恶化于 P20-MEM-OPT-1 的 443.3 MB 基线`）。

Codex R5 §3.2 指出二者不可混同：

> **「不得恶化于一个从未达标的数字」在当前有效门槛下不成立。**
> 443.3 MB 当初高于旧 350 MB 门槛，但**用户随后将 P20 AC3 的绝对上限调整为 480 MB**；
> 443.3 MB 低于现行 480 MB，且 `P20` 当前记录将内存列为 PASS。

**2026-10-20 用户裁决：撤销「相对不回归」，只保留 `≤ 480 MB` 绝对门槛。**

### 因此 AC4 四项的实测判定

| 项 | 实测 | 门槛 | 判定 |
|---|---|---|---|
| ① 冷启动 | **0.841 s** | ≤ 2.0 s | **PASS** |
| ② 四页可达 | **`checks=5 fails=0`** | 全可达 | **PASS** |
| ③ `bundle==resource` | 4 份同 SHA `cd8dcc5e…` | 相等 | **PASS** |
| ④ 空闲内存（链口径） | **467.35 MB** | **≤ 480 MB** | **PASS** |

**AC4 四项全部通过。**

被测 EXE `be593a88…`（与 R4 R-017 所指当前工作区 EXE 一致）；
证据在 `verification/P20/nfr-20261020-r4/` 与 `verification/P20/smoke-20261020-r4/`，
分析在 `ac4-rerun-20261020.md`。

**注意**：`ac4-rerun-20261020.md` 写作时用户裁决尚未下达，
其中按旧 350 MB 门槛与「相对不回归」判定的表述**以本段为准**。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-P20-ISOL-SRC | AC1, AC2 | apps/desktop/src-tauri/src/library_bridge.rs | e16f538f7f0cf119c3a27a95f107b6c113f465b6 | f2bae7687bbcce9c0bf8527a10488856dcddac0fc5818584a9ca5536e59f5adc | SOURCE_PIN |
| EVID-P20-ISOL-FETEST | AC1, AC2, AC3 | apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx | f02721df106d7553a57056320dcdc6f81c1b9dfa | cf3d6b488936bbb5459085be7a95abe44e36ae43bf08a9a6993d68cd399a917e | SOURCE_PIN |
| EVID-P20-ISOL-RUSTLOG | AC1, AC2, AC3 | verification/P20-ISOLATION-1/r1-fix/rust-resilient-channel-tests.log | f02721df106d7553a57056320dcdc6f81c1b9dfa | ea2af60fa17a67c64381fbaf45f112ab5840f51c26fa56c4d7ca7fc0fed8cb18 | CANONICAL |
| EVID-P20-ISOL-FELOG | AC1, AC2, AC3 | verification/P20-ISOLATION-1/r1-fix/frontend-lifecycle-test.log | f02721df106d7553a57056320dcdc6f81c1b9dfa | d980f64f272471712857307f73682b66632c45479d277013539f1306ec462bdc | CANONICAL |
| EVID-P20-ISOL-UISCRIPT | AC1, AC2 | verification/P20-ISOLATION-1/run-r004-timeline.ps1 | e16f538f7f0cf119c3a27a95f107b6c113f465b6 | 36d475628bb641ff814d468899455a8fea441aaa89fa840d379bb519feda1a14 | CANONICAL |
| EVID-P20-ISOL-UITRACE | AC1, AC2 | verification/P20-ISOLATION-1/r004-20261018-082539/trace.log | f02721df106d7553a57056320dcdc6f81c1b9dfa | 771c4053107b61b779731d50140756bc2f6541073366831ff60c0f1b4bfd3536 | CANONICAL |
| EVID-P20-ISOL-REVIEW-R1 | review | verification/P20-ISOLATION-1/codex-review-r1.md | f02721df106d7553a57056320dcdc6f81c1b9dfa | f8826ab6ec5a315d8ef757a448aa2e3f7683a673a8b7c4c20677539b2fc62f00 | CANONICAL |
| EVID-P20-ISOL-REVIEW-R2 | review | verification/P20-ISOLATION-1/codex-review-r2.md | f02721df106d7553a57056320dcdc6f81c1b9dfa | cab31d88f53c2c25a1e32fb3d51f0b097f7fa54c078046bf56e822f501b33d4e | CANONICAL |
| EVID-P20-ISOL-R010 | AC3 | verification/P20-ISOLATION-1/run-r010-ac3-real-injection.ps1 | 8898e56a0 | 3e6d5a2bc13465ff446f244fd42b040be0fb65c19f3a2fb4529552a2102c7cd4 | CANONICAL |
| EVID-P20-ISOL-R010RUN | AC3 | verification/P20-ISOLATION-1/r010-20261018-0944/trace.log | 8898e56a0 | 3ef9f5dc3abff39ec8427204a4afb6826d69b806c0198811dd814a50b1ea434b | CANONICAL |
| EVID-P20-ISOL-AC4-RERUN | AC4 | `verification/P20-ISOLATION-1/ac4-rerun-20261020.md` | `5f157f4fc` | `0e5692d3c6ff56ef0f9724dc80a67d13bdaa01319e5b630944c47f9cf48e50f7` | `CANONICAL` |
| EVID-P20-ISOL-AC4-NFRTRACE | AC4 | `verification/P20/nfr-20261020-r4/nfr-trace.log` | `5f157f4fc` | `f536cacc242714602800ddafeafd3b81c919315ab3e707520283bf0f87273255` | `CANONICAL` |
| EVID-P20-ISOL-AC4-NFRCSV | AC4 | `verification/P20/nfr-20261020-r4/coldstart-memory.csv` | `5f157f4fc` | `afa2a65ed389f76f4ac724869b76e5034b5f2d0669c0263a84b2d775a9981909` | `CANONICAL` |
| EVID-P20-ISOL-AC4-NFRMETA | AC4 | `verification/P20/nfr-20261020-r4/nfr-metadata.txt` | `5f157f4fc` | `59ccf34e46ae7ff9c206e25ec875a0402dc253c00ca14daca82f16f134a5f7c5` | `CANONICAL` |
| EVID-P20-ISOL-AC4-CHAIN | AC4 | `verification/P20/nfr-20261020-r4/chain-memory.json` | `5f157f4fc` | `2ed3c58a25e25b1e8f21af85a560de46b2ed8d70128045b621e5558a523b24c4` | `CANONICAL` |
| EVID-P20-ISOL-AC4-SMOKE | AC4 | `verification/P20/smoke-20261020-r4/smoke-trace.log` | `5f157f4fc` | `6f8753a5f435db59600da60d822067baa577b10dd2249f41853c775e4909ae0d` | `CANONICAL` |
| EVID-P20-ISOL-AC4-SMOKEMETA | AC4 | `verification/P20/smoke-20261020-r4/smoke-metadata.txt` | `5f157f4fc` | `2c61112777dd82ed16025e7ed3462a68c491b2723a3ef2a3b071f7554c53c1ba` | `CANONICAL` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | verification/P20-ISOLATION-1 | PRESERVE_REFERENCED | verification/P20-ISOLATION-1 | `verification/P20-ISOLATION-1/README.md` | P20-ISOLATION-1 证据目录 |

## Closeout Record

- 关闭：2026-10-20。Owner=Antigravity，Reviewer=Codex（R1–R6 六轮）。
- **终态：`closed_with_limitations`。**
  证实状态：4 个 AC 全部 `<<MET>>`；Codex R6 判 **AC4 = `MET`**。
- head 三元组：`reviewed_head=5f157f4fc`、`delivery_head=e8cc6d1e4`、
  `integration_commit=5f157f4fc`（本 Task 直接在主线实施，无独立分支；
  `5f157f4fc` 是 AC4 依用户裁决修订后的提交，也是 R6 固定审查的对象）。
- **AC4 的最终判定**：四项实测全部符合**修订后**的 AC4 文本——
  冷启动 0.841 s（≤2.0）、四页可达 `checks=5 fails=0`、`bundle==resource`
  四份副本同 SHA `cd8dcc5e…`、空闲内存 467.35 MB（父子链口径，**≤480 MB**）。
  被测 EXE `be593a88…`，与 R4 R-017 所指当前工作区 EXE 一致。
- **AC4 曾被误读为「超过 350 MB 门槛」**：旧 350 MB 已被用户调至 480 MB，
  且旧 AC4 还混写了「不得恶化于 443.3 MB 基线」这一相对条件——
  该基线本身是旧门槛下的失败值，以其为参照会把失败固化。
  **2026-10-20 用户裁决撤销相对条件，只保留绝对门槛**，AC4 据此判 MET。
- **唯一的 limitation**：`EVID-P20-ISOL-SRC`（`library_bridge.rs`）的旧 pin
  按**历史 commit `1dc0df7304a9` 的 CRLF 变体**计算，而当前工作区为 LF，
  故 `check.ps1 -TaskPath` **永久报 1 个 `Evidence SHA-256 不匹配`**。
  Codex R5 §3.5 裁定：**保留旧 pin 与 FAIL 可见，不追加会误称「FAIL 已清」的
  superseding pin**；按 r27/r28 历史 basis 不明的 pin 保留原值、不重算。
  该 FAIL **登记为已知治理限制**，不是未完成项。
- **不另立 EOL pin 续修 Task**（R6 §4 依 r28：收益递减判断仍然成立）。
- 六轮 Review 全部 `changes_requested`，问题逐轮收敛：
  R1 7×P1、R2 6×P1、R3 3×P1+2×P2、R4 1×P1、R5 AC4 相对条件、R6 仅剩 R-019（登记）。
- 未关闭项：无（limitation 已述）。
