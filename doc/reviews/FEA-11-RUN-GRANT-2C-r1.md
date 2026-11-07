---
task: FEA-11-RUN-GRANT-2C
title: 2C 长 Run 续期实现独立 Review r1（Host-only 周期重铸 + 重发 AuthorizeSourceReadForRun；C-06 v1.3 / C-16 v1.6）
reviewer: fresh subagent（独立上下文；session 361bfbe0-7cff-46c5-8fbe-dccf952de727；未参与本卡实现/返修/scope review/契约前置；只读）
session: 361bfbe0-7cff-46c5-8fbe-dccf952de727
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_independent_impl_review
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: e5e9c4c52
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C 独立实现 Review r1

## 结论先行

- **verdict = `changes_requested`（P0=0 / P1=1 / P2=1 / P3=5）。**
- 实现语义按静态审查成立：Run 非终态期间对**同一冻结** `{command, scope}` 每轮**新铸** grant（新 id、`expires_at=_clock()+300`）并重发 `AuthorizeSourceReadForRun`；不延长旧 grant、不扩 scope、每轮重走 `Registry.Authorize` + 物理 facts；typed 拒绝/全 skip/终态/轮次上限/单轮预算/Host 关停均 fail-closed 停止；零 Core、零 Run wire、零 App、零 `+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 改动。
- 我独立实跑均 PASS：build 0/0；13 单测；回归 32/0/7；gated 7/0/0；fake-clock 3 例；定向 pytest 92；pins 18/18；check（默认+`-TaskPath`）；API EXIT=0；证据 sha 19/19。
- **唯一阻断项 P1-01（关键验证缺失，非代码缺陷）**：HostRuntime 续期接线（`RunDispatchedAsync` / `MaybeStartRunGrantRenewal` / `RenewRunGrantsAsync` / `ProbeRunLivenessAsync`）**没有任何测试**。我把 `_runGrantRenewal` 恒置 `null`（整个功能关闭）后，全量 Host **277/0/65 EXIT=0**、gated **7/0/0 EXIT=0**，无一条测试变红。gated 的 `renewal-ipc.json` 是测试直接连调 `coordinator.AuthorizeRunAsync` 两次，**不经过 Host 续期循环**；AC-2C-1 要求的「删续期 → `PROVIDER_FAILED`/`DB_FAILED` RED」未以生产接线路径被判别。
- **P2-01（预算语义）**：`RoundBudget=50s` 在 `_renew` 返回**之后**才检查（`RunGrantRenewal.cs:348-355`）；单轮可包含最多 8×30s 的 on-demand 扫描（`HostRuntime.cs:2164,2167,2378,2395`）+ mint，可能越过旧 grant 的 300s 窗口并长时间占用 `_gate`，与 scope D-4b「超预算即跳过、不得长期占住 mint gate」和 EV「不长期占用 mint gate」不符（仍 fail-closed，但连续性会断）。
- **不夸大口径 PASS**：L-G1 只降级不关闭在卡/Handoff/EV 一致；未发现「任意长 Run 可用 / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」表述。

## 基线与只读事实

| 项 | 值 | 来源 |
|---|---|---|
| HEAD / branch | `7c979f18d` / `main` | 实测 |
| delivery head | `e5e9c4c52`（实现 `c40489b5d` + 测试 `e5e9c4c52`） | `git rev-parse 7c979f18d^` |
| 证据 head | `7c979f18d`（`e5e9c4c52..7c979f18d` 仅 docs/evidence：21 文件 +2013/−9） | `git diff --stat` |
| 工作树 | **clean**（评审开始/破坏恢复后/结束均 0 行）；`verification/FEA-09` 无残留 | `git status --porcelain` |
| 交付 8 文件 | `RunGrantRenewal.cs`（新）+ `HostRuntime`/`HostOptions`/`SourceReadCoordinator`/`HostCommandDispatcher` + 3 测试文件 | `git diff --name-status c5f1b416f e5e9c4c52` |

## A–I 逐项核对

| 项 | 判定 | 依据（实测/字节） |
|---|---|---|
| **A 续期主 AC** | **FAIL（P1-01）** | 时间维 Python before/after 成立（`tests/fea11/test_source_run_grant.py:774-806,810-857`：窗口后读 `ProviderInputError`、提交 `SOURCE_ACCESS_DENIED` 零业务写；手工续期后读/提交恢复、旧 grant 仍 `SOURCE_GRANT_EXPIRED`）。但 Host 续期循环未被执行：gated `RenewalMintsAndRebindsTheSameScopeTwice`（`Fea11RunGrantIpcTests.cs`）直接调 `coordinator.AuthorizeRunAsync` 两次；Probe-C 关闭 `_runGrantRenewal` 后全量 Host + gated 全绿。卡面判别「删续期 → PROVIDER_FAILED/DB_FAILED RED」未以 Host 路径判别。 |
| **B 不延长/不扩 scope/不改 command** | PASS | 每轮 `IssueLockedAsync` 新 GUID + `expiry=_clock()+300`（`SourceReadCoordinator.cs:602-633`），旧 payload 不写；单测 `Renewal_NeverWidensTheFrozenCommandOrScope`（`RunGrantRenewalTests.cs:93-115`）；gated 两帧 `command`/`scope.GetRawText()` 相等、`new_grant_id=true`；EV 断言旧 grant 仍过期。 |
| **C 撤销/漂移即停** | PASS（P1 证据缺口） | 每轮 `RenewRunGrantsAsync → AuthorizeSliceAsync`（`HostRuntime.cs:1626-1656,2294-2362`）→ `AuthorizeRunAsync` 逐源 `IssueLockedAsync` → `Registry.Authorize`×3 + facts（`SourceReadCoordinator.cs:515-601`）；单测 typed 停止不重试（`RunGrantRenewalTests.cs:122-167`）；Python 不同 scope/command typed 且零映射（`:860-913`）。真实 registry 撤销/换代经生产接线停止的路径无测试（并入 P1-01）。 |
| **D 失败不放行/不自动重试** | PASS | 任一非 `Renewed` → `Stop` 并移除（`RunGrantRenewal.cs:357-397`）；Core `authorize_run_bindings` 任一页拒绝整请求 typed、零映射（`src/infrastructure/resource_channel/source_read_refs.py` `authorize_run_bindings`）；gated `reattest_frames=0`、registry 结构不变；不新建 Run、不 reattest。 |
| **E 预算/间隔/轮次** | PASS（P2-01） | 默认 interval=240/max=12/budget=50；`Normalize` 只接受 240..249 与 1..100（`RunGrantRenewal.cs:89-137`）；`240+50<300` 单测断言；`_gate` 串行 mint（`SourceReadCoordinator.cs:283`）；超预算/轮次上限/终态 typed 停止 + `_stops` 计数；不并行绕 gate。预算检查是事后判定（P2-01）。 |
| **F 接线/无 App/零 wire/既有值不变** | PASS（P1 证据缺口） | dispatcher 新增 `runAuthorizeWithResult` + `runDispatched`（`HostCommandDispatcher.cs:71-93,173-225`，Host 内部，无 wire 字段）；`HostRuntime` 两入口启动（`HostRuntime.cs:86-101,1231-1253,1550-1624`）；App 零 diff；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 零改动（diff 仅新增 `LedgerStatus`）。接线无判别测试（P1-01）。 |
| **G 不夸大/L-G1 只降级** | PASS | 卡 `:55/61/75`、Handoff `:59-65`、EV `:4-6,101-112` 固定「有续期 + 子限制」并保留单步 >300s/续期失败/L-G2/L-G9/L-R1/L-G16/未 dispatch pending；无禁止词。STATUS 尚未更新（`doc/STATUS.md:7` 仍写 ready），属 Lead closeout，不判 FAIL。 |
| **H 独立实跑** | PASS | 见下表；build 0/0、13/0/0、32/0/7、7/0/0、fake-clock 3、92、pins 18/18、check×2 PASS(3w)、API 0；自选 2 破坏点均 RED 并逐字节恢复 sha；另加 1 个非 RED 覆盖探针（Probe-C）。 |
| **I 证据/判别性/scope** | PASS（P3 卫生） | manifest 19/19 sha 实测一致；`discrimination.log` 7/7 的原始/复原 sha 与当前两文件一致且脚本逐例复原；delivery 29 文件 ⊆ allowed_paths、`src/**` 与禁止面零 diff、C15/C17 blob 零漂移、`PROTOCOL_MINOR=3`、卡 `status: ready` 未变；gated JSON 与入库证据 sha 逐字节相同（`0BDE5BE4…`）。P3：manifest 含 ignored `__pycache__/*.pyc` 且 `repo_head_at_generation=6d3db3b04` 已被 amend 成孤儿。 |

## AC-2C-1…8 判定

| AC | 判定 | 说明 |
|---|---|---|
| AC-2C-1 续期主 AC | **FAIL（证据）** | 实现正确；生产接线无判别用例，卡面「删续期 → PROVIDER_FAILED/DB_FAILED RED」未满足（P1-01）。 |
| AC-2C-2 不延长/不扩/不改 | PASS | 新 id、旧 `expires_at` 不变、command/scope 同值（单测 + Python + gated）。 |
| AC-2C-3 撤销/漂移即停 | PASS | 每轮重走 Authorize+facts；typed 停止不重试；真实接线路径无测试（并入 P1-01）。 |
| AC-2C-4 失败不放行/不自动重试 | PASS | typed/异常/全 skip → 停止；Core 整请求原子拒绝；`reattest_frames=0`。 |
| AC-2C-5 预算/间隔/轮次 | PASS（P2-01） | 配置满足 240+50<300；`_gate` 串行；上限/预算/终态停止；预算为事后检查。 |
| AC-2C-6 接线/无 App | PASS（P1 证据缺口） | 代码接线、零 wire、零 App、既有值不变均在；无接线判别测试（P1-01）。 |
| AC-2C-7 不夸大 | PASS | 只降级不关闭，子限制清单完整。 |
| AC-2C-8 门禁 | PASS | pins 18/18、check×2、API、scope、全量日志数字均核；全量套件为 Lead/日志口径（我未重跑全量）。 |

## 独立实跑

| 场景 | 命令（摘要） | 结果 |
|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error** |
| 续期单测 | `--filter FullyQualifiedName~RunGrantRenewal` | **13/0/0 EXIT=0**（恢复后复跑同） |
| 回归 | `--filter "SourceRegistryTests|Fea11RunGrantIpc"`（无 gated env） | **32/0/7 EXIT=0** |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 --filter Fea11RunGrantIpc` | **7/0/0 EXIT=0**；新 fixture 的 `renewal-ipc.json` 与入库证据**逐字节相同**（sha `0BDE5BE4…`）：2 轮、new grant、`bound_pages=1`、页可读、wire 无路径、`reattest_frames=0` |
| fake clock | `pytest tests/fea11/test_source_run_grant.py -q -k "after_the_window or past_the_window or never_rebinds"` | **3 passed, 27 deselected** |
| 定向 pytest | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **92 passed** |
| pins | `verify_pins.ps1` | **PASS (all 18) EXIT=0**（C06 `75f8e2b4…`、C16 `b8f46fb1…`） |
| check | 默认 + `-TaskPath` | **PASS (3 warnings) ×2 EXIT=0** |
| API | `generate_api_inventory.py --check` | **EXIT=0** |
| 全量（Lead/日志口径，我未重跑） | pytest / .NET | 日志汇总 **3363/10**、**1674/0/96**，与任务书一致；日志 `EXIT=0` |

## 破坏性复跑（先备份字节，结束逐字节恢复 + sha 复核）

| # | 破坏点 | 目标测试 | 结果 | 恢复 |
|---|---|---|---|---|
| BR-A | `MaximumIntervalSeconds` 300−50−1 → 300−50（允许 250，`interval+round=300`） | `Renewal_Options_NormalizeIllegalValues_AndKeepTheContractBound` | **RED EXIT=1**（"interval 250 must fall back"） | sha `63517CCB…` MATCH=True |
| BR-B | `IsTerminalRunStatus` 删除 `"interrupted"` | `Renewal_TerminalStatusVocabulary_IsTheFrozenRunStateSet` | **RED EXIT=1**（"interrupted"） | sha `63517CCB…` MATCH=True |
| **Probe-C**（非 RED 覆盖探针） | `_runGrantRenewal = CreateRunGrantRenewal()` → `= null`（功能整体关闭） | 全量 `NewManga.Host.Tests` + gated `Fea11RunGrantIpc` | **GREEN 277/0/65 EXIT=0；7/0/0 EXIT=0** ⇒ 无测试覆盖接线（P1-01） | `HostRuntime.cs` sha `FCE654B8…` MATCH=True；重建 0 error |

备份位于 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\review-r1\`；未写 `verification/FEA-09/**`；结束 `git status` 0 行。

## Findings

| ID | 级别 | 位置 | 问题与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R2C-01 | **P1** | `HostRuntime.cs:1550-1700`；`RunGrantRenewalTests.cs`/`Fea11RunGrantIpcTests.cs` | 续期生产接线无任何判别测试：`RunDispatchedAsync`/`MaybeStartRunGrantRenewal`/`RenewRunGrantsAsync`/`ProbeRunLivenessAsync` 无引用；gated「续期轮」直接调 coordinator，不经过 Host 循环。AC-2C-1 的「删续期 → `PROVIDER_FAILED`/`DB_FAILED` RED」未成立；未来删除/改坏该接线不会被任何测试发现。 | Probe-C：功能置 null 后 277/0/65 + 7/0/0 全绿；`grep` 0 命中；gated 测试实现见 `Fea11RunGrantIpcTests.cs:1345` | 增加 1 个 HostRuntime/dispatcher 级判别用例（可用 `HostOptions.RunGrantRenewalTimeProvider` 或可注入 seam），在接线被删/`_runGrantRenewal=null` 时 RED；或在 `RunGrantRenewalTests.cs` 内测 post-dispatch 钩子与 Host 委托；同步补 EV AC-2C-1/6 证据。 |
| R2C-02 | **P2** | `RunGrantRenewal.cs:323-355`；`HostRuntime.cs:2164,2167,2378,2395` | `RoundBudget=50s` 是 `_renew` 返回后的**事后**判定；单轮可先执行最多 8×30s on-demand 扫描 + mint，再被判超预算停止。可能越过旧 grant 的 300s 窗口并长期占用 `_gate`，与 scope D-4b「超预算即跳过」/EV「不长期占用 mint gate」不一致（仍 fail-closed）。 | 代码路径；EV §5 第 5 条；scope §2.1/D-4b | 在 mint/扫描循环内加 deadline 预检（超预算即 skip 当前 source/轮次），或把真实最坏值写入 EV 子限制并修正「不长期占用」措辞。 |
| R2C-03 | P3 | `RunGrantRenewal.cs:348-360` | 预算超限分支先于 `!outcome.Renewed` 与 `_renewals++`：一次已成功 mint 的轮次被记为 `StoppedBudget`，且吞掉更重要的 typed stop code（诊断口径）。 | 单测只断言 Budget 停止，未断言已 mint/code | 先判 typed 结果再判预算，或保留原始 code；计数区分「minted-but-stopped」。 |
| R2C-04 | P3 | `HostRuntime.cs:1626-1656` | 真实 `RenewRunGrantsAsync` 把全 skip 折叠成 `RENEWAL_NO_TARGETS`/`RENEWAL_NOT_AUTHORIZED`，丢失 `SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_BUSY` 等 §6 code；单测的 `SOURCE_GRANT_REVOKED` 来自 fake delegate。 | `RenewRunGrantsAsync` 代码；`RunGrantRenewalTests.cs:122-148` | 保留 counts-only 的首个 typed skip code 进 `Status.LastCode`/日志。 |
| R2C-05 | P3 | `HostRuntime.cs:1595-1624`；`SourceReadCoordinator.cs:117` | `MaybeStartRunGrantRenewal` 在 `authorization=null`/`runId` 为空时也打 "bound_pages=0"；`LedgerStatus()` 无任何调用者/测试（EV「ledger 可观测」未落地）。 | `grep LedgerStatus` 0 调用 | 修正日志措辞；删除或把 LedgerStatus 接入 `RunGrantRenewalStatus`/测试。 |
| R2C-06 | P3 | `doc/handoffs/FEA-11-RUN-GRANT-2C-e5e9c4c52.md:48-50`；`verification/.../EV.md:56,63` | Handoff 仍有 `TBD-FULL-DOTNET`/`TBD-GATES`/`TBD-SCOPE`，EV 仍有 `TBD-FULL-DOTNET`（但日志/AC-8 已有 1674/0/96、PASS）；EV `:63` 含字面 `\n`。 | 日志 `full-dotnet.log` 合计 1674/0/96；`gates.log` PASS | Lead 在集成 docs 提交一次补齐数字并修 `\n`；不涉实现字节。 |
| R2C-07 | P3 | `verification/.../RESOURCE-MANIFEST.json:11,145`；`doc/plan/FEA-CONTRACT-FROZEN-C16.md:51` | manifest 含 ignored `tools/__pycache__/*.pyc`（clean clone 不存在、不可复现）；`repo_head_at_generation=6d3db3b04` 已被 amend 成孤儿（7c979f18d 同消息）；FROZEN-C16 §2 第 8 行仍 `⏳`，与载体处置 6「→✅」不符（PREREQ 记录，非 2C 字节）。 | 实测 sha；`git branch --contains 6d3db3b04` 空；`git show 7317837d5:` 行 | 重生成 manifest 排除 `__pycache__`；Lead 修 FROZEN-C16 状态格（docs-only，不动契约字节）。 |

## 结论与复审

- **可交 DSH 处置：`changes_requested`。** 实现本身（P0=0）按静态审查正确，未发现放行/扩权/延长 TTL/绕过撤销/新增 wire；阻断仅因 **AC-2C-1/6 的生产接线没有判别证据（P1-01）**，需补 1 个 HostRuntime/dispatcher 级测试或等价 seam 判别后再判 `approved`。
- 若 DSH 判定 P1-01 属可接受的冻结 scope 裁剪（最终 `allowed_paths` 未含 `SourceRegistryTests.cs`），则本报告的可批准残余为 P2-01 + P3×5；但 AC-2C-1 的「删续期 → `PROVIDER_FAILED`/`DB_FAILED RED`」仍应在其裁决中显式记录为 NOT_RUN/limitation，不得按 MET 计。
- 复审以新 head 增量复核 R2C-01 的测试判别 + R2C-02 的预算处置；其余 P3 可在集成 docs 提交一次性闭环。

## 真实性声明

1. **唯一写入**：本报告 `doc/reviews/FEA-11-RUN-GRANT-2C-r1.md`；未改实现/测试/证据/卡/契约，未 `git add/commit/push`；破坏性复跑前已备份至 `.workspace/FEA-11-RUN-GRANT-2C/review-r1/`，每例逐字节恢复并 sha 复核（见上表），结束工作树 clean、`verification/FEA-09` 无残留。
2. **独立性**：本会话为父会话 `session-5f1e719c…` 派发的 fresh subagent（`session 361bfbe0…`），未参与本卡实现、返修、scope review 或 PREREQ-1；只读 `e5e9c4c52` 实现/测试字节与 `7c979f18d` 证据字节。
3. **实测/未跑**：build、13 单测、32/0/7 回归、gated 7/0/0、3 例 fake-clock、92 定向 pytest、pins、check×2、API、2 个 RED 破坏点 + Probe-C 为本会话实测；**全量 pytest/.NET 未重跑**（采用任务书 Lead 门禁 + 入库日志汇总，已核数字）；未做真实 300s 墙钟、真实用户数据、`git push`、契约 byte-level 重审（pins/固定字节比对承担）。
4. **口径**：L-G1 只降级不关闭；本报告不声称 L-G1 关闭、任意长 Run、Run 全面恢复、自动恢复、自愈、自动重新授权或撤销后放行。
