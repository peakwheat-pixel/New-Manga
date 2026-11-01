# ApplicationCore

FEA-02-CORE 的纯 .NET 内存状态层。没有 Avalonia、Host、IPC、CoreClient 或数据库依赖，也没有应用入口与 DI 注册；本 Task 不接入 Current。

- `RunMonitor<T>`：由应用持有一个实例。为每个有订阅的 Run 建立一个查询循环；同一 Run 的订阅和并发 `RefreshAsync` 共享正在进行的查询。`T` 由后续适配层提供，须是不可变的既有领域快照。这里不定义第二套 Run DTO、完成状态或进度算法。
- `RunStateStore<T>`：保存最后一次成功的权威快照。查询失败作为该次 `RunObservation.Request.Error` 通知，不覆盖缓存；`Version` 只是本地快照发布序号，不是 Core revision。`GetSnapshots` 返回独立只读字典；无订阅后可用 `ForgetRun` 释放缓存。
- `IntentCoordinator<T>`：同一键的进行中操作共享一次调用、同一结果；单个调用方取消只停止自己的等待。完成、失败或超时后释放本地记录。它不是持久幂等存储，适配层必须把收到的原始意图键继续传给 Core；有不确定结果的重试沿用该键，新用户意图使用新键。
- `RequestExecutor`：每次请求独立持有 `RequestId`、结果与失败。`RequestFailureKind` 是本地请求生命周期分类，不是 Run 状态或 wire/category 码表。适配层可抛出 `RequestRejectedException` 携带原始 `SourceCode`；此层不解释或改写该码，也不得通过读取全局 `LastError` 构造请求错误。

## 生命周期与接线边界

构造 monitor 不启动查询；首个订阅启动查询，最后一个退订取消该 Run 查询和循环。应用关闭时 await `DisposeAsync`。`RefreshAsync` 要求活动订阅。查询结果在工作线程通知，缓存重放可能在 `Subscribe` 内同步通知；UI 适配层负责 dispatcher 切换，并检查自身生命周期。回调异常不会中断其他订阅；退订丢弃排队通知，但已经执行的回调可能完成。回调应快速返回，不应同步阻塞等待 monitor 关闭。

查询委托须异步返回并响应取消。超时或关闭会请求取消；即使外部操作忽略取消，本层也会结束等待并丢弃迟到结果，但不能保证外部副作用已经停止。后续接线必须保留 Core 的幂等保障与请求级错误返回，且只能使用一条启动/轮询路径；不能同时保留旧路径的调度与本层调度。Host lifetime、wire 错误投影、恢复锁、DDL 和 UI 组合根均不属于本层。

测试项目使用注入的 `TimeProvider`、闸门与调用计数验证并发及超时；不需要运行 Core、GUI 或访问用户数据。
