# V11R-F0-2 验证证据（Region 文本只读投影，关闭 F0-1 GAP-2）

- 任务：`V11R-F0-2`（团队任务板 task-12；Lead 裁定「GAP-2 必须补，立即执行」）
- Owner：core-writer（**未自审**，独立 Reviewer 由 Lead 指派；与 F0-1 同一审查轮或独立轮）
- 分支：`v11r/region-write`（沿用 F0-1）；基线：`f971ece07`（F0-1 delivery head）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **v1.1**（新增 C077；GAP-2 → CLOSED）
- 代码提交：见 `git log --oneline f971ece07..HEAD`（本证据提交前的实现提交；最终 delivery head 在
  Handoff 中钉 SHA）

## 0. 选型裁定（为什么是 `list_page_region_texts` 而不是 `get_region`）

任务卡允许二选一，判据是「Studio Page 载入一页 region 列表 + 文本在 **1 次**命令内完成（避免 N+1）」：

- Page 工作区首帧**必然**需要该页全部 live region 的文本/锁/确认态（画布覆盖 + 检查器 + 胶片条同源）；
- 单 region `get_region` 会让首帧退化为 `1 + N` 次 IPC 往返（每页通常 5–40 个 region）；
- 因此选择 **page-scoped `list_page_region_texts`**：一次请求返回整页投影；同时提供可选
  `region_ids` 严格过滤（刷新/选中重读），未知或跨页 id → `TARGET_NOT_FOUND`，不引入 N+1 也不放弃
  精确寻址。

## 1. 交付内容

| 层 | 文件 | 说明 |
|---|---|---|
| Core 应用层 | `src/application/editing/service.py` | 新增只读 `list_region_details()`（页级真实投影）+ 共享 `region_text_state()`（四级文本单一投影定义，写/读共用） |
| Core wire | `src/bootstrap/core_service.py` | 新增 `list_page_region_texts` handler（`page_id!` + 可选严格 `region_ids`）+ 归入既有 Region 读分支（typed error 不变）；模块 docstring 契约说明 |
| C# 注册 | `.../Commands/HostCommandRegistry.cs` | `list_page_region_texts`（Region 域、Core 同名、minor 3）；`RegionReadCommandNames` + `V11RAdditiveCommandNames`（10 写 + 1 读） |
| C# 分发 | `.../Commands/HostCommandDispatcher.cs` | `WriteCorePayload` case：`page_id` + 可选 `region_ids`（非空、互异非空字符串，发帧前 fail-closed） |
| C# DTO | `.../Commands/RegionTextProjection.cs` | 新增严格解析 DTO：`RegionPageTextProjection.Parse` / `RegionTextDetail` / `RegionFourTrackText` / `RegionLockProjection` / `RegionGeometryProjection`（缺字段即 `FormatException`，不静默空值） |
| Python 测试 | `tests/core/test_region_text_read_command.py` | 11 用例（见 §3） |
| C# 测试 | `.../Commands/RegionWriteCommandTests.cs` | 注册/minor/精确 payload/边界拒绝 + DTO 严格解析（含中文、null 几何、格式错误） |
| 契约 | `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` | v1.1：C077 全节、选型说明、C# 契约、GAP-2 CLOSED、GAP-3 显式保留、验证出口 |
| 证据 | `verification/V11R-F0-1/GAPS.md`、`verification/V11R-F0-1/README.md` | GAP-2 标 CLOSED（保留原始事实，仅更新状态） |
| 证据 | `verification/V11R-F0-2/**` | 本目录 |

边界遵守：未改 UI/ViewModel、旧 `apps/desktop`、未 push、未改 main；冻结 66 快照
`verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json` 未编辑；未改
`doc/contracts/V11R_COMMAND_CONTRACT_V1.md`（core-bridge 独占）。

## 2. 新命令契约摘要（C077，完整见契约 §2）

```
list_page_region_texts
  request : {page_id: str!, region_ids?: str[] (非空/互异)}
  result  : {page_id, page_size: {width,height}|null, regions: RegionTextDetail[]}
  RegionTextDetail:
    region_id, page_id, region_type, sfx_policy, reading_order,
    geometry: {bbox:[x,y,w,h], polygon:[[x,y],...]} | null,
    text: {ocr_text, machine_translation, edited_translation, final_translation,
           final_source, edited_confirmed, manual_edited, translation_locked},
    locks: {region_locked, translation_locked, inpaint_locked},
    review_state, origin, revision_no, current_revision_id,
    is_pinned, pinned_revision_nos: int[], created_at, updated_at
  errors  : INVALID_REQUEST(validation) / TARGET_NOT_FOUND(not_found, 过滤 id 不存在/软删/跨页) / UNKNOWN
  minor   : 3（零 protocol bump，与 C067–C076 同族）
  语义    : 只读；全部真实投影（未编辑 region 的空串/final_source="none" 是真实值，不补占位）；
            未知 page / 无 region → regions: []（C043 先例：空数据不是错误）；几何在页行不可用时
            为 null，不伪造；reading_order 升序；过滤时保持 reading_order 顺序。
```

## 3. 验证命令与结果（全部实测）

