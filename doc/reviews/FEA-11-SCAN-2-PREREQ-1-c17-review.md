---
review: C17 v1.1 UNFREEZE byte-level review（r1）
reviewer: fresh subagent（独立上下文；未参与 C-17 v1.1 提案/实现/前轮复核）
session: subagent-of-session-8db9dae5-49df-4d09-ac62-696f0805a95c（子会话 ID 以 DSH 派发记录为准）
date: 2026-11-06
verdict: APPROVE（P3×6 非阻断）
repo: G:\CODEX\New Manga
branch: main
repo_head: 470f7d2b565fe3e75a3992a6a4417cbdec70233c
worktree: dirty（M C-17/冻结记录/矩阵；?? 载体）；其余契约/ADJ-001 零 diff
reviewed_objects:
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md（未跟踪）
  - doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C17.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
c17_sha256_worktree: aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59
c17_blob_id: f767e158a43652ea092066081e53fa0810e395fb
c17_blob_sha256: 83c05ae9f575600ba93ea325b86214bd1d3207fa6f276c2bdbef5c976dccb9e8
pin_match: true
verify_pins: 18/18 PASS（C17=aefa0fa5b17e）
check_ps1: PASS（3 个既有 warning；-TaskPath）
---

# C-17 v1.1 UNFREEZE 独立 byte-level 复核（r1）

> **结论：`C17-V11-REVIEW: APPROVE`（P3×6，全部非阻断）。**
>
> C-17 v1.1 的契约字节与冻结记录/矩阵/载体在语义上满足本次 UNFREEZE 的冻结范围：只新增只读命令 `source_list_scan_targets`、`ScanTarget`/`ScanTargets` DTO、`source.sync.enumerate/1`（仅 `core.ping.capabilities`）、§5.3 守卫、§8 零新增错误码注记、§9 P3/P7/P8 适用声明与 header/§0 版本；未改既有命令/守卫/§6 CAS/§7 lineage/状态机。C-17 工作树 sha256 实测等于冻结记录 v1.1 pin；`verify_pins.ps1` **18/18 PASS**（C17=`aefa0fa5b17e`）；其余 17 契约与 ADJ-001 零 diff；`check.ps1 -TaskPath` PASS。
>
> 6 项 P3 均为**元数据/文档澄清或后续卡决策**，不改变 C-17 v1.1 的契约字节、pin 或本次冻结结论。建议 DSH 在 UNFREEZE 提交前顺手修 P3-1/P3-2/P3-5（只动冻结记录/矩阵，不动 C-17），在冻结 `FEA-11-SCAN-2` 实现卡前处置 P3-3/P3-4/P3-6。若 C-17 本体字节再改（含 P3-3/P3-4 若选择改契约），pin 必须重算并重新 byte-level 复核。

---

## 0. 复核对象、方法与边界

- **只读**：未修改仓库、未 commit/push、未运行 pytest/.NET；报告与复算临时文件只写仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-c17-v11\`。
- **工作树**：`main` @ `470f7d2b565fe3e75a3992a6a4417cbdec70233c`；`git status --porcelain` 仅 `M doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`、`M doc/plan/FEA-CONTRACT-FROZEN-C17.md`、`M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`?? doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md`。
- **执行过**：`Get-FileHash -Algorithm SHA256`、`git hash-object`、`git cat-file --filters`、`git diff/show/ls-files/status`、`tools/governance/verify_pins.ps1`、`tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2-PREREQ-1.md`；定向阅读 C-17/C-15/C-16/C-06/M2-C1、scope review、PREREQ-1、实现卡与 Core 代码（`schema.py`/`model.py`/`source_sync.py`/`core_service.py`）。
- **CRLF/LF 口径**：C-17/冻结记录/矩阵在 Windows 工作树为 `w/crlf`，C-17 pin 是**工作树原始字节** SHA-256；Git blob ID 与 blob 内容 SHA-256 按 LF 归一化后的 Git blob 计算。两者不同，分别记录，不混用（沿冻结记录 §1A 口径）。

---

## 1. 修订最小性/正确性

### 1.1 实际 diff 仅 8 处（C-17）

`git diff --unified=0` 实测 hunk：

