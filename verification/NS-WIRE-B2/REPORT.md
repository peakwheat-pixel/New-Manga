# NS-WIRE-B2：剩余 NOT_SUPPORTED 命令收尾接线（11 条）

> 状态：**ready-for-integration**（实现 + 证据 + Handoff 完成；待 DSH 复核/集成；Owner 不自审）
> 基线：`27b5a4005`（分支基于当前 HEAD `15b9b0441` 释放）
> 分支：`task/NS-WIRE-B2`；工作树：`G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2`
> 范围：`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-B2/**`、workspace。**未改 Python Core 语义、未改 Host 契约、未改旧壳、未 push。**

## 0. 结论

| 项 | 前 | 后 |
|---|---|---|
| IMPLEMENTED | 55 | **64** |
| NOT_SUPPORTED | 11 | **2**（`credential_put` / `credential_clear`，AC3 BLOCKED） |
| 命令面总数 | 66 | 66（不变） |

11 条中 **9 条接线并对冻结 sidecar 真实执行断言通过**，**2 条如实标 BLOCKED**：Core 侧路由存在（`BindProfileCredential` / `ClearProfileCredential`），但旧壳的语义是「Host 本地 OS 凭据存储 + 交互式凭据输入」两段式，Avalonia Host 目前没有凭据管理器端口 —— 伪造 `credential_ref` 会把无法解密的引用写进 Core，**因此按 AC3 不得标 IMPLEMENTED**。

---

## 1. AC1 清单（11 条逐条：Core 路由 / 参数 / 返回 / 是否支持）

来源：`HostCommandRegistry`（`CommandParityContractTests` 断言 notSupported=11 的同一份注册表）+ `verification/NS-RECLASSIFY-1/reclassification.json` 的 `core_command` 与路由探针结论。机器可读版本：`commands/ns-b2-inventory.json`（由 `Inventory_B2Commands_IsWrittenAsEvidence` 生成）。

| # | 命令 | 域 | 旧壳参数（Tauri 签名） | Core 路由 | minor | Core 入参（dispatcher 构造） | Core 返回（实测/源码） | Core 支持 | 本 Task 结论 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `backup_restore` | settings | `backup_id: String, confirm_restore: bool` | `backup.restore` | 3 | `{backup_id, confirm_restore}` | `{restored_from, pre_restore_backup_id, schema_versions{backup,restored}, managed_consistency{...}}` | ✅ 已实现 | **接线**（success） |
| 2 | `settings_provider_profiles_create` | settings | `provider_id, display_name, capabilities[], endpoint, model, network_profile_id?, enabled` | `settings_provider_profiles_create` | 7 | 同左（`network_profile_id` 保留显式 null） | `{profile:{profile_id, provider_id, display_name, capabilities[], endpoint, model, network_profile_id, enabled, credential_state}}` | ✅ | **接线**（success） |
| 3 | `settings_provider_profiles_update` | settings | `profile_id` + 同 #2 其余字段 | `settings_provider_profiles_update` | 7 | 同左 | `{profile:{...}}` | ✅ | **接线**（success） |
| 4 | `settings_provider_profiles_delete` | settings | `profile_id` | `settings_provider_profiles_delete` | 7 | `{profile_id}` | `{deleted:true}`；Core 守卫 `SETTINGS_ITEM_NOT_FOUND` / `SETTINGS_CONFLICT`（仍被 binding 或保护中 run 引用） | ✅ | **接线**（success） |
| 5 | `settings_provider_bindings_set` | settings | `scope: BindingScope, capability, profile_id` | `settings_provider_bindings_set` | 7 | `{scope, capability, profile_id}` | `{binding:{scope,capability,profile_id}}` | ✅ | **接线**（success） |
| 6 | `settings_network_profiles_test` | settings | `network_profile_id, provider_profile_id?` | `settings_network_profiles_test` | 7 | `{network_profile_id, provider_profile_id?}` | `{status, failed_stage, direct_fallback_used, stages[6]{stage,status,reason,duration_ms}}` | ✅（执行真实 Proxy/DNS/TCP/TLS/HTTP/ProviderAuth 诊断） | **接线**（success，`status=passed`，本地 loopback 假 `/models` 端点） |
| 7 | `settings_network_profile_resolve` | settings | `provider_profile_id?` | `settings_network_profile_resolve` | 7 | `{}` / `{provider_profile_id}` | `{network_profile_id, mode, source}`（有 provider 绑定时含该 profile 的解析视图） | ✅ | **接线**（success） |
| 8 | `credential_put` | settings | `request: Request<'_>`（凭据意图 + 目标） | `BindProfileCredential` | 7 | `{target:{kind,profile_id/net_profile_id}, credential_ref}` | `{state:"configured"}`；**要求 credential_ref 已存在于 Core 凭据存储** | ⚠️ 路由/处理器存在，但只是「绑定已存在凭据」 | **BLOCKED**（AC3） |
| 9 | `credential_clear` | settings | 同上 | `ClearProfileCredential` | 7 | `{target:{...}}` | `{state:"missing"}`；只清 Core 侧 `credential_ref` | ⚠️ 路由/处理器存在，但不删 OS 凭据 | **BLOCKED**（AC3） |
| 10 | `library_delete_books_permanently` | library | `payload: {book_ids[], confirmed_book_ids[], confirm_count, confirm_permanent_delete}` | `PermanentlyDeleteBooks` | 10 | 严格键集：`{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete}` | `{requested_count, completed_count, items[{book_id,status,error_code}]}`；Core 守卫 `BOOK_DELETE_BATCH_LIMIT_EXCEEDED` / `DUPLICATE_BOOK_ID` / `BOOK_DELETE_BATCH_WHOLE_LIBRARY` / `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` | ✅ | **接线**（success） |
| 11 | `list_region_revisions` | region | `region_id: String` | `list_region_revisions` | 3 | `{region_id}` | `{region_id, current_revision_no, revisions[{region_revision_id,revision_no,origin,review_state,is_pinned,restored_from_revision_id,created_at,region_type,sfx_policy,is_current}]}` | ✅（NS-RECLASSIFY 探针 ok:true，旧 S2 用假 id 才判未实现） | **接线**（success，真实 region fixture） |

