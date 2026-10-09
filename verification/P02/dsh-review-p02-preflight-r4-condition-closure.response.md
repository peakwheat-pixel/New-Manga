# P02 R10 条件闭合候选 — 非作者只读 exact-head Review（DeepSeek Harness）

## 0. 裁决摘要

| 项目 | 结论 |
|---|---|
| 决策 | **`APPROVED`** |
| 计数 | P0=0 / P1=0 / P2=0 / P3=0；另有 **5 项非阻断观察**（O-1..O-5，属可选措辞/可追溯性改进，不构成本候选的 Review 条件） |
| 条件闭合 | r9 六项条件的处置**全部成立**，且本轮对可复算的关键数字做了独立复算（详见 §3/§6） |
| 是否阻挡后续 Smoke admission 记录 | **不阻挡**。但本 Review 本身**不产生** Smoke admission；admission 仍须由 Codex 另立 checkpoint，并在**新鲜的非提权 stage-1 preflight 通过后**才可记录（§8） |

---

## 1. 审查对象与 checkout 状态

| 项目 | 值 | 核验方式 |
|---|---|---|
| 审查分支 | `review/deepseek/P02-preflight-r4-condition-closure-92dc7361` | `git rev-parse --abbrev-ref HEAD` |
| 审查 worktree | `C:/Users/49745/.codex/worktrees/P02-preflight-r4-condition-closure-92dc7361-review-dsh` | `git rev-parse --git-common-dir` = `G:/CODEX/New Manga/.git` |
| reviewed HEAD | `92dc7361194f1db8fdf7aff3a15a3d234ae56678` | `git rev-parse HEAD`（审查前后一致） |
| reviewed tree | `73511f7ba03d6b2215f4dad9c5a3c7f442471a6f` | `git rev-parse 'HEAD^{tree}'` |
| parent/base | `083d2b47f7051c2dedd0d9ae4346ae1affab6c1b`（单父） | `git rev-parse HEAD^` / `git log -1 --format=%P` |
| commit | `docs(P02): close r9 smoke review conditions`，`2026-10-10T03:08:23+08:00` | `git log -1` |
| 候选 diff | `083d2b47..92dc7361` = **7 paths**（3 A + 4 M），`+152 / −21`，全部落在 `verification/P02/**` | `git diff --name-status/--stat`，EXIT=0 |
| 作者侧一致性 | 作者 worktree `codex/P02-process-isolation` 亦在 `92dc7361` | `git worktree list` |
| 项目 live main | `ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50` | `git worktree list`（root main） |
| checkout 状态 | **干净**；审查开始前与结束后 `git status --porcelain=v1 -uall` 均为空，index 亦为空 | 两次 `git status`，EXIT=0 |

提交路径集合与候选声明**逐项一致**：`codex-scratch-build-process-isolation-scope-delta-r1.md`(M)、`codex-scratch-build-preflight-r2.md`(M)、`codex-scratch-build-preflight-observations-r2.json`(M)、`codex-checkpoint-p02-preflight-r4-start.md`(M)、`codex-preflight-r4-validation.md`(M)、`codex-checkpoint-p02-preflight-r4-condition-closure.md`(A)、`codex-checkpoint-p02-smoke-admission-r1.md`(A)。

**范围纪律**：仅审查 `083d2b47..92dc7361` 及必要引用语境。本轮**未修改任何文件、未创建 clone、未启动 Windows Sandbox、未运行 Smoke/Build/产品测试、未提权**（`Get-WindowsOptionalFeature` 仅复现了"需要提升"错误，`elevation_performed=false` 语义未被改变）。

---

## 2. 审查方法（只读）