| 位置（v1.1 行） | 内容 | 判定 |
|---|---|---|
| `:3` | header 状态行 `DRAFT v0.1 / 未冻结` → `FROZEN v1.1 / 2026-11-06 UNFREEZE 重冻`（含 v1.0 日期/载体） | 在载体 §2A 范围内 |
| `:12` | §0「文档」行 → C-17 v1.1 + UNFREEZE 载体 | 在范围内 |
| `:18` | §0 末句：v1.1 仅新增枚举命令/DTO；不改既有命令/守卫/错误闭集/§6 CAS/§7 lineage | 在范围内 |
| `:194` | §4 `core.ping.capabilities` 追加 `source.sync.enumerate/1`；明确 Capabilities DTO 仍 7 项、app 面、Host 内部直连、不登记 HostCommandRegistry/C-07、无 UI 面 | 在范围内 |
| `:228` | §5.1 新增 `ListScanTargets / source_list_scan_targets` 行（`{}` closed shape；`ScanTargets`；只读） | 在范围内 |
| `:261-262` | §5.2 新增 `ScanTarget`、`ScanTargets` 两行 | 在范围内 |
| `:279` | §5.3 新增 v1.1 枚举只读守卫 | 在范围内 |
| `:387` | §8 表后“零新增错误码”注记 | 在范围内（载体 §2F 明确要求） |
| `:404` | §9 P3/P7/P8 适用声明 | 在范围内 |

**未改**：§1/§2 SQL、§3 两张状态表、§5.1 既有命令行、§5.2 `Capabilities`/既有 DTO 行、§5.3 既有守卫、§6 CAS/事务、§7 lineage/resolve、§8 表行。`git diff --check` 无 whitespace 错误。

### 1.2 关键约束逐项核对

- **Capabilities DTO 仍恰好 7 项**：§5.2 `Capabilities` 行仍为 `items! Capability[恰好7，按上表顺序]`（`:237`）；`Capability.name` 仍 7 值（scan/plan/apply/relink/repoint/resync/operation）。`source.sync.enumerate/1` 只出现在 §4 `core.ping.capabilities` 字符串列表（`:194`），未进 DTO。**成立。**
- **新命令走 application 面**：§4 `:194` 明写“枚举命令走 application 面（非 host-control），Host 内部直连，不登记 HostCommandRegistry/C-07，不新增 UI 命令面”；§5.1 行亦标“只读枚举；零 DB 写、不建 plan/apply、不铸 grant”。**明确成立。**
- **§8 零新增错误码**：§8 表行数/语义未改，表后 `:387` 明写复用既有闭集（`INVALID_REQUEST`、`SOURCE_BUDGET_EXCEEDED`、`CORE_CAPABILITY_MISSING`、`SOURCE_REGISTRY_UNAVAILABLE`），并称“本表行数与既有语义不变”。**成立。**
- **§9 P3/P7/P8**：`:404` 明写枚举命令按 P3（命令/DTO/错误闭集/unknown 字段负例）、P7（独立 Review/冻结记录/三指纹/pin18）、P8（allowed_paths/旧 17 契约零 diff）执行，不改变 P1/P2/P4/P5/P6。**成立。**
- **header/§0 漂移修正**：v1.0 冻结记录写 FROZEN v1.0，但 C-17 v1.0 header 仍是 `DRAFT v0.1`；v1.1 header/§0 已改为 v1.1 并引用载体。**修正成立。**
- **未误改既有命令/守卫/§6 CAS/§7 lineage/状态机**：diff 仅上述 8 处；`ScanSourceSync`/`Apply*`/`GetSourceOperation`/`GetSourceSyncCapabilities` 行未动；§6/§7 零 hunk。**成立。**

> 非阻断注记（并入 P3-5）：PREREQ-1 AC2 的节清单写“§0/§4/§5.1/§5.2/§5.3/§9 与修订记录”，未列 §8 与 header；但载体 §2A/§2F 与父任务清单明确包含 §8 零码注记与 header/§0，实际 diff 与载体一致。建议 AC2 文字在 closeout 时补 §8/header，避免审计歧义。

---

## 2. 字段/DTO 正确性

### 2.1 `ScanTarget` 逐字段

