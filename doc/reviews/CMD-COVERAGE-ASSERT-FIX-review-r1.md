# CMD-COVERAGE-ASSERT-FIX 独立复核 r1

## 0. 审查者、来源与范围

- **审查者**：DSH 子 agent `review-cmd-coverage`（独立上下文；未参与本卡实现；由 root agent `lead` 派发）。
- **被审 head**：`f1835e437d73695338c4212cf4057821acab58e7`（`fix(cmd-coverage)`）。
- **基线**：`9a79b2a69`；`git merge-base --is-ancestor 9a79b2a69 HEAD` 返回 0。
- **方式**：只读代码/文档 + 可还原的临时实验；除本报告外未保留任何工作区改动。实验后、写报告前 `git status --short` 为空；所有被改文件均用 `git checkout --` 还原并核对 blob 与 HEAD 一致。
- **范围**：`doc/tasks/CMD-COVERAGE-ASSERT-FIX.md`、`verification/CMD-COVERAGE-ASSERT-FIX/README.md`、`four-pieces.log`、`git diff 9a79b2a69..HEAD`。

## 1. verdict

**ACCEPT_WITH_LIMITATIONS**

算术、根因的"21 条不属于六个 typed service"部分、零生产代码改动、原测试的修正与跨域断言保留，均经复核成立；新增测试在"新增一个 domain 命令"这一真实变更下会变红（已实测）。但交付的**表述强于测试实际证明的东西**：六个 `HostDomainService` 在生产代码中从未被实例化，所谓"两通路/六端口可达"只是测试夹具的域分类；"exactly one route"未被强制（服务覆盖集与 dispatcher 族集合可以重叠），且 SourceSync 族的这类重叠在无夹具全量中仍是绿的。另有 README 对补偿门禁的错误归因、证据引用缺失和一处越界证据文件改动。上述均非当前命令不可达的生产缺口，故不判 REJECT。

## 2. 算术与根因复核（亲自计算，不采信卡面）

通过反射加载 `apps/desktop-avalonia/src/NewManga.CoreClient/bin/Debug/net9.0/NewManga.CoreClient.dll` 读取 `HostCommandRegistry`，并用源码数组人工复核：

| 项 | 实测 |
|---|---:|
| `HostCommandRegistry.All.Count` | **111** |
| Settings / Library / Region | 33 / 21 / 17 |
| Reader / Resource / Workbench | 4 / 3 / 12 |
| 六服务合计（typed） | **90** |
| Drafts | **6** |
| SourceSync | **15** |
| Drafts + SourceSync | **21** = 111 − 90 |
| `DraftsCommandNames.Count` | **6** |
| `SourceSyncCommandNames.Count` | **15** |
| `NotSupported` / `Implemented` | **0 / 111** |
| Channel 分布 | CoreService 85、CoreHostControl 8、HostBridge 3、HostLocal 15 |

`DraftsCommandNames` / `SourceSyncCommandNames` 与各自 domain 的描述符集合实测完全相等（`SetEquals` 为 True）。**算术结论：卡面 "111 / 90 / 6 / 15 / 21" 全部正确。**

### 根因是否成立

- `drafts_*`：6 条在 `HostCommandRegistry.cs:300-305` 有 `CoreBindings`，在 `HostCommandDispatcher.cs:882-927` 有显式 payload case，channel 为 `CoreService`。**有 dispatcher 通路，成立。**
- `source_*`：15 条不是"全部 8 条 host-control"那么单一，但每条都有通路：
  - 6 条 `CoreService`（`source_plan_sync` / `source_preview_sync_plan` / `source_confirm_sync_plan` / `source_invalidate_sync_plan` / `source_get_operation` / `source_cancel_operation`），走 `HostCommandDispatcher.cs:192-205` 的通用 channel 分派；
  - 8 条 `CoreHostControl`（`HostCommandDispatcher.cs:398-408`），走 `InvokeHostControlAsync`（`:324-396`），其中写入类还经 journal；
  - 1 条 `source_get_sync_capabilities` 为 `HostLocal`，由生产 `HostRuntime.cs:1275-1282` 显式处理。
  - 除 `drafts_*` 外，`source_*` 没有逐命令显式 case，走 `WriteCorePayload` 的 `default` 透传（`:928-934`）；这与 README "其余走 default 透传"一致。**没有发现"某条 SourceSync 命令完全没有 dispatcher 通路"的情况。**
