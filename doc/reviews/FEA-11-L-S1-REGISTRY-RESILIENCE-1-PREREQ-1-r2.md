---
task: FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
title: Review r2（窄面）：C-15 v1.5 UNFREEZE —— P1-A/P1-B 关闭复核与最终字节判定
reviewer: fresh subagent（独立上下文；未参与起草、未参与 r1 复核、未参与实现；只读）
session: ccdae3ad-6ff7-4236-b59c-0b46b7ef9043
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 821b309a0f6145ba085af2581541ee946cd5f949
reviewed_worktree: dirty（UNFREEZE 待提交字节；快照 2026-11-07T07:42:35–07:52 +08:00）
verdict: approved
---

# Review r2（窄面）：C-15 v1.5 UNFREEZE

> 审查对象（UNFREEZE 面）：`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md`、`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/**`。
> 门禁证据（只读）：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`；背景只读：`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r1.md`、`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`（A 卡，仅供归属/一致性核对）、`SourceAccessRegistry.cs` 等调用面。
> 口径：事实以工作树最终字节为准（快照见 §1）；未运行项一律 `NOT_RUN`；并发未完成状态不作为被审字节。

## 0. 结论先行

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 15（全部非阻断）。**

- **P1-A 已关闭**：矩阵 C-15 行（`FEA-CONTRACT_FREEZE_MATRIX.md:36`）已从 `FROZEN v1.1` 改为 **`FROZEN v1.5` 2026-11-07**，条件列改为「①v1.5 独立 byte-level 复核 ②C-16/C-17 零改动 ③18/18 ④PASS」，与同文件 `:3`、C-15 `:3`、FROZEN-C15 §1/§2⑤/§7 自洽。
- **P1-B 已关闭**：`task_ledger.py --write` 后的台账与 `doc/tasks` 实际一致（529 task 文件 = 530 个 `.md` − `README.md`；非终态 11），`check.ps1` **默认 + `-TaskPath` 均 PASS（3 warnings）exit 0**；PLAN READY/DAG 已登记 PREREQ-1/A/L-S4-A（`REBASELINE_PLAN.md:49,53`），STATUS 当前任务同步（`STATUS.md:7`）。
- **C-15 v1.5 条款字节未变**（sha256 仍为 `f9e376a0ed4ce2aaf87c5c698798b0f7a802a3b87a0de9845bc96c3f9bfff4d6`，`git hash-object` `b0360cc9…`）→ 本轮只需复核记录/门禁/证据；**pin 不需要重算**。安全语义逐条复核**无放宽**：文件级损坏仍整库 fail-closed、`SOURCE_REGISTRY_UNAVAILABLE`、`.corrupt-*` 复制、不建空文件/不覆盖；根级不可用保持 `List` 可用、其余根不受影响、`Authorize` 逐请求核验、该请求 typed 拒绝且零写、缺失根 ≠ 无授权、不自动重建/重授权/恢复；撤销与恢复未放宽；错误码闭集零新增。
- **pin 与证据**：`verify_pins` **18/18 PASS**（exit 0）；其余 17 pins 与 HEAD 记录逐项相同（抽查 C05/C06/C16/C17 四项 hash 全等，且 `git diff HEAD` 对 17 契约为空）；EV **7/7 文件 sha256 MATCH**；`pre-post.sha256` pre = HEAD v1.1 blob 字节 `d8c0a3bc…`、post = v1.5 `f9e376a0…`；`changed-lines.diff` 与实际 `git diff` **归一化后逐字符相等**（4910 字符）。
- **零字节边界**：`git diff --name-only HEAD -- doc/plan` 只含 C-15/FROZEN-C15/矩阵；C-16（blob `b9be0ac…`）/C-17（blob `f767e15…`）与 HEAD 同 blob；`src/apps/tests/tools` 零 diff；`verify_pins.ps1` 零改动；`CORE_PROTOCOL_MINOR=3` 不变。
- **剩余 15 条 P3 全部为记录/引用/措辞级**（见 §5），不阻断冻结；其中唯一「事实性错误」是载体 §6② 的台账计数（533/13，实测 529/11），不影响门禁与字节。

## 1. 只读基线（实测）

| 项 | 命令 | 结果 |
|---|---|---|
| 分支 / HEAD | `git rev-parse --abbrev-ref HEAD` / `git rev-parse HEAD` | `main` / `821b309a0f6145ba085af2581541ee946cd5f949` |
| 工作树 | `git status --porcelain=v1 -uall`（07:46） | `M`：C-15、FROZEN-C15、矩阵、PREREQ 卡、**A 卡**、**L-S4 A 卡**、STATUS/PLAN/TASK_LEDGER；`??`：载体、r1 报告、**L-S4 scope-r1**、证据目录 8 文件 |
| C-15 实测 sha256 | `Get-FileHash -Algorithm SHA256` | `F9E376A0ED4CE2AAF87C5C698798B0F7A802A3B87A0DE9845BC96C3F9BFFF4D6` |
| C-15 `git hash-object` | `git hash-object` | `b0360cc975d361c3f1431b4c7e644bc1735981ab` |
| HEAD 原 v1.1 blob | `git rev-parse HEAD:doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `a0286bac06aa89587a6a7cbcf08461aae8add865`（`git cat-file` 后 sha256 `d8c0a3bc…`） |
| v1.5 blob 内容 sha256 | `git cat-file blob b0360cc9…` | `f9e376a0…`（三口径一致：工作树/blob/冻结记录） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，exit 0；C15 `f9e376a0ed4c` |
| 治理检查（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，exit 0；`Task: doc\tasks\FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` |
| 治理检查（本卡） | `... -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | **PASS (3 warnings)**，exit 0 |
| 台账（只读运行） | `python tools/governance/task_ledger.py` | 529 task files / 非终态 11 / 17 无关契约不变口径；与 `TASK_LEDGER.md` 一致 |
| 契约 diff 面 | `git diff --name-only HEAD -- doc/plan` | 仅 C-15 / FROZEN-C15 / 矩阵 3 文件 |
| 代码面 | `git diff --name-only HEAD -- src apps tests tools` | **0 文件** |

**并发说明**：工作树含 Lead 侧 A 卡（`FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`，mtime 07:29:48）与并行 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 的卡面/队列准备改动及 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md`。三者**不在本复审范围**；本报告只在「归属是否登记」这一项使用 A 卡（§2.C），未审查其字节、未据其判定任何结论。

