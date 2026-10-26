---
task_id: HOST-TILE-CHANNEL-1
author: avalonis-spike
recipient: DeepSeek Harness
base_commit: 2885861fa
delivery_head: c8ab135d10f0232d6717ff4471f7e568f099f613
status: draft
---

# Handoff：HOST-TILE-CHANNEL-1（S5-A）

## 结果（AC1–AC6 全 MET）
- tile 通道：`TileChannel` 新 C# Host 实现——issue（不透明 32-hex 句柄 + size + volume/file identity + per-tile SHA-256 清单）→ read（从 OS 句柄重导最终路径、允许根校验、identity/size/tile 摘要校验）→ revoke；UI 只拿到 `TileGrantView`/`TileReadResult`（无路径/摘要）。
- 缓存：授权查询 ≤1s TTL（实测命中率 0.667）；**revoke 事件立即打断缓存**，实测生效 **0.071ms**；expiry 到期拒绝（80ms TTL 负例）。
- containment：越界路径拒绝 `TilePathOutsideRoot`；`mklink /J` junction 拒绝 `TilePathReparse`（负例证据）。
- 完整性：per-tile SHA-256；**等长原地重写** 与 **保尺寸篡改 tile** 均 `TileDigestMismatch`（文件长度不变）；替换文件 `TileIdentityMismatch`。
- UI 接线：阅读器/工作台 `BindTileSource(ITileSource)`，`TileChannelSource` 走校验通道、失败返回 null（typed error 不外泄）；`FixtureTileSource` 保留旧 fixture 兜底。
- 性能：4MiB tile 冷读+摘要 **2.523ms**（≤60ms）；raw 读 vs 摘要开销比 5.39×（本机缓存口径，G5 ≤10% 目标交 S5-B 正式 run 统计，未放宽校验）。
- 门禁：`scripts/test.ps1 -CanonicalEvidence` **95/95 通过**；vitest 60/567；pytest 3F/2687P/9S = 基线；未改旧壳/Core，未 push。

## 证据 / 复跑
`verification/HOST-TILE-CHANNEL-1/**`（E1–E11，64-hex pin @c8ab135d1，MANIFEST `d8f5cd00…`）。复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`（rerun 写 workspace 不覆盖 pin）。

## Record Decision
1. **缓存失效语义**：授权缓存只缓存"已授权"状态，TTL 上限 1s；revoke 为事件驱动同步失效（不依赖 TTL 到期），因此 revoke 后首次读取即拒绝。
2. **digest 时机**：issue 时把 Core grant 的 per-tile 摘要固定到句柄内（不再向 UI 暴露）；每次 read 重新读取字节后计算并常量时间比较；不缓存已解密 tile 字节。
3. **误差边界**：identity = volume serial + file index（NTFS 可替换检测）；同 inode 等长原地重写由摘要覆盖；junction/reparse 在 issue 与 read 两处拒绝；摘要开销比为冷 IO 口径，不代表帧预算占比。
4. **范围**：S5-A 只做最小安全面；D4-1/3/5/6 完整 harness、Core 出 tile、安装 smoke 留 S5-B/C/D。

## 遗留
- `digest_overhead_ratio=5.39`：10% G5 门槛未达成本地测量口径；S5-B 需按"页加载预算内占比"重测（已记录边界，无放宽）。
- Core 侧尚无 tile 生成/digest 下发契约（S5-B）；修复前旧机制保持可用。
- 真实机器 smoke/IME 未做（S5-D）。
