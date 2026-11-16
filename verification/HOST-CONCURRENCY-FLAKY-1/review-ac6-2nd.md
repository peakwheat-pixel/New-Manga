# HOST-CONCURRENCY-FLAKY-1 AC6 二次独立复核

- 被审 head: `9ce819ae7`
- 分支/仓库: `main` / `G:\CODEX\New Manga`
- 复核者: `reviewer-hcf2`（独立上下文子 agent，全新上下文，未复用 reviewer-hcf 的会话）
- 复核时间: 2026-11-16T09:53+08:00
- 复核方式: 只读（`git log/show/cat-file/grep`、读代码/日志/TRX、只读 `check.ps1`；**未重跑 `test.ps1` / `dotnet test`**）
- 上一轮报告: `verification/HOST-CONCURRENCY-FLAKY-1/review-ac6.md`（361 行，被审 head `277406eeb`）

## 结论

**CHANGES_REQUESTED**

1. **代码侧可以放行**：P0-1 的补修经我独立复核**正确且完整** —— 两处 wire facts 写入点确实套了 53 位归一化（`SourceReadCoordinator.cs:408` / `:632`），语义是"mask 喂给 Core 的 wire 值、保留 registry 的 raw 本体"，Python 侧全部 comparator 已是在 masked 口径上比较，补偿链路成立；`TileChannel.cs:437` 经查**不参与跨语言 identity 比较、不构成同源风险**，不需要在本卡修。
2. **证据 pin 的 commit 列确已修对**：18/18 行 `git cat-file -e <commit>:<path>` 全部返回 0，且每行用 `git log --diff-filter=A` 反查到的实际引入提交与卡面**逐一相同**；EV-HCF-16/17/18 的 sha256 与 blob 实算值**一致**；EV-HCF-14/15 的因果顺序正确（commit 等于修复提交本身，日志生成于提交前 49 秒）。
3. **但上一轮 P1-2 明确要求修掉的卡面自相矛盾仍在**：AC 行（L82）已改为 `<<PARTIAL>>`，正文 L443 却仍写「**AC4 现在 MET**（两处缺陷都已修并验证）/ AC1 MET / AC5 MET」——同一文件两处状态冲突，未处置完成。
4. **新发现（门禁级）**：AC 标记格式不合规 —— AC1/AC4/AC5 三行均为 `- [x]` + `<<PARTIAL: …>>`，违反 `doc/09_COLLABORATION.md` §4.3 的勾选一致性表（`[x]` 只允许 `MET`/`NOT_APPLICABLE`）；AC6 行**缺状态标记**。`check.ps1` 现在 PASS 只是因为 `status: proposed` 不触发 §4.3 门禁；一旦进 `in_review`，该卡会因 4 条错误 FAIL。
5. P1-1 的 sha256 列仍 15 行 `PIN_PENDING`（模板要求 `BLOB` 字节校验，pin 仍不可校验）；P2-1/2/3/4/5 **全部未处置**；P1-3/P1-4 只"在处置节追加更正"，卡面正文（L71-72、L370-375、L445-450）与 `ac1-ac3-diagnosis.md:103` 的旧表述**原文未改**。
6. 另：P0-1 修复后没有任何直接测试覆盖（`test.ps1` 不设 `NEWMANGA_FEA11_IPC`，覆盖 source-read 路径的 IPC 测试仍被 skip；`after-p0-fix.log` 的绿只能证明"不退化"，不能证明"已修好"）。

因此：**代码修复可接受、保留；文档/证据/AC 门禁需再修一轮**后才能把本卡推进到 `in_review` 并关闭 AC6。

---

## 上一轮 findings 的逐条处置判定

