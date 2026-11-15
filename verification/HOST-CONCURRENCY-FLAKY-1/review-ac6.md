# HOST-CONCURRENCY-FLAKY-1 AC6 独立复核

- 被审 head: `277406eeb`
- 复核者: reviewer-hcf（独立上下文子 agent）

## 结论

**CHANGES_REQUESTED**

两个修复本身是**正确且应保留**的（`HostIssuer` 53 位归一化、`SourceAccessRegistry` 有界等待），
测试证据也经我用 TRX 独立复核确认是**真跑通、不是 skip 冒充 pass**。
但本卡不能按现在的形态关闭，原因：

1. **P0：`FILE_IDENTITY_CHANGED` 的 producer 只修了一个。** Host 侧还有第二个未 mask 的
   Windows handle probe（`NewManga.Host/Sources/SourceSecurity.cs:123-135`），它把未归一化的
   64 位 file id 写进 **source-read grant**，被 Python 的 masked comparator 直接对撞，路径是
   用户可见的 `ScanSourceSync`（FEA-11 source sync）。该文件本来就在本卡 `allowed_paths`
   的 `NewManga.Host/Sources/**` 内，不需要再扩范围。因此卡面「两处缺陷都已修并验证」
   （L440）与「这是本会话唯一一个确认影响真实用户的产品缺陷」（L447）都超出证据。
2. **P1：Canonical Evidence 表 15/15 行的 `commit` 列全部错位**（全部指向该证据"入库前的父提交"），
   且 15 行 sha256 全是 `PIN_PENDING`。最刺眼的是 EV-HCF-14/15 把"修复后首次全绿"的日志
   钉在**修复提交之前**的 `c75740cb9`——因果顺序自相矛盾。
3. **P1：AC1 / AC4 / AC5 的 `<<MET>>` 与证据不匹配**（AC1 缺它自己列出的"xUnit 并行配置"，
   且卡面 L70-72、诊断 L103 的"并行"叙事被 `AssemblyInfo.cs:1` 直接证伪；AC4 见 P0）。
4. **P1：「任何用户新导入的源文件都会稳定报 `FILE_IDENTITY_CHANGED`」过强**——是否触发取决于
   该卷 NTFS 文件 ID 的复用序列是否使 64 位值 > 2^53，仓库内长期可用的 `alpha.png`
   （`st_ino=844424931403221 < 2^53`）就是反例。

---

## 逐项核查（对应上面 6 点）

### 1. 代码改动是否与声称一致

**核查方法**：`git show 277406eeb -- apps/.../Issuer/HostIssuer.cs`、
`git show e66323bf2 -- apps/.../Sources/SourceAccessRegistry.cs`、`git show --stat`、`git status --porcelain`。

**实际发现**

| 声称 | 实际 | 判定 |
|---|---|---|
| `HostIssuer.cs:563` 文件 identity 套 mask | 当前 HEAD `HostIssuer.cs:563` = `ulong index = NormalizeFileId(((ulong)info.FileIndexHigh << 32) \| info.FileIndexLow);` | ✅ 一致 |
| `HostIssuer.cs:596` 目录 identity 套 mask | `HostIssuer.cs:596-597` = `return (info.VolumeSerialNumber, NormalizeFileId(...));` | ✅ 一致 |
| 新增 `FileIdMask` / `NormalizeFileId` | `HostIssuer.cs:622` `internal const ulong FileIdMask = (1UL << 53) - 1;`、`:625` `internal static ulong NormalizeFileId(ulong rawFileId) => rawFileId & FileIdMask;` | ✅ 一致 |
| `SourceAccessRegistry`：`WaitOne(0)` → `WaitOne(5000)` | `SourceAccessRegistry.cs:362` `try { acquired = mutex.WaitOne(LockWaitMillis); }`，`:347 LockWaitMillis = 5000` | ✅ 一致 |
| 文件锁改有界重试 | `SourceAccessRegistry.cs:366` `using (AcquireLockFile())`，`:379-398` 重试循环（25ms 间隔、同一 deadline、超时抛 BUSY） | ✅ 一致 |
| 未改 `Generation` 乐观并发 | `SourceAccessRegistry.cs:71` 仍是 `if (entry.Generation != expectedGeneration) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");`（无重试） | ✅ 与"冻结边界"一致 |
| 未改调用方 / 错误码集合 | 两个提交的 code diff 只有这两个文件；`HostErrorCodes.cs` 未在 diff 内 | ✅ 一致 |