`git show/cat-file/rev-parse/diff/--check`、逐行 `read` 候选文件、`python -B -X utf8` 只读复算（JSON/TSV/XML/哈希/manifest）、路线校验器、Markdown 本地链接解析、宿主环境只读复测。另引用了作者 worktree 内**未跟踪**的 r9 审查附件 `verification/P02/dsh-review-p02-preflight-r4.stdout.md` 作为引用语境（用于核对六条件原文），并**刻意未读取** `dsh-review-p02-preflight-r4-condition-closure.response.md`（0 字节，为本次答复落盘位置），以避免答案污染。

---

## 3. C-01..C-06 逐条处置判定

| 条件 | 判定 | 独立核验证据（含文件:行） |
|---|---|---|
| **C-01** 尺寸比较口径 | **CLOSED** | `observations-r2.json` 20 条记录中，`expected_size_bytes=""` 的恰 6 条 `size_match=null`（`:209,220,363,374,385,396`，其余 14 条 `true`）；声明计数 `:400-404` = hash 20/0、size 14/0、未登记 6，与记录重算逐项吻合。6 条未登记项的清单与冻结登记表 `codex-scratch-build-preflight-inputs-r1.tsv`（`expectedBytes` 为空的恰 6 行）**完全一致**；`preflight-r2.md:13`、`codex-preflight-r4-validation.md:21`、`codex-checkpoint-p02-preflight-r4-start.md:19` 均把 20/14/6 三者分开表述。r9 原引用（"4 条 pin"）本身低估，r10 的"6 条"为正确值。 |
| **C-02** 精确路径枚举 | **CLOSED** | r9 五路径集在 `codex-checkpoint-p02-preflight-r4-start.md:17` 逐名列出，经 `git diff --name-only ceffb747..083d2b47` 复核**恰为那 5 条**；r10 七路径集在 `codex-checkpoint-p02-preflight-r4-condition-closure.md:20-26`、`codex-preflight-r4-validation.md:19`、`codex-scratch-build-process-isolation-scope-delta-r1.md:173-179` 三处逐名列出，与提交集合 7/7 一致。 |
| **C-03** `mapping_domain` | **CLOSED** | 12 条根条目与 `codex-scratch-build-preflight-hostfolders-r1.tsv` 12 行按 `path` 全量比对（purpose/domain/expected/exists），**0 处不符**；域分布 = 1 `Scratch RW` + 9 `Smoke RO` + 2 `Build-only RO`。 |
| **C-04** 授权依据锚点 | **CLOSED** | r7 段落 "Authorization basis:" 确实存在（`scope-delta:85`，记 2026-10-10 用户签发持久 `PROJECT_ORCHESTRATION_AUTHORIZATION`），r9 段另行记录"用户续期并明确要求真实隔离证据"（`scope-delta:127`）；P02-task 侧 preflight checkpoint 亦记录同一授权（`codex-checkpoint-p02-preflight-r4-start.md:7`："User authorization: the user renewed PROJECT_ORCHESTRATION_AUTHORIZATION…"）。全仓 `verification/P02` 检索确认授权文本在库内多处版本化可核（另见 `codex-checkpoint-p02-preflight-scope-frozen.md:14`）。 |
| **C-05** admission checklist 前置项 | **CLOSED** | `codex-checkpoint-p02-smoke-admission-r1.md`：非提权交互宿主 shell 与 PID/token 记录（`:22`）、启动前即时 `wsb list --raw` 空且绑定到该次尝试（`:23`）、把启动后返回的 session/environment 身份绑定到可见 Sandbox UI 窗口并同存 session ID/窗口身份/截图哈希（`:28`）；checkpoint 自身仍为 `NOT_ADMITTED`（`:3`）且与本次文档 Review 分离。 |
| **C-06** 共享文档 `UNKNOWN / BLOCKED` 滞后登记 | **CLOSED** | 滞后已显式登记：`scope-delta:160`、`codex-checkpoint-p02-preflight-r4-condition-closure.md:30`、`codex-checkpoint-p02-preflight-r4-start.md:21`、`codex-preflight-r4-validation.md:25`；我实测共享文档此刻确实仍写 `Feature 未查询/UNKNOWN`、`完整 preflight=BLOCKED / INCOMPLETE`（`doc/STATUS.md:3`、`doc/tasks/P02.md:88`），与实测 `InstallState=1` / `PRESTART_STAGE_1_PASS` 的差异属实且被如实披露；更新时点被明确限定为"exact-head Review 通过后、仅当前段"。 |