| Finding | 上一轮要求 | 作者处置 | 我的判定 | 依据 |
|---|---|---|---|---|
| **P0-1** producer 遗漏 | 修 `SourceSecurity.Identity` 流入 source-read wire facts 的 raw/masked 对撞；另评估 `TileChannel.cs:437` | `bbeb28dcb` 在两处写 wire facts 处套 `SourceSecurity.NormalizeFileId`（新增 `CoreFileIdMask`/`NormalizeFileId`），**刻意不改** `Identity` 本体；TileChannel 标"待评估" | **已解决**（代码正确、完整、语义正确） | §1 全链路核对；Python comparator 全部 masked；registry 用途核实 |
| **P1-1** 证据 commit 列 15/15 错位 + sha256 全 PIN_PENDING | commit 列改为实际引入提交；补 sha256 | 15 行 commit 全部更正，新增 EV-16/17/18 也按同规则填；**sha256 列未补** | **部分解决**（commit 列已解决；sha256 列未解决） | §3 逐行校验：18/18 cat-file + A 提交一致；15 行仍 `PIN_PENDING` |
| **P1-2** AC4/AC5 标记与证据不匹配 + 卡面自相矛盾 | AC4 恢复 `<<PARTIAL>>`；修 L82 与 L440 的矛盾；AC5 改写判据或补裸跑日志 | AC4/AC5 已改 `<<PARTIAL>>` 并加原因；**正文 L443 旧状态未改**；AC5 判据文本未改写 | **部分解决** | L82 与 L443 仍冲突；L83 仍写「331/0/74」 |
| **P1-3** AC1 缺项 + 「并行」叙事被证伪 | AC1 降 PARTIAL；更正 L70-72 与 `ac1-ac3-diagnosis.md:103` | AC1 降 `<<PARTIAL>>`；处置节新增叙事更正；**正文 L71-72 与 diagnosis:103 原文未改** | **部分解决** | 见 §4；`61a16159e` 只追加卡面，未改 diagnosis |
| **P1-4** 「任何用户/唯一」绝对化表述 | 下调；连带改 `GOAL-WRAPUP-R100.md` | `07a8f828b` 已更正 handoff；卡面**正文 L370-375、L445-450 原文未改**（只在处置节 L512-518 追加更正） | **部分解决** | handoff ✅；卡面正文仍自相矛盾 |
| **P2-1** 控制字符损坏 | 修 TAB/VT | 未处置 | **未解决** | 11 TAB + 2 VT 仍在（§4） |
| **P2-2** front-matter/标题陈旧 | 更新 status/owner/reviewer/标题 | 未处置 | **未解决** | L3 仍「待定位」；L6/8/9 仍 proposed/null/null |
| **P2-3** `AcquireLockFile` 最坏等待 ~10s 未说明 | 注释/卡面写清总上界 | 未处置 | **未解决** | `SourceAccessRegistry.cs:347/382` 两段独立 5000ms；注释未写总上界 |
| **P2-4** 常量一致性测试 | 加测试 pin | 未处置 | **未解决** | `git grep NormalizeFileId\|FileIdMask\|CoreFileIdMask -- apps/desktop-avalonia/tests` 为空 |
| **P2-5** `test.ps1` 覆写 workspace evidence 目录副作用未登记 | 登记 | 未处置 | **未解决** | 卡面 L452-457 只登记 READER-OVERLAY 的 git 工作区污染；未登记 `task-envs/HOST-RESOURCE-SECURITY-1/evidence-rerun` 被覆写（本轮再次发生，见"未能独立验证"） |

---

## 逐项核查

### 1. P0-1 补修正确性

#### 1.1 两处归一化确实存在且语义正确

| 声称 | 实际（HEAD `9ce819ae7`） | 判定 |
|---|---|---|
| `SourceReadCoordinator.cs:408` 单文件 | `:407` `["volume_serial"] = before.Volume,` / `:408` `["file_id"] = SourceSecurity.NormalizeFileId(before.Id),` | ✅ |
| `SourceReadCoordinator.cs:632` 批量 entries | `:629` volume / `:632` `["file_id"] = SourceSecurity.NormalizeFileId(before.Id),` | ✅ |
| 新增 `CoreFileIdMask` / `NormalizeFileId` | `SourceSecurity.cs:138` `public const ulong CoreFileIdMask = (1UL << 53) - 1;`、`:154` `public static ulong NormalizeFileId(ulong rawFileId) => rawFileId & CoreFileIdMask;` | ✅ |
| **不改** `SourceSecurity.Identity` 本体 | `SourceSecurity.cs:123-128` 仍返回 `(info.Volume, ((ulong)info.IndexHigh << 32) | info.IndexLow, …)`（raw） | ✅ 与声称一致 |

**语义核对**：`before`/`after` 在同一函数内仍是 raw 自比（`:401`/`:622` `if (after != before) throw FILE_IDENTITY_CHANGED`），mask 只发生在写入 JSON wire facts 的那一行；`before.Volume` 是 `uint` 扩宽而来（`ulong`，天然 32 位），无需 mask。这符合 `identity.py:16/20` 的 `_VOLUME_MASK=0xFFFFFFFF` / `_FILE_MASK=(1<<53)-1`。

**行号漂移记录**：上一轮报告与卡面引用的 `:404/624` 是 `bbeb28dcb` **加注释前**的位置；加注释后实际为 `:408/:632`（+4/+8）。卡面 L82 注释、L484 处置节、`GOAL-WRAPUP-R100.md` 仍引用旧行号，属于引用未刷新（不构成事实错误，但应一并修正）。

#### 1.2 全 producer 表（C# 侧，独立用 `git grep` 穷举后逐个判定）

搜索式：`GetFileInformationByHandle|FileIndexHigh|IndexHigh|VolumeSerialNumber|volume_serial|file_id|file_index|st_ino|st_dev`（`apps/desktop-avalonia/src` + `src/`）。

| # | producer 位置 | 是否 mask | 跨语言（C#↔Python）identity 比较 | 判定 |
|---|---|---|---|---|
| 1 | `NewManga.CoreClient/Issuer/HostIssuer.cs:563` 文件 identity | ✅ `NormalizeFileId` | 进 import grant facts → `import_source_refs.py:349-359` → `scanner.py:163-171` / `source_strict_read.py:20-36` | 已修（上一轮） |
| 2 | `HostIssuer.cs:596-597` 目录 identity（`scope_identity`） | ✅ `NormalizeFileId` | → `import_source_refs.py:305` `normalize_identity(...) != grant.scope_identity`（两侧 masked） | 已修（上一轮） |
| 3 | **`NewManga.Host/Sources/SourceSecurity.cs:123-128` `Identity(...)`** | ❌ raw（**刻意**） | 经 `SourceReadCoordinator` 写入 source-read grant facts 时（现）masked；registry/scheduler 侧同进程 raw 自比 | ✅ 本卡 P0-1 已处置 |
| 4 | `NewManga.Host/Resources/TileChannel.cs:430-438` `FileIdentity.Read`（`:437` raw `long`） | ❌ raw | **否**（详见 §2） | 本卡不需修；已登记潜在风险 |
| 5 | `apps/desktop/src-tauri/src/resource_protocol.rs` / `host_issuer.rs`（Rust legacy） | ❌ | 属 Tauri legacy 架构，AD-002/AD-003 已退出当前产品路径，`test.ps1` 不构建 | 非当前 producer |
| 6 | `tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:1150`（测试 helper 直接 probe） | ❌ raw | **是**：`UpdateLocationRow`（`:1021-1049`）把 raw file id 直接写 `source_locations`，随后被 Python 与 masked grant facts 比较 | **新发现 P2**（opt-in 测试口径未同步，见 §5） |