两个提交的 `--stat` 里其余文件都是 `doc/tasks/...` 与 `verification/...` 证据，无夹带代码改动。
被审 head 工作区干净（`git status --porcelain` 空输出）。

**判定：✅ 代码改动与声称一致，没有超出冻结范围。**

附带一个严格性提醒（非缺陷）：`Locked<T>` 的实际最坏等待是
`mutex.WaitOne(5000)` + `AcquireLockFile()` 的另一个 5000ms deadline ≈ **10s**，
而卡面 L184-199 与 L336-346 注释只描述为 5000ms（见 P2-3）。

### 2. mask 常量是否正确

**核查方法**：对读 `HostIssuer.cs:605-625` 与 `src/application/importing/referenced/identity.py`；
用 PowerShell 复算 `st-ino-measured.md` 的 7 个样本。

**实际发现**

- 文件 mask：C# `FileIdMask = (1UL << 53) - 1 = 9007199254740991`；
  Python `identity.py:20` `_FILE_MASK = (1 << 53) - 1`。**数值完全一致** ✅
- 语义一致：C# `raw & mask` 与 Python `int(file_id) & _FILE_MASK` 等价，且都是幂等 ✅
- volume：`identity.py:16` `_VOLUME_MASK = 0xFFFFFFFF`；`HostIssuer.cs:787`
  `public uint VolumeSerialNumber;`（`uint`，本就 32 位）⇒ C# 侧做 `& 0xFFFFFFFF` 是 no-op。
  卡面「VolumeSerialNumber 无需 mask：dwVolumeSerialNumber 本身是 32 位」**成立** ✅。
  旁证：`SourceSecurity.cs:136-141` 的 `Volume` 同样是 `uint`；`scanner.py:165-167` 在 Windows 上
  还对 `dev` / `expected_volume` 双边再 `&= 0xffffffff`，所以 volume 侧即使有偏差也不会漏。
- 数值表复算（PowerShell `band ((2^53)-1)`）：

| 声称 st_ino | > 2^53 | 我算出的 masked | st-ino-measured.md 的值 |
|---|---|---|---|
| 844424931403221 | no | 844424931403221 | 844424931403221 ✅ |
| 36873221950633840 | YES | 844424931669872 | 844424931669872 ✅ |
| 27021597765760890 | YES | 1537914 | 1537914 ✅ |
| 19703248371283835 | YES | 1688849861801851 | 1688849861801851 ✅ |
| 27021597765760892 | YES | 1537916 | 1537916 ✅ |
| 25051272928786301 | YES | 7036874419304317 | 7036874419304317 ✅ |
| 22799473115101054 | YES | 4785074605619070 | 4785074605619070 ✅ |

**判定：✅ 常量正确、与权威定义（`identity.py:16/20/27`）一致；volume 侧无需 mask 的判断成立；
证据表数值可复算。**

### 3. 是否存在遗漏的 producer

**核查方法**：`git grep FileIndexHigh|FileIndexLow|volume_serial|file_id|st_ino|st_dev|GetFileInformationByHandle`
（src + apps），逐个判断"是否参与跨语言 identity 比较"；再沿
`ScanSourceSync`（`core_service.py:5761-5762`）→ `application/sources/scanner.py:332-334`
→ `scan_source` → `scan_folder` / `source_lease` 追踪 consumer。

**实际发现：C# 侧共有 3 处 Windows handle probe 计算 64 位 file index，本卡只修了 1 处。**