**「Core 支持」判定口径**：只有「路由存在 + handler 真的执行 + 返回域投影（不是 `UNKNOWN_COMMAND` / `INVALID_REQUEST`）」才算支持；`INVALID_REQUEST` 只证明路由存在，不能证明可接线 —— 这也是本 Task 对每条都构造了**完整合法 payload** 的原因。

---

## 2. AC2 接线（9 条，对冻结 sidecar 真实执行）

实现全部在 `apps/desktop-avalonia/**`：

- `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`：9 条 `CoreBindings`（路由 + minor 如上表）；`CoreRoute` 旧字典删除（其唯一条目 `list_region_revisions` 已接线），改为 `BlockedReasons`（仅 2 条凭据命令）。
- `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`：9 条 payload 翻译 + 边界校验。必填缺失/类型错误一律 `INVALID_ARGUMENTS` 且**不发帧**；`network_profile_id` 保留显式 JSON null；`library_delete_books_permanently` 兼容旧壳 `payload:{...}` 与内联两种调用形态（与单本删除一致）。
- `tests/.../Commands/CommandWiringB2Tests.cs`（新，5 项）：
  1. registry/路由/minor 断言 + BLOCKED 原因断言；
  2. AC1 清单写 `commands/ns-b2-inventory.json`；
  3. **9 条真实执行**（`B2Commands_ExecuteAgainstFrozenCore`，冻结 `core_service.exe` AC11 无标签副本），每条断言返回投影并留存**请求行**（含 minor 可见）；
  4. **`list_region_revisions` 用 S4 region fixture 真实数据**（`ListRegionRevisions_ExecutesAgainstRegionFixture`，真实 `region_id` → 真实 revision 历史，含 request/response 行）；
  5. 17 个非法参数用例全部 `INVALID_ARGUMENTS` 且 **Core 帧数零增量**。

