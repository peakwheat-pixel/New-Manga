# FEA-07 r7 返修：热切换性能 baseline（AC6 / H3 / W-5，真实 staging 门禁 + 真实 p95 口径）

- 时间：2026-11-02 20:14:00 +08:00
- code head：462141f57f7b00b34577dbf04d8415be7ab5fe95
- 机器：HOME-MY；OS：Microsoft Windows NT 10.0.26300.0；.NET：9.0.11
- 口径：headless Avalonia UI 线程；真实 AppShellV2 / FluentShellSurface content factory（内容树缓存复用）；**R-001 真实 staging 布局 / `Loaded` 事件 / `RequestAnimationFrame` 帧渲染门禁**；固定合成夹具
- 预热：**4 次单向切换**；测量：**20 次单向切换（10 次往返，交替目标）**
  - 口径说明（R-009 收尾）：原 12 样本时 `ceil(0.95×12)-1 = 11` 使 p95 恒等于 max；改为 20 样本后 p95 取第 19 个（排除单个最差离群），才是真正的 p95。W-5 门槛数值不变（p95 ≤ 1000 ms）。
- 记录 run（Release，第 2 次复测）：
  - **冷启动首次切换**：675.10 ms（单独记录，不计入热 p95）
  - **p50**：99.28 ms；**p95**：374.09 ms；**max / UI freeze 上限**：389.99 ms
  - 托管内存增量：-1,616 bytes；句柄增量：0
  - **W-5 门槛**：p95 = 374.09 ms ≤ 1000 ms → **PASS**
- 同一 head 2 次 Release 复测（20 样本制，均 PASS）：p95 **299.40 / 374.09 ms**（max 301.10 / 389.99 ms）
- 历史数值（r4 head：p95 313.95 ms；r5 head：248.42 ms；r6 head：261.38 ms）保留在历史证据与 Task 记录中，不与本 run 混算。

原始 JSON：`performance-baseline-release.json`（Release，正式，记录第 2 次运行）；`performance-baseline-debug.json` 为 r2 时期 Debug 对照样本。

> R-009 说明：UI freeze 仍为「切换事务总时长」上限估计，真实渲染冻结采样与真实规模合成负载仍待补；AC6 保持 PARTIAL。R-001 后事务包含 staging 挂树 + Loaded 事件 + 帧渲染门禁，数值不可与 r2 的 344.93 ms 直接比较；20 样本口径的 p95 不可与 12 样本的 max 口径直接比较。