Python 侧（比较点/契约，逐一读原文核对）：

- `scanner.py:99` `_stat_folder_entry` → `normalize_identity(st_dev, st_ino)`；`:163-171` 与 `facts.file_id` 比较 → 两侧都 masked ✅
- `source_strict_read.py:20-31`（Windows）`hr._identity_of(handle)` 已 mask（`handle_resolver.py:158-165`），与 `facts.volume_serial/file_id` 比较 ✅；`:45-56`（非 Windows）`normalize_identity` 后再比 ✅
- `source_read_refs.py:1061-1080` `_facts` **原样透传**，只校验"非负 int"，不 normalize —— 因此 Host 侧**必须**写 masked 值（本卡补修正是这一点）✅
- `source_read_refs.py:639-657` `_location_matches` 与 `:659-…` `_folder_scope_covers`：grant facts vs `source_locations`（DB 事实）——见 1.3 的补偿证据
- `application/sources/service.py:479-496`（relink）、`:733-737`（`_ensure_target_version`）、`:973-977`（`_location_auth_refresh`）、`application/sources/reattest.py:221-226`：都是 grant facts vs location facts，**全部原样整数比较、不 normalize**
- **关键补偿事实**：`source_locations` 的事实全部来自 Host grant facts —— import 首次写入走 `application/importing/referenced/runtime.py:618-621`（`find_source_by_physical_identity(content_digest, _volume_serial(resolved), _file_id(resolved))`）与 `service.py:746-760`（从 `grant facts` 写列），而 import grant 的 facts 由 `HostIssuer` 的 `FileIdentity`/`DirectoryIdentity` 产生，**早已是 masked**。因此 Core 的 DB 事实本来就是 53 位口径；P0-1 修复把 source-read wire facts 拉到同一口径，**不会引入新的 DB/grant 不一致**，反而修掉了"source-read grant 恒不匹配 location/reattest"这条更长的失败链。

**结论：C# 侧对跨语言 identity 有贡献的 producer 只有 HostIssuer（file/dir，已 masked）与 SourceReadCoordinator 的两处 wire facts（本卡已 masked）；无其他遗漏 producer。**

#### 1.3 不改 `Identity` 本体的取舍是否正确

作者理由："`Identity` 还被 `SourceAccessRegistry.cs:49`（写 `SourceRoot.FileId` → `registry.v1.dat`）、`:137-141`（校验）与 `SourceScanScheduler.cs:1730/1742` 使用；单边 mask 会让既有 registry 全部报 `SOURCE_REGISTRY_UNAVAILABLE`。"

我逐处核对了实际用法：

- `SourceAccessRegistry.Register`：`:49` `var identity = SourceSecurity.Identity(path);` → `:50` `new SourceRoot(path, identity.Volume, identity.Id, now, true)` → `Save` 持久化。**raw 值**写入 registry.v1.dat。
- `VerifyRootIdentity`：`:137` 再 probe → `:140-141` `if (identity.Volume != root.VolumeSerial || identity.Id != root.FileId) throw SOURCE_REGISTRY_UNAVAILABLE`。**raw vs raw 自洽**。
- `SourceScanScheduler`：`:1727-1747` 同样以 registry 中 raw `root.FileId` 与现场 probe 比。
- `SourceRootReattestPlanner.cs:212`、`HostOperationOrchestrator.cs:122/286`、`SourceOperationCoordinator.cs:284-410` 只使用 `Root` 路径或 Core 给的 `identity_digest`，**不把 volume/file id 发给 Python**（`git grep` 无 `source_register` 类跨语言通道）。
- 因此若把 mask 放进 `Identity`：`Register` 写 masked、旧文件里 raw 与 masked 在 `id > 2^53` 时不等 ⇒ 对**已存在**的 registry 报 `SOURCE_REGISTRY_UNAVAILABLE`；mask 不可逆，无法自动迁移。

**判定：取舍正确**（跨语言边界归一、Host 持久化本体保持原语义，分层正确）。**但作者理由的影响面表述过强**：`v0.1.1`/`v0.1.1-v11r` tag（2026-10-29/30）不含 `SourceAccessRegistry.cs`（该文件 2026-11-03 才由 `995d80ca5` 引入，`git cat-file -e v0.1.1:…` 返回 128），因此"既有**用户** registry"在发布产品意义上并不存在；真正受影响的是本机既有 dataRoot（开发自测）与"持久化格式语义变更需契约裁决"这一点。建议把理由改为"①契约口径只在跨语言边界统一；②Host 持久化事实保持 C-15 v1.5 §5 语义，改语义需版本迁移"更稳。

### 2. `TileChannel.cs:437` 同源风险判定（明确结论）

**结论：`TileChannel.cs:437` 不参与跨语言 identity 比较，不构成 `FILE_IDENTITY_CHANGED` 同源风险，本卡不需要修；但应登记为"潜在风险 + 契约约束注释"。**

