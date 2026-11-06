# FEA-11-RUN-GRANT-2（2B）Canonical Evidence：容器成员 entry 授权通道

> **结论先行。** 本卡按 **C-16 v1.4 §2**（容器源 `entries[]` 1..N）实现容器成员 entry 授权通道：
> **Core** 注册期接受 zip/cbz/pdf 的 1..N 容器成员条目（逐项校验：locator 安全、ordinal ≥ 0 且唯一、同一容器 `path`、
> facts 四键=容器物理身份；任一不符 **整 grant typed `SOURCE_ACCESS_DENIED`、零部分接受**；条目数超 `budget.max_entries`
> → **`SOURCE_BUDGET_EXCEEDED`，不截断**），匹配期沿用 `entry_key OR locator OR ordinal` + **容器 facts vs `source_locations`**
> （无路径回退、永不使用成员 digest；`find_bound_for_source`/`commit_guard` 不变）；**Host** 用 2A 的 `SourceIdentityCache`
> （Core 权威 `version_id` + `entries[]`）为容器源铸 **N 项** grant（locator/ordinal **原样使用**、容器 path/facts 同一、
> 容器文件只指纹一次），超 `max_entries` → **typed、不截断**；缓存不足 → best-effort 跳过（R-5 语义不变）。
> **真实 IPC 已证明**：真实 zip / cbz 各 3 成员 → 每个成员页 `authorize → resolve_page_resource` 成功；删/错一项 →
> typed `SOURCE_ACCESS_DENIED` 且**不可读到未授权成员**；**66 成员**容器由**一个** grant 覆盖（64 是 grant 数上限、不是成员数上限），
> **最后一个成员（ordinal 65）可授权**（不截断见证）。
> **不夸大**：本卡只覆盖「容器成员 entry 授权通道」；folder **>4096 成员不入缓存**（L-G16，沿用 2A 登记）、长 Run（L-G1）、
> 加密源（L-G2）、Core 重启（L-G9）、L-R11（L-G10）**均未解决**；**L-R1 未全修**；不得表述为「referenced Run 全场景可用」。