`settings_network_profiles_test` 的 `passed` 不是 mock：冻结 Core 真的跑了 6 段诊断；测试在 127.0.0.1 上起了一个只回 `GET /models` 的假端点（`FakeModelsEndpoint`），因此 **TCP/HTTP 两段真实通过、其余段按 Core 规则 not_applicable**，结果 `status=passed, failed_stage=null, stages=6`。全程无外网访问。

---

## 3. AC3 真缺口（2 条 BLOCKED 的原因）

两条命令的 **Core 半段**在，**Host 半段**不在：

- 旧 Tauri `credential_put`（`apps/desktop/src-tauri/src/settings_bridge.rs:288-332`）：
  1. 读当前 `credential_state` 做 intent 校验；
  2. `credential_manager::prompt_and_store(...)` —— **交互式凭据输入 + Windows 凭据存储**生成 `credential_ref`；
  3. 再调 Core `BindProfileCredential` 把这个 ref 绑到 profile。
- 旧 Tauri `credential_clear`（同文件 `:334-350`）：Core `ClearProfileCredential` + **Host 凭据管理器 delete** 两段式。

Avalonia Host 侧 `apps/desktop-avalonia/src/**` 目前没有任何 credential manager / OS 凭据端口（本次 grep 只有 CoreClient 文档字符串提到 credential），因此：

- 若强行接线，`credential_put` 只能伪造一个 `credential_ref`：Core 的 `_credential_store().has_credential()` 会拒（`SETTINGS_INVALID_INPUT`），或更糟 —— 若将来放行，会把**无法解密**的引用写进 profile；
- `credential_clear` 只接 Core 半段会把 `credential_state` 误报为 `missing`，而 OS 凭据仍在，属于**安全语义倒退**。

所以两条保持 `NOT_SUPPORTED`，但原因从旧的泛化文案（「S2 只迁移已探测通过的命令面」）升级为具名 BLOCKED：`BLOCKED（NS-WIRE-B2 AC3）…`，指向具体旧壳位置与缺失端口，待 Host 凭据端口移植（AD-002 后续 Slice）后接入。**未把验证不了的标 IMPLEMENTED。**

---

## 4. AC4 parity / 回归

> 本节数字由本次实际运行填入；命令与日志在 `test/` 与 `evidence/`。

| 门 | 命令 | 结果 |
|---|---|---|
| 命令面零漂移 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | **PASS**：`production command surface matches snapshot (66 commands, domains={resource:3, workbench:12, library:8, settings:33, region:6, reader:4})` |
| 冻结 sidecar 探针 | `scripts/probe-core-commands.ps1`（test.ps1 内） | 25 probes：13 `ok:true`；12 为**预期负向**（大写旧名 `ListRegionRevisions`/`ListChapters`/`ListRegions`… = `UNKNOWN_COMMAND`，小写正名 `list_region_revisions` = `TARGET_NOT_FOUND`，另有故意错参数/错版本用例）→ 正是 AC1 的「大小写/假 id」再确认 |
| .NET 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1` | **182/182 passed, 0 skipped**（coreclient 61 / host 46 / app 75） |
| vitest | `npm test`（apps/desktop/frontend） | **60 files / 567 tests passed** |
| pytest | `python -m pytest -q`（PYTHONPATH=src） | **3 failed / 2764 passed / 9 skipped**；失败集合与本仓既有基线（`verification/BOOK-FIXTURE-1/pytest.log` 等 10 份日志）**逐名一致** —— `test_detection_manga_real`×2 + `test_workbench_viewmodel`×1，**0 新增确定性失败**（本 Task 未改任何 Python 文件） |

**parity 明细**：`implemented 55 → 64`、`not_supported 11 → 2`、`coverage 100%`（66/66 有 owner）；`CommandParityContractTests` / `CommandIntegrationTests` / `CommandWiringB1Tests` 的计数断言同步更新，且新增「残留 NS 恰为 credential pair」的集合断言（防止将来悄悄回退）。日志：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`、`test/test.ps1.log`。

