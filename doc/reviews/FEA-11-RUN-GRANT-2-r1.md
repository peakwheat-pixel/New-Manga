---
task: FEA-11-RUN-GRANT-2
title: FEA-11-RUN-GRANT-2 独立实现 Review r1（2B：容器成员 entry 授权通道；C-16 v1.4 §2）
reviewer: fresh subagent（独立上下文；未参与实现/返修；只读）
session: fresh subagent（Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立实现 Review（fresh context / read-only / 非作者 / 非返修者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 0180089894b2286d8ff6a94289b84dd318871d18
reviewed_evidence_head: 8e1883655e2df90b6f5b8cdee256200f1511af5c
verdict: approved
---

# FEA-11-RUN-GRANT-2（2B）独立实现 Review r1

> **结论先行：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 4（均为口径、证据措辞与建议级，无门禁影响）。**
>
> 被审实现按 **C-16 v1.4 §2** 落地：Core 注册期接受 `zip`/`cbz`/`pdf` 的 1..N 容器成员条目并逐项校验
> （locator 安全、`ordinal ≥ 0` 且唯一、同一容器 `path`、四项 facts 同一），任一不符 **整 grant typed
> `SOURCE_ACCESS_DENIED`、零部分接受**；条目数超 `budget.max_entries` 或实现硬上限 10,000 → **`SOURCE_BUDGET_EXCEEDED`、不截断**
> （`source_read_refs.py:59,185-186,928-931,1022-1058`）。匹配期保持冻结的 `entry_key OR locator OR ordinal` +
> **容器 facts vs `source_locations`**、无路径回退（`:596-657`），`find_bound_for_source`/`commit_guard` 零改动。
> Host 只把 2A `SourceIdentityCache` 中的 **Core 权威** locator/ordinal 原样传入（`HostRuntime.cs:1796-1805`），
> 容器文件**每 grant 只指纹一次**（`SourceReadCoordinator.cs:238-275,405-420`），超 `max_entries` **typed 不截断**（`:368-378`）。
> **我独立实跑**：定向 pytest **74 passed**、Host 单测 **32 passed**、真实 IPC **5 passed**、全量 pytest **3305/10**、
> 全量 .NET **1562/0/91**（FEA-09 tracked 字节被重写后已按原字节恢复并 sha 复核）、pins **18/18**（C16 `ad25fb3c…`）、
> `check.ps1`（默认 + `-TaskPath`）**PASS(3w)**、API inventory **EXIT=0**、EV 逐文件 sha256 **15/15**；
> 并自选 **2 个破坏点**（Host 重编号 ordinal；Core image 单 entry 守卫）→ 目标用例 **RED**，随后 **逐字节恢复 + sha 复核**。
>
> **不夸大**：本卡只闭环「缓存可用的容器源」上的容器成员 entry 授权通道（L-G12② 的该面）；L-G16（>4096 成员不入缓存）、
> L-G1、L-G2、L-G9、L-G10 均**未解决**，**L-R1 未全修**；卡/Handoff/EV 未出现「referenced Run 全场景可用」式表述。

---

## 0. 基线与身份（全部实测）

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| `git rev-parse HEAD` | `8e1883655e2df90b6f5b8cdee256200f1511af5c`（docs 证据披露修正，最新） | 实测 |
| 交付 head（被审实现/测试） | `0180089894b2286d8ff6a94289b84dd318871d18`（实现 `7466cb99d` + 测试 `018008989`） | `git rev-parse` |
| 工作树 | **clean**（`git status --porcelain` 空，评审开始与结束各一次） | 实测 |
| 交付 head → 当前 HEAD 差异 | 17 个文件，**全部**为 `doc/tasks/FEA-11-RUN-GRANT-2.md`、`doc/handoffs/FEA-11-RUN-GRANT-2-018008989.md`、`verification/FEA-11-RUN-GRANT-2/**`（EV/Manifest/changed-files/8 logs/4 tools） | `git diff --name-status 018008989 8e1883655` |
| 本卡自有 commit 集 | `7466cb99d`、`018008989`；两者并集 = **7 文件**（与 `changed-files.txt` 逐行一致） | `git show --name-status --format=''` |
| 共享工作树起点/父链 | 起点 `5397be149`；首个交付 commit 父 = `61b7eb249`；区间另含 Lead 侧 docs commit `45fdabee6`/`61b7eb249`（前者仅 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`，后者仅 2A 卡/EV/Manifest） | `git log --format='%h %p %s'`、`git show --name-status` |
| Reviewer 身份 | 父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a` 派发的**独立上下文 fresh subagent**；未参与本卡实现/返修，也未参与 RUN-GRANT-1/2A 实现 | 本会话事实 |

