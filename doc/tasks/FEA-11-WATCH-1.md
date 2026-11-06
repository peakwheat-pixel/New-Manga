---
id: FEA-11-WATCH-1
title: FEA-11 目录 watcher 生产者/消费者（hint → 全量重枚举；Host-only）
kind: implementation
governance_version: 3
status: changes_requested
approval: 用户 2026-11-06「同意继续让 Codex/ZCode 决定下一项」→ Codex 首轮超时 → **ZCode 裁决 NEXT-TASK=FEA-11-WATCH-1**（AC11-1 唯一承接；须先独立 scope review 并裁决 watcher 必要性）；scope review `doc/reviews/FEA-11-WATCH-1-scope-r1.md` = **NECESSARY**（AC11-1 逐字含目录 watcher 生产者/消费者与丢 hint/overflow 全量重枚举；C-01b SC-25 FROZEN 把 watcher hint 列入检测组合；C-17 v1.1:18 声明四路检测为实现责任）；DSH 2026-11-06 接受并冻结释放（Owner 由 DSH 指定为 `fea12-core-host`，scope review 建议 ZCode 作独立 Review 备选）
suggested_owner: zcode（scope review 建议）；实际 Owner：fea12-core-host（DSH Agent Teams，Host .NET 分片）
owner: fea12-core-host
reviewer: 独立上下文 fresh subagent（r1 session `48af6d93-b456-4c17-9478-a694fb7bbb10`；报告 `doc/reviews/FEA-11-WATCH-1-r1.md`；CHANGES P0=0/P1=1/P2=1/P3=6；未参与实现）
depends_on:
  - FEA-11
  - FEA-11-SCAN-1
  - FEA-11-SCAN-2
base_commit: 919c9aa1e   # WATCH-1 释放点 main head（SCAN-2 closeout 后）
branch: null
worktree: null
integration_commit: null
delivery_head: e60105cf9   # 实现交付 commit（未 push；集成/推送由 DSH）
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-WATCH-1
allowed_paths:
  - doc/tasks/FEA-11-WATCH-1.md
  - doc/reviews/FEA-11-WATCH-1-*.md
  - doc/handoffs/FEA-11-WATCH-1-*.md
  - verification/FEA-11-WATCH-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
out_of_scope:
  - App/UI/通知/持久化改动；watcher 事件作为“已同步/已删除”证据；增量 diff
  - 扫描执行/周期调度（SCAN-1）、冷启动枚举（SCAN-2）的重写
  - Core 定时器/反向 RPC；C-01b/C-17/C-16/C-15/C-06/M2-C1 冻结字节；18 pins 变更
  - SQLite schema/迁移/索引；新依赖；真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-WATCH-1：目录 watcher 生产者/消费者（hint → 全量重枚举）

> **状态：`ready`（scope 已冻结；scope review = NECESSARY；待 Owner 认领实施）。**
> 承接 FEA-11 AC11-1 的 watcher 半边；**不做**启动全量扫描（「启动/访问前检查」的解释歧义留给 AC11-1 终态裁决），**不自动回填 AC11-1 MET**。

## 来源与依据

1. ZCode 2026-11-06 裁决（用户授权 Codex/ZCode 决定下一项；Codex 首轮超时未返回）。
2. 独立 scope review：`doc/reviews/FEA-11-WATCH-1-scope-r1.md`（fresh subagent；**NECESSARY**；In/Out、AC-W1…W5、allowed_paths、风险）。
3. 契约：C-01b FROZEN v5 **SC-25**（检测组合含「目录 watcher hint」）；C-17 v1.1:18（四路检测是 FEA-11 实现责任）；18 pins 不修改。
4. 现状：`SourceScanScheduler`（SCAN-1，done）已有 target/单飞/预算/退避/注入时钟；`HostSourceScanTargetEnumerator`（SCAN-2，done）；`HostRuntime` 启停顺序；`SourceAccessRegistry` 只读 List + typed 不可读。全仓生产代码 `FileSystemWatcher`/`ReadDirectoryChangesW` 0 命中。