**AC1 关键交叉证据（来自 `parity/core-command-probe.json`）**：同一份冻结 sidecar 上，`ListRegionRevisions`（旧壳大写名）返回 `UNKNOWN_COMMAND`，而 `list_region_revisions`（规范小写名）返回 `TARGET_NOT_FOUND` —— 即路由存在且 handler 已执行，只是假 id 才找不到。这直接复现了 NS-RECLASSIFY-1 对「旧 S2 探针用错命令名/假 id」的判断，也是本 Task 能把该命令接线的依据；真实 region_id 下 `ListRegionRevisions_ExecutesAgainstRegionFixture` 得到 `current_revision_no≥1` 与 `is_current` 条目。

---

## 5. AC5 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NS-WIRE-B2.md`：**PASS (3 warnings)** —— 3 条 warning 均为仓库既有预算/非终态提示（`STATUS.md` 80% 预算、`REBASELINE_PLAN.md` 80% 预算、12 个非终态 Task 不得批量关闭），与本 Task 内容无关。
- Canonical Evidence：见本卡 `## Canonical Evidence`（64-hex sha256，指向 delivery head）。
- Handoff + Record Decision：本卡内（见 `## Record Decision` 与 `## Handoff`）。

## 5.1 证据清单（本目录）

| 路径 | 内容 |
|---|---|
| `commands/ns-b2-inventory.json` | AC1：11 条清单（命令/域/状态/通道/Core 路由/minor/原因） |
| `commands/ns-b2-integration.json` | AC2：9 条真实执行的逐条 basis + Core 请求行 |
| `commands/ns-b2-list-region-revisions.json` | AC2：真实 region fixture 上的 revision 历史（含 request/response 行） |
| `commands/ns-b2-invalid-arguments.json` | AC2：17 个非法参数用例 + Core 帧数零增量 |
| `commands/parity-contract.json` | AC3/AC4：66 条覆盖矩阵与 implemented/not_supported 计数 |
| `parity/core-command-probe.json` | AC1/AC4：冻结 sidecar 25 条路由探针（含大小写对照） |
| `test/summary.json`、`test/test.ps1.log`、`test/dotnet-test-Debug.log` | AC4：test.ps1 182/182、build 与 extract/probe 输出 |
| `test/vitest.log`、`test/pytest.log` | AC4：旧壳 60/567、Python 3F/2764P/9S（同基线） |

---

## 6. Record Decision（摘要）

| 项 | 决定 |
|---|---|
| 批次范围 | 只接 registry 当前 11 条 NS；不碰其它 Task 范围（TRANSLATE/RACE） |
| 路由/minor | 沿用 NS-RECLASSIFY 成功探测：`backup.restore`/`list_region_revisions` = minor 3；P15 六个 settings 面 = minor 7；`PermanentlyDeleteBooks` = minor 10 |
| payload 翻译 | 以旧壳 Tauri 签名（`main.rs` / `settings_bridge.rs`）为准显式构造；必填校验 → `INVALID_ARGUMENTS` 且零 Core 帧；可选参数只在存在时发送；`network_profile_id` 保留显式 null；batch delete 兼容裁剪/内联两种形态 |
| 验证口径 | 真实请求冻结 core_service；**成功投影**才算实证；`INVALID_REQUEST`/`UNKNOWN_COMMAND` 不算实现；凭据对因 Host 端口缺失标 BLOCKED，不伪造 |
| 与其它 Task 边界 | registry 冲突按「先落地者为准、后落地者 rebase」（B1 同规则）；未改 Host 契约、未改 Core |

## 7. Handoff

- 交付：分支 `task/NS-WIRE-B2`，实现 + 5 项新测试 + 证据。
- 复核入口：`verification/NS-WIRE-B2/REPORT.md`（本文件）、`test/summary.json`、`commands/ns-b2-*.json`。
- 未做（明确留给后续）：
  1. **Host 凭据管理器端口**（Windows Credential Manager / DPAPI + 交互式凭据输入）→ 之后 `credential_put`/`credential_clear` 可接线；
  2. Avalonia 设置页/工作台 UI 对这些新命令的入口（本 Task 只做命令面）；
  3. `settings_network_profiles_test` 在真实网络下的可用性属产品验收，不在本 Task；
  4. 版本控制：minor 仍硬编码（P15=7、DELETE=10），Core 协议升级需重跑 `probe-core-commands.ps1`。
