# FEA-07-AC5-NATIVE-1 / DEFECTS

## D-AC5-1（P3，既有行为/产品缺口）：物理拔屏后主窗被最小化而非自动迁移

- 现象：应用主窗置于 4K（(3616,200) 2592×1458@150%）→ **物理拔掉 4K** → 窗口变为**最小化**（`iconic=True`，rect `(-32000,-32000)`），进程存活；未自动迁移到剩余屏幕。
- 恢复：`ShowWindow(SW_RESTORE)`（等价任务栏点击）后窗口落在主屏 `(703,134) 1728×972@100%`、完全在主屏内、可正常使用。
- 重插：4K 插回后窗口**自动回到 4K 原几何** `(3616,200) 2592×1458@150%`。
- 证据：`evidence/physical-state-after-physical-unplug-*.json`、`physical-state-after-unplug-restored-window-*.json`、`physical-state-after-replug-*.json`、`physical-unplug-before.log`。
- 判定：**不是崩溃/丢数据**；「不丢屏外」在最小化语义下成立（任务栏可恢复），但「自动回到主窗对应页面」未自动发生 → 登记为产品缺口/limitation，建议 re-home 到窗口管理卡（OS 显示移除事件下主动迁移）。
- 另：OS 级 `/internal` 拔屏路径（`DisplaySwitch`）**会自动迁移**窗口（1728×972@100%）——说明差异来自物理移除事件与显示变更通知路径。

## 过程缺陷（非产品）

- `physical-unplug-probe.ps1` 首次等待窗口 240s 超时（用户拔线晚于脚本窗口），未产出 JSON；失败日志已保留为 `evidence/physical-unplug-before.log`，随后用 `capture-physical-state.ps1` 直接抓状态完成取证。
