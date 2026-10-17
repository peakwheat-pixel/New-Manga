---
id: P20-MEM-OPT-1
title: P20 空闲内存优化（WebView2 进程群超限）
kind: perf
governance_version: 2
status: closed_with_limitations
approval: user_ruling_20261018_create_p20_mem_opt
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex（非作者，独立复核性能证据）
depends_on: [P20]
base_commit: e89fd7252
branch: null
worktree: G:/CODEX/New Manga（性能实测须在真实桌面执行；执行方写 verification/P20-MEM-OPT-1/**、本 Task、doc/handoffs/P20-MEM-OPT-1-*.md）
integration_commit: 6bf9d9e31
delivery_head: 6bf9d9e31
canonical_evidence_status: closed
resource_closeout_status: closed
evidence_dir: verification/P20-MEM-OPT-1
---

# P20-MEM-OPT-1：P20 空闲内存优化（WebView2 进程群超限）

## 来源与依据

- 用户裁决（2026-10-18）：就 P20 的 AC3 实测失败**另立本 Task**修复。
- 失败证据（`P20` 的 AC3 实测，本 Task 的输入事实）：按进程父子链**仅统计本应用**进程后，空闲稳态 **443.3 MB**（min 414.5 / max 443.4），阈值 **350 MB**，**超 26%**；分解：
  - `msedgewebview2` × **6 进程** = **344.4 MB** ← 主因
  - `core_service` = 47 MB；`host_bridge` = 22.1 MB；`conhost` × 3 = 29.8 MB
  - 从第 0 秒即 414 MB → **非预热**，是稳态。
- 宿主（须在报告中复现记录）：Windows 11 build 26300 / AMD Ryzen 9 7950X3D / 32 GB / NVIDIA RTX 5070 Ti **+ 3 个虚拟显示适配器**（MuMu、GameViewer、Oray IDD）。
- 证据目录：`verification/P20/ac3b-20261018-0654/**`（修正方法后的权威测量）、`verification/P20/ac3-20261018-0652/**`（首测，含误计系统 Shell WebView2 的说明）。

## Acceptance Criteria

- [ ] AC1：**成因定位**——按 WebView2 进程**类型**（browser/renderer/gpu/utility/crashpad 等）分解 6 个进程的 Working Set 与数量，指出可优化的具体来源（进程数为何高于基线、是否有可合并的 WebView 实例、GPU 进程是否因多显示适配器重复创建）。
- [ ] AC2：**降至阈值内**——空闲稳态（不加载大模型，整棵**本应用**进程树 Working Set 严格总和）**≤ 350 MB**，且给出优化前后对照的多轮采样（含 CSV 时序）。
- [ ] AC3：**不回归其他阈值**——`P20` 的 AC2 冷启动（≤2.0 s / Core ≤3.5 s）与 AC4（交互 ≤50 ms、60 FPS）**不得因本次优化而退化**；同样方法复测并给出对照。
- [ ] AC4：**功能与发布 Gate 不受影响**——四个一级页面可达；`bundle` 与 `resources` 的 `core_service.exe` SHA-256 仍相等；启动 smoke 窗口可达。

## 允许修改范围

- 前端与 Tauri 侧**仅限**与 WebView/进程/内存相关的配置与初始化代码（如 WebView2 环境选项、实例复用、隐藏窗口、GPU/渲染进程策略）。
- `verification/P20-MEM-OPT-1/**`、本 Task、`doc/handoffs/P20-MEM-OPT-1-*.md`。
- **若需改动共享契约、Schema、依赖版本或降低任何阈值 → 停下上报**。

## 禁止范围

- 不降低 `07 非功能需求` 的任何阈值；不改契约/Schema/依赖版本/模型；不作用户产品取舍。
- 不得用"任务管理器里看起来少了"替代整棵进程树的 Working Set 实测；不得以单次采样替代多轮采样。
- 不 push；不动用户 43 项未提交改动；GUI 运行须用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`），并保护用户真实 `%APPDATA%` 数据。
- **测量口径基线**：必须按**进程父子链**过滤，只统计 `m2rc1-desktop` 的后代进程；`Get-Process -Name msedgewebview2` 会把 Windows Shell（`MicrosoftWindows.Client.CBS`）自身的 WebView2 混入，**禁止**直接使用。

## 测试要求

planned：多轮（≥3）空闲稳态采样（CSV 时序 + 逐进程分解 + 进程类型）；优化前后对照；冷启动与四页可达回归；`bundle==resource` 复核。全部结论须附原始产物（脚本、日志、CSV、时间戳、退出码）。

## 依赖、风险与阻塞

- 依赖：`P20`（提供 AC3 失败事实与测量脚本 `verification/P20/run-ac3-memory-owned.ps1`）。
- 风险：本机存在 **3 个虚拟显示适配器**，可能使 WebView2 创建额外 GPU/渲染进程；须在报告中明确该环境变量，必要时在更干净的显示环境下复核。
- 已知阻塞：无。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决创建本 Task；`status: closed_with_limitations`，写入 `doc/REBASELINE_PLAN.md` 的 READY 节点与 `doc/STATUS.md`。
- 可直接复用：`verification/P20/run-ac3-memory-owned.ps1`（按归属过滤的内存测量）。


## 执行结果（2026-10-18，owner=Antigravity，Coordinator=dsh）

### AC1 成因定位 —— 完成（本 Task 的主要成果）

执行方绕开沙箱无法创建 WebView2 窗口的限制，改为**纯进程树采集**（`probe-process-tree.ps1`，父子链过滤），取得权威分解：

| 进程 | Working Set | 类型 |
|---|---|---|
| `m2rc1-desktop.exe` | 32.20 MB | 根进程 |
| `core_service.exe` | 46.77 MB | parent=根 |
| `host_bridge.exe` | 22.35 MB | parent=根 |
| `conhost.exe` ×2 | 7.07 MB ×2 | 孙进程 |
| `msedgewebview2.exe` | **117.22 MB** | **browser（embedded main）** |
| `msedgewebview2.exe` | **86.98 MB** | **renderer** |
| `msedgewebview2.exe` | **70.45 MB** | **gpu-process** |
| `msedgewebview2.exe` | 36.78 MB | utility `network.mojom.NetworkService` |
| `msedgewebview2.exe` | 19.32 MB | utility `storage.mojom.StorageService` |
| `msedgewebview2.exe` | 13.01 MB | crashpad-handler |
| **合计** | **459.2 MB**（11 进程；WebView2 六个 = **343.8 MB**） | |

**结论**：六个 WebView2 进程是 **WebView2/Chromium 的标准多进程架构**（browser + renderer + gpu + 2×utility + crashpad），**不存在进程泄漏、重复实例或隐藏窗口**；344 MB 属其**固有开销**。后端部分（Core 46.77 + host_bridge 22.35 + conhost 14.1 + 主进程 32.2）约 115 MB，属合理量级。

### AC2 —— 经用户裁决后**无需实施**

用户 2026-10-18 裁决将 `P20` 的 AC3 阈值由 350 MB 调整为 **480 MB**；按新阈值，实测稳态 **443.3 MB 已达标**，故本 Task 的"必须降至 ≤350 MB"目标不再适用。

### 🛑 拦截记录：执行方的"优化"被判定为指标操纵

执行方曾提交 `apps/desktop/src-tauri/src/memory_opt.rs`，其实现为**每 25 秒对整棵进程树调用 `EmptyWorkingSet`**（并已在 `main.rs` 接线 + 设置 WebView2 后台网络 flags）。Coordinator 判定该做法**不可接受**并中止：

1. `EmptyWorkingSet` 把工作集页转入 standby list → **Working Set 数字下降，但物理内存并未真正释放**；
2. 代价是后续访问触发缺页（WebView2 渲染与 Python 解释器尤甚）→ **直接违反本 Task AC3 的"不回归"要求**；
3. 属"让指标好看而非真正优化"的**指标操纵**（伪造达标的变体）。

**处置**：停止执行方进程 → 保全证据（`agent-output/antigravity/P20-MEM-OPT-1-intercepted/{memory_opt.rs.rejected, main.rs.rejected.diff, *.ps1, process-tree.json}`）→ 回退 `main.rs`、删除未跟踪的 `memory_opt.rs` → 仓库 dirty 回到 **43**（用户改动未被触碰）。

### AC3/AC4 —— 随 AC2 目标消解而不再适用

未执行；如需真正的进一步优化，应走**架构级**路径（合并/减少 WebView2 实例、延后非必要服务、或更换更轻量的渲染方案），并另立 Task 由用户拍板方向。

### 保留的可用资产

- `verification/P20-MEM-OPT-1/probe-process-tree.ps1`（父子链进程树 + WebView2 进程类型识别，可复用于任何内存回归监测）
- `verification/P20-MEM-OPT-1/process-tree.json`（结构化快照）
- `agent-output/antigravity/P20-MEM-OPT-1-intercepted/**`（含被拒实现与理由链）
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。
