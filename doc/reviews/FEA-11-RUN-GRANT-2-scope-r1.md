---
task: FEA-11-RUN-GRANT-2
title: FEA-11-RUN-GRANT-2 scope review r1（Host→Core source 身份通道 + 长 Run 续期候选；权威 scope 评审）
reviewer: fresh subagent（独立上下文；未参与 RUN-GRANT-1/RUN-GRANT-2 实现或返修；只读）
session: 委托子会话（isolation：不共享父会话上下文；会话 id 未在本会话暴露，身份来源见「真实性声明」）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非 RUN-GRANT-1 审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 3dc239d264686f90c3d6a7a1801d00e31ec9458d
reviewed_head_note: 任务书给的是 b2261825e；评审期间父会话在 main 追加了 docs-only 提交 3dc239d26（仅新增 doc/handoffs/DSH-PROGRESS-2026-11-07.md，+34 行），`git diff --name-only b2261825e..HEAD` 只有该文件，代码/契约/pins 零变化
verdict: READY-WITH-UNFREEZE
verdict_scope: 按「拆卡」执行——2A（version 通道，Host-only）READY-TO-FREEZE；2B（容器成员 entry 通道）READY-WITH-UNFREEZE（C-16 v1.4）；2C（长 Run 续期）不随本卡；2D（R3-02）READY（测试-only）
---

# FEA-11-RUN-GRANT-2：权威 scope review r1

> **结论先行。** 本卡方向正确，但**卡面与 L-G12 的现行措辞掩盖了一个生产级事实**：生产 Host 铸出的 `scope.version` **恒为 `"1"`**，而 Core 的 `binding.accepted_source_version` 恒为 `sv-…`；C-16 v1.3 §2.4 要求两者**相等**。因此**生产环境里任何含 referenced 页的 Run 都会在 dispatch 前被 typed `SOURCE_ACCESS_DENIED` 拒绝**（Run 根本不启动）。L-G12 描述的「可用边界 = image 单 entry + folder 逐成员 + 归档首成员」目前**只在测试里成立**（测试手工把 `"sv1"` 传给 `RunSourceScope`）。这不是「边界收窄」，而是「①版本通道 = 100% 阻断」。
>
> **因此本卡不应按「补边缘通道」的规格冻结**，而应：把 ① 当作 P0 生产阻断先修（Host-only，**无需 UNFREEZE**）；把 ② 容器成员 entry 通道单独成卡并**必须 C-16 v1.4 UNFREEZE**（Core 侧 `register` 与 `match` 两处硬性要求容器 grant **恰好 1 个 entry**，这是冻结条款邻域的安全面语义变化）；长 Run 续期（L-G1）另卡；R3-02 是测试-only，顺手收口。
>
> **裁决：`READY-WITH-UNFREEZE`**（按拆分口径：2A = `READY-TO-FREEZE`；2B = `READY-WITH-UNFREEZE`（仅 C-16，**不需要** C-17/C-06）；2C 不随本卡；2D 可并入 2A）。

---

## 0. 只读基线与命令（全部实测，除标注 NOT_RUN）

| 项 | 值 / 结果 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| reviewed_head | `3dc239d264686f90c3d6a7a1801d00e31ec9458d` | `git rev-parse HEAD` |
| 任务书声称基线 | `b2261825e`（main，clean） | 任务书 |
| 基线偏差（实测） | ①评审开始时 `b2261825e` 工作树**并非 clean**：存在未跟踪 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`（非本评审创建）；②评审期间父会话提交 `3dc239d26`（docs-only，+34 行，仅该 handoff）；③当前 HEAD `3dc239d26` 工作树 clean | `git status --porcelain=v1` 两次、`git show --stat 3dc239d26`、`git diff --name-only b2261825e..HEAD` |
| `verify_pins.ps1` | **PASS (all 18)**（C16 `7c355ccb8f82…`、C17 `aefa0fa5b17e…`、C06 `99831a20ffd6…`） | 实测 `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |
| `check.ps1`（默认） | **PASS (3 warnings)**（9 个非终态 Task；STATUS 80% 预算；REBASELINE_PLAN 80% 预算） | 实测 `pwsh -NoProfile -File tools/governance/check.ps1` |
| `check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-2.md` | **NOT_RUN** | 只读范围以默认检查为基线；未另跑（不影响结论） |
| 定向 pytest（`tests/core/test_host_control.py` + `tests/fea11/test_source_run_grant.py`） | **NOT_RUN** | 只读授权：本会话不得改生产/测试/证据字节；且卡面 AC-R6 明确全量 pytest/.NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`，需 `git checkout -- verification/FEA-09` 恢复——超出「只写一个文件」的硬约束 |
| 全量 `pytest tests` / 全量 `dotnet test NewManga.sln` / `NEWMANGA_FEA11_IPC=1` 真实 IPC | **NOT_RUN** | 同上（成本 + 会写 tracked 证据） |
| `generate_api_inventory.py --check` / `scope_validation.py` | **NOT_RUN** | 同上 |
| 写操作 | 仅写本文件；**未** `git add/commit/push`；未改生产代码/测试/契约/卡/STATUS/PLAN/LEDGER | 实测 `git status --porcelain=v1` = 空（写本文件前） |
| 文档声称的门禁数字（未复核，仅引用） | 定向 pytest 50 passed；SourceRegistry 21 passed；真实 IPC 3 passed；全量 pytest 3281/10；全量 .NET 1551/0/89；判别性 9/9；pins 18/18 | `verification/FEA-11-RUN-GRANT-1/EV.md:39-45,53-65`、`logs/host-ipc.log`（「通过: 3」） |

> 说明：表中「文档声称的门禁数字」只作为**被引用事实**，不是本评审的实测结论；凡未实跑者一律标 NOT_RUN，不以 Handoff/EV 自述替代。

---

## 1. 逐项代码事实（path:line）

### 1.1 ① 版本通道：生产铸造恒为 `"1"`（P0）

| # | 事实 | 位置 |
|---|---|---|
| F1 | 冷启动枚举把版本**硬编码** `"1"`：`target = new SourceScanTarget(sourceId!, root.Root, projectIds, "1", registryId!, generation, kind, identityDigest!)` | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1894-1895` |
| F2 | App 侧注册扫描目标的默认版本也是 `"1"`：`RegisterSourceScanTarget(string sourceId, string path, IReadOnlyList<string> projectIds, string version = "1")` | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:154-169` |
| F3 | 枚举结果**整体替换**内存目标（含被替换的 Path/Version）：`existing.Target = target;` / `_targets[target.SourceId] = new TargetState(target);` | `SourceScanScheduler.cs:640-662` |
| F4 | Run 铸造直接使用 `target.Version`：`new RunSourceScope(entry.RegistryId, entry.Generation, normalized, KindOfSource(target, normalized), target.SourceId, target.Version)` | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1717-1720` |
| F5 | 铸造把该值写进签名 scope：`["scope"] = new JsonObject { ["source_id"] = sourceId, ["version"] = version, … }` | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:373-374` |
| F6 | Core 的逐页匹配要求**严格相等**：`scope.get("source_id") != source_id or scope.get("version") != version_id` → 不匹配；`version_id = binding.get("accepted_source_version")` | `src/infrastructure/resource_channel/source_read_refs.py:566-570`、`:553` |
| F7 | Core 真实 version 形态为 `sv-…`：`version_id = existing_version_id or f"sv-{uuid.uuid4().hex}"`，并写入 `"accepted_source_version": version_id` | `src/application/importing/referenced/runtime.py:471,785` |
| F8 | 任一批次目标页不可授权 → **整体** typed `SOURCE_ACCESS_DENIED`、零映射：`if refused: raise SourceImportError("SOURCE_ACCESS_DENIED", …, details={"refused_pages": refused})` | `source_read_refs.py:519-524` |
| F9 | Host 对 Core typed 拒绝**不 dispatch**并把原码上抛：`await authorize(descriptor.Name, payload, cancellationToken)` 位于 dispatch 之前；`catch (CoreOperationException error) when (IsRunCommand(name)) → ProjectRunError` | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:147-183`（`:154-158`、`:175-178`） |
| F10 | 生产 App 只注册**路径**（不注册版本）：`writer.WriteString("locator", path); roots=[path]`；`FindOrRegisterRootAsync` 复用/注册 root，无 version 字段 | `apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs:205-211`、`:759-801` |

