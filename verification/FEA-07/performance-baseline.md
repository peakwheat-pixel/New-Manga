# FEA-07 切片 5：热切换性能 baseline（AC6 / H3 / W-5）

- 时间：2026-11-02 15:40:10 +08:00
- head：318fd34f2d73aa582802cfa3c2f289286ed97cbb
- 机器：HOME-MY；OS：Microsoft Windows NT 10.0.26300.0；.NET：9.0.11
- 口径：headless Avalonia UI 线程；真实 AppShellV2 / FluentShellSurface content factory；固定合成夹具
- 预热：2 次；测量：12 次往返
- **冷启动首次切换**：648.42 ms（单独记录，不计入热 p95）
- **p50**：118.51 ms；**p95**：429.47 ms；**max**：429.47 ms
- 托管内存增量：1363264 bytes；句柄增量：0
- **W-5 门槛**：热切换 p95 ≤ 1000 ms → **通过（True）**
- 样本（ms）：369.32, 116.72, 380.79, 118.51, 429.47, 136.4, 427.78, 68.73, 132.36, 72.26, 112.05, 84.04

原始 JSON：performance-baseline-release.json（Debug 配置对照：performance-baseline-debug.json）。