> 事实优先级：以 `018008989` 的实现/测试字节 + `8e1883655` 的卡/Handoff/证据字节为准；Handoff/EV 自述仅在标注「文档声称」时引用。
> 本评论的「实测」= 本会话亲自执行；「复算」= 用独立命令重算并比对。

---

## 1. A — 契约一致性（C-16 v1.4 §2）：**PASS**

| # | 契约要求（v1.4 §2） | 实现（`018008989`） | 判定 |
|---|---|---|---|
| A-1 | 容器（`zip/cbz/pdf`）`entries[]` **1..N**；`image` 保持单 entry、`folder` 逐成员 | `_parse_scope`：`image and len(parsed)!=1` → `SOURCE_ACCESS_DENIED`（`source_read_refs.py:1030-1033`）；`folder` 分支保持逐成员路径/大小（`:984-1021`）；容器分支对 1..N 循环校验（`:1034-1058`） | PASS |
| A-2 | 每项 `path` = **同一容器**绝对路径 | `container_norm` 归一后逐项比对（`:1049-1052`）；绝对性由 `Path(path).is_absolute()` + `.`/`..` 段拒绝（`:960-965`）；重复路径只 `stat`/指纹一次（`:966-983`） | PASS |
| A-3 | `locator` 安全（不得 `.`/`..`/绝对） | 容器分支逐项 `validate_locator`（`:1037-1043`）；该函数拒绝绝对、盘符、UNC、`.`/`..`、反斜杠、控制字符、空段、超长（`src/application/importing/referenced/model.py:31-59`） | PASS |
| A-4 | `ordinal ≥ 0` 且**唯一** | 解析期 `ordinal < 0` → malformed（`:956-959`）；容器分支 `ordinals` 集合去重（`:1044-1048`） | PASS |
| A-5 | 每项 `facts` = **容器物理身份**（四键同一） | 注册期：`_facts()` 严格四键 + 类型/hex 校验（`:1060-1080`），并逐项与首项 `facts` 比对（`:1053-1057`）；匹配期：`grant.container_facts` 与 `source_locations` 四键（`volume_serial`/`file_id`/`size_bytes`/`content_digest`）比对（`:621-623,639-657`） | PASS（见 P3-01 口径说明） |
| A-6 | 任一不符 → **整 grant `SOURCE_ACCESS_DENIED`、零部分接受** | `_parse_scope` 在 `_grants[grant_id] = grant` 之前抛错（`:187` 早于 `:227`），无任何状态写入；`_bindings` 不动 | PASS |
| A-7 | 超 `budget.max_entries` / 硬上限 10,000 → **`SOURCE_BUDGET_EXCEEDED` 不截断** | `register` 先按 budget 判（`:185-186`），`_parse_scope` 再按 `_MAX_SCOPE_ENTRIES=10000` 判（`:59,928-931`）；两处均 raise，无切片/截断路径 | PASS |
| A-8 | 不新增错误码；不放宽 facts/identity/撤销/TTL | 新增代码仅使用闭集既有码 `SOURCE_ACCESS_DENIED`/`SOURCE_BUDGET_EXCEEDED`/`SOURCE_ENTRY_MISSING`；`_checked`/TTL/撤销/`_bindings` 语义零 diff（实现 commit 仅 3 个 hunk 面） | PASS |
| A-9 | 匹配沿用 `entry_key OR locator OR ordinal` + **容器** facts vs `source_locations`、**无路径回退** | `_scope_covers_entry` 容器分支（`:611-636`）：facts 先过 `_location_matches(location, facts)`，再对授权 scope 的 entries 做 OR；`location` 全程来自 Core DB 行，无路径参与；P3-5 越界 ordinal 因"只与 binding 自身 entry 行比较"而天然不命中 | PASS |