证据链（逐条读代码）：

1. `FileIdentity.Read`（`:430-438`）返回 `(long VolumeSerial, long FileIndex)`，`:437` 用 `((long)info.FileIndexHigh << 32) | info.FileIndexLow`，raw。调用点只有两处：`Issue()` `:139` 与 `ReadTile()` `:196`。
2. `Issue()` `:140-148` 的 expected 值来自 `TileGrantRequest.VolumeSerial/FileIndex`（`:60-61` 两个 `long?` 可选参数，默认 null）。**唯一生产调用点** `HostRuntime.cs:1044-1050` 只传 6 个位置参数（`resolved.ResourceId, resolved.Revision, absolutePath, root, grant.Size, tiles`），**未传** VolumeSerial/FileIndex ⇒ 比较分支不生效。测试侧 `git grep "VolumeSerial:\|FileIndex:" apps/desktop-avalonia` 无传参调用；`D4SecurityHarnessTests.cs:270` 只断言 `TileGrantRequest` 的公开属性名集合（契约断言，不能删字段）。
3. `ReadTile()` `:196-200` 比较的是 `FileIdentity.Read(fileHandle)` 与 `Grant.VolumeSerial/FileIndex` —— 后者由**同一 `Issue()` 内的 `FileIdentity.Read`** 在 `:166-167` 写入。同进程、同 API、同 raw 口径的**自比**，不会因 Core 的 masked 值而误报。
4. `TileGrantView`（`:64-71`）与 `ToView`（`:318-325`）**不含** VolumeSerial/FileIndex（也不泄漏 OS 路径/digest），所以不存在"Host 内部值泄漏到 UI/Core"。
5. `HostBridgeClient.cs:10-18` `BridgeGrant` 确实有 `long VolumeSerial, long FileIndex`：
   - **谁写**：`HostBridgeClient.ResolveAsync` `:179-201` 从 Core `resolve` 响应读 `volume_serial`/`file_index`；Core 侧是 `src/infrastructure/resource_channel/host_bridge.py:103-116` 的 `"volume_serial": grant.facts.volume_serial`，而 `grant.facts` 来自 `handle_resolver.capture_facts`（`:296-324`，`_identity_of` **已 normalize**）。⇒ BridgeGrant 的这两字段是 **Python masked 值**。
   - **谁消费**：生产代码**零消费**（`git grep "grant.VolumeSerial\|grant.FileIndex"` 无结果；唯一 `ResolveAsync` 调用点 `HostRuntime.cs:1030` 只用 `ScopeClass/Size/RelPath/Sha256`）。仅测试 `HostBridgeIntegrationTests.cs:32-33` 断言 `> 0`（非 identity 比较）。
   - **是否与 TileChannel 同源**：**否**。若未来有人把 `BridgeGrant.VolumeSerial/FileIndex` 接进 `TileGrantRequest`，就会变成"Python masked vs 本地 raw"的比较，对 `raw > 2^53` 的文件误报 `TileIdentityMismatch`（不是 `FILE_IDENTITY_CHANGED`，也不是跨语言比较——数据源是 Core 值但比较发生在 Host 内）。
6. 附带：`:437` 的 `(long)info.FileIndexHigh << 32` 用 `long` 承载 64 位 index，当 `IndexHigh >= 0x80000000` 时溢出为负数；但由于只用于同侧自比（`Issue` 记录 → `ReadTile` 复比），符号一致不影响判定。**不是本卡问题**，可在未来把 `FileIdentity` 统一改成 `ulong` + `NormalizeFileId` 时一并清理。

**建议**：AC4 的 `<<PARTIAL>>` 原因"TileChannel 同源风险待评估"可以在下一轮改为"已评估：不参与跨语言比较，无需修；已在 `TileChannel.FileIdentity` 加注释说明与 Core 契约的关系"。

### 3. 证据 pin 18 行逐行校验

校验方法：从卡面 L134-151 解析 18 行；对每行执行
`git cat-file -e "<commit>:<path>"`（0=存在）
与 `git log --diff-filter=A --format=%h -- <path>`（反查实际引入提交）；
对非 `PIN_PENDING` 行，用 `git cat-file blob <commit>:<path>` 的原始字节实算 SHA-256。全部命令只读。