## 目标

Host 侧新增只读目录 watcher，作为**检测延迟优化**与 AC11-1「丢 hint/overflow 后可全量重枚举」的可测通道：watcher 事件只产生 per-source due hint，去抖/合并后触发一次既有 `ScanSourceSync` 全量重枚举；**hint 不是真值**，不得据此推断 changed/deleted，不得建 plan/apply/删除。

## Scope（冻结）

### In
1. **Host-only `SourceWatcher`**（新文件 `Sources/SourceWatcher.cs`）：仅 watch 已注册目标根；file target 仅精确文件，folder target 递归；随 Host 启停（Ready 后 arm、Stop 后零 hint）；registry 复核后才 arm；不可读/撤销 → typed skip。
2. **hint 语义**：per-source due bit；去抖/合并（默认 2000ms，可注入时钟；N 事件合并为 1 次）；overflow/根删除 → 全部 target due + 重枚举；buffer 64 KiB、max watches 256、可注入上限并降级（不崩、不泄路径）。
3. **与 SCAN-1 协同**：hinted source 优先；同 source 至多一个扫描（单飞）；预算/退避/pause 生效；命令集合精确 `{ScanSourceSync}`；零写、不建 plan/apply/journal；结果只进 `SourceScanStatus.Watcher`（closed record，无路径/grant/session）。
4. **测试/证据**：隔离根真实文件树测试（真实 `FileSystemWatcher`）+ 可注入时钟/队列；overflow/根删除/去抖/合并/单飞/停机取消/脱敏；全量 .NET 不降。

### Out
- App/UI/通知/持久化；watcher 事件当“已同步/已删除”证据；增量 diff；扫描本体/周期调度/冷启动枚举重写；Core 定时器/反向 RPC；契约/schema/依赖/18 pins；真实数据；push。

## 实现语义（DSH 冻结）

- hint 只触发一次 full re-enumeration（`ScanSourceSync`），不得作为 changed/deleted 结论。
- 去抖窗口内多事件合并；overflow 或根不可读 → 全目标 due，下一 tick 重枚举；watcher 生命周期与 HostRuntime 启停严格成对，Stop 后不得再发 hint。
- 上限（watches 256、buffer 64 KiB、每根/总事件可注入）与降级行为必须可测；日志/状态不得含路径。
- **AC11-1 不回填**：本卡不做启动全量扫描；AC11-1 终态（MET/limitation）由后续 DSH 裁决（或在 WATCH-1 closeout 时按「watcher 已兑现 + 访问前/操作前强验证 + 周期/冷启动扫描」组合判定 MET，需显式记录）。

## Acceptance Criteria

