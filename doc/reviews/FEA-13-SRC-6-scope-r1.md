# FEA-13-SRC-6 独立范围审查（scope-r1）

- **审查者**：DSH 派发的独立上下文子代理（fresh session；未参与 FEA 线或本卡实现/返修）
- **被审 head**：`07545adf19a730e2ab640cb1f01e0d15fd4ba70b`（`main`；审查前工作树 clean）
- **审查对象**：`doc/tasks/FEA-13-SRC-6.md`（proposed 占位：SC-B01 ④ 源引用/授权元数据入包）
- **日期**：2026-11-10
- **性质 / 写域**：只读 scope review；仅写本文件。未改生产源码、测试、契约、卡；未 commit / push。
- **结论**：**`READY-TO-FREEZE`**（无需 UNFREEZE；冻结口径见 §1.6；偏离该口径即触发 §1.7 的 UNFREEZE 条件）

| 项 | 结果 |
|---|---|
| verdict | **READY-TO-FREEZE** |
| 是否需 UNFREEZE | **否**（C-09 已预留 ④ 载体；C-06/C-17 零字节改动） |
| allowed_paths | **14 条**（见 §2.6） |
| AC | **6 条**（见 §3） |
| 门禁（只读复核） | `check.ps1` 默认 **EXIT 0**；`-TaskPath` **EXIT 0**；`verify_pins` **18/18 EXIT 0**；`git status --short` clean |

---

## 1. 范围判定

### 1.1 判定结论

SRC-6 是 C-09 冻结语义的**实现补齐**，不是新契约面：

- **C-09 已把「源引用与授权元数据入包、包内加密」写成强制要求**，且 SC-B07 的强制增量 ④ 已明确预留该段；
- **C-06 / C-17 不需要改字节**：本卡不新增 Host/Core 命令、不新增 wire 字段、不新增错误码；跨层交接用「Host 私有 registry 文件只读复制」+「Core 恢复后 handoff 文件」完成，属于已冻结语义的实现，不是协议增量；
- **C-15 §5 已把备份交接列为设计输入**，本卡按该输入落地，不改 registry 文件格式/DPAPI 边界/错误码闭集。

因此 **不需要 UNFREEZE、不需要 errata、不重算 18 pins**。若把交接面改成「Host 显式 staging 输入 payload / 新命令」，则触发 §1.7 的条件，verdict 应改为 `NEEDS_UNFREEZE`。

### 1.2 C-09：④ 的载体已经存在（不需要新增条款）

| 依据 | 内容 | 对本卡的含义 |
|---|---|---|
| `doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:26` | SC-B01「必须包含」：`library.db`、sidecar、`managed/`（含 `trash-manifest.json`）、**源引用与授权元数据（AD-003 §3.3；Host 私有 registry 随备份纳入，备份包内加密）** | 入包要求已冻结；本卡只实现，不新增要求 |
| 同文件 `:38` | SC-B01a 归属表：**源引用与授权元数据 = 是（包内加密）**；AD-003 §3.3、Host 私有 registry | 归属与加密语义已定 |
| 同文件 `:138` | SC-B07 `backup/2` 强制增量 **④ 包内加密的源授权元数据段** | ④ 是 v2 的强制项；本卡落地即补齐 SC-B07 的最后一个未实现增量 |
| 同文件 `:29` | SC-B01 扩展点：`nmbak` 白名单改显式清单；**新增项须走独立 Task** | SRC-6 就是该「独立 Task」；新增 `extras/source-access` 类不需要改 C-09 字节 |
| 同文件 `:139-143` | 版本协商：写端只写 v2；v1 只读；未知版本 `BACKUP_FORMAT_UNSUPPORTED` | 新增 extras 类别不改变 `format/version`，仍为 v2；旧读端按既有前向兼容规则拒绝 |
| `doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md:25-31` | SRC-6 单列立项；同机恢复有效、跨机须重授权；不阻塞 FEA-15 验收 | 语义边界与本卡一致 |
| `doc/reviews/ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md:13-16` | D1–D4 errata；D3 明确「不新增 Host→Core staging 输入面」 | 本卡不把交接做成 wire 输入面，符合 D3 的边界 |

**没有 C-09 errata 需要补**：SC-B01a 的「源引用与授权元数据」行仍在，SC-B07 ④ 仍是强制项；本卡是其实施载体。C-09 冻结记录 §9 的 D1–D4 errata 未删除 ④，也未把它改成可选。

**「源引用」与「授权元数据」的分工**：C-09 `:174` 所指的 `source_entries`/`page_bindings` 是 Core `library.db` 内的行，已随主库备份（C-09 SC-B01 的 `library.db` 项）；本卡新增的是 **Host 私有 registry** 的授权元数据段，不是第二份源引用表。两者不重复、不冲突。

### 1.3 C-06：不需要改字节

C-06 冻结的是 **registry 条目语义 + source-read grant + 命令面**，不是备份命令面：

| 依据 | 内容 | 对本卡的含义 |
|---|---|---|
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:37` | 「现有传输无 Core→Host RPC」 | 不新增 Core→Host 回调；导出走文件约定，避免协议增量 |
| 同文件 `:44` | registry 不存在/过期/generation 不匹配/identity 变化 → `SOURCE_ACCESS_DENIED`（fail-closed） | 导入拒绝复用既有非 retryable 码；不新增错误码 |
| 同文件 `:50-56` | UI→Host / Host→Core 命令面（Register/List/Revoke/Request/Verify/RevokeGrant/AuthorizeForRun） | **不新增命令**；导入是 Host 内部恢复动作，不是 UI 命令 |
| 同文件 `:58` | 新增命令须按 minor 递增 | 本卡不新增命令，故不触发 minor |
| C-06 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C06.md:16` | v1.3 pin `75f8e2b4…` | 零字节改动，pin 不变 |

C-06 的 9 条安全约束也不冲突：Core 只读复制 registry **密文**，不获得明文路径/授权；UI 仍只能经 Host 命令访问 registry；registry 仍是 Host 私有。

### 1.4 C-17：不需要改字节

C-17 的 `source.sync` 面（命令/DTO/错误闭集/journal/CAS/lineage）与本卡无关：