- **A-5 说明（P3-01）**：契约同句的括注「四键同一」与 §2.4「核验 facts 与 `source_locations` 当前物理身份一致」在本实现中分别落在
  **注册期（跨项同一）** 与 **逐页授权期（权威比对）**；卡片「实现注意 P3-4」写作「**注册期**…参考点锁定为 Core 权威 `source_locations`」，
  与实现时点不同。`SourceReadGrantRegistry` 无 DB 句柄，注册期无法做权威比对；安全性质未受影响（持成员 digest 充当容器 facts 的 grant
  可注册但**永不能授权任何页**，`test_container_grant_facts_reference_point_is_the_container_identity` 实证 typed 拒绝且零映射）。
  详见 §9 的 P3-01，不建议因此返修。

## 2. B — 安全语义：**PASS**

| # | 攻击/绕过面 | 结论 | 证据 |
|---|---|---|---|
| B-1 | 跨容器 `path`（把别的文件塞进同一 grant） | 拒绝 | `:1049-1052`；矩阵 `other_container` 两处用例（Core 真实装配 + 协议面）全 typed、grant 未注册 |
| B-2 | 成员 digest/尺寸冒充容器 facts | 不可用 | 匹配期 `_location_matches` 四键严格比对；`test_container_grant_facts_reference_point_is_the_container_identity`（P3-4 判别）；我的破坏点 R1/B2 类同向证明该比较是承重的（作者判别 B2 + 本评论 §8） |
| B-3 | 重复 / 越界 ordinal | 重复 → 注册期拒绝；越界 → 永不命中 | `:1044-1048`；`test_container_grant_out_of_range_ordinal_never_matches`（p2/p3 typed、p1 仍可授权 = 逐页 fail-closed 而非整 Run 放宽） |
| B-4 | locator 注入（`../`、绝对、盘符、UNC、控制字符） | 拒绝 | `validate_locator`；矩阵 `unsafe_locator`/`absolute_locator` |
| B-5 | 预算边界绕过 | 无 | budget 判 + 硬上限判均在注册早期；IPC 用 `max_entries=65`+66 项 → `SOURCE_BUDGET_EXCEEDED`；Core 用 20000 配置预算 + 10001 项 → 硬上限 typed |
| B-6 | 部分接受 / 静默截断 | 无 | 注册期无写入路径（`:227` 才是唯一注册点）；授权期 `refused` 非 0 即整体 raise 且 `pending` 不落库（`:511-556`，本卡零改动）；Host 超预算走 typed 而非 `Take()`（`:368-378`，我的破坏点 R3 类同向证明） |
| B-7 | `find_bound_for_source`/`commit_guard` 是否被改坏 | 零 diff，语义不变 | 实现 commit 的 hunk 不触及 `:738-771`、`:293-303`；`commit_guard` 仍用 `container_facts` 走 `source_lease`（`test_container_member_outside_the_signed_entries_cannot_be_read` 实证未授权页 commit 窗口不打开） |
| B-8 | folder / image 语义 | 未破坏 | folder 分支仅做 tuple 解包重构（`:984-1021`），`_folder_scope_covers` 零 diff；image 显式单 entry（`:1030-1033`）；我的破坏点 R2 证明该守卫承重（删除后 `test_image_grant_keeps_the_single_entry_shape` RED） |
| B-9 | 重名成员 + OR 的子集 grant（窄角） | 契约冻结语义，非实现偏差；生产不可达 | 见 P3-04：`locator` 命中使同名成员互相覆盖，但生产 Host 总是铸**全量**权威列表，且该 OR 条款是 v1.4 明文冻结 |

## 3. C — Host 侧：**PASS**