| 字段 | 契约位置/类型 | 代码事实 | 判定 |
|---|---|---|---|
| `source_id! ID` | `:261`；§5 ID=非空、无路径/控制字符、1..128 | Core `sources.source_id`（`schema.py:619-626`）；Core 生成 `src-<uuid>`（`runtime.py:470`） | 正确；§5.3 守卫另加来源/权威约束 |
| `registry_id! ID` | `:261`；ID | Core `source_locations.registry_id`（`schema.py:632`） | 正确 |
| `generation! G` | `:261`；G=1..2^53-1 | `source_locations.authorization_generation`（`schema.py:633`，>=1） | 正确 |
| `source_kind! ID` | `:261`；ID | `sources.source_kind` CHECK 五值 image/folder/zip/cbz/pdf（`schema.py:621`） | 字段正确；**类型用 ID 而非 scope review 建议的枚举** → P3-3 |
| `identity_digest! H` | `:261`；H=小写64hex | `identity_digest_of(content_digest,volume_serial,file_id,size_bytes)`（`model.py:255-268`），与 §5.2 `:264` 公式一致；facts 来自 `source_locations` | 正确 |
| `project_ids! ID[]` | `:261`；§5 全局 `project_ids 1..20唯一按ID排序`（`:207`） | `page_bindings` 非 superseded 引用集合（`schema.py:698-724`；`source_sync.py:427-463`） | 字段正确；**1..20 vs scope review 建议 10000/`>20` typed skip** → P3-4 |

- **无 `identity_facts`**：`:261` 行无该字段；载体 §2D 明确去掉，避免把 volume/file id 扩大暴露；与 scope review §1.3 建议一致。**成立。**
- **无 `version`**：`:261` 行无 version；载体/scope review 均指出 version 是 Host 侧 opaque 字符串，不是 Core 事实。**成立。**
- **含 `source_kind`**：已补入；Host `SourceReadCoordinator.IssueAsync` 需要 image/folder/zip/cbz/pdf 区分文件/文件夹路径解析（scope review §1.3）。**成立。**

### 2.2 `ScanTargets` 与上限

- `ScanTargets = targets! ScanTarget[]（按 source_id 升序、唯一；空数组合法）`（`:262`）。**排序/唯一/空数组均明确。**
- §5 全局规则：数组上限 10000、单消息/持久 body 最多 8MiB UTF-8、超限 `SOURCE_BUDGET_EXCEEDED`、禁止截断（`:207`）；§5.3 v1.1 守卫再次明写“超过数组上限 10000 或 8MiB → `SOURCE_BUDGET_EXCEEDED`（不静默截断）”（`:279`）。**与既有 §5 规则一致。**
- `targets` 的 eligibility（只含 `is_current=1` location 且 ≥1 非 superseded binding）未在 §5.3 逐字复述，但由 DTO 必填字段 + `project_ids 1..20` + 缺失 location 的 typed skip 隐含；scope review AC-S2-2 会实现侧断言。非阻断；实现卡冻结时建议明写。
- “location facts 缺失/损坏 → 该 target typed skip（不伪造 identity）”（`:279`）：语义是跳过该 target、不产出伪造 identity；“typed skip”在本契约未定义独立 wire 字段/错误。与 scope review 的“无 location/无 binding 不出现在 targets”一致；建议实现卡把 skip 的观测口径写清。

---

## 3. 与 scope review 裁决一致