- [ ] **AC-W1 生命周期与范围**：Ready 后对已注册目标 arm；file target 仅精确文件、folder 递归；registry 复核失败/撤销/不可读 → typed skip；Stop 后零 hint；重启幂等。 证据：`SourceWatcherTests` 15 例 + gated `Fea11WatchHostRuntimeTests`（Ready→armed→Active=1→真实事件 hint→Dispose 后 watcher/scheduler 均 null）；`logs/watcher-unit.log`、`logs/watcher-runtime.log` <<PARTIAL: r1 P2 撤销后 refresh 未拆除 watcher；修复后恢复>>
- [ ] **AC-W2 hint 语义与去抖**：N 事件 → 恰好 1 次 `ScanSourceSync`（可注入时钟，零 sleep）；hint 不写 changed/deleted；丢 hint（队列满/模拟 overflow）后周期扫描可兜底检测；hint 去抖合并可注入窗口。 （证据：5 事件→1 hint→1 scan，窗口后第 2 次；`last_result=ok` 非 changed；真实文件树 smoke；`hint` 仅按 source_id） <<PARTIAL: r1 P1 hint pass 从预算游标起步会跳过被 hint 源；修复后恢复>>
- [x] **AC-W3 overflow/根删除**：overflow、根删除/替换、buffer 满 → 不崩、全部 target due + 下一 tick 重枚举、watcher re-arm 或 typed 降级；上限（watches 256/buffer 64 KiB）可注入并验证。 （证据：overflow/根删除/上限/边界值用例；10 targets/budget=4 跨 tick 完成；`OverflowCount/Degraded/Uncovered` 计数；M2 变异红） <<MET>>
- [x] **AC-W4 与 SCAN-1 协同**：同 source 至多一扫描（单飞合并）、hinted 优先、backoff/pause 生效、命令集合精确 `{ScanSourceSync}`、零 Core 业务写、不建 plan/apply/journal。 （证据：hinted 优先/在飞合并 replay≤1/每 source≤2 次/无并发/backoff 不提前/pause 0 次；命令集合仅 `ScanSourceSync`；M1/M3 变异红） <<MET>>
- [x] **AC-W5 资源/隐私/门禁**：日志/状态无路径/secret/grant/session；无新依赖；无 schema/契约/pins 改动（`verify_pins.ps1` **18/18**）；全量 .NET 不降（基线 **1500/0/85**；flaky 复跑记录；跑后恢复 `verification/FEA-09`）；全量 pytest 引用基线 **3212/10**（本卡零 Python）；`check.ps1 -TaskPath` PASS；范围 diff 仅本卡 allowed_paths；AC11-1 仍 PARTIAL、L10 不解决。 （证据：全量 .NET **1521/0/86**（RUN1/RUN2）；pytest **3212/10** 实跑一致；pins 18/18、API PASS、check PASS、scope diff 空；脱敏断言；无新依赖） <<MET>>

## 预期行为变更（Review 不判回归）

1. 新目录/文件变化会在去抖窗口后触发一次全量重枚举（而不是等下一周期），扫描延迟降低；不改变扫描语义/零写。
2. watcher 启动失败/不可读/上限耗尽 → typed 降级（周期扫描兜底），不阻塞 Host 启动。
3. 不产生新的 UI/通知行为。

## 允许修改范围

frontmatter `allowed_paths` 为准（Host src/tests + 卡/Handoff/verification）。若编译连带需要 App 文件，必须先 message Lead 记录 allowlist 例外（SCAN-2 `LibraryViewModel.cs` 先例），不得自行扩大。

## 禁止范围

不改 App/UI/契约/schema/依赖/STATUS/PLAN/LEDGER/reviews；不把 watcher 事件当同步/删除证据；不建 plan/apply/删除；不碰真实数据；不 push；实现者不得自审。

## 测试要求