- 但"两通路/六个 typed port"是**测试层表述**，不是生产路由：`HostDomainService` 的六个具体类在 `apps/desktop-avalonia/src/**` 中没有任何实例化，只有测试构造（`CommandIntegrationTests.cs:37-42`、`CommandCoverageRoutingTests.cs:31-36`）；生产 `HostRuntime.cs:1588-1611` / `:1618` 直接构造 `HostCommandDispatcher`，所有 111 条都经同一个 dispatcher 的 channel switch。详见 P2-2。

**结论：不是"缺两个服务"，原断言确实是过时的测试口径；21 条均有生产分派路径。但"命令可达性"这一层并不是由六个 typed service 提供的。**

## 3. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 脱离 sidecar | **PASS（有注）** | `CommandCoverageRoutingTests` 为 `[Fact]`，不设 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 实跑 **4 passed**；原 `DomainServices_CoverEveryCommandExactlyOnce` 仍保留 `[SidecarFact]`，但其全量覆盖断言已移到新的无夹具测试，故 AC1 目标达成。 |
| AC2 口径正确 | **PASS（有保留）** | 新测试 `:62-87` 断言六服务 = `All − (Drafts ∪ SourceSync)`（按 domain）且服务内无重名；`:89-106` 断言未覆盖命令全部落在两族；`:108-115` 断言每个 domain ≥1。算术与集合实测成立。"exactly once"只在服务集合内部成立，跨"服务/族"未断言互斥（P2-1）。 |
| AC3 判别力 | **PASS（有保留）** | 真实实验：临时新增 `HostCommandDomain.ExperimentalProbe` + `experimental_probe_command` 并注册后，新类 **3 failed / 1 passed**，`AC3...` 报 `Actual: "experimental_probe_command"`；证明真实 registry 变化会使测试变红。但 AC3 内部的"合成 + 真实数据探针"与 `FirstUnrouted` 同源，方法论是自证的（P3-1）。 |
| AC4 sidecar 专属断言保留 | **PASS** | `CommandIntegrationTests.cs:421-425` 仅把三处期望值由 `All.Count` 改为 `typedCommandCount`；`:427-429` 的 `Assert.ThrowsAsync<ArgumentException>` 与 `Assert.Contains("Library", ...)` 原样保留；设旧 sidecar 实跑 **1 passed**。 |
| AC5 零生产代码改动 | **PASS（有注）** | `git diff --name-only 9a79b2a69..HEAD -- 'apps/desktop-avalonia/src/**'` 为空；无 `src/**` 改动。但提交额外含 `verification/FEA-09/logs/wire-redacted.ndjson` +1 行（P3-3），严格说不是"只含测试 + 文档"。 |
| AC6 不回归 | **PASS（有注）** | 无夹具全量复跑 **186 passed / 0 failed / 26 skipped**；`check.ps1` PASS（3 warnings）、`verify_pins.ps1` 18/18、`generate_api_inventory.py --check` exit 0、`extract-command-surface.py --check` exit 0。第一次全量曾因 `library.db-shm` 被占用出现 1 个非本卡相关的瞬时失败，重跑即绿；任务卡把 186/0/26 的证据指向 `four-pieces.log`，但该文件没有测试输出（P3-2）。 |

## 4. Findings

### P2-1 新测试没有强制"exactly one route"：服务覆盖集与 dispatcher 族集合可重叠，SourceSync 侧全量仍绿

