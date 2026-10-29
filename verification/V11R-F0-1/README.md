# V11R-F0-1 验证证据（Region 写面契约，高风险）

- 任务卡：`doc/tasks/V11R-F0-1.md`
- Owner：core-writer（实现 Agent；**未自审**，独立 Reviewer 由 Lead 指派）
- 分支：`v11r/region-write`，worktree `G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE`
- 基线：任务卡 `base_commit=c73239999`；实际开工时 `git merge --ff-only ba59a6c0d`（纯文档快进，取得冻结任务卡/契约；已获 Lead 批准）。代码分支历史：`ba59a6c0d` + 下述提交。
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（FROZEN；总契约 C067–C076 引用节）
- 提交（逻辑单元）：
  - `bb1f378f7` Core 应用层写用例守卫 + 显式锁 use case
  - `a29c0aeb2` Core IPC 10 条 Region 写命令
  - `25107770c` C# Registry/Dispatcher 注册与 payload
  - 本证据/契约提交（delivery head 见分支 `git log --oneline -4`）

## 1. 交付范围（允许路径内，逐项）

| 层 | 文件 | 说明 |
|---|---|---|
| Core 应用层 | `src/application/editing/service.py` | 既有写入方法 +`expected_revision_no`/`expected_revisions` keyword-only 守卫；新增薄 `set_locks()`；新增 `current_revision()` 读辅助 |
| Core 域 | `src/domain/regions/entities.py` | 新增 `RegionText.lock_translation()`、`Region.set_translation_locked()`（对称域方法，GAP-1 的一部分） |
| Core wire | `src/bootstrap/core_service.py` | 10 条命令 handler + dispatch + typed error 映射 + normalized 几何转换；模块 docstring 契约说明 |
| C# 协议 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 10 条命令注册（Region 域，Core 同名命令，minor 3）；`RegionWriteCommandNames` |
| C# 协议 | `.../HostCommandDispatcher.cs` | `WriteCorePayload` 10 个 case + 几何/映射/锁/文本参数 fail-closed 校验；`internal` 供测试断言 |
| C# 协议 | `.../NewManga.CoreClient.csproj` | `InternalsVisibleTo(NewManga.CoreClient.Tests)`（仅测试可断言 wire payload） |
| 测试 | `tests/core/test_region_write_commands.py` | 31 用例（真实 production Core assembly + 真实 SQLite，`tmp_path`，无硬编码绝对路径） |
| 测试 | `tests/editing/test_region_write_guards.py` | 7 用例（守卫/锁/pin，in-memory 契约 fake） |
| 测试 | `apps/.../tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs` | 注册/minor/精确 payload/边界拒绝/证据 |
| 测试（派生式改造） | `CommandParityContractTests.cs`、`CommandWiringB1Tests.cs`、`CommandWiringB2Tests.cs`、`CommandIntegrationTests.cs` | 66 硬断言 → 从冻结快照 + registry 派生（不改冻结快照 JSON） |
| 契约 | `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` | 新冻结文件 |
| 证据 | `verification/V11R-F0-1/**` | 本目录 |

边界遵守：未改 UI/ViewModel、旧 `apps/desktop`、未 push、未改 main、未改
`doc/contracts/V11R_COMMAND_CONTRACT_V1.md`（core-bridge 独占）、未编辑冻结快照
`verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json`（`git diff --name-only ba59a6c0d..HEAD -- verification/HOST-COMMAND-MIGRATION-1` 为空）。

## 2. 验证命令与结果（全部实测）

环境：Windows 10.0.26100；Python 3.14.6；dotnet SDK 10.0.401（项目目标 net9.0）；pytest 9.1.1。

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2661 passed, 10 skipped, 2 warnings in 215.16s** | `logs/pytest-full.log` |
| G2 | `python -m pytest -q tests/core/test_region_write_commands.py tests/editing/test_region_write_guards.py` | 0 | **38 passed in 2.04s**（本任务新增用例） | `logs/pytest-region-write.log` |
| G3 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| G4 | `dotnet test NewManga.sln --no-build`（`apps/desktop-avalonia`） | 0 | 全绿：App 137/137、Host 39 passed+21 skipped、CoreClient 87 passed+22 skipped；**0 failed** | `logs/dotnet-test.log` |
| G5 | `dotnet test NewManga.sln --no-build --filter "FullyQualifiedName~RegionWriteCommandTests|FullyQualifiedName~CommandParityContractTests"` | 0 | **53 passed / 0 failed**（本任务 + 派生式 parity） | `logs/dotnet-test-region-write.log` |