| 裁决项 | C-17 v1.1 落点 | 判定 |
|---|---|---|
| **B1**：Core 业务目标事实 + Host 持久 registry 核验授权、解析 locator、铸新会话 grant；Core/Host 真值分离 | §5.3 `:279` 明确 `source_id` 来自 Core `sources`、Host 对 registry 缺失/撤销/代次 fail-closed、Core 不返回路径/secret/grant；§5.1 只读枚举不铸 grant；既有 `ScanSourceSync`/C-16 grant 面未变 | **一致，无冲突、无过度承诺。** 契约没有把“Host 铸 grant”写成 Core 行为，也没有由枚举直接授权。 |
| **S-1②**：生产 file-root 缺失/替换 → typed `SOURCE_REGISTRY_UNAVAILABLE` 属 fail-closed；**不**声称“启动前缺失 → missing”，L-G 保留 | `:279` 末句逐字写明“生产 file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` 属 fail-closed（S-1 选项②：不声称‘启动前缺失 → missing’，L-G 保留）” | **一致。** |
| **S-2**：Core `source_id`（`src-<uuid>`）唯一权威；禁 `StableSourceId`/folder registry_id 冒充 | `:279` 明写 `source_id` 必须来自 Core `sources`（`src-<uuid>`），禁止 Host 用 `StableSourceId`/folder registry_id 冒充 | **一致。** 措辞主词为 Host（命令调用方）；App 侧“不再产生”属实现卡 AC-S2-4，建议实现卡同时覆盖 App。 |
| **S-4**：`refresh_source_location_auth` 死代码；撤销/重注册后 Core location auth 不更新；只读切片无法恢复；登记 limitation | C-17 不在契约内解决（未提 S-4）；载体 §4 风险 ⑤ 明确“死代码未修（limitation）”；PREREQ-1 approval 写明“S-4 登记 limitation / L-S4” | **一致，未过度承诺“撤销后可恢复扫描”。** |
| **B2**：不推荐/不采纳 | C-17 无 B2 的第二套索引/持久目标表；仅只读枚举 | **一致。** |

**需要 DSH 在冻结实现卡前决策的两处偏离（P3，不影响本次 C-17 字节结论）**：

1. **`source_kind` 类型**：scope review §1.3/§5.2 建议枚举 `image/folder/zip/cbz/pdf`（`:108`、`:273`）；C-17 v1.1 用 `ID`（`:261`）。Core DB CHECK 已限值，Host `IssueAsync` 也会拒绝未知值；但契约层不封闭。建议改为枚举，或在 §5.3 加一句“Host 对未知 `source_kind` typed 拒绝”。
2. **`project_ids` 上限**：scope review §5.2 建议 `ID[1..10000]`，并明确“scan 的 `MAX_PROJECT_IDS=20` 是另一面”（`:110`、`:273`）；C-17 v1.1 沿用 §5 全局 `project_ids 1..20`（`:207`），载体 §2D 亦写“1..20”。后果是 >20 个 book 共享的 source 无法被 `ScanTarget` 表示，scope review 的 AC-S2-6“>20 → typed skip，不截断/不静默丢”在实现卡中将不可实现（Core 无法返回 21 个 project_ids，Host 也无从得知被跳过）。建议二选一：**(a)** 保持 1..20，明确“>20 的 source 不进入 targets”（并据此改写 SCAN-2 AC）；或 **(b)** 把 `ScanTarget.project_ids` 上限改为 10000（显式覆盖 §5 的 20），并在 §5.3 加“Host 对 >20 project_ids 的 target typed skip（不截断/不静默丢）”。若选 (b)，C-17 字节变动 → 重算 pin、重新复核。

> 另：`doc/tasks/FEA-11-SCAN-2.md:53` 仍是旧示例 `ListSourceScanTargets → {source_id, registry_id, generation, identity_facts, project_ids[]}`（含 `identity_facts`、旧 CamelCase）。该卡仍是 `proposed` 占位，本 UNFREEZE 提交不含它；在冻结实现卡时必须替换为 C-17 v1.1 的 `ScanTarget`，否则下一 Owner 可能按旧形状实现（P3-6）。

---

## 4. 契约一致性

| 参照 | 核对 | 判定 |
|---|---|---|
| **C-16**（grant/MissingObservation） | C-16 grant `scope{sourceId,version,entry[],rendition}`、`MissingObservation{source_id,registry_id,generation,expected_identity_digest,observed_at}` 未改；新 `ScanTarget` 提供 `registry_id/generation/identity_digest`，正好可作为 `MissingObservation` 的 baseline；枚举本身不铸 grant、不读源 | **无冲突。** C-16 字节零 diff（`git status` 无变化）。 |
| **C-15**（locator/存储） | C-15 I-6 规定 Core DB 不存绝对路径、locator 仅容器内相对；`source_locations` 只有 registry_id/generation/content_digest/volume_serial/file_id/size，无路径；C-17 v1.1 DTO 无路径、无 locator | **无冲突。** C-15 字节零 diff。 |
| **C-06**（授权面） | Host 是唯一 grant 授予方；registry 的 generation/revoke/identity 由 Host 核验；C-17 枚举只返回业务事实，授权失败由 Host fail-closed；不新增自动重新授权 | **无冲突。** C-06 字节零 diff。 |
| **M2-C1**（typed IPC，无增量） | C-17 §0 明写“命令面由 C-17 承载，M2-C1 无增量”；新命令走 application 面，复用 ErrorEnvelope；`source.sync.enumerate/1` 只是 `core.ping.capabilities` additive 字符串；不改全局 taxonomy/旧命令 | **无冲突。** M2-C1 字节零 diff；rev 2.14 不变。 |
| **C-07/HostCommandRegistry** | §4 `:194` 明写不登记 HostCommandRegistry/C-07、不新增 UI 命令面；Host 内部直连 | **明确。** C-07 未改。 |
| **旧 Core fail-closed** | §4 既有文本“任一 probe 异常/缺能力 → `CORE_CAPABILITY_MISSING`；不以 `UNKNOWN_COMMAND` 探测”；§4 兼容表“旧 Core → capability 缺失拒绝同步；旧面继续”；§5.3 registry 缺失/撤销 Host fail-closed | **保留。** 新命令不会在旧 Core 上被误探测。 |
| **错误码零新增** | §8 表未增行；§8 `:387` 注记复用既有闭集；新命令可见错误均落在既有码（`INVALID_REQUEST`/`SOURCE_BUDGET_EXCEEDED`/`CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_SYNC_STORAGE_FAILED`） | **成立。** |
| **新命令 app 面** | §4 `:194` + §5.1 `:228`；与 host-control 的 Scan/Apply/ACK 面分开 | **明确。** |

---

## 5. 冻结/治理

### 5.1 独立 pin 实测

| 项 | 实测值 | 来源/方法 |
|---|---|---|
| C-17 v1.1 工作树 sha256 | `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59` | `Get-FileHash -Algorithm SHA256`；**等于**冻结记录 §1 `:15` v1.1 pin |
| C-17 v1.1 Git blob ID（LF） | `f767e158a43652ea092066081e53fa0810e395fb` | `git hash-object -- doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（filter 后） |
| C-17 v1.1 blob 内容 SHA-256（LF Git blob bytes） | `83c05ae9f575600ba93ea325b86214bd1d3207fa6f276c2bdbef5c976dccb9e8` | 手工构造 `blob <len>\0` + LF 内容后 SHA-256 |
| （C-17 v1.1 原始 CRLF blob bytes SHA-256，仅对照） | `aa43ac7a9e5d33dcf610d500197914db42fcbdec98e61afaa2e100d05f75fd9d` | 原始工作树字节 + `blob` header；**不是** Git blob 口径 |
| C-17 v1.0 历史 pin | `86b89ff83c9a818311d9d7f498a83e7984a77856cddc8b60bf9308bfb10f2c36` | `git cat-file --filters e94c4b8:...` 后 SHA-256；与冻结记录 §1 历史行一致 |
| C-17 v1.0 blob ID / blob SHA-256 | `9c6394bf1e56025611872e20679826343153f589` / `b6766e1a5b50c28af739639cb8da29dd2b5a5f36bf0f2745a127c41a8e5ca1f5` | `git cat-file blob` 后独立复算；与冻结记录 `:18-19` 一致 |

