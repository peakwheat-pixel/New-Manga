# FEA-07 r3 返修 part2：热切换性能 baseline（AC6 / H3 / W-5，含真实 staging 门禁）

- 时间：2026-11-02 17:52:00 +08:00
- code head：100d487ffb55518e98be5219d750ab85c8a71d2b
- 机器：HOME-MY；OS：Microsoft Windows NT 10.0.26300.0；.NET：9.0.11
- 口径：headless Avalonia UI 线程；真实 AppShellV2 / FluentShellSurface content factory（内容树缓存复用）；**R-001 后每个切换都经过真实 staging 布局 / `Loaded` 事件 / `RequestAnimationFrame` 帧渲染门禁**；固定合成夹具
- 预热：2 次；测量：12 次往返
- **冷启动首次切换**：593.99 ms（单独记录，不计入热 p95）
- **p50**：102.29 ms；**p95**：496.30 ms；**max / UI freeze 上限**：496.30 ms
- 托管内存增量：7,088 bytes；句柄增量：0（Release）
- **W-5 门槛**：热切换 p95 ≤ 1000 ms → **通过（True）**
- 样本（ms）：496.3, 74.92, 222.23, 102.29, 214.88, 58.61, 214.11, 55.62, 201.86, 80.43, 209.11, 51.49
- **三次 Release 复测**（同一 head，均 PASS）：p95 496.30 / 575.64 / 712.28 ms（p95 == max，因 n=12 时 ceil(0.95*12)-1 = 11 取到最大值）

原始 JSON：`performance-baseline-release.json`（Release，正式，记录第 3 次运行）；`performance-baseline-debug.json` 为 r2 时期 Debug 对照样本。

> R-009 说明：UI freeze 仍为「切换事务总时长」上限估计，真实渲染冻结采样与真实规模合成负载仍待补；AC6 因此保持 PARTIAL。本 baseline 与 r2 的 344.93 ms 不可直接比较：R-001 把提交门禁从 Dispatcher 优先级空回调替换为真实 staging 挂树 + Loaded 事件 + 帧渲染等待，事务因此包含渲染门禁成本。
