# FEA-15-DIAG-ACL-1 只读诊断记录

**记录时点：** 2026-11-11 00:36:13 UTC（Asia/Shanghai 08:36:13）

**诊断基线：** `1e4542a047e991a5f10b0b213ca5a96eafe919a4`

**本次开始 HEAD：** `5ed87d05d95e6b861c297c3063905b60e5fe7b7c`

**分支：** `main`
**Task 状态：** `in_progress`

本 Task 只读诊断。没有修改生产代码、测试、依赖、Schema 或冻结契约，没有更改/撤销系统解释器 ACL，没有清理文件或 AppContainer profile，也没有访问真实用户库。

## 结论摘要

| 主题 | 已证实 | 尚不可判定 | 当前处置 |
|---|---|---|---|
| 插件 sandbox / export hook | 相同失败族在主树、隔离 clean-tree 和专用 venv 对照中均出现；插件未产生预期结果，export audit 未见 hook 调用；源码对 `SandboxError` fail-closed | 失败发生于 profile 建立、`icacls` ACL 授权、`CreateProcessW`、AppContainer 运行或其他阶段中的哪一处；既有系统 ACE/profile 是否由本次运行产生 | 记录为可复现失败、根因未定；不再运行会改 ACL/profile 的测试，不清理已有授权 |
| Host ACL | `dotnet-full.log` 有 `SourceSecurity.PrivateDirectory` → `SetAccessControl` → `SetSecurityInfo` 的 `UnauthorizedAccessException`；archive 控制中另一项 Host ACL 样例仍失败；G:/C: 的 NTFS 均报告支持持久 ACL | 原 Host 失败的具体拒绝条件、适用环境边界；简单 PowerShell ACL 成功不能证明 Host 原方法成功 | 记录为独立 ACL 失败疑点；精确 `SourceSecurity.PrivateDirectory` 反射探针 `NOT_RUN` |
| Python ACL / AppContainer profile | 测试代码会调用 `icacls /grant`，AppContainer profile 可创建或复用；`close()` 只关闭对象状态 | `C:/Python314` 48/24 ACE 行中哪些由哪次运行新增；哪些用户级 profile 由本次测试创建 | 全部 `PRESERVE_UNKNOWN`，不修改、不撤销、不删除 |
| 62 个 FEA-11 fixture 候选 | 路径固定在共享 `G:/CODEX/New Manga.workspace/FEA-11/fixtures`；本轮时间窗口内观察到 62 项，目录由测试按用例名创建 | 单凭时间戳无法确认唯一创建者、是否仍被其他任务引用或可安全处置 | 继续原位保留；不清理 |
| v7 测试构造 | 未迁移 v7 fixture 缺少 v12 引入的 `chapters.custom_rank`；v14 正向内存探针迁移后对缺失章节查询返回 `None` | 不代表真实用户库迁移、业务数据完整性或回退已验证 | 记录为测试构造债；真实库仍不得访问 |

## 证据矩阵

所有历史测试日志均保留其自身的生成 HEAD、环境、命令和 EXIT；它们不是在本次 `5ed87d0` 上重跑的结果。

| 场景 | 实测结果 | 证据与限度 |
|---|---|---|
| clean-tree 全量 Python 回归 | 3515 passed / 16 failed / 12 skipped，EXIT 1 | `../FEA-15-ACCEPT-1/pytest-full-retry.log`，生成 HEAD `d63d735a712dbe47100db2e72b4d59a73dfd1f62`；失败含 sandbox、export hook、v7 fixture，不能等同产品缺陷总数 |
| 主树插件与 export hook 定向回归 | 4 passed / 15 failed，EXIT 1 | `../FEA-15-ACCEPT-1/pytest-main-targeted.log`，同隔离环境复现。export 测试断言应有 2 条 `hook_invoked`，实际 0；这支持“hook 未到达”，不能单独定位拦截层 |
| 专用 venv 插件对照 | 6 passed / 10 failed，EXIT 1 | `../FEA-15-ACCEPT-1/plugin-control.log` 与 `plugin-fixture.log`；`sys.executable` 确认为任务目录 venv，但其标准库/用户包仍依赖系统安装，不能视作完整独立解释器对照 |
| .NET 全量 | Host 198 passed / 123 failed / 74 skipped；8 项目中 2 项失败，整体 EXIT 1 | `../FEA-15-ACCEPT-1/dotnet-full.log`，HEAD `d63d735a712dbe47100db2e72b4d59a73dfd1f62`。失败混有 Host 仓库定位、ACL 与其他拒绝路径；不把全部 123 项归成同一原因 |
| Host archive 代表性对照 | 1 passed / 1 failed，EXIT 1；失败为 `UnauthorizedAccessException`，堆栈落在 `SetSecurityInfo` / `SourceSecurity.PrivateDirectory` | `../FEA-15-ACCEPT-1/dotnet-host-control.log`，用于证明 `.git` 形态对照不能解释该 ACL 样例；只有代表测试，不能外推全部 Host 失败 |
| 文件系统能力观察 | G:、C: 都为 NTFS 且 `FILE_PERSISTENT_ACLS=True`，EXIT 0 | `volume-winapi.log`。`volume-observation.log` 中 `fsutil fsinfo volumeinfo` 对两个卷均 Error 5 / EXIT 1；这仅说明该命令无法读取卷信息，不说明 `SetSecurityInfo` 的拒绝原因 |
| 独立 PowerShell ACL 等价探针 | 新建隔离目录上 `Set-Acl` 操作成功，所有者为当前用户，EXIT 0 | `acl-probe.log`。日志未保存完整探针脚本；API 调用、运行时和目录与 Host 控制不同，因此仅说明该次 PowerShell 操作成功，不能当作 Host 原方法复测 |

