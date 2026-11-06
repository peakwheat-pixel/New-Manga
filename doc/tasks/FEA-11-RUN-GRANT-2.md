---
id: FEA-11-RUN-GRANT-2
title: 容器成员 entry 授权通道（C-16 v1.4 + Core 多 entry 注册/匹配 + Host 铸 N 项；proposed，待依赖）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（2B READY-WITH-UNFREEZE）；依赖 `FEA-11-RUN-GRANT-2A`（done，a0bafc89e）+ `FEA-11-RUN-GRANT-2B-PREREQ-1`（done，C-16 v1.4 d8dcfc07a）均已完成；DSH 2026-11-07 释放为 ready（base 见 frontmatter）；Owner=`run-grant-impl` 复用）
suggested_owner: codex
owner: run-grant-2b-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修）：r1 `35d102d4-e845-4047-8d61-58c709b9c204`（**approved** P0=0/P1=0/P2=0/P3=4；reviewed_head `018008989`）；报告 `doc/reviews/FEA-11-RUN-GRANT-2-r1.md`
depends_on:
  - FEA-11-RUN-GRANT-2A
  - FEA-11-RUN-GRANT-2B-PREREQ-1
base_commit: 97812958d
branch: null
worktree: null
integration_commit: 0180089894b2286d8ff6a94289b84dd318871d18
delivery_head: 0180089894b2286d8ff6a94289b84dd318871d18
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-RUN-GRANT-2
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2.md
  - doc/reviews/FEA-11-RUN-GRANT-2-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2-*.md
  - verification/FEA-11-RUN-GRANT-2/**
  - src/infrastructure/resource_channel/source_read_refs.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - tests/core/test_host_control.py
  - tests/fea11/test_source_run_grant.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - 2A（Host 版本通道）与 2C（长 Run 续期）；L-G1/L-G2/L-G9/L-G10（另卡/保留）
  - C-17/C-06/M2-C1 及其他 16 份契约字节（仅 PREREQ 的 C-16 v1.4）
  - Run wire/`CORE_PROTOCOL_MINOR`/新错误码/schema/依赖；UI/App；真实用户数据；push
---

# FEA-11-RUN-GRANT-2：容器成员 entry 授权通道（proposed，待 2A + PREREQ）

> **状态：`ready`（依赖已全部完成：2A `a0bafc89e` + C-16 v1.4 `d8dcfc07a`；base `53dc38bd4`）。** 按冻结 In/AC 实施。

## 来源

- `FEA-11-RUN-GRANT-1` L-G12②：Host 对 zip/cbz/pdf 只铸容器单 entry（locator=容器名、ordinal=0），Core 按成员 `source_entries` 匹配 → 多成员容器仅首成员可授权。
- scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`：2B 需 **C-16 v1.4 UNFREEZE**（容器 entries 1..N）+ Core 注册/匹配实现 + Host 按 Core 权威 locator/ordinal 铸 N 项；≥3 成员真实 zip/cbz IPC；`max_entries`/64 上限 typed。

## In（草案，待释放时按卡冻结）

| # | 项 | 要点 |
|---|---|---|
| J-1 | Core 注册/匹配 | `_parse_scope` 接受容器 1..N（逐项校验：locator 安全、ordinal 唯一、path 同一容器、facts=容器身份、预算上限）；匹配沿用 `entry_key OR locator OR ordinal` + facts；任一不匹配整体 typed 零写；`_bindings` 语义不变 |
| J-2 | Host 铸 N 项 | 成员 locator/ordinal 必须来自 Core 权威扫描响应（2A 缓存）；容器保持容器 path/facts；超 `max_entries`/64 grant 上限 → typed，不截断 |
| J-3 | 测试/证据 | ≥3 成员真实 zip/cbz：每成员页 authorize+resolve；删/错一项 typed `SOURCE_ACCESS_DENIED`；零越权；判别性破坏点；EV/Manifest |
| J-4 | 门禁 | 全量 pytest/.NET 不降；pins 18/18（C16 v1.4）；check/API/scope；全量跑后恢复 FEA-09 |

## Out

- 2A 版本通道（已完成的前提）；长 Run 续期；加密源；Core 重启；L-R11 gate；UI/App；契约（PREREQ 已冻结）；schema/依赖；真实用户数据；push。

## Acceptance Criteria（草案，释放时冻结）

- [x] **AC-J1 容器 ≥3 成员真实 IPC：每个成员页均可 `AuthorizeSourceReadForRun` 绑定并 `resolve_page_resource`；不可读到未授权成员。** 证据：真实 IPC `Fea11RunGrantIpcTests.ContainerMemberEntriesAuthorizeEveryMemberOverRealIpc`（真实 `multi.zip` / `multi.cbz` 各 3 成员，经生产 scan→cache→range→mint 路径：每个成员页 `authorize → bound_pages=1 → resolve_page_resource` OK；`minted=1` 即一个 grant 覆盖全部成员）；Core 真实装配 `test_container_members_are_entry_granular_on_every_authorized_member[zip|cbz]`（provider 读到**该成员自己的像素尺寸**）；未授权面 `test_container_member_outside_the_signed_entries_cannot_be_read`（scope 少一项 → typed、`commit_guard` 不开、provider 拒绝）+ IPC 的「省略最后成员 → typed 且 resolve typed」。日志 `verification/FEA-11-RUN-GRANT-2/logs/host-ipc.log`、`logs/feature.log`；见证 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\fixtures\ipc-*\run-grant-2b-container-members.txt`。 <<MET>>
- [x] **AC-J2 fail-closed：N 项中任一项 locator/facts/ordinal 不符或 entry 不在 version → 整体 typed、零映射写入；容器替换/generation 漂移/撤销/过期 typed。** 证据：Core 注册矩阵 `test_container_grant_any_bad_entry_refuses_the_whole_grant[unsafe_locator|absolute_locator|negative_ordinal|duplicate_ordinal|other_container|facts_differ]`（全部 typed `SOURCE_ACCESS_DENIED`，grant 未注册、`_bindings` 空、业务表快照不变）+ 协议面 `test_container_grant_violations_are_typed_with_zero_partial_acceptance[...]`；**P3-4** `test_container_grant_facts_reference_point_is_the_container_identity`（成员 digest 冒充容器 facts → typed 拒绝；同形状真容器 facts → 成功）；**P3-5** `test_container_grant_out_of_range_ordinal_never_matches`（越界 ordinal 不命中、整 grant typed）；既有容器替换/撤销/过期用例（RUN-GRANT-1 50 例）全绿。判别性 B1/B2/B4/B5/B6 全 RED 后按字节恢复（`logs/discrimination.log`）。 <<MET>>
- [x] **AC-J3 上限：超过 `max_entries` 或 64 grant 上限 → typed，不截断；≥65 成员容器有明确用例。** 证据：Core `test_container_grant_entry_budget_is_typed_and_never_truncated`（`max_entries=3` 边界接受全部 3 成员；+1 项 → `SOURCE_BUDGET_EXCEEDED` 且未注册；配置预算 20000 时命中实现硬上限 10,000 → 同样 typed）；Host `ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`；真实 IPC：Host mint `max_entries=65` + 66 项 → typed `SOURCE_BUDGET_EXCEEDED`（**不截断**），且 **66 成员容器由 1 个 grant 覆盖、`ordinal=65` 的最后一个成员可授权/可读**（64 = 单次命令 `grant_ids` 上限，**不是**成员数上限，见 P3-6/N-4）。判别性 B3/B8 全 RED。 <<MET>>
- [x] **AC-J4 managed/旧路径零回归；零漂移（pins 18/18、Run wire/minor/schema/依赖零改动）；全量门禁不降；EV/Handoff 不夸大。** 证据：`verification/FEA-11-RUN-GRANT-2/scope-validation.log`（changed=7 全 ALLOWED；`doc/plan`/`doc/contracts`/`schema.py`/迁移/依赖/`NewManga.App`/STATUS/PLAN/LEDGER 全 ZERO_DIFF；`CORE_PROTOCOL_MINOR=3`、Run 授权命令保留）；`logs/gates.log`（PIN AUDIT 18/18 PASS、check 默认 + `-TaskPath` PASS(3 warnings)、API inventory EXIT=0）；全量 pytest 3281/10 → **3305/10**、全量 .NET 1559/0/90 → **1562/0/91**（+3 单测、+1 opt-in IPC skip，不降）；定向 50 → **74**；`logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/feature.log`；Handoff/EV 保留 L-G16/L-G1/L-G2/L-G9/L-G10 等 limitation 与未宣称项。 <<MET>>

## 实现注意（来自 C-16 v1.4 复核 P3，必须在本卡收口）

- **P3-4（facts 参考点）**：注册期「facts = 容器身份」的参考点必须锁定为 Core 权威 source_locations 的四键（volume_serial/file_id/size/sha256），不得由成员内容 digest 或 Host 推断；实现需有判别用例（成员 digest 充当容器 facts → typed 拒绝）。
- **P3-5（ordinal 越界）**：除 ordinal ≥ 0 且唯一外，需判别「ordinal 越界（超出该 version 的 source_entries）」→ 不命中、整 grant typed；Host 不得用越界 ordinal 探测。
- **P3-6/N-4（上限口径）**：max_entries 限制单 grant 条目数、64 限制单次命令 grant_ids 数；实现侧既有硬上限 10000 为更严 fail-closed，须在卡/证据注明，不得表述为「容器成员数上限」。
- **P3-2（wire 追溯）**：C-16 §0 wire 版本行保留历史追溯说明（v1.3 当时登记 1.2、后更正 1.3），实现不改 wire 字段/命令集。

## 依赖与下一步

1. 先完成 `FEA-11-RUN-GRANT-2A`（Host 版本通道）与 `FEA-11-RUN-GRANT-2B-PREREQ-1`（C-16 v1.4）。
2. 两者 done 后由 DSH 复核本卡 scope 是否仍成立（如 Core/Host 形状变化），再冻结/释放实施。

## 交付记录（Owner 回填；不改 status）

- **Owner**：`run-grant-2b-impl`（DSH Agent Teams teammate；Lead `lead`）。
- **交付基线**：卡 `base_commit=97812958d`；实现起点 `5397be149`（`main`，工作树 clean，实测）。
- **实现/测试 commit 链**（显式 pathspec，未 push；均在 `main`）：
  - `7466cb99d` — `feat(fea-11-run-grant-2)`：Core `_parse_scope` 容器 1..N 成员条目（逐项校验 + 零部分接受 + 预算 typed 不截断）+ `_scope_covers_entry` 多 entry 匹配（容器 facts vs `source_locations`、无路径回退）；Host `RunSourceScope.ContainerEntries` + `RunSourceRange` 只对 zip/cbz/pdf 传 Core 权威成员身份 + `SourceReadCoordinator.ContainerEntryPlan`（纯函数、超预算 typed 不截断）+ `IssueLockedAsync` 容器只指纹一次并铸 N 项。
  - `018008989` — `test(fea-11-run-grant-2)`：Core 真实装配多成员矩阵（1..N、facts 参考点、越界 ordinal、重复 locator、预算）、协议面注册矩阵、Host 单测（range 原样传递/plan 预算/authorizer 转发）、真实 IPC（3 成员 zip+cbz、省略/错项 typed、66 成员单 grant 不截断）；**`delivery_head`**。
  - 证据/卡/Handoff 同批文档提交（`verification/FEA-11-RUN-GRANT-2/**`、本卡、`doc/handoffs/FEA-11-RUN-GRANT-2-018008989.md`）。
- **实现落点**：`src/infrastructure/resource_channel/source_read_refs.py`（`_MAX_SCOPE_ENTRIES`、`_parse_scope` 容器分支、`_scope_covers_entry`）；`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`（`RunSourceScope.ContainerEntries`、`ContainerEntryPlan`、`DescribeContainer`、`IssueLockedAsync` 容器分支、`IssueAsync` 透传）；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（`RunSourceRange.Resolve` 传成员身份）。**`src/bootstrap/core_service.py` 零改动**（Run 授权 handler 的 `pages` 已携带 `entry`/`entries`，多 entry 语义只需匹配侧改动）。
- **门禁实测**（`delivery_head=018008989`；均真跑，日志在 `verification/FEA-11-RUN-GRANT-2/logs/`）：`dotnet build NewManga.sln -c Release` **成功 0 warning/0 error**（`build.log`）；定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **74 passed**（基线 50，+24；`feature.log`）；`--filter SourceRegistry` → **32 passed**（基线 29；`host-unit.log`）；`NEWMANGA_FEA11_IPC=1 --filter Fea11RunGrant` → **5 passed**（基线 4；`host-ipc.log`）；全量 `pytest tests` → **3305 passed / 10 skipped**（基线 3281/10；`full-pytest.log`）；全量 `dotnet test NewManga.sln -c Release` → **1562 / 0 / 91**（基线 1559/0/90；`full-dotnet.log`）；`verify_pins` **18/18 PASS**、`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**、`generate_api_inventory.py --check` **EXIT=0**（`gates.log`）；scope **PASS（changed=7 全 ALLOWED；zero-drift 全空；minor=3）**（`scope-validation.log`、`changed-files.txt`）；判别性 **8/8 破坏点 RED_AS_EXPECTED + 8/8 字节级 RESTORED + final rebuild EXIT=0 + 恢复后定向套件绿**（`discrimination.log`）。跑后均 `git checkout -- verification/FEA-09`（全量 .NET 命中重写，已恢复；全量 pytest 未命中）。
- **未运行项**：无（上述门禁全部实跑）。**已知 flaky 未命中**：`FluentResidual2VisualEvidenceTests`（证据目录同时写入时的 git-status 快照竞态）本次全量 .NET 未触发。
- **证据索引**：`verification/FEA-11-RUN-GRANT-2/EV.md`（结论/AC 矩阵/逐文件 sha256）、`logs/`（8 个日志）、`scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`（仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2\` 聚合 sha256 + `delivery_head`）、`tools/`（4 个可复现脚本）。
- **不夸大**：本卡只闭环「容器成员 entry 授权通道」（L-G12② 在**缓存可用的容器源**上闭环）；folder **>4096 成员不入缓存**（L-G16）、长 Run（L-G1）、加密源（L-G2）、Core 重启（L-G9）、L-R11（L-G10）**均不解决**；**L-R1 未全修**；不得表述为「referenced Run 全场景可用」。`status` 未改，等待 Lead 指派独立 Review 与集成门禁。

## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 Review r1 `doc/reviews/FEA-11-RUN-GRANT-2-r1.md`（fresh subagent `35d102d4-…`；reviewed_head `018008989`）：**approved，P0=0/P1=0/P2=0/P3=4**；AC-J1…J4 全 MET；自选 2 个破坏点（Host 重编号 ordinal / 删除 image 单 entry 守卫）独立 RED + 逐字节恢复；C-16 v1.4 §2 逐条 PASS。
- **P3-01（口径）**：容器 facts 约束分两层——注册期仅证明 N 项 facts 彼此相同（registry 无 DB 句柄），**逐页授权期**由 `_location_matches` 与 Core `source_locations` 权威比对；成员 digest 冒充容器 facts 的 grant 可注册但永不能授权（typed、零映射）。已在 EV 与本节登记「注册=同一性；授权=权威性」。
- **P3-02（EV 措辞，已修）**：改为「全量 .NET 重写并恢复；全量 pytest 未命中（`unchanged`）」。
- **P3-03（owner 署名，已修）**：卡面 `owner` 由 `run-grant-impl` 统一为实际实现者 `run-grant-2b-impl`。
- **P3-04（可选加固，follow-up）**：容器重名成员 + 冻结 OR 匹配的「同名子集 grant」窄角；生产 Host 总铸全量权威列表（产品路径无暴露），IPC 负例用不同 locator 未覆盖；**不改冻结语义**；建议另立小卡（Host 用 Core `EntryId` 作 `entry_key` + 同名子集判别用例）。
- **不改变** AC-J1…J4 MET 判定、实现/测试字节（`018008989`）与 r1 approved 结论。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-J1…J4 | verification/FEA-11-RUN-GRANT-2/EV.md | 2d69d0624 | 9c5a2d2579fd4ad56f7d21e090317dae5cd968d7925a323f0d6beb44334d432f | CANONICAL |
| EV-02 | AC-J1…J4 | doc/reviews/FEA-11-RUN-GRANT-2-r1.md | 2d69d0624 | 89e6bf16002d3ef0c287393af02662a1c92d25bf04a36be5904cb06215abfee5 | CANONICAL |
| EV-03 | AC-J4 | doc/handoffs/FEA-11-RUN-GRANT-2-018008989.md | 3dc822b77 | 92027aa8f61e17f111157f59fba3d98af7c128f8589bf1961c906a6fbe72c892 | CANONICAL |

> 证据树其余 15 个文件（logs 8、tools 4、Manifest、changed-files、scope-validation.log）逐文件 sha256 见 EV §5（15/15 与工作树一致，Review r1 独立复算）；本表只列 closeout 层新增/重签项。

## Resource Manifest

`verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json`

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `0180089894b2286d8ff6a94289b84dd318871d18`（实现 `7466cb99d` + 测试 `018008989`；证据/卡/Handoff 文档提交 `3dc822b77`/`8e1883655`）。
- **AC 判定**：AC-J1…AC-J4 **全 MET**；无 PARTIAL/BLOCKED。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=0/P3=4）**；P3-01 口径登记、P3-02 已修、P3-03 已统一、P3-04 登记 follow-up。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3281/10 → 3305/10**；全量 .NET **1559/0/90 → 1562/0/91**；定向 python **50 → 74**；SourceRegistry **29 → 32**；真实 IPC **4 → 5**；pins **18/18**；check（默认 + `-TaskPath`）PASS(3w)；API inventory PASS；scope **changed=7 全 ALLOWED**，zero-drift 全空，`CORE_PROTOCOL_MINOR=3`；判别性 **8/8**；跑后 `git checkout -- verification/FEA-09`。
- **limitations（保留）**：L-G16、L-G1、L-G2、L-G8、L-G9、L-G10、L-G11、L-G13、L-G14；L-G12② 的容器成员面已闭环（≤4096 成员缓存可用容器源），但 **L-R1 未全修**；P3-04 同名成员子集语义为冻结 OR 匹配固有行为（另卡可选加固）。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2/`（IPC 夹具/门禁日志/复核备份，无独有产品数据）→ `PRESERVE_REFERENCED`；Manifest 已披露 generation-time snapshot 与 integration/ 排除。
- **指针清理**：STATUS 当前 Task → 无活动 Task；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件/后续回填）。
