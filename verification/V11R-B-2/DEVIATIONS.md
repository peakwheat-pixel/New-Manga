# V11R-B-2 偏差记录（DEVIATIONS）

| ID | 规格/契约 | 实际实现 | 理由 | 影响 |
|---|---|---|---|---|
| D-1 | 任务允许路径只列 `Views/V2/Console`、`ViewModels/V2/Console`、`verification/V11R-B-2` | Console 需要壳接线（同 Owner 的 B-1 写域）：`ViewModels/V2/Shell/AppShellViewModel.cs`、`Views/V2/Shell/V2WorkspaceHost.axaml`；并按 Lead 裁决改 `Shell/V2/Statuses.cs` 的 queued 符号；测试目录按 Lead 追认只新增 `V2ConsoleUiTests.cs` 并在 `V2ShellUiTests.cs` 增加 fixture 方法 | 不接线无法在真实外壳内验证 9 分区；均为最小必要改动，无既有语义变更 | 请在 Review 中追认（非阻塞） |
| D-2 | SCREEN_SPECS §5 未规定 Run 列表来源 | 因冻结契约无 List Run，分区要求显式 `run_id`，快照/投影经壳共享 `RunStatusMonitor`（R-24，单一 poller）；进入/离开 Console 恢复/暂停订阅 | 不伪造任务列表；与 StatusBand 同源，不重复轮询 | 用户需从工位/记录获得 run id；已在 banner 说明 |
| D-3 | R-08 幂等键由调用方提供 | Restart / 重试失败目标要求操作方在「幂等键」框填写；缺失时本地拒绝，UI 不静默生成 | 遵守 R-08 | 操作多一步输入，但避免伪幂等 |
| D-4 | 危险动作清单（清缓存/删备份/永久删除） | 额外把「停止 Run」「删除 Provider/网络配置」「清除密钥」纳入确认 Modal（默认取消、写明影响面） | 这些动作同样破坏性/不可撤销，按同一安全纪律处理 | 更保守；无功能损失 |
| D-5 | 外观分区可放更多设置 | 只保留真实深浅切换 + Theme Studio 入口（C-2 内容不预先造假） | Lead 明确：⑨ 先留入口 + 「即将可用」 | C-2 交付后扩展 |
| D-6 | DS 自定义控件尚未交付 | 继续使用 B-1 的本地 `StatusBadge/AlertBanner/Kbd`（DS M0 未含这些控件） | 依赖未合入的既定降级；DS 交付后统一替换 | 视觉一致性等 DS 控件上收后复核 |
| D-7 | 凭据输入框掩码字符 | 使用 `PasswordChar="*"`（DS TextBox 标准样式） | Avalonia 标准能力；不需要本地控件 | 无 |
| D-8 | `queued` 状态符号 | 已按 Lead 裁决改为 `·`（DESIGN_SYSTEM §2.2 权威）；DS `StatusGlyph` 合入后切换为唯一源 | 契约 §2.3 笔误已由 Lead 更正 | 消除符号歧义 |
| D-9 | Console 左索引的摘要截断 | 摘要单行 `CharacterEllipsis`，完整文案通过 `ToolTip` 提供 | 9 分区 + 1600/1280 宽度下的可读性取舍 | 悬停可见完整说明 |
| D-10 | 诊断区不渲染 Host 原始 `ErrorMessage` | 只渲染 `Snapshot.ErrorCode`/`LastError`（typed）与状态行；banner 说明原因 | 安全：原始错误可能含本地路径 | 排障需日志（当前未接入） |
