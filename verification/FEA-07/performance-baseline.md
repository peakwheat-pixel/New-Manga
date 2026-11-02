# FEA-07 切片 5：热切换性能 baseline（AC6 / H3 / W-5）

- 时间：2026-11-02 16:11:43 +08:00
- code head：7ca2e367b09c41fe0253a68d77bbbfde99e8c772
- 机器：HOME-MY；OS：Microsoft Windows NT 10.0.26300.0；.NET：9.0.11
- 口径：headless Avalonia UI 线程；真实 AppShellV2 / FluentShellSurface content factory（内容树缓存复用）；固定合成夹具
- 预热：2 次；测量：12 次往返
- **冷启动首次切换**：475.62 ms（单独记录，不计入热 p95）
- **p50**：99.91 ms；**p95**：344.93 ms；**max / UI freeze 上限**：344.93 ms
- 托管内存增量：208 bytes；句柄增量：0（Release）
- **W-5 门槛**：热切换 p95 ≤ 1000 ms → **通过（True）**
- 样本（ms）：230.43, 92.72, 246.92, 98.58, 259.23, 99.91, 344.93, 114.16, 270.1, 56.32, 88.95, 54.38

原始 JSON：`performance-baseline-release.json`（Release，正式）；`performance-baseline-debug.json`（Debug 对照：p50 169.02 / p95 516.05 / 内存 +1,384,880 bytes / 句柄 +3）。

> R-009 说明：UI freeze 目前为「切换事务总时长」上限估计，真实渲染冻结采样与真实规模合成负载仍待补；AC6 因此保持 PARTIAL。