| # | 位置 | 是否 mask | 是否参与跨语言 identity 比较 | 结论 |
|---|---|---|---|---|
| 1 | `HostIssuer.cs:563`（file）/ `:596-597`（dir） | ✅ 已 mask（本卡修复） | 进 signed import grant → `import_source_refs._facts` → `scanner.py:168` | 已修 |
| 2 | **`SourceSecurity.cs:123-135`** `Identity(...)`：`return (info.Volume, ((ulong)info.IndexHigh << 32) \| info.IndexLow, ...)` | ❌ **未 mask** | 进 **source-read grant** → `source_read_refs.py:1021/1061-1080` → `scanner.py:168` / `source_strict_read.py:27` | **遗漏（P0）** |
| 3 | `TileChannel.cs:430-439`（`long` 索引，且 `(long)High << 32` 有符号移位风险） | ❌ 未 mask | 目前只与自身 `Grant` 自比；唯一生产调用点 `HostRuntime.cs:1044-1050` 未传 `VolumeSerial/FileIndex`（`git grep "VolumeSerial:\|FileIndex:" apps/desktop-avalonia` 无调用方） | **潜在风险（P2）** |

遗漏项的完整证据链（全部逐行核对过）：

- **producer**：`NewManga.Host/Sources/SourceSecurity.cs:123-135`
  ```csharp
  return (info.Volume, ((ulong)info.IndexHigh << 32) | info.IndexLow, ((long)info.SizeHigh << 32) | info.SizeLow);
  ```
  与 `HostIssuer.cs:563` 修复前的形状**完全相同**。
- **调用点**：`SourceReadCoordinator.cs:391/394`（`DescribeContainer`）、`:608/611`（folder 成员循环）。
- **写入 grant**：`SourceReadCoordinator.cs:404`
  `["volume_serial"] = before.Volume, ["file_id"] = before.Id`；`:624-625` 同形。
  grant 的 `operation` 是 `"source-read"`（`:636`）。
- **Python 侧原样接收**：`source_read_refs.py:1068` `numbers = (raw["volume_serial"], raw["file_id"], raw["size"])`
  → `:1080` `GrantFacts(*numbers, raw["sha256"])`；`source_read_refs.py:1021` 变成
  `folder_entries` / `:1034` `container_facts`。**该文件里没有 `normalize_identity`**
  （`git grep normalize_identity -- src` 命中：`identity.py`、`scanner.py:97`、
  `application/sources/service.py:481-487`、`handle_resolver.py:162`、
  `import_source_refs.py:302`、`source_strict_read.py:50` ——**不含 `source_read_refs.py`**）。
- **comparator 1**：`scanner.py:163-168`
  ```python
  dev, ino, size = _stat_folder_entry(path, root)   # ino 已在 scanner.py:99 被 mask
  ...
  if dev != expected_volume or ino != facts.file_id or size != facts.size:
      raise SourceImportError("FILE_IDENTITY_CHANGED", "granted folder member identity drifted")
  ```
- **comparator 2**：`source_strict_read.py:25-31`（Windows 分支）
  `identity = hr._identity_of(handle)`（**已 mask**，`handle_resolver.py:158-165`）
  再与 `(facts.volume_serial, facts.file_id)`（**raw**）比较 → 同样必然不等。
- **用户可见路径**：`core_service.py:5761-5762` `ScanSourceSync` → `application/sources/scanner.py:332-334`
  `scan_source(resolved["resolved"], ...)` → `scanner.py:435-446` → `scan_folder` / `scan_image`
  → 上面的 comparator。即 **"源同步扫描新导入的文件夹"** 这条真实用户路径同样会报
  `FILE_IDENTITY_CHANGED`，与本次修好的 import-grant 路径是**同一缺陷的两个 producer**。
- **为什么 test.ps1 全绿仍漏掉它**：覆盖这条路径的端到端测试是 opt-in
  （`Fea11ScanIpcTests.cs:1174-1180`、`Fea11RunGrantIpcTests.cs:1794-1800`、
  `Fea11SourceIpcTests.cs:591-593`，需 `NEWMANGA_FEA11_IPC=1`）；
  `apps/desktop-avalonia/scripts/test.ps1` 只跑 3 个 `dotnet test` 项目（`:156-175`）且未设该变量（`:82-134`），
  **这 44 个 `NotExecuted` 里就包含它们**（我解析 `results-host.trx` 实测：`Fea11ScanIpcTests` 4 条、
  `Fea11RunGrantIpcTests` 7 条、`Fea11SourceIpcTests` 3 条被跳过）。全绿只覆盖了 import-grant 这一条路径。