**推论（F1+F2+F4+F5+F6+F7）：** 生产 `scope.version == "1"`、`binding.accepted_source_version == "sv-…"` → 恒不匹配 → F8 整体拒绝 → F9 Run 不 dispatch。即**生产 referenced Run 100% 起不来**（managed-only Run 不受影响，因为无 binding 的页被 skip：`source_read_refs.py:505-513`）。

**与既有证据的对照：** RUN-GRANT-1 的真实 IPC 用例是**手工传版本**：`new RunSourceScope(registryId, generation, archive, "zip", "s1", "sv1")`（`Fea11RunGrantIpcTests.cs:77-78`），folder 用例同样取 seed receipt 的 `version_id`（`Fea11RunGrantIpcTests.cs:297-298`）。r3 已如实注明「该 folder IPC 的 Version 取自 seed receipt，不证明生产冷启动 `Version="1"` 的 version 通道」（`doc/reviews/FEA-11-RUN-GRANT-1-r3.md:125`）。**结论：现有全部「可用边界」证据都绕过了生产版本来源。**

### 1.2 ② 容器成员 entry 通道：Core 侧硬性「恰好一个 entry」

| # | 事实 | 位置 |
|---|---|---|
| F11 | Host 对非 folder 源只铸**容器单 entry**：`paths = sourceKind == "folder" ? EnumerateFolder(...) : new[] { path }`；`["locator"] = sourceKind == "folder" ? Path.GetRelativePath(...) : Path.GetFileName(member)`，`["ordinal"] = ordinal++` | `SourceReadCoordinator.cs:317,322-361`（关键 `:356-357`） |
| F12 | Core 注册期**拒绝**容器多 entry：`if len(parsed) != 1: raise SourceImportError("SOURCE_ACCESS_DENIED", "container grant must carry one entry")` | `source_read_refs.py:986-990` |
| F13 | Core 匹配期同样要求恰好 1 个 entry：`if len(raw_entries) != 1 or not isinstance(raw_entries[0], dict): return False`；随后用 `grant.container_facts` 与 `source_locations` 比对，并要求 `entry_key == binding.entry_id or locator == source_entries.locator or ordinal == source_entries.ordinal` | `source_read_refs.py:598-610` |
| F14 | 因此多成员容器的第 2..N 页无法命中（只有 `ordinal=0` 的成员能靠 ordinal 子句命中）；.NET IPC 用 p2（`ordinal=1`）实证 typed 拒绝 | `Fea11RunGrantIpcTests.cs:80-116` |
| F15 | 契约文本只写「`scope.entries[]` 中**某项**满足…」，**未**给容器 cardinality 约束；但 §2 又要求 `(source/version/entry locator, ordinal)` **可解析到 authorized_roots 内路径**——成员 locator（如 `001.png`）在语义上不是可解析路径，说明冻结文本**没有**正面规定容器成员 entry 形态 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:67`、`:73-90`（关键 `:87`） |
| F16 | folder 逐成员匹配已实现且要求「grant 成员数 == accepted version 的 `source_entries` 数」，按 locator/ordinal + sha256/size 比对 | `source_read_refs.py:633-651`、`:594-597` |

**推论：** ② 不是「Host 换个 locator 就行」。要让多成员容器可用，必须**同时**改 Core 的注册（F12）与匹配（F13）为 1..N 逐项语义；而 F15 说明冻结条款对该形态没有明文，属**共享安全面的语义扩展** → 需 **C-16 v1.4 UNFREEZE**（不是 C-17/C-06）。

### 1.3 现有可用的 Core 权威身份通道（①/② 的数据来源）

| # | 事实 | 位置 |
|---|---|---|
| F17 | `source_list_scan_targets` 的 DTO **只有** `source_id/registry_id/generation/source_kind/identity_digest/project_ids`——**无 `version_id`、无 entries** | `src/application/sources/scanner.py:164-176`；C-17 §5.2 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:261-262` |
| F18 | `ScanSourceSync` 响应（`Scan`）**同时**携带 `source.version_id`、`source.status`、`source.entries[]`（`entry_id/locator/ordinal/...`）、`bases[].version_id/entry_id`、`base_sources[].version_id` | `scanner.py:450-486`、`:461-474`、`:708-742`、`:611-634` |
| F19 | 同容器（未变更）→ 复用**已提交**版本：`target = _observation_ok(source_id, old_version_row["version_id"], …)`；容器变更 → 新候选 `sv-…`（`version_id = f"sv-{uuid...}"`，未提交） | `scanner.py:355-369`、`:370-400` |
| F20 | 「同容器」判定即 `old_version_row["content_digest"] == digest`，且 `totals` 会体现 changed（Host 已解析 totals） | `scanner.py:351-354`；`SourceScanScheduler.cs:1568-1581` |
| F21 | `ScanSourceSync` 自身需要 live grant（非 missing 源 `grant_ids` 必填），但 **`_resolve_grants` 不比对 scope.version**，只用 registry/generation/identity facts → 占位版本 grant 可用于扫描 | `scanner.py:330-331`、`:540-587` |
| F22 | Host **已经收到** Scan 响应，但**丢弃** version/entries：`ProjectScanResult` 只取 status/identity_digest/totals（仅缓存 identity） | `SourceScanScheduler.cs:1514-1566`（关键 `:1521-1530`、`:1557-1561`） |
| F23 | `GetRunSnapshot` 的 `targets[]` 只有 `target_id/target_type/order`——**不含** source/version/entry | `src/bootstrap/core_service.py:6083-6097` |
| F24 | 容器成员 locator/ordinal 由 Core 自生成：zip/cbz `locator=info.filename`、`ordinal` 按 `stable_sort_key(filename)` 自然序；PDF `locator=str(page+1)`、`ordinal=page` | `src/application/importing/referenced/scanner.py:224-231,306-313,413-414`；`model.py:81-87` |