| # | 要求 | 结论 | 证据 |
|---|---|---|---|
| C-1 | 容器 locator/ordinal **只来自 Core 权威扫描 entries**，不推断/不重编号 | 是 | `RunSourceRange.Resolve` 仅在 `kind ∈ {zip,cbz,pdf}` 时把 `identity.Entries` 原样放入 `RunSourceScope.ContainerEntries`（`HostRuntime.cs:1795-1805`）；`identity` 来自 `SourceIdentityCache`，其写入唯一入口 `ReadSourceIdentity` 逐项读 `source.entries[]`，拒绝空 locator/负 ordinal/越界（`SourceScanScheduler.cs:1750-1831,1837-1850`）。单测用 `ordinal=0/5/9` 断言"不重编号"；我的破坏点 R1（`Select((m,i)=>m with{Ordinal=i})`）使该用例 RED |
| C-2 | `ContainerEntryPlan` 预算语义（typed、不截断） | 是 | `SourceReadCoordinator.cs:368-378`：非容器 → null；空/缺 → null；`Count > maxEntries` → `SourceAccessException("SOURCE_BUDGET_EXCEEDED")`；边界 `==` 接受。单测 `ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`（含 `Assert.Same` 原样返回、边界 4/4 接受） |
| C-3 | 铸 N 项时容器文件**只指纹一次** | 是 | `DescribeContainer` 在 `containerPlan is not null` 时调用一次（`:405-420`），返回的 facts 以 `DeepClone()` 分配给每个 entry；容器路径不进 `paths` 循环（`paths = new[]{path}`），无每成员 I/O |
| C-4 | facts 参考点不由成员 digest / Host 推断 | 是 | `DescribeContainer` 对**容器句柄**取 identity before/after + SHA256（`:238-275`），非成员；成员内容从不参与 facts |
| C-5 | 缓存不足 / 超上限 → best-effort 跳过、不阻断 managed Run | 是 | 无 live identity → COLD（`HostRuntime.cs:1787-1793`）→ 有界 on-demand 扫描（每切片 ≤ 预算）→ 仍 cold 则跳过并只记计数（`:1996-2002`）；mint 失败/超预算 → 该源 skip 并记 typed code（`SourceReadCoordinator.cs:167-187`），全 skip 时**不发命令**（`:188-192`），managed-only Run 不受影响 |
| C-6 | Run wire 键集不变 | 是 | `AuthorizeRunAsync` 仍发 `{grant_ids, command, scope}`（`:193-202`）；scope 内部 `entries[]` 是 C-16 v1.4 既有形态；`CORE_PROTOCOL_MINOR=3` 实测；`core_service.py` 本卡零 diff |

## 4. D — AC-J1…J4 独立验证：**4/4 MET**

真实 IPC 命令（本机实跑，`cwd=apps/desktop-avalonia`）：

```text
NEWMANGA_FEA11_IPC=1 dotnet test tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11RunGrant"
→ 已通过! 失败: 0，通过: 5，已跳过: 0，总计: 5（7 s）EXIT=0
```

我的运行生成了新的真实见证（仓外隔离根，与作者证据同格式）：
`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\fixtures\ipc-5f399e8390174fbbaa514d4069e0f773\run-grant-2b-container-members.txt`，内容：

```text
scan -> cache: s1 entries=3 s2 entries=3 s3 entries=66
RunSourceRange -> container member plans 3/3/66
omitted member -> SOURCE_ACCESS_DENIED and resolve -> SOURCE_ACCESS_DENIED
out-of-range ordinal -> SOURCE_ACCESS_DENIED
mint over max_entries=65 -> SOURCE_BUDGET_EXCEEDED (not truncated)
66-member container: minted=1 bound_pages=1 for the LAST (ordinal 65) + first member
zip members p1..p3 -> authorize + resolve OK
cbz members q1..q3 -> authorize + resolve OK
wire/stderr path leak -> 0
PASS
```