| # | evidence_id | path（后缀） | 卡面 commit | `cat-file -e` | `--diff-filter=A` 实测引入提交 | sha256 列 | 判定 |
|---|---|---|---|---|---|---|---|
| 1 | EV-HCF-01 | code-evidence.log | 84b4a2456 | 0 | 84b4a2456 | PIN_PENDING | commit ✅ / sha ❌ |
| 2 | EV-HCF-02 | ac2-repro.md | fbf704a37 | 0 | fbf704a37 | PIN_PENDING | commit ✅ / sha ❌ |
| 3 | EV-HCF-03 | repro-1.log | fbf704a37 | 0 | fbf704a37 | PIN_PENDING | commit ✅ / sha ❌ |
| 4 | EV-HCF-04 | repro-2.log | fbf704a37 | 0 | fbf704a37 | PIN_PENDING | commit ✅ / sha ❌ |
| 5 | EV-HCF-05 | after-fix.log | e66323bf2 | 0 | e66323bf2 | PIN_PENDING | commit ✅ / sha ❌ |
| 6 | EV-HCF-06 | build.log | e66323bf2 | 0 | e66323bf2 | PIN_PENDING | commit ✅ / sha ❌ |
| 7 | EV-HCF-07 | correction-skip-vs-pass.md | ac434d911 | 0 | ac434d911 | PIN_PENDING | commit ✅ / sha ❌ |
| 8 | EV-HCF-08 | solo-detail.log | ac434d911 | 0 | ac434d911 | PIN_PENDING | commit ✅ / sha ❌ |
| 9 | EV-HCF-09 | file-identity-diagnosis.md | 062918039 | 0 | 062918039 | PIN_PENDING | commit ✅ / sha ❌ |
| 10 | EV-HCF-10 | st-ino-measured.md | 4b1198443 | 0 | 4b1198443 | PIN_PENDING | commit ✅ / sha ❌ |
| 11 | EV-HCF-11 | probe_st_ino.py | 4b1198443 | 0 | 4b1198443 | PIN_PENDING | commit ✅ / sha ❌ |
| 12 | EV-HCF-12 | st-ino-probe-output.log | 4b1198443 | 0 | 4b1198443 | PIN_PENDING | commit ✅ / sha ❌ |
| 13 | EV-HCF-13 | root-cause-proven.md | c75740cb9 | 0 | c75740cb9 | PIN_PENDING | commit ✅ / sha ❌ |
| 14 | EV-HCF-14 | after-identity-fix.log | 277406eeb | 0 | 277406eeb | PIN_PENDING | commit ✅ / sha ❌ |
| 15 | EV-HCF-15 | build-r99.log | 277406eeb | 0 | 277406eeb | PIN_PENDING | commit ✅ / sha ❌ |
| 16 | EV-HCF-16 | review-ac6.md | bbeb28dcb | 0 | bbeb28dcb | ca480b62…fbee | ✅ MATCH |
| 17 | EV-HCF-17 | after-p0-fix.log | bbeb28dcb | 0 | bbeb28dcb | c9ff683c…695d | ✅ MATCH |
| 18 | EV-HCF-18 | build-p0.log | bbeb28dcb | 0 | bbeb28dcb | 5a1e9523…0cef | ✅ MATCH |

**因果顺序（EV-HCF-14/15/17/18）**：

- EV-HCF-14/15 commit = `277406eeb` = HostIssuer 修复提交**本身**（该 fix commit 同时含代码与证据）。`after-identity-fix.log` 的 `at_utc` = 2026-11-15T21:13:14Z→21:19:53Z（+08 05:13:15→05:19:53），提交时间 2026-11-16 05:20:42 ⇒ 日志生成于提交前 49 秒，属"跑完即提交"，**因果顺序正确**（不再倒置）。
- EV-HCF-17/18 commit = `bbeb28dcb` = P0-1 修复提交**本身**。`after-p0-fix.log` `at_utc` = 21:32:09Z→21:38:54Z（05:32→05:38），提交时间 05:39:50 ⇒ 同样正确；且与 `after-identity-fix.log` 的 `trx_sha256` 三值全不相同（两次独立运行，不是复制旧日志）。

**结论：P1-1 的 commit 列已真正修对（18/18 可 cat-file，且就是实际引入提交）；但 sha256 列 15 行仍为 `PIN_PENDING` —— 模板 `doc/templates/TASK.md:63` 要求 `BLOB` 基准确认（"BLOB 校验 commit:path 的 Git blob 原始字节；任何来源不可读取均为失败"），`PIN_PENDING` 不是 sha256 ⇒ BLOB pin 仍不可校验。全仓库仅本卡含 `PIN_PENDING`（`git grep -l PIN_PENDING -- doc/tasks` 只命中本文件），属异常残留。P1-1 判定为部分解决。**

### 4. P1-2 / P1-3 / P1-4 / P2-x 处置判定

#### P1-2（AC4/AC5 与卡面自相矛盾）

- AC4 行（L82）：`- [x] … <<PARTIAL: 三处 producer 已修两处 + source-read 路径已补；TileChannel 同源风险待评估>>` —— 标记已降 PARTIAL ✅。
- **但正文 L441-444「### AC 状态」仍写**：
  `- AC1 MET / AC2 MET / AC3 MET / **AC4 现在 MET**（两处缺陷都已修并验证）/ **AC5 MET**`
  —— 与 L79/L82/L83 直接冲突，上一轮明确要求"修掉 L82 与 L440 的自相矛盾"，**未完成**。`git diff 277406eeb..HEAD` 中该行未出现在删除行里，确认原文未改。
- AC5：判据原文「`dotnet test` 直接跑仍全绿（331/0/74）」未改写，仅降 `<<PARTIAL>>` + HTML 注释说明"裸跑 331/0/74 是修复前数字，未单独重跑"。上一轮给的二选一（补裸跑日志 / 改写判据为全量 `test.ps1`）都未做；只做了"诚实降级"。
  **判定：部分解决（自相矛盾仍在、AC5 判据未落成可复核形式）。**

#### P1-3（AC1 降级 + 并行叙事）