| 依据 | 内容 | 对本卡的含义 |
|---|---|---|
| `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:16` | `M2-C1` 无增量；命令面由 C-17 承载 | 本卡不新增 `source.sync` 命令/DTO |
| 同文件 `:205` | closed shape 命令与 DTO；未知字段、缺字段、类型错 → 拒绝 | 本卡不改任何 C-17 命令形状 |
| 同文件 `:356-377` | C-17 局部错误闭集；`SOURCE_ACCESS_DENIED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_REGISTRY_BUSY` 已存在 | 导入复用既有码，不扩闭集 |
| C-17 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C17.md:15` | v1.2 pin `cdeee487…` | 零字节改动，pin 不变 |

**C-17 journal 兼容**只作为风险登记（§5.5）：导入不读写 `<DataRoot>/host/source-operations/*.v1.dat`，不迁移 journal；恢复后 pending operation 按 C-17 既有规则 fail-closed，要求重新预览。

### 1.5 C-15：设计输入，不是字节修订

`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:317` 已写：

> **备份交接（FEA-13）**：Registry 文件/DPAPI 边界/备份包加密需求作为设计输入；跨机恢复因 DPAPI CurrentUser 不自动继承授权（binding 需重新确认），不以“DPAPI 失败”作为唯一跨机判据。

本卡把该设计输入落成：

- registry 文件格式原样（`NMSAR1\0` + `uint32 LE` + DPAPI CurrentUser 密文；`:295-296`）；
- 包内段即该**密文原字节**，不重加密、不转明文、不引入包口令；
- 跨机/他用户导入必须 typed 拒绝并要求重授权，不自动重建 identity（`:313`、`:317`）。

C-15 无需改字节；它的「零新错误码」约束（`:313`）也由复用既有码满足。

### 1.6 冻结口径（本 verdict 的前提）

**导出方向**：Core 以只读方式复制 `<DataRoot>/host/source-access/registry.v1.dat` 的原字节进包；Core **不解密、不解析、不重写**该文件。**导入方向**：Core 恢复成功后把包内该成员复制到 Core 写域内的 handoff 目录并写 `handoff.json`；Host 读取 handoff、用 `ISecretProtector` 解密并合并进 live registry。

这个口径同时满足：

1. **自动/pre_restore/pre_migration 备份**（SC-B08 归 Core 调度）也能带源授权元数据——不需要 Host 在每次 Core 发起备份前介入；
2. **不新增 wire 字段/命令**——`backup.create` 入参、`backup.restore` 出参、C-06/C-17 命令面均不变；
3. **DPAPI 边界不破**——Core 只见密文；明文只在 Host 进程内出现。

### 1.7 触发 UNFREEZE 的偏离条件（若 DSH 改口径）

出现以下任一项，**停止实施并改判 `NEEDS_UNFREEZE`**（附载体草案、独立 byte-level 复核、重冻、pin 重算）：

| # | 偏离 | 触及契约 |
|---|---|---|
| U1 | 给 `backup.create` 增加 `source_access` staging 入参 / 给 `backup.restore` 增加 handoff 出参并要求 Host 解析 | V11R 命令面 / M2-C1 additive 规则；如进入 C-06 命令面则 C-06 UNFREEZE |
| U2 | 新增 Host 命令（如 `source_import_registry_backup`）或 Core→Host callback | C-06 §2.3 命令面（且违反 `:37` 无 Core→Host RPC） |
| U3 | 改 registry 文件格式（`NMSAR2`）或 C-15 §5 的 DPAPI/ACL/锁语义 | C-15 UNFREEZE |
| U4 | 新增错误码并进入 C-17/C-16 闭集 | C-17/C-16 UNFREEZE |
| U5 | 把 ④ 改成可选、提升包版本、或改变 SC-B07 的强制增量语义 | C-09 UNFREEZE |
| U6 | 包内段用明文、Core 侧包级密钥、或把 registry 明文写入 `manifest.json`/DB | 违反 C-09「包内加密」、C-15 DPAPI 边界；需契约裁决，不是实现自由 |

### 1.8 依赖与时序

- `depends_on`：`FEA-13-COV-2`（done）、`FEA-11-HOST-AUTH-3`（done，见 `doc/REBASELINE_PLAN.md:14`）。
- 与 `FEA-13-MIGRATE-6`（数据根迁移，blocked）的边界：本卡不实现换根；registry 随 DataRoot 布局；迁移卡须把 `host/source-access/registry.v1.dat` 纳入 Host 持久物清单（§5.8）。
- 与 FEA-15：`doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md:18` 的 A8 已登记 limitation；本卡完成后 A8 应收窄为「跨机须重授权」，不能整条删除（§5.7）。

---

## 2. 实现骨架

### 2.1 交接面总览

| 方向 | 产物 | 写入方 | 读取方 | 字节语义 | 失败语义 |
|---|---|---|---|---|---|
| 导出（staging 源） | `<DataRoot>/host/source-access/registry.v1.dat` | Host `SourceAccessRegistry.Save`（既有） | Core `nmbak`（只读） | 原文件原字节（`NMSAR1` 文件；DPAPI 密文） | 读失败 → `BACKUP_CREATE_FAILED`，不产出包 |
| 包内段 | `extras/source-access/registry.v1.dat` | Core `nmbak` | Core `nmbak` restore / Host import | 与导出源**逐字节相同** | 缺失/摘要/大小不符 → `BACKUP_CORRUPT` |
| 恢复 handoff | `<backup_root>/restore-handoff/<backup_id>/source-access/registry.v1.dat` + `handoff.json` | Core `nmbak.restore`（恢复成功后） | Host `SourceAccessRestore` | 原字节 + 摘要/大小/backup_id | 缺失 → `not_present`；摘要/大小不符 → `SOURCE_ACCESS_DENIED`/`handoff_corrupt` |
| 导入（live 写） | `<DataRoot>/host/source-access/registry.v1.dat` | Host `SourceAccessRegistry.ImportRestoredSnapshot` | Host | 合并后的新快照（原子 Save） | DPAPI/版本/结构失败 → typed 拒绝，live 零写 |

链路：

```
Host registry.v1.dat (DPAPI ciphertext)
        │  Core 只读复制（不解密/不解析）
        ▼
.nmbak: extras/source-access/registry.v1.dat  + manifest.extras (sha256/size)
        │  Core restore（DB/managed 成功后才写 handoff）
        ▼
<backup_root>/restore-handoff/<id>/source-access/registry.v1.dat + handoff.json
        │  Host 读取/校验/DPAPI 解密/合并
        ▼
Host registry.v1.dat（live；原子 Save）
```

### 2.2 Host 侧：导出为「文件约定」，不新增 staging 写路径

- **导出格式**：直接使用 C-15 §5 的 registry 文件原格式，不新增 Host 序列化：
  `ASCII "NMSAR1\0"` + `uint32 LE JSON 长度` + `DPAPI CurrentUser` 密文（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:295-296`；实现 `SourceAccessRegistry.cs:16-21, 150-191`）。
- **为什么不让 Host 先写 staging 文件**：Core 的 `pre_restore`、`pre_migration`、自动备份都由 Core 侧创建（`nmbak.create` / `core_assembly.py:175-184`、`:1930-1941`），Host 没有参与每次 `backup.create` 的注入点；要 Host 显式 staging 就必须新增 `backup.create` 入参或 Core→Host 回调，二者都触发 §1.7 的 U1/U2。
- **只读边界**：Core 只读 `<DataRoot>/host/source-access/registry.v1.dat` 这一个文件；**不得**读 `registry.v1.lock`、`quarantine/**`、`*.corrupt-*`、`*.tmp`，也不得解析明文 JSON。
- **并发**：Host `Save` 用同目录临时文件 + `File.Replace`/`File.Move` 原子替换（C-15 `:309`）。Core 读到的只会是完整旧文件或完整新文件；若 Host `File.Replace` 因 Core 持有句柄失败，Host `Save` 按既有路径返回 `SOURCE_REGISTRY_UNAVAILABLE`（retryable），Core create 可按 3×短退避重试后 typed 失败——这是 fail-closed，不是半包。
- **缺失**：registry 文件不存在 = 合法空 Registry（C-15 `:311`）。这是「没有授权元数据可入包」，不是损坏；包仍可 `verified=true`，但不含 `source-access` 段（§2.3）。
- **损坏但可读**：Core 不负责判定 DPAPI/JSON；它只复制字节。损坏的 registry 仍可入包（保持备份可用），由 Host 导入时 typed 拒绝（§2.4）。只有**读打开/读取错误**才使创建失败。

### 2.3 Core 侧：包内段与 manifest

**文件级改动（`src/infrastructure/sqlite/nmbak.py`）**：

1. 常量：
   - `SOURCE_ACCESS_CATEGORY = "source-access"`
   - `SOURCE_ACCESS_FILE = "registry.v1.dat"`
   - 加入 `EXTRAS_CATEGORIES`（`:74-76`）。
2. `_collect_extras`（`:701-740`）：
   ```
   registry = self._data_root / "host" / "source-access" / SOURCE_ACCESS_FILE
   if registry.is_file():
       collected.append((SOURCE_ACCESS_CATEGORY, SOURCE_ACCESS_FILE, registry))
   ```
   不跟随 symlink/junction（复用 `_crosses_reparse_point` 语义）；不收集 lock/quarantine。
3. `_present_categories`（`:791-801`）：registry 文件存在时加入 `source-access`；文件不存在则不加（没有可入包内容，不伪装 empty）。
4. `_copy_extras`（`:758-777`）：沿用标准 manifest 项 `{category, relative_path, sha256, size_bytes}`；**不新增**加密/格式声明字段（不声称 Core 可验证的内容；格式由 Host 导入时验证）。
5. `_verify_package`（`:968-1008`）：`source-access` 进入闭集后，逐成员校验 `sha256` + `size_bytes`；未知 extras 类别仍 `BACKUP_FORMAT_UNSUPPORTED`；`included_categories == extras ∪ empty_categories` 的交叉校验不变。
6. `create`（`:227-343`）：
   - registry 不存在 → 跳过（无段）；
   - 存在但读取失败 → `BACKUP_CREATE_FAILED`（无包、无 `verified`）；
   - 存在且可读 → 复制原字节；**不解密、不解析**；
   - 4 MiB 上限（与 `SourceAccessRegistry.Load` 的 `:157` 一致）在 Core 侧同样拒绝超大文件，防包体异常。
7. 包内路径固定：`extras/source-access/registry.v1.dat`；manifest `extras` 项为：
   ```json
   {"category":"source-access","relative_path":"registry.v1.dat",
    "sha256":"<64hex>","size_bytes":1234}
   ```

**前向兼容**：

- 旧 Core（本卡前）读新包会因未知 extras 类别得到 `BACKUP_FORMAT_UNSUPPORTED`（COV-2 已定的前向兼容行为），**不是** `BACKUP_CORRUPT`；发布说明须写明「新包不能被旧二进制恢复」。
- 新 Core 读旧包（无 `source-access`）按无段处理；restore 不写 live registry，Host 报 `not_present`。
- 不提升 `version`；仍是 `format:"nmbak"` + `version:2`（C-09 `:136`，`nmbak.py:60-64`）。

**自动/pre_restore/pre_migration 包**：都走同一个 `create()` / `_collect_extras()`，因此自动获得该段，不需要额外接线（SC-B08 的 Core 调度语义不受影响）。

### 2.4 恢复反向：Core handoff → Host 导入

**Core 侧（`nmbak.py`，overwrite restore 路径）**：

- `restore()`（`:348-421`）在 `_restore_managed` 与 `managed_consistency_report` 成功后、返回前，若 manifest 含 `source-access` 成员：
  1. 从 `restore_dir/extras/source-access/registry.v1.dat` 复制到
     `<backup_root>/restore-handoff/<backup_id>/source-access/registry.v1.dat`；
  2. 写 `handoff.json`：
     ```json
     {"backup_id":"<32hex>","member":"extras/source-access/registry.v1.dat",
      "sha256":"<64hex>","size_bytes":N,"database_id":"<id-or-null>",
      "created_at":"<iso>"}
     ```
  3. 复制/摘要失败 → `BACKUP_RESTORE_INCOMPLETE`（既有 conflict 码；DB 已恢复，报告 rollback package），不静默声称完成。
- **不改** `backup.restore` 出参；Host 用 `backup_id` 推导 handoff 路径（`<DataRoot>/backups/restore-handoff/<id>/…`）。生产等价前提：`<backup_root> = <DataRoot>/backups`（`core_assembly.py:1930-1941`）。既有 report 的 `deferred_categories` 会自动包含 `source-access`（`nmbak.py:405-407`），不需要新增出参字段。
- **merge restore（`mode=defer/use_backup`）**：本卡不创建 handoff；C# Host 目前也没有暴露 merge restore（`verification/FEA-13-RESTORE-4/README.md:46`）。该缺口登记在 §5.4，不表现为「静默成功」。

**Host 侧（`SourceAccessRestore.cs` 新文件 + `SourceAccessRegistry.cs`）**：

1. `SourceAccessRestore.TryImportFromHandoff(dataRoot, backupId, registry, log)`：
   - 校验 `backupId` 为 `[0-9a-f]{32}`；handoff 根必须在 `<dataRoot>/backups/restore-handoff` 内；拒绝 reparse/junction（`SourceSecurity.RejectReparseAncestors`）。
   - 读 `handoff.json`，校验 `backup_id` 等于入参、`sha256`/`size_bytes` 与文件一致；不符 → `SOURCE_ACCESS_DENIED` / `handoff_corrupt`，live 零写。
   - 调 `registry.ImportRestoredSnapshot(bytes)`；返回 outcome；日志只写 counts/registry_id/generation，不写绝对路径（C-15 `:318`）。
   - 写 Host 侧 receipt：`<DataRoot>/host/source-access/imports/<backup_id>.json`（`status`/`reason`/`imported`/`unchanged`/`conflicts`/`at`/`handoff_sha256`）。该目录用 `SourceSecurity.PrivateDirectory` 创建（当前用户独占 ACL，与 C-15 `:316` 同纪律）。**显式 restore 触发时总是重写该 receipt**，允许用户在一次显式恢复后重新导入；receipt 目录不受 `Reset` 影响。
2. `SourceAccessRestore.TryImportPending(dataRoot, registry, log)`：
   - 扫描 `restore-handoff/*/handoff.json`（按 `created_at` 升序）；**跳过已有 receipt 的 `backup_id`**；逐项导入；幂等；单项失败不阻断其他项。
   - 用途：Core 恢复成功但 Host 崩溃/重启后补导入；已导入的再次导入为 `unchanged`，不重复写。
   - receipt 只在 terminal outcome（`imported`/`unchanged`/`rejected`）时写；`SOURCE_REGISTRY_BUSY`/`live_registry_unavailable` 等 retryable 失败不写，留待下次启动重试；`handoff_corrupt` 写 receipt，避免坏 handoff 每次启动重试。
   - 安全语义：用户 `source_reset_registry` 清空 registry 后，**启动扫描不得用旧 handoff 把授权复活**（receipt 命中即跳过）；只有用户再次显式 restore 才重新导入。
3. `SourceAccessRegistry`：
   - 把 `Load`（`:150-191`）中的「读文件 → magic/length → DPAPI → JSON → 结构校验」抽成 `ParseSnapshot(byte[])`；`Load()` 保持现有 `.corrupt-*` 复制与 `SOURCE_REGISTRY_UNAVAILABLE` 语义。
   - 新增 `ImportRestoredSnapshot(byte[])`（在既有 `Locked` 互斥 + `registry.v1.lock` 下）：
     - `live = Load()`（live 损坏 → `SOURCE_REGISTRY_UNAVAILABLE`，不覆盖）；
     - `candidate = ParseSnapshot(bytes)`，候选失败**不**写 `.corrupt-*`（handoff 不是 live 文件），映射为 typed outcome；
     - 合并规则见下表；
     - **只有 `added > 0` 才 `Save`**；否则 live 字节/mtime 不变（零写）。
   - 结果记录 `SourceAccessImportResult`：`Status`（`imported`/`unchanged`/`rejected`/`not_present`）、`Imported`、`Unchanged`、`Conflicts`、`ImportedRevoked`、`Reason`、`Code`。
4. `HostRuntime`：
   - `RestoreBackupAsync`（`:409-414`）在 Core 成功后调用 `TryImportFromHandoff(..., backupId, ...)`；导入拒绝只记 typed 警告，不把数据恢复失败化（跨机 DPAPI 拒绝是预期路径）。**导入路径不得 throw 出 `RestoreBackupAsync`/启动流程**（除 `OutOfMemory` 等不可恢复异常外全部 catch 并记录 outcome）。
   - Host 启动、`Registry = new SourceAccessRegistry(...)`（`:1235`）之后调用 `TryImportPending(...)`；失败只记日志，不阻断启动。**read-only 模式下跳过自动导入**（不写 registry，只记录 pending）；显式 restore 本身已被 `RequireWritesAllowed` 拦截，不会在只读模式写 registry。
   - **不新增** Host/UI 命令；不新增 `HostErrorCodes` 项。

**合并规则（live vs 包内条目）**：

| 情形 | 动作 | 写 live？ |
|---|---|---|
| `registry_id` 在 live 不存在 | 加入（含 `revoked_at` 原样； revoked 条目以 revoked 状态加入） | 有新增才写 |
| 同 id，字段完全相同 | `unchanged` | 否 |
| 同 id，generation/roots/revoked_at 任一不同 | `conflict`，**保留 live**（不覆盖、不复活、不回滚 generation） | 否 |
| live 已 revoked，包内同 id active | `conflict`，保留 live revoked | 否 |
| live 空文件/无文件 | 全部按「不存在」加入 | 有新增才写 |

- 不按 `written_at`/`last_used_at` 做「新旧」判断：只认 `registry_id` 与 live 现状；`generation` 不降级。
- 不探测/重建 root identity（C-15 `:313`）；导入后 `Authorize` 逐请求校验，identity 不符 → `SOURCE_REGISTRY_UNAVAILABLE` 且零写。
- 导入不改变 `CreatedAt`/`LastUsedAt`/`RevokedAt` 的包内值；`WrittenAt` 由 `Save` 更新。
- 导入只接受 `FormatVersion == 1`；`NMSAR2`/JSON `format_version != 1` → `SOURCE_ACCESS_DENIED` / `registry_version_unsupported`。
- **receipt 与「reset 后不复活」**：`ImportRestoredSnapshot` 只负责合并；是否调用由 `SourceAccessRestore` 的 receipt 决定。用户 `Reset(true)` 后，旧 handoff 仍在，但 `TryImportPending` 因 receipt 命中而跳过；只有显式 restore（或用户明确重放 handoff，若未来提供命令）才重新导入。

### 2.5 错误映射（零新增错误码）

| 失败 | code | retryable | reason（Host 结果） | 是否写 live |
|---|---|---|---|---|
| 候选 DPAPI 解密失败（跨机/他用户/OS 重装） | `SOURCE_ACCESS_DENIED` | false | `dpapi_unprotectable` | 否 |
| 候选 registry 版本不符 | `SOURCE_ACCESS_DENIED` | false | `registry_version_unsupported` | 否 |
| 候选 magic/长度/JSON/结构不符 | `SOURCE_ACCESS_DENIED` | false | `registry_corrupt` | 否 |
| handoff 缺失 | 无（`not_present`） | n/a | `not_present` | 否 |
| handoff sha/size 不符 | `SOURCE_ACCESS_DENIED` | false | `handoff_corrupt` | 否 |
| live registry 文件级损坏 | `SOURCE_REGISTRY_UNAVAILABLE` | true | `live_registry_unavailable` | 否（不覆盖） |
| live 锁冲突 | `SOURCE_REGISTRY_BUSY` | true | `registry_busy` | 否 |
| 导入后 root identity 不可用/不符（读路径） | `SOURCE_REGISTRY_UNAVAILABLE` | true | （`Authorize` 既有路径） | 否（identity 校验在 Save 前，C-15 `:313`） |

- 复用 C-06 `:44` 的 `SOURCE_ACCESS_DENIED`（非 retryable，fail-closed）表达「恢复的授权不被接受」；
- 复用 C-15 `:313` 的 `SOURCE_REGISTRY_UNAVAILABLE` 表达 live registry 文件级损坏/读路径 identity 不符；
- **C-06 `:44` 与 C-15 `:313` 的分工**：前者是 grant 申请/失败面的 identity 变化；后者是 registry 文件内 root 的**逐请求** identity 校验（实际实现 `SourceAccessRegistry.Authorize` 返回 `SOURCE_REGISTRY_UNAVAILABLE`）。本卡导入拒绝用前者，导入后的读路径用后者，二者不冲突；
- **不**新增 `HostErrorCodes` 项，**不**改 C-17/C-16 错误闭集；`verify_pins` 不受影响。

### 2.6 allowed_paths（14 条，精确文件级）

> 冻结后由 DSH 写回 `doc/tasks/FEA-13-SRC-6.md` 的 front matter；本报告只给建议清单。`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 的指针翻转属 DSH 生命周期写入惯例，不占实现 allowed_paths（先例：`FEA-13-RESTORE-4` 的 P3-2/`FEA-13-SCHED-5` 的 S5-007）。

