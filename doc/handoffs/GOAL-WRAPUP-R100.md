# Goal 收尾总账（Rounds 72–100，共 29 轮）

- head（收尾时）：`277406eeb`
- goal id：`goal-10d37e8e-fe31-4a4c-adb1-0957c50880bf`
- 轮次上限：100/100（本轮为最后一轮）

## 目标 A —— 四件套持续通过

### 结论：✅ **达成**（本会话首次）

| 检查 | 要求 | 实际 | 判定 |
|---|---|---|---|
| `check.ps1` | PASS | **PASS (3 warnings)** | ✅ |
| `verify_pins` | 18/18 | **18/18** | ✅ |
| `api_inventory` | 1/80/6=87 | **OK: rendered counts match FEA-C07 doc（1/80/6=87）** | ✅ |
| `App.Tests` | 不退化基线 955/0/11 | **962 passed / 0 failed / 4 skipped** | ✅ 通过数 +7，失败 0 |

**额外**：`apps/desktop-avalonia/scripts/test.ps1` **EXIT=0**（1579/1627 passed, 48 skipped），
三大测试项目全部 0 failed：

```
已通过! - 失败: 0，通过: 256，已跳过: 0，总计: 256    (NewManga.CoreClient.Tests)
已通过! - 失败: 0，通过: 361，已跳过: 44，总计: 405   (NewManga.Host.Tests)
已通过! - 失败: 0，通过: 962，已跳过: 4，总计: 966    (NewManga.App.Tests)
```

### 达成路径

| 阶段 | 轮次 | 内容 |
|---|---|---|
| 起点 | R63 | 5 failed / 251 passed |
| CoreClient 测试期望对齐 | 77–85 | 6 处修复 → 0 failed / 256 passed |
| Host 锁等待缺陷 | 89–94 | `WaitOne(0)` → 有界等待，3→2 failed |
| 自我纠错 | 95 | 推翻「并发 flaky」错误定性（`EXIT=0` 实为 SKIP） |
| Host identity 缺陷 | 96–98 | 定位到 `HostIssuer.cs:563` |
| 修复 | 99 | `NormalizeFileId` 53 位 mask → **EXIT=0** |

## 目标 B —— Release Gate 六条中 Agent 可独立完成的部分

### 结论：⚠️ **部分关闭，未全部判定**

本会话实质推进了以下与 Gate 相关的事项：

| 事项 | 变化 |
|---|---|
| sidecar schema 与测试夹具对齐 | `prepare-sidecar.ps1` 默认源从已退役 Tauri 路径改为 Avalonia 产物；`test.ps1` 加 manifest 新鲜度校验；`package.ps1` 加 schema 安全阀（`SIDECAR-SCHEMA-STALE-1`） |
| 打包时 sidecar schema 不匹配即拒绝 | 新增安全阀，避免发布陈旧 schema 的安装包 |
| `test.ps1` 全绿 | 安装矩阵的前置条件（测试基线）现已成立 |
| `FILE_IDENTITY_CHANGED` 修复 | **可能影响真实用户导入路径**的产品缺陷已修 |

**未完成**：Release Gate 六条条件的逐条状态评估未系统化落盘。
`doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md` 做过 Agent/Human 划分，
但没有把六条 Gate 逐条映射到「已关闭 / 未关闭 / 需人判」。

## 目标 C —— 已登记技术债清零

### 结论：⚠️ **两项清零，第三项部分处置**

| 债项 | 状态 |
|---|---|
| `check.ps1` 历史终态卡 AC 豁免 | ✅ **已完成**（`$htmlAcExempt` / `$historicalAcExempt` 已实现） |
| `doc/tasks` 控制字符损坏修复 | ✅ **已完成**（`DOC-CTRLCHAR-FIX-1` done / `DOC-CTRLCHAR-FIX-2` closed_with_limitations） |
| AC blocked 项中可归因闭合项 | ⚠️ **部分**：`AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md` 核实 41 条可闭合，其中 8 条已处置；**剩余 33 条待处置**（`DOC` 8 / `RERUN` 5 / `IMPL` 20，`FEA-04` 独占 8 条需另立实现卡） |