## 2. A–G 逐项

### A. P1-A 关闭：矩阵 C-15 行 — **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| 矩阵 C-15 行版本/日期 | `FROZEN v1.5`、2026-11-07 | `FEA-CONTRACT_FREEZE_MATRIX.md:36` |
| 与状态行一致 | 矩阵 `:3` 已写 `C-15 v1.5`（2026-11-07） | `:3` |
| 与 C-15 状态行一致 | `FROZEN v1.5（2026-11-07 重冻；v1.0 2026-11-03、v1.1 2026-11-04 历史）` + 载体/冻结记录链接 | `FEA-C15_SOURCE_STORAGE_DRAFT.md:3-4` |
| 与 FROZEN §1 一致 | 版本 v1.5、sha256 `f9e376a0…`、blob `b0360cc9…`、blob 内容 sha256 `f9e376a0…` | `FEA-CONTRACT-FROZEN-C15.md:15-18` |
| 与 FROZEN §7 一致 | v1.5 重冻段、历史 pin v1.1/v1.0 保留、独立复核 pending、17 pins 不变 | `:75-85` |
| 条件列 | 「①v1.5 独立 byte-level 复核（载体）②C-16/C-17 零改动 ③18/18 ④PASS」；条件①未预填 approved（与 r2 pending 相符） | `:36` |
| 载体 §2 D 落地 | 「C-15 行 → `FROZEN v1.5`（2026-11-07）」已实现 | 载体 `CONTRACT-UNFREEZE-2026-11-07-C15.md:30`、`:54①` |