G4/G5 的 skip 均为**既有环境性 skip**（缺 AC11 sidecar / S4 region fixture 环境变量，见
`Support/SidecarFactAttribute.cs`、`Support/S4RegionFixture.cs`），与本任务无关；无失败用例。
G1 的 10 skipped 同为既有环境性 skip，无失败。改动前基线（同一环境）同样 `python -m pytest -q`
exit 0；未出现与本变更相关的新增失败。

机器可读证据：

- `dotnet-evidence/commands/v11r-region-write-registration.json`：10 条命令的注册/域/通道/Core 命令/minor。
- `dotnet-evidence/commands/parity-contract.json`：66 冻结快照命令 + 派生式覆盖矩阵（含 additive 标记）。
- `commands.json`：本文件 §3 的机器可读版本。

## 3. 验收对照（AC1–AC7）

| AC | 状态 | 证据 |
|---|---|---|
| AC1 复用既有实现 + 10 命令 | ✅ | 契约 §5 映射表；仅 `set_locks` 为 GAP-1 新增薄用例（组合既有域方法，非重写） |
| AC2 typed error + expected_revision + 幂等说明 | ✅ | 契约 §1.2/§1.4/§2；Python 38 用例逐命令覆盖成功/冲突/非法参数；契约逐命令幂等列 |
| AC3 Host/CoreClient 注册 + minor 策略 | ✅ | 契约 §1.1/§4；`RegionWriteCommandTests`（minor=3、精确 payload） |
| AC4 数据安全 | ✅ | 契约 §3；测试含 zero-write 冲突、软删除保留历史、pin 不改 current/不建 revision、重启后几何+三锁+pin 持久化 |
| AC5 pytest + dotnet test | ✅ | §2 G1–G5 |
| AC6 独立审查（非实现者） | ⏳ | 由 Lead 指派 Reviewer；本任务未自审。审查清单见 `REVIEWER_CHECKLIST.md` |
| AC7 契约文档 | ✅（经批准偏差） | `doc/contracts/V11R_REGION_WRITE_CONTRACT.md`；Lead 裁定不并入 A-3 总契约，作为 C067–C076 引用节，见 `CONTRACT_DIFF.md` |

## 4. 数据安全声明（可复核）

1. `current_revision_id` / pinned revision / 历史 `region_revisions` 行不被本任务删除或 upsert；
   所有 revision 写经既有 `commit_region_revision` 原子 seam（`BEGIN IMMEDIATE`）。
2. `pin_revision` 只翻 `is_pinned`，不建 revision、不动 current；`delete_region` 只写 `deleted_at`。
3. 写命令 payload/result 不含 OS 路径/文件名/base64/Managed Copy 路径；不读写用户源文件。
4. 冲突（`INPUT_REVISION_CHANGED`）零写；非法参数在任何持久化前拒绝；内部错误只回固定短语。
5. 测试数据全部临时：Python 用 `tmp_path` 真实 assembly；C# 用 `RepoLocator`/临时目录；
   **新增测试无 `G:\\` 绝对路径硬编码**（C# 既有 `S4RegionFixture.DefaultDataRoot` 是历史遗留，
   本任务未新增、未依赖）。

## 5. 已知 GAP / 风险（详见 `GAPS.md`）

- **GAP-2（未填，超出 F-01 范围）**：Region 文本只读投影在 IPC 上仍缺失（`list_regions` 为最小
  5 字段 DTO；`list_region_revisions` 只给摘要）。Studio Page 初次载入显示已有文本需要后续
  follow-up 读命令；写命令 result 已回显本次写后的 text。**UI 不得伪造文本**。
- GAP-1（已填）显式锁 use case、GAP-3 既有翻译锁双投影、GAP-4 create 无乐观锁（决策）、
  GAP-5 IHostController 便捷方法边界：见 GAPS。

## 6. 复现方法

```powershell
# 在 worktree 根
python -m pytest -q
python -m pytest -q tests/core/test_region_write_commands.py tests/editing/test_region_write_guards.py

# 在 apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test NewManga.sln --no-build --filter "FullyQualifiedName~RegionWriteCommandTests|FullyQualifiedName~CommandParityContractTests"
```

证据目录中的日志为上述命令的原始输出（含 `EXIT_CODE=` 行）；未做任何编辑或截断关键结论。
