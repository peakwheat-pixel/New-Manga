# CMD-COVERAGE-ASSERT-FIX 证据（E-1）

卡面：`doc/tasks/CMD-COVERAGE-ASSERT-FIX.md`。基线 `9a79b2a69`。

## 1. 缺陷与根因

`DomainServices_CoverEveryCommandExactlyOnce` 断言"六个 `HostDomainService` 覆盖
`HostCommandRegistry.All`（**111** 条）"，实测 `Expected: 111 / Actual: 90`。

**根因（实测确认，非推测）**：`HostCommandDomain` 有 8 个域，但只有 6 个由 `HostDomainService` 承载：

| 域 | 命令数 | 承载方式 |
|---|---|---|
| Settings / Library / Region / Reader / Resource / Workbench | **90** | 六个 `HostDomainService`（typed port） |
| `Drafts` | **6** | `HostCommandDispatcher` 显式分支（`HostCommandDispatcher.cs:882-927`：`drafts_open/patch/prepare/apply/status/discard`） |
| `SourceSync` | **15** | dispatcher / host-control 通道（`HostCommandDispatcher.cs:346` 等） |

6 + 15 = **21** = 111 − 90，与失败值完全吻合。**断言与现行两通路架构不符，不是"缺两个服务"。**

**为何长期未暴露**：该测试标注 `[SidecarFact]`；未设 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 时 SKIP，
而历史全量记录多为无夹具模式。关键事实：`HostCommandDispatcher` 的构造参数**全部有默认值**，
`HostDomainService.Descriptors` 完全来自静态 registry —— 这组断言**本不需要 sidecar**。

## 2. 改动

| 位置 | 改动 |
|---|---|
| **新增** `tests/NewManga.CoreClient.Tests/Commands/CommandCoverageRoutingTests.cs` | 4 个 `[Fact]`（**无 sidecar**）：① 六服务覆盖 = All − (Drafts ∪ SourceSync) 且全局唯一；② 未覆盖命令必须全部落在两族，且两族不得含非生产命令；③ 每个 domain 至少一条命令；④ AC3 判别力（合成 + 真实数据探针） |
| `tests/.../Commands/CommandIntegrationTests.cs` | 把 `DomainServices_CoverEveryCommandExactlyOnce` 的三处 `HostCommandRegistry.All.Count`（111）改为 `typedCommandCount`（非 Drafts/SourceSync 的命令数，90），并加注释说明 E-1 与两通路架构 |

**零生产代码改动**（`git diff` 不含 `src/**`）。

## 3. 验证

| 项 | 结果 |
|---|---|
| 新增无夹具测试 | `CommandCoverageRoutingTests` **4 passed**（76 ms，未设夹具） |
| **原失败测试修复后** | `DomainServices_CoverEveryCommandExactlyOnce`（设夹具）**1 passed**（修复前为 `Expected 111 / Actual 90` 失败） |
| AC3 判别力 | `AC3_AnOutOfRouteCommand_IsReportedAsUnrouted` 用三种方式验证同一谓词：基线无越界命令；合成命令被报为越界；**从真实覆盖集移除一条命令后该命令立刻被报为越界** |
| 契约面 | 未改 wire/DTO/Core；`generate_api_inventory.py --check` 仍 `1/80/6=87` |

## 4. 诚实边界（不得写成"命令可达性已完全验证"）

### 4.1 这组断言的**性质**（r1 复核 P2-2，必须登记）

六个 `HostDomainService`（`SettingsCommandService` 等）**只定义在 `DomainServices.cs`，生产 `src/**`
从未实例化** —— 生产分派只经 `HostRuntime` → `HostCommandDispatcher`。因此本卡恢复的守卫校验的是
**registry 的域划分与"六服务端口"这一契约抽象的一致性**，**不是**"生产命令可达性"。
用"两通路可达性"描述生产行为属表述过强，已在此更正。

### 4.2 本次断言能发现

- 新增/改域后某命令**既不被六服务覆盖、也不在 `Drafts`/`SourceSync` 两族**（AC3 已证：合成命令
  与"从真实覆盖集移除一条命令"两种方式都能报出）；
- **路由重叠**：一条命令同时被 typed service 覆盖**且**列在 dispatcher 族里（P2-1 已证：把
  `create_region` 塞进 `SourceSyncCommandNames` 后 5/5 变红，此前为 4/4 绿）；
- 某 domain 整体没有任何命令；
- `Drafts`/`SourceSync` 族里混入注册表之外的名字。

### 4.3 本次断言**不能**发现（前置说法更正，r1 复核 P2-3）

- 某条命令被**错误归类**进 `Drafts`/`SourceSync`（会被当作 dispatcher 直通而放行）；
- 族内命令在 dispatcher 上**没有对应的 payload 处理**（`drafts_*` 是显式 case，其余走 default 透传）。

**关于"registry ↔ Core 命令面一致性由谁保证"—— 此前写法不准确**：`scripts/extract-command-surface.py
--check` 比对的是**旧 Rust 端的 `PRODUCTION_COMMANDS` 与快照**，`core-command-probe.json` 的 25 条探测
里**没有** `drafts_*` / `source_*`。所以这 21 条与 Core 实际 handler 的一致性**没有**被本卡或该脚本覆盖，
属未验证面。