| AC | 判定 | 独立验证落点 |
|---|---|---|
| **AC-J1** 容器 ≥3 成员真实 IPC：每成员页 authorize + `resolve_page_resource`；未授权成员不可读 | **MET** | 真实 IPC：真实 `multi.zip`/`multi.cbz` 各 3 成员，生产 scan→cache→range→mint→authorize 路径，p1..p3 / q1..q3 每个 `bound_pages=1` 且 resolve OK；`minted=1`（一个 grant 覆盖全部成员）。Core 真实装配 `test_container_members_are_entry_granular_on_every_authorized_member[zip|cbz]` 用**逐成员不同像素尺寸**证明读的是该成员；`test_container_member_outside_the_signed_entries_cannot_be_read` 证明 scope 少一项 → typed、commit_guard 不开、provider 拒绝；IPC 省略末成员 → authorize typed 且 resolve typed |
| **AC-J2** 任一项 locator/facts/ordinal 不符或 entry 不在 version → 整体 typed、零映射；容器替换/漂移/撤销/过期 typed | **MET** | 注册矩阵 `test_container_grant_any_bad_entry_refuses_the_whole_grant[...]`（unsafe/absolute locator、负/重复 ordinal、跨容器 path、facts 不一致）全部 `SOURCE_ACCESS_DENIED`、grant 未注册、`_bindings` 空、业务表快照不变；协议面同矩阵 + `over_budget`；P3-4/P3-5 判别用例通过；越界 ordinal 不命中且不误伤同 grant 内其它成员；既有撤销/TTL/generation 用例（既有 50 例）全绿 |
| **AC-J3** 超 `max_entries`/硬上限 → typed 不截断；≥65 成员有明确用例 | **MET** | Core：`max_entries=3` 边界接受 3 项并逐页授权成功；+1 项 → `SOURCE_BUDGET_EXCEEDED` 且未注册；配置 20000 + 10001 项 → 硬上限 10,000 typed。Host：`ContainerEntryPlan` 超预算抛 typed、边界不截断。真实 IPC：mint `max_entries=65` + 66 项 → typed；**66 成员容器由 1 个 grant 覆盖，`ordinal=65` 的最后一个成员 authorize+resolve 成功**（`minted=1`，无 64 段截断） |
| **AC-J4** managed/旧路径零回归；零漂移（pins 18/18、Run wire/minor/schema/依赖零改动）；全量门禁不降；EV/Handoff 不夸大 | **MET** | 见 §6/§7：`doc/plan`/`doc/contracts`/`schema.py`/`core_assembly.py`/依赖/`NewManga.App`/STATUS/PLAN/LEDGER 自起点到当前 HEAD **零 diff**；`CORE_PROTOCOL_MINOR=3`；pins 18/18；全量 pytest 3305/10、全量 .NET 1562/0/91 均不低于基线；卡/Handoff/EV 保留 limitations 且无夸大表述 |

## 5. E — 零漂移 / 证据 / 治理门禁：**PASS**

| 项 | 实测 | 结果 |
|---|---|---|
| 自有 commit 集 ⊆ allowed_paths | `changed-files.txt` 7 行 vs `git show --name-status` 并集 **逐行一致**；7/7 均匹配卡面 allowed_paths | PASS |
| `doc/plan` / `doc/contracts` / `schema.py` / `core_assembly.py` / 依赖 / `NewManga.App` / STATUS/PLAN/LEDGER 零 diff | `git diff --name-status 5397be149 8e1883655 -- <这些路径>` → **空** | PASS（强于"仅本卡 commit"口径：起点到当前 HEAD 全区间） |
| `CORE_PROTOCOL_MINOR` | `src/bootstrap/core_service.py`：`PROTOCOL_MINOR = 3`；Run 授权命令 `AuthorizeSourceReadForRun` 仍在 | PASS |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`，`C16 ad25fb3c89bb`，EXIT=0 | PASS（与 C-16 v1.4 引脚一致） |
| `check.ps1` | 默认 **PASS (3 warnings)** / `-TaskPath doc/tasks/FEA-11-RUN-GRANT-2.md` **PASS (3 warnings)**，EXIT=0 ×2 | PASS |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` → `OK: rendered counts match FEA-C07 doc`，EXIT=0 | PASS |
| EV 逐文件 sha256 | 我对 EV §5 列出的 15 个文件用 `Get-FileHash` 全量复算：**15/15 匹配** | PASS |
| 证据树结构 | `logs/` **8** 份、`tools/` **4** 份、`EV.md`/`MANIFEST`/`changed-files`/`scope-validation.log` 齐 | PASS |
| `discrimination.log` 8/8 可信性 | 逐条审读 `tools/discrimination.py`：每个破坏点是对**一个已提交守卫**的唯一字节替换（`count(old)!=1` 即 SETUP_FAILED）、目标用例与该守卫一一对应、`finally` 按备份原字节恢复并 sha 比对、末尾 `final_rebuild` + 恢复后两套定向套件 exit 0。日志记录的恢复 sha（`713be364…`/`efc362b…`/`926da435…`）与当前工作树实测**逐一相等** | 可信 |
| `scope-validation.log` 的 foreign_commit/integration 说明 | 实测 `git log --oneline 5397be149..61b7eb249` = `61b7eb249`（仅 2A 卡/EV/Manifest）+ `45fdabee6`（仅 DSH-PROGRESS），与本卡无关；本卡自有 commit 集排除它们**成立**。仓外隔离根确实存在 `integration/{pytest,dotnet}.{log,exit}`（Lead 集成门禁 6:51/6:55 生成，晚于 Manifest 6:49），故"generation-time snapshot、非冻结终态"的披露**成立**。该 log 的 `repo_head=3dc822b77` 是重跑时的 HEAD（数值结果不变：changed=7/PASS/zero-drift 全空） | 成立 |