- AC1 行（L79）：`- [x] … <<PARTIAL: 并行叙事已被 AssemblyInfo 证伪，归因改为「零超时」>>` ✅ 已降级。
- 处置节 L503/L507-510 已写明 `NewManga.Host.Tests/AssemblyInfo.cs:1` = `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]`（我实测该文件只有这 1 行）并更正为"触发条件是同进程内多线程，而非测试并行" ✅。
- **未更正**：卡面正文 L71-72 仍写「在 xUnit 并行运行多个 Host 测试时，这些检查会互相触发；FILE_IDENTITY_CHANGED 也可能因为并行写入同一 granted folder 而误判」；`verification/HOST-CONCURRENCY-FLAKY-1/ac1-ac3-diagnosis.md:103` 仍写「它们在 test.ps1 下与其它 30 个新执行的测试并行」。`61a16159e` 只改卡面（+71 行追加），未改 diagnosis。
  **判定：部分解决（AC 标记已降级；两处原文未更正，只在处置节声明更正）。**

#### P1-4（绝对化表述 + handoff）

- `doc/handoffs/GOAL-WRAPUP-R100.md`：`07a8f828b` 已把「用户新导入的源文件（NTFS FileIndex > 2^53，实测 6/7）会**稳定报**」改为"当 file index 超过 2^53 时必然失败；新建文件场景下**高概率**触发，但非任何情况"，并加"「唯一一个」无法核验"注，同时补记 P0-1 漏点 ✅。
- **卡面正文未改**：L370-375「⇒ 任何用户**新导入**的源文件都会稳定报 `FILE_IDENTITY_CHANGED`」、L445-447「不是测试问题：任何用户**新导入**的源文件……**这是本会话唯一一个确认影响真实用户的产品缺陷。**」原文仍在；只有处置节 L512-518 追加了更正。卡面内部（正文绝对化 vs 处置节下调）自相矛盾。
  **判定：部分解决（handoff ✅；卡面正文 ❌）。**

#### P2-1（控制字符）

用原始字节统计 HEAD 工作树卡面（工作树与 HEAD blob 一致，`git status` 无该文件变更）：**U+0009 TAB = 11 个、U+000B VT = 2 个**，全部为词内替换：
- `<TAB>est.ps1`（t 被 TAB 替换）：L163、168、170、176、209、232、259、306、398、422、454
- `<VT>erification`（v 被 VT 替换）：L316、L454

**判定：未解决**。与上一轮统计（11 TAB + 2 VT）完全一致，说明本轮未动；行号相对上一轮报告（L160/165/167/…）整体 +3，属本轮追加后的偏移。

#### P2-2（front-matter/标题）

HEAD 卡面 L3 `title: …FILE_IDENTITY_CHANGED（待定位）`、L6 `status: proposed`、L8 `owner: null`、L9 `reviewer: null`，与"AC1/AC4/AC5 已降级、AC6 二轮复核中"的正文状态不符。**未解决。**

#### P2-3（最坏等待 ~10s）

`SourceAccessRegistry.cs:347` `LockWaitMillis = 5000`；`Locked<T>` `:362` `WaitOne(LockWaitMillis)`；`AcquireLockFile` `:382` 独立 `deadline = TickCount64 + LockWaitMillis`。最坏等待 ≈ 5000ms（mutex）+ 5000ms（文件锁）= **~10s**，而 `:334-346` 注释与卡面 L187-202 仍只描述 5000ms/单段语义。**未解决。**

#### P2-4（常量一致性测试）

`git grep -n "NormalizeFileId\|FileIdMask\|CoreFileIdMask" -- apps/desktop-avalonia/tests` **无匹配**。P0-1 修复新增的 `CoreFileIdMask` 也没有任何测试引用。**未解决**（且 P0-1 修复无直接回归测试，见 §5）。

#### P2-5（test.ps1 覆写 workspace evidence 目录）

卡面「附带发现」L452-457 只登记 `verification/READER-OVERLAY-HEADLESS-PNG-1/…` 被 test.ps1 重新生成（git 工作区污染），**未登记** `task-envs/HOST-RESOURCE-SECURITY-1/evidence-rerun` 被覆写。本轮复核期间再次实证：该目录先由 09:47-09:48 的并发运行覆写 `results-coreclient.trx`/`results-host.trx`，随后 09:53 的另一次全量运行重写 `results-app.trx` 并把 `summary.json` 的 `at_utc` 从 P0-1 的 21:38:54Z 覆写为 09:53:46 —— 这个副作用可反复发生，且会让任何依赖该目录的旧证据（如 `after-p0-fix.log` 声明的 `trx_sha256`）不可复验。**未解决。**

### 5. AC 标记格式合规

依据 `doc/09_COLLABORATION.md` §4.3（本卡 `governance_version: 3`，使用 `<<STATUS>>` 行末标记；L130-138 的勾选一致性表与矛盾组合规则）：`[x]` 只允许 `MET`/`NOT_APPLICABLE`；`[ ]` 只允许 `PARTIAL`/`BLOCKED`；任何缺标记的 v3 AC 不允许。

| AC | 行 | 勾选 | 行末标记（尾部） | `check.ps1` §4.3 预期 | 判定 |
|---|---|---|---|---|---|
| AC1 | L79 | `[x]` | `<<PARTIAL: 并行叙事已被 AssemblyInfo 证伪，归因改为「零超时」>>` | 勾选 + PARTIAL ⇒ `AC 标记为 PARTIAL 时不得勾选` | ❌ 不合规 |
| AC2 | L80 | `[x]` | `<<MET>>` | ✅ | 合规 |
| AC3 | L81 | `[x]` | `<<MET>>` | ✅ | 合规 |
| AC4 | L82 | `[x]` | `<<PARTIAL: 三处 producer 已修两处 + source-read 路径已补；TileChannel 同源风险待评估>>` | 同上 ⇒ FAIL | ❌ 不合规 |
| AC5 | L83 | `[x]` | `<<PARTIAL: 以 test.ps1 全量替代裸跑验证，未单独重跑裸跑>>` | 同上 ⇒ FAIL | ❌ 不合规 |
| AC6 | L84 | `[ ]` | **无标记** | `AC 状态标记缺失或非法` | ❌ 不合规 |