**修复该遗漏项时必须注意（不能照搬 HostIssuer 的"源头 mask"）**：
`SourceSecurity.Identity` 同时被 `SourceAccessRegistry.cs:49`（`Register` 写入 `SourceRoot.FileId`，
持久化到 `registry.v1.dat`）与 `:137`/`SourceScanScheduler.cs:1730/1742`（`VerifyRootIdentity` 比较）使用。
若只在 producer 处 mask，**既有用户/既有测试 dataRoot 的 registry 里存的是 raw 值**，
`VerifyRootIdentity`（`SourceAccessRegistry.cs:140-141`）会对 `file id > 2^53` 的 root 全部
报 `SOURCE_REGISTRY_UNAVAILABLE`。正确做法是"比较时双侧归一化"（或 registry 版本/迁移），
而不是单边改 producer。

`DirectoryIdentity`（`HostIssuer.cs:596-597`）**已被正确 mask** ✅（卡面自问自答的这一环成立）。

**判定：❌ 存在遗漏 producer（`SourceSecurity.cs:127`），且它在用户可见路径上；
`TileChannel.cs:437` 属潜在同源风险。卡面"唯一 producer"的结论不成立。**

### 4. 测试证据是否可信

**核查方法**：先读 `after-identity-fix.log` 的结果行；再用日志里声明的
`trx_sha256` 去**独立校验真实 TRX**（`git` 以外的事实源），并解析 TRX 的 outcome。

**实际发现**

1. 结果行（`verification/HOST-CONCURRENCY-FLAKY-1/after-identity-fix.log`）：
   - `:365` `已通过! - 失败: 0，通过: 256，已跳过: 0，总计: 256 … NewManga.CoreClient.Tests`
   - `:458` `已通过! - 失败: 0，通过: 361，已跳过: 44，总计: 405 … NewManga.Host.Tests`
   - `:471` `已通过! - 失败: 0，通过: 962，已跳过: 4，总计: 966 … NewManga.App.Tests`
   - `:519` `TEST PASS (Debug): 1579/1627 passed, 48 skipped`
   - 三个项目全部是 **`已通过!`**，不是 `已跳过!` / `失败!`。