- **位置**：`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandCoverageRoutingTests.cs:7`（类注释 "exactly one route"）、`:82`（只按 domain 派生 `expected`）、`:89-106`（只检查 *uncovered* 是否在族中，未检查 *covered ∩ families*）；`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:505-513`（公开 `SourceSyncCommandNames`）。
- **证据（实测）**：把 Region 域、加性命令 `create_region` 加入 `SourceSyncCommandNames` 后：
  - 新类 `CommandCoverageRoutingTests` **4/4 passed**；
  - `CommandParityContractTests.Registry_CoversSnapshotExactly_WithSixDomains`、`DraftCommandRegistryTests.Additive_Set_IsTheUnionOfTheDeclaredFamilies`、`CommandContractV11RTests.RegistrySurface_IsFullyDeclared_WithoutHardcodingTheTotal` 合计 **7/7 passed**；
  - 无夹具全量 **186/0/26 passed**。
  这说明"一个 Region 域命令同时被登记为 SourceSync 族"不会使任何无夹具测试变红。Drafts 侧类似实验（把 `settings_get` 加入 `DraftsCommandNames`）新类 4/4 通过；按 `DraftCommandRegistryTests.cs:56-62` 的集合相等断言应失败（未单独复跑），**SourceSync 没有等价的 domain 分区测试**。
- **影响**：新测试宣称的"每条命令恰好一条通路"并未被断言；若 `DraftsCommandNames`/`SourceSyncCommandNames` 与私有数组/domain 漂移，新增一个加性 typed 命令到 SourceSync 族可以完全绕过当前无夹具测试。对当前生产路由不是故障（descriptor 的 domain/channel 仍决定路由），但它直接削弱了本卡交付的核心断言，且不在 README §4 的"不能发现"清单里（§4 只写了"错误归类进 Drafts/SourceSync"这一抽象类别，未说明服务/族重叠）。
- **建议**：在新测试中补
  - `Assert.Empty(covered.Intersect(families))`；
  - `Assert.Equal(families, All.Where(d => d.Domain in {Drafts, SourceSync}).Select(d => d.Name))`；
  - 为 SourceSync 增加等价的 domain 分区测试（对齐 `DraftCommandRegistryTests.cs:56-62`）。

### P2-2 "可达性/两通路/六个 typed port"是测试夹具口径，不是生产路由；交付表述过强

- **位置**：`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandCoverageRoutingTests.cs:7-15`；`verification/CMD-COVERAGE-ASSERT-FIX/README.md:16-18`、`:44-52`；`doc/tasks/CMD-COVERAGE-ASSERT-FIX.md:41-44`；commit message。
- **证据**：`HostDomainService` 六个具体类仅在 `src/NewManga.CoreClient/Commands/DomainServices.cs:40-98` 定义；全仓库无生产实例化，只有测试构造（`CommandIntegrationTests.cs:37-42`、`CommandCoverageRoutingTests.cs:31-36`）。生产侧 `HostRuntime.cs:1588-1611` / `:1618` 直接构造 `HostCommandDispatcher`，由 `:192-205` 的 channel switch 统一分派全部 111 条。新测试自己 `new` 六个 service，因此它证明的是"描述符/domain 分类覆盖"，不是"生产命令可达"。
- **影响**：`CommandCoverageRoutingTests` 被写成 "every production command is reachable through exactly one route — either one of the six typed `HostDomainService` ports, or the `HostCommandDispatcher` direct family"，但"six ports"在运行时不参与分派；`恢复命令可达性守卫` 这一表述也过强。当前没有不可达命令（111/0 NotSupported，21 条均有 channel/binding），所以不是生产缺口；但 Gate/集成若把它当作可达性证明，会高估覆盖。
- **建议**：把类注释/README/卡面改为"domain/descriptor 分类守卫"；若确需可达性守卫，应显式检查每个 descriptor 的 `IsImplemented`、`Channel != None`、Core/ HostControl 的 `CoreCommand` 非空（`CommandWiringB1Tests.cs:41-50`、`CommandWiringB2Tests.cs:46-54` 已在做一部分），或补一条 dispatcher 级 mock 路由测试。

### P2-3 README/commit 把 `extract-command-surface.py --check` 说成 registry ↔ Core 一致性的保证，实际不是