### 5.2 `verify_pins.ps1` 18/18

实测输出：

```text
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b acc8f0e03d42
OK C05 f6e6f3cb1fe1
OK C06 8faa8cd139f2
OK C07 3fdb44e49afe
OK C08 453f993c1a16
OK C09 dc51226b336c
OK C10 ec8fd862f95f
OK C11 44f4273f7ad1
OK C12 f49835860143
OK C13 8faf1e805eac
OK C14 05056cbf65f9
OK C15 d8c0a3bcfc21
OK C16 0b9511a55ea1
OK C17 aefa0fa5b17e
OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 18)
```

C17 pin 来自冻结记录 §1 `:15`（脚本 `Select-String '^\|\s*sha256...'` 首个匹配），实测与 C-17 工作树一致。**18/18 PASS。**

### 5.3 其余 17 契约与 ADJ-001 零 diff

- `git status --porcelain` 仅 4 个路径（3 个 `M` + 载体 `??`）；`git diff --name-only HEAD -- doc/plan doc/contracts` 仅 C-17/冻结记录/矩阵。
- C-16/C-15/C-06/M2-C1/ADJ-001 的 `git status --porcelain -- <files>` 为空；`verify_pins` 其余 17 项全部 OK。
- 无 schema/migration/依赖/代码改动；未运行生产实现。