**结论**：六项条件全部闭合，无遗留 P0/P1/P2/P3。

---

## 4. Findings（严重度 + 精确文件:行）

**P0/P1/P2/P3 = 0/0/0/0**，无阻断项。以下 5 项为**非阻断观察**（建议在下次被授权的文档触及时一并处理，不构成本候选的 Review 条件，也不阻挡 admission 前置文档化）：

| ID | 级别 | 位置 | 描述 | 建议修复 |
|---|---|---|---|---|
| O-1 | 观察（措辞） | `scope-delta:160`；回响于 `codex-checkpoint-p02-preflight-r4-condition-closure.md:15` | 句中将授权依据锚点写为 "the P02 Task's Codex-only preflight checkpoint"。该措辞可指 `codex-checkpoint-p02-preflight-r4-start.md:7`（确实记录授权，成立），但若按字面理解为 `doc/tasks/P02.md` 内 "Codex Scratch Isolation Preflight checkpoint" 段（`:83-89`），该段**并无**授权依据记录（全文检索 `PROJECT_ORCHESTRATION_AUTHORIZATION` 无命中）。 | 改为点名 `codex-checkpoint-p02-preflight-r4-start.md:7` 与 `scope-delta:85/127`；若确实想在 P02 Task 段落登记授权依据，则放在 r9 已授权的"通过后仅改当前段"更新里。 |
| O-2 | 观察（可追溯） | `codex-checkpoint-p02-preflight-r4-condition-closure.md:6`、`scope-delta:158` | 引用"six P3 findings and one note"，但候选未identify/ disposition 该 "note"。经 r9 附件比对，其非 finding 记录为（a）r9 审查侧未能独立复算 root manifest digest、（b）受限 shell 内 CIM/Appx 查询 `NOT_RUN`。 | 本轮我已独立解决（a）（见 §6 digest 复现）；建议在 r9/r10 审查附件入库时把该 note 原文一并列出。 |
| O-3 | 观察（编号映射） | `codex-checkpoint-p02-preflight-r4-condition-closure.md:12-17` | r10 采用新编号 C-01..C-06，未记录与 r9 报告 `P3-01..P3-05` 的对应；r9 附件正文计数为 `P3=5`（其 §二另有一项标注为 P3 的共享文档问题），故两文档并读时会看到 "5 vs 6" 的数字差异。 | 入库 r9 附件时补一行映射（C-01↔P3-02、C-02↔P3-03、C-03↔P3-04、C-04↔P3-01、C-05↔P3-05、C-06↔§二共享文档项）。我本轮已验证该映射**覆盖完整、无遗漏**。 |
| O-4 | 观察（证据入库） | `codex-checkpoint-p02-preflight-r4-condition-closure.md:6` | r9 审查报告目前仅存在于作者 worktree 的**未跟踪**附件，未随候选入库；按 r7/r8 惯例，历轮 `dsh-review-*.response.md` 是入库的。 | 随 r10 审查附件一并入库 r9/r10 review packet。 |
| O-5 | 观察（in-place 修订标记） | `observations-r2.json:3`（`captured_at` 仍为 02:52:29） | 该 JSON 在 r10 被就地修订（仅 `mapping_domain`、`size_match`、新增计数键；`git diff` 证实**无任何实测量值被改动**），但文件内无修订时间/作者标记。披露存在于候选路径清单与 Git 历史。 | 可选：加 `revised_at`/`revision_note`。 |

---

## 5. 已运行检查（含退出码）与 NOT_RUN