其它格式项：
- 所有标记都在**行末**（`>>` 之后无任何字符，含尾随空格），HTML 注释/说明都在标记**之前** ⇒ 符合"标记在行末"✅。
- `PARTIAL` 原因均非空 ✅；`MET` 未附原因 ✅。
- 当前 `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (3 warnings)`：只是因为 `status: proposed` 不触发 `check.ps1:953` 的 v3 门禁分支（门禁仅在 `in_review/approved/done/closed_with_limitations` 生效）。**一旦把本卡推进 `in_review`，上述 4 条会立即 FAIL**。
- §4.3.1（存量卡 HTML 注释）不适用于本卡（本卡用 §4.3 的 `<<…>>` 格式），故 "blocked 必须不勾选/verified 必须勾选" 不直接适用；但其规则精神（勾选必须与状态一致）等价地由 §4.3 表判定，结论同上。

---

## 新发现

### P1（必须修，均为文档/门禁级）

**P1-N1 AC 勾选与状态标记不一致，AC6 缺标记（进入 `in_review` 会被 `check.ps1` 判 FAIL）**

- `AC1/AC4/AC5` 为 `- [x]` + `<<PARTIAL: …>>`；§4.3 表格规定 `[x]` 只允许 `MET/NOT_APPLICABLE`，`check.ps1:987` 会报 `AC 标记为 PARTIAL 时不得勾选`。
- `AC6`（L84）为 `- [ ]` 且**无任何标记**，`check.ps1:968-970` 会报"标记缺失或非法"。
- 建议：三处 PARTIAL 改为 `- [ ]`；AC6 在二次复核通过后填 `<<MET>>`（本卡 AC6 由本轮复核覆盖，但最终仍应由 DSH 在集成后勾选）。

### P2（建议，不阻塞代码放行）

**P2-N1 opt-in IPC 测试 `Fea11ScanIpcTests` 仍用 raw file id 写 `source_locations`，P0-1 修复后可能回归**

- `tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:1141-1153` `ReadFileIdentity` 返回 raw `((ulong)IndexHigh<<32)|IndexLow`；`:1021-1049` `UpdateLocationRow` 把 raw `facts.FileId` 直接写 `source_locations`。
- P0-1 修复后 Host source-read grant facts 是 masked，Python `service.py:733-737`（`_ensure_target_version`）、`reattest.py:221-226`、`source_read_refs.py:639-657` 都是"grant facts vs location"直接整数比较 ⇒ 当 raw > 2^53 时这批 opt-in 测试会不匹配（该测试用 %TEMP% 新建文件，raw 大概率 > 2^53）。
- 现状：`test.ps1` 不设 `NEWMANGA_FEA11_IPC=1`（`scripts/test.ps1` 无该变量），这 3 个测试类仍被 skip，所以本卡绿不暴露。**恢复 opt-in IPC 测试时需同步 mask 该 helper。**

**P2-N2 P0-1 修复无直接测试覆盖 / 无回归测试**

- `test.ps1` 只跑 CoreClient/Host/App 三个项目且不设 `NEWMANGA_FEA11_IPC`；覆盖 source-read 路径的端到端测试仍是 `NotExecuted`。我从 `after-p0-fix.log` 的 `[SKIP]` 行实测：`Fea11ScanIpcTests` 4 条、`Fea11RunGrantIpcTests` 7 条、`Fea11SourceIpcTests` 3 条被跳过（与上一轮报告数字一致）。
- `after-p0-fix.log` 的 `TEST PASS 1579/1627` 只能证明"既有测试不退化 + 编译通过"，**不能证明 P0-1 修复的运行时行为**。建议补一条 `SourceReadCoordinator` 的单元测试：raw file id > 2^53 时，wire facts 的 `file_id == raw & ((1<<53)-1)`；再补 C# `CoreFileIdMask` 与 `identity.py:_FILE_MASK` 的一致性 pin（P2-4）。

**P2-N3 测试/证据日志缺 EXIT 码与 shell/venv 头（§4 Q-009 证据纪律）**

- `after-p0-fix.log` 首行是 test.ps1 的输出（`sidecar fixture: …`），无 pwsh 版本/解释器路径头，尾行只有 `TEST PASS (Debug): 1579/1627 passed, 48 skipped`，**没有记录脚本 EXIT 码**。卡面多处声称 `EXIT=0`，但日志本身无法复核 EXIT。上一轮未提这一点，建议在证据头/尾补 `pwsh -NoProfile` 头与 `EXIT=$LASTEXITCODE` 行（`test.ps1` 已有 TEST PASS 行，属轻微）。

**P2-N4 卡面行号漂移**