2. **独立校验 TRX**（日志/`summary.json` 内声明的 SHA256 vs 磁盘文件实算）：
   `G:\CODEX\New Manga.workspace\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\test\`
   `results-coreclient.trx → 83C4875E…FD26`、`results-host.trx → BDA7B897…CA03`、`results-app.trx → 20B1F1E6…7826`
   与日志内 `trx_sha256` **逐一相同**。
3. **解析 TRX 的 outcome**（回答"是不是 skip 冒充 pass"）：
   - host：405 条 = **361 `Passed` + 44 `NotExecuted` + 0 `Failed`**；
     其中两个曾经的失败测试
     `GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant`（`Passed`, 0.758s）、
     `GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages`
     （`Passed`, 0.609s）——**有真实执行时长，确实是跑过后通过，不是 SKIP**。
     这正好补上了作者此前"把 EXIT=0/skip 当 passed"的漏洞。
   - coreclient：256 条 = 256 `Passed`；app：966 条 = 962 `Passed` + 4 `NotExecuted`。
     合计 **1579 passed / 48 skipped**，与 `TEST PASS` 行一致。
4. 时间线自洽：TRX 运行 05:13:15→05:19:53（+08），提交 `277406eeb` 时间 05:20:42。

**判定：✅ 这份绿是真绿（不是 skip 冒充 pass），统计数字可复算。
⚠️ 但"运行时的树 == 277406eeb"只能间接佐证（跑完才提交），我没有重跑测试
（只读授权，不执行构建/测试）；这一点见"未能独立验证"节。**

### 5. AC 标记是否属实

| AC | 卡面标记 | 我的判定 | 依据 |
|---|---|---|---|
| AC1 并发路径澄清（锁作用域 / `_lockName` / **xUnit 并行配置**） | `<<MET>>`（L79） | **应降为 PARTIAL** | `_lockName` 派生 ✅（`SourceAccessRegistry.cs:31-32`，诊断 L17-24）；锁作用域 ✅（`:355-356` Global→Local）。但**"xUnit 并行配置"这一项在 `ac1-ac3-diagnosis.md` 全篇未出现**；而实测 `apps/desktop-avalonia/tests/NewManga.Host.Tests/AssemblyInfo.cs:1` = `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]`（该文件只有 `eb123ad4f` 一个提交）⇒ **Host 测试根本不并行**。卡面 L70-72「在 xUnit 并行运行多个 Host 测试时…互相触发」与 `ac1-ac3-diagnosis.md:103`「与其它 30 个新执行的测试并行」**均被证伪**；正确叙事是 `ac1-ac3-diagnosis.md:92-95` 的单测试内 watcher 线程 vs 测试线程（这条成立）。根因结论不受影响 |
| AC2 受控复现 | `<<MET>>` | ✅ 成立 | `repro-1.log`/`repro-2.log` 均含 3 条同名失败与 `失败! - 失败: 3，通过: 358，已跳过: 44，总计: 405`；`FILE_IDENTITY_CHANGED` + `SOURCE_REGISTRY_BUSY` 两种签名都在（我核了 repro-1） |
| AC3 根因判定 | `<<MET>>` | ✅ 成立 | `WaitOne(0)`（旧 `:344`）+ 单次 `FileShare.None`（旧 `:349-352`）的代码级依据充分；后续"不是并发/是口径缺口"的更正也有实测支撑 |
| AC4 修复或登记 | 卡面 L82 `<<PARTIAL>>`，正文 L440 却写「AC4 现在 MET」 | **应保持 PARTIAL（自相矛盾需修）** | 见 P0：只修了 import-grant 一个 producer；且卡面自身 L82 与 L440 两处状态冲突 |
| AC5 不影响既有基线（`dotnet test` 仍全绿 331/0/74） | `<<MET>>` | **证据不足（建议改写判据或补一条日志）** | `331/0/74` 是 **R87 修复前**的数字，`verification/HOST-CONCURRENCY-FLAKY-1/` 里**没有修复后的裸跑日志**（文件清单：只有 repro/after-fix/after-identity-fix/build/solo-detail）。全量 `test.ps1` 全绿是更强的等价证据，但并不是 AC5 写的那个判据。App 基线 `955/0/11` 出处可查（`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:2972`），962/0/4 与之不退化 ✅ |
| AC6 独立复核 | 未勾选 | ✅ 正确（本轮即 AC6） | L84 |

**判定：AC2/AC3 属实；AC1、AC4、AC5 的标记与证据不匹配（另有卡内自相矛盾）。**

### 6. 是否有过度声明

**核查方法**：把"新导入文件必然失败"这个产品影响断言拆成机制（NTFS 64 位 file ID 构成）+
实测数据（`st-ino-measured.md`）+ 现有反例（仓库内 `alpha.png`）三部分核对。

**实际发现**

- **机制是真的**：`HostIssuer` 写未 mask 值、Python 用 mask 值比较，只要 64 位 file id > 2^53
  就必然不等 ⇒ 该缺陷真实存在，且本次修复方向与冻结契约（`identity.py:3-9`）一致。
  contract 原文确实点名 "the Windows handle probe" 与 "the grant scope" 都是 producer，
  卡面这一引用**属实**（我逐行核了 `identity.py:1-10`）。
- **"任何用户新导入的源文件都会稳定报"（L445-446 / 提交信息）过强**：
  NTFS 的 64 位 file reference ≈ (16 位复用序列 << 48) | 48 位 MFT 记录号；只有序列足够大
  （约 ≥ 32）才会让 64 位值 > 2^53。实测 6/7 的样本反推序列约 70–131（`36873221950633840 / 2^48 ≈ 131`），
  说明那是**一台高频 churn 的开发机 %TEMP% 卷**；而 `alpha.png` 的
  `st_ino=844424931403221`（≈ 序列 3，< 2^53）在仓库里长期可用，正是"低复用序列卷不触发"的反例。
  更准确的表述是"在文件 ID 复用序列较高的卷上，新导入会**必然**失败；新卷/低复用卷可能不触发"。
- **"这是本会话唯一一个确认影响真实用户的产品缺陷"（L447）**：
  ① 需要审计本会话全部门卡的缺陷性质才能成立，本轮做不到（见"未能独立验证"）；
  ② 更实质的问题是——**同一个 `FILE_IDENTITY_CHANGED` 在 source-read/`ScanSourceSync` 路径仍然可达**
  （见 P0），所以即使它确实是"唯一被识别出的产品缺陷"，"已修复"的表述也不成立。

**判定：⚠️ 缺陷存在性与修复方向属实，但"任何用户/唯一"的绝对化表述不成立，需下调。**

---

## 未能独立验证的项

1. **我没有重跑测试/构建**（本复核为只读，`dotnet test`、`test.ps1` 会产生构建产物与
   `verification/` 副作用）。因此 `after-identity-fix.log` 的"绿"我通过 TRX sha256 + outcome
   独立复核（强证据），但**"运行时的源码树 == `277406eeb`"** 只能间接推断（跑完 49 秒后才提交）。
2. **P0 的端到端复现未做**：遗漏 producer 的证据是**代码级链路核对**（逐行引用见第 3 点），
   端到端需要跑 opt-in 的 `NEWMANGA_FEA11_IPC=1` IPC 测试（会起真实 Python Core、写 workspace），
   不在只读授权内。故 P0 定性为"静态证据链成立、未实跑复现"。
3. **"本会话唯一一个影响真实用户的产品缺陷"** 无法核验（需审计本会话所有卡）。
4. 提交信息里的 `四件套: check PASS(3w) / pins 18/18 / inventory 1/80/6=87`：我只验证了
   `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (3 warnings)`（可复现）；
   "pins 18/18" 无法从卡面复算（卡面 15 行 EV 全是 `PIN_PENDING`），"inventory" 未核。

---

## Findings

### P0（必须修）

**P0-1 `FILE_IDENTITY_CHANGED` 的 producer 修复不完整 —— source-read 路径仍是 raw vs masked**

- 遗漏点：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceSecurity.cs:123-135` 返回**
  未 mask**的 `((ulong)info.IndexHigh << 32) | info.IndexLow`。
