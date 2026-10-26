---
task_id: HOST-RESOURCE-SECURITY-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: 09d7e76c1
delivery_head: 4a1dbe96fced6223426b2be7747282550d07e5e8
status: draft
---

# Handoff：HOST-RESOURCE-SECURITY-1（S5-B）

## 结果（AC1–AC6 全 MET）
- **D4-1**：同 size 原地改写并把 mtime 恢复原值 → \TileDigestMismatch\；证据记录 mtime_unchanged=true、validation_uses_mtime=false。
- **D4-3**：issue 处 dotdot / UNC / junction / symlink 全部拒绝（\TilePathOutsideRoot\ / \TilePathReparse\）；read 处把路径替换为 junction → 拒绝（\TilePathOutsideRoot\）。
- **D4-5**：同路径新文件替换（size 相同）→ \TileIdentityMismatch\（volume serial + file index）。
- **D4-6**：8×256KiB 页通过 tile 通道冷读+逐 tile digest：**2.259ms ≤60ms**；digest **0.8ms = 1.33% of 60ms 预算 ≤10%**（G5 预算口径，明确不沿用 S5-A 的 5.39× 缓存口径）；证据注明 OS 缓存状态，不声称磁盘冷读。
- **契约冻结**：\pps/desktop-avalonia/docs/TILE-CHANNEL-CONTRACT-V1.md\（grant manifest + UI 视图 + 安全不变量 + 错误码），契约测试校验字段/可见面/文档 token；本卡不改 Core。
- **门禁**：\scripts/test.ps1 -CanonicalEvidence\ **101/101**；vitest 60/567；pytest 3F/2687P/9S = 基线；check PASS；证据 E1–E7 64-hex pin。

## 复跑与证据
\erification/HOST-RESOURCE-SECURITY-1/**\（MANIFEST \3b833b9f…\）。复跑：\pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1\（rerun 写 workspace，不覆盖 pin）。

## Record Decision
1. **mtime 独立性**：有效性只由 per-tile digest + file identity 决定；mtime 不参与校验（测试显式恢复 mtime 仍拒绝）。
2. **escape 两处校验**：issue 走路径遍历 + 组件 reparse 检查；read 走 handle 重导最终路径 + 根内 + reparse + identity/size/digest。任一处失败即 typed error。
3. **D4-6 口径**：digest 占比 = digest 耗时 / 60ms 页加载预算（G5 文本口径）；实测 1.33%。另记 digest/实测 load = 35.4% 仅供诊断，不作为门槛。
4. **契约范围**：v1 冻结 manifest/UI 视图/错误码；Core 侧 tile 生成与 digest 下发的实现在独立 Core Task，契约测试只验证 Host 侧结构与文档一致性。

## 遗留
- Core 侧 tile 生成/digest 下发未实现（需独立 Core Task，本卡禁止改 Core）。
- 真机磁盘冷读未复现（OS 缓存；已注明口径）；安装 smoke/IME 留 S5-D。
- 旧壳未动（S5-C 归档前置 = 本卡 + S5-D 通过）。