**A = PASS**。r1 P1-A 关闭。

### B. P1-B 关闭：check / 台账 / DAG — **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| `check.ps1`（默认） | **PASS (3 warnings)**，exit 0；warnings 仅为「11 个非终态」「STATUS 80% 预算」「PLAN 80% 预算」 | 实跑输出；`verification/.../logs/check.log` 逐行相同 |
| `check.ps1 -TaskPath`（本卡） | **PASS (3 warnings)**，exit 0 | 实跑输出；`logs/check-taskpath.log` 逐行相同 |
| 台账重建 | `TASK_LEDGER.md`：task files 529 / terminal 517 / non-terminal 11 / named-in-plan 4 / outside 7；生成脚本口径（排除 `README.md`） | `TASK_LEDGER.md:9-16`；`task_ledger.py` `collect()` 跳过 `readme`，`non_terminal` 排除 `(none)`（与 `check.ps1` 对齐） |
| 台账与 `doc/tasks` 实际一致 | 磁盘 530 个 `.md`，其中 `README.md` 为索引 → 529 task 文件；`git ls-files` 同为 530 → 无 untracked 草稿 | 实测：`glob` 530 / `git ls-files` 530 / 差集为空 |
| 非终态计数一致 | 台账 11 = check 警告 11；清单 11 行（`ready` 4 / `in_progress` 2 / `in_review` 2 / `approved` 1 / `blocked` 1 / `proposed` 1） | `TASK_LEDGER.md:37-49` |
| PLAN READY 登记 | `READY 节点：FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1、FEA-11-L-S1-REGISTRY-RESILIENCE-1、FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` | `REBASELINE_PLAN.md:49` |
| PLAN DAG 登记 | 「…→ L-S1-PREREQ-1（ready）/ L-S1-A（ready）/ L-S4-A（ready）」 | `:53` |
| STATUS 同步 | 当前 Task = A `ready`（依赖 PREREQ-1），并行 PREREQ-1 与 L-S4 `ready` | `STATUS.md:7` |

**B = PASS**。r1 P1-B 关闭；修复所需治理文件改动属 Lead 身份更新，与卡面登记自洽。

> 附注（不影响判定）：台账 `By status` 中 `(none)` 1 行（`UIUX-FUSION-IMPL-1.md` 无 `status` 字段）按脚本注释被排除在「non-terminal」指标外，故按状态拆分合计 529 ≠ 517+11；这是既有脚本口径（与 `check.ps1` 对齐），非本轮回归。

### C. P2/P3 处置 — **PASS（无 P2 残留；P3 见 §5）**

| r1 finding | 级别 | 处置（本次实测） | 结论 |
|---|---|---|---|
| **P2-1** A 卡工作树额外改动 | P2 | 载体 §6③ 明写「A 卡工作树改动属 Lead 释放编辑（单独提交）」；A 卡 `status: ready`、`depends_on: PREREQ-1` 已登记进 PLAN READY/DAG、STATUS、台账（`mentioned`），不再是无归属漂移 | **CLOSED**（残余：提交隔离 `NOT_RUN`，见 §5 R-06） |
| **P2-2** 证据不可复现 / EV 缺失 | P2 | `EV.md` 已补（7 文件逐文件 sha256，**7/7 MATCH**）；`check.log`/`check-taskpath.log` 与本次重跑**逐行相同**；`pins.log` 与重跑相同 | **CLOSED**（残余：无命令/时间/HEAD/exit → R-01） |
| **P2-3** 跨契约错误码语义漂移 | P2 | 载体 §6④ 显式登记为 limitation（引用 C-16/C-06 码义不自洽、词表细化另案、不改本批字节）；A 卡 limitation 第 3 条同步登记；C-15 字节未改 | **CLOSED（accepted limitation）**（引用行号小偏差 → R-02） |
| **P2-4** 派生状态未明示 | P2 | 载体 §6⑤ 明写「派生状态…为 A 卡实现细节，契约不新增字段（不改变 C-15 字节）」；C-15 §5 JSON schema/`format_version=1` 未改；A 卡 AC-L5 约束「无 wire/schema/C-16/C-17 变化」 | **CLOSED**（A 卡 In.2 未字面写「派生/不持久化」→ R-03） |
| **P2-5** AC-T4 字面缺失 | P2 | 载体 §6⑥ 已含字面串「契约就绪 ≠ 实现/产品可用」；载体 §3/§4 仍为将来时与「A 卡不释放」表述，FROZEN §3「不构成」、C-15 §8「不构成」保留，未见「已实现/可用」宣称 | **CLOSED（字面）**（位于处置句内、缺独立边界声明 → R-04） |
| **P3-F08…F16** | P3 | 逐条见 §4；其中 F-11 的 EV 部分已修，其余未修/未显式接受 | **9 条 OPEN（非阻断）** |