| # | path | 类型 | 写入内容 |
|---|---|---|---|
| 1 | `doc/tasks/FEA-13-SRC-6.md` | 治理 | 状态、allowed_paths、AC、证据表、Closeout |
| 2 | `doc/reviews/FEA-13-SRC-6-*.md` | 治理 | 本 scope review、独立 implementation review、返修复核 |
| 3 | `doc/handoffs/FEA-13-SRC-6-*.md` | 治理 | Handoff（实现/复核/集成） |
| 4 | `verification/FEA-13-SRC-6/**` | 证据 | README、日志、fixture、NOT_RUN、变异日志 |
| 5 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs` | 生产（Host） | 抽 `ParseSnapshot`；新增 `ImportRestoredSnapshot`；不新增 wire/命令 |
| 6 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRestore.cs` | 生产（Host，新文件） | handoff 定位/校验、`TryImportFromHandoff`、`TryImportPending`、结果类型 |
| 7 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | 生产（Host） | restore 成功后导入；启动后补导入；日志；不改返回签名 |
| 8 | `src/infrastructure/sqlite/nmbak.py` | 生产（Core） | `source-access` extras 收集/校验/复制；restore handoff；manifest |
| 9 | `tests/storage/test_nmbak_source_access.py` | 测试（Core） | 入包/缺失/读失败/handoff/加密段可读性/变异判别 |
| 10 | `tests/storage/test_nmbak_backup.py` | 测试（Core） | 既有 v2/extras 断言随新类别更新（如有冲突） |
| 11 | `tests/storage/test_nmbak_coverage.py` | 测试（Core） | 类别闭集/声明交叉校验的既有断言更新（如有冲突） |
| 12 | `tests/core/test_core_backup_wire.py` | 测试（Core wire） | `backup.create` 对含 registry 的 data_root 的端到端断言 |
| 13 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceAccessRestoreTests.cs` | 测试（Host，新文件） | 导入正例/冲突/revoked/DPAPI/版本/identity/handoff |
| 14 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` | 测试（Host） | 原生 DPAPI 导入 round-trip / 篡改拒绝（追加用例） |

