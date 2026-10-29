# V11R-B-2 未接入能力清单（诚实降级）

原则：未接 API 的区块**不伪造数据、不显示假开关**；危险动作即使不可执行也必须给出影响面并可取消。

| # | 能力 | 现状 | UI 呈现 | 依赖 |
|---|---|---|---|---|
| 1 | 任务与队列 **Run 列表** | 冻结契约无「List Run」命令；`IRunController` 只有按 run_id 的快照/投影/控制 | 分区要求显式输入 run_id 后读取；无 run_id 时不发任何 Host 调用、不显示伪造行 | Core 契约扩展（list runs）或 B-4 共享 Run 视图 |
| 2 | 任务与队列 **订阅式更新** | 当前 Console 内独立 1s 轮询（`DispatcherTimer`）；数据源与 B-4 相同（`GetRunSnapshot`/`GetTaskProjection`） | banner 明示「数据同源；B-4 共享 Run 视图合入后改为订阅」；离开分区/离开控制台立即停轮询 | V11R-B-4 |
| 3 | 模型与设备（④） | Host 未暴露设备/模型查询命令；打包 `VERSION.json` 由 Host/打包层拥有，按 AD-002 UI 不直读文件 | banner「能力待接入」+ 前置条件；不显示 GPU/CPU 假状态 | Host 设备状态命令（契约扩展） |
| 4 | 缓存与版本清理（⑤） | `cleanup_preview`/`cleanup_run` 已在命令注册表，但 `IHostController` 无方法 | banner + 前置条件 + 「清理缓存与过期版本（能力待接入）」按钮 → 危险确认（确认禁用、原因可见、可取消） | core-bridge 追加 IHostController 方法（先预览影响面） |
| 5 | 备份与恢复（⑥） | `backup_list`/`backup_create` 已在注册表，`IHostController` 无方法；`.nmbak` 恢复策略未接入 | banner + 「创建备份/删除备份（能力待接入）」→ 危险确认（可取消、确认禁用、写明永久移除/覆盖范围） | core-bridge 追加方法 + 恢复策略 |
| 6 | 插件与 Hooks（⑦） | `plugins_list`/`plugins_set_enabled` 已在注册表，`IHostController` 无方法 | banner + 前置条件；无开关 | core-bridge 追加方法 + 插件审计 |
| 7 | 诊断包导出 / 日志查看（⑧） | 无 Host 诊断命令 | Host 状态与导出历史真实显示；日志/诊断包区域 banner「能力待接入」，不展示伪造日志 | Host 诊断命令 |
| 8 | 外观 → 主题工作室 7 分区（⑨） | 内容属 V11R-C-2 | 深浅外观真实切换；入口按钮「打开主题工作室（7 分区即将可用）」打开真实表面栈占位 | V11R-C-2 |
| 9 | 网络真实外网探针 | `TestNetworkProfileAsync` 真实调用 Core；本机无 sidecar 时无结果 | 无结果时显示「测试不可用：Host 未就绪或未返回真实结果（未伪造）」 | 运行时 sidecar |
| 10 | 凭据 OS vault 真实读写 | 真实命令存在，需 Core/vault | 状态来自 Core；失败只显示 typed code；无侧车时保存失败如实显示 | 运行时环境 |