- **位置**：`verification/CMD-COVERAGE-ASSERT-FIX/README.md:50-52`；`:45-47`；commit message 与 `doc/tasks/CMD-COVERAGE-ASSERT-FIX.md:47-48` 的相邻表述。
- **证据**：`apps/desktop-avalonia/scripts/extract-command-surface.py:1-10` 自述是提取**旧 Rust host** 的 `PRODUCTION_COMMANDS`；`:279-306` 的 `--check` 只把内存快照与 `verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json` 比较，不读 C# registry，也不读 Python Core。C# 的 `CommandParityContractTests.cs:72-91` 检查的是 registry ↔ 该 Rust 快照；`core-command-probe.json` 实测有 **25** 条探测，但其中没有 `drafts_*` / `source_*`（`CommandParityContractTests.cs:23-38` 硬编码的 13 条只是子集）。因此它对"族内命令在 dispatcher 上没有对应 payload 处理"这一已知缺口，**没有提供 README 所称的 Core 侧补偿门禁**。
- **影响**：§4 的"不能发现"本身是诚实的，但随后用错误归因把该风险说成"由 extract-command-surface.py --check 与 Core 契约测试保证"，属于证据夸大；集成评审可能据此误以为 21 条已有 Core 侧覆盖。
- **建议**：删除该保证句，改为"本卡未验证 Core 侧 handler 覆盖，需另立证据/任务"；若确有 Core 契约测试，请给出具体测试名、覆盖命令数和最近一次运行结果，而不要引用 Rust surface 脚本。

### P3-1 AC3 的"三种方式"是自证；真实判别力来自 baseline 与其他 fact

- **位置**：`CommandCoverageRoutingTests.cs:122-142`；helper `:55-59`。
- **证据**：`synthetic_unrouted_command` 被 append 到 `All.Keys` 后由同一个 `FirstUnrouted` 报出；"从真实覆盖集移除一条"也是把 `covered` 手动删一项再交给同一个 helper。两者只证明 helper 的实现，不证明生产覆盖谓词独立有效；真正扫描真实 registry 的只有 `:129` 的 `Assert.Null`。我们的新 domain 实验确实让 `:129` 变红，所以 AC3 在"真实 registry 出现越界命令"这一情形下有判别力，但这份判别力来自 baseline，不是"三种方式"。
- **影响**：AC3 的"判别力"证据被高估；如果 helper 的族/覆盖定义写错（与主测试同错），AC3 仍会绿。当前没有造成误绿，因为 `SixServices`/`EveryUncovered` 有独立断言。
- **建议**：把 AC3 改名为 predicate 自检，或增加一个与主测试不同源的断言（例如直接构造 `covered`/`families` 的空集、单元素集并验证 `FirstUnrouted` 的边界），不再宣称"三种方式证明判别力"。

### P3-2 任务卡把 186/0/26 的证据指向 `four-pieces.log`，该文件没有测试输出

- **位置**：`doc/tasks/CMD-COVERAGE-ASSERT-FIX.md:90`；`verification/CMD-COVERAGE-ASSERT-FIX/four-pieces.log:1-14`；`verification/CMD-COVERAGE-ASSERT-FIX/README.md:35-40`。
- **证据**：`four-pieces.log` 只有 `check.ps1`、`verify_pins.ps1`、api inventory 三段；没有 `dotnet test` 全量输出，也没有 186/0/26 或 skip 26 的记录。README §3 也没有记录全量结果。我们独立复跑得到 186/0/26，所以**结论为真，但指定证据不含该事实**。
- **影响**：AC6 的可追溯性不足；集成时不能仅凭 `four-pieces.log` 复核全量。
- **建议**：把无夹具全量的命令、环境、汇总行补进 README §3 或 `four-pieces.log`；明确 "186/0/26" 的原始输出位置。

### P3-3 提交越界修改 `verification/FEA-09/logs/wire-redacted.ndjson`，且该测试每次全量都会弄脏工作区

