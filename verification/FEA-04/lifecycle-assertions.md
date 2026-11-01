# FEA-04 AC6 生命周期断言（DSH 复跑，2026-11-02）

- 关闭/重建内容不 Dispose Host：FEA04CurrentAdapterTests 中 lifecycle 用例断言 `ReferenceEquals(hostBefore, hostAfter)` 且 FakeHostController.LifecycleLog 无 Dispose 记录。
- 不隐式 Start：FakeHostController.StartCalls 与 HostController.StartRequests 在 preflight/切换准备前后计数不增。
- RunStatusMonitor（head 实现）：**保持既有 Host 轮询**（DispatcherTimer 1s，读 IRunController.GetRunSnapshotAsync/GetTaskProjectionAsync）；Current 属性仅为共享门面引用，**不接管 Host 生命周期、不 Dispose Host**。Dispose() 释放定时器与本类型资源，不触 Host。
- CurrentFrontend 不创建/销毁 Host：For(controller) 仅缓存门面；Preflight 纯读 memento，零 Host 调用。