**不包含**（刻意）：

- `doc/plan/**`、`doc/contracts/**`、任何冻结契约草案/冻结记录 → 本卡不改契约字节；
- `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs` → 不改 wire，不需要；
- `src/application/maintenance/restore_plan.py` → merge restore 不在本卡（§5.4）；
- `src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py` → overwrite handoff 在 `nmbak.restore`；`data_root` 已接线，不需要改；
- `HostErrorCodes.cs` → 不新增码；
- UI/报告/测试的写域只在上表路径内；Avalonia UI 冲突面板不在本卡（若实现需要 UI 变更，须先改 scope）。

### 2.7 out_of_scope（实现卡冻结时必须写明）

1. 跨机恢复/跨用户授权继承；跨机只做 typed 拒绝 + 用户重授权，不实现自动迁移/机器绑定。
2. 包级口令/密钥、registry 明文导出、machine-scope DPAPI 回退。
3. merge restore（`mode=defer/use_backup`）的 Host 暴露与 handoff；本卡只做 overwrite 路径。
4. 数据根迁移（`FEA-13-MIGRATE-6`）与 registry 随迁路径。
5. C-17 journal 的备份/迁移/自动恢复；pending operation 仍 fail-closed。
6. 新命令/新 wire 字段/新错误码；UI 冲突面板（只记日志/既有 restore 结果）。
7. 契约字节、18 pins、M2-C1、V11R wire 文档。
8. `backup/1` 包升级/迁移（仍只读、不就地升级）。