| 计划测试 | 命令/方法 | 环境 | 期望 | 证据路径 |
|---|---|---|---|---|
| Watcher 单测 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Watcher"` | 隔离根真实文件树 + 注入时钟 | PASS（生命周期/去抖/merge/overflow/根删除/单飞/脱敏） | `verification/FEA-11-WATCH-1/logs/watcher-unit.log` |
| gated HostRuntime | 同 gated 用例（`[HostSidecarFact]` 或等价 seam） | 隔离 | PASS（Ready arm / Stop 后零 hint / 不阻塞） | `logs/watcher-runtime.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | 仓库根 | **≥1500/0/85**；flaky 复跑并记录；跑后 `git checkout -- verification/FEA-09` | `logs/dotnet-full-*.log` |
| 全量 pytest（引用） | `pytest tests -q -p no:warnings --tb=no` | 仓库根 | 基线 **3212/10**（本卡零 Python，非重跑） | 引用 SCAN-2 证据 |
| pins/check/API | `verify_pins.ps1`；`check.ps1 -TaskPath`；`generate_api_inventory.py --check` | 仓库根 | 18/18；PASS；PASS | `logs/gates.log` |
| 范围 diff | `git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/` | 仓库根 | 空 | `logs/scope-diff.log` |

## 依赖、风险与阻塞

- 依赖：FEA-11（AC11-1 PARTIAL）；SCAN-1 done；SCAN-2 done；C-01b SC-25 冻结条款；scope review NECESSARY。
- 风险/limitation：漏事件（周期扫描兜底，非正确性依赖）；卷类型/网络盘行为差异；句柄/资源泄漏；IO 放大；路径隐私（脱敏）；测试时序不稳定（flaky）；root 过宽（只 arm 已注册目标）；授权漂移（registry 复核）；无 UI 消费者；SCAN-2 RH-3 targets 只增不减不修；**AC11-1 不回填 MET**。
- 阻塞：无（scope 已冻结）。

## r1 Review 处置（DSH，2026-11-06）

- 结论：**CHANGES**（P0=0 / **P1=1** / P2=1 / P3=6；报告 `doc/reviews/FEA-11-WATCH-1-r1.md`，session `48af6d93…`）。
- **P1（阻断，AC-W2/AC-W4）**：`SourceScanScheduler.TickCoreAsync` 先把 hinted target 排到最前，但仍从 `start = _budgetCursor % targetCount` 开始取预算；Reviewer 仓外探针（10 targets/budget 4：先扫 s0..s3，再 hint s9）复现 hint pass 实际扫 s3..s6、s9 未扫（HintPending=true，需等 900s）。最小修复：`start = _hintedSources.Count > 0 ? 0 : (_budgetCursor % targetCount)`；补「先跑 rotation 再 hint」判别测试。
- **P2（AC-W1/L-W3）**：`RefreshTargetsAsync` 仅在 `added+updated>0` 时 `NotifyTargetSetChanged()`；撤销后成功 refresh（空枚举）不通知，watcher Active 仍=1。修：refresh 成功后也通知（使 watcher 复核/拆除）；补 revoke-after-refresh 测试。
- P3×6：Stop 后零 hint 的 timer/callback 窄竞态；canonical `pytest-full.log` 无结束 summary（需重抓完整日志）；`RootLost` 断言 `|| Active>=0` 恒真；缺 generation-drift/buffer 注入/hint-after-rotation/revoke-after-refresh 测试；redaction 口径限定 watcher/scheduler 行；`DisposeAsync` 未 await 在飞 hint task；`Sync` 的 `IntersectWith+UnionWith` 可简化为 Union。按最小修复或登记 limitation。
- 派发：`fea12-core-host`（r2 最小返修）→ Lead 集成复跑 → r2 窄面复审 → closeout；AC11-1 仍 PARTIAL、不回填。

## 交付与运行记录（2026-11-06）

- 交付：`e60105cf9`（feat：`SourceWatcher.cs` + Host 5 改 + 测试 3 文件 + 卡/Handoff + verification）→ `cf0ef2206`（docs 回填/提交后 check）。
- 实现要点：Host-only watcher 只 watch scheduler 当前 target 根（file 精确 filter + 事件名二次匹配、folder 递归）；arm 前 registry 复核（registry/generation/撤销/root readable），不可读/撤销/漂移 → typed `uncovered`（周期兜底）；事件只置 per-source due bit、2000ms 去抖 N→1（`TimeProvider` 注入）；overflow/根删除/句柄失效 → 全 target due（受预算跨 tick）+ `OverflowCount/Degraded/Uncovered`；与 SCAN-1 单飞/预算/退避/pause 协同、hinted 优先、replay≤1、命令集合精确 `{ScanSourceSync}`、零写；HostRuntime Ready 后 arm、Stop/Dispose 先 disarm。
- 测试：`SourceWatcherTests` 15 例（含真实隔离文件树）、gated `Fea11WatchHostRuntimeTests`、`SourceScanSchedulerTests` +6；变异 M1（去抖）/M2（overflow 全 due）/M3（hinted 优先）均转红后恢复。
- 门禁（实跑）：Host 单测 **179/0/55**；gated HostRuntime watcher **1/0/0**；全量 .NET **RUN1/RUN2 1521/0/86**（基线 1500/0/85 不降；跑后恢复 `verification/FEA-09`；本轮未触发 flaky）；全量 pytest **3212 passed/10 skipped**（实跑一致）；pins **18/18**；API inventory PASS；`check.ps1 -TaskPath` PASS；scope diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` **0 行**。
- AC-W1…AC-W5 全 MET（逐条证据见 `verification/FEA-11-WATCH-1/record.md` §2）。
- 限制：漏事件/设备差异依赖 SCAN-1 周期兜底（非正确性依赖）；folder 内任意事件=该 source due（无增量 diff、受预算约束）；SCAN-2 RH-3 target 只增不减不修；HostRuntime seam 无 fake-Core/注入时钟（成功路径组件级覆盖）；真实树事件测试理论可能 flaky（本轮两轮全绿）；**AC11-1 仍 PARTIAL（本卡不回填）**；L10 不解决。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-W5 | verification/FEA-11-WATCH-1/changed-files.txt | - | 046c059fac152a409a83d2f44c2e939b8a7bd8f2745fa292367aeb17b4a78678 | CANONICAL |
| EV-02 | AC-W1/2/3/4 | verification/FEA-11-WATCH-1/host-watch-runtime.json | - | 25baaac0fa55785a1d6062f6f7c28dcd20566ac0103a0bb45a330e99d323dfb6 | CANONICAL |
| EV-03 | AC-W5 | verification/FEA-11-WATCH-1/logs/api-inventory.log | - | b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47 | CANONICAL |
| EV-04 | AC-W5 | verification/FEA-11-WATCH-1/logs/check-post-commit.log | - | 495afa593898d7c6175829fe709bc17d284d1f62dcc69d4b5cdc82e3659779e7 | CANONICAL |
| EV-05 | AC-W5 | verification/FEA-11-WATCH-1/logs/check.log | - | 495afa593898d7c6175829fe709bc17d284d1f62dcc69d4b5cdc82e3659779e7 | CANONICAL |
| EV-06 | AC-W5 | verification/FEA-11-WATCH-1/logs/dotnet-full-1.log | - | 915f78a28237abae830c913aa1d9c841a96083af7aa7d14dd2326a9becf8e6fb | CANONICAL |
| EV-07 | AC-W5 | verification/FEA-11-WATCH-1/logs/dotnet-full-2.log | - | 7a53f0b9d45ae685dd25cf751ff61a7f6b24f34e3a1a3a979e3910a1321516eb | CANONICAL |
| EV-08 | AC-W5 | verification/FEA-11-WATCH-1/logs/gates.log | - | e5285a48a2c477411126054e4edf68ed5fb7fda56b31a3b33774004d0c79f4ce | CANONICAL |
| EV-09 | AC-W5 | verification/FEA-11-WATCH-1/logs/mutation-m1-debounce.log | - | 5f4560d20c9fc43d2492fa578e63a650a4449d30b4dfc371a6d001e15fd62355 | CANONICAL |
| EV-10 | AC-W5 | verification/FEA-11-WATCH-1/logs/mutation-m2-overflow.log | - | 8d7336cd899a74fcdc43137d6bc34fd97b81ff65a1d73a7d081ff445e3837f52 | CANONICAL |
| EV-11 | AC-W5 | verification/FEA-11-WATCH-1/logs/mutation-m3-priority.log | - | d045f86351fb7668bcb3dd272486a0ec4993b6687ab3fe7792a4e96245197324 | CANONICAL |
| EV-12 | AC-W5 | verification/FEA-11-WATCH-1/logs/pins.log | - | f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db | CANONICAL |
| EV-13 | AC-W5 | verification/FEA-11-WATCH-1/logs/pytest-full.log | - | da630cafd6368946e3e9ddb8b8f4b5dbe6620b8bcaa299e5bb16d3d76e029125 | CANONICAL |
| EV-14 | AC-W5 | verification/FEA-11-WATCH-1/logs/watcher-runtime.log | - | d6fe979a8bd84967865b02f96672f2d5405037bbd816fff4457cd1c6b3071699 | CANONICAL |
| EV-15 | AC-W5 | verification/FEA-11-WATCH-1/logs/watcher-unit.log | - | ed4145da78fa92b3e548812c235c628ac2ac410e4f042301d3ea88a01d82fd47 | CANONICAL |
| EV-16 | AC-W1/2/3/4 | verification/FEA-11-WATCH-1/record.md | - | db90ab3461188b6782065e3e66eb8c969fef2127f32ddad693576711d47b465a | CANONICAL |
| EV-17 | AC-W5 | verification/FEA-11-WATCH-1/scope-validation.log | - | 55a367bf87df4c1a606e261a8ef44eb8212b4e99068b57dc3fd4cd2941b910a9 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树） | NOT_APPLICABLE | — | — | 未创建独立 worktree |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-11-WATCH-1\` | DELETE_SAFE | — | verification/FEA-11-WATCH-1/logs/gates.log | 仅隔离文件树/IPC 临时根；closeout 删除并记录字节数 |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea11-watch-1\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\agent-output\fea11-watch-1` | verification/FEA-11-WATCH-1/logs/gates.log | 过程日志副本；保留不清理 |