- 流向：`SourceReadCoordinator.cs:391/394/608/611` → `:404`、`:624-625` 写入
  `source-read` grant 的 `facts.volume_serial` / `facts.file_id`（raw）→
  `source_read_refs.py:1068/1080` 原样构 `GrantFacts` → `scanner.py:163-171`
  （masked `ino` vs raw `facts.file_id`）与 `source_strict_read.py:25-31`
  （masked handle identity vs raw facts）→ **同签名 `FILE_IDENTITY_CHANGED`**。
- 用户路径：`core_service.py:5761-5762` `ScanSourceSync` → `application/sources/scanner.py:332-334`
  → `scanner.scan_source` → `scan_folder`/`scan_image`。
- 测试盲区：覆盖该路径的端到端测试是 opt-in（`NEWMANGA_FEA11_IPC=1`），`test.ps1` 不跑；
  所以本次全绿**不能**证明该路径无恙。
- 同时必须处理持久化兼容：`SourceSecurity.Identity` 还被 `SourceAccessRegistry.cs:49/137`
  用于 `SourceRoot.FileId` 的写入与校验（`registry.v1.dat`）；**只在 producer 处 mask 会让
  既有 registry 的 root 校验失败**（`SourceAccessRegistry.cs:140-141` 抛 `SOURCE_REGISTRY_UNAVAILABLE`）。
  建议改为"比较双侧归一化"（`SourceAccessRegistry.cs:49/140`、`SourceScanScheduler.cs:1730/1742`
  等）或引入 registry 版本迁移。
