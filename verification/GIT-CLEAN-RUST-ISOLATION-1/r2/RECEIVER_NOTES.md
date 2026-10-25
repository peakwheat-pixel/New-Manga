# Codex 接收观察（尚在编辑，非独立Review）

待Owner稳定交付后核对：
1. ChildIdentity.spawned_at_utc_ms 是测试墙钟而非OS创建时间；tag未查询核验。须保留自有process HANDLE并用WaitForSingleObject/GetProcessTimes，或实际查询OS创建时间/命令；不能据此宣称R003已闭环。
2. PID_LEDGER thread_local：取消worker线程push的identity不会进入主线程take_ledger，最终PID断言可能零次执行。应返回identity给join调用者/父Vec，并断言核验数=count。
3. scoped sampler的move closure若直接捕获AtomicBool/AtomicUsize，会使外层再次使用值编译失败；应先借引用或把started置闭包内、避免move。
4. tasklist probe须检查exit status，失败/不可用不能被字符串空判为进程消失；非Windows分支不应直接返回false制造PASS。
5. 资源账本不能仅打印预计线程数；需保存真实writer/reader完成或join标志的Arc，Drop/reaper后断言；处理完或明确PARTIAL，不得声称所有句柄已归零。
6. current_thread_override_registry本身也需fail-closed（owner标志存在但槽读取失败时不得把holder静默送global）。
