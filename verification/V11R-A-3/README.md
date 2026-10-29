# V11R-A-3 证据包：66 命令契约包（DTO/错误码/样例/minor 兼容）

- Task：`V11R-A-3`（`doc/tasks/V11R-A-3.md`）
- Owner：`core-bridge`（DSH teammate）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 基线 commit：`c73239999`（含 Lead 裁定的 main 已合入）
- 交付 commit：见本证据 commit 的父 commit（Handoff 钉 SHA；本 README 随证据提交）
- 契约文档：`doc/contracts/V11R_COMMAND_CONTRACT_V1.md`（`ISSUED`，独立 Reviewer 待指派）
- 状态：AC1–AC6 已交付并有真实执行证据；Owner 未自审。

## 1. 交付内容

| 文件 | 说明 |
|---|---|
| `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` | C001–C066 逐条签发（域/路由/通道/minor/入参/结果外形/错误码族/UI 消费者/状态/源码引用+样例）；§5 错误码族源码定位；§6 缺口清单；§7 `library_start_run` minor 兼容结论 + 实测探针；§8 C067–C076（+C077 占位）PENDING；§9 已知偏差。 |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandContractV11RTests.cs` | **新增独立测试**（6 条），不修改 `CommandParityContractTests`/`CommandWiringB1/B2Tests`/`CommandIntegrationTests`（Lead 裁定：66→76 改造归 core-writer）。 |
| `verification/V11R-A-3/tools/extract_contract_facts.py` | 从 CSV + Registry + Dispatcher + core_service.py + 既有 verification 证据提取 66 行事实（行号、channel、minor、样例），可复跑。 |
| `verification/V11R-A-3/tools/build_contract_doc.py` | 由 facts 机械生成契约文档（防止手写漂移）。 |
| `verification/V11R-A-3/tools/probe_start_run_minor.py` | AC5 minor 兼容探针（冻结 sidecar + BOOK-FIXTURE 副本）。 |
| `verification/V11R-A-3/contract-facts.json` | 66 行提取事实（供审计/复核）。 |
| `verification/V11R-A-3/minor-compat/start-run-minor-probe.json` | 四条 StartRun 的原始请求/响应。 |
| `verification/V11R-A-3/logs/` + `trx/` | 构建/测试日志与 TRX。 |

## 2. AC 覆盖

| AC | 结论 | 证据 |
|---|---|---|
| AC1 逐条覆盖 C001–C066：前端命令/路由/通道/minor/入参/结果外形/错误码集/UI 消费者/状态（FROZEN/PARTIAL/GAP） | PASS | 文档 §4 六域表；`contract-facts.json` |
| AC2 每条 FROZEN 有源码引用（文件+行）+ 至少一个样例（请求/响应 JSON 或测试断言） | PASS | 表内"源码引用 · 样例"列；FROZEN 49 条全部带 `registry:<行>` + Dispatcher/Core 行 + 样例文件/断言路径；PARTIAL 行也保留样例参考 |
| AC3 不可核实保持 PARTIAL/GAP 并写缺口；禁止把"透传"写成"已冻结" | PASS | **FROZEN 49 / PARTIAL 17 / GAP 0**；§6 逐条缺口；透传读（C001/C003/C007/C010）一律 PARTIAL |
| AC4 补强 parity：注册命令全部有契约断言（含参数特判与 minor 预期），不硬编码 66 | PASS | `CommandContractV11RTests` 6 条：派生 `HostCommandRegistry`；基线 66 行解析；declared⊆registry；core minor 相等；registry⊆baseline∪PENDING（66→76/77 不破）；PENDING 不入 FROZEN |
| AC5 `library_start_run` minor=3 vs Core minor 2.6 overrides 兼容结论 + 验证方法 | PASS | 文档 §7；`minor-compat/start-run-minor-probe.json`（实测 a/b/c/d 四变体） |
| AC6 证据 | PASS | 本目录 + 日志 |

## 3. 契约状态分布（诚实口径）

- **FROZEN 49**：注册表绑定 + Dispatcher 参数约束（或 Core 严格 key 集校验）+ Core 源码行 + 至少一个真实成功样例/测试断言。
- **PARTIAL 17**：C001/C003/C007/C010（Dispatcher 透传读、结果未在 C# 类型化）；C008/C012（仅错误样例）；C014/C039/C062（Host-local 无自动化成功样例）；C016–C019/C022/C027/C030/C041（有 Dispatcher 约束 + Core 源码 + 集成 basis=success 请求，但无响应外形样例）。
- **GAP 0**：无未绑定命令（registry 66/66 均已绑定）。
- 状态语义已在文档 §1 明确：`FROZEN` **不等于**"所有错误分支已运行验证"；错误码族为源码定位集合（§5），逐条运行验证列入后续补证（A-4 快照 CI 建议）。

## 4. 测试（真实执行）

`CommandContractV11RTests`（`tests/NewManga.CoreClient.Tests`）：

1. `BaselineRows_CoverC001ToC066_AndEveryCommandExistsInRegistry` — 66 行、ID 连续、命令唯一、declared⊆registry、通道一致。
2. `DeclaredCoreRows_KeepTheRegisteredProtocolMinor` — 每条 core 行 minor 与 `HostCommandRegistry` 相等（3/7/8/10）。
3. `RegistrySurface_IsFullyDeclared_WithoutHardcodingTheTotal` — `registry ⊆ baseline ∪ PENDING`；注册表不得小于签发基线；**不硬编码 66/76**。
4. `PendingIncrements_StayPending_AndNeverEnterTheFrozenSet` — C067–C077 状态为 `PENDING(...)`，与 FROZEN 集合无交集；若已注册则必须 Implemented。
5. `EveryBaselineRow_HasStatusAndSourceEvidence` — 每行状态合法、证据含 `registry:` 与样例；FROZEN+PARTIAL+GAP=66。
6. `LibraryStartRun_MinorCompatibilityConclusion_IsPresent` — 文档含 `library_start_run`/`provider_profiles`/`minor=7`/探针路径。

```
cd apps/desktop-avalonia
dotnet test tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --no-build \
  --filter "FullyQualifiedName~CommandContractV11R" --logger "console;verbosity=minimal"