- 建议处置：在本卡 AC4 解除 `<<MET>>`（恢复 `<<PARTIAL>>`），把该 producer 与
  `TileChannel.cs:437` 的同类问题一并修掉；`allowed_paths` 已覆盖，无需再扩范围。

### P1（应修）

**P1-1 Canonical Evidence 表 15/15 行 `commit` 列全部错位，且 sha256 全为 `PIN_PENDING`**

`doc/tasks/HOST-CONCURRENCY-FLAKY-1.md:132-148` 的 `commit` 列是"该证据入库前的父提交"，不是包含该证据的提交。
证明（`git cat-file -e` 直接验证）：

```
git cat-file -e 84b4a2456:verification/HOST-CONCURRENCY-FLAKY-1/ac2-repro.md   -> 128 (exists on disk, but not in '84b4a2456')
git cat-file -e fbf704a37:verification/HOST-CONCURRENCY-FLAKY-1/ac2-repro.md   -> 0
git cat-file -e c75740cb9:verification/HOST-CONCURRENCY-FLAKY-1/after-identity-fix.log -> 128
git cat-file -e 277406eeb:verification/HOST-CONCURRENCY-FLAKY-1/after-identity-fix.log -> 0
```

完整映射（卡面值 → `git log --diff-filter=A` 实测值）：

| 行 | 证据 | 卡面 commit | 实际入库 commit |
|---|---|---|---|
| EV-HCF-01 | code-evidence.log | 25e8f5492 | **84b4a2456** |
| EV-HCF-02 | ac2-repro.md | 84b4a2456 | **fbf704a37** |
| EV-HCF-03 | repro-1.log | 84b4a2456 | **fbf704a37** |
| EV-HCF-04 | repro-2.log | 84b4a2456 | **fbf704a37** |
| EV-HCF-05 | after-fix.log | fbf704a37 | **e66323bf2** |
| EV-HCF-06 | build.log | fbf704a37 | **e66323bf2** |
| EV-HCF-07 | correction-skip-vs-pass.md | e66323bf2 | **ac434d911** |
| EV-HCF-08 | solo-detail.log | e66323bf2 | **ac434d911** |
| EV-HCF-09 | file-identity-diagnosis.md | ac434d911 | **062918039** |
| EV-HCF-10 | st-ino-measured.md | 062918039 | **4b1198443** |
| EV-HCF-11 | probe_st_ino.py | 062918039 | **4b1198443** |
| EV-HCF-12 | st-ino-probe-output.log | 062918039 | **4b1198443** |
| EV-HCF-13 | root-cause-proven.md | 4b1198443 | **c75740cb9** |
| EV-HCF-14 | after-identity-fix.log | c75740cb9 | **277406eeb** |
| EV-HCF-15 | build-r99.log | c75740cb9 | **277406eeb** |

根因可从 workspace 里的生成脚本复现：
`G:\CODEX\New Manga.workspace\tasks\HOST-CONCURRENCY-FLAKY-1\apply_card_r98.py:20-46`
用 `git rev-parse --short HEAD` 取**当前** HEAD 填 commit 列，`git cat-file blob :<path>`
取不到 blob 时返回 `PIN_PENDING` —— 即这些行是在证据入库**之前**生成、之后从未刷新。
最严重的一行是 EV-HCF-14/15：把"修复后首次全绿"的日志钉在**修复提交之前**的 `c75740cb9`，因果倒置。
补充：`tools/governance/check.ps1` 仍 PASS(3 warnings)，说明该检查器**不校验 pin 的 commit 归属**，
"check PASS" 不能当作 pin 正确的依据。

**P1-2 AC4 / AC5 标记与证据不匹配**（详见第 3、5 点）：AC4 恢复 `<<PARTIAL>>` 并修掉
L82 与 L440 的自相矛盾；AC5 要么补一份修复后的裸跑 `dotnet test` 日志，要么把判据改写成
"全量 `test.ps1` 1627/0 failed"。

**P1-3 AC1 缺项 + "并行"叙事被证伪**（详见第 5 点）：AC1 降为 PARTIAL 或补 `xUnit 并行配置` 说明
（结论是 `DisableTestParallelization = true`），并更正 L70-72 / `ac1-ac3-diagnosis.md:103`。