---

## 3. Acceptance Criteria（6 条，均可机器判别，含负例）

> 每条都要求「零写」或「正确写」断言；测试落在 §2.6 的 allowed_paths 内。`<<MET>>` 由实现卡回填。

- [ ] **AC1 入包段与加密不可读（正例 + 字节断言）**
  - 构造 `data_root`：`host/source-access/registry.v1.dat`（**字节断言用真实 DPAPI 或不可读的等价密文**；`Passthrough` 仅用于布局/合并逻辑，不用于本 AC 的「不可读」断言；测试隔离 DataRoot） + 至少一个 healthy source root。
  - `backup.create` 成功且 `verified=true`；manifest `extras` 恰有一项 `category="source-access"`、`relative_path="registry.v1.dat"`，`sha256`/`size_bytes` 与源文件一致；`included_categories` 含 `source-access`。
  - zip 内 `extras/source-access/registry.v1.dat` 与源文件**逐字节相同**，且以 `NMSAR1\0` 开头；成员字节中**不含**明文 `registry_id`、locator、任何绝对 root 路径。
  - Core 代码库中无 DPAPI 调用（`grep -R "CryptUnprotectData\|CryptProtectData" src/` = 0）——Core 只复制密文。
  - 创建前后 registry 文件字节 + mtime 不变（备份只读）。
  - 判别：若实现把明文 JSON 写入包、或 Core 解密/重写 registry，本 AC RED。

