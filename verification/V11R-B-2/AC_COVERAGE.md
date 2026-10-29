# V11R-B-2 验收标准覆盖（AC → 证据）

| AC | 要求 | 实现 | 证据 |
|---|---|---|---|
| AC1 | SCREEN_SPECS §5 的 9 分区、布局、组件、状态、数据源；**无 Mock 冒充真实**（未接能力显示「待接入」） | 左侧 9 分区索引 + 右侧分区内容；②③⑧⑨ 走真实 Host/IPC；① 走真实 `IRunController`（显式 run_id）；④⑤⑥⑦ 全部 `AlertBanner`「能力待接入」+ 前置条件 + 阻断态危险确认；无任何假开关/伪造数据 | `01`–`08` 截图；`V2ConsoleUiTests` 13 条；`NOT_WIRED.md` 10 条 |
| AC2 | 空间/模式切换不重建 VM、不丢 selection/滚动/筛选 | Console VM 在 `AppShellViewModel` 构造时创建一次；B-1 的 `Assert.Same` 回归仍通过；R-24：进入 Console 且有已加载 Run → 恢复共享 `RunStatusMonitor` 并立即刷新一次；离开 Console → 暂停共享 poller（StatusBand 保留最后快照） | `V2ShellUiTests.SpaceAndModeSwitch_KeepsSelectionFiltersAndTheSameViewModels`（回归）；`ConsoleViewModel` 构造与 `SpaceChanged` 处理 |
| AC3 | 状态完备：idle/loading/ready/empty/error/partial 就地呈现 | idle：无 run_id/无导出记录提示；loading：`IsLoading` 行；ready：真实行；empty：`导出历史为空`/`尚未加载 Run`；error：`HasError` banner + 重试；partial：逐条状态（已保存/未保存、Run 行状态、网络测试明细） | `02`、`03`、`06`、`07` 截图；测试断言 |
| AC4 | 无裸色值/裸字号/裸间距/阴影/渐变/模糊；`{DynamicResource Nm.*}`；`-warnaserror` 0 warning | 新增 `Views/V2/Console/ConsoleView.axaml` 全部令牌；conformance 静态扫描（含 Console 文件）通过；令牌全部存在于 DS | `V2ConformanceTests`（4 条通过）；`conformance/v2-tokens-and-classes.json`；`BUILD_TEST.md` 0 warning |
| AC5 | 键盘可达 + 焦点可见 + Esc 逐级退出 + IME 安全 | 控制台继承 B-1 外壳键盘（Esc 逐级：确认→面板→…；输入框聚焦字母快捷键让位）；所有按钮/输入框均有焦点环（DS 样式） | B-1 `V2KeyMapTests`/`V2ShellUiTests` 回归；本任务确认/Esc 路径测试 |
| AC6 | 单测覆盖 ViewModel/状态机/交互规则；`dotnet test` 绿；关键屏截图 | 13 条 Console 测试；V2 145 条全绿；8 张真渲染截图 | `BUILD_TEST.md`、`test.log`、`screens/` |
| AC7 | 证据：构建/测试日志、截图、偏差与未接入清单 | 本目录全部文件 | `README.md`、`BUILD_TEST.md`、`build.log`、`test.log`、`screens/`、`DEVIATIONS.md`、`NOT_WIRED.md`、`conformance/` |

## Lead 追加要求 → 证据

| 要求 | 证据 |
|---|---|
| ② Provider 与凭据：**凭据永不回显 secret（有测试）** | `Credentials_DisplayStateOnly_AndTheSecretIsClearedAndNeverExposed`：保存成功后 `SecretInput` 清空 + 反射遍历 public string 属性断言无 secret；`01`/`02` 截图为掩码输入与状态标签 |
| ⑥ 备份与恢复：危险动作有影响面文案且可取消 | `NotWiredSections_...`：删除备份确认文案含「永久移除…无法恢复」、默认取消、确认禁用、原因可见、可取消；`04`/`08` 截图 |
| ⑨ 外观：只作为 Theme Studio 入口 + 「即将可用」，不假开关 | 外观分区只有真实深浅切换 + 「打开主题工作室（7 分区即将可用）」入口（打开真实表面栈），无其它开关；`05` 截图 |
| 合入 A-2 后 ① 用真实 `IRunController` 快照/投影；轮询与 StatusBand 同源（R-24） | `Tasks_LoadsRealRunSnapshotAndProjection_...` 断言 `GetRunSnapshotAsync`/`GetTaskProjectionAsync` 记录与真实字段；`RunSourceNote` 明示经壳共享 `RunStatusMonitor`（R-24）；`R24_ConsoleRunPolling_...` 断言离开暂停/切回恢复；`07` 截图 |
