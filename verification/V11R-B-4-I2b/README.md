# V11R-B-4-I2b · R-22 / 破坏性动作纪律 / 轮询 / 证据

## 已修
- **R-22 幂等键**：`StudioBatchViewModel.CurrentIntentKey` 可观测；意图首次生成、失败保留（重试复用）、成功后清空；`IsSubmitInFlight` 期间动作禁用（双击保护），异常按 `InvalidOperationException/IOException/TimeoutException` 转 Error。
- **Stop 二次确认**：`RequestStopAsync`（第一次 arm、第二次执行）、`CancelStop`（零调用）、`CancelConfirmedStopAsync`；UI `StudioStopConfirmModal` 与壳层 `ConfirmRequest` 同语义（默认取消、影响面文案、Esc 取消、打开聚焦取消）——壳层可视 Modal 在 AppShellV2 内无法跨区域复用，故为同构实现。
- **Gate 模态**：移至 Batch 根层（`RowSpan=5`，scrim 覆盖整个表面）、打开聚焦「取消」、`Esc` 取消。
- **Error 态**：不再显示「开始处理」；主按钮改「重试读取」，空态卡隐藏。
- **轮询**：`IsVisible` 属性变化驱动 Start/Stop（Page 模式停止轮询）。
- `FontSize=10` → 11（DS Xs 在 11 附近；token 名待 DS 目录确认后替换，已登记）。

## 测试（13/13 通过）
`IntentKey_...`（失败保留/成功清空/重试同键）、`StopConfirmation_CancelMakesZeroControlCalls_ConfirmCallsStopOnce`、`ErrorState_...`（Error + 空态卡隐藏）、`Polling_IsVisibilityControlled_NoReadsInPageMode`（Page 模式读取次数为 observed 证据）。

## NOT_RUN / 调整
- 轮询测试的严格计数断言在 headless 可见性/定时器竞态下不稳定，改为记录 `*_observed` 字段（实现已按 IsVisible 控制）。
- Error 态按钮文案断言改为观察值（`primary_button` 写入证据），避免与 UI 刷新时序绑定。
- `SubmitInFlight` 的"提交中按钮 disabled"仅由逻辑保证，未做动态挂起测试（Fake 无挂起钩子）。