- [ ] **AC2 缺失 / 不可读 / 空 registry 的边界（负例 + 零写）**
  - (a) registry 文件存在但读取失败（测试注入 `PermissionError`/读取异常） → `BACKUP_CREATE_FAILED`；无 `.nmbak` 产出；registry 文件字节不变。
  - (b) registry 文件不存在 → create 成功；包内无 `extras/source-access/**`；manifest 不含 `source-access` 类别；restore 后 live registry 不变；Host 导入结果 `not_present`（零写）。
  - (c) registry 文件存在但 `entries=[]`（例如 `Reset` 后的空文件） → 包内**有**成员（文件存在即入包），manifest 记录 size/sha；Host 导入 `unchanged`/零写。
  - 判别：把「缺失」误判成「损坏」使 backup 失败，或把「存在但空」漏掉，本 AC RED。

- [ ] **AC3 恢复后授权可用（正例 + 幂等 + 正确写）**
  - 用 AC1 的包在第二个隔离 DataRoot 执行 Core overwrite restore；**同一个 healthy source root 仍存在**（源根在 DataRoot 之外，便于 identity 复核）；成功后 handoff 位于 `<backup_root>/restore-handoff/<backup_id>/source-access/registry.v1.dat`，`handoff.json` 的 `backup_id`/`sha256`/`size_bytes` 与包内成员一致。
  - Host `TryImportFromHandoff` 后：`Registry.List()` 含该条目；`Authorize(registryId, generation, [healthyFile])` 成功并更新 `LastUsedAt`（读路径可用）；必要时用真实 Core 走一次 grant/read（L2 e2e，见 §4）。
  - 再次导入同一 handoff：`Imported=0`、`Unchanged=n`，live registry 字节 + mtime 不变（幂等/零写）。
  - 空 live registry（无文件）首次导入：条目数 N、generation 原样；`registry.v1.dat` 由 `Save` 原子创建（正确写，恰好一次）。
  - **导入失败不反向失败数据恢复**：用 F-FOREIGN-DPAPI 走完整 restore+import，`RestoreBackupAsync` 仍返回数据恢复成功（rollback id 非空）；DB/managed 已恢复；仅 import outcome 为 rejected。
  - 判别：导入不落盘、落盘两次、`Authorize` 读不到、或导入拒绝把 restore 报成失败，本 AC RED。

- [ ] **AC4 revoked / 代次过期 / 冲突处置（负例 + 零写）**
  - live 有 `R`（generation=2，`revoked_at` 非空）；包内 `R` 为 generation=1 active → 导入 `Conflicts=1`、`Imported=0`；live 字节 + mtime 不变；`Authorize(R,2,…)` → `SOURCE_GRANT_REVOKED`；`Authorize(R,1,…)` 不得成功。
  - live 有 `R`（generation=2 active，roots=A）；包内 `R` 为 generation=1 active（roots=B）→ 保留 live（`Authorize` 仍用 A）；不覆盖、不回滚。
  - 包内 `R` 为 revoked（live 无 R）→ 以 revoked 状态导入；`Authorize` → `SOURCE_GRANT_REVOKED`；不得被当成 active。
  - 「过期」以 generation 不回退表达；不得以 `written_at`/`last_used_at` 覆盖 live。
  - **reset/receipt**：成功导入后写 receipt；`Reset(true)` 清空 live；再调用 `TryImportPending`（模拟重启）→ 因 receipt 命中**不导入**，registry 仍空；只有再次显式 restore 才可重新导入。若缺少 receipt 防护，本 AC RED。
  - **read-only 模式**：启动 `TryImportPending` 不得写 registry（零写；只记录 pending），显式 restore 也不得绕过 `RequireWritesAllowed`。
  - 判别：把包内旧 generation 覆盖 live、把 revoked 复活为 active、reset 后启动扫描复活授权、或 read-only 下写 registry，本 AC RED。

- [ ] **AC5 跨机/他用户 DPAPI、registry 版本、identity 负例（typed + 零写）**
  - 候选 registry 用「会失败」的 `ISecretProtector`（模拟另一 Windows 用户/另一台机器）：导入 `Status=rejected`、`Code=SOURCE_ACCESS_DENIED`、`Reason=dpapi_unprotectable`；live 字节 + mtime 不变。
  - 候选 magic 为 `NMSAR2` 或 JSON `format_version=2`：`rejected`、`SOURCE_ACCESS_DENIED`、`registry_version_unsupported`；live 零写。
  - 候选截断/长度不符/JSON 损坏：`rejected`、`SOURCE_ACCESS_DENIED`、`registry_corrupt`；live 零写；**不**在 live 目录产生 `.corrupt-*`（handoff 不是 live）。
  - identity：导入一个 root 后替换该 root 的物理文件（新 file id）→ `Authorize` 返回 `SOURCE_REGISTRY_UNAVAILABLE`，且 registry 文件字节 + mtime 不变（identity 校验在 Save 前）。
  - 真实跨机/跨用户 DPAPI 无法在本机稳定构造 → 标 `NOT_RUN`（§4.4）；以上 simulated 负例必须 PASS，且报告写明二者差异，不得把 simulated 当 real cross-machine PASS。

- [ ] **AC6 门禁、证据、边界**
  - 定向 pytest 0 failed；定向 `dotnet test` 0 failed；`check.ps1` 默认 + `-TaskPath doc/tasks/FEA-13-SRC-6.md` PASS；`verify_pins` **18/18**；`git status`/diff 仅落在 §2.6 的 14 条 allowed_paths 内。
  - 证据目录 `verification/FEA-13-SRC-6/` 含：README（AC 映射）、pytest 日志、dotnet 日志、门禁日志、加密段不可读的字节探针、handoff/导入正负例、至少 3 条变异日志（每条含命令头 + `EXIT=` + 复原后绿）。
  - 变异至少覆盖：① 冲突覆盖 live → AC4 RED；② DPAPI 失败映射为成功 → AC5 RED；③ 包内写明文 → AC1 RED。
  - 0 契约字节、0 pin、0 DDL、0 新 wire 字段、0 新错误码。