# 通过: 6, 跳过: 0 → EXIT=0
```

## 5. 质量门（命令 / exit code / 结果）

| # | 命令（工作目录 `apps/desktop-avalonia`） | exit | 结果 | 证据 |
|---|---|---:|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `logs/build.log` |
| 2 | `dotnet test .../NewManga.CoreClient.Tests --filter CommandContractV11R` | 0 | 6/6 PASS | `logs/dotnet-test-command-contract.log`, `trx/command-contract-v11r.trx` |
| 3 | `dotnet test NewManga.sln --no-build`（整解） | 0 | 见 `logs/dotnet-test-full.log` 末行（App/Host/CoreClient 全绿） | `logs/dotnet-test-full.log` |

环境：`NEWMANGA_CORECLIENT_SIDECAR_DIR=task-envs/HOST-CORECLIENT-1/sidecar-copy`、
`NEWMANGA_BOOK_FIXTURE_ROOT=task-envs/BOOK-FIXTURE-1/isolated-data`、`NEWMANGA_EVIDENCE_DIR` 指向一次性目录（避免污染仓库）。

## 6. AC5 结论（摘要）

**当前命令路径无法通过 `overrides.provider_profiles`**：`library_start_run` 注册 minor=3，Core
`StartRun` 在 `provider_profiles` 出现时要求请求 minor=7（`core_service.py:3283-3284`，`_P15_PROTOCOL_MINOR=7`），
Host Dispatcher 不改 minor。实测（同一有效 book scope，BOOK-FIXTURE）：

| 变体 | minor | overrides | 实测 |
|---|---:|---|---|
| a | 3 | provider_bindings | 成功 `run_id=run-44e5…, status=pending` |
| b | 3 | provider_profiles | `INVALID_REQUEST`（minor 门拒绝） |
| c | 7 | provider_profiles | `INVALID_REQUEST` + `details.message_key=SETTINGS_INVALID_INPUT`（进入 P15 解析，需有效 profile 配置） |
| d | 7 | provider_bindings | 成功 `run_id=run-431c…, status=pending` |

结论：升 minor=7 是**必要条件**而非充分条件（还需 P15 provider profile/binding 配置有效）；在命令路径升级前，
`IRunController.StartRunAsync` 只承诺普通 overrides，UI 不得把 `provider_profiles` 当已支持能力。

## 7. C067–C077 增量（PENDING, V11R-F0-1）

按 Lead 裁定：C067–C076 逐条列名/路由/通道/参数外形，minor 写 **3（zero protocol bump）**，状态
`PENDING(V11R-F0-1)`，来源 `doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（core-writer 产出，合入后升级 FROZEN）；
另预留 C077（Region 文本投影读命令，命令名待 core-writer 确认）。测试断言这些条目不得进入 FROZEN 集合。

## 8. 偏差 / 遗留

1. **未改 core-writer 拥有的四个测试文件**：`CommandParityContractTests.cs`、`CommandWiringB1Tests.cs`、
   `CommandWiringB2Tests.cs`、`CommandIntegrationTests.cs`（`git diff` 无这些文件；66→76 改造归 V11R-F0-1）。
2. **不硬编码总数**：测试从 `HostCommandRegistry` 派生；registry 66→76/77 时只要契约同步更新 §8 即保持绿。
3. **PARTIAL 17 条**的缺口逐条写在文档 §6；补证方式（成功/错误双向 probe）建议纳入 `V11R-A-4` 快照 CI。
4. **错误分支未逐条注入运行**：§5 为源码定位集合；A-1/A-2 面（CreateChapter/Run）另有运行证据。
5. **C077 命令名**待 core-writer 契约确认；若最终名不同，只需更新文档 §8 与生成器，测试无需改（PENDING 名称解析自文档）。
6. **sidecar 副本非本 SHA 构建**（既有 AC11 副本）：本证据保留该声明；L4 前由 Lead 安排同 SHA 构建复验。