## 失败链与适用边界

### 插件 sandbox / export hook

当前实现中的调用链是 `PluginService._invoke_sandboxed` → `AppContainerSandbox.prepare_plugin` / `run`。profile 路径通过 `CreateAppContainerProfile` 创建，若已存在则由 SID 派生；解释器和插件目录权限通过 `icacls <path> /grant *<sid>:<rights>` 授予。若底层抛出 `SandboxError`，服务将其转换为 `PLUGIN_HOOK_UNAVAILABLE`，保持 fail-closed。`_grant` 只记录通用错误，不将 `icacls` stderr/返回码细节带到调用方，因此现有 pytest 输出不能定位实际失败调用。

跨主树、clean-tree 和专用 venv 仍出现失败，足以排除“仅 linked worktree `.git` 文件形态导致全部 sandbox 失败”的解释；不能据此断言系统 Python ACL 是根因。现存用例断言失败可能发生在 sandbox 初始化或启动任一阶段，现有记录没有失败操作的原始 Win32 错误/`icacls` stderr。

源码 `AppContainerSandbox.close()` 仅设置 `_closed=True`，没有撤销 ACL 或删除 profile。此前 `python-acl-observation.log` 是运行后检查、无运行前快照：`C:/Python314/python.exe` 观察到 48 行 AppContainer ACE，`C:/Python314` 观察到 24 行。它不能确定行数变化、SID 归属或本轮增量。profile 也没有事前清单，所以无法把现有 profile 归因到本轮。不得清理这些资源。

### Host `SetSecurityInfo`

`SourceSecurity.PrivateDirectory` 先拒绝重解析祖先并创建目录，再构造“设 owner + DACL 受保护 + 当前 SID FullControl”安全描述符，最后调用 `DirectoryInfo.SetAccessControl` 并读取验证。Host 全量日志记录 `UnauthorizedAccessException`，代表对照明确落在 `SetSecurityInfo`。本 Task 新增的卷能力观察确认两个卷均支持持久 ACL，故“卷格式完全不支持 ACL”不符合观测；它仍不能区分调用身份/特权、父路径授权、owner/DACL 操作、运行时/API 路径等因素。

**Host 原方法探针状态：`NOT_RUN`。** 曾请求对全新 Task 目标目录反射调用已有 `NewManga.Host.dll` 的 `SourceSecurity.PrivateDirectory`。自动审批审核服务因使用额度耗尽未执行该命令；这不是安全性判断，也没有测试结果。不能用 `acl-probe.log` 的 PowerShell 等价操作替代此探针。恢复条件是自动审批服务可再次审核后，在全新 Task 专属目录重试，并保存原始异常、HResult/Win32 错误、当前身份与目标目录安全信息；仍不得更改系统解释器 ACL 或清理任何资源。

## 资源归属与建议

| 资源 | 归属判断 | 建议 |
|---|---|---|
| `C:/Python314/python.exe` 与 `C:/Python314` 上的 AppContainer ACE | 未知；没有前置 ACL 快照，不能区分历史遗留与本轮新增 | `PRESERVE_UNKNOWN`。仅在后续专门 Task 获准、采用隔离解释器并有前置/后置快照时再调查；不尝试“恢复默认 ACL” |
| 用户级 AppContainer profiles | 未知；代码会创建或复用，既有测试没有前置清单 | `PRESERVE_UNKNOWN`。先只读盘点和记录 SID/name/时间，再经独立裁决决定范围；本 Task 不枚举/删除 profile |
| FEA-11 fixture 目录下 62 个候选 | 时间戳窗口及用例名与测试相关，但不足以证明专属/无人引用 | 保持整目录原位。后续新测试使用 Task 专属隔离 scratch root；旧目录只有经资源所有者核验和独立授权才处置 |
| 本 Task `acl-probe-001` | 本 Task 新建、仅用于等价 PowerShell ACL 探针；已有日志标记保持 | `PRESERVE_REFERENCED`；本 Task 不清理 |
| 精确 Host 探针目标 | 未创建；Host 原方法调用未执行 | 无待清理资源 |