- **位置**：`git show --stat HEAD`（`verification/FEA-09/logs/wire-redacted.ndjson | 1 +`）；`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs:30-52`；任务卡 `allowed_paths`（只含 `verification/CMD-COVERAGE-ASSERT-FIX/**`）。
- **证据**：`WireLogSourceRedactionTests.PersistedNdjsonContainsOnlyRewrittenBytes` 以 `RepoLocator.Root/verification/FEA-09/logs/wire-redacted.ndjson` 构造 `WireLog`，每次全量都会 append 一行；提交中新增行的 `timestamp_utc` 为 `2026-11-14T17:02:33Z`，与 `four-pieces.log` 的 `01:02:54+08:00` 前后吻合。内容已全部 `[REDACTED]`，未发现秘密泄漏。我们复跑全量时也各追加一行，已用 `git checkout --` 还原并核对 blob。
- **影响**：提交不是严格的"测试 + 文档"，超出 `allowed_paths`；每次全量测试都会产生无关的 tracked 文件脏改动。该行为在既有提交中也出现过（`13d836713`、`c459b279f`），属既有卫生问题，但本卡提交再次带入。
- **建议**：让该测试写入临时目录（或测试结束清理），不要把证据文件当测试输出；若确需更新，显式加入 `allowed_paths` 并在证据中说明。

### P3-4 `doc/TASK_LEDGER.md` 的 tracked/untracked 计数在提交后已过期

- **位置**：`doc/TASK_LEDGER.md:9-16`。
- **证据**：账本写 `task files 608 / tracked 607 / untracked 1 / non-terminal tracked 6`；直接运行 `python tools/governance/task_ledger.py` 得到 `608 / tracked 608 / untracked 0 / non-terminal tracked 7`（`CMD-COVERAGE-ASSERT-FIX.md` 已在同一提交中被跟踪，`git ls-files` 有、`git status` 无未跟踪）。这与 `READER-PREF-PERSIST-review-r1.md:89` 已指出的同类问题相同：账本在任务文件尚未提交时生成，提交后未重跑。`check.ps1` 只报 WARN，不校验该列。
- **影响**：治理账本与树不一致；不影响本卡测试结论，但会误导"非终态 tracked"计数。
- **建议**：提交后重跑 `python tools/governance/task_ledger.py --write`，并把结果纳入同一提交；`check.ps1` 或 `--diff` 增加 drift 检测。

### P3-5 任务卡/方法名/STATUS 的文档一致性小问题

- **位置**：`doc/tasks/CMD-COVERAGE-ASSERT-FIX.md:99-104`（仍写 Handoff/Review/实际测试 "尚无"，但已有提交、证据和测试表）；`CommandIntegrationTests.cs:379`（方法名仍为 `DomainServices_CoverEveryCommandExactlyOnce`，实际只覆盖六个 typed domain 的 90 条）；`doc/STATUS.md:7`（为控制预算删掉了 `READER-PREF-PERSIST` 的"读回半边 NOT_RUN"，`doc/REBASELINE_PLAN.md:54` 仍保留该限制）。
- **影响**：低。卡面"尚无"会让人误以为没有交付记录；旧方法名会误导后续读者以为它覆盖 111 条；STATUS 删限制削弱了顶层披露。
- **建议**：集成前回填任务卡交付记录；重命名旧测试为 `...TypedCommands...`（或加注释）；STATUS 用一行链接保留 READER-PREF-PERSIST 限制。

## 5. 判别力实验记录（均为临时改动，已还原）