- `SourceReadCoordinator.cs`：卡面 L82 注释、L484 处置节、`GOAL-WRAPUP-R100.md` 引用 `:404/624`；HEAD 实际为 `:408/:632`（`bbeb28dcb` 加注释 4/5 行所致）。
- `SourceAccessRegistry.cs`：卡面 L50 引用 `:346`、L107-109 引用 `:344`（修复前历史行号）；HEAD 对应 `:364`（抛 BUSY）/`:362`（`WaitOne(LockWaitMillis)`）。历史章节保留旧行号可接受，但处置节（L467）已用新行号 `:362/379-398`，两处并存易混淆。
- 证据表在 HEAD 为 L134-151（上一轮报告称 L132-148，偏移 +2）。

---

## 未能独立验证的项

1. **未重跑 `test.ps1` / `dotnet test`**（硬性约束：只读；且 Lead 正在跑全量测试，会冲突并产生 `verification/` 副作用）。因此 `after-p0-fix.log` 的绿只做了"日志内自洽 + summary.json 一致 + 时间线因果"级核对，**没有**重跑验证。
2. **TRX 无法实算校验（被并发测试覆写）**：`after-p0-fix.log:487/496/505` 声明的 `trx_sha256` 为 `49fddb12…` / `be8630b0…` / `e92edc19…`。但复核期间 Lead 的并发全量测试重写了 `task-envs/HOST-RESOURCE-SECURITY-1/evidence-rerun/test/`：复核开始时我读到 `summary.json` 仍是 P0-1 运行（`at_utc` 2026-11-15T21:38:54Z）；随后 `results-coreclient.trx`/`results-host.trx` 被 09:47/09:48 的新运行覆写，复核结束时 `results-app.trx` 生成于 09:53:45、`summary.json` 也被覆写为 09:53:46（新的全量运行）。因此**无法用当前磁盘文件复算 after-p0-fix.log 声明的那三份 TRX 哈希**——这与上一轮复核者"三个哈希逐一相同"的结论不矛盾（那是 05:38 时的状态），但本次不可复验。
   旁证（不作为本卡证据）：Lead 09:47-09:53 在**同一 head**（`git status` 干净）上的这次全量运行，其 `summary.json` 为 1627/1579 passed/0 failed/48 skipped，三项目全通过，且其声明的 `trx_sha256` 与磁盘 TRX 实算一致（`585223c0…`/`e75397c4…`/`09c83c40…`）。即"当前 head 全量绿"有多份独立运行旁证，但它仍不能验证 P0-1 修复覆盖的 source-read 路径（opt-in 测试未跑）。
3. **"运行时的源码树 == 提交树"**只能间接推断：`after-p0-fix.log` 跑于 05:32-05:38，`bbeb28dcb` 提交于 05:39:50（跑完即提交）；无法做 worktree 快照比对。
4. **P0-1 修复的端到端行为未实跑**：覆盖 source-read 路径的 `Fea11*IpcTests` 是 `NEWMANGA_FEA11_IPC=1` opt-in，本次只读授权下没有跑（会起真实 Python Core、写 workspace）。P0-1 的结论是**静态链路级**（Host 写 masked + Python 全部 comparator masked ⇒ 必然相等），未做运行时复现。
5. **"唯一一个影响真实用户的产品缺陷"**：需要审计本会话全部门卡，未核；且已确认 `v0.1.1` tag 不含 `SourceAccessRegistry.cs`，"既有用户 registry"在发布语义上不存在。
6. **复核期间工作区被并发进程瞬态写入**：复核开始时 `git status --porcelain` 为空；复核中途出现 2 个已修改文件：
   ` M verification/READER-OVERLAY-HEADLESS-PNG-1/immersive-reader.png`
   ` M verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`
   这是 `test.ps1` 的既有副作用（卡面 L452-457 提及、Lead 的并发全量测试所致），**不是本次复核所为**；复核结束时（09:54）`git status --porcelain` 再次为空，说明该副作用会自行还原。我未对仓库执行任何写操作。
7. 本轮复核期间 `origin/main` 已指向被审 head `9ce819ae7`（与 NEXT-SESSION-STARTER "从未 push" 的描述不符，属另一进程的 push，未纳入本卡结论）。

---

## 声明

本复核**未修改仓库 `G:\CODEX\New Manga` 下的任何文件**：未 commit、未 checkout、未写文件；仅执行只读命令（`git log/show/cat-file/rev-parse/grep`、读取代码/日志/TRX/summary、只读 `tools/governance/check.ps1`）。
唯一写操作是生成本报告与一个临时校验目录（`G:\CODEX\New Manga.workspace\tasks\HOST-CONCURRENCY-FLAKY-1\review-tmp\`，存放 `git cat-file blob` 的临时字节用于 SHA-256 复算），均在 `G:\CODEX\New Manga.workspace\` 下、不在仓库内。
本报告独立于 `reviewer-hcf` 的上一轮报告：所有行号、行内引用、哈希、行末标记均由本轮重新 `git grep -n` / 读文件 / 实测获得，未直接采信上一轮报告；对上一轮报告的引用均已注明。

---

FINAL: CHANGES_REQUESTED — P0-1 补修与 18 行证据 commit 列经独立复核均正确（代码可放行），但卡面自相矛盾未消（L443「AC4 现在 MET」vs L82 PARTIAL）、15 行 sha256 仍 PIN_PENDING、AC1/AC4/AC5 的 `[x]`+`<<PARTIAL>>` 与 AC6 缺标记违反 §4.3 门禁（进 in_review 即 FAIL）、P2-1/2/3/4/5 全部未处置，需再修一轮文档/证据后关闭 AC6。