### v7 测试构造债

`v7-repro-2.log` 记录未迁移的 v7 fixture 查询当前 schema 时缺少 `custom_rank`；`v7-v14-probe.log` 记录同一内存探针完整迁移到 v14 后查询正常返回 `None`。当前 schema 从 v12 起含 `chapters.custom_rank`。这证明 fixture 状态与当前查询路径不匹配，不证明真实旧库迁移或用户数据安全；修测试应另行释放 Task，本只读诊断不改测试。

## 本次新命令

| 时间 / HEAD | 命令或观察 | 结果 |
|---|---|---|
| 2026-11-11 00:59:41 +08:00 / `5ed87d05d95e6b861c297c3063905b60e5fe7b7c` | `fsutil fsinfo volumeinfo G:,C:` | 两卷各 Error 5，EXIT 1；见 `volume-observation.log` |
| 2026-11-11 00:59:59 +08:00 / 同上 | `GetVolumeInformationW`（只读） | 两卷 NTFS、持久 ACL 支持，EXIT 0；见 `volume-winapi.log` |
| 2026-11-11 01:00:24 +08:00 / 同上 | PowerShell 等价 ACL 探针 | 新目录操作成功，EXIT 0；见 `acl-probe.log` |
| 2026-11-11 08:36 +08:00 / 同上 | 只读查看 Task workspace 与 `acl-probe-001` | 目录存在，未写入/移动/删除；原始检查见 `workspace-observation.log` |

## AC 状态建议与待办

| AC | 当前诊断状态 | 收口前仍需 |
|---|---|---|
| AC1 sandbox/export | `PARTIAL`：失败跨多环境复现、调用链与边界已记录；底层失败阶段不可定位 | ZCode 复核是否接受作为有边界的诊断结论；若要求确因复现，待自动审批审核可运行精确探针 |
| AC2 Host ACL | `PARTIAL`：原始堆栈和适用范围有界；卷能力不支持简单格式归因；精确 Host 方法探针 `NOT_RUN` | 在新的 Task 目录中重试精确原方法探针；保留原异常和身份信息 |
| AC3 资源影响 | `PARTIAL`：归属不可判定，但证据缺口和保留原则已逐项列出 | 不做系统 ACL/profile 修改或清理；由 ZCode 裁决后续是否需要独立资源审计 |
| AC4 fixture | `MET`：62 项只按时间窗识别，建议和实际处置均为原位保留/零清理 | Review 确认该限制说明充分 |
| AC5 建议与交付 | `PARTIAL`：矩阵、v7 债和 NOT_RUN 已记录；独立 Review、门禁证据、最终 pin/提交/裁决未完成 | 完成 checkpoint、门禁复跑、独立 ZCode Review 和 ZCode 终态裁决；按结果更新 Task/STATUS/PLAN/ledger 与 Canonical Evidence |

## NOT_RUN 与限制

- `SourceSecurity.PrivateDirectory` 原始 Host 方法反射探针：`NOT_RUN`（自动审批审核额度耗尽，命令未执行）。
- sandbox / export hook 再运行：`NOT_RUN`；测试会调用系统 ACL 授权或创建/复用用户级 profile，当前没有可归属的前置快照，避免扩大未知 side effect。
- `C:/Python314` ACL 与 AppContainer profile 的归属、增量和所有者：`NOT_RUN` / 不可判定；不修改、不撤销、不删除。
- 62 个 fixture 候选清理或迁移：`NOT_RUN`；全量原位保留。
- 真实旧库迁移/回退和真实用户数据操作：`NOT_RUN`；本 Task 禁止访问。
- 本 Task 终态门禁、独立 Review、ZCode 裁决、Canonical Evidence pin：待执行，不能记录为 PASS。

## 下一步

先完成本 Task 的证据 pin 与门禁，再把上述报告和原始日志交 ZCode 独立 Review/裁决。若 ZCode 要求精确 Host 复现，待自动审批服务可运行后，仅对新的 Task 专属目录执行 `SourceSecurity.PrivateDirectory`；若审核仍不可用，保留 `NOT_RUN` 并由 ZCode 裁决是否带限制收口或申请新的 Task。没有授权进行 ACL 恢复、profile 删除、fixture 清理或产品代码修复。
