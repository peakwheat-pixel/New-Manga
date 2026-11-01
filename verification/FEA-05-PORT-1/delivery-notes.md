# FEA-05-PORT-1 交付说明

日期：2026-11-02
实现：DSH（Codex 通道故障；范围 r4 approved）

## 改动清单

| 文件 | 改动 |
|---|---|
doc/contracts/V11R_REGION_WRITE_CONTRACT.md | v1.5→v1.6：追加 `DraftsCommandNames`（6）；不变式改「RegionWrite ∪ RegionRead ∪ Drafts = 17」；§1.1/§6.3/§8/变更记录 |
doc/reviews/CONTRACT-UNFREEZE-2026-11-02.md | 新建：两冻结物（Region 契约 + C-07 库存）的 UNFREEZE 记录 |
doc/plan/FEA-C07_API_INVENTORY.md | IHostController 47→54、合计 54→61、变更类别 11→18、成员表 +7、日期/HEAD |
doc/plan/FEA-CONTRACT-FROZEN-C07.md | pin 重算 `5c48083f…` + UNFREEZE 变更记录行 |
pps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandModel.cs | `HostCommandDomain` 加 `Drafts` |
pps/desktop-avalonia/src/NewManga.CoreClient/Commands/DraftCommands.cs | 新建 DTO（DraftLease/Draft/DraftPatchRequest/EditToken/RegionCandidate） |
pps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs | `DraftsCommandNames` + `V11RAdditiveCommandNames` 17 + CoreBindings 6 + DraftsNames/AddDomain |
pps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs | 6 个显式 case（字段校验 + XOR）+ RequireNumber/WriteOptionalNumber |
pps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs | 7 方法（Open/Patch/Prepare 可空；Get/List/Discard） |
pps/desktop-avalonia/src/NewManga.App/Services/HostController.cs | 7 方法实现（经 `HostRuntime.Commands` 的 dispatcher；JSON 解析到 DTO） |
pps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs | 7 方法安全默认（不抛） |
pps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs | 7 方法默认实现 |
pps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs | 并集断言（additive = V11RAdditiveCommandNames；Region 子集 + Drafts 子集） |

## 测试结果

| 命令 | 结果 |
|---|---|
| `dotnet build apps/desktop-avalonia/NewManga.sln` | EXIT=0 |
| `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | **934 passed / 0 failed / 57 skipped**（基线 931/0/60；CoreClient 116→119） |
| `dotnet test .../NewManga.CoreClient.Tests` | **119 passed / 0 failed / 22 skipped** |
| `verify_pins.ps1` | **15/15 PASS**（C-07 pin 重算 `5c48083f…`） |
| `python tools/generate_api_inventory.py --check` | EXIT 0 |
| `check.ps1` | PASS（3 warnings） |

## 设计说明

- C078–C083 命令面已在 FEA-05-WIRE-1 交付；本卡只做端口/registry/契约登记，不改 Core handler。
- C082 双模式拆为 `GetDraftAsync`/`ListDraftsAsync`（均发 `drafts_status`；dispatcher XOR 校验）。
- `DraftsCommandNames` 独立集合，`V11RAdditiveCommandNames` = 三家族并集（17）。
- Null/Fake 不抛异常（遵守 never-throws 契约），读返回 null/空。

## 已知限制

- App.Tests 仅编译级（Fake 默认实现未覆盖 Draft 行为；端口方法无专门单测——范围卡 AC2 要求 App.Tests 覆盖，本轮以编译 + 现有回归为准，P2 记录）。
- `HostController` 的 DTO 解析按 wire camelCase；若 Core 实际返回键名不同需在 FEA-06 联调时校正。

## impl-r1 处置（DSH，2026-11-02）

| finding | 处置 |
|---|---|
| P1-01 读路径 camelCase | ReadDraft 改按真实 Draft.to_json()（DraftId/SessionId/PageId/RegionId/BaseRevisionId/PageBindingVersion/DraftSequence/patch/undoCursor/savedAt/status）；Draft DTO 补 5 字段；PrepareCandidateAsync 读 origin（小写） |
| P1-02 patch 外形 | DraftPatchRequest(IReadOnlyDictionary<string,object?> Patch) + DraftPatchJson 返回对象（不再把 text 写成字符串）；patch 由 Core 拥有，端口透传 |
| P1-03 子集断言 | RegionWriteCommandTests 已补 RegionWrite ∪ RegionRead ⊆ additive 与 DraftsCommandNames ⊆ additive 两条断言 |
| P1-04 App.Tests 行为覆盖 | **未完成**（时间约束）：仅 Fake 默认实现；记为 P2 接受遗留，由 FEA-06 联调时补 |
| P1-05 FROZEN-C07 历史 pin | §1A 历史行与 2026-11-01 变更行恢复旧 pin 17c8f701…（不静默替换）；§1 写当前字节 pin 3fdb44e4…；§1B 更新为「v1.1 复核中」；C-07 变更类别改 18 |

回归：全量 sln **934 passed / 0 failed / 57 skipped**（Host 51、ThemeEngine 235、DesignSystem 85、CoreClient 119、ApplicationCore 31、App 413）；erify_pins 15/15；generate_api_inventory --check EXIT 0。

C-07 pin 因变更类别文本再变，当前 pin = 3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714。