**推论：** ① 与 ② 的**数据**都能从**既有** `ScanSourceSync` 响应获得（F18/F19/F21/F22），前提是"该源近期被扫描过"；`source_list_scan_targets`（F17）与 Run 快照（F23）都不提供。这条通道**不需要任何契约变更**，只需要 Host 停止丢弃（F22）。

### 1.4 冻结面与 pins

| # | 事实 | 位置 |
|---|---|---|
| F25 | C-16 §2.4 冻结的逐页匹配/原子性/零副作用/幂等；v1.3 仅 additive 新命令 + `source.read.run/1` | C-16 `:17-23`、`:73-90` |
| F26 | C-16 pin：`7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`；C-17 pin：`aefa0fa5b17e…`；C-06 pin：`99831a20ffd6…`（18 个冻结对象） | `doc/plan/FEA-CONTRACT-FROZEN-C16.md:16,83`；`FEA-CONTRACT-FROZEN-C17.md:15`；`FEA-CONTRACT-FROZEN-C06.md:16`；`FEA-CONTRACT_FREEZE_MATRIX.md:3,24,36,39` |
| F27 | C-17 §5 明文：请求/嵌套 DTO 未知字段拒绝；**未来新字段须新 capability/版本登记** | C-17 `:205` |
| F28 | TTL 硬上限：注册期 `expires_at > now + 300` → `SOURCE_GRANT_EXPIRED`；Host 铸造固定 300s | `source_read_refs.py:166-167`；`SourceReadCoordinator.cs:366` |
| F29 | 单次授权 grant 上限 64；grant entry 上限 10000（budget `max_entries`） | `source_read_refs.py:445`、`:902-905`；`SourceReadCoordinator.cs:52-53,287` |
| F30 | 容器匹配只用 `grant.container_facts`（单份容器身份），且 `_parse_scope` 以「单 entry」构造 `container_path/container_facts` | `source_read_refs.py:60-71`、`:986-990`、`:603-605` |
| F31 | pins 脚本按 `doc/plan/FEA-CONTRACT-FROZEN-<id>.md` 的 `sha256` 行对契约原文取哈希；对象数固定 18（UNFREEZE 是「重算 pin」而非「加 pin」） | `tools/governance/verify_pins.ps1:6-13,20-25`；SCAN-2 先例 `doc/reviews/FEA-11-SCAN-2-scope-r1.md:219` |

---

## 2. Q1 最小可行路径（逐条评估 + 取舍）

### 2.1 ① 让生产 Host 拿到 Core `version_id`