**已运行（全部只读）**

| 检查 | 结果 |
|---|---|
| `git rev-parse HEAD / 'HEAD^{tree}' / HEAD^`、`git log -1`、`git worktree list` | EXIT=0；HEAD/tree/base 与声明完全一致 |
| `git status --porcelain=v1 -uall`（审查前/后） | EXIT=0；输出为空（clean，无写入） |
| `git diff --name-status / --stat 083d2b47..92dc7361` | EXIT=0；7 paths（3A+4M），`+152/−21` |
| `git diff --check 083d2b47..92dc7361` | **EXIT=0**（无空白错误） |
| `git diff --cached --check`（index） | **EXIT=0**（index 为空，无暂存内容） |
| `git merge-base --is-ancestor ceffb747… HEAD`、`--is-ancestor 7ce3c40c… HEAD` | 均 **EXIT=0**（r9 base 与固定 source commit 均为祖先） |
| `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | **EXIT=0**；7 项 PASS（196 节点/105 集成祖先/Plan-Task 状态/21 planned 无环/导航链接/governance），打印 `live HEAD=92dc7361…`，`Product tests/build/GUI: NOT_RUN (planning-only)` |
| Python JSON/TSV/XML 一致性复算 | EXIT=0；见 §6 |
| 候选 7 文件 Markdown 本地链接解析 | EXIT=0；7 链接 / 6 本地 / **0 missing**（与 `codex-preflight-r4-validation.md:23` 声明一致） |
| 根 203 项保护 manifest 独立复核（含 digest 复现） | EXIT=0；见 §6 |
| 宿主复测：12 HostFolder roots、20 pins（346,786,966 bytes 全量重算）、`wsb.exe` | EXIT=0；**0 drift** |
| r3 Smoke XML 结构解析（只读） | EXIT=0；11 mappings、**10 RO + 1 RW**、无 `LogonCommand` |
| `Get-WindowsOptionalFeature -Online`（复现提权需求，未提权） | EXIT=1，"请求的操作需要提升"（与 r9 记录一致） |

**NOT_RUN（如实标注，未运行）**

- `Get-CimInstance Win32_OptionalFeature`（本 worktree shell 返回"拒绝访问"，无法独立复现 `InstallState=1`；与 r9 审查侧同一环境限制）→ **NOT_RUN（环境限制，非证据缺陷）**；`Get-AppxPackage` 同样"拒绝访问" → WSB 包身份 NOT_RUN。
- `wsb.exe --version` / `wsb list --raw`（避免触碰 WSB 服务）→ NOT_RUN。
- Sandbox 启动/连接、固定 clone 创建、递归 HostFolder pre-start manifest、reparse 遍历、no-link/object-hardlink 核验、guest 探针、network fail-closed 判别、截图/session 绑定、post-run 保护比对 → **全部 NOT_RUN**（未授权、超出本 Review 范围）。
- Build / runner / Vitest / GUI / WebView / 产品测试 → **NOT_RUN**。

---

## 6. 独立复算的关键数字（本轮为"已实测"，非采信）

- **根 203 项 manifest**：**已独立复算**（r9 审查侧曾因无读权限记 NOT_RUN，本轮具备读权限）。`codex-process-isolation-root-start-manifest.json` 203 条 → live root `G:/CODEX/New Manga` 逐条存在性/kind/size/SHA-256 = **0 mismatch**；root `git status --porcelain -z` 恰 203 条、与 manifest **status 差异 0**、暂存 0、集合无差；候选 7 路径 ∩ root-dirty = **∅**；`entries_sha256` 我用 `sha256(json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(',',':')))` **精确复现为 `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`**，与 `codex-preflight-r4-validation.md:20` 记录一致。
- **r3 Smoke 配置**：canonical（CRLF→LF）= **2609 bytes**、SHA-256 = `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`，与 `observations-r2.json:406-411` 及 `preflight-r2.md:15` 声明一致（raw checkout 2631 bytes）。
- **pins**：20/20 SHA-256 与 14/14 已登记尺寸复测**全部一致**；`wsb.exe` 156160 B / `247e092b…` 一致。
- **候选范围**：7 路径全部为 `verification/P02/**` 文档/JSON，**无产品代码、Schema、IPC、依赖、Task 契约/AC、Owner allowlist、用户数据变更**。

---

## 7. 五个状态的显式分离

1. **process-isolation 方案/设计 Review**：设计线在此前轮次已获通过（R6 follow-up `2394dc98…` 关闭 N-06、新 findings `0/0/0/0`，引证 `scope-delta:129`、`doc/tasks/P02.md:85`）。**本轮不重审、不改变**该结论。
2. **本轮 r10 文档条件闭合 Review**：**`APPROVED`**（P0/P1/P2/P3=0，另有 5 项非阻断观察）。仅覆盖"r9 六项条件是否闭合"的文档/证据层。
3. **Smoke admission**：仍为 **`NOT_ADMITTED`**（`codex-checkpoint-p02-smoke-admission-r1.md:3`）。本候选的 admission checkpoint 与本次文档 Review **保持分离**；本 Review **不构成** admission，也**不授权** `wsb start` 或 clone 创建。
4. **Build Gate / Hard Build Barrier**：Build Gate = **`BLOCKED`**；build = **`NOT_AUTHORIZED / NOT_RUN`**；**Hard Build Barrier 继续有效、未解除**。
5. **产品验收与 AC1–AC7**：**`BLOCKED / NOT_RUN`**，**无任何 AC 通过**；隔离未被证明（`PRESTART_STAGE_1_PASS` 仅是 pre-start 必要条件）。

---

## 8. 是否阻挡"新鲜非提权 preflight 后的 Smoke admission 记录"

**不阻挡。** 六项 r9 条件均已闭合，候选无未处置的 P0/P1/P2/P3，记账数字（路径数、pin 计数、mapping、manifest、config hash）与我独立复算一致；O-1..O-5 均不改变任何 gate 事实。

仍需按既有规则完成（不得跳过）：按 `scope-delta:181` 的授权，在 Review 通过后**仅更新当前段**记录实测状态；重新执行**当前非提权 stage-1 preflight**（易变量重测、root HEAD/manifest 复核、pins/r3 hash 复核）；随后由 Codex **另立**独立 checkpoint 记录 `Smoke admission=ADMITTED`；admission 之后才可创建固定 clone，且在 `wsb start` 前完成 `codex-checkpoint-p02-smoke-admission-r1.md:18-24` 的全部前置项。

---

## 9. 推荐下一步（可直接转发）

> **Owner/Integrator=Codex**：r10 条件闭合候选 `92dc7361`（tree `73511f7b`）已获 DeepSeek Harness 非作者 exact-head **`APPROVED`**（P0/P1/P2/P3=0，另有 5 项非阻塞观察 O-1..O-5）。请仅在 r9 既有授权内操作：(1) 把 r9 与 r10 的 review packet 附件入库，并顺带处理 O-1（点名 `codex-checkpoint-p02-preflight-r4-start.md:7`）/O-2/O-3（补 note 原文与 C-xx↔P3-xx 映射）、O-4/O-5（可选）；(2) 按 `scope-delta:181` 仅更新 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md` 的当前段，记录实测状态与本 Review 结论，保留历史段；名称修订后重跑路线校验器、Markdown 链接与 `git diff --check`；(3) 在**非提权交互宿主 shell** 中重测易变量并复核 root manifest/pins/r3 hash，全部通过后**另立** checkpoint 记录 `Smoke admission=ADMITTED`。在 admission 之前不得创建 clone、不得 `wsb start`；Build Gate 保持 `BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 不解除。若任一检查失败或未知，停止并保留证据。