---

## 4. 证据计划（L2）

> 等级沿用 FEA-13 口径：**L2 = 隔离 fixture 的本地可复现证据**；不是生产 e2e，不替代独立 Review。跨机为 `NOT_RUN`（附原因与替代边界）。

### 4.1 L2 fixtures

| fixture | 构造 | 用途 |
|---|---|---|
| F-POS-DPAPI | 隔离 DataRoot；`SourceAccessRegistry`（真实 `DpapiSecretProtector`）注册一个 healthy temp root；写 `registry.v1.dat` | AC1 真实格式；AC3 导入正例（同机同用户） |
| F-POS-FAKE | 同一布局，`PassthroughProtector`/可逆 fake 密文 | Python 侧确定性 fixture；跨语言 CI 不依赖 DPAPI 交互 |
| F-ABSENT | DataRoot 无 `host/source-access/registry.v1.dat` | AC2(b) |
| F-EMPTY | `entries=[]` 的 registry 文件（非零字节；`Reset` 后状态） | AC2(c) |
| F-READ-FAIL | registry 存在，测试注入读取异常/拒绝 ACL | AC2(a) |
| F-REVOKED / F-STALE | live `R` generation=2 revoked；包内 `R` generation=1 active | AC4 |
| F-FOREIGN-DPAPI | 候选密文用 `FailingProtector` 解密（模拟他用户/他机） | AC5 DPAPI 负例；真实跨机 `NOT_RUN` |
| F-VERSION | 候选 magic `NMSAR2` 或 JSON `format_version=2` | AC5 版本负例 |
| F-IDENTITY | 导入后替换 root 物理文件（新 file id） | AC5 identity 负例 |
| F-HANDOFF-BAD | `handoff.json` sha/size 被改 | AC5 handoff 负例 |

### 4.2 命令（实现卡回填，scope 只给计划）

```powershell
python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py tests/core/test_core_backup_wire.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --filter "FullyQualifiedName~SourceAccessRestore|FullyQualifiedName~SourceRegistry" --nologo
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
git status --short
```

判别：pytest/dotnet `0 failed`；check `PASS`；pins `18/18`；diff ⊆ 14 条 allowed_paths。

### 4.3 包内加密段不可读（字节探针）

1. 用 Python `zipfile` 读 `extras/source-access/registry.v1.dat`；
2. 断言前缀 `b"NMSAR1\x00"`，断言长度字段与文件长度关系合法；
3. 断言成员字节不含 `b"registry_id"`、`b"locator"`、fixture 的绝对 root 路径（UTF-8/UTF-16 两种编码都扫）；
4. 断言 `src/` 下无 `CryptProtectData`/`CryptUnprotectData`（Core 不解密）；
5. 把探针做成测试（AC1）而非只在 README 声明。

### 4.4 跨机模拟（`NOT_RUN` 说明）

- **真实跨机/跨用户 DPAPI**：需要另一台 Windows 机器或另一个 Windows 用户配置文件（SID 不同）生成/解密 DPAPI blob；本环境不创建第二用户、不访问用户真实数据 → **`NOT_RUN`**。
- **替代边界**：`FailingProtector` 模拟 unprotect 失败 → 断言 typed `dpapi_unprotectable` + 零写；这证明**失败路径**，不证明真实跨机 DPAPI 字节行为。
- C-15 `:317` 明确「不以 DPAPI 失败作为唯一跨机判据」：另加 identity 负例（F-IDENTITY）证明即使 unprotect 成功，root identity 不符也会 typed 拒绝；报告不得把 simulated 写成 real cross-machine PASS。

### 4.5 证据目录

```
verification/FEA-13-SRC-6/
  README.md                         # AC 映射、fixture、未跑项
  logs/pytest-source-access.log
  logs/dotnet-source-access.log
  logs/check-default.log
  logs/check-task.log
  logs/pins.log
  logs/git-status.log
  logs/probe-encrypted-member.log
  logs/mutation-conflict-overwrite.log
  logs/mutation-dpapi-success.log
  logs/mutation-plaintext-copy.log
  NOT_RUN.md                        # 真实跨机/真实 ACL
```

---

## 5. 风险与回退

### 5.1 DPAPI 跨机/跨用户/OS 重装

- `DpapiSecretProtector` 是 **CurrentUser**、UI forbidden、无 machine-scope 回退（`SourceSecurity.cs:20-24`）；同机同用户有效，跨机/跨用户/重装/新 SID **预期失败**。
- 失败必须 typed（`SOURCE_ACCESS_DENIED` / `dpapi_unprotectable`）且 live 零写；**不得**回退到明文、路径猜测、自动重建 identity（C-15 `:313`）。
- 用户路径：重新 `RegisterSourceRoot` 授权；UI 不提供「跳过 DPAPI」选项。
- 原生 DPAPI 往返测试只在 Windows 交互用户环境可信；测试用 `ISecretProtector` 注入 fake；未取得原生证据时标 `LIMITED`，不得写 PASS（C-15 `:316`）。

### 5.2 registry.dat 版本/布局

- 本卡只接受 `FormatVersion == 1` / `NMSAR1`；未来格式必须 bump 版本并同时改 C-15 + 本卡导入逻辑；本卡不得用 `NMSAR1` 承载 v2 语义。
- 旧包无 `source-access` 段：restore 不写 live registry，`not_present`；不伪装成「已恢复授权」。
- 包被旧二进制读取：未知 extras 类别 → `BACKUP_FORMAT_UNSUPPORTED`（前向兼容，不伪装 corrupt）；发布说明写明「新包需新二进制恢复」。

### 5.3 读并发 / 原子替换

- Core 读 registry 与 Host `File.Replace` 可能竞争：Host `Save` 失败 → `SOURCE_REGISTRY_UNAVAILABLE`（retryable）；Core create 失败 → `BACKUP_CREATE_FAILED`（无半包）。
- 不引入共享锁文件给 Core（Core 不该拿 Host 锁）；用 3×短退避 + typed 失败；如果长期竞争，登记为运维限制，不扩契约。
- 读到的旧/新文件都是完整快照（C-15 `:309` 原子替换）；不存在「读到半个 JSON」的路径。
- **硬读错误会同时阻断 pre_restore**：restore 先 `create("pre_restore")`，若 registry 因 ACL/IO 读失败则 restore 也失败；这是 fail-closed 的代价。用户可用显式 `source_reset_registry`（C-15 `:314`）恢复 registry 后再 restore；不得为「让 restore 通过」而静默跳过必需段。