## 6. F — 门禁数字与不夸大：**PASS**

| Gate | 作者/Lead 记录 | 我本次实测 | 一致性 |
|---|---|---|---|
| 定向 pytest（`tests/core/test_host_control.py` + `tests/fea11/test_source_run_grant.py`） | 74 passed（基线 50） | **74 passed, 1 warning**（7.68s；二跑 9.73s） | 一致 |
| Host 单测 `--filter SourceRegistry` | 32 passed（基线 29） | **32 passed / 0 failed / 0 skipped**（214 ms） | 一致 |
| 真实 IPC `NEWMANGA_FEA11_IPC=1 --filter Fea11RunGrant` | 5 passed（基线 4） | **5 passed**（7 s） | 一致 |
| 全量 pytest | 3305 passed / 10 skipped | **3305 passed, 10 skipped, 11 warnings**（245.49s，EXIT=0） | 一致 |
| 全量 .NET | 1562 / 0 / 91 | **1562 passed / 0 failed / 91 skipped**（21+38+253+117+31+215+167+720=1562；skip 60+24+7=91；EXIT=0） | 一致（基线 1559/0/90：+3 单测、+1 opt-in IPC skip） |
| build | 0 warning / 0 error | 派生 rebuild 均 0 error（我为破坏点做的两次增量 build） | 一致 |
| 卡/Handoff/EV 数字与日志 | `feature.log`/`host-unit.log`/`host-ipc.log`/`full-pytest.log`/`full-dotnet.log` 原始输出逐项对应 | 全部核对 | 一致 |

**不夸大核对**：卡 `:95`、Handoff `:51-62`、EV `:13-14,117-122` 均明确保留 **L-G16（>4096 成员不入缓存）**、L-G1（300s/长 Run）、L-G2（加密源）、**L-G9**（Core 重启）、**L-G10**（L-R11）、L-G8（成本线性）、L-G13（flaky）与 **P3-6/N-4 口径**（`max_entries` = 单 grant 条目数；64 = 单命令 `grant_ids` 数；实现硬上限 10,000 为更严 fail-closed，**不得**表述为"成员数上限"）。全文检索「referenced Run 全场景可用」「L-R1 全修」仅出现在**否定句**中。**PASS**。

## 7. G — 回归与测试卫生：**PASS**

- 四个测试文件的 diff **无删除/弱化断言**（唯一行为性改动是 2A 的 IPC 第 (5) 步：归档第二成员由"typed 拒绝"改为"可用"，测试名同步更新，已在 Handoff §2/EV §7 登记，属本卡目标行为）。
- **无新增 skip/xfail**：新增 IPC 用例沿用既有 opt-in 属性 `[Fea11RunGrantIpcFact]`（全量默认运行即 +1 skip，已登记）；grep 全 diff 无 `skip`/`xfail` 新增。
- 无未登记行为变化：容器单 entry 场景现在也会执行 `validate_locator`（契约要求的收紧，卡面 J-1 已写明）；image 单 entry 守卫显式化（语义不变）。
- 日志无敏感路径泄漏：证据日志只含仓库路径与解释器路径；真实 IPC 断言 fixture 路径在 wire NDJSON 与 Core stderr **0 命中**（我的运行同样 `PASS`）。

---

## 8. 破坏性复跑记录（自选 2 点；已逐字节恢复 + sha 复核）