## 目标 D —— 剩余 HUMAN-REQUIRED 登记

### 结论：⚠️ **主体已登记，有 1 项待并入**

`doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 已登记 **H-01 … H-09**（物理设备 / 人眼判定 /
外部账号类事项，各附最小操作步骤）。

**待办**：`MICA-FIX-1` AC2 的人眼判定部分需并入 H-01（已在 `MICA-FIX-1` 卡上注明，未实际合并）。

## 本会话新增/闭合的 Task

| Task | 状态 |
|---|---|
| `SIDECAR-SCHEMA-STALE-1` | closed_with_limitations（2 个真缺陷修复 + 安全阀） |
| `DOC-CTRLCHAR-FIX-1` | done |
| `DOC-CTRLCHAR-FIX-2` | closed_with_limitations |
| `GOAL-C-DEBT-AUDIT-1` | done |
| `AC-BLOCKED-CLOSE-1` | done |
| `HUMAN-VS-AGENT-SPLIT-1` | done |
| `HOST-CONCURRENCY-FLAKY-1` | **新建**，AC1–AC5 MET，AC6 复核进行中 |

## 本会话发现的真实产品缺陷（非测试问题）

**1 个**：`HostIssuer.cs` 未套用 53 位 file-id 归一化 ⇒ 用户新导入的源文件
（NTFS FileIndex > 2^53，实测 6/7）会稳定报 `FILE_IDENTITY_CHANGED`
（"Import source reference was rejected"）。

**其余 6 处修复均为测试期望过时**（产品行为正确、测试未跟上 sidecar 演进）。

## 本会话的错误账（6 次同类）

| # | 错误 | 发现方式 |
|---|---|---|
| 1 | 夹具副本错认成产品 bundle | 独立复核（r1） |
| 2 | 从 weights 警告推断 pending 原因 | 自测 |
| 3 | probe 用点号命令名 | 自测 |
| 4 | probe 自己传 null | 自测 |
| 5 | 诊断代码改控制流跳过断言 | 自测 |
| 6 | **把 `EXIT=0`（含 skipped）当成 passed** | 自测（R95 详情日志） |

**共同根因**：用自己的临时工具/推断下结论，却不先验证那个工具/推断是否忠实反映真实链路。

**第 6 次的代价最大**：它让 R88–R92 共 3 轮建立在「并发 flaky」的错误定性上，
直到 R95 用 `--logger "console;verbosity=detailed"` 看到 `[SKIP]` 才推翻。

## 收尾时的遗留项（下一会话可直接接手）

| # | 事项 | 建议下一步 |
|---|---|---|
| 1 | `HOST-CONCURRENCY-FLAKY-1` AC6 独立复核 | 复核报告落盘后，按 findings 返修 → 集成提交 |
| 2 | 目标 C 剩余 33 条可闭合 AC | 按 `AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md` 分类处置；`FEA-04` 独占 8 条需另立实现卡 |
| 3 | 目标 B 六条 Gate 逐条评估 | 产出一份「Gate 条件 → 状态 → 证据 → 剩余动作」映射表 |
| 4 | `MICA-FIX-1` AC2 并入 H-01 | 编辑 `HUMAN-REQUIRED-2026-11-15.md` |
| 5 | `test.ps1` 污染 `verification/` 下文件 | 跑测试会改写 `READER-OVERLAY-HEADLESS-PNG-1/{immersive-reader.png, render-info.md}`；应登记并修（或改为输出到 workspace） |
| 6 | `RELEASE-PACKAGE-1.md` NUL 字节、`M2-REGION` 重复键、`PLAN:56/58` 漂移 | 既有小债 |

## 诚实结论

- **目标 A 达成**（本会话首次四件套 + `test.ps1` 全绿）；
- **目标 B/C/D 未完全达成**：B 缺六条 Gate 逐条评估、C 剩 33 条 AC、D 有 1 项待并入；
- 本会话修复了 **1 个真实产品缺陷** + **6 处测试期望** + **1 个锁等待缺陷**；
- 本会话犯了 **6 次同类判断错误**，全部已记录并更正，其中 1 次代价是 3 轮方向错误。

**目标未完全达成，不应标记为 complete。**