| # | 实验 | 结果 | 还原与核对 |
|---|---|---|---|
| 1 | 把原测试 `Assert.Equal(typedCommandCount, seen.Count)` 临时改回 `Assert.Equal(HostCommandRegistry.All.Count, seen.Count)`，设旧 sidecar 跑原测试 | **FAIL：Expected 111 / Actual 90**，精确复现 E-1 | `git checkout -- CommandIntegrationTests.cs`；blob 与 HEAD 一致 |
| 2 | 修复后的原测试 + 旧 sidecar（`HOST-CORECLIENT-1/sidecar-copy`） | **1 passed**（597 ms） | 无需还原；测试未写仓库 |
| 3 | 新类无夹具 | **4 passed**（15 ms） | 无改动 |
| 4 | 新 domain：`HostCommandModel.cs` 加 `ExperimentalProbe`，`HostCommandRegistry.cs` 加 `ExperimentalProbeNames = { "experimental_probe_command" }` 并 `AddDomain` | 新类 **3 failed / 1 passed**；`AC3...` 报 `Actual: "experimental_probe_command"`；`SixServices...`、`EveryUncovered...` 同时红 | 两个文件 `git checkout --`；`git hash-object` 与 HEAD 完全一致 |
| 5 | 未绑定 typed 命令：向 `SettingsNames` 加 `review_probe_unbound` | 新类 **4/4 passed**，但 registry 实测 `count=112, implemented=False, channel=None`；`CommandWiringB1Tests` / `B2Tests` 的 implemented 断言 **2 failed** | `git checkout -- HostCommandRegistry.cs`；blob 一致 |
| 6 | 服务/族重叠（Drafts）：向公开 `DraftsCommandNames` 加 `settings_get` | 新类 **4/4 passed**；`CommandParityContractTests.Registry_CoversSnapshotExactly_WithSixDomains` **FAIL（HashSets differ）** | `git checkout --`；blob 一致 |
| 7 | 服务/族重叠（SourceSync，全量盲区）：向公开 `SourceSyncCommandNames` 加 `create_region` | 新类 **4/4 passed**；parity/additive/contract 合计 **7/7 passed**；无夹具全量 **186/0/26 passed** | `git checkout -- HostCommandRegistry.cs` 与 `verification/FEA-09/logs/wire-redacted.ndjson`；两者 blob 均与 HEAD 一致 |
| 8 | 无夹具全量（未变异） | 第一次 **1 failed / 185 passed / 26 skipped**（`library.db-shm` 被占用）；重跑 **186 / 0 / 26** | 两次追加的 FEA-09 行已还原，blob 一致 |
| 9 | 治理四件套 | `check.ps1` PASS（3 warnings）；`verify_pins.ps1` 18/18；inventory `--check` exit 0；surface `--check` exit 0 | 只读，无改动 |

实验后 `git status --short` 为空（写入本报告前）。

## 6. 我没有验证的面

- 没有用真实 GUI/Host 对 21 条 Drafts/SourceSync 命令做端到端调用；只做了源码路径检查与既有测试复核。
- 没有跑带 sidecar 的全量套件（E-2：仓库 sidecar 早于多条现行命令），只跑了 `DomainServices_CoverEveryCommandExactlyOnce` 这一条；带 sidecar 的其他测试可能隐藏不同行为。
- 没有逐条核对 Python Core 是否真的能处理 21 条命令的 payload；README §4 已声明这部分不在本卡范围，我也不把它当作已验证。
- 没有独立在 pristine worktree 重跑基线（实验 1 是在当前树上临时改回旧期望值，得到同一 `111/90`）。
- 没有验证 `core-command-probe.json` 的 25 条探测之外的 Core 路由；没有验证所有 15 条 SourceSync 的实际 wire 往返。
- 没有审计 `verification/FEA-09/logs/wire-redacted.ndjson` 新增行的全部历史语义，只确认其内容为 `[REDACTED]`、由 `WireLogSourceRedactionTests` 写入。

## 7. 能否进入集成

**可以进入集成，但按 ACCEPT_WITH_LIMITATIONS 处理，并建议先做三项小修：**

1. **P2-1/P2-2 的文档与断言修正**：把"两通路/六端口可达/exactly one route"改为"domain/descriptor 分类守卫"；在新测试补 `covered ∩ families == ∅` 与 `families == {Drafts, SourceSync} domain set`（或加 SourceSync domain 分区测试）。这不需要生产代码改动，仍是测试/文档范围。
2. **P2-3 的证据更正**：删除或改写 `extract-command-surface.py --check` 对 registry↔Core 一致性的保证；明确 21 条 Core handler 覆盖未验证。
3. **P3-2/P3-4 的证据补齐**：把 186/0/26 的原始输出写进 README §3 或 `four-pieces.log`；提交后重跑 `task_ledger.py --write` 修正 tracked/untracked 计数。

若集成流程允许把上述登记为 limitation，则本卡的核心测试修复可以合入；若 Gate 依赖"命令可达性"这一层作为证据，则**不应**在修正 P2-2/P2-3 之前把它写成"已恢复可达性守卫"。

## 8. 附：工作区状态

- 实验全部还原后、报告写入前：`git status --short` 为空。
- 报告写入后，工作区只应多出本文件 `doc/reviews/CMD-COVERAGE-ASSERT-FIX-review-r1.md`；未修改任何生产代码、测试或证据文件。