## Owner 交付记录（fea12-core-host，2026-11-06）

- 状态：实现 + 测试 + 门禁完成，**in_review 待独立上下文 Review**；未 push、未自审、未回填 AC11-1。
- 交付内容：新增 Host-only `Sources/SourceWatcher.cs`；`SourceScanScheduler` 增加 hint 入口/合并重放/优先排序/`TargetSetChanged`/`TargetSnapshot`/`Watcher` 状态投影；`HostOptions` 4 个可注入 watcher 选项；`HostRuntime` Ready 后 arm、Stop/Dispose 先 disarm；`SourceScanStatus.Watcher` closed record；新增 `SourceWatcherTests`（15）、gated `Fea11WatchHostRuntimeTests`（1）、`SourceScanSchedulerTests` +6。
- AC-W：AC-W1…W5 全 MET（证据映射与判别变异见 `verification/FEA-11-WATCH-1/record.md`）。
- 门禁：全量 .NET **1521/0/86**（基线 1500/0/85；RUN1/RUN2）；pytest **3212 passed / 10 skipped**（引用基线一致，零 Python）；pins **18/18**；API inventory PASS；check PASS（3 既有 warnings）；scope diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` **空**；每轮全量后已恢复 `verification/FEA-09`。
- 变异判别：M1 去抖/合并移除、M2 overflow 全量 due 移除、M3 hinted 优先移除 → 分别转红后恢复（`logs/mutation-m*.log`）。
- limitation：漏事件/设备差异依赖周期扫描兜底（非正确性依赖）；folder 内任意事件视为该 source due（无增量 diff，受预算约束）；SCAN-2 RH-3 target 只增不减不修；HostRuntime seam 无 fake Core/注入时钟（成功路径由组件级覆盖）；AC11-1 仍 PARTIAL、L10 不解决。
- Handoff：`doc/handoffs/FEA-11-WATCH-1-delivery.md`。
- 实现 commit：`e60105cf9`（未 push；交付后由 DSH 更新 REBASELINE_PLAN/把卡置 in_review 并集成推送）。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：AC11-1 仍 PARTIAL（本卡不回填）；L10 不解决；SCAN-2 RH-3 不修；watcher 漏事件依赖周期兜底。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
