# V11R-INT-2 偏差记录

| ID | 规格/契约 | 实际实现 | 理由 | 影响 |
|---|---|---|---|---|
| D-INT2-1 | B-1 屏幕规格：StatusBand 只在有 Run/活动时出现 | 改为**始终可见**的 Host 就绪通道：Run > 导入 > Host 状态（就绪/失败/只读） | Lead P0：默认安装必须能看见 Host 是否就绪；否则“永远 Host 未就绪”无提示 | B-1 的“仅活动”行为被取代；状态栏无 Run 时显示 Host 状态，不再隐藏 |
| D-INT2-2 | v2/legacy 各自启动 Host | v2 在 `AppShellViewModel.InitializeCoreAsync` 显式启动；`HostController.StartAsync` 幂等（`StartRequests` + 单任务），legacy 调用点不变 | 唯一启动点、避免重复 sidecar；INT-1 后续可改为 App 启动链路 | legacy 行为不变，只多一个幂等保护 |
| D-INT2-3 | 启动失败必须可见 | `HostController` 把 typed 失败写入 `HostViewSnapshot` 而非抛出；v2 VM 同时捕获任何 typed 启动异常并生成“Host 启动失败（code/类型）：消息” | “失败不得吞”：既不崩溃，也不静默 | 状态栏/日志可见；不伪造 ready |
| D-INT2-4 | `--variant` 启动外观 | 壳构造采用 DS manager 已应用外观，不再用 VM 默认覆盖；Theme Studio 服务异步 persisted 设置后重新应用显式 `--variant` | 真实窗口发现 dark/light 截图相同；theme service 异步覆盖 startup | 显式参数优先；无参数时仍尊重 persisted 默认 |
| D-INT2-5 | Host 事件线程 | `HostController.Changed` 始终 marshal 到 UI 线程（`Dispatcher.UIThread.Post`）；壳订阅再做一次 CheckAccess 保护 | 真实窗口曾因 Changed 从线程池触发 `Call from invalid thread`，导致 Host 实际 ready 但界面显示失败 | 所有 Changed 消费者（壳/Studio/legacy）安全 |
| D-INT2-6 | 空态布局 | 4 个兄弟 Grid 改为单一状态容器 + 互斥选择器；加载骨架独立 `ShowLoadingState` | 修复 HostNotReady+空库同时可见的叠印（L4 发布级 P1） | 任意组合恰有一个块；文案/动作不变 |
| D-INT2-7 | 真实窗口截图尺寸 1600×1000 | 实际 PNG 1567×1009：请求 1600 宽但本机桌面可用宽度 1567，Windows 钳制窗口 | 环境限制；headless 证据仍 1600×1000 | 记录在 README；不改变 UI 响应式断言 |
| D-INT2-8 | CLI `--key value` | 本任务证据只能使用 `--key=value`；空格形式被解析成 `"true"`（core-bridge 修复中） | Lead 已说明 core-bridge 正在修 | 本任务不扩大范围；复现命令使用 `=` 形式 |
| D-INT2-9 | 证据 | R-19：headless 截图由 `curate.ps1` 生成；真实窗口图与 L4 修复前参考图手工保留（脚本显式排除） | 真实窗口证据无法 headless 生成 | 证据可复核，脚本可重复 |