环境：Windows 10.0.26100；Python 3.14.6；dotnet SDK 10.0.401（目标 net9.0）；pytest 9.1.1。

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2672 passed, 10 skipped, 2 warnings in 222.62s**（F0-1 后为 2661；+11 本任务用例，0 failed） | `logs/pytest-full.log` |
| G2 | `python -m pytest -q tests/core/test_region_text_read_command.py tests/core/test_region_write_commands.py tests/editing/test_region_write_guards.py` | 0 | **49 passed**（11 F0-2 + 31 F0-1 wire + 7 F0-1 guard） | `logs/pytest-region-text.log` |
| G3 | `dotnet build NewManga.sln -warnaserror` | 0 | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| G4 | `dotnet test NewManga.sln --no-build` | 0 | 全绿：App 137/137、Host 39 passed+21 skipped、CoreClient **98 passed**+22 skipped；0 failed | `logs/dotnet-test.log` |
| G5 | `dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests|CommandParityContractTests"` | 0 | **64 passed / 0 failed**（F0-1 时 53；+11 本任务用例） | `logs/dotnet-test-region-text.log` |

skip 均为既有环境性 skip（缺 AC11 sidecar / S4 region fixture 环境变量），与本任务无关；无失败用例。
所有测试使用临时数据根（Python `tmp_path`、C# 临时目录/RepoLocator），无新增硬编码绝对路径。

机器可读证据：
- `dotnet-evidence/commands/v11r-region-write-registration.json`（11 条追加命令注册/域/通道/minor）
- `dotnet-evidence/commands/parity-contract.json`（冻结 66 快照 + 派生式追加集覆盖矩阵）
- `commands.json`（本目录，机器可读命令契约与 gate 摘要）

## 4. AC 对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 Core 注册（minor=3，零 bump） | ✅ | 契约 §1.1/C077；Python 测试断言响应 `version.minor==3`；`PROTOCOL_MINOR==3` 断言 |
| AC2 C# 注册（Region 域；显式读集合；快照不改） | ✅ | `RegionReadCommandNames`/`V11RAdditiveCommandNames`；`RegionWriteCommandTests` 注册与 parity 断言；快照文件未改（`git diff` 空） |
| AC3 四轨文本+锁+review_state+is_pinned+几何真实投影 | ✅ | 11 个 Python 用例逐字段对照 `core.editing.get_region` / `current_revision().snapshot`（含真实 OCR/机翻/人工/确认历史、pin、锁、未编辑 region 的真实空值）；C# DTO 解析测试 |
| AC4 未知/越权 region → TARGET_NOT_FOUND；无 region → 空数组 | ✅ | `test_region_ids_filter_rejects_unknown_and_cross_page_ids`、`test_unknown_page_reads_empty_data_not_an_error`、`test_page_without_regions_is_an_empty_list_not_an_error` |
| AC5 Python：正常/多 region/软删不可见/无文本/未知 id；C#：注册/payload/DTO 解析 | ✅ | Python 11 用例；C# payload theory + `RegionTextProjection_*` 三个解析用例 + invalid cases |
| AC6 契约更新 + GAP-2 CLOSED | ✅ | 契约 v1.1 C077/§0/§4/§6/§7/§8/§9；`verification/V11R-F0-1/GAPS.md` GAP-2 = CLOSED |
| AC7 全量 gate 全绿 + 证据 `verification/V11R-F0-2/` | ✅ | §3 G1–G5（exit 0） |

## 5. 数据安全声明（可复核）

1. C077 是**纯读命令**：不写 DB、不建/改 revision、不改 current/pinned、不触碰用户源文件或 Managed Copy。
2. 投影不补默认值/占位：未编辑 region 的空串与 `final_source="none"` 就是持久化真值；几何/页尺寸
   在页行不可用时返回 `null`（不伪造 0 或默认值）；当前指针无法解析时抛内部错误（UNKNOWN），
   不编造一行。
3. 软删除 region 不出现在投影（`list_regions` 既有语义）；过滤 id 必须属于该页且 live，否则
   `TARGET_NOT_FOUND`（无跨页/越权读取面）。
4. 错误消息只含固定短语 / 校验原因；不含路径、原始异常、未请求 region 的文本。
5. GAP-3 双投影保持“原值投影”：`locks.translation_locked`（Region 列）与
   `text.translation_locked`（人工保护旗标）分别返回；**既有 manual save 未改**（契约 §6 GAP-3
   显式保留）。

## 6. 契约变更（v1 → v1.1）

- 新增 **C077** 节（命令、DTO、错误、幂等、语义、选型依据）；
- §0 范围：F-01 写面 + F0-2 读投影；原“非目标：文本只读投影”移除并替换为选型裁定；
- §1.1：11 条命令（10 写 + 1 读）minor=3，零 protocol bump；
- §4：C# `RegionReadCommandNames`/`V11RAdditiveCommandNames` 与 `RegionPageTextProjection.Parse`；
- §6：GAP-2 → **CLOSED**；GAP-3 保留“既有 manual save 未改”的显式说明；
- §7：Studio Page 首帧改为 1 次 `list_page_region_texts`；
- §8/§9：验证出口与 v1.1 变更记录。

## 7. 复现方法

```powershell
# worktree 根
python -m pytest -q
python -m pytest -q tests/core/test_region_text_read_command.py tests/core/test_region_write_commands.py tests/editing/test_region_write_guards.py

# apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test NewManga.sln --no-build --filter "FullyQualifiedName~RegionWriteCommandTests|FullyQualifiedName~CommandParityContractTests"
```

证据目录中的日志为上述命令的原始输出（含 `EXIT_CODE=` 行）；未做编辑或截断关键结论。