### 5.4 冻结记录

- v1.1 sha pin 已填且与实测一致；v1.0 历史 sha `86b89ff8…`、blob ID `9c6394…`、blob SHA-256 `b6766e…` 均保留且经独立复算一致；回退条件写明“恢复 v1.0 字节与冻结记录/matrix；SCAN-2 实现卡不释放”。
- v1.1 UNFREEZE 记录（§1C）写明触发/授权/修订内容/复核待补/pins/回退；`APPROVE 前 sha 行不构成最终 pin 声明` 的限定存在。
- **P3-1**：§1B `:34` 仍写“最终冻结字节三指纹”并给 **v1.0** 的 `86b89ff8…/9c6394…/b6766e…`，未标 v1.0；同时 `:17` 的“历史：v1.0 的 pin 为…”被插在 §1 表格中间（`:16` 空行 + `:17` 段落 + `:18-21` 无表头的行），Markdown 表格被截断，`:18-21` 的 blob ID/blob SHA-256/迁移版本/per-command 行不会再渲染为表格。建议：把 v1.0 历史移到表格之后或独立“v1.0 历史”小节；`§1B` 行显式标“v1.0”；UNFREEZE 提交后补 v1.1 blob ID `f767e158…` / blob SHA-256 `83c05ae9…`。**非阻断**（pin 行仍可被 verify_pins 正确读取）。
- **P3-5**：§2 `:55` 仍写“C-17 v1.0”；§3 `:65` 仍写“verify_pins仅追加第18项”；C-17 `:401` P7 仍写“当前17/17不是18项完成”；`:38` “本记录已由 DSH 冻结（FROZEN v1.1）”在复核前预写。建议在 closeout 时标为 v1.0 历史并补 v1.1 现状（18/18、pin `aefa0fa5…`），或保留但明确“v1.0 历史”。**非阻断。**

### 5.5 矩阵

- C-17 行 `:39` 已由 `DRAFT` 改为 `FROZEN v1.1`（2026-11-06 UNFREEZE 重冻；v1.0 2026-11-04），与冻结记录/载体一致。
- **P3-2**：同一行最后列仍写“Review/冻结未完成”（该列在其它行是“阻塞项/未完成”）；本复核 APPROVE 后应改为“无（实现释放归 FEA-11-SCAN-2）”或“Review 完成/待 DSH 重冻”。矩阵 `:3` 仍写“17 个冻结对象”，未提 C-17/pin #18；建议改为“17 个既有冻结对象 + C-17（pin #18，18 pins）”或等价说明。**非阻断**（状态列已正确）。

### 5.6 载体

- 触发/授权链：用户 2026-11-06「让 Codex 判断下一部任务，由 DSH 执行」→ Codex `NEXT-TASK=FEA-11-SCAN-2`（先 scope review、优先 B1）→ scope review `READY-WITH-UNFREEZE` → DSH 裁决 B1/S-1②/S-2/S-4；载体 §1-§2 写明。**成立。**
- 逐项修订：§2A–§2G 与 C-17 实际 8 处 diff 对应；§2G 的 pins/冻结记录/矩阵/零 diff 与实测一致。**成立。**
- 复核要求：§5 写明 fresh subagent、只读、最终字节、APPROVE/P3、提交范围、随后重冻/释放 SCAN-2。**成立。**
- 回退：§4 给出 v1.0 sha `86b89ff8…`、恢复冻结记录/matrix、SCAN-2 不释放。**成立。**
- 兼容/影响：§3 的旧 Core fail-closed、新 Host×旧 Core 旧面继续、无 schema/M2-C1/C-16/C-15/C-06 字节变化、旧 v7 schema gate/C-16 导入/C-15 读规则不变，与契约/实测一致。**成立。**
- 风险：S-1 registry resilience limitation、S-4 死代码 limitation、大库预算、18 pins 重冻；与 scope review/裁决一致。**成立。**

### 5.7 治理检查