**C = PASS**。P2 全部有显式处置（修 / 接受为 limitation），未见静默丢弃。

### D. 最终字节安全语义复核 — **PASS（无放宽）**

> C-15 字节与 r1 复核字节**完全相同**（sha256 `f9e376a0…` 不变），下列判定系对**工作树最终字节**重新逐条核对（非沿用 r1 结论）。

| # | 安全断言 | 判定 | 最终字节证据 |
|---|---|---|---|
| D-1 | 文件级损坏（magic/version/长度/DPAPI/JSON 任一不合法）→ 整库 fail-closed、所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`、`.corrupt-<utc>` **复制不移动**、不创建空文件、不覆盖 | **PASS** | `FEA-C15_SOURCE_STORAGE_DRAFT.md:312`；`:311`「文件缺失 = 合法空 Registry」未变；`:316-318` ACL/加密/备份/日志未变 |
| D-2 | 根级不可用（根不存在/不可读/identity 与登记不符）不再判文件损坏；registry 仍合法可读；`List` 可用；其余根不受影响；`Authorize` **逐请求**对请求路径所属根重核验 identity；不可用/不匹配 → 该请求 typed 拒绝、**零写** | **PASS** | `:313`；生产调用面 `SourceReadCoordinator.cs:400/403/467`、`HostOperationOrchestrator.cs:132/296` 均经 `Authorize` 铸造型授权；`List()` = `Load().Entries`（`SourceAccessRegistry.cs:54`），A 卡 In.2 要求 List 可用 |
| D-3 | 缺失根 ≠ 无授权；不得自动重建 identity、不得自动重授权/自动恢复；不得因根缺失静默重建 | **PASS** | `:313`「缺失根永不等于『无授权』」「不得自动重建 identity、不得自动重授权/自动恢复」；`:314`「不得自动、不得因根缺失而静默重建」 |
| D-4 | 恢复语义不变：文件级损坏仍仅 `source_reset_registry {confirm:true}`（显式用户操作，移入 `quarantine/` 后建新空 registry）；根级恢复由显式用户操作完成 | **PASS** | `:314`；diff 中该行为「-旧行/+新行」改写，旧「用户显式操作」保留并新增「根级不得自动」= 收紧 |
| D-5 | 撤销语义不变：generation+1、持久化 `revoked_at`、`RevokeSourceReadGrant`（C-16）+ Core ACK、ACK 失败仍持久化撤销 | **PASS** | `:315` 在 diff 中为**上下文行**（未改动），与 v1.1 同字节；C-16 字节零改 |
| D-6 | 错误码闭集零新增（复用既有 `SOURCE_REGISTRY_UNAVAILABLE`）；无路径回退/部分读取/静默自动恢复 | **PASS** | `:313` 明写「零新错误码」；C-16 错误码表（`:177`）字节未变；C-15 无新增码字符串；四项语义未见放宽 |

**D = PASS**。拆分是**可用性放宽**，不是授权放宽：不可用根仍被 `Authorize` 拒绝，且缺失根不被视为「无授权」，无自动重授权/自动恢复；文件级损坏仍整库 fail-closed。

### E. pin 与证据 — **PASS**

| 项 | 期望（记录） | 实测 | 结论 |
|---|---|---|---|
| C-15 v1.5 sha256 | `f9e376a0ed4ce2aaf87c5c698798b0f7a802a3b87a0de9845bc96c3f9bfff4d6`（FROZEN §1） | 同值 | **MATCH** |
| `git hash-object` | `b0360cc975d361c3f1431b4c7e644bc1735981ab`（FROZEN §1） | 同值 | **MATCH** |
| blob 内容 sha256（LF） | `f9e376a0…`（FROZEN §1） | `git cat-file blob b0360cc9…` → `f9e376a0…` | **MATCH**（三口径一致） |
| pre = HEAD v1.1 | `d8c0a3bc…`（`pre-post.sha256:1`） | `git cat-file blob a0286bac0…` → `d8c0a3bc…` | **MATCH** |
| post = v1.5 | `f9e376a0…`（`pre-post.sha256:2`） | 同值 | **MATCH** |
| `verify_pins` | 18/18 | **PASS (all 18)**，exit 0 | **PASS** |
| 其余 17 pins 不变 | 与 HEAD 记录逐项相同 | `verify_pins` 全 OK；`other-17-pins.txt` 17 行 `UNCHANGED` + `changed=0`；抽查 C05 `f6e6f3cb…`、C06 `99831a20…`、C16 `ad25fb3c…`、C17 `aefa0fa5…` 均与各自冻结记录的 pin 一致 | **PASS** |
| `changed-lines.diff` | 与工作树实际 diff 一致 | 归一化（CRLF→LF + 去尾换行）后 **逐字符相等**（4910 字符），含全部 4 个 hunk（头部状态/日期、§5 两行拆分、§9 条件⑤、变更记录 v1.5） | **PASS** |
| `verify_pins.ps1` 口径 | 不改 | `git diff HEAD` 为空；pin 取自各 FROZEN 记录 §1 的 `sha256` 行（脚本 `Select-String` 逻辑） | **PASS** |
| EV 逐文件 sha256 | 7 文件 | **7/7 MATCH**（carrier/`changed-lines`/3 logs/`other-17-pins`/`pre-post`） | **PASS** |

**E = PASS**。

### F. 冻结包一致性 / 不夸大 — **PASS（残留 P3）**

| 检查 | 结果 | 证据 |
|---|---|---|
| FROZEN 版本/历史 pin | v1.5 + v1.0 `6da686…` / v1.1 `d8c0a3bc…` 保留 | `FEA-CONTRACT-FROZEN-C15.md:4,15-18,71,84` |
| §1A pin 口径 | 三口径定义保留未改 | `:22-26` |
| §1B 复核字节 | v1.5 复核字节 = `f9e376a0…` = 冻结字节；断言与实测相符 | `:36` |
| §2 条件行 5 | `⏳`（未预填 ✅） | `:46` |
| §7 v1.5 段 | 载体/触发授权/修订内容/独立复核 pending/冻结字节/历史 pin/17 pins 自洽 | `:75-85` |
| 载体 §6 = r1 处置 + r2 pending | r1 结论（changes_requested P0=0/P1=2/P2=5/P3=9）与六项处置、C-15 字节未变、进入 r2 | 载体 `:53-55`；`EV.md:3`「r1 changes_requested → r2 pending」 |
| 无预填 approved | 矩阵条件①、FROZEN §2⑤ `⏳`、§7 `pending`、载体 §6 均无 v1.5 approved 字样（仅 v1.0/v1.1 历史 approved） | 全文 grep |
| 不夸大（契约 ≠ 实现） | 载体 §3 用「新实现…（受 A 卡控制）」将来时、§4「A 卡不释放」；FROZEN §3「不构成：实现授权、DB 迁移已执行、产品 AC 已达成」；C-15 §8「不构成实现授权…不证明任何 AC 已达成」；PREREQ 卡「只起草 + 复核 + 重冻；不实现」 | 载体 `:35-38,43`；FROZEN `:52`；C-15 `:343`；PREREQ 卡 `:38` |

**F = PASS**。残留：FROZEN §1B/§7 的「r1 复核 pending」未随 r1 完成刷新（F-08/R-05）；载体 §6⑥ 措辞位置（R-04）。均不构成预填批准或能力夸大。

### G. C-16/C-17/其余契约零字节 — **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| `doc/plan` diff 面 | 仅 3 文件：C-15、FROZEN-C15、矩阵 | `git diff --name-only HEAD -- doc/plan` |
| C-16 字节 | blob `b9be0acfa232154510d8453133ef8803b6b8fbbe` = HEAD | `git rev-parse HEAD:…` = `git hash-object …`；pin `ad25fb3c89bb…` OK |
| C-17 字节 | blob `f767e158a43652ea092066081e53fa0810e395fb` = HEAD | 同上；pin `aefa0fa5b17e…` OK |
| 其余 17 契约 | 逐字节不变 | `git diff HEAD` 对 17 契约为空；`other-17-pins.txt` `changed=0` |
| wire/命令集/能力/TTL/schema/依赖 | 零改动 | 无 `src/apps/tests/tools` diff；C-16 TTL/§6 闭集未变；C-15 §5 JSON schema 未变；`CORE_PROTOCOL_MINOR = 3`（`src/bootstrap/core_service.py:320`） |

**G = PASS**。

## 3. r1 findings 逐条处置

| r1 ID | 级别 | 处置 | 说明 |
|---|---|---|---|
| F-01 | P1 | **CLOSED** | 矩阵 `:36` 已改 `FROZEN v1.5` 2026-11-07 + 18/18 + PASS；与 `:3`/C-15 `:3`/FROZEN §1/§7 一致 |
| F-02 | P1 | **CLOSED** | 台账 529/11 与 `doc/tasks` 一致；PLAN READY/DAG + STATUS 登记；`check` 默认与 `-TaskPath` 均 PASS exit 0 |
| F-03 | P2 | **CLOSED** | 归属已登记（载体 §6③ + PLAN/STATUS/台账）；提交隔离属 `NOT_RUN`（见 §4-R-06） |
| F-04 | P2 | **CLOSED（残余 R-01）** | EV 已补且 7/7 一致；两个 check 日志与重跑逐行相同；pins.log 相同；仍无命令行/时间戳/HEAD/exit |
| F-05 | P2 | **CLOSED（accepted limitation；残余 R-02）** | 载体 §6④ 显式登记 limitation + 另案；引用 C-16 行号 `:174` 应为 `:177` |
| F-06 | P2 | **CLOSED（残余 R-03）** | 载体 §6⑤「契约不新增字段」+ AC-L5「无 wire/schema 变化」；A 卡 In.2 未字面写「派生态/不持久化」 |
| F-07 | P2 | **CLOSED（字面；残余 R-04）** | 载体 §6⑥ 含字面串；建议补一句独立边界声明 |
| F-08 | P3 | **OPEN** | FROZEN §1B `:36`「r1 复核 pending」、§7 `:82`「pending（r1…）」未随 r1 完成刷新（未预填 approved，故非 P1/P2） |
| F-09 | P3 | **OPEN** | PREREQ 卡 I-2 `:68` 仍写「§10 冻结条件」，C-15 实际为 **§9**（`:347`） |
| F-10 | P3 | **OPEN（pre-existing）** | FROZEN 头部 `:6` 授权/r7 approved 仅覆盖 v1.0/v1.1；§3 `:50` 仍写 C-05 v1.1/C-06 v1.1（现状 v1.2） |
| F-11 | P3 | **PARTIAL** | `EV.md` 已补（引用闭合）；`carrier.md` 副本与源文件**逐字节相同**，副本内 `../plan/…`/`../reviews/…` 相对链接从 verification 目录仍不可解析，未注明「副本，链接以源文件为准」 |
| F-12 | P3 | **OPEN** | C-15 `:312` 文件级枚举仍为 magic/version/长度/DPAPI/JSON，未含「条目结构」；A 卡 In.1 明确把条目结构留在文件级 → 实现取严方向（不构成授权放宽） |
| F-13 | P3 | **OPEN** | C-15 `:313` 未显式写「条目保留/不删除/不静默丢弃」（A 卡 In.2 有） |
| F-14 | P3 | **OPEN** | C-15 `:314` 未明写 `source_reset_registry` 不得用于根级恢复 |
| F-15 | P3 | **OPEN** | C-15 `:313` 未规定 `Authorize` 的 revoked/generation 与 identity 检查顺序 |
| F-16 | P3 | **OPEN（pre-existing）** | `core.autocrlf=true`、根 `.gitattributes` 未给契约 `eol=lf`；C-15 当前 `i/lf w/lf`、C-16 `i/lf w/lf`、矩阵 `i/lf w/crlf`；跨 checkout 工作树若写 CRLF 会使 `Get-FileHash` 口径偏离 |

## 4. 新 findings（全部 P3、非阻断）

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **N-01** | P3 | 载体 `CONTRACT-UNFREEZE-2026-11-07-C15.md:54②` | 「台账重建（**533 Task/13 非终态**）」与实测不符：台账 = 529 task 文件（530 `.md` − `README.md`）、非终态 **11**（check 亦报 11；HEAD 为 528/10）。重建本身已完成且一致，仅该计数陈述错误 | 改为「529 Task/11 非终态（`README.md` 除外）」或直接引 `TASK_LEDGER.md:9-16` |
| R-01 | P3 | `logs/*.log` | 3 个日志仍无命令行/时间戳/HEAD/exit code，独立复现需靠本报告重跑 | 在日志首行加 `# cmd/head/time/exit` 元数据 |
| R-02 | P3 | 载体 `:54④` | 引用「C-16 `:174`」，实际码行在 `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:177`（`:174` 是表头行） | 改为 `:177` |
| R-03 | P3 | C-15 `:313`；A 卡 In.2 `:48` | 「当前不可用」状态未字面写「派生/不持久化」；合同侧已由「契约不新增字段」+ AC-L5 兜住，但 A 卡 In.2 未同步该定语 | 在 A 卡 In.2 或 AC-L5 加「该状态为派生态、不持久化、不新增 wire 字段」 |
| R-04 | P3 | 载体 `:54⑥` | AC-T4 所需字面串位于「处置」句内（自指「措辞已补」），载体正文 §1–§5 无独立边界声明（对比 2B 先例：§5 括注被接受为非阻断） | 在 §3 或 §5 增一句「本载体仅冻结契约字节，不构成实现授权/产品可用证据；A/B 实现另卡」 |
| R-05 | P3 | 矩阵 `:36-37` | C-15 行依赖列仍 `C-05 v1.1/C-06 v1.1`（C-06 现为 v1.2）；C-16 行依赖列仍 `C-15 v1.1`。均为历史依赖记录，非字节冲突 | 标注 `historical` 或同步版本号（pre-existing 口径） |
| R-06 | **NOT_RUN** | 提交面 | UNFREEZE 提交隔离（只 stage C-15/FROZEN/矩阵/载体/PREREQ 卡/证据/报告，排除 A 卡与 L-S4 A 卡）尚未发生，无法核验；`git status` 当前两类卡仍在工作树 | 提交时按显式 pathspec stage，提交后用 `git show --stat` 复核 |
| R-07 | P3 | FROZEN §7 `:75-85` | 载体 §6④ 的码义 limitation 未在冻结记录 §7 留一行（只在载体 + A 卡） | 如需读者从冻结记录即见，可加「limitation：码义收窄另案」一行 |

> 计数说明：P3 合计 **15** = r1 原 P3 的 F-08…F-16 共 9 条 + 残余 R-01…R-05 共 5 条 + 新增 N-01 1 条。R-06 是尚未执行的提交动作（`NOT_RUN`），不计数；R-07 与 F-08/R-05 同族，只在 §4 列出、不重复计数。

## 5. 最终 verdict 与放行建议

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 15（非阻断）。**

- **P0 = 0**：未发现数据损坏、授权放宽、fail-open、静默自动恢复、冻结字节污染。
- **P1 = 0**：r1 的两条 P1（矩阵行、check 门禁）均已关闭并实测复现。
- **P2 = 0**：r1 的五条 P2 均有显式处置（修 / accepted limitation），残余项降级为 P3。
- **P3 = 15**：记录/引用/措辞级（§2.F、§4），按本冻结包「approved（可含非阻断 P3）」标准不阻断。

**放行与收口建议（按序）**：

1. 在载体 §6 追加 r2 结论（`approved` P0/P1/P2=0/P3=15）并记录 **r2 session `ccdae3ad-6ff7-4236-b59c-0b46b7ef9043` + reviewed_head `821b309a0`**（AC-T2 要求 session/reviewed_head 入载体），随后 FROZEN §2⑤ 由 `⏳` 改 `✅`、§7「独立复核」行改 approved、矩阵条件①补 `approved`。
2. **C-15 字节不变 → pin 不需重算**（`f9e376a0…` 仍有效）。
3. UNFREEZE 提交按**显式 pathspec** 只含：`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、C-15、FROZEN-C15、矩阵、PREREQ 卡、`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/**`、r1/r2 报告；**排除** A 卡与 L-S4 A 卡（R-06）。提交后用 `git show --stat` 与 `verify_pins`/`check` 再复核一次。
4. 可选（不阻断）同批处置：N-01 计数、R-02 行号、F-09 `§10`→`§9`、F-11 副本链接注明、F-08 FROZEN 复核状态行。

**关于 C-15 字节**：任何对 C-15 文字的进一步修改（F-12…F-15 等）都会改变 pin，须重走 UNFREEZE + 独立复核；本轮不要求。

## 6. 真实性声明

- 本报告作者为**独立上下文 fresh subagent**（session `ccdae3ad-6ff7-4236-b59c-0b46b7ef9043`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`），未参与本 UNFREEZE 的起草、未参与 r1 复核、未参与任何实现；**本报告是本次复核唯一写入的文件**。
- 未修改 `doc/plan/**`、`doc/tasks/**`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`verification/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 的任何字节；未执行 `git add`/`commit`/`push`；未运行 `task_ledger.py --write`（仅只读摘要运行）。
- 事实以 `2026-11-07 07:42–07:52 +08:00` 的工作树最终字节为准；`reviewed_head = 821b309a0f6145ba085af2581541ee946cd5f949`；工作树 dirty（UNFREEZE 待提交字节 + Lead 侧并行卡面），差异面已在 §1 完整记录。
- **已运行**：`git rev-parse/status/diff/diff --stat/hash-object/cat-file/ls-files --eol`、`Get-FileHash`、`verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、`task_ledger.py`（只读）、Python/`.NET` 静态文件集比对、`Select-String`/`Get-Content`、EV 逐文件哈希比对。
- **未运行（`NOT_RUN`）**：pytest / .NET 构建与测试（本卡零代码）、真机 IPC、DPAPI 原生往返、A 卡实现与其测试（未实施）、B 卡恢复流程（不存在）、UNFREEZE 提交隔离（尚未提交）、干净 checkout 的 EOL 行为（F-16 为推断）。以上均不作为本报告结论依据。