| 选项 | 机制 | 契约影响 | 成本 | 覆盖冷启动 | 判定 |
|---|---|---|---|---|---|
| **(a) 从 `ScanSourceSync`/扫描结果缓存** | Host 在既有扫描路径（scheduled / SCAN-3 tick）与冷缓存 on-demand 扫描中，从 `Scan` 响应缓存 `(source_id → version_id, entries[])`，Run 铸造时使用 | **无**（零契约字节变更；F18 早已在响应里） | 每次冷缓存 1 次容器哈希（scan 自身要 digest；同容器不重新解码） | **是**（on-demand 兜底） | **推荐（最小）** |
| (b) C-17 `ScanTarget` 加 `version_id` | 枚举直接带版本 | **需 C-17 v1.2 UNFREEZE**（F27：新字段要新 capability/版本登记；pin 重算 + 独立字节复核） | 运行期最省（无哈希） | 是 | 备选（若 DSH 不愿让 Run 期做扫描） |
| (c) 新 C-16 host-control 只读命令（如 `DescribeSourceReadScope`） | 返回 source/version/entries | **需 C-16 v1.4 UNFREEZE** + 新能力 + 新命令面 | 最小运行期成本（SELECT 级），但新增 host-control 面 | 是 | 与 ② 合并时才有价值 |
| (d) Host 从 Core 现有 Run 命令获取 | 例如 `GetRunSnapshot` | 无 | — | — | **不可行**：F23 快照无 version/entry |
| (d') App 传入 version | App 知道 version | 无 | — | **否**（App 无持久 version；F10 只注册路径） | 不足 |

**结论（①）：** 最小机制 = **(a) 缓存既有 `ScanSourceSync` 响应的 `source.version_id`**（F18/F22 已具备），配 **冷缓存 on-demand 一次有界扫描**；无需 UNFREEZE。`(b)/(c)` 只有在 DSH 判定「Run 期扫描不可接受」时才值得触发契约 UNFREEZE。

### 2.2 ② 让 Host 拿到容器成员 entry 身份（locator/ordinal）

| 选项 | 数据来源 | Core 改动 | 契约影响 | 风险 | 判定 |
|---|---|---|---|---|---|
| **(a2) 缓存扫描响应的 `source.entries[]`（Core 权威 locator/ordinal），Host 铸 N 项** | 同 ①（F18） | **必须**：注册接受 N 项（F12）+ 匹配逐项（F13） | **C-16 v1.4 UNFREEZE**（F15：冻结文本未正面规定成员 entry） | 安全面语义扩展；需独立字节复核 | **推荐** |
| (b2) Host 自己按容器解码推导 locator/ordinal（zip `info.filename` + 自然序；PDF 页码） | Host 本地容器 | 同上（仍需接受 N 项） | 同上 + Host 复制 Core 规则（F24） | **漂移风险高**（locator 字符串/排序必须逐字节一致；重名/编码边角） | 不推荐 |
| (c2) 每成员 1 个**单 entry grant**（每次 Run 铸 N 个 grant） | 同 (a2) | **无需** Core 改动（F12/F13 保持） | 无 | 受 `MaxRunGrants=64` 上限（F29）→ 大容器不可用；grant 面膨胀；`_bindings` 逐 grant 记录 | 仅适合 ≤64 成员 |
| (d2) 「facts-only / identity 回退」匹配 | — | — | — | 2026-11-06 已被裁决否决（RUN-GRANT-1 U-A；见 `doc/handoffs/DSH-PROGRESS-2026-11-07.md:26`） | 否决 |

**结论（②）：** 数据侧最小 = 同 ① 的扫描响应缓存；**但 Core 侧必须改**（F12/F13 是硬编码「容器恰好 1 entry」）。因此 ② 的 **UNFREEZE 判定 = 需 C-16 v1.4**（**不需要** C-17、**不需要** C-06；pins 数仍 18，只重算 C16）。
若 DSH 希望**完全不 UNFREEZE**，唯一合法路径是 (c2) 每成员单 entry grant，并且必须接受「>64 成员容器仍不可用」这个 limitation——本评审不推荐（对一个 300 页 cbz 等于没修）。

### 2.3 UNFREEZE 判定汇总

| 卡 | 契约 | 需要 UNFREEZE？ | 触发点 | pins |
|---|---|---|---|---|
| 2A（version 通道，Host-only） | 无 | **否** | 零契约字节变更；`doc/plan`/`doc/contracts` 应零 diff | 18/18 不变（应仍 PASS） |
| 2B（容器成员 entry） | **C-16**（§2 四维 scope 说明 + §2.4 逐页匹配语义澄清） | **是 → v1.4** | F12/F13 现状与 F15 文本空白 | C16 pin 重算，对象数仍 18；C06/C17 零 diff |
| 2C（长 Run 续期） | 可能 C-16（TTL 语义）+ 新编排 | 待设计；**不建议本轮** | F28 300s 硬上限 | — |
| 2D（R3-02 委托行） | 无 | 否 | 测试-only | 18/18 |

---

## 3. Q2 拆卡与范围

### 3.1 拆卡建议（推荐 4 张，按顺序）

| 顺序 | 卡 | 一句话目标 | 依赖 | UNFREEZE |
|---|---|---|---|---|
| 1 | **FEA-11-RUN-GRANT-2A**：生产 version 通道 | 让生产 Host 用 **Core 权威** `version_id` 铸造 Run 授权 grant（缓存扫描响应 + 冷缓存有界 on-demand 扫描），使 image / folder / 归档首成员在**生产 path 上**真正可用 | RUN-GRANT-1（done） | 无 |
| 2 | **FEA-11-RUN-GRANT-2B**：容器成员 entry 通道 | 让 zip/cbz/pdf 的**任意成员页**可授权：Core 接受 1..N 容器 entry（逐项匹配、无路径回退），Host 按 Core 权威 locator/ordinal 铸 N 项 | 2A；C-16 v1.4 冻结 | **C-16 v1.4** |
| 3 | **FEA-11-RUN-GRANT-2C**：长 Run 授权续期（独立设计卡，非实现卡） | 设计 >300s Run 的 grant 重铸/重绑与原子性（或明确永久 limitation） | 2A/2B | 待设计 |
| — | **R3-02**（并入 2A） | 判别 `AcceptRunAsync → AuthorizePreparedRunForAcceptAsync` 的**委托行**本身 | — | 无 |

**理由：** 2A 是 P0 生产阻断且零契约风险，能独立验收、独立回滚；2B 触及冻结安全面，需要独立 UNFREEZE 周期与字节复核，混在一张卡会让「契约重冻 + Host 编排 + Core 语义」三重变更同时落地，不可判别。2C 的复杂度（时钟、预算、半途 grant 失效、与 Run 终态的竞态）会淹没 2A/2B 的验收面。

### 3.2 本卡（按 DSH 若坚持单卡）recommended In / Out

**In（若单卡）**
1. Host 源身份缓存：从 `ScanSourceSync` 响应缓存 `version_id` + `entries[]`（仅 `status=ok && changed=false`）；以 `source_id` 为键；仅内存；有界（R-8 同构上界）；冷缓存时**至多一次**有界 on-demand 扫描。
2. Run 铸造改用缓存版本；容器保持单 entry（2A 边界）。
3. Core 侧（仅 2B）：容器 scope 接受 1..N entry（逐项匹配，facts 必须等于容器身份；任一项不匹配 → 整体 typed 零写）；`_parse_scope` 与 `_scope_covers_entry` 同步；注册/匹配的 fail-closed 矩阵。
4. Host 侧（仅 2B）：容器按 Core 权威 entries 铸 N 项；`max_entries`/64 grant 上限的显式 typed 处理。
5. R3-02 收口（测试-only）。
6. 契约（仅 2B）：C-16 v1.4 UNFREEZE 载体 + 冻结记录 + pin 重算，独立 byte-level 复核。
7. 测试/证据/Handoff/卡面回填。

**Out**
- 长 Run 定期重铸/重绑（L-G1）——另卡；本卡不得宣称长 Run 可用。
- 加密源（L-G2）、Core 重启续跑（L-G9）、L-R11 两读面 gate 统一（L-G10）——均不碰。
- C-17 `ScanTarget` 扩展 / 新 host-control 命令（除非 DSH 明确改选 (b)/(c)）。
- UI/XAML/ViewModel/通知/本地化；`NewManga.App/**`；扫描调度语义重写；schema/迁移/依赖；真实用户数据；push。
- 任何 `scope.version` 的「猜测/回退」：**禁止** fallback 到 `"1"` 或从文件内容推断版本。

### 3.3 allowed_paths（文件级建议）

**2A（无 UNFREEZE）**
```
doc/tasks/FEA-11-RUN-GRANT-2.md
doc/reviews/FEA-11-RUN-GRANT-2-*.md
doc/handoffs/FEA-11-RUN-GRANT-2-*.md
verification/FEA-11-RUN-GRANT-2/**
apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs
```
（若新增独立缓存类型，建议 **新建** `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceIdentityCache.cs` 而非塞进既有文件。）

**2B（在 2A 基础上追加）**
```
doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
doc/plan/FEA-CONTRACT-FROZEN-C16.md
doc/reviews/CONTRACT-UNFREEZE-*-C16*.md
src/infrastructure/resource_channel/source_read_refs.py
tests/core/test_host_control.py
tests/fea11/test_source_run_grant.py
apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
```
**禁止面（两卡一致）：** `src/bootstrap/core_service.py`（除非 DSH 改选 (c) 新命令）、`schema.py`/迁移、依赖、`NewManga.App/**`、C-06/C-17 字节、Run wire / `CORE_PROTOCOL_MINOR`（仍 3）/ `AllowedRunErrorCodes`。

### 3.4 AC 草案（v3 口径：判别性 + fail-closed + 零漂移 + 门禁）

**2A**
- [ ] **AC-G1 生产版本通道（判别核心，P0）**：Host 铸造的 `scope.version` 来自 Core 权威数据；**禁止**常量 `"1"`。判别性：把缓存取值回退为 `"1"` → 目标用例必须 RED（Core 返回 typed `SOURCE_ACCESS_DENIED`，Run 不 dispatch）。真实 IPC：seed 后**不手工传 version**，由生产路径（扫描响应 → 缓存 → 铸造）取得；`authorize → bound_pages≥1 → resolve_page_resource` 成功。证据：IPC 日志 + discrimination。
- [ ] **AC-G2 缓存新鲜度与来源约束**：仅缓存 `status=ok` 且 `changed=false` 的 `version_id`/`entries[]`；`changed`/`encrypted`/`unsupported`/`missing` 一律**不更新**（从而不铸或 typed fail-closed）；缓存仅内存、以 `source_id` 为键、有界（断言上界与过期裁剪）。判别性：允许 `changed` 覆盖 → 用例 RED（版本与 binding 不匹配仍被铸出）。
- [ ] **AC-G3 冷缓存策略**：缓存缺失 → 每源至多 1 次有界 on-demand `ScanSourceSync`（超时/预算显式），失败/超时**跳过该源**并继续 dispatch（best-effort，不阻断 managed-only Run）；不得无限重试、不得静默回退占位版本。判别性：删除"跳过"分支 → managed-only Run 被阻断的用例 RED。
- [ ] **AC-G4 生产口径可用边界**：真实 IPC 证明 **image 单 entry + folder（逐成员）+ 归档首成员** 在**生产版本通道**下可用；多成员容器其余页仍 typed fail-closed（②未修），卡面/Handoff **不得**写成「referenced Run 全场景可用」。
- [ ] **AC-G5 managed 零回归**：沿用 RUN-GRANT-1 AC-R5 口径（Core 面 managed skip；Host best-effort 不阻断；managed 读/metadata 零变化），新增版本通道不改变 managed-only Run 行为。
- [ ] **AC-G6 R3-02 收口**：新增判别用例覆盖 `AcceptRunAsync` 对 `AuthorizePreparedRunForAcceptAsync` 的**委托行**；删除该委托 → RED。
- [ ] **AC-G7 零漂移**：`doc/plan`/`doc/contracts`/`schema.py`/依赖/`NewManga.App/**` **零 diff**；`CORE_PROTOCOL_MINOR=3`；Run wire 请求/响应键集快照不变；`verify_pins` 18/18；`check.ps1` PASS；API inventory EXIT=0；scope diff ⊆ allowed_paths。
- [ ] **AC-G8 门禁/证据/不夸大**：全量 pytest **不降**（基线 3281/10）、全量 .NET **不降**（基线 1551/0/89）、定向 + 真实 IPC 实跑记录；EV 每文件 sha256 + commit；Handoff 保留 L-G1/L-G2/L-G8/L-G9/L-G12（②）/L-G13，并新增"生产版本常量已修"的明确边界；不得把 2A 表述为 L-R1 修复。

**2B**
- [ ] **AC-H1 C-16 v1.4 UNFREEZE**：新增/澄清容器成员 entry 语义（`entries[]` 1..N；每项 `path` = 容器绝对路径、`locator`/`ordinal` = 成员身份、`facts` = 容器物理身份；Core 逐项匹配、无路径回退、任一不匹配整体 typed 零写）；独立 byte-level 复核 P0/P1=0；C16 pin 重算且 pins 仍 18/18；C06/C17 字节零 diff；冻结记录含 reviewed_head/复核 session。
- [ ] **AC-H2 Core 注册/匹配**：`_parse_scope` 接受容器 1..N（facts 必须一致于容器身份，不一致 → typed）；`_scope_covers_entry` 逐项匹配；`_bindings` 写入语义不变；fail-closed 矩阵（N 项中 1 项 locator 错 / facts 错 / entry 不在 version → 整体 typed、零写）。
- [ ] **AC-H3 Host 铸 N 项**：locator/ordinal 必须来自 Core 权威（扫描响应），**不得**由 Host 自行推断（若 DSH 允许推断，须有一致性判别测试 + 契约明文）；超出 `max_entries`/64 grant 上限 → typed，不截断。
- [ ] **AC-H4 真实 IPC**：≥3 成员真实 zip/cbz → 每个成员页均可 authorize 并 resolve；删/错一项 → typed `SOURCE_ACCESS_DENIED`；zero 越权（不可读到未授权成员）。
- [ ] **AC-H5 门禁/证据**：同 AC-G7/AC-G8。

---

## 4. Q3 测试与证据

### 4.1 现有 fixture 能否覆盖

| 能力 | 现状 | 覆盖结论 |
|---|---|---|
| 真实 zip / folder 容器 | `tests/fea11/test_source_run_grant.py:113-198`（真实 2 成员 zip + 真实迁移库）；`.NET` `Fea11RunGrantIpcTests` 真实 folder（`:250-330`） | **有**，但成员数少（2） |
| 真实 Core IPC | `Fea11RunGrantIpcTests`（opt-in `NEWMANGA_FEA11_IPC=1`，证据 3 passed） | **有**，但**版本是手工 `"sv1"`**（`:77-78`、`:297-298`）→ 不覆盖生产版本来源 |
| 多成员容器（entry 粒度） | Python `:514-547` 用 **手写 grant**（`locator="002-current.png", ordinal=1`）证明 entry 粒度；生产 Host 铸不出该形状 | **部分**：只能证明 Core 语义，不能证明生产可铸 |
| version 匹配 | 仅"手工传值相等"的用例 | **不覆盖**生产通道 |
| Core 权威 entries 缓存 | 无（Host 不缓存；F22） | **缺** |
| 多成员 >2 / cbz / pdf 页码 | 无 | **缺** |
| 缓存失效（changed/encrypted/missing） | 无 | **缺** |
| 冷缓存 on-demand 扫描 | 无 | **缺** |
| 生产 registry 形状（file-root） | 有：`SourceImportModels.cs:205-211` 生产注册 file 为 root；SCAN-2 scope review `:22,:82` 已确认 | **有**（可作为 2A 的注册前提） |

### 4.2 需要新增

1. **Host 单测**：身份缓存写入/读取/上界/过期裁剪；`changed=true` 不写；`status≠ok` 不写；冷缓存触发 1 次扫描且失败即跳过（fake executor 计数）。
2. **Host 单测**：`RunSourceRange.Resolve` 使用缓存版本（而非 `"1"`）；缓存缺失 → 不铸（或触发扫描）。
3. **真实 IPC（2A 判别核心）**：真实 Core + 真实 zip/folder；**不手工传 version**；走"扫描 → 缓存 → 铸造 → authorize → resolve"；并做一次「斜破坏」：把缓存回退常量 → RED。
4. **真实 IPC（2B）**：3+ 成员 zip/cbz 每个成员页 authorize + resolve；错误 locator/ordinal 一项 → typed；无越权读取。
5. **Core 单测（2B）**：容器 N entry 注册/匹配矩阵 + 原子性（部分匹配 → 零写）+ 幂等；`_parse_scope` 的 N=0/超限/重复 entry_key。
6. **R3-02**：`AcceptRunAsync` 委托行判别（删委托 → RED）。
7. **证据**：新增/更新 `verification/FEA-11-RUN-GRANT-2/**`（AC 矩阵、logs、discrimination、scope-validation、Resource Manifest、每文件 sha256）。

### 4.3 门禁成本与已知 flaky

| 门禁 | 基线 | 成本 | 注意 |
|---|---|---|---|
| 定向 pytest（host_control + source_run_grant） | 50 passed | ~8s | 可直接作为 AC-G1 判别面 |
| Host 单测（`~SourceRegistry`） | 21 passed | 秒级 | 2A 会新增用例 |
| 真实 IPC（`NEWMANGA_FEA11_IPC=1`） | 3 passed / 未设 env 时 3 skipped | ~4s + Core 启动 | **必须**新增"生产版本路径"用例，否则 2A 无判别证据 |
| 全量 pytest | 3281/10 | 数分钟 | 跑后 `git checkout -- verification/FEA-09`（会重写 tracked `wire-redacted.ndjson`） |
| 全量 .NET | 1551/0/89 | 数分钟 | 同上 |
| pins / check / API inventory / scope_validation | 18/18、PASS(3w)、EXIT=0、PASS | 秒级 | 2B UNFREEZE 会重算 C16 pin（对象数不变） |
| 已知 flaky | — | — | `FluentResidual2VisualEvidenceTests`（`verification/` 写入时 git-status 快照竞态）；`library.db-shm` 锁；`test_sandbox_job_kills_grandchildren`——首跑失败须如实记录 + 隔离复跑，不得静默重试 |

---

## 5. Q4 风险与 limitation（至少含指定项）

1. **C-16 UNFREEZE 风险（2B）**：容器 entry 从 1 → 1..N 是**授权接受面**的变化；若实现把「任一 entry 命中」写成「任一 entry 的 locator/ordinal 命中而 facts 不校验」，等于放宽越权面。必须：facts 必须等于容器身份（F30）、无路径回退、任一项失败整体拒、独立 byte-level 复核、pins 重算。**C-17 不需要 UNFREEZE**（若选 (b) 才需要，且要注意 §5「新字段须新能力」）。C-06 不需要。
2. **Host 缓存失效 / 多源**：缓存键必须 `source_id`（同 bytes 不同物理源是不同 source，C-17 §5.3）；版本过期/容器变更 → typed 拒绝（fail-closed），**绝不允许**回退 `"1"`；缓存必须有界（R-8 同构）；一个 Run 可能覆盖 64 源上限（F29），超出必须 typed/跳过并记录计数。
3. **加密源（L-G2）**：扫描返回 `encrypted` → 无 version/entries → 不铸 → typed `SOURCE_PASSWORD_REQUIRED` 语义不变；2A/2B **不得**顺手实现密码通道。
4. **长 Run（L-G1）**：单 grant ≤300s（F28）不变；2A/2B 不得宣称长 Run；Run 超窗仍是 fail-closed；续期另卡。
5. **Core 重启（L-G9）**：`_grants`/`_bindings` 在进程内 → 重启后丢失；version 缓存本身是 DB 持久值（重启后仍有效），但**授权必须按 Run 重建**；已开始 Run 不可续跑（既有 limitation 保留）。
6. **重复注册 / 多项目**：`source_id` 为唯一权威（S-2；`SourceImportModels.cs` 的 `StableSourceId` 已被 SCAN-2 废弃）；`project_ids` 1..20；`scope=all` 扫描要求 project 集与冻结引用集**完全相等**，否则 `SOURCE_PLAN_STALE`——Host 必须使用 `ScanTarget.project_ids`，不得自行裁剪。重复 root 注册会被 `FindOrRegisterRootAsync` 复用（避免 registry 无界增长），但 2A/2B 仍须断言「同一 source_id 只铸 1 个 Run grant」。
7. **证据夸大（最高风险）**：RUN-GRANT-1 的「可用边界」是**测试口径**。2A 的验收证据必须是「version 经生产路径取得」的 IPC；不得引用既有 `"sv1"` 手工用例作为生产可用性证明；不得把 2A 写成 L-R1 修复；不得把 2B 之外的容器页写成可用。
8. **性能（L-G8 延伸）**：冷缓存扫描 = 每源 1 次容器哈希（大文件线性）；应计入 L-G8 并记录预算（例如 64 源 × 容器大小），不得静默无界。
9. **schema/迁移零漂移**：2A/2B 都**不需要** schema 变更（缓存仅内存）；任何「为缓存加表」的方案都应被拒绝（违反 In/Out）。

---

## 6. Q5 优先级（与其它候选对比）

| 候选 | 性质 | 生产影响 | 建议 |
|---|---|---|---|
| **RUN-GRANT-2A（version 通道）** | P0 生产阻断 | **任何 referenced Run 起不来**（F1–F10） | **立即优先**（小而独立、零 UNFREEZE、可判别） |
| RUN-GRANT-2B（容器成员） | P1 功能缺口 | 多成员容器仅首成员可用 | 2A 之后；需 C-16 v1.4 |
| **L-S1（registry resilience）** | P1 可用性 | file-root 缺失/替换 → 整个 registry `SOURCE_REGISTRY_UNAVAILABLE`（SCAN-2 scope review `:22`） | 2A 之后、2B 并行候选（与 2A 无文件冲突，但会碰 registry 语义） |
| L-S4（`refresh_source_location_auth` 死代码） | P2 正确性 | 撤销/重注册后 Core location auth 不更新 | 可穿插（小） |
| L-R11（两读面 gate 统一） | P2 一致性 | 只在「无 publication 行」判定差异处显形 | 2B 之后（避免与 2B 的 gate 语义交叉） |
| C-04b 文档 residual（8 项） | P3 文档 | 无运行时影响 | 任何空档 |
| SCAN-2 RH-1…RH-5 | P2/P3 扫描/状态正确性 | 扫描状态/覆盖的边角 | 与 2A 无耦合，可穿插 |

**结论：** RUN-GRANT-2（先 2A）**应优先**。理由：(i) 它决定「referenced Run 能否启动」，比 L-S1 的窄失败模式影响面更大；(ii) 2A 改动面小、无契约风险、可在一次交付内完成并判别；(iii) L-S1/L-S4/L-R11/C-04b/SCAN-RH 都不解决「生产 Run 起不来」，并行或穿插即可，不应抢占 2A 的窗口。不建议现在启动 2C（长 Run）。

---

## 7. Q6 裁决所需输入（DSH/Codex 决策项，附推荐）

| ID | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | 是否确认 F1–F10 = **生产 referenced Run 100% 在 dispatch 前被拒**（Run 不启动），并据此修正 L-G12① 措辞（现文读起来像"边界收窄"，实际是"完全阻断"）？ | **确认**；L-G12① 改写为"生产 version 恒定 `\"1\"` → 授权恒拒 → Run 不 dispatch"；必要时登记新 limitation L-G15 | 卡面/STATUS/Handoff 口径；后续优先级 |
| **D-2** | 单卡还是拆卡？ | **拆 2A/2B/2C**（R3-02 并入 2A） | 交付节奏、UNFREEZE 独立周期 |
| **D-3** | ② 的契约路线：C-16 v1.4 UNFREEZE（明文容器成员 entry），还是裁决"冻结文本已允许、按实现缺陷修"？ | **C-16 v1.4 UNFREEZE**（授权接受面变化需要明文 + 独立字节复核；F15 显示文本未正面规定） | pins 重算、冻结记录、复核成本 |
| **D-4** | ① 的数据通道：扫描响应缓存（(a)），还是 C-17 `version_id` 字段（(b)），还是新 C-16 命令（(c)）？ | **(a)**（零契约变更，Host-only；F18/F22） | 是否触发 C-17 UNFREEZE |
| **D-5** | 冷缓存策略：Run 期有界 on-demand 扫描 vs 无版本即 typed 拒绝 | **有界 on-demand（每源 1 次，超时/预算上限，失败跳过）** | 首次 Run 的可用性 vs 成本 |
| **D-6** | 2B 的 entry 上限与超限行为：沿用 `max_entries=10000` / 64 grant？超限 typed 还是跳过该源？ | 沿用上限；超限 → **跳过该源并计数**（Run 由 Core 对目标页 fail-closed），不截断 | 大容器行为 |
| **D-7** | 2B 是否允许 Host 自行推导 locator/ordinal？ | **不允许**（必须 Core 权威；F24 说明规则在 Core 侧） | 漂移风险 |
| **D-8** | 2C（长 Run 续期）本轮是否只登记 limitation 并另立设计卡？ | **是**（避免把 2A/2B 拖成高复杂卡） | 交付范围 |
| **D-9** | Owner 与审查者任命：`suggested_owner: codex` 是否沿用？审查者需独立上下文（可为 DSH 派发的 fresh subagent） | 沿用 Codex（或 DSH 指定）；审查者独立上下文、只读 delivery head | 协作与独立性 |

---

## 8. 真实性声明

1. **审查者身份与来源**：本会话是父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a` 派发的**独立上下文子会话**；未参与 `FEA-11-RUN-GRANT-1` 的实现/返修/审查，也未参与 `FEA-11-RUN-GRANT-2` 的任何实现。本会话只读：**只写本文件**，未修改任何生产代码、测试、契约、卡、STATUS、PLAN、LEDGER，未 `git add/commit/push`，未创建 worktree，未删除/移动任何资源。
2. **实测命令**（全部只读）：`git rev-parse HEAD`、`git status --porcelain=v1`（两次）、`git log --oneline`、`git show --stat 3dc239d26`、`git diff --name-only b2261825e..HEAD`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（PASS 18/18）、`pwsh -NoProfile -File tools/governance/check.ps1`（PASS 3 warnings）、以及 `Select-String`/文本读取（scanner.py、core_service.py、source_read_refs.py、SourceReadCoordinator.cs、HostRuntime.cs、SourceScanScheduler.cs、HostCommandDispatcher.cs、SourceImportModels.cs、tests、EV、r3、C-16/C-17/C-06、FROZEN/pins、STATUS、handoff）。
3. **NOT_RUN**：定向 pytest、全量 pytest、全量 .NET、`NEWMANGA_FEA11_IPC=1` 真实 IPC、`generate_api_inventory.py --check`、`check.ps1 -TaskPath`、`scope_validation.py`、判别性脚本。原因：只读授权与「只写一个文件」的硬约束（全量门禁会重写 tracked `verification/FEA-09` 字节，需 `git checkout` 恢复）。因此本文对门禁数字只做**引用**（注明来源），不作实测断言。
4. **证据优先级**：本文所有结论以**仓库真实字节**（代码/测试/契约/pins/Git）为准；Handoff/EV 自述仅在被明确标注为「文档声称」时引用，不作为事实来源。
5. **基线偏差如实记录**：任务书称 `b2261825e` clean，实测该 HEAD 工作树存在未跟踪 handoff；评审期间 HEAD 前进到 `3dc239d26`（docs-only）。本文 `reviewed_head` 取实测值；代码/契约/pins 与该 docs 提交无关，`git diff --name-only b2261825e..HEAD` 仅 1 个 handoff 文件。
6. **未宣称**：本文不宣称 2A/2B 已实现、不宣称 referenced Run 生产可用、不宣称 ② 已修、不宣称长 Run 可用；也不对 `verification/**` 中未复核的数字背书。

---

## 9. 建议的下一步

DSH 裁决 D-1…D-9 后：若采纳拆卡与推荐路径，先冻结 **2A**（无 UNFREEZE，allowed_paths 见 §3.3），Owner 实现后用 §3.4 的 AC-G1…G8 做独立 Review；**2A 通过后**再启动 **2B** 的 C-16 v1.4 UNFREEZE 周期（独立 byte-level 复核 + pin 重算），不得先改实现后补契约。
