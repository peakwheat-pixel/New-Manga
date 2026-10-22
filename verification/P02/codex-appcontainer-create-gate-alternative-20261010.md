# P02 注册表准入条件替代方案草案

**状态：**`DRAFT_FOR_INDEPENDENT_REVIEW`  
**Task：**P02 静态方法研究；Owner=Codex Lead，Reviewer=`/root/orchestration_docs_review`，Integrator=Codex  
**仓库快照：**`G:/CODEX/New Manga`，`main@cddff58469b56e181019a8ddfeade80684bc7eb9`  
**固定输入：**`doc/tasks/P02.md`=`140979 bytes / CA68887C2A822377AD2A5D437AE02DCA16B20E682A7BB09FB6D72BC31B5A29DA`；提权评估 r2=`19618 bytes / BB95709DE27A5E13FE302FA3B3E68EB8B92143352B88B45C0668218138B3C736`；其 r2 Review=`6859 bytes / C45B8194D5923A7B8B315C5821A7924881EA13FC43EC6E151093E2DB8A469D21`。

## 目的与当前限制

P02 Task 已授权 Codex 确定和执行精确本机隔离范围，但也明确规定：如果不能在创建前无副作用地证明目标 private registry 缺失，就不得猜测注册表路径、调用可能创建存储的 API 或创建 profile，必须保持 `BLOCKED`。当前值为 `private_registry_absence=UNPROVABLE / BLOCKED`、profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。

因此，`CreateAppContainerProfile` 不能满足现行的创建前证明条件。本文件只提出一个**验收准入条件变更候选**，不把它描述成原 Gate 已通过，也不授权本文件所列 API 调用。P02 的提权方案评估 r2 与独立 Review 已收口，结论是管理员/ETW/驱动方案没有消除本项创建前状态阻塞；当前也没有 READY 的产品实现任务。

## 官方文档确认的语义

Microsoft 文档将 `CreateAppContainerProfile` 描述为为当前用户创建 per-user、per-app profile。其明确列出的返回语义包括：精确 `S_OK` 表示 data store 创建成功；`HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)` 表示 application data store 已存在；profile 包含文件夹和 registry storage。文档没有声明操作具有事务原子性、已存在错误分支完全无副作用、失败会自动回滚，或逐个私有 registry 子对象的先前状态可由成功返回反推。[Microsoft Learn：CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)

`GetAppContainerRegistryLocation` 可按调用者请求的访问权返回当前 profile 的 registry-storage `HKEY`，但文档没有提供它在 profile 创建前检查缺失且保证无副作用的语义。[Microsoft Learn：GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)

`DeleteAppContainerProfile` 对不存在的 profile 也返回成功；调用前应关闭 profile storage 的文件句柄；删除失败时 profile 状态不确定，文档建议再次调用。故删除成功不能证明先前不存在；其他失败分支也不能据此自动回滚或清理。[Microsoft Learn：DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)

## 提请用户裁决的替代 Gate

若用户明确接受下列风险，可将“创建前无副作用地证明全部目标 registry storage 缺失”改为“对固定当前用户和固定 moniker 单次调用，接受 API 的精确新建成功语义，并在创建后进行只读验证”。这是一项安全与验收语义变更；Codex 不得通过 Task erratum 自行视为已授权。

候选准入条件如下：

1. 唯一允许的 moniker 继续为 `NewManga-P02-LPAC-20261010-cddff584`，仅当前用户，capability 数量为零；不得猜测或遍历其他 profile、用户或 registry 路径。调用的完整用户身份、显示名/描述、空 capability 参数表示、API 版本、返回 HRESULT 比较及证据格式须在任何调用前进入独立 Review 的精确 manifest。
2. 仅调用一次 `CreateAppContainerProfile`。只接受精确 `S_OK` 作为“本轮新建”；必须保留返回的 AppContainer SID 和该调用结果。不得以 `SUCCEEDED(hr)` 代替精确判断。
3. `HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)` 时立即停止；不复用现存 profile、不删除后重建、不继续 probe。任何其他 HRESULT、缺少/无效输出 SID、调用中断或进程异常均记 `UNKNOWN / BLOCKED`；不推断 absence、不自动删除可能的部分残留，也不继续写入。
4. 只有精确 `S_OK` 后，才能按已 Review 的只读 manifest 检查返回 SID、精确 profile folder、registry-storage 句柄及相关安全描述符。registry 访问只请求 `KEY_READ`；不枚举未授权根、不创建/修改 key、不改变 ACL/label。任一项无法绑定到本轮新建对象或检查结果不符即停止并保留证据。
5. 只有满足现有独立隔离方案的其余 Gate 后，才可继续现有 preflight。profile 清理仍严格限于同一用户、同一 moniker，且仅当本轮精确 `S_OK` 已记录；先关闭该 profile 的文件句柄。失败仅可依文档对同一 moniker 重试并标记 `CLEANUP_BLOCKED`，禁止递归删除或清理任何未知失败产生的残留。
6. `CreateAppContainerProfile` 未文档化的部分失败/子对象状态仍为已知风险。用户接受该风险，不代表将 `UNKNOWN` 标记为 PASS；所有无法绑定、验证或安全清理的分支继续阻塞。Build Gate、Hard Build Barrier、build 与 AC1–AC7 状态均不因此自动变化。

此方案并不证明调用前每个 private-registry 子对象不存在。其潜在依据仅是 API 对精确 `S_OK` 与“data store created successfully”的文档语义，加上创建后的只读验证。若用户不接受这种替换，保留原标准并继续 `private_registry_absence=UNPROVABLE / BLOCKED`。

## 精确决策

请用户选择：

- **接受替代准入条件：**允许后续 Codex 将 P02 的创建前缺失证明改为上列“固定 moniker 单次精确 `S_OK` + 创建后只读验证”标准，并把部分失败状态未知作为明确残余风险；此回复不单独构成对未 Review manifest 的执行许可，后续必须先冻结完整参数和路径并经独立 Review。
- **维持原标准：**禁止创建前无法证明的 profile/storage 创建；P02 保持 `HUMAN_REQUIRED / BLOCKED`，Codex 继续寻找满足原标准的方法。

在用户裁决及后续 manifest Review 之前，profile 仍为 `NOT_CREATED`；ACL/registry 仍为 `NOT_MODIFIED`；不调用任何 profile/registry API，不进行 OS preflight、build、Cargo、AC1–AC7 或 Windows Sandbox 操作。

## 独立 Review 验收范围

Reviewer 仅评审本固定文档及上述 P02 Task 快照：检查 Microsoft API 语义、精确 `S_OK` 与碰撞分支、失败残留/清理边界、是否确实把语义变更留给用户，以及是否错误暗示 Gate/系统/产品验证通过。Reviewer 唯一写入路径为 `verification/P02/codex-appcontainer-create-gate-alternative-review-20261010.md`。Review 不是用户裁决、执行授权或 Gate 证据。

未检查：未读取或探测本机 profile、registry、ACL、用户令牌或 OS 状态；未运行 API、probe、build、Cargo、AC1–AC7 或 Sandbox。剩余风险：创建 API 的部分失败状态及私有 registry 子对象语义未被 Microsoft 文档承诺；未经用户接受及精确 manifest 独立 Review，不得尝试创建。