约束遵守：先备份原字节到仓外 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\review-r1\`，替换前断言 `old` 出现次数 == 1，结束后写回备份字节并 `Get-FileHash` 比对；仓内 `git status --porcelain` 恢复为空。

| # | 自选破坏点（均不在作者 B1–B8 内） | 目标用例 | 结果 | 恢复 |
|---|---|---|---|---|
| **R1** | Host **重编号**权威 ordinal：`identity.Entries` → `identity.Entries.Select((member,index)=> member with { Ordinal = index }).ToArray()`（`HostRuntime.cs:1803-1804`） | `SourceRegistryTests.RunSourceRangeCarriesContainerMemberIdentitiesVerbatim`（0/5/9 原样断言） | **RED_AS_EXPECTED**：`失败! 失败:1，通过:0`，堆栈落在该测试，EXIT=1 | `HostRuntime.cs` sha `efc362bbb9ec97ef19a76b7e79d14955dd3cd9eeabcae982721e51dc27805ecb`（=交付 head 工作树字节，byte-identical）；rebuild 0 error；`--filter SourceRegistry` → **32 passed** |
| **R2** | Core **删除 `image` 单 entry 守卫**（`source_read_refs.py:1030-1033`） | `tests/core/test_host_control.py::test_image_grant_keeps_the_single_entry_shape` | **RED_AS_EXPECTED**：`1 failed`，EXIT=1 | `source_read_refs.py` sha `713be364b0d04727a9c6252cce30257a012834c54507c46f2ae98d8616211382`（=交付 head 工作树字节，byte-identical）；定向套件 → **74 passed** |

**补充：全量 .NET 的 tracked 证据重写与恢复（破坏性操作，已逐字节恢复）**
- 跑前 `verification/FEA-09/logs/wire-redacted.ndjson` 工作树 sha256 = `548de629d163d80b9cd8d1e62251de2016782e46a0c48a48575749d2a059d593`（备份字节）。
- 全量 .NET 结束后该文件被重写（工作树 sha256 = `8cf9749ca72492ea55484a8e44e889a61936e36ac379c91699ca931065e54c62`，`git status` 显示 ` M`）。
- 写回备份字节后 sha256 恢复为 `548de629…`，`git hash-object` = `ee126f8aef95b8b0557e166ed6390e721f0b097e` = `HEAD:verification/FEA-09/logs/wire-redacted.ndjson`；`git status --porcelain` 空。
- **结论**：作者/Handoff 所述"全量 .NET 会重写 FEA-09、跑后 `git checkout` 恢复"**属实**；**全量 pytest 不会命中**（我的全量 pytest 结束后工作树仍 clean，与 `full-pytest.log` 末尾 `unchanged` 一致）。

---

## 9. Findings

| ID | 级别 | 位置 | 事实 | 影响 | 建议 |
|---|---|---|---|---|---|
| **P3-01** | P3（口径） | 卡「实现注意 P3-4」；`source_read_refs.py:1034-1057` vs `:621-623`；`tests/fea11/test_source_run_grant.py`（P3-4 用例 docstring） | 卡片 P3-4 要求「**注册期** facts 参考点锁定 Core 权威 `source_locations`」；实现注册期只证明"四项 facts 彼此相同"，与 `source_locations` 的权威比对发生在**逐页授权期**（`_location_matches`）。`SourceReadGrantRegistry` 无 DB 句柄，注册期无法做权威比对 | 无安全影响：持成员 digest 充当容器 facts 的 grant 可注册但**永不能授权**（typed、零映射、零绑定）；AC-J2 与 P3-4 判别用例均通过 | 不返修；建议 closeout 时把该口径写入卡/EV（"注册=同一性；授权=权威性"），若确需注册期 DB 校验则另立卡 |
| **P3-02** | P3（证据措辞） | `verification/FEA-11-RUN-GRANT-2/EV.md:52-53` | EV 写「全量 pytest / 全量 .NET …**两次均执行** `git checkout -- verification/FEA-09`」；实测全量 pytest 未重写该文件（`full-pytest.log` 末尾 `unchanged`，我本次全量 pytest 后 `git status` 亦为空）。Handoff §2 的表述准确 | 仅措辞，不影响任何结论 | 后续更新 EV 时改为"全量 .NET 重写并恢复；全量 pytest 未命中" |
| **P3-03** | P3（署名/溯源） | 卡 frontmatter `owner: run-grant-impl`；Handoff/EV/Manifest `run-grant-2b-impl` | 卡面 Owner 与交付记录/Handoff 的作者标识不一致（实现者为 DSH Agent Teams teammate `run-grant-2b-impl`） | 不影响实现/证据有效性；影响 closeout 的 owner 字段一致性 | Lead closeout 时统一（卡面 owner 或交付记录注明 teammate 映射） |
| **P3-04** | P3（冻结语义的窄角 + 建议） | `_scope_covers_entry:627-635`；`test_container_grant_duplicate_member_locators_are_legitimate` | 容器允许重名成员（C-15 §3.2），冻结的 OR 匹配使"按 locator 命中"对同名成员不具选择性：**若**某 grant 只签其中一个同名成员（契约允许 1..N 的子集），同名兄弟成员的页也会因 `locator` 相等而被授权（读取仍用 binding 自身 entry 行）。生产 Host 的 `ContainerEntryPlan` 总是原样铸**全量**权威列表，因此产品路径无扩大；IPC 的"省略成员"负例用的是不同 locator（`066.png`），未覆盖此角 | 无生产暴露；属 v1.4 明文（`entry_key OR locator OR ordinal`）的固有语义，非本实现放宽 | 可选加固（非本卡门禁）：Host 用权威 `SourceIdentityEntry.EntryId` 作 `entry_key`（当前用本地 `entry-0..N-1`），并补一条"同名成员子集 grant"用例把行为钉死；如需改变语义必须新契约定，不在本卡 |

> 计数：**P0 = 0，P1 = 0，P2 = 0，P3 = 4**。无 changes-requested 级问题。

---

## 10. 最终判定

**`approved`。** AC-J1…J4 全部 **MET**；C-16 v1.4 §2 的容器 1..N 授权接受面、逐项校验、零部分接受、typed 预算不截断、匹配期 facts 权威比对与无路径回退均逐字落地；Host 侧"只取 Core 权威身份、每容器只指纹一次、超限 typed、缓存不足 best-effort 跳过、Run wire 不变"全部成立；零漂移、pins/check/API/EV sha 与两套全量门禁均独立复现且不降；判别性 8/8 可信，另有我的 2 个新破坏点 RED 后逐字节恢复。4 个 P3 不影响合并结论，建议在 Lead closeout 中一并回填（P3-01 口径、P3-02 EV 措辞、P3-03 owner、P3-04 可选加固/用例）。

**建议下一步（供 Lead）**：①closeout 回填卡面 `status`/`delivery_head=018008989…`/`canonical_evidence_status`（2A 先例）；②处置 P3-01/02/03（文档层，不需重跑门禁）；③P3-04 若采纳，作为独立小卡（Core/Host + 用例），不在本卡返修；④本卡不宣称长 Run / 加密源 / Core 重启 / L-R11 / L-G16 / L-R1 全场景。

---

## 11. 真实性声明

1. **身份与独立性**：本会话是父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a` 派发的**独立上下文 fresh subagent**；未参与 `FEA-11-RUN-GRANT-2` 或 `FEA-11-RUN-GRANT-2A`/`RUN-GRANT-1` 的实现、返修或审查。只读被审字节（`018008989` 实现/测试 + `8e1883655` 文档/证据）。
2. **写操作仅一处**：只写本文件 `doc/reviews/FEA-11-RUN-GRANT-2-r1.md`；未改实现/测试/证据/卡/契约；未 `git add/commit/push`；未创建 worktree；未删除/移动任何仓库资源。
3. **实测命令**（本会话亲自执行）：`git rev-parse/status/log/show/diff/ls-tree/hash-object`；`pwsh tools/governance/verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、`C:/Python314/python.exe tools/generate_api_inventory.py --check`；`pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`（两次）；`pytest tests -q`（全量）；`dotnet test … --filter SourceRegistry`；`NEWMANGA_FEA11_IPC=1 dotnet test … --filter Fea11RunGrant`；`dotnet test NewManga.sln -c Release`（全量）；`Get-FileHash`（证据 15 文件 + 破坏点恢复复核）；两次自选破坏点的定向复跑。
4. **NOT_RUN（如实标注）**：`verification/FEA-11-RUN-GRANT-2/tools/{scope_validation,discrimination,gen_ev,gen_manifest}.py` **未重跑**——它们会**重写** committed 证据字节，超出"只写一个文件"的硬约束；我改为逐行审读工具 + 独立用 git 重算其结论（7 文件/zero-drift/foreign commit/恢复 sha），并另做 2 个新破坏点补强判别性。作者 `logs/` 内的 8/8 破坏点未逐条重跑，仅做可信性审读与恢复 sha 复核。
5. **证据优先级**：所有结论以仓库真实字节（代码/测试/契约/pins/Git/实跑输出）为准；Handoff/EV 自述仅在标注「文档声称」处引用。我的全量门禁日志另存仓外 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\review-r1\`（不进入本卡证据树，避免污染）。
6. **未宣称**：本文不宣称 referenced Run 全场景可用、不宣称 L-R1 全修、不宣称长 Run/加密源/Core 重启/L-R11/L-G16 可用，也不对未实跑项背书。