| 项 | 值 |
|---|---|
| task | `FEA-11-RUN-GRANT-2`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-2.md`；`status` 未改） |
| Owner | `run-grant-2b-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=97812958d`；实现起点 `5397be149`（工作树 clean，实测） |
| 本次 delivery_head | `0180089894b2286d8ff6a94289b84dd318871d18`（实现 `7466cb99d` + 测试 `018008989`；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 |
| 契约字节 | **本卡零变更**：C-16 v1.4 已冻结（`doc/plan/**`、`doc/contracts/**` 本卡零 diff；`verify_pins` 18/18）；wire 字段/命令集/`CORE_PROTOCOL_MINOR=3`/错误闭集零改动 |
| 依赖 | **零新增** |
| 证据生成 | `verification/FEA-11-RUN-GRANT-2/tools/gen_ev.py`（`repo_head_at_generation=3dc822b777c726905e36aa7cd83e7391adf602ba`） |

## 1. 交付 commit 链（起点 `5397be149` → delivery_head `0180089894b2286d8ff6a94289b84dd318871d18`）

```text
0180089894b2286d8ff6a94289b84dd318871d18 test(fea-11-run-grant-2): container member entry matrix, 3-member zip/cbz IPC and the 66-member no-truncation witness
7466cb99d feat(fea-11-run-grant-2): container member entries in the Core grant registry + Host N-entry Run mint
5397be149 (起点 HEAD，工作树 clean)
```

文档提交（本卡记录 / Handoff / 本证据树）随后同批提交，均在卡面 `allowed_paths` 内。

## 2. 门禁实测（`0180089894b2286d8ff6a94289b84dd318871d18`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **已成功生成。 / 0 个警告 / 0 个错误** | `logs/build.log` |
| 定向 Python（AC-J1/J2/J3 + 既有 50 例回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **74 passed, 1 warning in 6.78s**（基线 50，新增 24） | `logs/feature.log` |
| Host 单测（AC-H3 + 2A 回归） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **32 passed / 0 failed / 0 skipped（1 个测试程序集）**（基线 29，+3） | `logs/host-unit.log` |
| 真实 IPC（AC-H4 / AC-J1/J2/J3） | `NEWMANGA_FEA11_IPC=1 dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **5 passed / 0 failed / 0 skipped（1 个测试程序集）**（基线 4，+1 容器成员用例；2A 用例扩展为第二成员可用） | `logs/host-ipc.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **3305 passed, 10 skipped, 11 warnings in 241.31s (0:04:01)**（基线 3281/10） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release` | **1562 passed / 0 failed / 91 skipped（8 个测试程序集）**（基线 1559/0/90） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **PIN AUDIT: PASS (all 18)** / **Governance check: PASS (3 warnings)** / **OK: rendered counts match FEA-C07 doc** | `logs/gates.log` |
| 范围 | `python verification/FEA-11-RUN-GRANT-2/tools/scope_validation.py` | **result=PASS changed=7 out_of_scope=[]** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-2/tools/discrimination.py` | **result=PASS breaks=8 all_red_then_restored** | `logs/discrimination.log` |

**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行
`git checkout -- verification/FEA-09`（见各日志末尾的 `RESTORED`/`unchanged` 行）。

## 3. 判别性验证（8 破坏点；删掉实现必须变红）

`logs/discrimination.log` 逐个破坏**一个已提交的实现分支**后运行**一个**目标用例，要求变红（exit≠0），随后按**原字节**恢复并复核
sha256，最后重新 build 恢复二进制并对恢复后的树补跑定向套件。

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| B1 | Core 容器基数回退为 2B 前「恰好 1 entry」（多成员通道被禁用） | tests/fea11/test_source_run_grant.py::test_container_members_are_entry_granular_on_every_authorized_member[zip] | RED_AS_EXPECTED / RESTORED |
| B2 | Core 容器 facts 参考点不再与 source_locations 比对（成员 digest 可冒充容器身份） | tests/fea11/test_source_run_grant.py::test_container_grant_facts_reference_point_is_the_container_identity | RED_AS_EXPECTED / RESTORED |
| B3 | Core 单 grant 条目预算检查被删除（超 max_entries 不再 typed，AC-J3 判别） | tests/fea11/test_source_run_grant.py::test_container_grant_entry_budget_is_typed_and_never_truncated | RED_AS_EXPECTED / RESTORED |
| B4 | Core 容器 ordinal 唯一性校验被删除（重复 ordinal 被接受） | tests/core/test_host_control.py::test_container_grant_violations_are_typed_with_zero_partial_acceptance[duplicate_ordinal] | RED_AS_EXPECTED / RESTORED |
| B5 | Core 容器「同一容器路径」校验被删除（跨容器条目被接受） | tests/core/test_host_control.py::test_container_grant_violations_are_typed_with_zero_partial_acceptance[other_container] | RED_AS_EXPECTED / RESTORED |
| B6 | Core 容器成员 locator 安全校验被删除（`../` locator 被接受） | tests/core/test_host_control.py::test_container_grant_violations_are_typed_with_zero_partial_acceptance[unsafe_locator] | RED_AS_EXPECTED / RESTORED |
| B7 | Host Run range 不再传递 Core 权威成员身份（回到容器单 entry，AC-H3/IPC 判别） | FullyQualifiedName~ContainerMemberEntriesAuthorizeEveryMemberOverRealIpc | RED_AS_EXPECTED / RESTORED |
| B8 | Host 超额成员列表被静默截断（不再 typed SOURCE_BUDGET_EXCEEDED，AC-J3 判别） | FullyQualifiedName~ContainerEntryPlanIsVerbatimAndTypedOverTheBudget | RED_AS_EXPECTED / RESTORED |

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性/真实证据 | 证据 |
|---|---|---|---|
| **AC-J1** 容器 ≥3 成员真实 IPC：每个成员页可 `AuthorizeSourceReadForRun` 绑定并 `resolve_page_resource`；不可读到未授权成员 | MET | 真实 IPC `ContainerMemberEntriesAuthorizeEveryMemberOverRealIpc`（真实 zip/cbz 各 3 成员：逐个 `authorize → bound_pages=1 → resolve_page_resource` OK；`minted=1` 即一个 grant 覆盖全部成员）；Core 真实装配 `test_container_members_are_entry_granular_on_every_authorized_member[zip|cbz]`（每成员 provider 读到**该成员自己的像素尺寸**）；未授权面 `test_container_member_outside_the_signed_entries_cannot_be_read`（scope 少一项 → typed、`commit_guard` 不开、provider 拒绝） | `logs/host-ipc.log`、`logs/feature.log`、`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\fixtures\ipc-*\run-grant-2b-container-members.txt` |
| **AC-J2** fail-closed：任一项 locator/facts/ordinal 不符或 entry 不在 version → 整体 typed、零映射写入 | MET | Core 注册矩阵 `test_container_grant_any_bad_entry_refuses_the_whole_grant[...]`（unsafe/absolute locator、负 ordinal、重复 ordinal、跨容器 path、facts 不一致 → 全部 typed 且 grant 未注册、`_bindings` 空、业务表快照不变）；协议面 `test_container_grant_violations_are_typed_with_zero_partial_acceptance[...]`；P3-4 `test_container_grant_facts_reference_point_is_the_container_identity`（成员 digest 冒充容器 facts → typed 拒绝；同形状真容器 facts → 成功）；P3-5 `test_container_grant_out_of_range_ordinal_never_matches`（越界 ordinal 不命中）；IPC 删一项/错一项 → typed `SOURCE_ACCESS_DENIED`；判别 B1/B2/B4/B5/B6 | `logs/feature.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| **AC-J3** 上限：超 `max_entries` 或 64 grant 上限 → typed/按契约，不截断；≥65 成员有明确用例 | MET | Core `test_container_grant_entry_budget_is_typed_and_never_truncated`（`max_entries=3` 边界接受、+1 项 → `SOURCE_BUDGET_EXCEEDED` 且未注册；配置预算 20000 时命中实现硬上限 10000 → 同样 typed）；Host `ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`（超预算抛 typed、边界不截断）；真实 IPC：Host mint `max_entries=65` + 66 项 → typed `SOURCE_BUDGET_EXCEEDED`（不截断），**66 成员容器由 1 个 grant 覆盖且 ordinal=65 的最后一个成员可授权/可读**（64 为单次命令 grant 数上限，不是成员数上限）；判别 B3/B8 | `logs/feature.log`、`logs/host-unit.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| **AC-J4** managed/旧路径零回归；零漂移（pins 18/18、Run wire/minor/schema/依赖零改动）；全量门禁不降；EV/Handoff 不夸大 | MET | `scope-validation.log`（changed=7 全 ALLOWED；`doc/plan`/`doc/contracts`/schema/迁移/依赖/`NewManga.App`/STATUS/PLAN/LEDGER 全 ZERO_DIFF；`CORE_PROTOCOL_MINOR=3`）；`verify_pins` 18/18；全量 pytest / 全量 .NET 不降（见 §2）；既有 50 例定向回归全绿；Handoff 与本节均保留 limitation 与未宣称项 | `scope-validation.log`、`logs/gates.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |

### 4.1 与卡面 AC-H1…H5 的对应（scope review 口径）

| 卡面 AC | 本卡证据 |
|---|---|
| AC-H1（C-16 v1.4 UNFREEZE） | 由前置卡 `FEA-11-RUN-GRANT-2B-PREREQ-1`（`d8dcfc07a`）完成；本卡 `doc/plan/**` 零 diff、pins 18/18（`logs/gates.log`）。 |
| AC-H2（Core 注册/匹配） | §4 AC-J2 全部 Core 用例 + `_scope_covers_entry` 多 entry 匹配；`_bindings` 写入语义不变（`bind_imported_entry`/`find_bound_for_source` 未改，既有回归全绿）。 |
| AC-H3（Host 铸 N 项、权威来源、上限 typed） | `RunSourceRangeCarriesContainerMemberIdentitiesVerbatim`（缓存值原样、不重编号、image/folder 保持）、`ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`、`RunAuthorizerForwardsTheContainerMemberPlanToTheMint`；真实 IPC 生产路径（scan → cache → range → mint → Core）。 |
| AC-H4（真实 IPC ≥3 成员 zip/cbz、删/错一项 typed、零越权） | §4 AC-J1/AC-J2 的 IPC 证据；wire/stderr 路径 0 泄漏断言。 |
| AC-H5（门禁/证据） | §2 门禁表 + §3 判别性 + §5 逐文件 sha256 + Handoff 的 limitation/未宣称。 |

## 5. 证据文件 sha256（本文件 `EV.md` 除外）

| 文件 | sha256 |
|---|---|
| `changed-files.txt` | `29257dc05a669990f19550cc951bd125a08dfa61ce855cecbe05ddb035423769` |
| `logs/build.log` | `20c2998b1b24965e29d5eeaca506c20dca793e1ecca0b3b3206bb0214557c4de` |
| `logs/discrimination.log` | `a6e62b7f6bdd335d013679b1287680b1eb5ea3fe76e6446d599de2cf0789bd5c` |
| `logs/feature.log` | `fb7b0da3f4a96d4e643530d3f7a05c7ff7a37cb6c353d37acf6f54ef41b03076` |
| `logs/full-dotnet.log` | `ead164532dba267df87abec6d6cbfb4c1c925dde983d427499e2b62ce2b8cbef` |
| `logs/full-pytest.log` | `32ae890b605934588f2b4b5164eeacec738e986a9e29b47e94768cea4bbf41e2` |
| `logs/gates.log` | `a65776f5231ef4843d8b3d6236e3596bf20c4b98f3fcde4a753920b00e998a0b` |
| `logs/host-ipc.log` | `e500514d29659e254b7f40b4a9d847cc1e0c508ed5625183c0dd250b45b4c63e` |
| `logs/host-unit.log` | `11162ad349a438d92cc50e68dabe72144efb2477ed21ad1956eaf25ed4a29304` |
| `RESOURCE-MANIFEST.json` | `35c1015a83598eea9eee23be2d259f2dc5193a4ffe1a42182c95724e11ffacb2` |
| `scope-validation.log` | `5ed7ff212effa39ee304fa1b56d65acf855643a65ec77d7c6aa666d9430a1b9c` |
| `tools/discrimination.py` | `39d18b652d722b58d6a5468ec798e44b4e9e75e808f37ecce5ae44a551aded1a` |
| `tools/gen_ev.py` | `0b73461c5f33c5c66f9baa09b36ab7e7ba4649275d1bb45ae5c02b7e5f7b16d7` |
| `tools/gen_manifest.py` | `188d1bb9820d1abc3b055e899b8567ad4a50f7067728c4b179e32fccb063baa9` |
| `tools/scope_validation.py` | `b1ba8fad787e1e053bc9949e5bcf09617162d56849e1cc72c881f22f792c22cb` |

> sha256 为**工作树字节**（检出配置 `core.autocrlf=true`；与 RUN-GRANT-1/2A 证据同口径）。
> `RESOURCE-MANIFEST.json` 记录仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\`
> 的聚合 sha256 与逐文件详情，并钉 `delivery_head=0180089894b2286d8ff6a94289b84dd318871d18`。

## 6. NOT_RUN / 未宣称 / 保留 limitation

- **NOT_RUN**：无。本卡 §2 全部门禁均真跑；`logs/*.log` 为原始输出（含 `EXIT=` 行）。
- **未宣称**：本卡不宣称「referenced Run 全场景可用」、不宣称「L-R1 全修」、不宣称长 Run/加密源/Core 重启可用、不宣称 folder >4096 成员可用、不宣称 2C（长 Run 续期）有任何进展。
- **保留 limitation**：
  - **L-G16**（2A 登记，本卡不解决）：`SourceIdentityCache.MaxEntriesPerIdentity=4096` < `DefaultMaxEntriesPerSource=10000` → **>4096 成员的 folder/容器源不入缓存**，Run 期每次触发 on-demand 扫描但不铸造（fail-closed，无错误授权）。
  - **L-G1**（300s TTL/长 Run）、**L-G2**（加密源）、**L-G8**（扫描/铸造成本：容器 grant 的 entries 规模 = 成员数，payload/注册成本随成员数线性增长）、**L-G9**（Core 重启）、**L-G10**（L-R11 gate 两读面差异）、**L-G12②**（在本卡**已闭环**：缓存可用的容器源其多成员 entry 可授权；>4096 成员/L-G16 场景仍不可）、**L-G13**（flaky）。
  - **P3-6/N-4 口径**：`budget.max_entries` 限制**单 grant 条目数**；64 限制**单次命令 `grant_ids` 数**；实现侧硬上限 10,000 为更严 fail-closed；**不得**表述为「容器成员数上限」。
  - **P3-2（wire 追溯）**：C-16 §0 wire 版本行保留历史追溯说明，本卡未改 wire 字段/命令集。
- **接口/边界**：本卡未改 Run wire / `CORE_PROTOCOL_MINOR` / 错误码闭集 / schema / 迁移 / 依赖 / `NewManga.App/**`；未 push。

## 7. 真实性与证据边界

- 本 EV 的数字全部来自 `logs/` 内**原始输出**；未把未跑写成 PASS。
- IPC 夹具/`discrimination` 备份在仓外隔离根；仓内证据为 `verification/FEA-11-RUN-GRANT-2/**`。
- 2A 的 IPC 用例在本卡中被**扩展**（归档第二成员由「typed 拒绝」改为「可用」，测试名相应更新）；2A 的历史 canonical 证据仍按 commit `a0bafc89e` 的字节保留，不受本卡影响。
- 独立 Review 由 Lead 指派（本会话不自审）；集成门禁由 Lead 重跑。

> **P3-01 口径（Review r1）**：契约对容器 facts 的约束在本实现中分两层——**注册期**只证明「N 项 facts 彼此相同」（Core registry 无 DB 句柄），**逐页授权期**由 `_location_matches` 与 Core `source_locations` 四键权威比对；持成员 digest 冒充容器 facts 的 grant 可注册但永不能授权（typed、零映射）。「注册=同一性；授权=权威性」为冻结语义的落地口径，不构成本卡返修项。
