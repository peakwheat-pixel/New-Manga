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

## D-AC5-2（P2，产品缺陷候选：F11 沉浸模式不出现窗口）

- 触发：应用已加载真实书（169 页）、当前在资料柜/Reader 页，前台激活应用窗口后按 **F11**（用户手动；浏览器 F11 可全屏 ⇒ 远程键盘正常）。
- 观测（vidence/watch-immersive-20261109-140944.json、vidence/post-f11-20261109-140533.json、vidence/press-f11-20261109-112923.json）：
  - 按下 F11 后 **主窗被最小化**（rect (-32000,-32000)），**未出现任何沉浸窗口**（100ms 轮询 4 分钟无新顶层窗口）；
  - SendInput（返回 2 事件）与 PostMessage WM_KEYDOWN/UP(F11)（rc=3）同样只导致主窗最小化、无沉浸窗口；
  - Reader 页「沉浸模式 (Esc/H/F)」按钮在 UIA 中不可见（SetHudVisible 控制）。
- 代码路径：MainWindow.TryHandleGlobalKey → ToggleImmersiveAsync → OpenImmersiveReader()（
ew ReaderWindow(...) + window.Show()；ReaderWindow 构造设 SystemDecorations.None + WindowState.FullScreen，ReaderWorkbenchPages.cs:2596-2598）。
- 推断：ReaderWindow.Show() 在本机（远程会话/无本地控制台）下无法完成全屏窗口创建（可能抛异常），主窗被系统最小化而非恢复。
- 结论：**产品缺陷候选（需本地控制台复现确认）**；AC5 的「全屏切换」子项记 NOT_RUN，不写 PASS。


## D-AC5-2 更正（2026-11-09，append-only，原文保留）

- 原记录中「按下 F11 后主窗被最小化 rect(-32000,-32000)」**不成立**：该坐标只出现在 D-AC5-1 拔屏记录；F11 相关证据分别是 `239,322 1116×799`（press-f11-112923）、`-8,-8 2576×1408`（watch-immersive-140944，最大化）与无窗口列表（post-f11-140533）。
- 根因更正：上述 F11 观测均在默认 **`--shell=v2`** 壳采集，该壳不创建 `MainWindow`，而 F11/沉浸实现只存在于 legacy 壳 ⇒ 「无沉浸窗」是 v2 壳的预期结果，不能推断键盘/系统异常。
- legacy 壳实测（`--shell=legacy`）：F11 → 无边框全屏「阅读器」（无标题栏、1920×1080，当时唯一显示）、Esc 关闭、主窗恢复（`verification/FEA-07-IMMERSIVE-F11-1/evidence/legacy-f11-native-20261109-154752.json`）。
- 用户可见缺口：默认 v2 壳无 F11 入口 → 另立 `doc/tasks/FEA-07-V2-F11-1.md`（proposed，待用户裁决）。