**P1-4 "任何用户新导入的源文件都会稳定报 / 唯一一个产品缺陷" 过强**（详见第 6 点）：
改为"在文件 ID 复用序列较高的卷上必然失败（本机 %TEMP% 实测 6/7）；import-grant 路径已修，
source-read/扫描路径仍待修"。
补充：同一断言已在被审 head 之后继续向 handoff 传播——`doc/handoffs/GOAL-WRAPUP-R100.md:49`
「**可能影响真实用户导入路径**的产品缺陷已修」、`:86-89`「…会稳定报 `FILE_IDENTITY_CHANGED`」、
`:125`「本会话修复了 **1 个真实产品缺陷**」（该文件由 `343260c20` 引入，docs-only）。
更正口径时要连带改这一处，否则后续会话会继承过强结论。

### P2（建议）

**P2-1 卡面文本被控制字符破坏**（文档可审查性问题）

`doc/tasks/HOST-CONCURRENCY-FLAKY-1.md` 的 HEAD blob 里有 **11 个 U+0009 TAB + 2 个 U+000B VT**：
`test.ps1` 被写成 `<TAB>est.ps1`（L160/165/167/173/206/229/256/303/395/419/451），
`\verification` 被写成 `<VT>erification`（L313、L451，渲染成 `erification/...`）。
另有多处代码/日志块只用单反引号行（如 L208/L211/L220）而不是 ``` 围栏，渲染后代码块失效。
损坏在 HEAD blob 内，`git log -S` 指向 `e66323bf2` 引入的 TAB 行；
而输入文件 `card-tail.md` / `card-tail-r98.md` 本身 TAB=0/VT=0（我实测），说明是**拼装卡面时被转义吞掉**。
（workspace 里已有 `DOC-CTRLCHAR-FIX-1`/`DOC-CTRLCHAR-FIX-2` 这类先例卡，建议走同一处置。）

**P2-2 卡面元数据陈旧**：标题仍写「FILE_IDENTITY_CHANGED（待定位）」（L3）；
front-matter `status: proposed` / `owner: null` / `reviewer: null`（L6-9）与正文"AC1-AC5 MET"不符。

**P2-3 `AcquireLockFile` 的最坏等待是 ~10s 不是 5s**：`WaitOne(5000)` + 文件锁独立 deadline 5000ms。
建议注释/卡面写清总上界，或让文件锁复用 mutex 的同一 deadline。

**P2-4 新常量无任何测试引用**：`git grep NormalizeFileId|FileIdMask -- apps/desktop-avalonia/tests` 为空。
建议加一条 pin 测试：C# `FileIdMask` 与 `identity.py:_FILE_MASK` 一致 + 一个 `raw > 2^53` 的
`NormalizeFileId` 断言，防止两侧常量漂移（卡面自己已担心"常量单一事实来源"）。

**P2-5 跑 `test.ps1` 会覆写别的卡的 evidence 目录**：本次 `after-identity-fix.log` 内的
`evidence_root` 是 `task-envs/HOST-RESOURCE-SECURITY-1/evidence-rerun`，TRX 时间 05:13–05:19 表示
该目录被本卡重写。卡面"附带发现"只提到 `verification/READER-OVERLAY-.../immersive-reader.png` 污染，
漏了这条 workspace 副作用；建议一并登记。

---

## 声明

本复核未修改任何仓库文件；仅读取代码、git 历史与证据日志。
复核期间只执行了只读命令（`git log/show/cat-file/grep`、读取 log/TRX、
`pwsh -NoProfile -File tools/governance/check.ps1` 这一只读检查器）。
唯一的写操作是**生成本报告本身**（位于 `G:\CODEX\New Manga.workspace\`，不在仓库内）。

补充事实：复核期间仓库在被审 head 之上又前进了一个 **docs-only** 提交 `343260c20`
（只改 `doc/handoffs/GOAL-WRAPUP-R100.md`），代码文件与 `277406eeb` 无差异，
因此本报告引用的代码行号对 `343260c20` 同样成立。
