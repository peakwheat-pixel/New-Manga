# FEA-04 Host 生命周期断言

新增用例：Rebuilt_shell_content_uses_the_same_host_and_session_without_starting_it，位于 apps/desktop-avalonia/tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs。

用例构造第一个 AppShellViewModel，修改 ShellState 的书籍选择、空间与 StudioMode，释放其 RunStatusMonitor 订阅后重建第二个 AppShellViewModel。两者通过 CurrentFrontend.For(host) 复用同一个 Host keyed façade 和 Session memento。断言包括：

- Assert.Same(hostBefore, second.Current.HostController)，并再次确认第一壳仍映射到同一 Host。
- 重建后的 Selection.BookId、CurrentSpace、StudioMode 与原会话相同。
- host.StartCalls、host.StartRequests 与 LifecycleLog 均等于重建前值。
- RunStatusMonitor.Dispose 只释放 Current RunMonitor 的订阅；没有调用 Host.DisposeAsync 或 StartAsync。

按 Task 指定的解决方案测试命令在 restore 失败后运行 no-build。六个测试工程 DLL 均不存在，因此该用例当前为 NOT_RUN，未获得执行断言。原始命令和输出见 [implementation-build-final.log](implementation-build-final.log)、[implementation-test-no-build-final.log](implementation-test-no-build-final.log)。