`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2-PREREQ-1.md` → `Governance check: PASS (3 warnings)`；warning 为既有“11 个非终态 Task”“STATUS 80% 预算”“REBASELINE_PLAN 80% 预算”，与本次变更无因果。**PASS。** PREREQ-1 仍 `status: ready`、AC 未勾选；复核 APPROVE 后由 DSH 提交/关闭，符合流程。

---

## 6. Findings（P3，非阻断）

### P3-1 冻结记录 §1B/§1 的 v1.0/v1.1 三指纹与表格结构

- **位置**：`doc/plan/FEA-CONTRACT-FROZEN-C17.md:16-21`、`:34`、`:38`。
- **问题**：`§1B` 的“最终冻结字节三指纹”仍是 v1.0（`86b89ff8…/9c6394…/b6766e…`）且未标 v1.0；`:17` 的 v1.0 历史段落插在 §1 表格内，导致 `:18-21` 的 blob ID/blob SHA-256/迁移版本/per-command 行失去表头；v1.1 的 blob ID/blob SHA-256 未记录。
- **影响**：审计者可能把 v1.0 三指纹误读为 v1.1；表格渲染不完整；不改变 pin/18 项结论。
- **建议文本/动作**：把 `:17` 历史移到表格之后，或改为独立“v1.0 历史”小节；`§1B` 行改为“v1.0 最终冻结字节三指纹（历史）”；UNFREEZE 提交后追加“v1.1 三指纹：工作树 `aefa0fa5…` / blob ID `f767e158…` / blob SHA-256 `83c05ae9…`”。只动冻结记录，不动 C-17。

### P3-2 矩阵 C-17 行尾列与表头计数

- **位置**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:3`、`:39`。
- **问题**：行状态已 FROZEN v1.1，但“阻塞项/未完成”列仍写“Review/冻结未完成”；表头仍“17 个冻结对象”，未提 C-17/pin #18。
- **影响**：矩阵自相矛盾；不影响 pin。
- **建议**：复核 APPROVE/重冻后把尾列改为“无（实现释放归 FEA-11-SCAN-2）”；表头改为“17 个既有冻结对象 + C-17（pin #18；共 18 pins）”或等价。

### P3-3 `ScanTarget.source_kind` 用 `ID` 而非封闭枚举

- **位置**：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:261`；对照 scope review `:108`、`:273`。
- **问题**：scope review 建议 `source_kind! "image"|"folder"|"zip"|"cbz"|"pdf"`；C-17 v1.1 用 `ID`，契约层不拒绝未知值。Core DB CHECK 与 Host `IssueAsync` 会兜底，但闭集不在 DTO 层。
- **影响**：若未来 Core 返回/损坏出未知值，Host 行为依赖实现侧校验；不改变现有五值。
- **建议**：改为五值枚举；或在 §5.3 加“Host 对未知 `source_kind` typed 拒绝（既有错误闭集）”。若改 C-17 字节，重算 pin/重审；也可仅在实现卡 AC 中明确，保持 C-17 字节不变。

### P3-4 `ScanTarget.project_ids` 1..20 与 scope review 的 10000/`>20` typed skip