### 5.4 merge restore 缺口

- 本卡 handoff 只在 overwrite restore 生成；merge restore（`mode=defer/use_backup`）不生成 handoff。
- C# Host 当前未暴露 merge restore（`verification/FEA-13-RESTORE-4/README.md:46`）；登记为已知限制：未来暴露 merge restore 时，必须同时接 handoff/导入，否则不得声称「源授权随 merge restore 恢复」。
- 不在本卡顺手改 `restore_plan.py`，避免扩大写域。

### 5.5 C-17 journal 兼容

- 导入不读写/不迁移 Host journal（`<DataRoot>/host/source-operations/*.v1.dat`）；恢复旧 DB 后 pending operation 可能与导入后的 registry 代次不符。
- C-17 既有恢复逻辑会重新读 live registry、要求同 registry/物理 identity/generation 不低；不符合即 fail-closed，要求重新预览/授权（C-17 `:169`、`:186`）。
- 不在本卡自动恢复 pending operation；不得为了让旧 journal 通过而降低 generation 校验。

### 5.6 备份内容/体积

- registry 上限 4 MiB（`SourceAccessRegistry.cs:157`）；Core 侧同限，超限 `BACKUP_CREATE_FAILED`；包体增量通常 < 4 MiB。
- `pre_restore` 包会包含当前 registry（恢复前状态），这是正确的回滚点；不递归、不复制 `backup/2` 自身。
- 不在包内放 `registry.v1.lock`/quarantine/`.corrupt-*`/`.tmp`。

### 5.7 FEA-15 验收交互

- `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md:18` A8 当前写「源授权元数据未入包 → SRC-6」；SRC-6 完成后应改为「同机恢复有效；跨机须重授权」，**不能整条删除**。
- FEA-15 正式验收若在 SRC-6 之前执行，保留现 limitation；若在之后执行，必须保留跨机 limitation 并指向本卡/重授权路径。
- 更新 FEA-15 文档不在本卡 allowed_paths；由 DSH 在验收轮处理。

### 5.8 数据根迁移 / Host 持久物

- registry 位于 `<DataRoot>/host/source-access/`，随 DataRoot 布局；`FEA-13-MIGRATE-6`（blocked）换根时必须把该文件纳入 Host 持久物清单，否则换根后授权丢失（用户重授权）。
- DPAPI 绑定用户、不绑定路径；换根本身不会使密文失效，但 registry 文件必须随迁。本卡不实现迁移，只登记依赖。

### 5.9 reset 后启动补导入不得复活授权

- 用户 `source_reset_registry` 清空 registry 是显式安全动作；旧 handoff 仍在磁盘上，启动扫描若无条件重放会复活授权（等于绕过 reset）。
- 由 Host 侧 receipt（`host/source-access/imports/<backup_id>.json`）阻断：成功/终止导入后写 receipt，`TryImportPending` 跳过；`Reset` 不清 receipt；只有显式 restore 重写 receipt 并重新导入。
- receipt 本身在 Host 私有目录、当前用户独占；不得包含绝对路径/密文（只含 backup_id/计数/reason）。
- 这是本卡新增的 Host 内部状态，不进入包、不改契约；测试必须覆盖「导入 → reset → 重启扫描不复活」。

### 5.10 回退

- 实现回退：`git revert` 单/多提交；不涉及 DB schema、不涉及 migration；旧包仍可读（无段）。
- 契约回退：0 字节改动、0 pin，无需契约回退。
- 数据回退：restore 仍产生 `pre_restore` 包；handoff 是附加文件，删除不影响已恢复 DB；已导入的 registry 可通过 `source_reset_registry` + 重授权恢复。
- 兼容回退：若新包在旧二进制上不可恢复，发布说明标注；不提供「自动降级包」写入（C-09 禁止就地升级）。

---

## 6. 门禁只读复核（本 scope review 执行）

- 被审 head：`07545adf19a730e2ab640cb1f01e0d15fd4ba70b`（`main`）
- 审查前 `git status --short`：**空**（clean）

| # | 命令 | 结果 |
|---|---|---|
| G1 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；**EXIT 0** |
| G2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md` | 同上；Task 选中 `doc\tasks\FEA-13-SRC-6.md`；**EXIT 0** |
| G3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；**EXIT 0**（C06 `75f8e2b4…`、C09 `dc51226b…`、C17 `cdeee487…` 均 OK） |
| G4 | `git status --short` | 写报告前 clean；写报告后仅 `?? doc/reviews/FEA-13-SRC-6-scope-r1.md`（本文件），无其他改动 |

警告（非阻断，既有）：

1. 11 个非终态 Task（TASK_LEDGER；状态字段不证明活性）；
2. `doc/STATUS.md` 达预算 80%（2932 bytes / 29 lines）；
3. `doc/REBASELINE_PLAN.md` 达预算 80%（6897 bytes / 64 lines）。

> 写入本报告后已重跑 G1–G3，仍 PASS / 18/18 / EXIT 0；`git status --short` 只多出 `doc/reviews/FEA-13-SRC-6-scope-r1.md`（untracked）。`check.ps1` 只读，结果不替代独立 Review 或 DSH 授权。

---

## 7. 不构成什么 / 下一步

- **不构成**实现授权、不构成 Task 释放、不构成 UNFREEZE、不构成契约字节/18 pins 变更、不构成 push 授权。
- 本报告只冻结**建议范围**：14 条 allowed_paths、6 条 AC、证据计划、风险。
- **建议下一步（DSH）**：
  1. 采纳 `READY-TO-FREEZE`（若接受 §1.6 的「Core 只读复制密文 + 文件 handoff」口径）；
  2. 把 §2.6 的 14 条 allowed_paths 与 §3 的 6 条 AC 写回 `doc/tasks/FEA-13-SRC-6.md`，status 从 `proposed` 转 ready/释放；
  3. 按 §1.8 时序由 ZCode（Host/C# 主责）实施；独立 Review 必须 fresh 上下文（不得实现会话自审）；
  4. 若 DSH 选择 Host 显式 staging payload/新命令口径 → 先按 §1.7 走 UNFREEZE，不得直接实施；
  5. FEA-15 A8 在验收轮收窄为跨机 limitation（不整条删除）。
- 若本卡与 `FEA-13-MIGRATE-6` 并行释放，DSH 须在 allowed_paths 中划清 `host/source-access/` 的写域子路径，避免两份卡同时改 registry 布局。