- **位置**：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:207`、`:261`；载体 `CONTRACT-UNFREEZE…:34`；对照 scope review `:110`、`:273`、AC-S2-6 `:224`。
- **问题**：§5 全局规则把 `project_ids` 限为 1..20；scope review 建议 `ScanTarget.project_ids` 上限 10000，并让 Host 对 >20 的 source `typed skip`。C-17 v1.1 未给 >20 规则，>20 source 无法被 DTO 表示；实现卡若照 AC-S2-6 实现会与契约冲突。
- **影响**：>20 book 共享源可能在枚举中不可见（或被实现侧静默丢弃），与 scope review“不静默丢”目标不一致；不影响常规 ≤20 目标。
- **建议**：在冻结 `FEA-11-SCAN-2` 前二选一：**(a)** 保持 1..20，并在实现卡 AC 明写“>20 source 不进入 targets（记录于 status/日志，不静默实现为失败）”；或 **(b)** 把 `ScanTarget.project_ids` 上限改为 10000（显式覆盖 §5 的 20），§5.3 加“Host 对 >20 project_ids 的 target typed skip（不截断/不静默丢）”。选 (b) 会改 C-17 字节 → 必须重算 pin 并重新 byte-level 复核。

### P3-5 v1.0-era 文案残留（冻结记录/C-17 §9）

- **位置**：`FEA-CONTRACT-FROZEN-C17.md:38`、`:55`、`:65`；`FEA-C17_SOURCE_SYNC_DRAFT.md:401`。
- **问题**：“C-17 v1.0”“verify_pins仅追加第18项”“当前17/17不是18项完成”是 v1.0 冻结期表述；v1.1 已是 18/18、pin 重算而非追加。
- **影响**：历史可读性/审计歧义；不影响 pin/契约。
- **建议**：closeout 时标为“v1.0 历史”，并补 v1.1 现状（18/18、C17=`aefa0fa5…`）；不要求改 C-17 契约字节，但若改 §9 文本则需重算/重审。

### P3-6 实现卡 `FEA-11-SCAN-2.md:53` 的旧 DTO 示例

- **位置**：`doc/tasks/FEA-11-SCAN-2.md:53`。
- **问题**：仍写 `ListSourceScanTargets → {source_id, registry_id, generation, identity_facts, project_ids[]}`（含 `identity_facts`、旧 CamelCase），与 C-17 v1.1 的 `ScanTarget`（无 `identity_facts`、含 `source_kind`、`source_list_scan_targets`）不一致。该卡是 `proposed` 占位，本 UNFREEZE 提交不含它。
- **影响**：下一 Owner 按旧示例实现会重复 scope review §1.3 已否定的字段。
- **建议**：冻结 `FEA-11-SCAN-2` 时（PREREQ-1 AC5）替换为 C-17 v1.1 DTO；不属于本次 UNFREEZE 提交的阻断项。

---

## 7. 回退 / 风险

- **回退条件**：若本复核被否决或用户要求回退，恢复 C-17 v1.0 字节（sha `86b89ff83c9a818311d9d7f498a83e7984a77856cddc8b60bf9308bfb10f2c36`）与冻结记录/matrix；SCAN-2 实现卡不释放。载体 §4 与冻结记录 §1C 已写明。
- **不变量**：无 schema/migration/依赖；C-16/C-15/C-06/M2-C1/ADJ-001 零 diff；旧 Core fail-closed；旧 v7 schema gate/C-16 导入/C-15 读规则不变。
- **残余风险**：① S-1 registry resilience 未解决（生产 file-root 缺失/替换仍整库 `SOURCE_REGISTRY_UNAVAILABLE`；L-G 保留）；② S-4 `refresh_source_location_auth` 死代码（撤销/重注册后 Core location auth 不更新；只读切片无法恢复）；③ `project_ids` 1..20 vs >20 共享源（P3-4）；④ `source_kind` 非枚举（P3-3）；⑤ 大库 >10000 targets / >8MiB 时枚举整体 typed 失败（scope review L-E 未标定 SLA）；⑥ 本复核为最终字节复核，但 C-17 在 UNFREEZE 提交后若再改任何字节，pin `aefa0fa5…` 失效，必须重算/重审。
- **不要**：把本复核当作 SCAN-2 运行时实现授权；不要释放 `FEA-11-WATCH-1`；不要把 S-1② 写成“启动前缺失 → missing”；不要用 `StableSourceId`/folder registry_id 替代 Core `source_id`。

---

## 8. 结论

```text
C17-V11-REVIEW: APPROVE
```

本复核对应工作树 SHA：**`aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59`**（C-17 v1.1，HEAD `470f7d2b5`；blob ID `f767e158…`；blob SHA-256 `83c05ae9…`）。该 SHA 等于冻结记录 §1 `:15` 的 v1.1 pin，`verify_pins.ps1` 18/18 PASS。

**可提交 UNFREEZE 提交**（载体 + C-17 + 冻结记录 + 矩阵），前提：P3-1/P3-2/P3-5 的元数据修正只动冻结记录/矩阵，不动 C-17 字节；提交后由 DSH 重新冻结并释放 `FEA-11-SCAN-2` 实现卡。P3-3/P3-4/P3-6 应在冻结实现卡前决策/修正；若选择修改 C-17 字节（如 `source_kind` 枚举或 `project_ids` 10000），则本 pin 失效，须重算三指纹并重新 byte-level 复核。

复核者：fresh subagent（独立上下文；未参与 C-17 v1.1 提案/实现/前轮复核）；只读，未修改仓库。
